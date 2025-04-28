"""Test configuration and constants."""

import os
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/stockapp_test"
)

# Test API configuration
TEST_API_CONFIG = {
    "ALPACA_API_KEY": "test_key",
    "ALPACA_API_SECRET": "test_secret",
    "ALPACA_API_BASE_URL": "https://paper-api.alpaca.markets",
}

# Test symbols
TEST_SYMBOLS = ["AAPL", "MSFT", "GOOGL"]

# Time periods for testing
TEST_TIMEFRAMES = {
    "1D": {"days": 1},
    "1W": {"weeks": 1},
    "1M": {"days": 30},
    "3M": {"days": 90},
    "1Y": {"days": 365},
}

# Test user
TEST_USER = {
    "username": "test_user",
    "email": "test@example.com",
    "password": "test_password",
}

# WebSocket test configuration
WEBSOCKET_TEST_CONFIG = {
    "url": "ws://localhost:8000/ws",
    "timeout": 5,
} 