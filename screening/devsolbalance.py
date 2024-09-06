import requests
import json
import sys
import os
from dotenv import load_dotenv
from typing import Tuple, Optional
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pumpfundev import getpumpfundevwallet
from config import solscan_cookie, user_agent, ua_platform


def dev_sol_balance(base_token_address: str) -> Tuple[bool, Optional[str]]:  
    try:
        with open('./extracted_data.json', 'r') as file:
            extracted_data = json.load(file)
        
        token = next((item for item in extracted_data if item["mint"] == base_token_address), None)
        if not token:
            return False, "No extracted data found. Blacklisting:"
        
        dev_address = token.get("dev")

        if not dev_address:
            return False, "Dev address not found. Blacklisting:"
        
        if dev_address == "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM":
            dev_address = getpumpfundevwallet(base_token_address)
            if dev_address == "":
                return False, "Dev address not found. Blacklisting:"
            

        url = f"https://api-v2.solscan.io/v2/account?address={dev_address}"
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
            account_data = data.get('data', {})
            lamports = account_data.get('lamports', 0)

            # If dev sol > 10
            if lamports > 10000000000:
                return False, "Dev SOL > 10. Blacklisting:"
            return True, "Dev SOL Balance Pass"
        else:
            return False, "An error occured obtaining dev address. Blacklisting:"

    except Exception as e:
        return False, "An error occured obtaining dev address. Blacklisting:"
