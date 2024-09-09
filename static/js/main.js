console.log('Document properties:');
//console.log(document.title);
//console.log(document.lastModified);
//console.log(document.domain);
//console.log(document.URL);
console.log(document.charset);

/*
*  Попытка поймать событие при закрытии окна
*/
//window.onclick = function (event) {
//window.onbeforeunload = function (event) {
window.onunload = function (event) {
    console.log('On close start: ' + window.closed);
    document.cookie = 'closed = ' + window.closed


  // Выполнить HTTP Request (GET) - уменьшить счетчик текущих сессий на стороне сервера
    if (true) {
        var req = new XMLHttpRequest();
        req.open("GET", "/close", true);
        req.send();
    }
}

/*
*  Диалог подтверждения удаления - перемещение, изменение размера
*  Вариант без регистрации события на кнопке в html
*  На текущий момент вызывается при удалении записи отработанного времени (timesheet)
*/
const delete_dialog = document.getElementById("confirm_dialog_id");
const okButton = document.getElementById("delete_btn_yes_id");
const cancelButton = document.getElementById("delete_btn_no_id");

// Listeners для всех кнопок с именем delete_btn
if (delete_dialog != null && document.title == 'TimeSheets') { // Режим модального диалога включен, только для TimeSheets
    let listDelButtons = document.getElementsByName("delete_btn");
    if (listDelButtons.length > 0) {
        for( let i = 0; i < listDelButtons.length; i++) { // Для всех кнопок с именем "delete_btn"
            console.log("Confirmation Dialog: Добавлен обработчик для кнопки: " + listDelButtons[i].name + "; value=" + listDelButtons[i].value)
            listDelButtons[i].addEventListener("click", () => {
                okButton.value = listDelButtons[i].value
                delete_dialog.showModal();
            });
        }
    }
//    else console.log("Confirmation Dialog: На форме нет доступных кнопок удаления (с именем delete_btn)")

    // Listener на кнопку Cancel
    cancelButton.addEventListener("click", () => {
      delete_dialog.close()
    });

    // Перемещение диалога за заголовок - функция в common.js
    reg_move_dialog(delete_dialog, document.getElementById("confirm_header_id"));

    // Изменение размера окна диалога - функция в common.js
    reg_resize_dialog(delete_dialog,
                      document.getElementById("confirm_right_line_id"),
                      document.getElementById("confirm_bottom_line_id"),
                      document.getElementById("confirm_corner_line_id"));
}


/*
*  Показать диалог Message, если в cookie есть ключ "showMessage"
*/
const message_dialog = document.getElementById("message_dialog_id");
const message_dialog_title = document.getElementById("message_dialog_title_id");
const closeButton = document.getElementById("message_dialog_ok_btn_id");


message_type = getCookie('showMessage')
console.log('showMessage.type: ' + message_type);
show_msg(message_type, "");

/*
*  Показать сообщения по записи отработанного времени
*/
const notifications_dialog = document.getElementById("notifications_dialog_id");
const notifications_close_button = document.getElementById("notifications_dialog_close_btn_id");

// Listeners для всех кнопок с именем delete_btn
if (notifications_dialog != null) { // Режим модального диалога включен
    let listCloseButtons = document.getElementsByName("notifications_btn"); // Кнопка на timesheets_info
    if (listCloseButtons != null) {
        for( let i = 0; i < listCloseButtons.length; i++) {
            console.log("Add listener for: " + listCloseButtons[i].name + "; tsh_id=" + listCloseButtons[i].value)
            listCloseButtons[i].addEventListener("click", () => {
                notifications_dialog.showModal();
            });
        }
    }

    // Listener на кнопку Cancel
    notifications_close_button.addEventListener("click", () => {
      notifications_dialog.close()
    });

    // Перемещение диалога за заголовок - функция в common.js
    reg_move_dialog(notifications_dialog,
                    document.getElementById("notifications_dialog_header_id"));

    // Изменение размера окна диалога - функция в common.js
    reg_resize_dialog(notifications_dialog,
                      document.getElementById("notifications_right_line_id"),
                      document.getElementById("notifications_bottom_line_id"),
                      document.getElementById("notifications_corner_line_id"));
}




/*
* SOCKETS
*/
var socket = io(); /* Достаточно только создать сокет */
//socket.emit('message', 'Сокет создан');
//socket.emit('message', {data: 'Сокет создан'});

//socket.on('connect', function() { /* Регистрация действия на событие <connect>*/
//    console.log('socket connect');
//    socket.emit('message', {data: 'connected!'});
//});

socket.on('message', function(msg) { /* Регистрация обработчика на событие <message>*/
    if (msg.startsWith('show#')) {
        msg = msg.substring(5);
        console.log('get message: ' + msg);
        message_dialog_text.innerHTML = msg
        message_dialog.showModal();
    } else {
        console.log('get message: ' + msg);
    }
});

socket.on('test', function() { /* Регистрация обработчика на событие <test>*/
    console.log('get test message...');
    socket.emit('test_ok', {'status': 'ok'});
});


/*
*  Обработка кнопки "Отправить сообщение"
*/
let listNotificationButtons = document.getElementsByName("add_msg_btn"); // Кнопка "Отправить сообщение"
let listNotificationMessages = document.getElementsByName("notification_message"); // Поле ввода текста сообщения

if (listNotificationMessages.length > 0 && listNotificationButtons.length  > 0) {
    listNotificationMessages[0].addEventListener("keyup", (e) => {

      if (e.target.value == "") {
//        const attribute = document.createAttribute("disabled");
//        listNotificationButtons[0].setAttributeNode(attribute);
//        listNotificationButtons[0].setAttribute("visibility", "hidden");
//        listNotificationButtons[0].disabled = true;

        listNotificationButtons[0].style.visibility = "hidden"; // Скрыть кнопку
      }
      else {
//        listNotificationButtons[0].removeAttribute("disabled");
//        listNotificationButtons[0].setAttribute("visibility", "visible");
//        listNotificationButtons[0].disabled = false;

        listNotificationButtons[0].style.visibility = "visible"; // Показать кнопку
      }
    });
}

