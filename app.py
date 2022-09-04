# -------------------------------------82-----------------------------------------
# 命名規則
# スネークケースが好きではないので、基本、キャメルケースで書いていますが、flask-SQLAlchemyのモデルの項目とテーブル名はスネークケースで書いています。
# flask-SQLAlchemyのモデルの項目はキャメルケースで書くと、自動的にスネークケースに変換されてしまうので、外部キー制約を行う際にバグの発生源になります。

# 問題
# ・保守後にデータベース内の登録をクリアにした際
# ユーザーのPCに保守前のセッション情報が残っていたらまずい

# ・css
# メッセージのスタイルが反映されない
# レスポンシブ対応
# BEMがわからん

# ・パスワード再設定
# mail API わからん

# ・csrf

# タスク
# ・データベース関係以外の定数をjsに移す

# ・フロントエンドとバックエンドの棲み分け
# Vueに任せて、jinja2は極力書かない
# カレンダーはVueで

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

import datetime, pytz, os
import numpy as np
# from tkinter import messagebox

from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail, Message
from flask_bootstrap import Bootstrap
# from flask_wtf.csrf import CSRFProtect

from itsdangerous import BadSignature, SignatureExpired
from itsdangerous.url_safe import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
# from google_auth_oauthlib.flow import InstalledAppFlow

import const

if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shift.db'
app.secret_key = os.environ['SECRET_KEY']
AUTHENTICATION_CODE = os.environ['AUTHENTICATION_CODE']
SALT = os.environ['SALT']

# app.config['DEBUG'] = True
# app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_DEBUG'] =
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = os.environ['MAIL_DEFAULT_SENDER']
# app.config['MAIL_MAX_EMAILS'] = None
# app.config['MAIL_SUPPRESS_SEND'] =
# app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)
# csrf = CSRFProtect(app)
db = SQLAlchemy(app, session_options={"autoflush": False})
admin = Admin(app)
bootstrap = Bootstrap(app)


class User(db.Model):
    __tabelname__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(5), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    is_full_time = db.Column(db.Boolean, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    hope_shift = db.relationship('HopeShift', backref='user')


class HopeShift(db.Model):
    __tabelname__ = 'hope_shift'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_year = db.Column(db.Integer, nullable=False)
    target_month = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.String(30), nullable=False)
    is_user_submission = db.Column(db.Boolean, nullable=False)
    hope_shift_time = db.relationship('HopeShiftTime', backref='hope_shift')


class HopeShiftTime(db.Model):
    __tabelname__ = 'hope_shift_time'
    id = db.Column(db.Integer, primary_key=True)
    hope_shift_id = db.Column(
        db.Integer,
        db.ForeignKey('hope_shift.id'),
        nullable=False
    )
    day = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)


class Condition(db.Model):
    __tabelname__ = 'condition'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.Integer, nullable=False)
    sum_full_time = db.Column(db.Integer, nullable=False)
    sum_part_time = db.Column(db.Integer, nullable=False)
    last = db.Column(db.Integer, nullable=False)
    condition_part_time = db.relationship(
        'ConditionPartTime',
        backref='condition'
    )


class ConditionPartTime(db.Model):
    __tabelname__ = 'condition_part_time'
    id = db.Column(db.Integer, primary_key=True)
    condition_id = db.Column(
        db.Integer,
        db.ForeignKey('condition.id'),
        nullable=False
    )
    part_id = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)


class SpecialDay(db.Model):
    __tabelname__ = 'special_day'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    event = db.Column(db.Integer, nullable=False)


# 最終的にはコメントアウトする
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(HopeShift, db.session))
admin.add_view(ModelView(HopeShiftTime, db.session))
admin.add_view(ModelView(Condition, db.session))
admin.add_view(ModelView(ConditionPartTime, db.session))
admin.add_view(ModelView(SpecialDay, db.session))

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


