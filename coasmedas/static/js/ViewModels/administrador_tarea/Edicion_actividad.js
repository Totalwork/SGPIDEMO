function EdicionViewModel() {
	
	var self = this;
    self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.listado_soporte=ko.observableArray([]);
    self.mensaje_soporte=ko.observable('');

    self.comentario=ko.observable('');
    
    self.listado_usuarios=ko.observableArray([]);
    self.filtro_usuario=ko.observable('');
    self.id_empresa=ko.observable(0);
    self.checkall2=ko.observable(false);
    self.mensaje_usuario=ko.observable('');
    self.mensaje_guardando_usuario=ko.observable('');

    self.edicionVO={
        id:ko.observable(0),
        tipo_id:ko.observable(0).extend({ required: { message: '(*)Seleccione un tipo' } }),
        asunto:ko.observable('').extend({ required: { message: '(*)Digite un asunto' } }),
        solicitante_id:ko.observable(0),
        fecha:ko.observable('').extend({ required: { message: '(*)Digite una fecha' } }),
        fecha_transaccion:ko.observable(''),
        lugar:ko.observable('').extend({ required: { message: '(*)Digite una lugar' } }),
        fecha_transaccion:ko.observable(''),
        invitados_id:ko.observable('')      
    }

    self.listado_invitados=ko.observableArray([]);
    self.listado_archivo=ko.observableArray([]);

    self.soporteVO={
        ruta:ko.observable('').extend({ required: { message: '(*)Seleccione un archivo' } }),
        tarea_actividad_id:ko.observable($('#id_actividad').val()),
        nombre:ko.observable('')
    }

    self.paginacion_usuario = {
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


     self.llenar_paginacion_usuario = function (data,pagina) {

        self.paginacion_usuario.pagina_actual(pagina);
        self.paginacion_usuario.total(data.count);       
        self.paginacion_usuario.cantidad_por_paginas(resultadosPorPagina);

    }

      self.paginacion_usuario.pagina_actual.subscribe(function (pagina) {
            self.consultar_usuario(pagina);
        });

    self.consulta_enter_usuario = function (d,e) {
        if (e.which == 13) {
            self.consultar_usuario(1);
        }
        return true;
    }


    self.guardar_soporte=function(){

           if (EdicionViewModel.errores_soporte().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            self.soporteVO.nombre(self.soporteVO.ruta().name);

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.soporteVO.ruta('');
                            $('#archivo').fileinput('reset');
                            $('#archivo').val('');
                            self.listado_archivo.push(datos);
                            //console.log(self.listado_archivo())
                        }                        
                        
                        $('#loading').hide();
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/TareaActividadSoporte/',//url api
                     parametros:self.soporteVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
    
        } else {
             EdicionViewModel.errores_soporte.showAllMessages();//mostramos las validacion
        }
    }


    self.guardar_usuario=function(){
      ko.utils.arrayForEach(self.listado_usuarios(), function(d) {

                if(d.eliminado()==true){
                    self.listado_invitados.push(d);
                }
      }); 
      self.mensaje_guardando_usuario();
      self.mensaje_guardando_usuario('<div class="alert alert-success alert-dismissable"><i class="fa fa-check"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>El registro ha sido guardado exitosamente.</div>');
      self.mensaje('');
      self.checkall2(false);

    }

  

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
            path = path_principal+'/api/usuario/?format=json';
            parameter = {'empresa_id':empresa,dato:self.filtro_usuario()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje_usuario('');
                    //self.listado(results); 
                    self.listado_usuarios(agregarOpcionesObservable(datos.data));

                } else {
                    self.mensaje_usuario('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron registros</div>');
                    self.listado_usuarios([]);
                }

                self.llenar_paginacion_usuario(datos,pagina);
                //$('#loading').hide();
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter,undefined, false,false);
        }

    }

    self.eliminar_usuario=function(val){
      self.listado_invitados.remove(val);

     }

    self.guardar=function(){

         if (EdicionViewModel.errores_edicion().length == 0) {//se activa las validaciones

                self.edicionVO.invitados_id('');

                ko.utils.arrayForEach(self.listado_invitados(), function(d) {

                    if(self.edicionVO.invitados_id()==''){
                       self.edicionVO.invitados_id(d.id);
                    }else{
                       self.edicionVO.invitados_id(self.edicionVO.invitados_id()+','+d.id);
                    }
                }); 

                var parametros={  
                     metodo:'PUT',                         
                     callback:function(datos, estado, mensaje){
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/TareaActividad/'+self.edicionVO.id()+'/',//url api
                     parametros:self.edicionVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
    
        } else {
             EdicionViewModel.errores_edicion.showAllMessages();//mostramos las validacion
        }

    }

    self.checkall2.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_usuarios(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.id_empresa.subscribe(function (valor) {
           
          self.filtro_usuario($('#txtBuscar2').val());
          self.consultar_usuario(1); 
          
    });

     self.eliminar_soporte = function (obj) {

        
        var path =path_principal+'/api/TareaActividadSoporte/'+obj.id+'/';
        RequestAnularOEliminar("Esta seguro que desea eliminar el soporte?", path, parameter, function () {
            self.listado_archivo.remove(obj);
        })    
        
    }

    self.ver_soporte = function(id){
        window.open(path_principal+"/administrador_tarea/ver-soporte-actividad/?id="+ id, "_blank");
    }
    
    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) { 

            path = path_principal+'/api/TareaActividad/'+$('#id_actividad').val();
            parameter = '';
            RequestGet(function (datos, estado, mensage) {
                
                self.edicionVO.asunto(datos.asunto);
                self.edicionVO.fecha(datos.fecha_format);
                self.edicionVO.lugar(datos.lugar); 
                self.edicionVO.tipo_id(datos.tipo.id); 
                self.edicionVO.solicitante_id(datos.solicitante.id); 
                self.edicionVO.id(datos.id); 
                self.listado_archivo(datos.soporte);
                self.listado_invitados(datos.usuario_inivitado);
                self.edicionVO.fecha_transaccion(datos.fecha_transaccion);

                
                cerrarLoading();
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter,undefined, false);
        }


    }

    self.abrir_modal_usuario = function () {
        //self.limpiar();
        $('#modal_usuario').modal('show');
    }



 }

var edicion = new EdicionViewModel();
edicion.consultar(1);//iniciamos la primera funcion
edicion.consultar_usuario(1);
EdicionViewModel.errores_edicion = ko.validation.group(edicion.edicionVO);
EdicionViewModel.errores_soporte = ko.validation.group(edicion.soporteVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(edicion,content);
ko.applyBindings(edicion,header);