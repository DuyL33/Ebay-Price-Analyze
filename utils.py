import re
import statistics

def clean_price(raw_price):
    # Standard QA logic: Handle ranges and clean symbols
    price_strip = raw_price.split('to')[0]
    clean_p = re.sub(r'[^\d.]', '', price_strip)
    return float(clean_p) if clean_p else 0.0

def get_market_stats(price_list):
    if not price_list:
        return None
    return {
        "mean": statistics.mean(price_list),
        "median": statistics.median(price_list),
        "min": min(price_list),
        "max": max(price_list)
    }