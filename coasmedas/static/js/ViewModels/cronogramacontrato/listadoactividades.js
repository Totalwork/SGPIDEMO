function ListadoActividadesViewModel(){
    var self = this;
    self.cambio = 0;
    self.listado_capitulos = ko.observableArray([]);
    self.filtro=ko.observable('');
    self.posiblesValores = ko.observableArray([{value: true,text: "Si"},{value: false,text: "No"}]);
    self.listado_actividades = ko.observableArray([]);
    self.cronograma_id = ko.observable();
    self.nombreCronograma = ko.observable();
    self.cambio_id = ko.observable();
    self.capituloid = ko.observable($('#capituloid').val());
    self.idCapitulo = ko.observable('');
    self.nombreCapitulo = ko.observable('');
    self.mensaje = ko.observable('');
    self.nregistros = ko.observable('');
    self.titulo = ko.observable('');
    self.url=path_principal+'/api/';
    self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(5),
        directiones: ko.observable(true),
        limite: ko.observable(true),
        cantidad_por_paginas: ko.observable(0),
        text: {
            first: ko.observable('Inicio'),
            last: ko.observable('Fin'),
            back: ko.observable('<'),
            forward: ko.observable('>')
        }
    }

    self.capituloVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: ' Digite el nombre del capitulo.' } }),
        cronograma_id:ko.observable('').extend({ required: { message: ' Selecione el nombre del cronograma.' } }),
        orden:ko.observable('').extend({ required: { message: ' Digite el orden del capitulo.' } })
    }

    self.actividadVO={
        id:ko.observable(0),
        capitulo_id:ko.observable('').extend({ required: { message: ' Selecione el nombre del capitulo.' } }),
        orden:ko.observable('').extend({ required: { message: ' Digite el orden del capitulo.' } }),
        descripcion:ko.observable('').extend({ required: { message: ' Digite la descripción del capitulo.' } }),
        inicioprogramado:ko.observable('').extend({ required: { message: ' Digite el valor del inicio programado.' } }),
        finprogramado:ko.observable('').extend({ required: { message: ' Digite el valor del fin programado.' } }),
        requiereSoporte:ko.observable('').extend({ required: { message: ' Digite el valor del soporte.' } }),
        soporteObservaciones:ko.observable('').extend({ required: { message: ' Digite el valor del soporteObservaciones.' } }),
        
    }



    self.paginacion.pagina_actual.subscribe(function (pagina) {    
        self.getDataTable(pagina);
     });
 
     self.llenar_paginacion = function (data,pagina) {
 
         self.paginacion.pagina_actual(pagina);
         self.paginacion.total(data.count);       
         self.paginacion.cantidad_por_paginas(resultadosPorPagina);
     }

     self.consultar = function (pagina) {
        
        self.filtro($('#txtBuscar').val());
        // alert(self.filtro()+' consultar')
        path = path_principal + '/api/CActividad/?filterbyname=1&nombre='+self.filtro()+'&capituloid=' + self.capituloid()+'&page='+pagina+'';
        if(self.filtro() == ''){
            path = path_principal + '/api/CActividad/?listbyid=1&capituloid='+ self.capituloid()+'&page='+pagina;
        }
        parameter = {};
        RequestGet(function (datos, estado, mensage) {

            if(estado == 'ok' && datos!=null){
                // alert(datos.data)
                self.listado_actividades(datos.data);
                self.nregistros(datos.count);
                self.mensaje('');
                cerrarLoading();  
            }
             else {
                // alert('else')
                self.listado_actividades(['']);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                cerrarLoading();
                
            }
            self.llenar_paginacion(datos, pagina);
        }, path, parameter);
    }


     self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }



     self.crear = function(){
        self.titulo('Crear actividad');
        self.limpiar();
        $("#activacrear").show();
        $("#activaeditar").hide();
        $('#modal_actividad').modal('show');
     }

     self.editar = function(obj){
        self.limpiar();
        self.cambio = 0;
        // alert('editando ' + obj.descripcion + ' id capitulo: ' + obj.capitulo.id);
        self.titulo('Editar Actividad');
        self.actividadVO.id(obj.id);
        self.actividadVO.capitulo_id(obj.capitulo.id);
        // alert(obj.capitulo.id)
        self.actividadVO.orden(obj.orden);
        self.actividadVO.descripcion(obj.descripcion);
        self.actividadVO.inicioprogramado(obj.inicioprogramado);
        self.actividadVO.finprogramado(obj.finprogramado);
        self.actividadVO.requiereSoporte(obj.requiereSoporte);
        self.actividadVO.soporteObservaciones(obj.soporteObservaciones);
        $("#activacrear").hide();
        $("#activaeditar").show();
        $('#modal_actividad').modal('show');
    }

     self.eliminar_actividad=function(id){
        var path =path_principal+'/api/CActividad/'+id+'/';
        var parameter = {metodo:'DELETE'};
        RequestAnularOEliminar("Esta seguro que desea eliminar el registro?", path, parameter, 
            function(datos, estado, mensaje){
                if (estado=='ok') { 
                    self.getDataTable(1);
                }        
        });
    }

    self.modal_mover=function(obj){
        // alert(obj.id);
        self.limpiar();
        self.cambio = 1;
        self.getCapitulos(1);
        self.titulo('Mover Actividad');
        self.actividadVO.id(obj.id);
        self.actividadVO.capitulo_id(self.cambio_id());
        self.actividadVO.orden(obj.orden);
        self.actividadVO.descripcion(obj.descripcion);
        self.actividadVO.inicioprogramado(obj.inicioprogramado);
        self.actividadVO.finprogramado(obj.finprogramado);
        self.actividadVO.requiereSoporte(obj.requiereSoporte);
        self.actividadVO.soporteObservaciones(obj.soporteObservaciones);
        
        
        $('#modal_mover_actividad').modal('show');
    }

    self.mover_actividad=function(){
        self.cambio_id();
        self.actividadVO.capitulo_id(self.cambio_id());
    }

    self.guardar_tabla = function () {
        var lista_id = [];
        var count = 0;
        ko.utils.arrayForEach(self.listado_actividades(), function (d) {
            lista_id.push({
                id: d.id,
                descripcion: d.descripcion,
                orden: d.orden,
                inicioprogramado: d.inicioprogramado,
                finprogramado: d.finprogramado,
                requiereSoporte: d.requiereSoporte,
                soporteObservaciones: d.soporteObservaciones
            })
        });

        
        var path = path_principal + '/cronogramacontrato/actualizaractividad/';
        var parameter = { lista: lista_id };

        // RequestAnularOEliminar("Esta seguro que desea actualizar las actividades seleccionadas?", path, parameter, function (){
        //     self.getDataTable(1);
        // });
        var contenido = "Esta seguro que desea actualizar las actividades seleccionadas?";
        $.confirm({
            title: 'Confirmar!',
            content: "<h4>" + contenido + "</h4>",
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.getDataTable(1);
                        }                     
                     },//funcion para recibir la respuesta 
                     url: path,//url api
                     parametros:parameter                       
                };                
                Request(parametros);
            }
        });

    }


    self.getCapitulos = function(pagina){
        path = path_principal + '/api/CCapitulo?filterbyid=1&cronograma_id=' + self.cronograma_id()+'&page='+pagina;
        parameter = {};

        RequestGet(function (datos){
            if( datos!=null){
                self.listado_capitulos(datos.data);
                // alert(datos.data)
                
            } else{
                self.listado_capitulos([]);
                alert('false')
            }
            self.llenar_paginacion(datos, pagina);
        }, path,parameter);

    }


    self.guardar = function(){
        // self.mover_actividad();
        // if (CapitulosEsquemaViewModel.errores_capitulo().length == 0) {//se activa las validaciones
            if(self.actividadVO.id()==0){
                self.actividadVO.capitulo_id(self.capituloid());
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.getDataTable(1);
                            $('#modal_actividad').modal('hide');
                            self.limpiar();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url+'CActividad/',//url api
                     parametros:self.actividadVO                        
                };
                
                RequestFormData(parametros);
            }else{
                // self.actividadVO.capitulo_id(self.idCapitulo());        
                if (self.cambio == 1){
                    self.mover_actividad();
                }
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                                self.getDataTable(1);
                                $('#modal_actividad').modal('hide');
                                $('#modal_mover_actividad').modal('hide');
                                self.limpiar();
                            } 
                       },//funcion para recibir la respuesta 
                       url: self.url+'CActividad/'+ self.actividadVO.id()+'/',
                       parametros:self.actividadVO                        
                  };
                  RequestFormData(parametros);
            }
        // } else {
        //     CapitulosEsquemaViewModel.errores_capitulo.showAllMessages();//mostramos las validacion
        //     alert('else ' + CapitulosEsquemaViewModel.errores_capitulo.showAllMessages());
            
        // }
    }

    self.limpiar = function(){
        self.actividadVO.id(0);
        self.actividadVO.descripcion('');
        self.actividadVO.descripcion.isModified(false);
        
        self.actividadVO.capitulo_id(0);
        self.actividadVO.capitulo_id.isModified(false);
        self.actividadVO.orden('');
        self.actividadVO.inicioprogramado('');
        self.actividadVO.finprogramado('');
        self.actividadVO.requiereSoporte('');
        self.actividadVO.soporteObservaciones('');

    }


    self.getDataTable = function(pagina){
        path = path_principal + '/api/CActividad/?listbyid=1&capituloid='+ self.capituloid()+'&page='+pagina;
        parameter = {};

        RequestGet(function (datos){
            if(datos!=null && datos.count > 0){
                self.listado_actividades(datos.data);
                if (datos.count > 0){
                    self.nombreCapitulo(datos.data[0].capitulo.nombre);
                    self.nombreCronograma(datos.data[0].capitulo.cronograma.nombre);
                    self.cronograma_id(datos.data[0].capitulo.cronograma.id);
                }
                self.idCapitulo(self.capituloid());
                self.nregistros(datos.count);
                self.mensaje('');
            } else{
                self.listado_actividades([]);
                self.mensaje(mensajeNoFound);
            }
            self.llenar_paginacion(datos, pagina);
        }, path,parameter);

        
    }

}

var listadoactividades = new ListadoActividadesViewModel();
ko.applyBindings(listadoactividades);
listadoactividades.getDataTable(1);
