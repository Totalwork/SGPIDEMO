function EnlaceViewModel(){
	var self = this;
  var map;
  var lat;
  self.titulo=ko.observable('');
	self.mensaje=ko.observable('');
	self.nodo=ko.observable('');
	self.capa=ko.observable('');
	self.filtro=ko.observable('');
	self.listado=ko.observableArray([]);
	self.url=path_principal+'/api/';
  self.checkall=ko.observable(false);

  self.checkall_tendido=ko.observable(false);

  self.mensaje_tendidos=ko.observable('');

  self.archivo_carga=ko.observable('');
  self.listado_nodos=ko.observableArray([]);
  self.listado_apoyos=ko.observableArray([]);

  self.listado_enlaces=ko.observableArray([]);
  self.listado_detalles=ko.observableArray([]);

  self.habilitar_cambio=ko.observable(false);

  self.porcentaje_total=ko.observable(0);
  self.id_cambio=ko.observable(0);
  self.nombre_cambio=ko.observable('');

  self.cambio_crea=ko.observable(false);
  self.cambio_eliminar=ko.observable(false);
  self.cambio_modificar=ko.observable(false);

  self.listado_id_nodos_eliminar=ko.observableArray([]);

  self.listado_actividades=ko.observableArray([]);
  self.listado_actividades_modificacion=ko.observableArray([]);

  self.id_nodo=ko.observable(0);

  self.listado_estado=ko.observableArray([]);
  self.id_estado_busqueda=ko.observable('');


  self.nombre_nodo_origen=ko.observable('');
  self.id_nodo_origen=ko.observable('');

  self.listado_tendidos=ko.observableArray([]);

  self.listado_cambios=ko.observableArray([]);

  self.ejecutado=ko.observable(0);
  self.no_ejecutado=ko.observable(0);
  self.filtro_ejecutado=ko.observable(0);


  self.nombre_apoyo=ko.observable('');

  self.habilitar_reporte=ko.observable(false);

  self.sin_poste=ko.observable(false);

  self.apoyoVO={
        nodoOrigen_id:ko.observable(0),
        nodoDestino_id:ko.observable(0),
        capa_id:ko.observable($('#capa_id').val()),
        detallepresupuesto_id:ko.observable(0),
        presupuesto_id:ko.observable($('#id_presupuesto').val())
     };


  self.nodoVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del nodo' } }),
        longitud:ko.observable(''),
        latitud:ko.observable(''),
        presupuesto_id:ko.observable($("#id_presupuesto").val()),
        id_cambio:ko.observable(0),
        capa_id:ko.observable($("#capa_id").val()),
        noProgramado:ko.observable(true)
     };


   self.cambioCronogramaVO={
        cronograma_id:ko.observable($('#id_cronograma').val()),
        estado_id:ko.observable(1),
        motivo:ko.observable('').extend({ required: { message: '(*)Digite el motivo del cambio' } }),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del cambio' } }),
        solicitante_id:ko.observable($('#id_usuario').val()),
        empresa_tecnica_id:ko.observable('').extend({ required: { message: '(*)Seleccione una empresa tecnica' } }),
        empresa_financiera_id:ko.observable('').extend({ required: { message: '(*)Seleccione una empresa financiera' } }),
        tipo_accion_id:ko.observable('').extend({ required: { message: '(*)Seleccione un tipo de accion' } }),
        motivoRechazoTecnico:ko.observable(''),
        motivoRechazoTecnico:ko.observable(''),
        motivoRechazoTecnico:ko.observable('')
     };
    //funcion consultar todos los enlaces


    
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Apoyo');
        $('#modal_acciones').modal('show');
        
    }


    self.abrir_modal_carga = function (id) {
       self.limpiar();
        self.titulo('Registro de Cantidaddes Ejecutadas');
        self.consultar_apoyo(id);
        
    }

    self.abrir_modal_tendido = function (id) {
      self.apoyoVO.detallepresupuesto_id(0);
      self.apoyoVO.nodoDestino_id(0);
      self.consultar_detalle(id);
      self.titulo('Registrar de Tendido');
      $('#modal_tendido').modal('show');
        
    }


     self.abrir_modal_detalle_tendido = function (id) {
      self.titulo('Detalle del Tendido');
      self.nombre_nodo_origen('');
      self.id_nodo_origen(0);
      self.consultar_tendidos(id);
        
    }

    self.abrir_modal_cambio = function () {
      self.titulo('Registrar Cambio');
      $('#modal_cambios').modal('show');
        
    }

    self.abrir_modal_modificar_datos = function (id) {
      self.titulo('Modificar Datos');
      self.id_nodo(id);
      self.consultar_modificacion_actividades();
        
    }

    self.abrir_modal_detalle_cambio = function (id) {
      self.titulo('Detalles Cambio');
      self.consultar_detalle_cambio(id);
        
    }

    self.limpiar=function(){
        //self.apoyoVO.nombre('');
    }


    self.consultar_detalle_cambio=function(id){

        path = path_principal+'/api/avanceGrafico2DetalleReporteTrabajo/?sin_paginacion';
        parameter = {reporte_id:$('#reporte_id').val(),nodo_id:id};
        RequestGet(function (datos, estado, mensage) {

             
              self.listado_cambios(datos);
              
              $('#modal_detalle_cambio').modal('show');
              cerrarLoading();
        }, path, parameter);
    }


    self.consultar_tendidos=function(id){


        path = path_principal+'/api/avanceGrafico2Enlace/?sin_paginacion';
        parameter = {presupuesto_id:$('#id_presupuesto').val(),nodo_origen:id};
        RequestGet(function (datos, estado, mensage) {

              ko.utils.arrayForEach(self.listado(), function(d) {
                    
                    if(id==d.id){
                      self.nombre_nodo_origen(d.nombre);
                    }
              }); 
              self.id_nodo_origen(id);

               if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje_tendidos('');
                    //self.listado(results); 
                    self.listado_tendidos(agregarOpcionesObservable(datos));
                    

                } else {
                    self.listado_tendidos([]);
                    self.mensaje_tendidos(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

             

              
              $('#modal_detalle_tendido').modal('show');
              cerrarLoading();
        }, path, parameter);

    }


     self.checkall_tendido.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_tendidos(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.eliminar_tendidos=function(){

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_tendidos(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un nodo para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraGrafico2/eliminar_id_nodo_destino/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los nodos seleccionados?", path, parameter, function () {
                 self.consultar_tendidos(self.id_nodo_origen());
                 self.checkall_tendido(false);
                 self.consultar(1);
             })

         }  
    }

    self.consultar_modificacion_actividades=function(){


        path = path_principal+'/avanceObraGrafico/consultar_detalle_modificacion/';
        parameter = {nodo_id:self.id_nodo()};
        RequestGet(function (datos, estado, mensage) {

              self.listado_actividades_modificacion(self.llenar_actividad_modificacion(datos));

              $('#modal_modificar_datos').modal('show');
              cerrarLoading();
        }, path, parameter);

    }


    self.guardar_modificacion=function(){

       var listado=[];
      ko.utils.arrayForEach(self.listado_actividades_modificacion(), function(d) {

                  if(d.cantidad_nueva()>0 && d.cantidad_nueva()!=''){
                        listado.push({
                            id_presupuesto:d.id(),
                            cantidad:d.cantidad_nueva()
                      })
                  }

                  
        }); 

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {

                            $('#modal_modificar_datos').modal('hide');
                            self.id_nodo(0);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/guardar_modificacion/',//url api
                     parametros:{id_cambio:self.id_cambio(),id_nodo:self.id_nodo(),lista:listado}
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

    }


     self.guardar_reporte=function(){
     

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.habilitar_reporte(true);
                           
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico2/guardar_reporte_trabajo/'+$('#reporte_id').val()+'/',//url api
                     parametros:''
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

    }


    self.consultar_apoyo=function(id){
        self.id_nodo(id);
        path = path_principal+'/avanceObraGrafico2/consultar_ingresos_datos/';
        parameter = {nodo_id:id,reporte_id:$('#reporte_id').val()};
        RequestGet(function (datos, estado, mensage) {

              self.listado_detalles(self.llenar_apoyo(datos));

              $('#modal_listado').modal('show');
              cerrarLoading();
        }, path, parameter);

    }

    self.llenar_apoyo=function(data){

      self.porcentaje_total(0);
       var lista=[];
       var total=0;
       var cant=0;
        ko.utils.arrayForEach(data, function(d) {

                  var valor=parseFloat(d.cantidad_ejecutada)/ parseFloat(d.cantidad)
                  total=total+valor;
                  cant=cant+1;

                  lista.push({
                        id:ko.observable(d.id_detalle),
                        nodo_id:ko.observable(d.nodo_id),
                        codigoUC:ko.observable(d.codigo),
                        descripcionUC:ko.observable(d.descripcion),
                        cantidad_ejecutada:ko.observable(d.cantidad_ejecutada),
                        cantidad:ko.observable(d.cantidad),
                        cantidad_registrar:ko.observable(0)
                  })
        }); 

        total_por=(total/cant)*100
        if(total_por>100){
          total_por=100;
        }

        self.porcentaje_total(total_por.toFixed(2));

        


        return lista;

    }

    self.llenar_actividad=function(data){

      var lista=[];
        ko.utils.arrayForEach(data, function(d) {

                  lista.push({
                        id:ko.observable(d.id),
                        nombre_padre:ko.observable(d.nombre_padre),
                        actividad:ko.observable(d.actividad.nombre),
                        codigoUC:ko.observable(d.codigoUC),
                        descripcionUC:ko.observable(d.descripcionUC),
                        fecha:ko.observable(''),
                        cantidad:ko.observable(0)
                  })
        }); 

        


        return lista;

    }


     self.llenar_actividad_modificacion=function(data){

      var lista=[];
        ko.utils.arrayForEach(data, function(d) {

                  lista.push({
                        id:ko.observable(d.id),
                        nombre_padre:ko.observable(d.hito),
                        actividad:ko.observable(d.nombre_actividad),
                        codigoUC:ko.observable(d.codigoUC),
                        descripcionUC:ko.observable(d.descripcionUC),
                        cantidad:ko.observable(d.cantidad),
                        cantidad_nueva:ko.observable(0)
                  })
        }); 

        


        return lista;

    }

    self.guardar_cambio_cantidades=function(){

      var lista=[];
      ko.utils.arrayForEach(self.listado_detalles(), function(d) {
            if(d.cantidad_registrar()>0 && d.cantidad_registrar()!=''){

                lista.push({
                   id_detalle:d.id(),
                   cantidad:d.cantidad_registrar()
                })

            }
      });

              var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_listado').modal('hide');
                            self.id_nodo(0);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico2/guardar_cambio_cantidades/',//url api
                     parametros:{lista:lista,id_nodo:self.id_nodo(),id_reporte:$('#reporte_id').val()}                     
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
    }


    self.consultar_detalle=function(id){
          self.apoyoVO.nodoOrigen_id(id);
          path = path_principal+'/api/avanceGrafico2DetallePresupuesto/?sin_paginacion';
          parameter = {dato:'tendido',presupuesto_id:$('#id_presupuesto').val(),listado_apoyo:1,id_apoyo:id};
          RequestGet(function (datos, estado, mensage) {
              
              ko.utils.arrayForEach(self.listado(), function(d) {
                    
                    if(id==d.id){
                      self.nombre_nodo_origen(d.nombre);
                    }
              }); 


              self.listado_nodos(agregarOpcionesObservable(datos.datos));
              self.listado_apoyos(datos.apoyos);
               cerrarLoading();
          }, path, parameter);

    }

    self.crear_tendido=function(){
        if(self.apoyoVO.detallepresupuesto_id()==0 || self.apoyoVO.nodoDestino_id()==0){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione el nodo destino y el codigo de UUCC.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{

            path = path_principal+'/api/avanceGrafico2Enlace/?sin_paginacion';
            parameter = {presupuesto_id:$('#id_presupuesto').val(),nodo_origen:self.apoyoVO.nodoOrigen_id(),nodo_destino:self.apoyoVO.nodoDestino_id()};
            RequestGet(function (datos, estado, mensage) {

                   if(datos.length==0){

                        var parametros={                     
                             callback:function(datos, estado, mensaje){

                                if (estado=='ok') {
                                    self.consultar();
                                    self.nombre_nodo_origen('');
                                    $('#modal_tendido').modal('hide');
                                }                        
                                
                             },//funcion para recibir la respuesta 
                             url:path_principal+'/api/avanceGrafico2Enlace/',//url api
                             parametros:self.apoyoVO                        
                        };
                        //parameter =ko.toJSON(self.contratistaVO);
                        Request(parametros);
                   }
            }, path, parameter, undefined, false, false);

        }

    }

    self.consultar=function(){

        self.filtro($('#txtBuscar').val());
        sessionStorage.setItem("filtro_avance",self.filtro() || '');


        self.cargar();

    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            //self.limpiar();
            self.consultar();
        }
        return true;
    }

    self.cargar = function () {
            programado='';
            if(self.cambio_crea()==false){
                programado=0;
            }else{
              programado=1;
            }

            if(self.id_estado_busqueda()==''){
                  self.id_estado_busqueda('2,3');
            }

            if($('#reporte_cerrado').val()=='True' || $('#reporte_cerrado').val()==true){
                self.habilitar_reporte(true);
            }

            let filtro_avance=sessionStorage.getItem("filtro_avance");
            path = path_principal+'/avanceObraGrafico2/consultar_avance_obra/';
            parameter = {presupuesto_id:$("#id_presupuesto").val(),
            cronograma_id:$('#id_cronograma').val(),dato:filtro_avance,programando:programado};
            // parameter = {presupuesto_id:$("#id_presupuesto"),
            // cronograma_id:$('#id_cronograma').val(),id_estados:self.id_estado_busqueda(),dato:filtro_avance,programando:programado};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.datos!=null && datos.datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.datos));
                    self.listado_enlaces(datos.enlace);
                    

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                if($('#sin_poste').val()=='False'){
                  self.sin_poste(false);
                }else{
                  self.sin_poste(true);
                }
                self.initMap();

               
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
        }


    self.guardar=function(){
        self.guardar_nodo(lat);
    }


   



    self.initMap = function(){
  // defino el mapa con estilo nocturno
    map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 10.9494272, lng: -74.801152},
    zoom: 4,
    styles: [
      {elementType: 'geometry', stylers: [{color: '#242f3e'}]},
      {elementType: 'labels.text.stroke', stylers: [{color: '#242f3e'}]},
      {elementType: 'labels.text.fill', stylers: [{color: '#746855'}]},
      {
        featureType: 'administrative.locality',
        elementType: 'labels.text.fill',
        stylers: [{color: '#d59563'}]
      },
      {
        featureType: 'poi',
        elementType: 'labels.text.fill',
        stylers: [{color: '#d59563'}]
      },
      {
        featureType: 'poi.park',
        elementType: 'geometry',
        stylers: [{color: '#263c3f'}]
      },
      {
        featureType: 'poi.park',
        elementType: 'labels.text.fill',
        stylers: [{color: '#6b9a76'}]
      },
      {
        featureType: 'road',
        elementType: 'geometry',
        stylers: [{color: '#38414e'}]
      },
      {
        featureType: 'road',
        elementType: 'geometry.stroke',
        stylers: [{color: '#212a37'}]
      },
      {
        featureType: 'road',
        elementType: 'labels.text.fill',
        stylers: [{color: '#9ca5b3'}]
      },
      {
        featureType: 'road.highway',
        elementType: 'geometry',
        stylers: [{color: '#746855'}]
      },
      {
        featureType: 'road.highway',
        elementType: 'geometry.stroke',
        stylers: [{color: '#1f2835'}]
      },
      {
        featureType: 'road.highway',
        elementType: 'labels.text.fill',
        stylers: [{color: '#f3d19c'}]
      },
      {
        featureType: 'transit',
        elementType: 'geometry',
        stylers: [{color: '#2f3948'}]
      },
      {
        featureType: 'transit.station',
        elementType: 'labels.text.fill',
        stylers: [{color: '#d59563'}]
      },
      {
        featureType: 'water',
        elementType: 'geometry',
        stylers: [{color: '#17263c'}]
      },
      {
        featureType: 'water',
        elementType: 'labels.text.fill',
        stylers: [{color: '#515c6d'}]
      },
      {
        featureType: 'water',
        elementType: 'labels.text.stroke',
        stylers: [{color: '#17263c'}]
      }
    ]

  });

  

  
  ko.utils.arrayForEach(self.listado(), function(d) {
          
        var marker = new google.maps.Marker({
          position: {
                      lat: parseFloat(d.latitud),
                      lng:  parseFloat(d.longitud)
          },
          map: map,
          title: d.nombre,
          draggable:false
        });

        marker.addListener('click', function(e) {
            self.nombre_apoyo(d.nombre);
            var contentStringOrg = '<div id="content">'+
            '<div id="siteNotice">'+
            '</div>'+
            '<h1 id="firstHeading" class="firstHeading">'+d.nombre+'</h1>'+
            '<div id="bodyContent">';
            if(self.habilitar_reporte()==false){
                contentStringOrg=contentStringOrg+'<p><button onclick="llamarDetalle('+d.id+')">Ingresar Cantidades Ejecutadas</button></p>';
            }
            
            contentStringOrg=contentStringOrg+'<p><button onclick="detalleDatos('+d.id+')">Detalles del Trabajo</button></p>';

            if(self.habilitar_reporte()==false){
                contentStringOrg=contentStringOrg+'<p><button onclick="llamarTendido('+d.id+')">Crear tendido</button></p>';
            }
           
            contentStringOrg=contentStringOrg+'<p><button onclick="detalleTendido('+d.id+')">Detalle del tendido</button></p>';

            contentStringOrg=contentStringOrg+'</div></div>';           
            var infowindow = new google.maps.InfoWindow({
              content: contentStringOrg
            });
          infowindow.open(map, marker);
        });
  }); 

  ko.utils.arrayForEach(self.listado_enlaces(), function(obj) {

        var flightPlanCoordinates=[
        {lat:parseFloat(obj['nodoOrigen__latitud']), lng: parseFloat(obj['nodoOrigen__longitud'])},
        {lat: parseFloat(obj['nodoDestino__latitud']), lng: parseFloat(obj['nodoDestino__longitud'])}
        ]

         var flightPath = new google.maps.Polyline({
              path: flightPlanCoordinates,
              geodesic: true,
              strokeColor: obj['capa__color'],
              strokeOpacity: 1.0,
              strokeWeight: 6,
              desde: obj['nodoOrigen__nombre'],
              hasta: obj['nodoDestino__nombre'],
              codigo_id: obj['id']
          });

         flightPath.setMap(map);
  });
   
   

  map.addListener('click', function(e) {
      if(self.cambio_crea()==true){
          lat=e.latLng;
          map=map;
          self.abrir_modal();

      }
  });


 
  //dibujar los nodos y enlaces
  //console.log(self.listado['0']);
 }


  self.actualizar_nodo=function(data){

                  self.apoyoVO.id(data.id);
                  self.apoyoVO.nombre(data.nombre);
                  self.apoyoVO.presupuesto_id(data.presupuesto.id);
                  self.apoyoVO.longitud(data.longitud);
                  self.apoyoVO.latitud(data.latitud);
                  self.apoyoVO.capa_id(data.capa.id);

                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.consultar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/avanceObraGraficoNodo/'+self.apoyoVO.id()+'/',
                       parametros:self.apoyoVO,
                       alerta:false                    
                  };

                  Request(parametros);

  }

  self.cancelar_cambio=function(){

              var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.id_cambio(0);
                          self.nombre_cambio('');
                          self.cambio_crea(false);
                          self.habilitar_cambio(false);
                          self.cambio_eliminar(false);
                          self.cambio_modificar(false);
                          self.id_nodo(0);
                          self.consultar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/eliminar_cambio/',//url api
                     parametros:{id_nodo:self.id_cambio(),tipo_accion:self.cambioCronogramaVO.tipo_accion_id()},
                     alerta:false                   
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);



  }




  self.consultar_actividades=function(){

            path = path_principal+'/api/avanceObraGraficoDetallePresupuesto/?sin_paginacion';
            parameter = {presupuesto_id:$('#id_presupuesto').val()};
            RequestGet(function (datos, estado, mensage) {

                     if (estado=='ok' && datos!=null && datos.length > 0) {
                                    self.listado_actividades(self.llenar_actividad(datos));
                                    $('#modal_cantidad_nueva').modal('show');
                      }  
                      cerrarLoading();
            }, path, parameter, undefined, false, false);
       
  }





   self.consultar_estados=function(){

            path = path_principal+'/api/avanceObraGraficoEstadoCambio/?sin_paginacion';
            parameter = '';
            RequestGet(function (datos, estado, mensage) {

                if (datos.length > 0) {
                    self.listado_estado(agregarOpcionesObservable(datos));
                }else{
                  self.listado_estado([]);
                }
            }, path, parameter, undefined, false, false);
    }


  self.consultar_cambio_estado=function(value){
     sw=0;
     self.id_estado_busqueda('');
     ko.utils.arrayForEach(self.listado_estado(), function(obj) {

          if(obj.eliminado()==true){
              if(sw==0){
                self.id_estado_busqueda(obj.id);
                sw=1;
              }else{
                self.id_estado_busqueda(self.id_estado_busqueda()+","+obj.id);
              }
              
          }             
                         
      }); 

      self.consultar();

    return true;
  }

   self.consultar_cambio_ejecucion=function(){
      console.log(self.ejecutado())
      if(self.ejecutado()==true){
        self.filtro_ejecutado(2);
      }else if(self.no_ejecutado()==true){
        self.filtro_ejecutado(1);
      }else{
        self.filtro_ejecutado(0);
      }
      self.consultar();

    return true;
  }


  self.guardar_detalle_cambio=function(){


      var listado=[];
      ko.utils.arrayForEach(self.listado_cambios(), function(d) {

                  if(d.cantidadEjecutada>0 && d.cantidadEjecutada!=''){
                        listado.push({
                            id:d.id,
                            cantidad:d.cantidadEjecutada
                      })
                  }

                  
        }); 

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {

                            $('#modal_detalle_cambio').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico2/guardar_cambio_detalle/',//url api
                     parametros:{lista:listado}
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

  }

   self.abrir_grafico=function(){

             location.href=path_principal+"/avanceObraGrafico/grafico/"+$('#id_presupuesto').val()+"/"+$('#id_proyecto').val()+"/"+$('#id_cronograma').val()+"/";

    }


}

var enlace = new EnlaceViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
EnlaceViewModel.errores_apoyo = ko.validation.group(enlace.nodoVO);
EnlaceViewModel.errores_cambio = ko.validation.group(enlace.cambioCronogramaVO);
enlace.cargar();
enlace.consultar_estados();
ko.applyBindings(enlace);

function llamarDetalle(id){
    //Mostrar el popup con las propiedades
    enlace.abrir_modal_carga(id);
}

function llamarTendido(id){
    //Mostrar el popup con las propiedades
   enlace.abrir_modal_tendido(id);
}

function eliminarpunto(id){
    //Mostrar el popup con las propiedades
    enlace.eliminar_punto(id);
}

function modificarpunto(id){
    //Mostrar el popup con las propiedades
    enlace.abrir_modal_modificar_datos(id);
}

function detalleTendido(id){
    //Mostrar el popup con las propiedades
   enlace.abrir_modal_detalle_tendido(id);
}

function detalleDatos(id){
    //Mostrar el popup con las propiedades
   enlace.abrir_modal_detalle_cambio(id);
}




