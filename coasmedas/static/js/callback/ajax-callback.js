var mensajeNoFound = '<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron registros</div>';
var mensajeNoFoundOk = '<div class="alert alert-success alert-dismissable"><i class="fa fa-warning"></i>No se encontraron eventos para alertar</div>';
var mensajeInformativoBusuqeda = '<div class="alert alert-info alert-dismissable"><i class="fa fa-info pr10"></i> No se han seleccionado parametros de busqueda.</div>';
var resultadosPorPagina = 20;
//var path_principal='http://52.42.43.115:8000';// la ruta del servidor
//var path_principal = 'http://localhost:8000'; // la ruta del servidor
var path_principal = ''; // se deja vacia esta variable para poder trabajr en el local y el servidor
var token = localStorage.getItem('token');
var ver_div = true

function mensajeExitoso(mensaje, titulo) {
    $.confirm({
        title: titulo || 'Confirmación',
        content: '<h4><i class="text-success fa fa-check-circle-o fa-2x"></i> ' + mensaje + '<h4>',
        cancelButton: 'Cerrar',
        confirmButton: false
    });
}

function mensajeError(mensaje, titulo) {
    $.confirm({
        title: titulo || 'Error',
        content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i> ' + mensaje + '<h4>',
        cancelButton: 'Cerrar',
        confirmButton: false
    });
}

function mensajeInformativo(mensaje, titulo) {
    $.confirm({
        title: titulo || 'Información',
        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> ' + mensaje + '<h4>',
        cancelButton: 'Cerrar',
        confirmButton: false
    });
}


function mensageNoFound(mensaje) {
    return '<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>' + mensaje + '</div>';
}

function cerrarLoading() {
    $('#loading').hide();
}

function RequestAnularOEliminar(contenido, path, parameter, callback, completado, alerta) {

    $.confirm({
        title: 'Confirmar!',
        content: "<h4>" + contenido + "</h4>",
        confirmButton: 'Si',
        confirmButtonClass: 'btn-info',
        cancelButtonClass: 'btn-danger',
        cancelButton: 'No',
        confirm: function() {

            var parametros = {
                callback: callback,
                url: path,
                parametros: parameter,
                completado: completado,
                metodo: 'DELETE',
                alerta: alerta == undefined ? true : alerta

            };
            Request(parametros);
        }
    });
}

function RequestAnular(contenido, path, parameter, callback, completado, alerta) {

    $.confirm({
        title: 'Confirmar!',
        content: "<h4>" + contenido + "</h4>",
        confirmButton: 'Si',
        confirmButtonClass: 'btn-info',
        cancelButtonClass: 'btn-danger',
        cancelButton: 'No',
        confirm: function() {

            var parametros = {
                callback: callback,
                url: path,
                parametros: parameter,
                completado: completado,
                metodo: 'POST',
                alerta: alerta == undefined ? true : alerta

            };
            Request(parametros);
        }
    });


}

// La funcion RequestGet reciebe los siguiente parametros que ya muchos de ellos conocesmos:

// RequestGet(callback, path, parameter, completado, cerrarLoading)

// callback: Recibe la funcion que nos devuelve la respuesta de la peticion
// path: ruta del api o servicio
// parameter: parametros del api o servicio
// completado: recibe la funcion que nos indica cuando se completo la peticion ej:
// RequestGet(function (datos, estado, mensage) {   

// }, path, {}, function(){
//                     //codigo que queremos q se ejecute una ves la peticion se halla completado
//                    }, false/true/Vacio);

// cerrarLoading: parametro que se puede dejar vacio y se nos va a cerrar el Loading o establecerlo en true y false para que no se cierre 
// el Loading y cerrarlo nosotros con la funcion cerrarLoadin()

function RequestGet(callback, path, parameter, completado, cerrarLoading, abrirLoading) {
    //PETICION GET
    $.ajax({
        data: parameter,
        url: path,
        type: 'GET',
        dataType: "JSON",
        headers: { 'Authorization': 'Bearer ' + token },
        beforeSend: function(xhr) {
            if (abrirLoading == undefined || abrirLoading == true)
                $('#loading').show();
        },
        success: function(response) {

            if (response.results == undefined) {
                callback(response.data, response.success || response.status, response.message);
            } else if (response.results != undefined) {
                // var data = {
                //     count: response.data.count,
                //     next: response.data.next,
                //     previous: response.data.previous,
                //     data: response.data.result.data
                // };
                if (response.data != undefined) {
                    callback(response.data, response.success || response.status, response.message);
                } else {
                    callback(response.results, response.results.success || response.results.status, response.results.message);
                }
            }

            if (cerrarLoading == undefined || cerrarLoading == true)
                $('#loading').hide();

        },
        complete: function() {
            if (completado != undefined) {
                completado();
            }
            if (cerrarLoading == undefined || cerrarLoading == true)
                $('#loading').hide();
        },
        error: function(response) {

            mensajeError(response.responseJSON.message);
            $('#loading').hide();
        }
    });
}


