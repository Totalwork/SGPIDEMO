function PuntoViewModel() {
	
	var self = this;
    self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

    self.panel=ko.observable(false);

    self.listado_usuarios=ko.observableArray([]);
    self.mensaje_soporte=ko.observable('');
    self.filtro_usuario=ko.observable('');
    self.id_empresa=ko.observable(0);
    self.mensaje_usuario=ko.observable('');

    self.listado_usuarios_notificaciones=ko.observableArray([]);
    self.id_empresa_notificacion=ko.observable(0);

    self.listado_personas=ko.observableArray([]);

    self.asignacionVO={
        estado_id:ko.observable(0).extend({ required: { message: '(*)Seleccione un estado a pasar' } }),
        comentario:ko.observable(''),
        tarea_id:ko.observable(0),
        fecha:ko.observable(''),
        colaborador_id:ko.observable(0),
        solicitante_id:ko.observable(0),
        lista_id:ko.observable('')
    }


    self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
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

     self.paginacion_usuario = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
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

    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

    self.eliminar_usuario=function(obj){
        self.listado_personas.remove(obj);
    }

    self.llenar_paginacion_usuario = function (data,pagina) {

        self.paginacion_usuario.pagina_actual(pagina);
        self.paginacion_usuario.total(data.count);       
        self.paginacion_usuario.cantidad_por_paginas(resultadosPorPagina);

    }



    self.abrir_modal = function (obj) {
        //self.limpiar();
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

     self.agregar_usuario=function(){
             count=0;
             ko.utils.arrayForEach(self.listado_usuarios_notificaciones(), function(d) {

                    if(d.eliminado()==true){
                        count=1;
                        sw=0;
                        ko.utils.arrayForEach(self.listado_personas(), function(x) {

                                if(d.id==x.id){
                                    sw=1;
                                }
                         });

                        if(sw==0){
                            self.listado_personas.push(d);
                        }
                    }
             });

     }



    self.guardar=function(){

         if (PuntoViewModel.errores_puntos().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
           self.asignacionVO.colaborador_id($('#colaborador').val());
           self.asignacionVO.solicitante_id($('#id_usuario').val());
           self.asignacionVO.tarea_id($('#id_tarea').val());

           ko.utils.arrayForEach(self.listado_personas(), function(d) {

                    if(self.asignacionVO.lista_id()==''){
                      self.asignacionVO.lista_id(d.id);
                    }else{
                       self.asignacionVO.lista_id(self.asignacionVO.lista_id()+","+d.id);
                    }
             }); 

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                           location.href=path_principal+"/administrador_tarea/detalle_tarea/"+$('#id_tarea').val();
                        }                        
                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/AsignacionTarea/',//url api
                     parametros:self.asignacionVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
    
        } else {
             PuntoViewModel.errores_puntos.showAllMessages();//mostramos las validacion
        }

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

                
                cerrarLoading();
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
        }


    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar_usuario(pagina);
    });

    self.paginacion_usuario.pagina_actual.subscribe(function (pagina) {
        self.consultar_usuario_notificar(pagina);
    });

    self.asignacionVO.estado_id.subscribe(function (value) {
        if(value==$('#reasignada').val()){
            self.panel(true);
        }else{
            self.panel(false);
        }
    });

    self.consultar_usuario=function(pagina){

        if (pagina > 0) { 
            var empresa=0;             
            self.filtro_usuario($('#txtBuscar2').val());
            if(self.id_empresa()==0){
                empresa=$("#id_empresa").val();
            }else{
                empresa=self.id_empresa();
            }
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            path = path_principal+'/api/usuario/?format=json&page='+pagina;
            parameter = {'empresa_id':empresa,pagina: pagina,dato:self.filtro_usuario()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje_usuario('');
                    //self.listado(results); 
                    self.listado_usuarios(agregarOpcionesObservable(datos.data));

                } else {
                    self.mensaje_usuario('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron registros</div>');
                    self.listado_usuarios([]);
                }

                self.llenar_paginacion(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter);
        }

    }

     self.consultar_usuario_notificar=function(pagina){

        if (pagina > 0) { 
            var empresa=0;             
            self.filtro_usuario($('#txtBuscar3').val());
            if(self.id_empresa_notificacion()==0){
                empresa=$("#id_empresa").val();
            }else{
                empresa=self.id_empresa_notificacion();
            }
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            path = path_principal+'/api/usuario/?format=json&page='+pagina;
            parameter = {'empresa_id':empresa,pagina:pagina,dato:self.filtro_usuario(),activado:1};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje_usuario('');
                    //self.listado(results); 
                    self.listado_usuarios_notificaciones(agregarOpcionesObservable(datos.data));

                } else {
                    self.mensaje_usuario('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron registros</div>');
                    self.listado_usuarios_notificaciones([]);
                }

                self.llenar_paginacion_usuario(datos,pagina);
                
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
        }

    }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_usuarios_notificaciones(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.id_empresa.subscribe(function (valor) {
            
            self.filtro_usuario($('#txtBuscar2').val());
            self.consultar_usuario(1);
    });

    self.id_empresa_notificacion.subscribe(function (valor) {
            
            self.filtro_usuario($('#txtBuscar3').val());
            self.consultar_usuario_notificar(1);
    });

    self.consulta_enter_usuario = function (d,e) {
        if (e.which == 13) {
            self.consultar_usuario(1);
        }
        return true;
    }

    self.consulta_enter_usuario_notificar = function (d,e) {
        if (e.which == 13) {
            self.consultar_usuario_notificar(1);
        }
        return true;
    }


    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            //self.limpiar();
            self.consultar(1);
        }
        return true;
    }


 }

var punto = new PuntoViewModel();
punto.consultar_usuario(1);
PuntoViewModel.errores_puntos = ko.validation.group(punto.asignacionVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(punto,content);
ko.applyBindings(punto,header);