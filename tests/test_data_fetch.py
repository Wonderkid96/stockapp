import pytest
from datetime import datetime, timedelta
from trading_bot.data_fetch import fetch_daily, fetch_historical_data

def test_fetch_daily():
    """Test daily data fetching for a single symbol"""
    symbol = "AAPL"
    data = fetch_daily(symbol)
    
    assert data is not None
    assert len(data) > 0
    assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
    assert data.index.is_monotonic_increasing

def test_fetch_historical_data():
    """Test historical data fetching with date range"""
    symbol = "AAPL"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data = fetch_historical_data(symbol, start_date, end_date)
    
    assert data is not None
    assert len(data) > 0
    assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
    assert data.index.is_monotonic_increasing
    assert data.index[0] >= start_date
    assert data.index[-1] <= end_date

def test_fetch_invalid_symbol():
    """Test handling of invalid symbol"""
    with pytest.raises(Exception):
        fetch_daily("INVALID_SYMBOL")

def test_fetch_multiple_symbols():
    """Test fetching data for multiple symbols"""
    symbols = ["AAPL", "MSFT", "GOOGL"]
    data_dict = fetch_daily(symbols)
    
    assert isinstance(data_dict, dict)
    assert all(symbol in data_dict for symbol in symbols)
    for symbol, data in data_dict.items():
        assert data is not None
        assert len(data) > 0
        assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']) 