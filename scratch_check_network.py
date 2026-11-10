import json
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
    driver.execute_cdp_cmd("Network.enable", {})
    driver.get("https://www.apple.com/in/shop/buy-iphone/iphone-16")
    time.sleep(4)

    # Click Ultramarine, 128GB, No trade-in, No AppleCare
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@name='dimensionColor' and @value='ultramarine']"))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@name='dimensionCapacity' and contains(@value, '128')]"))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@id='noTradeIn']"))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@name='applecare-options' and (contains(@id, 'no') or contains(@data-autom, 'noapplecare'))]"))
    time.sleep(2)

    # Let's see what scripts are loaded and what window.AOS or similar has
    scripts = driver.execute_script("""
        let scripts = Array.from(document.querySelectorAll('script')).map(s => s.src).filter(Boolean);
        return {
            scriptCount: scripts.length,
            sample: scripts.slice(-10)
        };
    """)
    print("Loaded scripts:", scripts)

    # Let's see what is inside window
    keys = driver.execute_script("""
        return Object.keys(window).filter(k => !k.startsWith('webkit') && !k.startsWith('on'));
    """)
    print("Window keys count:", len(keys))
    apple_keys = [k for k in keys if any(x in k.lower() for x in ['apple', 'cart', 'bag', 'shop', 'order', 'step', 'product'])]
    print("Matching window keys:", apple_keys)

finally:
    driver.quit()
