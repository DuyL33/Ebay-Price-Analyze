import re
import statistics
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ebay_advanced_analysis(search_query, condition="used", limit=20):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    # Filtering for SOLD and COMPLETED listings
    cond_code = "1000" if condition.lower() == "new" else "3000"
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1&LH_ItemCondition={cond_code}"
    
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "srp-results")))
        results = driver.find_elements(By.CSS_SELECTOR, ".srp-results .s-card")
        
        prices = []
        for item in results[:limit]:
            try:
                # Use your discovered class names here
                price_text = item.find_element(By.CLASS_NAME, "s-card__price").text
                # Extract numbers only, handling "to" ranges by taking the first number
                clean_p = float(re.sub(r'[^\d.]', '', price_text.split('to')[0]))
                prices.append(clean_p)
            except:
                continue

        if len(prices) > 1:
            print(f"\n--- Market Report: {search_query} ({condition.upper()}) ---")
            print(f"Sample Size: {len(prices)} sold items")
            print(f"Lowest:  ${min(prices):.2f}")
            print(f"Highest: ${max(prices):.2f}")
            print(f"Mean:    ${statistics.mean(prices):.2f}")
            print(f"Median:  ${statistics.median(prices):.2f}")
            
            # Seller Advice
            if statistics.median(prices) < statistics.mean(prices):
                print("\nAdvice: A few high-priced sales are inflating the average. Stick to the Median for a quick sale.")
        else:
            print("Not enough data found to calculate statistics.")

    finally:
        driver.quit()

ebay_advanced_analysis("lego 2067 hero factory evo 2.0", condition="used", limit=20)