# 希望シフトのリスト化
def form2list(tableName, **arg):
    if tableName == 'hope_shift_time':
        part_full = arg['part_full']
        hopeDayList = []
        if part_full == const.PART_FULL_ENG_LIST[0]:
            startList = []
            endList = []
            for iDay in const.DAYS_OF_TARGET_MONTH_LIST:
                print(request.form.get(f'day{iDay}'))
                if request.form.get(f'day{iDay}'):
                    hopeDayList.append(iDay)
                    startList.append(int(request.form.get(f'start_{iDay}')))
                    endList.append(int(request.form.get(f'end_{iDay}')))
        if part_full == const.PART_FULL_ENG_LIST[1]:
            for iDay in const.DAYS_OF_TARGET_MONTH_LIST:
                print(request.form.get(f'day{iDay}'))
                if request.form.get(f'day{iDay}'):
                    hopeDayList.append(iDay)
            startList = [const.FULL_TIME_START_END_LIST[0]] * len(hopeDayList)
            endList = [const.FULL_TIME_START_END_LIST[1]] * len(hopeDayList)

        return hopeDayList, startList, endList

    if tableName == 'condition_part_time':
        sumPartTime = arg['sumPartTime']
        startList = []
        endList = []
        for iPart in range(sumPartTime):
            startList.append(int(request.form.get(f'partStart{iPart+1}')))
            endList.append(int(request.form.get(f'partEnd{iPart+1}')))

        # 早い順に並びかえ
        startEndList = np.vstack((
            np.array(startList),
            np.array(endList),
        )).transpose().tolist()
        startEndList = np.array(sorted(startEndList)).transpose().tolist()

        startList, endList = startEndList
        return startList, endList


# 対象レコードのIDを返す。なければNone
def getIdOfTargetRecord(tableName, **filter):
    if tableName == 'hope_shift':
        userId = filter['userId']
        targetYearMonth = filter['targetYearMonth']
        hopeShift = HopeShift.query.filter_by(
            user_id=userId,
            target_year=targetYearMonth[0],
            target_month=targetYearMonth[1],
        ).one_or_none()
        if hopeShift:
            return hopeShift.id
        else:
            return None

    elif tableName == 'condition':
        condition = Condition.query.filter_by(
            event=filter['event'],
            sum_full_time=filter['sumFullTime'],
        ).one_or_none()
        if condition:
            return condition.id
        else:
            return None

    elif tableName == 'special_day':
        specialDay = SpecialDay.query.filter_by(
            year=filter['year'],
            month=filter['month'],
            day=filter['day'],
        ).one_or_none()
        print('--------------')
        print(specialDay)
        if specialDay:
            return specialDay.id
        else:
            return None


def deleteRecords(target, deleteId):
    if target == 'hopeShift':
        hopeShift = HopeShift.query.filter_by(id=deleteId).one()
        db.session.delete(hopeShift)
        hopeShiftTimeArr = HopeShiftTime.query.filter_by(hope_shift_id=deleteId)
        for hopeShiftTime in hopeShiftTimeArr:
            db.session.delete(hopeShiftTime)
        db.session.commit()

    elif target == 'condition':
        condition = Condition.query.filter_by(id=deleteId).one()
        db.session.delete(condition)
        conditionPartTimeArr = ConditionPartTime.query.filter_by(
            condition_id=deleteId,
        )
        for conditionPartTime in conditionPartTimeArr:
            db.session.delete(conditionPartTime)
        db.session.commit()

    elif target == 'special_day':
        specialDay = SpecialDay.query.filter_by(id=deleteId).one()
        db.session.delete(specialDay)
        db.session.commit()

    elif target == 'user':
        user = User.query.filter_by(id=deleteId).one()
        db.session.delete(user)
        hopeShiftArr = HopeShift.query.filter_by(user_id=deleteId).all()
        for hopeShift in hopeShiftArr:
            hopeShiftTimeArr = HopeShiftTime.query.filter_by(
                hope_shift_id=hopeShift.id,
            ).all()
            db.session.delete(hopeShift)
            for hopeShiftTime in hopeShiftTimeArr:
                db.session.delete(hopeShiftTime)

        db.session.commit()


