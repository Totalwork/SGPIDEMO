
var mensajeAlerta= '<div class="alert alert-warning alert-dismissable"><i class="fa fa-info pr10"></i> Se ha encontrado diferencias entre las Cant. UUCC del presupuesto y la programación. </div>';
function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
    self.listado_detalles=ko.observableArray([]);

	self.mensaje=ko.observable('');
    self.mensaje_detalles=ko.observable('');
    
	self.titulo=ko.observable('');
    self.titulo2=ko.observable('');
	self.filtro=ko.observable('');
    self.filtro_detalles=ko.observable('');
    
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   

    self.id_capitulo=ko.observable(0);
    self.id_actividad=ko.observable(0);
    self.listado_actividades=ko.observableArray([]);
    self.listado_actividades_detalles=ko.observableArray([]);
    
    self.archivo_carga=ko.observable('');
    self.cierre_programacion=ko.observable(0);
    self.confirmarFechas=ko.observable(0);

    self.cronogramaVO = {
        id_cronograma: ko.observable($('#cronograma_id').val()),
        fechaFinal:ko.observable('').extend({ required: { message: 'Ingrese una fecha de inicio' } }),
        fechaInicio:ko.observable('').extend({ required: { message: 'Ingrese una fecha final' } }),
        periodicidad_id:ko.observable('').extend({ required: { message: 'Seleccionar periodicidad' } }),
    }

    self.diagramaVO={
        id:ko.observable(0),
        fechaDesde:ko.observable('').extend({ required: { message: '(*)Digite la fecha de inicio' } }),
        fechaHasta:ko.observable('').extend({ required: { message: '(*)Digite la fecha de final' } }),        
        cronograma_id:ko.observable($('#cronograma_id').val())
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

    self.habilitar_detalles = ko.observable(false);


    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar');
        $('#modal_acciones').modal('show');
    }

    self.abrir_carga_masiva = function () {
        self.limpiar();
        self.titulo('Carga masiva de cantidades de Programación');
        $('#modal_acciones_carga_masiva').modal('show');
    }
     

    self.descargar_plantilla=function(){

        if ($('#cmbPresupuesto').val()==0){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un presupuesto.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{
            $.confirm({
                title:'Informativo',
                // content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Las columnas de la "A" a la "G" son de caracter informativo, las cuales no se deben modificar. <br> Tambien puede encontrar filas de color gris, unicamente sirve para ubicar el Hito principal<h4>',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>En la planilla en Excel solo debe ingresar las cantidades de las UUCC en los respectivos periodos y verificar que el "% Cant. Reportada" es igual a 100% para cada UUCC<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            setTimeout(function(){ location.href=path_principal+"/avanceObraLite/descargar-plantilla-programacion/?presupuesto_id="+$('#cmbPresupuesto').val()+"&cronograma_id="+$('#id_cronograma').val(); }, 1000);
            
        }
        
    }


    self.guardar_carga_masiva=function(){

         if((self.archivo_carga()=='') || ($('#cmbPresupuesto').val()==0)){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar la programación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('presupuesto_id',$('#cmbPresupuesto').val());
            data.append('cronograma_id',$('#id_cronograma').val());
            data.append('esquema_id',$('#id_esquema').val());
            data.append('archivo',self.archivo_carga());

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        //if (estado=='ok') {
                        self.consultar_por_id_cronograma();
                        self.cargar_detalles(1);
                        self.cargar(1);
                        //}

                        $('#modal_acciones_carga_masiva').modal('hide');
                        $('#archivo').fileinput('reset');
                        $('#archivo').val('');
                        self.archivo_carga('');

                        setTimeout(function(){ cambiar_a_pestana(); }, 1000);
                         
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraLite/guardar-programacion-archivo/',//url api
                     parametros:data,
                     alerta: true                 
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
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


    self.limpiar=function(){
        self.diagramaVO.id(0);
        self.diagramaVO.fechaDesde('');
        self.diagramaVO.fechaHasta('');

        self.diagramaVO.fechaDesde.isModified(false);
        self.diagramaVO.fechaHasta.isModified(false);
       
    }


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_avance",self.filtro() || '');

            self.cargar(pagina);

        }


    }


    self.cargar =function(pagina){           
        
            if($('#programacion_cierre').val()=='True'){
                self.cierre_programacion(1);
            }
            if($('#confirmarFechas').val()=='True'){
                self.confirmarFechas(1);
            }
            let filtro_avance=sessionStorage.getItem("filtro_avance");

            path = path_principal+'/api/avanceObraLitePeriodoProgramacion/?format=json&page='+pagina;
            parameter = {dato: filtro_avance, page: pagina,cronograma_id:$('#cronograma_id').val()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));
                     $('#modal_acciones').modal('hide');

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

    self.busquedaVO={
        hito_id:ko.observable(''),
        actividad_id:ko.observable('')
    };

    self.paginacion_detalles = {
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

    self.llenar_paginacion_detalles = function (data,pagina) {

        self.paginacion_detalles.pagina_actual(pagina);
        self.paginacion_detalles.total(data.count);       
        self.paginacion_detalles.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion_detalles.totalRegistrosBuscados(buscados);

    }


    self.paginacion_detalles.pagina_actual.subscribe(function (pagina) {
        self.consultar_detalles(pagina);
    });

    self.abrir_modal_filter = function () {
        self.titulo('Filtro');
        $('#modal_filtro').modal('show');
    }

    self.filtrar=function(){
       self.consultar_detalles(1);
        $('#modal_filtro').modal('hide');
    }

    self.busquedaVO.hito_id.subscribe(function(value ){

             if(value!=0){
                path = path_principal+'/api/avanceObraLiteEsquemaCapitulosActividades/?sin_paginacion';
                parameter = {padre_id:value};
                RequestGet(function (datos, estado, mensage) {

                    self.listado_actividades_detalles(datos);
                }, path, parameter,function(){
                    // self.disenoVO.municipio_id(0);
                    // self.disenoVO.municipio_id(self.municipio());
                }
                );
            }else{
                self.listado_actividades_detalles([]);
                self.busquedaVO.actividad_id('')
            }
    });


    self.consultar_detalles = function (pagina) {
        if (pagina > 0) {            

            self.filtro_detalles($('#txtBuscar_detalles').val());
            sessionStorage.setItem("filtro_avance_detalle_diagrama",self.filtro_detalles() || '');
            self.cargar_detalles(pagina);
        }
    }

    self.cargar_detalles=function(pagina){ 

        let filtro_avance_detalle=sessionStorage.getItem("filtro_avance_detalle_diagrama");

        path = path_principal+'/api/avanceObraLiteDetallePresupuesto/?format=json&page='+pagina;
        parameter = {
            dato: filtro_avance_detalle,
            cronograma_id: $('#cronograma_id').val(),
            hito_id:self.busquedaVO.hito_id(),
            actividad_id:self.busquedaVO.actividad_id(),
            lite3:1};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.datos.length > 0) {
                self.mensaje_detalles('');
                //self.listado(results); 
                self.listado_detalles(agregarOpcionesObservable(self.llenar_datos(datos.data.datos)));
                self.cant_inferiores(datos.data.cant_inferior);
                self.cant_superiores(datos.data.cant_superior);

                if(self.cant_inferiores()>0 || self.cant_superiores()>0){
                    self.mensaje_detalles(mensajeAlerta);
                }

                $('#modal_filtro').modal('hide');

            } else {
                self.listado_detalles([]);
                self.mensaje_detalles(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }

            
            self.llenar_paginacion_detalles(datos,pagina);
            //}
            cerrarLoading();
        }, path, parameter,undefined, false);
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            //self.limpiar();
            self.consultar(1);
        }
        return true;
    }


    self.id_capitulo.subscribe(function (value) {
            
             if(value!=0){
                path = path_principal+'/api/avanceObraLiteEsquemaCapitulosActividades/?sin_paginacion';
                parameter = {padre_id:value};
                RequestGet(function (datos, estado, mensage) {

                    self.listado_actividades(datos);
                }, path, parameter,function(){
                    self.diagramaVO.actividad_id(self.id_actividad());
                    // self.disenoVO.municipio_id(self.municipio());
                }
                );
            }else{
                self.listado_actividades([]);
            }

    });



    self.guardar=function(){

        if (IndexViewModel.errores_diagrama().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.diagramaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            //self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceObraLitePeriodoProgramacion/',//url api
                     parametros:self.diagramaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{

                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                          self.limpiar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/avanceObraLitePeriodoProgramacion/'+self.diagramaVO.id()+'/',
                       parametros:self.diagramaVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             IndexViewModel.errores_diagrama.showAllMessages();//mostramos las validacion
        }

    }

     self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });


     self.eliminar=function(){

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una actividad para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraLite/eliminar_diagrama/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las actividades del diagrama seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }  

    }

    self.guardar_cantidad=function(){        
        
        var path =path_principal+'/avanceObraLite/actualizar_cantidad/';
        var parameter = { lista: self.listado_cantidad()};
        RequestAnularOEliminar("Esta seguro que desea actualizar las cantidades del presupuesto?", path, parameter, function () {
             self.cargar_detalles(1);
        })

    }
    self.listado_cantidad=function(){
        var lista=[];
        ko.utils.arrayForEach(self.listado_detalles(), function(obj) {
            if(obj.cantidad()==''){
                obj.cantidad(0);
            }
            lista.push({
                id:obj.id(),
                cantidad:obj.cantidad()
            });
        });

        return lista;
    }

    self.llenar_datos=function(data){
         var lista=[];
         sw=true;
         //alert(self.cerrado_presupuesto())
         if(self.cierre_programacion()==true || self.cierre_programacion()=='True'){
            sw=false;
         }
         
          ko.utils.arrayForEach(data, function(obj) {                    
                    lista.push({
                        id:ko.observable(obj.id),
                        nombre_padre:ko.observable(obj.nombre_padre),
                        actividad_nombre:ko.observable(obj.actividad.nombre),
                        codigoUC:ko.observable(obj.codigoUC),
                        descripcionUC:ko.observable(obj.descripcionUC),
                        valorUC:ko.observable(obj.valorGlobal),
                        cantidad:ko.observable(obj.cantidad),
                        cantidad_programada:ko.observable(obj.cantidad_programada),
                        habilitar:ko.observable(sw)
                    });
                    
             });
        return lista;
    }

     self.cerrar_programacion=function(){

            $.confirm({
                title: 'Cerrar Programacion!',
                content: "<h4>Esta seguro que desea cerrar la programacion? una vez cerrada no podrá modificar la programación de este cronograma.</h4>",
                confirmButton: 'Si',
                confirmButtonClass: 'btn-info',
                cancelButtonClass: 'btn-danger',
                cancelButton: 'No',
                confirm: function() {
                        self.cronogramaVO.id_cronograma($('#cronograma_id').val());
                        var parametros={     
                        metodo:'POST',                
                        callback:function(datos, estado, mensaje){

                                if (estado=='ok') {
                                    self.cierre_programacion(1);
                                    self.cargar_detalles(1);
                                }                        
                                
                             },//funcion para recibir la respuesta 
                             url:path_principal+'/avanceObraLite/cierre_programacion/',//url api
                             parametros:{ id_cronograma: $('#cronograma_id').val() }
                             //parametros: self.cronogramaVO
                          };
                        Request(parametros);
                    
                }
            });

    }

    self.reformar_uucc = function(obj){

    }

     self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
        path =path_principal+'/api/avanceObraLitePeriodoProgramacion/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
           
             self.titulo('Actualizar Periodo/Semana');

             self.diagramaVO.id(results.id);
             self.diagramaVO.fechaDesde(results.fechaDesde);
             self.diagramaVO.fechaHasta(results.fechaHasta);
             self.diagramaVO.cronograma_id(results.cronograma.id);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }



   self.exportar_excel=function(){

        location.href=path_principal+"/avanceObraLite/informe_diagrama/?cronograma_id="+$('#cronograma_id').val();

   }

   


   self.abrir_editar_fechas=function(){
    // self.consultar_por_id_cronograma();
    self.titulo('Modificar periodo principal');
    self.consultar_por_id_cronograma();    
    $('#modal_moficiar_periodo').modal('show');
   }

   self.consultar_por_id_cronograma=function(){
       path =path_principal+'/api/avanceObraLiteCronograma/'+self.cronogramaVO.id_cronograma()+'/?lite=True&format=json';
        RequestGet(function (results,count) {               
            self.habilitar_detalles(results.detalles_cargados);
            $('#fechas_cronograma').text(results.fechaInicio+' - '+results.fechaFinal)
            self.cronogramaVO.periodicidad_id(results.periodicidad.id);
            self.cronogramaVO.fechaInicio(results.fechaInicio);
            self.cronogramaVO.fechaFinal(results.fechaFinal);
            self.cronogramaVO.periodicidad_id.isModified(false);
            self.cronogramaVO.fechaInicio.isModified(false);
            self.cronogramaVO.fechaFinal.isModified(false);

        }, path, parameter);
       
    }


   self.guardar_fechas_principales=function(){
        if (IndexViewModel.errores_cronograma().length == 0) {//se activa las validaciones
            if(self.cronogramaVO.id_cronograma()>0){                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                          self.consultar_por_id_cronograma();
                          self.consultar(1);
                          $('#modal_moficiar_periodo').modal('hide');
                        }
                       },//funcion para recibir la respuesta 
                       url:path_principal+'/avanceObraLite/ActualizarPeriodoPrincipal/',
                       parametros:self.cronogramaVO                        
                  };
                  RequestFormData(parametros);
            }
        } else {
             IndexViewModel.errores_cronograma.showAllMessages();//mostramos las validacion
        }
   }


   self.confirmar_fechas=function(){
        $.confirm({
                title: 'Confirmar programación!',
                content: "<h4>Esta seguro que desea confirmar las fechas de la programación? <br> Una vez confirmado no podrá modificar la programación de este cronograma.</h4>",
                confirmButton: 'Si',
                confirmButtonClass: 'btn-info',
                cancelButtonClass: 'btn-danger',
                cancelButton: 'No',
                confirm: function() {
                        self.cronogramaVO.id_cronograma($('#cronograma_id').val());
                        var parametros={     
                        metodo:'POST',                
                        callback:function(datos, estado, mensaje){

                                if (estado=='ok') {
                                    self.confirmarFechas(1);
                                    self.consultar_por_id_cronograma();
                                    self.consultar(1);
                                    
                                }                        
                                
                             },//funcion para recibir la respuesta 
                             url:path_principal+'/avanceObraLite/confirmar_fechas/',//url api
                             parametros:{ id_cronograma: $('#cronograma_id').val() }
                             //parametros: self.cronogramaVO
                          };
                        Request(parametros);
                    
                }
        });
   }

    self.DetallesPeriodoVO={
        id: ko.observable(0),        
        detallePresupuesto_id: ko.observable('').extend({ required: { message: '(*)Seleccione un registro' } }),
        periodoProgramacion_id: ko.observable(''),
        cantidad: ko.observable('').extend({ required: { message: '(*)Ingrese la cantidad' } }),
    }
    self.mensaje_detalles_periodo= ko.observable('');
    self.listado_uucc_disponibles=ko.observable([]);
    self.listado_detalles_periodo=ko.observable([]);

    self.cant_superiores= ko.observable(0);
    self.cant_inferiores= ko.observable(0);

    self.actividad_id = ko.observable('');

    self.actividad_id.subscribe(function(value){
        if(value!=""){
            self.consultar_uucc_disponibles(value); 
        }else{
            self.listado_uucc_disponibles([]);
        }
        
    });
    

   self.limpiar_detalles_periodo=function(){
        self.DetallesPeriodoVO.id('');       
        self.DetallesPeriodoVO.detallePresupuesto_id('');
        // self.DetallesPeriodoVO.periodoProgramacion_id('');
        self.DetallesPeriodoVO.cantidad('');
               
        self.DetallesPeriodoVO.detallePresupuesto_id.isModified(false);
        self.DetallesPeriodoVO.cantidad.isModified(false);
   }



    self.guardar_actividad=function(){
        if (IndexViewModel.errores_actividad().length == 0 && IndexViewModel.errores_actividad().length == 0 ) {
            if(self.DetallesPeriodoVO.id()==0){

                var parametros={
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.cargar_por_detalles(self.DetallesPeriodoVO.periodoProgramacion_id());
                            self.cargar(1);
                            self.cargar_detalles(1);
                            ocultarNuevoRegistro();  
                        }

                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/avanceObraLiteDetallePeriodoProgramacion/',//url api
                    parametros:self.DetallesPeriodoVO,                     
                };
                RequestFormData(parametros);
            }else{
                var parametros={
                    metodo:'PUT',
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {                             
                            self.cargar_por_detalles(self.DetallesPeriodoVO.periodoProgramacion_id());
                            self.cargar(1);
                            self.cargar_detalles(1);
                            ocultarNuevoRegistro(); 
                        }

                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/avanceObraLiteDetallePeriodoProgramacion/'+self.DetallesPeriodoVO.id()+'/',//url api
                    parametros:self.DetallesPeriodoVO,                 
                };
                RequestFormData(parametros);
            }
        }else {
            if (IndexViewModel.errores_actividad().length > 0 ) {
                IndexViewModel.errores_actividad.showAllMessages();
            }           
        }
    }


    self.abrir_edicion_detalles_periodo=function(obj){
        nuevaRegistro();

        self.DetallesPeriodoVO.id(obj.id);
        self.DetallesPeriodoVO.detallePresupuesto_id(obj.detallePresupuesto.id);
        self.DetallesPeriodoVO.periodoProgramacion_id(obj.periodoProgramacion.id);
        self.DetallesPeriodoVO.cantidad(obj.cantidad);
        $('#nombre_actividad').val(obj.detallePresupuesto.descripcionUC);
        self.titulo2('Edición')
        
        $('#modal_list_actividades').animate({
            scrollTop: '0px'
        }, 300)
        cerrarLoading();
    }


    self.eliminar_detalles_periodo=function(obj){
        var path =path_principal+'/api/avanceObraLiteDetallePeriodoProgramacion/'+obj.id+'/';
        var parameter = {metodo:'DELETE'};
        RequestAnularOEliminar("Esta seguro que desea eliminar el registro?", path, parameter, 
            function(datos, estado, mensaje){
                if (estado=='ok') { 
                    self.cargar_por_detalles(obj.periodoProgramacion.id);
                    self.cargar(1);
                    self.cargar_detalles(1);
                }        
        });
    }




   self.consultar_por_detalles=function(obj){
        self.limpiar_detalles_periodo(); 
        self.titulo('Cantidades del periodo: ('+obj.fechaDesde+' - '+obj.fechaHasta+')');
        self.DetallesPeriodoVO.periodoProgramacion_id(obj.id);
        
        self.cargar_por_detalles(obj.id)
       
    }

    self.cargar_por_detalles=function(id){
        path = path_principal+'/api/avanceObraLiteDetallePeriodoProgramacion/?format=json';
        parameter = {
            periodoProgramacion_id: id,            
            sin_paginacion: true,

        };
        RequestGet(function (datos, estado, mensage) {

            if (estado=='ok' && datos!=null && datos.length > 0) {
                //alert('3');               
                self.mensaje_detalles_periodo('');                
                self.listado_detalles_periodo(datos); 
                ocultarNuevoRegistro();
                //                
            }else{
                //alert('4');                
                self.mensaje_detalles_periodo(mensajeNoFound);
                self.listado_detalles_periodo([]);
            }

            $('#modal_detalles_periodo').modal('show');
            cerrarLoading();
        }, path, parameter, undefined, false, false);
    }

    self.consultar_uucc_disponibles=function(actividad_id){
        path = path_principal+'/api/avanceObraLiteDetallePresupuesto/?format=json';
        parameter = {
            cronograma_id: $('#cronograma_id').val(),
            actividad_id: actividad_id,
            periodoProgramacion_id: self.DetallesPeriodoVO.periodoProgramacion_id(),
            lite3: true,
            sin_paginacion:true,

        };
        RequestGet(function (datos, estado, mensage) {

            if (estado=='ok' && datos!=null && datos.length > 0) {
                //alert('3');               
                // self.mensaje('');
                self.listado_uucc_disponibles(datos);
                // self.limpiar_detalles_periodo();
            }else{
                //alert('4');                
                // self.mensaje(mensajeNoFound);
                self.listado_uucc_disponibles([]);
            }
            cerrarLoading();
        }, path, parameter, undefined, false, false);
    }

    self.DetallesPeriodo2VO={
        id: ko.observable(0),        
        detallePresupuesto_id: ko.observable(''),
        periodoProgramacion_id: ko.observable('').extend({ required: { message: '(*)Seleccione un registro' } }),
        cantidad: ko.observable('').extend({ required: { message: '(*)Ingrese la cantidad' } }),
    }

    self.listado_periodos_disponibles=ko.observable([]);
    self.listado_reformado=ko.observable([]);
    self.mensaje_reformado=ko.observable('');

    self.guardar_reformado=function(){
        if (IndexViewModel.errores_reformado().length == 0 && IndexViewModel.errores_reformado().length == 0 ) {
            if(self.DetallesPeriodo2VO.id()==0){

                var parametros={
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.cargar_reformados(self.DetallesPeriodo2VO.detallePresupuesto_id());
                            self.cargar_detalles(1);
                            self.cargar(1)
                            ocultarNuevoRegistro_reformado();  
                        }

                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/avanceObraLiteDetallePeriodoProgramacion/',//url api
                    parametros:self.DetallesPeriodo2VO,                     
                };
                RequestFormData(parametros);
            }else{
                var parametros={
                    metodo:'PUT',
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {                             
                            self.cargar_reformados(self.DetallesPeriodo2VO.detallePresupuesto_id());
                            self.cargar_detalles(1);
                            ocultarNuevoRegistro_reformado(); 
                        }

                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/avanceObraLiteDetallePeriodoProgramacion/'+self.DetallesPeriodo2VO.id()+'/',//url api
                    parametros:self.DetallesPeriodo2VO,                 
                };
                RequestFormData(parametros);
            }
        }else {
            if (IndexViewModel.errores_reformado().length > 0 ) {
                IndexViewModel.errores_reformado.showAllMessages();
            }           
        }
    }

    self.limpiar_detalles_periodo_reformado=function(){
        self.DetallesPeriodo2VO.id('');       
        self.DetallesPeriodo2VO.periodoProgramacion_id('');
        self.DetallesPeriodo2VO.cantidad('');
               
        self.DetallesPeriodo2VO.periodoProgramacion_id.isModified(false);
        self.DetallesPeriodo2VO.cantidad.isModified(false);
   }
    self.reformar_uucc=function(obj){
        self.limpiar_detalles_periodo_reformado(); 
        self.titulo('Detalles de la UUCC : ('+obj.descripcionUC()+')');
        self.DetallesPeriodo2VO.detallePresupuesto_id(obj.id);
        self.cargar_reformados(obj.id)
       
    }

    self.abrir_edicion_reformado_periodo=function(obj){
        nuevaRegistro_reformado();

        self.DetallesPeriodo2VO.id(obj.id);
        self.DetallesPeriodo2VO.detallePresupuesto_id(obj.detallePresupuesto.id);
        self.DetallesPeriodo2VO.periodoProgramacion_id(obj.periodoProgramacion.id);
        self.DetallesPeriodo2VO.cantidad(obj.cantidad);
        $('#nombre_actividad').val(obj.periodoProgramacion.fechaDesde+' - '+obj.periodoProgramacion.fechaHasta);
        self.titulo2('Edición')
        
        $('#modal_list_actividades').animate({
            scrollTop: '0px'
        }, 300)
        cerrarLoading();
    }

    self.eliminar_reformado_periodo=function(obj){
        var path =path_principal+'/api/avanceObraLiteDetallePeriodoProgramacion/'+obj.id+'/';
        var parameter = {metodo:'DELETE'};
        RequestAnularOEliminar("Esta seguro que desea eliminar el registro?", path, parameter, 
            function(datos, estado, mensaje){
                if (estado=='ok') { 
                    self.cargar_reformados(obj.detallePresupuesto.id);
                    self.cargar_detalles(1);
                    self.cargar(1);
                }        
        });
    }

    self.cargar_reformados =function(id){ 
        path = path_principal+'/api/avanceObraLiteDetallePeriodoProgramacion/?format=json';
        parameter = {
            detallePresupuesto_id: id,            
            sin_paginacion: true,

        };
        RequestGet(function (datos, estado, mensage) {

            if (estado=='ok' && datos!=null && datos.length > 0) {
                //alert('3');               
                self.mensaje_reformado('');
                self.listado_reformado(datos);          
                ocultarNuevoRegistro();
                //                
            }else{
                //alert('4');                
                self.mensaje_reformado(mensajeNoFound);
                self.listado_reformado([]);
            }

            $('#modal_reformado').modal('show');
            cerrarLoading();
        }, path, parameter, undefined, false, false);
    }

    self.consultar_periodos_disponibles=function(){
        path = path_principal+'/api/avanceObraLitePeriodoProgramacion/?format=json';
        parameter = {
            detallePresupuesto_id: self.DetallesPeriodo2VO.detallePresupuesto_id(),
            lite: true,
            ignorePagination:true,

        };
        RequestGet(function (datos, estado, mensage) {

            if (estado=='ok' && datos!=null && datos.length > 0) {
                //alert('3');               
                // self.mensaje('');
                self.listado_periodos_disponibles(datos);
                // self.limpiar_detalles_periodo();
            }else{
                //alert('4');                
                // self.mensaje(mensajeNoFound);
                self.listado_periodos_disponibles([]);
            }
            cerrarLoading();
        }, path, parameter, undefined, false, false);
    }


 }



