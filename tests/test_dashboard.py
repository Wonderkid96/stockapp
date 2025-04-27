import pytest
from datetime import datetime
import pandas as pd
from trading_bot.dashboard import create_dashboard, update_signals_table, create_candlestick_chart

def test_create_dashboard():
    """Test dashboard creation"""
    app = create_dashboard()
    assert app is not None
    assert hasattr(app, 'layout')
    assert hasattr(app, 'callback')

def test_update_signals_table():
    """Test signals table update"""
    # Create sample signals data
    signals = pd.DataFrame({
        'timestamp': [datetime.now()],
        'symbol': ['AAPL'],
        'signal_type': ['BUY'],
        'strength': [0.8],
        'executed': [False]
    })
    
    # Test table update
    table = update_signals_table(signals)
    assert table is not None
    assert hasattr(table, 'data')
    assert len(table.data) == 1
    assert table.data[0]['symbol'] == 'AAPL'
    assert table.data[0]['signal_type'] == 'BUY'

def test_create_candlestick_chart():
    """Test candlestick chart creation"""
    # Create sample price data
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    data = pd.DataFrame({
        'Open': [150.0, 151.0, 152.0, 153.0, 154.0, 155.0, 156.0, 157.0, 158.0, 159.0],
        'High': [155.0, 156.0, 157.0, 158.0, 159.0, 160.0, 161.0, 162.0, 163.0, 164.0],
        'Low': [145.0, 146.0, 147.0, 148.0, 149.0, 150.0, 151.0, 152.0, 153.0, 154.0],
        'Close': [152.0, 153.0, 154.0, 155.0, 156.0, 157.0, 158.0, 159.0, 160.0, 161.0]
    }, index=dates)
    
    # Create sample signals
    signals = pd.DataFrame({
        'timestamp': [dates[5]],
        'symbol': ['AAPL'],
        'signal_type': ['BUY'],
        'strength': [0.8],
        'executed': [False]
    })
    
    # Test chart creation
    chart = create_candlestick_chart(data, signals)
    assert chart is not None
    assert hasattr(chart, 'data')
    assert len(chart.data) > 0

def test_dashboard_layout():
    """Test dashboard layout components"""
    app = create_dashboard()
    
    # Check that layout contains required components
    layout = app.layout
    assert any(component.type == 'Table' for component in layout.children)
    assert any(component.type == 'Graph' for component in layout.children)

def test_dashboard_callback():
    """Test dashboard callback functionality"""
    app = create_dashboard()
    
    # Check that callback is properly registered
    assert hasattr(app, 'callback')
    assert callable(app.callback)

def test_empty_data_handling():
    """Test handling of empty data"""
    # Test empty signals
    empty_signals = pd.DataFrame(columns=['timestamp', 'symbol', 'signal_type', 'strength', 'executed'])
    table = update_signals_table(empty_signals)
    assert table is not None
    assert len(table.data) == 0
    
    # Test empty price data
    empty_data = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close'])
    chart = create_candlestick_chart(empty_data, empty_signals)
    assert chart is not None
    assert len(chart.data) == 0

def test_data_validation():
    """Test data validation in dashboard components"""
    # Test invalid signals data
    invalid_signals = pd.DataFrame({
        'timestamp': [datetime.now()],
        'symbol': ['AAPL'],
        'signal_type': ['INVALID'],  # Invalid signal type
        'strength': [1.5],  # Invalid strength
        'executed': [False]
    })
    
    with pytest.raises(ValueError):
        update_signals_table(invalid_signals)
    
    # Test invalid price data
    invalid_data = pd.DataFrame({
        'Open': [-150.0],  # Invalid negative price
        'High': [155.0],
        'Low': [145.0],
        'Close': [152.0]
    })
    
    with pytest.raises(ValueError):
        create_candlestick_chart(invalid_data, pd.DataFrame()) 