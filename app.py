from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bootstrap import Bootstrap

from werkzeug.security import generate_password_hash, check_password_hash

import pytz
import os, math, calendar, datetime

def getSMTWTFS(year,month,day): 
    date = datetime.date(year, month, day)
    return SMTWTFS[(date.weekday()+1) % SEVEN_DAY]

        
dt_now = datetime.datetime.now()
LAST_MONTH = 12
SMTWTFS = ['日', '月', '火', '水', '木', '金', '土']
SEVEN_DAY = len(SMTWTFS)
FULL_TIME = [14, 26]

if dt_now.month != LAST_MONTH:
    year = dt_now.year
    month = dt_now.month + 1
else:
    year = dt_now.year + 1
    month = 1

    
nDay = calendar.monthrange(year, month)[1]
print('test')
date = datetime.date(year, month, 1)
lastMonthRem = (date.weekday()+1) % SEVEN_DAY
n = lastMonthRem + nDay

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(pytz.timezone('Asia/Tokyo')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12), nullable=False)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html', posts=posts)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User(username=username, password=generate_password_hash(password, method='sha256'))
        
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).one_or_none()
        if user == None:
            return render_template('login.html', error="ユーザー名またはパスワードが正しくありません")
        if check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect('/')
        else:
            return render_template('login.html', error="ユーザー名またはパスワードが正しくありません")
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

hopeWorkDayList = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
workTimeRadioNameList = [i+'_'+str(iDay) for iDay in hopeWorkDayList for i in ['start', 'end']]
nWorkDay = len(hopeWorkDayList)
START_SELECT_LIST = [16, 17, 18]
END_SELECT_LIST = [22, 23, 24, 25, 26]
START_END_DEFAULT = [16, 26]
nStartSelect = len(START_SELECT_LIST)
nEndSelect = len(END_SELECT_LIST)
monthDayList = []
for iRow in range(nWorkDay):
    monthDayList.append(f'{month}/{hopeWorkDayList[iRow]}({getSMTWTFS(year,month,hopeWorkDayList[iRow])})')
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        
        post = Post(title=title, body=body)
        
        db.session.add(post)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('create.html'
                               ,nWorkDay=nWorkDay
                               ,START_SELECT_LIST=START_SELECT_LIST
                               ,nStartSelect=nStartSelect
                               ,END_SELECT_LIST=END_SELECT_LIST
                               ,nEndSelect=nEndSelect
                               ,hopeWorkDayList=hopeWorkDayList
                               ,monthDayList=monthDayList
                               ,workTimeRadioNameList=workTimeRadioNameList,
                               START_END_DEFAULT=START_END_DEFAULT)

@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        
        db.session.commit()
        return redirect('/')

@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)
    
    db.session.delete(post)
    db.session.commit()
    return redirect('/')
    