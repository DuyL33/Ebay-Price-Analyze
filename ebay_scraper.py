import re
from utils import clean_price, get_market_stats
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ebay_advanced_analysis(search_query, condition="used", limit=20):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    # options.add_argument("--headless") # Recommendation: Run headless for faster QA testing
    
    driver = webdriver.Chrome(options=options)

    # Building the URL with SOLD and COMPLETED filters
    cond_code = "1000" if condition.lower() == "new" else "3000"
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1&LH_ItemCondition={cond_code}"
    
    driver.get(search_url)

    try:
        # 1. Wait for the results to inject into the DOM
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "srp-results")))
        results = driver.find_elements(By.CSS_SELECTOR, ".srp-results .s-card")
        
        raw_prices = []
        for item in results[:limit]:
            try:
                # 2. Extract raw text only
                price_text = item.find_element(By.CLASS_NAME, "s-card__price").text
                # 3. Use your imported utility to clean the data
                raw_prices.append(clean_price(price_text))
            except Exception as e:
                # In QA, we often log errors rather than just 'passing'
                continue

        # 4. Use your imported utility to calculate stats
        stats = get_market_stats(raw_prices)

        if stats:
            print(f"\n--- Market Report: {search_query.upper()} ({condition.upper()}) ---")
            print(f"Sample Size: {len(raw_prices)} sold items")
            print(f"Lowest:  ${stats['min']:.2f}")
            print(f"Highest: ${stats['max']:.2f}")
            print(f"Mean:    ${stats['mean']:.2f}")
            print(f"Median:  ${stats['median']:.2f}")
        else:
            print("Validation Failed: No price data could be processed.")

    finally:
        driver.quit()

if __name__ == "__main__":
    ebay_advanced_analysis("LEGO Star Wars: The Mandalorian N-1 Starfighter (75325)", condition="used", limit=50)