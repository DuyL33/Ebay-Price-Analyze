import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import get_market_stats, calculate_total_price, clean_price, remove_outliers_iqr
from helpers import (
    extract_shipping_text_from_card,
    extract_title_from_card,
    extract_url_from_card,
    extract_ebay_item_id,
)
from model_matching import match_watch_title
from db import connect_db, init_db, create_run, save_listings


def ebay_advanced_analysis(
    search_query: str,
    condition: str = "used",
    limit: int = 50,
    include_shipping: bool = True,
    trim_ratio: float = 0.10,
    db_path: str = "market.db",
):
    # --- DB init ---
    conn = connect_db(db_path)
    init_db(conn)
    run_id = create_run(
        conn=conn,
        source="ebay",
        query=search_query,
        condition=condition.lower(),
        include_shipping=include_shipping,
        limit_n=limit,
    )

    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )
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
        cards = driver.find_elements(By.CSS_SELECTOR, ".srp-results .s-card")

        records = []
        totals = []

        for card in cards[:limit]:
            try:
                title = extract_title_from_card(card)

                if not match_watch_title(title, search_query):
                    print(f"Rejected title: {title}")
                    continue
                url = extract_url_from_card(card)
                item_id = extract_ebay_item_id(url)

                item_price_text = card.find_element(By.CLASS_NAME, "s-card__price").text
                shipping_text = extract_shipping_text_from_card(card) if include_shipping else None

                total = calculate_total_price(
                    item_price_text=item_price_text,
                    shipping_text=shipping_text,
                    include_shipping=include_shipping,
                )

                if total <= 0:
                    continue

                item_price = clean_price(item_price_text)
                shipping_val = max(0.0, total - item_price) if include_shipping else 0.0

                records.append(
                    {
                        "item_id": item_id,
                        "title": title,
                        "url": url,
                        "item_price": item_price,
                        "shipping": shipping_val,
                        "total": total,
                    }
                )
                totals.append(total)

            except Exception:
                continue
    
        removed_outliers = remove_outliers_iqr(totals)
        stats = get_market_stats(removed_outliers, trim_ratio=trim_ratio)

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

        inserted = save_listings(
            conn=conn,
            run_id=run_id,
            source="ebay",
            query=search_query,
            condition=condition.lower(),
            records=records,
        )
        print(f"\nDB: saved {inserted} new listings (duplicates ignored). Run ID: {run_id}")

    finally:
        driver.quit()
        conn.close()

