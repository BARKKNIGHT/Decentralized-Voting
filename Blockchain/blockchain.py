from .block import Block
import time

class Blockchain:
    transactions = 1
    def __init__(self,chain = None) -> None:
        self.pending_transactions = []
        self.chain = chain if chain is not None else []
        if not self.chain:  # If no blocks found in input params, create a genesis block
            self._create_genesis_block()

    def _create_genesis_block(self): #first block
        genesis = Block(0)
        self.add_block(genesis)

    def add_transaction(self, transaction): #append transactions in a buffer
        self.pending_transactions.append(transaction)
    
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
        if len(self.pending_transactions)>Blockchain.transactions-1:
            new_block = Block(index=last_block.index + 1, 
                                previous_hash=last_block.hash, 
                                transactions=self.pending_transactions[0:Blockchain.transactions])
            self.pending_transactions = self.pending_transactions[Blockchain.transactions:]
            new_block.nonce = self.proof_of_work(new_block)
            print(self.add_block(new_block))

    def proof_of_work(self, block : Block, difficulty=4)->int: #Calculate PoW for a block (get a nonce value that satisfies difficulty)
        block.nonce = 0
        while not block.hash.startswith('0' * difficulty):
            block.nonce += 1
            block.hash = block.compute_hash()
        return block.nonce
    
    def is_chain_valid(self)->int:
        prev_hash = 0
        for i in range(0,len(self.chain)):
            if prev_hash == self.chain[i].previous_hash:
                hash = self.chain[i].hash
                curr_hash = self.chain[i].compute_hash()
                if curr_hash == hash:
                    self.chain[i].hash = hash
                    prev_hash = hash
                else:
                    return self.chain[i-1]
            else:
                return self.chain[i]
        return 0
    
    def add_vote(self, vote_transaction):
        if self.has_user_voted(vote_transaction['public_key']):
            return False
        # Add the vote to pending transactions
        self.add_transaction(vote_transaction)
        return True

    
    def has_user_voted(self, public_key):
        # Check each block in the blockchain
        for block in self.chain:
            for transaction in block.transactions:
                if transaction['public_key'] == public_key:
                    return True  # User has voted
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



    
# blockchain = Blockchain()
# print(blockchain.get_last_block())
# start_time = time.time()
# for i in range(0,12):
#     blockchain.add_transaction(f"Alice pays BOB ${i}.")
#     blockchain.mine_pending_transactions()

# end_time = time.time()
# print("mining time is:",end_time-start_time)
# print(blockchain.chain)

# blockchain.chain[1].hash = 0

# print("Is the chain valid?")
# print(blockchain.chain[0].to_dict())
# print(blockchain.is_chain_valid())