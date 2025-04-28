def premarket_scan(data):
    """
    Scan premarket data and return top N tickers by gap% and volume.
    Args:
        data: list of dicts with keys 'symbol', 'gap_pct', 'volume'
    Returns:
        list: top 20 symbols
    """
    sorted_ = sorted(data, key=lambda x: x["gap_pct"], reverse=True)
    return [r["symbol"] for r in sorted_[:20]]
