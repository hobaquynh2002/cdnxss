from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from werkzeug.utils import secure_filename
import hashlib
import re

xxx={}
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER']='/home/kali/Desktop/task-clb/static/'
db = SQLAlchemy(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
def hash_code(password):
    # hash the password using sha256
    hash_object = hashlib.sha256(password.encode())
    return hash_object.hexdigest()

@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('profile.html')
    else:
        return render_template('index.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(username=request.form['username'], password=request.form['password']))
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('index.html')
    else:
        return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        u = request.form['username']
        p = request.form['password']
        data = User.query.filter_by(username=u, password=p).first()
        if data is not None:
            session['logged_in'] = hash_code(p)
            global xxx
            xxx[session['logged_in']]=u
            return redirect(url_for('profile',username=u))
        return render_template('index.html')

@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = None
    xxx.clear()
    return redirect(url_for('index'))


@app.route('/profile/<username>',methods=['GET','POST'])
def profile(username):
    user=username
    print(username)
    if request.method == 'POST' and session['logged_in']:
        file= request.files['file']
        filename = secure_filename(file.filename)
        filename=hash_code(username+app.secret_key)+'.png'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('display_file',filename=filename))
    elif request.method == 'GET' and username==xxx[session['logged_in']] and session['logged_in']:
        filename=hash_code(user+app.secret_key)+'.png'
        return render_template('profile.html',uploaded_file=url_for('static',filename=filename),username=user)
    elif not session['logged_in'] or username==xxx[session['logged_in']]:   
        return redirect(url_for('logout'))

@app.route('/uploads/<filename>')
def display_file(filename):
    if session['logged_in']:
        return render_template('profile.html',uploaded_file=url_for('static',filename=filename))
    if not session['logged_in']:   
        return redirect(url_for('logout'))
if(__name__ == '__main__'):
    app.secret_key = "ThisIsNotASecret:p"
    login_manager = LoginManager()
    db.create_all()
    app.run()
