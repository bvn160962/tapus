#
# Для отладки - вход без регистрации
DBG_DO_LOGIN = True
DBG_USER_ID = 102
DBG_USER_NAME = 'user'
DBG_USER_ROLE = 'Administrator'

SHOW_EMPTY_PROJECTS = True

# Тип сообщения
MSG_TYPE_ERR = 'Error'
MSG_TYPE_INFO = 'Info'


# Для отправки сообщения без timesheet (фиктивный tsh_id)
# Необходим из-за ограничения целостности в таблице ts_messages
INTERNAL_USER_ID = '100'
INTERNAL_PROJECT_ID = '100'
INTERNAL_TIMESHEET_ID = '100'
INTERNAL_NAME = 'internal'  # Имя для проекта и пользователя, используемых для служебных целей

# Длительность ожидания ответа при проверке существования сессии Socket в секундах
SOCKET_TEST_TIMEOUT = 0.5

# Использовать систему оповещения
USE_NOTIFICATIONS = True
NOTIFICATIONS_DIALOG_ID = 'notifications_dialog_id'
NOTIFICATIONS_DIALOG_HEADER_ID = 'notifications_dialog_header_id'
NOTIFICATIONS_DIALOG_CLOSE_BTN_ID = 'notifications_dialog_close_btn_id'
NOTIFICATIONS_BOTTOM_LINE_ID = 'notifications_bottom_line_id'
NOTIFICATIONS_RIGHT_LINE_ID = 'notifications_right_line_id'
NOTIFICATIONS_CORNER_LINE_ID = 'notifications_corner_line_id'
NOTIFICATIONS_BOUNDARY_BOX = (NOTIFICATIONS_BOTTOM_LINE_ID, NOTIFICATIONS_RIGHT_LINE_ID, NOTIFICATIONS_CORNER_LINE_ID)


# REST API
# Получение списка отработанного времени
API_TIMESHEETS = '/api/timesheets/'
API_TIMESHEETS_BY_USER = f'{API_TIMESHEETS}<user_name>'

# Получение списка проектов
API_PROJECTS = '/api/projects/'
API_PROJECTS_BY_NAME = f'{API_PROJECTS}<project_name>'

# Получение списка записей на согласование
API_APPROVEMENTS = '/api/approvements/'
API_APPROVEMENTS_BY_MANAGER = f'{API_APPROVEMENTS}<manager_name>'

# Получение списка пользователей
API_USERS = '/api/users/'
API_USERS_BY_NAME = f'{API_USERS}<user_name>'

# Использовать авторизацию при вызове API запросов
API_USE_AUTHORIZATION = True
API_AUTHORIZATION_HEADER = 'Authorization'
API_AUTHORIZATION_TOKEN = 'Y8OxltVburAc95YN92ln/2r9XUVmiQusLigbFvOJQ!pTRVEr6RjCwwPfBbPxsmcM'

# Показывать диалог подтверждения удаления в виде модального окна
USE_MODAL_CONFIRMATION_DIALOG = True
CONFIRMATION_DIALOG_ID = 'confirm_dialog_id'
CONFIRMATION_HEADER_ID = 'confirm_header_id'
CONFIRMATION_MESSAGE_ID = 'confirm_message_id'
CONFIRMATION_BOTTOM_LINE_ID = 'confirm_bottom_line_id'
CONFIRMATION_RIGHT_LINE_ID = 'confirm_right_line_id'
CONFIRMATION_CORNER_LINE_ID = 'confirm_corner_line_id'
CONFIRMATION_BOUNDARY_BOX = (CONFIRMATION_BOTTOM_LINE_ID, CONFIRMATION_RIGHT_LINE_ID, CONFIRMATION_CORNER_LINE_ID)

# Показывать сообщение в виде модального окна
USE_MESSAGE_DIALOG = True
MESSAGE_DIALOG_ID = 'message_dialog_id'
MESSAGE_DIALOG_TEXT_ID = 'message_dialog_text_id'
MESSAGE_DIALOG_TITLE_ID = 'message_dialog_title_id'
MESSAGE_DIALOG_HEADER_ID = 'message_dialog_header_id'
MESSAGE_DIALOG_CLOSE_BUTTON_ID = 'message_dialog_ok_btn_id'
MESSAGE_BOTTOM_LINE_ID = 'message_bottom_line_id'
MESSAGE_RIGHT_LINE_ID = 'message_right_line_id'
MESSAGE_CORNER_LINE_ID = 'message_corner_line_id'
MESSAGE_BOUNDARY_BOX = (MESSAGE_BOTTOM_LINE_ID, MESSAGE_RIGHT_LINE_ID, MESSAGE_CORNER_LINE_ID)

