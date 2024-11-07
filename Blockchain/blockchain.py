from .block import Block
import requests
import time

class Blockchain:
    # blockchain structure : 
    def __init__(self,difficulty=4,transactions=1): 
        self.chain: list[Block] = []
        self.pending_transactions: list[dict] = []
        # Initialize with genesis block
        self.difficulty = difficulty
        self.transactions = transactions # Number of transactions before a block is hashed.
        self._create_genesis_block()

    def _create_genesis_block(self): #first block
        genesis = Block(0)
        self.add_block(genesis)
    
    def add_block(self,block : Block): #append block to chain
        if self.verify_unique_node(block)==1:
            self.chain.append(block)
            return "block appended"
        else:
            return "block not appended"
    
    def get_last_block(self): #retreive last block from the chain
        if self.chain!=[]:
            return self.chain[-1]
        else:
            return None

    def mine_pending_votes(self): #push pending transactions into a new block(max transacs = 6) and (min transacs = 1)
        last_block = self.get_last_block()
        if len(self.pending_transactions)>self.transactions-1:
            start_time = time.time()
            new_block = Block(index=last_block.index + 1, 
                                previous_hash=last_block.hash, 
                                transactions=self.pending_transactions[0:Blockchain.transactions],
                                public_keys = ([x['public_key'] for x in self.pending_transactions[0:Blockchain.transactions]])
                            )
            self.pending_transactions = self.pending_transactions[Blockchain.transactions:]
            new_block.nonce = self.proof_of_work(new_block,self.difficulty)
            self.add_block(new_block)
            stop_time = time.time()
            transaction_times = {
                x['public_key']: stop_time - x['time'] for x in new_block.transactions
            }
            return {'status':True,'time':stop_time-start_time,'transaction_times':transaction_times}
        return {'status':False}

    @staticmethod
    def proof_of_work(block : Block, difficulty=4)->int: #Calculate PoW for a block (get a nonce value that satisfies difficulty)
        block.nonce = 0
        while not block.hash.startswith('0' * difficulty):
            block.nonce += 1
            block.hash = block.compute_hash()
        return block.nonce
    
    def is_chain_valid(self)->dict:
        prev_hash = 0
        for i in range(0,len(self.chain)):
            if prev_hash == self.chain[i].previous_hash:
                hash = self.chain[i].hash
                curr_hash = self.chain[i].compute_hash()
                if curr_hash == hash:
                    self.chain[i].hash = hash
                    prev_hash = hash
                else:
                    return {
                        'validity':False,
                        'index':self.chain[i-1].index
                    }
            else:
                return {
                    'validity':False,
                    'index':self.chain[i].index
                    }
        return {
                    'validity':True,
                    'index': None
                }
    
    def add_vote(self, vote_transaction):
        if self.has_user_voted(vote_transaction['public_key']):
            return False
        # Add the vote to pending transactions
        self.pending_transactions.append(vote_transaction)
        return True

    
    def has_user_voted(self, public_key):
        # Check each block in the blockchain
        for block in self.chain:
            for transaction in block.transactions:
                if transaction['public_key'] == public_key:
                    return True  # User has voted
        for vote in self.pending_transactions:
            if vote['public_key'] == public_key:
                return True
        return False  # User has not voted
    
    def verify_unique_node(self,block)->int:
        if block not in self.chain:
            for i in range(len(self.chain)):
                if self.chain[i].index == block.index:
                    return 0
                else:
                    continue
            return 1
        else:
            return 0
    
    def valid_proof(current_block:Block,previous_block:Block):
        if Block.compute_hash(previous_block)==current_block.previous_hash:
            return True
        else:
            return False

    def __calculate_votes__(self):
        dict_votes = {}
        for i in range(len(self.chain)):
            for j in range(len(self.chain[i].transactions)):
                if (self.chain[i].transactions[j]['vote']) in dict_votes.keys():
                    dict_votes[self.chain[i].transactions[j]['vote']] += 1
                else:
                    dict_votes[self.chain[i].transactions[j]['vote']] = 1
        return dict_votes

# blockchain = Blockchain()
# print(blockchain.get_last_block())
# start_time = time.time()
# for i in range(0,6):
#     vote = {
#         'public_key' : f'Alice{i}',
#         'vote' : 'bob'
#     }
#     blockchain.add_vote(vote)
#     # print(blockchain.pending_transactions)
#     test = blockchain.mine_pending_votes()
#     if test['status'] == True:  
#         print(i,":",test['time'])

# for i in range(6,13):
#     vote = {
#         'public_key' : f'Alice{i}',
#         'vote' : 'bob'
#     }
#     blockchain.add_vote(vote)
#     # print(blockchain.pending_transactions)
#     test = blockchain.mine_pending_votes()
#     if test['status'] == True:
#         print(i,":",test['time'])

# print(blockchain.pending_transactions)
# # blockchain.chain[2].hash = 0
# # print("Chain is:",blockchain.chain)

# print("Is the chain valid?")
# dict = blockchain.chain[1].to_dict()
# print(dict)
# print(blockchain.is_chain_valid())
# print(blockchain.__calculate_votes__())