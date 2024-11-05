import requests
import time

start = time.time()
for i in range(901,1000):
    new_transaction = {
            'public_key': f"Alice{i}",
            'vote': f"BOB{i}.",
            'time': time.time()
        }
    print(new_transaction)
    r = requests.post('http://127.0.0.1:5001/add_vote', json=new_transaction)
    print(r.content)

stop = time.time()
time_ = stop - start
print(time_)

