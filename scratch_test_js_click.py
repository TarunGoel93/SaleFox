import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

opts = Options()
opts.add_argument('--start-maximized')
opts.add_argument('--no-first-run')
opts.add_argument('--no-default-browser-check')
driver = webdriver.Chrome(options=opts)

try:
    print("Navigating to https://www.apple.com/in/shop/buy-iphone/iphone-16...")
    driver.get("https://www.apple.com/in/shop/buy-iphone/iphone-16")
    time.sleep(3)

    # 1. Color: Ultramarine
    color = driver.find_element(By.XPATH, "//input[@name='dimensionColor' and @value='ultramarine']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", color)
    print("Clicked Ultramarine radio via JS!")
    time.sleep(2)

    # 2. Storage: 128GB
    storage = driver.find_element(By.XPATH, "//input[@name='dimensionCapacity' and contains(@value, '128')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", storage)
    print("Clicked 128GB radio via JS!")
    time.sleep(2)

    # 3. Trade-in: No
    tradein = driver.find_element(By.XPATH, "//input[@id='noTradeIn']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", tradein)
    print("Clicked No trade-in radio via JS!")
    time.sleep(2)

    # 4. AppleCare: No
    care = driver.find_element(By.XPATH, "//input[@name='applecare-options' and (contains(@id, 'no') or contains(@data-autom, 'noapplecare'))]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", care)
    print("Clicked No AppleCare+ radio via JS!")
    time.sleep(2.5)

    # Check Add to Bag state
    add_btn = driver.find_element(By.XPATH, "//button[@name='add-to-cart']")
    is_disabled = add_btn.get_attribute("disabled")
    aria_disabled = add_btn.get_attribute("aria-disabled")
    print(f"Add to Bag button: disabled={is_disabled}, aria_disabled={aria_disabled}")

    if not is_disabled and aria_disabled != "true":
        print("Add to Bag is ACTIVE and ENABLED!")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
        time.sleep(1)
        # Click button
        add_btn.click()
        print("Clicked Add to Bag button directly with selenium click()!")
        time.sleep(5)
        print("Current URL after click:", driver.current_url)

        # Check for Review Bag button
        review_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Review Bag')] | //a[contains(., 'Review Bag')]")
        print(f"Found {len(review_btns)} Review Bag elements:")
        for rb in review_btns:
            print("Review Bag:", rb.text, "tag:", rb.tag_name, "visible:", rb.is_displayed())
            if rb.is_displayed():
                rb.click()
                print("Clicked Review Bag button!")
                break
        
        time.sleep(4)
        print("Bag URL:", driver.current_url)
        
        # Check Checkout button
        checkouts = driver.find_elements(By.XPATH, "//button[@id='shoppingCart.actions.checkout']")
        print(f"Found {len(checkouts)} Checkout button on Bag page!")
        for co in checkouts:
            print("Checkout button visible:", co.is_displayed())

finally:
    time.sleep(5)
    driver.quit()
