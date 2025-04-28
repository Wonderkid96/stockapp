"""
Pydantic models for data validation and serialization.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class SymbolBase(BaseModel):
    """Base model for symbol data."""
    symbol: str


class Symbol(SymbolBase):
    """Model for symbol data with ID."""
    id: int
    
    class Config:
        from_attributes = True


class MarketDataBase(BaseModel):
    """Base model for market data."""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class MarketData(MarketDataBase):
    """Model for market data with ID."""
    id: int
    
    class Config:
        from_attributes = True


class SignalBase(BaseModel):
    """Base model for trading signals."""
    symbol: str
    timestamp: datetime
    signal_type: str
    details: Optional[Dict[str, Any]] = None
    executed: bool = False
    execution_details: Optional[Dict[str, Any]] = None


class Signal(SignalBase):
    """Model for trading signals with ID and execution status."""
    id: int
    
    class Config:
        from_attributes = True


class IndicatorBase(BaseModel):
    """Base model for technical indicators."""
    symbol: str
    timestamp: datetime
    rsi: float
    sma20: float
    ema50: float


class Indicator(IndicatorBase):
    """Model for technical indicators with ID."""
    id: int
    
    class Config:
        from_attributes = True 