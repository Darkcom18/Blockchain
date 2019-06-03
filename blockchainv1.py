# Create a Blockchain
#This will be the selection code to build future Dapp
# To be installed:
#The code is written in python, thus anaconda would be a good choice for environment
# Flask
# Postman HTTP Client: https://www.getpostman.com/

# Importing the libraries
import datetime # Each block has the own time
import hashlib #To hash the block
import json # When we will import Jason Jason library, we will use the functions from this library to encode before hash
from flask import Flask, jsonify #For web interface

# Building a Blockchain
class DarkcomBlockchain:

    def __init__(self):
        self.chain = []
        #Create empty mist
        #Then create the genenis block
        self.create_block(proof = 1, previous_hash = '0')
   # The second arg is the block of the first, but since genesis is the first, so we can use 0. SHA256 only encoded string.
   # After function create the first block, we going add new minied block to the list
   # The proof shows the block is mined while the previous_hash shows the link between new and old blocks'''
    
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block
        # Dictionary includes 4 essential keys index, timestamp,proof of block, and previous
        # More any data can be added based on the project
    def get_previous_block(self):
        return self.chain[-1]
    # Get the lastest block by index -1 of the chain
    # Proof of work: Must be hard to find but easy to verify. if it easy to find, miner will get tons of crytocurrencies
    # Easy to verify, that other miners can verify the first miner is ok
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            # Zero leading ID is a classic way of defining a problems that the miners have to solve to find the proof of work
            # More 0 leading, harder to solve
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    # Create the function which encrypt the block info by SHA256
    # The block is a dictionary, thus we can use Dom funtion in Json convert into string
    
    def is_valid(self, chain):
    # To check the validation of the chain, we use while loop to check.
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block # Since after validation True, the current block will become previous block
            block_index += 1
        return True # If all check is True, then the block is valid

#Mining our Blockchain

# Creating a Web App interface
app = Flask(__name__)

# Creating a Blockchain
blockchain = DarkcomBlockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
# To mine the block, we need to solve the proof of work problem fastest:
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations! You got a Darkcom block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200 # 200 is the HTTP OK which success return

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'The Darkcom Blockchain is valid.'}
    else:
        response = {'message': 'Hum...The Darkcom Blockchain is not valid.'}
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 5000)  # Host addr 0.0.0.0 to make it public
