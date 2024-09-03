import requests
import os
from dotenv import load_dotenv
load_dotenv()

def getpumpfundevwallet(base_token_address):
     
    solscan_cookie = os.getenv('SOLSCAN_COOKIE')
    sol_aut = os.getenv('SOL_AUT')
    api_key = os.getenv('SOLANA_FM_API_KEY')

    
    url = f"https://api-v2.solscan.io/v2/account?address={base_token_address}"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cookie": solscan_cookie,
        "if-none-match": 'W/"bc9-NHG88bcSKuuMBPl02DHyHuDhYL0"',
        "origin": "https://solscan.io",
        "priority": "u=1, i",
        "referer": "https://solscan.io/",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sol-aut": sol_aut,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
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