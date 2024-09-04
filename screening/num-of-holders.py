import requests
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import remove_address_from_potential, add_address_to_blacklist
from config import solscan_cookie, ua_platform, user_agent

def main(base_token_address):  
    url = f"https://api-v2.solscan.io/v2/token/holder/total?address={base_token_address}"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": solscan_cookie, 
        "Origin": "https://solscan.io",
        "Referer": "https://solscan.io/",
        "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": ua_platform,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": user_agent,
        "Priority": "u=1, i"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            total_holders = data.get('data', 0)

            if total_holders < 10 or total_holders > 2000:
                add_address_to_blacklist(base_token_address)
                remove_address_from_potential(base_token_address)
                print(f"Blacklisted: {base_token_address}.")
        else:
            print(f"Failed to fetch number of top holders. Blacklisting")
            add_address_to_blacklist(base_token_address)
            remove_address_from_potential(base_token_address)

    except Exception as e:
        print(f"An error occurred: {e}")
        add_address_to_blacklist(base_token_address)
        remove_address_from_potential(base_token_address)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python num-of-holders.py <BaseTokenAddress>")
        sys.exit(1)

    base_token_address = sys.argv[1]
    main(base_token_address)
