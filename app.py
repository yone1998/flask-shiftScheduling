## 命名規則
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
# HopeShift.idとHopeShiftTime.hope_shift_idで片方しかないIDがあった場合は削除する

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
import numpy as np

import const


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
    hope_shift    = db.relationship('HopeShift', backref='user')

class HopeShift(db.Model):
    __tabelname__ = 'hope_shift'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_year       = db.Column(db.Integer, nullable=False)
    target_month      = db.Column(db.Integer, nullable=False)
    created_at       = db.Column(db.String(30), nullable=False)
    is_user_submission = db.Column(db.Boolean, nullable=False)
    hope_shift_time    = db.relationship('HopeShiftTime', backref='hope_shift')

class HopeShiftTime(db.Model):
    __tabelname__ = 'hope_shift_time'
    id        = db.Column(db.Integer, primary_key=True)
    hope_shift_id = db.Column(db.Integer, db.ForeignKey('hope_shift.id'), nullable=False)
    day       = db.Column(db.Integer, nullable=False)
    start     = db.Column(db.Integer, nullable=False)
    end       = db.Column(db.Integer, nullable=False)

class Condition(db.Model):
    __tabelname__ = 'condition'
    id        = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.Integer, nullable=False)
    sum_full_time = db.Column(db.Integer, nullable=False)
    sum_part_time = db.Column(db.Integer, nullable=False)
    last = db.Column(db.Integer, nullable=False)
    condition_part_time = db.relationship('ConditionPartTime', backref='condition')

class ConditionPartTime(db.Model):
    __tabelname__ = 'condition_part_time'
    id        = db.Column(db.Integer, primary_key=True)
    condition_id = db.Column(db.Integer, db.ForeignKey('condition.id'), nullable=False)
    part_id   = db.Column(db.Integer, nullable=False)
    start     = db.Column(db.Integer, nullable=False)
    end       = db.Column(db.Integer, nullable=False)

# -----------------------------------------------
# -----------------------------------------------
# 本番環境
# app.secret_key = os.environ['SECRET_KEY']
# AUTHENTICATION_CODE = os.environ['AUTHENTICATION_CODE']
# ローカル環境
app.secret_key = const.SECRET_KEY
AUTHENTICATION_CODE = const.AUTHENTICATION_CODE
# -----------------------------------------------
# -----------------------------------------------

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(HopeShift, db.session))
admin.add_view(ModelView(HopeShiftTime, db.session))
admin.add_view(ModelView(Condition, db.session))
admin.add_view(ModelView(ConditionPartTime, db.session))

if not app.secret_key:
    raise ValueError("No SECRET_KEY set for Flask application")
app.permanent_session_lifetime = datetime.timedelta(minutes=60)
# -----------------------------------------------
# -----------------------------------------------

def isMatchLoggedId(userId):
    return userId == session.get("loggedId")

def isAdminMethod():
    return session.get("loggedId") == const.ADMIN_ID

# userのisFullTimeを返す。なければNone
def getFullOrPart(userId):
    user = User.query.filter_by(id=userId).one_or_none()

    if user is None:
        return None
    else:
        return const.PART_FULL_ENG_LIST[user.is_full_time]

def isMatchFullOrPart(userId, part_full):
    return part_full == getFullOrPart(userId)

def tryClearSession():
    try:
        session.clear()
        print('message: Session information has been deleted.')
    except AttributeError:
        print('message: Attempted to delete session information, but could not find it.')

# 対象月のhopeShift.idを返す。なければNone
def getHopeShiftIdOfTarget(userId, targetYearMonth):
    hopeShift = HopeShift.query.filter_by(
        user_id=userId
        ,target_year = targetYearMonth[0]
        ,target_month = targetYearMonth[1]
        ).one_or_none()
    if hopeShift:
        return hopeShift.id
    else:
        return None

