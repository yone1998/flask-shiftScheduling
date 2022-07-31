# ローカル環境は正常だが、本番環境でUnauthorizedになる（何回かリロードするとリクエストが通る）
# ・signup
# 登録済みの名前を入力するとInternal Server Errorになる
# 片方だけ入力するとInternal Server Errorになる
# 1回だけ無名（パスワードだけ）で登録できる
# ・create
# 投稿日時がログイン日時（？）になる
# ・update
# 変更が反映されるのが一時的（元に戻る）
# 削除した投稿の編集URL（/2/update）
# Internal Server Errorになる
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bootstrap import Bootstrap

from werkzeug.security import generate_password_hash, check_password_hash

import pytz
import os, calendar, datetime
import config

def getSMTWTFS(year,month,day): 
    date = datetime.date(year, month, day)
    return (date.weekday()+1) % len(SMTWTFS)

SMTWTFS = config.SMTWTFS
# FULL_TIME = config.FULL_TIME
# nDay = calendar.monthrange(tergetYear, tergetMonth)[1]
# print('test')
# lastMonthRem = getSMTWTFS(tergetYear, tergetMonth, 1)
# n = lastMonthRem + nDay
NEXT_YEAR_MONTH = config.NEXT_YEAR_MONTH

# 来月をターゲットとする
tergetYear = NEXT_YEAR_MONTH[0]
tergetMonth = NEXT_YEAR_MONTH[1]
tergetDateStr = f'{tergetYear}年{tergetMonth}月'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shift.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12), nullable=False)

class HopeTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)
    userName = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12), nullable=False)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')

@app.route('/userHome', methods=['GET', 'POST'])
# @login_required
def userHome():
    if request.method == 'GET':
        hopeShiftStr = f'{tergetDateStr}の希望シフト'
        posts = Post.query.all()
        return render_template('userHome.html'
                               ,posts=posts
                               ,hopeShiftStr=hopeShiftStr
                               )

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        userName = request.form.get('userName')
        password = request.form.get('password')
        
        user = User(userName=userName, password=generate_password_hash(password, method='sha256'))
        
        db.session.add(user)
        db.session.commit()
        return redirect('/userHome')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form.get('userName')
        password = request.form.get('password')
        
        user = User.query.filter_by(userName=userName).one_or_none()
        if user == None:
            return render_template('login.html', error="ユーザー名またはパスワードが正しくありません")
        if check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect('/userHome')
        else:
            return render_template('login.html', error="ユーザー名またはパスワードが正しくありません")
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/create/hopeDay', methods=['GET', 'POST'])
# @login_required
def hopeDay():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        created_at = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        
        post = Post(title=title, body=body, created_at=created_at)
        
        db.session.add(post)
        db.session.commit()
        return redirect('/userHome')
    else:
        return render_template('hopeDay.html'
                               )

@app.route('/create/hopeTime', methods=['GET', 'POST'])
# @login_required
def hopeTime():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        
        post = Post(title=title, body=body)
        
        db.session.add(post)
        db.session.commit()
        return redirect('/userHome')
    else:
        START_SELECT_LIST = config.START_SELECT_LIST
        END_SELECT_LIST   = config.END_SELECT_LIST
        START_END_DEFAULT = config.START_END_DEFAULT
        hopeDayList = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        
        workTimeRadioNameList = [i+'_'+str(iDay) for iDay in hopeDayList for i in ['start', 'end']]
        hopeDayStrList = [f'{tergetMonth}/{iDay}({SMTWTFS[getSMTWTFS(tergetYear, tergetMonth, iDay)]})' for iDay in hopeDayList] # 勤務可能日のリスト 例: 8/2(火)
        # hopeDayStrList = []
        # for iDay in hopeDayList:
        #     hopeDayStrList.append(f'{tergetMonth}/{iDay}({SMTWTFS[getSMTWTFS(tergetYear,tergetMonth,iDay)]})')
        return render_template('hopeTime.html'
                               ,hopeDayStrList=hopeDayStrList
                               ,workTimeRadioNameList=workTimeRadioNameList
                               ,START_SELECT_LIST=START_SELECT_LIST
                               ,END_SELECT_LIST=END_SELECT_LIST
                               ,START_END_DEFAULT=START_END_DEFAULT)

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
        return redirect('/userHome')

@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)
    
    db.session.delete(post)
    db.session.commit()
    return redirect('/userHome')
    