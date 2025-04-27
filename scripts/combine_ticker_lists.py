# Combine S&P 500 and NASDAQ-100 ticker lists into all_tickers.txt
data_dir = 'data'
sp500_file = f'{data_dir}/tickers.txt'
nasdaq_file = f'{data_dir}/nasdaq100.txt'
combined_file = f'{data_dir}/all_tickers.txt'

with open(sp500_file) as f:
    sp500 = set(line.strip() for line in f if line.strip())
with open(nasdaq_file) as f:
    nasdaq = set(line.strip() for line in f if line.strip())

combined = sorted(sp500 | nasdaq)

with open(combined_file, 'w') as f:
    for ticker in combined:
        f.write(f"{ticker}\n")

print(f"Combined universe: {len(combined)} unique tickers written to {combined_file}.") 