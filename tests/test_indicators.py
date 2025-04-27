import pytest
import pandas as pd
import numpy as np
from trading_bot.indicators import calculate_sma, calculate_ema, calculate_rsi, calculate_macd

def create_sample_data():
    """Create sample price data for testing"""
    dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
    prices = pd.Series(np.random.normal(100, 5, len(dates)), index=dates)
    return prices

def test_calculate_sma():
    """Test Simple Moving Average calculation"""
    prices = create_sample_data()
    sma = calculate_sma(prices, window=5)
    
    assert sma is not None
    assert len(sma) == len(prices)
    assert sma.index.equals(prices.index)
    assert sma.iloc[4:].notna().all()  # First 4 values should be NaN
    assert sma.iloc[:4].isna().all()

def test_calculate_ema():
    """Test Exponential Moving Average calculation"""
    prices = create_sample_data()
    ema = calculate_ema(prices, window=5)
    
    assert ema is not None
    assert len(ema) == len(prices)
    assert ema.index.equals(prices.index)
    assert ema.iloc[4:].notna().all()  # First 4 values should be NaN
    assert ema.iloc[:4].isna().all()

def test_calculate_rsi():
    """Test Relative Strength Index calculation"""
    prices = create_sample_data()
    rsi = calculate_rsi(prices, window=14)
    
    assert rsi is not None
    assert len(rsi) == len(prices)
    assert rsi.index.equals(prices.index)
    assert rsi.iloc[14:].notna().all()  # First 14 values should be NaN
    assert rsi.iloc[:14].isna().all()
    assert (rsi >= 0).all() and (rsi <= 100).all()  # RSI should be between 0 and 100

def test_calculate_macd():
    """Test MACD calculation"""
    prices = create_sample_data()
    macd, signal, hist = calculate_macd(prices)
    
    assert macd is not None and signal is not None and hist is not None
    assert len(macd) == len(prices)
    assert len(signal) == len(prices)
    assert len(hist) == len(prices)
    assert macd.index.equals(prices.index)
    assert signal.index.equals(prices.index)
    assert hist.index.equals(prices.index)
    
    # Check that MACD line crosses signal line
    assert (hist > 0).any() and (hist < 0).any()

def test_indicator_edge_cases():
    """Test indicator calculations with edge cases"""
    # Empty series
    empty_series = pd.Series([], index=pd.DatetimeIndex([]))
    assert calculate_sma(empty_series, window=5).empty
    assert calculate_ema(empty_series, window=5).empty
    assert calculate_rsi(empty_series, window=14).empty
    assert calculate_macd(empty_series)[0].empty
    
    # Single value
    single_value = pd.Series([100], index=[pd.Timestamp('2023-01-01')])
    assert calculate_sma(single_value, window=5).iloc[0] == 100
    assert calculate_ema(single_value, window=5).iloc[0] == 100
    assert calculate_rsi(single_value, window=14).iloc[0] == 50  # RSI should be 50 for single value 