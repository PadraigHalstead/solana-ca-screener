import requests
import json
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import remove_address_from_potential, add_address_to_blacklist
from pumpfundev import getpumpfundevwallet
from config import solscan_cookie, user_agent, ua_platform


def main(base_token_address):  
    try:
        with open('./extracted_data.json', 'r') as file:
            extracted_data = json.load(file)
        
        token = next((item for item in extracted_data if item["mint"] == base_token_address), None)
        if not token:
            print(f"No extracted data found for {base_token_address}.")
            return
        
        print("wasd")
        dev_address = token.get("dev")
        print(dev_address)

        if not dev_address:
            print(f"No dev address found for {base_token_address}.")
            remove_address_from_potential(base_token_address)
            add_address_to_blacklist(base_token_address)
            return
        
        if dev_address == "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM":
            dev_address = getpumpfundevwallet(base_token_address)
            if dev_address == "":
                print("Error getting dev address")
                remove_address_from_potential(base_token_address)
                add_address_to_blacklist(base_token_address)
                sys.exit(0)
            

        url = f"https://api.solscan.io/v2/account?address={dev_address}"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": solscan_cookie ,
            "Origin": "https://solscan.io",
            "Priority": "u=1, i",
            "Referer": "https://solscan.io/",
            "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": ua_platform,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": user_agent
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            lamports = data.get('data', {}).get('lamports', 0)

            # If dev sol > 10
            if lamports > 10000000000:
                add_address_to_blacklist(base_token_address)
                remove_address_from_potential(base_token_address)
                print(f"Blacklisted: {base_token_address}.")
        else:
            print(f"Failed to fetch data for {dev_address}. Status code: {response.status_code}")
            remove_address_from_potential(base_token_address)
            add_address_to_blacklist(base_token_address)

    except Exception as e:
        print(f"An error occurred: {e}")
        remove_address_from_potential(base_token_address)
        add_address_to_blacklist(base_token_address)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check-lamports.py <BaseTokenAddress>")
        sys.exit(1)

    base_token_address = sys.argv[1]
    main(base_token_address)
