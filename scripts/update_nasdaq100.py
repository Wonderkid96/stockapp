import requests
import pandas as pd

WIKI_URL = 'https://en.wikipedia.org/wiki/NASDAQ-100'

response = requests.get(WIKI_URL)
df_list = pd.read_html(response.text)
df = df_list[4]  # The NASDAQ-100 table is usually the 5th table

# The column may be named 'Ticker' or 'Company', handle both
if 'Ticker' in df.columns:
    tickers = df['Ticker'].tolist()
else:
    tickers = df.iloc[:, 1].tolist()  # fallback: second column

tickers = [t.replace('.', '-') for t in tickers]

with open('data/nasdaq100.txt', 'w') as f:
    for ticker in tickers:
        f.write(f"{ticker}\n")

print(f"Updated data/nasdaq100.txt with {len(tickers)} NASDAQ-100 tickers.") 