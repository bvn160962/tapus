import requests
from flask import redirect, url_for

import app
import glob_module
import pg_module
import util_module as util
import settings
import ui_module
import data_module


# COMMON BLOCK
#

# Определить ip клиента
#
def get_client_ip(request):
    # Get client ip
    ip = request.environ.get('REMOTE_ADDR')

    if ip == '':
        isNginx = request.headers.get('T-Nginx')
        if isNginx is None:
            util.log_error('Host is ""')
        else:
            # Определяем хост для nginx установки
            # util.log_debug(f'headers: {request.headers}')
            ip_addrs = request.headers.get('X-Real-Ip')
            if ip_addrs is None:
                util.log_error('Host is None')
            else:
                ips = ip_addrs.split(',')
                if len(ips) == 0:
                    util.log_error(f'Bad Host: {ip_addrs}')
                else:
                    ip = ips[0]

    return ip


# Очистка "зависших" сессий
def clear_sessions():
    all_sess = glob_module.get_session_list()
    r_list = []

    for usr in all_sess:
        if not bool(test_session_by_user(usr)):
            r_list.append(usr)

    for usr in r_list:
        util.log_debug(f'clear session for: {usr}')
        glob_module.remove_user_from_session_list(usr)


# Проверка состояния сессии через REST API - api/test_session/<user_name>
def test_session_by_user(user_name):
    # Для пользователя, выполняющего тестирование (например, нажавшего кнопку Debug) - проверка не производится!
    # Последовательность действий в контексте <SocketIO> такова:
    #   сначала выполняется disconnect (сессия закрывается, удаляется 'sid' в записи текущего пользователя),
    #   затем выполняется код (test_session_by_user - запись в словаре сессий с пустым 'sid'!!!),
    #   и далее выполняется connect (регистрируется новая сессия, обновляется запись в словаре сессий с новым 'sid')
    # Таким образом, на момент выполнения кода, для текущего пользователя нет 'sid' в записи словаря сессий!!!
    # Следовательно, для текущего пользователя - сессия всегда считается активной
    if user_name == app.get_c_prop(settings.C_USER_NAME):
        return True

    # Сессии с пустым 'sid' (кроме текущей) считаются неактивными
    if glob_module.get_sid_by_user(user_name) == '':
        return False

    try:
        # Проверяем активность сессий для непустых 'sid' через REST API
        url = url_for('api_test_session', _external=True, user_name=user_name)
        # url = f'http://193.168.46.78/api/test_session/{user_name}'
        util.log_debug(f'test_session_by_user for: {user_name}; {util.normalize_url(url)}')
        response = requests.get(util.normalize_url(url), headers={'Authorization': settings.API_AUTHORIZATION_TOKEN})
        status = response.json().get('Status')
        util.log_debug(f'test_session_by_user: {user_name}; {status}')

        # rstatus = response.status_code
        # util.log_tmp(f'response: {rstatus}; {status}')
        return status

    except Exception as ex:
        util.log_error(f'test_session_by_user: {ex}')
        return False


def init_module(request):
    # Определить ip адрес
    # ip = get_client_ip(request)

    # Определить тип ОС браузера
    os_type = app.get_c_prop(settings.C_CLIENT_OS_TYPE)
    if os_type == '':
        os_type = util.get_client_os_type(request)
        app.set_c_prop(settings.C_CLIENT_OS_TYPE, os_type)
    util.log_debug(f'Тип ОС браузера: {os_type}')

    # Получить значения формы
    values = request.form
    util.log_debug(f'FORM={values}')

    # Проверка доступности БД
    # Пропустить ,если нажата DEBUG
    debug_mode = False
    for key in values:
        if key == settings.DEBUG_BUTTON:
            debug_mode = True

    if debug_mode:
        html_test_db = ''
    else:
        html_test_db = pg_module.test_connection()

    return values, html_test_db


