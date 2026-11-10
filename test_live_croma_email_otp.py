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

    # 1. Click user link to open login modal
    user_btn = driver.find_element(By.XPATH, "//a[contains(@class, 'user-link')] | //div[contains(@class, 'custom-login')]")
    print("Clicking user link...")
    driver.execute_script("arguments[0].click();", user_btn)
    time.sleep(2)

    # 2. Find login input
    inps = driver.find_elements(By.XPATH, "//input[contains(@class, 'input-login')]")
    vis = [i for i in inps if i.is_displayed()]
    if not vis:
        print("ERROR: input-login not visible!")
    else:
        inp = vis[0]
        email = "debrajshil.bcseiot2024@huroorkee.ac.in"
        print(f"Entering email: {email}")
        inp.clear()
        inp.send_keys(email)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", inp)
        time.sleep(1)

        # 3. Click Continue
        cont_btns = driver.find_elements(By.XPATH, "//button[contains(@class, 'login-btn')] | //button[contains(., 'Continue')]")
        cont_vis = [b for b in cont_btns if b.is_displayed()]
        if cont_vis:
            print("Clicking Continue button:", cont_vis[0].text)
            driver.execute_script("arguments[0].click();", cont_vis[0])
            time.sleep(4)

            # Check if OTP screen is active
            otp_boxes = driver.find_elements(By.XPATH, "//input[@id='partitioned' or contains(@class, 'otpinput')]")
            print("OTP boxes count:", len(otp_boxes))
            for o in otp_boxes:
                print("OTP Box displayed:", o.is_displayed())

            # Print text
            body_text = driver.find_element(By.TAG_NAME, 'body').text
            for line in body_text.splitlines():
                if any(w in line.lower() for w in ['otp', 'verify', 'sent', 'resend', 'seconds']):
                    print("OTP Line:", line.strip())

finally:
    driver.quit()