function RequestGetNoToken(callback, path, parameter, completado, cerrarLoading, abrirLoading) {
    //PETICION GET
    $.ajax({
        data: parameter,
        url: path,
        type: 'GET',
        dataType: "JSON",
        // headers: { 'Authorization': 'Bearer ' + token },
        beforeSend: function(xhr) {
            if (abrirLoading == undefined || abrirLoading == true)
                $('#loading').show();
        },
        success: function(response) {

            if (response.results == undefined) {
                callback(response.data, response.success || response.status, response.message);
            } else if (response.results != undefined) {
                // var data = {
                //     count: response.data.count,
                //     next: response.data.next,
                //     previous: response.data.previous,
                //     data: response.data.result.data
                // };
                if (response.data != undefined) {
                    callback(response.data, response.success || response.status, response.message);
                } else {
                    callback(response.results, response.results.success || response.results.status, response.results.message);
                }
            }

            if (cerrarLoading == undefined || cerrarLoading == true)
                $('#loading').hide();

        },
        complete: function() {
            if (completado != undefined) {
                completado();
            }
            if (cerrarLoading == undefined || cerrarLoading == true)
                $('#loading').hide();
        },
        error: function(response) {

            mensajeError(response.responseJSON.message);
            $('#loading').hide();
        }
    });
}



/*
Estructura que recibe

{
     metodo:'POST',//por defecto
     callback:function(){},//funcion para recibir la respuesta
     url:'htt://localhost/api/metodo'//url api
     parametros:{},//parametros
     completado:function(){},//funcion completa del ajax
     alerta:true,//si quiere que devuelva el mensaje de confirmacion
 }

*/
function Request(parametros) {

    var defaultOptions = {
        metodo: 'POST', //por defecto
        url: '',
        callback: function() {},
        parametros: {}, //parametros
        completado: function() {}, //funcion completa del ajax
        alerta: true //si quiere que devuelva el mensaje de confirmacion
    };
    parametros = $.extend(true, {}, defaultOptions, parametros);
    $.ajax({
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            _content_type: "application/json",
            _method: parametros.metodo,
            _content: ko.toJSON(parametros.parametros)
        },
        // data: ko.toJSON(parametros.parametros),
        url: parametros.url,
        type: parametros.metodo,
        //contentType: "application/json; charset=utf-8",
        dataType: "json",
        headers: { 'Authorization': 'Bearer ' + token },

        beforeSend: function(xhr) {
            $('#loading').show();
        },
        success: function(response) {

            //parametros.callback(response);
            if (response.success == 'ok' || response.status == 'success') {
                parametros.callback(response.data, response.success || response.status, response.message);
                if (parametros.alerta)
                    mensajeExitoso(response.message);
            } else {
                parametros.callback(response.data, response.success || response.status, response.message);
                if (parametros.alerta)
                    mensajeError(response.message);
            }
            $('#loading').hide();
        },
        complete: function() {
            parametros.completado();
            $('#loading').hide();
        },
        error: function(response) {

            mensajeError(response.responseJSON.message);

            $('#loading').hide();
        }
    });
}

