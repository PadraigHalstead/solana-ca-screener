import os
from dotenv import load_dotenv
import sys
import platform
import asyncio
load_dotenv()
from utils import get_user_agent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print('Configuring settings. Please wait...')
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
        raise Exception("Unsupported Operating System. This project only supports: Windows, Linux")

    print("Setting up user agent. Your browser will now open")
    user_agent = asyncio.run(get_user_agent())
    print('Ready to screen')

except KeyboardInterrupt:
    print(f"\nStopping...")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occured: {e}")
    sys.exit(1)