"""
Croma Strict Query & Model Matcher Engine
Handles intelligent token matching, strict base model vs variant isolation,
and rigorous accessory filtering.
"""

import re
from typing import Tuple, List, Optional

ACCESSORY_KEYWORDS = {
    "case", "cover", "tempered glass", "screen protector", "screen guard",
    "protective glass", "charging cable", "usb cable", "type-c cable",
    "lightning cable", "charger", "power adapter", "wall adapter", "car charger",
    "power bank", "strap", "watch band", "sleeve", "stylus", "s-pen tip",
    "cleaning kit", "mount", "stand", "car mount", "dock", "skin", "folio",
    "bumper", "back case", "lens protector", "camera protector", "pouch",
    "ear tips", "replacement band", "earbuds", "buds", "tws", "headphone",
    "headphones", "earphone", "earphones", "neckband", "smartwatch", "watch",
    "band", "tablet", "pad", "tab"
}

VARIANT_TAGS = ["pro max", "pro", "max", "plus", "ultra", "fe", "mini", "lite", "fold", "flip"]


def is_accessory_product(title: str) -> bool:
    """Detect if product title indicates an accessory."""
    title_lower = title.lower()
    for acc in ACCESSORY_KEYWORDS:
        # Match whole word or exact phrase
        pattern = r"\b" + re.escape(acc) + r"\b"
        if re.search(pattern, title_lower):
            return True
    return False


def query_requests_accessories(query: str) -> bool:
    """Check if the user explicitly asked for accessories."""
    q_lower = query.lower()
    for acc in ACCESSORY_KEYWORDS:
        if acc in q_lower:
            return True
    return False


def extract_model_specs(text: str) -> dict:
    """Extract model series, number, and variant modifiers from text."""
    text_lower = text.lower()
    info = {
        "is_iphone": bool(re.search(r"\biphone\b", text_lower)),
        "is_galaxy": bool(re.search(r"\b(galaxy|samsung galaxy)\b", text_lower)),
        "is_macbook": bool(re.search(r"\bmacbook\b", text_lower)),
        "is_ipad": bool(re.search(r"\bipad\b", text_lower)),
        "number": None,
        "variant": None,
    }

    # Detect iPhone generation (e.g. 11, 12, 13, 14, 15, 16, 17, 18, SE)
    if info["is_iphone"]:
        gen_m = re.search(r"\biphone\s*(\d{2}|se)\b", text_lower)
        if gen_m:
            info["number"] = gen_m.group(1)

    # Detect Galaxy S or Z series (e.g. S21, S22, S23, S24, S25, Z Fold 6, Z Flip 6)
    if info["is_galaxy"]:
        gal_m = re.search(r"\b([sz]\d{1,2}|fold\s*\d|flip\s*\d)\b", text_lower)
        if gal_m:
            info["number"] = gal_m.group(1).replace(" ", "")

    # Detect MacBook type (Air vs Pro)
    if info["is_macbook"]:
        if "air" in text_lower:
            info["variant"] = "air"
        elif "pro" in text_lower:
            info["variant"] = "pro"

    # Detect modifiers: 'pro max', 'pro', 'plus', 'ultra', 'fe', 'mini'
    # Guard against accessory adjectives like 'ultra hybrid', 'ultra clear', 'pro case'
    is_acc = is_accessory_product(text)
    if not info["variant"]:
        if "pro max" in text_lower:
            info["variant"] = "pro max"
        elif re.search(r"\bpro\b", text_lower) and not (is_acc and re.search(r"\bpro(tective|tection)\b", text_lower)):
            info["variant"] = "pro"
        elif re.search(r"\b(plus|\+)\b", text_lower):
            info["variant"] = "plus"
        elif re.search(r"\bultra\b", text_lower) and not (is_acc and re.search(r"\bultra\s*(hybrid|slim|clear|thin|tough|guard)\b", text_lower)):
            info["variant"] = "ultra"
        elif re.search(r"\bfe\b", text_lower):
            info["variant"] = "fe"
        elif re.search(r"\bmini\b", text_lower):
            info["variant"] = "mini"
        elif re.search(r"\blite\b", text_lower):
            info["variant"] = "lite"

    return info


def is_strict_match(query: str, title: str) -> Tuple[bool, str]:
    """
    Validate whether a product title strictly matches the user's query.
    Returns (is_match: bool, reason: str).
    """
    q_clean = query.strip()
    if not q_clean or q_clean.lower() in ["all", "*", "everything", ""]:
        return True, "wildcard"

    q_lower = q_clean.lower()
    t_lower = title.lower()

    # 1. Accessory check
    wants_acc = query_requests_accessories(q_lower)
    is_acc = is_accessory_product(title)
    if is_acc and not wants_acc:
        return False, "accessory_filtered"

    # 2. Model specification matching for smart devices
    q_info = extract_model_specs(q_lower)
    t_info = extract_model_specs(t_lower)

    # iPhone matching
    if q_info["is_iphone"]:
        if not t_info["is_iphone"]:
            return False, "not_iphone"
        # Generation matching
        if q_info["number"] and t_info["number"] != q_info["number"]:
            return False, f"generation_mismatch (query={q_info['number']}, product={t_info['number']})"
        
        # Variant matching (Base vs Pro vs Pro Max vs Plus)
        q_var = q_info["variant"]
        t_var = t_info["variant"]
        if q_var is None and t_var is not None:
            # Base iPhone queried, but product is Pro / Plus / Pro Max
            return False, f"base_model_queried_found_{t_var}"
        if q_var is not None and t_var != q_var:
            return False, f"variant_mismatch (query={q_var}, product={t_var})"
        return True, "iphone_strict_match"

    # Galaxy matching
    if q_info["is_galaxy"]:
        if not t_info["is_galaxy"]:
            return False, "not_galaxy"
        if q_info["number"] and t_info["number"] != q_info["number"]:
            return False, f"galaxy_model_mismatch"
        q_var = q_info["variant"]
        t_var = t_info["variant"]
        if q_var is None and t_var is not None:
            return False, f"base_galaxy_queried_found_{t_var}"
        if q_var is not None and t_var != q_var:
            return False, f"galaxy_variant_mismatch"
        return True, "galaxy_strict_match"

    # MacBook matching
    if q_info["is_macbook"]:
        if not t_info["is_macbook"]:
            return False, "not_macbook"
        if q_info["variant"] and t_info["variant"] != q_info["variant"]:
            return False, f"macbook_variant_mismatch (query={q_info['variant']}, product={t_info['variant']})"
        return True, "macbook_strict_match"

    # 3. Standard Token Word-Boundary Matching
    # Extract significant alphanumeric keywords (exclude small noise words and generic phone terms)
    noise_words = {
        "in", "for", "with", "and", "the", "a", "an", "at", "by", "from", "to", "on",
        "phone", "phones", "mobile", "mobiles", "smartphone", "smartphones", "handset",
        "handsets", "device", "devices", "5g", "4g", "buy", "online", "best", "new", "under"
    }
    tokens = [w for w in re.findall(r"[a-z0-9]+", q_lower) if w not in noise_words]
    
    if not tokens:
        return True, "empty_tokens"

    for token in tokens:
        pattern = r"\b" + re.escape(token) + r"\b"
        if not re.search(pattern, t_lower):
            return False, f"missing_token_{token}"

    return True, "token_match"