def createRecords(target, **arg):
    if target == 'hopeShift':
        userId = arg['userId']
        isUserSubmission = arg['isUserSubmission']
        hopeDayList = arg['hopeDayList']
        startList = arg['startList']
        endList = arg['endList']

        # hopeShiftレコードの追加
        created_at = str(
            datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        ).split(".")[0]
        addHopeShift = HopeShift(
            user_id=userId,
            target_year=const.TARGET_YEAR_MONTH[0],
            target_month=const.TARGET_YEAR_MONTH[1],
            created_at=created_at,
            is_user_submission=isUserSubmission,
        )
        db.session.add(addHopeShift)
        db.session.commit()
        hopeShift = HopeShift.query.filter_by(
            user_id=userId,
            target_year=const.TARGET_YEAR_MONTH[0],
            target_month=const.TARGET_YEAR_MONTH[1],
        ).one()
        addHopeShiftId = hopeShift.id
        print('add HopeShift record')

        # hopeShiftTimeレコードの追加
        for iDay in range(len(hopeDayList)):
            addHopeShiftTime = HopeShiftTime(
                hope_shift_id=addHopeShiftId,
                day=hopeDayList[iDay],
                start=startList[iDay],
                end=endList[iDay],
            )
            db.session.add(addHopeShiftTime)
            db.session.commit()
            print(
                hopeDayList[iDay],
                startList[iDay],
                endList[iDay],
                'addHopeShiftTime',
            )

    elif target == 'condition':
        event = arg['event']
        sumFullTime = arg['sumFullTime']
        sumPartTime = arg['sumPartTime']
        startList = arg['startList']
        endList = arg['endList']

        # conditionレコードの追加
        addCondition = Condition(
            event=event,
            sum_full_time=sumFullTime,
            sum_part_time=sumPartTime,
            last=max(endList),
        )
        db.session.add(addCondition)
        db.session.commit()
        condition = Condition.query.filter_by(
            event=event,
            sum_full_time=sumFullTime,
        ).one()
        addConditionId = condition.id
        print('add Condition record')

        # conditionPartTimeレコードの追加
        for iPart in range(len(startList)):
            addConditionPartTime = ConditionPartTime(
                condition_id=addConditionId,
                part_id=iPart+1,
                start=startList[iPart],
                end=endList[iPart],
            )
            db.session.add(addConditionPartTime)
            db.session.commit()
            print(iPart+1, startList[iPart], endList[iPart], 'addHopeShiftTime')

    elif target == 'special_day':
        specialDay = SpecialDay(
            year=arg['year'],
            month=arg['month'],
            day=arg['day'],
            event=arg['event'],
        )
        db.session.add(specialDay)
        db.session.commit()
        print('add SpecialDay record')


def isRecentHopeShiftRecords(userId):
    hopeShift = HopeShift.query.filter_by(
        user_id=userId,
        target_year=const.TARGET_YEAR_MONTH[0],
        target_month=const.TARGET_YEAR_MONTH[1],
    ).filter_by(
        user_id=userId,
        target_year=const.CURRENT_YEAR_MONTH[0],
        target_month=const.CURRENT_YEAR_MONTH[1],
    ).all()
    return hopeShift is not None


def table2defaultHopeShiftList(userId, part_full):
    PART_FULL_ENG_LIST = const.PART_FULL_ENG_LIST
    DAYS_OF_TARGET_MONTH_LIST = const.DAYS_OF_TARGET_MONTH_LIST
    PART_TIME_START_END_DEFAULT_LIST = const.PART_TIME_START_END_DEFAULT_LIST
    FULL_TIME_START_END_LIST = const.FULL_TIME_START_END_LIST

    # 初期値
    if part_full == PART_FULL_ENG_LIST[0]:
        defaultStartList = [PART_TIME_START_END_DEFAULT_LIST[0]] \
            * len(DAYS_OF_TARGET_MONTH_LIST)
        defaultEndList = [PART_TIME_START_END_DEFAULT_LIST[1]] \
            * len(DAYS_OF_TARGET_MONTH_LIST)
    elif part_full == PART_FULL_ENG_LIST[1]:
        defaultStartList = [FULL_TIME_START_END_LIST[0]] \
            * len(DAYS_OF_TARGET_MONTH_LIST)
        defaultEndList = [FULL_TIME_START_END_LIST[1]] \
            * len(DAYS_OF_TARGET_MONTH_LIST)

    hopeShiftId = getIdOfTargetRecord(
        'hope_shift',
        userId=userId,
        targetYearMonth=const.TARGET_YEAR_MONTH,
    )
    if hopeShiftId:
        defaultIsHopeDayList = [False]*len(DAYS_OF_TARGET_MONTH_LIST)
        hopeShiftTimeArr = HopeShiftTime.query.filter_by(
            hope_shift_id=hopeShiftId
        ).order_by(HopeShiftTime.day).all()
        for hopeShiftTime in hopeShiftTimeArr:
            defaultIsHopeDayList[hopeShiftTime.day-1] = True
            defaultStartList[hopeShiftTime.day-1] = hopeShiftTime.start
            defaultEndList[hopeShiftTime.day-1] = hopeShiftTime.end
    else:
        defaultIsHopeDayList = [True]*len(DAYS_OF_TARGET_MONTH_LIST)

    return defaultIsHopeDayList, defaultStartList, defaultEndList


