import requests
import json
import time
import sys
import os
from typing import Tuple, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

    if mint_authority is not None and  (mint_authority != '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1' or mint_authority != '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8'):
        print(mint_authority)
        return data, False, "Mint Authority is enabled. Blacklisting:"
    elif freeze_authority is not None:
        return data, False, "Freeze Authority is enabled. Blacklisting:"
    elif token_meta.get("mutable", True):
        return data, False, "Metadata is mutable. Blacklisting:"
    else:
        risks = rugcheck_response.get("risks", [])
        for risk in risks:
            if risk.get("name") == "Low Liquidity":
                return data, False, "Token has very Low Liquidity. Blacklisting:"
            if risk.get("name") == "Copycat token":
                return data, False, "Token is copying a verifed token symbol. Blacklisting:"
    
    markets = rugcheck_response.get("markets", [])
    for market in markets:
        lp_locked_pct = market.get('lp', {}).get('lpLockedPct', None)
        if lp_locked_pct is not None and lp_locked_pct < 97:
            return data, False, "Deployer is holding LP. Blacklisting:"

        return data, True, "Rugcheck Pass"

def rugcheck(base_token_address: str) -> Tuple[bool, Optional[str]]:

    rugcheck_response = call_rugcheck_api(base_token_address)
    if rugcheck_response is None:
        return False, "No response from Rugcheck. Blacklisting:"

    extracted_data, is_blacklisted, reason = extract_data(rugcheck_response)

    try:
        with open('./extracted_data.json', 'w') as file:
            json.dump([], file) 

        with open('./extracted_data.json', 'w') as file:
            json.dump([extracted_data], file, indent=4)
    except Exception as e:
        print(f"Error updating extracted data file: {e}")

    return is_blacklisted, reason

