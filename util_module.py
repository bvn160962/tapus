import datetime
import hashlib
import os
import logging
import sys
from uuid import uuid4

import glob_module
import settings

CLIENT_OS_SUPPORTED = ('Windows', 'iPad', 'iPhone')

IS_WINDOWS = (sys.platform == 'win32')
if IS_WINDOWS:
    LOG_DIR = 'c:\\tsh_home\\logs\\'
else:
    LOG_DIR = '/var/log/timesheets/'

LOG_FILE_NAME = LOG_DIR + 'app_server.log'
LOG_FILE_MODE = 'w'  # 'a' - append, 'w' - rewrite
LOG_FILE_LEVEL = logging.DEBUG

LOG_FILE_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
# LOG_FILE_FORMAT = '%(asctime)s %(funcName)s, line %(lineno)s: %(message)s'


# Убирает дублирование ip в url (http://193.168.46.78,193.168.46.78/api/test_session/user)
def normalize_url(url):
    pos_comma = url.find(',')
    if pos_comma == -1:
        return url

    pos_slash = url.find('/api')
    if pos_slash < pos_comma:
        return url

    return f'url={url[:pos_comma]}{url[pos_slash:]}'


def generate_uid():
    return str(uuid4().hex)


def parse_string(s_in, res):

    i_1 = s_in.find('(')
    i_2 = s_in.find(' ')
    if i_1 == -1 and i_2 == -1:
        res.append(s_in)
        # log_tmp(f'финиш: ({str(i_1)}:{str(i_2)}) - res: {res}')
        return res

    if -1 < i_1 < i_2:  # Позиция первой найденной скобки (
        i_2 = s_in.find(')')
        add = s_in[i_1 + 1: i_2]
        remains = s_in[i_2 + 1:]
        if add != '':
            # log_tmp(f'скобка: ({str(i_1)}:{str(i_2)}) - add: {add}; remains: "{remains}"')
            res.append(add)
        return parse_string(remains, res)
    else:  # Позиция первого найденного пробела
        add = s_in[:i_2]
        remains = s_in[i_2 + 1:]
        if add != '':
            # log_tmp(f'пробел: ({str(i_1)}:{str(i_2)}) - add: {add}; remains: "{remains}"')
            res.append(add)
        return parse_string(remains, res)


def parse_user_agent_header(request):
    ua_header = str(request.headers.get("User-Agent"))
    # log_debug(f'{ua_header}')
    return parse_string(ua_header, [])


def get_client_os_type(request):
    # Windows NT 10.0 | iPad | iPhone
    #
    return parse_user_agent_header(request)[1].split(';')[0]


# Для работы с паролями
#
def get_hash(s):
    sha256_hash = hashlib.new('sha256')
    sha256_hash.update(s.encode())
    return sha256_hash.hexdigest()


# Логирование
#
def log_info(msg):
    print(f'--{msg}')
    logger.info(msg)


def log_debug(msg):
    print(f'++{msg}')
    logger.debug(msg)


def log_error(msg):
    print(f'**{msg}')
    logger.error(msg)


def log_tmp(msg):
    print(f'=={msg}')
    logger.debug(msg)


# Вспомогательные функции
#
def get_week():
    return get_week_by_date(datetime.datetime.now())


# def get_date():
#     return datetime.datetime.now().date()


def get_week_by_date(date):

    year, i_week, day = date.isocalendar()
    s_week = f'{i_week:0{2}}'  # 1 -> 01, 12 -> 12
    out = str(year) + '-W' + s_week

    # log_debug(f'{year}, {week}, {w}, {out}')
    return out


# Количество недель в году
def weeks_for_year(year):
    last_week = datetime.date(year, 12, 28)
    return last_week.isocalendar().week


# Рабочий день?
def is_work_day(date):
    d = date.split('-')
    year = int(d[0])
    month = int(d[1])
    day = int(d[2])
    date_num = f'{datetime.date(year, month, day):%j}'  # Номер дня в году
    data = glob_module.get_all_days_for_year(year)  # Строка по всем дням в году: 0-рабочий, 1-выходной

    if data.find('1') == -1:  # Строка, состоящая из одних 0 - календарь еще не опубликован!
        return not is_week_end(date)  # Отображаются только субботы и воскресенья
    else:
        return data[int(date_num)-1] == '0'


