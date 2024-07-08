import traceback

import app
import pg_module
import settings
import util_module as util


# Увеличивает счетчик подключений (посещений)
def set_session_count(count):
    params = pg_module.Parameters
    params.update_param(settings.PRM_LOGIN_COUNT, count)


# Извлекает счетчик подключений (посещений)
def get_session_count():
    params = pg_module.Parameters
    param_values = params.get_param(settings.PRM_LOGIN_COUNT)
    if len(param_values) == 0:
        util.log_error(f'Parameter: {settings.PRM_LOGIN_COUNT} - not found')
        return '-1'
    else:
        value = getattr(param_values[0], settings.F_PRM_VALUE)
        # util.log_tmp(f'get_session_count: {value}')
        return value


# TIMESHEETS
#
def get_entries_by_user_name(user_name):
    entries = pg_module.Entries()
    entries_data = entries.get_entries_by_user_name(user_name)

    data = {}
    cnt = 0
    for e in entries_data:
        tsh_note = '' if settings.F_TSH_NOTE is None else settings.F_TSH_NOTE
        tsh_comment = '' if settings.F_TSH_COMMENT is None else settings.F_TSH_COMMENT
        data[str(cnt)] = {
            settings.F_TSH_STATUS: str(getattr(e, settings.F_TSH_STATUS)),
            settings.F_TSH_DATE: str(getattr(e, settings.F_TSH_DATE)),
            settings.F_PRJ_NAME: str(getattr(e, settings.F_PRJ_NAME)),
            settings.F_TSH_HOURS: str(getattr(e, settings.F_TSH_HOURS)),
            settings.F_TSH_NOTE: str(getattr(e, tsh_note)),
            settings.F_TSH_COMMENT: str(getattr(e, tsh_comment)),
            settings.F_USR_NAME: str(getattr(e, settings.F_USR_NAME)),
        }
        cnt += 1

    return data


def get_data(user_id=None, week=None):
    time_sheets_data = get_all_entries(user_id=user_id, week=week)
    return time_sheets_data


def get_entry(tsh_id=None):
    # util.log_debug(f'{prj_id}, {tsh_id}')

    tsh_dict = get_timesheet_dict(tsh_id)
    return tsh_dict


def update_entry(tsh_id=None, data=None):
    # util.log_debug(f'update_entry({project_id}, {tsh_id}, {data})')

    entries = pg_module.Entries()
    entries.update_entry(tsh_id=tsh_id, data=data)


def update_status(e_list, verdict, comment):
    entries = pg_module.Entries()
    entries.update_for_approval_status(e_list, verdict, comment)


def insert_entry(user_id=None, prj_id=None, data=None):
    entries = pg_module.Entries()
    return entries.add_entry(user_id=user_id, prj_id=prj_id, data=data)


def delete_entry(tsh_id=None):
    entries = pg_module.Entries()
    entries.delete_entry(tsh_id=tsh_id)


def get_timesheet_dict(tsh_id):
    # util.log_debug(f'get_timesheet_dict: tsh_id={tsh_id}')

    entry = pg_module.Entries()
    tsh_entry = entry.get_entry_by_id(tsh_id)
    comment = getattr(tsh_entry[0], settings.F_TSH_COMMENT)
    if comment is None:
        comment = ''

    if tsh_entry is None or len(tsh_entry) == 0:
        util.log_error(f'get_timesheet_dict: Запись id={tsh_id} не найдена в базе данных')
        return None

    return {
            settings.F_TSH_ID: tsh_id,
            settings.F_TSH_HOURS: getattr(tsh_entry[0], settings.F_TSH_HOURS),
            settings.F_TSH_NOTE: getattr(tsh_entry[0], settings.F_TSH_NOTE),
            settings.F_TSH_STATUS: getattr(tsh_entry[0], settings.F_TSH_STATUS),
            settings.F_TSH_DATE: getattr(tsh_entry[0], settings.F_TSH_DATE),
            settings.F_TSH_COMMENT: comment,
            settings.F_PRJ_NAME: getattr(tsh_entry[0], settings.F_PRJ_NAME),
            }


