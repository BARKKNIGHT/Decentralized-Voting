from flask import Flask, render_template, request, redirect
from User.hash_method import hashing_password
from User.init_db import init_db
from cs50 import SQL
import csv
import os

DATABASE = "voters.db"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

init_db(DATABASE=DATABASE)
db = SQL(f"sqlite:///{DATABASE}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect("/admin")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle CSV upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                with open(filepath, 'r') as csvfile:
                    csv_reader = csv.reader(csvfile)
                    next(csv_reader)  # Skip header row if exists
                    for row in csv_reader:
                        user, password = row[0], row[1]
                        salt, hashed_password = hashing_password(password)
                        if not db.execute('SELECT * FROM users WHERE user = ?', user):
                            db.execute('INSERT INTO users (user, password, salt, voted) VALUES (?, ?, ?, ?)', user, hashed_password, salt, 0)
                os.remove(filepath)
                return render_template('register.html', error='CSV upload successful')
            else:
                return render_template('register.html', error='Invalid file format. Please upload a CSV file.')
        # Handle single user registration
        else:
            user = request.form['user']
            password = request.form['pass']
            salt, hashed_password = hashing_password(password)
            if not db.execute('SELECT * FROM users WHERE user = ?', user):
                db.execute('INSERT INTO users (user, password, salt, voted) VALUES (?, ?, ?, ?)', user, hashed_password, salt, 0)
                return render_template('register.html', error='Registration successful')
            else:
                return render_template('register.html', error='User already exists')
    return render_template("register.html")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Handle CSV upload for candidates
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                with open(filepath, 'r') as csvfile:
                    csv_reader = csv.reader(csvfile)
                    next(csv_reader)  # Skip header row if exists
                    for row in csv_reader:
                        candidate, party = row[0], row[1]
                        if not db.execute('SELECT * FROM candidates WHERE candidate = ?', candidate):
                            db.execute('INSERT INTO candidates (candidate, party, votes) VALUES (?, ?, ?)', candidate, party, 0)
                os.remove(filepath)
                candidates = db.execute('SELECT * FROM candidates')
                return render_template('admin.html', candidates=candidates, error='CSV upload successful')
            else:
                return render_template('admin.html', error='Invalid file format. Please upload a CSV file.')

        # Handle single candidate addition
        candidate = request.form.get('candidate')
        party = request.form.get('party')
        if not db.execute('SELECT * FROM candidates WHERE candidate = ?', candidate):
            db.execute('INSERT INTO candidates (candidate, party, votes) VALUES (?, ?, ?)', candidate, party, 0)
            candidates = db.execute('SELECT * FROM candidates')
            return render_template('admin.html', candidates=candidates)
        else:
            candidates = db.execute('SELECT * FROM candidates')
            return render_template('admin.html', candidates=candidates, error="Candidate already exists!")
    
    # GET method: Show all candidates
    candidates = db.execute('SELECT * FROM candidates')
    return render_template('admin.html', candidates=candidates)

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