def binaryHopeShiftList(defaultStartList, defaultEndList):
    PART_TIME_START_OPTION_LIST = const.PART_TIME_START_OPTION_LIST
    PART_TIME_END_OPTION_LIST = const.PART_TIME_END_OPTION_LIST

    defaultIsStartList = [
        [False] * len(PART_TIME_START_OPTION_LIST)
        for _ in range(len(defaultStartList))
    ]
    defaultIsEndList = [
        [False] * len(PART_TIME_END_OPTION_LIST)
        for _ in range(len(defaultEndList))
    ]
    for iDay in range(len(defaultStartList)):
        defaultIsStartList[iDay][PART_TIME_START_OPTION_LIST.index(
            defaultStartList[iDay]
        )] = True
        defaultIsEndList[iDay][PART_TIME_END_OPTION_LIST.index(
            defaultEndList[iDay]
        )] = True

    return defaultIsStartList, defaultIsEndList


def create_token(user_id, secret_key, salt):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(user_id, salt=salt)


def isTokenOk(token, secret_key, salt):
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        tmp = serializer.loads(
            token,
            salt=salt,
            return_timestamp=True,
            max_age=const.MAX_AGE,
        )
    except (BadSignature, SignatureExpired):
        return False

    return True


def loadToken(token, secret_key, salt):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.loads(
        token,
        salt=salt,
        return_timestamp=True,
        max_age=const.MAX_AGE,
    )


def tokenError(token, secret_key, salt):
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        tmp = serializer.loads(
            token,
            salt=salt,
            return_timestamp=True,
            max_age=const.MAX_AGE,
        )
    except SignatureExpired:
        errorType = 'SignatureExpired'
    except BadSignature:
        errorType = 'BadSignature'

    return errorType


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
        return render_template(
            'signup.html',
            PART_FULL_JA_LIST=const.PART_FULL_JA_LIST
        )

    elif request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        # passwordCheck = request.form.get('passwordCheck')
        isFullTime = request.form.get('isFullTime')
        print('name')
        print(name)
        print('email')
        print(email)

        user = User.query.filter_by(email=email).one_or_none()
        if user is None:
            if int(isFullTime) == 1:
                level = const.FULL_LEVEL
            elif int(isFullTime) == 0:
                level = const.PART_DEFAULT_LEVEL

            # Userテーブルに新規登録
            user = User(
                name=name,
                email=email,
                password=generate_password_hash(
                    password,
                    method='sha256'
                ),
                is_full_time=bool(int(isFullTime)),
                level=level,
            )
            db.session.add(user)
            db.session.commit()

            # session情報にログインしているユーザーのIDを登録
            user = User.query.filter_by(email=email).one()
            userId = user.id
            print('get', userId)
            session.permanent = True
            session["loggedId"] = userId
            flash('新規登録が完了しました', 'ok')
            return redirect(url_for('userHome', userId=userId))
        else:
            flash('既に使われているユーザーIDです', 'no')
            flash(
                '登録済みの場合は、ログインページからログインしてください',
                'no',
            )
            return render_template(
                'signup.html',
                PART_FULL_JA_LIST=const.PART_FULL_JA_LIST,
            )


@app.route('/userLogin', methods=['GET', 'POST'])
def userLogin():
    tryClearSession()

    if request.method == 'GET':
        return render_template('userLogin.html')

    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print('password')
        print(len(password) == 0)

        if len(email) * len(password) == 0:
            isOK = False
            flash('入力もれがあります', 'no')
        else:
            user = User.query.filter_by(email=email).one_or_none()
            if not user or not check_password_hash(user.password, password):
                isOK = False
                flash('ユーザーIDまたはパスワードが正しくありません', 'no')
                flash(
                    'はじめての利用の場合は、新規登録ページから新規登録してください',
                    'no',
                )
            else:
                isOK = True
                userId = user.id
                session.permanent = True
                session["loggedId"] = userId

        if isOK:
            return redirect(url_for('userHome', userId=userId))
        elif not isOK:
            return render_template('userLogin.html')


