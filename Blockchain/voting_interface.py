from .sql_handler import sql_handler
from time import time

def cast_vote(public_key, vote : dict, blockchain_handler : sql_handler):
    # Create a vote transaction
    vote_transaction = {
        'public_key':public_key, 
        'vote':vote,
        'time': time()
    }
    
    # Add the vote to the blockchain
    temp = blockchain_handler.add_vote(vote_transaction)
    if type(temp) == bool and temp==True:
        return "Vote cast successfully!"
    elif type(temp) == dict:
        return "Vote cast successfully!"+f"\nTime:{temp['transaction_times'][public_key]} seconds"
    else:
        return "Failed to cast vote. You may have already voted."
    

