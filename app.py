# ・hopeDay
# isHopeDayListはsessionにするとなぜか挙動がおかしくなる
# jyserverとsessionの相性が悪いのか？
# ・update
# 変更が反映されるのが一時的（元に戻る）
# 削除した投稿の編集URL（/2/update）
# Internal Server Errorになる
# ・css
# メッセージのスタイルが反映されない

from enum import unique
from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_login import UserMixin
from flask_bootstrap import Bootstrap
# from flask_wtf.csrf import CSRFProtect

from werkzeug.security import generate_password_hash, check_password_hash

import jyserver.Flask as jsf

import os, datetime, pytz

import config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shift.db'

# 本番環境
# app.secret_key = os.environ['SECRET_KEY']
# ローカル環境
app.secret_key = config.SECRET_KEY
if not app.secret_key:
    raise ValueError("No SECRET_KEY set for Flask application")
app.permanent_session_lifetime = datetime.timedelta(minutes=10)

# csrf = CSRFProtect(app)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userLastName = db.Column(db.String(10), nullable=False)
    userFirstName = db.Column(db.String(10), nullable=False)
    loginID = userLastName = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)

class HopeDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.String(30), nullable=False)
    targetYear = db.Column(db.Integer, nullable=False)
    targetMonth = db.Column(db.Integer, nullable=False)

class HopeTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hopeDayID = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)

def isNotMatchLoggedID(userID):
    if userID != session.get("loggedID"):
        session.pop("loggedID", None)
    return userID != session.get("loggedID")

