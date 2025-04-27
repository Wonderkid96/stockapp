import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from trading_bot.signal_engine import SignalEngine, SignalType

def create_sample_indicators():
    """Create sample indicator data for testing"""
    dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
    data = pd.DataFrame({
        'sma_20': np.random.normal(100, 5, len(dates)),
        'sma_50': np.random.normal(100, 5, len(dates)),
        'rsi': np.random.uniform(0, 100, len(dates)),
        'macd': np.random.normal(0, 2, len(dates)),
        'macd_signal': np.random.normal(0, 2, len(dates))
    }, index=dates)
    return data

def test_signal_engine_initialization():
    """Test signal engine initialization"""
    engine = SignalEngine()
    assert engine is not None
    assert isinstance(engine, SignalEngine)

def test_generate_signals():
    """Test signal generation from indicators"""
    engine = SignalEngine()
    indicators = create_sample_indicators()
    signals = engine.generate_signals(indicators)
    
    assert signals is not None
    assert isinstance(signals, pd.DataFrame)
    assert 'signal_type' in signals.columns
    assert 'timestamp' in signals.columns
    assert 'symbol' in signals.columns
    assert 'strength' in signals.columns

def test_sma_crossover_signal():
    """Test SMA crossover signal generation"""
    engine = SignalEngine()
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    data = pd.DataFrame({
        'sma_20': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'sma_50': [105, 104, 103, 102, 101, 100, 99, 98, 97, 96]
    }, index=dates)
    
    signals = engine.generate_signals(data)
    assert len(signals) > 0
    assert any(signals['signal_type'] == SignalType.BUY)
    assert any(signals['signal_type'] == SignalType.SELL)

def test_rsi_signals():
    """Test RSI-based signal generation"""
    engine = SignalEngine()
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    data = pd.DataFrame({
        'rsi': [30, 25, 20, 15, 10, 90, 85, 80, 75, 70]
    }, index=dates)
    
    signals = engine.generate_signals(data)
    assert len(signals) > 0
    assert any(signals['signal_type'] == SignalType.BUY)  # RSI < 30
    assert any(signals['signal_type'] == SignalType.SELL)  # RSI > 70

def test_macd_signals():
    """Test MACD-based signal generation"""
    engine = SignalEngine()
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    data = pd.DataFrame({
        'macd': [0, 1, 2, 3, 4, 3, 2, 1, 0, -1],
        'macd_signal': [0, 0, 1, 2, 3, 4, 3, 2, 1, 0]
    }, index=dates)
    
    signals = engine.generate_signals(data)
    assert len(signals) > 0
    assert any(signals['signal_type'] == SignalType.BUY)  # MACD crosses above signal
    assert any(signals['signal_type'] == SignalType.SELL)  # MACD crosses below signal

def test_signal_strength():
    """Test signal strength calculation"""
    engine = SignalEngine()
    indicators = create_sample_indicators()
    signals = engine.generate_signals(indicators)
    
    assert 'strength' in signals.columns
    assert (signals['strength'] >= 0).all()
    assert (signals['strength'] <= 1).all()

def test_signal_validation():
    """Test signal validation logic"""
    engine = SignalEngine()
    indicators = create_sample_indicators()
    signals = engine.generate_signals(indicators)
    
    # Check that signals have required fields
    required_fields = ['timestamp', 'symbol', 'signal_type', 'strength']
    assert all(field in signals.columns for field in required_fields)
    
    # Check that signal types are valid
    valid_types = [SignalType.BUY, SignalType.SELL]
    assert all(signal_type in valid_types for signal_type in signals['signal_type']) 