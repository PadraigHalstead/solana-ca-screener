import requests
import json
import os
import sys
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import add_address_to_blacklist, remove_address_from_potential

def get_transfer_details(dev_address, ca):
    api_key = os.getenv('SOLANA_FM_API_KEY')
    if not api_key:
        remove_address_from_potential(base_token_address)
        add_address_to_blacklist(base_token_address)
        raise Exception("API key not found. Please add your SOLANA_FM_API_KEY to the .env file")


    url = f"https://api.solana.fm/v0/accounts/{dev_address}/transfers?mint={ca}&page=1"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python transfers.py <BaseTokenAddress>")
        sys.exit(1)

    base_token_address = sys.argv[1]

    try:
        with open('./extracted_data.json', 'r') as file:
            extracted_data = json.load(file)
    except Exception as e:
        print(f"Error reading extracted data file: {e}")
        sys.exit(1)

    token_data = next((item for item in extracted_data if item["mint"] == base_token_address), None)
    if not token_data:
        print(f"No extracted data found for {base_token_address}.")
        sys.exit(1)

    dev_address = token_data.get("dev")
    token_supply = token_data.get("token_supply")

    if not dev_address or not token_supply:
        print(f"Dev address or token supply not found for {base_token_address}.")
        sys.exit(1)

    transfer_details = get_transfer_details(dev_address, base_token_address)
    if not transfer_details or 'results' not in transfer_details:
        print("Failed to retrieve transfer details.")
        sys.exit(1)

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
            print(f"Error processing transaction hash {transaction['transactionHash']}: {e}")

    percentage_transferred = calculate_percentage(total_transferred_amount, token_supply)
    print(f"Percentage transferred: {percentage_transferred}%")

    if percentage_transferred > 3:
        add_address_to_blacklist(base_token_address)
        remove_address_from_potential(base_token_address)
        print(f"Blacklisted {base_token_address}.")
