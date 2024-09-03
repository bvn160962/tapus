import requests
import util_module

#
# Счетчик активных сессий через socket: connect/disconnect
# Работает правильно!!!

sess_cnt = 1


def inc_sess_cnt():
    global sess_cnt
    sess_cnt += 1


def dec_sess_cnt():
    global sess_cnt
    sess_cnt -= 1


def get_sess_cnt():
    global sess_cnt
    return sess_cnt


#
# Счетчик активных сессий через login/logout
# Сбивается, если закрывать окно через x!!!
session_count = 0


def inc_session_count():
    global session_count
    session_count += 1


def dec_session_count():
    global session_count
    session_count -= 1


def get_session_count():
    global session_count
    return session_count


# Список активных сессий
#
session_list = {}


def get_session_list():
    return session_list


def remove_user_from_session_list(user_name):
    try:
        session_list.pop(user_name)
    except Exception as ex:
        util_module.log_error(f'remove_user_from_session_list: {ex}')


def get_sid_by_user(user_name):
    try:
        return session_list[user_name]['sid']
    except Exception as ex:
        util_module.log_error(f'get_sid_by_user: {ex}')
        return ''


#
# Массивы по годам для определения праздничных дней
workdays_by_years = {}


# Получить список рабочих/выходных дней за год
# строка из 366 0 и 1, где 0 - рабочий день, 1 - праздничный или выходной
def get_all_days_for_year(year):
    year_array = workdays_by_years.get(year)
    if year_array is None:  # Сформировать массив за год
        # util_module.log_tmp(f'year_array.get: {year}')
        # requests.get(f'https://isdayoff.ru/api/getdata?year={year}&month={month}&day={day}').json()
        year_array = requests.get(f'https://isdayoff.ru/api/getdata?year={year}').text
        workdays_by_years[year] = year_array
        if year_array.find('1') == -1:  # Строка, состоящая из одних 0 - календарь еще не опубликован!
            util_module.log_info(f'Для выбранного года {year} рабочий календарь еще не опубликован.')

    return year_array

