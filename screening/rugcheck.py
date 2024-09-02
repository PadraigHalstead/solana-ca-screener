import requests
import json
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import remove_address_from_potential, add_address_to_blacklist, load_addresses_from_csv, save_addresses_to_csv

def call_rugcheck_api(ca):
    url = f"https://api.rugcheck.xyz/v1/tokens/{ca}/report"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Rate limit exceeded, waiting for 10 seconds...")
        time.sleep(10)
        return call_rugcheck_api(ca)
    elif response.status_code == 502:
        time.sleep(0.5)
        return call_rugcheck_api(ca)
    else:
        print(f"Unknown error for token {base_token_address}. Blacklisting.")
        add_address_to_blacklist(base_token_address)
        remove_address_from_potential(base_token_address)
        return None

def extract_data(rugcheck_response):
    mint_authority = rugcheck_response["token"].get("mintAuthority", None)
    freeze_authority = rugcheck_response["token"].get("freezeAuthority", None)
    token_meta = rugcheck_response.get("tokenMeta", {})

    data = {
        "mint": rugcheck_response.get("mint", False),
        "mintAuthority": mint_authority,
        "freezeAuthority": freeze_authority,
        "dev": token_meta.get("updateAuthority", False),
        "token_supply": rugcheck_response["token"].get("supply", False),
        "mutable": token_meta.get("mutable", False)
    }

    if mint_authority is not None and mint_authority != '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1':
        return data, True
    elif freeze_authority is not None:
        return data, True
    elif token_meta.get("mutable", False):
        return data, True
    else:
        risks = rugcheck_response.get("risks", [])
        for risk in risks:
            if risk.get("name") == "Low Liquidity":
                return data, True
        return data, False

def process_base_token_address(base_token_address):
    blacklist_addresses = load_addresses_from_csv('./lists/blacklist.csv')
    potential_addresses = load_addresses_from_csv('./lists/potential.csv')

    if base_token_address in blacklist_addresses:
        print(f"Address {base_token_address} is already blacklisted.")
        return

    rugcheck_response = call_rugcheck_api(base_token_address)
    if rugcheck_response is None:
        return

    extracted_data, is_blacklisted = extract_data(rugcheck_response)

    try:
        with open('./extracted_data.json', 'w') as file:
            json.dump([], file) 

        with open('./extracted_data.json', 'w') as file:
            json.dump([extracted_data], file, indent=4)
    except Exception as e:
        print(f"Error updating extracted data file: {e}")

    if is_blacklisted:
        add_address_to_blacklist(base_token_address)
        remove_address_from_potential(base_token_address)
        print(f"Blacklisted {base_token_address}.")
    else:
        if base_token_address not in potential_addresses:
            potential_addresses.add(base_token_address)
            save_addresses_to_csv(list(potential_addresses))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rugcheck.py <BaseTokenAddress>")
        sys.exit(1)

    base_token_address = sys.argv[1]
    process_base_token_address(base_token_address)
