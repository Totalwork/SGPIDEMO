ko.bindingHandlers.fileData = {
    init: function (element, valueAccessor) {
              
        ko.utils.registerEventHandler(element, "change", function () {

            var value = valueAccessor();
            value.value(element.files[0]);

        });

        var options = ko.utils.unwrapObservable(valueAccessor());
        var defaultOptions = {
            browseClass: "btn btn-primary",
            browseLabel: "&nbsp;Buscar",
            browseIcon: "<i class=\"fa fa-folder-open\"></i>",
            removeClass: "btn btn-danger",
            removeLabel: "Remover",
            removeIcon: "<i class=\"fa fa-trash\"></i>&nbsp;",
            showUpload: false,
            showPreview: false,
            removeTitle: "Remover archivo"
        };
        options = $.extend(true, {}, defaultOptions, options);
        $(element).fileinput(options);

        $(element).parent('div').parent('div').find('.fileinput-remove-button').click(function () {
            options.value('');           
        });

    }
};

ko.bindingHandlers.perfilImage = {
    init: function (element, valueAccessor) {

        ko.utils.registerEventHandler(element, "change", function () {

            var value = valueAccessor();
            value.value(element.files[0]);

        });

        var id=Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 5);
        var options = ko.utils.unwrapObservable(valueAccessor());
        var defaultOptions = {
            overwriteInitial: true,
            previewFileType: "image",
            browseOnZoneClick: true,
            //maxFileSize: 1500,
            showZoom: false,
            showClose: false,
            showCaption: false,            
            browseLabel: '',
            removeLabel: '',
            browseIcon: '<i class="glyphicon glyphicon-folder-open"></i>',
            removeIcon: '<i class="glyphicon glyphicon-remove"></i>',
            removeTitle: 'Remover imagen',
            elErrorContainer: '#errorBlock',
            msgErrorClass: 'alert alert-block alert-danger',
            defaultPreviewContent: '<img id="file_foto_'+id+'" src="https://s3-us-west-2.amazonaws.com/source-sinin-prueba/media/usuario/default.jpg" alt="imagen de perfil" style="width:160px"><h6>Clic aquí para seleccionar</h6>',
            //layoutTemplates: {main2: '{preview} ' +  btnCust + ' {remove} {browse}'},
            allowedFileExtensions: ["jpg","jpge"],
            showUpload: false,
            //initialPreview:[obj.source()]
        };
        options = $.extend(true, {}, defaultOptions, options);
        $(element).fileinput(options);

        var obj = valueAccessor();
        if (obj.source()!=undefined) {
           obj.source.subscribe(function(value){
            var image=obj.source && obj.source()!=null && obj.source()!='' ? obj.source() : 'https://s3-us-west-2.amazonaws.com/source-sinin-prueba/media/usuario/default.jpg';           
            $('#file_foto_'+id).attr('src',image);
           }); 
        }

        $(element).parent('div').parent('div').find('.fileinput-remove-button').click(function () {
            options.value('');           
        });

    }
};


(function () {
    var format = function (value) {
        toks = value.toFixed(2).replace('-', '').split('.');
        var display = '$' + $.map(toks[0].split('').reverse(), function (elm, i) {
            return [(i % 3 === 0 && i > 0 ? ',' : ''), elm];
        }).reverse().join('');

        return value < 0 ? '-' + display : display;
    };

    ko.subscribable.fn.money = function () {
        var target = this;
        
        var writeTarget = function (value) {
            var stripped = value.toString().replace(/[^0-9.-]/g, '');
            target(parseFloat(stripped));
        };

        var result = ko.computed({
            read: function () {
                return target();
            },
            write: writeTarget
        });

        result.formatted = ko.computed({
            read: function () {
                return format(target());
            },
            write: writeTarget
        });

        result.isNegative = ko.computed(function () {
            return target() < 0;
        });

        return result;
    };
})();


ko.bindingHandlers.onlyNumber = {
    init: function (element, valueAccessor) {
        $(element).on("keydown", function (event) {
            // Allow: backspace, delete, tab, escape, and enter
            if (event.keyCode == 46 || event.keyCode == 8  || event.keyCode == 109 || event.keyCode == 189 || event.keyCode == 9 || event.keyCode == 27 || event.keyCode == 13 ||
                // Allow: Ctrl+A
                (event.keyCode == 65 && event.ctrlKey === true) ||
                // Allow: Ctrl+V
                (event.keyCode == 86 && event.ctrlKey === true) ||
                // Allow: . ,
                (event.keyCode == 188 || event.keyCode == 190 || event.keyCode == 110) ||
                // Allow: home, end, left, right
                (event.keyCode >= 35 && event.keyCode <= 39)) {
                // let it happen, don't do anything
                return;
            }
            else {
                // Ensure that it is a number and stop the keypress
                if (event.shiftKey || (event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105)) {
                    event.preventDefault();
                }
            }

        });
    }

};


