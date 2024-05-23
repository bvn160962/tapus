import util_module as util


# Глобальные переменные
#

# Счетчик текущих сессий
session_count = 0


def inc_session_count():
    global session_count
    session_count += 1
    # util.log_tmp(f'session_count+: {session_count}')


def dec_session_count():
    global session_count
    session_count -= 1
    # util.log_tmp(f'session_count-: {session_count}')


def get_session_count():
    global session_count
    # util.log_tmp(f'session_count: {session_count}')
    return session_count

