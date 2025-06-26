import json
import os
from web3 import Web3
from eth_account import Account

# --- CONFIGURATION ---

# Alchemy Sepolia RPC URL
# ALCHEMY_SEPOLIA_RPC_URL = "https://eth-sepolia.g.alchemy.com/v2/x_t22IRjJp871CHZrKJQB"

# Connect to Sepolia
# w3 = Web3(Web3.HTTPProvider(ALCHEMY_SEPOLIA_RPC_URL))
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

if not w3.is_connected():
    raise ConnectionError("Failed to connect to local hardhat network")

print(f"Connected to Sepolia: {w3.is_connected()}, Chain ID: {w3.eth.chain_id}")

# Load ABI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ABI_PATH = os.path.join(BASE_DIR, "LandRegistry_abi.json")
with open(ABI_PATH, "r") as abi_file:
    abi = json.load(abi_file)

# Contract address
CONTRACT_ADDRESS = Web3.to_checksum_address("0x5FbDB2315678afecb367f032d93F642f64180aa3")
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# --- TRANSACTION SENDER ---

def build_and_send_tx(function, sender_private_key, value_eth=0, gas=300000, gas_price_gwei=10):
    sender_account = Account.from_key(sender_private_key)
    sender_address = sender_account.address
    nonce = w3.eth.get_transaction_count(sender_address)

    txn = function.build_transaction({
        'chainId': w3.eth.chain_id,
        'gas': gas,
        'gasPrice': w3.to_wei(gas_price_gwei, 'gwei'),
        'nonce': nonce,
        'value': w3.to_wei(value_eth, 'ether'),
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=sender_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # Wait for transaction receipt before returning
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        raise Exception(f"Transaction failed or reverted: {tx_hash.hex()}")

    return tx_hash.hex()


# --- SMART CONTRACT INTERACTION FUNCTIONS ---

def register_land(plot_id, owner_name, district, subcounty, parish, village, plot_size, national_nin, sender_private_key):
    fn = contract.functions.registerLand(
        plot_id, owner_name, district, subcounty, parish, village, plot_size, national_nin
    )
    # The contract expects a payable call with 0.01 ETH for registration fee
    return build_and_send_tx(fn, sender_private_key, value_eth=0.01)

def transfer_land(plot_id, new_owner_name, new_national_nin, new_owner_address, sender_private_key):
    fn = contract.functions.transferLand(
        plot_id, new_owner_name, new_national_nin, Web3.to_checksum_address(new_owner_address)
    )
    return build_and_send_tx(fn, sender_private_key)

def start_lease(plot_id, tenant_address, lease_start_timestamp, lease_end_timestamp, sender_private_key):
    fn = contract.functions.startLease(
        plot_id, Web3.to_checksum_address(tenant_address), lease_start_timestamp, lease_end_timestamp
    )
    return build_and_send_tx(fn, sender_private_key)

def end_lease(plot_id, sender_private_key):
    fn = contract.functions.endLease(plot_id)
    return build_and_send_tx(fn, sender_private_key)

def split_and_transfer_land(original_plot_id, new_plot_id, new_owner_name, new_nin, new_owner_address, split_plot_size, sender_private_key):
    fn = contract.functions.splitAndTransferLand(
        original_plot_id,
        new_plot_id,
        new_owner_name,
        new_nin,
        Web3.to_checksum_address(new_owner_address),
        split_plot_size
    )
    return build_and_send_tx(fn, sender_private_key)

# --- READ-ONLY VIEWS ---

def get_land_parcel(plot_id):
    return contract.functions.viewLandByPlotId(plot_id).call()

def get_all_plots():
    return contract.functions.allPlotIds().call()

def get_owner_plots(owner_address):
    return contract.functions.ownerToPlots(Web3.to_checksum_address(owner_address)).call()

def get_plots_by_owner(owner_name):
    return contract.functions.searchLandsByOwnerName(owner_name).call()

def get_user_role(user_address):
    return contract.functions.getRole(Web3.to_checksum_address(user_address)).call()

# --- EXAMPLE USAGE ---

if __name__ == "__main__":
    PRIVATE_KEY = "95a3fcf63a41292887276f5f992cff36c5fcfbc6b06f4a59a0f2265e0b7dac9c"  # Replace with your private key

    # Register a land parcel (this will send 0.01 ETH registration fee)
    tx = register_land(
        plot_id="PLOT-345",
        owner_name="Alouzious Muhereza",
        district="Kabale",
        subcounty="Bubare",
        parish="Nyamweru",
        village="Katenga",
        plot_size=500,
        national_nin="M393887uyt67572JJ",
        sender_private_key=PRIVATE_KEY,
    )
    print("Register Land Tx Hash:", tx)

    # Split and transfer part of the land
    tx2 = split_and_transfer_land(
        original_plot_id="PLOT-345",
        new_plot_id="PLOT-345A",
        new_owner_name="Evelyn K",
        new_nin="C9000887EVL345TQ",
        new_owner_address="0xB44e4B2736Ca5D0A7aEf3251BdA7A123FbADd982",
        split_plot_size=200,
        sender_private_key=PRIVATE_KEY
    )
    print("Split & Transfer Tx Hash:", tx2)

    # View the updated original land parcel info
    info = get_land_parcel("PLOT-345")
    print("Updated Original Land Info:", info)

    # View the new parcel info
    info2 = get_land_parcel("PLOT-345A")
    print("New Parcel Info:", info2)
