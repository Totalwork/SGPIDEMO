
function SolicitudViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false); 

    self.habilitar=ko.observable(false);

    self.listado_diseno=ko.observableArray([]);
    self.mensaje_diseno=ko.observable('');

    self.listado_soporte=ko.observableArray([]);
    self.mensaje_soporte=ko.observable('');

    self.listado_soporte_edicion=ko.observableArray([]);

    self.solicitudVO={
	 	id:ko.observable(0),
	 	nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del solicitante' } }),
        entidad:ko.observable('').extend({ required: { message: '(*)Digite el nombre de la entidad' } }),
        fecha:ko.observable('').extend({ required: { message: '(*)Digite la fecha' } }),
        fecha_visita:ko.observable(''),
        fecha_respuesta:ko.observable(''),
        descripcion_visita:ko.observable(''),
        soporte:ko.observableArray([]),
        visita:ko.observable('').extend({ required: { message: '(*)Seleccione la visita' } })
	 };


	 self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
        directiones: ko.observable(true),
        limite: ko.observable(true),
        cantidad_por_paginas: ko.observable(0),
        totalRegistrosBuscados:ko.observable(0),
        text: {
            first: ko.observable('Inicio'),
            last: ko.observable('Fin'),
            back: ko.observable('<'),
            forward: ko.observable('>')
        }
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Solicitud');
        $('#modal_acciones').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }
   
    // //limpiar el modelo 
     self.limpiar=function(){    	 
         
            self.solicitudVO.id(0);
            self.solicitudVO.nombre('');
            self.solicitudVO.visita('');
            $('#archivo').fileinput('reset');
            $('#archivo').val('');
            self.solicitudVO.entidad('');
            self.solicitudVO.fecha('');
            self.solicitudVO.fecha_visita('');
            self.solicitudVO.fecha_respuesta('');
            self.solicitudVO.descripcion_visita('');
            self.solicitudVO.soporte([]);
            self.listado_soporte_edicion([]);
            
     }
    // //funcion guardar
     self.guardar=function(){

    	if (SolicitudViewModel.errores_solicitud().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

            var data= new FormData();
            data.append('fecha',self.solicitudVO.fecha());
            data.append('nombre',self.solicitudVO.nombre());
            data.append('entidad',self.solicitudVO.entidad());
            data.append('visita',self.solicitudVO.visita());
            data.append('fecha_visita',self.solicitudVO.fecha_visita());
            data.append('fecha_respuesta',self.solicitudVO.fecha_respuesta());
            data.append('descripcion_visita',self.solicitudVO.descripcion_visita());

                
            var files2= $('#archivo')[0].files;

            for (var i = 0; i < files2.length; i++){               

                if(files2[i]!==undefined){

                    data.append('soporte[]', files2[i]); 
                }
            }   
           
            if(self.solicitudVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/GestionProyectoSolicitud/',//url api
                     parametros:data                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData2(parametros);
            }else{

                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#archivo').fileinput('reset');
                            $('#archivo').val('');
                            self.listado_soporte_edicion([]);
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/GestionProyectoSolicitud/'+self.solicitudVO.id()+'/',
                       parametros:data                        
                  };

                  RequestFormData2(parametros);

            }

        } else {
             SolicitudViewModel.errores_solicitud.showAllMessages();//mostramos las validacion
        }
     }
    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/GestionProyectoSolicitud?format=json&page='+pagina;
            parameter = { dato: self.filtro(), pagina: pagina };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));  

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
        }


    }

    self.abrir_modal_diseno = function (obj) {
        self.titulo('Listado de Diseños');
        path = path_principal+'/api/GestionProyectoDiseno?sin_paginacion';
        parameter = { solicitud_id: obj.id };
        RequestGet(function (datos, estado, mensage) {
                self.mensaje_diseno('');                    
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    //self.listado(results); 
                    self.listado_diseno(agregarOpcionesObservable(datos));  

                } else {
                    self.listado_diseno([]);
                    self.mensaje_diseno(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                $('#modal_diseno').modal('show');
        }, path, parameter);
    }


    self.abrir_modal_soporte = function (obj) {
        self.titulo('Listado de Soporte');
        path = path_principal+'/api/GestionProyectoSoporteSolicitud?sin_paginacion';
        parameter = { solicitud_id: obj.id };
        RequestGet(function (datos, estado, mensage) {
                self.mensaje_soporte('');                    
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    //self.listado(results); 
                    self.listado_soporte(agregarOpcionesObservable(datos));  

                } else {
                    self.listado_soporte([]);
                    self.mensaje_soporte(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                $('#modal_soporte').modal('show');
        }, path, parameter);
    }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.verSoporte=function(obj){
        window.open(path_principal+"/gestion_proyecto/ver-soporte-solicitud/?id="+ obj.id, "_blank");
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


     self.solicitudVO.visita.subscribe(function (value) {
            if(value==1){
                self.habilitar(true);
            }else{
                self.habilitar(false);
                self.solicitudVO.fecha_visita('');
                self.solicitudVO.descripcion_visita('');
            }
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/GestionProyectoSolicitud/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Solicitud');
             self.solicitudVO.id(results.id);
             self.solicitudVO.nombre(results.nombre);
             if(results.visita==true){
                self.solicitudVO.visita('1');
             }else if(results.visita==false){
                self.solicitudVO.visita('0');
             }
             self.solicitudVO.entidad(results.entidad);
             self.solicitudVO.fecha(results.fecha);
             self.solicitudVO.fecha_visita(results.fecha_visita);
             self.solicitudVO.fecha_respuesta(results.fecha_respuesta);
             self.solicitudVO.descripcion_visita(results.descripcion_visita);  
             self.listado_soporte_edicion(agregarOpcionesObservable(results.soportes));         
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }

    self.consultar_soporte=function(){
        path =path_principal+'/api/GestionProyectoSoporteSolicitud/?sin_paginacion';
        parameter={solicitud_id:self.solicitudVO.id()};
         RequestGet(function (results,count) {
             self.listado_soporte_edicion([]);
             self.listado_soporte_edicion(agregarOpcionesObservable(results)); 
         }, path, parameter);

    }

    self.eliminar_soporte=function(obj){
             var path =path_principal+'/api/GestionProyectoSoporteSolicitud/'+obj.id+"/";
             var parameter = '';
             RequestAnularOEliminar("Esta seguro que desea eliminar el soporte "+obj.nombre+"?", path, parameter, function () {
                 self.consultar_soporte();
             })

    }

    self.solicitud_diseno=function(obj){
            location.href=path_principal+"/gestion_proyecto/solicitud_diseno/"+obj.id+"/";
    }
       
    self.eliminar = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id.push({
                        id:d.id
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una solicitud para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/gestion_proyecto/eliminar_solicitudes/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las solicitudes seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

 }

var solicitud = new SolicitudViewModel();
SolicitudViewModel.errores_solicitud = ko.validation.group(solicitud.solicitudVO);
solicitud.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(solicitud,content);
ko.applyBindings(solicitud,header);