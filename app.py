import os
import time
import traceback
import datetime

from flask import Flask, request, redirect, url_for, session, make_response, render_template
from flask_socketio import SocketIO, send, emit

import data_module
import glob_module
import ui_module
import settings
import util_module as util
import app_module as apm


application = Flask(__name__)
application.secret_key = os.urandom(32)  # для принудительного сброса всех сессий при перезагрузке приложения
application.permanent = settings.S_PERMANENT

if settings.S_PERMANENT:
    application.permanent_session_lifetime = datetime.timedelta(minutes=settings.S_LIFETIME_IN_MINUTES)

socketio = SocketIO(application)

cnt_sessions = 0

send_message_ok = False


def check_authorization(req):
    if not settings.API_USE_AUTHORIZATION:
        return ''

    err_message = 'Авторизация не прошла'
    token = req.headers.get(settings.API_AUTHORIZATION_HEADER)
    if token is None:
        util.log_error(f'Не задан заголовок {settings.API_AUTHORIZATION_HEADER}')
        return err_message

    if token != settings.API_AUTHORIZATION_TOKEN:
        util.log_error(f'Недостоверный токен')
        return err_message
    else:
        return ''


def get_sessions_count():
    # global cnt_sessions
    # return cnt_sessions
    return glob_module.get_sess_cnt()


def get_sid_by_user(user_name):
    data = glob_module.get_session_list().get(user_name)
    if data is None:
        return ''
    else:
        return data.get('sid')


def send_message(msg, user='', msg_type='message'):
    global socketio

    if user == '':  # Всем пользователям
        util.log_debug(f'send_message to all sessions')
        socketio.emit(msg_type, msg)
    else:
        sid = get_sid_by_user(user)
        if sid != '':
            util.log_debug(f'send_message to: {user}; {sid}')
            socketio.emit(msg_type, msg, to=sid)


@socketio.on_error()
def error_handler(ex):
    util.log_error(f'Error on SocketIO: {ex}')


# Connect происходит каждый раз после обновления страницы (любым способом) и после успешного логина
#
@socketio.on('connect')
def connect():
    # global cnt_sessions
    # cnt_sessions += 1
    # util.log_tmp(f'cnt_sessions={cnt_sessions}')

    user_name = get_c_prop(settings.C_USER_NAME)

    # Добавить sid в словарь сессий
    sid = request.sid
    env = request.environ.get('werkzeug.socket')
    ip = apm.get_client_ip(request)
    if user_name == '':  # Для сессий без кэша - как правило, остаются после перезагрузки сервера
        user_name = f'hng-{util.generate_uid()}'

    glob_module.get_session_list()[user_name] = {'sid': sid, 'ip': ip}
    util.log_debug(f'add session for user: {user_name}; sid: {sid}; env: {env}')

    # Увеличить счетчик сессий
    glob_module.inc_sess_cnt()
    # util.log_debug(f'do connect: {glob_module.get_session_list()}')


# Disconnect происходит каждый раз перед обновлением страницы (любым способом) и при закрытии закладки браузера
#
@socketio.on('disconnect')
def disconnect():
    # global cnt_sessions
    # cnt_sessions -= 1
    # util.log_tmp(f'cnt_sessions={cnt_sessions}')

    # Удалить sid из словаря сессий
    sess_list = glob_module.get_session_list()

    # Поиск user_name по sid текущей сессии и очистка ключа 'sid'
    for sess in sess_list:
        if sess_list[sess].get('sid') == request.sid:
            sess_list[sess]['sid'] = ''
            util.log_debug(f'close session for user: {sess}')

    # Уменьшить счетчик сессий
    glob_module.dec_sess_cnt()
    # util.log_debug(f'disconnect, cnt_sessions={glob_module.get_sess_cnt()}')


# Обработчик сообщения <message> от клиента
@socketio.on('message')
def message(data):
    emit('message', data)
    # util.log_tmp(f'message: {data}; {glob_module.get_sess_cnt()}')


