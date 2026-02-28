import re
import statistics

def clean_price(raw_price):
    """Extract first numeric amount (handles 'Free', avoids digit-concat disasters)."""
    if not raw_price:
        return 0.0

    text = raw_price.lower()
    if "free" in text:
        return 0.0

    m = re.search(r"\d+(?:\.\d{1,2})?", text.replace(",", ""))
    return float(m.group()) if m else 0.0


def calculate_total_price(item_price_text, shipping_text=None, include_shipping=True):
    item_price = clean_price(item_price_text)
    if not include_shipping:
        return item_price
    shipping_cost = clean_price(shipping_text) if shipping_text else 0.0
    return item_price + shipping_cost


def get_trimmed_mean(price_list, trim_ratio=0.10):
    if not price_list:
        return None
    sorted_prices = sorted(price_list)
    n = len(sorted_prices)
    trim = int(n * trim_ratio)

    # If too small, fall back to mean
    if trim == 0 or (n - 2 * trim) <= 0:
        return statistics.mean(sorted_prices)

    trimmed = sorted_prices[trim:n - trim]
    return statistics.mean(trimmed)


def get_market_stats(price_list, trim_ratio=0.10):
    if not price_list:
        return None

    sorted_prices = sorted(price_list)
    n = len(sorted_prices)

    def percentile(p):
        k = (n - 1) * (p / 100)
        f = int(k)
        c = min(f + 1, n - 1)
        if f == c:
            return sorted_prices[f]
        return sorted_prices[f] * (c - k) + sorted_prices[c] * (k - f)

    return {
        "mean": statistics.mean(price_list),
        "trimmed_mean": get_trimmed_mean(price_list, trim_ratio),
        "median": statistics.median(price_list),
        "min": sorted_prices[0],
        "max": sorted_prices[-1],
        "p25": percentile(25),
        "p50": percentile(50),
        "p75": percentile(75),
    }


def estimate_net_proceeds(gross_price, fee_rate=0.1325, fixed_fee=0.0):
    """
    Rough eBay net proceeds estimator (not exact):
    net = gross - fee_rate*gross - fixed_fee
    """
    return gross_price * (1 - fee_rate) - fixed_fee