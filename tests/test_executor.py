import pytest
from datetime import datetime
from trading_bot.executor import Executor, OrderType, OrderStatus
from trading_bot.signal_engine import SignalType

def create_sample_signal():
    """Create a sample trading signal for testing"""
    return {
        'timestamp': datetime.now(),
        'symbol': 'AAPL',
        'signal_type': SignalType.BUY,
        'strength': 0.8,
        'price': 150.0
    }

def test_executor_initialization():
    """Test executor initialization"""
    executor = Executor(paper_trading=True)
    assert executor is not None
    assert isinstance(executor, Executor)
    assert executor.paper_trading is True

def test_order_creation():
    """Test order creation from signal"""
    executor = Executor(paper_trading=True)
    signal = create_sample_signal()
    order = executor.create_order(signal)
    
    assert order is not None
    assert order['symbol'] == signal['symbol']
    assert order['type'] == OrderType.MARKET
    assert order['side'] == 'buy'
    assert order['qty'] > 0
    assert order['status'] == OrderStatus.PENDING

def test_order_execution():
    """Test order execution"""
    executor = Executor(paper_trading=True)
    signal = create_sample_signal()
    order = executor.create_order(signal)
    executed_order = executor.execute_order(order)
    
    assert executed_order is not None
    assert executed_order['status'] == OrderStatus.FILLED
    assert 'executed_price' in executed_order
    assert 'executed_time' in executed_order

def test_cash_management():
    """Test cash management and position sizing"""
    executor = Executor(paper_trading=True, initial_cash=10000.0)
    signal = create_sample_signal()
    order = executor.create_order(signal)
    
    # Check that order quantity is within cash limits
    max_possible_qty = 10000.0 / signal['price']
    assert order['qty'] <= max_possible_qty
    
    # Execute order and check cash balance
    executed_order = executor.execute_order(order)
    remaining_cash = executor.get_cash_balance()
    assert remaining_cash >= 0
    assert remaining_cash <= 10000.0

def test_multiple_orders():
    """Test handling multiple orders"""
    executor = Executor(paper_trading=True, initial_cash=10000.0)
    signals = [
        create_sample_signal(),
        create_sample_signal(),
        create_sample_signal()
    ]
    
    orders = [executor.create_order(signal) for signal in signals]
    executed_orders = [executor.execute_order(order) for order in orders]
    
    assert len(executed_orders) == len(signals)
    assert all(order['status'] == OrderStatus.FILLED for order in executed_orders)
    
    # Check that cash balance is properly updated
    remaining_cash = executor.get_cash_balance()
    assert remaining_cash >= 0
    assert remaining_cash <= 10000.0

def test_order_validation():
    """Test order validation logic"""
    executor = Executor(paper_trading=True)
    signal = create_sample_signal()
    order = executor.create_order(signal)
    
    # Check required fields
    required_fields = ['symbol', 'type', 'side', 'qty', 'status']
    assert all(field in order for field in required_fields)
    
    # Check order type
    assert order['type'] in [OrderType.MARKET, OrderType.LIMIT]
    
    # Check order side
    assert order['side'] in ['buy', 'sell']
    
    # Check quantity
    assert order['qty'] > 0

def test_error_handling():
    """Test error handling in order execution"""
    executor = Executor(paper_trading=True)
    signal = create_sample_signal()
    order = executor.create_order(signal)
    
    # Test invalid order
    invalid_order = order.copy()
    invalid_order['qty'] = -1
    with pytest.raises(ValueError):
        executor.execute_order(invalid_order)
    
    # Test insufficient cash
    executor = Executor(paper_trading=True, initial_cash=1.0)
    with pytest.raises(ValueError):
        executor.create_order(signal) 