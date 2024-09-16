import requests
import json
import time
import sys
import os
from typing import Tuple, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import ua_platform, user_agent
from pumpfundev import getpumpfundevwallet

def call_rugcheck_api(ca):
    url = f"https://api.rugcheck.xyz/v1/tokens/{ca}/report"
    
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTg4NzczNTcsImlkIjoiR2NybmVkSGVZTkxMaGNmeTV2Mll0cUpVVEhIc2o2akFUeVpXTHk1cFVhOUUifQ.JuO9PvGviVtzNJRNaNZ98qI5GKuu6bUVdTXzS5KKHGM",
        "Content-Type": "application/json",
        "Origin": "https://rugcheck.xyz",
        "Priority": "u=1, i",
        "Referer": "https://rugcheck.xyz/",
        "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": ua_platform,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": user_agent,
        "X-Wallet-Address": "null"
    }

    response = requests.get(url, headers=headers)
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

def extract_data(rugcheck_response, base_token_address: str):
    mint_authority = rugcheck_response["token"].get("mintAuthority", None)
    freeze_authority = rugcheck_response["token"].get("freezeAuthority", None)
    token_meta = rugcheck_response.get("tokenMeta", {})

    dev = token_meta.get("updateAuthority", False)
    if dev == "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM":
        dev_address = getpumpfundevwallet(base_token_address)
        if dev_address == "":
            return None, False, "Error getting dev address"
        else:
            dev = dev_address
    print(dev)

    data = {
        "mint": rugcheck_response.get("mint", False),
        "mintAuthority": mint_authority,
        "freezeAuthority": freeze_authority,
        "dev": dev,
        "token_supply": rugcheck_response["token"].get("supply", False),
        "mutable": token_meta.get("mutable", False)
    }

    if mint_authority is not None and (mint_authority != '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1' or mint_authority != '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8'):
        return data, False, "Mint Authority is enabled. Blacklisting:"
    elif freeze_authority is not None:
        return data, False, "Freeze Authority is enabled. Blacklisting:"
    elif token_meta.get("mutable", True):
        return data, False, "Metadata is mutable. Blacklisting:"
    else:
        risks = rugcheck_response.get("risks", [])
        for risk in risks:
            if risk.get("name") == "Low Liquidity" and risk.get("value") == "$0.00":
                return data, False, "Liquidity pool rugged. Blacklisting:"
            if risk.get("name") == "Low Liquidity":
                return data, False, "Token has very Low Liquidity. Blacklisting:"
            if risk.get("name") == "Copycat token":
                return data, False, "Token is copying a verifed token symbol. Blacklisting:"
    
    markets = rugcheck_response.get("markets", [])
    for market in markets:
        lp_locked_pct = market.get('lp', {}).get('lpLockedPct', None)
        if lp_locked_pct is not None and lp_locked_pct > 97:
             return data, True, "Rugcheck Pass"
        else:
            return data, False, "Deployer is holding LP. Blacklisting:"

    total_insider_pct = 0
    top_holders = rugcheck_response.get("topHolders", [])
    for holder in top_holders:
        if holder.get("insider", False):
            total_insider_pct += holder.get("pct", 0)

        if total_insider_pct >= 10:
            return data, False, f"Insider holdings are too high ({total_insider_pct}%). Blacklisting:"

        return data, True, "Rugcheck Pass"

def rugcheck(base_token_address: str) -> Tuple[bool, Optional[str]]:

    rugcheck_response = call_rugcheck_api(base_token_address)
    if rugcheck_response is None:
        return False, "No response from Rugcheck. Blacklisting:"

    extracted_data, is_blacklisted, reason = extract_data(rugcheck_response, base_token_address)

    try:
        with open('./extracted_data.json', 'w') as file:
            json.dump([], file) 

        with open('./extracted_data.json', 'w') as file:
            json.dump([extracted_data], file, indent=4)
    except Exception as e:
        print(f"Error updating extracted data file: {e}")

    return is_blacklisted, reason

