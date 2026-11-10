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
    driver.get('https://www.croma.com')
    time.sleep(5)

    # Find the user icon or login button in header
    # Let's search for icons, SVG, or links with user/login/account
    elems = driver.find_elements(By.XPATH, "//*[contains(@class, 'user') or contains(@class, 'account') or contains(@class, 'login') or contains(@class, 'profile') or contains(@href, 'login') or contains(@href, 'my-account')]")
    print(f"Candidate elements: {len(elems)}")
    for e in elems:
        try:
            if e.is_displayed():
                print(f"Tag: {e.tag_name}, Class: {e.get_attribute('class')}, Text: '{e.text}', Href: {e.get_attribute('href')}")
        except:
            pass

    # Specifically look for user icon or button in header
    user_btns = driver.find_elements(By.XPATH, "//div[contains(@class, 'user-icon') or contains(@class, 'account-icon') or contains(@class, 'navigation-item')] | //button[contains(@class, 'user')] | //a[contains(@class, 'user')]")
    print(f"User buttons: {len(user_btns)}")
    for ub in user_btns:
        if ub.is_displayed():
            print("Clicking candidate:", ub.tag_name, ub.get_attribute('class'))
            driver.execute_script("arguments[0].click();", ub)
            time.sleep(2)
            break

    # Now check inputs on page
    inputs = driver.find_elements(By.TAG_NAME, 'input')
    for inp in inputs:
        if inp.is_displayed():
            print("Visible Input:", inp.get_attribute('id'), inp.get_attribute('class'), inp.get_attribute('placeholder'))

finally:
    driver.quit()

