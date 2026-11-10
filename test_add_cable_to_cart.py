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

    # Check Add to cart / buy now buttons
    buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Add to Cart') or contains(., 'Buy Now') or contains(@class, 'add-to-cart') or contains(@class, 'buy-now')]")
    print("Found action buttons:", len(buttons))
    for b in buttons:
        print("Button text:", b.text, "visible:", b.is_displayed(), "class:", b.get_attribute('class'))
        if b.is_displayed():
            driver.execute_script("arguments[0].click();", b)
            print("Clicked button:", b.text)
            time.sleep(3)
            break

    # Go to cart
    driver.get("https://www.croma.com/cart")
    time.sleep(4)
    print("Cart URL:", driver.current_url)
    body = driver.find_element(By.TAG_NAME, "body").text
    for l in body.splitlines()[:20]:
        print("Cart line:", l.strip())

finally:
    driver.quit()

