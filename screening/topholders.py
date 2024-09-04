import requests
import json
import numpy as np
import time
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import save_addresses_to_csv, load_addresses_from_csv, append_to_csv, replace_top_holders, remove_address_from_potential, add_address_to_blacklist
from config import solscan_cookie, user_agent, ua_platform


def call_solscan_api(ca):
    url = f"https://api-v2.solscan.io/v2/token/holders?address={ca}&page_size=20&page=1"
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

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {ca}. Status code: {response.status_code}")
        add_address_to_blacklist(base_token_address)
        remove_address_from_potential(base_token_address)
        return None

def read_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def filter_wallets(holders):
    excluded_wallets = [
        "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM",
        "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
    ]
    return [holder for holder in holders if holder['owner'] not in excluded_wallets]

def calculate_percentage(token_supply, holders, top_n):
    filtered_holders = filter_wallets(holders)
    total_amount = sum(holder['amount'] for holder in filtered_holders[:top_n])
    percentage = (total_amount / token_supply) * 100
    return percentage

def check_holder_percentage(token_supply, holders):
    filtered_holders = filter_wallets(holders)
    for holder in filtered_holders:
        percentage = (holder['amount'] / token_supply) * 100
        if percentage > 6:
            return True
    return False

def check_same_amount(holders):
    amount_counts = {}
    for holder in holders:
        amount = holder['amount']
        if amount in amount_counts:
            amount_counts[amount] += 1
        else:
            amount_counts[amount] = 1
    for amount, count in amount_counts.items():
        if count >= 3:
            return True
    return False

def process_base_token_address(base_token_address):
    blacklist_addresses = load_addresses_from_csv('./lists/blacklist.csv')
    potential_addresses = load_addresses_from_csv('./lists/potential.csv')

    if base_token_address in blacklist_addresses:
        print(f"Address {base_token_address} is already blacklisted.")
        return

    extracted_data = read_json('./extracted_data.json')

    token = next((item for item in extracted_data if item["mint"] == base_token_address), None)
    if not token:
        print(f"No extracted data found for {base_token_address}.")
        return

    token_supply = token.get("token_supply")
    if not token_supply:
        print(f"Token supply not found for {base_token_address}.")
        return

    response_data = call_solscan_api(base_token_address)
    if response_data and response_data.get('data'):
        holders = response_data['data']

        try:
            percentage_top_10 = calculate_percentage(token_supply, holders, 10)
            percentage_top_20 = calculate_percentage(token_supply, holders, 20)
            holder_exceeds_6_percent = check_holder_percentage(token_supply, holders)
            same_amount_check = check_same_amount(holders[:20])

            if percentage_top_10 > 32 or percentage_top_20 > 40 or holder_exceeds_6_percent or same_amount_check:
                print(f"Blacklisted {base_token_address}.")
                append_to_csv([base_token_address], './lists/blacklist.csv')
                potential_addresses.discard(base_token_address)
                blacklist_addresses.add(base_token_address)
            else:
                replace_top_holders(base_token_address, holders)
        except Exception as e:
            print(f"Top Holders Unavailable: {e}")
            append_to_csv([base_token_address], './lists/blacklist.csv')
            potential_addresses.discard(base_token_address)
            blacklist_addresses.add(base_token_address)

        time.sleep(1)

    save_addresses_to_csv(list(potential_addresses), './lists/potential.csv')
    save_addresses_to_csv(list(blacklist_addresses), './lists/blacklist.csv')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python topholders.py <BaseTokenAddress>")
        sys.exit(1)

    base_token_address = sys.argv[1]

    if not os.path.exists('../top_holders.json'):
        with open('../top_holders.json', 'w') as file:
            json.dump({}, file)

    process_base_token_address(base_token_address)
