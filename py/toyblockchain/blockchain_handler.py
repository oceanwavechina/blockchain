'''
Created on Mar 21, 2018

@author: liuyanan
'''

import json
from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import BlockChain
from jinja2.nodes import Block


app = Flask(__name__)

# generate a node address
node_identifier = str(uuid4()).replace('-', '')

# initantiate the blockchain
blockchain = BlockChain()


@app.route('/mine', methods=['GET'])
def mine():
    # run the proof of work to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(sender='0', recipient=node_identifier, amount=1)

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    required = ['sender', 'recipient', 'amount']
    values = request.get_json()

    if not all(k in values for k in required):
        return 'Missiong values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'transaction will be added to Block {index}'}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'new nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'new_chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':

    try:
        blockchain.set_self_node_id('localhost:5000')
        app.run(host='0.0.0.0', port=5000)
    except OSError:
        blockchain.set_self_node_id('localhost:5001')
        app.run(host='0.0.0.0', port=5001)