@app.route('/test', methods=['GET'])
def test():
    if request.method == 'GET':
        return render_template('test.html')

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return redirect(url_for('userLogin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    elif request.method == 'POST':
        userLastName = request.form.get('userLastName')
        userFirstName = request.form.get('userFirstName')
        loginID = request.form.get('loginID')
        password = request.form.get('password')
        if len(userLastName) == 0 or len(userFirstName) == 0 or len(loginID) == 0 or len(password) == 0:
            isOK = False
            flash('入力もれがあります', 'ng')
        else:
            user = User.query.filter_by(loginID=loginID).one_or_none()
            if user is None:
                isOK = True

                # Userテーブルに新規登録
                user = User(
                    userLastName=userLastName
                    ,userFirstName=userFirstName
                    ,loginID=loginID
                    ,password=generate_password_hash(password, method='sha256'))
                db.session.add(user)
                db.session.commit()

                # session情報にログインしているユーザーのIDを登録
                user = User.query.filter_by(loginID=loginID).one()
                userID = user.id
                session.permanent = True
                session["loggedID"] = userID
                flash('新規登録が完了しました', 'ok')
            else:
                isOK = False
                flash('既に使われているユーザーIDです', 'ng')
                flash('登録済みの場合はログインページからログインしてください', 'ng')

        if isOK == True:
            return redirect(url_for('userHome', userID=userID))
        elif isOK == False:
            return redirect(url_for('signup'))

@app.route('/userLogin', methods=['GET', 'POST'])
def userLogin():
    if request.method == 'GET':
        return render_template('userLogin.html')

    elif request.method == 'POST':
        loginID = request.form.get('loginID')
        password = request.form.get('password')
        if len(loginID) == 0 or len(password) == 0:
            isOK = False
            flash('入力もれがあります', 'ng')
        else:
            user = User.query.filter_by(loginID=loginID).one_or_none()
            if user is None or check_password_hash(user.password, password) == False:
                isOK = False
                flash('ユーザーIDまたはパスワードが正しくありません', 'ng')
            else:
                isOK = True
                userID = user.id
                session.permanent = True
                session["loggedID"] = userID

        if isOK == True:
            return redirect(url_for('userHome', userID=userID))
        elif isOK == False:
            return render_template('userLogin.html')

@app.route('/<int:userID>/user/home', methods=['GET', 'POST'])
def userHome(userID):
    if isNotMatchLoggedID(userID):
        return redirect(url_for('userLogin'))

    if request.method == 'GET':
        hopeDay = HopeDay.query.filter_by(
            userID = userID
            ,targetYear = config.TARGET_YEAR
            ,targetMonth = config.TARGET_MONTH
            ).one_or_none()
        print(hopeDay)

        if hopeDay is None:
            flash('提出済みの希望シフトはありません', 'ng')
            return render_template('userHome.html'
                ,userID = userID
                ,HOPE_SHIFT_STR=config.HOPE_SHIFT_STR
                )
        else:
            hopeTime = HopeTime.query.filter_by(hopeDayID = hopeDay.id).first()
            if hopeTime is not None:
                return render_template('userHome.html'
                    ,userID = userID
                    ,HOPE_SHIFT_STR=config.HOPE_SHIFT_STR
                    ,hopeDay=hopeDay
                    ,hopeTime=hopeTime
                    )
            else: # 想定外のバグ（hopeDayはあるがhopeTimeはない状態）
                # hopeDayのレコードの削除
                db.session.delete(hopeDay)
                db.session.commit()
                return redirect(url_for('userHome', userID=userID))


@app.route('/<int:userID>/user/hopeShift', methods=['GET', 'POST'])
def hopeShift(userID):
    if isNotMatchLoggedID(userID):
        return redirect(url_for('userLogin'))

    if request.method == 'GET':
        return render_template('hopeShift.html'
            ,userID=userID
            ,SMTWTFS=config.SMTWTFS
            ,NUM_FIRST_WEEKDAY_OF_TARGET_MONTH=config.NUM_FIRST_WEEKDAY_OF_TARGET_MONTH
            ,SUM_DAYS_OF_TARGET_MONTH=config.SUM_DAYS_OF_TARGET_MONTH
            ,SUM_BLOCKS_OF_CALENDAR=config.SUM_BLOCKS_OF_CALENDAR
            ,SELECT_DAYS_LIST=config.SELECT_DAYS_LIST
            ,DAY_STR_LIST=config.DAY_STR_LIST
            ,WORK_TIME_RADIO_NAME_LIST=config.WORK_TIME_RADIO_NAME_LIST
            ,DAY_LABEL_ID_LIST=config.DAY_LABEL_ID_LIST
            ,HOPE_DAY_CHECK_BOX_NAME_LIST=config.HOPE_DAY_CHECK_BOX_NAME_LIST
            ,START_SELECT_LIST=config.START_SELECT_LIST
            ,END_SELECT_LIST=config.END_SELECT_LIST
            ,START_END_DEFAULT=config.START_END_DEFAULT
            ,TARGET_YEAR=config.TARGET_YEAR
            ,TARGET_MONTH=config.TARGET_MONTH
            )

    elif request.method == 'POST':
        # HopeDayテーブル
        # 前回のレコードの削除
        deleteHopeDay = HopeDay.query.filter_by(
            userID=userID
            ,targetYear = config.TARGET_YEAR
            ,targetMonth = config.TARGET_MONTH
            ).one_or_none()
        if deleteHopeDay:
            deleteHopeDayID = deleteHopeDay.id
            db.session.delete(deleteHopeDay)
            db.session.commit()
            print('deleteHopeDay')
        # 今回のレコードの追加
        created_at = str(datetime.datetime.now(pytz.timezone('Asia/Tokyo'))).split(".")[0]
        addHopeDay = HopeDay(
            userID=userID
            ,created_at=created_at
            ,targetYear=config.TARGET_YEAR
            ,targetMonth=config.TARGET_MONTH
            )
        db.session.add(addHopeDay)
        db.session.commit()
        print('addHopeDay')

        hopeDay = HopeDay.query.filter_by(
            userID = userID
            ,targetYear = config.TARGET_YEAR
            ,targetMonth = config.TARGET_MONTH
            ).one_or_none()
        print(hopeDay, 'one_or_none')

        # HopeTimeテーブル
        # 前回のレコードの削除
        if deleteHopeDay is not None:
            deleteHopeTimes = HopeTime.query.filter_by(
                hopeDayID=deleteHopeDayID
                )
            print(deleteHopeTimes)
            for deleteHopeTime in deleteHopeTimes:
                db.session.delete(deleteHopeTime)
                db.session.commit()
            print('deleteHopeTime')
        # 今回のレコードの追加
        hopeDay = HopeDay.query.filter_by(
            userID=userID
            ,targetYear = config.TARGET_YEAR
            ,targetMonth = config.TARGET_MONTH
            ).order_by(desc(HopeDay.id)).first()
        print(hopeDay, 'first')
        for iDay in range(config.SUM_DAYS_OF_TARGET_MONTH):
            if request.form.get(f'hopeDayCheckBox_{iDay+1}'):
                start = int(request.form.get(f'start_{iDay+1}'))
                end = int(request.form.get(f'end_{iDay+1}'))
                addHopeTime = HopeTime(
                    hopeDayID=hopeDay.id
                    ,day=iDay
                    ,start=start
                    ,end=end
                    )
                db.session.add(addHopeTime)
                db.session.commit()
                print(iDay+1,start,end,'addHopeTime')
        print('hopeShiftFinish')

        flash('シフト希望の提出が完了しました', 'ok')
        return redirect(url_for('userHome', userID=userID))

@app.route('/logout')
def logout():
    if session.get("loggedID") is not None: # ログインしてない状態でアクセスすることも考慮してifとした
        session.pop("loggedID", None)

    return redirect(url_for('userLogin'))
