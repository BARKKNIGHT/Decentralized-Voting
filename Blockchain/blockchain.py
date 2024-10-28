from block import Block
import requests
import time

class Blockchain:
    transactions = 6
    def __init__(self, node_id: str):
        self.chain: list[Block] = []
        self.pending_transactions: list[dict] = []
        self.node_id = node_id
        self.peer_nodes = set()
        # Initialize with genesis block
        self._create_genesis_block()

    def _create_genesis_block(self): #first block
        genesis = Block(0)
        self.add_block(genesis)

    def add_peer(self, peer_address: str):
        """Add a new peer node to the network."""
        self.peer_nodes.add(peer_address)

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
            start_time = time.time()
            new_block = Block(index=last_block.index + 1, 
                                previous_hash=last_block.hash, 
                                transactions=self.pending_transactions[0:Blockchain.transactions])
            self.pending_transactions = self.pending_transactions[Blockchain.transactions:]
            new_block.nonce = self.proof_of_work(new_block)
            self.add_block(new_block)
            stop_time = time.time()
            self.broadcast_block(new_block)
            return {'status':True,'time':stop_time-start_time}
        return {'status':False}

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

    def sync_with_peers(self):
        """Synchronize blockchain with all peer nodes."""
        longest_chain = None
        max_length = len(self.chain)
        
        # Query all peers for their chains
        for peer in self.peer_nodes:
            try:
                response = requests.get(f"{peer}/chain")
                if response.status_code == 200:
                    chain = response.json()['chain']
                    length = len(chain)
                    
                    # Verify the received chain
                    if length > max_length and self.is_valid_chain(chain):
                        max_length = length
                        longest_chain = chain
            except requests.RequestException:
                continue
        
        # Replace our chain if we found a longer valid one
        if longest_chain:
            self.chain = longest_chain
            return True
        return False    
    
    def broadcast_block(self, block: Block):
        """Broadcast a new block to all peers."""
        block_data = {
            'block': {
                'index': block.index,
                'timestamp': block.timestamp,
                'transactions': block.transactions,
                'previous_hash': block.previous_hash,
                'nonce': block.nonce
            }
        }

        for peer in self.peer_nodes:
            try:
                requests.post(f"{peer}/receive_block", json=block_data)
            except requests.RequestException:
                continue
    
    def receive_block(self, block_data: dict):
        """Handle receiving a new block from a peer."""
        block = Block(
            index=block_data['index'],
            timestamp=block_data['timestamp'],
            transactions=block_data['transactions'],
            previous_hash=block_data['previous_hash'],
            nonce=block_data['nonce']
        )
        
        # Verify the block is valid
        if (block.index == len(self.chain) and
            block.previous_hash == self.chain[-1].calculate_hash() and
            self.proof_of_work(block)):  # simplified difficulty check
            
            self.chain.append(block)
            return True
        return False