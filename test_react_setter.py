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
    driver.get('https://www.croma.com')
    time.sleep(4)

    user_link = driver.find_element(By.XPATH, "//a[contains(@class, 'user-link')]")
    driver.execute_script("arguments[0].click();", user_link)
    time.sleep(2)

    email = "debrajshil.bcseiot2024@huroorkee.ac.in"
    
    # Inject via React Native Input Setter
    js_inject = """
    const input = document.querySelector('input.input-login');
    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    nativeSetter.call(input, arguments[0]);
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    """
    driver.execute_script(js_inject, email)
    time.sleep(1)

    # Click Continue
    btn = driver.find_element(By.XPATH, "//button[contains(@class, 'login-btn')]")
    print("Clicking Continue...")
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(4)

    # Check modal text
    modal = driver.find_elements(By.XPATH, "//div[contains(@class, 'desktop-modal-otp') or contains(@class, 'MuiDialog-paper')]")
    for m in modal:
        if m.is_displayed():
            print("--- MODAL TEXT AFTER INJECTION ---")
            print(m.text)

finally:
    driver.quit()

