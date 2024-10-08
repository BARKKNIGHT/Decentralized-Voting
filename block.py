import hashlib
from datetime import datetime

class Block:
    def __init__(self,index = 0,timestamp=datetime.now(),nonce=0,transactions=[],previous_hash = 0) -> None:
        self.index = index
        self.timestamp = timestamp
        self.nonce = nonce
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()
    def compute_hash(self) -> str:
        data = f"{self.index}{self.timestamp}{self.previous_hash}{self.nonce}{self.transactions}".encode()
        hash = hashlib.sha3_512(data).hexdigest()
        return hash
    
    def __repr__(self):
        return f"Block(Index:{self.index},\nTimestamp:{self.timestamp},\nNonce:{self.nonce},\nTransactions:{self.transactions},\nPrevious_Hash:{self.previous_hash},\nHash:{self.hash})\n"
    
    @classmethod
    def update_class_var(cls, difficulty):
        cls.difficulty = difficulty

