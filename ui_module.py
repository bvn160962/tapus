import traceback
from xml.etree import ElementTree as et

import app
import data_module
import settings
import util_module as util

DATE_NAME = 'current_date'
INPUT_WEEK_NAME = 'inp_week'
INPUT_HOURS_NAME = 'inp_hours'
INPUT_NOTE_NAME = 'inp_note'
INPUT_COMMENT_NAME = 'inp_comment'
SELECT_STATUS_NAME = 'selected_status'
SELECT_PROJECT_NAME = 'selected_project'

FORM_HEIGHT = '500px'  # При высоте менее этого значения появляется вертикальная прокрутка
FORM_WIDTH = '800px'   # При ширине менее этого значения появляется горизонтальная прокрутка (иначе строка с модулями превращается в 2 строки)

# Коды возврата HTML
#  https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BA%D0%BE%D0%B4%D0%BE%D0%B2_%D1%81%D0%BE%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D1%8F_HTTP
#  200 - Ok
#  201-203 - обновляет html
#  204 No Content - не обновляет html
#  205 Reset Content
# Client:
#  404 Not Found
# Server:
#  520 Unknown Error

# Стили общих кнопок в заголовке
h_btn_tag = 'button class="material-symbols-outlined right btn-t-cell"'
h_btn_style = 'padding-inline: 0px; margin-left: 0; margin-right: 3px'

# Стили обычных кнопок
c_btn_tag = 'button class="material-symbols-outlined btn-icon"'
c_btn_style = 'position: relative; top: 7px;'


