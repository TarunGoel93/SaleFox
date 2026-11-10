from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

opts = Options()
opts.add_argument('--start-maximized')
driver = webdriver.Chrome(options=opts)

try:
    driver.get('https://www.croma.com/croma-type-a-to-type-c-3-3-feet-1m-cable-dash-warp-protocols-red-/p/256182')
    time.sleep(4)

    # Dump all buttons that contain 'buy' or 'cart' in text or attributes
    all_btns = driver.find_elements(By.TAG_NAME, 'button')
    for b in all_btns:
        text = b.text.strip()
        cls = b.get_attribute('class') or ''
        if any(k in text.lower() or k in cls.lower() for k in ['buy', 'cart', 'order']):
            print(f"Tag button: '{text}' | class: '{cls}' | visible: {b.is_displayed()}")

    all_links = driver.find_elements(By.TAG_NAME, 'a')
    for a in all_links:
        text = a.text.strip()
        cls = a.get_attribute('class') or ''
        if any(k in text.lower() or k in cls.lower() for k in ['buy', 'cart', 'order']):
            print(f"Tag a: '{text}' | class: '{cls}' | visible: {a.is_displayed()}")

finally:
    driver.quit()

