"""
Signal Generator Module

This module calculates technical indicators and generates trading signals
based on SMA20/EMA50 crossover and RSI thresholds.
"""

import logging
import pandas as pd
from typing import Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from . import crud, schemas

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Strategy parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
SMA_PERIOD = 20
EMA_PERIOD = 50


def calculate_indicators(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate RSI, SMA20, and EMA50 for the given price data."""
    if len(prices) < max(RSI_PERIOD, SMA_PERIOD, EMA_PERIOD):
        return pd.DataFrame()
    # Calculate price changes
    delta = prices['close'].diff()
    # Calculate RSI
    gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    # Calculate moving averages
    sma20 = prices['close'].rolling(window=SMA_PERIOD).mean()
    ema50 = prices['close'].ewm(span=EMA_PERIOD, adjust=False).mean()
    return pd.DataFrame({
        'close': prices['close'],
        'rsi': rsi,
        'sma20': sma20,
        'ema50': ema50
    })


def check_signal_conditions(
    row: pd.Series,
    prev_row: Optional[pd.Series]
) -> Tuple[bool, Optional[str]]:
    """
    Check if current data point generates a trading signal.
    Returns (signal_exists, signal_type).
    """
    if prev_row is None:
        return False, None
    # Check for SMA/EMA crossover
    prev_sma_above_ema = prev_row['sma20'] > prev_row['ema50']
    curr_sma_above_ema = row['sma20'] > row['ema50']
    # Buy signal conditions
    if (not prev_sma_above_ema and curr_sma_above_ema and
            row['rsi'] < RSI_OVERBOUGHT):
        return True, 'BUY'
    # Sell signal conditions
    if (prev_sma_above_ema and not curr_sma_above_ema and
            row['rsi'] > RSI_OVERSOLD):
        return True, 'SELL'
    return False, None


def generate_signals(db: Session, symbol: str) -> None:
    """Generate trading signals for a symbol based on latest market data."""
    try:
        # Get latest market data
        start_date = datetime.now() - pd.Timedelta(days=100)
        market_data = crud.get_market_data(
            db=db,
            symbol=symbol,
            start_date=start_date
        )
        if not market_data:
            logger.warning(f"No market data found for {symbol}")
            return
        # Convert to DataFrame
        df = pd.DataFrame([
            {'close': data.close, 'timestamp': data.timestamp}
            for data in market_data
        ])
        df.set_index('timestamp', inplace=True)
        # Calculate indicators
        indicators = calculate_indicators(df)
        if indicators.empty:
            msg = f"Not enough data to calculate indicators for {symbol}"
            logger.warning(msg)
            return
        # Check for signals
        for i in range(1, len(indicators)):
            curr_row = indicators.iloc[i]
            prev_row = indicators.iloc[i-1]
            has_signal, signal_type = check_signal_conditions(
                curr_row, prev_row
            )
            if has_signal:
                # Create signal
                signal = schemas.SignalBase(
                    symbol=symbol,
                    timestamp=curr_row.name,
                    signal_type=signal_type,
                    price=curr_row['close'],
                    rsi=curr_row['rsi'],
                    sma20=curr_row['sma20'],
                    ema50=curr_row['ema50']
                )
                # Save signal to database
                crud.create_signal(db, signal)
                # Save indicator values
                indicator = schemas.IndicatorBase(
                    symbol=symbol,
                    timestamp=curr_row.name,
                    rsi=curr_row['rsi'],
                    sma20=curr_row['sma20'],
                    ema50=curr_row['ema50']
                )
                crud.create_indicator(db, indicator)
                msg = f"Generated {signal_type} signal for {symbol}"
                logger.info(f"{msg} at {curr_row.name}")
    except Exception as e:
        logger.error(f"Error generating signals for {symbol}: {e}")
        raise
