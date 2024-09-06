import requests
import json
import os
import sys
from dotenv import load_dotenv
from typing import Tuple, Optional
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import add_address_to_blacklist, remove_address_from_potential
from config import api_key, user_agent

def get_transfer_details(dev_address, ca):
    url = f"https://api.solana.fm/v0/accounts/{dev_address}/transfers?mint={ca}&page=1"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "User-Agent": user_agent,
        "ApiKey": api_key
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch transfer details from Solana FM API. Status code: {response.status_code}")
            remove_address_from_potential(base_token_address)
            add_address_to_blacklist(base_token_address)
            return None
    except Exception as e:
        print(f"Error fetching transfer details: {e}")
        remove_address_from_potential(base_token_address)
        add_address_to_blacklist(base_token_address)
        return None

def calculate_percentage(amount, token_supply):
    return round((amount / token_supply) * 100)

def airdrops(base_token_address: str) -> Tuple[bool, Optional[str]]:

    try:
        with open('./extracted_data.json', 'r') as file:
            extracted_data = json.load(file)
    except Exception as e:
        return False, "An error occured obtaining extracted data. Blacklisting:"

    token_data = next((item for item in extracted_data if item["mint"] == base_token_address), None)
    if not token_data:
        return False, "No extracted data found for token. Blacklisting:" 

    dev_address = token_data.get("dev")
    token_supply = token_data.get("token_supply")

    if not dev_address:
        return False, "Dev address not found for token. Blacklisting:"
    elif not token_supply:
        return False, "Token supply not found. Blacklisting:"

    transfer_details = get_transfer_details(dev_address, base_token_address)
    if not transfer_details or 'results' not in transfer_details:
        return False, ("Failed to retrieve transfer details.")

    total_transferred_amount = 0

    for transaction in transfer_details['results']:
        try:
            for action in transaction['data']:
                if action['action'] == 'transfer':
                    if action['source'] != action['destination']: 
                        if action['source'] == dev_address and action['token'] == base_token_address and action['destination'] != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                            print(action['amount'])
                            total_transferred_amount += action['amount']
                        elif action['source'] == "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1" and action['destination'] == dev_address:
                            total_transferred_amount += action['amount']
        except Exception as e:
            return False, "Error processing transaction hash {transaction['transactionHash']}: {e}"

    percentage_transferred = calculate_percentage(total_transferred_amount, token_supply)

    if percentage_transferred > 3:
        return False, f"Airdrops/bundle snipe is {percentage_transferred}. Blacklisting:"
    return True, "Airdrops/Bundle Snipe Passed"