# Обработчик сообщения <test_ok> от клиента
@socketio.on('test_ok')
def test_ok(data):
    global send_message_ok
    send_message_ok = True
    # util.log_tmp(f'test_ok: {data}; {send_message_ok}')


# Поверка существования сессии Socket
def test_session(user):
    global send_message_ok
    send_message_ok = False

    send_message('test_session', user, 'test')
    time.sleep(settings.SOCKET_TEST_TIMEOUT)

    # util.log_debug(f'{user}: {send_message_ok}')
    return send_message_ok


#
# SESSION Cache
def set_c_prop(key, value):
    session[key] = value


def get_c_prop(key):
    return session.get(key, '')


def del_c_prop(key):
    session.pop(key)


def clear_cache():
    session.clear()


def clear_timesheet():
    set_c_prop(settings.C_TIMESHEET_ID, '')
    set_c_prop(settings.C_DATE, '')
    set_c_prop(settings.C_TSH_BTN_VALUE, '')
    set_c_prop(settings.C_PROJECT_ID, '')


def print_cache():
    util.log_info(f'session cache:')
    for k in settings.C_LIST_NAMES:
        util.log_info(f' .. {k}={session.get(k)}')


def create_module_html(module, msg, **params):

    # Вызов функции из модуля <ui_module> по имени
    create_html = getattr(ui_module, settings.MODULES[module][settings.M_HTML])
    return create_html(err_message=msg, **params)

    # Прямой вызов функции не подходит по причине зацикливания
    # return settings.MODULES[module][settings.M_HTML](err_message=err_msg)


def new_response(status, data=''):
    resp = make_response(data)
    resp.status = status
    return resp


def response(msg='', module='', msg_type=settings.MSG_TYPE_ERR, **params):
    if get_c_prop(settings.C_USER_ID) == '':  # До логина !!!
        return ui_module.create_info_html(settings.INFO_TYPE_ERROR, msg)

    if ui_module.use_message_dialog():  # Сообщение в виде модального окна

        if module == '':  # Сообщение в виде отдельного HTML
            return ui_module.create_info_html(settings.INFO_TYPE_ERROR, msg)

        resp = make_response(create_module_html(module, msg, **params))
        # resp.headers.set('Content-Type', 'text/html; charset=windows-1251')

        if msg != '':  # Показать модальное окно с сообщением
            resp.set_cookie(settings.COOKIE_SHOW_MESSAGE, msg_type)

        return resp
    else:  # Сообщение в виде отдельного HTML
        return ui_module.create_info_html(settings.INFO_TYPE_ERROR, msg, module)


# @application.before_request
# def before_request():
#     util.log_tmp(f'g: {g}; session: {len(session)}')
#     for k in session:
#         util.log_tmp(f'k: {k}')
#     # g.user = None
#     # if 'user' in session:
#     #     g.user = session['user']


#
# CLOSE - для обработки запросов из JS при закрытии браузера (windows.onbeforeunload)
#
@application.route('/close', methods=['GET'])
def close():
    try:

        # GET
        #
        if request.method == 'GET':
            # util.log_info(f'On close...{request.cookies};')
            # Срабатывает чаще, чем нужно: обновление, переход на другую страницу и ...
            # glob_module.dec_session_count()
            return f'On Close...'

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')


#
# upload_image - обработчик запросов из JS для сохранения файлов изображения (Users)
#
@application.route('/image_upload/<user_id>', methods=['POST'])
def image_upload(user_id):
    try:
        if request.method == 'POST':
            raise Exception('1234567908')
            # Сохранить файл в базе данных
            # util.log_tmp(f'request.data: {request.data}')
            data_module.update_user_image(user_id, request.data)
            return new_response(200)

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return new_response(500, f'{ex}')


#
# load_image - обработчик запросов из JS для загрузки файлов изображения (Users)
#
@application.route('/image_download/<user_id>', methods=['GET'])
def image_download(user_id):
    try:
        if request.method == 'GET':
            img = data_module.get_user_image(user_id)
            # util.log_tmp(f'load_image for {user_id}; {img}; {len(img)}')
            if len(img) == 0 or getattr(img[0], settings.F_USR_IMAGE) is None:
                return new_response(201, 'Нет изображения')
            else:
                data = bytes(getattr(img[0], settings.F_USR_IMAGE))
                return new_response(200, data)

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return new_response(500, f'{ex}')


