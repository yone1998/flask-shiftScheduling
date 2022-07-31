import datetime

def getDateOfNextMonth():
    dt_now = datetime.datetime.now()
    if dt_now.month != LAST_MONTH:
        year = dt_now.year
        month = dt_now.month + 1
    else:
        year = dt_now.year + 1
        month = 1
    return [year, month]

LAST_MONTH = 12
SMTWTFS = ['日', '月', '火', '水', '木', '金', '土']
FULL_TIME = [14, 26]
START_SELECT_LIST = [16, 17, 18]
END_SELECT_LIST = [22, 23, 24, 25, 26]
START_END_DEFAULT = [16, 26]

NEXT_YEAR_MONTH = getDateOfNextMonth()