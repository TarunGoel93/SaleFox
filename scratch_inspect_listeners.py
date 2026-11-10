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

    info = driver.execute_script("""
        let b = document.querySelector('button[name="add-to-cart"]');
        let f = b ? b.closest('form') : null;
        
        // Let's check window global objects for cart/bag
        let globals = Object.keys(window).filter(k => k.toLowerCase().includes('bag') || k.toLowerCase().includes('cart') || k.toLowerCase().includes('aos'));
        
        return {
            hasButton: !!b,
            buttonText: b ? b.innerText : null,
            formAction: f ? f.action : null,
            globals: globals
        };
    """)
    print("Info:", info)

    # Let's inspect how Chrome DevTools or React handles it
    react_info = driver.execute_script("""
        let b = document.querySelector('button[name="add-to-cart"]');
        if (!b) return "No button";
        let reactPropsKey = Object.keys(b).find(k => k.startsWith('__reactProps') || k.startsWith('__reactEventHandlers') || k.startsWith('__reactFiber'));
        if (reactPropsKey) {
            let props = b[reactPropsKey];
            return {
                reactKey: reactPropsKey,
                hasOnClick: !!props.onClick,
                keys: Object.keys(props)
            };
        }
        return "No react props directly on button";
    """)
    print("React info on button:", react_info)

    # Let's check react info on parent form
    react_form = driver.execute_script("""
        let f = document.querySelector('form[data-feature-name="Step1"]') || (document.querySelector('button[name="add-to-cart"]') ? document.querySelector('button[name="add-to-cart"]').closest('form') : null);
        if (!f) return "No form";
        let reactPropsKey = Object.keys(f).find(k => k.startsWith('__reactProps') || k.startsWith('__reactEventHandlers') || k.startsWith('__reactFiber'));
        if (reactPropsKey) {
            let props = f[reactPropsKey];
            return {
                reactKey: reactPropsKey,
                hasOnSubmit: !!props.onSubmit,
                keys: Object.keys(props)
            };
        }
        return "No react props on form";
    """)
    print("React form info:", react_form)

finally:
    driver.quit()
