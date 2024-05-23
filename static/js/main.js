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

