from flask import Flask, render_template, request, redirect, url_for, jsonify
from Blockchain.block import Block
from Blockchain.blockchain import Blockchain
from Blockchain.sql_handler import sql_handler
from Blockchain.init_db import init_db
import User.init_db
from Blockchain.consensus import valid_chain
from urllib.parse import urlparse
import json
from cs50 import SQL
import requests
import secrets
import os

# Database setup
DATABASE = "blockchain.db"
DATABASE_USER = "voters.db"

# initialize the database
init_db(DATABASE=DATABASE)
User.init_db.init_db(DATABASE=DATABASE_USER)

# app
app = Flask(__name__)

# blockchain handlers
handler = sql_handler(DATABASE=DATABASE, DATABASE_USER=DATABASE_USER,difficulty=5,transactions=1)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Database handler
db = SQL(f"sqlite:///{DATABASE}")

# List to store known nodes in the net
cursor = db.execute('SELECT * FROM peers;')
nodes_set = set()
if cursor!=[]:
    for i in cursor:
        nodes_set.add(i['peers'])

def broadcast_block():
    """Broadcast the latest block to all nodes in the network."""
    new_block = handler.blockchain.chain[-1]
    block_dict = new_block.to_dict()
    for node in nodes_set:
        try:
            r = requests.post(f'http://{node}/append_block', json=json.dumps(block_dict))
        except requests.exceptions.RequestException as e:
            print(f"Could not reach node {node}: {e}")

@app.route('/')
def home():
    return redirect('/blockchain')

@app.route('/append_block', methods=['POST'])
def append_block():
    values = request.get_json()
    block = Block.from_dict(json.loads(values)) 
    if (block.index == (handler.blockchain.chain[-1].index + 1)):
        prev_hash = handler.blockchain.chain[-1].hash
        if prev_hash == block.previous_hash:
            hash = block.hash
            curr_hash = block.compute_hash()
            if curr_hash == hash:
                print(handler.blockchain.add_block(block))
                return jsonify({'validity': True, 'index': i}), 201
            else:
                return jsonify({'validity': False}), 500
        else:
            return jsonify({'validity': False}), 500

@app.route('/get_chain', methods=['GET'])
def get_chain():
    # nodes_set.add((request.host_url))
    print(request.host_url.lstrip('https://'))
    chain_data = [block.to_dict() for block in handler.blockchain.chain]
    return jsonify({"length": len(chain_data), "chain": chain_data, "nodes": list(nodes_set)})

@app.route('/add_vote', methods=['POST'])
def add_transaction():
    new_transaction = request.json
    temp = handler.add_vote(new_transaction)
    if isinstance(temp, bool) and temp:
        broadcast_block()
        return jsonify({"message": "Vote cast successfully!"}), 201
    elif isinstance(temp,dict) and temp.get('status') == True:
        broadcast_block()
        return jsonify({"message": f"Vote cast successfully!\nTime: {temp['transaction_times'][new_transaction['public_key']]} seconds"}), 201
    else:
        handler.push_blockchain()
        for node in nodes_set:
            requests.get(f'http://{node}/nodes/resolve')
        return jsonify({"message": "User already voted!"}), 500

@app.route('/blockchain', methods=['GET'])
def view_blockchain():
    chain = handler.blockchain.chain
    return render_template('blockchain.html', blockchain=chain)

@app.route('/mine', methods=['GET'])
def mine_block():
    handler.blockchain.mine_pending_votes()
    handler.push_blockchain()
    broadcast_block()
    resolve_conflicts()
    return redirect(url_for('view_blockchain'))

@app.route('/validate', methods=['GET'])
def validate_blockchain():
    is_valid = handler.blockchain.is_chain_valid()
    return render_template('validate.html', is_valid=is_valid)

@app.route('/verify_vote',methods=['GET','POST'])
def verify_vote():
    pub_key = request.json['public_key']
    vote = handler.verify_vote(pub_key)
    return vote

@app.route('/result')
def result():
    votes = handler.calculate_votes()
    return render_template('result.html', candidates=votes)

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values['nodes']
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        if node not in nodes_set:
            nodes_set.add(node)
            db.execute('INSERT INTO peers(peers) VALUES (?)',node)
    return jsonify({'message': 'New nodes have been added', 'total_nodes': list(nodes_set)}), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """Resolve conflicts by replacing the chain with the longest one in the network."""
    replaced = resolve_conflicts()
    if replaced:
        return jsonify({"message": "Chain was replaced with a longer, valid chain."}), 200
    else:
        return jsonify({"message": "This chain is already the longest, no replacement occurred."}), 200

def resolve_conflicts():
    """Resolve conflicts by replacing our chain with the longest one in the network."""
    longest_chain = None
    max_length = len(handler.blockchain.chain)
    for node in nodes_set:
        try:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                chain_data = response.json()
                length = chain_data['length']
                chain = [Block.from_dict(b) for b in chain_data['chain']]
                if length > max_length and valid_chain(chain,handler.blockchain.difficulty):
                    max_length = length
                    longest_chain = chain
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to node {node}: {e}")

    if longest_chain:
        handler.blockchain.chain = longest_chain
        handler.push_blockchain()
        return True
    return False

if __name__ == '__main__':
    port = 5001  # Default port; adjust for other nodes
    resolve_conflicts()
    app.run(host='0.0.0.0', port=port)
