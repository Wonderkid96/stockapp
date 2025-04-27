"""
Indicator Engine Module

This module is responsible for calculating technical indicators (SMA, EMA, RSI, MACD, etc.)
from historical price data and storing the results in the database.
"""

# Technical indicator computations
import logging
import pandas as pd
import pandas_ta as ta
from sqlalchemy.orm import Session
from trading_bot.db_models import get_db, RawPrice, Indicator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_price_data(db: Session, symbol: str, days: int = 200) -> pd.DataFrame:
    """
    Get historical price data for a symbol from the database.
    """
    query = db.query(RawPrice).filter(
        RawPrice.symbol == symbol
    ).order_by(RawPrice.timestamp.desc()).limit(days)
    result = query.all()
    if not result:
        logger.warning(f"No price data found for {symbol}")
        return pd.DataFrame()
    data = pd.DataFrame([
        {
            'timestamp': r.timestamp,
            'open': r.open,
            'high': r.high,
            'low': r.low,
            'close': r.close,
            'volume': r.volume
        } for r in result
    ])
    data = data.sort_values('timestamp')
    data.set_index('timestamp', inplace=True)
    return data

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators on price data.
    """
    if df.empty:
        return df
    if 'close' not in df.columns:
        logger.error("Required column 'close' not found in DataFrame.")
        return df
    if df['close'].isna().any():
        logger.warning("NaN values found in 'close' column. Filling with forward fill.")
        df['close'] = df['close'].fillna(method='ffill')
    df['sma_20'] = ta.sma(df['close'], length=20)
    df['ema_50'] = ta.ema(df['close'], length=50)
    df['rsi_14'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'])
    df = pd.concat([df, macd], axis=1)
    bbands = ta.bbands(df['close'])
    df = pd.concat([df, bbands], axis=1)
    return df

def save_indicators_to_db(db: Session, symbol: str, df: pd.DataFrame) -> int:
    """
    Save calculated indicators to the database.
    """
    if df.empty:
        return 0
    rows_added = 0
    indicator_columns = [col for col in df.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
    for timestamp, row in df.iterrows():
        if row[indicator_columns].isna().all():
            continue
        existing = db.query(Indicator).filter(
            Indicator.symbol == symbol,
            Indicator.timestamp == timestamp
        ).first()
        indicators_dict = {col: float(row[col]) for col in indicator_columns if not pd.isna(row[col])}
        if existing:
            existing.values = indicators_dict
            db.add(existing)
        else:
            indicator = Indicator(
                symbol=symbol,
                timestamp=timestamp,
                values=indicators_dict
            )
            db.add(indicator)
            rows_added += 1
    db.commit()
    return rows_added

def update_indicators(db: Session, symbols: list):
    """
    Update indicators for multiple symbols.
    """
    for symbol in symbols:
        logger.info(f"Updating indicators for {symbol}")
        price_data = get_price_data(db, symbol)
        if price_data.empty:
            logger.warning(f"No price data available for {symbol}, skipping indicator calculation")
            continue
        with_indicators = calculate_indicators(price_data)
        rows_added = save_indicators_to_db(db, symbol, with_indicators)
        logger.info(f"Updated indicators for {symbol}, added {rows_added} new records")

# Example usage
if __name__ == "__main__":
    db = next(get_db())
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    update_indicators(db, symbols) 