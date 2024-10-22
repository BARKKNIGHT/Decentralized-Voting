from flask import Flask, render_template, request, redirect, session,url_for
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user,current_user
from User.hash_method import  hashing_password,login_hash
from User.init_db import init_db
from flask_session import Session
from cs50 import SQL
import requests
import secrets

app = Flask(__name__)

# Configuration
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = secrets.token_hex(16)
Session(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)

# Database setup
DATABASE = "voters.db"

init_db(DATABASE)
db = SQL(f"sqlite:///{DATABASE}")

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

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
        voted = db.execute('SELECT voted FROM users WHERE user = ?', (data,))
        print(voted)
        if voted and voted[0]['voted'] == 0:
            candidates = db.execute('SELECT * FROM candidates')
            print(candidates)
            return render_template('vote.html', USER_INFO=data, candidates=candidates)
        else:
            return render_template('gotvote.html', USER_INFO=data, error="You have already voted!")

    elif request.method == 'POST':
        data = session.get('name')
        candidate = request.form.get('candidate_name')
        print(candidate)
        if not candidate:
            return render_template('vote.html', USER_INFO=session.get('name'), error="No candidate selected.")

        # Create a new transaction in the blockchain for the vote
        new_transaction = {
        'public_key':db.execute('SELECT salt FROM users WHERE user = ?', (data,))[0]['salt'],
        'vote':f"{candidate}"
    }
        try:
            r = requests.post('http://127.0.0.1:5001/add_transaction', json=new_transaction)
            r.raise_for_status()  # Ensure the request was successful
            print("........")
            # Update vote count and user status in the database
            db.execute('UPDATE users SET voted = ? WHERE user = ?', 1, session.get('name'))
            return render_template('gotvote.html', USER_INFO=session.get('name'), error="Successfully Voted!")
        except:
            return render_template('404.html', USER_INFO=session.get('name'), error="Invalid candidate.")

@app.route('/result')
@login_required
def result():       
    candidates = db.execute('SELECT * FROM candidates;')
    print(candidates)
    # lead=lead
    return render_template('result.html',USER_INFO=session.get('name'),candidates=candidates)

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
