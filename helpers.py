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


def extract_title_from_card(card):
    """
    Get listing title from card. eBay commonly uses .s-card__title.
    Fallback: scan for the longest non-empty line as a last resort.
    """
    # Primary selector
    try:
        t = card.find_element(By.CSS_SELECTOR, ".s-card__title").text.strip()
        if t:
            return t
    except Exception:
        pass

    # Fallback heuristic
    best = ""
    try:
        for el in card.find_elements(By.CSS_SELECTOR, "span, div"):
            text = el.text.strip()
            if len(text) > len(best):
                best = text
    except Exception:
        pass
    return best


def extract_url_from_card(card):
    """
    Extract URL from the main link in the card.
    """
    try:
        a = card.find_element(By.CSS_SELECTOR, "a.s-card__link")
        href = a.get_attribute("href")
        return href
    except Exception:
        return None