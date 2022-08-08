# ・保守後にデータベース内の登録をクリアにした際
# ユーザーのPCに保守前のセッション情報が残っていたらまずい
# ・update
# 変更が反映されるのが一時的（元に戻る）
# 削除した投稿の編集URL（/2/update）
# Internal Server Errorになる
# ・css
# メッセージのスタイルが反映されない

from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_login import UserMixin
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
# from flask_wtf.csrf import CSRFProtect

from werkzeug.security import generate_password_hash, check_password_hash

import jyserver.Flask as jsf

import os, datetime, pytz

import config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shift.db'

# csrf = CSRFProtect(app)
db        = SQLAlchemy(app)
bootstrap = Bootstrap(app)
admin     = Admin(app)

class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(10), nullable=False)
    loginID    = db.Column(db.String(20), nullable=False, unique=True)
    password   = db.Column(db.String(20), nullable=False)
    isFullTime = db.Column(db.Boolean, nullable=False)

class HopeDay(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    userID           = db.Column(db.Integer, nullable=False)
    targetYear       = db.Column(db.Integer, nullable=False)
    targetMonth      = db.Column(db.Integer, nullable=False)
    created_at       = db.Column(db.String(30), nullable=False)
    isUserSubmission = db.Column(db.Boolean, nullable=False)

class HopeTime(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    hopeDayID = db.Column(db.Integer, nullable=False)
    day       = db.Column(db.Integer, nullable=False)
    start     = db.Column(db.Integer, nullable=False)
    end       = db.Column(db.Integer, nullable=False)

# -----------------------------------------------
# -----------------------------------------------
# 本番環境
# app.secret_key = os.environ['SECRET_KEY']
# AUTHENTICATION_CODE = os.environ['AUTHENTICATION_CODE']
# ローカル環境
app.secret_key = config.SECRET_KEY
AUTHENTICATION_CODE = config.AUTHENTICATION_CODE
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(HopeDay, db.session))
admin.add_view(ModelView(HopeTime, db.session))
# -----------------------------------------------
# -----------------------------------------------
if not app.secret_key:
    raise ValueError("No SECRET_KEY set for Flask application")
app.permanent_session_lifetime = datetime.timedelta(minutes=10)

def isMatchLoggedID(ID):
    if ID != session.get("loggedID"):
        session.clear()
        return False
    return True

def isMatchIsFullTime(userID, part_full):
    user = User.query.filter_by(id=userID).one_or_none()

    if user is None:
        session.clear()
        return False
    if part_full != config.PART_FULL_ENG_LIST[user.isFullTime]:
        session.clear()
        return False

    return True

def tryClearSession():
    try:
        session.clear()
        print('message: Session information has been deleted.')
    except AttributeError:
        print('message: Attempted to delete session information, but could not find it.')

@app.route('/test', methods=['GET'])
def test():
    if request.method == 'GET':
        return render_template('test.html')

@app.route('/', methods=['GET'])
def index():
    tryClearSession()

    if request.method == 'GET':
        return redirect(url_for('userLogin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    tryClearSession()

    if request.method == 'GET':
        return render_template('signup.html', PART_FULL_JA_LIST=config.PART_FULL_JA_LIST)

    elif request.method == 'POST':
        name  = request.form.get('name')
        loginID   = request.form.get('loginID')
        password  = request.form.get('password')
        passwordCheck  = request.form.get('passwordCheck')
        isFullTime  = request.form.get('isFullTime')

        if name is None or loginID is None or password is None or passwordCheck is None or isFullTime is None:
            flash('入力もれがあります', 'ng')
            return render_template('signup.html')

        if passwordCheck != password:
            flash('パスワードが一致していません', 'ng')
            return render_template('signup.html')

        user = User.query.filter_by(loginID=loginID).one_or_none()
        if user is None:
            # Userテーブルに新規登録
            user = User(
                name=name
                ,loginID=loginID
                ,password=generate_password_hash(password, method='sha256')
                ,isFullTime=bool(int(isFullTime))
                )
            db.session.add(user)
            db.session.commit()

            # session情報にログインしているユーザーのIDを登録
            user = User.query.filter_by(loginID=loginID).one()
            userID = user.id
            print('get', userID)
            session.permanent = True
            session["loggedID"] = userID
            flash('新規登録が完了しました', 'ok')
            return redirect(url_for('userHome', userID=userID))
        else:
            flash('既に使われているユーザーIDです', 'ng')
            flash('登録済みの場合は、ログインページからログインしてください', 'ng')
            return render_template('signup.html')

@app.route('/userLogin', methods=['GET', 'POST'])
def userLogin():
    tryClearSession()

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
                flash('はじめての利用の場合は、新規登録ページから新規登録してください', 'ng')
            else:
                isOK = True
                userID = user.id
                session.permanent = True
                session["loggedID"] = userID

        if isOK == True:
            return redirect(url_for('userHome', userID=userID))
        elif isOK == False:
            return render_template('userLogin.html')

@app.route('/adminLogin', methods=['GET', 'POST'])
def adminLogin():
    tryClearSession()

    if request.method == 'GET':
        return render_template('adminLogin.html')

    elif request.method == 'POST':
        adminAuthenticationCode = request.form.get('adminAuthenticationCode')
        if len(adminAuthenticationCode) == 0:
            isOK = False
            flash('入力もれがあります', 'ng')
        else:
            if adminAuthenticationCode == AUTHENTICATION_CODE:
                isOK = True
                session.permanent = True
                adminID = 0
                session["loggedID"] = adminID
                flash('認証が完了しました', 'ok')
            else:
                isOK = False
                flash('認証コードが間違っています', 'ng')

        if isOK == True:
            return redirect(url_for('adminHome', adminID=adminID))
        elif isOK == False:
            return render_template('adminLogin.html')

@app.route('/<int:userID>/user/home', methods=['GET', 'POST'])
def userHome(userID):
    if not isMatchLoggedID(userID):
        return redirect(url_for('userLogin'))

    if request.method == 'GET':
        user = User.query.filter_by(id = userID).one()
        hopeDay = HopeDay.query.filter_by(
            userID = userID
            ,targetYear = config.TARGET_YEAR
            ,targetMonth = config.TARGET_MONTH
            ).one_or_none()
        print(hopeDay)

        if hopeDay is None:
            flash('提出済みの希望シフトはありません', 'ng')
            return render_template('userHome.html'
                ,user = user
                ,HOPE_SHIFT_USER_STR=config.HOPE_SHIFT_USER_STR
                ,PART_FULL_JA_LIST=config.PART_FULL_JA_LIST
                ,PART_FULL_ENG_LIST=config.PART_FULL_ENG_LIST
                )
        else:
            hopeTime = HopeTime.query.filter_by(hopeDayID = hopeDay.id).first()
            if hopeTime is not None:
                return render_template('userHome.html'
                    ,user=user
                    ,HOPE_SHIFT_USER_STR=config.HOPE_SHIFT_USER_STR
                    ,PART_FULL_JA_LIST=config.PART_FULL_JA_LIST
                    ,PART_FULL_ENG_LIST=config.PART_FULL_ENG_LIST
                    ,hopeDay=hopeDay
                    ,hopeTime=hopeTime
                    ,LAST_EDIT_LIST=config.LAST_EDIT_LIST
                    )
            else: # 想定外のバグ（hopeDayはあるがhopeTimeはない状態）
                # hopeDayのレコードの削除
                db.session.delete(hopeDay)
                db.session.commit()
                return redirect(url_for('userHome', userID=userID))

@app.route('/<int:adminID>/admin/home', methods=['GET', 'POST'])
def adminHome(adminID):
    if not isMatchLoggedID(adminID):
        return redirect(url_for('adminLogin'))

    if request.method == 'GET':
        userArr     = User.query.order_by(User.isFullTime.desc(), User.id).all()
        hopeDayArr  = HopeDay.query.order_by(HopeDay.userID).all()
        hopeTimeArr = HopeTime.query.order_by(HopeTime.hopeDayID).all()
        print(userArr)
        print(hopeDayArr)

        if userArr is None:
            return render_template('adminHome.html'
                ,adminID=adminID
                ,HOPE_SHIFT_ADMIN_STR=config.HOPE_SHIFT_ADMIN_STR
                )
        elif hopeDayArr is None or hopeTimeArr is None:
            return render_template('adminHome.html'
                ,adminID=adminID
                ,userArr=userArr
                ,HOPE_SHIFT_ADMIN_STR=config.HOPE_SHIFT_ADMIN_STR
                ,PART_FULL_JA_LIST=config.PART_FULL_JA_LIST
                )
        else:
            return render_template('adminHome.html'
                ,adminID=adminID
                ,userArr=userArr
                ,hopeDayArr=hopeDayArr
                ,hopeTimeArr=hopeTimeArr
                ,LAST_EDIT_LIST=config.LAST_EDIT_LIST
                ,HOPE_SHIFT_ADMIN_STR=config.HOPE_SHIFT_ADMIN_STR
                ,PART_FULL_JA_LIST=config.PART_FULL_JA_LIST
                )

# @app.route('/<int:userID>/user/create', methods=['GET'])
# def create(userID):
#     if not isMatchLoggedID(userID):
#         return redirect(url_for('userLogin'))

#     if request.method == 'GET':
#         return redirect('hopeShift'
#                         ,userID=userID
#                         ,part_full=config.PART_FULL_ENG_LIST[isFullTime])


@app.route('/<int:userID>/user/create/<string:part_full>/hopeShift', methods=['GET', 'POST'])
def hopeShift(userID, part_full):
    if not isMatchLoggedID(userID):
        return redirect(url_for('userLogin'))

    if not isMatchIsFullTime(userID, part_full):
        return redirect(url_for('userLogin'))

    if request.method == 'GET':
        if part_full == config.PART_FULL_ENG_LIST[0]:
            return render_template('hopeShiftPartTime.html'
                ,userID=userID
                ,SMTWTFS=config.SMTWTFS
                ,DAY_STR_LIST=config.DAY_STR_LIST
                ,WORK_TIME_RADIO_NAME_LIST=config.WORK_TIME_RADIO_NAME_LIST
                ,DAY_LABEL_ID_LIST=config.DAY_LABEL_ID_LIST
                ,HOPE_DAY_CHECK_BOX_NAME_LIST=config.HOPE_DAY_CHECK_BOX_NAME_LIST
                ,START_SELECT_LIST=config.START_SELECT_LIST
                ,END_SELECT_LIST=config.END_SELECT_LIST
                ,START_END_DEFAULT=config.START_END_DEFAULT
                )

        elif part_full == config.PART_FULL_ENG_LIST[1]:
            return render_template('hopeShiftFullTime.html'
                ,userID=userID
                ,SMTWTFS=config.SMTWTFS
                ,NUM_FIRST_WEEKDAY_OF_TARGET_MONTH=config.NUM_FIRST_WEEKDAY_OF_TARGET_MONTH
                ,SUM_DAYS_OF_TARGET_MONTH=config.SUM_DAYS_OF_TARGET_MONTH
                ,SUM_BLOCKS_OF_CALENDAR=config.SUM_BLOCKS_OF_CALENDAR
                ,SELECT_DAYS_LIST=config.SELECT_DAYS_LIST
                ,FULL_TIME_LIST=config.FULL_TIME_LIST
                )

    elif request.method == 'POST':
        hopeDayList = []
        if part_full == config.PART_FULL_ENG_LIST[0]:
            startList = []
            endList = []
            for iDay in range(config.SUM_DAYS_OF_TARGET_MONTH):
                print(request.form.get(f'hopeDayCheckBox_{iDay+1}'))
                if request.form.get(f'hopeDayCheckBox_{iDay+1}'):
                    hopeDayList.append(iDay+1)
                    startList.append(int(request.form.get(f'start_{iDay+1}')))
                    endList.append(int(request.form.get(f'end_{iDay+1}')))
        if part_full == config.PART_FULL_ENG_LIST[1]:
            for iDay in range(config.SUM_DAYS_OF_TARGET_MONTH):
                print(request.form.get(f'isHopeDay{iDay+1}'))
                if request.form.get(f'isHopeDay{iDay+1}') is None:
                    hopeDayList.append(iDay+1)
            startList = [config.FULL_TIME_LIST[0]]*len(hopeDayList)
            endList = [config.FULL_TIME_LIST[1]]*len(hopeDayList)

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
            ,targetYear=config.TARGET_YEAR
            ,targetMonth=config.TARGET_MONTH
            ,created_at=created_at
            ,isUserSubmission=True
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
            deleteHopeTimeArr = HopeTime.query.filter_by(
                hopeDayID=deleteHopeDayID
                )
            print(deleteHopeTimeArr)
            for deleteHopeTime in deleteHopeTimeArr:
                db.session.delete(deleteHopeTime)
                db.session.commit()
            print('deleteHopeTime')
        # 今回のレコードの追加
        hopeDay = HopeDay.query.filter_by(
            userID=userID
            ,targetYear = config.TARGET_YEAR
            ,targetMonth = config.TARGET_MONTH
            ).one()
        print(hopeDay, 'first')
        for iDay in range(len(hopeDayList)):
            addHopeTime = HopeTime(
                hopeDayID=hopeDay.id
                ,day=hopeDayList[iDay]
                ,start=startList[iDay]
                ,end=endList[iDay]
                )
            db.session.add(addHopeTime)
            db.session.commit()
            print(hopeDayList[iDay], startList[iDay], endList[iDay], 'addHopeTime')
        print('hopeShiftFinish')

        flash('シフト希望の提出が完了しました', 'ok')
        return redirect(url_for('userHome', userID=userID))

@app.route('/logout')
def logout():
    tryClearSession()
    return redirect(url_for('userLogin'))
