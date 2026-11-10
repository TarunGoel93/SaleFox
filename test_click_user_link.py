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

    # Click specifically a.user-link
    user_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'user-link')]")
    print(f"User links found: {len(user_links)}")
    for ul in user_links:
        print("Clicking a.user-link...")
        driver.execute_script("arguments[0].click();", ul)
        time.sleep(2)
        break

    # Check for login inputs
    inps = driver.find_elements(By.XPATH, "//input[contains(@class, 'input-login')]")
    print(f"Login inputs found: {len(inps)}")
    for i in inps:
        print(f"Input visible: {i.is_displayed()}")
        if i.is_displayed():
            email = "debrajshil.bcseiot2024@huroorkee.ac.in"
            print(f"Typing email {email}...")
            i.clear()
            i.send_keys(email)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", i)
            time.sleep(1)

            btn = driver.find_element(By.XPATH, "//button[contains(@class, 'login-btn')]")
            print("Clicking Continue:", btn.text)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(4)

            # Check for OTP partitioned input
            otp_boxes = driver.find_elements(By.XPATH, "//input[@id='partitioned' or contains(@class, 'otpinput')]")
            print(f"OTP boxes: {len(otp_boxes)}")
            for o in otp_boxes:
                print(f"OTP box visible: {o.is_displayed()}")

            body_text = driver.find_element(By.TAG_NAME, 'body').text
            for line in body_text.splitlines():
                if any(w in line.lower() for w in ['otp', 'verify', 'sent', 'resend', 'seconds', 'error']):
                    print("OTP Line:", line.strip())

finally:
    driver.quit()

