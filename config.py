import os
from dotenv import load_dotenv
import sys
import platform
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

solscan_cookie = os.getenv('SOLSCAN_COOKIE')
if not solscan_cookie:
    raise Exception("API key not found. Please add your SOLSCAN_COOKIE to the .env file")

api_key = os.getenv('SOLANA_FM_API_KEY')
if not api_key:
    raise Exception("API key not found. Please add your SOLANA_FM_API_KEY to the .env file")

allow_pumpfun = os.getenv('ALLOW_PUMP_FUN', 'false').lower() == 'true'

if platform.system() == 'Linux':
    python_executable = '/usr/bin/python3'
    ua_platform = "Linux"
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
else:
    python_executable = 'python'
    ua_platform = "Windows"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'