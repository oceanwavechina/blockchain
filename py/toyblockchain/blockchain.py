'''
Created on Mar 21, 2018

@author: liuyanan
'''

import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests

'''
    https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

    Understanding Proof of Work
    A Proof of Work algorithm (PoW) is how new Blocks are created or mined on the blockchain.
    The goal of PoW is to discover a number which solves a problem.
    The number must be difficult to find but easy to verify—computationally speaking—by anyone on the network.
    This is the core idea behind Proof of Work.
'''


class BlockChain(object):
    def __init__(self):
        self.chain = []
        self.currrent_transactions = []

        # create the genesis block
        self.new_block(previous_hash=1, proof=100)

        self.nodes = set()
        self.self_node = None

    def set_self_node_id(self, node):
        self.self_node = node

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(address)

        # 如果其他节点伪装成该节点，就完蛋了
        if parsed_url.netloc is not self.self_node:
            self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('\n---------------\n')

            # check hash is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # check proof of work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """
        neighbours = self.nodes
        new_chain = None

        # we're only looking for chains longer than ours
        max_length = len(self.chain)

        for node in neighbours:
            print(f'http://{node}/chain')
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        block = {'index': len(self.chain) + 1,
                 'timestamp': time(),
                 'transactions': self.currrent_transactions,
                 'proof': proof,
                 'previous_hash': previous_hash or self.hash(self.chain[-1]),
                 }

        # reset current transaction list, why ??
        self.currrent_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.currrent_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.

        这里还要用到上一次的proof，所以我们没办法复用我们之前的proof，这就保证了每次重新计算
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>

        这个是 共识机制 中的一种 POW (proof of work), DPOS(Delegated Proof of Stake)
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof
