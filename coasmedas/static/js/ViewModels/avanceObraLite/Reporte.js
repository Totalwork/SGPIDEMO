var mensajeAlerta= '<div class="alert alert-warning alert-dismissable"><i class="fa fa-info pr10"></i> Se ha encontrado diferencias entre las Cant. UUCC a ejecutar y las Cant. UUCC ejecutadas ingresadas.</div>';
function IndexViewModel() {
	
	var self = this;
    self.listado_detalles=ko.observableArray([]);
    self.mensaje_detalles=ko.observable('');

	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   

   self.habilitar_motivo=ko.observable(false);

   self.mensaje_sin_avance=ko.observable('');

   self.mensaje_rechazo=ko.observable('');
   self.listado_rechazo=ko.observableArray([]);
   self.listado_actividades_detalles=ko.observableArray([]);
   self.habilitar_detalles = ko.observable(false);

    self.reporteVO={
        id:ko.observable(0),
        reporteTrabajo_id:ko.observable(),
        cronograma_id:ko.observable($("#cronograma_id").val()),
        fechaReporte:ko.observable('').extend({ required: { message: '(*)Digite la fecha del reporte' } }),
        sinAvance:ko.observable(false),
        motivoSinAvance:ko.observable(''),
        usuario_registro_id:ko.observable($("#usuario_id").val()),
        usuario_aprueba_id:ko.observable(''),       
        reporteCerrado: ko.observable(false),
    };



     self.listado_estado=ko.observableArray([]);
     self.id_estado=ko.observable();


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
        self.titulo('Registrar');
        $('#modal_acciones').modal('show');
    }

    self.abrir_modal_rechazo = function (obj) {
        //self.limpiar();
        self.titulo('Motivo de Rechazo');
        self.consultar_mensaje(obj.id);
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });


    self.consultar_mensaje=function(id){

         path =path_principal+'/api/avanceGrafico2MensajeRechazoReporte/?format=json&sin_paginacion=0';
         parameter={reporte_trabajo_id:id}
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado_rechazo(agregarOpcionesObservable(datos));

                } else {
                    self.listado_rechazo([]);
                    self.mensaje_rechazo(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
           
            $('#modal_rechazo').modal('show');
         }, path, parameter);

    }


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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un reporte para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraLite/eliminar_id_reportetrabajo/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los reportes seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    }


    self.exportar_excel=function(){
        
    }

    // //limpiar el modelo 
     self.limpiar=function(){   
           self.reporteVO.fechaReporte('');
           self.reporteVO.sinAvance(false);
           self.reporteVO.motivoSinAvance('');
           self.habilitar_motivo(false);
           self.reporteVO.usuario_aprueba_id('');

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


            let filtro_avance=sessionStorage.getItem("filtro_avance");

            path = path_principal+'/api/avanceObraLiteReporteTrabajo/?format=json&lite=1&page='+pagina;
            parameter = {
                dato: filtro_avance, 
                pagina: pagina,
                cronograma_id:$("#cronograma_id").val(),
                fechaReporte: self.filtroVO.fechaReporte(), 
                sinAvance: self.filtroVO.sinAvance(), 
                reporteCerrado: self.filtroVO.reporteCerrado(), 
            };
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


    self.reporteVO.sinAvance.subscribe(function (valor) {
        if(valor==true){
            self.habilitar_motivo(true);
        }else{
            self.habilitar_motivo(false);
        }
    });


    self.guardar=function(){

        

        if (IndexViewModel.errores_cronograma().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.reporteVO.id()==0){
                if(self.reporteVO.sinAvance()==true){
                    self.reporteVO.reporteCerrado(true);
                }else{
                    self.reporteVO.reporteCerrado(false);
                }
                
                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceObraLiteReporteTrabajo/',//url api
                     parametros:self.reporteVO                        
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
                       url:path_principal+'/api/avanceObraLiteReporteTrabajo/'+self.reporteVO.id()+'/',
                       parametros:self.reporteVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             IndexViewModel.errores_cronograma.showAllMessages();//mostramos las validacion
        }
    }



    self.abrir_avance_con_gps=function(obj){

        if(self.habilitar_motivo()==true){
               $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>En este reporte de trabajo no hay avance.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{

            path =path_principal+"/avanceObraLite/menu_gps/"+obj.presupuesto.id+"/";
            parameter='';
            RequestGet(function (datos, estado, mensage) {
                   
               if (estado == 'ok') {


                    if(datos=='2'){
                        sessionStorage.setItem("ubicacionActual", 'null');
                        location.href=path_principal+"/avanceObraLite/avance_con_gps/"+obj.id+"/";    

                    }else if(datos=='3'){
                        
                        location.href=path_principal+"/avanceObraLite/avance_sin_gps/"+obj.id+"/";
                    }else{
                         $.confirm({
                            title:'Informativo',
                            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>En este avance no tiene ningun punto de gps registrado.<h4>',
                            cancelButton: 'Cerrar',
                            confirmButton: false
                        });
                    }
                }

             }, path, parameter);
            
        }
        
       
    }

    //  self.abrir_avance_sin_gps=function(obj){

    //      if(self.habilitar_motivo()==true){
    //            $.confirm({
    //             title:'Informativo',
    //             content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>En este reporte de trabajo no hay avance.<h4>',
    //             cancelButton: 'Cerrar',
    //             confirmButton: false
    //         });
    //     }else{
            
    //     }
        
       
    // }

    self.abrir_modal_sin_avance=function(obj){

        self.titulo('Motivo de Sin Avance');
        self.mensaje_sin_avance(obj.motivoSinAvance);
        $('#modal_sin_avance').modal('show');
    }


    self.abrir_grafico=function(){

             location.href=path_principal+"/avanceObraLite/grafico/"+$('#presupuesto_id').val()+"/";

    }

    self.DetallesReporteVO={
        id: ko.observable(0),        
        detallePresupuesto_id: ko.observable('').extend({ required: { message: '(*)Seleccione un registro' } }),
        reporteTrabajo_id: ko.observable(''),
        cantidad: ko.observable('').extend({ required: { message: '(*)Ingrese la cantidad' } }),
        reporteTrabajo_reporteCerrado: ko.observable(false),
    }

    self.mensaje_detalles_periodo= ko.observable('');
    self.listado_uucc_disponibles=ko.observable([]);
    self.listado_detalles_periodo=ko.observable([]);
    self.titulo2=ko.observable('');

    self.cant_superiores= ko.observable(0);
    self.cant_inferiores= ko.observable(0);

    self.actividad_id = ko.observable('');
    self.cantidad_maxima = ko.observable('');
    self.consultar_por_detalles=function(obj){
        self.limpiar_detalles_periodo(); 
        self.titulo('Detalles del reporte de trabajo del : ('+obj.fechaReporte+')');
        self.DetallesReporteVO.reporteTrabajo_id(obj.id);
        self.DetallesReporteVO.reporteTrabajo_reporteCerrado(obj.reporteCerrado);
        self.cargar_por_detalles(obj.id)
       
    }

    self.abrir_carga_masiva = function () {
        self.limpiar();
        self.titulo('Actualización masiva de reportes de trabajo');
        $('#modal_acciones_carga_masiva').modal('show');
    }

    self.archivo_carga=ko.observable('');
    self.descargar_plantilla=function(){

        
        $.confirm({
            title:'Informativo',
            // content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Las columnas de la "A" a la "G" son de caracter informativo, las cuales no se deben modificar. <br> Tambien puede encontrar filas de color gris, unicamente sirve para ubicar el Hito principal<h4>',
            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>En el archivo Excel modifique las cantidades ejecutadas de las UUCC en cada respectiva fecha, segun el rango de fechas establecido. <br> Esta plantilla solo contendrá las fechas de los reportes abiertos<h4>',
            cancelButton: 'Cerrar',
            confirmButton: false
        });
        setTimeout(function(){ 

            location.href=path_principal+
            "/avanceObraLite/descargar-plantilla-reporte-trabajo/?presupuesto_id="+ $('#presupuesto_id').val()+
            "&cronograma_id="+$('#cronograma_id').val()+
            "&fechaDesde="+self.cargaVO.fechaDesde()+
            "&fechaHasta="+self.cargaVO.fechaHasta(); 

        }, 1000);
        
        
        
    }


    self.guardar_carga_masiva=function(){
        if((self.archivo_carga()=='') || ($('#presupuesto_id').val()==0)){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar la programación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('presupuesto_id',$('#presupuesto_id').val());
            data.append('cronograma_id',$('#cronograma_id').val());
            // data.append('esquema_id',$('#id_esquema').val());
            data.append('fechaDesde',self.cargaVO.fechaDesde());
            data.append('fechaHasta',self.cargaVO.fechaHasta());
            data.append('archivo',self.archivo_carga());

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        //if (estado=='ok') {
                        // self.consultar_por_id_cronograma();
                        self.cargar_detalles(1);
                        // self.cargar(1);
                        //}

                        $('#modal_acciones_carga_masiva').modal('hide');
                        $('#archivo').fileinput('reset');
                        $('#archivo').val('');
                        self.archivo_carga('');

                        setTimeout(function(){ cambiar_a_pestana(); }, 1000);
                         
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraLite/guardar-reporte-archivo/',//url api
                     parametros:data,
                     alerta: true                 
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }
    }

    // self.DetallesReporteVO.detallePresupuesto_id.subscribe(function(value){
    //     if(value!=""){
    //         self.consultar_cantidad_maxima(value);
    //     }else{
    //         self.cantidad_maxima('');
    //     }
    // });


    // self.consultar_cantidad_maxima = function(detallePresupuesto_id){
    //     path = path_principal+'/avanceObraLite/cantidad_maxima_detallePresupuesto/?format=json';
    //     parameter = {
    //         detallePresupuesto_id: detallePresupuesto_id,            
    //         DetalleReporteTrabajo_id: self.DetallesReporteVO.id(),
    //     };
    //     RequestGet(function (datos, estado, mensage) {
    //         if (estado=='ok') {
    //             self.cantidad_maxima(datos.cantidad_maxima);             
    //         }else{
                
    //         }

    //         $('#modal_detalles_reporte').modal('show');
    //         cerrarLoading();
    //     }, path, parameter, undefined, false, false);
    // }

    self.cargar_por_detalles=function(id){
        path = path_principal+'/api/avanceObraLiteDetalleReporteTrabajo/?format=json';
        parameter = {
            reporteTrabajo_id: id,            
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

            $('#modal_detalles_reporte').modal('show');
            cerrarLoading();
        }, path, parameter, undefined, false, false);
    }

    self.abrir_edicion_detalles_periodo=function(obj){
        nuevaRegistro();

        self.DetallesReporteVO.id(obj.id);
        self.DetallesReporteVO.detallePresupuesto_id(obj.detallePresupuesto.id);
        self.DetallesReporteVO.reporteTrabajo_id(obj.reporteTrabajo.id);
        self.DetallesReporteVO.cantidad(obj.cantidad);
        $('#nombre_actividad').val(obj.detallePresupuesto.descripcionUC);
        self.titulo2('Edición')
        
        $('#modal_list_actividades').animate({
            scrollTop: '0px'
        }, 300)
        cerrarLoading();
    }

    self.actividad_id.subscribe(function(value){
        if(value!=""){
            self.consultar_uucc_disponibles(value); 
        }else{
            self.listado_uucc_disponibles([]);
        }
        
    });

    

    self.consultar_uucc_disponibles=function(actividad_id){
        path = path_principal+'/api/avanceObraLiteDetallePresupuesto/?format=json';
        parameter = {
            presupuesto_id: $('#presupuesto_id').val(),
            actividad_id: actividad_id,
            reporteTrabajo_id: self.DetallesReporteVO.reporteTrabajo_id(),
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

    self.limpiar_detalles_periodo=function(){
        self.DetallesReporteVO.id('');       
        self.DetallesReporteVO.detallePresupuesto_id('');
        self.DetallesReporteVO.cantidad('');
               
        self.DetallesReporteVO.detallePresupuesto_id.isModified(false);
        self.DetallesReporteVO.cantidad.isModified(false);
   }
     

     self.eliminar_detalles_periodo=function(obj){
        var path =path_principal+'/api/avanceObraLiteDetalleReporteTrabajo/'+obj.id+'/';
        var parameter = {metodo:'DELETE'};
        RequestAnularOEliminar("Esta seguro que desea eliminar el registro?", path, parameter, 
            function(datos, estado, mensaje){
                if (estado=='ok') { 
                    self.cargar_por_detalles(obj.reporteTrabajo.id);
                    self.cargar_detalles(1);
                }        
        });
    }

    self.guardar_actividad=function(){
        // if (self.DetallesReporteVO.cantidad()<=self.cantidad_maxima()){
            if (IndexViewModel.errores_actividad().length == 0 && IndexViewModel.errores_actividad().length == 0 ) {
                if(self.DetallesReporteVO.id()==0){

                    var parametros={
                        callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                                self.cargar_por_detalles(self.DetallesReporteVO.reporteTrabajo_id());
                                self.cargar_detalles(1);
                                ocultarNuevoRegistro();  
                            }

                        }, //funcion para recibir la respuesta 
                        url:path_principal+'/api/avanceObraLiteDetalleReporteTrabajo/',//url api
                        parametros:self.DetallesReporteVO,                     
                    };
                    RequestFormData(parametros);
                }else{
                    var parametros={
                        metodo:'PUT',
                        callback:function(datos, estado, mensaje){
                            if (estado=='ok') {                             
                                self.cargar_por_detalles(self.DetallesReporteVO.reporteTrabajo_id());
                                self.cargar_detalles(1);
                                ocultarNuevoRegistro(); 
                            }

                        }, //funcion para recibir la respuesta 
                        url:path_principal+'/api/avanceObraLiteDetalleReporteTrabajo/'+self.DetallesReporteVO.id()+'/',//url api
                        parametros:self.DetallesReporteVO,                 
                    };
                    RequestFormData(parametros);
                }
            }else {
                if (IndexViewModel.errores_actividad().length > 0 ) {
                    IndexViewModel.errores_actividad.showAllMessages();
                }           
            }

        // }else{
        //     $.confirm({
        //         title:'Informativo',
        //         content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>La cantidad que desea reportar es superior a la cantidad maxima<h4>',
        //         cancelButton: 'Cerrar',
        //         confirmButton: false
        //     });
        // }
        
    }

    self.cerrar_reporte = function() {        
         var path =path_principal+'/avanceObraLite/cerrar_reportetrabajo/';
         var parameter = { id: self.DetallesReporteVO.reporteTrabajo_id()};
         RequestAnularOEliminar("Está seguro que desea cerrar el reporte seleccionado?", path, parameter, function () {
             self.consultar(1);
             self.DetallesReporteVO.reporteTrabajo_reporteCerrado(true);
         })
    }
    self.cargaVO={
        fechaDesde: ko.observable(''),
        fechaHasta: ko.observable(''),
    };

    self.filtroVO={
        fechaReporte: ko.observable(''),
        sinAvance: ko.observable(''),
        reporteCerrado: ko.observable(''),
    };

    self.abrir_modal_filter_principal = function () {
        self.titulo('Filtro de reportes');
        $('#modal_filtro_principal').modal('show');
    }

    self.filtrar_principal=function(){
       self.consultar(1);
        $('#modal_filtro_principal').modal('hide');
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
        self.titulo('Filtro de UUCC');
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

    self.filtro_detalles=ko.observable('');

    self.consultar_detalles = function (pagina) {
        if (pagina > 0) {            

            self.filtro_detalles($('#txtBuscar_detalles').val());
            sessionStorage.setItem("filtro_avance_detalle_reporte",self.filtro_detalles() || '');
            self.cargar_detalles(pagina);
        }
    }

    self.cargar_detalles =function(pagina){ 

        let filtro_avance_detalle=sessionStorage.getItem("filtro_avance_detalle_reporte");

        path = path_principal+'/api/avanceObraLiteDetallePresupuesto/?format=json&page='+pagina;
        parameter = {
            dato: filtro_avance_detalle,
            cronograma_id: $('#cronograma_id').val(),
            hito_id:self.busquedaVO.hito_id(),
            actividad_id:self.busquedaVO.actividad_id(),
            lite4:1};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.datos.length > 0) {
                self.mensaje_detalles('');
                //self.listado(results); 
                self.listado_detalles(agregarOpcionesObservable(datos.data.datos));
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


 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
$('#txtBuscar_detalles').val(sessionStorage.getItem("filtro_avance_detalle_reporte"));
index.cargar(1);//iniciamos la primera funcion
index.cargar_detalles(1);
IndexViewModel.errores_cronograma = ko.validation.group(index.reporteVO);
IndexViewModel.errores_actividad = ko.validation.group(index.DetallesReporteVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

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


function cambiar_a_pestana() {
    
  $('#tab_div_1').prop('class', 'tab-pane');
  $('#tab_div_2').prop('class', 'tab-pane active');

  $('#tab_li_1').prop('class', '');
  $('#tab_li_2').prop('class', 'active');

  $('#tab_a_1').prop("aria-expanded", "false");
  $('#tab_a_2').prop("aria-expanded", "true");
    

}