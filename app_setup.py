from flask import Flask,render_template,request,redirect
from User.hash_method import hashing_password
from User.init_db import init_db
from cs50 import SQL

DATABASE = "voters.db"

app = Flask(__name__)

init_db(DATABASE=DATABASE)

db = SQL(f"sqlite:///{DATABASE}")

@app.route('/')
def home():
    return redirect("/admin")

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
                return render_template('register.html', error='Registration successful')
            else:
                return render_template('register.html', error='User already exists')
        except Exception as e:
            return render_template('register.html', error=str(e))
    else:
        return render_template("register.html")
    
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
        
if __name__ == "__main__":
    app.run(debug=True)