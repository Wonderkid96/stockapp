"""
Database CRUD operations.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from . import db_models, schemas


def create_market_data(
    db: Session,
    market_data: schemas.MarketDataBase
) -> db_models.RawPrice:
    """Create a new market data entry."""
    db_market_data = db_models.RawPrice(
        symbol=market_data.symbol,
        timestamp=market_data.timestamp,
        open=market_data.open,
        high=market_data.high,
        low=market_data.low,
        close=market_data.close,
        volume=market_data.volume
    )
    db.add(db_market_data)
    db.commit()
    db.refresh(db_market_data)
    return db_market_data


def get_market_data(
    db: Session,
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[db_models.RawPrice]:
    """Get market data for a symbol within optional date range."""
    query = db.query(db_models.RawPrice).filter(
        db_models.RawPrice.symbol == symbol
    )
    if start_date:
        query = query.filter(db_models.RawPrice.timestamp >= start_date)
    if end_date:
        query = query.filter(db_models.RawPrice.timestamp <= end_date)
    return query.order_by(db_models.RawPrice.timestamp).all()


def create_signal(db: Session, signal: schemas.SignalBase) -> db_models.Signal:
    """Create a new trading signal."""
    db_signal = db_models.Signal(
        symbol=signal.symbol,
        timestamp=signal.timestamp,
        signal_type=signal.signal_type,
        price=signal.price,
        rsi=signal.rsi,
        sma20=signal.sma20,
        ema50=signal.ema50,
        executed=False  # New signals are not executed by default
    )
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    return db_signal


def get_latest_signals(db: Session, limit: int = 20) -> List[db_models.Signal]:
    """Get the latest trading signals."""
    return db.query(db_models.Signal)\
        .order_by(desc(db_models.Signal.timestamp))\
        .limit(limit)\
        .all()


def mark_signal_executed(db: Session, signal_id: int) -> db_models.Signal:
    """Mark a signal as executed."""
    signal = db.query(db_models.Signal).filter(
        db_models.Signal.id == signal_id
    ).first()
    if signal:
        signal.executed = True
        db.commit()
        db.refresh(signal)
    return signal


def create_indicator(
    db: Session,
    indicator: schemas.IndicatorBase
) -> db_models.Indicator:
    """Create a new indicator entry."""
    db_indicator = db_models.Indicator(
        symbol=indicator.symbol,
        timestamp=indicator.timestamp,
        rsi=indicator.rsi,
        sma20=indicator.sma20,
        ema50=indicator.ema50
    )
    db.add(db_indicator)
    db.commit()
    db.refresh(db_indicator)
    return db_indicator


def get_latest_indicator(
    db: Session,
    symbol: str
) -> Optional[db_models.Indicator]:
    """Get the latest indicator values for a symbol."""
    return db.query(db_models.Indicator)\
        .filter(db_models.Indicator.symbol == symbol)\
        .order_by(desc(db_models.Indicator.timestamp))\
        .first()
