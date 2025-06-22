import sys
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions

INSPECTION_URL = "https://miztv.top/stream/stream-622.php"
FIREFOX_BINARY_PATH = '/usr/bin/firefox'

def discover_referer():
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.binary_location = FIREFOX_BINARY_PATH
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0")

    driver = webdriver.Firefox(options=options)
    
    final_referer = None
    
    try:
        driver.get(INSPECTION_URL)
        
        # Προσπάθεια 1: Network Request
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            driver.switch_to.frame(0)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "body"))).click()
            req = driver.wait_for_request(r'.*?\.m3u8', timeout=25)
            if req and req.headers.get('Referer'):
                final_referer = req.headers['Referer'].strip('/')
        except Exception:
            pass # Απλά συνεχίζουμε στην επόμενη μέθοδο

        # Προσπάθεια 2: Fallback στο iframe src (ΜΟΝΟ αν η πρώτη απέτυχε)
        if not final_referer:
            driver.switch_to.default_content()
            iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            iframe_src = iframe.get_attribute('src')
            # Ελέγχουμε αν είναι έγκυρο HTTP URL
            if iframe_src and iframe_src.startswith('http'):
                from urllib.parse import urlparse
                parsed_url = urlparse(iframe_src)
                final_referer = f"{parsed_url.scheme}://{parsed_url.netloc}"

    except Exception as e:
        # Τυπώνουμε το σφάλμα μόνο αν κάτι πάει πολύ στραβά
        print(f"A critical error occurred: {e}", file=sys.stderr)
    finally:
        driver.quit()
        if final_referer:
            # Τυπώνουμε ΜΟΝΟ το τελικό αποτέλεσμα
            print(final_referer)
        else:
            # Αν δεν βρέθηκε τίποτα, βγαίνουμε με σφάλμα
            sys.exit(1)

if __name__ == "__main__":
    discover_referer()
