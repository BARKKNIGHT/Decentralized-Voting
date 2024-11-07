import requests
from urllib.parse import urlparse
from Blockchain.block import Block
from Blockchain.blockchain import Blockchain
from Blockchain.sql_handler import sql_handler

def startswith(block : Block,zeros):
    if block.hash[:len(zeros)]== zeros:
        return True
    else:
        return False

def valid_proof(last_block, block,difficulty):
    """
    Validate the block's proof of work by ensuring the hash has a specified number of leading zeroes.
    :param last_block: The previous block in the chain
    :param block: The current block to validate
    :return: True if the block's hash meets the difficulty criteria, False otherwise
    """
    # Verify the block's hash starts with the number of zeroes defined by the difficulty level
    return startswith(block,'0' * difficulty) and block.previous_hash == last_block.hash

def valid_chain(chain):
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
            if not valid_proof(last_block, block,4):
                return False

            last_block = block
            current_index += 1

        return True

def resolve_conflicts(blockchain: Blockchain):
    """
    This is our consensus algorithm, it resolves conflicts
    by replacing our chain with the longest one in the network.
    :return: True if our chain was replaced, False if not
    """
    neighbours = blockchain.peer_nodes
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