import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from trading_bot.app import app
from trading_bot.db_models import Base, RawPrice, Indicator, Signal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)

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

def test_health_check(test_client):
    """Test health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_latest_signals(test_client, db_session):
    """Test getting latest signals"""
    # Create some test signals
    signals = [
        Signal(
            symbol='AAPL',
            timestamp=datetime.now(),
            signal_type='BUY',
            strength=0.8,
            executed=False
        ),
        Signal(
            symbol='MSFT',
            timestamp=datetime.now(),
            signal_type='SELL',
            strength=0.6,
            executed=False
        )
    ]
    for signal in signals:
        db_session.add(signal)
    db_session.commit()
    
    # Test the endpoint
    response = test_client.get("/latest")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(s['symbol'] == 'AAPL' for s in data)
    assert any(s['symbol'] == 'MSFT' for s in data)

def test_websocket_connection(test_client):
    """Test WebSocket connection"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send a test message
        websocket.send_json({"type": "subscribe", "symbol": "AAPL"})
        # Receive response
        response = websocket.receive_json()
        assert response["type"] == "subscribed"
        assert response["symbol"] == "AAPL"

def test_invalid_endpoint(test_client):
    """Test invalid endpoint handling"""
    response = test_client.get("/invalid_endpoint")
    assert response.status_code == 404

def test_get_historical_data(test_client, db_session):
    """Test getting historical data"""
    # Create some test price data
    prices = [
        RawPrice(
            symbol='AAPL',
            timestamp=datetime.now(),
            open=150.0,
            high=155.0,
            low=145.0,
            close=152.0,
            volume=1000000
        ),
        RawPrice(
            symbol='AAPL',
            timestamp=datetime.now(),
            open=151.0,
            high=156.0,
            low=146.0,
            close=153.0,
            volume=1000000
        )
    ]
    for price in prices:
        db_session.add(price)
    db_session.commit()
    
    # Test the endpoint
    response = test_client.get("/historical/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(p['symbol'] == 'AAPL' for p in data)

def test_get_indicators(test_client, db_session):
    """Test getting indicators"""
    # Create some test indicators
    indicators = [
        Indicator(
            symbol='AAPL',
            timestamp=datetime.now(),
            indicator_type='SMA',
            value=150.0,
            parameters={'window': 20}
        ),
        Indicator(
            symbol='AAPL',
            timestamp=datetime.now(),
            indicator_type='RSI',
            value=65.0,
            parameters={'window': 14}
        )
    ]
    for indicator in indicators:
        db_session.add(indicator)
    db_session.commit()
    
    # Test the endpoint
    response = test_client.get("/indicators/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(i['indicator_type'] == 'SMA' for i in data)
    assert any(i['indicator_type'] == 'RSI' for i in data)

def test_error_handling(test_client):
    """Test error handling"""
    # Test invalid symbol
    response = test_client.get("/historical/INVALID_SYMBOL")
    assert response.status_code == 404
    
    # Test invalid date range
    response = test_client.get("/historical/AAPL?start_date=invalid")
    assert response.status_code == 400 