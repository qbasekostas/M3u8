import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver import Firefox
from urllib.parse import urlparse

# --- Ρυθμίσεις ---
INSPECTION_URL = "https://miztv.top/stream/stream-622.php"
FIREFOX_BINARY_PATH = '/usr/bin/firefox'

class iframe_src_is_http:
    """
    Μια προσαρμοσμένη συνθήκη αναμονής του Selenium.
    Περιμένει μέχρι το src του iframe να αρχίζει με 'http'.
    """
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            iframe = driver.find_element(*self.locator)
            src = iframe.get_attribute('src')
            if src and src.startswith('http'):
                return src  # Επιστρέφει το URL όταν το βρει
            return False
        except:
            return False

def get_referer_by_observing_dom():
    """
    Ξεκινά τον browser και περιμένει μέχρι να εμφανιστεί το πραγματικό URL του iframe.
    """
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.binary_location = FIREFOX_BINARY_PATH
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0")

    driver = None
    try:
        # ΣΗΜΑΝΤΙΚΗ ΑΛΛΑΓΗ: Χρησιμοποιούμε το κανονικό Selenium, όχι το selenium-wire
        driver = Firefox(options=options)
        driver.get(INSPECTION_URL)

        # Περιμένουμε μέχρι και 35 δευτερόλεπτα χρησιμοποιώντας τη νέα μας συνθήκη
        print("Waiting up to 35 seconds for the iframe src to become a valid HTTP URL...", file=sys.stderr)
        
        iframe_real_src = WebDriverWait(driver, 35).until(
            iframe_src_is_http((By.TAG_NAME, "iframe"))
        )
        
        # Εξάγουμε το domain (origin) από το URL που βρήκαμε
        parsed_url = urlparse(iframe_real_src)
        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        print(f"SUCCESS: Found Referer by observing the iframe: {origin}", file=sys.stderr)
        
        # Τυπώνουμε ΜΟΝΟ το τελικό αποτέλεσμα
        print(origin)

    except Exception as e:
        print(f"ERROR: Failed to get a valid iframe src. The site may be down or has changed significantly. Details: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    get_referer_by_observing_dom()
