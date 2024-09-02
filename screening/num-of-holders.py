import requests
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import remove_address_from_potential, add_address_to_blacklist

def main(base_token_address):

    solscan_cookie = os.getenv('SOLSCAN_COOKIE')
    if not solscan_cookie:
        remove_address_from_potential(base_token_address)
        add_address_to_blacklist(base_token_address)
        raise Exception("API key not found. Please add your SOLSCAN_COOKIE to the .env file")
    
    sol_aut = os.getenv('SOL_AUT')
    if not sol_aut:
        remove_address_from_potential(base_token_address)
        add_address_to_blacklist(base_token_address)
        raise Exception("API key not found. Please add your SOL_AUT to the .env file")
    
    url = f"https://api.solscan.io/v2/token/holders?token={base_token_address}&offset=0&size=1"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": solscan_cookie,
        "If-None-Match": 'W/"74d-zOuTCYGR/0cByRr2/qCIiJs/h/o"',
        "Origin": "https://solscan.io",
        "Priority": "u=1, i",
        "Referer": "https://solscan.io/",
        "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Sol-Aut": sol_aut,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            total_holders = data.get('data', {}).get('total', 0)

            if total_holders < 10 or total_holders > 2000:
                add_address_to_blacklist(base_token_address)
                remove_address_from_potential(base_token_address)
                print(f"Blacklisted: {base_token_address}.")
        else:
            print(f"Failed to fetch number of top holders. Blacklisting")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python num-of-holders.py <BaseTokenAddress>")
        sys.exit(1)

    base_token_address = sys.argv[1]
    main(base_token_address)
