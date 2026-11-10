import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}
req = urllib.request.Request('https://www.jiomart.com/', headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    routes = set(re.findall(r'/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+', html))
    search_routes = [r for r in routes if 'search' in r or 'product' in r or 'catalog' in r]
    print('Search / product routes:', search_routes)

