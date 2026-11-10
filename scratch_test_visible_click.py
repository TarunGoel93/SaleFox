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

    # 1. Color: Ultramarine - click label or swatch
    clicked_color = False
    for el in driver.find_elements(By.XPATH, "//img[contains(@src, 'ultramarine')]/.. | //label[contains(@data-autom, 'ultramarine') or contains(@id, 'label') and contains(., 'ultramarine')]"):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.5)
            el.click()
            print("Clicked Ultramarine via swatch/label!")
            clicked_color = True
            break
        except Exception:
            pass

    if not clicked_color:
        # Click radio via javascript
        radio = driver.find_element(By.XPATH, "//input[@name='dimensionColor' and @value='ultramarine']")
        driver.execute_script("arguments[0].click();", radio)
        print("Clicked Ultramarine radio via JS!")

    time.sleep(2)

    # 2. Storage: 128GB - click label
    for el in driver.find_elements(By.XPATH, "//label[contains(., '128GB') or contains(., '128 GB')]"):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.5)
            el.click()
            print("Clicked 128GB label!")
            break
        except Exception as e:
            print("Storage click err:", e)

    time.sleep(2)

    # 3. Trade-in: No - click label
    for el in driver.find_elements(By.XPATH, "//label[@id='noTradeIn_label'] | //label[contains(., 'No trade-in')]"):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.5)
            el.click()
            print("Clicked No trade-in label!")
            break
        except Exception as e:
            print("Trade-in click err:", e)

    time.sleep(2)

    # 4. AppleCare: No - click label
    for el in driver.find_elements(By.XPATH, "//label[contains(., 'No AppleCare+ Coverage')]"):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.5)
            el.click()
            print("Clicked No AppleCare+ Coverage label!")
            break
        except Exception as e:
            print("AppleCare click err:", e)

    time.sleep(2.5)

    # 5. Add to Bag
    add_btn = driver.find_element(By.XPATH, "//button[@name='add-to-cart']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
    time.sleep(1)
    
    print("Clicking Add to Bag button...")
    add_btn.click()
    time.sleep(5)
    print("Current URL after click:", driver.current_url)

    # Look for Review Bag
    for el in driver.find_elements(By.XPATH, "//button[contains(., 'Review Bag')] | //a[contains(., 'Review Bag')]"):
        if el.is_displayed():
            print("Found Review Bag CTA:", el.text)
            el.click()
            print("Clicked Review Bag CTA!")
            break

    time.sleep(4)
    print("Bag URL:", driver.current_url)

    # Look for Checkout button
    for el in driver.find_elements(By.XPATH, "//button[@id='shoppingCart.actions.checkout'] | //button[contains(., 'Check Out')]"):
        if el.is_displayed():
            print("Found Checkout button:", el.text, "ID:", el.get_attribute("id"))

finally:
    time.sleep(5)
    driver.quit()
