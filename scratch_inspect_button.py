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
    driver.get("https://www.apple.com/in/shop/buy-iphone/iphone-16")
    time.sleep(3)

    # Ultramarine
    for el in driver.find_elements(By.XPATH, "//input[@name='dimensionColor' and @value='ultramarine']"):
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
        break
    time.sleep(1)

    # 128GB
    for el in driver.find_elements(By.XPATH, "//input[@name='dimensionCapacity' and contains(@value, '128')]"):
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
        break
    time.sleep(1)

    # Trade in No
    for el in driver.find_elements(By.XPATH, "//label[contains(., 'No trade-in')] | //input[@id='noTradeIn']"):
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
        break
    time.sleep(1)

    # Apple Care No
    for el in driver.find_elements(By.XPATH, "//label[contains(., 'No AppleCare+ Coverage')]"):
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
        break
    time.sleep(1.5)

    add_btn = driver.find_element(By.XPATH, "//button[@name='add-to-cart']")
    parent_form = driver.execute_script("""
        let b = arguments[0];
        let f = b.closest('form');
        if (!f) return { hasForm: false };
        return {
            hasForm: true,
            action: f.getAttribute('action'),
            method: f.getAttribute('method'),
            id: f.id,
            className: f.className,
            html: f.outerHTML.substring(0, 500)
        };
    """, add_btn)
    print("Parent form info:", parent_form)

    btn_info = driver.execute_script("""
        let b = arguments[0];
        return {
            type: b.type,
            name: b.name,
            value: b.value,
            onclick: b.getAttribute('onclick'),
            outerHTML: b.outerHTML
        };
    """, add_btn)
    print("Button info:", btn_info)

finally:
    driver.quit()
