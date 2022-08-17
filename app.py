## 命名規則
# 「ID」は大文字
# スネークケースが好きではないので、基本、キャメルケースで書いていますが、flask-SQLAlchemyのモデルの項目はスネークケースで書いています。
# flask-SQLAlchemyのモデルの項目はキャメルケースで書くと、自動的にスネークケースに変換されてしまうので、外部キー制約を行う際にバグの発生源になります。

## 問題
# ・保守後にデータベース内の登録をクリアにした際
# ユーザーのPCに保守前のセッション情報が残っていたらまずい

# ・css
# メッセージのスタイルが反映されない
# レスポンシブ対応
# base.cssが反映されない
# BEMがわからん

# ・csrf

## タスク
# ・フォーム判定
# Vueに任せて、バックエンドの条件分岐を減らしたい（可読性のため）

# ・登録済み情報を反映させる

# ・CSS
# メッセージをおしゃれにする

# ・データベースの整合性を保つ
# Submit.idとHopeShift.submit_idで片方しかないIDがあった場合は削除する

# ・pyファイルを分ける

# ・管理者機能
# 1. 祝日設定（この後に希望調査）
# 来月の設定のみ、変更した場合は来月の希望シフトを削除する（整合性をとるため）
# 2. 最適化システム
# パラメータのチューニングどうする？
# 3. 人の手による微調整
# PCのみ対応（スマホ非対応）
# レベル変更（適宜）
# 勤務時間帯条件設定（適宜）

# ・ユーザー機能
# 個人: 「今月のシフト」「来月の希望シフトまたは決定シフト」
# 全体: 今月と来月のシフトを表示

# ・設計書作成
# ・サブスク機能

# ・疑問
# メンテナンスにおけるデータベースの整合性はどうやって保証する
# エクセルにして吐き出す機能も必要？
# テストのやり方

from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
# from flask_login import UserMixin
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
# from flask_wtf.csrf import CSRFProtect

from werkzeug.security import generate_password_hash, check_password_hash

import datetime, pytz, os

import config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shift.db'

# csrf = CSRFProtect(app)
db        = SQLAlchemy(app, session_options={"autoflush": False})
bootstrap = Bootstrap(app)
admin     = Admin(app)

class User(db.Model):
    __tabelname__ = 'user'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(10), nullable=False)
    login_id    = db.Column(db.String(20), nullable=False, unique=True)
    password   = db.Column(db.String(20), nullable=False)
    is_full_time = db.Column(db.Boolean, nullable=False)
    level      = db.Column(db.Integer, nullable=False)
    submit    = db.relationship('Submit', backref='user')

class Submit(db.Model):
    __tabelname__ = 'submit'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_year       = db.Column(db.Integer, nullable=False)
    target_month      = db.Column(db.Integer, nullable=False)
    created_at       = db.Column(db.String(30), nullable=False)
    is_user_submission = db.Column(db.Boolean, nullable=False)
    hope_time    = db.relationship('HopeShift', backref='submit')

class HopeShift(db.Model):
    __tabelname__ = 'hope_time'
    id        = db.Column(db.Integer, primary_key=True)
    submit_id = db.Column(db.Integer, db.ForeignKey('submit.id'), nullable=False)
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
admin.add_view(ModelView(Submit, db.session))
admin.add_view(ModelView(HopeShift, db.session))
# -----------------------------------------------
# -----------------------------------------------
if not app.secret_key:
    raise ValueError("No SECRET_KEY set for Flask application")
app.permanent_session_lifetime = datetime.timedelta(minutes=10)
# -----------------------------------------------
# -----------------------------------------------

def isMatchLoggedID(userID):
    return userID == session.get("loggedID")

def isAdminMethod():
    return session.get("loggedID") == config.ADMIN_ID

# userのisFullTimeを返す。なければNone
def getFullOrPart(userID):
    user = User.query.filter_by(id=userID).one_or_none()

    if user is None:
        return None
    else:
        return config.PART_FULL_ENG_LIST[user.is_full_time]

def isMatchFullOrPart(userID, part_full):
    return part_full == getFullOrPart(userID)

def tryClearSession():
    try:
        session.clear()
        print('message: Session information has been deleted.')
    except AttributeError:
        print('message: Attempted to delete session information, but could not find it.')

# 対象月のsubmitのIDを返す。なければNone
def getSubmitIDOfTarget(userID, targetYearMonth):
    submit = Submit.query.filter_by(
        user_id=userID
        ,target_year = targetYearMonth[0]
        ,target_month = targetYearMonth[1]
        ).one_or_none()
    if submit:
        return submit.id
    else:
        return None

def deleteSubmitAndHopeShift(deleteSubmitID):
    deleteSubmit = Submit.query.filter_by(id=deleteSubmitID).one()
    db.session.delete(deleteSubmit)
    deleteHopeShiftArr = HopeShift.query.filter_by(
        submit_id=deleteSubmitID
        )
    for deleteHopeShift in deleteHopeShiftArr:
        db.session.delete(deleteHopeShift)
    db.session.commit()
    print('deleted Submit and HopeShift record')

# 希望シフトのリスト化
def listHopeShift(part_full):
    hopeDayList = []
    if part_full == config.PART_FULL_ENG_LIST[0]:
        startList = []
        endList = []
        for iDay in config.DAYS_OF_TARGET_MONTH_LIST:
            print(request.form.get(f'hopeDayCheckBox_{iDay}'))
            if request.form.get(f'hopeDayCheckBox_{iDay}'):
                hopeDayList.append(iDay)
                startList.append(int(request.form.get(f'start_{iDay}')))
                endList.append(int(request.form.get(f'end_{iDay}')))
    if part_full == config.PART_FULL_ENG_LIST[1]:
        for iDay in config.DAYS_OF_TARGET_MONTH_LIST:
            print(request.form.get(f'isHopeHoliday{iDay}'))
            if request.form.get(f'isHopeHoliday{iDay}') is None:
                hopeDayList.append(iDay)
        startList = [config.FULL_TIME_START_END_LIST[0]]*len(hopeDayList)
        endList = [config.FULL_TIME_START_END_LIST[1]]*len(hopeDayList)

    return hopeDayList, startList, endList

# submitとhopeShiftレコードの追加
def addSubmitAndHopeShift(userID, isUserSubmission, hopeDayList, startList, endList):
    # submitレコードの追加
    created_at = str(datetime.datetime.now(pytz.timezone('Asia/Tokyo'))).split(".")[0]
    addSubmit = Submit(
        user_id=userID
        ,target_year=config.TARGET_YEAR_MONTH[0]
        ,target_month=config.TARGET_YEAR_MONTH[1]
        ,created_at=created_at
        ,is_user_submission=isUserSubmission
        )
    db.session.add(addSubmit)
    db.session.commit()
    submit = Submit.query.filter_by(
        user_id=userID
        ,target_year = config.TARGET_YEAR_MONTH[0]
        ,target_month = config.TARGET_YEAR_MONTH[1]
        ).one()
    addSubmitID = submit.id
    print('add Submit record')

    # hopeShiftレコードの追加
    for iDay in range(len(hopeDayList)):
        addHopeShift = HopeShift(
            submit_id=addSubmitID
            ,day=hopeDayList[iDay]
            ,start=startList[iDay]
            ,end=endList[iDay]
            )
        db.session.add(addHopeShift)
        db.session.commit()
        print(hopeDayList[iDay], startList[iDay], endList[iDay], 'addHopeShift')

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
        print('name')
        print(name)
        print('loginID')
        print(loginID)

        if len(name) * len(loginID) * len(password) * len(passwordCheck) * len(isFullTime) == 0:
            flash('入力もれがあります', 'ng')
            return render_template('signup.html', PART_FULL_JA_LIST=config.PART_FULL_JA_LIST)

        if passwordCheck != password:
            flash('パスワードが一致していません', 'ng')
            return render_template('signup.html', PART_FULL_JA_LIST=config.PART_FULL_JA_LIST)

        user = User.query.filter_by(login_id=loginID).one_or_none()
        if user is None:
            if int(isFullTime) == 1:
                level = config.FULL_LEVEL
            elif int(isFullTime) == 0:
                level = config.PART_DEFAULT_LEVEL

            # Userテーブルに新規登録
            user = User(
                name=name
                ,login_id=loginID
                ,password=generate_password_hash(password, method='sha256')
                ,is_full_time=bool(int(isFullTime))
                ,level=level
                )
            db.session.add(user)
            db.session.commit()

            # session情報にログインしているユーザーのIDを登録
            user = User.query.filter_by(login_id=loginID).one()
            userID = user.id
            print('get', userID)
            session.permanent = True
            session["loggedID"] = userID
            flash('新規登録が完了しました', 'ok')
            return redirect(url_for('userHome', userID=userID))
        else:
            flash('既に使われているユーザーIDです', 'ng')
            flash('登録済みの場合は、ログインページからログインしてください', 'ng')
            return render_template('signup.html', PART_FULL_JA_LIST=config.PART_FULL_JA_LIST)

@app.route('/userLogin', methods=['GET', 'POST'])
def userLogin():
    tryClearSession()

    if request.method == 'GET':
        return render_template('userLogin.html')

    elif request.method == 'POST':
        loginID = request.form.get('loginID')
        password = request.form.get('password')
        print('password')
        print(len(password) == 0)

        if len(loginID) * len(password) == 0:
            isOK = False
            flash('入力もれがあります', 'ng')
        else:
            user = User.query.filter_by(login_id=loginID).one_or_none()
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
                session["loggedID"] = config.ADMIN_ID
            else:
                isOK = False
                flash('認証コードが間違っています', 'ng')

        if isOK == True:
            return redirect(url_for('adminHome'))
        elif isOK == False:
            return render_template('adminLogin.html')

@app.route('/<int:userID>/user/home', methods=['GET', 'POST'])
def userHome(userID):
    if not isMatchLoggedID(userID):
        session.clear()
        return redirect(url_for('userLogin'))

    if request.method == 'GET':
        user = User.query.filter_by(id=userID).one()
        submit = Submit.query.filter_by(
            user_id=userID
            ,target_year = config.TARGET_YEAR_MONTH[0]
            ,target_month = config.TARGET_YEAR_MONTH[1]
            ).one_or_none()
        print(submit)

        if submit is None:
            flash('提出済みの希望シフトはありません', 'ng')
            return render_template('userHome.html'
                ,user = user
                ,TARGET_DATE_STR=config.TARGET_DATE_STR
                ,PART_FULL_JA_LIST=config.PART_FULL_JA_LIST
                ,PART_FULL_ENG_LIST=config.PART_FULL_ENG_LIST
                )
        else:
            hopeShift = HopeShift.query.filter_by(submit_id = submit.id).first()
            if hopeShift is not None:
                return render_template('userHome.html'
                    ,user=user
                    ,TARGET_DATE_STR=config.TARGET_DATE_STR
                    ,PART_FULL_JA_LIST=config.PART_FULL_JA_LIST
                    ,PART_FULL_ENG_LIST=config.PART_FULL_ENG_LIST
                    ,submit=submit
                    ,LAST_EDIT_LIST=config.LAST_EDIT_LIST
                    )
            else: # 想定外のバグ（Submit.idはあるがHopeShift.submit_idにないIDがある状態）
                # submitのレコードの削除
                db.session.delete(submit)
                db.session.commit()
                return redirect(url_for('userHome', userID=userID))

@app.route('/admin/home', methods=['GET', 'POST'])
def adminHome():
    if not isAdminMethod():
        session.clear()
        return redirect(url_for('adminLogin'))

    if request.method == 'GET':
        targetMonthArr = db.session.query(
            User, Submit)\
            .filter(or_(and_(Submit.target_year == config.TARGET_YEAR_MONTH[0]
            ,Submit.target_month == config.TARGET_YEAR_MONTH[1]), Submit.target_year == None))\
            .order_by(User.is_full_time.desc(), User.id)\
            .outerjoin(Submit, User.id == Submit.user_id)\
            .all()
        print(targetMonthArr)
        return render_template('adminHome.html'
            ,targetMonthArr=targetMonthArr
            ,LAST_EDIT_LIST=config.LAST_EDIT_LIST
            ,CURRENT_DATE_STR=config.CURRENT_DATE_STR
            ,TARGET_DATE_STR=config.TARGET_DATE_STR
            ,PART_FULL_JA_LIST=config.PART_FULL_JA_LIST
            ,PART_FULL_ENG_LIST=config.PART_FULL_ENG_LIST
            )

