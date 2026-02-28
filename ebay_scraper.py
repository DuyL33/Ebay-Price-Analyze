import re
import csv
from datetime import datetime

from utils import get_market_stats, calculate_total_price, estimate_net_proceeds
from helpers import extract_shipping_text_from_card, extract_title_from_card, extract_url_from_card

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def export_to_csv(records, filename):
    fieldnames = ["title", "item_price", "shipping", "total", "url"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k) for k in fieldnames})


def print_extremes(records, k=3):
    """
    Print k cheapest and k most expensive listings based on total.
    """
    if not records:
        return

    sorted_recs = sorted(records, key=lambda r: r["total"])
    lows = sorted_recs[:k]
    highs = sorted_recs[-k:][::-1]

    print("\n--- Lowest Listings ---")
    for r in lows:
        print(f"${r['total']:.2f} | item=${r['item_price']:.2f} ship=${r['shipping']:.2f} | {r['title']}")
        if r.get("url"):
            print(f"  {r['url']}")

    print("\n--- Highest Listings ---")
    for r in highs:
        print(f"${r['total']:.2f} | item=${r['item_price']:.2f} ship=${r['shipping']:.2f} | {r['title']}")
        if r.get("url"):
            print(f"  {r['url']}")


def ebay_advanced_analysis(
    search_query: str,
    condition: str = "used",
    limit: int = 50,
    include_shipping: bool = True,
    trim_ratio: float = 0.10,
    export_csv: bool = True,
    fee_rate: float = 0.1325,
):
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )
    # options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    cond_code = "1000" if condition.lower() == "new" else "3000"
    search_url = (
        f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}"
        f"&LH_Sold=1&LH_Complete=1&LH_ItemCondition={cond_code}"
    )

    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "srp-results"))
        )

        results = driver.find_elements(By.CSS_SELECTOR, ".srp-results .s-card")

        records = []
        totals = []

        for item in results[:limit]:
            try:
                title = extract_title_from_card(item)
                url = extract_url_from_card(item)

                item_price_text = item.find_element(By.CLASS_NAME, "s-card__price").text

                shipping_text = extract_shipping_text_from_card(item) if include_shipping else None

                # Compute totals via utils (parses safely)
                total = calculate_total_price(
                    item_price_text=item_price_text,
                    shipping_text=shipping_text,
                    include_shipping=include_shipping,
                )

                # Split into item + shipping numeric values for record
                # (We compute shipping numeric by total - item_price)
                # Note: if shipping_text is None/Free/pickup, shipping becomes 0
                from utils import clean_price
                item_price = clean_price(item_price_text)
                shipping_val = max(0.0, total - item_price) if include_shipping else 0.0

                # Basic sanity guard (optional; tune per category)
                if total <= 0:
                    continue

                record = {
                    "title": title,
                    "item_price": item_price,
                    "shipping": shipping_val,
                    "total": total,
                    "url": url,
                }
                records.append(record)
                totals.append(total)

            except Exception:
                continue

        stats = get_market_stats(totals, trim_ratio=trim_ratio)

        print(f"\n--- Market Report: {search_query.upper()} ({condition.upper()}) ---")
        print(f"Sample Size: {len(totals)} sold items")
        if not stats:
            print("Validation Failed: No price data could be processed.")
            return

        print(f"Lowest:  ${stats['min']:.2f}")
        print(f"Highest: ${stats['max']:.2f}")
        print(f"Mean:    ${stats['mean']:.2f}")
        print(f"Trimmed Mean: ${stats['trimmed_mean']:.2f}")
        print(f"Median:  ${stats['median']:.2f}")
        print(f"P25:     ${stats['p25']:.2f}")
        print(f"P50:     ${stats['p50']:.2f}")
        print(f"P75:     ${stats['p75']:.2f}")

        # Strategy block (actionable)
        print("\n--- Pricing Recommendation (Total Buyer Cost) ---")
        quick = stats["p25"]
        fair = stats["p50"]
        patient = stats["p75"]
        print(f"Quick Sale (P25):   ${quick:.2f} | est net ~ ${estimate_net_proceeds(quick, fee_rate=fee_rate):.2f}")
        print(f"Fair Market (P50):  ${fair:.2f} | est net ~ ${estimate_net_proceeds(fair, fee_rate=fee_rate):.2f}")
        print(f"Patient (P75):      ${patient:.2f} | est net ~ ${estimate_net_proceeds(patient, fee_rate=fee_rate):.2f}")

        # Extremes view (the “intelligence”)
        # print_extremes(records, k=3)

        # CSV export
        # if export_csv and records:
        #     ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", search_query).strip("_")
        #     filename = f"ebay_{safe_name}_{condition}_{ts}.csv"
        #     export_to_csv(records, filename)
        #     print(f"\nSaved CSV: {filename}")

    finally:
        driver.quit()


if __name__ == "__main__":
    ebay_advanced_analysis(
        "Studio Series 82 Deluxe Class Bumblebee Autobot Ratchet",
        condition="used",
        limit=50,
        include_shipping=False,
        
    )

    ebay_advanced_analysis(
        "Studio Series 80 Deluxe Class Bumblebee Autobot Brawn",
        condition="used",
        limit=50,
        include_shipping=False,
        
    )

    ebay_advanced_analysis(
        "Baiwei TW1029 Megatron",
        condition="used",
        limit=50,
        include_shipping=False,
        
    )

    ebay_advanced_analysis(
        "BAIWEI TW1030 Optimus Prime",
        condition="used",
        limit=10,
        include_shipping=False,
        
    )