def get_all_entries(user_id=None, week=None):
    try:
        range_dates = util.get_dates_by_week(week)

        # Выполняем поиск тймшитов в БД
        #
        entries = pg_module.Entries()
        if entries is None:
            raise Exception('entries is None')

        entries_data = entries.get_entries(s_date=range_dates[0], e_date=range_dates[1], user_id=user_id)

        if entries_data is None:
            util.log_error(f'Data Base is not available')
            exit(0)

        if len(entries_data) == 0:
            util.log_debug(f'There are no entries for user_id: "{user_id}", dates between "{range_dates[0]}" and "{range_dates[1]}"')
            return None

        # util.log_debug(f'select: {entries_data}')

        # Возвращаем словарь
        #
        return get_all_timesheet_dict(week=week, entries=entries_data)

    except Exception as ex:
        traceback.print_exc()
        raise ex


def get_entries_for_approval_id(user_id):
    try:
        # Выполняем поиск таймшитов по идентификатору РП
        #
        entries = pg_module.Entries()
        if entries is None:
            raise Exception('entries is None')

        entries_data = entries.get_for_approval_entries_id(user_id)

        if entries_data is None:
            util.log_error(f'Data Base is not available')
            exit(0)

        if len(entries_data) == 0:
            util.log_debug(f'Нет записей для утверждения пользователем user_id={user_id}')
            return None

        # util.log_debug(f'select: {entries_data}')

        # Формируем словарь
        #
        data = {}
        for e in entries_data:
            tsh_id = str(getattr(e, settings.F_TSH_ID))
            tsh_note = '' if settings.F_TSH_NOTE is None else settings.F_TSH_NOTE
            tsh_comment = '' if settings.F_TSH_COMMENT is None else settings.F_TSH_COMMENT
            # util.log_debug(f'ТИП ДАННЫХ: {type(settings.F_TSH_COMMENT)}')
            data[tsh_id] = {
                settings.F_USR_NAME: str(getattr(e, settings.F_USR_NAME)),
                settings.F_TSH_DATE: str(getattr(e, settings.F_TSH_DATE)),
                settings.F_PRJ_NAME: str(getattr(e, settings.F_PRJ_NAME)),
                settings.F_TSH_HOURS: str(getattr(e, settings.F_TSH_HOURS)),
                settings.F_TSH_NOTE: str(getattr(e, tsh_note)),
                settings.F_TSH_COMMENT: str(getattr(e, tsh_comment)),
                settings.F_TSH_USER_ID: str(getattr(e, settings.F_TSH_USER_ID))
            }

        return data

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'Exception: {ex}')


def get_entries_for_approval_name(user_name):
    try:
        # Выполняем поиск таймшитов в БД по имени РП
        #
        entries = pg_module.Entries()
        entries_data = entries.get_for_approval_entries_name(user_name)

        if len(entries_data) == 0:
            util.log_debug(f'Нет записей для утверждения пользователем user_name={user_name}')
            return None

        # Формируем словарь
        #
        data = {}
        cnt = 0
        for e in entries_data:
            tsh_id = str(getattr(e, settings.F_TSH_ID))
            tsh_note = '' if settings.F_TSH_NOTE is None else settings.F_TSH_NOTE
            tsh_comment = '' if settings.F_TSH_COMMENT is None else settings.F_TSH_COMMENT
            data[str(cnt)] = {
                settings.F_USR_NAME: str(getattr(e, settings.F_USR_NAME)),
                settings.F_TSH_DATE: str(getattr(e, settings.F_TSH_DATE)),
                settings.F_PRJ_NAME: str(getattr(e, settings.F_PRJ_NAME)),
                settings.F_TSH_HOURS: str(getattr(e, settings.F_TSH_HOURS)),
                settings.F_TSH_NOTE: str(getattr(e, tsh_note)),
                settings.F_TSH_COMMENT: str(getattr(e, tsh_comment))
            }
            cnt += 1

        return data

    except Exception as ex:
        traceback.print_exc()
        raise ex


