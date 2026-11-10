import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1920,1080')
opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
driver = webdriver.Chrome(options=opts)
try:
    driver.get('https://www.apple.com/in/shop/buy-iphone/iphone-16')
    time.sleep(4)
    print('Title:', driver.title)
    
    # 1. Colors
    print('--- COLOR ELEMENTS ---')
    for el in driver.find_elements(By.XPATH, "//input[@name='dimensionColor']"):
        val = el.get_attribute('value')
        label = el.get_attribute('aria-label') or el.get_attribute('id')
        print(f"color: val={val} id={label}")

    # 2. Trade-in
    print('--- TRADE-IN ELEMENTS ---')
    for el in driver.find_elements(By.XPATH, "//input[contains(@id, 'noTradeIn') or contains(@id, 'tradein')] | //label[contains(., 'No trade-in')]"):
        print(f"trade-in: tag={el.tag_name} id={el.get_attribute('id')} text={el.text.strip()}")

    # 3. AppleCare
    print('--- APPLECARE ELEMENTS ---')
    for el in driver.find_elements(By.XPATH, "//input[@name='applecare-options'] | //label[contains(., 'No AppleCare')]"):
        print(f"applecare: tag={el.tag_name} id={el.get_attribute('id')} text={el.text.strip()}")

    # 4. Add to cart / bag
    print('--- ADD TO BAG BUTTONS ---')
    for el in driver.find_elements(By.XPATH, "//button[@name='add-to-cart']"):
        print(f"add-to-cart: tag={el.tag_name} text={el.text.strip()} displayed={el.is_displayed()}")

finally:
    driver.quit()
