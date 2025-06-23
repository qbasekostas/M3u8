import sys
import re
import requests
from urllib.parse import urlparse

# --- Η ΠΗΓΗ ΤΗΣ ΑΛΗΘΕΙΑΣ ---
# Το API που μας δίνει τα τρέχοντα ενεργά domains.
CENTRAL_API_URL = "https://tinyurl.is/api.json"

def get_final_referer():
    """
    1. Παίρνει τα ενεργά domains από το κεντρικό API.
    2. Δοκιμάζει ένα-ένα τα domains μέχρι να βρει ένα που λειτουργεί.
    3. Εξάγει και επιστρέφει το τελικό Referer.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://miztv.top/" # Ένα γενικό referer για να μοιάζουμε legit
    })

    # --- ΒΗΜΑ 1: Πάρε τα ενεργά domains από το API ---
    try:
        print("Fetching active player domains from Central API...", file=sys.stderr)
        api_data = session.get(CENTRAL_API_URL, timeout=15).json()
        # Δημιουργούμε μια λίστα από τα URLs, αγνοώντας τα κλειδιά
        player_domains = [f"https://{domain}" for domain in api_data.values() if isinstance(domain, str) and '.' in domain]
        if not player_domains:
            raise ValueError("Central API did not return any valid domains.")
        print(f"Found {len(player_domains)} potential domains: {player_domains}", file=sys.stderr)
    except Exception as e:
        print(f"FATAL ERROR: Could not fetch or parse the Central API: {e}", file=sys.stderr)
        sys.exit(1)

    # --- ΒΗΜΑ 2: Δοκιμή των domains ένα-ένα ---
    for domain in player_domains:
        try:
            print(f"Testing domain: {domain} ...", file=sys.stderr)
            
            # Ακολουθούμε την γνωστή διαδικασία με token και get.php
            embed_url = f"{domain}/embed.php?id=stream-622"
            embed_content = session.get(embed_url, timeout=15).text
            token = re.search(r'"token":\s*"([^"]+)"', embed_content).group(1)

            api_url = f"{domain}/get.php"
            api_headers = {'Referer': embed_url, 'X-Requested-With': 'XMLHttpRequest'}
            api_data = {'id': 'stream-622', 'token': token}
            
            api_response = session.post(api_url, headers=api_headers, data=api_data, timeout=15).json()
            final_stream_url = api_response.get('url')
            
            if not final_stream_url: continue

            auth_url = re.search(r'(https?://.*?/auth\.php\?.*?)(?:#|$)', final_stream_url).group(1)
            
            # Εξουσιοδότηση IP
            session.get(auth_url, timeout=15).raise_for_status()
            
            # Εξαγωγή του τελικού Referer
            new_referer_domain = f"{urlparse(auth_url).scheme}://{urlparse(auth_url).netloc}/"
            
            print(f"SUCCESS! Found working Referer: {new_referer_domain}", file=sys.stderr)
            # Τυπώνουμε το αποτέλεσμα και τελειώνουμε
            print(new_referer_domain)
            return

        except Exception as e:
            print(f"  -> Domain '{domain}' failed, trying next. Reason: {type(e).__name__}", file=sys.stderr)
            continue
    
    # Αν φτάσουμε εδώ, κανένα από τα ενεργά domains δεν λειτούργησε
    print("FATAL ERROR: None of the active domains from the API are working.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    get_final_referer()
