import sys
import re
import requests
from urllib.parse import urlparse

# --- ΛΙΣΤΑ ΠΙΘΑΝΩΝ DOMAINS ΤΟΥ PLAYER ---
# Αυτή η λίστα είναι το κλειδί. Μπορούμε να την επεκτείνουμε στο μέλλον.
PLAYER_DOMAINS = [
    "https://allupplay.xyz",
    "https://streambtw.com",
    "https://liveon.sx",
    "https://tinyurl.is", # Προσθήκη από άλλα παρόμοια projects
    "https://ourplayer.xyz", # Προσθήκη από άλλα παρόμοια projects
]

def find_working_domain_and_get_referer():
    """
    Δοκιμάζει ένα-ένα τα domains ΜΟΝΟ με requests, χωρίς browser,
    μέχρι να βρει ένα που λειτουργεί.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    })

    for domain in PLAYER_DOMAINS:
        try:
            print(f"Testing domain: {domain} ...", file=sys.stderr)
            
            # ΒΗΜΑ 1: Πάρε το token από το embed.php
            embed_url = f"{domain}/embed.php?id=stream-622"
            # Προσθέτουμε ένα header Referer που δείχνει στο miztv, για να μοιάζει πιο "νόμιμο"
            embed_content = session.get(embed_url, headers={'Referer': 'https://miztv.top/'}, timeout=15).text
            token_match = re.search(r'"token":\s*"([^"]+)"', embed_content)
            
            if not token_match:
                print(f"  -> No token found. Skipping.", file=sys.stderr)
                continue
            
            token = token_match.group(1)

            # ΒΗΜΑ 2: Κάλεσε το get.php API
            api_url = f"{domain}/get.php"
            api_headers = {'Referer': embed_url, 'X-Requested-With': 'XMLHttpRequest'}
            api_data = {'id': 'stream-622', 'token': token}
            
            api_response = session.post(api_url, headers=api_headers, data=api_data, timeout=15).json()
            final_stream_url = api_response.get('url')
            
            if not final_stream_url:
                print(f"  -> API response has no 'url'. Skipping.", file=sys.stderr)
                continue

            # ΒΗΜΑ 3: Βρες το Auth URL και εξουσιοδότησε
            auth_url_match = re.search(r'(https?://.*?/auth\.php\?.*?)(?:#|$)', final_stream_url)
            if not auth_url_match:
                print(f"  -> Could not find auth.php URL. Skipping.", file=sys.stderr)
                continue

            auth_url = auth_url_match.group(1)
            
            session.get(auth_url, timeout=15).raise_for_status()
            
            # ΒΗΜΑ 4: Εξαγωγή του νέου Referer
            new_referer_domain = f"{urlparse(auth_url).scheme}://{urlparse(auth_url).netloc}/"
            
            print(f"SUCCESS! Found working domain '{domain}' and new Referer '{new_referer_domain}'", file=sys.stderr)
            print(new_referer_domain) # Τυπώνουμε το τελικό αποτέλεσμα και τελειώνουμε
            return

        except Exception as e:
            print(f"  -> Domain '{domain}' failed: {e}. Trying next.", file=sys.stderr)
            continue
    
    # Αν φτάσουμε εδώ, κανένα domain δεν λειτούργησε
    print("FATAL ERROR: None of the provided player domains are working.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    find_working_domain_and_get_referer()
