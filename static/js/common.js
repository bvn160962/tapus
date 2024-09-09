/*
* Не реагировать на нажатие Enter (в узлах input и других)
*/
function skip_enter(event) {
    if(event.keyCode==13) {
        return false;
    }
}


/*
* Показать модальное окно с сообщением
*/
function show_msg(p_msg_type, p_msg_text) {
    if (message_dialog != null) {
        // Перемещение диалога за заголовок - функция в common.js
        reg_move_dialog(message_dialog, document.getElementById("message_dialog_header_id"));

        // Изменение размера окна диалога - функция в common.js
        reg_resize_dialog(message_dialog,
                          document.getElementById("message_right_line_id"),
                          document.getElementById("message_bottom_line_id"),
                          document.getElementById("message_corner_line_id"));
        // Listener на кнопку Ok
        closeButton.addEventListener("click", () => {
          message_dialog.close()
        });

        // Показать сообщение
        if (p_msg_type != null) { // Заголовок диалога
            if (p_msg_type == 'Error')
                message_dialog_title.innerHTML = 'Ошибка';
            else
                message_dialog_title.innerHTML = 'Сообщение';

            if (p_msg_text != "") { // Изменить текст сообщения
                const msg_text = document.getElementById("message_dialog_text_id");
                msg_text.innerHTML = p_msg_text;
            }

            message_dialog.showModal();
            document.activeElement.blur(); // Убирает фокус на кнопке Close

            console.log('delete cookie key showMessage');
            document.cookie = 'showMessage=; Max-Age=-1;'; // delete cookie key
        }
    }

}


/*
* Обработка onclick на узле "Количество непрочитанных сообщений"
* через нажатие кнопки с именем "notification_btn" (передается в качестве параметра btn_name)
* Событие регистрируется в Python!
*/
function msg_count_click(btn_name) {
    let buttons = document.getElementsByName(btn_name);
    if (buttons.length > 0)
        buttons[0].dispatchEvent(new MouseEvent("click"));
    else
       console.log('msg_count_click.Error: Кнопка с именем "' + btn_name + '" не найдена!')
}


/*
* Прочитать значение куки по ключу
*/
function getCookie(key) {
  let cookie = document.cookie.split('; ').find(row => row.startsWith(key + '='));
  return cookie ? cookie.split('=')[1] : null;
}


/*
*  Функция обработки диалога подтверждения удаления - перемещение, изменение размера
*  Вариант с регистрацией события на кнопке в html
*  На текущий момент вызывается при удалении пользователя или проекта (users, projects)
*/
function show_confirm_dialog(params) {
    dialog_id = params[0];
    cancel_button_id = params[1];
    ok_button_id = params[2];
    msg_id = params[3];
    header_id = params[4];
    bottom_line_id = params[5];
    right_line_id = params[6];
    corner_line_id = params[7];
    msg_text = params[8];
    obj_id = params[9];

    const dialog = document.getElementById(dialog_id);
    if (dialog == null) {
        console.log("show_confirm_dialog.Error: Диалог подтверждения id=" + dialog_id + " не найден!");
        return;
    }

    const close_btn = document.getElementById(cancel_button_id);
    if (close_btn == null) {
        console.log("show_confirm_dialog.Error: Кнопка отмены id=" + cancel_button_id + " не найдена!");
        return;
    }

    const ok_btn = document.getElementById(ok_button_id);
    if (ok_btn == null) {
        console.log("show_confirm_dialog.Error: Кнопка подтверждения id=" + ok_button_id + " не найдена!");
        return;
    }

    const header = document.getElementById(header_id);
    const bottom_line = document.getElementById(bottom_line_id);
    const right_line = document.getElementById(right_line_id);
    const corner_line = document.getElementById(corner_line_id);

    const msg_label = document.getElementById(msg_id);
    if (msg_label == null) {
        console.log("show_confirm_dialog.Error: Метка текста сообщения id=" + msg_label + " не найдена!");
        return;
    }

    // Подсветка удаляемого объекта
    const obj_delete_btn = document.getElementById(obj_id);
    if (obj_delete_btn == null) {
        console.log("show_confirm_dialog.Error: Кнопка удаления объекта id=" + obj_id + " не найдена!");
    } else { // установить подсветку
        obj_delete_btn.style.borderTop = "3px solid blue"
        obj_delete_btn.style.borderBottom = "3px solid blue"
        obj_delete_btn.style.borderRadius = "7px"
        obj_delete_btn.style.padding = "0 0 0 0"
    }

    // Обработчик кнопки close_btn
    close_btn.addEventListener("click", () => {
        console.log("close...");
        // убрать подсветку
        obj_delete_btn.style.border = "";
        obj_delete_btn.style.padding = "0 0 0 2";
        dialog.close();
    });


    // Идентификатор удаляемого объекта
    ok_btn.value = obj_id

    // Текст сообщения
    msg_label.textContent = msg_text;

    dialog.showModal();

    // Перемещение диалога за заголовок - функция в common.js
    reg_move_dialog(dialog, header);

    // Изменение размера окна диалога - функция в common.js
    reg_resize_dialog(dialog, right_line, bottom_line, corner_line);
}