# Формирует словарь из курсора entries (для таблицы)
#
def get_all_timesheet_dict(week=None, entries=None):
    dates = util.list_dates_in_week(week=week)

    # Сформировать словарь дат
    #
    dates_dict = {}
    for d in dates:
        dates_dict[d] = {settings.EMPTY_ID_KEY: {}}

    # сформировать словарь проектов
    #
    time_sheets_dict = {}
    for e in entries:
        prj_id = str(getattr(e, settings.F_TSH_PRJ_ID))
        prj_name = str(getattr(e, settings.F_PRJ_NAME))

        prj_dict = {settings.F_PRJ_NAME: prj_name, settings.FLD_TSH_DICT: dates_dict.copy()}
        time_sheets_dict[prj_id] = prj_dict

    # Заполнить словари 'data': {...} для каждого проекта
    #
    for e in entries:
        tsh_id = str(getattr(e, settings.F_TSH_ID))
        prj_id = str(getattr(e, settings.F_TSH_PRJ_ID))
        status = getattr(e, settings.F_TSH_STATUS)
        note = getattr(e, settings.F_TSH_NOTE)
        if note is None: note = '-'
        hours = getattr(e, settings.F_TSH_HOURS)
        date = getattr(e, settings.F_TSH_DATE)
        comment = getattr(e, settings.F_TSH_COMMENT)
        if comment is None: comment = '-'

        tsh_dict = {tsh_id:
                        {
                            settings.F_TSH_HOURS: hours,
                            settings.F_TSH_NOTE: note,
                            settings.F_TSH_STATUS: status,
                            settings.F_TSH_COMMENT: comment
                        }
        }

        p_dict = time_sheets_dict[prj_id]
        p_dict = p_dict[settings.FLD_TSH_DICT]
        p_dict[str(date)] = tsh_dict

    # util.log_debug(f'time_sheets_dict fin: {time_sheets_dict}')
    return time_sheets_dict


# USERS
#
def get_all_users_dict(managers=False):
    users = pg_module.Users()
    if managers:
        all_users = users.get_managers()
    else:
        all_users = users.get_all_users()

    if all_users is None or len(all_users) == 0:
        util.log_error(f'get_all_users_dict: не удалось сформировать список пользователей из Базы Данных')
        return {}

    users = {}
    for user in all_users:
        usr_id = str(getattr(user, settings.F_USR_ID))
        mail = getattr(user, settings.F_USR_MAIL)
        if mail is None:
            mail = ''
        info = getattr(user, settings.F_USR_INFO)
        if info is None:
            info = ''

        u_dict = {
            settings.F_USR_ID: usr_id,
            settings.F_USR_NAME: getattr(user, settings.F_USR_NAME),
            settings.F_USR_PASSWORD: getattr(user, settings.F_USR_PASSWORD),
            settings.F_USR_ROLE: getattr(user, settings.F_USR_ROLE),
            settings.F_USR_MAIL: mail,
            settings.F_USR_INFO: info,
        }
        users[usr_id] = u_dict

    return users


def get_user_by_name_list(usr_name):
    users = pg_module.Users()
    all_users = users.get_user_by_name(usr_name)

    if all_users is None or len(all_users) == 0:
        util.log_error(f'get_user_by_name_dict: не удалось найти пользователя: {usr_name}')
        return ()

    user = all_users[0]
    return (
        getattr(user, settings.F_USR_ID),
        getattr(user, settings.F_USR_ROLE),
        getattr(user, settings.F_USR_PASSWORD)
    )


def get_users_by_name(usr_name):
    users = pg_module.Users()
    all_users = users.get_user_by_name(usr_name)

    if all_users is None or len(all_users) == 0:
        util.log_error(f'get_users_by_name: не удалось найти пользователя: {usr_name}')
        return {'info': f'Не найдено ни одного пользователя, удовлетворяющего критерию: {usr_name}'}

    data = {}
    cnt = 0
    for e in all_users:
        # tsh_comment = '' if settings.F_TSH_COMMENT is None else settings.F_TSH_COMMENT
        data[str(cnt)] = {
            settings.F_USR_NAME: str(getattr(e, settings.F_USR_NAME)),
            settings.F_USR_ROLE: str(getattr(e, settings.F_USR_ROLE)),
            settings.F_USR_MAIL: str(getattr(e, settings.F_USR_MAIL)),
            settings.F_USR_INFO: str(getattr(e, settings.F_USR_INFO)),
        }
        cnt += 1

    return data


