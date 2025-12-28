import sys
import re
import requests
from urllib.parse import urlparse

MIZTV_URL = "https://miztv.top/stream/stream-622.php"

def fetch_data():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    })

    try:
        # 1. Παίρνουμε τη σελίδα του Miztv για να βρούμε το iframe
        response = session.get(MIZTV_URL, timeout=20)
        iframe_match = re.search(r'iframe\s+src="([^"]+)"', response.text)
        if not iframe_match:
            return None, None, None
        
        iframe_url = iframe_match.group(1)
        player_domain = f"{urlparse(iframe_url).scheme}://{urlparse(iframe_url).netloc}/"

        # 2. Μπαίνουμε στο iframe για να πάρουμε το AUTH_TOKEN
        # Στέλνουμε Referer τη σελίδα που μας έδωσε το iframe
        player_page = session.get(iframe_url, headers={"Referer": MIZTV_URL}, timeout=20).text
        
        # Ψάχνουμε το AUTH_TOKEN ή το SESSION_TOKEN στον κώδικα Javascript
        token_match = re.search(r'AUTH_TOKEN\s*=\s*"([^"]+)"', player_page)
        if not token_match:
            token_match = re.search(r'SESSION_TOKEN\s*=\s*"([^"]+)"', player_page)

        if token_match:
            token = token_match.group(1)
            return token, player_domain, player_domain.rstrip('/')
        
        return None, player_domain, player_domain.rstrip('/')

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None, None, None

if __name__ == "__main__":
    token, ref, origin = fetch_data()
    if not token:
        print("FAILED")
        sys.exit(1)
    # Επιστροφή δεδομένων διαχωρισμένων με |
    print(f"{token}|{ref}|{origin}")
