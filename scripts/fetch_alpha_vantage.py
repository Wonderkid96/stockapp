from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import time
import os

API_KEY = 'EDD8RUCO3CM1VAP3'  # <-- Replace with your real key

def load_tickers(filename='data/etoro_tickers.txt'):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip()]

TICKERS = load_tickers()

# Alpha Vantage free tier: 5 requests per minute
RATE_LIMIT = 5
SLEEP_TIME = 60 / RATE_LIMIT

ts = TimeSeries(key=API_KEY, output_format='pandas')

for ticker in TICKERS:
    print(f'Fetching data for {ticker}...')
    try:
        data, meta = ts.get_daily(symbol=ticker, outputsize='full')
        data = data.sort_index()  # Oldest to newest
        filename = os.path.join('data', f'{ticker}_alpha_vantage.csv')
        data.to_csv(filename)
        print(f'Saved {filename} ({len(data)} rows)')
    except Exception as e:
        print(f'Error fetching {ticker}:', e)
    time.sleep(SLEEP_TIME)

print('Done fetching all tickers.') 