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


def get_market_stats(price_list):
    if not price_list:
        return None
    return {
        "mean": statistics.mean(price_list),
        "median": statistics.median(price_list),
        "min": min(price_list),
        "max": max(price_list),
    }