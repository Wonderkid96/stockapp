def compute_opening_range(highs, lows, minutes):
    """
    Compute the opening range breakout entry and stop.
    Args:
        highs: list of high prices for each minute in the opening range
        lows: list of low prices for each minute in the opening range
        minutes: number of minutes in the opening range
    Returns:
        entry (float): breakout entry price
        stop (float): stop loss price
    """
    opening_high = max(highs[:minutes])
    opening_low = min(lows[:minutes])
    entry = opening_high
    stop = opening_low
    return entry, stop
