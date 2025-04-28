def volume_ok(volume, avg_volume, multiplier):
    """
    Check if the current volume meets the threshold.
    Args:
        volume: current volume
        avg_volume: average volume
        multiplier: threshold multiplier
    Returns:
        bool: True if volume is sufficient
    """
    return volume >= avg_volume * multiplier
