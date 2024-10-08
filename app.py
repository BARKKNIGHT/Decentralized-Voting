from flask import Flask, render_template, request, redirect, session, abort,url_for
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user,current_user
from block import Block
from blockchain import Blockchain
from flask_session import Session
from cs50 import SQL
import hashlib
import secrets
import os
import sqlite3

app = Flask(__name__)

#init blockchain
blockchain = Blockchain()

# Configuration
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = secrets.token_hex(16)
Session(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)

# Database setup
DATABASE = "users.db"

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            password TEXT NOT NULL,
            salt TEXT NOT NULL,
            voted INTEGER DEFAULT 0
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
        cursor.execute('''
        CREATE TABLE blockchain (
            index INTEGER PRIMARY KEY,
            hash TEXT NOT NULL,
            party TEXT NOT NULL,
            votes INTEGER DEFAULT 0
        )  
        ''')
        conn.commit()
        conn.close()

init_db()
db = SQL(f"sqlite:///{DATABASE}")

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Password hashing functions
def hashing_password(password):
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return salt, hashed

def login_hash(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('vote'))
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template('about.html',USER_INFO=session.get('name'))

@app.route('/contact')
def contact():
    return render_template('contact.html',USER_INFO=session.get('name'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['pass']
        session['name'] = user

        try:
            cursor = db.execute('SELECT user, password, salt FROM users WHERE user = ?', user)
            if cursor:
                salt = cursor[0]['salt']
                hashed_password = login_hash(password, salt)
                if hashed_password == cursor[0]['password']:
                    user_obj = User(user)
                    login_user(user_obj)
                    return redirect('vote')
                else:
                    return render_template('index.html', error="INCORRECT LOGIN INFORMATION!")
            else:
                return render_template('index.html', error="USER DOESN'T EXIST!")
        except Exception as e:
            return render_template('index.html', error=str(e))
    else:
        return redirect('/')

@app.route('/logout',methods=['POST','GET'])
def logout():
    data = session.get('name')
    session.clear()
    logout_user()
    return render_template('logout.html', user=data)

@app.route('/user', methods=['GET'])
@login_required
def user_data():
    return render_template('user.html', USER_INFO=session.get('name'))

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    if request.method == 'POST':
        db.execute('DELETE FROM users WHERE user = ?', session.get('name'))
        return redirect('/logout')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['pass']
        salt, hashed_password = hashing_password(password)

        try:
            cursor = db.execute('SELECT * FROM users WHERE user = ?', user)
            if not cursor:
                db.execute('INSERT INTO users (user, password, salt,voted) VALUES (?, ?, ?, ?)', user, hashed_password, salt,0)
                return render_template('index.html', error='Registration successful')
            else:
                return render_template('register.html', error='User already exists')
        except Exception as e:
            return render_template('register.html', error=str(e))
    else:
        return render_template("register.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e.code), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html', error=e.code), 500
@app.route('/leaderboard')
def leaderboard():
        # Retrieve the leaderboard data from the database
        leaderboard_data = db.execute('SELECT user, carbon_footprint FROM users ORDER BY carbon_footprint DESC')

        # Render the leaderboard template with the data
        return render_template('leaderboard.html', leaderboard_data=leaderboard_data,User_Info=session.get('name'))

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if request.method == 'GET':
        data = session.get('name')
        voted = db.execute('SELECT voted FROM users WHERE user=?', data)
        if voted[0]['voted'] == 1:
            candidates = db.execute('SELECT * FROM candidates;')
            return render_template('vote.html', USER_INFO=data, candidates=candidates)
        else:
            return render_template('gotvote.html', USER_INFO=session.get('name'), error="Successfully Voted!")

    elif request.method == 'POST':
        candidate = request.form.to_dict().keys()
        candidate = list(candidate)[0]
        
        # Create a new transaction in the blockchain for the vote
        new_transaction = {
            'user': session.get('name'),
            'vote': candidate
        }
        blockchain.add_transaction(new_transaction)

        # Update vote count in the database
        votes = db.execute('SELECT candidate, votes FROM candidates WHERE candidate=?', (candidate))
        votes = votes[0]['votes'] + 1
        db.execute('UPDATE candidates SET votes = ? WHERE candidate = ?;', votes, candidate)
        db.execute('UPDATE users SET voted = ? WHERE user = ?', 1, session.get('name'))

        # Mine the pending transactions (if 5 transactions in pending already)
        blockchain.mine_pending_transactions()

        return render_template('gotvote.html', USER_INFO=session.get('name'), error="Successfully Voted!")


@app.route('/result')
@login_required
def result():       
    candidates = db.execute('SELECT * FROM candidates;')
    print(candidates)
    # lead=lead
    return render_template('result.html',USER_INFO=session.get('name'),candidates=candidates)

@app.route('/admin',methods=['GET','POST'])
# @login_required
def admin():
    if request.method=='GET':
        candidates = db.execute('SELECT * FROM candidates;')
        return render_template('admin.html',candidates=candidates)
    elif request.method=='POST':
        candidate = request.form.get('candidate')
        party = request.form.get('party')
        cursor = db.execute('SELECT * FROM candidates WHERE candidate = ?', candidate)
        if not cursor:
            db.execute('INSERT INTO candidates (candidate,party,votes) VALUES (?,?,?);',candidate,party,0)
            candidates = db.execute('SELECT * FROM candidates;')
            return render_template('admin.html',candidates=candidates)
        else:
            candidates = db.execute('SELECT * FROM candidates;')
            return render_template('admin.html',candidates=candidates,error="Candidate already exists!")

@app.route('/blockchain', methods=['GET'])
@login_required
def view_blockchain():
    chain = blockchain.chain  # Get the current chain
    return render_template('blockchain.html', blockchain=chain)

@app.route('/mine', methods=['GET'])
@login_required
def mine_block():
    blockchain.mine_pending_transactions()  # Mine all pending transactions
    return redirect(url_for('view_blockchain'))

@app.route('/validate', methods=['GET'])
@login_required
def validate_blockchain():
    is_valid = blockchain.is_chain_valid()
    return render_template('validate.html', is_valid=is_valid)

@app.errorhandler(401)
def unauthorized(e):
    return render_template('404.html', error=e.code), 401

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

if __name__ == "__main__":
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=443)
    app.run(host="0.0.0.0",port=80,debug=True)