@app.route('/<int:userId>/user/home', methods=['GET', 'POST'])
def userHome(userId):
    if not isMatchLoggedId(userId):
        session.clear()
        return redirect(url_for('userLogin'))

    if request.method == 'GET':
        user = User.query.filter_by(id=userId).one()
        hopeShift = HopeShift.query.filter_by(
            user_id=userId,
            target_year=const.TARGET_YEAR_MONTH[0],
            target_month=const.TARGET_YEAR_MONTH[1],
        ).one_or_none()
        print(hopeShift)

        if hopeShift is None:
            return render_template(
                'userHome.html',
                user=user,
                TARGET_DATE_STR=const.TARGET_DATE_STR,
                PART_FULL_JA_LIST=const.PART_FULL_JA_LIST,
                PART_FULL_ENG_LIST=const.PART_FULL_ENG_LIST,
            )
        else:
            hopeShiftTime = HopeShiftTime.query.filter_by(
                hope_shift_id=hopeShift.id,
            ).first()
            if hopeShiftTime is not None:
                return render_template(
                    'userHome.html',
                    user=user,
                    TARGET_DATE_STR=const.TARGET_DATE_STR,
                    PART_FULL_JA_LIST=const.PART_FULL_JA_LIST,
                    PART_FULL_ENG_LIST=const.PART_FULL_ENG_LIST,
                    hopeShift=hopeShift,
                    LAST_EDIT_LIST=const.LAST_EDIT_LIST,
                )


@app.route(
    '/<int:userId>/user/create/<string:part_full>/hopeShift',
    methods=['GET', 'POST']
)
def hopeShift(userId, part_full):
    if isAdminMethod():
        isAdmin = True
    else:
        isAdmin = False
        if not isMatchLoggedId(userId) \
                or not isMatchFullOrPart(userId, part_full):
            session.clear()
            return redirect(url_for('userLogin'))

    if request.method == 'GET':
        PART_FULL_ENG_LIST = const.PART_FULL_ENG_LIST
        DAYS_OF_TARGET_MONTH_LIST = const.DAYS_OF_TARGET_MONTH_LIST

        # hopeDay、start、endのデフォルトリストを作成
        defaultIsHopeDayList, defaultStartList, defaultEndList = \
            table2defaultHopeShiftList(userId, part_full)
        if part_full == PART_FULL_ENG_LIST[0]:
            defaultIsStartList, defaultIsEndList = binaryHopeShiftList(
                defaultStartList,
                defaultEndList,
            )

        if part_full == PART_FULL_ENG_LIST[0]:
            return render_template(
                'hopeShiftPartTime.html',
                userId=userId,
                isAdmin=isAdmin,
                DAY_STR_LIST=const.DAY_STR_LIST,
                WORK_TIME_RADIO_NAME_LIST=const.WORK_TIME_RADIO_NAME_LIST,
                DAYS_OF_TARGET_MONTH_LIST=DAYS_OF_TARGET_MONTH_LIST,
                FIRST_SUNDAY_TARGET_MONTH=const.FIRST_SUNDAY_TARGET_MONTH,
                PART_TIME_START_OPTION_LIST=const.PART_TIME_START_OPTION_LIST,
                PART_TIME_END_OPTION_LIST=const.PART_TIME_END_OPTION_LIST,
                PART_TIME_START_END_DEFAULT_LIST=const.PART_TIME_START_END_DEFAULT_LIST,
                TARGET_YEAR_MONTH=const.TARGET_YEAR_MONTH,
                defaultIsHopeDayList=defaultIsHopeDayList,
                defaultIsStartList=defaultIsStartList,
                defaultIsEndList=defaultIsEndList,
            )

        elif part_full == PART_FULL_ENG_LIST[1]:
            print(defaultIsHopeDayList)
            return render_template(
                'hopeShiftFullTime.html',
                userId=userId,
                isAdmin=isAdmin,
                SMTWTFS=const.SMTWTFS,
                NUM_FIRST_WEEKDAY_OF_TARGET_MONTH=const.NUM_FIRST_WEEKDAY_OF_TARGET_MONTH,
                SUM_BLOCKS_OF_CALENDAR=const.SUM_BLOCKS_OF_CALENDAR,
                DAYS_OF_TARGET_MONTH_LIST=DAYS_OF_TARGET_MONTH_LIST,
                FIRST_SUNDAY_TARGET_MONTH=const.FIRST_SUNDAY_TARGET_MONTH,
                FULL_TIME_START_END_LIST=const.FULL_TIME_START_END_LIST,
                TARGET_YEAR_MONTH=const.TARGET_YEAR_MONTH,
                defaultIsHopeDayList=defaultIsHopeDayList,
            )

    elif request.method == 'POST':
        hopeDayList, startList, endList = form2list(
            'hope_shift_time',
            part_full=part_full,
        )

        deleteHopeShiftId = getIdOfTargetRecord(
            'hope_shift',
            userId=userId,
            targetYearMonth=const.TARGET_YEAR_MONTH,
        )

        if deleteHopeShiftId is not None:
            deleteRecords('hopeShift', deleteHopeShiftId)

        createRecords(
            'hopeShift',
            userId=userId,
            isUserSubmission=isAdmin ^ 1,
            hopeDayList=hopeDayList,
            startList=startList,
            endList=endList,
        )

        if isAdmin:
            flash('希望シフトの変更が完了しました', 'ok')
            return redirect(url_for('adminHome'))
        else:
            flash('希望シフトの提出が完了しました', 'ok')
            return redirect(url_for('userHome', userId=userId))


