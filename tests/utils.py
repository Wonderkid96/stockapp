"""Test utilities and helper functions."""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

def generate_ohlcv_data(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    freq: str = "1D"
) -> pd.DataFrame:
    """Generate synthetic OHLCV data for testing.
    
    Args:
        symbol: The stock symbol
        start_date: Start date for the data
        end_date: End date for the data
        freq: Data frequency (default: "1D")
        
    Returns:
        DataFrame with OHLCV data
    """
    dates = pd.date_range(start=start_date, end=end_date, freq=freq)
    base_price = np.random.uniform(10, 1000)
    
    data = pd.DataFrame({
        'Open': np.random.normal(base_price, base_price * 0.02, len(dates)),
        'High': np.random.normal(base_price * 1.02, base_price * 0.02, len(dates)),
        'Low': np.random.normal(base_price * 0.98, base_price * 0.02, len(dates)),
        'Close': np.random.normal(base_price, base_price * 0.02, len(dates)),
        'Volume': np.random.randint(100000, 1000000, len(dates))
    }, index=dates)
    
    # Ensure High is highest and Low is lowest
    data['High'] = data[['Open', 'High', 'Low', 'Close']].max(axis=1)
    data['Low'] = data[['Open', 'High', 'Low', 'Close']].min(axis=1)
    
    return data

def generate_indicator_data(
    price_data: pd.DataFrame,
    indicator_type: str,
    params: Optional[Dict] = None
) -> pd.DataFrame:
    """Generate synthetic indicator data for testing.
    
    Args:
        price_data: OHLCV price data
        indicator_type: Type of indicator (e.g., 'SMA', 'RSI')
        params: Indicator parameters
        
    Returns:
        DataFrame with indicator values
    """
    if indicator_type == 'SMA':
        window = params.get('window', 20) if params else 20
        return price_data['Close'].rolling(window=window).mean()
    elif indicator_type == 'RSI':
        return pd.Series(np.random.uniform(0, 100, len(price_data)), index=price_data.index)
    else:
        raise ValueError(f"Unsupported indicator type: {indicator_type}")

def generate_signals(
    dates: Union[pd.DatetimeIndex, List[datetime]],
    symbol: str,
    signal_probability: float = 0.2
) -> List[Dict]:
    """Generate synthetic trading signals for testing.
    
    Args:
        dates: List of dates
        symbol: The stock symbol
        signal_probability: Probability of generating a signal for each date
        
    Returns:
        List of signal dictionaries
    """
    signals = []
    for date in dates:
        if np.random.random() < signal_probability:
            signal = {
                'timestamp': date,
                'symbol': symbol,
                'signal_type': np.random.choice(['BUY', 'SELL']),
                'price': np.random.uniform(10, 1000),
                'confidence': np.random.uniform(0.5, 1.0),
                'indicators': {
                    'sma_20': np.random.uniform(10, 1000),
                    'rsi': np.random.uniform(0, 100)
                }
            }
            signals.append(signal)
    return signals

def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame, rtol: float = 1e-5) -> bool:
    """Compare two DataFrames for approximate equality.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        rtol: Relative tolerance for floating point comparison
        
    Returns:
        True if DataFrames are approximately equal
    """
    if df1.shape != df2.shape:
        return False
    if not all(df1.columns == df2.columns):
        return False
    if not all(df1.index == df2.index):
        return False
    return np.allclose(df1.values, df2.values, rtol=rtol) 