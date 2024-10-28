from flask import Flask, render_template, request, redirect, session, abort,url_for,jsonify
from Blockchain.block import Block
from Blockchain.blockchain import Blockchain
from Blockchain.sql_handler import sql_handler
from Blockchain.init_db import init_db
from Blockchain.consensus import register_node,resolve_conflicts,valid_chain
from cs50 import SQL
from urllib.parse import urlparse
import requests
import secrets
import os
import sqlite3

# Database setup
DATABASE = "blockchain.db"

# initialize the database
init_db(DATABASE=DATABASE)

app = Flask(__name__)

handler = sql_handler(DATABASE=DATABASE)

# List to store known nodes in the network
nodes_set = set()

nodes_set.add("http://127.0.0.1:5002")

#init blockchain
blockchain = handler.init_blockchain()

print("Blockchain:",blockchain.chain)

app.config['SECRET_KEY'] = secrets.token_hex(16)

db = SQL(f"sqlite:///{DATABASE}")

# Routes
@app.route('/')
def home():
    return redirect('/blockchain')

@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.todict())
    return jsonify({"length": len(chain_data), "chain": chain_data, "nodes": list(blockchain.peer_nodes)})

# Update the add_transaction function to broadcast changes
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    new_transaction = request.json
    if blockchain.add_vote(new_transaction):
        blockchain.mine_pending_votes()
        handler.push_blockchain(blockchain)
        print(new_transaction)

        return jsonify({"message": "Transaction added and broadcasted", "transaction": new_transaction}), 201
    else:
        handler.push_blockchain(blockchain)
        return jsonify({"message":"User already voted!"}),500

@app.route('/blockchain', methods=['GET'])
def view_blockchain():
    chain = blockchain.chain  # Get the current chain
    return render_template('blockchain.html', blockchain=chain)

@app.route('/mine', methods=['GET'])
def mine_block():
    blockchain.mine_pending_votes()  # Mine all pending transactions
    handler.push_blockchain(blockchain=blockchain) #update the database with the current blockchain
    return redirect(url_for('view_blockchain'))

@app.route('/validate', methods=['GET'])
def validate_blockchain():
    is_valid = blockchain.is_chain_valid()
    return render_template('validate.html', is_valid=is_valid)

@app.route('/result')
def result():
        vote_counts = []
        for block in blockchain.chain:
            for transaction in block.transactions:
                if isinstance(transaction, dict) and 'vote' in transaction:
                    vote = transaction['vote']
                    vote_counts[vote] = vote_counts.get(vote, 0) + 1
        return vote_counts

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        consensus.register_node(nodes_set,node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(nodes_set),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = consensus.resolve_conflicts(blockchain,nodes_set)

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)



