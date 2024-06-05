function DetalleViewModel() {
	
	var self = this;
    self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.listado_soporte=ko.observableArray([]);
    self.mensaje_soporte=ko.observable('');

    self.comentario=ko.observable('');

    self.soporteVO={
        ruta:ko.observable('').extend({ required: { message: '(*)Seleccione un archivo' } }),
        asignacion_tarea_id:ko.observable(''),
        nombre:ko.observable('')
    }



    self.abrir_modal = function (obj) {
        self.limpiar();
        self.titulo('Comentario');
        self.comentario(obj.comentario);
        $('#modal_comentario').modal('show');
    }

    self.abrir_modal_soporte = function (obj) {
        self.titulo('Archivos asociados a la tarea');
        self.soporteVO.asignacion_tarea_id(obj.id);
        self.consultar_soporte(obj.id);        
        $('#modal_soportes').modal('show');
    }

    self.abrir_nuevo_punto = function () {
        location.href=path_principal+"/administrador_tarea/nuevo_punto/"+$('#id_tarea').val();
    }


     self.limpiar=function(){ 


     }


     self.consultar_soporte=function(id){

        
        self.mensaje_soporte('');
        path = path_principal+'/api/SoporteAsignacionTarea/?format=json&sin_paginacion';
        parameter = {asignacion_tarea_id:id};
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado_soporte(agregarOpcionesObservable(datos));

                } else {
                    self.listado_soporte([]);
                    self.mensaje_soporte('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron registros</div>');
                    
                    //self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                $('#loading').hide();

                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
        }, path, parameter);
     }


    self.guardar=function(){

         if (DetalleViewModel.errores_soporte().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            self.soporteVO.nombre(self.soporteVO.ruta().name);

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.soporteVO.ruta('');
                            $('#archivo').fileinput('reset');
                            $('#archivo').val('');
                            self.consultar_soporte(self.soporteVO.asignacion_tarea_id());
                        }                        
                        
                        $('#loading').hide();
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/SoporteAsignacionTarea/',//url api
                     parametros:self.soporteVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
    
        } else {
             DetalleViewModel.errores_soporte.showAllMessages();//mostramos las validacion
        }

    }

     self.eliminar_soporte = function (obj) {

        
        var path =path_principal+'/api/SoporteAsignacionTarea/'+obj.id+'/';
        RequestAnularOEliminar("Esta seguro que desea eliminar el soporte?", path, parameter, function () {
            self.consultar_soporte(self.soporteVO.asignacion_tarea_id());
        })    
        
    }


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) { 

            path = path_principal+'/api/AsignacionTarea?format=json&sin_paginacion';
            parameter = {tarea_id:$('#id_tarea').val()};
            RequestGet(function (datos, estado, mensage) {
                
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos));
                    $('#modal_acciones').modal('hide');

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                
                $('#loading').hide();
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
        }


    }


    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.limpiar();
            self.consultar(1);
        }
        return true;
    }


 }

var detalle = new DetalleViewModel();
detalle.consultar(1);//iniciamos la primera funcion
DetalleViewModel.errores_soporte = ko.validation.group(detalle.soporteVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(detalle,content);
ko.applyBindings(detalle,header);