def check_password(values):
    err_msg = 'Неправильно введен логин или пароль!'
    # util.set_user_name(ip, '')
    # app.clear_cache()
    app.set_c_prop(settings.C_USER_NAME, '')

    usr_name = ''
    usr_pwd = ''
    for v in values:
        if v == settings.LOGIN_USERNAME:
            usr_name = values[v]
        if v == settings.LOGIN_PASSWORD:
            usr_pwd = values[v]

    if usr_name != '':
        user = data_module.get_user_by_name_list(usr_name)
        if len(user) == 0:  # Нет такого пользователя!!!
            pass
            # Сбросить кэш
            # util.clear_user_cache(host)
        else:
            pwd_db = user[2]  # из базы данных
            pwd_in = util.get_hash(usr_pwd)  # хэш введенного пароля

            # util.log_debug(f'{pwd_in}={pwd_db}')
            if pwd_in == pwd_db:
                err_msg = ''

                # Увеличить счетчик текущих сессий - сбрасывается при рестарте приложения
                glob_module.inc_session_count()

                # Увеличить счетчик сессий (посещений) - сбрасывается только "руками"
                cnt = int(data_module.get_session_count())
                cnt += 1
                data_module.set_session_count(cnt)

                app.set_c_prop(settings.C_USER_ID, user[0])
                app.set_c_prop(settings.C_USER_NAME, usr_name)
                app.set_c_prop(settings.C_USER_ROLE, user[1])

    # util.print_cache()
    return err_msg


def logoff(module):
    # util.log_debug(f'Logoff: {app.get_c_prop(settings.C_USER_NAME)}')
    glob_module.remove_user_from_session_list(app.get_c_prop(settings.C_USER_NAME))
    glob_module.dec_session_count()
    app.clear_cache()

    return redirect(url_for(settings.M_LOGIN, module=module))


def debug(module):

    title = 'Содержимое переменных текущей сессии'
    s_list = [
        ('Имя переменной', 'Значение'),

        ('*** CACHE ***', ''),
        (settings.C_WEEK, str(app.get_c_prop(settings.C_WEEK))),
        (settings.C_DATE, str(app.get_c_prop(settings.C_DATE))),
        (settings.C_TIMESHEET_ID, str(app.get_c_prop(settings.C_TIMESHEET_ID))),
        (settings.C_PROJECT_ID, str(app.get_c_prop(settings.C_PROJECT_ID))),
        (settings.C_TSH_BTN_VALUE, str(app.get_c_prop(settings.C_TSH_BTN_VALUE))),
        (settings.C_USER_ID, str(app.get_c_prop(settings.C_USER_ID))),
        (settings.C_USER_NAME, str(app.get_c_prop(settings.C_USER_NAME))),
        (settings.C_USER_ROLE, str(app.get_c_prop(settings.C_USER_ROLE))),
        (settings.C_CLIENT_OS_TYPE, str(app.get_c_prop(settings.C_CLIENT_OS_TYPE))),

        ('*** SETTINGS ***', ''),
        ('DBG_DO_LOGIN', str(settings.DBG_DO_LOGIN)),
        ('S_PERMANENT', str(app.application.permanent)),
        ('S_LIFETIME_IN_MINUTES', str(app.application.permanent_session_lifetime)),
        ('SHOW_EMPTY_WEEK', str(settings.SHOW_EMPTY_WEEK)),
        ('IS_WINDOWS', str(util.IS_WINDOWS)),
        ('LOG_DIR', str(util.LOG_DIR)),
        ('LOG_FILE_NAME', str(util.LOG_FILE_NAME)),
        ('LOG_FILE_MODE', str(util.LOG_FILE_MODE)),
        ('LOG_FILE_LEVEL', str(util.LOG_FILE_LEVEL)),

        ('*** POSTGRES ***', ''),
        ('PG_HOST', str(pg_module.PG_HOST)),
        ('PG_PORT', str(pg_module.PG_PORT)),
        ('PG_USER', str(pg_module.PG_USER)),
        ('PG_DATABASE', str(pg_module.PG_DATABASE)),
    ]

    if pg_module.DB_CONNECT is not None:
        s_list.append(('*** DATABASE ***', ''))
        s_list.append(('DB_VERSION', str(pg_module.DB_CONNECT.server_version)))
        s_list.append(('DB_STATUS', str(pg_module.DB_CONNECT.status)))
        s_list.append(('DB_TR_STATUS', str(pg_module.DB_CONNECT.get_transaction_status())))

        s_list.append(('*** DB PARAMETERS ***', ''))
        s_list.append(('LOGIN_COUNT', str(data_module.get_session_count())))

        s_list.append(('*** ACTIVE SESSIONS ***', ''))
        clear_sessions()  # Удалить зависшие сессии
        s_list.append(('SESSION_COUNT', f'{len(glob_module.get_session_list())} [{str(glob_module.get_sess_cnt())}] '))
        sess_list = glob_module.get_session_list()
        for usr in sess_list:
            s_list.append((f'{usr} / {sess_list[usr].get("sid")} ', f'{sess_list[usr].get("ip")} '))

    return ui_module.create_info_html(settings.INFO_TYPE_INFORMATION, s_list, module, title)


