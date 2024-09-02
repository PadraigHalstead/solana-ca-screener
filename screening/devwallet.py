import sys
import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import save_addresses_to_csv, load_addresses_from_csv, add_address_to_blacklist, remove_address_from_potential

def call_solscan_api(dev_address, base_token_address):

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
    
    
    url = f"https://api.solscan.io/v2/account/v2/tokens?address={dev_address}"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cookie": solscan_cookie,
        "Origin": "https://solscan.io",
        "Priority": "u=1, i",
        "Referer": "https://solscan.io/",
        "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Sol-Aut": sol_aut,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    return response

def main():
    if len(sys.argv) < 2:
        print("Usage: python devwallet.py <BaseTokenAddress>")
        sys.exit(1)

    base_token_address = sys.argv[1]

    with open('./extracted_data.json', 'r') as file:
        extracted_data = json.load(file)

    entry = next((item for item in extracted_data if item["mint"] == base_token_address), None)
    
    if entry:
        dev_address = entry.get("dev")
        token_supply = entry.get("token_supply")

        if not dev_address or token_supply is None:
            print("Required data missing in the extracted data")
            sys.exit(1)

        if dev_address == "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM":
            #extra logic
            #top holders - look through top 20 for "devwallet" - set as new dev wallet
            sys.exit(0)

        response = call_solscan_api(dev_address, base_token_address)

        try:
            content = response.text
            response_data = json.loads(content)

            if response_data.get('data', {}).get('count', 0) == 0:
                print("No tokens")
                return

            tokens = response_data.get('data', {}).get('tokens', [])
            amount = None
            for token in tokens:
                if token.get('tokenAddress') == base_token_address:
                    amount = token.get('amount')
                    break

            if amount is not None:
                percentage = (amount / token_supply) * 100
                if percentage > 6:
                    blacklist_addresses = load_addresses_from_csv('./lists/blacklist.csv')
                    potential_addresses = load_addresses_from_csv('./lists/potential.csv')
                    
                    if base_token_address in potential_addresses:
                        remove_address_from_potential(base_token_address)
                        add_address_to_blacklist(base_token_address)
                    
                    save_addresses_to_csv(potential_addresses)
                    save_addresses_to_csv(blacklist_addresses)
                    print(f"Blacklisted: {base_token_address}.")

        except ValueError as e:
            print("Failed to calculate dev %")
            remove_address_from_potential(base_token_address)
            add_address_to_blacklist(base_token_address)
            print("Response Content:", response.content)

if __name__ == "__main__":
    main()
