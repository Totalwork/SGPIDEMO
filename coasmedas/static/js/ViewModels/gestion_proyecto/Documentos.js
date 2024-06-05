

function DocumentoViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false); 

    self.documentosVO={
	 	id:ko.observable(0),
	 	nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del datos.' } }),
        campana_id:ko.observable($('#id_campana').val()),
        estado_id:ko.observable('').extend({ required: { message: '(*)Seleccione un estado.' } })
	 };

     self.clonacionVO={
        id_campana_clonar:ko.observable('').extend({ required: { message: '(*)Seleccione un campaña.' } }),
        campana_id:ko.observable($('#id_campana').val())
    }


    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Documento de Datos');
        $('#modal_acciones').modal('show');
    }

    self.abrir_modal_clonacion=function(){
        self.limpiar();
        self.titulo('Clonacion de documentos');
        $('#modal_clonacion').modal('show');
    }


    self.consultar_id=function(id){
       
        path =path_principal+'/api/GestionProyectoDocumentoEstado/'+id+'/?format=json';
        RequestGet(function (results,count) {
           
             self.titulo('Actualizar Documento de Datos');

             self.documentosVO.id(results.id);
             self.documentosVO.nombre(results.nombre);
             self.documentosVO.campana_id(results.campana.id);
             self.documentosVO.estado_id(results.estado.id);
             $('#modal_acciones').modal('show');
             
         }, path, parameter);

     }


   
    // //limpiar el modelo 
     self.limpiar=function(){    	 
         
             self.documentosVO.id(0);
             self.documentosVO.nombre('');
             self.clonacionVO.id_campana_clonar(0);
     }


     self.eliminar_documento=function(id,nombre){
            var path =path_principal+'/api/GestionProyectoDocumentoEstado/'+id+'/';
            var parameter = '';
            RequestAnularOEliminar("Esta seguro que desea eliminar el documento "+nombre+"?", path, parameter, function () {
                 location.reload();
            })
     }


     self.clonar=function(){

        if (DocumentoViewModel.errores_clonar().length == 0) {//se activa las validaciones

            path = path_principal+'/api/GestionProyectoDocumentoEstado?sin_paginacion';
            parameter = { id_campana: self.documentosVO.campana_id()};
            RequestGet(function (datos, estado, mensage) {

                    if(datos.length>0){

                         $.confirm({
                            title: 'Confirmar de Clonacion!',
                            content: "<h4>La campaña actual tiene creados documentos, al realizar una clonacion, estos documentos seran reemplazados.¿Esta seguro que desea proceder la clonacion?</h4>",
                            confirmButton: 'Si',
                            confirmButtonClass: 'btn-info',
                            cancelButtonClass: 'btn-danger',
                            cancelButton: 'No',
                            confirm: function() {

                                var parametros={                     
                                 callback:function(datos, estado, mensaje){

                                    if (estado=='ok') {
                                        location.reload();
                                    }                        
                                    
                                 },//funcion para recibir la respuesta 
                                 url:path_principal+'/gestion_proyecto/clonar_campana/',//url api
                                 parametros:self.clonacionVO                       
                                    };
                                    //parameter =ko.toJSON(self.contratistaVO);
                                    Request(parametros); 
                            }
                        });

                    }else{
                         var parametros={                     
                                 callback:function(datos, estado, mensaje){

                                    if (estado=='ok') {
                                        location.reload();
                                    }                        
                                    
                                 },//funcion para recibir la respuesta 
                                 url:path_principal+'/gestion_proyecto/clonar_campana/',//url api
                                 parametros:self.clonacionVO                       
                                    };
                                    //parameter =ko.toJSON(self.contratistaVO);
                                    Request(parametros); 
                    }

            }, path, parameter);

        } else {
             DocumentoViewModel.errores_clonar.showAllMessages();//mostramos las validacion
        }


     }
    // //funcion guardar
     self.guardar=function(){

    	if (DocumentoViewModel.errores_documentos().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

            if(self.documentosVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            location.reload();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/GestionProyectoDocumentoEstado/',//url api
                     parametros:self.documentosVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
            }else{

                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            location.reload();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/GestionProyectoDocumentoEstado/'+self.documentosVO.id()+'/',
                       parametros:self.documentosVO                        
                  };

                  Request(parametros);

            }

        } else {
             DocumentoViewModel.errores_documentos.showAllMessages();//mostramos las validacion
        }
     }

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function () {
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            path = path_principal+'/api/GestionProyectoDocumentoEstado?filtro_estado';
            parameter = { id_campana: self.documentosVO.campana_id()};
            RequestGet(function (datos, estado, mensage) {

                self.listado(agregarOpcionesObservable(datos)); 
                $("#demo-accordion").zozoAccordion({
                    theme: "blue"
                 });
                
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
        }


 }

var documentos = new DocumentoViewModel();
DocumentoViewModel.errores_documentos = ko.validation.group(documentos.documentosVO);
DocumentoViewModel.errores_clonar= ko.validation.group(documentos.clonacionVO);
documentos.consultar();//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(documentos,content);
ko.applyBindings(documentos,header);


function mensaje_eliminacion(id,nombre){
        documentos.eliminar_documento(id,nombre);
}

function consultar_por_id(id){
        documentos.consultar_id(id);
}