@app.route('/<int:userID>/user/create/<string:part_full>/hopeShift', methods=['GET', 'POST'])
def hopeShift(userID, part_full):
    if isAdminMethod():
        isAdmin = True
    else:
        isAdmin = False
        if not isMatchLoggedID(userID) or not isMatchFullOrPart(userID, part_full):
            session.clear()
            return redirect(url_for('userLogin'))

    if request.method == 'GET':
        # hopeDay、start、endのデフォルトリストを作成
        DAYS_OF_TARGET_MONTH_LIST = config.DAYS_OF_TARGET_MONTH_LIST
        defaultHopeDayList = [1]*len(DAYS_OF_TARGET_MONTH_LIST)
        if part_full == config.PART_FULL_ENG_LIST[0]:
            defaultStartList = [config.PART_TIME_START_END_DEFAULT_LIST[0]]*len(defaultHopeDayList)
            defaultEndList = [config.PART_TIME_START_END_DEFAULT_LIST[1]]*len(defaultHopeDayList)
        elif part_full == config.PART_FULL_ENG_LIST[1]:
            defaultStartList = [config.FULL_TIME_START_END_LIST[0]]*len(defaultHopeDayList)
            defaultEndList = [config.FULL_TIME_START_END_LIST[1]]*len(defaultHopeDayList)

        submitID = getSubmitIDOfTarget(userID, config.TARGET_YEAR_MONTH)
        if submitID:
            defaultHopeDayList = [0]*len(DAYS_OF_TARGET_MONTH_LIST)
            hopeShiftArr = HopeShift.query.filter_by(submit_id=submitID).order_by(HopeShift.day).all()
            for hopeShift in hopeShiftArr:
                defaultHopeDayList[hopeShift.day-1] = 1
                defaultStartList[hopeShift.day-1] = hopeShift.start
                defaultEndList[hopeShift.day-1] = hopeShift.end

        if part_full == config.PART_FULL_ENG_LIST[0]:
            return render_template('hopeShiftPartTime.html'
                ,userID=userID
                ,isAdmin=isAdmin
                ,SMTWTFS=config.SMTWTFS
                ,DAY_STR_LIST=config.DAY_STR_LIST
                ,WORK_TIME_RADIO_NAME_LIST=config.WORK_TIME_RADIO_NAME_LIST
                ,DAYS_OF_TARGET_MONTH_LIST=DAYS_OF_TARGET_MONTH_LIST
                ,FIRST_SUNDAY_TARGET_MONTH=config.FIRST_SUNDAY_TARGET_MONTH
                ,PART_TIME_START_OPTION_LIST=config.PART_TIME_START_OPTION_LIST
                ,PART_TIME_END_OPTION_LIST=config.PART_TIME_END_OPTION_LIST
                ,PART_TIME_START_END_DEFAULT_LIST=config.PART_TIME_START_END_DEFAULT_LIST
                ,TARGET_YEAR_MONTH=config.TARGET_YEAR_MONTH
                ,defaultHopeDayList=defaultHopeDayList
                ,defaultStartList=defaultStartList
                ,defaultEndList=defaultEndList
                )

        elif part_full == config.PART_FULL_ENG_LIST[1]:
            return render_template('hopeShiftFullTime.html'
                ,userID=userID
                ,isAdmin=isAdmin
                ,SMTWTFS=config.SMTWTFS
                ,NUM_FIRST_WEEKDAY_OF_TARGET_MONTH=config.NUM_FIRST_WEEKDAY_OF_TARGET_MONTH
                ,SUM_BLOCKS_OF_CALENDAR=config.SUM_BLOCKS_OF_CALENDAR
                ,DAYS_OF_TARGET_MONTH_LIST=DAYS_OF_TARGET_MONTH_LIST
                ,FIRST_SUNDAY_TARGET_MONTH=config.FIRST_SUNDAY_TARGET_MONTH
                ,FULL_TIME_START_END_LIST=config.FULL_TIME_START_END_LIST
                ,TARGET_YEAR_MONTH=config.TARGET_YEAR_MONTH
                ,defaultHopeDayList=defaultHopeDayList
                ,defaultStartList=defaultStartList
                ,defaultEndList=defaultEndList
                )

    elif request.method == 'POST':
        hopeDayList, startList, endList = listHopeShift(part_full)

        deleteSubmitID = getSubmitIDOfTarget(userID, config.TARGET_YEAR_MONTH)

        # 既存の対象レコードの削除
        if deleteSubmitID is not None:
            deleteSubmitAndHopeShift(deleteSubmitID)

        addSubmitAndHopeShift(userID, isAdmin^1, hopeDayList, startList, endList)

        if isAdmin:
            flash('希望シフトの変更が完了しました', 'ok')
            return redirect(url_for('adminHome'))
        else:
            flash('希望シフトの提出が完了しました', 'ok')
            return redirect(url_for('userHome', userID=userID))

@app.route('/admin/delete/user/<int:userID>', methods=['GET', 'POST'])
def editUserTable():
    if request.method == 'GET':
        return render_template('editUserTable.html')
    elif request.method == 'POST':
        return redirect(url_for('adminHome'))

@app.route('/admin/create/shift', methods=['GET', 'POST'])
def createShift():
    if request.method == 'GET':
        hopeShiftArr = db.session.query(
            User, Submit, HopeShift)\
            .filter(Submit.target_year == config.TARGET_YEAR_MONTH[0]
            ,Submit.target_month == config.TARGET_YEAR_MONTH[1])\
            .order_by(User.is_full_time.desc(), User.id)\
            .join(Submit, User.id == Submit.user_id)\
            .join(HopeShift, Submit.id == HopeShift.submit_id)\
            .all()
        return render_template('createShift.html'
            ,hopeShiftArr=hopeShiftArr
            ,TARGET_YEAR_MONTH=config.TARGET_YEAR_MONTH
            ,PART_FULL_JA_LIST=config.PART_FULL_JA_LIST)

@app.route('/admin/edit/user', methods=['GET', 'POST'])
def editUserInfo():
    if request.method == 'GET':
        userArr  = User.query.order_by(User.is_full_time.desc(), User.id).all()

@app.route('/logout')
def logout():
    tryClearSession()
    return redirect(url_for('userLogin'))
