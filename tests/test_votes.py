from Blockchain.voting_interface import cast_vote
from Blockchain.sql_handler import sql_handler
import time
handler = sql_handler("blockchain.db","voters.db")
print(handler.get_last_block())
for i in range(0,100):
    vote = {
        'public_key':i,
        'vote':"test_guy",
        'time':time.time()
    }
    print(cast_vote(i,"test_guy",handler))

# print(handler.blockchain.chain)

# print(handler.calculate_votes())