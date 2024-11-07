import hashlib
from datetime import datetime

class Block:
    def __init__(self,index = 0,timestamp=datetime.now(),nonce=0,transactions=[],public_keys=[],previous_hash = 0) -> None:
        self.index = index
        self.timestamp = timestamp
        self.nonce = nonce
        self.transactions : dict = transactions
        self.public_keys = public_keys
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        data = f"{self.index}{self.timestamp}{self.previous_hash}{self.nonce}{self.public_keys}{self.transactions}".encode()
        hash = hashlib.sha3_512(data).hexdigest()
        return hash
    
    def __repr__(self):
        return f"Block(Index:{self.index},\nTimestamp:{self.timestamp},\nPublic_keys:{self.public_keys}\nNonce:{self.nonce},\nTransactions:{self.transactions},\nPrevious_Hash:{self.previous_hash},\nHash:{self.hash})\n"
    
    @classmethod
    def update_class_var(cls, difficulty):
        cls.difficulty = difficulty
    
    def to_dict(self):
        """Convert block to dictionary for JSON serialization."""
        return {
            'Index': self.index,
            'Timestamp':f"{self.timestamp}",
            'Previous_hash': self.previous_hash,
            'Transactions':  self.transactions,
            'Public_keys' : self.public_keys,
            'Nonce': self.nonce,
            'Hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, block_dict):
        """Rebuild block object from a dictionary."""
        block = cls(
            index=block_dict['Index'],
            timestamp=block_dict['Timestamp'],
            previous_hash=block_dict['Previous_hash'],
            transactions=block_dict['Transactions'],
            public_keys=block_dict['Public_keys'],
            nonce=block_dict['Nonce']
        )

        block.hash = block_dict['Hash']

        return block