def get_user_by_id_list(usr_id):
    users = pg_module.Users()
    all_users = users.get_user_by_id(usr_id)

    if all_users is None or len(all_users) == 0:
        util.log_error(f'get_user_by_name_dict: не удалось найти пользователя: id={usr_id}')
        return ()

    user = all_users[0]
    return (
        usr_id,
        getattr(user, settings.F_USR_NAME),
        getattr(user, settings.F_USR_ROLE),
        getattr(user, settings.F_USR_PASSWORD),
        getattr(user, settings.F_USR_MAIL),
        getattr(user, settings.F_USR_INFO),
    )


def insert_user(user_props):
    users = pg_module.Users()
    users.add_user(user_props)


def update_user(user_props):
    users = pg_module.Users()
    users.update_user(user_props)


def delete_user(usr_id):
    users = pg_module.Users()
    users.delete_user(usr_id)


def where_user_refs(usr_id):
    obj_list = []
    users = pg_module.Users()

    prj_team = users.where_user_refs_team(usr_id)
    if prj_team is not None and len(prj_team) > 0:
        for k in prj_team:
            obj_list.append([
                str(getattr(k, settings.F_PRJ_NAME)),
                f'Project ({str(getattr(k, settings.F_USR_NAME))})',
                'В команде проекта',
            ])

    prj_managers = users.where_user_refs_manager(usr_id)
    if prj_managers is not None and len(prj_managers) > 0:
        for k in prj_managers:
            obj_list.append([
                str(getattr(k, settings.F_PRJ_NAME)),
                f'Project ({str(getattr(k, settings.F_USR_NAME))})',
                'Руководитель',
            ])

    tsh_user = users.where_user_refs_timesheets(usr_id)
    if tsh_user is not None and len(tsh_user) > 0:
        for k in tsh_user:
            obj_list.append([
                str(getattr(k, settings.F_PRJ_NAME)),
                f'Timeshhets ({str(getattr(k, settings.F_TSH_DATE))}; {str(getattr(k, settings.F_TSH_STATUS))}; {str(getattr(k, settings.F_TSH_NOTE))})',
                f'Исполнитель',
            ])

    return obj_list


# PROJECTS
#
def get_all_projects_dict(usr_id, all_p=True):
    projects = pg_module.Projects()

    if all_p:
        all_projects = projects.get_all_projects(usr_id)
    else:
        all_projects = projects.get_own_projects(usr_id)

    if all_projects is None:
        util.log_error(f'get_all_projects: не удалось сформировать список проектов из Базы Данных')
        return None

    # Определить текущую неделю
    week = app.get_c_prop(settings.C_WEEK)
    # util.log_debug(f'get_all_projects_dict: current week={week}')

    projects = {}
    for prj in all_projects:
        prj_id = str(getattr(prj, settings.F_PRJ_ID))
        manager_id = str(getattr(prj, settings.F_PRJ_MANAGER_ID))
        prj_name = str(getattr(prj, settings.F_PRJ_NAME))
        start_date = '' if getattr(prj, settings.F_PRJ_START_DATE) is None else str(getattr(prj, settings.F_PRJ_START_DATE))
        end_date = '' if getattr(prj, settings.F_PRJ_END_DATE) is None else str(getattr(prj, settings.F_PRJ_END_DATE))
        prj_org = '' if getattr(prj, settings.F_PRJ_ORG) is None else str(getattr(prj, settings.F_PRJ_ORG))

        # Фильтр на соответствие дат проекта с текущей неделей
        #
        if not all_p or util.is_project_in_week(week, (getattr(prj, settings.F_PRJ_START_DATE), getattr(prj, settings.F_PRJ_END_DATE))):
            p_dict = {
                settings.F_PRJ_MANAGER_ID: manager_id,
                settings.F_PRJ_NAME: prj_name,
                settings.F_PRJ_START_DATE: start_date,
                settings.F_PRJ_END_DATE: end_date,
                settings.F_PRJ_ORG: prj_org,
            }
            projects[prj_id] = p_dict
        # else:
        #     util.log_debug(f'skip project: prj_name={prj_name}')

    return projects


