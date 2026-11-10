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

    # Let's inspect event listeners via CDP
    btn_box = add_btn.rect
    print("Button box:", btn_box)
    
    # Let's check CDP Input.dispatchMouseEvent
    center_x = btn_box['x'] + btn_box['width'] / 2
    center_y = btn_box['y'] + btn_box['height'] / 2
    print(f"Center coords: ({center_x}, {center_y})")

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
    time.sleep(1)

    btn_box = add_btn.rect
    center_x = int(btn_box['x'] + btn_box['width'] / 2)
    center_y = int(btn_box['y'] + btn_box['height'] / 2)
    print(f"New center coords: ({center_x}, {center_y})")

    # Send true hardware mouse click via CDP
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mousePressed",
        "x": center_x,
        "y": center_y,
        "button": "left",
        "clickCount": 1
    })
    time.sleep(0.1)
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseReleased",
        "x": center_x,
        "y": center_y,
        "button": "left",
        "clickCount": 1
    })

    print("Dispatched CDP mouse click!")
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

finally:
    time.sleep(5)
    driver.quit()
