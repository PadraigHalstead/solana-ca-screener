import requests, time
from config import solscan_cookie, user_agent, ua_platform

def call_solscan_api(url: str):

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
    
def call_rugcheck_api(ca):
    url = f"https://api.rugcheck.xyz/v1/tokens/{ca}/report"
    
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTg4NzczNTcsImlkIjoiR2NybmVkSGVZTkxMaGNmeTV2Mll0cUpVVEhIc2o2akFUeVpXTHk1cFVhOUUifQ.JuO9PvGviVtzNJRNaNZ98qI5GKuu6bUVdTXzS5KKHGM",
        "Content-Type": "application/json",
        "Origin": "https://rugcheck.xyz",
        "Priority": "u=1, i",
        "Referer": "https://rugcheck.xyz/",
        "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": ua_platform,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": user_agent,
        "X-Wallet-Address": "null"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Rate limit exceeded, waiting for 10 seconds...")
        time.sleep(10)
        return call_rugcheck_api(ca)
    elif response.status_code == 502:
        time.sleep(0.5)
        return call_rugcheck_api(ca)
    else:
        return None