def table2defaultHopeShiftList(userId, part_full):
    DAYS_OF_TARGET_MONTH_LIST = const.DAYS_OF_TARGET_MONTH_LIST
    defaultHopeDayList = [1]*len(DAYS_OF_TARGET_MONTH_LIST)
    if part_full == const.PART_FULL_ENG_LIST[0]:
        defaultStartList = [const.PART_TIME_START_END_DEFAULT_LIST[0]]*len(defaultHopeDayList)
        defaultEndList = [const.PART_TIME_START_END_DEFAULT_LIST[1]]*len(defaultHopeDayList)
    elif part_full == const.PART_FULL_ENG_LIST[1]:
        defaultStartList = [const.FULL_TIME_START_END_LIST[0]]*len(defaultHopeDayList)
        defaultEndList = [const.FULL_TIME_START_END_LIST[1]]*len(defaultHopeDayList)

    hopeShiftId = getHopeShiftIdOfTarget(userId, const.TARGET_YEAR_MONTH)
    if hopeShiftId:
        defaultHopeDayList = [0]*len(DAYS_OF_TARGET_MONTH_LIST)
        hopeShiftTimeArr = HopeShiftTime.query.filter_by(hope_shift_id=hopeShiftId).order_by(HopeShiftTime.day).all()
        for hopeShiftTime in hopeShiftTimeArr:
            defaultHopeDayList[hopeShiftTime.day-1] = 1
            defaultStartList[hopeShiftTime.day-1] = hopeShiftTime.start
            defaultEndList[hopeShiftTime.day-1] = hopeShiftTime.end

    return defaultHopeDayList, defaultStartList, defaultEndList

# 希望シフトのリスト化
def form2hopeShiftList(part_full):
    hopeDayList = []
    if part_full == const.PART_FULL_ENG_LIST[0]:
        startList = []
        endList = []
        for iDay in const.DAYS_OF_TARGET_MONTH_LIST:
            print(request.form.get(f'hopeDayCheckBox_{iDay}'))
            if request.form.get(f'hopeDayCheckBox_{iDay}'):
                hopeDayList.append(iDay)
                startList.append(int(request.form.get(f'start_{iDay}')))
                endList.append(int(request.form.get(f'end_{iDay}')))
    if part_full == const.PART_FULL_ENG_LIST[1]:
        for iDay in const.DAYS_OF_TARGET_MONTH_LIST:
            print(request.form.get(f'day{iDay}'))
            if request.form.get(f'day{iDay}'):
                hopeDayList.append(iDay)
        startList = [const.FULL_TIME_START_END_LIST[0]]*len(hopeDayList)
        endList = [const.FULL_TIME_START_END_LIST[1]]*len(hopeDayList)

    return hopeDayList, startList, endList

def deleteHopeShiftOrCondition(deleteId, role):
    if role == 'hopeShift':
        deleteHopeShift = HopeShift.query.filter_by(id=deleteId).one()
        db.session.delete(deleteHopeShift)
        deleteHopeShiftTimeArr = HopeShiftTime.query.filter_by(
            hope_shift_id=deleteId
            )
        for deleteHopeShiftTime in deleteHopeShiftTimeArr:
            db.session.delete(deleteHopeShiftTime)
        db.session.commit()
        print('deleted HopeShift and HopeShiftTime record')
    elif role == 'condition':
        deleteCondition = Condition.query.filter_by(id=deleteId).one()
        db.session.delete(deleteCondition)
        deleteConditionPartTimeArr = ConditionPartTime.query.filter_by(
            hope_shift_id=deleteId
            )
        for deleteConditionPartTime in deleteConditionPartTimeArr:
            db.session.delete(deleteConditionPartTime)
        db.session.commit()
        print('deleted Condition and ConditionPartTime record')

