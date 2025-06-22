import sys
import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver import FirefoxProfile

INSPECTION_URL = "https://miztv.top/stream/stream-622.php"
FIREFOX_BINARY_PATH = '/usr/bin/firefox' # Η διαδρομή για το εκτελέσιμο του Firefox

def discover_referer():
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = FIREFOX_BINARY_PATH
    
    profile = FirefoxProfile()
    profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0")

    driver = webdriver.Firefox(options=options, firefox_profile=profile)
    
    try:
        print(f"Navigating to inspection URL: {INSPECTION_URL}")
        driver.get(INSPECTION_URL)
        
        try:
            print("Waiting for iframe to be present...")
            iframe = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            
            print("Switching to iframe...")
            driver.switch_to.frame(iframe)
            
            print("Attempting to click inside the iframe to trigger video...")
            body = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "body")))
            body.click()
            
            print("Waiting up to 30 seconds for .m3u8 network request...")
            req = driver.wait_for_request(r'.*?\.m3u8', timeout=30)
            
            if req and req.headers.get('Referer'):
                referer = req.headers['Referer'].strip('/')
                print(f"SUCCESS (Method 1): Found Referer in network request: {referer}")
                print(referer)
                return
        except Exception as e:
            import traceback
            print(f"INFO: Method 1 (network request) failed: {e}\n{traceback.format_exc()}\nTrying fallback.")

        driver.switch_to.default_content()
        print("Fallback: Finding iframe source URL...")
        
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        iframe_src = iframe.get_attribute('src')
        
        if iframe_src:
            from urllib.parse import urlparse
            parsed_url = urlparse(iframe_src)
            origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
            print(f"SUCCESS (Method 2): Found Referer from iframe src: {origin}")
            print(origin)
            return

        print("ERROR: Both methods failed. Could not determine Referer.", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        import traceback
        print(f"ERROR: A critical exception occurred: {e}\n{traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    discover_referer()