#
# delete_image - обработчик запросов из JS для удаления файлов изображения (Users)
#
@application.route('/image_delete/<user_id>', methods=['GET'])
def image_delete(user_id):
    try:
        if request.method == 'GET':
            data_module.update_user_image(user_id, None)
            return new_response(200, 'Ok')

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return new_response(500, f'{ex}')


#
# LOGIN
#
@application.route('/login/<module>', methods=['GET', 'POST'])
def login(module):
    try:
        # GET
        #
        if request.method == 'GET':
            # util.log_info(f'login.GET: {glob_module.get_session_list()}')
            # print_cache()

            if settings.DBG_DO_LOGIN:  # Показать логин
                return ui_module.create_login_html('', module)
            else:  # Отладка - Default user
                if get_c_prop(settings.C_USER_NAME) == '':

                    set_c_prop(settings.C_USER_ID, settings.DBG_USER_ID)
                    set_c_prop(settings.C_USER_NAME, settings.DBG_USER_NAME)
                    set_c_prop(settings.C_USER_ROLE, settings.DBG_USER_ROLE)
                    # print_cache()

                    return redirect(url_for(module))
                else:
                    return ui_module.create_login_html('', module)

        # POST
        #
        if request.method == 'POST':
            values = request.form
            util.log_info(f'login.POST...{values}')
            for value in values:
                # Нажата кнопка LOGIN
                #
                if value == settings.LOGIN_BUTTON:
                    # Проверка на повторную регистрацию
                    user_name = values[settings.LOGIN_USERNAME]
                    user_session = glob_module.get_session_list().get(user_name)
                    if user_session is not None:  # Пользователь с именем "user_name" уже зарегистрирован
                        if user_session.get('sid') != '':  # "Висячая" сессия - sid = ''
                            return ui_module.create_login_html(f'Пользователь уже используется!', module, user_name)

                    # Проверка корректности введенных данных - user name, password
                    msg = apm.check_password(values)
                    if msg == '':
                        # Добавить сессию, для отслеживания
                        # util.log_tmp(f'cookies: {request.cookies}')
                        # glob_module.add_session(request.cookies.get("session"))

                        return redirect(url_for(module))
                    else:
                        return ui_module.create_login_html(msg, module, user_name)

            return f'values: {values}'

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return response(f'{ex}', module)


#
# TIMESHEETS
#
@application.route('/', methods=['GET', 'POST'])
@application.route(settings.MODULES[settings.M_TIMESHEETS][settings.M_URL], methods=['GET', 'POST'])
# @socketio.on('connect')
def timesheets():
    try:
        # util.log_tmp(f'timesheets.session_count: {get_session_count()}')
        values, html_test_db = apm.init_module(request)

        if html_test_db != '':
            return html_test_db

        # Зарегистрироваться, если еще не выполнен вход
        if get_c_prop(settings.C_USER_NAME) == '':
            return redirect(url_for(settings.M_LOGIN, module=settings.M_TIMESHEETS))

        # Установить неделю в кэш
        #
        week = get_c_prop(settings.C_WEEK)
        if week is None or week == '':
            current_week = util.get_week()
            set_c_prop(settings.C_WEEK, current_week)

        # GET
        #
        if request.method == 'GET':
            # for test..
            #
            # flash('Error')
            # return render_template('test.html')
            # return render_template(ui_module.t_html())
            # return ui_module.t_html()
            # util.log_tmp(f'test: {util.parse_user_agent_header(request)}')

            util.log_info(f'timesheets.GET...')

            # Проверить доступность модуля для роли
            html_not_available = ui_module.is_available_html(settings.M_TIMESHEETS)
            if html_not_available != '':
                return html_not_available
            else:
                return apm.timesheets_get()

        # POST
        #
        if request.method == 'POST':
            util.log_info(f'timesheets.POST...')
            # raise Exception('Привет! Привет! Привет! Привет! Привет! Привет! Привет! Привет! ')
            return apm.timesheets_post(values)

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return response(f'{ex}', settings.M_TIMESHEETS)


