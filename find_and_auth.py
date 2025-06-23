import sys
import re
import requests
from urllib.parse import urlparse

# --- Η ΑΡΧΙΚΗ ΠΗΓΗ ΠΛΗΡΟΦΟΡΙΩΝ ---
MIZTV_URL = "https://miztv.top/stream/stream-622.php"

def find_player_domain():
    """
    1. Παίρνει το HTML του miztv.
    2. Βρίσκει το domain του player από το iframe.
    3. Επιστρέφει ΑΥΤΟ το domain.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    })

    try:
        print(f"Fetching main page to find iframe: {MIZTV_URL}", file=sys.stderr)
        miztv_content = session.get(MIZTV_URL, timeout=25).text
        
        # Χρησιμοποιούμε regular expression για να βρούμε το src του iframe
        iframe_src_match = re.search(r'iframe\s+src="([^"]+)"', miztv_content)
        if not iframe_src_match:
            raise ValueError("Could not find iframe src in the main page HTML.")
            
        iframe_url = iframe_src_match.group(1)
        # Εξάγουμε το domain (π.χ. https://forcedtoplay.xyz)
        player_domain = f"{urlparse(iframe_url).scheme}://{urlparse(iframe_url).netloc}/"
        
        print(f"SUCCESS! Dynamically discovered player domain: {player_domain}", file=sys.stderr)
        # Τυπώνουμε ΜΟΝΟ το τελικό αποτέλεσμα
        print(player_domain)

    except Exception as e:
        print(f"FATAL ERROR: The process failed. Details: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    find_player_domain()