# hopeShiftとhopeShiftTimeレコードの追加
def addHopeShiftAndHopeShiftTime(userId, isUserSubmission, hopeDayList, startList, endList):
    # hopeShiftレコードの追加
    created_at = str(datetime.datetime.now(pytz.timezone('Asia/Tokyo'))).split(".")[0]
    addHopeShift = HopeShift(
        user_id=userId
        ,target_year=const.TARGET_YEAR_MONTH[0]
        ,target_month=const.TARGET_YEAR_MONTH[1]
        ,created_at=created_at
        ,is_user_submission=isUserSubmission
        )
    db.session.add(addHopeShift)
    db.session.commit()
    hopeShift = HopeShift.query.filter_by(
        user_id=userId
        ,target_year = const.TARGET_YEAR_MONTH[0]
        ,target_month = const.TARGET_YEAR_MONTH[1]
        ).one()
    addHopeShiftId = hopeShift.id
    print('add HopeShift record')

    # hopeShiftTimeレコードの追加
    for iDay in range(len(hopeDayList)):
        addHopeShiftTime = HopeShiftTime(
            hope_shift_id=addHopeShiftId
            ,day=hopeDayList[iDay]
            ,start=startList[iDay]
            ,end=endList[iDay]
            )
        db.session.add(addHopeShiftTime)
        db.session.commit()
        print(hopeDayList[iDay], startList[iDay], endList[iDay], 'addHopeShiftTime')

# 条件のリスト化
def form2conditionPartTimeList():
    startList = []
    endList = []
    iPart = 1
    while (request.form.get(f'partStart{iPart}') is not None):
        startList.append(int(request.form.get(f'partStart{iPart}')))
        endList.append(int(request.form.get(f'partEnd{iPart}')))
        iPart += 1

    # 早い順に並びかえ
    startEndList = np.vstack((np.array(startList), np.array(endList))).transpose().tolist()
    startEndList = np.array(sorted(startEndList)).transpose().tolist()

    startList, endList = startEndList
    return startList, endList

# conditionとconditionPartTimeレコードの追加
def addConditionAndConditionPartTime(conditionList, startList, endList):
    # class Condition(db.Model):
    # sum_full_time = db.Column(db.Integer, nullable=False)
    # sum_part_time = db.Column(db.Integer, nullable=False)
    # last = db.Column(db.Integer, nullable=False)
# class ConditionPartTime(db.Model):
#     part_id   = db.Column(db.Integer, nullable=False)
#     start     = db.Column(db.Integer, nullable=False)
#     end       = db.Column(db.Integer, nullable=False)
    # conditionレコードの追加
    addCondition = Condition(
        event = conditionList[0]
        ,sum_full_time = conditionList[1]
        ,sum_part_time = conditionList[2]
        ,last = max(endList)
        )
    db.session.add(addCondition)
    db.session.commit()
    condition = Condition.query.filter_by(
        event = conditionList[0]
        ,sum_full_time = conditionList[1]
        ).one()
    addConditionId = condition.id
    print('add Condition record')

    # conditionPartTimeレコードの追加
    for iPart in range(len(startList)):
        addConditionPartTime = ConditionPartTime(
            condition_id=addConditionId
            ,part_id=iPart+1
            ,start=startList[iPart]
            ,end=endList[iPart]
            )
        db.session.add(addConditionPartTime)
        db.session.commit()
        print(iPart+1, startList[iPart], endList[iPart], 'addHopeShiftTime')

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
        return render_template('signup.html', PART_FULL_JA_LIST=const.PART_FULL_JA_LIST)

    elif request.method == 'POST':
        name  = request.form.get('name')
        loginId   = request.form.get('loginId')
        password  = request.form.get('password')
        passwordCheck  = request.form.get('passwordCheck')
        isFullTime  = request.form.get('isFullTime')
        print('name')
        print(name)
        print('loginId')
        print(loginId)

        if len(name) * len(loginId) * len(password) * len(passwordCheck) * len(isFullTime) == 0:
            flash('入力もれがあります', 'ng')
            return render_template('signup.html', PART_FULL_JA_LIST=const.PART_FULL_JA_LIST)

        if passwordCheck != password:
            flash('パスワードが一致していません', 'ng')
            return render_template('signup.html', PART_FULL_JA_LIST=const.PART_FULL_JA_LIST)

        user = User.query.filter_by(login_id=loginId).one_or_none()
        if user is None:
            if int(isFullTime) == 1:
                level = const.FULL_LEVEL
            elif int(isFullTime) == 0:
                level = const.PART_DEFAULT_LEVEL

            # Userテーブルに新規登録
            user = User(
                name=name
                ,login_id=loginId
                ,password=generate_password_hash(password, method='sha256')
                ,is_full_time=bool(int(isFullTime))
                ,level=level
                )
            db.session.add(user)
            db.session.commit()

            # session情報にログインしているユーザーのIDを登録
            user = User.query.filter_by(login_id=loginId).one()
            userId = user.id
            print('get', userId)
            session.permanent = True
            session["loggedId"] = userId
            flash('新規登録が完了しました', 'ok')
            return redirect(url_for('userHome', userId=userId))
        else:
            flash('既に使われているユーザーIDです', 'ng')
            flash('登録済みの場合は、ログインページからログインしてください', 'ng')
            return render_template('signup.html', PART_FULL_JA_LIST=const.PART_FULL_JA_LIST)

