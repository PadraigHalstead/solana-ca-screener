import json, sys, os
from typing import Tuple, Optional
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pumpfundev import getpumpfundevwallet
from api_request import call_rugcheck_api

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

    data = {
        "mint": rugcheck_response.get("mint", False),
        "mintAuthority": mint_authority,
        "freezeAuthority": freeze_authority,
        "dev": dev,
        "token_supply": rugcheck_response["token"].get("supply", False),
        "mutable": token_meta.get("mutable", False)
    }
    markets = rugcheck_response.get("markets", [])
    top_holders = rugcheck_response.get("topHolders", [])


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
    
    for market in markets:
        lp_locked_pct = market.get('lp', {}).get('lpLockedPct', None)
        if lp_locked_pct is not None and lp_locked_pct > 97:
             return data, True, "Rugcheck Pass"
        else:
            return data, False, "Deployer is holding LP. Blacklisting:"

    total_insider_pct = 0
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

