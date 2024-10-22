from .sql_handler import sql_handler

def cast_vote(public_key, vote, blockchain_handler):
    # Create a vote transaction
    vote_transaction = {
        'public_key':public_key, 
        'vote':vote
    }
    
    # Add the vote to the blockchain
    if blockchain_handler.add_vote(vote_transaction):
        return "Vote cast successfully!"
    else:
        return "Failed to cast vote. You may have already voted."

