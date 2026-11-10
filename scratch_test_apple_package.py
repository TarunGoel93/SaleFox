import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

sys.path.append(r"C:\Users\DEBRAJ\Downloads\apple_automation\apple_automation")
from browser_manager import BrowserManager
from account_manager import Account
from product_manager import ProductManager
from utils import button_present, click, wait_for_clickable_text
import config

account = Account(1)
bm = BrowserManager()
driver = bm.launch(account)

try:
    products = ProductManager(driver)
    info = products.open_and_verify()
    products.select_options()
    print("Options confirmed:", products.options_confirmed())

    # Now click Add to Bag and see what happens
    btn = wait_for_clickable_text(driver, config.ADD_TO_BAG_TEXTS, "Add to Bag")
    print("Add to Bag found:", btn.text)
    driver.save_screenshot("before_click.png")

    click(driver, btn)
    print("Add to Bag clicked!")
    time.sleep(2)
    driver.save_screenshot("after_click_2s.png")
    print("URL after 2s:", driver.current_url)

    time.sleep(3)
    driver.save_screenshot("after_click_5s.png")
    print("URL after 5s:", driver.current_url)

    # Print any overlay or modal text
    print("Page text snippet:", driver.find_element(By.TAG_NAME, "body").text[:500])

finally:
    driver.quit()
