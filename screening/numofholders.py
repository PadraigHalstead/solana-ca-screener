import sys, os
from typing import Tuple, Optional
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_request import call_solscan_api


def num_of_holders(base_token_address: str) -> Tuple[bool, Optional[str]]:
    try:
        url = f"https://api-v2.solscan.io/v2/token/holder/total?address={base_token_address}"
        response = call_solscan_api(url)

        if response is None:
            return False, "Failed to fetch data from Solscan API. Blacklisting."

        total_holders = response.get('data', 0)

        if total_holders is None:
            return False, "Failed to fetch number of top holders. Blacklisting."

        if total_holders < 10:
            return False, "Very low number of holders. Blacklisting."
        elif total_holders > 4000:
            return False, "Very High number of holders. Blacklisting."

        return True, "Number Of Holders Pass"
    
    except Exception as e:
        return False, f"An error occurred obtaining number of holders: {str(e)}. Blacklisting."
