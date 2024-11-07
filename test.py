from Blockchain.init_db import init_db
from Blockchain.sql_handler import sql_handler
from Blockchain.block import Block
from Blockchain.consensus import valid_chain
import User.init_db
from cs50 import SQL
import requests

# Database setup
DATABASE = "blockchain.db"
DATABASE_USER = "voters.db"

# List to store known nodes in the network
nodes_set = set()

handler = sql_handler(DATABASE=DATABASE, DATABASE_USER=DATABASE_USER)

# initialize the database
init_db(DATABASE=DATABASE)
User.init_db.init_db(DATABASE=DATABASE_USER)

db = SQL(f"sqlite:///{DATABASE}")

cursor = db.execute('SELECT * FROM peers;')
nodes_set = set()
if cursor!=[]:
    for i in cursor:
        nodes_set.add(i['peers'])

def resolve_conflicts():
    """Resolve conflicts by replacing our chain with the longest one in the network."""
    longest_chain = None
    max_length = len(handler.blockchain.chain)
    for node in nodes_set:
        try:
            print(node)
            response = requests.get(f'http://{node}/get_chain')
            print(response.content)
            if response.status_code == 200:
                chain_data = response.json()
                length = chain_data['length']
                print(length)
                chain = [Block.from_dict(b) for b in chain_data['chain']]
                if length > max_length and valid_chain(chain):
                    print("t")
                    max_length = length
                    longest_chain = chain
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to node {node}: {e}")
    if longest_chain!=None:
        handler.blockchain.chain = longest_chain
        return True
    else:
        return False

resolve_conflicts()





