import csv
import os
import json
import asyncio
from playwright.async_api import async_playwright


BLACKLIST_FILE = './lists/blacklist.csv'
POTENTIAL_FILE = './lists/potential.csv'
GEMS_FILE = './lists/gems.csv'
TOP_HOLDERS_FILE = './top_holders.json'

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


async def get_user_agent():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="chrome")
        page = await browser.new_page()
        await page.goto("https://www.google.com")
        user_agent = await page.evaluate("navigator.userAgent")
        await browser.close()
        return user_agent
    

