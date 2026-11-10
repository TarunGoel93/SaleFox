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
    time.sleep(4)

    user_link = driver.find_element(By.XPATH, "//a[contains(@class, 'user-link')]")
    driver.execute_script("arguments[0].click();", user_link)
    time.sleep(2)

    # Find the modal element
    modals = driver.find_elements(By.XPATH, "//div[contains(., 'Login') and contains(., 'Create Account')]")
    for m in modals:
        if m.is_displayed():
            print("--- MODAL HTML ---")
            print(m.get_attribute('outerHTML')[:3000])
            break

finally:
    driver.quit()

