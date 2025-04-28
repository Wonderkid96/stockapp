"""
Order Executor Module

This module handles the execution of trading signals through the Alpaca API
while enforcing zero-leverage trading rules.
"""

import logging
import os
from typing import Optional

from alpaca_trade_api.rest import REST, APIError
from sqlalchemy.orm import Session

from . import crud, schemas

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Initialize Alpaca API client
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET")
ALPACA_API_URL = os.getenv("ALPACA_API_URL", "https://paper-api.alpaca.markets")

api = REST(key_id=ALPACA_API_KEY, secret_key=ALPACA_API_SECRET, base_url=ALPACA_API_URL)


def get_buying_power() -> float:
    """Get current buying power (cash) from Alpaca account."""
    try:
        account = api.get_account()
        return float(account.cash)
    except APIError as e:
        logger.error(f"Error getting account info: {e}")
        raise


def calculate_order_size(signal: schemas.Signal, buying_power: float) -> Optional[int]:
    """
    Calculate the number of shares to trade based on available cash.
    Ensures zero-leverage by checking order_size * price <= buying_power.
    """
    if signal.price <= 0:
        logger.error(f"Invalid price {signal.price} for {signal.symbol}")
        return None

    # Calculate maximum shares possible with available cash
    max_shares = int(buying_power / signal.price)

    if max_shares <= 0:
        logger.warning(
            f"Insufficient buying power ({buying_power}) "
            f"for {signal.symbol} at {signal.price}"
        )
        return None

    # For now, use all available buying power
    # This could be modified to use a position sizing strategy
    return max_shares


def execute_signal(db: Session, signal_id: int) -> bool:
    """
    Execute a trading signal through Alpaca while enforcing zero-leverage.
    Returns True if order was executed successfully.
    """
    try:
        # Get signal from database
        signal = crud.get_signal(db, signal_id)
        if not signal:
            logger.error(f"Signal {signal_id} not found")
            return False

        # Check if signal was already executed
        if signal.executed:
            logger.warning(f"Signal {signal_id} already executed")
            return False

        # Get current buying power
        buying_power = get_buying_power()

        # Calculate order size
        qty = calculate_order_size(signal, buying_power)
        if not qty:
            return False

        # Submit order to Alpaca
        side = "buy" if signal.signal_type == "BUY" else "sell"
        try:
            api.submit_order(
                symbol=signal.symbol,
                qty=qty,
                side=side,
                type="market",
                time_in_force="day",
            )

            # Mark signal as executed
            crud.mark_signal_executed(db, signal_id)

            logger.info(
                f"Executed {side} order for {qty} shares of "
                f"{signal.symbol} at {signal.price}"
            )
            return True

        except APIError as e:
            logger.error(f"Error submitting order: {e}")
            return False

    except Exception as e:
        logger.error(f"Error executing signal {signal_id}: {e}")
        return False
