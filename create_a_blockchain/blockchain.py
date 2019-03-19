import datetime
import hashlib
import json
from flask import Flask, jsonify

#Part 1 - Build a Blockchain

class Blockchain:
    #initialize chain and genisis block
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')
        
    #Creates a block with timestamp 
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    #Returns previous block in chain
    def get_previous_block(self):
        return self.chain[-1]
    
    #Finding nonce that fits our target for hexadecimal hash that starts with '0000'
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            #Validating proof of work by generating hash until it starts with '0000'
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
        