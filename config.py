import sys, requests, os, platform, asyncio
from dotenv import load_dotenv
load_dotenv()
from utils import get_user_agent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def check_solscan_valid(solscan_cookie):
    headers = {
        "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": solscan_cookie ,
            "Origin": "https://solscan.io",
            "Priority": "u=1, i",
            "Referer": "https://solscan.io/",
            "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": ua_platform,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": user_agent
    }
    
    response = requests.get("https://api.solscan.io", headers=headers)
    return response.status_code == 200

try:
    print('Configuring settings. Please wait...')

    excluded_addresses = ['TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM', '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8']

    solscan_cookie = os.getenv('SOLSCAN_COOKIE')
    if not solscan_cookie:
        print("API key not found. Please add your SOLSCAN_COOKIE to the .env file")
        sys.exit(1)

    api_key = os.getenv('SOLANA_FM_API_KEY')
    if not api_key:
        print("API key not found. Please add your SOLANA_FM_API_KEY to the .env file")
        sys.exit(1)

    allow_pumpfun_raw = os.getenv('ALLOW_PUMP_FUN', 'false').lower()

    if allow_pumpfun_raw not in ['true', 'false']:
        print("Error: ALLOW_PUMP_FUN not set correctly. Please set ALLOW_PUMP_FUN to 'true' or 'false' in your .env file.")
        sys.exit(1)

    allow_pumpfun = allow_pumpfun_raw == 'true'

    if platform.system() == 'Linux':
        ua_platform = "Linux"
    elif platform.system() == 'Windows':
        ua_platform = "Windows"
    else:
        print("Unsupported Operating System. This project only supports: Windows, Linux")
        sys.exit(1)

    print("Setting up user agent. Your browser will now open")
    user_agent = asyncio.run(get_user_agent())
    print("Obtained user agent")
    
    solscan_cookie_valid = check_solscan_valid(solscan_cookie)

    if not(solscan_cookie_valid):
        print("Solscan cookie is not valid, please obtain a new one.")
        sys.exit(1)
    else:
        print("Solscan Cookie is valid")
    print("Ready for screening")


except KeyboardInterrupt:
    print(f"\nStopping...")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occured: {e}")
    sys.exit(1)