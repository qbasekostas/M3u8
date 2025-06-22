import sys
import time
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Ορίζουμε τις σταθερές μας
INSPECTION_URL = "https://miztv.top/stream/stream-622.php"
FIREFOX_BINARY_PATH = '/usr/bin/firefox'
WAIT_SECONDS = 15 # Δίνουμε λίγο παραπάνω χρόνο για το περιβάλλον του GitHub

def find_referer_simple():
    """
    Ακολουθεί την απλή λογική: επισκέπτεται τη σελίδα, περιμένει,
    και ψάχνει στα network requests για το σωστό Referer.
    """
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.binary_location = FIREFOX_BINARY_PATH
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0")

    driver = None
    try:
        driver = webdriver.Firefox(options=options)
        
        # Καθαρίζουμε τα προηγούμενα requests για σιγουριά
        del driver.requests
        
        # 1. Επισκεπτόμαστε τη σελίδα
        driver.get(INSPECTION_URL)
        
        # 2. Περιμένουμε απλά (η κρίσιμη αλλαγή)
        # Τυπώνουμε τα διαγνωστικά μηνύματα στο stderr για να μην "μολύνουν" την έξοδο
        print(f"Waiting for {WAIT_SECONDS} seconds for network traffic to be captured...", file=sys.stderr)
        time.sleep(WAIT_SECONDS)
        
        # 3. Ψάχνουμε στα requests
        for request in reversed(driver.requests):
            if '.m3u8' in request.url and request.headers.get('Referer'):
                referer = request.headers['Referer'].strip('/')
                print(f"SUCCESS: Found Referer: {referer}", file=sys.stderr)
                # Τυπώνουμε ΜΟΝΟ το τελικό URL στην έξοδο για να το πιάσει το Action
                print(referer)
                sys.exit(0) # Βγαίνουμε με επιτυχία

        # Αν ο βρόχος τελειώσει χωρίς αποτέλεσμα, σημαίνει αποτυχία.
        print("ERROR: Could not find any .m3u8 request with a Referer header.", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: A critical exception occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    find_referer_simple()
