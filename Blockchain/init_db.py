import os
import sqlite3
def init_db(DATABASE):
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE blockchain (
            id INTEGER PRIMARY KEY,
            block_json TEXT NOT NULL
        )  
        ''')
        cursor.execute('''
        CREATE TABLE peers (
            id INTEGER PRIMARY KEY,
            peers TEXT NOT NULL
        )  
        ''')
        conn.commit()

