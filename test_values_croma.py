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
    for test_val in ["7003533173", "debraj1849@gmail.com", "debrajshil.bcseiot2024@huroorkee.ac.in"]:
        print(f"\n================ TESTING: {test_val} ================")
        driver.get('https://www.croma.com')
        time.sleep(3)

        user_link = driver.find_element(By.XPATH, "//a[contains(@class, 'user-link')]")
        driver.execute_script("arguments[0].click();", user_link)
        time.sleep(2)

        inp = driver.find_element(By.XPATH, "//input[contains(@class, 'input-login')]")
        inp.clear()
        inp.send_keys(test_val)
        time.sleep(1)

        btn = driver.find_element(By.XPATH, "//button[contains(@class, 'login-btn')]")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(3)

        # Check for error or OTP
        modals = driver.find_elements(By.XPATH, "//div[contains(@class, 'desktop-modal-otp')]")
        for m in modals:
            if m.is_displayed():
                print("Modal output:\n", m.text)

        otp_boxes = driver.find_elements(By.XPATH, "//input[@id='partitioned' or contains(@class, 'otpinput')]")
        print("OTP Box found?:", len(otp_boxes) > 0)

finally:
    driver.quit()