@app.route('/adminLogin', methods=['GET', 'POST'])
def adminLogin():
    tryClearSession()

    if request.method == 'GET':
        messageDictList = []
        return render_template('adminLogin.html', messageDictList=messageDictList)

    elif request.method == 'POST':
        authenticationCode = request.form.get('authenticationCode')
        if authenticationCode == AUTHENTICATION_CODE:
            session.permanent = True
            session["loggedId"] = const.ADMIN_ID
            return redirect(url_for('adminHome'))

        else:
            print(authenticationCode)
            messageDictList = [
                {
                    'id': 'authenticationCode',
                    'isOk': False,
                    'message': '認証コードが間違っています',
                }
            ]
            return render_template(
                'adminLogin.html',
                messageDictList=messageDictList,
            )


@app.route('/admin/home', methods=['GET', 'POST'])
def adminHome():
    if not isAdminMethod():
        session.clear()
        return redirect(url_for('adminLogin'))

    messageDictList = []
    crud = request.args.get('crud')
    section = request.args.get('section')
    print(section)
    print('====')
    if crud:
        if (section == 'user') & (crud == 'delete'):
            userId = int(request.args.get('userId'))
            if isRecentHopeShiftRecords(userId):
                messageDictList = [
                    {
                        'id': 'user',
                        'isOk': False,
                        'message': '今月または来月の希望シフトがあるユーザーは削除できません',
                    }
                ]
            else:
                deleteRecords('user', userId)

    userArr = User.query\
        .order_by(User.is_full_time.desc(), User.level, User.id).all()
    targetMonthArr = db.session.query(
        User,
        HopeShift,
    ).filter(
        or_(
            and_(
                HopeShift.target_year == const.TARGET_YEAR_MONTH[0],
                HopeShift.target_month == const.TARGET_YEAR_MONTH[1]
            ),
            not HopeShift.target_year
        )
    ).order_by(
        User.is_full_time.desc(),
        User.level,
        User.id,
    ).outerjoin(
        HopeShift, User.id == HopeShift.user_id,
    ).all()
    print(targetMonthArr)

    conditionArr = Condition.query.order_by(
        Condition.event,
        Condition.sum_full_time,
    ).all()
    conditionPartTimeArr = db.session.query(
        Condition,
        ConditionPartTime,
    ).order_by(
        Condition.event,
        Condition.sum_full_time,
        ConditionPartTime.part_id,
        ConditionPartTime.start,
        ConditionPartTime.end,
    ).join(
        Condition, Condition.id == ConditionPartTime.condition_id,
    ).all()

    return render_template(
        'adminHome.html',
        messageDictList=messageDictList,
        userArr=userArr,
        targetMonthArr=targetMonthArr,
        conditionArr=conditionArr,
        conditionPartTimeArr=conditionPartTimeArr,
        LAST_EDIT_LIST=const.LAST_EDIT_LIST,
        CURRENT_DATE_STR=const.CURRENT_DATE_STR,
        TARGET_DATE_STR=const.TARGET_DATE_STR,
        PART_FULL_JA_LIST=const.PART_FULL_JA_LIST,
        PART_FULL_ENG_LIST=const.PART_FULL_ENG_LIST,
        PART_TIME_START_OPTION_LIST=const.PART_TIME_START_OPTION_LIST,
        PART_TIME_END_OPTION_LIST=const.PART_TIME_END_OPTION_LIST,
        CONDITION_LIST=const.CONDITION_LIST,
        EVENT_LIST=const.EVENT_LIST,
        PARTID_START_END_LIST=const.PARTID_START_END_LIST,
    )