def update(module):
    try:
        app.clear_timesheet()
        app.set_c_prop(settings.C_WEEK, util.get_week())
        app.print_cache()

        pg_module.DB_CONNECT = None

        # Вызов функции из модуля <ui_module> по имени
        create_html = getattr(ui_module, settings.MODULES[module][settings.M_HTML])
        return create_html()

    except Exception as ex:
        return app.response(f'{ex}', module)


def notifications(module):
    try:
        msgs = data_module.get_messages(app.get_c_prop(settings.C_USER_ID))
        title = 'Сообщения'
        s_list = [
            ('Пользователь', 'Текст сообщения', 'Дата', 'Прочитано', 'Ссылка'),
        ]
        for msg in msgs:
            is_read = 'да' if getattr(msg, settings.F_MSG_IS_READ) else 'нет'
            ref_obj = f'{getattr(msg, settings.F_TSH_DATE)}/ '\
                      f'{getattr(msg, settings.F_TSH_STATUS)}/ '\
                      f'{getattr(msg, settings.F_TSH_NOTE)}/ '\
                      f'{getattr(msg, settings.F_TSH_ID)}/ '
            s_list.append(
                (
                    str(getattr(msg, settings.F_USR_NAME)),
                    str(getattr(msg, settings.F_MSG_TEXT)),
                    str(getattr(msg, settings.F_MSG_CREATION_DATE)),
                    str(is_read),
                    str(ref_obj),
                 )
            )

        return ui_module.create_info_html(settings.INFO_TYPE_INFORMATION, s_list, module, title)

    except Exception as ex:
        return app.response(f'{ex}', module)


# Обработчик кнопок, общих для всех модулей
def common_buttons(value, module):
    if value == settings.NOTIFICATION_BUTTON:
        return notifications(module)

    # Нажата кнопка LOGOFF
    #
    if value == settings.LOGOFF_BUTTON:
        return logoff(module)

    # Нажата кнопка DEBUG
    #
    if value == settings.DEBUG_BUTTON:
        return debug(module)

    # Нажата кнопка REFRESH
    #
    if value == settings.UPDATE_BUTTON:
        return update(module)

    # Не нажата ни одна из общих кнопок
    return ''


# TIMESHEETS BLOCK
#
def timesheets_select(value=''):
    # util.log_debug(f'Нажата кнопка в Таблице: {value}')

    # Разбор значения value (prj_id#tsh_id#date)
    #
    s = value.split(settings.SPLITTER)
    if s is None:
        raise Exception('Ошибка при парсинге values: None')

    if len(s) != 3:
        raise Exception(f'Ошибка при парсинге values: len={len(s)}')

    # Set cache
    #
    app.set_c_prop(settings.C_PROJECT_ID, s[0])
    app.set_c_prop(settings.C_TIMESHEET_ID, s[1])
    app.set_c_prop(settings.C_DATE, s[2])
    app.set_c_prop(settings.C_TSH_BTN_VALUE, value)

    return ui_module.create_timesheet_html()


def week_select(values=None):
    app.clear_timesheet()
    week = values[ui_module.INPUT_WEEK_NAME]
    app.set_c_prop(settings.C_WEEK, week)


