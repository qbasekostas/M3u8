import sys
import time
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# --- Ρυθμίσεις για το GitHub Action ---
INSPECTION_URL = "https://miztv.top/stream/stream-622.php"
FIREFOX_BINARY_PATH = '/usr/bin/firefox'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
WAIT_SECONDS = 15 # Ο χρόνος αναμονής, μπορούμε να τον αυξήσουμε αν χρειαστεί

def discover_referer():
    """
    Πιστή μεταφορά της λογικής του αρχικού script.
    """
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.binary_location = FIREFOX_BINARY_PATH
    options.set_preference("general.useragent.override", USER_AGENT)

    driver = None
    try:
        driver = webdriver.Firefox(options=options)
        del driver.requests

        # 1. Επισκεπτόμαστε τη σελίδα
        driver.get(INSPECTION_URL)
        
        # 2. Περιμένουμε
        print(f"Waiting for {WAIT_SECONDS} seconds for network traffic...", file=sys.stderr)
        time.sleep(WAIT_SECONDS)
        
        # 3. Ψάχνουμε στα requests (από το τελευταίο προς το πρώτο)
        for request in reversed(driver.requests):
            if '.m3u8' in request.url and request.headers.get('Referer'):
                referer = request.headers['Referer'].strip('/')
                print(f"SUCCESS: Found Referer: {referer}", file=sys.stderr)
                # Τυπώνουμε ΜΟΝΟ το τελικό URL στην έξοδο
                print(referer)
                return # Χρησιμοποιούμε return για να βγούμε αμέσως

        # Αν φτάσουμε εδώ, αποτύχαμε
        print("ERROR: Could not find any .m3u8 request with a Referer header.", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: A critical exception occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    discover_referer()