ko.bindingHandlers.onlyNumberNit = {
    init: function (element, valueAccessor) {
        $(element).on("keydown", function (event) {
            // Allow: backspace, delete, tab, escape, and enter
            if (event.keyCode == 46 || event.keyCode == 8  || event.keyCode == 109 || event.keyCode == 189 || event.keyCode == 9 || event.keyCode == 27 || event.keyCode == 13 ||
                // Allow: Ctrl+A
                (event.keyCode == 65 && event.ctrlKey === true) ||
                // Allow: Ctrl+V
                (event.keyCode == 86 && event.ctrlKey === true) ||
                // Allow: home, end, left, right
                (event.keyCode >= 35 && event.keyCode <= 39)) {
                // let it happen, don't do anything
                return;
            }
            else {
                // Ensure that it is a number and stop the keypress
                if (event.shiftKey || (event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105)) {
                    event.preventDefault();
                }
            }

        });
    }

};

// excluir caracteres \/:*?"<>|
ko.bindingHandlers.excludeCaracterMinube = {
    init: function (element, valueAccessor) {
        $(element).on("keydown", function (event) {

           
            
            // Allow: backspace, delete, tab, escape, and enter
            if (event.keyCode == 46 || event.keyCode == 8  || event.keyCode == 109 || event.keyCode == 189 || event.keyCode == 9 || event.keyCode == 27 || event.keyCode == 13 ||
                event.keyCode == 16 ||
                // Allow: Ctrl+A
                (event.keyCode == 65 && event.ctrlKey === true) ||
                // Allow: Ctrl+V
                (event.keyCode == 86 && event.ctrlKey === true) ||
                // Allow: home, end, left, right
                (event.keyCode >= 35 && event.keyCode <= 39)) {
                // let it happen, don't do anything
                
                // Allow: Ctrl+V
                if (event.keyCode == 86 && event.ctrlKey === true) {
                    // console.log(event.currentTarget.value)
                    // console.log($(element).val())

                } 

                return;
            }
            else {
                // Ensure that it is a number and stop the keypress
                /*
                \=92 , 222 ,/=47 ,:=58 ,*=42 ,?=63 ,"=34 ,<=60 ,>=62 ,|=124 
                */
                if(event.shiftKey || 
                        (                            
                            event.keyCode == 92 || event.keyCode == 222 ||
                            event.keyCode == 47 ||
                            event.keyCode == 58 ||
                            event.keyCode == 42 ||
                            event.keyCode == 63 ||
                            event.keyCode == 34 || 
                            event.keyCode == 60 ||
                            event.keyCode == 62 ||
                            event.keyCode == 124 || event.keyCode ==172                           

                        ) 
                    ) {

                    event.preventDefault();
                }
            }

        });
    }

};





ko.bindingHandlers.dropdown = {
     init: function (element, valueAccessor) {
     $(element).on('shown.bs.dropdown', function (e) {
            var $table = $(this),
                $menu = $(e.target).find('.dropdown-menu'),
                tableOffsetHeight = $table.offset().top + $table.height(),
                menuOffsetHeight = $menu.offset().top + $menu.outerHeight(true);

            if (menuOffsetHeight > tableOffsetHeight)
                $table.css("padding-bottom", menuOffsetHeight - tableOffsetHeight);
        });

        $(element).on('hide.bs.dropdown', function () {
            $(this).css("padding-bottom", 0);
        })
}
};

function ucwords(str) {

    str = str.toLowerCase();
    return str.replace(/(^([a-zA-Z\p{M}]))|([ -][a-zA-Z\p{M}])/g,
      function (s) {
          return s.toUpperCase();
      });

}

function truncar(texto, limite) {
    if (texto.length > limite) {
        limite--;
        last = texto.substr(limite - 1, 1);
        while (last != ' ' && limite > 0) {
            limite--;
            last = texto.substr(limite - 1, 1);
        }
        last = texto.substr(limite - 2, 1);
        if (last == ',' || last == ';' || last == ':') {
            texto = texto.substr(0, limite - 2) + '...';
        } else if (last == '.' || last == '?' || last == '!') {
            texto = texto.substr(0, limite - 1);
        } else {
            texto = texto.substr(0, limite - 1) + '...';
        }
    }
    return texto;
}

