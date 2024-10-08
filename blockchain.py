from block import Block

class Blockchain:
    transactions = 6
    def __init__(self,chain = []) -> None:
        self.pending_transactions = []
        self.chain = chain
        if not self.chain:  # If no blocks found in input params, create a genesis block
            self._create_genesis_block()

    def _create_genesis_block(self): #first block
        genesis = Block(0)
        self.add_block(genesis)

    def add_block(self,block): #append block to chain
        self.chain.append(block)
    
    def get_last_block(self): #retreive last block from the chain
        return self.chain[-1] if self.chain else None

    def add_transaction(self, transaction): #append transactions in a buffer
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self): #push pending transactions into a new block(max transacs = 5) and (min transacs = 1)
        last_block = self.get_last_block()
        if len(self.pending_transactions)>Blockchain.transactions-1:
            new_block = Block(index=last_block.index + 1, 
                                previous_hash=last_block.hash, 
                                transactions=self.pending_transactions[0:Blockchain.transactions])
            self.pending_transactions = self.pending_transactions[Blockchain.transactions:]
            new_block.nonce = self.proof_of_work(new_block)
            self.add_block(new_block)

    def proof_of_work(self, block, difficulty=5): #Calculate PoW for a block (get a nonce value that satisfies difficulty)
        block.nonce = 0
        while not block.hash.startswith('0' * difficulty):
            block.nonce += 1
            block.hash = block.compute_hash()
        return block.nonce
    
    def is_chain_valid(self):
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
        return "0"
    
blockchain = Blockchain()

for i in range(0,12):
    blockchain.add_transaction(f"Alice pays BOB ${i}.")
    blockchain.mine_pending_transactions()

print(blockchain.chain)

blockchain.chain[1].hash = 0

print("Is the chain valid?")
print(blockchain.is_chain_valid())