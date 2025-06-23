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
    player_domain = None
    
    try:
        # Δεν χρειάζεται πλέον το service, το Selenium θα βρει το geckodriver στο PATH
        driver = Firefox(options=options)
        driver.get(MIZTV_URL)
        
        print("Waiting for iframe to get a valid HTTP source...", file=sys.stderr)
        iframe_url = WebDriverWait(driver, 40).until(
            iframe_src_is_http((By.TAG_NAME, "iframe"))
        )
        
        player_domain = f"{urlparse(iframe_url).scheme}://{urlparse(iframe_url).netloc}"
        print(f"Found Player Domain: {player_domain}", file=sys.stderr)
        
    except Exception as e:
        print(f"ERROR during DOM observation phase: {e}", file=sys.stderr)
        if driver:
            driver.quit()
        sys.exit(1)
    finally:
        if driver:
            driver.quit()

    try:
        embed_url_for_api = f"{player_domain}/embed.php?id=stream-622"
        
        embed_page_content = requests.get(embed_url_for_api).text
        token_match = re.search(r'"token":\s*"([^"]+)"', embed_page_content)
        
        if not token_match:
            raise Exception("Could not find token on the embed page.")
                
        token = token_match.group(1)
        print(f"Found Token: {token}", file=sys.stderr)
        
        get_php_url = f"{player_domain}/get.php"
        headers = {'Referer': embed_url_for_api, 'X-Requested-With': 'XMLHttpRequest'}
        data = {'id': 'stream-622', 'token': token}
        
        api_response_json = requests.post(get_php_url, headers=headers, data=data).json()
        final_stream_url = api_response_json.get('url')
        
        if not final_stream_url:
             raise Exception("API response did not contain a 'url' key.")

        auth_url_match = re.search(r'(https?://.*?/auth\.php\?.*?)\#', final_stream_url)
        if not auth_url_match:
            raise Exception("Could not find the auth.php URL in the final stream URL.")
        
        auth_url = auth_url_match.group(1)
        print(f"Found Auth URL: {auth_url}", file=sys.stderr)
        
        requests.get(auth_url).raise_for_status()
        print("Successfully visited Auth URL. IP is now authorized.", file=sys.stderr)

        new_referer_domain = f"{urlparse(auth_url).scheme}://{urlparse(auth_url).netloc}/"
        
        print(f"SUCCESS: The new Referer is: {new_referer_domain}", file=sys.stderr)
        print(new_referer_domain)

    except Exception as e:
        print(f"ERROR during API call phase: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    find_final_referer()
