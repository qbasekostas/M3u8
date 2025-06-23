import sys
import re
import requests
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urlparse

# --- Ρυθμίσεις ---
MIZTV_URL = "https://miztv.top/stream/stream-622.php"
FIREFOX_BINARY_PATH = '/usr/bin/firefox'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"

class iframe_src_is_http:
    """Custom wait condition: waits for iframe src to be a valid http(s) url."""
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

def main():
    player_domain = None
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.binary_location = FIREFOX_BINARY_PATH
    options.set_preference("general.useragent.override", USER_AGENT)

    # --- ΒΗΜΑ 1: Βρες το domain του player από το miztv.top ---
    driver = None
    try:
        driver = Firefox(options=options)
        driver.get(MIZTV_URL)
        print("Waiting for iframe to get a valid HTTP source...", file=sys.stderr)
        iframe_url = WebDriverWait(driver, 40).until(iframe_src_is_http((By.TAG_NAME, "iframe")))
        player_domain = f"{urlparse(iframe_url).scheme}://{urlparse(iframe_url).netloc}"
        print(f"Found Player Domain: {player_domain}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR during DOM observation phase: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if driver:
            driver.quit()
            
    if not player_domain:
        print("ERROR: Could not determine player domain.", file=sys.stderr)
        sys.exit(1)

    # --- ΒΗΜΑ 2: Ακολούθησε τη μέθοδο DrewLive για να πάρεις το Auth URL ---
    try:
        embed_url = f"{player_domain}/embed.php?id=stream-622"
        embed_content = requests.get(embed_url, headers={'Referer': MIZTV_URL}).text
        token = re.search(r'"token":\s*"([^"]+)"', embed_content).group(1)
        print(f"Found Token: {token}", file=sys.stderr)

        api_url = f"{player_domain}/get.php"
        api_headers = {'Referer': embed_url, 'X-Requested-With': 'XMLHttpRequest'}
        api_data = {'id': 'stream-622', 'token': token}
        
        # Το api_response περιέχει το τελικό stream URL με το auth.php μέσα
        api_response_json = requests.post(api_url, headers=api_headers, data=api_data).json()
        final_stream_url = api_response_json.get('url')
        
        if not final_stream_url:
             raise Exception("API response did not contain a 'url' key.")

        # --- ΒΗМА 3: Εξαγωγή του auth.php και εξουσιοδότηση ---
        auth_url_match = re.search(r'(https?://.*?/auth\.php\?.*?)\#', final_stream_url)
        if not auth_url_match:
            raise Exception("Could not find the auth.php URL in the final stream URL.")
        
        auth_url = auth_url_match.group(1)
        print(f"Found Auth URL: {auth_url}", file=sys.stderr)
        
        # Επισκεπτόμαστε το Auth URL για να εξουσιοδοτήσουμε την IP
        auth_response = requests.get(auth_url)
        auth_response.raise_for_status() # Θα πετάξει σφάλμα αν η επίσκεψη αποτύχει
        print("Successfully visited Auth URL. IP is now authorized.", file=sys.stderr)

        # --- ΒΗΜΑ 4: Εξαγωγή του νέου Referer και έξοδος ---
        # Ο νέος Referer είναι το domain του auth.php
        new_referer_domain = f"{urlparse(auth_url).scheme}://{urlparse(auth_url).netloc}/"
        
        print(f"SUCCESS: The new Referer is: {new_referer_domain}", file=sys.stderr)
        # Τυπώνουμε ΜΟΝΟ το τελικό αποτέλεσμα για το workflow
        print(new_referer_domain)

    except Exception as e:
        print(f"ERROR during API/Auth phase: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
