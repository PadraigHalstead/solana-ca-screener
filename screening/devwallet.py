import sys, json, os
from typing import Tuple, Optional
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_request import call_solscan_api

def devwallet(base_token_address: str) -> Tuple[bool, Optional[str]]:

    with open('./extracted_data.json', 'r') as file:
        extracted_data = json.load(file)

    entry = next((item for item in extracted_data if item["mint"] == base_token_address), None)
    
    if entry:
        dev_address = entry.get("dev")
        token_supply = entry.get("token_supply")

        if not dev_address or token_supply is None:
            return False, "Required data missing in the extracted data. Blacklisting:"

        url = f'https://api-v2.solscan.io/v2/account/tokenaccounts?address={dev_address}&page=1&page_size=480&type=token&hide_zero=true'
        response_data = call_solscan_api(url)

        try:
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
        