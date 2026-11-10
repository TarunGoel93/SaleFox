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
    driver.get("https://www.apple.com/in/shop/buy-iphone/iphone-16")
    time.sleep(3)

    # 1. Color: Ultramarine
    for el in driver.find_elements(By.XPATH, "//input[@name='dimensionColor' and @value='ultramarine']"):
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
        break
    time.sleep(1)

    # 2. Storage: 128GB
    for el in driver.find_elements(By.XPATH, "//input[@name='dimensionCapacity' and contains(@value, '128')]"):
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
        break
    time.sleep(1)

    # 3. Trade-in: No
    for el in driver.find_elements(By.XPATH, "//label[contains(., 'No trade-in')] | //input[@id='noTradeIn']"):
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
        break
    time.sleep(1)

    # 4. AppleCare: No
    for el in driver.find_elements(By.XPATH, "//label[contains(., 'No AppleCare+ Coverage')]"):
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
        break
    time.sleep(1.5)

    # 5. Add to Bag
    add_btn = driver.find_element(By.XPATH, "//button[@name='add-to-cart']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
    time.sleep(0.5)
    
    # Try normal click or ActionChains click
    ActionChains(driver).move_to_element(add_btn).click().perform()
    time.sleep(4)
    print("Page URL after 4s:", driver.current_url)
    driver.save_screenshot("after_add_cart.png")
    
    # Check all visible buttons
    print("--- ALL VISIBLE BUTTONS ---")
    for b in driver.find_elements(By.TAG_NAME, "button"):
        if b.is_displayed() and b.text.strip():
            print("button:", b.text.strip().replace("\n", " "))
    for a in driver.find_elements(By.TAG_NAME, "a"):
        if a.is_displayed() and ("bag" in a.text.lower() or "checkout" in a.text.lower() or "review" in a.text.lower()):
            print("link:", a.text.strip().replace("\n", " "), "href:", a.get_attribute("href"))

    # Now check /shop/bag
    driver.get("https://www.apple.com/in/shop/bag")
    time.sleep(3)
    print("Bag URL:", driver.current_url)
    print("Bag text contains 'Your bag is empty'?:", "your bag is empty" in driver.page_source.lower())
    driver.save_screenshot("bag_screen.png")
    
    # Check buttons on Bag page
    for b in driver.find_elements(By.TAG_NAME, "button"):
        if b.is_displayed() and b.text.strip():
            print("Bag button:", b.text.strip().replace("\n", " "), "id:", b.get_attribute("id"))

finally:
    driver.quit()
