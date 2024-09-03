/*
* Выбрать изображение
*/
async function select_img(img_tag) {
//    console.log('select_image: ' + img_tag); // Почему-то передается сам тег, а не его имя ?!!!!!!!
//    const img_tag = document.getElementById(img_tag_id_name); // Область отображения изображения

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


function FileUpload(img_tag) {
//    var file = new Blob([data], {type: file_type});

//    var a = document.createElement('a'),
//        url = URL.createObjectURL(img_tag.file);
//    a.href = url;
//    a.download = 'c:\\temp\\xxx.png';
//    document.body.appendChild(a);
//    a.click();
//    setTimeout(function() {
//      document.body.removeChild(a);
//      window.URL.revokeObjectURL(url);
//    }, 0);

    var reader = new FileReader();
    var req = new XMLHttpRequest();
    user_id = '141'

    req.open('POST', '/upload_image/'+user_id, true);
    req.setRequestHeader("Content-Type", "image/png; charset=x-user-defined-binary;")
//    req.overrideMimeType("text/plain; charset=x-user-defined-binary");
    req.overrideMimeType("image/png; charset=x-user-defined-binary");

    reader.readAsBinaryString(img_tag.file);
    reader.onload = (evt) => { // По завершении чтения файла
        console.log("data:" + evt.target.result)
        req.send(evt.target.result);
    };
}