@app.route('/admin/create/shift', methods=['GET', 'POST'])
def createShift():
    if not isAdminMethod():
        session.clear()
        return redirect(url_for('adminLogin'))

    if request.method == 'GET':
        hopeShiftArr = db.session.query(
            User,
            HopeShift,
        ).filter(
            HopeShift.target_year == const.TARGET_YEAR_MONTH[0],
            HopeShift.target_month == const.TARGET_YEAR_MONTH[1],
        ).order_by(
            User.is_full_time.desc(), User.level, User.id,
        ).join(
            HopeShift, User.id == HopeShift.user_id,
        ).all()
        startEndListArr = []
        for user, _ in hopeShiftArr:
            userId = user.id
            part_full = const.PART_FULL_ENG_LIST[user.is_full_time]
            isHopeDayList, startList, endList = table2defaultHopeShiftList(
                userId,
                part_full,
            )
            startEndList = []
            for iDay, hopeDay in enumerate(isHopeDayList):
                if hopeDay:
                    startEndList.append(f'{startList[iDay]}-{endList[iDay]}')
                else:
                    startEndList.append('-')
            startEndListArr.append(startEndList)
            print(startEndListArr)

        specialDayArr = SpecialDay.query.filter_by(
            year=const.TARGET_YEAR_MONTH[0],
            month=const.TARGET_YEAR_MONTH[1],
        ).order_by(
            SpecialDay.day,
        ).all()

        return render_template(
            'createShift.html',
            hopeShiftArr=hopeShiftArr,
            specialDayArr=specialDayArr,
            TARGET_YEAR_MONTH=const.TARGET_YEAR_MONTH,
            PART_FULL_JA_LIST=const.PART_FULL_JA_LIST,
            PART_FULL_ENG_LIST=const.PART_FULL_ENG_LIST,
            startEndListArr=startEndListArr,
            CONDITION_LIST=const.CONDITION_LIST,
            SUM_DAYS_OF_TARGET_MONTH=const.SUM_DAYS_OF_TARGET_MONTH,
            TARGET_DATE_STR=const.TARGET_DATE_STR,
            EVENT_LIST=const.EVENT_LIST,
        )


@app.route('/admin/create/condition', methods=['POST'])
def createCondition():
    if not isAdminMethod():
        session.clear()
        return redirect(url_for('adminLogin'))

    if request.method == 'POST':
        print(request.form.get('event'))
        print(request.form.get('sumFullTime'))
        print(request.form.get('sumPartTime'))
        event = int(request.form.get('event'))
        sumFullTime = int(request.form.get('sumFullTime'))
        sumPartTime = int(request.form.get('sumPartTime'))
        startList, endList = form2list(
            'condition_part_time',
            sumPartTime=sumPartTime,
        )

        deleteConditionId = getIdOfTargetRecord(
            'condition',
            event=event,
            sumFullTime=sumFullTime,
        )

        if deleteConditionId is not None:
            deleteRecords('condition', deleteConditionId)

        createRecords(
            'condition',
            event=event,
            sumFullTime=sumFullTime,
            sumPartTime=sumPartTime,
            startList=startList,
            endList=endList,
        )

        return redirect(url_for('adminHome'))