def current_week():
    app.clear_timesheet()
    app.set_c_prop(settings.C_WEEK, util.get_week())
    return ui_module.create_timesheet_html()


def next_week():
    app.clear_timesheet()
    week = app.get_c_prop(settings.C_WEEK)
    app.set_c_prop(settings.C_WEEK, util.shift_week(week, True))
    return ui_module.create_timesheet_html()


def prev_week():
    app.clear_timesheet()
    week = app.get_c_prop(settings.C_WEEK)
    app.set_c_prop(settings.C_WEEK, util.shift_week(week, False))
    return ui_module.create_timesheet_html()


def timesheets_save(values):
    try:
        # util.log_info(f'Нажата кнопка Save: {values}')

        # Прочитать значения из формы (values = request.form)
        #
        tsh_id, prj_id, inp_hours, inp_note, inp_status, current_date, comment, man_id = '', '', '', '', '', '', '', ''
        for value in values:
            if value == settings.SAVE_BUTTON:
                tsh_id = values[value]
            if value == ui_module.SELECT_PROJECT_NAME:
                prj_id = values[value].split(settings.SPLITTER)[0]
                man_id = values[value].split(settings.SPLITTER)[1]
            if value == ui_module.INPUT_HOURS_NAME:
                inp_hours = values[value]
            if value == ui_module.INPUT_NOTE_NAME:
                inp_note = values[value]
            if value == ui_module.SELECT_STATUS_NAME:
                inp_status = values[value]
            if value == ui_module.DATE_NAME:
                current_date = values[value]
            if value == ui_module.INPUT_COMMENT_NAME:
                comment = values[value]

        util.log_tmp(f'prj_id: {prj_id}; man_id: {man_id}; status: {inp_status}')

        if tsh_id == '':
            # Новая запись - Insert
            #
            if prj_id == '' or current_date == '' or inp_hours == '':
                msg = 'Атрибут(ы):'
                if current_date == '':
                    msg += '\n\t- "Дата";'
                if inp_hours == '':
                    msg += '\n\t- "Часы";'
                msg += '\nдолжны быть заполнены!'
                util.log_debug(msg)
                return app.response(msg, settings.M_TIMESHEETS)
            else:
                tsh_id = data_module.insert_entry(
                    user_id=app.get_c_prop(settings.C_USER_ID),
                    prj_id=prj_id,
                    data={
                        settings.F_TSH_DATE: current_date,
                        settings.F_TSH_HOURS: inp_hours,
                        settings.F_TSH_NOTE: inp_note,
                        settings.F_TSH_STATUS: inp_status,
                        settings.F_TSH_COMMENT: comment
                    }
                )
                app.set_c_prop(settings.C_TIMESHEET_ID, f'{tsh_id}')
                # prj_id + settings.SPLITTER + settings.SPLITTER + day
                btn_value = f'{prj_id}{settings.SPLITTER}{tsh_id}{settings.SPLITTER}'
                app.set_c_prop(settings.C_TSH_BTN_VALUE, btn_value)
        else:
            # Существующая запись - Update
            #
            data_module.update_entry(
                tsh_id=tsh_id,
                data={
                    settings.F_TSH_HOURS: inp_hours,
                    settings.F_TSH_NOTE: inp_note,
                    settings.F_TSH_STATUS: inp_status,
                    settings.F_TSH_COMMENT: comment
                }
            )

        # Оповестить руководителя проекта
        if ui_module.use_notifications_dialog() and inp_status == settings.IN_APPROVE_STATUS:
            data_module.add_message(comment, app.get_c_prop(settings.C_USER_ID), {tsh_id: man_id})

        return ''

    except Exception as ex:
        return app.response(f'{ex}', settings.M_TIMESHEETS)


