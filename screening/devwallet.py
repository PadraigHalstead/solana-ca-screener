import sys
import json
import requests
import os
from typing import Tuple, Optional
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pumpfundev import getpumpfundevwallet
from config import solscan_cookie, ua_platform, user_agent

def call_solscan_api(dev_address):
    url = f'https://api-v2.solscan.io/v2/account/tokenaccounts?address={dev_address}&page=1&page_size=480&type=token&hide_zero=true'
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cookie": solscan_cookie,
        "origin": "https://solscan.io",
        "priority": "u=1, i",
        "referer": "https://solscan.io/",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": ua_platform,
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": user_agent
    }

    response = requests.get(url, headers=headers)
    return response

def devwallet(base_token_address: str) -> Tuple[bool, Optional[str]]:

    with open('./extracted_data.json', 'r') as file:
        extracted_data = json.load(file)

    entry = next((item for item in extracted_data if item["mint"] == base_token_address), None)
    
    if entry:
        dev_address = entry.get("dev")
        token_supply = entry.get("token_supply")

        if not dev_address or token_supply is None:
            return False, "Required data missing in the extracted data. Blacklisting:"

        # Pump.fun wallet address
        if dev_address == "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM":
            dev_address = getpumpfundevwallet(base_token_address)
            if dev_address == "":
                return False, "Error getting dev address"

        response = call_solscan_api(dev_address)

        try:
            response_data = response.json()
            token_accounts = response_data.get('data', {}).get('tokenAccounts', [])
            amount = None
            for account in token_accounts:
                if account.get('tokenAddress') == base_token_address:
                    amount = account.get('balance')
                    break

            if amount is not None:
                percentage = (amount / token_supply) * 100
                if percentage > 6:
                    return False, "Dev owns more than 6%. Blacklisting:"
                return True, "Dev Holdings Pass"
            else:
                return False, "Dev has sold. Blacklisting:"
            

        except ValueError as e:
            return False, "Failed to calculate dev %. Blacklisting:"
        