from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class SymbolBase(BaseModel):
    symbol: str

class Symbol(SymbolBase):
    id: int
    
    class Config:
        from_attributes = True

class MarketDataBase(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class MarketData(MarketDataBase):
    id: int
    
    class Config:
        from_attributes = True

class SignalBase(BaseModel):
    symbol: str
    timestamp: datetime
    signal_type: str
    details: Optional[Dict[str, Any]] = None
    executed: bool = False
    execution_details: Optional[Dict[str, Any]] = None

class Signal(SignalBase):
    id: int
    
    class Config:
        from_attributes = True 