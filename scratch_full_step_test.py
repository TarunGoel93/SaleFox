import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1920,1080')
opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
driver = webdriver.Chrome(options=opts)

try:
    print("Navigating to https://www.apple.com/in/shop/buy-iphone/iphone-16...")
    driver.get("https://www.apple.com/in/shop/buy-iphone/iphone-16")
    time.sleep(3)

    # 1. Select Model if needed
    for el in driver.find_elements(By.XPATH, "//input[@name='dimensionScreensize' and contains(@value, '6.1')] | //label[contains(., 'iPhone 16') and contains(., '6.1')]"):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", el)
            print("Selected Model: iPhone 16 (6.1 inch)")
            break
        except Exception:
            pass

    time.sleep(1)

    # 2. Select Color (e.g. ultramarine)
    color_clicked = False
    for el in driver.find_elements(By.XPATH, "//input[@name='dimensionColor' and @value='ultramarine']"):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", el)
            print("Selected Color: Ultramarine")
            color_clicked = True
            break
        except Exception:
            pass
    if not color_clicked:
        for el in driver.find_elements(By.XPATH, "//label[contains(@for, 'dimensionColor') and contains(translate(., 'ULTRAMARINE', 'ultramarine'), 'ultramarine')]"):
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", el)
            print("Selected Color via label: Ultramarine")
            break

    time.sleep(1)

    # 3. Select Storage (128GB)
    for el in driver.find_elements(By.XPATH, "//input[@name='dimensionCapacity' and contains(@value, '128')] | //label[contains(., '128GB') or contains(., '128 GB')]"):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", el)
            print("Selected Storage: 128GB")
            break
        except Exception:
            pass

    time.sleep(1)

    # 4. Select Trade-in: "No trade-in"
    for el in driver.find_elements(By.XPATH, "//label[contains(., 'No trade-in')] | //input[@id='noTradeIn']"):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", el)
            print("Selected Trade-in: No trade-in")
            break
        except Exception:
            pass

    time.sleep(1)

    # 5. Select AppleCare: "No AppleCare+ Coverage"
    for el in driver.find_elements(By.XPATH, "//label[contains(., 'No AppleCare+ Coverage')] | //input[@name='applecare-options' and contains(@id, 'no')]"):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", el)
            print("Selected AppleCare: No AppleCare+ Coverage")
            break
        except Exception:
            pass

    time.sleep(2)

    # 6. Check for Add to Bag
    add_btns = driver.find_elements(By.XPATH, "//button[@name='add-to-cart']")
    print(f"Found {len(add_btns)} 'add-to-cart' buttons")
    if add_btns:
        add_btn = add_btns[0]
        print(f"Add to Bag button visible: {add_btn.is_displayed()}")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
        time.sleep(1)
        # Click span
        spans = add_btn.find_elements(By.TAG_NAME, "span")
        if spans:
            ActionChains(driver).move_to_element(spans[0]).click().perform()
            print("Clicked span of Add to Bag via ActionChains!")
        else:
            ActionChains(driver).move_to_element(add_btn).click().perform()
            print("Clicked Add to Bag via ActionChains!")

        time.sleep(3)
        print(f"Current URL after Add to Bag click: {driver.current_url}")
        
        # Check transition screen / review bag button
        review_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Review Bag')] | //a[contains(., 'Review Bag')] | //*[contains(text(), 'Review Bag')]")
        print(f"Found {len(review_btns)} 'Review Bag' buttons/links:")
        for rb in review_btns:
            print(f" - {rb.tag_name}: {rb.text} (displayed: {rb.is_displayed()})")

finally:
    driver.quit()
