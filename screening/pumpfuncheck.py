import requests
from typing import Tuple, Optional
from config import allow_pumpfun

def check_pumpfun(base_token_address: str) -> Tuple[bool, Optional[str]]:
    url = f"https://frontend-api.pump.fun/candlesticks/{base_token_address}?offset=0&limit=1&timeframe=5"
    
    response = requests.get(url)
    
    try:
        if response.status_code == 200:
            if response.text != "[]":
                if not(allow_pumpfun):
                    return False, "Pump.fun tokens not allowed. Blacklisting:"
                else:
                    return True, "Pump.fun Check Pass"
            else: 
                return True, "Pump.fun Check Pass"
    except:
        return False, "Error fetching pump.fun token status. Blacklisting:"


def check_pumpfun_test(base_token_address: str, allow_pump_fun: bool) -> bool:
    url = f"https://frontend-api.pump.fun/candlesticks/{base_token_address}?offset=0&limit=1&timeframe=5"
    
    response = requests.get(url)
    
    try:
        if response.status_code == 200:
            if response.text != "[]":
                if not(allow_pump_fun):
                    return False, "Pump.fun tokens not allowed. Blacklisting:"
                else:
                    return True, "Pump.fun Check Pass"
            else: 
                return True, "Pump.fun Check Pass"
    except:
        return False, "Error fetching pump.fun token status. Blacklisting:"