ko.bindingHandlers.dateRanges = {
    init: function (element, valueAccessor, allBindingsAccessor) {

        $(element).daterangepicker({
            autoUpdateInput: false,
            locale: {
                cancelLabel: 'Limpiar',
                applyLabel: 'Aplicar',
                "fromLabel": "Desde",
                "toLabel": "Hasta",
                "daysOfWeek": [
                    "Do",
                    "Lu",
                    "Ma",
                    "Mi",
                    "Ju",
                    "Vi",
                    "Sa"
                ],
                monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril',
               'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
               'Octubre', 'Noviembre', 'Diciembre'],
            }
        });

        $(element).on('apply.daterangepicker', function (ev, picker) {
            var value = valueAccessor();
            value(picker.startDate.format('YYYY-MM-DD') + ' - ' + picker.endDate.format('YYYY-MM-DD'));
        });

        $(element).on('cancel.daterangepicker', function (ev, picker) {
            var value = valueAccessor();
            value('');
        });

    }
};


ko.bindingHandlers.datePicker = {
    init: function (element, valueAccessor, allBindingsAccessor) {
        //initialize datepicker with some optional options

        var defaultOptions = { format: 'YYYY-MM-DD', 
                                locale: 'es',
                                pickTime:false};
                               
        options = allBindingsAccessor().dateTimePickerOptions || {};
        options = $.extend(true, {}, defaultOptions, options);

        $(element).datetimepicker(options);

        //when a user changes the date, update the view model
        ko.utils.registerEventHandler(element, "dp.change", function (event) {
            var value = valueAccessor();
            if (ko.isObservable(value)) {
                if (event.date != null && !(event.date instanceof Date)) {
                    var date = event.date.toDate();
                    var day = date.getDate();
                    var monthIndex = date.getMonth();
                    var year = date.getFullYear();
                    value($(element).val());
                } else {
                    var date = new Date(event.date)
                    var day = date.getDate();
                    var monthIndex = date.getMonth();
                    var year = date.getFullYear();
                    value($(element).val());
                }
            }
        });

        //  $(element).on("dp.change", function (e) {
        //     $('#datetimepicker6').data("DateTimePicker").maxDate(e.date);
        // });

        //ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        //    var picker = $(element).data("DateTimePicker");
        //    if (picker) {
        //        picker.destroy();
        //    }
        //});
    },
    //update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {

    //    var picker = $(element).data("DateTimePicker");
    //    //when the view model is updated, update the widget
    //    if (picker) {
    //        var koDate = ko.utils.unwrapObservable(valueAccessor());

    //        //in case return from server datetime i am get in this form for example /Date(93989393)/ then fomat this
    //        koDate = (typeof (koDate) !== 'object') ? new Date(parseFloat(koDate.replace(/[^0-9]/g, ''))) : koDate;

    //        picker.date(koDate);
    //    }
    //}
};

ko.bindingHandlers.datetimePicker = {
    init: function (element, valueAccessor, allBindingsAccessor) {
        //initialize datepicker with some optional options

        var options = { format: 'YYYY-MM-DD HH:mm:ss', locale: 'es'};
        options=$.extend(true, {}, allBindingsAccessor().dateTimePickerOptions, options);
        //options = allBindingsAccessor().dateTimePickerOptions || options;

        $(element).datetimepicker(options);

        //when a user changes the date, update the view model
        ko.utils.registerEventHandler(element, "dp.change", function (event) {
            var value = valueAccessor();
            if (ko.isObservable(value)) {
                if (event.date != null && !(event.date instanceof Date)) {
                    var date = event.date.toDate();
                    var day = date.getDate();
                    var monthIndex = date.getMonth();
                    var year = date.getFullYear();
                    value($(element).val());
                } else {
                    var date = new Date(event.date)
                    var day = date.getDate();
                    var monthIndex = date.getMonth();
                    var year = date.getFullYear();
                    value($(element).val());
                }
            }
        });

       
    },
   

};

ko.bindingHandlers.timePicker = {
    init: function (element, valueAccessor, allBindingsAccessor) {
        //initialize datepicker with some optional options
        var options = { pickDate: false };
        options = allBindingsAccessor().dateTimePickerOptions || options;
        $(element).datetimepicker(options);

        //when a user changes the date, update the view model
        ko.utils.registerEventHandler(element, "dp.change", function (event) {
            var value = valueAccessor();
            if (ko.isObservable(value)) {
                if (event.date != null && !(event.date instanceof Date)) {
                    var date = event.date.toDate();
                    var day = date.getDate();
                    var monthIndex = date.getMonth();
                    var year = date.getFullYear();
                    value($(element).val());
                } else {
                    var date = new Date(event.date)
                    var day = date.getDate();
                    var monthIndex = date.getMonth();
                    var year = date.getFullYear();
                    value($(element).val());
                }
            }
        });

       
    },
   
};