#
# PROJECTS
#
@application.route(settings.MODULES[settings.M_PROJECTS][settings.M_URL], methods=['GET', 'POST'])
def projects():
    try:
        values, html_test_db = apm.init_module(request)
        if html_test_db != '':
            return html_test_db

        # Зарегистрироваться, если еще не выполнен вход
        if get_c_prop(settings.C_USER_NAME) == '':
            return redirect(url_for(settings.M_LOGIN, module=settings.M_PROJECTS))

        # GET
        #
        if request.method == 'GET':
            util.log_info(f'projects.GET...')

            # Проверить доступность модуля для роли
            html_not_available = ui_module.is_available_html(settings.M_PROJECTS)
            if html_not_available != '':
                return html_not_available

            return apm.projects_get()

        # POST
        #
        if request.method == 'POST':
            util.log_info(f'projects.POST...')
            return apm.projects_post(values)

        # return 'nothing', 204

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return response(f'{ex}', settings.M_PROJECTS)


#
# APPROVEMENT
#
@application.route(settings.MODULES[settings.M_APPROVEMENT][settings.M_URL], methods=['GET', 'POST'])
def approvement():
    try:
        values, html_test_db = apm.init_module(request)
        if html_test_db != '':
            return html_test_db

        # Зарегистрироваться, если еще не выполнен вход
        if get_c_prop(settings.C_USER_NAME) == '':
            return redirect(url_for(settings.M_LOGIN, module=settings.M_APPROVEMENT))

        # GET
        #
        if request.method == 'GET':
            util.log_info(f'approvement.GET...')

            # Проверить доступность модуля для роли
            html_not_available = ui_module.is_available_html(settings.M_APPROVEMENT)
            if html_not_available != '':
                return html_not_available

            return apm.approvement_get()

        # POST
        #
        if request.method == 'POST':
            util.log_info(f'approvement.POST...')
            return apm.approvement_post(values)

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return response(f'{ex}', settings.M_APPROVEMENT)


#
# USERS
#
@application.route(settings.MODULES[settings.M_USERS][settings.M_URL], methods=['GET', 'POST'])
def users():
    try:
        values, html_test_db = apm.init_module(request)
        if html_test_db != '':
            return html_test_db

        # Зарегистрироваться, если еще не выполнен вход
        if get_c_prop(settings.C_USER_NAME) == '':
            return redirect(url_for(settings.M_LOGIN, module=settings.M_USERS))

        # GET
        #
        if request.method == 'GET':
            util.log_info(f'users.GET...')

            # Проверить доступность модуля для роли
            html_not_available = ui_module.is_available_html(settings.M_USERS)
            if html_not_available != '':
                return html_not_available

            return apm.users_get()

        # POST
        #
        if request.method == 'POST':
            util.log_debug(f'users.POST...')
            return apm.users_post(values)

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return response(f'{ex}', settings.M_USERS)


#  API: Список записей timesheets
#
@application.route(settings.API_TIMESHEETS, methods=['GET'])  # все
@application.route(settings.API_TIMESHEETS_BY_USER, methods=['GET'])  # по имени пользователя
def api_timesheets(user_name='%'):
    try:
        # GET
        #
        if request.method == 'GET':
            # util.log_info(f'API_TIMESHEETS: {user_name}; {request.headers}')

            msg = check_authorization(request)
            if msg != '':
                raise Exception(msg)

            data = data_module.get_entries_by_user_name(user_name)
            if data is None:
                raise Exception('Empty data')

            return data

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return {'Error': f'{ex}'}