def timesheets_delete(tsh_id):
    try:
        # tsh_id = app.get_c_prop(settings.C_TIMESHEET_ID)
        util.log_debug(f'pressed_delete_button: Delete entry: tsh_id={tsh_id}')

        if tsh_id != '':
            data_module.delete_entry(tsh_id=tsh_id)
            app.set_c_prop(settings.C_TIMESHEET_ID, '')  # убрать tsh_id из кэша
            return ''
        else:
            raise Exception('Попытка удалить запись с пустым tsh_id')

    except Exception as ex:
        return app.response(f'{ex}', settings.M_TIMESHEETS)


# GET
#
def timesheets_get():
    try:
        return ui_module.create_timesheet_html()
    except Exception as ex:
        return app.response(f'{ex}', settings.M_TIMESHEETS)


# POST
#
def timesheets_post(values):
    try:
        for value in values:
            # Нажата одна из общих кнопок?
            html = common_buttons(value, settings.M_TIMESHEETS)
            if html != '':
                return html

            # Нажата одна из кнопок в таблице?
            #
            if value == settings.TABLE_BUTTON:
                return timesheets_select(values[value])

            # Нажата кнопка SAVE Entry
            #
            if value == settings.SAVE_BUTTON:
                html = timesheets_save(values)
                if html != '':
                    return html
                else:
                    return ui_module.create_timesheet_html()

            # Нажата кнопка DELETE YES
            #
            if value == settings.DELETE_BUTTON_YES:
                html = timesheets_delete(values[value])
                if html != '':
                    return html
                else:
                    return ui_module.create_timesheet_html()

            # Нажата кнопка DELETE NO
            #
            if value == settings.DELETE_BUTTON_NO:
                return ui_module.create_timesheet_html()

            # Нажата кнопка DELETE Entry
            #
            if value == settings.DELETE_BUTTON:
                # Show confirmation dialog
                return ui_module.create_delete_confirm_html(app.get_c_prop(settings.C_TIMESHEET_ID), settings.M_TIMESHEETS)

            # Нажата кнопка WEEK
            #
            if value == settings.WEEK_BUTTON_SELECT:
                week_select(values)
                return ui_module.create_timesheet_html()

            # Нажата кнопка NEW Entry
            #
            if value == settings.NEW_BUTTON:
                app.set_c_prop(settings.C_TIMESHEET_ID, '')
                return ui_module.create_timesheet_html()

            # Нажата кнопка CURRENT WEEK
            #
            if value == settings.WEEK_BUTTON_CURRENT:
                return current_week()

            # Нажата кнопка NEXT WEEK
            #
            if value == settings.WEEK_BUTTON_NEXT:
                return next_week()

            # Нажата кнопка PREV WEEK
            #
            if value == settings.WEEK_BUTTON_PREV:
                return prev_week()

        return 'Кнопка не обработана!', 404

    except Exception as ex:
        return app.response(f'{ex}', settings.M_TIMESHEETS)


# PROJECTS BLOCK
#
def projects_delete(prj_id):
    try:
        util.log_debug(f'Delete Project: prj_id={prj_id}')
        data_module.delete_project(prj_id)
        return ui_module.create_projects_html(())
    except Exception as ex:
        return app.response(f'{ex}', settings.M_PROJECTS)


def projects_not_delete(prj_id):
    try:
        props = data_module.get_project_by_id_list(prj_id)
        m_props = (str(props[0]), str(props[1]), str(props[2]), str(props[3]), str(props[4]), str(props[5]))

        return ui_module.create_projects_html(m_props)
    except Exception as ex:
        return app.response(f'{ex}', settings.M_PROJECTS)


# def projects_update():
#     try:
#         # util.log_debug(f'Нажата кнопка Update Projects')
#         util.update()
#         return ui_module.create_projects_html()
#
#     except Exception as ex:
#         return app.response(f'{ex}', settings.M_PROJECTS)


def projects_select(prj_id):
    try:
        # util.log_debug(f'Нажата кнопка Select Project id={prj_id}')
        prj_props = data_module.get_project_by_id_list(prj_id)
        return ui_module.create_projects_html(prj_props)

    except Exception as ex:
        return app.response(f'{ex}', settings.M_PROJECTS)


