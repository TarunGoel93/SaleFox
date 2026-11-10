from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

opts = Options()
opts.add_argument('--start-maximized')
driver = webdriver.Chrome(options=opts)

try:
    # Let's search on croma for mobile phones under 10000 or earphones
    search_urls = [
        "https://www.croma.com/searchB?q=earphones%3Arelevance&text=earphones",
        "https://www.croma.com/phones-wearables/mobile-phones/c/10",
        "https://www.croma.com/searchB?q=adapter%3Arelevance&text=adapter"
    ]

    for surl in search_urls:
        print("\nChecking:", surl)
        driver.get(surl)
        time.sleep(4)
        
        # Check products
        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        print("Found product links:", len(links))
        for l in links[:5]:
            href = l.get_attribute("href")
            text = l.text.strip()
            if href and text:
                print(f"Product: {text[:40]} -> {href}")

finally:
    driver.quit()

