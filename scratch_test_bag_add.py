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
    # Test 1: Direct bag add
    driver.get("https://www.apple.com/in/shop/bag/add?product=MYEC3HN/A")
    time.sleep(3)
    print("URL after direct add:", driver.current_url)
    print("Page title:", driver.title)
    
    # Check if bag has item
    driver.get("https://www.apple.com/in/shop/bag")
    time.sleep(3)
    text = driver.find_element(By.TAG_NAME, "body").text
    print("Bag empty?:", "your bag is empty" in text.lower())
    for btn in driver.find_elements(By.XPATH, "//button[@id='shoppingCart.actions.checkout']"):
        print("Found checkout button! displayed:", btn.is_displayed())
finally:
    driver.quit()