//este metodo lo utilizamos cuando vamos a guardar archivos y el parametro de es tipo array
function RequestFormData(parametros) {


    var met = '';
    if ((parametros.metodo == undefined) || (parametros.metodo == 'POST')) {
        met = 'POST'
    } else {
        met = 'PUT'
    }



    var defaultOptions = {
        //metodo: 'POST', //por defecto
        metodo: met,
        url: '',
        callback: function() {},
        parametros: {}, //parametros
        completado: function() {}, //funcion completa del ajax
        alerta: true //si quiere que devuelva el mensaje de confirmacion
    };
    parametros = $.extend(true, {}, defaultOptions, parametros);
    //PETICION POST CON FORMDATA Y ENVIAR ARCHIVOS
    var forData = new FormData();
    var parameter = parametros.parametros;
    forData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    forData.append('_method', parametros.metodo);
    for (var key in parameter) {

        if (typeof parameter[key] == 'function' && (parameter[key]() == null || parameter[key]().toString() != '[object Object]')) { //si es un dato comun
            forData.append(key, parameter[key]());
        } else if (typeof parameter[key] != 'function' && parameter[key].toString() == '[object Object]' && parameter[key] != null) { //si es un arreglo
            for (var key2 in parameter[key]) {
                forData.append(key + '.' + key2, parameter[key][key2]());
            }
        } else if ((typeof parameter[key]()) == 'object' && parameter[key]() != null && parameter[key]().length > 0 &&
            (parameter[key]().__proto__ == null || parameter[key]().__proto__ == undefined)) { //si es un json
            for (var key2 in parameter[key]()) {
                for (var key3 in parameter[key][key2]) {
                    forData.append(key + '[' + key2 + '][' + key3 + ']', parameter[key][key2][key3]());
                }
            }
        } else if (parameter[key]().toString() == '[object File]' && parameter[key]() != null &&
            parameter[key]().size != null && parameter[key]().size != undefined && parameter[key]().size > 0) { //si es un archivo
            forData.append(key, parameter[key]());
        }

    }

    var bar = $('#progressbar .progress-bar');
    var percent = $('#progressbar .progress-bar');
    var status = $('#status');

    percent.text("0%");
    bar.attr("aria-valuenow", 0);
    bar.css("width", "0%");

    $.ajax({

        xhr: function() {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener("progress", function(evt) {
                if (evt.lengthComputable) {
                    var percentComplete = evt.loaded / evt.total;
                    percentComplete = parseInt(percentComplete * 100);
                    //console.log(percentComplete);
                    percent.text(percentComplete + "%");
                    // actualizamos la cantidad avanzada en la barra de progreso
                    bar.attr("aria-valuenow", percentComplete);
                    bar.css("width", percentComplete + "%");
                }
            }, false);
            return xhr;
        },
        url: parametros.url,
        //type: 'POST',
        type: met,
        contentType: false,
        data: forData,
        processData: false,
        cache: false,
        dataType: 'json',
        headers: { 'Authorization': 'Bearer ' + token },
        beforeSend: function(xhr) {
            $('#progressbar').show();
        },
        success: function(response) {

            if (response.success == 'ok' || response.status == 'success') {
                parametros.callback(response.data, response.success || response.status, response.message);
                if (parametros.alerta)
                    mensajeExitoso(response.message);
            } else {
                parametros.callback(response.data, response.success || response.status, response.message);
                if (parametros.alerta)
                    mensajeError(response.message);
            }

            //parametros.callback(response);
            $('#progressbar').hide();
        },
        complete: function() {
            parametros.completado();
            $('#progressbar').hide();
        },
        error: function(response) {

            mensajeError(response.responseJSON.message);

            $('#progressbar').hide();
        }

    });
}