# Суббота или воскресенье?
def is_week_end(date):
    d = date.split('-')
    dt = datetime.datetime(int(d[0]), int(d[1]), int(d[2]))
    return dt.weekday() in [5, 6]


def date_to_day(date):
    s_date = str(date).split('-')
    return f'{s_date[2]}.{s_date[1]}'


def list_dates_in_week(week):
    # Функция datetime.datetime.strptime(week+'-1', "%Y-W%W-%w").date()
    #   неправильно считает дату в ...2020, 2025... (если первая неделя года начинается с дней декабря)
    #   выдает дату - начало следующей недели!!!
    #   в таком году необходимо уменьшать на 1 номер недели !!!
    #
    # s_date = datetime.datetime.strptime(week+'-1', "%Y-W%W-%w").date()
    # date_str = s_date.isocalendar()
    # year_ = date_str[0]
    # week_ = date_str[1]
    # log_debug(f'week:{week}; s_date: {s_date}; date_str: {date_str}')
    #
    # Признак года, в котором 1-ая неделя начинается с декабря!
    # if (
    #         datetime.datetime.strptime(f'{year_}-1-1', "%Y-%W-%w") !=
    #         datetime.datetime.strptime(f'{year_}-0-1', "%Y-%W-%w")):
    #     if week_ > 1:
    #         week_ = week_ - 1
    # log_debug(f'week: {week_}')

    # Другой способ определения года и недели:
    w = week.split('-')
    year_ = int(w[0])
    week_ = int(w[1][1:])
    # log_debug(f'week:{week}; year_: {year_}; week_: {week_}')

    out = []
    for day in range(1, 8):
        date = datetime.datetime.fromisocalendar(year=year_, week=week_, day=day).date()
        out.append(str(date))

    return out


# Начальная и конечная даты в неделе
#
def get_dates_by_week(week):

    s_date = datetime.datetime.strptime(week + '-1', "%Y-W%W-%w").date()
    date_str = s_date.isocalendar()
    e_date = datetime.datetime.fromisocalendar(year=date_str[0], week=date_str[1], day=7).date()

    return s_date, e_date


def is_project_in_week(week, prj_range):
    week_range = get_dates_by_week(week)
    s_edge = False
    e_edge = False

    # Нижняя граница проекта
    if prj_range[0] is None:
        s_edge = True
    else:
        if prj_range[0] <= week_range[1]:
            s_edge = True

    # Верхняя граница проекта
    if prj_range[1] is None:
        e_edge = True
    else:
        if prj_range[1] >= week_range[0]:
            e_edge = True

    return s_edge and e_edge


# Возвращает следующую (next_week==True) или предыдущую неделю в формате '1985-W06'
def shift_week(week, next_week):
    s = week.split('-')
    # Год
    year = int(s[0])

    # Номер недели
    c_week = int(s[1][1:])  # Текущая неделя
    if next_week:
        last_week = weeks_for_year(year)  # Последняя неделя текущего года
        if c_week != last_week:
            week_ = c_week + 1
        else:  # Первая неделя следующего года
            week_ = 1
            year += 1
    else:
        if c_week != 1:
            week_ = int(s[1][1:]) - 1
        else:  # Последняя неделя предыдущего года
            year -= 1
            week_ = weeks_for_year(year)

    return f'{year}-W{week_:0{2}}'  # Формат '1985-W06'


# Создать лог папку если ее нет
if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)

# Инициализировать logger
logger = logging.getLogger(__name__)
logger.setLevel(level=LOG_FILE_LEVEL)

file_handler = logging.FileHandler(LOG_FILE_NAME, mode=LOG_FILE_MODE)
formatter = logging.Formatter(LOG_FILE_FORMAT)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
print(f'logger started: {logger}')


# Ограничение длины строки
#
def str_cutter(s, limit = settings.MAX_STR_LENGTH_FOR_NOTIFICATION):
    if len(s) > limit:
        s = f'{s[:limit - 3]}...'
    return s


# Формирование строки для кнопок из уведомления
#
def get_str_from_user_and_date(user, date):
    user = str_cutter(user, settings.MAX_STR_LENGTH_FOR_NOTIFICATION - len(str(date)) - 1)
    s = f'{user}{"  "*(settings.MAX_STR_LENGTH_FOR_NOTIFICATION - len(user) - len(str(date)) + 5)}{date}'
    return s


