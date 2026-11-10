import re

MODIFIERS = [
    'pro max', 'promax', 'pro', 'max', 'ultra', 'plus', 'neo', 'fe', 'lite',
    'ce', 'r', 'mini', 'fold', 'flip'
]

KNOWN_BRANDS = [
    'apple', 'oneplus', 'one plus', 'samsung', 'poco', 'xiaomi', 'redmi',
    'realme', 'vivo', 'oppo', 'motorola', 'moto', 'iqoo', 'google', 'nothing',
    'honor', 'tecno', 'infinix', 'nokia', 'asus', 'lava'
]

def clean_text(text: str) -> str:
    """Normalize text: lowercase, replace +, normalize punctuation."""
    t = text.lower()
    t = re.sub(r'\+', ' plus ', t)
    t = re.sub(r'[\(\)\[\]\-_,/:;]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def parse_natural_query(query: str):
    raw = clean_text(query)
    
    max_price = None
    min_price = None
    
    # under/below/less than
    budget_m = re.search(r'(?:under|below|less\s+than|<)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand|lakh|l)?\b', raw)
    if budget_m:
        val = float(budget_m.group(1))
        unit = (budget_m.group(2) or '').lower()
        if unit in ['k', 'thousand']:
            val *= 1000
        elif unit in ['l', 'lakh']:
            val *= 100000
        max_price = val
        raw = raw[:budget_m.start()] + ' ' + raw[budget_m.end():]

    above_m = re.search(r'(?:above|more\s+than|>)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand|lakh|l)?\b', raw)
    if above_m:
        val = float(above_m.group(1))
        unit = (above_m.group(2) or '').lower()
        if unit in ['k', 'thousand']:
            val *= 1000
        elif unit in ['l', 'lakh']:
            val *= 100000
        min_price = val
        raw = raw[:above_m.start()] + ' ' + raw[above_m.end():]

    noise_patterns = [
        r'\b\d+\s*gb\s*ram\b', r'\b\d+\s*gb\b', r'\b\d+\s*tb\b',
        r'\b(?:black|white|blue|green|red|purple|gold|silver|yellow|gray|grey|pink|velvet|silk|titanium)\b',
        r'\b(?:phone|mobile|smartphone|handset|best|new|5g|4g)\b'
    ]
    cleaned_query = raw
    for p in noise_patterns:
        cleaned_query = re.sub(p, ' ', cleaned_query)
    cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()

    target_brand = None
    for b in KNOWN_BRANDS:
        pattern = r'\b' + re.escape(b) + r'\b'
        if re.search(pattern, cleaned_query):
            target_brand = b.replace('one plus', 'oneplus')
            cleaned_query = re.sub(pattern, ' ', cleaned_query).strip()
            break

    query_modifiers = set()
    for m in MODIFIERS:
        pattern = r'\b' + re.escape(m) + r'\b'
        if re.search(pattern, cleaned_query):
            query_modifiers.add(m)
            cleaned_query = re.sub(pattern, ' ', cleaned_query)

    model_terms = re.sub(r'\s+', ' ', cleaned_query).strip()
    is_generic = len(model_terms) == 0 and len(query_modifiers) == 0

    return {
        'brand': target_brand,
        'model': model_terms,
        'model_tokens': [t for t in model_terms.split() if t],
        'query_modifiers': query_modifiers,
        'max_price': max_price,
        'min_price': min_price,
        'is_generic': is_generic
    }

def match_exact_model(parsed_query, product_title: str, product_brand: str = '') -> tuple[bool, str]:
    norm_title = clean_text(product_title)
    norm_brand = clean_text(product_brand).replace('one plus', 'oneplus')
    
    # 1. Brand check if target brand specified
    if parsed_query['brand']:
        q_brand = parsed_query['brand']
        if q_brand not in norm_brand and not re.search(r'\b' + re.escape(q_brand) + r'\b', norm_title):
            return False, f"Brand mismatch: expected {q_brand}"

    if parsed_query['is_generic']:
        return True, "Generic search match"

    # 2. Every token in base model must be matched as word boundary in title
    for token in parsed_query['model_tokens']:
        pattern = r'\b' + re.escape(token) + r'\b'
        if not re.search(pattern, norm_title):
            return False, f"Missing model token '{token}'"

    # 3. Every requested modifier MUST be present in title
    for req_mod in parsed_query['query_modifiers']:
        pattern = r'\b' + re.escape(req_mod) + r'\b'
        if not re.search(pattern, norm_title):
            return False, f"Missing requested modifier '{req_mod}'"

    # 4. Disqualify sub-variants NOT in query
    for mod in MODIFIERS:
        if mod not in parsed_query['query_modifiers']:
            # 'pro max' is checked before 'pro' or 'max'
            pattern = r'\b' + re.escape(mod) + r'\b'
            if mod == 'r':
                if re.search(r'\b\d+r\b', norm_title):
                    return False, f"Sub-variant 'R' in title but not requested"
            elif re.search(pattern, norm_title):
                # Special case: if user requested 'pro', do not reject for 'pro', but DO reject for 'pro max'
                if mod == 'max' and 'pro max' in norm_title and 'pro' in parsed_query['query_modifiers']:
                    return False, "Sub-variant 'Pro Max' in title but only 'Pro' requested"
                return False, f"Sub-variant '{mod}' in title but not requested"

    return True, "Exact model match"

# Test cases
tests = [
    ("OnePlus 12", "OnePlus 12 (16GB RAM, 512GB Storage, Silky Black)", True),
    ("OnePlus 12", "OnePlus 12R 5G (16GB RAM, 256GB Storage, Iron Gray)", False),
    ("OnePlus 12", "OnePlus 11 5G (16GB RAM, 256GB Storage, Titan Black)", False),
    ("iPhone 15", "Apple iPhone 15 128GB Black", True),
    ("iPhone 15", "Apple iPhone 15 Pro 128GB Natural Titanium", False),
    ("iPhone 15", "Apple iPhone 15 Pro Max 256GB Blue Titanium", False),
    ("iPhone 15", "Apple iPhone 15 Plus 128GB Pink", False),
    ("iPhone 15", "Apple iPhone 14 128GB Blue", False),
    ("iPhone 15 Pro", "Apple iPhone 15 Pro 128GB Natural Titanium", True),
    ("iPhone 15 Pro", "Apple iPhone 15 Pro Max 256GB Blue Titanium", False),
    ("Poco X6", "POCO X6 5G (Mirror Black, 256 GB) (8 GB RAM)", True),
    ("Poco X6", "POCO X6 Neo 5G (Horizon Blue, 128 GB) (8 GB RAM)", False),
    ("Poco X6", "POCO X6 Pro 5G (Spectre Black, 256 GB) (8 GB RAM)", False),
    ("Poco X6 Neo", "POCO X6 Neo 5G (Horizon Blue, 128 GB) (8 GB RAM)", True),
    ("Samsung S24 Ultra", "Samsung Galaxy S24 Ultra 5G (Titanium Gray, 256 GB)", True),
    ("Samsung S24 Ultra", "Samsung Galaxy S24 Plus 5G (Onyx Black, 256 GB)", False),
    ("Samsung S24 Ultra", "Samsung Galaxy S24 5G (Amber Yellow, 128 GB)", False),
]

all_passed = True
for q, title, expected in tests:
    pq = parse_natural_query(q)
    matched, reason = match_exact_model(pq, title, title.split()[0])
    res = (matched == expected)
    if not res:
        all_passed = False
        print(f"FAILED: Query='{q}' Title='{title}' Expected={expected} Got={matched} ({reason})")
    else:
        print(f"PASSED: Query='{q}' Title='{title[:35]}...' -> {matched}")

print("\nALL TESTS PASSED?", all_passed)
