"""
Database Models Module

This module defines the SQLAlchemy ORM models for the trading bot,
including tables for raw prices, indicators, and signals.
"""

# SQLAlchemy ORM definitions
import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class RawPrice(Base):
    __tablename__ = "raw_prices"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('symbol', 'timestamp', name='uix_raw_prices'),)

class Indicator(Base):
    __tablename__ = "indicators"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    values = Column(JSON, nullable=False)
    __table_args__ = (UniqueConstraint('symbol', 'timestamp', name='uix_indicators'),)

class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    signal_type = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    executed = Column(Boolean, default=False, index=True)
    execution_details = Column(JSON, nullable=True)

def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Yield a new database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 