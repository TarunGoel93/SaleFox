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
    driver.get("https://www.apple.com/in/shop/buy-iphone/iphone-16")
    time.sleep(3)

    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@name='dimensionColor' and @value='ultramarine']"))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@name='dimensionCapacity' and contains(@value, '128')]"))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@id='noTradeIn']"))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@name='applecare-options' and (contains(@id, 'no') or contains(@data-autom, 'noapplecare'))]"))
    time.sleep(1.5)

    add_btn = driver.find_element(By.XPATH, "//button[@name='add-to-cart']")

    # Let's see what inputs are inside the form:
    inputs = driver.execute_script("""
        let b = arguments[0];
        let f = b.closest('form');
        let inputs = Array.from(f.querySelectorAll('input, button')).map(i => ({
            name: i.name,
            value: i.value,
            type: i.type
        }));
        return {
            action: f.getAttribute('action'),
            method: f.getAttribute('method'),
            inputs: inputs
        };
    """, add_btn)
    print("Form inputs:", inputs)

finally:
    driver.quit()
