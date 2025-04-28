"""
Trading Bot Package

This package contains modules for a zero-leverage, end-to-end Python trading bot.
It includes data ingestion, indicator calculation, signal generation, backtesting,
live execution, and a FastAPI server with a Dash-based dashboard.
"""

from .db_models import Base, Indicator, RawPrice, SessionLocal, Signal, engine, get_db

__all__ = [
    "RawPrice",
    "Indicator",
    "Signal",
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
]

# Makes this directory a Python package
