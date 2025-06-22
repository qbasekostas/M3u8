import sys
import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions

INSPECTION_URL = "https://miztv.top/stream/stream-622.php"

def discover_referer():
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0")
    driver = webdriver.Firefox(options=options)

    try:
        driver.get(INSPECTION_URL)
        iframe = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        body = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "body")))
        body.click()
        req = driver.wait_for_request(r'.*?\.m3u8', timeout=30)
        if req and req.headers.get('Referer'):
            referer = req.headers['Referer'].rstrip('/')
            print(referer)
            return
        # Εναλλακτικά, πάρε src του iframe
        driver.switch_to.default_content()
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        iframe_src = iframe.get_attribute('src')
        if iframe_src:
            from urllib.parse import urlparse
            parsed_url = urlparse(iframe_src)
            origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
            print(origin)
            return
        print("ERROR: Could not determine Referer.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    discover_referer()
