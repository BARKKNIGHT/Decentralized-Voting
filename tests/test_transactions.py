import requests
import time

for i in range(0,12):
    new_transaction = {
            'public_key': f"Alice{i}",
            'vote': f"BOB{i}."
        }
    
    print(new_transaction)
    r = requests.post('http://127.0.0.1:5000/add_transaction', json=new_transaction)

for i in range(0,1):
    new_transaction = {
            'public_key': "Alice",
            'vote': f"BOB{i}."
    }

    print(new_transaction)
    r = requests.post('http://127.0.0.1:5000/add_transaction', json=new_transaction)



