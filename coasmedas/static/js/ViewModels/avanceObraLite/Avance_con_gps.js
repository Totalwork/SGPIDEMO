function EnlaceViewModel(){
	var self = this;
  var map;
  var lat;
  self.titulo=ko.observable('');
	self.mensaje=ko.observable('');
	self.nodo=ko.observable('');
	self.capa=ko.observable('');
	self.filtro=ko.observable('');
  self.tituloFotosNodo = ko.observable('');
  self.tituloNoconformidadNodo = ko.observable('');
  self.no_conformidad_titulo = ko.observable('');

	self.listado=ko.observableArray([]);
	self.url=path_principal+'/api/';
  self.checkall=ko.observable(false);

  self.checkall_tendido=ko.observable(false);

  self.mensaje_tendidos=ko.observable('');

  self.archivo_carga=ko.observable('');
  self.listado_nodos=ko.observableArray([]);
  self.listado_apoyos=ko.observableArray([]);

  self.listadoNoconformidadNodo =ko.observableArray([]);
  self.mensajeNoconformidadsNodo =ko.observable('');

  self.listado_enlaces=ko.observableArray([]);
  self.listado_detalles=ko.observableArray([]);
  self.listadoMat_detalle = ko.observableArray([]);
  self.listadoPorcentajes = ko.observableArray([]);
  self.mensajeMateriales = ko.observable('');

  self.listadoFotosNodo = ko.observableArray([]);
  self.mensajeFotosNodo = ko.observable('');

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

  self.fotoNodoVO = {
    id: ko.observable(0),
    fecha: ko.observable('').extend({ required: { message: '(*)Seleccione la fecha' } }),
    comentario: ko.observable(''),
    ruta: ko.observable('').extend({ required: { message: '(*)Seleccione el archivo' } })
  }


  self.nombre_usuario=ko.observable('');

  self.listado_empresa_contratante=ko.observable([]);
  self.id_empresa = ko.observable(0);
  self.nombre_usuario = ko.observable('');
  self.nom_usuario = ko.observable('');
  self.list_usuario=ko.observable([]);
  self.id_detectada=ko.observable(0);
  self.ver_usuario=ko.observable(false);
  self.mensaje_usuario=ko.observable('');

  self.noconformidadNodoVO = {
    id:ko.observable(0),
    proyecto_id:ko.observable(),
    usuario_id:ko.observable(0),
    estado_id:ko.observable(0),
    detectada_id:ko.observable().extend({ required: { message: '(*)Seleccione un funcionario' } }),
    descripcion_no_corregida:ko.observable('').extend({ required: { message: '(*)Digite la descripcion de la No Conformidad' } }),
    descripcion_corregida:ko.observable(''),
    fecha_no_corregida:ko.observable('').extend({ required: { message: '(*)Seleccione una fecha' } }),
    fecha_corregida:ko.observable(''),
    terminada:ko.observable(0),
    estructura:ko.observable(''),
    primer_correo:ko.observable(''),
    segundo_correo:ko.observable(''),
    tercer_correo:ko.observable(''),
    foto_no_corregida:ko.observable(),//.extend({ required: { message: '(*)Seleccione una foto de la No Conformidad' } }),
    foto_no_corregida2:ko.observable(),
    foto_no_corregida3:ko.observable(),
    foto_corregida:ko.observable(''),
    foto_corregida2:ko.observable(''),
    foto_corregida3:ko.observable(''),
    tipo_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de No Conformidad' } }),
    valoracion_id:ko.observable('').extend({ required: { message: '(*)Seleccione la valoración de la No Conformidad' } }),
  }

     //paginacion de la fotos del proyecto
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

    //paginacion
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultarFotosNodo(pagina);

    });

    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }


    self.paginacion_noconformidad = {
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

    //paginacion
    self.paginacion_noconformidad.pagina_actual.subscribe(function (pagina) {
        self.consultarNoconformidadNodo(pagina);

    });

    self.llenar_paginacion_noconformidad = function (data,pagina) {

        self.paginacion_noconformidad.pagina_actual(pagina);
        self.paginacion_noconformidad.total(data.count);       
        self.paginacion_noconformidad.cantidad_por_paginas(resultadosPorPagina);

    }



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
        self.titulo('Registro de Cantidades Ejecutadas');
        self.consultar_apoyo(id);
        
    }



    self.ver_soporte = function(obj) {
      window.open(path_principal+"/avanceObraLite/verfoto?id="+ obj.id, "_blank");
    }

    self.abrir_modal_fotos = function (id) {
      //traer las fotos:
        self.fotoNodoVO.id(id);
        self.consultarFotosNodo(1);
        ocultarNuevaFoto();
      //abrir el modal:
        $('#modal_fotos').modal('show');

    }

    self.consultarFotosNodo = function (page) {
        //self.id_nodo(nodo_id);
        path = path_principal+'/api/fotonodo/';
        parameter = {
          nodo : self.fotoNodoVO.id(),
          page : page,
          desde : $('#desde').val(),
          desde : $('#hasta').val(),
        };
        RequestGet(function (datos, estado, mensage) {
          if (datos.data != null && datos.data.length > 0){
            self.listadoFotosNodo(datos.data);
            self.mensajeFotosNodo('');
          } else {
            self.listadoFotosNodo([]);
            self.mensajeFotosNodo(mensajeNoFound);
          }
          cerrarLoading();
          self.llenar_paginacion(datos,page);
        }, path, parameter);      
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
             var path =path_principal+'/avanceObraLite/eliminar_id_nodo_destino/';
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
                RequestFormData(parametros);

    }


     self.guardar_reporte=function(){
     

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.habilitar_reporte(true);
                           
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraLite/guardar_reporte_trabajo/'+$('#reporte_id').val()+'/',//url api
                     parametros:''
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);

    }


    self.consultar_apoyo=function(id){
        self.id_nodo(id);
        path = path_principal+'/avanceObraLite/consultar_ingresos_datos/';
        parameter = {nodo_id:id,reporte_id:$('#reporte_id').val()};
        RequestGet(function (datos, estado, mensage) {
              self.listado_detalles(self.llenar_apoyo(datos.unidadesConstructivas));
              self.listadoPorcentajes(datos.porcentajeEjecucion)
              
              if (datos.materiales.length > 0){
                self.listadoMat_detalle(datos.materiales);
                self.mensajeMateriales('');
              }else{
                self.listadoMat_detalle([]);
                self.mensajeMateriales(mensajeNoFound);
              }
              $('#modal_listado').modal('show');
              demoCircleGraphs();
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
                        cantidad_registrar:ko.observable(0),
                        editable: ko.observable(d.editable)
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
                            location.reload();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraLite/guardar_cambio_cantidades/',//url api
                     parametros:{lista:lista,id_nodo:self.id_nodo(),id_reporte:$('#reporte_id').val()}                     
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
                

    }


    self.consultar_detalle=function(id){
          self.apoyoVO.nodoOrigen_id(id);
          path = path_principal+'/api/avanceObraLiteDetallePresupuesto/?sin_paginacion';
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
                        RequestFormData(parametros);
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
            path = path_principal+'/avanceObraLite/consultar_avance_obra/';
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
    center = {lat: 10.9494272, lng: -74.801152}
    zoom = 6
    if (sessionStorage.getItem("ubicacionActual") != 'null') {
      array = sessionStorage.getItem("ubicacionActual").split(",");
      center = {lat: parseFloat(array[0]), lng: parseFloat(array[1])}
      zoom = parseInt(array[2]);
    }
    map = new google.maps.Map(document.getElementById('map'), {
    center: center,
    zoom: zoom,
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
        var qurl = "";
        if (d.porcentajeAcumulado == 0){
          qurl = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";
        }else{
          if (d.porcentajeAcumulado >= 100){
            qurl = "http://maps.google.com/mapfiles/ms/icons/green-dot.png";
          }else{
            qurl = "http://maps.google.com/mapfiles/ms/icons/orange-dot.png";
          }
        }
          
        var marker = new google.maps.Marker({
          position: {
                      lat: parseFloat(d.latitud),
                      lng:  parseFloat(d.longitud)
          },
          map: map,
          title: d.nombre,
          draggable:false,
          icon: {
            url: qurl,
            scaledSize : new google.maps.Size(50,50)
          }
        });

        marker.addListener('click', function(e) {
            self.nombre_apoyo(d.nombre);
            var contentStringOrg = '<div id="content">'+
            '<div id="siteNotice">'+
            '</div>'+
            '<h1 id="firstHeading" class="firstHeading">'+d.nombre+'</h1>'+
            '<div id="bodyContent">';
            contentStringOrg = contentStringOrg + '<div class="progress">'+
            '<div class="progress-bar progress-bar-success" role="progressbar"'+
            ' aria-valuenow="'+d.porcentajeAcumulado+'" aria-valuemin="0" aria-valuemax="100"'+
            ' style="width: '+d.porcentajeAcumulado+'%;">'+d.porcentajeAcumulado+'%</div>'+
            '</div>';
            if(self.habilitar_reporte()==false){
                contentStringOrg=contentStringOrg+'<p><button onclick="llamarDetalle('+d.id+')">Cantidades Ejecutadas</button></p>';
            }
            
            contentStringOrg=contentStringOrg+'<p><button onclick="detalleDatos('+d.id+')">Detalles del Trabajo</button></p>';

            if(self.habilitar_reporte()==false){
                contentStringOrg=contentStringOrg+'<p><button onclick="llamarTendido('+d.id+')">Crear tendido</button></p>';
            }

            self.noconformidadNodoVO.estructura(d.nombre);
           
            contentStringOrg=contentStringOrg+'<p><button onclick="detalleTendido('+d.id+')">Detalle del tendido</button></p>';
            contentStringOrg=contentStringOrg+'<p><button onclick="fotosnodo('+d.id+')">Registro fotografico del nodo</button></p>';
            contentStringOrg=contentStringOrg+'<p><button onclick="noconformidadnodo()">No conformidades del nodo</button></p>';
            self.tituloFotosNodo('Registro fotografico del nodo ' + d.nombre);
            self.tituloNoconformidadNodo('No conformidades del nodo ' + d.nombre);
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

google.maps.event.addListener(map, 'zoom_changed', function() {
    var c = map.getCenter();
    sessionStorage.setItem("ubicacionActual", c.lat() + ',' 
                                  + c.lng() + ',' + map.getZoom());   
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

                  RequestFormData(parametros);

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
                RequestFormData(parametros);



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
                     url:path_principal+'/avanceObraLite/guardar_cambio_detalle/',//url api
                     parametros:{lista:listado}
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

  }

   self.abrir_grafico=function(){

             location.href=path_principal+"/avanceObraGrafico/grafico/"+$('#id_presupuesto').val()+"/"+$('#id_proyecto').val()+"/"+$('#id_cronograma').val()+"/";

    }

    self.guardarFoto = function() {
      //alert('guardando la foto...');
      var data = new FormData();
      if (EnlaceViewModel.errores().length == 0) {//se activa las validaciones
        data.append('nodo_id',self.fotoNodoVO.id());
        data.append('fecha',self.fotoNodoVO.fecha());
        data.append('comentario',self.fotoNodoVO.comentario());

        for (var i = 0; i <  $('#archivo')[0].files.length; i++) {
          data.append('archivo[]', $('#archivo')[0].files[i]); 
        };

        var parametros={                     
            callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                    self.limpiarFotoNodo();
                    self.consultarFotosNodo(1);
                    //$('#modal_fotos').modal('hide');
                }                        
                    
            },//funcion para recibir la respuesta 
            url:path_principal+'/api/fotonodo/',//url api
            parametros:data                        
        };
        RequestFormData2(parametros);
      }else{
        EnlaceViewModel.errores.showAllMessages();//mostramos las validacion
      }
    }

    self.eliminarFoto = function (obj) {
      var path =path_principal+'/api/fotonodo/'+obj.id+'/';
      var parameter = {};
      RequestAnularOEliminar("Esta seguro que desea eliminar la foto del nodo?", path, parameter, function () {
          self.consultarFotosNodo(1);
      })
    }

    self.limpiarFotoNodo = function () {
      $('#archivo').fileinput('reset');
      $('#archivo').val('');      

      //self.fotoNodoVO.id(0);
      self.fotoNodoVO.fecha('');
      self.fotoNodoVO.comentario('');
      self.fotoNodoVO.ruta('');

      self.fotoNodoVO.fecha.isModified(false);
      self.fotoNodoVO.ruta.isModified(false);

      $('#nuevaFoto').hide();
      $('#divOcultarFoto').hide();
      $('#divNuevaFoto').show();

    }



    // funciones para No conformidad
    self.abrir_no_conformidad = function(){
      //traer las fotos:
        self.noconformidadNodoVO.id(0);
        self.noconformidadNodoVO.proyecto_id($('#id_proyecto').val());

        self.consultarNoconformidadNodo(1);
        //ocultarNuevaNoconformidad();
      //abrir el modal:
      //alert('algo');
        
    }

    self.consultarNoconformidadNodo = function (page) {
        //self.id_nodo(nodo_id);
        path = path_principal+'/api/no_conformidad/';
        parameter = {
          estructura: self.noconformidadNodoVO.estructura(),
          id_proyecto: self.noconformidadNodoVO.proyecto_id(),
        };
        RequestGet(function (datos, estado, mensage) {
          if (datos.data != null && datos.data.length > 0){
            self.listadoNoconformidadNodo(datos.data);
            self.mensajeNoconformidadsNodo('');
          } else {
            self.listadoNoconformidadNodo([]);
            self.mensajeNoconformidadsNodo(mensajeNoFound);
          }

          $('#modal_noconformidad').modal('show');
          cerrarLoading();
          self.llenar_paginacion_noconformidad(datos,page);
          self.listar_usuario();
          self.llenarSelect();
          
        }, path, parameter);      
    }

    self.abrir_modal_usuario = function () {
      $('#modal_usuario').modal('show');
    }

    self.consulta_enter_usuario = function (d,e) {
      if (e.which == 13) {
        //self.filtro($('#txtBuscar').val());
        self.listar_usuario();
        //console.log("asa;"+$('#nom_nit1').val());
      }
      return true;
    }


    self.listar_usuario=function(){
        path =path_principal+'/api/usuario/?lite=1&sin_paginacion=1';
        parameter = '';
        faltante = 0;
        // alert('ola:'+self.nombre_usuario());

      
        if (self.id_empresa()!=0){
          var empresa_id = self.id_empresa();
        }else{
          var empresa_id = $('#id_empresa').val();
        }

        if(empresa_id != 0){
          parameter = 'empresa_id='+ empresa_id;
          faltante = 1;
        }
        if($('#id_nombre_usuario').val() != ''){
          parameter = parameter+'&dato='+ $('#id_nombre_usuario').val();
        }

        if(faltante == 1){
          RequestGet(function (results,success,message) {

            if (success == 'ok' && results!=null && results.length > 0) {
              self.mensaje_usuario('');
              self.list_usuario(agregarOpcionesObservable(results));
              self.ver_usuario(true);
            } else {
              self.list_usuario([]);
              self.ver_usuario(false);
              self.mensaje_usuario(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
              //mensajeInformativo('No se encontraron registros');
            }
            //self.llenar_paginacion(datos,pagina);
          }, path, parameter);
        }else{
          mensajeInformativo('Seleccione una Empresa.','Información');return false;
        }
    }

    self.llenarSelect=function(dato){
      parameter={};
      path = path_principal+'/api/Contrato/?format=json';
      parameter = {sin_list_contrato:1,//tipo:1,
             contratante:1};
      RequestGet(function (datos, estado, mensage) {
        self.listado_empresa_contratante(datos.contratante);
      }, path, parameter,function(){},false,false);
    }

    self.guardar_noconformidad=function(){
        if (EnlaceViewModel.errores_no_conformidad().length == 0){ //se activa las validaciones

        // self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
        if(self.noconformidadNodoVO.id()==0){
          var soporte = true;
          if($('#archivo')[0].files.length==0){
            //self.noconformidadNodoVO.soporte('');
            soporte = false;
          }
          if($('#archivo2')[0].files.length==0){
            self.noconformidadNodoVO.foto_no_corregida2('');
            
          }
          if($('#archivo3')[0].files.length==0){
            self.noconformidadNodoVO.foto_no_corregida3('');
            
          }
          //console.log("val:"+self.noconformidadNodoVO.valor());
          if(soporte){
            if((self.noconformidadNodoVO.proyecto_id() != 0) && (self.noconformidadNodoVO.detectada_id() != 0)){
              var parametros={
                callback:function(datos, estado, mensaje){

                  if (estado=='ok') {

                    $('#divNuevaNoconformidad').modal('hide');
                    self.limpiar_conformidad();
                    self.consultarNoconformidadNodo(1);
                  }else{
                    mensajeError(mensaje);
                  }
                }, //funcion para recibir la respuesta 
                url:path_principal+'/api/no_conformidad/',//url api
                parametros:self.noconformidadNodoVO
              };
              //parameter =ko.toJSON(self.noconformidadNodoVO);
              //Request(parametros);
              RequestFormData(parametros);
            }else{
              mensajeInformativo('Falta por ingresar proyecto o el usuario.','Información');
            }
          }else{
            mensajeInformativo('Falta por seleccionar la Foto.','Información');
          }
        }else{
          if($('#archivo')[0].files.length==0){
            self.noconformidadNodoVO.foto_no_corregida('');
          }
          if($('#archivo2')[0].files.length==0){
            self.noconformidadNodoVO.foto_no_corregida2('');
          }
          if($('#archivo3')[0].files.length==0){
            self.noconformidadNodoVO.foto_no_corregida3('');
          }

          if($('#archivo_corregido')[0].files.length==0){
            self.noconformidadNodoVO.foto_corregida('');
          }
          if($('#archivo_corregido2')[0].files.length==0){
            self.noconformidadNodoVO.foto_corregida2('');
          }
          if($('#archivo_corregido3')[0].files.length==0){
            self.noconformidadNodoVO.foto_corregida2('');
          }
          //console.log("val:"+self.noconformidadNodoVO.valor());
          if((self.noconformidadNodoVO.proyecto_id() != 0) && (self.noconformidadNodoVO.detectada_id() != 0)){
            var parametros={
              metodo:'PUT',
              callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                  self.filtro("");
                  self.consultar(self.paginacion.pagina_actual());
                  $('#modal_acciones').modal('hide');
                  $('#modal_correccion').modal('hide');
                  self.limpiar();
                }

              },//funcion para recibir la respuesta 
              url:path_principal+'/api/no_conformidad/'+self.noconformidadNodoVO.id()+'/',
              parametros:self.noconformidadNodoVO
            };
            RequestFormData(parametros);
          }else{
            mensajeInformativo('Falta por ingresar proyecto o el usuario.','Información');
          }
        }
      } else {
        EnlaceViewModel.errores_no_conformidad.showAllMessages();
      }

    }

    self.agregar_usuario = function () {

      self.noconformidadNodoVO.detectada_id(self.id_detectada());
      self.nom_usuario($('#nom_usuario option:selected').text());
      $('#modal_usuario').modal('hide');
      // alert('id_proy:'+self.usuario_select());
      // alert('nom_proy:'+$('#nom_usuario option:selected').text());
    }


    self.limpiar_conformidad=function(){
        self.noconformidadNodoVO.id(0);
        self.noconformidadNodoVO.usuario_id(0);
        self.noconformidadNodoVO.estado_id(0);
        self.noconformidadNodoVO.detectada_id(0);
        self.noconformidadNodoVO.descripcion_no_corregida('');
        self.noconformidadNodoVO.descripcion_corregida('');
        self.noconformidadNodoVO.fecha_no_corregida('');
        self.noconformidadNodoVO.fecha_corregida('');
        self.noconformidadNodoVO.terminada(0);
        self.noconformidadNodoVO.primer_correo('');
        self.noconformidadNodoVO.segundo_correo('');
        self.noconformidadNodoVO.tercer_correo('');
        self.noconformidadNodoVO.foto_no_corregida('');
        self.noconformidadNodoVO.foto_no_corregida2('');
        self.noconformidadNodoVO.foto_no_corregida3('');
        self.noconformidadNodoVO.foto_corregida('');
        self.noconformidadNodoVO.foto_corregida2('');
        self.noconformidadNodoVO.foto_corregida3('');
        self.nom_usuario('');
        $('#archivo').fileinput('reset');
        $('#archivo').val('');

        $('#archivo2').fileinput('reset');
        $('#archivo2').val('');


        $('#archivo3').fileinput('reset');
        $('#archivo3').val('');

        $('#archivo_corregido').fileinput('reset');
        $('#archivo_corregido').val('');

        self.noconformidadNodoVO.fecha_no_corregida.isModified(false);
        self.noconformidadNodoVO.descripcion_no_corregida.isModified(false);
        self.noconformidadNodoVO.estructura.isModified(false);
        self.noconformidadNodoVO.tipo_id('');
        self.noconformidadNodoVO.valoracion_id('');
        self.noconformidadNodoVO.foto_no_corregida('');

    }


    self.ver_examinar_noconformidad = function (proyecto_id,estructura,descripcion,proyecto) {
      sessionStorage.setItem("app_no_conformidad_id_proyecto",proyecto_id || '');
      sessionStorage.setItem("app_no_conformidad_estructura",estructura || '');
      sessionStorage.setItem("app_no_conformidad_dato",descripcion || '');
      sessionStorage.setItem("app_no_conformidad_proyecto_nombre",proyecto || '');
      ruta = self.url+'../../no_conformidad/no_conformidad/';
      window.location.href = ruta

    }
}

var enlace = new EnlaceViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
EnlaceViewModel.errores_apoyo = ko.validation.group(enlace.nodoVO);
EnlaceViewModel.errores_cambio = ko.validation.group(enlace.cambioCronogramaVO);
EnlaceViewModel.errores = ko.validation.group(enlace.fotoNodoVO);
EnlaceViewModel.errores_no_conformidad = ko.validation.group(enlace.noconformidadNodoVO);

enlace.cargar();
enlace.consultar_estados();
ko.applyBindings(enlace);

function noconformidadnodo(){
  enlace.abrir_no_conformidad();
}
function fotosnodo(id){
    //Mostrar el popup con las fotos
    enlace.abrir_modal_fotos(id);
    
}

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

function demoCircleGraphs() {
    var infoCircle = $('.info-circle');
    if (infoCircle.length) {
        // Color Library we used to grab a random color
        var colors = {
            "primary": [bgPrimary, bgPrimaryLr,
                bgPrimaryDr
            ],
            "info": [bgInfo, bgInfoLr, bgInfoDr],
            "warning": [bgWarning, bgWarningLr,
                bgWarningDr
            ],
            "success": [bgSuccess, bgSuccessLr,
                bgSuccessDr
            ],
            "alert": [bgAlert, bgAlertLr, bgAlertDr]
        };
        // Store all circles
        var circles = [];
        infoCircle.each(function(i, e) {
            //alert($(e).attr('title'));
            // Define default color
            var color = ['#DDD', bgPrimary];
            // Modify color if user has defined one
            var targetColor = $(e).data(
                'circle-color');
            if (targetColor) {
                var color = ['#DDD', colors[
                    targetColor][0]]
            }
            // Create all circles
            var circle = Circles.create({
                id: $(e).attr('id'),
                value: $(e).attr('value'),
                radius: $(e).width() / 2,
                width: 14,
                colors: color,
                text: function(value) {
                    var title = $(e).attr('title');
                    if (title) {
                        return '<h2 class="circle-text-value">' + value + '</h2><p>' + title + '</p>' 
                    } 
                    else {
                        return '<h2 class="circle-text-value mb5">' + value + '</h2>'
                    }
                }
            });
            circles.push(circle);
        });
        // Add debounced responsive functionality
        // var rescale = function() { 
        //     infoCircle.each(function(i, e) {
        //         var getWidth = $(e).width() / 2;
        //         circles[i].updateRadius(
        //             getWidth);
        //     });
        //     setTimeout(function() {
        //         // Add responsive font sizing functionality
        //         $('.info-circle').find('.circle-text-value').fitText(0.4);
        //     },50);
        // } 
        // var lazyLayout = _.debounce(rescale, 300);
        // $(window).resize(lazyLayout);
      
    }
} // End Circle Graphs Demo

function nuevaFoto() {
  $("#nuevaFoto").show();
  $("#divNuevaFoto").hide();
  $("#divOcultarFoto").show();
}

function ocultarNuevaFoto() {
  $("#nuevaFoto").hide();
  $("#divNuevaFoto").show();
  $("#divOcultarFoto").hide();
}



function nuevaNoconformidad() {
  $("#divNuevaNoconformidad").modal('show');
  enlace.limpiar_conformidad();
  enlace.no_conformidad_titulo('Registro de No conformidad - Estructura '+enlace.noconformidadNodoVO.estructura());
}


