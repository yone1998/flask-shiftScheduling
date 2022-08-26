import datetime, calendar, math

def getNumWeekday(year_month,day):
    date = datetime.date(year_month[0], year_month[1], day)
    return (date.weekday()+1) % len(SMTWTFS)

def getFirstSunday(year_month):
    return len(SMTWTFS) - datetime.date(year_month[0], year_month[1], 1).weekday()

def getDateOfCurrentMonth():
    dt_now = datetime.datetime.now()
    return [dt_now.year, dt_now.month]

def getDateOfNextMonth():
    LAST_MONTH = 12

    dt_now = datetime.datetime.now()
    if dt_now.month != LAST_MONTH:
        year = dt_now.year
        month = dt_now.month + 1
    else:
        year = dt_now.year + 1
        month = 1
    return [year, month]


# ローカル環境用
SECRET_KEY = 'a1f97b7b5e0fda68759b3ef515663cc8'
AUTHENTICATION_CODE = 'a1f97b'

SMTWTFS = ['日', '月', '火', '水', '木', '金', '土']
FULL_TIME_START_END_LIST = [14, 26]
PART_TIME_START_OPTION_LIST = [16, 17, 18]
PART_TIME_END_OPTION_LIST = [22, 23, 24, 25, 26]
PART_TIME_START_END_DEFAULT_LIST = [16, 26]
PART_DEFAULT_LEVEL = 1 # 新規登録時に割り当てられる。実際のレベルの設定は管理者が行う
# レベル2は各日に1人以上必要なバイト
FULL_LEVEL = 3
ADMIN_ID = 0
LAST_EDIT_LIST = ['管理者', '本人']
PART_FULL_ENG_LIST = ['part', 'full']
PART_FULL_JA_LIST = ['バイト', '社員']
CONDITION_LIST = ['日付の種類', '社員 (人)', 'バイト (人)', 'ラスト (時)']
EVENT_LIST = ['平日', '金', '土', '日', '祝日', '祝前日']
PARTID_START_END_LIST = ['バイトID', '開始時間 (時)', '終了時間 (時)']

# Target is next month
CURRENT_YEAR_MONTH  = getDateOfCurrentMonth()
TARGET_YEAR_MONTH  = getDateOfNextMonth()
FIRST_SUNDAY_TARGET_MONTH = getFirstSunday(TARGET_YEAR_MONTH)
CURRENT_DATE_STR = f'（{CURRENT_YEAR_MONTH[0]}年{CURRENT_YEAR_MONTH[1]}月）'
TARGET_DATE_STR = f'（{TARGET_YEAR_MONTH[0]}年{TARGET_YEAR_MONTH[1]}月）'
SUM_DAYS_OF_TARGET_MONTH = calendar.monthrange(TARGET_YEAR_MONTH[0], TARGET_YEAR_MONTH[1])[1]
DAYS_OF_TARGET_MONTH_LIST = [iDay+1 for iDay in range(SUM_DAYS_OF_TARGET_MONTH)]
NUM_FIRST_WEEKDAY_OF_TARGET_MONTH = getNumWeekday(TARGET_YEAR_MONTH, 1)
SUM_BLOCKS_OF_CALENDAR = math.ceil((SUM_DAYS_OF_TARGET_MONTH+NUM_FIRST_WEEKDAY_OF_TARGET_MONTH)/len(SMTWTFS)) * len(SMTWTFS)
WORK_TIME_RADIO_NAME_LIST = [f'{iLabel}_{iDay}' for iDay in DAYS_OF_TARGET_MONTH_LIST for iLabel in ['start', 'end']]
DAY_STR_LIST = [f'({SMTWTFS[getNumWeekday(TARGET_YEAR_MONTH, iDay)]})' for iDay in DAYS_OF_TARGET_MONTH_LIST] # 曜日のリスト
