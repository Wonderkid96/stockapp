"""
Backtesting Module

This module is responsible for running historical backtests using the same logic as the signal engine,
generating performance metrics, and comparing results with the signals table.
"""

# Historical backtesting script
import logging

import pandas as pd

from stockapp.db_models import Indicator, RawPrice, get_db
from stockapp.signal_engine import detect_ma_crossover, detect_rsi_signals

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_historical_data(db, symbol, start_date, end_date):
    """
    Load historical price and indicator data for backtesting.
    """
    prices = (
        db.query(RawPrice)
        .filter(
            RawPrice.symbol == symbol,
            RawPrice.timestamp >= start_date,
            RawPrice.timestamp <= end_date,
        )
        .order_by(RawPrice.timestamp.asc())
        .all()
    )
    indicators = (
        db.query(Indicator)
        .filter(
            Indicator.symbol == symbol,
            Indicator.timestamp >= start_date,
            Indicator.timestamp <= end_date,
        )
        .order_by(Indicator.timestamp.asc())
        .all()
    )
    # Convert to DataFrames
    price_df = pd.DataFrame(
        [
            {
                "timestamp": r.timestamp,
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume,
            }
            for r in prices
        ]
    )
    ind_df = pd.DataFrame([dict(timestamp=r.timestamp, **r.values) for r in indicators])
    if not price_df.empty:
        price_df = price_df.sort_values("timestamp").set_index("timestamp")
    if not ind_df.empty:
        ind_df = ind_df.sort_values("timestamp").set_index("timestamp")
    return price_df, ind_df


def run_backtest(db, symbol, start_date, end_date):
    """
    Run a simple backtest using the same logic as the signal engine.
    """
    logger.info(f"Running backtest for {symbol} from {start_date} to {end_date}")
    price_df, ind_df = load_historical_data(db, symbol, start_date, end_date)
    if ind_df.empty:
        logger.warning(f"No indicator data for {symbol} in backtest range.")
        return
    signals = []
    for i in range(1, len(ind_df)):
        window = ind_df.iloc[i - 1 : i + 1]
        ma_signals = detect_ma_crossover(window)
        rsi_signals = detect_rsi_signals(window)
        for sig in ma_signals + rsi_signals:
            signals.append(
                {
                    "timestamp": window.index[-1],
                    "signal_type": sig["signal_type"],
                    "reason": sig["reason"],
                    "values": sig["values"],
                }
            )
    logger.info(f"Backtest for {symbol}: {len(signals)} signals generated.")
    # Placeholder: Add portfolio simulation, P&L, and performance metrics here
    return signals


# Example usage
if __name__ == "__main__":
    db = next(get_db())
    symbol = "AAPL"
    start_date = "2022-01-01"
    end_date = "2022-12-31"
    run_backtest(db, symbol, start_date, end_date)
