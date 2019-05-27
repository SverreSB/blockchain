import datetime
import hashlib
import json
#Installs: 
#   pip install Flask==0.12.2
#   pip install requests==2.18.4 
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
#Part 2 - Build a cryptocurrency

class Blockchain:
    #initialize chain and genisis block
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        
    #Creates a block with timestamp 
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'hash': '',
                'previous_hash': previous_hash,
                'transactions': self.transactions} 
        self.transactions = []
        self.chain.append(block)
        
        return block

    #Returns previous block in chain
    def get_previous_block(self):
        return self.chain[-1]
    
    #Finding nonce that fits our target for hexadecimal hash that starts with '0000'
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        
        #Validating proof of work by generating hash until it starts with '0000'
        while check_proof is False:
            hash_operator = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operator[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
                
        return new_proof
    
    #Function that returns a 64 char hashed block
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    #Boolean function for checking if chain is valid or not
    def is_valid_chain(self, chain):
        previous_block = chain[0]
        block_index = 1
        
        #Iterate through chain
        while block_index < len(chain):
            #Create current block and check if previous_block has same hash as block's previous_hash key
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            #To validate proof of work
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operator = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operator[:4] != '0000':
                return False
            
            #Setting new values to previous_block and block_index to keep iterating through chain
            previous_block = block
            block_index += 1
            
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain())
        
        for node in network:
            response = request.get(f'http://{node}/mine_block')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if(length > max_length and self.is_valid_chain(chain)):
                    max_length = length
                    longest_chain = chain
            
        if longest_chain:
            self.chain = longest_chain
            return True
        
#Part 2 - mining
        
#Creating a web app
app = Flask(__name__)

#creating an address for the node on port 5000
node_address = str(uuid4()).replace('-', '')

#creating a blockchain
blockchain = Blockchain()

#Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    #Checking proof of work
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    
    #Finding previous hash, adding transaction and creating new block
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Sverre', amount = 6)
    block = blockchain.create_block(proof, previous_hash)
    
    response = {'message': 'Confirmation: Block successfully mined',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'hash': block['hash'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200
    
#Getting the complete chain
@app.route('/get_chain', methods = ['GET'])
def get_block():
    response = {'chain': blockchain.chain,
                'lenght': len(blockchain.chain)}
    return jsonify(response), 200

#Checking if blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    valid = blockchain.is_valid_chain(blockchain.chain)
    response = {'message': "Is blockchain valid: {}".format(valid)}
    return jsonify(response), 200

#Adding transaction to blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transactions are missing'
    index = add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201

#Connecting new node
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')

    if nodes is None:
        return 'No node', 400

    for node in nodes:
        blockchain.add_node(node)
    
    response = {
        'message': 'All the nodes are connected. The blockchain now contains the following nodes: ',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message': 'The nodes had different chains so the chain was replaced by the longer chain',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'All good. The chain is the largest one.',
            'actual_chain': blockchain.chain
            }
    
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)