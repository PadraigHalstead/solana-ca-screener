import time
import subprocess
import csv
import os
import sys
import logging
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import remove_address_from_potential, add_address_to_gems
from config import python_executable, allow_pumpfun, solscan_cookie, api_key

def ensure_file_exists(file_path):
    try:
        if not os.path.exists(file_path):
            open(file_path, 'a').close()
    except Exception as e:
        logging.error(f"Error ensuring file exists: {file_path}, Error: {e}")

def is_blacklisted(base_token_address):
    try:
        with open('./lists/blacklist.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0] == base_token_address:
                    return True
    except Exception as e:
        logging.error(f"Error reading blacklist file. Error: {e}")
    return False

def screen():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    blacklist_file = os.path.join(base_dir, 'lists', 'blacklist.csv')
    potential_file = os.path.join(base_dir, 'lists', 'potential.csv')
    gems_file = os.path.join(base_dir, 'lists', 'gems.csv')

    ensure_file_exists(blacklist_file)
    ensure_file_exists(potential_file)
    ensure_file_exists(gems_file)

    while True:
        with open(potential_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                base_token_address = row['BaseTokenAddress']

                if is_blacklisted(base_token_address):
                    continue

                if not (allow_pumpfun): 
                    subprocess.run([python_executable, os.path.abspath(os.path.join(base_dir, "screening", "pump-fun-check.py")), base_token_address])
                    if is_blacklisted(base_token_address):
                        print(f"Pump.fun launch. Blacklisting")
                        continue 

                
                print(f"Screening: {base_token_address}")
                subprocess.run([python_executable, os.path.abspath(os.path.join(base_dir, "screening", "rugcheck.py")), base_token_address])
                if is_blacklisted(base_token_address):
                    print(f"Rugcheck Fail")
                    continue
                print(f"Rugcheck Pass")                

                subprocess.run([python_executable, os.path.abspath(os.path.join(base_dir, "screening", "topholders.py")), base_token_address])
                if is_blacklisted(base_token_address):
                    print(f"Top Holders Fail")
                    continue
                print(f"Top Holders Pass")

                subprocess.run([python_executable, os.path.abspath(os.path.join(base_dir, "screening", "devwallet.py")), base_token_address])
                if is_blacklisted(base_token_address):
                    print(f"Dev Holdings Fail")
                    continue
                print(f"Dev Holdings Pass")

                subprocess.run([python_executable, os.path.abspath(os.path.join(base_dir, "screening", "num-of-holders.py")), base_token_address])
                if is_blacklisted(base_token_address):
                    print(f"Holders Fail")                
                    continue
                print(f"Holders Pass")                

                subprocess.run([python_executable, os.path.abspath(os.path.join(base_dir, "screening", "dev-sol-balance.py")), base_token_address])
                if is_blacklisted(base_token_address):
                    print(f"Sol Balance Fail")
                    continue
                print(f"Dev Sol Balance Pass")


                subprocess.run([python_executable, os.path.abspath(os.path.join(base_dir, "screening", "airdrops.py")), base_token_address])
                if is_blacklisted(base_token_address):
                    print(f"Airdrops / Bundle Snipe Fail")                
                    continue
                print(f"Airdrops / Bundle Snipe Pass")

                remove_address_from_potential(base_token_address)
                add_address_to_gems(base_token_address)

        time.sleep(0.1)

if __name__ == "__main__": 
    if allow_pumpfun == "":
        raise Exception("Pump.fun configuration not found. Please add ALLOW_PUMP_FUN to your .env file")
    if not solscan_cookie:
        raise Exception("Solscan cookie not found. Please add SOLSCAN_COOKIE to your .env file")
    if not api_key:
        raise Exception("API key not found. Please add SOLANA_FM_API_KEY to your .env file")
    screen()

