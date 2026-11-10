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
    driver.get('https://www.croma.com/login')
    time.sleep(4)

    inp = driver.find_element(By.XPATH, "//input[contains(@class, 'input-login') or contains(@placeholder, 'Email ID or phone number')]")
    print('Found login input:', inp.get_attribute('placeholder'))

    test_emails = [
        "debrajshil.bcseiot2024@huroorkee.ac.in",
        "debraj1849@gmail.com"
    ]

    for email in test_emails:
        print(f"\n--- TESTING EMAIL: {email} ---")
        driver.get('https://www.croma.com/login')
        time.sleep(3)
        inp = driver.find_element(By.XPATH, "//input[contains(@class, 'input-login') or contains(@placeholder, 'Email ID or phone number')]")
        inp.clear()
        inp.send_keys(email)
        time.sleep(1)

        btn = driver.find_element(By.XPATH, "//button[contains(@class, 'login-btn')]")
        print('Clicking Continue...')
        driver.execute_script('arguments[0].click();', btn)
        time.sleep(3)

        # Check for error or OTP
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        matched = []
        for line in body_text.splitlines():
            if any(k in line.lower() for k in ['otp', 'sent', 'error', 'invalid', 'wait', 'seconds', 'verify', 'resend']):
                matched.append(line.strip())
        print("Page response:")
        for m in matched[:10]:
            print("  ->", m)

        # Check if partitioned OTP input exists
        otp_boxes = driver.find_elements(By.XPATH, "//input[@id='partitioned' or contains(@class, 'otpinput')]")
        print(f"OTP Box present: {len(otp_boxes) > 0}")

finally:
    driver.quit()

