import requests
from urllib.parse import urlparse
from Blockchain.block import Block
from Blockchain.blockchain import Blockchain
from Blockchain.sql_handler import sql_handler

def register_node(nodes, address):
    """
    Add a new node to the list of nodes
    :param address: Address of node. Eg. 'http://192.168.0.5:5000'
    """
    parsed_url = urlparse(address)
    nodes.add(parsed_url.netloc)

def valid_chain(blockchain, chain):
    """
    Determine if a given blockchain is valid
    :param chain: A blockchain
    :return: True if valid, False if not
    """
    last_block = chain[0]
    current_index = 1

    while current_index < len(chain):
        block = chain[current_index]
        # Check that the hash of the block is correct
        if block.previous_hash != last_block.hash:
            return False

        # Check that the Proof of Work is correct
        if not block.valid_proof(last_block, block):
            return False

        last_block = block
        current_index += 1

    return True

def resolve_conflicts(blockchain,nodes):
    """
    This is our consensus algorithm, it resolves conflicts
    by replacing our chain with the longest one in the network.
    :return: True if our chain was replaced, False if not
    """
    neighbours = nodes
    new_chain = None

    # We're only looking for chains longer than ours
    max_length = len(blockchain.chain)

    # Grab and verify the chains from all the nodes in our network
    for node in neighbours:
        response = requests.get(f'http://{node}/chain')

        if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['chain']

            # Check if the length is longer and the chain is valid
            if length > max_length and blockchain.valid_chain(chain):
                max_length = length
                new_chain = chain

    # Replace our chain if we discovered a new, valid chain longer than ours
    if new_chain:
        blockchain.chain = new_chain
        return True

    return False