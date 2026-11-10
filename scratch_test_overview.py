import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--start-maximized')
opts.add_argument('--no-first-run')
opts.add_argument('--no-default-browser-check')
driver = webdriver.Chrome(options=opts)

try:
    print("Navigating to https://www.apple.com/in/shop/buy-iphone...")
    driver.get("https://www.apple.com/in/shop/buy-iphone")
    time.sleep(3)
    driver.save_screenshot("buy_iphone_start.png")

    # Look for iPhone 16 tab or Buy button
    print("Looking for iPhone 16 / Buy button...")
    for b in driver.find_elements(By.XPATH, "//button[contains(., 'Buy') or contains(., 'iPhone 16')] | //a[contains(., 'Buy') or contains(., 'iPhone 16')]"):
        if b.is_displayed():
            print("Found CTA:", b.text.strip().replace("\n", " "), "tag:", b.tag_name)

finally:
    driver.quit()
