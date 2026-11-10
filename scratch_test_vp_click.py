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
    driver.get("https://www.apple.com/in/shop/buy-iphone/iphone-16")
    time.sleep(3)

    # Click Ultramarine, 128GB, No trade-in, No AppleCare
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@name='dimensionColor' and @value='ultramarine']"))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@name='dimensionCapacity' and contains(@value, '128')]"))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@id='noTradeIn']"))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//input[@name='applecare-options' and (contains(@id, 'no') or contains(@data-autom, 'noapplecare'))]"))
    time.sleep(1.5)

    add_btn = driver.find_element(By.XPATH, "//button[@name='add-to-cart']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
    time.sleep(1)

    # Get exact viewport coordinates
    vp_coords = driver.execute_script("""
        let rect = arguments[0].getBoundingClientRect();
        return {
            x: Math.round(rect.left + rect.width / 2),
            y: Math.round(rect.top + rect.height / 2)
        };
    """, add_btn)
    print("Exact Viewport Coords:", vp_coords)

    # Dispatch mouseMove first, then press, then release
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseMoved",
        "x": vp_coords['x'],
        "y": vp_coords['y']
    })
    time.sleep(0.1)
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mousePressed",
        "x": vp_coords['x'],
        "y": vp_coords['y'],
        "button": "left",
        "clickCount": 1
    })
    time.sleep(0.15)
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseReleased",
        "x": vp_coords['x'],
        "y": vp_coords['y'],
        "button": "left",
        "clickCount": 1
    })
    print("Dispatched hardware click at exact viewport coords!")
    time.sleep(5)
    print("Current URL:", driver.current_url)

    # Check for Review Bag button
    review_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Review Bag')] | //a[contains(., 'Review Bag')] | //*[contains(text(), 'Review Bag')]")
    print(f"Found {len(review_btns)} Review Bag elements:")
    for rb in review_btns:
        print("Review Bag:", rb.text, "tag:", rb.tag_name, "visible:", rb.is_displayed())
        if rb.is_displayed():
            rb.click()
            print("Clicked Review Bag button!")
            break

    time.sleep(4)
    print("Bag URL:", driver.current_url)

    # Check if bag has item
    driver.get("https://www.apple.com/in/shop/bag")
    time.sleep(3)
    text = driver.find_element(By.TAG_NAME, "body").text
    print("Bag contains 'your bag is empty'?:", "your bag is empty" in text.lower())
    for btn in driver.find_elements(By.XPATH, "//button[@id='shoppingCart.actions.checkout']"):
        print("Checkout button visible:", btn.is_displayed())

finally:
    time.sleep(3)
    driver.quit()
