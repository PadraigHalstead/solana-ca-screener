import json, os, sys
from dotenv import load_dotenv
from typing import Tuple, Optional
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_request import call_solscan_api


def get_token_supply_and_dev_address(base_token_address: str) -> Tuple[Optional[int], Optional[str]]:
    file_path = './extracted_data.json'
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                extracted_data = json.load(file)
            token = next((item for item in extracted_data if item["mint"] == base_token_address), None)
            if token:
                token_supply = token.get("token_supply", 0)
                dev_address = token.get("dev", None)
                return token_supply, dev_address
        except Exception as e:
            print(f"Error reading extracted data: {e}")
    print(f"Token supply or dev address not found for {base_token_address}")
    return None, None


def calculate_percentage(amount: int, token_supply: int) -> float:
    return round((amount / token_supply) * 100, 1)


def airdrops(base_token_address: str) -> Tuple[bool, str]:

    # Get token supply and dev address from extracted_data.json
    token_supply, dev_address = get_token_supply_and_dev_address(base_token_address)
    if not dev_address:
        return False, "Dev address not found"
    
    if not token_supply:
        return False, "Token supply not found"

    # Get transfer data
    url = f"https://api-v2.solscan.io/v2/token/transfer?address={base_token_address}&page=1&page_size=50&exclude_amount_zero=false&to={dev_address}"
    transfer_data = call_solscan_api(url)
    if not transfer_data or "data" not in transfer_data:
        return True, "No transfers found"

    total_sniped_amount = 0
    for entry in transfer_data["data"]:
        try:
            if (
                "transfer" in entry["activity_type"].lower() and
                entry["to_address"] == dev_address and
                entry["token_address"] == base_token_address
            ):
                total_sniped_amount += entry["amount"]
        except KeyError:
            print(f"Error processing entry {entry}")

    sniped_percentage = calculate_percentage(total_sniped_amount, token_supply)

    if sniped_percentage > 0:
        return False, f"Dev sniped amount: {sniped_percentage}%. Blacklisting:"
    return True, "Dev Snipe Pass"