@app.route('/admin/create/specialDay', methods=['POST'])
def createSpecialDay():
    if not isAdminMethod():
        session.clear()
        return redirect(url_for('adminLogin'))

    if request.method == 'POST':
        year = const.TARGET_YEAR_MONTH[0]
        month = const.TARGET_YEAR_MONTH[1]
        day = int(request.form.get('day'))
        event = int(request.form.get('event'))

        deleteSpecialDayId = getIdOfTargetRecord(
            'special_day',
            year=year,
            month=month,
            day=day,
        )
        print(deleteSpecialDayId)

        if deleteSpecialDayId is not None:
            deleteRecords('special_day', deleteSpecialDayId)

        createRecords(
            'special_day',
            year=year,
            month=month,
            day=day,
            event=event,
        )

        return redirect(url_for('createShift'))


@app.route('/admin/switch/userLevel/<int:userId>', methods=['GET', 'POST'])
def switchUserLevel(userId):
    if not isAdminMethod():
        session.clear()
        return redirect(url_for('adminLogin'))

    if request.method == 'GET':
        user = User.query.filter_by(id=userId).one()
        if user.level == 1:
            user.level = 2
        elif user.level == 2:
            user.level = 1
        db.session.commit()
        return redirect(url_for('adminHome'))


@app.route('/admin/delete/user/<int:userId>', methods=['GET', 'POST'])
def deleteUser(userId):
    if request.method == 'GET':
        if isRecentHopeShiftRecords(userId):
            flash(
                '今月または来月の希望シフトがあるユーザーは削除できません',
                'no',
            )
            deleteRecords('user', userId)
        return redirect(url_for('adminHome'))


@app.route('/admin/delete/userHopeShift/<int:userId>', methods=['GET', 'POST'])
def deleteUserHopeShift():
    if request.method == 'GET':
        return render_template('editUserTable.html')
    elif request.method == 'POST':
        return redirect(url_for('adminHome'))


@app.route('/admin/delete/condition/<int:conditionId>', methods=['GET'])
def deleteCondition(conditionId):
    if not isAdminMethod():
        session.clear()
        return redirect(url_for('adminLogin'))

    if request.method == 'GET':
        deleteRecords('condition', conditionId)
        return redirect(url_for('createShift'))


@app.route('/logout')
def logout():
    if isAdminMethod():
        tryClearSession()
        return redirect(url_for('adminLogin'))
    else:
        tryClearSession()
        return redirect(url_for('userLogin'))


@app.route('/sendResetPasswordUrl', methods=['GET', 'POST'])
def sendResetPasswordUrl():
    if request.method == 'GET':
        return render_template('sendResetPasswordUrl.html')

    elif request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).one_or_none()

        if user is not None:
            print(user.id)
            token = create_token(user.id, app.secret_key, SALT)
            url = url_for('resetPassword', token=token, _external=True)

            msg = Message(
                'パスワード再設定のお知らせ',
                sender='shoichitwitterapi@gmail.com',
                recipients=[user.email],
            )
            msg.body = f'{user.name} 様\nパスワード再設定のご依頼を受け付けました。\n\n以下より再設定することが出来ます。\n※ 再設定用URLの期限は60分です。\n{url}'
            mail.send(msg)
            flash(
                '入力されたメールアドレスにパスワード再設定用URLを送信しました',
                'ok',
            )
        else:
            flash('登録されていないメールアドレスです', 'no')

        return redirect(url_for('sendResetPasswordUrl'))


@app.route('/resetPassword?token=<token>', methods=['GET', 'POST'])
def resetPassword(token):
    if request.method == 'GET':
        return render_template('resetPassword.html')
    if request.method == 'POST':
        password = request.form.get('password')
        if isTokenOk(token, app.secret_key, SALT):
            userId, time = loadToken(token, app.secret_key, SALT)
            user = User.query.filter_by(id=userId).one()
            user.password = generate_password_hash(password, method='sha256')
            db.session.commit()

            session.permanent = True
            session["loggedId"] = userId
            flash('パスワード再設定が完了しました', 'ok')

            return redirect(url_for('userHome', userId=userId))

        else:
            errorType = tokenError(token, app.secret_key, SALT)
            if errorType == 'SignatureExpired':
                flash('このトークンは期限切れです', 'no')
            elif errorType == 'BadSignature':
                flash('トークンが正しくありません', 'no')

            return render_template('resetPassword.html')