@app.route('/userLogin', methods=['GET', 'POST'])
def userLogin():
    tryClearSession()

    if request.method == 'GET':
        return render_template('userLogin.html')

    elif request.method == 'POST':
        loginId = request.form.get('loginId')
        password = request.form.get('password')
        print('password')
        print(len(password) == 0)

        if len(loginId) * len(password) == 0:
            isOK = False
            flash('入力もれがあります', 'ng')
        else:
            user = User.query.filter_by(login_id=loginId).one_or_none()
            if user is None or check_password_hash(user.password, password) == False:
                isOK = False
                flash('ユーザーIDまたはパスワードが正しくありません', 'ng')
                flash('はじめての利用の場合は、新規登録ページから新規登録してください', 'ng')
            else:
                isOK = True
                userId = user.id
                session.permanent = True
                session["loggedId"] = userId

        if isOK == True:
            return redirect(url_for('userHome', userId=userId))
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
                session["loggedId"] = const.ADMIN_ID
            else:
                isOK = False
                flash('認証コードが間違っています', 'ng')

        if isOK == True:
            return redirect(url_for('adminHome'))
        elif isOK == False:
            return render_template('adminLogin.html')

@app.route('/<int:userId>/user/home', methods=['GET', 'POST'])
def userHome(userId):
    if not isMatchLoggedId(userId):
        session.clear()
        return redirect(url_for('userLogin'))

    if request.method == 'GET':
        user = User.query.filter_by(id=userId).one()
        hopeShift = HopeShift.query.filter_by(
            user_id=userId
            ,target_year = const.TARGET_YEAR_MONTH[0]
            ,target_month = const.TARGET_YEAR_MONTH[1]
            ).one_or_none()
        print(hopeShift)

        if hopeShift is None:
            return render_template('userHome.html'
                ,user = user
                ,TARGET_DATE_STR=const.TARGET_DATE_STR
                ,PART_FULL_JA_LIST=const.PART_FULL_JA_LIST
                ,PART_FULL_ENG_LIST=const.PART_FULL_ENG_LIST
                )
        else:
            hopeShiftTime = HopeShiftTime.query.filter_by(hope_shift_id = hopeShift.id).first()
            if hopeShiftTime is not None:
                return render_template('userHome.html'
                    ,user=user
                    ,TARGET_DATE_STR=const.TARGET_DATE_STR
                    ,PART_FULL_JA_LIST=const.PART_FULL_JA_LIST
                    ,PART_FULL_ENG_LIST=const.PART_FULL_ENG_LIST
                    ,hopeShift=hopeShift
                    ,LAST_EDIT_LIST=const.LAST_EDIT_LIST
                    )
            # else: # 想定外のバグ（HopeShift.idはあるがHopeShiftTime.hope_shift_idにないIDがある状態）
            #     # hopeShiftのレコードの削除
            #     db.session.delete(hopeShift)
            #     db.session.commit()
            #     return redirect(url_for('userHome', userId=userId))

