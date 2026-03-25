import re

WATCH_STOPWORDS = {
    "used", "watch", "automatic", "mens", "men", "unworn", "preowned",
    "pre-owned", "wristwatch", "dial", "brand", "new"
}

VARIANT_WORDS = {
    "white", "black", "blue", "green", "silver", "gold", "red", "cream",
    "38mm", "39mm", "40mm", "41mm", "42mm", "43mm", "44mm"
}


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9.\s]", " ", text)
    return text.split()


def extract_reference_tokens(tokens):
    """
    Reference-like tokens:
    - contain digits + letters, e.g. snk803, srpc41k1
    - or dot-separated reference numbers, e.g. 310.30.42.50.04.001
    """
    refs = []
    for token in tokens:
        if "." in token and any(c.isdigit() for c in token):
            refs.append(token)
        elif any(c.isdigit() for c in token) and any(c.isalpha() for c in token):
            refs.append(token)
    return refs


def extract_variant_tokens(tokens):
    return [t for t in tokens if t in VARIANT_WORDS]


def extract_core_words(tokens):
    core = []
    for token in tokens:
        if token in WATCH_STOPWORDS:
            continue
        if token in VARIANT_WORDS:
            continue
        if token.isdigit():
            continue
        if any(c.isdigit() for c in token):
            continue
        if len(token) >= 3:
            core.append(token)
    return core


def match_watch_title(title, query):
    """
    Strict watch matching logic:
    1. Brand/core identity must overlap
    2. Reference numbers must match if query contains them
    3. Variant words must match if query contains them
    """

    if not title or not query:
        return False

    title_tokens = set(normalize_text(title))
    query_tokens = normalize_text(query)

    query_refs = extract_reference_tokens(query_tokens)
    query_variants = extract_variant_tokens(query_tokens)
    query_core = extract_core_words(query_tokens)

    # Rule 1: all reference tokens in query must appear in title
    if query_refs:
        for ref in query_refs:
            if ref not in title_tokens:
                return False

    # Rule 2: all explicit variant tokens in query must appear in title
    if query_variants:
        for variant in query_variants:
            if variant not in title_tokens:
                return False

    # Rule 3: require strong overlap on core words
    # Example: omega + speedmaster
    if query_core:
        overlap = sum(1 for token in query_core if token in title_tokens)
        required_overlap = max(1, len(query_core) // 2)
        if overlap < required_overlap:
            return False

    return True