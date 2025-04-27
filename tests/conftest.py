import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from trading_bot.db_models import Base, RawPrice, Indicator, Signal

@pytest.fixture
def db_engine():
    """Create a test database engine"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(db_engine):
    """Create a test database session"""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def sample_price_data():
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

@pytest.fixture
def sample_indicators():
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

@pytest.fixture
def sample_signals():
    """Create sample trading signals for testing"""
    dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
    signals = pd.DataFrame({
        'timestamp': dates,
        'symbol': ['AAPL'] * len(dates),
        'signal_type': np.random.choice(['BUY', 'SELL'], len(dates)),
        'strength': np.random.uniform(0, 1, len(dates)),
        'executed': np.random.choice([True, False], len(dates))
    })
    return signals

@pytest.fixture
def populated_db(db_session, sample_price_data, sample_indicators, sample_signals):
    """Create a database populated with sample data"""
    # Add price data
    for date, row in sample_price_data.iterrows():
        price = RawPrice(
            symbol='AAPL',
            timestamp=date,
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
            volume=row['Volume']
        )
        db_session.add(price)
    
    # Add indicators
    for date, row in sample_indicators.iterrows():
        for indicator_type, value in row.items():
            indicator = Indicator(
                symbol='AAPL',
                timestamp=date,
                indicator_type=indicator_type,
                value=value,
                parameters={'window': 20}
            )
            db_session.add(indicator)
    
    # Add signals
    for _, row in sample_signals.iterrows():
        signal = Signal(
            symbol=row['symbol'],
            timestamp=row['timestamp'],
            signal_type=row['signal_type'],
            strength=row['strength'],
            executed=row['executed']
        )
        db_session.add(signal)
    
    db_session.commit()
    return db_session

@pytest.fixture
def mock_alpaca_api():
    """Create a mock Alpaca API for testing"""
    class MockAlpacaAPI:
        def __init__(self):
            self.orders = []
            self.positions = {}
            self.cash = 10000.0
        
        def submit_order(self, symbol, qty, side, type, time_in_force):
            order = {
                'id': len(self.orders) + 1,
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'type': type,
                'time_in_force': time_in_force,
                'status': 'filled',
                'filled_at': datetime.now(),
                'filled_avg_price': 150.0
            }
            self.orders.append(order)
            return order
        
        def get_position(self, symbol):
            return self.positions.get(symbol)
        
        def get_account(self):
            return {'cash': self.cash}
    
    return MockAlpacaAPI() 