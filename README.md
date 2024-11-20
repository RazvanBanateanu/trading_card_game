TRADING CARD GAME

Setup

1. Install required packages

To install the required Python packages, run:
pip install -r requirements.txt

2. Configure the API

Ensure you have the necessary files in place:
    - wallet.pem: This file should contain your private key for signing transactions.
    - tema-1.abi.json: ABI file of the smart contract you are interacting with.
    - update variable razvan with your wallet's address.

3. Running the API

To run the Flask API, execute the following command:
python3 main.py


API Endpoints

1. GET / - Welcome Message

Description: Returns a simple welcome message.

Response Example:

{
  "message": "Welcome to NFT Trading Card Game!"
}

2. GET /nft-supply - Get NFT Supply

Description: Returns the current supply of NFTs from the contract.

Response Example:

{
  "supply": [
    {
      "amount": "1",
      "attributes": "b'\\x00\\x00\\x01'",
      "creator": `b"d\\xc8z\\xfd$\\..."`,
      "frozen": "False",
      "name": "b'BPDA-TRADING-CARD'"
      "royalties": "10000",
      "token_type": "_EnumPayload(_discriminant__=1)"
      "uris": "[]"
    },
    ...
  ]
}

3. GET /nft-properties - Get NFT Properties

Description: Fetches the properties of the NFT you can trade with (power, class and rarity).

Response Example:

{
  "data": "080202"
}

4. GET /create-nft - Create a New NFT Card

Description: Creates a new NFT card with the properties obtained previously by using GET /nft-properties and uploads it to the MultiversX blockchain.

You must have a collection and the permissions to create NFTs. For this API, the collection should be named BPDA-8b7282.

Response Example:

{
  "message": "NFT created successfully"
}

5. GET /nft-to-trade-with - Get NFT to Trade With

Description: Fetches the NFT that is available for trading with the contract.

Response Example:

{
  "supply": 55
}

POST /exchange-nft - Exchange NFTs

Description: Allows users to exchange NFTs by providing nft_index and token_nonce in the request. The exchange will occur if the transaction is successful. 
 - "nft_index" : The nonce of the NTF that the user is trying to trade with from the contract's supply.
 - "token_nonce" : The nonce of the NTF that the user is trying to trade with from his wallet.
 
Example: curl -X POST "http://127.0.0.1:5000/exchange-nft?nft_index=81&token_nonce=5"

Response Example:

{
  "message": "NFT exchanged successfully",
  "transaction_hash": "0x123456789abcdef"
}
