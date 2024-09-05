import requests
from typing import Tuple, Optional

def check_pumpfun(base_token_address: str) -> Tuple[bool, Optional[str]]:
    url = f"https://frontend-api.pump.fun/candlesticks/{base_token_address}?offset=0&limit=1&timeframe=5"
    
    response = requests.get(url)
    
    try:
        if response.status_code == 200:
            if response.text != "[]":
                return False, "Pump.fun tokens not allowed. Blacklisting"
            else: 
                return True, None
    except:
        return False, "Error fetching pump.fun token status. Blacklisting"

