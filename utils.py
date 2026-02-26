import re
import statistics


def clean_price(raw_price):
    """
    Extract the first valid monetary value from a string.
    """
    if not raw_price:
        return 0.0

    text = raw_price.lower()

    if "free" in text:
        return 0.0

    # find first number like 123 or 123.45
    match = re.search(r"\d+(?:\.\d{1,2})?", text.replace(",", ""))

    if match:
        return float(match.group())

    return 0.0


def calculate_total_price(item_price_text, shipping_text=None, include_shipping=True):
    """
    Returns final price based on include_shipping flag.
    Keeps business logic separate from scraping logic.
    """
    item_price = clean_price(item_price_text)

    if not include_shipping:
        return item_price

    shipping_cost = clean_price(shipping_text) if shipping_text else 0.0

    return item_price + shipping_cost

# Percentile-based pricing (quantile positioning)
# ----------------------------------------------
# We compute P25, P50 (median), and P75 from sold price data.
# Percentiles show where a price sits within the distribution,
# instead of relying only on mean (which is sensitive to outliers).
#
# P25  -> aggressive pricing (faster sale, high liquidity)
# P50  -> fair market equilibrium
# P75  -> premium positioning (slower sale, higher proceeds)
#
# Percentiles are calculated via linear interpolation on the
# sorted sold prices to produce stable values even with small samples.
# All values are based on total buyer cost (item + shipping).
def get_market_stats(price_list):
    if not price_list:
        return None

    sorted_prices = sorted(price_list)
    n = len(sorted_prices)

    def percentile(p):
        k = (n - 1) * (p / 100)
        f = int(k)
        c = min(f + 1, n - 1)
        if f == c:
            return sorted_prices[int(k)]
        d0 = sorted_prices[f] * (c - k)
        d1 = sorted_prices[c] * (k - f)
        return d0 + d1

    return {
        "mean": statistics.mean(price_list),
        "median": statistics.median(price_list),
        "min": sorted_prices[0],
        "max": sorted_prices[-1],
        "p25": percentile(25),
        "p50": percentile(50),  # technically same as median
        "p75": percentile(75),
    }