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
        conn.commit()
        cursor.execute('''
        CREATE TABLE candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT NOT NULL,
            party TEXT NOT NULL,
            votes INTEGER DEFAULT 0
        )  
        ''')
        conn.commit()
        conn.close()
