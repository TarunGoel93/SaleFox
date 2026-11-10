import requests
import re
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
r = requests.get("https://www.oppo.com/in/smartphones/", headers=headers, timeout=10)
soup = BeautifulSoup(r.text, "html.parser")

# Find all links to /smartphones/ or /product/
links = soup.find_all("a", href=True)
phone_links = {}
for a in links:
    href = a["href"]
    text = a.get_text(strip=True)
    if "/smartphones/series-" in href or ("/product/" in href and not any(acc in href for acc in ["case", "cable", "earbud", "pad", "pencil", "power-bank", "cooling", "bubble", "adapter"])):
        # Find associated image
        img = a.find("img")
        img_url = ""
        if img:
            img_url = img.get("src") or img.get("data-src") or ""
            if img_url and not img_url.startswith("http"):
                img_url = "https://www.oppo.com" + img_url
        
        # Look for sibling or parent text describing model and specs
        parent_text = a.parent.get_text(strip=True) if a.parent else ""
        
        slug = href.strip("/").split("/")[-1]
        phone_links[slug] = {
            "slug": slug,
            "text": text,
            "href": href if href.startswith("http") else "https://www.oppo.com" + href,
            "img": img_url,
            "parent_text": parent_text[:120]
        }

print(f"Total unique phone links found: {len(phone_links)}")
for s, d in phone_links.items():
    print(f"- {s} | text: {d['text']} | href: {d['href']} | parent: {d['parent_text']}")

