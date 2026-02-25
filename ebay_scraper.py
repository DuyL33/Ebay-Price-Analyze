import re
from utils import clean_price, get_market_stats, calculate_total_price
from helpers import extract_shipping_text_from_card

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def ebay_advanced_analysis(
    search_query: str,
    condition: str = "used",
    limit: int = 20,
    include_shipping: bool = True,
):
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )
    # options.add_argument("--headless")  # optional

    driver = webdriver.Chrome(options=options)

    # SOLD + COMPLETED filters
    cond_code = "1000" if condition.lower() == "new" else "3000"
    search_url = (
        f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}"
        f"&LH_Sold=1&LH_Complete=1&LH_ItemCondition={cond_code}"
    )

    driver.get(search_url)

    try:
        # wait for results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "srp-results"))
        )

        results = driver.find_elements(By.CSS_SELECTOR, ".srp-results .s-card")

        sold_prices = []

        for item in results[:limit]:
            try:
                # item price
                item_price_text = item.find_element(By.CLASS_NAME, "s-card__price").text

                # shipping (optional)
                shipping_text = None
                if include_shipping:
                    shipping_text = extract_shipping_text_from_card(item)

                # total price according to include_shipping flag
                total_price = calculate_total_price(
                    item_price_text=item_price_text,
                    shipping_text=shipping_text,
                    include_shipping=include_shipping,
                )

                # basic validation
                if total_price > 0:
                    sold_prices.append(total_price)

            except Exception:
                continue

        stats = get_market_stats(sold_prices)

        #label = "WITH SHIPPING" if include_shipping else "ITEM ONLY"
        if stats:
            print(
                f"\n--- Market Report: {search_query.upper()} ({condition.upper()}) ---"
            )
            print(f"Sample Size: {len(sold_prices)} sold items")
            print(f"Lowest:  ${stats['min']:.2f}")
            print(f"Highest: ${stats['max']:.2f}")
            print(f"Mean:    ${stats['mean']:.2f}")
            print(f"Median:  ${stats['median']:.2f}")
        else:
            print("Validation Failed: No price data could be processed.")

    finally:
        driver.quit()


if __name__ == "__main__":
    ebay_advanced_analysis(
        "Seiko mini turtle",
        condition="used",
        limit=50,
        include_shipping=False,
    )
    ebay_advanced_analysis(
        "Seiko mini turtle",d
        condition="used",
        limit=50,
        include_shipping=True,
    )

