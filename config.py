import datetime, calendar, math

def getNumWeekday(year,month,day):
    date = datetime.date(year, month, day)
    return (date.weekday()+1) % len(SMTWTFS)

def getDateOfNextMonth():
    dt_now = datetime.datetime.now()
    if dt_now.month != LAST_MONTH:
        year = dt_now.year
        month = dt_now.month + 1
    else:
        year = dt_now.year + 1
        month = 1
    return year, month

# -----------------------------------------------
# -----------------------------------------------
SECRET_KEY = 'a1f97b7b5e0fda68759b3ef515663cc8'
# -----------------------------------------------
# -----------------------------------------------

LAST_MONTH = 12
SMTWTFS = ['日', '月', '火', '水', '木', '金', '土']
FULL_TIME = [14, 26]
START_SELECT_LIST = [16, 17, 18]
END_SELECT_LIST = [22, 23, 24, 25, 26]
START_END_DEFAULT = [16, 26]

# 来月をターゲットとする
TARGET_YEAR, TARGET_MONTH  = getDateOfNextMonth()
HOPE_SHIFT_STR = f'提出済みの希望シフト（{TARGET_YEAR}年{TARGET_MONTH}月）'
SUM_DAYS_OF_TARGET_MONTH = calendar.monthrange(TARGET_YEAR, TARGET_MONTH)[1]
SELECT_DAYS_LIST = [f'selectDay{iDay+1}' for iDay in range(SUM_DAYS_OF_TARGET_MONTH)]
NUM_FIRST_WEEKDAY_OF_TARGET_MONTH = getNumWeekday(TARGET_YEAR, TARGET_MONTH, 1)
SUM_BLOCKS_OF_CALENDAR = math.ceil((SUM_DAYS_OF_TARGET_MONTH+NUM_FIRST_WEEKDAY_OF_TARGET_MONTH)/len(SMTWTFS)) * len(SMTWTFS)

WORK_TIME_RADIO_NAME_LIST = [f'{i}_{iDay+1}' for iDay in range(SUM_DAYS_OF_TARGET_MONTH) for i in ['start', 'end']]
DAY_LABEL_ID_LIST = [f'dayLabel_{iDay+1}' for iDay in range(SUM_DAYS_OF_TARGET_MONTH)]
HOPE_DAY_CHECK_BOX_NAME_LIST = [f'hopeDayCheckBox_{iDay+1}' for iDay in range(SUM_DAYS_OF_TARGET_MONTH)]
DAY_STR_LIST = [f'({SMTWTFS[getNumWeekday(TARGET_YEAR, TARGET_MONTH, iDay+1)]})' for iDay in range(SUM_DAYS_OF_TARGET_MONTH)] # 曜日のリスト
