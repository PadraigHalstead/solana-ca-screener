import requests
import sys
import os
from typing import Tuple, Optional 
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import solscan_cookie, ua_platform, user_agent

def num_of_holders(base_token_address: str) -> Tuple[bool, Optional[str]]:  
    url = f"https://api-v2.solscan.io/v2/token/holder/total?address={base_token_address}"
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

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            total_holders = data.get('data', 0)

            if total_holders < 10:
                return False, "Very low number of holders. Blacklisting."
            elif total_holders > 5000:
                return False, "Very High number of holders. Blacklisting."
        else:
            return False, "Failed to fetch number of top holders. Blacklisting"
        return True, "Number Of Holders Pass"

    except Exception as e:
        return False, "An error occured obtaining number of holders. Blacklisting"
