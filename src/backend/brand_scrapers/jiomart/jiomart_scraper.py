"""
JioMart Pro Intelligence Scraper
Production-grade Stealth E-Commerce Engine for jiomart.com
"""

import os
import re
import json
import time
import base64
import random
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Callable

import requests
from bs4 import BeautifulSoup
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("JioMartScraper")

BASE_URL = "https://www.jiomart.com"
DEFAULT_APP_ID = "685945f46c8c7aee3f3af605"
DEFAULT_TOKEN = "TpKw7wD9h"
DEFAULT_PINCODE = "110058"

MODIFIERS = [
    "pro max", "promax", "pro", "max", "ultra", "plus", "neo", "fe", "lite",
    "ce", "r", "mini", "fold", "flip"
]

KNOWN_BRANDS = [
    "apple", "oneplus", "one plus", "samsung", "poco", "xiaomi", "redmi",
    "realme", "vivo", "oppo", "motorola", "moto", "iqoo", "google", "nothing",
    "honor", "tecno", "infinix", "nokia", "asus", "lava", "micromax", "itel"
]

BRAND_PRICE_FLOORS = {
    "apple": 20000.0,
    "oneplus": 12000.0,
    "samsung": 5000.0,
    "poco": 5000.0,
    "realme": 5000.0,
    "vivo": 5000.0,
    "oppo": 5000.0,
    "xiaomi": 5000.0,
    "redmi": 4500.0,
    "iqoo": 8000.0,
    "google": 25000.0,
    "nothing": 15000.0,
    "motorola": 5000.0,
    "moto": 5000.0,
    "feature_phone": 800.0
}

ACCESSORY_KEYWORDS = [
    "case", "cover", "tempered glass", "screen protector", "camera protector",
    "guard", "lens protector", "cable", "charger", "charging adapter", "adapter",
    "power bank", "powerbank", "smartwatch", "fitness band", "smart band",
    "earbuds", "tws", "earphones", "headphone", "neckband", "bluetooth headset",
    "mobile holder", "phone holder", "wall mount", "car mount", "wallet", "mobile wallet",
    "wrist strap", "stylus pen", "apple pencil", "combo folder", "back cover",
    "silicone case", "leather case", "bumper case", "tripod", "gimbal", "charging dock",
    "docking station", "replacement battery", "battery pack", "battery case",
    "housing", "skin", "pouch", "flip cover", "keypad phone battery"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]


