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

  self.archivo_carga=ko.observable('');
  self.checkall=ko.observable(false);

  self.habilitar_cambio=ko.observable(false);
  self.id_nodo=ko.observable(0);
  self.porcentaje_total=ko.observable(0);
  self.id_cambio=ko.observable(0);
  self.nombre_cambio=ko.observable('');

  self.cambio_crea=ko.observable(false);
  self.cambio_eliminar=ko.observable(false);
  self.cambio_modificar=ko.observable(false);

  self.listado_actividades=ko.observableArray([]);
  self.listado_actividades_modificacion=ko.observableArray([]);

  self.listado_cambios=ko.observableArray([]);

  self.listado_id_nodos_eliminar=ko.observableArray([]);

  self.listado_detalles=ko.observableArray([]);

  self.id_estado_busqueda=ko.observable('');
  self.filtro_ejecutado=ko.observable(0);


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

    //funcion consultar todos los enlaces


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
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

     self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    self.abrir_modal_detalle_cambio = function (obj) {
      self.titulo('Detalles Cambio');
      self.consultar_detalle_cambio(obj.id);
        
    }


    self.consultar_detalle_cambio=function(id){

        path = path_principal+'/api/avanceObraGraficoEjecucionProgramada/?sin_paginacion';
        parameter = {cronograma_id:$('#id_cronograma').val(),nodo_id:id};
        RequestGet(function (datos, estado, mensage) {

             
              self.listado_cambios(datos);
              
              $('#modal_detalle_cambio').modal('show');
              cerrarLoading();
        }, path, parameter);
    }
    
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Apoyo');
        $('#modal_acciones').modal('show');
        
    }


     self.abrir_modal_carga = function (obj) {
       self.limpiar();
        self.titulo('Registros de Apoyo');
        self.consultar_apoyo(obj.id);
       
        
    }


    self.consultar_apoyo=function(id){
        self.id_nodo(id);
        path = path_principal+'/api/avanceObraGraficoLinea/?sin_paginacion';
        parameter = {nodo_id:id,tipo_linea:2,sin_cantidad:0,cronograma_id:$('#id_cronograma').val()};
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

                  var valor=parseFloat(d.cantidad_ejecutadas)/ parseFloat(d.cantidadesNodo.cantidad)
                  total=total+valor;
                  cant=cant+1;

                  lista.push({
                        id:ko.observable(d.id),
                        codigoUC:ko.observable(d.cantidadesNodo.detallepresupuesto.codigoUC),
                        descripcionUC:ko.observable(d.cantidadesNodo.detallepresupuesto.descripcionUC),
                        cantidad_ejecutada:ko.observable(d.cantidadesNodo.cantidad),
                        fecha_programada:ko.observable(d.fecha),
                        cantidad_sumada:ko.observable(d.cantidad_ejecutadas),
                        fecha:ko.observable(''),
                        cantidad:ko.observable(0),
                        notas:ko.observable('')
                  })
        }); 

        total_por=(total/cant)*100
        if(total_por>100){
          total_por=100;
        }

        self.porcentaje_total(total_por.toFixed(2));

        


        return lista;

    }

     self.guardar_cambio_cantidades=function(){

      var lista=[];
      ko.utils.arrayForEach(self.listado_detalles(), function(d) {
            if(d.cantidad()>0 && d.fecha()!='' && d.cantidad()!=''){

                lista.push({
                   programacion_id:d.id,
                   cantidad:d.cantidad,
                   fecha:d.fecha,
                   observacion:d.notas
                })

            }
      });

              var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_listado').modal('hide');
                            self.id_nodo(0);
                            self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/guardar_cambio_cantidades/',//url api
                     parametros:{lista:lista,id_nodo:self.id_nodo(),id_cronograma:$('#id_cronograma').val()}                     
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
    }

     self.abrir_modal_modificar_datos = function (obj) {
      self.titulo('Modificar Datos');
      self.id_nodo(obj.id);
      self.consultar_modificacion_actividades();
        
    }


    self.abrir_modal_cambio = function () {
      self.titulo('Registrar Cambio');
      $('#modal_cambios').modal('show');
        
    }

    self.limpiar=function(){
        //self.apoyoVO.nombre('');
    }

    self.consultar=function(pagina){

        self.filtro($('#txtBuscar').val());
        sessionStorage.setItem("filtro_avance",self.filtro() || '');

        self.cargar(pagina);

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
                            self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/guardar_modificacion/',//url api
                     parametros:{id_cambio:self.id_cambio(),id_nodo:self.id_nodo(),lista:listado}
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

    }

     self.guardar_detalle_cambio=function(){


      var listado=[];
      ko.utils.arrayForEach(self.listado_cambios(), function(d) {

                  if(d.cantidadEjecutada>0 && d.cantidadEjecutada!=''){
                        listado.push({
                            id:d.id,
                            cantidad:d.cantidadEjecutada,
                            fecha:d.fecha,
                            observacion:d.observacion
                      })
                  }

                  
        }); 

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {

                            $('#modal_detalle_cambio').modal('hide');
                             self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/guardar_cambio_detalle/',//url api
                     parametros:{lista:listado}
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

  }



    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            //self.limpiar();
            self.consultar(1);
        }
        return true;
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

    self.eliminar_punto=function(ob){
        valor=ob.id;

        self.listado_id_nodos_eliminar.push({
                id:valor
        });
        ko.utils.arrayForEach(self.listado(), function(obj) {
                        
                        if(obj!=undefined){

                            if(obj.id==valor){
                                self.listado.remove(obj);
                                valor=0;
                                return true;
                            }

                        }
                }); 
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

  self.guardar_nuevas_cantidades=function(){

          var listado_id=[];         
          ko.utils.arrayForEach(self.listado_actividades(), function(obj) {

                   listado_id.push({
                            id:obj.id(),
                            cantidad:obj.cantidad(),
                            fecha:obj.fecha()
                    });
                          
                         
          }); 
      
          var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.listado_actividades([]);
                          self.id_nodo(0);
                          $('#modal_cantidad_nueva').modal('hide');
                           self.consultar(1);

                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/guardar_nuevas_cantidades/',//url api
                     parametros:{lista:listado_id,id_nodo:self.id_nodo(),id_cronograma:$('#id_cronograma').val()}
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
  }

   self.guardar_nodo=function(latLng){

      if (EnlaceViewModel.errores_apoyo().length == 0) {//se activa las validaciones

       
           // self.contratistaVO.logo($('#archivo')[0].files[0]);            
                self.nodoVO.id_cambio(self.id_cambio());
                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                            self.id_nodo(datos[0].id);
                            self.listado.push({
                                  id:datos[0].id,
                                  nombre:datos[0].nombre,
                                  longitud:datos[0].longitud,
                                  latitud:datos[0].latitud
                            });
                            self.consultar_actividades();
                            self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/guardar_nodos_nuevos/',//url api
                     parametros:self.nodoVO,
                     alerta:false                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
        } else {
             EnlaceViewModel.errores_apoyo.showAllMessages();//mostramos las validacion
        }
  }

    self.cargar = function (pagina) {

            programado='';
            if(self.cambio_crea()==false){
                programado=0;
            }else{
              programado=1;
            }

            if(self.id_estado_busqueda()==''){
                  self.id_estado_busqueda('2,3');
            }

            let filtro_avance=sessionStorage.getItem("filtro_avance");
            path = path_principal+'/api/avanceObraGraficoNodo/?format=json';
            parameter = {ejecucion:self.filtro_ejecutado(),cronograma_id:$('#id_cronograma').val(),
            id_estados:self.id_estado_busqueda(),programando:programado,apoyo_cambio:0,
            presupuesto_id:$('#id_presupuesto').val(),dato: filtro_avance};
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
                cerrarLoading();
            }, path, parameter,undefined, false);
        }


    



  self.guardar=function(){


      if (EnlaceViewModel.errores_apoyo().length == 0) {//se activa las validaciones

          if(self.apoyoVO.id()==0){


           // self.contratistaVO.logo($('#archivo')[0].files[0]);            
            self.apoyoVO.capa_id($('#id_capa_manual').val());
                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                            self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceObraGraficoNodo/',//url api
                     parametros:self.apoyoVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

          }else{
              var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                           $('#modal_acciones').modal('hide');
                            self.limpiar();
                            self.consultar(1);
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/avanceObraGraficoNodo/'+self.apoyoVO.id()+'/',
                       parametros:self.apoyoVO        
                  };

                  Request(parametros);
          }

        } else {
             EnlaceViewModel.errores_apoyo.showAllMessages();//mostramos las validacion
        }
  }


 self.guardar_cambio=function(){


         if (EnlaceViewModel.errores_cambio().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);            
           var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            if(self.cambioCronogramaVO.tipo_accion_id()==1){
                              self.cambio_crea(true);
                            }else if(self.cambioCronogramaVO.tipo_accion_id()==2){
                              self.cambio_eliminar(true);
                            }
                            else if(self.cambioCronogramaVO.tipo_accion_id()==3){
                              self.cambio_modificar(true);
                            }
                            $('#modal_cambios').modal('hide');
                            self.id_cambio(datos.id);
                            self.nombre_cambio(datos.nombre);
                            self.habilitar_cambio(true);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceObraGraficoCambio/',//url api
                     parametros:self.cambioCronogramaVO,
                     alerta:false                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
        } else {
             EnlaceViewModel.errores_cambio.showAllMessages();//mostramos las validacion
        }


  }

  self.guardar_datos=function(){

         if(self.archivo_carga()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar el presupuesto.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('presupuesto_id',$('#id_presupuesto').val());
            data.append('capa_id',$('#id_capa_archivo').val());
            data.append('archivo',self.archivo_carga());

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar(1);
                            $('#modal_cargar').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/guardar_apoyo_archivo_sinposicion/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }
  }


  self.abrir_grafico=function(){

             location.href=path_principal+"/avanceObraGrafico/grafico/"+$('#id_presupuesto').val()+"/"+$('#id_proyecto').val()+"/"+$('#id_cronograma').val()+"/";

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
                          self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/eliminar_cambio/',//url api
                     parametros:{id_nodo:self.id_cambio(),tipo_accion:self.cambioCronogramaVO.tipo_accion_id()},
                     alerta:false                   
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);



  }


    self.guardar_cambio_final=function(){

      if(self.cambioCronogramaVO.tipo_accion_id()==2){
                
                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.listado_id_nodos_eliminar([]);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/guardar_nodo_eliminacion/',//url api
                     parametros:{lista:self.listado_id_nodos_eliminar(),id_cambio:self.id_cambio()},
                     alerta:false                   
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
      }
      self.habilitar_cambio(false);
      self.cambio_crea(false);
      self.cambio_eliminar(false);
      self.cambio_modificar(false);
      self.id_cambio(0);
      self.nombre_cambio('');
      self.id_nodo(0);
      self.consultar(1);
       $.confirm({
        title: 'Confirmación',
        content: '<h4><i class="text-success fa fa-check-circle-o fa-2x"></i> El registro ha sido guardando exitosamente<h4>',
        cancelButton: 'Cerrar',
        confirmButton: false
    });

  }

 

}

var enlace = new EnlaceViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
EnlaceViewModel.errores_apoyo = ko.validation.group(enlace.nodoVO);
EnlaceViewModel.errores_cambio = ko.validation.group(enlace.cambioCronogramaVO);
enlace.cargar(1);
//enlace.consultar_estados();
ko.applyBindings(enlace);

function llamarDetalle(id){
    //Mostrar el popup con las propiedades
    enlace.abrir_modal_carga(id);
}


function detalleDatos(id){
    //Mostrar el popup con las propiedades
   enlace.abrir_modal_detalle_cambio(id);
}




