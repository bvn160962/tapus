/*
* Выбрать изображение
*/
async function select_img(img_tag) {
//    const img_tag = document.getElementById(img_tag_id_name); // Область отображения изображения
    console.log('select_img: ' + img_tag);                  // Почему-то, иногда, передается сам тег, а не его имя ?!

    // Выбрать файл
    [img_file] = await window.showOpenFilePicker();
    data = await img_file.getFile();


    img_tag.src = URL.createObjectURL(data); // Добавляем изображение
    img_tag.file = data;                     // Добавляем файл к тегу, для последующей выгрузки на сервер
    img_tag.onload = () => {                 // Удаляем объект после загрузки
        // console.log('unload');
        URL.revokeObjectURL(img_tag.src);
    };

    console.log(data);
}


/*
* Сохранить изображение в базе данных
*/
function upload_img(img_tag) {
//    console.log('upload_image: ' + img_tag);
    new FileUpload(img_tag)
//    console.log(img_tag.file);
}

/*
* Отправить содержимое файла (blob) на сервер
*/
function FileUpload(img_tag) {
//    const img_tag = document.getElementById(img_tag_id_name); // Область отображения изображения
    user_id = get_user_id(img_tag)
    console.log("FileUpload: " + user_id)
    if (user_id == "") {
        show_msg("Warning", "Необходимо сначала сохранить основные атрибуты пользователя, \nа затем сохранять изображение!")
        return;
    }

    if (img_tag.file == null) {
        show_msg("Warning", "Необходимо сначала выбрать изображение!")
        return;
    }

    var reader = new FileReader();
    var req = new XMLHttpRequest();
    // Обязательно POST! GET не отправляет данные
    req.open("POST", "/image_upload/"+user_id, true);
    req.onload = function (e) {
        const rq = e.target
        if (rq.status != 200) {
            console.log("Ошибка при сохранении изображения: " + rq.response + "(" + rq.status +")")
        }
    };
//    req.setRequestHeader("Content-Type", "image/png; charset=x-user-defined-binary;")
//    req.overrideMimeType("text/plain; charset=x-user-defined-binary");  // Можно и без него!

    reader.readAsArrayBuffer(img_tag.file);
    reader.onload = (evt) => { // По завершении чтения файла
        req.send(evt.target.result);
    };
}


/*
*  Загрузить изображение с сервера
*/
//function load_image() { // Почему-то не находит JS функцию !!!
//    console.log("load_image: ");
//}
// Через поиск области отображения (тэг img)
let imgArea = document.getElementsByName("img_tag_name");
load_image();

function load_image() {
    if (imgArea.length > 0) { // Нужный тэг найден
        img_tag = imgArea[0]
        user_id = get_user_id(img_tag)
        if (user_id != "") {
            var request = new XMLHttpRequest();
            request.open("GET", "/image_download/"+user_id);
            request.responseType = "blob"; // "arraybuffer" | "blob"
            request.onload = function (e) {
                const rq = e.target
                if (rq.status == 200) { // Успешно сформировано изображение
                    img_tag.src = URL.createObjectURL(rq.response);
                }
                else {
                    // Вывод сообщения через Reader:
//                    print_blob(rq.response, "Загрузка изображения: ", " (" + rq.status +")")
                    // Вывод сообщения через Promise:
                    //* rq.response - blob
                    //* rq.response.text() - Promise
                    //* rq.response.text().then - метод Promise - успешное завершение (есть еще методы catch и finally)
                    rq.response.text().then((txt, s=rq.status)  => { // Перевод blob в строку (через Promise)
                        console.log("Загрузка изображения: " + txt + " (" + s +")");
                    });

                    img_tag.src = "/static/img/no_image.png";
                }
            };
            request.send();
        }
    }
}


/*
* Удалить изображение
*/
function delete_img(img_tag) {
    user_id = get_user_id(img_tag)
    console.log("delete_img: "+user_id);
    if (user_id != "") {
        const has_img = !String(img_tag.src).endsWith("no_image.png");
        console.log("SRC: " + has_img);
        if (has_img) {
            var request = new XMLHttpRequest();
            request.open("GET", "/image_delete/"+user_id);
            request.onload = function (e) {
                const rq = e.target
                if (request.status == 200) { // Изображение успешно удалено
                    load_image()
                } else {
                    console.log("Ошибка при удалении изображения: " + rq.response + "(" + rq.status +")")
                }
            };
            request.send();
        }
    }
}


/*
* Получить user_id
*/
function get_user_id(img_tag) {
    return img_tag.id.split("_")[1];
}