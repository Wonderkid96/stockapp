"""Tests for data fetching functionality."""

import pytest
from datetime import datetime, timedelta
from stockapp.data_fetch import fetch_daily, fetch_historical_data
from .test_config import TEST_SYMBOLS, TEST_TIMEFRAMES
from .utils import generate_ohlcv_data, compare_dataframes

def test_fetch_daily(mocker):
    """Test daily data fetching for a single symbol."""
    # Arrange
    symbol = TEST_SYMBOLS[0]
    end_date = datetime.now()
    start_date = end_date - timedelta(**TEST_TIMEFRAMES["1D"])
    mock_data = generate_ohlcv_data(symbol, start_date, end_date)
    
    # Mock the yfinance API call
    mock_yf = mocker.patch("yfinance.Ticker")
    mock_yf.return_value.history.return_value = mock_data
    
    # Act
    data = fetch_daily(symbol)
    
    # Assert
    assert data is not None
    assert len(data) > 0
    assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
    assert data.index.is_monotonic_increasing
    assert compare_dataframes(data, mock_data)

def test_fetch_historical_data(mocker):
    """Test historical data fetching with date range."""
    # Arrange
    symbol = TEST_SYMBOLS[0]
    end_date = datetime.now()
    start_date = end_date - timedelta(**TEST_TIMEFRAMES["1M"])
    mock_data = generate_ohlcv_data(symbol, start_date, end_date)
    
    # Mock the yfinance API call
    mock_yf = mocker.patch("yfinance.Ticker")
    mock_yf.return_value.history.return_value = mock_data
    
    # Act
    data = fetch_historical_data(symbol, start_date, end_date)
    
    # Assert
    assert data is not None
    assert len(data) > 0
    assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
    assert data.index.is_monotonic_increasing
    assert data.index[0].date() >= start_date.date()
    assert data.index[-1].date() <= end_date.date()
    assert compare_dataframes(data, mock_data)

def test_fetch_invalid_symbol():
    """Test handling of invalid symbol."""
    with pytest.raises(Exception):
        fetch_daily("INVALID_SYMBOL")

def test_fetch_multiple_symbols(mocker):
    """Test fetching data for multiple symbols."""
    # Arrange
    end_date = datetime.now()
    start_date = end_date - timedelta(**TEST_TIMEFRAMES["1D"])
    mock_data = {
        symbol: generate_ohlcv_data(symbol, start_date, end_date)
        for symbol in TEST_SYMBOLS
    }
    
    # Mock the yfinance API call
    mock_yf = mocker.patch("yfinance.Ticker")
    mock_yf.return_value.history.side_effect = lambda **kwargs: (
        mock_data[kwargs.get('symbol', TEST_SYMBOLS[0])]
    )
    
    # Act
    data_dict = fetch_daily(TEST_SYMBOLS)
    
    # Assert
    assert isinstance(data_dict, dict)
    assert all(symbol in data_dict for symbol in TEST_SYMBOLS)
    for symbol, data in data_dict.items():
        assert data is not None
        assert len(data) > 0
        assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
        assert compare_dataframes(data, mock_data[symbol]) 