class BaseHTML:

    def __init__(self, title, module, err_message='', notifications=None):
        def get_href_class(mdl):  # Для выделения текущего модуля жирным шрифтом
            base = 'right btn-head border-left'
            if module != mdl:
                return f'{base} normal'
            else:
                return base

        charset = 'windows-1251'
        # util.log_debug(f'BaseHTML: New(title={title})')

        # dt = et.ProcessingInstruction('!DOCTYPE', 'html')
        self.__html = et.Element('html', {'lang': 'ru'})

        # HEAD
        self.__head = et.SubElement(self.__html, 'head')
        et.SubElement(self.__head, 'link', {"rel": "stylesheet", "type": "text/css", "href": 'static/css/common.css'})
        et.SubElement(self.__head, 'link', {"rel": "stylesheet", "type": "text/css", "href": 'static/css/buttons.css'})
        et.SubElement(self.__head, 'link', {"rel": "stylesheet", "type": "text/css", "href": 'static/css/inputs.css'})
        et.SubElement(self.__head, 'link', {"rel": "stylesheet", "type": "text/css", "href": 'static/css/tables.css'})
        # et.SubElement(self.__head, 'link', {'rel': 'icon', 'type': 'image/x-icon', 'href': 'static/img/edit.png'})

        et.SubElement(self.__head, 'link', {"rel": "stylesheet", "href": 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'})
        et.SubElement(self.__head, 'link', {"rel": "stylesheet", "href": 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined'})
        et.SubElement(self.__head, 'meta', {"charset": charset})

        t_title = et.SubElement(self.__head, 'title')
        t_title.text = title

        # BODY
        self.__body = et.SubElement(self.__html, 'body', {'style': f'min-height: {FORM_HEIGHT}; margin-top: 0; min-width: {FORM_WIDTH}'})

        # MODAL CONFIRMATION DIALOG
        if use_modal_confirmation_dialog():
            self.__confirm_message_lab = add_confirmation_dialog(self.__body)

        # MODAL INFO MESSAGE DIALOG
        if use_message_dialog():
            self.__message_lab = add_message_dialog(self.__body, err_message)

        # MODAL NOTIFICATIONS DIALOG
        if use_notifications_dialog() and module == settings.M_TIMESHEETS and notifications is not None:
            self.__notifications_table = add_notifications_dialog(self.__body, notifications)
        else:
            self.__notifications_table = None

        # FORM
        self.__form = et.SubElement(self.__body, 'form', attrib={'name': 'form', 'method': 'POST'})

        # SCRIPT
        socket = et.SubElement(self.__body, 'script', {  # Для socket
            'src': 'https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js',
            'integrity': 'sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==',
            'crossorigin': 'anonymous',
        })
        socket.text = '\n'

        self.__script = et.SubElement(self.__body, 'script', {'src': 'static/js/common.js', 'charset': charset})
        self.__script.text = '\n'

        self.__script = et.SubElement(self.__body, 'script', {'src': 'static/js/main.js', 'charset': charset})
        self.__script.text = '\n'

        self.__script = et.SubElement(self.__body, 'script', {'src': 'static/js/files.js', 'charset': charset})
        self.__script.text = '\n'

        # MODULE
        header = et.SubElement(self.__form, 'header class="head_style sticky"', {'style': 'margin-top: 0;'})
        m = et.SubElement(header, 'a', {'style': 'margin:20px; font-weight: 200;'})

        # INFO
        if module == '':
            m.text = '()'
        else:
            m.text = settings.MODULES[module][settings.M_NAME] + ': ' + f'{str(app.get_c_prop(settings.C_USER_NAME))} ({str(app.get_c_prop(settings.C_USER_ROLE))})'

        # Общие кнопки для всего приложения
        #

        # LOGOFF button
        btn = et.SubElement(header, f'{h_btn_tag} title="Завершить работу"', {'style': h_btn_style, 'name': settings.LOGOFF_BUTTON})
        btn.text = 'logout'   # logout move_item
        # log_off = et.SubElement(p, 'button title="Завершить работу"', attrib={'type': 'submit', 'name': settings.LOGOFF_BUTTON, 'class': 'right btn-icon'})
        # i = et.SubElement(log_off, 'i', {'class': 'fa fa-user-circle-o fa-lg'})  # fa-user-o
        # i.text = '\n'  # !!!Обязательно!!! Иначе, создает одиночный тэг <i .... />, вместо парного <i> ... </i>

        # DEBUG button
        btn = et.SubElement(header, f'{h_btn_tag} title="Состояние текущей сессии"', {'style': h_btn_style, 'name': settings.DEBUG_BUTTON})
        btn.text = 'info'  # 'pest_control'

        # REFRESH button
        btn = et.SubElement(header, f'{h_btn_tag} title="Обновить"',{'style': h_btn_style, 'name': settings.UPDATE_BUTTON})
        btn.text = 'sync'

        # NOTIFICATION button
        user_id = app.get_c_prop(settings.C_USER_ID)
        if use_notifications_dialog() and user_id != '':  # Еще не было логина
            # Получить количество не прочтенных сообщений
            msgs = data_module.get_unread_count(user_id)
            count = getattr(msgs[0], "count")

            # util.log_tmp(f'msg count: {count}')
            container = et.SubElement(
                header,
                f'div class="h-btn-container" onclick="msg_count_click(\'{settings.NOTIFICATION_BUTTON}\');"',
                {'style': 'cursor: pointer;'},
            )
            if count > 0:
                text = et.SubElement(container, f'a class="h-btn-text" title="Непрочитанных сообщений: {count}"')
                text.text = str(count)
            btn = et.SubElement(container, f'button class="material-symbols-outlined h-btn-icon" title="Сообщения"', {'style': h_btn_style, 'name': settings.NOTIFICATION_BUTTON})
            btn.text = 'notifications'

        # Навигация по сайту
        #
        if is_module_available(settings.M_APPROVEMENT):
            b = et.SubElement(header,
                              f'a title="{settings.MODULES[settings.M_APPROVEMENT][settings.M_TITLE]}"',
                              {'href': settings.MODULES[settings.M_APPROVEMENT][settings.M_URL],
                               'class': f'{get_href_class(settings.M_APPROVEMENT)} border-right'})
            b.text = settings.MODULES[settings.M_APPROVEMENT][settings.M_NAME]

        if is_module_available(settings.M_USERS):
            b = et.SubElement(header,
                              f'a title="{settings.MODULES[settings.M_USERS][settings.M_TITLE]}"',
                              {'href': settings.MODULES[settings.M_USERS][settings.M_URL],
                               'class': get_href_class(settings.M_USERS)})
            b.text = settings.MODULES[settings.M_USERS][settings.M_NAME]

        if is_module_available(settings.M_PROJECTS):
            b = et.SubElement(header,
                              f'a title="{settings.MODULES[settings.M_PROJECTS][settings.M_TITLE]}"',
                              {'href': settings.MODULES[settings.M_PROJECTS][settings.M_URL],
                               'class': get_href_class(settings.M_PROJECTS)})
            b.text = settings.MODULES[settings.M_PROJECTS][settings.M_NAME]

        if is_module_available(settings.M_TIMESHEETS):
            b = et.SubElement(header,
                              f'a title="{settings.MODULES[settings.M_TIMESHEETS][settings.M_TITLE]}"',
                              {'href': settings.MODULES[settings.M_TIMESHEETS][settings.M_URL],
                               'class': get_href_class(settings.M_TIMESHEETS)})
            b.text = settings.MODULES[settings.M_TIMESHEETS][settings.M_NAME]


    def get_html(self):
        # util.log_debug(f'===={self.__html}')
        # util.log_debug(f'====get_html:{et.tostring(self.__html)}')

        return et.tostring(self.__html).decode(encoding='utf-8')

    def get_body(self):
        return self.__body

    def get_head(self):
        return self.__head

    def get_form(self):
        return self.__form

    def set_confirm_message(self, msg):
        if self.__confirm_message_lab is not None:
            self.__confirm_message_lab.text = msg

    def set_message(self, msg):
        if self.__message_lab is not None:
            self.__message_lab.text = msg

    def set_notifications_message(self, msg):
        if self.__notifications_table is not None:
            pass
            # self.__notifications_lab.text = msg


# Показывать пустые проекты в таблице
def show_empty_projects():
    cache_prop = app.get_c_prop(settings.C_SHOW_EMPTY_PROJECTS)

    if cache_prop == '':  # Установить свойство в кэш
        app.set_c_prop(settings.C_SHOW_EMPTY_PROJECTS, str(settings.SHOW_EMPTY_PROJECTS))
        cache_prop = app.get_c_prop(settings.C_SHOW_EMPTY_PROJECTS)

    if cache_prop == 'True':
        return True
    else:
        return False


# Использовать модальное окно для диалога подтверждения?
def use_modal_confirmation_dialog():
    verdict = False
    if settings.USE_MODAL_CONFIRMATION_DIALOG:
        verdict = app.get_c_prop(settings.C_CLIENT_OS_TYPE) != util.CLIENT_OS_SUPPORTED[1]
    return verdict


# Использовать модальное окно для диалога подтверждения?
def use_message_dialog():
    verdict = False
    if settings.USE_MESSAGE_DIALOG:
        verdict = app.get_c_prop(settings.C_CLIENT_OS_TYPE) != util.CLIENT_OS_SUPPORTED[1]
    return verdict


# Использовать модальное окно для показа списка сообщений по записи отработанного времени (tsh_id)?
def use_notifications_dialog():
    verdict = False
    if settings.USE_NOTIFICATIONS:
        verdict = app.get_c_prop(settings.C_CLIENT_OS_TYPE) != util.CLIENT_OS_SUPPORTED[1]
    return verdict


# Доступность модулей для различных ролей
#
def is_module_available(module):
    role = app.get_c_prop(settings.C_USER_ROLE)

    if module == settings.M_TIMESHEETS:
        return True

    if module == settings.M_USERS:
        return role == settings.R_ADMIN

    if module == settings.M_PROJECTS:
        return role == settings.R_ADMIN or role == settings.R_MANAGER

    if module == settings.M_APPROVEMENT:
        return role == settings.R_ADMIN or role == settings.R_MANAGER

    return False


def is_available_html(module):
    if not is_module_available(module):
        html_is_available = create_info_html(
            i_type=settings.INFO_TYPE_WARNING,
            module=module,
            msg=f'Модуль "{settings.MODULES[module][settings.M_TITLE]}" недоступен для роли "{app.get_c_prop(settings.C_USER_ROLE)}"!',
            url=settings.MODULES[settings.M_TIMESHEETS][settings.M_URL]  # Ссылка на модуль Timesheets
        )
    else:
        html_is_available = ''
    return html_is_available


def get_row_color(row):
    return '#E5E5E5' if row % 2 == 0 else '#FFFFFF'


def add_table_buttons(col, obj_id, module):

    # Reference button
    btn = et.SubElement(col,
                        'button class="material-symbols-outlined btn-t-cell" title="Ссылки"',
                        {
                            'style': 'padding-inline: 0px; margin-left: 0; margin-right: 0; padding-left: 1px',  # padding-left - добавлен для корректного отображения на ipad
                            'name': settings.REF_BUTTON,
                            'value': obj_id,
                        })
    btn.text = 'quick_reference_all'

    # Delete button
    if use_modal_confirmation_dialog():
        btn_type = 'button'
    else:
        btn_type = 'submit'

    # Текст сообщения для
    if module == settings.M_PROJECTS:
        msg_text = f'Проект:\n\t- Название: {data_module.get_project_by_id_list(obj_id)[2]}'
    elif module == settings.M_USERS:
        msg_text = f'Пользователя:\n\t- Имя: {data_module.get_user_by_id_list(obj_id)[1]}'
    else:
        msg_text = ''

    params = [
        settings.CONFIRMATION_DIALOG_ID,
        settings.DELETE_BUTTON_NO_ID,
        settings.DELETE_BUTTON_YES_ID,
        settings.CONFIRMATION_MESSAGE_ID,
        settings.CONFIRMATION_HEADER_ID,
        settings.CONFIRMATION_BOTTOM_LINE_ID,
        settings.CONFIRMATION_RIGHT_LINE_ID,
        settings.CONFIRMATION_CORNER_LINE_ID,
        msg_text,
        obj_id,
        ]

    btn = et.SubElement(col,
                        'button class="material-symbols-outlined btn-t-cell" title="Удалить" '
                        f'onclick="show_confirm_dialog({params});"',
                        {
                            'style': 'padding-inline: 0px; margin-left: 0; margin-right: 0; padding: 0 0 0 2',
                            'name': settings.DELETE_BUTTON,
                            'id': obj_id,
                            'value': obj_id,
                            'type': btn_type,
                        })
    btn.text = 'delete'

    # Edit button
    btn = et.SubElement(col,
                        'button class="material-symbols-outlined btn-t-cell" title="Редактировать"',
                        {
                            'style': 'padding-inline: 0px; margin-left: 0; margin-right: 0; padding: 0 0 0 2',
                            'name': settings.TABLE_BUTTON,
                            'value': obj_id,
                        })
    btn.text = 'draft_orders'


def add_buttons(col, btn_id):

    btn = et.SubElement(col,
                        'button class="material-symbols-outlined btn-t-cell" title="Сохранить"',
                        {
                            'style': 'padding-inline: 0px; margin-left: 0; margin-right: 0;',
                            'name': settings.SAVE_BUTTON,
                            'value': btn_id,
                        })
    btn.text = 'save'

    btn = et.SubElement(col,
                        'button class="material-symbols-outlined btn-t-cell" title="Скрыть атрибуты"',
                        {
                            'style': 'padding-inline: 0px; margin-left: 0; margin-right: 0;',
                            'name': settings.HIDEINFO_BUTTON,
                            'value': btn_id,
                        })
    btn.text = 'stat_minus_2'


def create_login_html(err_msg, module='', user_name=''):
    util.log_debug(f'craete_login_html: ...')
    html = et.Element('html', attrib={'lang': 'ru'})

    # HEAD
    head = et.SubElement(html, 'head')
    et.SubElement(head, 'meta', {'charset': 'UTF-8'})
    et.SubElement(head, 'meta', {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'})
    et.SubElement(head, 'link', {'rel': 'stylesheet', 'href': '/static/css/common.css'})
    # et.SubElement(head, 'link', {'rel': 'icon', 'href': '/static/img/4388342.png', 'type': 'image/x-icon'})
    # et.SubElement(head, 'link', {'rel': 'icon', 'href': '/static/img/timesheets.png', 'type': 'image/x-icon'})
    t = et.SubElement(head, 'title')
    t.text = 'Регистрация'

    # BODY
    body = et.SubElement(html, 'body')

    # FORM
    form = et.SubElement(body, 'form', attrib={'name': 'login', 'method': 'POST', 'class': 'center_frame'})
    et.SubElement(form, 'img', {'src': '/static/img/timesheets.png', 'class': 'fit-picture'})
    script = et.SubElement(body, 'script', {'src': '/static/js/common.js'})
    script.text = '\n'

    et.SubElement(form, settings.TAG_INPUT, {'style': 'margin: 5px;', 'type': 'text', 'value': user_name, 'name': settings.LOGIN_USERNAME, 'placeholder': 'логин'})
    et.SubElement(form, 'input', {'style': 'margin: 3px;', 'type': 'password', 'name': settings.LOGIN_PASSWORD, 'placeholder': 'пароль'})

    p = et.SubElement(form, 'p')
    msg = et.SubElement(p, 'a', {'style': 'color: red;'})
    if err_msg == '':
        msg.text = '\n'
    else:
        msg.text = err_msg

    btn = et.SubElement(form, 'button',
                        {
                            'style': 'margin: 10px;',
                            'type': 'submit',
                            'name': settings.LOGIN_BUTTON,
                            'value': module,
                            'class': 'sub_button'})
    btn.text = 'ВОЙТИ'

    return et.tostring(html).decode()


def create_info_html(i_type='', msg=(), module='', title='', url=''):
    # util.log_debug(f'size: {len(msg)}')
    try:
        if msg == '':
            msg = 'Информация'

        if i_type == '':
            i_type = settings.INFO_TYPE_INFORMATION

        if module == '':
            mdl = ''
            url_ = ''
        else:
            mdl = module
            if url != '':
                url_ = url
            else:
                url_ = settings.MODULES[mdl][settings.M_URL]

        base_html = BaseHTML(i_type, mdl)
        p = base_html.get_form()

        # Ссылка для возврата
        comeback_link(url_, p)

        # MESSAGE
        h = et.SubElement(p, 'H3', {'style': 'display: inline-block; margin:7px'})
        if title == '':
            h.text = i_type + ':'
        else:
            h.text = title + ':'

        # et.SubElement(p, 'br')
        # et.SubElement(p, 'br')

        if isinstance(msg, str):  # div
            # util.log_debug(f'type: строка')
            div = et. SubElement(p, 'div', {'style': 'display: inline-block; margin:7px'})
            div.text = msg
        else:
            if isinstance(msg, tuple) or isinstance(msg, list):
                # Элемент с прокруткой
                # et.SubElement(p, 'div', {'style': f'height: {FORM_HEIGHT}; overflow: auto visible;'})

                if isinstance(msg[0], str):  # divs
                    # util.log_debug(f'type: массив строк ({len(msg)})')
                    for m in msg:
                        div = et.SubElement(p, 'div')
                        div.text = m
                if isinstance(msg[0], tuple) or isinstance(msg[0], list):  # table
                    # util.log_debug(f'type: таблица из строк ({len(msg)}x{len(msg[0])})')
                    table = et.SubElement(p, 'table')
                    row_num = 0
                    for r in msg:
                        # util.log_debug(f'row: {r}')
                        row = et.SubElement(table, 'tr')
                        for c in r:
                            if row_num == 0:  # Заголовок таблицы
                                td = 'td align=center'
                                style = 'border-bottom: 2px solid gray; border-top: 2px solid gray; padding-left: 10px; background-color: #C0C0C0; font-weight: bold;'
                            else:
                                td = 'td align=left'
                                style = 'border-bottom: 1px solid gray; min-width: 100px; max-width: 300px; padding-left: 10px; padding-top: 10px;'
                            col = et.SubElement(row, td, {'style': style})
                            a = et.SubElement(col, 'a')
                            a.text = c
                        row_num += 1

        return base_html.get_html()

    except Exception as ex:
        traceback.print_exc()
        return f'Произошла ошибка при формировании html страницы (Create INFO):\n {ex}', 520  # Server Unknown Error


# Диалог подтверждения
def add_confirmation_dialog(body):

    # Dialog
    dialog = et.SubElement(body, 'dialog',
                           {
                               'id': settings.CONFIRMATION_DIALOG_ID,
                               'class': 'head_style dial-pos',
                               'style': 'min-width: 300px; max-width: 500px; min-height: 170; max-height: 400; border-radius: 5px;'})

    form = et.SubElement(dialog, 'form',
                         {
                             'method': 'POST',
                             'style': 'margin-bottom: 0px;'})

    # Header
    header = et.SubElement(form, 'div', {
        'id': settings.CONFIRMATION_HEADER_ID,
        'style': 'padding: 0 0 0 5px; border-bottom: solid 1px black; background-color: gray; color: white; user-select: none;'})
    header.text = "Подтверждение удаления"

    # Title
    p = et.SubElement(form, 'p align=center', {'style': 'user-select: none;'})
    l_title = et.SubElement(p, 'label', {
        'style': 'white-space: pre-wrap; border-bottom: solid 1px gray; padding-bottom: 5px'})
    l_title.text = 'Вы действительно хотите удалить?'

    # Message
    p = et.SubElement(form, 'p', {
        'style': 'user-select: none;'
    })
    l_message = et.SubElement(p, 'label', {
        'id': settings.CONFIRMATION_MESSAGE_ID,
        'style': 'white-space: pre-wrap; color: black; font-weight: normal; padding: 0 0 0 5px;'})
    l_message.text = ''

    # Confirm Buttons
    p = et.SubElement(form, 'p', {'class': 'center', 'style': 'margin: 10 0 5 0px; user-select: none;'})
    # Ok
    btn = et.SubElement(p, 'button', {
        'type': 'submit',
        'id': settings.DELETE_BUTTON_YES_ID,
        'name': settings.DELETE_BUTTON_YES,
        'style': 'margin-right: 5px; width: 50px'})
    btn.text = 'Да'
    # Cancel
    btn = et.SubElement(p, 'button', {
        'type': 'button',
        'id': settings.DELETE_BUTTON_NO_ID,
        'style': 'width: 50px'})
    btn.text = 'Нет'

    # Resizing lines
    add_border_for_resizing(form, settings.CONFIRMATION_BOUNDARY_BOX)

    return l_message


# Рамка справа и внизу для изменения размера окна
def add_border_for_resizing(form, box):
    c_style = 'margin: 0px; border: 2px solid transparent; position: absolute;'
    et.SubElement(form, 'hr', {
        'id': box[0],
        # 'color': 'red',
        'style': f'{c_style} cursor: ns-resize; bottom: 0; width: 98%'})

    et.SubElement(form, 'hr', {
        'id': box[1],
        # 'color': 'green',
        'style': f'{c_style} cursor: ew-resize; right: 0; top: 0; height: 94%;'})

    et.SubElement(form, 'hr', {
        'id': box[2],
        # 'color': 'blue',
        'style': f'{c_style} cursor: nwse-resize; right: 0; bottom: 0; height: 2%;  width: 1%'})


def add_notifications_dialog(body, notifications):
    add_info_dialog(body, notifications,
                    ('От кого', 'Кому', 'Дата', 'Текст сообщения'),
                    f'История переписки по записи отработанного времени ({len(notifications)})',
                    'Сообщений нет!')


def add_info_dialog(body, obj_list, tbl_header, title, empty_msg):
    # Dialog
    dialog = et.SubElement(body, 'dialog',
                           {
                               'id': settings.NOTIFICATIONS_DIALOG_ID,
                               'class': 'head_style dial-pos',
                               'style': 'padding: 0; border-radius: 5px'})
    form = et.SubElement(dialog, 'form',
                         {
                             'style': 'margin-bottom: 0px'})

    header = et.SubElement(form, 'header',
                           {
                               'id': settings.NOTIFICATIONS_DIALOG_HEADER_ID,
                               'class': 'sticky',
                               'style': 'margin: 0; padding:0; border-bottom: solid 2px black; background-color: gray; color: white; user-select: none;'})
    p = et.SubElement(form, 'p',
                      {'style': '; min-width: 550px; max-height: 300px; text-align: center;'})

    # Close Button
    btn = et.SubElement(header, f'{h_btn_tag} id={settings.NOTIFICATIONS_DIALOG_CLOSE_BTN_ID} type=button title="Закрыть окно"',
                        {'style': f'{h_btn_style}; color: black;', 'name': settings.LOGOFF_BUTTON})
    btn.text = 'disabled_by_default'

    # Title
    l_title = et.SubElement(header, 'label', {'style': 'white-space: pre-wrap; padding: 5px;'})
    l_title.text = title

    # Notifications
    if len(obj_list) > 0:
        table = et.SubElement(p, 'table', {'style': 'border: 2px; padding: 10px'})

        min_max_width = 'min-width: 100px; max-width: 300px;'
        h_border = 'border-bottom: 2px solid gray; border-top: 2px solid gray;'
        h_style = f'{min_max_width} {h_border} padding-left: 10px; background-color: #C0C0C0; font-weight: bold;'
        b_border = 'border-bottom: 1px solid gray;'
        b_style = f'{min_max_width} {b_border}  padding-left: 10px; padding-top: 10px;'

        # Заголовок таблицы
        row = et.SubElement(table, 'tr')
        for h in tbl_header:
            col = et.SubElement(row, 'td align=left', {'style': h_style})
            a = et.SubElement(col, 'a')
            a.text = h

        # Заполнение таблицы
        for r in obj_list:
            row = et.SubElement(table, 'tr')
            for c in r:
                td = 'td align=left'
                col = et.SubElement(row, td, {'style': b_style})
                a = et.SubElement(col, 'a')
                a.text = c
    else:
        lab = et.SubElement(p, 'label')
        lab.text = empty_msg
        table = None

    # Resizing lines
    add_border_for_resizing(form, settings.NOTIFICATIONS_BOUNDARY_BOX)

    return table


def add_message_dialog(body, message, title=''):

    # Dialog
    dialog = et.SubElement(body, 'dialog',
                           {
                               'id': settings.MESSAGE_DIALOG_ID,
                               'class': 'head_style dial-pos',
                               'style': 'padding: 0; border-radius: 5px'})

    form = et.SubElement(dialog, 'form',
                         {
                             'style': 'margin-bottom: 0px'})

    header = et.SubElement(form, 'header',
                           {
                               'id': settings.MESSAGE_DIALOG_HEADER_ID,
                               'class': 'sticky',
                               'style': 'margin: 0; padding:0; border-bottom: solid 2px black; background-color: gray; color: white; user-select: none;'})

    # Close Button
    btn = et.SubElement(header, f'{h_btn_tag} id={settings.MESSAGE_DIALOG_CLOSE_BUTTON_ID} type=button title="Закрыть окно"',
                        {'style': f'{h_btn_style}; color: black;', 'name': settings.LOGOFF_BUTTON})
    btn.text = 'disabled_by_default'
    # Title
    l_title = et.SubElement(header, 'label',
                            {
                                'id': settings.MESSAGE_DIALOG_TITLE_ID,
                                'style': 'white-space: pre-wrap; margin: 5 5 10 10;'})
    if title == '':
        l_title.text = 'Сообщение'
    else:
        l_title.text = title

    # Message
    p = et.SubElement(form, 'p ',
                      {'style': '; min-width: 200; max-width: 500; max-height: 300; text-align: left;'})

    l_message = et.SubElement(p, 'div', {
        'id': settings.MESSAGE_DIALOG_TEXT_ID,
        'style': 'white-space: pre-wrap; color: black; font-weight: normal; margin: 5 5 15 10;'})
    # Если присвоить пробел - граничные теги добавятся в div а не в form (т.к. div "не закроется"!)
    l_message.text = message if message != '' else '\n'

    # Resizing lines
    add_border_for_resizing(form, settings.MESSAGE_BOUNDARY_BOX)

    return l_message


def create_delete_confirm_html(obj_id, module):
    try:
        # FORM
        #
        base_html = BaseHTML('Подтверждение', module)
        form = base_html.get_form()

        # INFO AREA
        #
        p_msg = et.SubElement(form, 'p')

        msg = 'Вы действительно хотите удалить запись?\n'

        values = None
        rows = 10
        cols = 60
        if module == settings.M_TIMESHEETS:
            values = data_module.get_timesheet_dict(obj_id)
            msg = 'Вы действительно хотите удалить запись?\n'
            msg += f'   - Дата: {values[settings.F_TSH_DATE]}\n'
            msg += f'   - Часы: {values[settings.F_TSH_HOURS]}\n'
            msg += f'   - Статус: {values[settings.F_TSH_STATUS]}\n'
            msg += f'   - Замечание: {values[settings.F_TSH_NOTE]}\n'
            msg += f'   - Комментарий: {values[settings.F_TSH_COMMENT]}\n'
            rows = 7

        if module == settings.M_USERS:
            refs = data_module.where_user_refs(obj_id)
            values = data_module.get_user_by_id_list(obj_id)
            msg = 'Вы действительно хотите удалить пользователя?\n'
            msg += f'   - Имя: {values[1]}\n'
            msg += f'   - Роль: {values[2]}\n'
            if len(refs) > 0:
                msg += '--------------------------------------\n'
                msg += f'На пользователя существуют ссылки - {str(len(refs))}\n'
                msg += f'Нажмите "Ссылки" - для подробностей\n'
                msg += '--------------------------------------\n'
                rows = 8
            else:
                rows = 4

        if module == settings.M_PROJECTS:
            refs = data_module.where_project_refs(obj_id)
            values = data_module.get_project_by_id_list(obj_id)
            msg = 'Вы действительно хотите удалить проект?\n'
            msg += f'   - Имя: {values[2]}\n'
            msg += f'   - Начало: {values[3]}\n'
            msg += f'   - Окончание: {values[4]}\n'
            if len(refs) > 0:
                msg += '------------------------------------------------------\n'
                msg += f'На проект существуют ссылки - {str(len(refs))}\n'
                msg += f'Нажмите "Ссылки" - для получения детальной информации\n'
                msg += '------------------------------------------------------\n'
                rows = 9
            else:
                rows = 5

        text = et.SubElement(p_msg, f'textarea cols="{cols}" rows="{rows}" readonly')  # style="background-color:LightGray"
        text.text = msg

        # CONFIRM AREA
        #
        p_confirm = et.SubElement(form, 'p')

        btn_yes = et.SubElement(p_confirm, 'button',
                                attrib={
                                    'type': 'submit',
                                    'name': settings.DELETE_BUTTON_YES,
                                    'value': obj_id,
                                    'style': 'margin-left:100px; width: 60px;'
                                })  #   style="margin-left:150px;"
        btn_yes.text = 'Да'

        btn_no = et.SubElement(p_confirm,
                               'button',
                               {'type': 'submit', 'name': settings.DELETE_BUTTON_NO, 'value': obj_id, 'style': 'width: 60px;'})
        btn_no.text = 'Нет'

        return base_html.get_html()

    except Exception as ex:
        return f'Произошла ошибка при формировании html страницы (Confirm):\n {ex}', 520  # Server Unknown Error


# TIMESHEETS
#
def add_timesheets_info(base_html, tsh_entry=None, notifications=()):

    form = base_html.get_form()

    tsh_id = app.get_c_prop(settings.C_TIMESHEET_ID)
    week = app.get_c_prop(settings.C_WEEK)

    # parsing attributes
    #
    hours = ''
    note = ''
    status = ''
    date = ''
    comment = ''
    if tsh_entry is not None:
        hours = tsh_entry.get(settings.F_TSH_HOURS)
        note = tsh_entry.get(settings.F_TSH_NOTE)
        status = tsh_entry.get(settings.F_TSH_STATUS)
        date = str(tsh_entry.get(settings.F_TSH_DATE))
        comment = str(tsh_entry.get(settings.F_TSH_COMMENT))

    p = et.SubElement(form, 'p')

    # TABLE
    table = et.SubElement(p, 'table')

    # WEEK ROW
    #
    row = et.SubElement(table, 'tr')
    col = et.SubElement(row, 'td colspan="5" align="center"')  # Объединенная ячейка

    # Кнопка Текущая неделя
    btn = et.SubElement(col, f'{c_btn_tag} title="Текущая неделя"',{'name': settings.WEEK_BUTTON_CURRENT, 'style': c_btn_style})
    btn.text = 'event'
    # Awesome icon
    # btn = et.SubElement(col, 'button title="Текущая неделя" class="btn-icon"', attrib={'type': 'submit', 'name': settings.WEEK_BUTTON_CURRENT})
    # i = et.SubElement(btn, 'i class="fa fa-calendar fa-lg" aria-hidden="true"')
    # i.text = '\n'

    # Кнопка Назад
    btn = et.SubElement(col, f'{c_btn_tag} title="Предыдущая неделя"',{'name': settings.WEEK_BUTTON_PREV, 'style': c_btn_style})
    btn.text = 'chevron_left'
    # Awesome icon
    # btn = et.SubElement(col, 'button title="Предыдущая неделя" class="btn-icon"', attrib={'type': 'submit', 'name': settings.WEEK_BUTTON_PREV})
    # i = et.SubElement(btn, 'i class="fa fa-arrow-circle-o-left fa-lg" aria-hidden="true"')
    # i.text = '\n'

    # Кнопка Вперед
    btn = et.SubElement(col, f'{c_btn_tag} title="Следующая неделя"',{'name': settings.WEEK_BUTTON_NEXT, 'style': c_btn_style})
    btn.text = 'chevron_right'
    # Awesome icon
    # btn = et.SubElement(col, 'button title="Следующая неделя" class="btn-icon"', attrib={'type': 'submit', 'name': settings.WEEK_BUTTON_NEXT})
    # i = et.SubElement(btn, 'i class="fa fa-arrow-circle-o-right fa-lg" aria-hidden="true"')
    # i.text = '\n'

    # Календарь
    # util.log_debug(f'week html={week}; {type(week)}')
    et.SubElement(col, settings.TAG_INPUT, attrib={'type': 'week', 'name': INPUT_WEEK_NAME, 'value': week, 'style': 'border-radius: 10px; margin: 0px 7px 5px 7px;'})

    # Кнопка Применить выбранную неделю
    btn = et.SubElement(col, f'{c_btn_tag} title="Выбрать неделю"',{'name': settings.WEEK_BUTTON_SELECT, 'style': c_btn_style})
    btn.text = 'event_available'
    # Awesome icon
    # btn = et.SubElement(col, 'button title="Выбрать неделю" class="btn-icon"', attrib={'type': 'submit', 'name': settings.WEEK_BUTTON_SELECT})
    # i = et.SubElement(btn, 'i class="fa fa-arrow-circle-o-down fa-lg" aria-hidden="true"')
    # i.text = '\n'

    # Разделитель на панели кнопок
    splitter = et.SubElement(col, 'label', {'style': 'margin-left: 25; margin-right: 15'})
    # splitter.text = '|'

    # Кнопка Копировать атрибуты
    btn = et.SubElement(col, f'{c_btn_tag} title="Копировать атрибуты текущей записи"',{'name': settings.COPY_ATTRIBUTES_BUTTON, 'style': c_btn_style})
    btn.text = 'content_copy'

    # Кнопка Заполнить атрибуты
    btn = et.SubElement(col, f'{c_btn_tag} title="Заполнить атрибуты текущей записи"', {'name': settings.PASTE_ATTRIBUTES_BUTTON, 'style': c_btn_style})
    btn.text = 'content_paste'

    # Разделитель на панели кнопок
    splitter = et.SubElement(col, 'label', {'style': 'margin-left: 25; margin-right: 15'})

    # Кнопка Показать/Скрыть пустые проекты
    if show_empty_projects():
        btn = et.SubElement(col, f'{c_btn_tag} title="Скрыть пустые проекты"', {'name': settings.HIDE_EMPTY_PROJECTS_BUTTON, 'style': c_btn_style})
        btn.text = 'date_range'
    else:
        btn = et.SubElement(col, f'{c_btn_tag} title="Отобразить пустые проекты"', {'name': settings.SHOW_EMPTY_PROJECTS_BUTTON, 'style': c_btn_style})
        btn.text = 'calendar_month'

    # HEADERS ROW
    #
    row = et.SubElement(table, 'tr', {'style': 'border: 2px solid green'})
    col = et.SubElement(row, settings.TAG_TD_CENTER)
    lab = et.SubElement(col, settings.TAG_A_HEAD)
    lab.text = 'Дата:'

    col = et.SubElement(row, settings.TAG_TD_CENTER)
    lab = et.SubElement(col, settings.TAG_A_HEAD)
    lab.text = 'Проект:'

    col = et.SubElement(row, settings.TAG_TD_CENTER)
    lab = et.SubElement(col, settings.TAG_A_HEAD)
    lab.text = 'Часы:'

    col = et.SubElement(row, settings.TAG_TD_CENTER)
    lab = et.SubElement(col, settings.TAG_A_HEAD + ' title="Дополнительная информация"')
    lab.text = 'Описание:'

    col = et.SubElement(row, settings.TAG_TD_CENTER)
    lab = et.SubElement(col, settings.TAG_A_HEAD + ' title="Комментарий согласования с руководителем"')
    lab.text = 'Комментарий:'

    col = et.SubElement(row, settings.TAG_TD_CENTER)
    lab = et.SubElement(col, settings.TAG_A_HEAD)
    lab.text = 'Статус:'

    # FIELDS ROW
    #
    row = et.SubElement(table, 'tr')
    # ДАТА
    col = et.SubElement(row, 'td')
    et.SubElement(col, settings.TAG_INPUT, attrib={'type': 'date', 'name': DATE_NAME, 'value': date})

    # ПРОЕКТЫ
    col = et.SubElement(row, 'td')
    prj_id = app.get_c_prop(settings.C_PROJECT_ID)  # текущий проект из кэш
    prj_dict = data_module.get_all_projects_dict(app.get_c_prop(settings.C_USER_ID))
    p_list = et.SubElement(col, 'select', {'name': SELECT_PROJECT_NAME, 'style': 'min-width: 150px'})

    if prj_dict is None:
        raise Exception(f'Список проектов не сформирован. Возможно, нет подключения к базе данных!')

    for pid in prj_dict:
        p_dict = prj_dict[pid]
        # util.log_debug(f'=={value}={p_dict}')
        val = f'{pid}{settings.SPLITTER}{p_dict[settings.F_PRJ_MANAGER_ID]}'
        if pid == prj_id:  # текущий проект (из кэша)
            opt_tag = 'option selected'
        else:
            opt_tag = 'option'

        opt = et.SubElement(p_list, opt_tag, attrib={'value': val})
        opt.text = p_dict[settings.F_PRJ_NAME]

    # ЧАСЫ
    col = et.SubElement(row, 'td')
    et.SubElement(col, settings.TAG_INPUT + ' size="3"', attrib={'type': 'text', 'name': INPUT_HOURS_NAME, 'value': hours})

    # ЗАМЕТКИ
    col = et.SubElement(row, 'td')
    et.SubElement(col, settings.TAG_INPUT + ' size="20"', attrib={'type': 'text', 'name': INPUT_NOTE_NAME, 'value': note, 'title': note})

    # КОММЕНТАРИЙ
    col = et.SubElement(row, 'td')
    et.SubElement(col, settings.TAG_INPUT + ' size="20"', attrib={'type': 'text', 'name': INPUT_COMMENT_NAME, 'value': comment, 'title': comment})

    # СТАТУСЫ
    col = et.SubElement(row, 'td')
    select_status = et.SubElement(col, 'select style="max-width:150px;"', attrib={'name': SELECT_STATUS_NAME})
    valid_statuses = settings.get_valid_statuses(status)

    # util.log_tmp(f'valid_statuses: {valid_statuses}; status: {status}')

    for value in valid_statuses:
        if value == status:
            opt = et.SubElement(select_status, 'option selected', attrib={'value': value})
        else:
            opt = et.SubElement(select_status, 'option', attrib={'value': value})
        opt.text = valid_statuses[value]

    # TABLE & BUTTONS ROW
    #
    row_1 = et.SubElement(table, 'tr')
    col_table = et.SubElement(row_1, 'td colspan=5 rowspan=3 align=center', {'style': 'border: 2px solid'})  # Объединенная ячейка для таблицы
    col_btns = et.SubElement(row_1, 'td', {'align': 'center', 'valign': 'top', 'width': '50'})

    # Кнопка "Сохранить"
    if status == settings.EDIT_STATUS or status == settings.REJECTED_STATUS or status == '':
        btn_tag = 'button'
    else:
        btn_tag = 'button disabled'
    btn_save = et.SubElement(col_btns, btn_tag, {'type': 'submit', 'name': settings.SAVE_BUTTON, 'value': tsh_id})
    btn_save.text = 'сохранить'

    # Кнопка "Удалить"
    if tsh_id == '':
        btn_tag = 'button disabled'
    else:
        btn_tag = f'button name={settings.DELETE_BUTTON} value={tsh_id}'
        if use_modal_confirmation_dialog():  # Для показа модального окна
            btn_tag = f'{btn_tag} type=button'
            msg = (
                   f'Запись:'
                   f'\n\t- Дата: {date}'
                   f'\n\t- Часы: {hours}'
                   f'\n\t- Статус: {status}'
                   f'\n\t- Замечание: {note}'
                   f'\n\t- Комментарий: {comment}'
                   )
            base_html.set_confirm_message(msg)
        else:  # Для показа html страницы
            btn_tag = f'{btn_tag} type=submit'

    btn_delete = et.SubElement(col_btns, btn_tag)
    btn_delete.text = 'удалить'

    # Кнопка "Показать сообщения"
    if use_notifications_dialog():
        msg_cnt = len(notifications)
        if tsh_id != '' and  msg_cnt > 0:
            btn_msg = et.SubElement(col_btns, 'button', {'type': 'button', 'name': settings.MSG_BUTTON, 'value': tsh_id, 'style': 'min-width: 120px'})
            btn_msg.text = f'переписка ({msg_cnt})'
        # if tsh_id == '':
        #     btn_tag = 'button disabled'
        # else:
        #     btn_tag = 'button'
        # btn_msg = et.SubElement(col_btns, btn_tag, {'type': 'button', 'name': settings.MSG_BUTTON, 'value': tsh_id})
        # btn_msg.text = f'переписка ({len(notifications)})'

    # TABLE AREA
    #
    time_sheets_data = data_module.get_all_entries(app.get_c_prop(settings.C_USER_ID), week)
    add_timesheet_table(time_sheets_data, col_table)


def add_timesheet_table(data, column):

    prj_col_width = '330px'
    date_col_width = '50px'
    c_btn_value = app.get_c_prop(settings.C_TSH_BTN_VALUE)

    table_tsh = et.SubElement(column, 'table', {'style': 'width: 100%; border-spacing: 0px 0px;'})

    # HEAD ROW (project + dates)
    #
    dates_node = et.SubElement(table_tsh, 'tr')
    dates_col_node = et.SubElement(dates_node, settings.TAG_TD_BTN_HEADER, {'style': f'width: {prj_col_width};'})
    dates_col_node.text = 'Проекты'

    days = util.list_dates_in_week(app.get_c_prop(settings.C_WEEK))
    for day in days:
        dates_cell_node = et.SubElement(dates_node, settings.TAG_TD_BTN_HEADER, {'style': f'width: {date_col_width};'})
        btn_day = et.SubElement(dates_cell_node, 'a', attrib={'type': 'submit', 'name': 'btn_' + day, 'value': day})
        btn_day.text = util.date_to_day(day)

    # TABLE ROWS (project + hours)
    #
    # if settings.SHOW_EMPTY_WEEK:
    prj_dict = data_module.get_all_projects_dict(app.get_c_prop(settings.C_USER_ID))
    row = 0
    for prj_id in prj_dict:
        if data is not None:
            curr_prj_data = data.get(prj_id)  # Данные на проект, на выбранную неделю
        else:
            curr_prj_data = None  # Данных на выбранную неделю нет ни по одному проекту

        if curr_prj_data is not None or (curr_prj_data is None and show_empty_projects()):  # Показывать пустые строчки проектов?
            row += 1
            prj_data = prj_dict[prj_id]
            prj_name = prj_data[settings.F_PRJ_NAME]
            row_node = et.SubElement(table_tsh, 'tr',
                                     {'style': f'background-color: {get_row_color(row)}; padding: none;'})
            project_ceil = et.SubElement(row_node, 'td', {'style': f'width: {prj_col_width};'})
            project_ceil.text = prj_name

            for day in days:
                # Для кнопки без записи
                btn_value = prj_id + settings.SPLITTER + settings.SPLITTER + day
                hours = '0'

                # Выходные
                if not util.is_work_day(day):  # util.is_week_end(day):
                    btn_tag = settings.TAG_BUTTON_TABLE_WEEKEND
                else:
                    btn_tag = settings.TAG_BUTTON_TABLE

                # Найти запись на дату и проект
                if curr_prj_data is not None:
                    tsh_data = curr_prj_data[settings.FLD_TSH_DICT].get(day)
                    tsh_id = list(tsh_data)[0]
                    if tsh_id != settings.EMPTY_ID_KEY:  # Найдена запись на эту дату
                        btn_value = prj_id + settings.SPLITTER + tsh_id + settings.SPLITTER + day
                        hours = tsh_data[tsh_id][settings.F_TSH_HOURS]
                        note = tsh_data[tsh_id][settings.F_TSH_NOTE]
                        comment = tsh_data[tsh_id][settings.F_TSH_COMMENT]

                        # Раскрасить по статусам
                        status = tsh_data[tsh_id][settings.F_TSH_STATUS]
                        title = f' title="Статус: {settings.get_status_name(status)}\nОписание: {note}\nКомментарий: {comment}"'
                        if status == settings.EDIT_STATUS:
                            btn_tag = settings.TAG_BUTTON_TABLE_EDIT + title

                        if status == settings.IN_APPROVE_STATUS:
                            btn_tag = settings.TAG_BUTTON_TABLE_IN_APPROVE + title

                        if status == settings.APPROVED_STATUS:
                            btn_tag = settings.TAG_BUTTON_TABLE_APPROVED + title

                        if status == settings.REJECTED_STATUS:
                            btn_tag = settings.TAG_BUTTON_TABLE_REJECTED + title
                # util.log_debug(f'add_timesheet_table_area: day={day}; prj_id={prj_id}; tsh_id={tsh_id}; tsh_data={tsh_data}')

                # Сформировать html для кнопки
                day_node = et.SubElement(row_node, 'td', {'style': f'width: {date_col_width};'})
                if btn_value == c_btn_value:  # Выбранная ячейка
                    btn_node = et.SubElement(day_node, btn_tag,
                                             {
                                                 'type': 'submit',
                                                 'name': settings.TABLE_BUTTON,
                                                 'value': btn_value,
                                                 'style': 'border: 3px solid blue;'})
                else:
                    btn_node = et.SubElement(day_node, btn_tag,
                                             {
                                                 'type': 'submit',
                                                 'name': settings.TABLE_BUTTON,
                                                 'value': btn_value})
                btn_node.text = hours


def add_timesheet_table_old(data, column):

    prj_col_width = '330px'
    date_col_width = '50px'
    c_btn_value = app.get_c_prop(settings.C_TSH_BTN_VALUE)

    # curr_tsh_id = app.get_c_prop(settings.C_TIMESHEET_ID)
    table_tsh = et.SubElement(column, 'table', {'style': 'width: 100%; border-spacing: 0px 0px;'})

    # HEAD ROW (project + dates)
    #
    dates_node = et.SubElement(table_tsh, 'tr')
    dates_col_node = et.SubElement(dates_node, settings.TAG_TD_BTN_HEADER, {'style': f'width: {prj_col_width};'})
    dates_col_node.text = 'Проекты'

    days = util.list_dates_in_week(app.get_c_prop(settings.C_WEEK))
    for day in days:
        dates_cell_node = et.SubElement(dates_node, settings.TAG_TD_BTN_HEADER, {'style': f'width: {date_col_width};'})
        btn_day = et.SubElement(dates_cell_node, 'a', attrib={'type': 'submit', 'name': 'btn_' + day, 'value': day})
        btn_day.text = util.date_to_day(day)

    # TABLE ROWS (project + hours)
    #
    if data is not None:
        row = 0
        for prj_id in data:
            # projects
            #
            row += 1
            days = data[prj_id][settings.FLD_TSH_DICT]
            col = 0
            row_node = et.SubElement(table_tsh, 'tr', {'style': f'background-color: {get_row_color(row)}; padding: none;'})
            project_ceil = et.SubElement(row_node, 'td', {'style': f'width: {prj_col_width};'})
            project_ceil.text = data[prj_id][settings.F_PRJ_NAME]
            for day in days:
                col += 1
                time_sheets = days[day]
                # util.log_debug(f'time_sheets: {day}={time_sheets}')
                for tsh_id in time_sheets:
                    btn_tag = settings.TAG_BUTTON_TABLE
                    tag_td = settings.TAG_TD_CENTER
                    day_node = et.SubElement(row_node, tag_td, {'style': f'width: {date_col_width};'})
                    if tsh_id == settings.EMPTY_ID_KEY:
                        # new timesheet button
                        btn_value = prj_id + settings.SPLITTER + settings.SPLITTER + day
                        hours = '0'
                    else:
                        # existing timesheet button
                        btn_value = prj_id + settings.SPLITTER + tsh_id + settings.SPLITTER + day
                        hours = time_sheets[tsh_id][settings.F_TSH_HOURS]
                        note = time_sheets[tsh_id][settings.F_TSH_NOTE]
                        comment = time_sheets[tsh_id][settings.F_TSH_COMMENT]

                        # Раскрасить по статусам
                        status = time_sheets[tsh_id][settings.F_TSH_STATUS]
                        title = f' title="Статус: {settings.get_status_name(status)}\nОписание: {note}\nКомментарий: {comment}"'
                        if status == settings.EDIT_STATUS:
                            btn_tag = settings.TAG_BUTTON_TABLE_EDIT + title

                        if status == settings.IN_APPROVE_STATUS:
                            btn_tag = settings.TAG_BUTTON_TABLE_IN_APPROVE + title

                        if status == settings.APPROVED_STATUS:
                            btn_tag = settings.TAG_BUTTON_TABLE_APPROVED + title

                        if status == settings.REJECTED_STATUS:
                            btn_tag = settings.TAG_BUTTON_TABLE_REJECTED + title

                    if btn_value == c_btn_value:  # Выбранная ячейка
                        btn_node = et.SubElement(day_node, btn_tag,
                                                 attrib={
                                                     'type': 'submit',
                                                     'name': settings.TABLE_BUTTON,
                                                     'value': btn_value,
                                                     'style': 'border: 3px solid blue;'})
                    else:
                        btn_node = et.SubElement(day_node, btn_tag,
                                                 attrib={
                                                     'type': 'submit',
                                                     'name': settings.TABLE_BUTTON,
                                                     'value': btn_value})

                    # util.log_tmp(f'btn_value: {btn_value}; btn_cache: {c_btn_value}')
                    btn_node.text = hours

    else:  # Показать доступные проекты с пустыми кнопками
        if settings.SHOW_EMPTY_PROJECTS:
            prj_dict = data_module.get_all_projects_dict(app.get_c_prop(settings.C_USER_ID))
            row = 0
            for prj_id in prj_dict:
                row += 1
                prj_data = prj_dict[prj_id]
                prj_name = prj_data[settings.F_PRJ_NAME]

                row_node = et.SubElement(table_tsh, 'tr', {'style': f'background-color: {get_row_color(row)}; padding: none;'})
                project_ceil = et.SubElement(row_node, 'td', {'style': f'width: {prj_col_width};'})
                project_ceil.text = prj_name
                # util.log_debug(f'add_timesheet_table_area: {prj_id}={prj_name}')
                for day in days:
                    day_node = et.SubElement(row_node, 'td', {'style': f'width: {date_col_width};'})
                    btn_value = prj_id + settings.SPLITTER + settings.SPLITTER + day
                    # btn_node = et.SubElement(day_node, settings.TAG_BUTTON_TABLE, attrib={'type': 'submit', 'name': settings.TABLE_BUTTON, 'value': btn_value})
                    if btn_value == c_btn_value:  # Выбранная ячейка
                        btn_node = et.SubElement(day_node,
                                                 settings.TAG_BUTTON_TABLE,
                                                 attrib={
                                                     'type': 'submit',
                                                     'name': settings.TABLE_BUTTON,
                                                     'value': btn_value,
                                                     'style': 'border: 3px solid blue;'})
                    else:
                        btn_node = et.SubElement(day_node,
                                                 settings.TAG_BUTTON_TABLE,
                                                 attrib={
                                                     'type': 'submit',
                                                     'name': settings.TABLE_BUTTON,
                                                     'value': btn_value})
                    btn_node.text = '0'


def create_timesheet_html(err_message='', values=None):
    try:
        tsh_id = app.get_c_prop(settings.C_TIMESHEET_ID)
        tsh_date = app.get_c_prop(settings.C_DATE)

        # Формируем атрибуты записи
        if values is not None:  # Режим вставки значений из кэша
            # Определить статус
            if tsh_id != '':  # При вставке в существующую запись - текущий статус
                status = values[SELECT_STATUS_NAME]
            else:  # При вставке в новую запись - всегда редактирование
                status = settings.EDIT_STATUS

            # Сформировать атрибуты
            tsh_entry = {
                settings.F_TSH_HOURS: app.get_c_prop(settings.C_HOUR_VALUE),
                settings.F_TSH_NOTE: app.get_c_prop(settings.C_NOTE_VALUE),
                settings.F_TSH_COMMENT: app.get_c_prop(settings.C_COMMENT_VALUE),
                settings.F_TSH_STATUS: status,
                settings.F_TSH_DATE: tsh_date
            }
        else:
            if tsh_id == '':  # нажата пустая кнопка на дату
                tsh_entry = {
                        settings.F_TSH_HOURS: '',
                        settings.F_TSH_NOTE: '',
                        settings.F_TSH_COMMENT: '',
                        settings.F_TSH_STATUS: '',
                        settings.F_TSH_DATE: tsh_date
                    }
            else:  # кнопка на дату с данными
                tsh_entry = data_module.get_entry(tsh_id)
                if tsh_entry is None:
                    msg = f'create_timesheet_html: Запись tsh_id="{tsh_id}" не найдена в базе данных'
                    return app.response(msg)  # Пока еще не сформирован html!!!

        # Формируем список сообщений по tsh_id
        if use_notifications_dialog() and tsh_id != '':
            notifications = data_module.get_timesheet_messages(tsh_id)
        else:
            notifications = ()

        # Формируем HTML
        base_html = BaseHTML('TimeSheets', settings.M_TIMESHEETS, err_message, notifications)

        add_timesheets_info(base_html, tsh_entry, notifications)

        # util.log_tmp(f'HTML: {base_html.get_html()}')
        return base_html.get_html()

    except Exception as ex:
        traceback.print_exc()
        return f'Произошла ошибка при формировании html страницы (TimeSheets):\n {ex}', 520  # Server Unknown Error


# USERS
#
def add_user_info(table, fields):
    def get_img_id(usr_id):
        return f'{settings.IMG_TAG_ID}_{u_id}'

    u_id = fields[0][5]
    u_role = fields[2][5]

    row = 0
    for f in fields:
        if f[0] != 'ID':  # Пропустить атрибут user_id
            first_row = et.SubElement(table, 'tr')  # 1-ая строка в общей таблице
            if row == 0:
                # Ячейка с таблицей для имен и значений текстовых свойств (1-ая ячейка 1-ой строки)
                col_props = et.SubElement(first_row, 'td', {
                    'style': 'min-width: 250px;',
                    'valign': 'top',
                })
                table_props = et.SubElement(col_props, 'table')

            props_row = et.SubElement(table_props, 'tr')  # Текущая строка в таблице текстовых свойств
            col_1 = et.SubElement(props_row, 'td', {
                'style': 'min-width: 250px;',
                'align': 'right'
            })

            # Название атрибута
            if f[4] == 'ir' or f[4] == 'p':  # Обязательные атрибуты
                fld = et.SubElement(col_1, settings.TAG_A_HEAD_REQ)
            else:
                fld = et.SubElement(col_1, settings.TAG_A_HEAD)
            fld.text = f[0]

            # Значение атрибута
            col_2 = et.SubElement(props_row, 'td', {
                'style': 'width: 300; padding-left: 5px; border: 0px solid blue;'
            })
            if f[4] == 'i' or f[4] == 'ir':  # Input
                et.SubElement(col_2, f'{settings.TAG_INPUT} size={f[1]} class=input-bottom-border',
                                  {'type': 'text', 'name': f[3], 'value': f[5]})

            if f[4] == 'p':  # Password
                et.SubElement(col_2, f'{settings.TAG_INPUT} size={f[1]} class=input-bottom-border', {
                    'type': 'password',
                    'name': f[3],
                    'value': ''
                })

            if f[4] == 'r':  # Roles List
                p_list = et.SubElement(col_2, 'select class=input-bottom-border', {'name': settings.F_USR_ROLE})
                for k in settings.R_LIST:
                    if u_role == k:
                        opt = et.SubElement(p_list, 'option selected', {'value': k})
                    else:
                        opt = et.SubElement(p_list, 'option', {'value': k})
                    opt.text = settings.R_LIST[k]

            if row == 0:
                # Ячейка с изображением пользователя (2-ая ячейка 1-ой строки)
                if u_id != '':
                    col = et.SubElement(first_row, 'td class="td-buttons"', {
                        'align': 'left',
                        'valign': 'top'
                    })
                    # Кнопки
                    img_tag_id = get_img_id(u_id)
                    div = et.SubElement(col, 'div', {
                        'style': 'background-color: #C0C0C0; border: 0px solid red;'
                    })
                    # Выбрать изображение
                    btn_select = et.SubElement(div, 'button', {
                        'onclick': f'select_img({img_tag_id});',
                        'type': 'button',
                        'class': 'material-symbols-outlined btn-t-cell',
                        'title': 'Выбрать файл с изображением',
                        'style': 'padding-inline: 0px; margin-left: 0; margin-right: 0;'
                    })
                    btn_select.text = 'person_search'
                    # Сохранить изображение
                    btn_upload = et.SubElement(div, 'button', {
                        'onclick': f'upload_img({img_tag_id});',
                        'type': 'button',
                        'class': 'material-symbols-outlined btn-t-cell',
                        'title': 'Сохранить изображение',
                        'style': 'padding-inline: 0px; margin-left: 0; margin-right: 0;'
                    })
                    btn_upload.text = 'save'
                    # Удалить изображение
                    btn_upload = et.SubElement(div, 'button', {
                        'onclick': f'delete_img({img_tag_id});',
                        'type': 'button',
                        'class': 'material-symbols-outlined btn-t-cell',
                        'title': 'Удалить изображение',
                        'style': 'padding-inline: 0px; margin-left: 0; margin-right: 0;'
                    })
                    btn_upload.text = 'delete'
                    # Область изображения
                    et.SubElement(col, 'img', {
                        # 'onload': f'upload_img({img_tag_id});',  # Почему-то не находит JS функцию ?!!
                        'id': img_tag_id,
                        'name': settings.IMG_TAG_NAME,
                        'src': '/static/img/no_image.png',
                        'style': 'width: 200; max-height: 140'
                    })
                    # et.SubElement(div, 'input', {'name': 'zxc', 'id': 'zxc_id', 'type': 'file'})

                # Ячейка с общими кнопками (3-я ячейка 1-ой строки)
                col = et.SubElement(first_row, 'td class="td-buttons"', {
                    'align': 'left', 'valign': 'top'
                })
                add_buttons(col, u_id)

                # Пустая, объединенная ячейка для выравнивания общей ширины (4-ая ячейка 1-ой строки)
                et.SubElement(first_row, 'td class="td-buttons"', {
                    'align': 'left',
                    'valign': 'middle',
                    'width': '100%',
                    'style': 'border: 0px solid blue;'
                })

            row += 1


def add_user_table(table, fields):
    x = '0px'
    # Объединенная ячейка для таблицы пользователей
    row = et.SubElement(table, 'tr')
    col = et.SubElement(row, 'td colspan=5 align=left', {'style': f'border: {x} solid black;'})  # Объединенная ячейка

    # Таблица пользователей
    table_usr = et.SubElement(col, 'table', {'style': 'width: 100%; border-spacing: 0px 0px;'})
    t_head = et.SubElement(table_usr, 'thead', {'style': 'display: table; width: 100%;'})
    # t_body = et.SubElement(table_usr, 'tbody', {'style': 'display: block; width: 100%; max-height: 100px; overflow: auto;'})

    # Заголовок таблицы пользователей
    hd_row = et.SubElement(t_head, 'tr')
    for f in fields:
        if f[4] != 'p':
            if f[0] != 'ID':
                col = et.SubElement(hd_row,
                                    'td align=left class="td-header td-header-borders"',
                                    {'style': f'width: {f[2]}; border: {x} solid red;'})
                col.text = f[0]
            else:  # Кнопка NEW вместо ID
                col = et.SubElement(hd_row,
                                    'td align=left class="td-header td-header-borders"',
                                    {'style': f'min-width: {f[2]}; border: {x} solid red;'})
                btn = et.SubElement(col,
                                    'button class="material-symbols-outlined btn-t-cell" title="Создать нового пользователя"',
                                    {
                                        'style': 'padding-inline: 0px; margin: 0; margin-left: 5',
                                        'name': settings.NEW_BUTTON,
                                    })
                btn.text = 'person_add'

    # Список пользователей из БД (тело таблицы пользователей)
    users = data_module.get_all_users_dict()
    # util.log_debug(f'create_users_html: users={users}')

    n_row = 1
    for user in users:
        row = et.SubElement(t_head, 'tr', {'style': f'background-color: {get_row_color(n_row)}; padding: none;'})
        for f in fields:
            if f[4] == 'p':
                continue
            if f[0] != 'ID':
                col = et.SubElement(row, 'td class=td-table-border',
                                    {'style': f'width: {f[2]}; border: {x} solid green;'})
                col.text = users[user][f[3]]
            else:  # Кнопки в строке таблицы
                col = et.SubElement(row, 'td align=left class=td-table-border',
                                    {'style': f'min-width: {f[2]}; border: {x} solid red;'})
                add_table_buttons(col, users[user][f[3]], settings.M_USERS)

        n_row += 1


def create_users_html(user_props=(), show_info=False, err_message='', **params):
    try:
        # Извлечение параметров, переданных через общую функцию создания HTML: app.create_module_html
        props = params.get('props')
        if props is not None:
            user_props = props

        show = params.get('show')
        if show is not None:
            show_info = show

        # Дополнительная обработка атрибутов
        u_id = '' if len(user_props) == 0 or user_props[0] is None else str(user_props[0])
        u_name = '' if len(user_props) == 0 or user_props[1] is None else str(user_props[1])
        u_role = '' if len(user_props) == 0 or user_props[2] is None else str(user_props[2])
        u_pwd = '' if len(user_props) == 0 or user_props[3] is None else str(user_props[3])
        u_mail = '' if len(user_props) == 0 or user_props[4] is None else str(user_props[4])
        u_info = '' if len(user_props) == 0 or user_props[5] is None else str(user_props[5])

        fields = (
            ('ID', 10, 80, settings.F_USR_ID, 'i', u_id),
            ('Имя', 60, 100*3, settings.F_USR_NAME, 'ir', u_name),
            ('Роль', 60, 150*3, settings.F_USR_ROLE, 'r', u_role),
            ('Пароль', 35, 100*3, settings.F_USR_PASSWORD, 'p', u_pwd),
            ('Электронный адрес', 60, 150*3, settings.F_USR_MAIL, 'i', u_mail),
            ('Дополнительная информация', 60, 500*3, settings.F_USR_INFO, 'i', u_info),
        )

        # HTML
        #
        base_html = BaseHTML('Users', settings.M_USERS, err_message)
        form = base_html.get_form()
        p = et.SubElement(form, 'p')

        # Общая таблица
        table = et.SubElement(p, 'table', {'style': 'width: 100%; border: 0px solid blue;'})

        # Поля редактирования
        if len(user_props) > 0 or show_info:
            add_user_info(table, fields)

        # Таблица пользователей
        add_user_table(table, fields)

        # util.log_debug(f'html={base_html.get_html()}')
        return base_html.get_html()

    except Exception as ex:
        traceback.print_exc()
        return f'Произошла ошибка при формировании html страницы (Users):\n {ex}', 520  # Server Unknown Error


# PROJECTS
#
def add_project_info(table, fields):

    p_id = fields[0][5]
    # get managers
    users = data_module.get_all_users_dict(managers=True)  # Поиск Managers
    # util.log_debug(f'add_project_info: managers={users}')
    if len(users) == 0:
        raise Exception(f'В базе данных нет пользователей с ролью {settings.R_MANAGER}.\nВозможно, база данных недоступна!')

    row = 0
    for f in fields:
        if f[0] != 'ID':  # Пропустить атрибут ID
            edt_row = et.SubElement(table, 'tr')

            # Название атрибута
            col_1 = et.SubElement(edt_row, 'td', {'style': 'width: 150px;', 'align': 'right'})
            if f[4] == 'ir' or f[4] == 'm':  # Обязательные атрибуты
                fld = et.SubElement(col_1, settings.TAG_A_HEAD_REQ)
            else:
                fld = et.SubElement(col_1, settings.TAG_A_HEAD)
            fld.text = f[0]

            col_2 = et.SubElement(edt_row, 'td', {'style': 'width: 200px; padding-left: 5px;'})
            # Значение атрибута
            if f[4] == 'i' or f[4] == 'ir':  # Input
                et.SubElement(col_2,
                              f'{settings.TAG_INPUT} size={f[1]} class=input-bottom-border',
                              {'type': 'text', 'name': f[3], 'value': f[5]})

            if f[4] == 'm':  # Managers list
                if p_id == '':  # Смена руководителя доступна только для существующих проектов!?
                    select = 'select disabled class=input-bottom-border'
                else:
                    select = 'select class=input-bottom-border'
                m_list = et.SubElement(col_2, select, attrib={'name': f[3], 'style': 'min-width:200px;'})
                for u in users:
                    u_id = users[u][settings.F_USR_ID]
                    u_name = users[u][settings.F_USR_NAME]
                    # util.log_debug(f'=={f[5]}={u_id}:{u_name}')
                    if f[5] == u_id:
                        opt = et.SubElement(m_list, 'option selected', attrib={'value': u_id})
                    else:
                        opt = et.SubElement(m_list, 'option', attrib={'value': u_id})
                    opt.text = u_name

            if f[4] == 'd':  # Date
                et.SubElement(col_2, settings.TAG_INPUT, attrib={'type': 'date', 'name': f[3], 'value': f[5], 'style': 'min-width:150px;'})

            # Объединенные ячейки
            if row == 0:
                # Ячейка с командой проекта
                col_3 = et.SubElement(edt_row,
                                         'td rowspan=5 class=td-buttons',
                                         {'align': 'left', 'valign': 'top', 'width': '300'})
                add_project_team(col_3, p_id)

                # Ячейка с кнопками
                col_4 = et.SubElement(edt_row,
                                         'td rowspan=5 class=td-buttons',
                                         {'align': 'left', 'valign': 'top', 'width': '40'})
                add_buttons(col_4, p_id)

                # Пустая, объединенная ячейка для выравнивания общей ширины
                col_4 = et.SubElement(edt_row,
                                      'td rowspan=5 class=td-buttons',
                                      {'align': 'left', 'valign': 'middle', 'width': 'auto',
                                       'style': 'border: 0px solid red;'})

            row += 1


def add_project_team(col, prj_id):
    # util.log_debug(f'add_project_team: {col}, {prj_id}')
    table = et.SubElement(col, 'table', {'style': 'width: 100%; border: 0px solid blue;'})
    t_head = et.SubElement(table, 'thead', {'style': 'display: table; width: 100%'})
    t_body = et.SubElement(table, 'tbody', {'style': 'display: block; height: 110px; overflow: auto; width: 100%'})

    # Заголовок таблицы
    #
    r = et.SubElement(t_head, 'tr')
    c = et.SubElement(r, 'td align="center" class="td-header td-header-borders"', {'style': 'width: 100%; border: 0px solid red;'})
    a = et.SubElement(c, 'a')
    a.text = 'Исполнители'

    # Участники (Пользователи)
    #
    users = data_module.get_all_users_dict()  # список всех пользователей
    if prj_id != '':  # команда проекта
        team = data_module.get_project_team_list(prj_id)
    else:
        team = ()
    for u in users:
        # util.log_debug(f'u={u}:{users[u][settings.F_USR_NAME]}:{users[u][settings.F_USR_ROLE]}')
        r = et.SubElement(t_body, 'tr')

        # Checkbox
        c = et.SubElement(r, 'td align="left"', {'style': 'border: 0px solid red;'})
        # util.log_debug(f'u={u} in team={team}')
        if str(u) in team:
            tag_cb = 'input type=checkbox checked'
        else:
            tag_cb = 'input type=checkbox'
        cb = et.SubElement(c, tag_cb, {'name': u, 'style': 'height: 15px'})
        # cb.text = users[u][settings.F_USR_NAME]

        # Text
        c = et.SubElement(r, 'td align="left"', {'style': 'border: 0px solid blue;'})
        a = et.SubElement(c, 'a')
        a.text = f'{users[u][settings.F_USR_NAME]} ({users[u][settings.F_USR_ROLE]})'


def add_project_table(table, fields):
    x = '0px'
    brd = 'border: 0px solid gray;'
    row = et.SubElement(table, 'tr')

    # Объединенная ячейка для таблицы проектов
    col = et.SubElement(row, 'td colspan=5 align=left', {'style': brd})

    # Таблица проектов
    table_prj = et.SubElement(col, 'table', {'style': 'width: 100%; border-spacing: 0px 0px;'})
    t_head = et.SubElement(table_prj, 'thead', {'style': 'display: table; width: 100%'})
    # t_body = et.SubElement(table_prj, 'tbody', {'style': 'display: block; max-height: 300px; overflow: auto; width: 100%'})

    # Заголовок таблицы проектов
    hd_row = et.SubElement(t_head, 'tr', {'style': 'width: 100%'})
    for f in fields:
        if f[4] == 'm':  # Пропустить колонку список пользователей
            continue
        if f[0] != 'ID':
            col_h = et.SubElement(hd_row,
                                  'td align=left class="td-header td-header-borders"',
                                  {'style': f'width: {f[2]}; border: {x} solid blue'})
            fld = et.SubElement(col_h, 'a')
            fld.text = f[0]
        else:
            col = et.SubElement(hd_row,
                                'td align=left class="td-header td-header-borders"',
                                {'style': f'width: {f[2]}; border: {x} solid blue'})
            btn = et.SubElement(col,
                                'button class="material-symbols-outlined btn-t-cell" title="Создать новый проект"',
                                {
                                    'style': 'padding-inline: 0px; margin: 0; margin-left: 5',
                                    'name': settings.NEW_BUTTON,
                                })
            btn.text = 'add_chart'

    # Список проектов из БД (тело таблицы)
    projects = data_module.get_all_projects_dict(app.get_c_prop(settings.C_USER_ID), False)
    # util.log_debug(f'add_project_table: projects={projects}')

    n_row = 1
    for p in projects:
        row = et.SubElement(t_head, 'tr', {'style': f'background-color: {get_row_color(n_row)}; padding: none;'})
        for f in fields:
            if f[4] == 'm':  # Пропустить колонку список пользователей
                continue
            if f[0] != 'ID':
                if f[4] != 'p':
                    col = et.SubElement(row, 'td class=td-table-border', {'style': f'width: {f[2]}; border: {x} solid blue'})
                    col.text = projects[p][f[3]]
            else:  # Кнопки в строке таблицы
                col = et.SubElement(row, 'td class=td-table-border', {'style': f'min-width: {f[2]}; border: {x} solid blue'})
                add_table_buttons(col, p, settings.M_PROJECTS)

        n_row += 1


def create_projects_html(prj_props=(), show_info=False, err_message='', **params):
    try:
        # Извлечение параметров, переданных через общую функцию создания HTML: app.create_module_html
        props = params.get('props')
        if props is not None:
            prj_props = props

        show = params.get('show')
        if show is not None:
            show_info = show

        # Дополнительная обработка атрибутов
        p_id = '' if len(prj_props) == 0 or prj_props[0] is None else str(prj_props[0])
        p_mgr_id = str(app.get_c_prop(settings.C_USER_ID)) if len(prj_props) == 0 or prj_props[1] is None else str(prj_props[1])
        p_name = '' if len(prj_props) == 0 or prj_props[2] is None else str(prj_props[2])
        p_s_date = '' if len(prj_props) == 0 or prj_props[3] is None else str(prj_props[3])
        p_e_date = '' if len(prj_props) == 0 or prj_props[4] is None else str(prj_props[4])
        p_org = '' if len(prj_props) == 0 or prj_props[5] is None else str(prj_props[5])

        fields = (
            ('ID', 10, 80, settings.F_PRJ_ID, 'i', p_id),
            ('Название', 50, 550*3, settings.F_PRJ_NAME, 'ir', p_name),
            ('Организация', 50, 400*3, settings.F_PRJ_ORG, 'i', p_org),
            ('Руководитель', 50, 200*3, settings.F_PRJ_MANAGER_ID, 'm', p_mgr_id),
            ('Начало', 40, 90*3, settings.F_PRJ_START_DATE, 'd', p_s_date),
            ('Окончание', 40, 40*3, settings.F_PRJ_END_DATE, 'd', p_e_date),
        )

        # HTML
        #
        base_html = BaseHTML('Projects', settings.M_PROJECTS, err_message)
        form = base_html.get_form()
        p = et.SubElement(form, 'p')

        # Общая таблица
        table = et.SubElement(p, 'table', {'style': 'width: 100%; border: 0px solid blue;'})

        # Поля редактирования
        if len(prj_props) > 0 or show_info:
            add_project_info(table, fields)

        # Таблица проектов
        add_project_table(table, fields)

        return base_html.get_html()

    except Exception as ex:
        traceback.print_exc()
        return f'Произошла ошибка при формировании html страницы (Projects):\n {ex}', 520  # Server Unknown Error


# APPROVEMENT
#
def add_approvement_info(table):
    row1 = et.SubElement(table, 'tr')

    col1 = et.SubElement(row1, 'td', {'style': 'border: 0px solid red'})
    note = et.SubElement(col1, 'textarea', {'name': 'feedback', 'placeholder': 'замечание', 'class': 'feedback'})
    note.text = '\n'

    col2 = et.SubElement(row1, 'td', {'style': 'border: 0px solid green; max-width: 105px'})
    agree_btn = et.SubElement(col2, 'button', {'type': 'submit', 'name': 'agree_btn', 'class': 'btn-left-width'})
    agree_btn.text = 'Согласовать'
    del_btn = et.SubElement(col2, 'button', {'type': 'submit', 'name': 'del_btn', 'class': 'btn-left-width'})
    del_btn.text = 'Отклонить'

    et.SubElement(row1, 'td', {'style': 'border: 0px solid black; width: 100%'})


def add_approvement_table(table, entries, is_clear):
    row = et.SubElement(table, 'tr', {'style': 'width: 100%'})
    col = et.SubElement(row, 'td colspan=3 align=left', {'style': 'border: 0px solid grey;'})  # Объединенная ячейка

    # Таблица согласований
    # Заголовок таблицы
    table_app = et.SubElement(col, 'table', {'style': 'width: 100%; border-spacing: 0px 0px;'})
    t_head = et.SubElement(table_app, 'thead class="td-header"', {'style': 'display: table; width: 100%'})
    # t_body = et.SubElement(table_app, 'tbody', {'style': 'display: block; max-height: 300px; overflow: auto; width: 100%'})

    hd_row = et.SubElement(t_head, 'tr')
    col_h = et.SubElement(hd_row, 'td align="left" class="td-header td-header-borders"',
                          {'style': 'max-width: 30; border: 0px solid blue'})
    if is_clear == '1':
        btn = et.SubElement(col_h,
                            'button class="material-symbols-outlined btn-t-cell" title="Выделить всё"',
                            {
                                'style': 'padding-inline: 0px; margin: 0; margin-left: 0',
                                'name': settings.ALL_FLAG_BUTTON, 'value': '0'
                            })
        btn.text = 'check_box'
    else:
        btn = et.SubElement(col_h,
                            'button class="material-symbols-outlined btn-t-cell" title="Очистить всё"',
                            {
                                'style': 'padding-inline: 0px; margin: 0; margin-left: 0',
                                'name': settings.ALL_FLAG_BUTTON, 'value': '1'
                            })
        btn.text = 'check_box_outline_blank'

    col_h = et.SubElement(hd_row, 'td align="left" class="td-header td-header-borders"',
                          {'style': 'width: 80; border: 0px solid blue;'})
    fld = et.SubElement(col_h, 'a')
    fld.text = 'Имя'

    col_h = et.SubElement(hd_row, 'td align="left" class="td-header td-header-borders"',
                          {'style': 'width: 80; border: 0px solid blue;'})
    fld = et.SubElement(col_h, 'a')
    fld.text = 'Дата'

    col_h = et.SubElement(hd_row, 'td align="left" class="td-header td-header-borders"',
                          {'style': 'width: 300; border: 0px solid blue;'})
    fld = et.SubElement(col_h, 'a')
    fld.text = 'Проект'

    col_h = et.SubElement(hd_row, 'td align="left" class="td-header td-header-borders"',
                          {'style': 'width: 50; border: 0px solid blue;'})
    fld = et.SubElement(col_h, 'a')
    fld.text = 'Часы'

    col_h = et.SubElement(hd_row, 'td align="left" class="td-header td-header-borders"',
                          {'style': 'width: 300; border: 0px solid blue;'})
    fld = et.SubElement(col_h, 'a')
    fld.text = 'Описание'

    col_h = et.SubElement(hd_row, 'td align="left" class="td-header td-header-borders"',
                          {'style': 'width: 300; border: 0px solid blue;'})
    fld = et.SubElement(col_h, 'a')
    fld.text = 'Комментарий'

    # Тело таблицы
    if entries is None:
        row = et.SubElement(t_head, 'tr', {'style': f'background-color: #FFFFFF;font-weight: normal'})
        col = et.SubElement(row, 'td colspan=7 align=center')
        col.text = 'Нет доступных записей'

    else:
        n_row = 1
        for s in entries:
            row = et.SubElement(t_head, 'tr', {'style': f'background-color: {get_row_color(n_row)}; padding: none;'
                                                        f'font-weight: normal'})

            cb_name = f'{s}#{entries[s][settings.F_TSH_USER_ID]}'

            if is_clear == '1':
                col = et.SubElement(row, 'td align=left', {'style': 'max-width: 30'})
                et.SubElement(col, 'input', {'type': 'checkbox', 'name': f'{cb_name}'})
            else:
                col = et.SubElement(row, 'td align=left', {'style': 'min-width: 30; max-width: 30'})
                et.SubElement(col, 'input checked', {'type': 'checkbox', 'name': f'{cb_name}'})

            col = et.SubElement(row, 'td align=left', {'style': f'width:80'})
            col.text = entries[s][settings.F_USR_NAME]
            col = et.SubElement(row, 'td align=left', {'style': 'width:80'})
            col.text = entries[s][settings.F_TSH_DATE]
            col = et.SubElement(row, 'td align=left', {'style': 'width:300'})
            col.text = entries[s][settings.F_PRJ_NAME]
            col = et.SubElement(row, 'td align=left', {'style': 'width:50'})
            col.text = entries[s][settings.F_TSH_HOURS]
            col = et.SubElement(row, 'td align=left', {'style': 'width:300'})
            col.text = entries[s][settings.F_TSH_NOTE]
            col = et.SubElement(row, 'td align=left', {'style': 'width:300'})
            col.text = entries[s][settings.F_TSH_COMMENT]

            n_row += 1


def create_approvement_html(is_clear='1', err_message=''):
    try:
        # Ищем записи на согласование
        entries = data_module.get_entries_for_approval_id(app.get_c_prop(settings.C_USER_ID))

        # HTML
        #
        base_html = BaseHTML('Approvement', settings.M_APPROVEMENT, err_message=err_message)
        form = base_html.get_form()
        p = et.SubElement(form, 'p')

        # Общая таблица
        table = et.SubElement(p, 'table', {'style': 'border: 0px solid blue;'})

        # Поля редактирования
        add_approvement_info(table)

        # Таблица на согласование
        add_approvement_table(table, entries, is_clear)

        return base_html.get_html()

    except Exception as ex:
        traceback.print_exc()
        return f'Произошла ошибка при формировании html страницы (Approvement):\n {ex}', 520  # Server Unknown Error


# Для тестирования создания html
#
def t_html():
    html = et.Element('html', attrib={'lang': 'ru'})
    head = et.SubElement(html, 'head')
    et.SubElement(head, 'link', attrib={"rel": "stylesheet", "type": "text/css", "href": 'static/css/_style.css'})
    et.SubElement(head, 'link', attrib={"rel": "stylesheet", "type": "text/css", "href": 'static/css/common.css'})
    et.SubElement(head, 'link', attrib={"rel": "stylesheet", "href": 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'})
    et.SubElement(head, 'link', {"rel": "stylesheet", "href": 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined'})

    t_title = et.SubElement(head, 'title')
    t_title.text = 'test'

    body = et.SubElement(html, 'body')
    # body.text = '{% with messages = get_flashed_messages() %} {% if messages %} {% for message in messages %} {{ message }} {% endfor %} {% endif %} {% endwith %}'
    # et.SubElement(body, "{% with messages = get_flashed_messages() %}")


    s_html = et.tostring(html).decode()
    # util.log_debug(f'=={s_html}')

    return s_html


# просмотр входящих сообщений
#
def create_msg_html(module, obj_id='', page='notifications'):

    # Если нажата кнопка Уведомления или Исходящие в Уведомлениях
    #
    if page == 'notifications' or page == 'outbox':
        return add_notifications(module, obj_id, page)

    # Если нажата кнопка Чаты
    #
    elif page == 'charts':
        return add_notifications_chats(module, obj_id)


# Формирование ссылки для возврата в текущий модуль
#
def comeback_link(url, p):
    if url != '':
        ret_url = et.SubElement(p,
                                'a class="material-symbols-outlined" title="Возврат..."',
                                {
                                    'href': url,
                                    'type': 'submit',
                                    'style': 'text-decoration-color: transparent; color: #008B8B; padding: 10px;'})
        ret_url.text = 'text_select_jump_to_beginning'


#  Формируем вкладку Уведомления или Исходящие для NOTIFICATIONS
#
def add_notifications(module, obj_id='', page='notifications'):
    msg_id = ''
    if obj_id != '':
        id_list = obj_id.split(settings.SPLITTER)
        obj_id = id_list[0]
        msg_id = id_list[1]
    # util.log_tmp(f'obj_id={obj_id}; msg_id={msg_id}')

    try:
        url_ = settings.MODULES[module][settings.M_URL]

        base_html = BaseHTML('Сообщения', module)
        p = base_html.get_form()

        # Ссылка для возврата
        comeback_link(url_, p)

        # Переключение режимов Уведомления/ Чаты
        if page == 'notifications':
            confirmation_btn = et.SubElement(p, 'button',
                                             {'style': 'width: 100;'
                                                       'font-family: Times New Roman;'
                                                       'background-color: transparent;'
                                                       'border: 2px solid var(--def-color);'
                                                       'font-weight: bold',
                                              'type': 'submit',
                                              'name': f'{settings.NOTIFICATION_BUTTON}'})
            confirmation_btn.text = 'Уведомления'
            confirmation_btn = et.SubElement(p, 'button',
                                             {'style': 'width: 100;'
                                                       'font-family: Times New Roman;'
                                                       'font-weight: normal;'
                                                       'background-color: transparent;'
                                                       'border: 1px solid var(--def-color);',
                                              'type': 'submit',
                                              'name': f'{settings.NOTIFICATION_OUTBOX_BUTTON}'})
            confirmation_btn.text = 'Исходящие'
            confirmation_btn = et.SubElement(p, 'button', {'style': 'width: 100;'
                                                                    'font-family: Times New Roman;'
                                                                    'font-weight: normal;'
                                                                    'background-color: transparent;'
                                                                    'border: 1px solid',
                                                           'type': 'submit',
                                                           'name': f'{settings.NOTIFICATION_CHARTS_BUTTON}'})
            confirmation_btn.text = 'Чаты'

            # Список сообщений(кнопки)
            msgs = data_module.get_to_me_messages(app.get_c_prop(settings.C_USER_ID))
            util.log_tmp(f'MSGS-->{msgs}')
            # msgs = data_module.get_my_messages(app.get_c_prop(settings.C_USER_ID))

        elif page == 'outbox':
            confirmation_btn = et.SubElement(p, 'button',
                                             {'style': 'width: 100;'
                                                       'font-family: Times New Roman;'
                                                       'font-weight: normal;'
                                                       'background-color: transparent;'
                                                       'border: 1px solid var(--def-color);',
                                              'type': 'submit',
                                              'name': f'{settings.NOTIFICATION_BUTTON}'})
            confirmation_btn.text = 'Уведомления'
            confirmation_btn = et.SubElement(p, 'button',
                                             {'style': 'width: 100;'
                                                       'font-family: Times New Roman;'
                                                       'background-color: transparent;'
                                                       'border: 2px solid var(--def-color);'
                                                       'font-weight: bold',
                                              'type': 'submit',
                                              'name': f'{settings.NOTIFICATION_OUTBOX_BUTTON}'})
            confirmation_btn.text = 'Исходящие'
            confirmation_btn = et.SubElement(p, 'button', {'style': 'width: 100;'
                                                                    'font-family: Times New Roman;'
                                                                    'font-weight: normal;'
                                                                    'background-color: transparent;'
                                                                    'border: 1px solid',
                                                           'type': 'submit',
                                                           'name': f'{settings.NOTIFICATION_CHARTS_BUTTON}'})
            confirmation_btn.text = 'Чаты'

            # Список сообщений(кнопки)
            # msgs = data_module.get_to_me_messages(app.get_c_prop(settings.C_USER_ID))
            msgs = data_module.get_my_messages(app.get_c_prop(settings.C_USER_ID))

        if len(msgs) == 0:
            d = et.SubElement(p, 'label')
            d.text = 'Записей нет'

        table = et.SubElement(p, 'table', {'style': 'border-right: 0px solid gray'})
        cnt = 0
        msg_props_qnt = 3
        fields = (
            ['От кого:', settings.F_USR_NAME],
            ['Дата:', settings.F_MSG_CREATION_DATE],
            ['Сообщение:', settings.F_MSG_TEXT],
            ['Дата исполнения:', settings.F_TSH_DATE],
            ['Проект:', settings.F_PRJ_NAME],
            ['Часы:', settings.F_TSH_HOURS],
            ['Статус:', settings.F_TSH_STATUS],
            ['Описание:', settings.F_TSH_NOTE],
            ['Комментарий:', settings.F_TSH_COMMENT])

        rend_2_col = False

        for m in msgs:
            util.log_tmp(f'смотрим m-->{m}')
            m_tsh_id = str(getattr(m, settings.F_TSH_ID))
            m_msg_id = str(getattr(m, settings.F_MSG_ID))
            cnt += 1
            row1 = et.SubElement(table, 'tr')
            col1 = et.SubElement(row1, 'td', {'style': f'background-color: {get_row_color(cnt)}'})
            if obj_id == m_tsh_id and msg_id == m_msg_id:
                if getattr(m, settings.F_MSG_IS_READ) == False:
                    data_module.set_read_message(msg_id)
                msg_button = et.SubElement(col1, 'button',
                                           {
                                               'style': f'white-space: pre-wrap; width: {settings.WIDTH_NOTIFICATION_BUTTON}px; border: 3px solid var(--def-color);',
                                               'type': 'submit',
                                               'name': settings.NOTIFICATION_MESSAGE_BUTTON,
                                               'value': f'{getattr(m, settings.F_TSH_ID)}{settings.SPLITTER}{getattr(m, settings.F_MSG_ID)}',
                                               'class': 'btn-msg'})
            else:
                if getattr(m, settings.F_MSG_IS_READ) == False:
                    msg_button = et.SubElement(col1, 'button',
                                               {
                                                   'style': f'white-space: pre-wrap;'
                                                            f'width: {settings.WIDTH_NOTIFICATION_BUTTON}px;'
                                                            f'font-weight: bold',
                                                   'type': 'submit',
                                                   'name': 'btn_msg',
                                                   'value': f'{getattr(m, settings.F_TSH_ID)}{settings.SPLITTER}{getattr(m, settings.F_MSG_ID)}',
                                                   'class': 'btn-msg'})
                elif getattr(m, settings.F_MSG_IS_READ) == True:
                    msg_button = et.SubElement(col1, 'button',
                                               {
                                                   'style': f'white-space: pre-wrap;'
                                                            f'width: {settings.WIDTH_NOTIFICATION_BUTTON}px;',
                                                   'type': 'submit',
                                                   'name': 'btn_msg',
                                                   'value': f'{getattr(m, settings.F_TSH_ID)}{settings.SPLITTER}{getattr(m, settings.F_MSG_ID)}',
                                                   'class': 'btn-msg'})

            msg_button.text = (
                f'{util.get_str_from_user_and_date(getattr(m, settings.F_USR_NAME), getattr(m, settings.F_MSG_CREATION_DATE))}\n'
                f'{util.str_cutter(getattr(m, settings.F_MSG_TEXT))}')

            if cnt == 1:
                if obj_id != '':
                    col2 = et.SubElement(row1, 'td',
                                         {'style': 'border: 0px solid green; vertical-align: top; padding-left: 10',
                                          'rowspan': f'{len(msgs)}'})

            util.log_tmp(f'm_tsh_id :{m_tsh_id}')
            if obj_id == m_tsh_id and msg_id == m_msg_id and not rend_2_col:
                rend_2_col = True
                row_cnt = 0
                edt_table = et.SubElement(col2, 'table',
                                          {
                                              'style': 'border: 2px solid gray; border-radius: 5px; position: top;padding-left: 5'})
                for f in fields:
                    row_cnt += 1
                    if row_cnt <= msg_props_qnt:
                        f.append(getattr(m, f[1]))
                    else:
                        tsh_props = data_module.get_entry(obj_id)
                        util.log_tmp(f'tsh_props: {tsh_props}')
                        if tsh_props['tsh_id'] != settings.INTERNAL_TIMESHEET_ID:
                            f.append(tsh_props[f[1]])

                for f in fields:
                    if len(f) >= msg_props_qnt:
                        row_1 = et.SubElement(edt_table, 'tr')
                        col_1 = et.SubElement(row_1, 'td',
                                              {'style': 'min-width: 50px; color: gray', 'align': 'right'})
                        msg_info = et.SubElement(col_1, 'label')
                        msg_info.text = f'{f[0]}'
                        col_2 = et.SubElement(row_1, 'td',
                                              {
                                                  'style': 'min-width: 200; padding-left: 5px; border-bottom: 0px solid blue;'})
                        msg_info = et.SubElement(col_2, 'label')
                        msg_info.text = f'{f[2]}'

                ## пока решили не использовать кнопку 'Удалить уведомление'
                #
                # del_conf_btn = et.SubElement(col2, 'button',
                #                              {
                #                                  'name': settings.NOTIFICATIONS_DELETE_BUTTON,
                #                                  'value': f'{msg_id}'})
                # del_conf_btn.text = 'Удалить уведомление'

        return base_html.get_html()

    except Exception as ex:
        return f'Произошла ошибка при формировании html страницы (Create MSG_HTML):\n {ex}', 520  # Server Unknown Error


#  Формируем вкладку Чаты для NOTIFICATIONS
#
def add_notifications_chats(module, obj_id=''):
    try:
        url_ = settings.MODULES[module][settings.M_URL]

        base_html = BaseHTML('Сообщения', module)
        p = base_html.get_form()

        # Ссылка для возврата
        comeback_link(url_, p)

        # Переключение режимов Уведомления/ Чаты
        confirmation_btn = et.SubElement(p, 'button',
                                         {'style': 'width: 150;'
                                                   'background-color: transparent;'
                                                   'border: 0px solid;',
                                          'type': 'submit',
                                          'name': f'{settings.NOTIFICATION_BUTTON}'})
        confirmation_btn.text = 'Уведомления'
        confirmation_btn = et.SubElement(p, 'button',
                                         {'style': 'width: 150;'
                                                   'background-color: transparent;'
                                                   'border: 0px solid var(--def-color);',
                                          'type': 'submit',
                                          'name': f'{settings.NOTIFICATION_OUTBOX_BUTTON}'})
        confirmation_btn.text = 'Исходящие'
        confirmation_btn = et.SubElement(p, 'button', {'style': 'width: 50;'
                                                                'background-color: transparent;'
                                                                'border: 0px solid;'
                                                                'font-weight: 900;'
                                                                'text-decoration: underline',
                                                       'type': 'submit',
                                                       'name': 'charts_btn'})
        confirmation_btn.text = 'Чаты'

        # Список пользователей(кнопки)
        users = data_module.get_all_users_dict(without_me=True)
        # util.log_debug(f'создаём список чатов: users={users}')
        table = et.SubElement(p, 'table', {'style': 'border-right: 0px solid gray'})

        cnt = 0
        rend_2_col = False

        for user in users:
            cnt += 1
            row1 = et.SubElement(table, 'tr')
            col1 = et.SubElement(row1, 'td', {'style': f'background-color: {get_row_color(cnt)}'})
            user_chart_button = et.SubElement(col1, 'button',
                                              {
                                                  'style': f'white-space: pre-wrap; width: {settings.WIDTH_NOTIFICATION_BUTTON}px;',
                                                  'type': 'submit',
                                                  'name': f'{settings.NOTIFICATION_USER_CHART_BUTTON}',
                                                  'value': f'{user}',
                                                  'class': 'btn-msg'})
            user_chart_button.text = (f"{users[user]['usr_name']}")

            if cnt == 1:
                if obj_id != '':
                    col2 = et.SubElement(row1, 'td',
                                         {'style': 'border: 0px solid green; vertical-align: top; padding-left: 10',
                                          'rowspan': f'{len(users)}'})
                    edt_table = et.SubElement(col2, 'table',
                                              {
                                                  'style': 'border: 0px solid gray; border-radius: 5px; position: top;padding-left: 5'})

                    # тут будет fields присвоено значение через ф-цию в дата модуле
                    msgs = data_module.get_chat_messages(obj_id, app.get_c_prop(settings.C_USER_ID))
                    fields = []
                    for m in msgs:
                        f = [m[10], m[2]]
                        fields.append(f)
                        util.log_tmp(f'msgs: {msgs}')
                    util.log_tmp(f'cписок сообщений списком---> {fields}')
                    # fields = [
                    #     [f'{obj_id}', 'Привет'],
                    #     ['You', 'Привет'],
                    #     [f'{obj_id}', 'Согласуй'],
                    #     ['You', 'Нет'],
                    #     ['You', 'Жирно будет'],
                    #     [f'{obj_id}', 'Почему?'],
                    #     ['You', 'Ты занимался ерундой, слишком много лалалала аплалдадсад']
                    # ]

                    for f in fields:
                        if f[0] == app.get_c_prop(settings.C_USER_ID):
                            row_1 = et.SubElement(edt_table, 'tr')
                            col_1 = et.SubElement(row_1, 'td',
                                                  {'style': 'width: 300px;', 'align': 'left'})
                            msg_info = et.SubElement(col_1, 'label',
                                                     {'style': 'border: 2px solid gray;'
                                                               'background-color: #E5E5E5;'
                                                               'border-radius: 5px;'
                                                               'padding-left: 3px;'
                                                               'padding-right: 3px'})
                            msg_info.text = f'{f[1]}'
                        else:
                            row_1 = et.SubElement(edt_table, 'tr')
                            col_1 = et.SubElement(row_1, 'td',
                                                  {'style': 'width: 300px;'})
                            msg_info = et.SubElement(col_1, 'pre',
                                                     {'style': 'border: 2px solid #008B8B;'
                                                               'background-color: #E8F0FE;'
                                                               'border-radius: 5px;'
                                                               'padding-left: 3px;'
                                                               'padding-right: 3px;'
                                                               'white-space: pre-wrap',
                                                      'align': 'right'})
                            msg_info.text = f'{f[1]}'

                    r1 = et.SubElement(edt_table, 'tr', {'style': 'border: 0px solid green'})
                    c1 = et.SubElement(r1, 'td', {'style': 'border: 0px solid red'})
                    add_msg = et.SubElement(c1, 'textarea',
                                            {'name': settings.NOTIFICATION_MESSAGE,
                                             'placeholder': 'Введите сообщение',
                                             'class': 'message'})
                    add_msg.text = '\n'

                    c2 = et.SubElement(r1, 'td', {'style': 'border: 0px solid blue'})
                    send_btn = et.SubElement(c2, 'button class="material-symbols-outlined btn-t-cell" title="Send"',
                                             {'style': 'height: 20px; '
                                                       'visibility: hidden; '
                                                       'width: 20px; '
                                                       'border-radius: 10px;',
                                              'type': 'submit',
                                              'name': settings.NOTIFICATIONS_ADD_MSG_BUTTON,
                                              'value': f'{obj_id}'})
                    send_btn.text = 'message'

        return base_html.get_html()

    except Exception as ex:
        return f'Произошла ошибка при формировании html страницы (Create MSG_HTML):\n {ex}', 520  # Server Unknown Error