var index = new IndexViewModel();
IndexViewModel.errores_diagrama = ko.validation.group(index.diagramaVO);
IndexViewModel.errores_cronograma = ko.validation.group(index.cronogramaVO);
IndexViewModel.errores_actividad = ko.validation.group(index.DetallesPeriodoVO);
IndexViewModel.errores_reformado = ko.validation.group(index.DetallesPeriodo2VO);

$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
$('#txtBuscar_detalles').val(sessionStorage.getItem("filtro_avance_detalle_diagrama"));
index.cargar(1);//iniciamos la primera funcion
index.cargar_detalles(1);
index.consultar_por_id_cronograma();
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);



function cambiar_a_pestana() {
    
  $('#tab_div_1').prop('class', 'tab-pane');
  $('#tab_div_2').prop('class', 'tab-pane active');

  $('#tab_li_1').prop('class', '');
  $('#tab_li_2').prop('class', 'active');

  $('#tab_a_1').prop("aria-expanded", "false");
  $('#tab_a_2').prop("aria-expanded", "true");
    

}


function nuevaRegistro() {
    index.limpiar_detalles_periodo();
    index.listado_uucc_disponibles([]);
    $("#nuevoRegistro").show();

    $("#divNuevoRegistro").hide();
    $("#divOcultarRegistro").show();

    
    index.titulo2('Registro')
}

function ocultarNuevoRegistro() {
    index.limpiar_detalles_periodo();
    $("#nuevoRegistro").hide();

    $("#divNuevoRegistro").show();
    $("#divOcultarRegistro").hide();
}


function nuevaRegistro_reformado() {
    index.limpiar_detalles_periodo_reformado();
    index.consultar_periodos_disponibles();
    $("#nuevoRegistro_reformado").show();

    $("#divNuevoRegistro_reformado").hide();
    $("#divOcultarRegistro_reformado").show();

    
    index.titulo2('Registro')
}

function ocultarNuevoRegistro_reformado() {
    index.limpiar_detalles_periodo_reformado();
    $("#nuevoRegistro_reformado").hide();

    $("#divNuevoRegistro_reformado").show();
    $("#divOcultarRegistro_reformado").hide();
}