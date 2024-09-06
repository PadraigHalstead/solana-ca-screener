import requests
from dotenv import load_dotenv
load_dotenv()

from config import solscan_cookie, ua_platform, user_agent, api_key

def getpumpfundevwallet(base_token_address: str) -> str:
    url = f"https://api-v2.solscan.io/v2/account?address={base_token_address}"
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

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return ""

    data = response.json()
    mint_tx = data['data']['tokenInfo']['first_mint_tx']

  
    url = f"https://api.solana.fm/v0/transfers/{mint_tx}" 
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "User-Agent": user_agent,
        "ApiKey": api_key
    } 
    response = requests.get(url, headers)
    
    if response.status_code != 200:
        return ""

    transfers = response.json()

    devwallet = None
    for entry in transfers['result']['data']:
        if entry.get('action') == 'pay_tx_fees':
            devwallet = entry.get('source')
            break
    
    if devwallet:
        return devwallet
    else:
        return ""