@app.route('/<int:userId>/user/create/<string:part_full>/hopeShift', methods=['GET', 'POST'])
def hopeShift(userId, part_full):
    if isAdminMethod():
        isAdmin = True
    else:
        isAdmin = False
        if not isMatchLoggedId(userId) or not isMatchFullOrPart(userId, part_full):
            session.clear()
            return redirect(url_for('userLogin'))

    if request.method == 'GET':
        # hopeDay、start、endのデフォルトリストを作成
        defaultHopeDayList, defaultStartList, defaultEndList = table2defaultHopeShiftList(userId, part_full)
        DAYS_OF_TARGET_MONTH_LIST = const.DAYS_OF_TARGET_MONTH_LIST

        if part_full == const.PART_FULL_ENG_LIST[0]:
            return render_template('hopeShiftPartTime.html'
                ,userId=userId
                ,isAdmin=isAdmin
                ,SMTWTFS=const.SMTWTFS
                ,DAY_STR_LIST=const.DAY_STR_LIST
                ,WORK_TIME_RADIO_NAME_LIST=const.WORK_TIME_RADIO_NAME_LIST
                ,DAYS_OF_TARGET_MONTH_LIST=DAYS_OF_TARGET_MONTH_LIST
                ,FIRST_SUNDAY_TARGET_MONTH=const.FIRST_SUNDAY_TARGET_MONTH
                ,PART_TIME_START_OPTION_LIST=const.PART_TIME_START_OPTION_LIST
                ,PART_TIME_END_OPTION_LIST=const.PART_TIME_END_OPTION_LIST
                ,PART_TIME_START_END_DEFAULT_LIST=const.PART_TIME_START_END_DEFAULT_LIST
                ,TARGET_YEAR_MONTH=const.TARGET_YEAR_MONTH
                ,defaultHopeDayList=defaultHopeDayList
                ,defaultStartList=defaultStartList
                ,defaultEndList=defaultEndList
                )

        elif part_full == const.PART_FULL_ENG_LIST[1]:
            print(defaultHopeDayList)
            return render_template('hopeShiftFullTime.html'
                ,userId=userId
                ,isAdmin=isAdmin
                ,SMTWTFS=const.SMTWTFS
                ,NUM_FIRST_WEEKDAY_OF_TARGET_MONTH=const.NUM_FIRST_WEEKDAY_OF_TARGET_MONTH
                ,SUM_BLOCKS_OF_CALENDAR=const.SUM_BLOCKS_OF_CALENDAR
                ,DAYS_OF_TARGET_MONTH_LIST=DAYS_OF_TARGET_MONTH_LIST
                ,FIRST_SUNDAY_TARGET_MONTH=const.FIRST_SUNDAY_TARGET_MONTH
                ,FULL_TIME_START_END_LIST=const.FULL_TIME_START_END_LIST
                ,TARGET_YEAR_MONTH=const.TARGET_YEAR_MONTH
                ,defaultHopeDayList=defaultHopeDayList
                )

    elif request.method == 'POST':
        hopeDayList, startList, endList = form2hopeShiftList(part_full)

        deleteHopeShiftId = getHopeShiftIdOfTarget(userId, const.TARGET_YEAR_MONTH)

        # 既存の対象レコードの削除
        if deleteHopeShiftId is not None:
            deleteHopeShiftOrCondition(deleteHopeShiftId, 'hopeShift')

        addHopeShiftAndHopeShiftTime(userId, isAdmin^1, hopeDayList, startList, endList)

        if isAdmin:
            flash('希望シフトの変更が完了しました', 'ok')
            return redirect(url_for('adminHome'))
        else:
            flash('希望シフトの提出が完了しました', 'ok')
            return redirect(url_for('userHome', userId=userId))

