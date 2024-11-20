from flask import Flask, jsonify, request
from pathlib import Path
from multiversx_sdk import Address, Token, TokenTransfer
from multiversx_sdk import (ProxyNetworkProvider, QueryRunnerAdapter, SmartContractQueriesController)
from multiversx_sdk.abi import Abi
from multiversx_sdk import UserSigner, TransactionComputer
from multiversx_sdk import SmartContractTransactionsFactory, TransactionsFactoryConfig
import base64

app = Flask(__name__)

# Initialize necessary objects
contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqrqz7r8yl5dav2z0fgnn302l2w7xynygruvaq76m26j")
razvan = Address.new_from_bech32("erd13c9vzmjfpwfl8lm4u7pdlu30uer0a7y2swklj7lra7kxkn36fpkstqmtsw")
signer = UserSigner.from_pem_file(Path("./lastwallet.pem"))
config = TransactionsFactoryConfig(chain_id="D")
provider = ProxyNetworkProvider("https://devnet-api.multiversx.com/")
transaction_computer = TransactionComputer()
query_runner = QueryRunnerAdapter(ProxyNetworkProvider("https://devnet-api.multiversx.com/"))
abi = Abi.load(Path("/home/ubuntu/bpda/tema-1/output/tema-1.abi.json"))
query_controller = SmartContractQueriesController(query_runner, abi)
factory = SmartContractTransactionsFactory(config)


nft_properties = None

# API Routes

@app.route('/', methods=['GET'])
def hello():
    return "Welcome to NFT Trading Card Game!"



@app.route('/nft-supply', methods=['GET'])
def get_nft_supply():
    try:
        result = getNFTSupply()
        result_list = [convert_namespace_to_dict(item) for item in result]
        return jsonify({"supply": result_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/nft-properties', methods=['GET'])
def get_nft_properties():
    try:
        data = getNFTProperties()
        return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create-nft', methods=['GET'])
def create_nft_card():
    try:
        createNFTCard()
        return jsonify({"message": "NFT created successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/nft-to-trade-with', methods=['GET'])
def get_nft_to_trade_with():
    try:
        result = getNFTtoTradeWith()
        return jsonify({"supply": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/exchange-nft', methods=['POST'])
def exchange_nft():
    try:
        nft_index = request.args.get('nft_index', 95)  
        token_nonce = request.args.get('token_nonce', 1) 
        result = exchangeNFT(int(nft_index), int(token_nonce))  
        return jsonify({"message": "NFT exchanged successfully", "transaction_hash": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Helper Functions 

def getNFTProperties():
    global nft_properties
    
    tx = factory.create_transaction_for_execute(
        sender = razvan,
        contract = contract,
        function = "getYourNftCardProperties",
        gas_limit = 30000000,
        arguments = []
    )

    account_on_network = provider.get_account(razvan)
    tx.nonce = account_on_network.nonce
    tx.signature = signer.sign(transaction_computer.compute_bytes_for_signing(tx))
    hash = provider.send_transaction(tx)
    print(hash)    
    tx_details = provider.get_transaction(hash)
    tx_status = tx_details.status
    while str(tx_status) != "success":
        tx_details = provider.get_transaction(hash)
        tx_status = tx_details.status
        print(tx_status)
 
    if str(tx_status) == "success":
        if "smartContractResults" in tx_details.raw_response:
            raw_data = tx_details.raw_response['smartContractResults'][0]['data']
            result = raw_data.split('@')[-1]
        elif "logs" in tx_details.raw_response:
            raw_data = tx_details.raw_response['logs']['events'][0]['data']
            print(raw_data)
            decoded_bytes = base64.b64decode(raw_data)
            decoded_string = decoded_bytes.decode('utf-8')
            result = decoded_string.split('@')[-1]
    if len(result) > 8:
        return "An error occurred..."
    
    nft_properties = result
    return result

def createNFTCard():
    uri = 'https://www.freepnglogos.com/uploads/dog-png/bow-wow-gourmet-dog-treats-are-healthy-natural-low-4.png'

    tx = factory.create_transaction_for_execute(
        sender= razvan,
        contract= razvan,
        gas_limit= 30000000,
        function="ESDTNFTCreate",
        arguments= ["BPDA-8b7282", 1, "test.api", 1000, 0, int(nft_properties, 16), uri]
    )

    account_on_network = provider.get_account(razvan)
    tx.nonce = account_on_network.nonce
    tx.signature = signer.sign(transaction_computer.compute_bytes_for_signing(tx))
    hash = provider.send_transaction(tx)
    return hash


def getNFTtoTradeWith():
    query = query_controller.create_query(
        contract=contract.to_bech32(),
        function="nftSupply",
        arguments=[],
    )

    response = query_controller.run_query(query)
    data_parts = query_controller.parse_query_response(response)

    byte_sequence = bytes.fromhex(nft_properties)

    counter = 1
    for item in data_parts[0]:
        if item.attributes == byte_sequence:
            return counter
        counter+=1


def getNFTSupply():
    query = query_controller.create_query(
        contract=contract.to_bech32(),
        function="nftSupply",
        arguments=[],
    )

    response = query_controller.run_query(query)
    data_parts = query_controller.parse_query_response(response)
    return data_parts[0]


def exchangeNFT(nft_index, token_nonce):

    token_transfer = [TokenTransfer(Token("BPDA-8b7282", token_nonce), 1)]

    tx = factory.create_transaction_for_execute(
        sender=razvan,
        contract=contract,
        gas_limit=60000000,
        function="exchangeNft",
        arguments=[nft_index],
        token_transfers=token_transfer
    )

    account_on_network = provider.get_account(razvan)
    tx.nonce = account_on_network.nonce
    tx.signature = signer.sign(transaction_computer.compute_bytes_for_signing(tx))
    hash = provider.send_transaction(tx)
    return hash

def convert_namespace_to_dict(namespace_obj):
    result_dict = vars(namespace_obj)
    result_dict = {str(key): str(value) for key, value in result_dict.items()}
    return result_dict


    

if __name__ == '__main__':
    app.run(debug=True)
