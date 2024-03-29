# Create a Darkcom crytocurrency

# The code continue based on the blockchainv1 skelection file

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

"""
The thing makes a blockchain become a crytocurrency is the transaction.
Second, to make the transaction become global, verified and updated by other nodes, we also need the transaction consensus 
"""
# Part 1 - Building a Blockchain

class DarkcomBlockchain:

    def __init__(self):
        self.chain = []
        #The transaction function order is very important.
        #Transaction happend before the block is created. When the transaction is done, new blocks will be added into the chain
        #Thus the transaction must happen before the geneus block, thus it will know what to transfer, and time.
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set() #Create other nodes to do transaction and test the funtions

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions':self.transactions} # The order here is not important
        self.transactions = [] # The transaction must be empty when the process finish, then welcome the new transaction
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_valid(self, chain):
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
            previous_block = block
            block_index += 1
        return True
    def add_transaction(self,sender, receiver, amount): # Info of transaction
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'amount':amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1 
        # We return the block transaction. Since the lastest block is a fix block in the chain, thus it cannot be transferred anymore
        # Therefore, we would return the index of the next block, which can be used for transaction.      
    def add_node(self, address):
        parsed_url = urlparse(address) # address = http://127.0.0.1:5000/
        self.nodes.add(parsed_url.netloc) #since nodes is a set, thus we cannt use append
    
    def replace_chain(self): #each node have their own, thus we need to update by the longest chain
        network = self.nodes
        longest_chain =  None #Since we have ot scanned all the network to know the longest.
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')  
            # Because we check in all specific nodes, thus it s better to get response from nodes
            # Each node has different port. we used parsed url to the node
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_valid(chain):#check the length to update and the validation
                    max_length = length
                    longest_chain = chain
        if longest_chain: #If longest_chain is not none, the chain is updated
            self.chain = longest_chain # Here we update the chain of the whole class by the longest chain
            return True
        return False # If the nodes is not in the network
          
# Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

#Create an address for the node on Port 5000
node_address = str(uuid4()).replace('-','')
# We need address, whenever miner mines, there will be reward or fee from sender to the miner.
# uuid4 will rabdome create address

# Creating a Blockchain
blockchain = DarkcomBlockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    blockchain.add_transaction(sender = node_address,receiver='Pham',amount=18) # Add info of transaction
    response = {'message': 'Congratulations! You got a Darkcom block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions':block['transactions']} # Add the transaction into the response
    return jsonify(response), 200

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
#Add a new transaction to the blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all(key in json for key in transaction_keys):
        return 'Some missing elements in transactions',400 #400 is the response of http for bad request
    index = blockchain.add_transaction(json['sender'],json['receiver'],json['amount'])
    response = {'message': f'The transaction will be added to the block {index}'}
    return jsonify(response), 201 #since we create the new block, so we use 201 instead of 200

# Descentralized
#2 more request to do, to connect nodes, and update them
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes') #get the address of the nodes
    if nodes is None:
        return 'No node!', 400
    for node in nodes: #create a loop to add node to the nodes list
        blockchain.add_node(node)
    response = {'message':'Nodes are connected! The Darkcom chain has been updated!',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response),201
#Replace the out-of-date chain by the newest chain:
@app.route('/replace_chain', methods = ['GET']) #nothing to create more
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'Hum...The Darkcom Blockchain is out of date!',
                    'new_chain':blockchain.chain} #since the chain has already been updated!
    else:
        response = {'message': 'Congrats! The Darkcom Blockchain is up to date chain!.',
                    'actual_chain':blockchain.chain}
    return jsonify(response), 200  

# Running the app 
app.run(host = '0.0.0.0', port = 5002)

