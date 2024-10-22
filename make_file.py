'''
Write a initialization file to:
1.Create users.db and blockchain.db
'''

import Blockchain.init_db
import User.init_db

User.init_db.init_db("users.db")
Blockchain.init_db.init_db("blockchain.db")