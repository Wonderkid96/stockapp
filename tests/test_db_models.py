import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from trading_bot.db_models import Base, RawPrice, Indicator, Signal

@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_raw_price_model(db_session):
    """Test RawPrice model"""
    price = RawPrice(
        symbol='AAPL',
        timestamp=datetime.now(),
        open=150.0,
        high=155.0,
        low=145.0,
        close=152.0,
        volume=1000000
    )
    db_session.add(price)
    db_session.commit()
    
    # Query and verify
    saved_price = db_session.query(RawPrice).first()
    assert saved_price is not None
    assert saved_price.symbol == 'AAPL'
    assert saved_price.open == 150.0
    assert saved_price.high == 155.0
    assert saved_price.low == 145.0
    assert saved_price.close == 152.0
    assert saved_price.volume == 1000000

def test_indicator_model(db_session):
    """Test Indicator model"""
    indicator = Indicator(
        symbol='AAPL',
        timestamp=datetime.now(),
        indicator_type='SMA',
        value=150.0,
        parameters={'window': 20}
    )
    db_session.add(indicator)
    db_session.commit()
    
    # Query and verify
    saved_indicator = db_session.query(Indicator).first()
    assert saved_indicator is not None
    assert saved_indicator.symbol == 'AAPL'
    assert saved_indicator.indicator_type == 'SMA'
    assert saved_indicator.value == 150.0
    assert saved_indicator.parameters == {'window': 20}

def test_signal_model(db_session):
    """Test Signal model"""
    signal = Signal(
        symbol='AAPL',
        timestamp=datetime.now(),
        signal_type='BUY',
        strength=0.8,
        executed=False,
        execution_time=None,
        execution_price=None
    )
    db_session.add(signal)
    db_session.commit()
    
    # Query and verify
    saved_signal = db_session.query(Signal).first()
    assert saved_signal is not None
    assert saved_signal.symbol == 'AAPL'
    assert saved_signal.signal_type == 'BUY'
    assert saved_signal.strength == 0.8
    assert saved_signal.executed is False
    assert saved_signal.execution_time is None
    assert saved_signal.execution_price is None

def test_model_relationships(db_session):
    """Test relationships between models"""
    # Create a price
    price = RawPrice(
        symbol='AAPL',
        timestamp=datetime.now(),
        open=150.0,
        high=155.0,
        low=145.0,
        close=152.0,
        volume=1000000
    )
    db_session.add(price)
    
    # Create an indicator based on the price
    indicator = Indicator(
        symbol='AAPL',
        timestamp=datetime.now(),
        indicator_type='SMA',
        value=150.0,
        parameters={'window': 20}
    )
    db_session.add(indicator)
    
    # Create a signal based on the indicator
    signal = Signal(
        symbol='AAPL',
        timestamp=datetime.now(),
        signal_type='BUY',
        strength=0.8,
        executed=False
    )
    db_session.add(signal)
    
    db_session.commit()
    
    # Verify all records were created
    assert db_session.query(RawPrice).count() == 1
    assert db_session.query(Indicator).count() == 1
    assert db_session.query(Signal).count() == 1

def test_model_constraints(db_session):
    """Test model constraints"""
    # Test unique constraint on RawPrice
    price1 = RawPrice(
        symbol='AAPL',
        timestamp=datetime.now(),
        open=150.0,
        high=155.0,
        low=145.0,
        close=152.0,
        volume=1000000
    )
    db_session.add(price1)
    db_session.commit()
    
    # Try to add duplicate price
    price2 = RawPrice(
        symbol='AAPL',
        timestamp=price1.timestamp,  # Same timestamp
        open=151.0,
        high=156.0,
        low=146.0,
        close=153.0,
        volume=1000000
    )
    db_session.add(price2)
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()

def test_model_validation(db_session):
    """Test model validation"""
    # Test invalid price values
    with pytest.raises(ValueError):
        price = RawPrice(
            symbol='AAPL',
            timestamp=datetime.now(),
            open=-150.0,  # Invalid negative price
            high=155.0,
            low=145.0,
            close=152.0,
            volume=1000000
        )
        db_session.add(price)
        db_session.commit()
    
    # Test invalid signal strength
    with pytest.raises(ValueError):
        signal = Signal(
            symbol='AAPL',
            timestamp=datetime.now(),
            signal_type='BUY',
            strength=1.5,  # Invalid strength > 1
            executed=False
        )
        db_session.add(signal)
        db_session.commit() 