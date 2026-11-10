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

    # Let's inspect what happens on submit
    analysis = driver.execute_script("""
        let b = arguments[0];
        let f = b.closest('form');
        
        // Listen to all fetch and XHR
        window._networkLog = [];
        let origFetch = window.fetch;
        window.fetch = function(...args) {
            window._networkLog.push({ type: 'fetch', url: args[0] });
            return origFetch.apply(this, args);
        };
        let origOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url) {
            window._networkLog.push({ type: 'xhr', method: method, url: url });
            return origOpen.apply(this, arguments);
        };

        return {
            formId: f ? f.id : null,
            formAction: f ? f.action : null,
            formMethod: f ? f.method : null
        };
    """, add_btn)
    print("Form analysis:", analysis)

    # Now let's see what happens if we prevent the default submit on the form
    driver.execute_script("""
        let b = arguments[0];
        let f = b.closest('form');
        if (f) {
            f.addEventListener('submit', function(e) {
                console.log("Form submit event fired!", e);
            });
        }
    """, add_btn)

    # Let's see if clicking the span or button triggers anything
    span = add_btn.find_element(By.TAG_NAME, "span")
    driver.execute_script("""
        let s = arguments[0];
        s.click();
    """, span)
    time.sleep(3)
    print("URL after span click:", driver.current_url)

    network_log = driver.execute_script("return window._networkLog || [];")
    print("Network log:", network_log)

finally:
    driver.quit()