//este metodo lo utilizamos cuando vamos a guardar archivos y el parametro es tipo formdata
function RequestFormData2(parametros) {

    var met = '';
    if ((parametros.metodo == undefined) || (parametros.metodo == 'POST')) {
        met = 'POST'
    } else {
        met = 'PUT'
    }

    var defaultOptions = {
        metodo: 'POST', //por defecto
        url: '',
        callback: function() {},
        parametros: {}, //parametros
        completado: function() {}, //funcion completa del ajax
        alerta: true //si quiere que devuelva el mensaje de confirmacion
    };
    parametros = $.extend(true, {}, defaultOptions, parametros);

    var bar = $('#progressbar .progress-bar');
    var percent = $('#progressbar .progress-bar');
    var status = $('#status');

    percent.text("0%");
    bar.attr("aria-valuenow", 0);
    bar.css("width", "0%");

    parametros.parametros.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    parametros.parametros.append('_method', parametros.metodo);


    $.ajax({

        xhr: function() {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener("progress", function(evt) {
                if (evt.lengthComputable) {
                    var percentComplete = evt.loaded / evt.total;
                    percentComplete = parseInt(percentComplete * 100);
                    //console.log(percentComplete);
                    percent.text(percentComplete + "%");
                    // actualizamos la cantidad avanzada en la barra de progreso
                    bar.attr("aria-valuenow", percentComplete);
                    bar.css("width", percentComplete + "%");
                }
            }, false);
            return xhr;
        },
        url: parametros.url,
        type: met,
        contentType: false,
        data: parametros.parametros,
        processData: false,
        cache: false,
        dataType: 'json',
        headers: { 'Authorization': 'Bearer ' + token },
        beforeSend: function(xhr) {
            $('#progressbar').show();
        },
        success: function(response) {
            //alert('entro al success ' + response.status);

            if ((response.success == 'ok') || (response.success == 'success') || (response.status == 'success') || (response.status == 'ok')) {
                parametros.callback(response.data, response.success || response.status, response.message);
                if (parametros.alerta)
                    mensajeExitoso(response.message);
            } else {
                parametros.callback(response.data, response.success || response.status, response.message);
                if (parametros.alerta)
                    mensajeError(response.message);
            }
            $('#progressbar').hide();
        },
        complete: function() {
            parametros.completado();
            $('#progressbar').hide();
        },
        error: function(response) {
            //alert('entro al error');
            mensajeError(response.responseJSON.message);

            $('#progressbar').hide();
        }

    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



function RequestGetAutenticacion(callback, path, parameter, completado, cerrarLoading, abrirLoading) {
    //PETICION GET
    $.ajax({
        data: parameter,
        url: path,
        type: 'GET',
        dataType: "JSON",
        headers: { 'Authorization': 'Basic bGVjdHVyYV9kaXNwYWM6MTIzNDU=' },
        beforeSend: function() {
            if (abrirLoading == undefined || abrirLoading == true)
                $('#loading').show();
        },
        success: function(response) {

            if (response.results == undefined) {
                callback(response.data, response.success || response.status, response.message);
            } else if (response.results != undefined) {
                var data = {
                    count: response.count,
                    next: response.next,
                    previous: response.previous,
                    data: response.results.data
                };
                callback(data, response.results.success || response.status, response.results.message);
            }

            if (cerrarLoading == undefined || cerrarLoading == true)
                $('#loading').hide();

        },
        complete: function() {
            if (completado != undefined) {
                completado();
            }
            if (cerrarLoading == undefined || cerrarLoading == true)
                $('#loading').hide();
        },
        error: function(response) {

            mensajeError(response.responseJSON.message);
            $('#loading').hide();
        }
    });
}

function Request37(parametros) {

    var defaultOptions = {
        metodo: 'POST', //por defecto
        url: '',
        callback: function() {},
        parametros: {}, //parametros
        completado: function() {}, //funcion completa del ajax
        alerta: true //si quiere que devuelva el mensaje de confirmacion
    };
    parametros = $.extend(true, {}, defaultOptions, parametros);
    $.ajax({
        data: ko.toJSON(parametros.parametros),
        url: parametros.url,
        type: parametros.metodo,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        headers: { 'Authorization': 'Bearer ' + token },

        beforeSend: function(xhr) {
            $('#loading').show();
        },
        success: function(response) {

            //parametros.callback(response);
            if (response.success == 'ok' || response.status == 'success') {
                parametros.callback(response.data, response.success || response.status, response.message);
                if (parametros.alerta)
                    mensajeExitoso(response.message);
            } else {
                parametros.callback(response.data, response.success || response.status, response.message);
                if (parametros.alerta)
                    mensajeError(response.message);
            }
            $('#loading').hide();
        },
        complete: function() {
            parametros.completado();
            $('#loading').hide();
        },
        error: function(response) {

            mensajeError(response.responseJSON.message);

            $('#loading').hide();
        }
    });
}

//este metodo lo utilizamos cuando vamos a guardar archivos y el parametro es tipo formdata
function RequestFormData37(parametros) {

    var met = '';
    if ((parametros.metodo == undefined) || (parametros.metodo == 'POST')) {
        met = 'POST'
    } else {
        met = 'PUT'
    }

    var defaultOptions = {
        metodo: 'POST', //por defecto
        url: '',
        callback: function() {},
        parametros: {}, //parametros
        completado: function() {}, //funcion completa del ajax
        alerta: true //si quiere que devuelva el mensaje de confirmacion
    };
    parametros = $.extend(true, {}, defaultOptions, parametros);

    var bar = $('#progressbar .progress-bar');
    var percent = $('#progressbar .progress-bar');
    var status = $('#status');

    percent.text("0%");
    bar.attr("aria-valuenow", 0);
    bar.css("width", "0%");

    $.ajax({

        xhr: function() {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener("progress", function(evt) {
                if (evt.lengthComputable) {
                    var percentComplete = evt.loaded / evt.total;
                    percentComplete = parseInt(percentComplete * 100);
                    //console.log(percentComplete);
                    percent.text(percentComplete + "%");
                    // actualizamos la cantidad avanzada en la barra de progreso
                    bar.attr("aria-valuenow", percentComplete);
                    bar.css("width", percentComplete + "%");
                }
            }, false);
            return xhr;
        },
        url: parametros.url,
        type: parametros.metodo,
        contentType: false,
        data: parametros.parametros,
        processData: false,
        cache: false,
        dataType: 'json',
        headers: { 'Authorization': 'Bearer ' + token },
        beforeSend: function(xhr) {
            $('#progressbar').show();
        },
        success: function(response) {

            if (response.success == 'ok' || response.status == 'success') {
                parametros.callback(response.data, response.success || response.status, response.message);
                if (parametros.alerta)
                    mensajeExitoso(response.message);
            } else {
                parametros.callback(response.data, response.success || response.status, response.message);
                if (parametros.alerta)
                    mensajeError(response.message);
            }
            $('#progressbar').hide();
        },
        complete: function() {
            parametros.completado();
            $('#progressbar').hide();
        },
        error: function(response) {

            mensajeError(response.responseJSON.message);

            $('#progressbar').hide();
        }

    });
}