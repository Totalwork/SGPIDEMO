
function TableroViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false); 

    self.listado_empresa=ko.observableArray([]);
    self.descripcion_estado=ko.observable('');
    self.id_estado=ko.observable('');

    self.listado_estado=ko.observableArray([]);
    self.listado_datos=ko.observableArray([]);

    self.listado_fecha=ko.observableArray([]);
    self.listado_gps=ko.observableArray([]);

    self.listado_documentos=ko.observableArray([]);
    self.mensaje_documentos=ko.observable('');

    self.listado_comentarios=ko.observableArray([]);

    self.soporte_localizacion=ko.observable('');

    self.listado_estado_documentos=ko.observableArray([]);

    self.habilitar_btn_reporte=ko.observable(false);
    self.habilitar_btn_exitosa=ko.observable(false);
    self.comentario_novedad=ko.observable('');
    self.listado_comentarios_diseno=ko.observableArray([]);

  
   self.soporteVO={
      id:ko.observable(0),
      nombre:ko.observable(''),
      usuario_id:ko.observable($('#id_usuario').val()),
      estado_diseno_id:ko.observable(0),
      documento_estado_id:ko.observable('').extend({ required: { message: '(*)Seleccione un documento.' } }),
      ruta:ko.observable('').extend({ required: { message: '(*)Seleccione un archivo.' } })
   }


    self.mapaVO={
      id:ko.observable(0),
      nombre:ko.observable('').extend({ required: { message: '(*)Digite un nombre.' } }),
      longitud:ko.observable('').extend({ required: { message: '(*)Digite una longitud.' } }),
      latitud:ko.observable('').extend({ required: { message: '(*)Digite una latitud.' } }),
      diseno_id:ko.observable($('#id_diseno').val()),
      version_diseno_id:ko.observable($('#version_diseno_id').val())
   }

   self.soporteinfoVO={
      nombre_documento:ko.observable(''),
      nombre_soporte:ko.observable(''),
      fecha:ko.observable(''),
      nombre_usuario:ko.observable('')
   }

   self.comentarioVO={
      id:ko.observable(0),
      usuario_id:ko.observable($('#id_usuario').val()),
      comentario:ko.observable('').extend({ required: { message: '(*)Digite un comentario.' } }),
      fecha:ko.observable(''),
      soporte_estado_id:ko.observable(0)
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

    self.abrir_modal_documentos = function () {
        //self.limpiar();
        self.titulo('Registrar Soporte');
        $('#modal_documentos').modal('show');
    }


    self.abrir_modal_comentario_diseno = function () {
        //self.limpiar();
        self.titulo('Registrar Insconsistencia');
        self.consultar_comentario_diseno();
        $('#modal_comentarios_diseno').modal('show');
    }


    self.abrir_modal_documentos_editar = function (obj) {

       
        //self.limpiar();
        path =path_principal+'/api/GestionProyectoSoporteEstado/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
            self.titulo('Actualizar Soporte');

             self.soporteVO.id(results.id);
             self.soporteVO.nombre(results.nombre);
             self.soporteVO.ruta(results.ruta);
             self.soporteVO.usuario_id(results.usuario.id);
             self.soporteVO.estado_diseno_id(results.estado_diseno.id);
             self.soporteVO.documento_estado_id(results.documento_estado.id);
            $('#modal_documentos_editar').modal('show');
         }, path, parameter);
       
    }


    self.abrir_modal_mapa = function () {
        self.limpiar_mapa();
        self.titulo('Registrar Punto');
        $('#modal_agregar_mapa').modal('show');
    }


    self.abrir_modal_comentario = function (obj) {
        self.comentarioVO.soporte_estado_id(obj.id);
        self.consultar_comentario(obj.id);
        self.titulo('Comentarios');
        $('#modal_comentarios').modal('show');
    }


    self.abrir_modal_mapa_archivo = function () {
        self.titulo('Registrar Punto por Archivo');
        $('#modal_documentos_localizacion').modal('show');
    }

    self.abrir_modal_documentos_info = function (obj) {
        //self.limpiar();
        self.soporteinfoVO.nombre_usuario(obj.usuario.persona.nombres+" "+obj.usuario.persona.apellidos);
        self.soporteinfoVO.nombre_documento(obj.documento_estado.nombre);
        self.soporteinfoVO.nombre_soporte(obj.nombre);
        self.soporteinfoVO.fecha(obj.fecha);
        self.titulo('Informacion Soporte');
        $('#modal_documentos_info').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

    self.consultar_soporte_documento=function(obj){
        self.descripcion_estado(obj.nombre);
        self.id_estado(obj.id);
        self.consultar_documentos(obj.id,false);
        self.documentos_estado(obj.id_estado);
        self.soporteVO.estado_diseno_id(obj.id);
    }

    self.documentos_estado=function(id_estado){

        path = path_principal+'/api/GestionProyectoDocumentoEstado?sin_paginacion';
        parameter = { id_estado:id_estado,id_campana:$('#id_campana').val()};
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_estado_documentos(agregarOpcionesObservable(datos));  

                } else {
                    self.listado_estado_documentos([]);
                }
        }, path, parameter,undefined, false);

    }

   
    // //limpiar el modelo 
     self.limpiar=function(){    	 
         
             self.soporteVO.id(0);
             self.soporteVO.nombre('');
             self.soporteVO.documento_estado_id('');
             self.soporteVO.usuario_id($('#id_usuario').val());
             self.soporteVO.ruta('');
     }


      self.limpiar_mapa=function(){       
         
             self.mapaVO.id(0);
             self.mapaVO.nombre('');
             self.mapaVO.longitud('');
             self.mapaVO.latitud('');
     }
    // //funcion guardar
     self.guardar_soporte=function(){

    	if (TableroViewModel.errores_soporte().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

            self.soporteVO.nombre(self.soporteVO.ruta().name);
            if(self.soporteVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar_documentos(self.soporteVO.estado_diseno_id,false);
                            $('#modal_documentos').modal('hide');
                            self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/GestionProyectoSoporteEstado/',//url api
                     parametros:self.soporteVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{

                self.soporteVO.ruta('');
                var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.consultar_documentos(self.soporteVO.estado_diseno_id,false);
                          $('#modal_documentos_editar').modal('hide');
                          self.limpiar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/GestionProyectoSoporteEstado/'+self.soporteVO.id()+'/',
                       parametros:self.soporteVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             TableroViewModel.errores_soporte.showAllMessages();//mostramos las validacion
        }
     }



    self.guardar_localizacion=function(){

      if (TableroViewModel.errores_mapa().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

            if(self.mapaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar_puntos(1);
                            $('#modal_agregar_mapa').modal('hide');
                            self.limpiar_mapa();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/GestionProyectoMapaDiseno/',//url api
                     parametros:self.mapaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
            }else{

                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.consultar_puntos(1);
                          $('#modal_agregar_mapa').modal('hide');
                          self.limpiar_mapa();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/GestionProyectoMapaDiseno/'+self.mapaVO.id()+'/',
                       parametros:self.mapaVO                        
                  };

                  Request(parametros);

            }

        } else {
             TableroViewModel.errores_mapa.showAllMessages();//mostramos las validacion
        }
     }

    self.consultar_comentario=function(id_soporte){

        path = path_principal+'/api/GestionProyectoSoporteEstadoComentario?sin_paginacion';
        parameter = { soporte_estado_id:id_soporte};
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_comentarios(agregarOpcionesObservable(datos));  

                } else {
                    self.listado_comentarios([]);
                }
                cerrarLoading();
        }, path, parameter,undefined, false);
    }

    self.guardar_comentario=function(){

      if (TableroViewModel.errores_comentario().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar_comentario(self.comentarioVO.soporte_estado_id);
                            self.consultar_documentos(self.soporteVO.estado_diseno_id(),false)
                            self.comentarioVO.comentario('');
                           
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/GestionProyectoSoporteEstadoComentario/',//url api
                     parametros:self.comentarioVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
         

        } else {
             TableroViewModel.errores_comentario.showAllMessages();//mostramos las validacion
        }
     }
    //funcion consultar de tipo get recibe un parametro
    self.consultar = function () {  
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            
            path = path_principal+'/gestion_proyecto/consultar_tablero/';
            parameter = { version_diseno_id:$('#version_diseno_id').val(),diseno_id: $('#id_diseno').val()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado_empresa(agregarOpcionesObservable(datos.empresas));
                    self.listado_estado(agregarOpcionesObservable(datos.estados));  
                    self.descripcion_estado(datos.estados[0].nombre);
                    self.id_estado(datos.estados[0].id);
                    self.listado_fecha(LLenarEstadoFecha(datos.estados));
                    self.listado_datos(datos.datos);
                    
                    if($('#reportar_diseno').val()=='False'){
                        self.habilitar_btn_reporte(false);
                    }else{
                        self.habilitar_btn_reporte(true);
                    }

                    if($('#reportar_satisfaccion').val()=='False'){
                        self.habilitar_btn_exitosa(false);
                    }else{
                        self.habilitar_btn_exitosa(true);
                    }
                    
                    self.documentos_estado(datos.estados[0].id_estado);
                    self.soporteVO.estado_diseno_id(datos.estados[0].id);
                    self.consultar_documentos(self.soporteVO.estado_diseno_id(),true);

                } else {
                    self.listado_empresa([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}

                
            }, path, parameter,undefined, false);

    }

    self.consultar_por_id_mapa = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/GestionProyectoMapaDiseno/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Punto');

             self.mapaVO.id(results.id);
             self.mapaVO.nombre(results.nombre);
             self.mapaVO.longitud(results.longitud);
             self.mapaVO.latitud(results.latitud);
             $('#modal_agregar_mapa').modal('show');
         }, path, parameter);

     }



    self.consultar_puntos=function(pagina){

         if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/GestionProyectoMapaDiseno?format=json&page='+pagina;
            parameter = { version_diseno_id:$('#version_diseno_id').val(),diseno_id:$('#id_diseno').val(), pagina: pagina,dato:self.filtro()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado_gps(agregarOpcionesObservable(datos.data));  

                } else {
                    self.listado_gps([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                newposition(datos.data);
                self.llenar_paginacion(datos,pagina);
                
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
               
            }, path, parameter,function(){
                 cerrarLoading();
            }, false);
        }
    }

    self.consultar_documentos=function(id_estado,completo){
            self.mensaje_documentos('');
            self.listado_documentos([]);
            path = path_principal+'/api/GestionProyectoSoporteEstado?sin_paginacion';
            parameter = { estado_id:id_estado};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_documentos(agregarOpcionesObservable(datos));  

                } else {
                    self.listado_documentos([]);
                    self.mensaje_documentos(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
                 
            }, path, parameter,function(){
                    if(completo==true){
                        self.consultar_puntos(1);
                    }else{
                        cerrarLoading();
                    }
            }, false);
    }



  function LLenarEstadoFecha(data){

    var lista=[];     
    var i=0;   

    ko.utils.arrayForEach(data, function(d) {
          
          if(d['fecha']!=''){
            i=i+1;
              lista.push({
                  id:ko.observable(d['id']),
                  nombre:ko.observable(d['nombre']),
                  id_estado:ko.observable(d['id_estado']),
                  fecha:ko.observable(d['fecha'])
              });
          }

    });

    if(i<data.length){
             lista.push({
                 id:ko.observable(data[i]['id']),
                 nombre:ko.observable(data[i]['nombre']),
                  id_estado:ko.observable(data[i]['id_estado']),
                 fecha:ko.observable(data[i]['fecha'])
             });
    }

    return lista;
  }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_gps(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar_puntos(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar_puntos(1);
        }
        return true;
    }


    self.descargar_plantilla=function(){
      location.href=path_principal+"/gestion_proyecto/descargar_plantilla";
    }


    self.mapa_grande=function(){
      location.href=path_principal+"/gestion_proyecto/mapa_grande/"+$('#id_diseno').val()+"/";
    }


    self.guardar_fechas=function(){


        var lista=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_fecha(), function(d) {

                if(d.fecha!=''){
                    count=1;
                   lista.push({
                        id:d.id(),
                        fecha:d.fecha(),
                        id_estado:d.id_estado(),
                        id_diseno:$('#id_diseno').val(),
                        version_diseno_id:$('#version_diseno_id').val()
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Digite una fecha en algùn estado .<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            })

         }else{

                var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/gestion_proyecto/actualizar_fechas/',//url api
                     parametros:lista                         
                  };
                Request(parametros);
         }    
    }


   



    self.guardar_info=function(){


        var lista=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_datos(), function(d) {

                if(d.valor!=''){
                    count=1;
                   lista.push({
                        id:d.id,
                        valor:d.valor,
                        id_dato:d.id_dato,
                        id_diseno:$('#id_diseno').val(),
                        version_diseno_id:$('#version_diseno_id').val()
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Digite un valor en cualquier dato tecnico .<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            })

         }else{

                var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){
                   
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/gestion_proyecto/actualizar_info/',//url api
                     parametros:lista                         
                  };
                Request(parametros);
         }    
    }


    function newposition(data){

        if(data.length>0){

          var place2 = new Array();
          var marker=[];
          var conteo=0;

          ko.utils.arrayForEach(data, function(d) {            
                
                place2[d.nombre]=new google.maps.LatLng(d.latitud, d.longitud);
                conteo=conteo+1;
           });

           
          var mapProp = {
              center:new google.maps.LatLng(10.084631601432866, -73.96812207270507),
              zoom:7,
              mapTypeId:google.maps.MapTypeId.ROADMAP
              };

            map=new google.maps.Map(document.getElementById("googleMap"),mapProp);
            var limits = new google.maps.LatLngBounds();

            if(data.length!=0){
                    for(var i in place2){
             
                        marker=new google.maps.Marker({
                          position:place2[i],
                          title:i
                          });
                        marker.setMap(map);
                         google.maps.event.addListener(marker, 'click', function(){
                            var popup = new google.maps.InfoWindow();
                            var note = this.title;
                            popup.setContent(note);
                            popup.open(map, this);
                        });

                        limits.extend(place2[i]);
                }

          
              
               map.fitBounds(limits);  
                if(conteo==1){
                  
                  zoomChangeBoundsListener = google.maps.event.addListenerOnce(map, 'bounds_changed', function(event) {
                          if (this.getZoom()){
                              this.setZoom(14);
                          }
                  });
              }  
               
               google.maps.event.trigger(map, 'resize');
  
            }else{
              google.maps.event.addDomListener(window, 'load');
            }
        }


      }


    self.eliminar_punto = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_gps(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un punto de localizacion para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/gestion_proyecto/eliminar_puntos/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los puntos de localizacion seleccionados?", path, parameter, function () {
                 self.consultar_puntos(1);
                 self.checkall(false);
             })

         }     
    
        
    }

    self.cargar_localizaciones=function(){

        if(self.soporte_localizacion()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar los puntos.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('id_diseno',$('#id_diseno').val());
            data.append('version_diseno_id',$('#version_diseno_id').val());
            data.append('archivo',self.soporte_localizacion());

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar_puntos(1);
                            $('#modal_documentos_localizacion').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/gestion_proyecto/guardar_puntos_soporte/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }
    }


    self.eliminar_soporte= function (obj) {

        
             var path =path_principal+'/api/GestionProyectoSoporteEstado/'+obj.id+'/';
             var parameter = '';
             RequestAnularOEliminar("Esta seguro que desea eliminar el soporte seleccionado?", path, parameter, function () {
                 self.consultar_documentos(self.soporteVO.estado_diseno_id(),false);
             });
        
    }

    self.reportar_exitosa=function(){

             var path =path_principal+'/gestion_proyecto/reportar_reporte_exitoso/';
             var parameter = {version_diseno_id:$('#version_diseno_id').val(),diseno_id:$('#id_diseno').val()};
             RequestAnularOEliminar("Esta seguro que desea marcar este proyecto con satisfaccion?", path, parameter, function () {
                 self.habilitar_btn_exitosa(true);
             });
    }

     self.reportar_diseno=function(){
           var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.habilitar_btn_reporte(true);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/gestion_proyecto/reportar_reporte_diseno/',//url api
                     parametros:{diseno_id:$('#id_diseno').val(),version_diseno_id:$('#version_diseno_id').val()}                         
                  };
                Request(parametros);
    }

     self.guardar_insconsistencia=function(){

            if(self.comentario_novedad()==''){

                     $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe escribir un comentario de la insconsistencia.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });

            }else{

                var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){

                        self.consultar_comentario_diseno();
                        self.comentario_novedad('');
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/gestion_proyecto/reportar_insconsistencia/',//url api
                     parametros:{version_diseno_id:$('#version_diseno_id').val(),diseno_id:$('#id_diseno').val(),comentario:self.comentario_novedad()}                         
                  };
                Request(parametros);

            }
          
    }

    self.consultar_comentario_diseno=function(){

        path = path_principal+'/api/GestionProyectoComentarioDiseno?sin_paginacion';
        parameter = { diseno_id:$('#id_diseno').val(),version_diseno_id:$('#version_diseno_id').val()};
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_comentarios_diseno(agregarOpcionesObservable(datos));  

                } else {
                    self.listado_comentarios_diseno([]);
                }

                cerrarLoading();
        }, path, parameter,undefined, false);


    }



 }

var tablero = new TableroViewModel();
TableroViewModel.errores_soporte = ko.validation.group(tablero.soporteVO);
TableroViewModel.errores_mapa = ko.validation.group(tablero.mapaVO);
TableroViewModel.errores_comentario = ko.validation.group(tablero.comentarioVO);
tablero.consultar();//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(tablero,content);
ko.applyBindings(tablero,header);