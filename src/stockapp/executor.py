"""
Executor Module

This module is responsible for polling for unexecuted signals, connecting to the Alpaca API,
placing market orders, marking signals as executed, and logging the results.
"""
import logging
import os
import time

import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from stockapp.db_models import Signal, get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET")
ALPACA_PAPER_URL = os.getenv("ALPACA_PAPER_URL", "https://paper-api.alpaca.markets")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

if not ALPACA_API_KEY or not ALPACA_API_SECRET:
    logger.error("Alpaca API keys not set. Please check your .env file.")
    exit(1)

# Initialize Alpaca API
api = tradeapi.REST(
    ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_PAPER_URL, api_version="v2"
)


def poll_and_execute(db: Session):
    """
    Poll for unexecuted signals and execute them (or simulate if dry-run).
    """
    signals = (
        db.query(Signal)
        .filter(Signal.executed.is_(False))
        .order_by(Signal.timestamp.asc())
        .all()
    )
    logger.info(f"Found {len(signals)} unexecuted signals.")
    for signal in signals:
        symbol = signal.symbol
        signal_type = signal.signal_type
        logger.info(f"Processing signal: {signal_type} {symbol} at {signal.timestamp}")
        if DRY_RUN:
            logger.info(f"[DRY RUN] Would execute {signal_type} order for {symbol}.")
            signal.executed = True
            signal.execution_details = {"dry_run": True, "timestamp": str(time.time())}
            db.add(signal)
            db.commit()
            continue
        try:
            account = api.get_account()
            cash = float(account.cash)
            price = api.get_latest_trade(symbol).price
            qty = int(cash // price) if signal_type == "BUY" else 0
            if qty > 0:
                order = api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side=signal_type.lower(),
                    type="market",
                    time_in_force="gtc",
                )
                signal.executed = True
                signal.execution_details = {
                    "order_id": order.id,
                    "qty": qty,
                    "price": price,
                }
                db.add(signal)
                db.commit()
                logger.info(f"Order placed: {order}")
            else:
                logger.warning(f"Not enough cash to place order for {symbol}")
        except Exception as e:
            logger.error(f"Order failed for {symbol}: {e}")
            continue


def run_executor_loop(db: Session, poll_interval: int = 10):
    """
    Continuously poll and execute signals.
    """
    while True:
        poll_and_execute(db)
        time.sleep(poll_interval)


# Example usage
if __name__ == "__main__":
    db = next(get_db())
    run_executor_loop(db, poll_interval=10)
