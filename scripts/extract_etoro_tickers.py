import pandas as pd

df = pd.read_csv('data/etoro.csv')
# Try to find the column with ticker symbols
possible_cols = [col for col in df.columns if 'symbol' in col.lower() or 'ticker' in col.lower() or 'code' in col.lower()]
if possible_cols:
    col = possible_cols[0]
else:
    col = df.columns[0]  # fallback: first column

tickers = df[col].astype(str).str.upper().unique()

with open('data/etoro_tickers.txt', 'w') as f:
    for ticker in tickers:
        f.write(f"{ticker}\n")

print(f"Extracted {len(tickers)} unique eToro tickers to data/etoro_tickers.txt.") 