def projects_save(prj_id, props):
    try:
        # Сформировать список свойств проекта
        #
        p_name, p_manager_id, p_s_date, p_e_date, p_org = '', '', '', '', ''
        team_list = []
        for p in props:
            if p == settings.F_PRJ_NAME:
                p_name = props[p]
            if p == settings.F_PRJ_ORG:
                p_org = props[p]
            if p == settings.F_PRJ_MANAGER_ID:  # Не передается, если список значений disabled
                p_manager_id = props[p]
            if p == settings.F_PRJ_START_DATE:
                p_s_date = props[p]
            if p == settings.F_PRJ_END_DATE:
                p_e_date = props[p]
            # Команда проекта
            if props[p] == 'on':
                team_list.append(p)

        if p_manager_id == '':  # Список ролей disabled
            p_manager_id = app.get_c_prop(settings.C_USER_ID)

        prj_props = (prj_id, p_manager_id, p_name, p_s_date, p_e_date, p_org)
        prj_props_db = (prj_id, p_manager_id, p_name, None if p_s_date == '' else p_s_date, None if p_e_date == '' else p_e_date, p_org)

        # Проверка переданных атрибутов
        if p_name == '':
            msg = 'Атрибут "Название проекта" должен быть заполнен!'
            return app.response(msg, settings.M_PROJECTS, props=prj_props, info=True)
            # return app.response(msg, settings.M_PROJECTS)

        if prj_id == '':  # Создать нового пользователя
            util.log_debug('Insert')
            data_module.insert_project(prj_props_db, team_list)
        else:  # Обновить существующего пользователя
            util.log_debug('Update')
            data_module.update_project(prj_props_db, team_list)

        return ui_module.create_projects_html(())

    except Exception as ex:
        return app.response(f'{ex}', settings.M_PROJECTS)


def projects_new_button():
    # util.log_debug(f'Нажата кнопка New Project')
    return ui_module.create_projects_html((), True)


def projects_ref_button(prj_id):
    try:
        prj = data_module.get_project_by_id_list(prj_id)
        prj_name = prj[2]
        # util.log_debug(f'Нажата кнопка Project Reference: {prj_id}; {prj_name}')

        e_list = data_module.where_project_refs(prj_id)
        if len(e_list) == 0:
            return ui_module.create_info_html(settings.INFO_TYPE_INFORMATION, f'Нет записей учета отработанного времени на проекте "{prj_name}".', settings.M_PROJECTS)
        else:
            title = f'Записи учета отработанного времени на проекте "{prj_name}"'
            e_list.insert(0, ('Дата', 'Статус', 'Комментарий', 'Исполнитель'))  # Заголовок таблицы
            return ui_module.create_info_html(settings.INFO_TYPE_INFORMATION, e_list, settings.M_PROJECTS, title)

    except Exception as ex:
        return app.response(f'{ex}', settings.M_PROJECTS)


# GET
#
def projects_get():
    try:
        return ui_module.create_projects_html(())

    except Exception as ex:
        return app.response(f'{ex}', settings.M_PROJECTS)


# POST
#
def projects_post(values):
    try:
        for value in values:
            # Нажата одна из общих кнопок?
            html = common_buttons(value, settings.M_PROJECTS)
            if html != '':
                return html

            # Нажата кнопка SELECT
            #
            if value == settings.TABLE_BUTTON:
                return projects_select(values[value])

            # Нажата кнопка SAVE
            #
            if value == settings.SAVE_BUTTON:
                return projects_save(values[value], values)

            # Нажата кнопка NEW
            #
            if value == settings.NEW_BUTTON:
                return projects_new_button()

            # Нажата кнопка REFERENCE
            #
            if value == settings.REF_BUTTON:
                return projects_ref_button(values[value])

            # Нажата кнопка HIDEINFO
            #
            if value == settings.HIDEINFO_BUTTON:
                return ui_module.create_projects_html()

            # Нажата кнопка DELETE
            #
            if value == settings.DELETE_BUTTON:
                # Show confirmation dialog
                return ui_module.create_delete_confirm_html(values[value], settings.M_PROJECTS)

            # Отклонение DELETE NO
            #
            if value == settings.DELETE_BUTTON_NO:
                return projects_not_delete(values[value])

            # Подтверждение DELETE YES
            #
            if value == settings.DELETE_BUTTON_YES:
                return projects_delete(values[value])

    except Exception as ex:
        return app.response(f'{ex}', settings.M_PROJECTS)