#  API: Список проектов
#
@application.route(settings.API_PROJECTS, methods=['GET'])  # все
@application.route(settings.API_PROJECTS_BY_NAME, methods=['GET'])  # по имени проекта
def api_projects(project_name=''):
    try:

        # GET
        #
        if request.method == 'GET':
            # util.log_info(f'API_PROJECTS: {project_name}; {request.headers}')

            msg = check_authorization(request)
            if msg != '':
                raise Exception(msg)

            if project_name == '':
                project_name = '%'
            else:
                project_name = f'%{project_name}%'

            data = data_module.get_projects_by_name(project_name)
            if data is None:
                raise Exception('Empty data')
            return data

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return {'Error': f'{ex}'}


#  API: Список записей на согласование
#
@application.route(settings.API_APPROVEMENTS, methods=['GET'])  # все
@application.route(settings.API_APPROVEMENTS_BY_MANAGER, methods=['GET'])  # по имени руководителя проекта
def api_approvements(manager_name='%'):
    try:

        # GET
        #
        if request.method == 'GET':
            # util.log_info(f'API_APPROVEMENTS: {manager_name}; {request.headers}')

            msg = check_authorization(request)
            if msg != '':
                raise Exception(msg)

            data = data_module.get_entries_for_approval_name(manager_name)
            if data is None:
                return {'Info': f'Нет записей для утверждения руководителем проекта: {manager_name}'}
            return data

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return {'Error': f'{ex}'}


#  API: Список пользователей
#
@application.route(settings.API_USERS, methods=['GET'])  # все
@application.route(settings.API_USERS_BY_NAME, methods=['GET'])  # по имени пользователя
def api_users(user_name='%'):
    try:

        if request.method == 'GET':
            # util.log_info(f'API_USERS: {user_name}; {request.headers}')
            msg = check_authorization(request)
            if msg != '':
                raise Exception(msg)

            return data_module.get_users_by_name(user_name)

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return {'Error': f'{ex}'}


@application.route('/api/test_session/<user_name>', methods=['GET'])
def api_test_session(user_name):
    try:
        if request.method == 'GET':
            util.log_info(f'api_test_session: {user_name};')
            msg = check_authorization(request)
            if msg != '':
                raise Exception(msg)

            status = test_session(user_name)
            return {'Status': status}

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return {'Error': f'{ex}'}


@application.route('/api/clear_sessions', methods=['GET'])
def api_clear_sessions():
    try:
        if request.method == 'GET':
            util.log_info(f'api_clear_sessions')
            msg = check_authorization(request)
            if msg != '':
                raise Exception(msg)

            s_list = glob_module.get_session_list()
            s_inactive = []

            # Test sessions
            for usr in s_list:
                if bool(test_session(usr)):
                    util.log_info(f'session for: {usr} is Active')
                else:
                    util.log_info(f'session for: {usr} is Inactive')
                    s_inactive.append(usr)

            # Clear inactive sessions
            for usr in s_inactive:
                util.log_debug(f'clear session for: {usr}')
                glob_module.remove_user_from_session_list(usr)

            return glob_module.get_session_list()

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return {'Error': f'{ex}'}


@application.route('/api/sessions/<user_name>', methods=['GET'])
def api_sessions(user_name):
    try:
        if request.method == 'GET':
            # util.log_info(f'api_sessions: {user_name};')
            msg = check_authorization(request)
            if msg != '':
                raise Exception(msg)

            if user_name == '*':
                send_message('show#Всем привет!')
            else:
                send_message(f'show#Привет, {user_name}!', user_name)
            return glob_module.get_session_list()

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return {'Error': f'{ex}'}


#
# run application
#
if __name__ == '__main__':
    #
    # sudo gunicorn -b 0.0.0.0:1000 -w 1 app:application
    # util.log_info(f'app:application.url_map: {application.url_map}')
    if util.IS_WINDOWS:  # Не стартует на UNIX !!!
        util.log_info(f'app:application: {application.permanent}; {application.permanent_session_lifetime}')

        # application.run(debug=True, port=1000, host='0.0.0.0')
        socketio.run(application, allow_unsafe_werkzeug=True, debug=True, port=1000, host='0.0.0.0')

