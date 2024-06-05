function CapitulosEsquemaViewModel(){
    var self = this;
    self.listado_capitulos = ko.observableArray([]);
    self.filtro=ko.observable('');
    self.cronograma_id = ko.observable($('#id_cronograma').val());
    self.nombreCronograma = ko.observable('');
    self.idCronograma = ko.observable('');
    self.nregistros = ko.observable('');
    self.titulo = ko.observable('');
    self.mensaje = ko.observable('');
    self.url=path_principal+'/api/';
    self.mensaje = ko.observable('');
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
        path = path_principal + '/api/CCapitulo/?filterbyname=1&nombre='+self.filtro()+'&cronograma_id=' + self.cronograma_id()+'&page='+pagina+'';
        if(self.filtro() == ''){
            path = path_principal + '/api/CCapitulo?filterbyid=1&cronograma_id=' + self.cronograma_id()+'&page='+pagina;
        }
        parameter = {};
        RequestGet(function (datos, estado, mensage) {

            if(estado == 'ok' && datos!=null){
                // alert(datos.data)
                self.listado_capitulos(datos.data);
                self.nregistros(datos.count);
                self.mensaje('');
                cerrarLoading();  
            }
             else {
                // alert('else')
                self.listado_capitulos(['']);
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


     self.editar = function(obj){
        self.limpiar();
        // alert('editando ' + obj.nombre);
        self.titulo('Editar capitulo');
        self.capituloVO.nombre(obj.nombre);
        self.capituloVO.id(obj.id);
        self.capituloVO.cronograma_id(obj.cronograma.id);
        self.capituloVO.orden(obj.orden);
        $("#activacrear").hide();
        $('#modal_capitulo').modal('show');
    }

    self.crear = function(){
        if (self.capituloVO.id() == 0){
            self.titulo('Crear capitulo');
            self.capituloVO.cronograma_id(self.cronograma_id());
            $("#activacrear").show();
            $('#modal_capitulo').modal('show');    
        }
        self.limpiar(); 
    }

    self.guardar_tabla = function () {
        var lista_id = [];
        var count = 0;
        ko.utils.arrayForEach(self.listado_capitulos(), function (d) {
            lista_id.push({
                id: d.id,
                orden: d.orden
            })
        });

        var path = path_principal + '/cronogramacontrato/actualizarcapitulo/';
        var parameter = { lista: lista_id };
        RequestAnularOEliminar("Esta seguro que desea actualizar los capitulos seleccionados?", path, parameter, function () {
            self.getDataTable(1);
        });


    }


    self.guardar = function(){
        // alert('guardar');
        // if (CapitulosEsquemaViewModel.errores_capitulo().length == 0) {//se activa las validaciones
            if(self.capituloVO.id()==0){
                self.capituloVO.cronograma_id(self.cronograma_id());
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.getDataTable(1);
                            $('#modal_capitulo').modal('hide');
                            self.limpiar();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url+'CCapitulo/',//url api
                     parametros:self.capituloVO                        
                };
                
                RequestFormData(parametros);
            }else{        
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                                self.getDataTable(1);
                                $('#modal_capitulo').modal('hide');
                                self.limpiar();
                            } 
                       },//funcion para recibir la respuesta 
                       url: self.url+'CCapitulo/'+ self.capituloVO.id()+'/',
                       parametros:self.capituloVO                        
                  };
                  RequestFormData(parametros);
            }
        // } else {
        //     CapitulosEsquemaViewModel.errores_capitulo.showAllMessages();//mostramos las validacion
        //     alert('else ' + CapitulosEsquemaViewModel.errores_capitulo.showAllMessages());
            
        // }
    }

    self.limpiar = function(){
        self.capituloVO.id(0);
        self.capituloVO.nombre('');
        self.capituloVO.nombre.isModified(false);
        
        self.capituloVO.cronograma_id('');
        self.capituloVO.cronograma_id.isModified(false);
        self.capituloVO.orden('');

    }


    self.eliminar_capitulo=function(id){
        var path =path_principal+'/api/CCapitulo/'+id+'/';
        var parameter = {metodo:'DELETE'};
        
        RequestAnularOEliminar("Esta seguro que desea eliminar el registro?", path, parameter, 
            function(datos, estado, mensaje){
                if (estado=='ok') { 
                    self.getDataTable(1);
                }        
        });
    }


    self.getDataTable = function(pagina){
        path = path_principal + '/api/CCapitulo?filterbyid=1&cronograma_id=' + self.cronograma_id()+'&page='+pagina;
        parameter = {};

        RequestGet(function (datos){
            if( datos!=null && datos.count > 0){
                self.listado_capitulos(['']);
                self.listado_capitulos(datos.data);
                self.mensaje('');
                if (datos.count > 0){
                    self.nombreCronograma(datos.data[0].cronograma.nombre);
                    self.idCronograma(datos.data[0].cronograma.id);
                    
                }
                self.mensaje('');
                self.nregistros(datos.count);
                // alert(datos.data[0].cronograma.nombre)
                
            } else{
                self.listado_capitulos([]);
                self.mensaje(mensajeNoFound);
            }
            self.llenar_paginacion(datos, pagina);
        }, path,parameter);

        
    }


}

var capitulosesquema = new CapitulosEsquemaViewModel();
CapitulosEsquemaViewModel.errores_capitulo = ko.validation.group(capitulosesquema.capituloVO);
ko.applyBindings(capitulosesquema);

capitulosesquema.getDataTable(1);