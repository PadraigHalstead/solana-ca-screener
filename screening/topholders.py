import requests
import json
import numpy as np
import time
import sys
import os
from dotenv import load_dotenv
from typing import Tuple, Optional
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import replace_top_holders
from config import solscan_cookie, user_agent, ua_platform


def call_solscan_api(ca):
    url = f"https://api-v2.solscan.io/v2/token/holders?address={ca}&page_size=30&page=1"
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

def read_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def filter_wallets(holders):
    excluded_wallets = [
        "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM",
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
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

def check_distribution(token_supply, holders, tolerance=0.1):

    if len(holders) < 25:
        return False
    
    selected_holders = holders[14:27]
    percentages = [(holder['amount'] / token_supply) * 100 for holder in selected_holders]

    max_pct = max(percentages)
    min_pct = min(percentages)
    
    difference = max_pct - min_pct
    if (difference <= tolerance):
        return False
    return True



def top_holders(base_token_address: str) -> Tuple[bool, Optional[str]]:
 
    if not os.path.exists('./top_holders.json'):
        with open('./top_holders.json', 'w') as file:
            json.dump({}, file)

    extracted_data = read_json('./extracted_data.json')

    token = next((item for item in extracted_data if item["mint"] == base_token_address), None)
    if not token:
        return False, "No extracted data found for this token. Blacklisting:"

    token_supply = token.get("token_supply")
    if not token_supply:
        return False, "Token supply not found. Blacklisting:"

    response_data = call_solscan_api(base_token_address)
    if response_data and response_data.get('data'):
        holders = response_data['data']
        
        try:
            percentage_top_10 = calculate_percentage(token_supply, holders, 10)
            percentage_top_20 = calculate_percentage(token_supply, holders, 20)
            holder_exceeds_6_percent = check_holder_percentage(token_supply, holders)
            distribution_check = check_distribution(token_supply, holders, tolerance=0.01)

            if percentage_top_10 > 32:
                return False, f"Top 10 holder is {percentage_top_10}%. Blacklisting:"
            elif percentage_top_20 > 40:
                return False, f"Top 20 holder is {percentage_top_20}%. Blacklisting:"
            elif holder_exceeds_6_percent:
                return False, "One or more holders with more than 6%. Blacklisting:"
            elif not distribution_check:
                return False, "Suspicious distribution. Potential mass sell bot. Blacklisting:"
            else:
                replace_top_holders(base_token_address, holders)
                return True, "Top Holders Pass"
        except Exception as e:
            return False, "Error occured obtaining top holders. Blacklisting:"
    else:
        return False, "Top holders data not found. Blacklisting:"