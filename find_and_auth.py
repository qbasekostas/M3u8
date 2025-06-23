import sys
import re
import requests
from urllib.parse import urlparse

# --- Η ΑΡΧΙΚΗ ΠΗΓΗ ΠΛΗΡΟΦΟΡΙΩΝ ---
MIZTV_URL = "https://miztv.top/stream/stream-622.php"

def find_referer_the_right_way():
    """
    1. Παίρνει το HTML του miztv.
    2. Βρίσκει το domain του player από το iframe.
    3. Εκτελεί τη διαδικασία API.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    })

    try:
        # --- ΒΗΜΑ 1: Βρες το domain του player από την πηγαία σελίδα ---
        print(f"Fetching main page: {MIZTV_URL}", file=sys.stderr)
        miztv_content = session.get(MIZTV_URL, timeout=20).text
        
        # Χρησιμοποιούμε regular expression για να βρούμε το src του iframe
        iframe_src_match = re.search(r'iframe\s+src="([^"]+)"', miztv_content)
        if not iframe_src_match:
            raise ValueError("Could not find iframe src in the main page HTML.")
            
        iframe_url = iframe_src_match.group(1)
        player_domain = f"{urlparse(iframe_url).scheme}://{urlparse(iframe_url).netloc}"
        print(f"Dynamically discovered Player Domain: {player_domain}", file=sys.stderr)

        # --- ΒΗΜΑ 2: Ακολούθησε τη διαδικασία API με το σωστό domain ---
        embed_url = f"{player_domain}/embed.php?id=stream-622"
        embed_content = session.get(embed_url, headers={'Referer': MIZTV_URL}, timeout=20).text
        token = re.search(r'"token":\s*"([^"]+)"', embed_content).group(1)
        print(f"Found Token: {token}", file=sys.stderr)

        api_url = f"{player_domain}/get.php"
        api_headers = {'Referer': embed_url, 'X-Requested-With': 'XMLHttpRequest'}
        api_data = {'id': 'stream-622', 'token': token}
        
        api_response = session.post(api_url, headers=api_headers, data=api_data, timeout=20).json()
        final_stream_url = api_response.get('url')
        if not final_stream_url:
            raise ValueError("API response did not contain a 'url' key.")

        # --- ΒΗΜΑ 3: Εξουσιοδότηση και εξαγωγή τελικού Referer ---
        auth_url = re.search(r'(https?://.*?/auth\.php\?.*?)(?:#|$)', final_stream_url).group(1)
        session.get(auth_url, timeout=20).raise_for_status()
        
        new_referer_domain = f"{urlparse(auth_url).scheme}://{urlparse(auth_url).netloc}/"
        
        print(f"SUCCESS! New Referer is: {new_referer_domain}", file=sys.stderr)
        # Τυπώνουμε ΜΟΝΟ το τελικό αποτέλεσμα
        print(new_referer_domain)

    except Exception as e:
        print(f"FATAL ERROR: The process failed. Details: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    find_referer_the_right_way()
