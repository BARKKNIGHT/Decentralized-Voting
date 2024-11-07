from cs50 import SQL
from .block import Block
from .blockchain import Blockchain
import time
import datetime
import json

class sql_handler:
    def __init__(self,DATABASE,DATABASE_USER,difficulty=4,transactions=1):
        self.db = SQL(f"sqlite:///{DATABASE}")
        self.user_db = SQL(f"sqlite:///{DATABASE_USER}")
        self.blockchain : Blockchain = self.fetch_blockchain(difficulty,transactions)

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
        
    def push_blockchain(self):
        current_list = self.blockchain.chain
        last_block = self.get_last_block()
        if last_block!=None:
            for i in range(last_block.index+1,len(current_list)):
                self.push_block(current_list[i])
        else:
            for i in range(0,len(self.blockchain.chain)):
                self.push_block(current_list[i])

    def fetch_block(self,index : int):
        temp = self.db.execute('SELECT * FROM blockchain WHERE id=?',(index,))
        if temp!=None:
            block = Block.from_dict(json.loads(temp[0]['block_json']))
            return block
        else:
            return None
        
    def fetch_blockchain(self,difficulty=4,transactions=1):
        '''This is a function to fetch the blockchain from the database (type : Blockchain)'''
        current_list = self.db.execute('SELECT * FROM blockchain')

        if current_list is not None and current_list != []:
            chain = []
            for i in range(0,len(current_list)):
                block_temp = Block.from_dict(json.loads(current_list[i]['block_json']))
                chain.append(block_temp)
            blockchain = Blockchain(difficulty=difficulty,transactions=transactions)
            blockchain.chain = chain
            return blockchain
        else:
            blockchain = Blockchain(difficulty=difficulty,transactions=transactions)
            self.blockchain = blockchain
            return blockchain

    def add_vote(self, vote_transaction):
        if self.blockchain.add_vote(vote_transaction):
            temp = self.blockchain.mine_pending_votes()
            if temp['status'] == True:
                self.push_blockchain()
            return temp
        return False
    
    def calculate_votes(self):
        votes = self.blockchain.__calculate_votes__()
        candidates = self.user_db.execute('SELECT * FROM candidates;')
        print(candidates)
        votes = {}
        for k in range(len(candidates)):
            votes[candidates[k]['candidate']] = 0
        for i in range(len(self.blockchain.chain)):
            print(i)
            for j in range(Blockchain.transactions):
                try:
                    if len(self.blockchain.chain[i].transactions) != 0:
                        votes[self.blockchain.chain[i].transactions[j]['vote']] += 1
                        print(self.blockchain.chain[i].transactions[j]['vote'])
                except:
                    print("key error!")
                    print(votes)
        try:
            for i in votes.keys():
                self.user_db.execute('UPDATE candidates SET votes = ? WHERE candidate = ?',votes[i],i)
            return votes
        except:
            return votes
        
    def verify_vote(self,public_key):
        for block in self.blockchain.chain:
            if block.transactions != []:
                for vote in block.transactions:
                    if vote['public_key'] == public_key:
                        return json.dumps(block.to_dict())
        return json.dumps('VOTE NOT FOUND!')