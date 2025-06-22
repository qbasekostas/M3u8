import sys
import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

INSPECTION_URL = "https://miztv.top/stream/stream-622.php"

def discover_referer():
    """
    Starts a headless Chrome, tries to find the Referer header, 
    and has a fallback method if that fails.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Navigating to inspection URL...")
        driver.get(INSPECTION_URL)
        
        # --- ΠΡΟΣΠΑΘΕΙΑ 1: Η μέθοδος με το network request (η προτιμώμενη) ---
        try:
            print("Waiting for iframe to be present...")
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            
            # Μπαίνουμε μέσα στο iframe
            driver.switch_to.frame(0)
            
            # Προσπαθούμε να κάνουμε κλικ στο body του iframe, μήπως ξεκινήσει το stream
            print("Attempting to click inside the iframe to trigger video...")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "body"))).click()
            
            print("Waiting for .m3u8 network request...")
            req = driver.wait_for_request(r'.*?\.m3u8', timeout=20)
            
            if req and req.headers.get('Referer'):
                print("SUCCESS (Method 1): Found Referer in network request.")
                print(req.headers['Referer'].strip('/'))
                return
        except Exception as e:
            print(f"INFO: Method 1 (network request) failed: {e}. Trying fallback method.")

        # --- ΠΡΟΣΠΑΘΕΙΑ 2: Μέθοδος Fallback (αν η πρώτη απέτυχε) ---
        # Επιστρέφουμε στο κυρίως περιεχόμενο της σελίδας
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

        # Αν φτάσουμε εδώ, τίποτα δεν δούλεψε
        print("ERROR: Both methods failed. Could not determine Referer.", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: A critical exception occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    discover_referer()
