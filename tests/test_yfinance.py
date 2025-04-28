import yfinance as yf
import pandas as pd

symbol = "AAPL"
start = "2023-01-01"
end = "2023-02-01"

print(f"Fetching {symbol} from {start} to {end}")
data = yf.download(symbol, start=start, end=end, interval="1d")
print(data)
if data.empty:
    print("No data returned!")
else:
    print(f"Fetched {len(data)} rows.") 