@app.route('/admin/home', methods=['GET', 'POST'])
def adminHome():
    if not isAdminMethod():
        session.clear()
        return redirect(url_for('adminLogin'))

    if request.method == 'GET':
        targetMonthArr = db.session.query(
            User, HopeShift)\
            .filter(or_(and_(HopeShift.target_year == const.TARGET_YEAR_MONTH[0]
            ,HopeShift.target_month == const.TARGET_YEAR_MONTH[1]), HopeShift.target_year == None))\
            .order_by(User.is_full_time.desc(), User.id)\
            .outerjoin(HopeShift, User.id == HopeShift.user_id)\
            .all()
        print(targetMonthArr)
        return render_template('adminHome.html'
            ,targetMonthArr=targetMonthArr
            ,LAST_EDIT_LIST=const.LAST_EDIT_LIST
            ,CURRENT_DATE_STR=const.CURRENT_DATE_STR
            ,TARGET_DATE_STR=const.TARGET_DATE_STR
            ,PART_FULL_JA_LIST=const.PART_FULL_JA_LIST
            ,PART_FULL_ENG_LIST=const.PART_FULL_ENG_LIST
            )

@app.route('/admin/delete/user/<int:userId>', methods=['GET', 'POST'])
def editUserTable():
    if request.method == 'GET':
        return render_template('editUserTable.html')
    elif request.method == 'POST':
        return redirect(url_for('adminHome'))

@app.route('/admin/create/shift', methods=['GET', 'POST'])
def createShift():
    if not isAdminMethod():
        session.clear()
        return redirect(url_for('adminLogin'))

    if request.method == 'GET':
        hopeShiftArr = db.session.query(
            User, HopeShift)\
            .filter(HopeShift.target_year == const.TARGET_YEAR_MONTH[0]
            ,HopeShift.target_month == const.TARGET_YEAR_MONTH[1])\
            .order_by(User.is_full_time.desc(), User.id)\
            .join(HopeShift, User.id == HopeShift.user_id)\
            .all()
        startEndListArr = []
        for user, _ in hopeShiftArr:
            userId = user.id
            part_full = const.PART_FULL_ENG_LIST[user.is_full_time]
            hopeDayList, startList, endList = table2defaultHopeShiftList(userId, part_full)
            startEndList = []
            for iDay, hopeDay in enumerate(hopeDayList):
                if hopeDay:
                    startEndList.append(f'{startList[iDay]}-{endList[iDay]}')
                else:
                    startEndList.append('-')
            startEndListArr.append(startEndList)
            print(startEndListArr)

        return render_template('createShift.html'
            ,hopeShiftArr=hopeShiftArr
            ,TARGET_YEAR_MONTH=const.TARGET_YEAR_MONTH
            ,PART_FULL_JA_LIST=const.PART_FULL_JA_LIST
            ,PART_FULL_ENG_LIST=const.PART_FULL_ENG_LIST
            ,startEndListArr=startEndListArr
            ,SUM_DAYS_OF_TARGET_MONTH=const.SUM_DAYS_OF_TARGET_MONTH
            ,TARGET_DATE_STR=const.TARGET_DATE_STR
            ,PART_TIME_START_OPTION_LIST=const.PART_TIME_START_OPTION_LIST
            ,PART_TIME_END_OPTION_LIST=const.PART_TIME_END_OPTION_LIST
            ,CONDITION_LIST = const.CONDITION_LIST
            ,EVENT_LIST = const.EVENT_LIST
            ,PARTID_START_END_LIST = const.PARTID_START_END_LIST
            )

@app.route('/admin/create/shift/addCondition', methods=['GET'])
def addCondition():
    if not isAdminMethod():
        session.clear()
        return redirect(url_for('adminLogin'))

    if request.method == 'GET':

        return redirect(url_for('createShift'))

@app.route('/admin/edit/user', methods=['GET', 'POST'])
def editUserInfo():
    if request.method == 'GET':
        userArr  = User.query.order_by(User.is_full_time.desc(), User.id).all()

@app.route('/logout')
def logout():
    if isAdminMethod():
        tryClearSession()
        return redirect(url_for('adminLogin'))
    else:
        tryClearSession()
        return redirect(url_for('userLogin'))