def get_projects_by_name(prj_name):
    projects = pg_module.Projects
    projects_data = projects.get_projects_by_name(prj_name)

    data = {}
    cnt = 0
    for e in projects_data:
        # tsh_note = '' if settings.F_TSH_NOTE is None else settings.F_TSH_NOTE
        # tsh_comment = '' if settings.F_TSH_COMMENT is None else settings.F_TSH_COMMENT
        data[str(cnt)] = {
            settings.F_PRJ_ID: str(getattr(e, settings.F_PRJ_ID)),
            settings.F_USR_NAME: str(getattr(e, settings.F_USR_NAME)),
            settings.F_PRJ_NAME: str(getattr(e, settings.F_PRJ_NAME)),
            settings.F_PRJ_START_DATE: str(getattr(e, settings.F_PRJ_START_DATE)),
            settings.F_PRJ_END_DATE: str(getattr(e, settings.F_PRJ_END_DATE)),
            settings.F_PRJ_ORG: str(getattr(e, settings.F_PRJ_ORG)),
        }
        cnt += 1

    return data


def get_project_by_id_list(prj_id):
    projects = pg_module.Projects()
    all_projects = projects.get_project_by_id(prj_id)

    if all_projects is None or len(all_projects) == 0:
        util.log_error(f'get_project_by_id_list: не удалось найти проект: id={prj_id}')
        return ()

    project = all_projects[0]
    return (
        getattr(project, settings.F_PRJ_ID),
        getattr(project, settings.F_PRJ_MANAGER_ID),
        getattr(project, settings.F_PRJ_NAME),
        getattr(project, settings.F_PRJ_START_DATE),
        getattr(project, settings.F_PRJ_END_DATE),
        getattr(project, settings.F_PRJ_ORG),
    )


def get_project_team_list(prj_id):
    projects = pg_module.Projects()
    team = projects.get_project_team(prj_id)

    team_list = []
    if team is None or len(team) == 0:
        util.log_debug(f'get_project_team_list: команда проекта id={prj_id} не определена')
        return team_list

    for t in team:
        team_list.append(str(getattr(t, settings.F_PTM_USR_ID)))
    return team_list


def insert_project(prj_props, team_list):
    projects = pg_module.Projects()
    projects.add_project(prj_props, team_list)


def update_project(prj_props, team_list):
    projects = pg_module.Projects()
    projects.update_project(prj_props, team_list)


def delete_project(prj_id):
    projects = pg_module.Projects()
    projects.delete_project(prj_id)

def where_project_refs(prj_id):
    projects = pg_module.Projects()
    entries = projects.where_project_refs(prj_id)

    entries_list = []
    if entries is None or len(entries) == 0:
        util.log_debug(f'where_project_refs: на проект id={prj_id} нет ссылок')
        return entries_list

    for e in entries:
        entries_list.append([
            str(getattr(e, settings.F_TSH_DATE)),
            str(getattr(e, settings.F_TSH_STATUS)),
            str(getattr(e, settings.F_TSH_NOTE)),
            str(getattr(e, settings.F_USR_NAME)),
        ])

    return entries_list


# MESSAGES
#
def set_read_message(msg_id):
    msgs = pg_module.Messages
    msgs.set_read(msg_id)


def add_message(msg, from_usr_id, data):
    msgs = pg_module.Messages
    msgs.add_message(msg, from_usr_id, data)


def get_messages(to_usr_id):
    msgs = pg_module.Messages
    return msgs.get_messages(to_usr_id)


def get_timesheet_messages(tsh_id):
    msgs = pg_module.Messages
    cursor = msgs.get_timesheet_messages(tsh_id)
    msg_list = []
    for r in cursor:
        msg_list.append(
            (
                str(getattr(r, settings.F_MSG_FROM_USER)),
                str(getattr(r, settings.F_MSG_TO_USER)),
                str(getattr(r, settings.F_MSG_CREATION_DATE)),
                str(getattr(r, settings.F_MSG_TEXT)),
            )
        )
    return msg_list


def get_unread_count(to_usr_id):
    msgs = pg_module.Messages
    return msgs.get_unread_count(to_usr_id)


