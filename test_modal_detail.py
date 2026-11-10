from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

opts = Options()
opts.add_argument('--start-maximized')
opts.add_argument('--disable-features=CalculateNativeWinOcclusion')
opts.add_argument('--disable-backgrounding-occluded-windows')
opts.add_argument('--disable-renderer-backgrounding')
driver = webdriver.Chrome(options=opts)

try:
    driver.get('https://www.croma.com')
    time.sleep(4)

    user_link = driver.find_element(By.XPATH, "//a[contains(@class, 'user-link')]")
    driver.execute_script("arguments[0].click();", user_link)
    time.sleep(2)

    inp = driver.find_element(By.XPATH, "//input[contains(@class, 'input-login')]")
    email = "debrajshil.bcseiot2024@huroorkee.ac.in"
    print("Typing email character by character...")
    inp.clear()
    for ch in email:
        inp.send_keys(ch)
        time.sleep(0.02)
    
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", inp)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", inp)
    time.sleep(1)

    btn = driver.find_element(By.XPATH, "//button[contains(@class, 'login-btn')]")
    print("Button enabled:", btn.is_enabled())
    print("Button text:", btn.text)
    
    # Try normal click and js click
    try:
        btn.click()
    except Exception as e:
        print("Normal click failed:", e)
        driver.execute_script("arguments[0].click();", btn)

    time.sleep(3)

    # Print modal HTML or error messages
    modal = driver.find_elements(By.XPATH, "//div[contains(@class, 'login-modal') or contains(@class, 'modal-content') or contains(@class, 'MuiDialog') or contains(@class, 'login')]")
    for m in modal:
        if m.is_displayed():
            print("Modal displayed text:\n", m.text)

finally:
    driver.quit()

