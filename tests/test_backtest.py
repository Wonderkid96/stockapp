import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from trading_bot.backtest import Backtest, BacktestResult

def create_sample_data():
    """Create sample price data for testing"""
    dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
    data = pd.DataFrame({
        'Open': np.random.normal(150, 5, len(dates)),
        'High': np.random.normal(155, 5, len(dates)),
        'Low': np.random.normal(145, 5, len(dates)),
        'Close': np.random.normal(152, 5, len(dates)),
        'Volume': np.random.randint(1000000, 2000000, len(dates))
    }, index=dates)
    return data

def test_backtest_initialization():
    """Test backtest initialization"""
    backtest = Backtest(initial_cash=10000.0)
    assert backtest is not None
    assert isinstance(backtest, Backtest)
    assert backtest.initial_cash == 10000.0

def test_run_backtest():
    """Test running a backtest"""
    backtest = Backtest(initial_cash=10000.0)
    data = create_sample_data()
    result = backtest.run(data)
    
    assert result is not None
    assert isinstance(result, BacktestResult)
    assert hasattr(result, 'trades')
    assert hasattr(result, 'portfolio_value')
    assert hasattr(result, 'returns')

def test_backtest_results():
    """Test backtest results calculation"""
    backtest = Backtest(initial_cash=10000.0)
    data = create_sample_data()
    result = backtest.run(data)
    
    # Check portfolio value
    assert len(result.portfolio_value) == len(data)
    assert result.portfolio_value.iloc[0] == 10000.0
    assert (result.portfolio_value >= 0).all()
    
    # Check returns
    assert len(result.returns) == len(data)
    assert (result.returns >= -1).all()  # Returns can't be less than -100%
    
    # Check trades
    assert isinstance(result.trades, pd.DataFrame)
    if len(result.trades) > 0:
        assert all(col in result.trades.columns for col in ['entry_time', 'exit_time', 'entry_price', 'exit_price', 'pnl'])

def test_backtest_metrics():
    """Test backtest performance metrics"""
    backtest = Backtest(initial_cash=10000.0)
    data = create_sample_data()
    result = backtest.run(data)
    
    # Check that metrics are calculated
    assert hasattr(result, 'total_return')
    assert hasattr(result, 'sharpe_ratio')
    assert hasattr(result, 'max_drawdown')
    assert hasattr(result, 'win_rate')
    
    # Check metric ranges
    assert result.total_return >= -1  # Can't lose more than 100%
    assert result.max_drawdown >= 0 and result.max_drawdown <= 1
    assert result.win_rate >= 0 and result.win_rate <= 1

def test_backtest_parameters():
    """Test backtest with different parameters"""
    # Test different initial cash
    backtest1 = Backtest(initial_cash=5000.0)
    backtest2 = Backtest(initial_cash=20000.0)
    data = create_sample_data()
    
    result1 = backtest1.run(data)
    result2 = backtest2.run(data)
    
    assert result1.portfolio_value.iloc[0] == 5000.0
    assert result2.portfolio_value.iloc[0] == 20000.0
    
    # Test different position sizes
    backtest3 = Backtest(initial_cash=10000.0, position_size=0.5)  # 50% position size
    result3 = backtest3.run(data)
    
    assert result3.trades['position_size'].iloc[0] == 0.5

def test_backtest_validation():
    """Test backtest input validation"""
    backtest = Backtest(initial_cash=10000.0)
    
    # Test invalid initial cash
    with pytest.raises(ValueError):
        Backtest(initial_cash=-10000.0)
    
    # Test invalid position size
    with pytest.raises(ValueError):
        Backtest(initial_cash=10000.0, position_size=1.5)
    
    # Test invalid data
    invalid_data = pd.DataFrame({
        'Open': [-150.0],  # Invalid negative price
        'High': [155.0],
        'Low': [145.0],
        'Close': [152.0],
        'Volume': [1000000]
    })
    with pytest.raises(ValueError):
        backtest.run(invalid_data)

def test_backtest_comparison():
    """Test comparing different backtest results"""
    backtest1 = Backtest(initial_cash=10000.0)
    backtest2 = Backtest(initial_cash=10000.0)
    data = create_sample_data()
    
    result1 = backtest1.run(data)
    result2 = backtest2.run(data)
    
    # Compare results
    assert isinstance(result1.compare(result2), dict)
    assert 'return_diff' in result1.compare(result2)
    assert 'sharpe_diff' in result1.compare(result2)
    assert 'drawdown_diff' in result1.compare(result2) 