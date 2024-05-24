import datetime
import traceback

import psycopg2
from psycopg2.extras import NamedTupleCursor

import settings
import ui_module
import util_module as util

DB_CONNECT = None

if settings.IS_WINDOWS:
    # PG_HOST = '192.168.62.71'  # VM office
    PG_HOST = '192.168.1.219'  # VM home
    # PG_HOST = '127.0.0.1'    # Docker Desktop
else:
    PG_HOST = 'localhost'      # Cloud

PG_PORT = '5432'
PG_DATABASE = 'timesheets_db'
PG_USER = 'timesheets_user'
PG_PASSWORD = 'infodba'

# Создать соединение с БД, если еще не установлено
#
def get_connect():
    global DB_CONNECT

    try:

        if DB_CONNECT is None:
            util.log_info('DB_Connect...')
            DB_CONNECT = psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DATABASE, user=PG_USER, password=PG_PASSWORD)

        #0 util.log_debug(f'TRANSACTION_STATUS_IDLE={psycopg2.extensions.TRANSACTION_STATUS_IDLE}')
        #1 util.log_debug(f'TRANSACTION_STATUS_ACTIVE={psycopg2.extensions.TRANSACTION_STATUS_ACTIVE}')
        #2 util.log_debug(f'TRANSACTION_STATUS_INTRANS={psycopg2.extensions.TRANSACTION_STATUS_INTRANS}')
        #3 util.log_debug(f'TRANSACTION_STATUS_INERROR={psycopg2.extensions.TRANSACTION_STATUS_INERROR}')
        #4 util.log_debug(f'TRANSACTION_STATUS_UNKNOWN={psycopg2.extensions.TRANSACTION_STATUS_UNKNOWN}')

        # util.log_debug(f'DB_CONNECT status: {DB_CONNECT.status}; transaction status: {DB_CONNECT.get_transaction_status()}')
        # util.log_debug(f'session={DB_CONNECT}, PID={DB_CONNECT.get_backend_pid()}, status={DB_CONNECT.closed}')

        # Проверить на зависшие транзакции
        #
        if DB_CONNECT.get_transaction_status() == 3 or DB_CONNECT.get_transaction_status() == 4:
            util.log_error(f'DB_CONNECT transaction status: {DB_CONNECT.get_transaction_status()} - rollback()!!!')
            DB_CONNECT.rollback()

        return DB_CONNECT

    except Exception as ex:
        DB_CONNECT = None
        util.log_error(f'Can`t establish connection to database {ex}: host={PG_HOST}, port={PG_PORT}, dbname={PG_DATABASE}, user={PG_USER}')
        raise ex


# Проверка соединения с БД
#
def test_connection():
    global DB_CONNECT
    # util.log_debug('Test connection...')

    try:
        get_connect()
        return ''
    except Exception as ex:
        DB_CONNECT = None
        msg = 'Нет подключения к Базе Данных!', f'{ex}'
        return ui_module.create_info_html(i_type=settings.INFO_TYPE_ERROR, msg=msg)


