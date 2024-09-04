import requests
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import add_address_to_blacklist, remove_address_from_potential

def check_pumpfun(base_token_address):
    url = f"https://frontend-api.pump.fun/candlesticks/{base_token_address}?offset=0&limit=1&timeframe=5"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        if response.text != "[]":
            print(f"pump.fun launch. Blacklisting")
            add_address_to_blacklist(base_token_address)
            remove_address_from_potential(base_token_address)
    else:
        print(f"Unknown error while checking pump.fun launch. Blacklisting")
        add_address_to_blacklist(base_token_address)
        remove_address_from_potential(base_token_address)
            

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pumpfuncheck.py <BaseTokenAddress>")
        sys.exit(1)

    base_token_address = sys.argv[1]
    check_pumpfun(base_token_address)
