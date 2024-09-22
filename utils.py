import csv, sys, os, json, logging
from playwright.async_api import async_playwright

BLACKLIST_FILE = './lists/blacklist.csv'
POTENTIAL_FILE = './lists/potential.csv'
GEMS_FILE = './lists/gems.csv'
TOP_HOLDERS_FILE = './top_holders.json'

if os.name == 'nt':
    import winreg 

def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_addresses_to_csv(addresses, file_path):
    ensure_directory_exists(file_path)
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['BaseTokenAddress'])
            for address in addresses:
                writer.writerow([address])
    except Exception as e:
        print(f"Error writing to CSV: {e}")

def append_to_csv(row, file_path):
    ensure_directory_exists(file_path)
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row)

def load_addresses_from_csv(file_path):
    addresses = set()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    addresses.add(row['BaseTokenAddress'])
        except Exception as e:
            print(f"Error reading CSV: {e}")
    return addresses

def remove_address_from_potential(base_token_address):
    file_path = POTENTIAL_FILE
    lines = []
    found = False
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['BaseTokenAddress'] != base_token_address:
                    lines.append(row)
                else:
                    found = True

        if found:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['BaseTokenAddress']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(lines)
        else:
            print(f"Address {base_token_address} not found in potential CSV.")
    except Exception as e:
        print(f"Error processing potential CSV: {e}")

def add_address_to_gems(base_token_address):
    file_path = GEMS_FILE
    addresses = load_addresses_from_csv(file_path)
    if base_token_address in addresses:
        print(f"Address {base_token_address} already exists in gems CSV.")
        return
    try:
        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([base_token_address])
        print(f"Added {base_token_address} to gems CSV.")
    except Exception as e:
        print(f"Error writing to gems CSV: {e}")

def remove_address_from_gems(base_token_address):
    file_path = GEMS_FILE
    lines = []
    found = False
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['BaseTokenAddress'] != base_token_address:
                    lines.append(row)
                else:
                    found = True

        if found:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['BaseTokenAddress']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(lines)
            print(f"Removed {base_token_address} from gems CSV.")
        else:
            print(f"Address {base_token_address} not found in gems CSV.")
    except Exception as e:
        print(f"Error processing gems CSV: {e}")


def add_address_to_blacklist(base_token_address):
    file_path = BLACKLIST_FILE
    addresses = load_addresses_from_csv(file_path)
    if base_token_address in addresses:
        print(f"Address {base_token_address} already exists in blacklist CSV.")
        return
    try:
        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([base_token_address])
    except Exception as e:
        print(f"Error writing to blacklist CSV: {e}")

def blacklist(base_token_address):
    add_address_to_blacklist(base_token_address)
    remove_address_from_potential(base_token_address)

def replace_top_holders(ca, holders):
    top_holders_file = TOP_HOLDERS_FILE
    filtered_holders = [{"wallet": holder['owner'], "amount": holder['amount']} for holder in holders]

    if os.path.exists(top_holders_file):
        try:
            with open(top_holders_file, 'r') as file:
                existing_data = json.load(file)
        except json.JSONDecodeError:
            existing_data = {}
    else:
        existing_data = {}

    existing_data[ca] = filtered_holders

    with open(top_holders_file, 'w') as file:
        json.dump(existing_data, file, indent=4)

def get_default_browser_windows():
    try:
        reg_path = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            browser_prog_id = winreg.QueryValueEx(key, "ProgId")[0]
        
        if "Chrome" in browser_prog_id:
            return "chrome"
        elif "Firefox" in browser_prog_id:
            return "firefox"
        elif "Edge" in browser_prog_id:
            return "msedge"
        else:
            return None
    except Exception as e:
        print(f"Error fetching default browser: {e}")
        return None
    
import subprocess

def get_default_browser_linux():
    try:
        result = subprocess.run(['xdg-settings', 'get', 'default-web-browser'], stdout=subprocess.PIPE)
        browser = result.stdout.decode().strip()
        if "chrome" in browser:
            return "chrome"
        elif "firefox" in browser:
            return "firefox"
        else:
            return None
    except Exception as e:
        print(f"Error fetching default browser: {e}")
        return None


async def get_user_agent():
    async with async_playwright() as p:
        browser_name = None
        if os.name == 'nt':
            browser_name = get_default_browser_windows()
        elif os.name == 'posix': 
            browser_name = get_default_browser_linux()

        if browser_name == "chrome":
            browser = await p.chromium.launch(channel="chrome", headless=False)
        elif browser_name == "firefox":
            browser = await p.firefox.launch(headless=False)
        elif browser_name == "msedge":
            browser = await p.chromium.launch(channel="msedge", headless=False)
        else:
            print("Default browser not supported or detected")
            sys.exit(1)

        page = await browser.new_page()
        await page.goto("https://www.google.com")
        user_agent = await page.evaluate("navigator.userAgent")
        await browser.close()
        return user_agent
    

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

def ensure_file_exists(file_path):
    try:
        if not os.path.exists(file_path):
            open(file_path, 'a').close()
    except Exception as e:
        logging.error(f"Error ensuring file exists: {file_path}, Error: {e}")

def read_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}