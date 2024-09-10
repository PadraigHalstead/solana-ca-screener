import requests, json, sys, os, time
from typing import List, Dict, Optional, Tuple

# Adjust the system path to import configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import api_key, user_agent


def load_top_holders(token_address: str) -> Optional[List[Dict]]:
    """
    Load the top holders for a specific token address from the top_holders.json file.
    
    Args:
        token_address (str): The token address to look up.

    Returns:
        Optional[List[Dict]]: A list of holder dictionaries or None if not found.
    """
    try:
        with open('top_holders.json', 'r') as f:
            data = json.load(f)
            return data.get(token_address, None)
    except FileNotFoundError:
        print("Error: top_holders.json file not found.")
        return None
    except json.JSONDecodeError:
        print("Error: top_holders.json contains invalid JSON.")
        return None


def create_wallet_map(holders: List[Dict], excluded_wallets: List[str], top_n: int = 20) -> Dict[str, int]:
    """
    Create a map of wallet addresses to their holdings, excluding certain wallets.

    Args:
        holders (List[Dict]): List of holder dictionaries.
        excluded_wallets (List[str]): Wallet addresses to exclude.
        top_n (int): Number of top wallets to include.

    Returns:
        Dict[str, int]: A dictionary mapping wallet addresses to their amounts.
    """
    wallet_map = {}
    count = 0
    for holder in holders:
        wallet = holder.get('wallet')
        amount = holder.get('amount')
        if wallet and amount and wallet not in excluded_wallets:
            wallet_map[wallet] = amount
            count += 1
            if count >= top_n:
                break
    return wallet_map


def get_transactions(wallet: str, base_token_address: str) -> Optional[Dict]:
    """
    Fetch transactions for a specific wallet.

    Args:
        wallet (str): The wallet address.
        base_token_address (str): The base token address.

    Returns:
        Optional[Dict]: Transaction data or None if no transactions found.
    """
    url = f"https://api.solana.fm/v0/accounts/{wallet}/transactions"
    params = {
        "actions": "transfer",
        "inflow": "false",
        "outflow": "true",
        "mints": base_token_address,
        "page": 1
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "User-Agent": user_agent,
        "ApiKey": api_key
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("message") != "Retrieved 0 transactions":
            return data
    except requests.RequestException as e:
        print(f"Request error for wallet {wallet}: {e}")
    except json.JSONDecodeError:
        print(f"Invalid JSON response for wallet {wallet}.")
    return None


def get_transfer_details(signatures: List[str]) -> List[Dict]:
    """
    Get transfer details for a set of transaction signatures.

    Args:
        signatures (List[str]): List of transaction signatures.

    Returns:
        List[Dict]: List of transfer detail dictionaries.
    """
    url = "https://api.solana.fm/v0/transfers"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "User-Agent": user_agent,
        "ApiKey": api_key
    }
    body = {
        "transactionHashes": signatures
    }
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        transfers = []
        for txn_info in data.get("result", []):
            transfers.extend(txn_info.get("data", []))
        return transfers
    except requests.RequestException as e:
        print(f"Transfer details request error: {e}")
    except json.JSONDecodeError:
        print("Invalid JSON response for transfer details.")
    return []


def clusters(base_token_address: str) -> Tuple[bool, Optional[str]]:
    """
    Main function that handles top holders clustering.

    Args:
        base_token_address (str): The base token address for analysis.

    Returns:
        Tuple[bool, Optional[str]]: Status and message.
    """
    excluded_wallets = [
        "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM",
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
        "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
    ]

    # Load the top holders for the specific token
    top_holders = load_top_holders(base_token_address)
    if not top_holders:
        return False, "No top holders data found for this token."

    # Create a map of wallets and holdings (top 20 excluding excluded wallets)
    wallet_map = create_wallet_map(top_holders, excluded_wallets, top_n=10)
    if not wallet_map:
        return False, "No wallets available after filtering excluded wallets."

    signatures = []
    signature_to_wallet = {}

    # Collect all signatures from top wallets
    for wallet, amount in wallet_map.items():
        time.sleep(1.2)
        transactions = get_transactions(wallet, base_token_address)
        #time.sleep(2)
        if transactions:
            txns = transactions.get("result", {}).get("data", [])
            for txn in txns:
                signature = txn.get("signature")
                if signature:
                    signatures.append(signature)
                    signature_to_wallet[signature] = wallet

    if not signatures:
        print("No signatures found for the top wallets.")
        return False, "No transactions found."

    # Fetch transfer details for all collected signatures
    transfer_details = get_transfer_details(signatures)

    # Set to track wallets with mismatched transfers
    wallets_with_mismatches = set()

    # Define criteria for matching transfers
    def is_transfer_matching(transfer: Dict) -> bool:
        return (
            transfer.get("action") == "transfer" and
            transfer.get("status") == "Successful" and
            transfer.get("token") == base_token_address and
            transfer.get("destination") not in excluded_wallets
        )

    # Process each transfer detail
    for transfer in transfer_details:
        source_wallet = transfer.get("source")
        destination_wallet = transfer.get("destination")

        if source_wallet in wallet_map:
            if not is_transfer_matching(transfer):
                wallets_with_mismatches.add(source_wallet)

    # Print the amounts for wallets with mismatched transfers
    for wallet in wallets_with_mismatches:
        amount = wallet_map.get(wallet, 0)
        print(f"Wallet {wallet} has mismatched transfers. Amount: {amount}")

    return True, "Cluster analysis completed."


clusters("MBCccZZEbcvWzaHD9otPjmBMFaa6pG7XRYSw39HT5n2")
