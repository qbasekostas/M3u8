import sys
import re
import requests
from urllib.parse import urlparse

MIZTV_URL = "https://miztv.top/stream/stream-622.php"

def fetch_data():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
        "Referer": "https://miztv.top/"
    }

    try:
        # 1. Παίρνουμε τη σελίδα του Miztv για να βρούμε το iframe
        response = session.get(MIZTV_URL, headers=headers, timeout=20)
        iframe_match = re.search(r'iframe\s+src="([^"]+)"', response.text)
        if not iframe_match:
            return "ERROR", "NO_IFRAME", "NO_DOMAIN"
        
        iframe_url = iframe_match.group(1)
        player_domain = f"{urlparse(iframe_url).scheme}://{urlparse(iframe_url).netloc}/"

        # 2. Μπαίνουμε στο iframe για να πάρουμε το AUTH_TOKEN
        # Πρέπει να στείλουμε Referer το Miztv
        headers["Referer"] = MIZTV_URL
        player_page = session.get(iframe_url, headers=headers, timeout=20).text
        
        token_match = re.search(r'AUTH_TOKEN\s*=\s*"([^"]+)"', player_page)
        if not token_match:
            # Δοκιμή για το εναλλακτικό όνομα μεταβλητής
            token_match = re.search(r'SESSION_TOKEN\s*=\s*"([^"]+)"', player_page)

        if token_match:
            token = token_match.group(1)
            # Επιστρέφουμε: TOKEN, DOMAIN_WITH_SLASH, DOMAIN_WITHOUT_SLASH
            return token, player_domain, player_domain.rstrip('/')
        else:
            return "ERROR", "NO_TOKEN", player_domain

    except Exception as e:
        return "ERROR", str(e), "ERROR"

if __name__ == "__main__":
    token, ref, origin = fetch_data()
    if token == "ERROR":
        print(f"FAILED: {ref}")
        sys.exit(1)
    # Τυπώνουμε τα αποτελέσματα σε μία γραμμή για να τα πάρει το bash
    print(f"{token}|{ref}|{origin}")
