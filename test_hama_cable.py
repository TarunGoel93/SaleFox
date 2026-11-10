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
    url = "https://www.croma.com/hama-type-c-to-type-c-3-3-feet-1m-cable-sync-and-charge-black-/p/252773"
    driver.get(url)
    time.sleep(4)

    print("Title:", driver.title)
    
    # Check buttons on product page
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for b in buttons:
        if b.is_displayed() and b.text.strip():
            print("Button:", b.text.strip(), "class:", b.get_attribute("class"))

    # Check stock text
    body = driver.find_element(By.TAG_NAME, "body").text
    for line in body.splitlines():
        if any(w in line.lower() for w in ['out of stock', 'add to cart', 'buy now', 'delivery', 'pincode']):
            print("Line:", line.strip())

finally:
    driver.quit()