# Имя ключа куки для передачи сообщения
COOKIE_SHOW_MESSAGE = 'showMessage'


# SESSION
S_PERMANENT = False
S_LIFETIME_IN_MINUTES = 15

# Список ролей
#
R_ADMIN = 'Administrator'
R_MANAGER = 'Manager'
R_USER = 'User'
R_LIST = {
    R_ADMIN: 'Администратор',
    R_MANAGER: 'Руководитель проектов',
    R_USER: 'Исполнитель',
}

# Регистрация модулей
#
M_TIMESHEETS = 'timesheets'
M_APPROVEMENT = 'approvement'
M_USERS = 'users'
M_PROJECTS = 'projects'
M_LOGIN = 'login'

M_NAME = 'name'
M_URL = 'url'
M_TITLE = 'title'
M_HTML = 'create_html'

MODULES = {
    M_TIMESHEETS: {M_NAME: 'Табель', M_URL: '/timesheets', M_TITLE: 'Учет отработанного времени', M_HTML: 'create_timesheet_html'},
    M_APPROVEMENT: {M_NAME: 'Согласование', M_URL: '/approvement', M_TITLE: 'Согласование отработанного времени', M_HTML: 'create_approvement_html'},
    M_USERS: {M_NAME: 'Пользователи', M_URL: '/users', M_TITLE: 'Управление пользователями', M_HTML: 'create_users_html'},
    M_PROJECTS: {M_NAME: 'Проекты', M_URL: '/projects', M_TITLE: 'Управление проектами', M_HTML: 'create_projects_html'},
    M_LOGIN: {M_NAME: 'Регистрация', M_URL: '/login/<module>', M_TITLE: 'Регистрация', M_HTML: 'create_login_html'}
}

# Стили для тэгов
#
ENTER_DISABLE = 'onkeydown="return skip_enter(event);"'  # Предотвращение нажатия Enter на Input (через функцию в main.js)
# ENTER_DISABLE = 'onkeydown="if(event.keyCode==13){return false;}"'  # Предотвращение нажатия Enter на Input (напрямую)
TAG_INPUT = f'input {ENTER_DISABLE}'

TAG_BUTTON_TABLE = 'button class="btn-t"'  # Кнопка в таблице timesheets
TAG_BUTTON_TABLE_WEEKEND = 'button class="btn-t btn-t-weekend"'  # Кнопка в таблице timesheets выходной день
TAG_BUTTON_TABLE_EDIT = 'button class="btn-t btn-t-edit"'  # Кнопка в таблице timesheets статус Edit
TAG_BUTTON_TABLE_IN_APPROVE = 'button class="btn-t btn-t-in_approve"'  # Кнопка в таблице timesheets статус In-Approve
TAG_BUTTON_TABLE_APPROVED = 'button class="btn-t btn-t-approved"'  # Кнопка в таблице timesheets статус Approved
TAG_BUTTON_TABLE_REJECTED = 'button class="btn-t btn-t-rejected"'  # Кнопка в таблице timesheets статус Rejected

TAG_TD_CENTER = 'td align=center'  # Ячейка под заголовки: атрибутов в timesheets info и кнопки в таблице timesheets
TAG_A_HEAD = 'a class="a-head"'  # Названия атрибутов в timesheets info
TAG_A_HEAD_REQ = 'a class="a-head required"'  # Названия обязатедьного атрибутов в timesheets info

TAG_TD_SELECTED = 'td align=center class=td-selected'  # Ячейка под нажатую кнопку в таблице timesheets
TAG_TD_BTN_HEADER = 'td align="center" class=td-header'  # Ячейка под заголовки в таблице timesheets
TAG_A_HEADER_P = 'a class=a-prj-head'  # Заголовок "Проекты" в таблице timesheets

# Типы информационных сообщений
#
INFO_TYPE_INFORMATION = 'Информация'
INFO_TYPE_WARNING = 'Предупреждение'
INFO_TYPE_ERROR = 'Ошибка'

