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
    url = "https://www.croma.com/croma-type-a-to-type-c-3-3-feet-1m-cable-dash-warp-protocols-red-/p/256182"
    driver.get(url)
    time.sleep(4)

    # 1. Click 'Add Pincode' button to set pincode
    pin_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Pincode') or contains(@class, 'pincode')] | //a[contains(., 'Pincode')]")
    for pb in pin_btns:
        if pb.is_displayed():
            driver.execute_script("arguments[0].click();", pb)
            time.sleep(1)
            break

    # 2. Enter Pincode
    pin_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'Pincode') or contains(@id, 'pincode')]")
    for pi in pin_inputs:
        if pi.is_displayed():
            pi.clear()
            pi.send_keys("249205")
            time.sleep(0.5)
            # Click check/apply
            for b in driver.find_elements(By.XPATH, "//button[contains(., 'Apply') or contains(., 'Check') or contains(., 'Continue')]"):
                if b.is_displayed():
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(2)
                    break
            break

    time.sleep(2)

    # 3. Check action buttons again
    buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'buyNowBtn') or contains(@class, 'pdp-add-to-cart') or contains(., 'Buy Now') or contains(., 'Add to Cart')]")
    print("Action buttons after pincode:")
    for b in buttons:
        print("Text:", b.text, "Visible:", b.is_displayed(), "Class:", b.get_attribute('class'))
        if b.is_displayed():
            driver.execute_script("arguments[0].click();", b)
            print("Successfully clicked:", b.get_attribute('class'))
            time.sleep(3)
            break

    # 4. Check cart
    driver.get("https://www.croma.com/cart")
    time.sleep(3)
    print("Cart URL:", driver.current_url)
    body = driver.find_element(By.TAG_NAME, "body").text
    print("Cart preview:\n", "\n".join(body.splitlines()[:15]))

finally:
    driver.quit()

