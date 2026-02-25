from selenium.webdriver.common.by import By


def extract_shipping_text_from_card(card):
    """
    Extract shipping/delivery text from an eBay result card
    using keyword-based detection (robust against CSS changes).
    """
    keywords = ( "delivery")

    for el in card.find_elements(By.CSS_SELECTOR, "span, div"):
        text = el.text.strip()
        if not text:
            continue

        lower_text = text.lower()

        if any(keyword in lower_text for keyword in keywords):
            return text

    return None