# Переменные кэша
#
C_USER_ID = 'c_user_id'
C_USER_NAME = 'c_user_name'
C_USER_ROLE = 'c_user_role'
C_PROJECT_ID = 'c_project_id'
C_TIMESHEET_ID = 'c_timesheet_id'
C_DATE = 'c_date'
C_WEEK = 'c_week'
C_TSH_BTN_VALUE = 'c_tsh_btn_value'
C_CLIENT_OS_TYPE = 'c_client_os_type'
C_HOUR_VALUE = 'c_hour_value'
C_NOTE_VALUE = 'c_note_value'
C_COMMENT_VALUE = 'c_comment_value'
C_STATUS_VALUE = 'c_status_value'
C_SHOW_EMPTY_PROJECTS = 'c_show_empty_projects'

C_LIST_NAMES = (
    C_CLIENT_OS_TYPE,
    C_USER_ID, C_USER_NAME, C_USER_ROLE,
    C_PROJECT_ID, C_TIMESHEET_ID, C_TSH_BTN_VALUE,
    C_DATE, C_WEEK, C_SHOW_EMPTY_PROJECTS,
    C_HOUR_VALUE, C_STATUS_VALUE, C_NOTE_VALUE, C_COMMENT_VALUE,
)

# Name для кнопок
#
TABLE_BUTTON = 'table_cell_btn'
SAVE_BUTTON = 'save_btn'
MSG_BUTTON = 'notifications_btn'
NEW_BUTTON = 'new_btn'
REF_BUTTON = 'reference_btn'
DELETE_BUTTON = 'delete_btn'
DELETE_BUTTON_ID = 'delete_btn_id'
DELETE_BUTTON_YES = 'delete_btn_yes'
DELETE_BUTTON_YES_ID = 'delete_btn_yes_id'
DELETE_BUTTON_NO = 'delete_btn_no'
DELETE_BUTTON_NO_ID = 'delete_btn_no_id'
WEEK_BUTTON_SELECT = 'week_btn'
WEEK_BUTTON_NEXT = 'next_week_btn'
WEEK_BUTTON_PREV = 'prev_week_btn'
WEEK_BUTTON_CURRENT = 'current_week_btn'
UPDATE_BUTTON = 'update_btn'
LOGOFF_BUTTON = 'logoff_btn'
HIDEINFO_BUTTON = 'hideinfo_btn'
DEBUG_BUTTON = 'debug_btn'
NOTIFICATION_BUTTON = 'notification_btn'
NOTIFICATION_OUTBOX_BUTTON = 'outbox_btn'
NOTIFICATION_MESSAGE_BUTTON = 'btn_msg'
NOTIFICATION_CHARTS_BUTTON = 'charts_btn'
NOTIFICATION_USER_CHART_BUTTON = 'user_chart_button'
NOTIFICATIONS_ADD_MSG_BUTTON = 'add_msg_btn'
NOTIFICATIONS_DELETE_BUTTON = 'del_notification_btn'
COPY_ATTRIBUTES_BUTTON = 'copy_attributes_btn'
PASTE_ATTRIBUTES_BUTTON = 'paste_attributes_btn'
SHOW_EMPTY_PROJECTS_BUTTON = 'show_empty_projects_button'
HIDE_EMPTY_PROJECTS_BUTTON = 'hide_empty_projects_button'
NOTIFICATION_MESSAGE = 'notification_message'

# Name для login диалога
#
LOGIN_BUTTON = 'login_btn'
LOGIN_USERNAME = 'user_name'
LOGIN_PASSWORD = 'user_password'

# Атрибуты таблицы <Projects>
#
F_PRJ_ID = 'prj_id'
F_PRJ_MANAGER_ID = 'prj_manager_id'
F_PRJ_NAME = 'prj_name'
F_PRJ_ORG = 'prj_organization'
F_PRJ_START_DATE = 'prj_start_date'
F_PRJ_END_DATE = 'prj_end_date'
F_PRJ_ALL = f'{F_PRJ_MANAGER_ID}, {F_PRJ_NAME}, {F_PRJ_START_DATE}, {F_PRJ_END_DATE}, {F_PRJ_ORG}'
F_PRJ_ALL_ID = f'{F_PRJ_ID}, {F_PRJ_ALL}'
F_PTM_PRJ_ID = 'ptm_project_id'
F_PTM_USR_ID = 'ptm_user_id'


