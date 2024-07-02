console.log('start...');
/*
*  Работа с куками
*/
//document.cookie = "login=tom32";
//document.cookie = "password=tom32";
//console.log(document.cookie);

/*
*  Попытка поймать событие при закрытии окна
*/

//window.onclick = function (event) {
//window.onbeforeunload = function (event) {
window.onunload = function (event) {
    console.log('On close start: ' + window.closed);
    document.cookie = 'closed = ' + window.closed

/*
*  Выполнить HTTP Request (GET)
*/
    if (true) {
        var req = new XMLHttpRequest();
        req.open("GET", "/close", true);
        req.send();
    }

/*
*  Управление кэшем сессии
*/
//    console.log('Key_1 before: '+sessionStorage.getItem('key_1'));
//    sessionStorage.setItem('key_1', 'value_1');
//    console.log('Key_1 after: '+sessionStorage.getItem('key_1'));

//    window.close()

/*
*  Информационный диалог
*/
//    alert('WClosed')

/*
*  Диалог подтверждения
*/
//    const result = confirm("Завершить выполнение программы?");
//    if(result===true)
//        console.log("Работа программы завершена");
//    else
//        console.log("Программа продолжает работать");
}



/*
*  Диалог подтверждения удаления
*/
const delete_dialog = document.getElementById("confirm_dialog_id");
const okButton = document.getElementById("delete_btn_yes_id");
const cancelButton = document.getElementById("delete_btn_no_id");

// Listener для кнопки с идентификатором delete_btn_id
/***
const deleteButton = document.getElementById("delete_btn_id");
if (deleteButton != null) {
    console.log("Add listener for: " + deleteButton.id)
    deleteButton.addEventListener("click", () => {
      console.log(deleteButton);
      dialog.showModal();
    });
} else console.log("**Delete Confirm Dialog: Delete button not found!");
***/

// Listeners для всех кнопок с именем delete_btn
if (delete_dialog != null) { // Режим модального диалога включен
    let listDelButtons = document.getElementsByName("delete_btn");
    if (listDelButtons != null) {
        for( let i = 0; i < listDelButtons.length; i++) {
            console.log("Add listener for: " + listDelButtons[i].name + "; value=" + listDelButtons[i].value)
            listDelButtons[i].addEventListener("click", () => {
                okButton.value = listDelButtons[i].value
                delete_dialog.showModal();
            });
        }
    }

    // Listener на кнопку Ok
    /*
    okButton.addEventListener("click", () => {
      console.log("Ok button pressed for: " + okButton.value);
    });
    */

    // Listener на кнопку Cancel
    cancelButton.addEventListener("click", () => {
      delete_dialog.close()
    });
}




/*
*  Показать сообщение, если в cookie есть ключ "showMessage"
*/
const message_dialog = document.getElementById("message_dialog_id");
const message_dialog_text = document.getElementById("message_dialog_label_id");
const closeButton = document.getElementById("message_dialog_ok_btn_id");

function getCookie(name) {
  let cookie = document.cookie.split('; ').find(row => row.startsWith(name + '='));
  return cookie ? cookie.split('=')[1] : null;
}

console.log('showMessage: ' + getCookie('showMessage'));

message_text = getCookie('showMessage')
if (message_dialog != null) {
    // Listener на кнопку Ok
    closeButton.addEventListener("click", () => {
      message_dialog.close()
    });

    // Показать сообщение
    if (message_text != null) {
//        alert(message_text)
        message_dialog.showModal();
        console.log('delete cookie key showMessage');
        document.cookie = 'showMessage=; Max-Age=-1;'; // delete cookie key
    }
}






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

