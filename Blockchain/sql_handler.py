from cs50 import SQL
from .block import Block
from .blockchain import Blockchain
import time
import json

class sql_handler:
    def __init__(self,DATABASE):
        self.db = SQL(f"sqlite:///{DATABASE}")

    def push_block(self,block : Block):
        block_dict = block.to_dict()
        self.db.execute('INSERT INTO blockchain(id,block_json) VALUES(?,?)',block_dict['Index'],json.dumps(block_dict))

    def get_last_block(self):
        '''Get last block from the database (type : Block | None)'''
        block = self.db.execute('SELECT * FROM blockchain ORDER BY id DESC LIMIT 1')
        if block is not None and block!=[]:
            block = Block.from_dict(json.loads(block[0]['block_json']))
            return block
        else:
            return None
        
    def push_blockchain(self,blockchain: Blockchain):
        current_list = blockchain.chain
        
        print(current_list)
        last_block = self.get_last_block()
        if last_block!=None:
            for i in range(last_block.index+1,len(current_list)):
                self.push_block(blockchain.chain[i])
        else:
            for i in range(0,len(blockchain.chain)):
                self.push_block(blockchain.chain[i])

    def fetch_block(self,index : int):
        block = self.db.execute('SELECT * FROM blockchain WHERE id=?',(index,))
        block = Block.from_dict(json.loads(block[0]['block_json']))

    def fetch_blockchain(self):
        '''This is a function to fetch the blockchain from the database (type : Blockchain)'''
        current_list = self.db.execute('SELECT * FROM blockchain')

        if current_list is not None and current_list != []:
            blockchain = []
            for i in range(0,len(current_list)):
                block_temp = Block.from_dict(json.loads(current_list[i]['block_json']))
                blockchain.append(block_temp)
            blockchain = Blockchain(blockchain)
            return blockchain
        else:
            blockchain = Blockchain()
            return blockchain

    def fetch_blockchain_auto_append(self,blockchain : Blockchain):
        block = self.db.execute('SELECT * FROM blockchain')
        for i in range(1,len(block)):
            block = Block.from_dict(json.loads(block[i]['block_json']))
            blockchain.add_block(block)
    
    def init_blockchain(self):
        if self.get_last_block() == None:
            blockchain = Blockchain()
            self.push_blockchain(blockchain=blockchain)
            return blockchain
        else:
            blockchain = Blockchain()
            blockchain.chain = []
            blockchain.chain = self.fetch_blockchain().chain
            return blockchain
        
    def add_vote(self, vote_transaction):
        blockchain = self.fetch_blockchain()
        if blockchain.add_vote(vote_transaction):
            blockchain.mine_pending_transactions()
            self.push_blockchain(blockchain)
            return True
        return False

# handler = sql_handler("blockchain.db")
# blockchain = handler.init_blockchain()
# print(handler.get_last_block())
# for i in range(0,12):
#     vote = {
#         'public_key':i,
#         'vote':"Alice pays BOB ${i}."
#     }
#     blockchain.add_vote(vote)
#     blockchain.mine_pending_votes()
#     handler.push_blockchain(blockchain)

# handler.fetch_blockchain()

# print(blockchain.chain)