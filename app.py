import os
import traceback
import datetime

from flask import Flask, request, redirect, url_for, session, make_response

import data_module
import glob_module
import ui_module
import settings
import util_module as util
import app_module as app


application = Flask(__name__)
application.secret_key = os.urandom(32)  # для принудительного сброса всех сессий при перезагрузке приложения
application.permanent = settings.S_PERMANENT

if settings.S_PERMANENT:
    application.permanent_session_lifetime = datetime.timedelta(minutes=settings.S_LIFETIME_IN_MINUTES)


# def _test():
#     # return ui_module.create_html_static()
#     return ui_module.t_html()
#     # s = settings.MODULES[settings.M_TIMESHEETS]['url']
#     # print(f'=={s}')


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


def new_session():
    session.new = True


def print_cache():
    util.log_info(f'session cache:')
    for k in session.keys():
        util.log_info(f' .. {k}={session.get(k)}')


def response(msg='', module='', msg_type=settings.INFO_TYPE_ERROR):

    if util.use_message_dialog():  # Сообщение в виде модального окна

        if module == '':  # Сообщение в виде отдельного HTML
            return ui_module.create_info_html(msg_type, msg)

        if module == settings.M_APPROVEMENT:
            resp = make_response(ui_module.create_approvement_html(err_message=msg))

        if module == settings.M_TIMESHEETS:
            resp = make_response(ui_module.create_timesheet_html(err_message=msg))

        if module == settings.M_USERS:
            resp = make_response(ui_module.create_users_html(err_message=msg))

        if msg != '':
            resp.set_cookie(settings.COOKIE_SHOW_MESSAGE, 'Yes')

        return resp
    else:  # Сообщение в виде отдельного HTML
        return ui_module.create_info_html(msg_type, msg, module)





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
            util.log_info(f'On close...{request.cookies};')
            # Срабатывает чаще, чем нужно: обновление, переход на другую страницу и ...
            # glob_module.dec_session_count()
            return f'On Close...'

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return ui_module.create_info_html(settings.INFO_TYPE_ERROR, f'{ex}')


#
# LOGIN
#
@application.route('/login/<module>', methods=['GET', 'POST'])
def login(module):
    try:
        # GET
        #
        if request.method == 'GET':
            util.log_info(f'login.GET...')
            print_cache()

            if settings.DBG_DO_LOGIN:  # Показать логин
                return ui_module.craete_login_html('', module)
            else:  # Отладка - Default user
                if get_c_prop(settings.C_USER_NAME) == '':

                    set_c_prop(settings.C_USER_ID, settings.DBG_USER_ID)
                    set_c_prop(settings.C_USER_NAME, settings.DBG_USER_NAME)
                    set_c_prop(settings.C_USER_ROLE, settings.DBG_USER_ROLE)
                    print_cache()

                    return redirect(url_for(module))
                else:
                    return ui_module.craete_login_html('', module)

        # POST
        #
        if request.method == 'POST':
            values = request.form
            util.log_info(f'login.POST...{values}')
            for value in values:
                # Нажата кнопка LOGIN
                #
                if value == settings.LOGIN_BUTTON:
                    msg = app.check_password(values)
                    if msg == '':
                        # Добавить сессию, для отслеживания
                        # util.log_tmp(f'cookies: {request.cookies}')
                        # glob_module.add_session(request.cookies.get("session"))

                        return redirect(url_for(module))
                    else:
                        return ui_module.craete_login_html(msg, module)

            return f'values: {values}'

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return ui_module.create_info_html(settings.INFO_TYPE_ERROR, f'{ex}', module)


#
# TIMESHEETS
#
@application.route('/', methods=['GET', 'POST'])
@application.route(settings.MODULES[settings.M_TIMESHEETS][settings.M_URL], methods=['GET', 'POST'])
def timesheets():
    try:

        # util.log_tmp(f'timesheets.session_count: {get_session_count()}')
        values, html_test_db = app.init_module(request)

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

        html = ui_module.create_info_html(
            i_type=settings.INFO_TYPE_ERROR,
            module=settings.M_TIMESHEETS,
            msg=('Empty HTML.', 'Возможно, не задан обработчик кнопки.',)
        )
        # return html

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

            html = app.timesheets_get()

        # POST
        #
        if request.method == 'POST':
            util.log_info(f'timesheets.POST...')
            html = app.timesheets_post(values)

        # return html #'nothing', 204
        # util.log_tmp(f'isResponse: {isinstance(html, Response)}')
        # resp = make_response(html)
        # resp.set_cookie(settings.COOKIE_SHOW_MESSAGE, 'Текст сообщения')
        # return resp
        return html

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return ui_module.create_info_html(msg=str(ex), module=settings.M_TIMESHEETS, i_type=settings.INFO_TYPE_ERROR)


#
# PROJECTS
#
@application.route(settings.MODULES[settings.M_PROJECTS][settings.M_URL], methods=['GET', 'POST'])
def projects():
    try:
        values, html_test_db = app.init_module(request)
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

            return app.projects_get()

        # POST
        #
        if request.method == 'POST':
            util.log_info(f'projects.POST...')
            return app.projects_post(values)

        # return 'nothing', 204

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return ui_module.create_info_html(msg=str(ex), module=settings.M_PROJECTS, i_type=settings.INFO_TYPE_ERROR)


#
# APPROVEMENT
#
@application.route(settings.MODULES[settings.M_APPROVEMENT][settings.M_URL], methods=['GET', 'POST'])
def approvement():
    try:
        values, html_test_db = app.init_module(request)
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

            return app.approvement_get()

        # POST
        #
        if request.method == 'POST':
            util.log_info(f'approvement.POST...')
            return app.approvement_post(values)

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return ui_module.create_info_html(msg=str(ex), module=settings.M_APPROVEMENT, i_type=settings.INFO_TYPE_ERROR)


#
# USERS
#
@application.route(settings.MODULES[settings.M_USERS][settings.M_URL], methods=['GET', 'POST'])
def users():
    try:
        values, html_test_db = app.init_module(request)
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

            return app.users_get()

        # POST
        #
        if request.method == 'POST':
            util.log_info(f'users.POST...')
            return app.users_post(values)

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'{ex}')
        return ui_module.create_info_html(msg=str(ex), module=settings.M_USERS, i_type=settings.INFO_TYPE_ERROR)


#  API: Список записей по имени пользователя
#
@application.route(settings.API_TIMESHEETS_BY_USER, methods=['GET'])
def api(user_name):
    try:

        # GET
        #
        if request.method == 'GET':
            util.log_info(f'API_TIMESHEETS_BY_USER: {user_name}')
            data = data_module.get_entries_by_user_name(user_name)

            if data is None:
                raise Exception('Empty data')
            return data

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
    if settings.IS_WINDOWS:
        util.log_info(f'app:application: {application.permanent}; {application.permanent_session_lifetime}')

        application.run(debug=True, port=1000, host='0.0.0.0')

