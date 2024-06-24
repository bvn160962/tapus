#
# Счетчик активных сессий через socket: connect/disconnect
# Работает правильно!!!
import util_module

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

