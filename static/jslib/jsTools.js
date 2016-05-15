/**
@kangtian
@date: 2015/11/28
@desc: JS Tools lib
*/

function printString(str, end)
{
    if(end != ''){
        str += '\n';
    }
    $("#debug").append(str);
}

function formatToString(x)
{
    var s;
    if(typeofMe(x) == '[object Object]'){
        s = JSON.stringify(x);
    }else if(typeofMe(x) == '[object Array]'){
        for(var i = 0; i < x.length; i ++){
            if(typeofMe(x[i]) == '[object Object]' || typeofMe(x[i]) == '[object Array]'){
                x[i] = formatToString(x[i]);
            }
        }
        s = x.join(', ');
    }else{
        s = x + '';
    }
    return s;
}

function typeofMe(x)
{
    var res = Object.prototype.toString.call(x);
    return res;
}

function get_value_of_key_in_JSON(json_obj, find_key, path, result_list)
{
    if(typeof(result_list) == "undefined")
        result_list = [];
    if(typeofMe(json_obj) != '[object Object]' && typeofMe(json_obj) != '[object Array]')
        return null;
    if(typeofMe(json_obj) == '[object Object]'){
        for(var key in json_obj){
            if(key == find_key){
                result_list.push(json_obj[key]);
            }
            if(typeofMe(json_obj[key]) == '[object Array]' || typeofMe(json_obj[key]) == '[object Object]'){
                p = path + '.' + formatToString(key);
                get_value_of_key_in_JSON(json_obj[key], find_key, p, result_list);
            }
        }
    }else if(typeofMe(json_obj) == '[object Array]'){
        for(var i = 0; i < json_obj.length; i ++){
            var item = json_obj[i];
            if(typeofMe(item) == '[object Object]' || typeofMe(item) == '[object Array]'){
                p = path + '.' + formatToString(json_obj);
                get_value_of_key_in_JSON(item, find_key, p, result_list);
            }
        }
    }
    return result_list;
}

// order can be 'desc' or 'esc', default is 'desc'
function lambda_sort(data_list, func_map, func_cmp, order, parameter)
{
    var len = data_list.length;
    var temp;
    for(var i = 0; i < len - 1; i ++){
        for(var j = i + 1; j < len; j ++){
            if(func_map == "" || func_map == undefined || func_map == null){
                a = data_list[i];
                b = data_list[j];
            }else{
                a = func_map(data_list[i], parameter);
                b = func_map(data_list[j], parameter);
            }
            cmp = func_cmp(a, b, parameter);
            if(cmp < 0 && order != 'esc' || cmp > 0 && order == 'esc'){
                temp = data_list[i];
                data_list[i] = data_list[j];
                data_list[j] = temp;
            }
        }
    }
    return data_list;
}

function number_fix(num, length) {
  return ('' + num).length < length ? ((new Array(length + 1)).join('0') + num).slice(-length) : '' + num;
}

function map_version(version){
    v = version.split('.');
    s = '';
    for(var i = 0; i < v.length && i < 3; i ++){
        s += number_fix(v[i], 3)
    }
    return s;
}

function show_cond_selector(selector, status, show_list, now) {
    if (now == null) {
        now = $(selector).attr('selected');
        if (!now) {
            now = show_list[0];
        }
    }
    $(selector).empty();
    if(status == 'ok'){
        for (var i in show_list){
            text = show_list[i];
            if (text == now)
                $(selector).append('<option  selected="' + text + '" value=' + text + ' > ' + text + ' </option>');
            else
                $(selector).append('<option value="' + text + '" > ' + text + ' </option>');
        }
    }else{
        text = now;
        $(selector).append('<option  selected="' + text + '" value=' + text + ' > ' + text + ' </option>');

    }
}

/** Python Code:
def get_value_of_key_in_JSON(json_dict, pkey, path='root', result_list=[]):
    if not (isinstance(json_dict, dict) or isinstance(json_dict, list)):
        return None
    for key in json_dict:
        p = path + '.' + str(key)
        if pkey == key and isinstance(json_dict, dict):
            result_list.append(json_dict[key])
        if isinstance(json_dict, dict) and (isinstance(json_dict[key], dict) or isinstance(json_dict[key], list)):
            get_value_of_key_in_JSON(json_dict[key], pkey, path=p, result_list=result_list)
        if isinstance(json_dict, list):
            get_value_of_key_in_JSON(key, pkey, path=p, result_list=result_list)
    return result_list
*/

/**
 * W3C File API
 * Note: 当发生 submit 事件时, 调试 console 内容会被清空(网页刷新), 因此调试时请不要讲 startRead 绑定到 submit 事件.
 * readFile(obj_id, i, callback_done, callback_process);
 * callback_done(data, status);
 *     data: utf-8 text
 *     status: success or failed.
 * callback_process(percent);
 */

function readFile(obj_id, callback_done, callback_process){
    _callback_done_function = callback_done;
    _callback_process_function = callback_process;
    _file_name_now = null;
    startRead(obj_id, 0);
}

function startRead(obj_id, i){
    // obtain input element through DOM
    if(i == null){
        i = 0;
    }
    var file = document.getElementById(obj_id).files[i];
    if(file){
        getAsArrayBuffer(file);
    }else{
        console.log('There are no file in file-obj ... ');
    }
}

function getAsArrayBuffer(readFile) {
    var reader = new FileReader();
    _file_name_now = readFile.name;

    reader.readAsArrayBuffer(readFile);

    reader.onprogress = updateProgress;
    reader.onload = loadedArrayBuffer;
    reader.onerror = errorHandler;
}

function getAsText(readFile) {
    var reader = new FileReader();
    _file_name_now = readFile.name;

    reader.readAsText(readFile, "UTF-8");

    reader.onprogress = updateProgress;
    reader.onload = loadedText;
    reader.onerror = errorHandler;
}

function updateProgress(evt) {
    if (evt.length > 0) {
        var loaded = (evt.loaded / evt.total);
        if (loaded < 1) {
            console.log('Mark-loaded: ' + loaded + '%');
            if(typeof(_callback_process_function) == 'function')
                _callback_process_function(loaded);
        }
    }
}

function loadedText(evt) {
    var fileString = evt.target.result;

    if(typeof(_callback_done_function) == 'function')
        _callback_done_function(fileString, _file_name_now, 'success');
}

function loadedArrayBuffer(evt) {
    var data = evt.target.result;
    var array = new Int8Array(data);

    if(typeof(_callback_done_function) == 'function')
        _callback_done_function(array, _file_name_now, 'success');
}

function errorHandler(evt) {
    if(evt.target.error.name == "NotReadableError") {
        console.log('open file failed... ');
    }
    console.log('read file failed, unknown reason ... ');
    _call_back_function(fileString, 'failed');
}

/**************   W3C File API end  ****************/


function uploadFile(post_url, file)
{
    // Uploading - for Firefox, Google Chrome and Safari
    var xhr = new XMLHttpRequest();

    // File uploaded
    xhr.addEventListener("load", function ()
    {
        alert('upload finish');
    }, false);

    xhr.open("post", post_url, true);

    // Set appropriate headers
    xhr.setRequestHeader("Content-Type", "multipart/form-data");
    xhr.setRequestHeader("X-File-Name", file.fileName);
    xhr.setRequestHeader("X-File-Size", file.fileSize);
    xhr.setRequestHeader("X-File-Type", file.type);

    // Send the file
    xhr.send(file);
}

