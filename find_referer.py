import sys
import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options

INSPECTION_URL = "https://miztv.top/stream/stream-622.php"

def discover_referer():
    """
    Starts a headless Chrome browser, captures network traffic,
    and prints the Referer header from the first .m3u8 request.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    
    # Use selenium-wire's webdriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(INSPECTION_URL)
        # Wait for the specific request containing .m3u8
        req = driver.wait_for_request(r'.*?\.m3u8', timeout=45)
        
        if req and req.headers.get('Referer'):
            # Print the Referer URL to standard output
            # We remove any trailing slash for consistency
            print(req.headers['Referer'].strip('/'))
        else:
            # Print to standard error if not found
            print("ERROR: Referer header not found in M3U8 request.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: An exception occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    discover_referer()
