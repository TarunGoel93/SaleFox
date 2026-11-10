from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

opts = Options()
opts.add_argument('--start-maximized')
opts.add_argument('--disable-features=CalculateNativeWinOcclusion')
opts.add_argument('--disable-backgrounding-occluded-windows')
opts.add_argument('--disable-renderer-backgrounding')
driver = webdriver.Chrome(options=opts)

try:
    # Search for cables on croma
    driver.get("https://www.croma.com/searchB?q=cable%3Arelevance&text=cable")
    time.sleep(5)

    # Let's check products on the search results page
    products = driver.find_elements(By.XPATH, "//li[contains(@class, 'product-item')]")
    print("Found products on search page:", len(products))

    # Look for items under 150 that have 'Add to Cart' or 'Buy Now'
    items = driver.find_elements(By.XPATH, "//div[contains(@class, 'cp-product')] | //li[contains(@class, 'product-item')]")
    for it in items[:15]:
        text = it.text
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        links = it.find_elements(By.TAG_NAME, "a")
        href = links[0].get_attribute("href") if links else ""
        has_buy = any('add to cart' in l.lower() or 'buy now' in l.lower() for l in lines)
        print("Item:", lines[:3], "Buyable:", has_buy, "Href:", href)

finally:
    driver.quit()

