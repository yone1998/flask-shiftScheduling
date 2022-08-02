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
from sqlalchemy import desc
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bootstrap import Bootstrap

from werkzeug.security import generate_password_hash, check_password_hash

import jyserver.Flask as jsf

import os, datetime, pytz

import config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shift.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userLastName = db.Column(db.String(15), nullable=False)
    userFirstName = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(12), nullable=False)

class HopeDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.String(30), nullable=False)
    targetYear = db.Column(db.Integer, nullable=False)
    targetMonth = db.Column(db.Integer, nullable=False)
    isMySubmission = db.Column(db.Boolean, nullable=False, default=True)

class HopeTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hopeDayId = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)


isHopeDayList = [1]*config.SUM_DAYS_OF_TARGET_MONTH

@jsf.use(app)
class App:
    def switch(self, day):
        day = int(day)
        isHopeDayList[day-1] = isHopeDayList[day-1] ^ 1
        if isHopeDayList[day-1]:
            self.js.document.getElementById(f'selectDay{day}').style.backgroundColor = 'buttonface'
        else:
            self.js.document.getElementById(f'selectDay{day}').style.backgroundColor = 'pink'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        userLastName = request.form.get('userLastName')
        userFirstName = request.form.get('userFirstName')
        password = request.form.get('password')
        if len(userLastName) == 0 or len(userFirstName) == 0 or len(password) == 0:
            return render_template('signup.html', errorList=["入力漏れがあります"])
        
        user = User.query.filter_by(userLastName=userLastName, userFirstName=userFirstName).one_or_none()
        if user is None:
            user = User(userLastName=userLastName
                ,userFirstName=userFirstName
                ,password=generate_password_hash(password, method='sha256'))
        else:
            return render_template('signup.html', errorList=["既に登録されている名前です", "ログインページからログインしてください"])
            
        db.session.add(user)
        db.session.commit()
        return redirect(f'/login')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == 'POST':
        userLastName = request.form.get('userLastName')
        userFirstName = request.form.get('userFirstName')
        password = request.form.get('password')
        
        user = User.query.filter_by(userLastName=userLastName, userFirstName=userFirstName).one_or_none()
        if user is None or check_password_hash(user.password, password) == False:
            return render_template('login.html', error="氏名またはパスワードが正しくありません")
        else:
            login_user(user, remember=True)
            return redirect(f'/{user.id}/user/home')

@app.route('/<int:id>/user/home', methods=['GET', 'POST'])
@login_required
def userHome(id):
    if request.method == 'GET':
        userId = id
        del id
        hopeDay = HopeDay.query.filter_by(userId = userId
            ,targetYear = config.TARGET_YEAR
            ,targetMonth = config.TARGET_MONTH).order_by(desc(HopeDay.id)).first()
        if hopeDay is None:
            return render_template('userHome.html'
                ,userId = userId
                ,HOPE_SHIFT_STR=config.HOPE_SHIFT_STR
                ,error="提出済みの希望シフトはありません"
                )
        else:
            return render_template('userHome.html'
                ,userId = userId
                ,HOPE_SHIFT_STR=config.HOPE_SHIFT_STR
                ,hopeDay=hopeDay
                )

@app.route('/<int:id>/user/create/hopeDay', methods=['GET', 'POST'])
@login_required
def hopeDay(id):
    if request.method == 'GET':
        global isHopeDayList
        isHopeDayList = [1]*config.SUM_DAYS_OF_TARGET_MONTH
        return App.render(render_template('hopeDay.html'
            ,id=id
            ,SMTWTFS=config.SMTWTFS
            ,NUM_FIRST_WEEKDAY_OF_TARGET_MONTH=config.NUM_FIRST_WEEKDAY_OF_TARGET_MONTH
            ,SUM_DAYS_OF_TARGET_MONTH=config.SUM_DAYS_OF_TARGET_MONTH
            ,SUM_BLOCKS_OF_CALENDAR=config.SUM_BLOCKS_OF_CALENDAR
            ,TARGET_DATE_STR=config.TARGET_DATE_STR
            ,SELECT_DAYS_LIST=config.SELECT_DAYS_LIST
            ))
    elif request.method == 'POST':
        return render_template('hopeTime.html')

@app.route('/<int:id>/user/create/hopeTime', methods=['GET', 'POST'])
@login_required
def hopeTime(id):
    if request.method == 'GET':
        TARGET_YEAR = config.TARGET_YEAR
        TARGET_MONTH = config.TARGET_MONTH
        
        global hopeDayList
        hopeDayList = [iDay+1 for iDay in range(len(isHopeDayList)) if isHopeDayList[iDay] == 1]
        workTimeRadioNameList = [i+'_'+str(iDay) for iDay in hopeDayList for i in ['start', 'end']]
        hopeDayStrList = [f'{TARGET_MONTH}/{iDay}({config.SMTWTFS[config.getNumWeekday(TARGET_YEAR, TARGET_MONTH, iDay)]})' for iDay in hopeDayList] # 勤務可能日のリスト 例: 8/2(火)
        return render_template('hopeTime.html'
            ,id=id
            ,hopeDayStrList=hopeDayStrList
            ,workTimeRadioNameList=workTimeRadioNameList
            ,START_SELECT_LIST=config.START_SELECT_LIST
            ,END_SELECT_LIST=config.END_SELECT_LIST
            ,START_END_DEFAULT=config.START_END_DEFAULT
            )
        
    elif request.method == 'POST':
        print('point1')
        created_at = str(datetime.datetime.now(pytz.timezone('Asia/Tokyo'))).split(".")[0]
        hopeDay = HopeDay(userId=id
            ,created_at=created_at
            ,targetYear=config.TARGET_YEAR
            ,targetMonth=config.TARGET_MONTH
            )
        db.session.add(hopeDay)
        
        hopeDay = HopeDay.query.filter_by(userId = id
            ,targetYear = config.TARGET_YEAR
            ,targetMonth = config.TARGET_MONTH).order_by(desc(HopeDay.id)).first()
        
        print('point2')
        for iDay in hopeDayList:
            start = int(request.form.get(f'start_{iDay}'))
            end = int(request.form.get(f'end_{iDay}'))
            hopeTime = HopeTime(hopeDayId=hopeDay.id
                ,day=iDay
                ,start=start
                ,end=end
                )
            db.session.add(hopeTime)
            print('point3')
        db.session.commit()
        print('point4')
        return redirect(f'/{id}/user/home')

@app.route('/<int:id>/user/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    
    elif request.method == 'POST':
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        
        db.session.commit()
        return redirect(f'/{id}/user/home')

@app.route('/<int:id>/user/delete', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)
    
    db.session.delete(post)
    db.session.commit()
    return redirect(f'/{id}/user/home')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')
