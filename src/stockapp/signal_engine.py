"""
Signal Engine Module

This module is responsible for generating trading signals based on technical indicators,
applying rule-based logic (crossovers, RSI thresholds, etc.), and saving the signals to the database.
"""

# Strategy logic & signal generation
import logging
from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session

from stockapp.db_models import Indicator, Signal, get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_indicator_data(db: Session, symbol: str, days: int = 10) -> pd.DataFrame:
    """
    Get recent indicator data for a symbol.
    """
    query = (
        db.query(Indicator)
        .filter(Indicator.symbol == symbol)
        .order_by(Indicator.timestamp.desc())
        .limit(days)
    )
    result = query.all()
    if not result:
        logger.warning(f"No indicator data found for {symbol}")
        return pd.DataFrame()
    rows = []
    for r in result:
        row = {"timestamp": r.timestamp, "symbol": r.symbol}
        row.update(r.values)
        rows.append(row)
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("timestamp")
        df.set_index("timestamp", inplace=True)
    return df


def detect_ma_crossover(df: pd.DataFrame) -> list:
    """
    Detect moving average crossovers.
    """
    signals = []
    if len(df) < 2:
        return signals
    if "sma_20" in df.columns and "ema_50" in df.columns:
        prev_row = df.iloc[-2]
        curr_row = df.iloc[-1]
        if (
            prev_row["sma_20"] <= prev_row["ema_50"]
            and curr_row["sma_20"] > curr_row["ema_50"]
        ):
            signals.append(
                {
                    "signal_type": "BUY",
                    "reason": "SMA_20_CROSS_ABOVE_EMA_50",
                    "values": {
                        "sma_20": curr_row["sma_20"],
                        "ema_50": curr_row["ema_50"],
                    },
                }
            )
        elif (
            prev_row["sma_20"] >= prev_row["ema_50"]
            and curr_row["sma_20"] < curr_row["ema_50"]
        ):
            signals.append(
                {
                    "signal_type": "SELL",
                    "reason": "SMA_20_CROSS_BELOW_EMA_50",
                    "values": {
                        "sma_20": curr_row["sma_20"],
                        "ema_50": curr_row["ema_50"],
                    },
                }
            )
    return signals


def detect_rsi_signals(df: pd.DataFrame) -> list:
    """
    Detect RSI overbought/oversold conditions.
    """
    signals = []
    if len(df) < 1 or "rsi_14" not in df.columns:
        return signals
    curr_row = df.iloc[-1]
    if curr_row["rsi_14"] < 30:
        signals.append(
            {
                "signal_type": "BUY",
                "reason": "RSI_OVERSOLD",
                "values": {"rsi": curr_row["rsi_14"]},
            }
        )
    elif curr_row["rsi_14"] > 70:
        signals.append(
            {
                "signal_type": "SELL",
                "reason": "RSI_OVERBOUGHT",
                "values": {"rsi": curr_row["rsi_14"]},
            }
        )
    return signals


def save_signals(db: Session, symbol: str, timestamp: datetime, signals: list) -> int:
    """
    Save detected signals to the database.
    """
    if not signals:
        return 0
    count = 0
    for signal_data in signals:
        if not signal_data.get("signal_type") or not signal_data.get("reason"):
            logger.error("Invalid signal data: missing signal_type or reason.")
            continue
        if not signal_data.get("values"):
            logger.warning("Signal data missing values. Skipping.")
            continue
        signal = Signal(
            symbol=symbol,
            timestamp=timestamp,
            signal_type=signal_data["signal_type"],
            details={"reason": signal_data["reason"], "values": signal_data["values"]},
            executed=False,
        )
        db.add(signal)
        count += 1
    db.commit()
    return count


def detect_signals(db: Session, symbols: list):
    """
    Run signal detection for multiple symbols.
    """
    for symbol in symbols:
        logger.info(f"Detecting signals for {symbol}")
        indicator_data = get_indicator_data(db, symbol)
        if indicator_data.empty:
            logger.warning(
                f"No indicator data available for {symbol}, skipping signal detection"
            )
            continue
        latest_timestamp = indicator_data.index[-1]
        existing = (
            db.query(Signal)
            .filter(Signal.symbol == symbol, Signal.timestamp == latest_timestamp)
            .first()
        )
        if existing:
            logger.info(
                f"Signals already exist for {symbol} at {latest_timestamp}, skipping"
            )
            continue
        all_signals = []
        all_signals.extend(detect_ma_crossover(indicator_data))
        all_signals.extend(detect_rsi_signals(indicator_data))
        if all_signals:
            count = save_signals(db, symbol, latest_timestamp, all_signals)
            logger.info(
                f"Detected {count} new signals for {symbol} at {latest_timestamp}"
            )
        else:
            logger.info(f"No signals detected for {symbol} at {latest_timestamp}")


# Example usage
if __name__ == "__main__":
    db = next(get_db())
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    detect_signals(db, symbols)