function formatMoney(num) {   
    return accounting.formatMoney(num);
}

ko.bindingHandlers.expander = {
    init: function (element, valueAccessor, allBindingsAccessor) {

        $(element).expander({
            slicePoint: 50,
            widow: 2,
            expandEffect: 'show',
            userCollapseText: '[^]'
        });

    }
};

function sumar_valores(lista, key) {
    var total = 0;
    ko.utils.arrayForEach(lista, function (item) {
        if (item[key].toString()==='[object Function]')
            total += item[key]();
        else
           total += item[key];     
    });
    return total;
}

function obtener_mes(mes) {

    var meses = ['Enero', 'Febrero', 'Marzo', 'Abril',
                     'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
                     'Octubre', 'Noviembre', 'Diciembre'];

    return meses[mes - 1];

}

ko.bindingHandlers.colorPicker = {
    init: function (element, valueAccessor) {

        var value = ko.utils.unwrapObservable(valueAccessor());
        $(element).val(value);

        $(element).colorpicker({
            color: '#FFFFFF'
        });

        $(element).on("keyup", function () {
            var observable = valueAccessor();
            alert($(element).data('colorpicker').color);
            observable($(element).data('colorpicker').color);
        });

        //ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        //    $(element).colorpicker("destroy");
        //});
    }
    //update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    //    var value = ko.utils.unwrapObservable(valueAccessor());       
    //    $(element).colorpicker('setValue',value);  
    //    $(element).change();
    //}
};

ko.bindingHandlers.dropdown_stop_propagacion = {
    init: function (element, valueAccessor) {
        $(element).on('click', function (e) {
            e.stopPropagation();
        });
    }
};

function convertToObservableArray(datos) {
    var data = [];
    ko.utils.arrayForEach(datos, function (p) {
        data.push(ko.mapping.fromJS(p));
    });
    return data;
}

function convertToObservable(row) {
    return ko.mapping.fromJS(row);
}

ko.bindingHandlers.cutWord = {
    init: function (element, valueAccessor) {


        var value = valueAccessor();
        var campo = value.text==null ? '' : value.text;
        var verMax = value.verMax || 'Ver Mas';
        var verMin = value.verMin || 'Ver Menos';
        var num = value.num || 10;
        var textMin = campo.substr(0, num);        
        var span = $('<span>'+textMin+'</span>');
        $(element).append(span);

        if (campo != num && campo.length > num) {

            var linkMax = $('<a style="cursor:pointer;color:#4a89dc">' + verMax + '</a>');
            var linkMin = $('<a style="cursor:pointer;display:none;;color:#4a89dc">' + verMin + '</a>');
           
            var textMax = campo;
           
            $(element).append(linkMax);
            $(element).append(linkMin);

            $(linkMax).click(function () {                
                $(span).text(textMax);
                $(this).hide();
                $(linkMin).show();
            });

            $(linkMin).click(function () {                
                $(span).text(textMin);
                $(this).hide();
                $(linkMax).show();
            });

        }

    }
};


function roundNumber(num, decimal) {
    return num.toString().substring(0, num.toString().indexOf('.')) + (num.toString().substr(num.toString().indexOf('.'), decimal + 1));
}


ko.bindingHandlers.selectedText = {
    init: function (element, valueAccessor, allBindingsAccessor) {
        $(element).click(function () {
            $(element).select();
            return false;
        });
    }
}




function agregarOpcionesObservable(data){
  
  if (data!=null) {
   for (var i = 0; i < data.length; i++) {
     data[i]['procesar']=ko.observable(false);
     data[i]['eliminado']=ko.observable(false);
     data[i]['valor_generico']=ko.observable('');
   };
  }
   return data;
}



function agregarOpciones(data){
  
  if (data!=null) {
   for (var i = 0; i < data.length; i++) {
     data[i]['procesar']=false;
     data[i]['eliminado']=false;
   };
  }
   return data;
}


ko.bindingHandlers.tooltip = {
    init: function (element, valueAccessor, allBindingsAccessor) {
        var value = valueAccessor()
        $(element).tooltip(value); 
    }
}


function format_fecha(fecha){

    var fecha=new Date(fecha);
    var anno=fecha.getFullYear();
    var mes= fecha.getMonth()+1;
    var dia= fecha.getDate();
    var hora= fecha.getHours();
    var minutos= fecha.getMinutes();
    var segundos= fecha.getSeconds();
    mes = (mes < 10) ? ("0" + mes) : mes;
    dia = (dia < 10) ? ("0" + dia) : dia;
    var fecha_completa=anno+'-'+mes+'-'+dia+" "+hora+":"+minutos+":"+segundos;

    return fecha_completa

}

