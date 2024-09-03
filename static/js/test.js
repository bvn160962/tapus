/*
*  Работа с куками
*/
//document.cookie = "login=tom32";
//document.cookie = "password=tom32";
//console.log(document.cookie);

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

/*
* Получить полный путь к файлу
*/
//const load_file = document.getElementById('zxc_id');
//load_file.addEventListener('change', async function() {
////    var fullPath = load_file.value;
////    console.log(fullPath);
//    // Вызов диалога загрузки файла
////    [fileHandle] = await window.showOpenFilePicker();
////    data = await fileHandle.getFile();
////    console.log('path: ' + data.webkitRelativePath + ';');
//});

/*
* Загрузить файл
*/
const load_file = document.getElementById('zxc_id');
const img_tag = document.getElementById('img_id');
load_file.addEventListener('change', async function() {
    img_file = load_file.files[0]
//    console.log(img_tag);
//    console.log(img_file);

    img_tag.src = URL.createObjectURL(img_file);
//    img_tag.classList.add("img");  // Добавляем class узла, для поиска
    img_tag.file = img_file;       // Добавляем файл
    img_tag.onload = () => { // Удаляем объект после загрузки
//        console.log(img_tag.src);
        URL.revokeObjectURL(img_tag.src);
    };

    // Список всех узлов с классом 'img'
//    const imgs = document.querySelectorAll('img');
//    console.log('Количество: ' + imgs.length);
//
//    console.log(imgs[0], imgs[0].file);
    console.log(img_tag.file);

});