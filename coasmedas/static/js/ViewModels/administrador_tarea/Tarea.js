function TareaViewModel() {
	
	var self = this;
    self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.listado_soporte=ko.observableArray([]);
    self.mensaje_soporte=ko.observable('');

    self.listado_soporte_vista=ko.observableArray([]);

    self.comentario=ko.observable('');

    self.listado_comentario=ko.observableArray([]);
    self.porcentaje=ko.observable(3);
    self.texto_comentario=ko.observable('');

    self.comentarioVO={
        tarea_id:ko.observable(0),
        comentario:ko.observable(''),
        usuario_id:ko.observable(0),
        fecha:ko.observable('')   
    }

    self.abrir_modal = function (obj) {
        self.limpiar();
        self.titulo('Comentario');
        self.comentario(obj.comentario);
        $('#modal_comentario').modal('show');
    }

    self.abrir_modal_soporte = function (obj) {
        self.titulo('Archivos asociados a la tarea');
        self.consultar_soporte(obj.id);        
        $('#modal_soportes').modal('show');
    }



     self.limpiar=function(){ 


     }

      self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_soporte(), function(d) {

                    d.eliminado(value);
             }); 
    });


           //agregar un comentario
  self.addcomentarios = function(d,e) {

    
            if(e.keyCode === 13 || e.keyCode==undefined) {
                
                if(self.texto_comentario()!==''){

                    self.comentarioVO.tarea_id($('#id_tarea').val());
                    self.comentarioVO.comentario(self.texto_comentario());
                    self.comentarioVO.usuario_id($('#id_usuario').val());

                    var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.texto_comentario('');
                            self.listado_comentario.push(datos);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/TareaComentario/',//url api
                     parametros:self.comentarioVO                        
                    };
                    //parameter =ko.toJSON(self.contratistaVO);
                    Request(parametros);

                }else{
                 $("#meg_error").html('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning fa-2x"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>Asegurese de haber agregando algun comentario.</div>');
                
                 }
                return true;

            }
            return true;
        
    };

    self.ver_mar_comentarios=function(value){
        self.porcentaje(self.porcentaje()+3);
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

              
                cerrarLoading();
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
        }, path, parameter,undefined, false);
     }


  


    self.guardar=function(){

        //  if (TareaViewModel.errores_soporte().length == 0) {//se activa las validaciones

        //    // self.contratistaVO.logo($('#archivo')[0].files[0]);
        //     self.soporteVO.nombre(self.soporteVO.ruta().name);

        //         var parametros={                     
        //              callback:function(datos, estado, mensaje){

        //                 if (estado=='ok') {
        //                     self.soporteVO.ruta('');
        //                     $('#archivo').fileinput('reset');
        //                     $('#archivo').val('');
        //                     self.consultar_soporte(self.soporteVO.asignacion_tarea_id());
        //                 }                        
                        
        //                 $('#loading').hide();
        //              },//funcion para recibir la respuesta 
        //              url:path_principal+'/api/SoporteAsignacionTarea/',//url api
        //              parametros:self.soporteVO                        
        //         };
        //         //parameter =ko.toJSON(self.contratistaVO);
        //         RequestFormData(parametros);
    
        // } else {
        //      TareaViewModel.errores_soporte.showAllMessages();//mostramos las validacion
        // }

    }

      self.consultar_listado_soporte=function(id_tarea){

        path = path_principal+'/api/Tarea/'+id_tarea;
        parameter = {tarea_id:id_tarea};
        RequestGet(function (datos, estado, mensage) {

                self.listado_soporte_vista(datos.soporte);
                self.listado_comentario(datos.comentarios);
                $( '#carousel1' ).elastislide();

                cerrarLoading();

                
        }, path, parameter,undefined, false);

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
                
                self.consultar_listado_soporte($('#id_tarea').val());
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter,undefined, false,false);
        }


    }

    self.archivo_zip=function(){
        var cont=0;
        listado_id="";
        ko.utils.arrayForEach(self.listado_soporte(), function(d) {

                if(d.eliminado()==true){
                    if(listado_id==""){
                        listado_id=d.id;
                    }else{
                        listado_id=listado_id+","+d.id;
                    }
                    cont++;
                }
        }); 

        if(cont==0){
            self.mensaje_soporte('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>Seleccione un archivo para descargar.</div>');
            return true;
        }

        window.open(path_principal+"/administrador_tarea/download_zip?archivo="+ listado_id,'_blank');
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

var tarea = new TareaViewModel();
tarea.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(tarea,content);
ko.applyBindings(tarea,header);