import time,csv, os, sys
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import remove_address_from_potential, add_address_to_gems, blacklist, is_blacklisted, ensure_file_exists
from config import allow_pumpfun, solscan_cookie, api_key, user_agent, solscan_cookie_valid # Adding user agent to set on startup
from screening.pumpfuncheck import check_pumpfun
from screening.rugcheck import rugcheck
from screening.topholders import top_holders
from screening.devwallet import devwallet
from screening.numofholders import num_of_holders
from screening.devsolbalance import dev_sol_balance
from screening.airdrops import airdrops
from screening.bundlesnipe import bundlesnipe


def screen():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    blacklist_file = os.path.join(base_dir, 'lists', 'blacklist.csv')
    potential_file = os.path.join(base_dir, 'lists', 'potential.csv')
    gems_file = os.path.join(base_dir, 'lists', 'gems.csv')

    ensure_file_exists(blacklist_file)
    ensure_file_exists(potential_file)
    ensure_file_exists(gems_file)
    try:
        while True:
            with open(potential_file, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    base_token_address = row['BaseTokenAddress']

                    if is_blacklisted(base_token_address):
                        continue
                    
                    # if not allow_pumpfun:
                    #     is_valid, reason = check_pumpfun(base_token_address)
                    #     if not is_valid:
                    #         blacklist(base_token_address)
                    #         print(f"{reason} {base_token_address}")
                    #         continue    
                    #     print(reason)              

                    is_valid, reason = rugcheck(base_token_address)
                    # if not is_valid:
                    #     blacklist(base_token_address)
                    #     print(f"{reason} {base_token_address}")
                    #     continue
                    # print(reason)              

                    # is_valid, reason = top_holders(base_token_address)
                    # if not is_valid:
                    #     blacklist(base_token_address)
                    #     print(f"{reason} {base_token_address}")
                    #     continue
                    # print(reason)  

                    # is_valid, reason = devwallet(base_token_address)
                    # if not is_valid:
                    #     blacklist(base_token_address)
                    #     print(f"{reason} {base_token_address}")
                    #     continue
                    # print(reason)

                    # is_valid, reason = num_of_holders(base_token_address)
                    # if not is_valid:
                    #     blacklist(base_token_address)
                    #     print(f"{reason} {base_token_address}")
                    #     continue
                    # print(reason)             

                    # is_valid, reason = dev_sol_balance(base_token_address)
                    # if not is_valid:
                    #     blacklist(base_token_address)
                    #     print(f"{reason} {base_token_address}")
                    #     continue
                    # print(reason)

                    is_valid, reason = airdrops(base_token_address)
                    if not is_valid:
                        blacklist(base_token_address)
                        print(f"{reason} {base_token_address}")
                        continue
                    print(reason)

                    # is_valid, reason = bundlesnipe(base_token_address)
                    # if not is_valid:
                    #     blacklist(base_token_address)
                    #     print(f"{reason} {base_token_address}")
                    #     continue
                    # print(reason)

                    remove_address_from_potential(base_token_address)
                    add_address_to_gems(base_token_address)
                    print(f"Added to gems: {base_token_address}")


            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        sys.exit(1)

if __name__ == "__main__": 
    if allow_pumpfun == "":
        raise Exception("Pump.fun configuration not found. Please add ALLOW_PUMP_FUN to your .env file")
    if not solscan_cookie:
        raise Exception("Solscan cookie not found. Please add SOLSCAN_COOKIE to your .env file")
    if not api_key:
        raise Exception("API key not found. Please add SOLANA_FM_API_KEY to your .env file")
    screen()

