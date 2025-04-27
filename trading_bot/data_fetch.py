"""
Data Ingestion Module

This module is responsible for fetching daily OHLCV data from Yahoo Finance,
handling rate limits and retries, and saving the data to the database.
"""

# Data ingestion module
import os
import time
import logging
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import yfinance as yf
from sqlalchemy.orm import Session
from trading_bot.db_models import get_db, RawPrice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BACKFILL_CHUNK = os.getenv("YFINANCE_BACKFILL_CHUNK", "30D")

def fetch_daily(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    Fetch daily OHLCV data for a given symbol and date range.
    Returns a DataFrame with timezone-naive index.
    """
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            logger.info(f"Fetching data for {symbol} from {start} to {end}")
            data = yf.download(symbol, start=start, end=end, interval="1d")
            if data.empty:
                logger.warning(f"No data found for {symbol} from {start} to {end}")
                return pd.DataFrame()
            data.index = data.index.tz_localize(None)
            data.columns = [col.lower() for col in data.columns]
            return data
        except Exception as e:
            retry_count += 1
            wait_time = 2 ** retry_count
            logger.error(f"Error fetching data for {symbol}: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    logger.error(f"Failed to fetch data for {symbol} after {max_retries} retries")
    return pd.DataFrame()

def save_to_db(db: Session, symbol: str, data: pd.DataFrame) -> int:
    """
    Save price data to database.
    Returns number of rows inserted.
    """
    if data.empty:
        return 0
    rows_added = 0
    for timestamp, row in data.iterrows():
        existing = db.query(RawPrice).filter(
            RawPrice.symbol == symbol,
            RawPrice.timestamp == timestamp
        ).first()
        if not existing:
            price = RawPrice(
                symbol=symbol,
                timestamp=timestamp,
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume']
            )
            db.add(price)
            rows_added += 1
    if rows_added > 0:
        db.commit()
        logger.info(f"Added {rows_added} new records for {symbol}")
    return rows_added

def backfill_data(db: Session, symbol: str, start_date: str, end_date: str = None):
    """
    Backfill historical data in chunks to avoid API limits.
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    current = start
    total_records = 0
    while current < end:
        next_chunk = current + pd.Timedelta(BACKFILL_CHUNK)
        if next_chunk > end:
            next_chunk = end
        chunk_start = current.strftime("%Y-%m-%d")
        chunk_end = next_chunk.strftime("%Y-%m-%d")
        data = fetch_daily(symbol, chunk_start, chunk_end)
        records_added = save_to_db(db, symbol, data)
        total_records += records_added
        current = next_chunk
        time.sleep(1)
    logger.info(f"Backfill complete for {symbol}. Added {total_records} records total.")

def update_latest(db: Session, symbols: list):
    """
    Update database with the latest data for multiple symbols.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    for symbol in symbols:
        latest = db.query(RawPrice).filter(
            RawPrice.symbol == symbol
        ).order_by(RawPrice.timestamp.desc()).first()
        if latest:
            start_date = (latest.timestamp + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        if start_date < today:
            data = fetch_daily(symbol, start_date, today)
            save_to_db(db, symbol, data)

# Example usage
if __name__ == "__main__":
    db = next(get_db())
    symbol = "AAPL"
    backfill_data(db, symbol, "2023-01-01", "2023-02-01")
    # Regular update of latest data
    update_latest(db, ["AAPL"]) 