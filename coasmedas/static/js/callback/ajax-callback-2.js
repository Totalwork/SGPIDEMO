
var mensajeNoFound='<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning fa-2x"></i>No se encontraron registros</div>';
var resultadosPorPagina = 2;

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
        title: titulo || 'Confirmación',
        content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i> ' + mensaje + '<h4>',
        cancelButton: 'Cerrar',
        confirmButton: false
    });
}

function mensajeInformativo(mensaje, titulo) {
    $.confirm({
        title: titulo || 'Confirmación',
        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> ' + mensaje + '<h4>',
        cancelButton: 'Cerrar',
        confirmButton: false
    });
}

function RequestAnularOEliminar(contenido, path, parameter, completado) {

    $.confirm({
        title: 'Confirmar!',
        content: "<h4>" + contenido + "</h4>",
        confirmButton: 'Si!',
        confirmButtonClass: 'btn-info',
        cancelButtonClass: 'btn-danger',
        cancelButton: 'No',
        confirm: function () {
            RequestPost(function (datos, estado, mensaje) {
                //if (estado == 'success') {
                //    mensajeExitoso(mensaje);
                //} else {
                //    mensajeError(mensaje);
                //}
            }, path, parameter, completado);
        }
    });


}

function RequestGet(callback, path, parameter, completado) {
    //PETICION GET
    $.ajax({

        data: parameter,
        url: path,
        type: 'GET',
        dataType: "JSON",
        beforeSend: function () {
            $('#loading').show();
        },
        success: function (response) {
           // console.log(response.results);
            if(response.results==undefined){
                callback(response, response.count);
            }else{
               callback(response.results, response.count); 
            }
            
            $('#loading').hide();
        },
        complete: function () {
            if (completado != undefined) {
                completado();
            }
            $('#loading').hide();
        },
        error: function (data, textStatus, jqXHR) {
            $('#loading').hide();
        }
    });
}

function RequestPost(callback, path, parameter, completado) {
    //PETICION POST
    $.ajax({
        data:{csrfmiddlewaretoken : getCookie('csrftoken'),
            _content_type:"application/json",_content:parameter},
        url: path,
        type: 'POST',
        //contentType: "application/json; charset=utf-8",
        dataType: "json",
        //crossDomain:false,
        beforeSend: function () {
            $('#loading').show();
        },
        success: function (response) {
            alert(response)
            if (response.estado == 'success') {
                callback(response.datos, response.estado, response.mensaje);
                mensajeExitoso(response.mensaje);
            } else {
                mensajeError(response.mensaje);
            }
            $('#loading').hide();
        },
        complete: function () {
            if (completado != undefined) {
                completado();
            }
            $('#loading').hide();
        },
        error: function (data, textStatus, jqXHR) {
            $('#loading').hide();
        }
    });
}
//esta peticion no manda un mensaje
function RequestPostNotMsg(callback, path, parameter, completado) {
    //PETICION POST
    $.ajax({
        data: parameter,
        url: path,
        type: 'POST',
        beforeSend: function () {
            $('#loading').show();
        },
        success: function (response) {
            if (response.estado == 'success') {
                callback(response.datos, response.estado, response.mensaje);
                //mensajeExitoso(response.mensaje);
            } else {
                //mensajeError(response.mensaje);
            }
            $('#loading').hide();
        },
        complete: function () {
            if (completado != undefined) {
                completado();
            }
            $('#loading').hide();
        },
        error: function (data, textStatus, jqXHR) {
            $('#loading').hide();
        }
    });
}

function RequestPostFormData(callback, path, parameter, completado) {
    //PETICION POST CON FORMDATA Y ENVIAR ARCHIVOS    
    var forData = new FormData();
    forData.append('csrfmiddlewaretoken',getCookie('csrftoken'));
    for (var key in parameter) {

        if (typeof parameter[key] == 'function' && (parameter[key]() == null || parameter[key]().toString() != '[object Object]')) {//si es un dato comun
            forData.append(key, parameter[key]());
        }
        else if (typeof parameter[key] != 'function' && parameter[key].toString() == '[object Object]' && parameter[key] != null) {//si es un arreglo
            for (var key2 in parameter[key]) {
                forData.append(key + '.' + key2, parameter[key][key2]());
            }
        }
        else if ((typeof parameter[key]()) == 'object' && parameter[key]() != null && parameter[key]().length > 0 &&
            (parameter[key]().__proto__ == null || parameter[key]().__proto__ == undefined)) {//si es un json
            for (var key2 in parameter[key]()) {
                for (var key3 in parameter[key][key2]) {
                    forData.append(key + '[' + key2 + '][' + key3 + ']', parameter[key][key2][key3]());
                }
            }
        }
        else if (parameter[key]().toString() == '[object File]' && parameter[key]() != null &&
            parameter[key]().size != null && parameter[key]().size != undefined && parameter[key]().size > 0) {//si es un archivo
            forData.append(key, parameter[key]());
        }

    }

    var bar = $('.progress-bar');
    var percent = $('.progress-bar');
    var status = $('#status');

    $.ajax({

        xhr: function () {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener("progress", function (evt) {
                if (evt.lengthComputable) {
                    var percentComplete = evt.loaded / evt.total;
                    percentComplete = parseInt(percentComplete * 100);
                    console.log(percentComplete);
                    percent.text(percentComplete + "%");
                    // actualizamos la cantidad avanzada en la barra de progreso
                    bar.attr("aria-valuenow", percentComplete);
                    bar.css("width", percentComplete + "%");
                }
            }, false);
            return xhr;
        },
        url: path,
        type: 'PUT',
        contentType: false,
        data: forData,
        processData: false,
        cache: false,
        dataType: 'json',
        beforeSend: function () {
            $('#progressbar').show();
        },
        success: function (response) {
            if (response.estado == 'success') {
                callback(response.datos, response.estado, response.mensaje);
                mensajeExitoso(response.mensaje);
            } else {
                mensajeError(response.mensaje);
            }
            $('#progressbar').hide();
        },
        complete: function () {
            $('#progressbar').hide();
        },
        error: function () {
            $('#progressbar').hide();
        }

    });
}

function RequestPostFormData2(callback, path, parameter, completado) {
  
    var bar = $('.progress-bar');
    var percent = $('.progress-bar');
    var status = $('#status');
    forData.append('csrfmiddlewaretoken',getCookie('csrftoken'));
    
    $.ajax({

        xhr: function () {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener("progress", function (evt) {
                if (evt.lengthComputable) {
                    var percentComplete = evt.loaded / evt.total;
                    percentComplete = parseInt(percentComplete * 100);
                    console.log(percentComplete);
                    percent.text(percentComplete + "%");
                    // actualizamos la cantidad avanzada en la barra de progreso
                    bar.attr("aria-valuenow", percentComplete);
                    bar.css("width", percentComplete + "%");
                }
            }, false);
            return xhr;
        },
        url: path,
        type: 'POST',
        contentType: false,
        data: parameter,
        processData: false,
        cache: false,
        dataType: 'json',
        beforeSend: function () {
            $('#progressbar').show();
        },
        success: function (response) {
            if (response.estado == 'success') {
                callback(response.datos, response.estado, response.mensaje);
                mensajeExitoso(response.mensaje);
            } else {
                mensajeError(response.mensaje);
            }
            $('#progressbar').hide();
        },
        complete: function () {
            $('#progressbar').hide();
        },
        error: function () {
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


