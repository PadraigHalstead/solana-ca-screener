import requests, json, os, sys
from typing import Tuple, Optional
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import user_agent, ua_platform, solscan_cookie, excluded_addresses


def get_transfer_data(base_token_address: str, dev_address: str) -> Optional[dict]:
    url = f"https://api-v2.solscan.io/v2/token/transfer?address={base_token_address}&page=1&page_size=10&exclude_amount_zero=false&to={dev_address}"

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
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from Solscan: {response.status_code}")
        return None


def get_token_supply_and_dev_address(base_token_address: str) -> Tuple[Optional[int], Optional[str]]:
    file_path = './extracted_data.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            extracted_data = json.load(file)
        
        token = next((item for item in extracted_data if item["mint"] == base_token_address), None)
        if token:
            token_supply = token.get("token_supply", 0)
            dev_address = token.get("dev", None)
            return token_supply, dev_address
    
    print(f"Token supply or dev address not found for {base_token_address}")
    return None, None


def bundlesnipe(base_token_address: str) -> Tuple[bool, str]:

    # Get token supply and dev address from extracted_data.json
    token_supply, dev_address = get_token_supply_and_dev_address(base_token_address)
    if not dev_address:
        return False, "Dev address not found"
    
    if not token_supply:
        return False, "Token supply not found"

    # Get transfer data
    transfer_data = get_transfer_data(base_token_address, dev_address)
    if not transfer_data or "data" not in transfer_data:
        return True, "No transfers found"

    total_sniped_amount = 0
    for entry in transfer_data["data"]:
        if (
            "transfer" in entry["activity_type"].lower() and
            entry["from_address"] == dev_address and
            entry["to_address"] not in excluded_addresses and
            entry["token_address"] == base_token_address
        ):
            total_sniped_amount += entry["amount"]

    # Calculate sniped percentage
    sniped_percentage = (total_sniped_amount / token_supply) * 100
    sniped_percentage = round(sniped_percentage, 1)

    if sniped_percentage > 0:
        return False, f"Dev outgoing sniped amount: {sniped_percentage}%"
    else:
        return True, "Passed"

