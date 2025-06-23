import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver import Firefox
from urllib.parse import urlparse
import requests
import re

# --- Ρυθμίσεις ---
MIZTV_URL = "https://miztv.top/stream/stream-622.php"
FIREFOX_BINARY_PATH = '/usr/bin/firefox'

class iframe_src_is_http:
    """Περιμένει μέχρι το src του iframe να αρχίζει με 'http'."""
    def __init__(self, locator):
        self.locator = locator
    def __call__(self, driver):
        try:
            src = driver.find_element(*self.locator).get_attribute('src')
            if src and src.startswith('http'):
                return src
            return False
        except:
            return False

def find_final_referer():
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.binary_location = FIREFOX_BINARY_PATH
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0")

    driver = None
    try:
        # --- ΒΗΜΑ 1: ΒΡΙΣΚΟΥΜΕ ΤΟ DOMAIN ΤΟΥ PLAYER ---
        driver = Firefox(options=options)
        driver.get(MIZTV_URL)
        
        print("Waiting for iframe to get a valid HTTP source...", file=sys.stderr)
        iframe_url = WebDriverWait(driver, 40).until(
            iframe_src_is_http((By.TAG_NAME, "iframe"))
        )
        
        # Εξάγουμε το domain (π.χ. https://allupplay.xyz)
        player_domain = f"{urlparse(iframe_url).scheme}://{urlparse(iframe_url).netloc}"
        print(f"Found Player Domain: {player_domain}", file=sys.stderr)
        
    finally:
        if driver:
            driver.quit()

    # --- ΒΗΜΑ 2: ΧΡΗΣΙΜΟΠΟΙΟΥΜΕ ΤΗ ΜΕΘΟΔΟ DREWLIVE ΜΕ ΤΟ ΣΩΣΤΟ DOMAIN ---
    try:
        embed_url_for_api = f"{player_domain}/embed.php?id=stream-622"
        
        # Παίρνουμε το περιεχόμενο του embed για να βρούμε το token
        embed_page_content = requests.get(embed_url_for_api).text
        token_match = re.search(r'"token":\s*"([^"]+)"', embed_page_content)
        
        if not token_match:
            raise Exception("Could not find token on the embed page.")
            
        token = token_match.group(1)
        print(f"Found Token: {token}", file=sys.stderr)
        
        # Κάνουμε την κλήση στο get.php API
        get_php_url = f"{player_domain}/get.php"
        headers = {
            'Referer': embed_url_for_api,
            'X-Requested-With': 'XMLHttpRequest',
        }
        data = {'id': 'stream-622', 'token': token}
        
        api_response = requests.post(get_php_url, headers=headers, data=data).text
        
        # Εξάγουμε το τελικό URL του referer
        final_referer_match = re.search(r'Referer=([^&]+)', api_response)

        if not final_referer_match:
            raise Exception("Could not find the final Referer in the API response.")

        final_referer = final_referer_match.group(1)
        print(f"SUCCESS: Found Final Referer: {final_referer}", file=sys.stderr)
        
        # Τυπώνουμε ΜΟΝΟ το τελικό αποτέλεσμα
        print(final_referer)

    except Exception as e:
        print(f"ERROR during API call phase: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    find_final_referer()
