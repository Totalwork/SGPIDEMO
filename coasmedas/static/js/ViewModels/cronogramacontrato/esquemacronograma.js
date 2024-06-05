function EsquemaCronogramaViewModel(){
    var self = this;
    
    self.mensaje = ko.observable('');
    self.listado_cronogramas = ko.observableArray([]);
    self.listado=ko.observableArray([]);
    self.nregistros = ko.observable('');
    self.mensaje = ko.observable('');
    self.titulo = ko.observable('');
    self.filtro=ko.observable('');
    self.url=path_principal+'/api/';
    self.urlasociar=path_principal+'/';
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

    self.cronogramaVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: ' Digite el nombre del cronograma.' } })
    }

    self.actividadContratoVO={
        id: ko.observable(0),
        cronograma_id:ko.observable(0),
        contrato_id: ko.observable(0),
    }

    self.listado_contratos_asociar = ko.observableArray([]);



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

        path = path_principal + '/api/CronogramaCcontrato/?filterbyname=1&nombre='+self.filtro()+'&page='+pagina+'';
        parameter = {};
        RequestGet(function (datos, estado, mensage) {

            if(estado == 'ok' && datos!=null){
                // alert(datos.data)
                self.listado_cronogramas(datos.data);
                self.nregistros(datos.count);
                
                self.mensaje('');
                cerrarLoading();  
            }

             else {
                // alert('else')
                self.listado_cronogramas(['']);
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
        self.titulo('Editar cronograma');
        self.cronogramaVO.nombre(obj.nombre);
        self.cronogramaVO.id(obj.id);
        $('#modal_cronograma').modal('show');
    }

    self.crear = function(){
        self.limpiar();
        self.titulo('Crear cronograma');
        $('#modal_cronograma').modal('show');
    }


    self.asociarcronogramas_modal = function(obj){
        self.limpiarContrato();
        self.titulo('Asociar cronograma a contrato');
        // alert(obj.id)
        self.actividadContratoVO.cronograma_id(obj.id)
        self.getListContratos();
        // self.getListCronogramas();
        $('#modal_asociar').modal('show');
    }


    self.getListContratos=function(){
        path = path_principal + '/cronogramacontrato/getslistacontratos/';
        parameter = {};

        RequestGet(function (datos, success, massage){
            if(success == 'ok' && datos!=null){
                // alert(datos)
                self.listado_contratos_asociar(datos);
                self.mensaje('');
            }else{
                self.listado_contratos_asociar([]);
                self.mensaje(mensajeNoFound);
            }
            
        }, path,parameter);

    }

    self.asociarcronogramas=function(){        
        if(self.actividadContratoVO.id()==0){
            var parametros={                     
                 callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        $('#modal_asociar').modal('hide');
                        self.getDataTable(1);
                        self.limpiarContrato();
                    }                     
                 },//funcion para recibir la respuesta 
                 url: self.urlasociar+'cronogramacontrato/asociarcronogramacontrato/',//url api
                 parametros:self.actividadContratoVO                        
            };
            //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData(parametros);
        }else{                 
              var parametros={     
                    metodo:'PUT',                
                   callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.getDataTable(1);
                            $('#modal_asociar').modal('hide');
                            self.limpiarContrato();
                        } 
                   },//funcion para recibir la respuesta 
                   url: self.urlasociar+'cronogramacontrato/asociarcronogramacontrato/'+ self.actividadContratoVO.id()+'/',
                   parametros:self.actividadContratoVO                        
              };
              RequestFormData(parametros);
        }
    
    }


    self.limpiarContrato = function(){
        self.actividadContratoVO.id(0);
        self.actividadContratoVO.cronograma_id(0);
        self.actividadContratoVO.contrato_id(0);
    }


    self.guardar = function(){
        if (EsquemaCronogramaViewModel.errores_cronograma().length == 0) {//se activa las validaciones
            if(self.cronogramaVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.getDataTable(1);
                            $('#modal_cronograma').modal('hide');
                            self.limpiar();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url+'CronogramaCcontrato/',//url api
                     parametros:self.cronogramaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                                self.getDataTable(1);
                                $('#modal_cronograma').modal('hide');
                                self.limpiar();
                            } 
                       },//funcion para recibir la respuesta 
                       url: self.url+'CronogramaCcontrato/'+ self.cronogramaVO.id()+'/',
                       parametros:self.cronogramaVO                        
                  };
                  RequestFormData(parametros);
            }
        } else {
            EsquemaCronogramaViewModel.errores_cronograma.showAllMessages();//mostramos las validacion
        }
    }

    self.limpiar = function(){
        self.cronogramaVO.id(0);
        self.cronogramaVO.nombre('');
        self.cronogramaVO.nombre.isModified(false);
    }


    self.getDataTable = function(pagina){
        path = path_principal + '/api/CronogramaCcontrato/'+'?page='+pagina+'';
        parameter = {};

        RequestGet(function (datos, success){
            if(success == 'ok' && datos!=null){
                self.listado_cronogramas(datos.data);
                self.nregistros(datos.count);
                self.mensaje('');
            } else{
                self.listado_cronogramas(['']);   
                self.mensaje(mensajeNoFound);
            }
            self.llenar_paginacion(datos, pagina);
        }, path,parameter);
    }

    self.changestate = function(id, estado){
        var contenido = "¿Esta seguro que desea desactivar el cronograma?";
        $.confirm({
            title: 'Confirmar!',
            content: "<h4>" + contenido + "</h4>",
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {
                path = path_principal + '/cronogramacontrato/cambiarestadocronograma/?id=' + id + '&estado='+ estado;
                var parametros={                     
                     callback:function(datos, success, mensaje){
                        if (success=='ok') {
                            self.getDataTable(1);
                        }                
                     },//funcion para recibir la respuesta 
                     url: path,//url api
                     parametros:parameter,
                     alert: false
                };                
                Request(parametros);
            }
        });
    }

}


var esquemacronograma = new EsquemaCronogramaViewModel();
EsquemaCronogramaViewModel.errores_cronograma = ko.validation.group(esquemacronograma.cronogramaVO);
ko.applyBindings(esquemacronograma);

esquemacronograma.getDataTable(1);