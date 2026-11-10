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
    print("Navigating to clean URL: https://www.apple.com/in/shop/buy-iphone/iphone-16")
    driver.get("https://www.apple.com/in/shop/buy-iphone/iphone-16")
    time.sleep(3)

    # 1. Color: Ultramarine
    color = driver.find_element(By.XPATH, "//input[@name='dimensionColor' and @value='ultramarine']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", color)
    print("1. Selected Color: Ultramarine")
    time.sleep(1.5)

    # 2. Storage: 128GB
    storage = driver.find_element(By.XPATH, "//input[@name='dimensionCapacity' and contains(@value, '128')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", storage)
    print("2. Selected Storage: 128GB")
    time.sleep(1.5)

    # 3. Trade-in: No
    tradein = driver.find_element(By.XPATH, "//input[@id='noTradeIn']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", tradein)
    print("3. Selected Trade-in: No trade-in")
    time.sleep(1.5)

    # 4. AppleCare: No
    care = driver.find_element(By.XPATH, "//input[@name='applecare-options' and (contains(@id, 'no') or contains(@data-autom, 'noapplecare'))]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", care)
    print("4. Selected AppleCare: No AppleCare+ Coverage")
    time.sleep(2)

    # 5. Add to Bag
    add_btn = driver.find_element(By.XPATH, "//button[@name='add-to-cart']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
    time.sleep(1)
    
    print("Clicking Add to Bag...")
    # Click via JS or normal click
    driver.execute_script("arguments[0].click();", add_btn)
    time.sleep(4)
    print("URL after Add to Bag click:", driver.current_url)

    # Check for Review Bag button
    review_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Review Bag')] | //a[contains(., 'Review Bag')] | //*[contains(text(), 'Review Bag')]")
    print(f"Found {len(review_btns)} Review Bag elements:")
    for rb in review_btns:
        print("Review Bag:", rb.text, "tag:", rb.tag_name, "visible:", rb.is_displayed())
        if rb.is_displayed():
            driver.execute_script("arguments[0].click();", rb)
            print("Clicked Review Bag button!")
            break

    time.sleep(4)
    print("URL after Review Bag:", driver.current_url)
    
    driver.save_screenshot("clean_bag_test.png")
    bag_text = driver.find_element(By.TAG_NAME, "body").text
    print("Bag has 'Your bag is empty'?:", "your bag is empty" in bag_text.lower())
    print("Bag has 'iPhone 16'?:", "iphone 16" in bag_text.lower())
    for btn in driver.find_elements(By.XPATH, "//button[@id='shoppingCart.actions.checkout'] | //button[contains(., 'Check Out')]"):
        print("Found Checkout button! visible:", btn.is_displayed(), "text:", btn.text)

finally:
    time.sleep(3)
    driver.quit()