def clean_text(text: str) -> str:
    """Normalizes text with spacing standardization for letters and numbers."""
    if not text:
        return ""
    t = str(text).lower()
    t = re.sub(r'\+', ' plus ', t)
    t = re.sub(r'[\(\)\[\]\-_,/:;"]', ' ', t)
    # Standardize letter/number spacing: "m 17" -> "m17", "17 e" -> "17e", "m17 e" -> "m17e"
    t = re.sub(r'\b([a-z])\s+(\d+)', r'\1\2', t)
    t = re.sub(r'(\d+)\s+([a-z])\b', r'\1\2', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


class JioMartScraper:
    def __init__(self, pincode: str = DEFAULT_PINCODE, progress_cb: Optional[Callable[[str, int], None]] = None):
        self.pincode = str(pincode).strip() if pincode else DEFAULT_PINCODE
        self.progress_cb = progress_cb or (lambda msg, pct: None)
        self.session = requests.Session()
        self.app_id = DEFAULT_APP_ID
        self.token = DEFAULT_TOKEN
        self.update_headers()

    def update_headers(self):
        auth = "Bearer " + base64.b64encode(f"{self.app_id}:{self.token}".encode()).decode()
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": BASE_URL + "/",
            "authorization": auth,
            "x-currency-code": "INR",
            "x-location-detail": json.dumps({"country_iso_code": "IN", "pincode": self.pincode})
        })

    def log(self, msg: str, pct: int = -1):
        logger.info(msg)
        self.progress_cb(msg, pct)

    def refresh_app_credentials(self) -> bool:
        """Fetch latest app_id and token from live jiomart.com homepage."""
        try:
            r = self.session.get(BASE_URL + "/", timeout=8)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                for s in soup.find_all("script"):
                    txt = s.text.strip()
                    if txt.startswith("window.APP_DATA"):
                        raw = re.sub(r':\s*undefined\b', ': null', txt[txt.find('=')+1:].strip())
                        data, _ = json.JSONDecoder().raw_decode(raw)
                        cfg = data.get("reduxData", {}).get("configuration", {})
                        app = cfg.get("application", {})
                        new_id = app.get("_id")
                        new_tok = app.get("token")
                        if new_id and new_tok:
                            self.app_id = new_id
                            self.token = new_tok
                            self.update_headers()
                            self.log("Refreshed JioMart app credentials from live homepage", 5)
                            return True
        except Exception as e:
            self.log(f"Credential refresh note: {e}", 5)
        return False

    @staticmethod
    def parse_natural_query(query: str) -> Dict[str, Any]:
        raw = clean_text(query)

        max_price = None
        min_price = None

        budget_m = re.search(r'(?:under|below|less\s+than|<=|<)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand|lakh|l)?\b', raw)
        if budget_m:
            val = float(budget_m.group(1))
            unit = (budget_m.group(2) or '').lower()
            if unit in ['k', 'thousand']:
                val *= 1000
            elif unit in ['l', 'lakh']:
                val *= 100000
            max_price = val
            raw = raw[:budget_m.start()] + ' ' + raw[budget_m.end():]

        above_m = re.search(r'(?:above|more\s+than|>=|>)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand|lakh|l)?\b', raw)
        if above_m:
            val = float(above_m.group(1))
            unit = (above_m.group(2) or '').lower()
            if unit in ['k', 'thousand']:
                val *= 1000
            elif unit in ['l', 'lakh']:
                val *= 100000
            min_price = val
            raw = raw[:above_m.start()] + ' ' + raw[above_m.end():]

        require_5g = bool(re.search(r'\b5g\b', raw))

        noise_patterns = [
            r'\b\d+\s*gb\s*ram\b', r'\b\d+\s*gb\b', r'\b\d+\s*tb\b',
            r'\b(?:black|white|blue|green|red|purple|gold|silver|yellow|gray|grey|pink|velvet|silk|titanium|orange|lavender|violet|charcoal)\b',
            r'\b(?:phones?|mobiles?|smartphones?|handsets?|best|new|5g|4g|dual\s*sim|sim)\b'
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
            "raw_query": query,
            "brand": target_brand,
            "model": model_terms,
            "model_tokens": [t for t in model_terms.split() if t],
            "query_modifiers": query_modifiers,
            "max_price": max_price,
            "min_price": min_price,
            "is_generic": is_generic,
            "require_5g": require_5g
        }

    @staticmethod
    def is_phone_handset(item: Dict[str, Any]) -> Tuple[bool, str]:
        name = item.get("name", "")
        norm_name = clean_text(name)
        attrs = item.get("attributes", {})
        comm = attrs.get("commodity-name", "") if isinstance(attrs, dict) else ""
        norm_comm = clean_text(comm)

        for kw in ACCESSORY_KEYWORDS:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, norm_name) or re.search(pattern, norm_comm):
                return False, f"Accessory keyword detected: '{kw}'"

        brand_info = item.get("brand", {})
        bname = (brand_info.get("name") if isinstance(brand_info, dict) else str(brand_info or "")).lower()
        price_obj = item.get("price", {})
        eff_price = 0.0
        if isinstance(price_obj, dict):
            eff_price = float(price_obj.get("effective", {}).get("min") or 0.0)

        for b_key, floor in BRAND_PRICE_FLOORS.items():
            if b_key in bname:
                if eff_price < floor:
                    return False, f"Price {eff_price} below brand floor for {b_key} ({floor})"
                break
        else:
            if eff_price < BRAND_PRICE_FLOORS["feature_phone"]:
                return False, f"Price {eff_price} below absolute handset floor"

        return True, "Authentic phone handset"

    @staticmethod
    def match_exact_model(parsed_query: Dict[str, Any], item: Dict[str, Any]) -> Tuple[bool, str]:
        title = item.get("name", "")
        norm_title = clean_text(title)
        brand_info = item.get("brand", {})
        bname = (brand_info.get("name") if isinstance(brand_info, dict) else str(brand_info or "")).lower()
        norm_brand = clean_text(bname).replace("one plus", "oneplus")

        if parsed_query["brand"]:
            q_brand = parsed_query["brand"]
            if q_brand not in norm_brand and not re.search(r'\b' + re.escape(q_brand) + r'\b', norm_title):
                return False, f"Brand mismatch: expected {q_brand}"

        if parsed_query["is_generic"]:
            return True, "Generic search match"

        for token in parsed_query["model_tokens"]:
            if token == "galaxy" and (norm_brand == "samsung" or "samsung" in norm_title):
                continue
            pattern = r'\b' + re.escape(token) + r'\b'
            if not re.search(pattern, norm_title):
                return False, f"Missing model token '{token}'"

        for req_mod in parsed_query["query_modifiers"]:
            pattern = r'\b' + re.escape(req_mod) + r'\b'
            if not re.search(pattern, norm_title):
                return False, f"Missing requested modifier '{req_mod}'"

        for mod in MODIFIERS:
            if mod not in parsed_query["query_modifiers"]:
                pattern = r'\b' + re.escape(mod) + r'\b'
                if mod == 'r':
                    if re.search(r'\b\d+r\b', norm_title):
                        return False, "Sub-variant 'R' detected but not requested"
                elif re.search(pattern, norm_title):
                    if mod == 'max' and 'pro max' in norm_title and 'pro' in parsed_query["query_modifiers"]:
                        return False, "Sub-variant 'Pro Max' detected when only 'Pro' requested"
                    return False, f"Sub-variant '{mod}' detected but not requested"

        return True, "Exact model match"

    def normalize_product(self, item: Dict[str, Any], query_str: str) -> Dict[str, Any]:
        title = item.get("name", "").strip()
        brand_obj = item.get("brand", {})
        brand = (brand_obj.get("name") if isinstance(brand_obj, dict) else str(brand_obj or "JioMart")).strip()

        model_name = title
        m_match = re.split(r'\(|\d+\s*gb|\d+\s*tb', title, flags=re.IGNORECASE)
        if m_match and len(m_match[0].strip()) > 3:
            model_name = m_match[0].strip().rstrip(",- ")

        price_obj = item.get("price", {})
        eff_min = 0.0
        mrp_min = 0.0
        if isinstance(price_obj, dict):
            eff_min = float(price_obj.get("effective", {}).get("min") or 0.0)
            mrp_min = float(price_obj.get("marked", {}).get("min") or eff_min)

        price_formatted = f"₹{int(eff_min):,}" if eff_min else "Out of Stock"
        mrp_formatted = f"₹{int(mrp_min):,}" if mrp_min > eff_min else ""

        discount_str = str(item.get("discount") or "")
        if not discount_str and mrp_min > eff_min > 0:
            calc_disc = round(((mrp_min - eff_min) / mrp_min) * 100)
            discount_str = f"{calc_disc}% OFF" if calc_disc > 0 else ""
        elif discount_str and not discount_str.endswith("%") and not "off" in discount_str.lower():
            discount_str = f"{discount_str}% OFF"

        in_stock = item.get("sellable", True) is not False and eff_min > 0
        availability = "In Stock" if in_stock else "Out of Stock"

        rating = item.get("rating")
        review_count = item.get("rating_count") or 0
        rating_val = float(rating) if rating is not None else 4.2

        attrs = item.get("attributes", {})
        specs: List[str] = []
        if isinstance(attrs, dict):
            for k in ["cellular_technology", "ram", "internal-storage", "colour", "battery_capacity", "screen_size_diagonal"]:
                v = attrs.get(k)
                if v:
                    specs.append(str(v).split("-")[-1].strip())

        seen_specs = set()
        clean_specs = []
        for s in specs:
            sc = s.strip()
            if sc and sc.lower() not in seen_specs:
                seen_specs.add(sc.lower())
                clean_specs.append(sc)

        medias = item.get("medias", [])
        image_url = ""
        if isinstance(medias, list) and medias:
            image_url = medias[0].get("url", "")
        if not image_url:
            image_url = "https://www.jiomart.com/assets/version1728470557/smartweb/images/jiomart_default_pdp.svg"

        slug = item.get("slug", "")
        article_id = str(item.get("item_code") or item.get("uid") or item.get("sku_code") or f"jm_{int(time.time()*1000)}")

        if slug and article_id and not slug.endswith(article_id):
            product_url = f"{BASE_URL}/p/digital/{slug}/{article_id}"
        elif slug:
            product_url = f"{BASE_URL}/p/digital/{slug}"
        else:
            clean_q = urllib.parse.quote(query_str or title or "smartphone")
            product_url = f"{BASE_URL}/search?q={clean_q}"

        return {
            "title": title,
            "brand": brand,
            "model": model_name,
            "slug": slug,
            "article_id": article_id,
            "price": price_formatted,
            "price_num": eff_min,
            "mrp": mrp_formatted,
            "mrp_num": mrp_min,
            "discount": discount_str,
            "in_stock": in_stock,
            "availability": availability,
            "rating": rating_val,
            "review_count": review_count,
            "seller": "JioMart Official Store / Express Delivery",
            "specs": clean_specs,
            "image_url": image_url,
            "url": product_url,
            "pincode": self.pincode,
            "scraped_at": datetime.now().isoformat()
        }

    def fetch_page_api(self, query: str, page_no: int = 1, page_size: int = 12) -> List[Dict[str, Any]]:
        """Fetch products directly from JioMart Catalog Application API with smartphone filter."""
        url = f"{BASE_URL}/api/service/application/catalog/v1.0/products"
        params = {
            "q": query,
            "f": "l3_category:smartphones-l3",
            "page_size": page_size,
            "page_no": page_no
        }
        try:
            r = self.session.get(url, params=params, timeout=8)
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", [])
                if items:
                    return items
            elif r.status_code == 401:
                self.log("JioMart authorization token expired. Refreshing...", 15)
                if self.refresh_app_credentials():
                    r2 = self.session.get(url, params=params, timeout=8)
                    if r2.status_code == 200:
                        items = r2.json().get("items", [])
                        if items:
                            return items

            # Fallback without category filter if zero items returned
            params_broad = {"q": query, "page_size": page_size, "page_no": page_no}
            r_broad = self.session.get(url, params=params_broad, timeout=8)
            if r_broad.status_code == 200:
                return r_broad.json().get("items", [])
        except Exception as e:
            self.log(f"JioMart catalog fetch warning: {e}", -1)
        return []

    def scrape_catalog(
        self,
        query: str,
        pages: int = 2,
        in_stock_only: bool = False,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        self.log(f"Initiating JioMart Pro Intelligence Scraper for '{query}' [PIN: {self.pincode}]", 5)
        parsed = self.parse_natural_query(query)

        effective_max_price = max_price if max_price is not None else parsed["max_price"]
        effective_min_price = min_price if min_price is not None else parsed["min_price"]

        if parsed["is_generic"]:
            if parsed.get("require_5g"):
                search_term = "5G Mobile"
            elif parsed.get("brand"):
                search_term = f"{parsed['brand']} phone"
            else:
                search_term = "mobile phones"
        elif parsed["brand"] and parsed["model"]:
            model_str = parsed["model"]
            search_term = f"{parsed['brand']} {model_str}".strip()
        elif parsed["model"]:
            search_term = parsed["model"]
        else:
            search_term = query

        pages = max(1, min(pages, 4))
        raw_items: List[Dict[str, Any]] = []
        seen_slugs_raw = set()

        for p in range(1, pages + 1):
            pct = 15 + int((p / pages) * 55)
            self.log(f"Fetching JioMart catalog page {p}/{pages}...", pct)
            items = self.fetch_page_api(search_term, page_no=p, page_size=12)
            if not items and search_term != query:
                items = self.fetch_page_api(query, page_no=p, page_size=12)

            for it in items:
                slug = it.get("slug")
                if slug and slug not in seen_slugs_raw:
                    seen_slugs_raw.add(slug)
                    raw_items.append(it)

            if len(items) < 12 and p > 1:
                break

        self.log(f"Captured {len(raw_items)} raw listings. Running handset authenticity & model isolation...", 75)

        exact_model_products: List[Dict[str, Any]] = []
        all_visible_handsets: List[Dict[str, Any]] = []
        seen_slugs = set()

        for item in raw_items:
            slug = item.get("slug")
            if slug and slug in seen_slugs:
                continue
            if slug:
                seen_slugs.add(slug)

            is_phone, _ = self.is_phone_handset(item)
            if not is_phone:
                continue

            prod = self.normalize_product(item, query)

            if effective_max_price is not None and prod["price_num"] > effective_max_price:
                continue
            if effective_min_price is not None and prod["price_num"] < effective_min_price:
                continue
            if in_stock_only and not prod["in_stock"]:
                continue

            all_visible_handsets.append(prod)

            matches_model, _ = self.match_exact_model(parsed, item)
            if matches_model:
                exact_model_products.append(prod)

        if exact_model_products:
            valid_products = exact_model_products
            self.log(f"Exact model isolation: {len(valid_products)} matching variants identified on JioMart.", 90)
        elif all_visible_handsets:
            valid_products = all_visible_handsets
            self.log(f"Surfacing {len(valid_products)} authentic phone handsets on JioMart for '{query}'.", 90)
        elif parsed.get("brand"):
            # Brand was requested but specific model was out of stock or only covers were returned.
            # Perform intelligent fallback to brand handsets so user never gets 0 results.
            fallback_term = f"{parsed['brand']} phone"
            self.log(f"No direct model handsets in stock. Surfacing authentic {parsed['brand'].title()} handsets...", 85)
            fallback_items = self.fetch_page_api(fallback_term, page_no=1, page_size=12)
            fallback_handsets = []
            for item in fallback_items:
                is_phone, _ = self.is_phone_handset(item)
                if is_phone:
                    fallback_handsets.append(self.normalize_product(item, query))
            valid_products = fallback_handsets
            self.log(f"Surfacing {len(valid_products)} authentic {parsed['brand'].title()} handsets from JioMart.", 90)
        else:
            valid_products = []

        # Do not force-sort ascending if user did not request price sorting
        if effective_min_price is not None or effective_max_price is not None:
            valid_products.sort(key=lambda x: x["price_num"])

        if valid_products:
            self.save_results(valid_products)
        self.log(f"JioMart scrape complete. Total handsets: {len(valid_products)}", 100)
        return valid_products

    def save_results(self, products: List[Dict[str, Any]]):
        try:
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(curr_dir, "scraped_data")
            os.makedirs(data_dir, exist_ok=True)

            json_path = os.path.join(data_dir, "jiomart_products.json")
            
            # Load existing catalog to avoid wiping out handsets
            existing_products = []
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        existing_products = json.load(f)
                except Exception:
                    existing_products = []

            # Deduplicate and merge by product URL / SKU
            merged_map = {}
            for p in existing_products:
                k = p.get("url") or p.get("sku") or p.get("title")
                if k:
                    merged_map[k] = p
            for p in products:
                k = p.get("url") or p.get("sku") or p.get("title")
                if k:
                    merged_map[k] = p

            final_products = list(merged_map.values()) if merged_map else products

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(final_products, f, indent=2, ensure_ascii=False)

            csv_path = os.path.join(data_dir, "jiomart_products.csv")
            csv_rows = []
            for p in final_products:
                r = dict(p)
                r["specs"] = ", ".join(p.get("specs", []))
                csv_rows.append(r)
            if csv_rows:
                df = pd.DataFrame(csv_rows)
                df.to_csv(csv_path, index=False, encoding="utf-8")
        except Exception as e:
            logger.warning(f"Could not persist scraped datasets: {e}")