# USERS BLOCK
#
# def users_update():
#     try:
#         # util.log_debug(f'Нажата кнопка Update Users')
#         util.update()
#         return ui_module.create_users_html()
#
#     except Exception as ex:
#         return app.response(f'{ex}', settings.M_USERS)


def users_select(usr_id):
    try:
        # util.log_debug(f'Нажата кнопка Select User for user_id={usr_id}')
        usr_props = data_module.get_user_by_id_list(usr_id)
        # util.log_debug(f'props: {usr_props}')

        return ui_module.create_users_html(usr_props)

    except Exception as ex:
        return app.response(f'{ex}', settings.M_USERS)


def users_save(usr_id, usr_props):
    try:
        # util.log_debug(f'Нажата кнопка Save User for user_id={usr_id}, props={usr_props}')

        # Сформировать список свойств
        #
        u_name, u_role, u_pwd, u_mail, u_info = '', '', '', '', ''
        for p in usr_props:
            if p == settings.F_USR_NAME:
                u_name = usr_props[p]
            if p == settings.F_USR_ROLE:
                u_role = usr_props[p]
            if p == settings.F_USR_PASSWORD:
                u_pwd = usr_props[p]
                # u_pwd = util.get_hash(props[p])
            if p == settings.F_USR_MAIL:
                u_mail = usr_props[p]
            if p == settings.F_USR_INFO:
                u_info = usr_props[p]

        if usr_id == '':  # Создать нового пользователя
            # util.log_debug('Insert')
            usr_props = (usr_id, u_name, u_role, util.get_hash(u_pwd), u_mail, u_info)
            # Проверка атрибутов
            if u_name == '' or u_pwd == '':
                msg = 'Атрибут(ы):'
                if u_name == '':
                    msg += '\n\t- "Имя пользователя";'
                if u_pwd == '':
                    msg += '\n\t- "Пароль";'
                msg += '\nдолжны быть заполнены!'
                return app.response(msg, settings.M_USERS, props=usr_props, show=True)
            data_module.insert_user(usr_props)
        else:  # Обновить существующего пользователя
            # util.log_debug('Update')
            usr_props = (usr_id, u_name, u_role, u_pwd, u_mail, u_info)
            # Проверка атрибутов
            if u_name == '':
                msg = 'Атрибут "Имя пользователя" должен быть заполнен!'
                return app.response(msg, settings.M_USERS, props=usr_props, show=True)
            if u_pwd != '':
                u_pwd = util.get_hash(u_pwd)
            data_module.update_user(usr_props)

        return app.response(module=settings.M_USERS)

    except Exception as ex:
        return app.response(f'{ex}', settings.M_USERS)


def users_new():
    return ui_module.create_users_html((), True)


def users_delete(usr_id):
    try:
        # util.log_debug(f'Нажата кнопка Delete User: usr_id={usr_id}')
        data_module.delete_user(usr_id)
        return app.response(module=settings.M_USERS)

    except Exception as ex:
        return app.response(f'{ex}', settings.M_USERS)


def users_ref_button(usr_id):
    try:
        usr = data_module.get_user_by_id_list(usr_id)
        usr_name = usr[1]
        # util.log_debug(f'Нажата кнопка Project Reference: {usr_id}; {usr_name}')

        obj_list = data_module.where_user_refs(usr_id)

        if len(obj_list) == 0:
            return app.response(f'На пользователя "{usr_name}" ссылок нет.', settings.M_USERS)
        else:
            title = f'Ссылки на пользователя "{usr_name}"'
            obj_list.insert(0, ('Проект', 'Куда ссылается', 'Участие',))  # Заголовок таблицы
            return ui_module.create_info_html(settings.INFO_TYPE_INFORMATION, obj_list, settings.M_USERS, title)

    except Exception as ex:
        return app.response(f'{ex}', settings.M_USERS)