/*
*  Проверка доступности элементов управления для перемещения окна
*/
function check_moving(p_dialog, p_holder) {
    if (p_dialog == null) {
        console.log("check_moving.Error: Диалог подтверждения не найден! Перемещение недоступно.");
        return false;
    }

    if (p_holder == null) {
        console.log("check_moving.Error: Элемент, за который необходимо тянуть не найден! Перемещение недоступно.");
        return false;
    }

    return true;
}


/*
*  Обработка перемещения диалога
*/
function reg_move_dialog(p_dialog, p_holder) {
    // Проверка доступности элементов управления
    if (check_moving(p_dialog, p_holder) != true) return;

    // Запретить drag&drop (иногда срабатывает после перемещения правее границы)
    p_holder.ondragstart = function() {
        console.log("ondragstart...")
      return false;
    }

    // Начать перетаскивания заголовка
    p_holder.onmousedown = function(event) {

        let shiftX = event.clientX - p_holder.getBoundingClientRect().left + 200; // 200 это margin-left для dialog в классе .dial-pos
        let shiftY = event.clientY - p_holder.getBoundingClientRect().top + 100; // 100 это margin-top для dialog в классе .dial-pos

        function onMouseMove(event) {
            p_dialog.style.left = event.pageX - shiftX + 'px';
            p_dialog.style.top = event.pageY - shiftY + 'px';
        }

        document.addEventListener('mousemove', onMouseMove);

        p_dialog.onmouseup = function() {
            document.removeEventListener("mousemove", onMouseMove);
            p_dialog.onmouseup = null;
        };
    }
}


/*
*  Проверка доступности элементов управления для изменения размеров окна
*/
function check_sizing(p_dialog, p_right, p_bottom, p_corner) {
    if (p_dialog == null) {
        console.log("check_sizing.Error: Диалог подтверждения не найден! Изменение размеров недоступно.");
        return false;
    }

    if (p_right == null) {
        console.log("check_sizing.Error: Элемент правая граница не найден! Изменение размеров недоступно.");
        return false;
    }

    if (p_bottom == null) {
        console.log("check_sizing.Error: Элемент нижняя граница не найден! Изменение размеров недоступно.");
        return false;
    }

    if (p_corner == null) {
        console.log("check_sizing.Error: Элемент нижний правый угол не найден! Изменение размеров недоступно.");
        return false;
    }

    return true;
}


/*
*  Обработка изменения размера окна диалога
*/
function reg_resize_dialog(p_dialog, p_right, p_bottom, p_corner) {
    // Проверка доступности элементов управления
    if (check_sizing(p_dialog, p_right, p_bottom, p_corner) != true) return;

    // Начать изменение размера окна по Х
    p_right.onmousedown = function(event) {
        let xLeft = p_dialog.getBoundingClientRect().left;

        function onMouseMove(event) {
            p_dialog.style.width = event.clientX - xLeft;
            console.log('width: ' + p_dialog.style.width)
        }
        document.addEventListener('mousemove', onMouseMove);

        p_dialog.onmouseup = function() {
            console.log('UP')
            document.removeEventListener("mousemove", onMouseMove);
            p_dialog.onmouseup = null;
        };
    }

    // Начать изменение размера окна по У
    p_bottom.onmousedown = function(event) {
        let yTop = p_dialog.getBoundingClientRect().top;

        function onMouseMove(event) {
            p_dialog.style.height = event.clientY - yTop;
        }
        document.addEventListener('mousemove', onMouseMove);

        p_dialog.onmouseup = function() {
            document.removeEventListener("mousemove", onMouseMove);
            p_dialog.onmouseup = null;
        };
    }

    // Начать изменение размера окна по Х и У
    p_corner.onmousedown = function(event) {
        let yTop = p_dialog.getBoundingClientRect().top;
        let xLeft = p_dialog.getBoundingClientRect().left;

        function onMouseMove(event) {
            p_dialog.style.height = event.clientY - yTop;
            p_dialog.style.width = event.clientX - xLeft;
        }
        document.addEventListener('mousemove', onMouseMove);

        p_dialog.onmouseup = function() {
            document.removeEventListener("mousemove", onMouseMove);
            p_dialog.onmouseup = null;
        };
    }
}


/*
* Перекодировка строки для текста с кириллицей в куке
* Используется кодировка в виде: \108\206... (похожа на raw-unicode-escape)
* Пока не работает!!!
*/
function buffer_to_string (buffer) {
// result.decode('unicode-escape').encode('raw-unicode-escape')
    const decoder = new TextDecoder('unicode-escape');
    str = buffer.substr(1, buffer.length - 2)

//    let bu = new ArrayBuffer(4);
//    let view = new Uint8Array(bu);
//    view[0] = 206;
//    view[1] = 207;
//    view[2] = 208;
//    view[3] = 209;
//    const text = decoder.decode(bu);
//    console.log('bu: ' + text)
//    return text;


    const arrayBuffer = new TextEncoder().encode(str);
    console.log('arrayBuffer: ' + arrayBuffer)


    return decoder.decode(arrayBuffer);
}


// Вывести сообщение, содержащее текст в виде blob (b"\x02...")
function print_blob(blob_msg, text, status) {
    var reader = new FileReader();
    reader.onload = (e) => { // Преобразовать blob в строку
        console.log(text + e.target.result + status)
    };
    reader.readAsText(blob_msg);
}