class Entries:

    SQL_GET_ENTRY_BY_ID = f'Select {settings.F_TSH_ALL_ID} From ts_entries Where {settings.F_TSH_ID} = %s'

    SQL_INSERT_ENTRY = f'Insert INTO ts_entries ({settings.F_TSH_ALL}) \
                       VALUES (%s, %s, %s, %s, %s, %s, %s)\
                       '

    SQL_DELETE_ENTRY = f'Delete From ts_entries Where {settings.F_TSH_ID} = %s'

    SQL_ALL_ENTRIES = f'Select {settings.F_TSH_ALL_ID}, {settings.F_PRJ_NAME} \
                       From ts_entries, ts_projects \
                       Where {settings.F_TSH_DATE} >= %s and {settings.F_TSH_DATE} <= %s \
                       And {settings.F_TSH_USER_ID} = %s \
                       And {settings.F_TSH_PRJ_ID} = {settings.F_PRJ_ID} \
                       Order by {settings.F_PRJ_NAME}\
                      '

    SQL_UPDATE_ENTRY = f'Update ts_entries \
                        Set {settings.F_TSH_HOURS} = %s, {settings.F_TSH_NOTE} = %s, {settings.F_TSH_STATUS} = %s, {settings.F_TSH_COMMENT} = %s \
                        Where {settings.F_TSH_ID} = %s\
                       '

    SQL_FOR_APPROVAL_ENTRIES = f'Select {settings.F_TSH_ALL_ID}, {settings.F_PRJ_NAME}, {settings.F_USR_NAME} \
                                From ts_entries, ts_projects, ts_users \
                                Where {settings.F_TSH_STATUS} = \'{settings.IN_APPROVE_STATUS}\' \
                                And {settings.F_TSH_PRJ_ID} = {settings.F_PRJ_ID} \
                                And {settings.F_TSH_USER_ID} = {settings.F_USR_ID} \
                                And {settings.F_PRJ_MANAGER_ID} = %s'

    SQL_UPDATE_STATUS = f'Update ts_entries \
                        Set {settings.F_TSH_STATUS} = %s, {settings.F_TSH_COMMENT} = %s \
                        Where {settings.F_TSH_ID} in %s\
                       '
    SQL_GET_ENTRIES_BY_USER_NAME = (f'Select {settings.F_TSH_COMMENT}, {settings.F_TSH_DATE}, {settings.F_TSH_HOURS}, '
                                    f'{settings.F_TSH_NOTE}, {settings.F_TSH_STATUS}, {settings.F_PRJ_NAME} '
                                    f'From ts_entries e, ts_users u, ts_projects p '
                                    f'Where {settings.F_USR_NAME} = %s '
                                    f'And {settings.F_TSH_USER_ID} = {settings.F_USR_ID} '
                                    f'And {settings.F_TSH_PRJ_ID} = {settings.F_PRJ_ID}'
                                    )

    @classmethod
    def get_entries(cls, s_date=None, e_date=None, user_id=None):
        try:
            # sql = "select *, to_char(date, 'YYYY-MM-DD') as d from ts_entries"
            if s_date is None:
                raise Exception('s_date is None')
            if e_date is None:
                raise Exception('e_date is None')
            if user_id is None:
                raise Exception('user_id is None')

            # util.log_debug(f'select: for user_id={user_id} in ({s_date}, {e_date})')
            conn = get_connect()

            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_ALL_ENTRIES, (s_date, e_date, user_id))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on Select Entries for user id: {user_id} ({ex})')
            raise ex

    @classmethod
    def get_entry_by_id(cls, tsh_id=None):
        try:
            if tsh_id is None:
                raise Exception('entry id is None')

            # util.log_debug(f'get entry by id: {tsh_id}')

            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_GET_ENTRY_BY_ID, (tsh_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on Select Entry for id {tsh_id}: ({ex})')
            raise ex

    @classmethod
    def add_entry(cls, user_id=None, prj_id=None, data=None):
        # util.log_debug(f'add_entry {prj_id}, {user_id}, {data}')

        hours = data.get(settings.F_TSH_HOURS)
        status = data.get(settings.F_TSH_STATUS)
        note = data.get(settings.F_TSH_NOTE)
        date = data.get(settings.F_TSH_DATE)
        comment = data.get(settings.F_TSH_COMMENT)

        conn = get_connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                curs.execute(cls.SQL_INSERT_ENTRY, (user_id, prj_id, hours, status, note, date, comment))
            except Exception as ex:
                util.log_error(f'Error on Insert Entry for prj_id "{prj_id}": ({ex})')
                curs.execute('rollback')
                raise ex

            curs.execute('commit')

    @classmethod
    def update_entry(cls, tsh_id=None, data=None):
        # parsing data
        #
        hours = data.get(settings.F_TSH_HOURS)
        note = data.get(settings.F_TSH_NOTE)
        status = data.get(settings.F_TSH_STATUS)
        comment = data.get(settings.F_TSH_COMMENT)

        # util.log_debug(f'update entry: {tsh_id}')
        conn = get_connect()

        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                curs.execute(cls.SQL_UPDATE_ENTRY, (hours, note, status, comment, tsh_id))
            except Exception as ex:
                util.log_error(f'Error on Update Entry for id {tsh_id}: ({ex})')
                curs.execute('rollback')
                raise ex

            curs.execute('commit')

    @classmethod
    def delete_entry(cls, tsh_id):
        util.log_debug(f'delete_entry: {tsh_id}')

        conn = get_connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                curs.execute(cls.SQL_DELETE_ENTRY, (tsh_id,))
            except Exception as ex:
                util.log_error(f'Error on Delete Entry for tsh_id "{tsh_id}": ({ex})')
                curs.execute('rollback')
                raise ex

            curs.execute('commit')

    @classmethod
    def get_for_approval_entries(cls, user_id=None):
        try:
            # util.log_debug(f'get_for_approval_entries: for user_id={user_id}')
            if user_id is None:
                raise Exception('user_id is None')

            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_FOR_APPROVAL_ENTRIES, (user_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on Select for approval Entries for user_id={user_id}: ({ex})')
            raise ex

    @classmethod
    def update_for_approval_status(cls, e_list, verdict, comment):
            # util.log_debug(f'update_for_approval_status: for list={e_list} with verdict={verdict}')
            if e_list is None:
                raise Exception('list of entries is None')

            if verdict:
                status = f'{settings.APPROVED_STATUS}'
            else:
                status = f'{settings.REJECTED_STATUS}'

            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                try:
                    curs.execute(cls.SQL_UPDATE_STATUS, (status, comment, e_list))
                except Exception as ex:
                    util.log_error(f'Error on Update for approval Entries for list={e_list}, verdict={verdict}: ({ex})')
                    curs.execute('rollback')
                    raise ex

                curs.execute('commit')

    @classmethod
    def get_entries_by_user_name(cls, user_name=None):
        try:
            # util.log_debug(f'get_entries_by_user_name: for user_name={user_name}')
            if user_name is None:
                raise Exception('user_name is None')

            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_GET_ENTRIES_BY_USER_NAME, (user_name,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on Select Entries for user_name={user_name}: ({ex})')
            raise ex



class Projects:

    SQL_GET_PROJECT_ID = f'Select nextval(\'project_id\'::regclass) as {settings.F_PRJ_ID}'

    SQL_ALL_PROJECTS = (f'Select {settings.F_PRJ_ALL_ID} From ts_projects, ts_project_teams '
                        f'Where {settings.F_PRJ_ID} = {settings.F_PTM_PRJ_ID} '
                        f'And {settings.F_PTM_USR_ID} = %s '
                        f'Order by {settings.F_PRJ_NAME}')

    SQL_OWN_PROJECTS = (f'Select {settings.F_PRJ_ALL_ID} From ts_projects '
                        f'Where {settings.F_PRJ_MANAGER_ID} = %s '
                        f'Order by {settings.F_PRJ_NAME}')

    SQL_PROJECT_BY_ID = (f'Select {settings.F_PRJ_ALL_ID} From ts_projects '
                         f'Where {settings.F_PRJ_ID} = %s')

    SQL_INSERT_PROJECT = f'Insert INTO ts_projects ({settings.F_PRJ_ALL_ID}) VALUES (%s, %s, %s, %s, %s, %s)'

    SQL_UPDATE_PROJECT = f'Update ts_projects \
                        Set {settings.F_PRJ_MANAGER_ID} = %s, {settings.F_PRJ_NAME} = %s, {settings.F_PRJ_START_DATE} = %s, {settings.F_PRJ_END_DATE} = %s, {settings.F_PRJ_ORG} = %s \
                        Where {settings.F_PRJ_ID} = %s'

    SQL_DELETE_PROJECT = f'Delete From ts_projects Where {settings.F_PRJ_ID} = %s'

    SQL_GET_TEAM = f'Select {settings.F_PTM_USR_ID} From ts_project_teams Where {settings.F_PTM_PRJ_ID} = %s'
    SQL_DELETE_TEAM = f'Delete From ts_project_teams Where {settings.F_PTM_PRJ_ID} = %s'
    SQL_INSERT_TEAM = f'Insert INTO ts_project_teams ({settings.F_PTM_PRJ_ID}, {settings.F_PTM_USR_ID}) VALUES (%s, %s)'

    SQL_ENTRIES_BY_PROJECT_ID = (f'Select {settings.F_TSH_DATE}, {settings.F_TSH_STATUS}, {settings.F_TSH_NOTE}, {settings.F_USR_NAME} '
                                 f'From ts_entries, ts_users '
                                 f'Where {settings.F_TSH_PRJ_ID} = %s '
                                 f'And {settings.F_TSH_USER_ID} = {settings.F_USR_ID}')

    @classmethod
    def get_all_projects(cls, usr_id):
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_ALL_PROJECTS, (usr_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting all projects: ({ex})')
            raise ex

    @classmethod
    def get_own_projects(cls, usr_id):
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_OWN_PROJECTS, (usr_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting own projects: ({ex})')
            raise ex

    @classmethod
    def get_project_by_id(cls, prj_id):
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_PROJECT_BY_ID, (prj_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting project by id={prj_id}: ({ex})')
            raise ex

    @classmethod
    def get_project_team(cls, prj_id):
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_GET_TEAM, (prj_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting project team by id={prj_id}: ({ex})')
            raise ex

    @classmethod
    def add_project(cls, prj_props, team_list):
        util.log_debug(f'add_project: prj_props={prj_props}')
        conn = get_connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                # Get project id
                curs.execute(cls.SQL_GET_PROJECT_ID)
                prj_id = getattr(curs.fetchall()[0], settings.F_PRJ_ID)
                # Insert project
                curs.execute(cls.SQL_INSERT_PROJECT, (prj_id, prj_props[1], prj_props[2], prj_props[3], prj_props[4], prj_props[5]))
                # Update team
                curs.execute(cls.SQL_DELETE_TEAM, (prj_id, ))  # delete all team
                for t in team_list:
                    # util.log_error(f'team_list={t}')
                    curs.execute(cls.SQL_INSERT_TEAM, (prj_id, t))  # insert prj_id, usr_id

            except Exception as ex:
                util.log_error(f'Error on Insert project: {prj_props[1]}: ({ex})')
                curs.execute('rollback')
                raise ex

            curs.execute('commit')

    @classmethod
    def update_project(cls, prj_props, team_list):
        # util.log_debug(f'update_project: prj_props={prj_props}')
        conn = get_connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                prj_id = prj_props[0]
                # Update project
                curs.execute(cls.SQL_UPDATE_PROJECT, (prj_props[1], prj_props[2], prj_props[3], prj_props[4], prj_props[5], prj_id))
                # Update team
                curs.execute(cls.SQL_DELETE_TEAM, (prj_id, ))  # delete all team
                for t in team_list:
                    # util.log_debug(f'team_list={t}')
                    curs.execute(cls.SQL_INSERT_TEAM, (prj_id, t))  # insert prj_id, usr_id

            except Exception as ex:
                util.log_error(f'Error on Update prj_id: {prj_props[0]}: ({ex})')
                curs.execute('rollback')
                raise ex

            curs.execute('commit')  #commit

    @classmethod
    def delete_project(cls, prj_id):
        # util.log_debug(f'delete_project: prj_id={prj_id}')
        conn = get_connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                curs.execute(cls.SQL_DELETE_PROJECT, (prj_id,))
            except Exception as ex:
                util.log_error(f'Error on Delete Project prj_id={prj_id}: ({ex})')
                curs.execute('rollback')
                raise ex

            curs.execute('commit')

    @classmethod
    def where_project_refs(cls, prj_id):
        try:
            if prj_id is None:
                raise Exception('project id is None')

            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_ENTRIES_BY_PROJECT_ID, (prj_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on Select Entry by project id {prj_id}: ({ex})')
            raise ex


class Users:

    SQL_ALL_USERS = f'Select {settings.F_USR_ALL_ID} From ts_users Order by {settings.F_USR_NAME}'

    SQL_MANAGERS = f'Select {settings.F_USR_ALL_ID} ' \
                   f'From ts_users ' \
                   f'Where {settings.F_USR_ROLE} in (\'{settings.R_MANAGER}\', \'{settings.R_ADMIN}\') ' \
                   f'Order by {settings.F_USR_NAME}'

    SQL_USER_BY_NAME = f'Select {settings.F_USR_ALL_ID} From ts_users Where {settings.F_USR_NAME} = %s'

    SQL_USER_BY_ID = f'Select {settings.F_USR_ALL_ID} From ts_users Where {settings.F_USR_ID} = %s'

    SQL_INSERT_USER = f'Insert INTO ts_users ({settings.F_USR_ALL}) VALUES (%s, %s, %s, %s, %s)'

    SQL_UPDATE_USER = f'Update ts_users \
                        Set {settings.F_USR_NAME} = %s, {settings.F_USR_ROLE} = %s, {settings.F_USR_MAIL} = %s, {settings.F_USR_INFO} = %s  \
                        Where {settings.F_USR_ID} = %s'

    SQL_UPDATE_USER_PWD = f'Update ts_users \
                        Set {settings.F_USR_NAME} = %s, {settings.F_USR_ROLE} = %s, {settings.F_USR_PASSWORD} = %s, {settings.F_USR_MAIL} = %s, {settings.F_USR_INFO} = %s  \
                        Where {settings.F_USR_ID} = %s'

    SQL_DELETE_USER = f'Delete From ts_users Where {settings.F_USR_ID} = %s'

    SQL_USER_REF_TEAM = f'Select {settings.F_PRJ_ALL_ID}, {settings.F_USR_NAME} ' \
                        f'From ts_project_teams, ts_projects, ts_users ' \
                        f'Where {settings.F_PTM_USR_ID} = %s ' \
                        f'And {settings.F_PTM_PRJ_ID} = {settings.F_PRJ_ID} ' \
                        f'And {settings.F_PRJ_MANAGER_ID} = {settings.F_USR_ID}'

    SQL_USER_REF_MANAGER = f'Select {settings.F_PRJ_ALL_ID}, {settings.F_USR_NAME} ' \
                           f'From ts_projects, ts_users ' \
                           f'Where {settings.F_PRJ_MANAGER_ID} = %s ' \
                           f'And {settings.F_PRJ_MANAGER_ID} = {settings.F_USR_ID}'

    SQL_USER_REF_TIMESHEET = f'Select {settings.F_TSH_ALL}, {settings.F_PRJ_NAME} ' \
                             f'From ts_entries, ts_projects ' \
                             f'Where {settings.F_TSH_USER_ID} = %s ' \
                             f'And {settings.F_TSH_PRJ_ID} = {settings.F_PRJ_ID}'

    @classmethod
    def get_all_users(cls):
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_ALL_USERS)
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting all users: ({ex})')
            raise ex

    @classmethod
    def get_managers(cls):
        try:
            # util.log_debug(f'SQL={cls.SQL_MANAGERS}')
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_MANAGERS)
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting managers: ({ex})')
            raise ex

    @classmethod
    def get_user_by_name(cls, usr_name):
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_USER_BY_NAME, (usr_name,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting user by name={usr_name}: ({ex})')
            raise ex

    @classmethod
    def get_user_by_id(cls, usr_id):
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_USER_BY_ID, (usr_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting user by id={usr_id}: ({ex})')
            raise ex

    @classmethod
    def add_user(cls, usr_props):
        util.log_debug(f'add_user: usr_props={usr_props}')
        conn = get_connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                curs.execute(cls.SQL_INSERT_USER, (usr_props[1], usr_props[2], usr_props[3], usr_props[4], usr_props[5]))
            except Exception as ex:
                util.log_error(f'Error on Insert user: {usr_props[1]}: ({ex})')
                curs.execute('rollback')
                raise ex

            curs.execute('commit')

    @classmethod
    def update_user(cls, usr_props):
        # util.log_debug(f'update_user: usr_props={usr_props}')
        conn = get_connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                if usr_props[3] == '':  # Обновление без пароля
                    # util.log_debug(f'Обновление без пароля: {usr_props}')
                    curs.execute(cls.SQL_UPDATE_USER, (usr_props[1], usr_props[2], usr_props[4], usr_props[5], usr_props[0]))
                else:                   # Обновление с паролем
                    # util.log_debug(f'Обновление c паролем: {usr_props}')
                    curs.execute(cls.SQL_UPDATE_USER_PWD, (usr_props[1], usr_props[2], usr_props[3], usr_props[4], usr_props[5], usr_props[0]))
            except Exception as ex:
                util.log_error(f'Error on Update usr_id: {usr_props[0]}: ({ex})')
                curs.execute('rollback')
                raise ex

            curs.execute('commit')

    @classmethod
    def delete_user(cls, usr_id):
        # util.log_debug(f'delete_user: usr_id={usr_id}')
        conn = get_connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                curs.execute(cls.SQL_DELETE_USER, (usr_id,))
            except Exception as ex:
                util.log_error(f'Error on Delete User usr_id={usr_id}: ({ex})')
                curs.execute('rollback')
                raise ex

            curs.execute('commit')

    @classmethod
    def where_user_refs_team(cls, usr_id):
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_USER_REF_TEAM, (usr_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting user references in team for user id={usr_id}: ({ex})')
            raise ex

    @classmethod
    def where_user_refs_manager(cls, usr_id):
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_USER_REF_MANAGER, (usr_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting user references as manager for user id={usr_id}: ({ex})')
            raise ex

    @classmethod
    def where_user_refs_timesheets(cls, usr_id):
        # util.log_debug(f'where_user_refs_timesheets: usr_id={usr_id}, sql={cls.SQL_USER_REF_TIMESHEET}')
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_USER_REF_TIMESHEET, (usr_id,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting user references in timesheets for user id={usr_id}: ({ex})')
            raise ex


class Parameters:

    SQL_GET_PARAM_VALUE = f'Select {settings.F_PRM_VALUE} From ts_parameters Where {settings.F_PRM_NAME} = %s'

    SQL_UPDATE_PARAM = f'Update ts_parameters Set {settings.F_PRM_VALUE} = %s Where {settings.F_PRM_NAME} = %s'

    @classmethod
    def get_param(cls, p_name):
        try:
            conn = get_connect()
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(cls.SQL_GET_PARAM_VALUE, (p_name,))
                return curs.fetchall()

        except Exception as ex:
            util.log_error(f'Error on getting param: {p_name}: ({ex})')
            raise ex

    @classmethod
    def update_param(cls, p_name, p_value):
        util.log_debug(f'update_param: {p_name}={p_value}')
        conn = get_connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                curs.execute(cls.SQL_UPDATE_PARAM, (p_value, p_name))
            except Exception as ex:
                util.log_error(f'Error on Update param: {p_name}={p_value}: ({ex})')
                curs.execute('rollback')
                raise ex

            curs.execute('commit')






# Отладка
#
if __name__ == '__main__':
    util.log_debug(f'{__name__}')
    try:
        pass

    except Exception as ex:
        traceback.print_exc()
        util.log_error(f'Exception: {ex}')