# GET
#
def users_get():
    try:
        return ui_module.create_users_html()
    except Exception as ex:
        return app.response(f'{ex}', settings.M_USERS)


# POST
#
def users_post(values):
    try:
        for value in values:
            # Нажата одна из общих кнопок?
            html = common_buttons(value, settings.M_USERS)
            if html != '':
                return html

            # Нажата кнопка SELECT
            #
            if value == settings.TABLE_BUTTON:
                return users_select(values[value])

            # Нажата кнопка SAVE
            #
            if value == settings.SAVE_BUTTON:
                return users_save(values[value], values)

            # Нажата кнопка NEW
            #
            if value == settings.NEW_BUTTON:
                return users_new()

            # Нажата кнопка REFERENCE
            #
            if value == settings.REF_BUTTON:
                return users_ref_button(values[value])

            # Нажата кнопка HIDEINFO
            #
            if value == settings.HIDEINFO_BUTTON:
                return ui_module.create_users_html()

            # Нажата кнопка DELETE
            #
            if value == settings.DELETE_BUTTON:
                # Show confirmation dialog
                return ui_module.create_delete_confirm_html(values[value], settings.M_USERS)

            # Отклонение DELETE NO
            #
            if value == settings.DELETE_BUTTON_NO:
                return ui_module.create_users_html()

            # Подтверждение DELETE YES
            #
            if value == settings.DELETE_BUTTON_YES:
                return users_delete(values[value])

    except Exception as ex:
        return app.response(f'{ex}', settings.M_USERS)


# APPROVE BLOCK
#
# Согласовать/Отклонить
def approve(values, verdict=True):
    try:
        # Сформировать:
        tsh_id_list = []  # список идентификаторов записей отработанного времени
        tsh_id_dict = {}  # словарь пар {'tsh_id': 'to_user_id'} для оповещения
        msg = ''
        for key in values:
            if key == 'feedback':
                msg = values[key]
            if values[key] == 'on':
                tsh_id_dict[int(key.split(settings.SPLITTER)[0])] = int(key.split(settings.SPLITTER)[1])
                tsh_id_list.append(int(key.split(settings.SPLITTER)[0]))

        # Выполнить согласование
        if not tsh_id_list:
            if verdict:
                error_msg = 'Не выбрано ни одной записи на согласование'
            else:
                error_msg = 'Не выбрано ни одной записи на отклонение'
            return app.response(error_msg, settings.M_APPROVEMENT)
        else:
            # Обновить статус
            if msg == '':
                msg = 'Согласовано' if verdict else 'Отклонено'
            data_module.update_status(tuple(tsh_id_list), verdict, msg)

            # Оповестить пользователей об отклонении записей
            if ui_module.use_notifications_dialog():
                data_module.add_message(msg, app.get_c_prop(settings.C_USER_ID), tsh_id_dict)

            return ui_module.create_approvement_html()

    except Exception as ex:
        return app.response(f'{ex}', settings.M_APPROVEMENT)


# GET
#
def approvement_get():
    try:
        return ui_module.create_approvement_html()
    except Exception as ex:
        return app.response(f'{ex}', settings.M_APPROVEMENT)


def approvement_post(values):
    try:
        for value in values:
            # Нажата одна из общих кнопок?
            html = common_buttons(value, settings.M_APPROVEMENT)
            if html != '':
                return html

            # Нажата кнопка СОГЛАСОВАТЬ
            #
            if value == settings.AGREE_BUTTON:
                return approve(values, True)

            # Нажата кнопка ОТКЛОНИТЬ
            #
            if value == settings.REJECT_BUTTON:
                return approve(values, False)

            # Нажата кнопка ВЫДЕЛИТЬ ВСЁ/УБРАТЬ ВСЁ
            #
            if value == settings.ALL_FLAG_BUTTON:
                # util.log_info(f'значение кнопки реверс: {type(values[value])}')
                return ui_module.create_approvement_html(values[value])

    except Exception as ex:
        return app.response(f'{ex}', settings.M_APPROVEMENT)