#  Атрибуты таблицы <Timesheets>
#
F_TSH_ID = 'tsh_id'
F_TSH_USER_ID = 'tsh_user_id'
F_TSH_PRJ_ID = 'tsh_project_id'
F_TSH_HOURS = 'tsh_hours'
F_TSH_NOTE = 'tsh_note'
F_TSH_COMMENT = 'tsh_comment'
F_TSH_STATUS = 'tsh_status'
F_TSH_DATE = 'tsh_date'
F_TSH_ALL = f'{F_TSH_USER_ID}, {F_TSH_PRJ_ID}, {F_TSH_HOURS}, {F_TSH_STATUS}, {F_TSH_NOTE}, {F_TSH_DATE}, {F_TSH_COMMENT}'
F_TSH_ALL_ID = f'{F_TSH_ID}, {F_TSH_ALL}'

# Атрибуты таблицы <Users>
#
F_USR_ID = 'usr_id'
F_USR_NAME = 'usr_name'
F_USR_ROLE = 'usr_role'
F_USR_PASSWORD = 'usr_password'
F_USR_MAIL = 'usr_mail'
F_USR_INFO = 'usr_info'
F_USR_IMAGE = 'usr_image'
F_USR_ALL = f'{F_USR_NAME}, {F_USR_ROLE}, {F_USR_PASSWORD}, {F_USR_MAIL}, {F_USR_INFO}'
F_USR_ALL_ID = f'{F_USR_ID}, {F_USR_ALL}'

# Атрибуты таблицы <ts_parameters>
#
F_PRM_NAME = 'prm_name'
F_PRM_VALUE = 'prm_value'
PRM_LOGIN_COUNT = 'login_count'

# Атрибуты таблицы <Messages>
#
F_MSG_ID = 'msg_id'
F_MSG_FROM_USER = 'msg_from_user_id'
F_MSG_TO_USER = 'msg_to_user_id'
F_MSG_TEXT = 'msg_text'
F_MSG_IS_READ = 'msg_is_read'
F_MSG_CREATION_DATE = 'msg_creation_date'
F_MSG_TIMESTAMP = 'msg_timestamp'
F_MSG_TIMESHEET = 'msg_timesheet_id'
F_MSG_ALL = f'{F_MSG_FROM_USER}, {F_MSG_TO_USER}, {F_MSG_TEXT}, {F_MSG_IS_READ}, {F_MSG_CREATION_DATE}, {F_MSG_TIMESHEET}'
F_MSG_ALL_ID = f'{F_MSG_ID}, {F_MSG_ALL}'

# Название словаря свойств Timesheet Entry
FLD_TSH_DICT = 'data'

# Признак незаполненного timesheet на дату и проект (пустая кнопка в таблице Timesheets)
EMPTY_ID_KEY = '-'

# Разделитель на кнопке в таблице Timesheets между prj_id, tsh_id и date
SPLITTER = '#'

# Статусы для Timesheet
#
EDIT_STATUS = 'edit'
IN_APPROVE_STATUS = 'in_approve'
APPROVED_STATUS = 'approved'
REJECTED_STATUS = 'rejected'


def get_status_name(status):
    if status == EDIT_STATUS:
        return 'Редактируется'
    elif status == IN_APPROVE_STATUS:
        return 'На согласовании'
    elif status == APPROVED_STATUS:
        return 'Согласован'
    elif status == REJECTED_STATUS:
        return 'Отклонен'
    else:
        return 'Неизвестен'



# Доступный список статусов для статуса выбранного Timesheet
#
def get_valid_statuses(status=None):
    if status is None:
        return {
        }

    if status == '':
        return {
            EDIT_STATUS: 'Редактировать',
            IN_APPROVE_STATUS: 'Согласовать',
        }

    if status == EDIT_STATUS:
        return {
            EDIT_STATUS: 'Редактировать',
            IN_APPROVE_STATUS: 'Согласовать'
        }

    if status == IN_APPROVE_STATUS:
        return {IN_APPROVE_STATUS: 'На согласовании'}

    if status == APPROVED_STATUS:
        return {APPROVED_STATUS: 'Согласован'}

    if status == REJECTED_STATUS:
        return {
            EDIT_STATUS: 'Редактировать',
            IN_APPROVE_STATUS: 'Согласовать',
        }

    return {}


# модуль Approval
AGREE_BUTTON = 'agree_btn'
REJECT_BUTTON = 'del_btn'
ALL_FLAG_BUTTON = 'all_flag_btn'

MAX_STR_LENGTH_FOR_NOTIFICATION = 30
WIDTH_NOTIFICATION_BUTTON = 270

# Загрузка изображения для пользователя
IMG_TAG_ID = 'imgtagid'
IMG_TAG_NAME = 'img_tag_name'
