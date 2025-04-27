import requests
import pandas as pd

# Wikipedia S&P 500 table URL
WIKI_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

response = requests.get(WIKI_URL)
df_list = pd.read_html(response.text)
df = df_list[0]
tickers = df['Symbol'].tolist()

# Some tickers have dots (e.g., BRK.B) which Alpha Vantage expects as - (BRK-B)
tickers = [t.replace('.', '-') for t in tickers]

with open('data/tickers.txt', 'w') as f:
    for ticker in tickers:
        f.write(f"{ticker}\n")

print(f"Updated data/tickers.txt with {len(tickers)} S&P 500 tickers.") 