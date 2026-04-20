import re

WATCH_STOPWORDS = {
    "used", "watch", "automatic", "mens", "men", "unworn", "preowned",
    "pre-owned", "wristwatch", "dial", "brand", "new"
}

WATCH_VARIANT_WORDS = {
    "white", "black", "blue", "green", "silver", "gold", "red", "cream",
    "38mm", "39mm", "40mm", "41mm", "42mm", "43mm", "44mm"
}

LEGO_STOPWORDS = {
    "used", "lego", "set", "building", "toy", "new"
}

LEGO_VARIANT_WORDS = {
    "sealed", "complete", "incomplete", "retired", "misb"
}


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9.\s]", " ", text)
    return text.split()


def extract_reference_tokens(tokens, category="watch"):
    """
    Reference-like tokens:
    - watch refs: snk803, srpc41k1
    - omega refs: 310.30.42.50.04.001
    - lego set numbers: 10265, 75367
    """
    refs = []
    for token in tokens:
        if "." in token and any(c.isdigit() for c in token):
            refs.append(token)
        elif any(c.isdigit() for c in token) and any(c.isalpha() for c in token):
            refs.append(token)
        elif category == "lego" and token.isdigit() and len(token) >= 4:
            refs.append(token)
    return refs


def extract_variant_tokens(tokens, variant_words):
    return [t for t in tokens if t in variant_words]


def extract_core_words(tokens, stopwords, variant_words):
    core = []
    for token in tokens:
        if token in stopwords:
            continue
        if token in variant_words:
            continue
        if token.isdigit():
            continue
        if any(c.isdigit() for c in token):
            continue
        if len(token) >= 3:
            core.append(token)
    return core


def match_title(title, query, category="watch"):
    """
    Strict matching logic by category:
    1. Reference numbers must match if query contains them
    2. Variant words must match if query contains them
    3. Require decent overlap on core words
    """

    if not title or not query:
        return False

    if category == "lego":
        stopwords = LEGO_STOPWORDS
        variant_words = LEGO_VARIANT_WORDS
    else:
        stopwords = WATCH_STOPWORDS
        variant_words = WATCH_VARIANT_WORDS

    title_tokens = set(normalize_text(title))
    query_tokens = normalize_text(query)

    query_refs = extract_reference_tokens(query_tokens, category=category)
    query_variants = extract_variant_tokens(query_tokens, variant_words)
    query_core = extract_core_words(query_tokens, stopwords, variant_words)

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
    if query_core:
        overlap = sum(1 for token in query_core if token in title_tokens)
        required_overlap = max(1, len(query_core) // 2)
        if overlap < required_overlap:
            return False

    return True