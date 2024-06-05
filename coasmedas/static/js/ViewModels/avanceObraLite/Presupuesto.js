function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
    self.listado_detalles=ko.observableArray([]);
    self.mensaje_detalles=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.filtro_detalles=ko.observable('');

    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   


    self.presupuestoVO={
        id:ko.observable(0),
        cronograma_id:ko.observable($('#cronograma_id').val()),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre' } }),
        cerrar_presupuesto:ko.observable(false),
        aiu: ko.observable('').extend({ required: { message: '(*)Digite la constancia AIU/K' } }),
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

    self.select_presupuestoVO={
        id:ko.observable(0),
        cronograma_id:ko.observable(''),
        nombre:ko.observable(''),
        cerrar_presupuesto:ko.observable(false),
        aiu: ko.observable(''),
    };

    self.presupuesto_id = ko.observable(0);
    self.cerrado_presupuesto=ko.observable(false);
    self.valor_total=ko.observable(0);
    self.archivo_carga=ko.observable('');
    self.listado_actividades=ko.observableArray([]);

    self.busquedaVO={
        hito_id:ko.observable(''),
        actividad_id:ko.observable('')
    };


    self.abrir_modal = function () {
        //self.limpiar();
        self.titulo('Registrar');
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

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.liquidacionuucc=function(obj){

        location.href=path_principal+"/avanceObraLite/ver-liquidacionuucc/"+obj.id+"/";
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un presupuesto para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraLite/eliminar_id_presupuesto/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los presupuestos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    }


    self.exportar_excel=function(){
        
    }

    // //limpiar el modelo 
     self.limpiar=function(){   
           self.presupuestoVO.nombre('');
           self.presupuestoVO.aiu();
           self.presupuestoVO.nombre.isModified(false);
           self.presupuestoVO.aiu.isModified(false);

     }



    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

             self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_avance_presupuesto",self.filtro() || '');

            self.cargar(pagina);

        }


    }


    self.cargar =function(pagina){           


            let filtro_avance_presupuesto=sessionStorage.getItem("filtro_avance_presupuesto");

            path = path_principal+'/api/avanceObraLitePresupuesto/?format=json&page='+pagina;
            parameter = {dato: filtro_avance_presupuesto, pagina: pagina,cronograma_id:$("#cronograma_id").val()};
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


    self.guardar=function(){

         if (IndexViewModel.errores_cronograma().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.presupuestoVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceObraLitePresupuesto/',//url api
                     parametros:self.presupuestoVO                        
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
                       url:path_principal+'/api/avanceObraLitePresupuesto/'+self.presupuestoVO.id()+'/',
                       parametros:self.presupuestoVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             IndexViewModel.errores_cronograma.showAllMessages();//mostramos las validacion
        }
    }





    self.abrir_apoyo_con_gps=function(obj){
        sessionStorage.setItem("ubicacionActual",null);
        path =path_principal+"/avanceObraLite/menu_gps/"+obj.id+"/";
        parameter='';
        RequestGet(function (datos, estado, mensage) {
               
           if (estado == 'ok') {

                if(datos=='1'){

                         $.confirm({
                            title: 'Confirmar!',
                            content: "<h4>Tiene los puntos de localizacion?</h4>",
                            confirmButton: 'Si',
                            confirmButtonClass: 'btn-info',
                            cancelButtonClass: 'btn-danger',
                            cancelButton: 'No',
                            confirm: function() {

                                location.href=path_principal+"/avanceObraLite/apoyo_con_gps/"+obj.id+"/";                               
                            },
                            cancel: function() {
                                location.href=path_principal+"/avanceObraLite/apoyo_sin_gps/"+obj.id+"/";
                            }
                        });
                
                }else if(datos=='2'){

                    location.href=path_principal+"/avanceObraLite/apoyo_con_gps/"+obj.id+"/";     

                }else if(datos=='3'){
                    
                    location.href=path_principal+"/avanceObraLite/apoyo_sin_gps/"+obj.id+"/";
                }
            }

         }, path, parameter);


        
    }

       self.cantidad_apoyo=function(obj){

        location.href=path_principal+"/avanceObraLite/cantidad_apoyo/"+obj.id+"/";
    }


    self.reporte_trabajo=function(obj){

        location.href=path_principal+"/avanceObraLite/reporte_trabajo/"+obj.id+"/";
    }

    self.reformado=function(obj){

        location.href=path_principal+"/avanceObraLite/reformado/"+obj.id+"/";
    } 

    self.seguimiento_cantidades=function(obj){

        location.href=path_principal+"/avanceObraLite/seguimientocantidades/"+obj.id+"/";
    }    

    self.seguimiento_materiales=function(obj){

        location.href=path_principal+"/avanceObraLite/seguimientomateriales/"+obj.id+"/";
    } 



    self.abrir_detalle_presupuesto=function(obj){
        
        // location.href=path_principal+"/avanceObraLite/detalle_presupuesto/"+obj.id+"/";

        self.select_presupuestoVO.id(obj.id);
        self.select_presupuestoVO.cronograma_id(obj.cronograma.id);
        self.select_presupuestoVO.nombre(obj.nombre);
        self.select_presupuestoVO.cerrar_presupuesto(obj.cerrar_presupuesto);
        self.select_presupuestoVO.aiu(obj.aiu);
        // alert(self.select_presupuestoVO.cerrar_presupuesto());
        self.consultar_detalles(1);
        
        
    }

    self.cerrar_detalles=function(){
        
       // location.href=path_principal+"/avanceObraLite/detalle_presupuesto/"+ob j.id+"/";

       self.select_presupuestoVO.id(0);
       self.select_presupuestoVO.nombre('');
       self.select_presupuestoVO.cerrar_presupuesto(false);
       self.select_presupuestoVO.aiu('');
       // alert(self.select_presupuestoVO.cerrar_presupuesto());
       // self.consultar_detalles(1);
    }

    self.abrir_modal_carga_masiva = function () {
        self.titulo('Carga Masiva de Presupuesto');
        $('#modal_acciones_carga_masiva').modal('show');
    }

    self.guardar_carga_masiva=function(){

        if ((self.archivo_carga()=='') || ($('#cmbCatalogo').val()==0)){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo y el catalogo de UUCC para cargar el presupuesto.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('presupuesto_id', self.select_presupuestoVO.id());
            data.append('archivo',self.archivo_carga());
            data.append('catalogoUnidadConstructiva_id', $('#cmbCatalogo').val())
            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar_detalles(1);
                            $('#modal_acciones_carga_masiva').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraLite/guardar_presupuesto_archivo/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }
   
    }

    self.descargar_plantilla=function(){

        location.href=path_principal+"/avanceObraLite/descargar_plantilla_presupuesto/?id_esquema="+$('#id_esquema').val();

    }



    self.abrir_modal_filter = function () {
        self.titulo('Filtro');
        $('#modal_filtro').modal('show');
    }

    self.filtrar=function(){
       self.consultar_detalles(1);
        $('#modal_filtro').modal('hide');
    }

    //funcion consultar de tipo get recibe un parametro
    self.consultar_detalles = function (pagina) {
        if (pagina > 0) {            

            self.filtro_detalles($('#txtBuscar_detalles').val());
            sessionStorage.setItem("filtro_avance_detalle",self.filtro_detalles() || '');
            self.cargar_detalles(pagina);
        }
    }

    self.cargar_detalles =function(pagina){ 

        let filtro_avance_detalle=sessionStorage.getItem("filtro_avance_detalle");

        path = path_principal+'/api/avanceObraLiteDetallePresupuesto/?format=json&page='+pagina;
        parameter = {dato: filtro_avance_detalle,presupuesto_id:self.select_presupuestoVO.id(),
        hito_id:self.busquedaVO.hito_id(),actividad_id:self.busquedaVO.actividad_id(),lite2:1};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje_detalles('');
                //self.listado(results); 
                self.listado_detalles(agregarOpcionesObservable(self.llenar_datos(datos.data)));
                //self.cargar_total_presupuesto(datos);
                 $('#modal_acciones').modal('hide');

            } else {
                self.listado_detalles([]);
                self.mensaje_detalles(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }

            
            self.llenar_paginacion_detalles(datos,pagina);
            //}
            cerrarLoading();
        }, path, parameter,undefined, false);
    }

    self.llenar_datos=function(data){
        self.valor_total(0);
         var lista=[];
         sw=true;
         //alert(self.cerrado_presupuesto())
         if(self.select_presupuestoVO.cerrar_presupuesto()==true || self.select_presupuestoVO.cerrar_presupuesto()=='True'){
            sw=false;
         }
         
          ko.utils.arrayForEach(data, function(obj) {
                    color='';
                    if(obj.codigoUC=='' || obj.codigoUC == null){
                        color='#E18989'
                    }
                    valor=parseFloat(obj.cantidad)*parseFloat(obj.valorGlobal);
         
                    lista.push({
                        id:ko.observable(obj.id),
                        nombre_padre:ko.observable(obj.nombre_padre),
                        actividad_nombre:ko.observable(obj.actividad.nombre),
                        codigoUC:ko.observable(obj.codigoUC),
                        descripcionUC:ko.observable(obj.descripcionUC),
                        valorUC:ko.observable(obj.valorGlobal),
                        cantidad:ko.observable(obj.cantidad),
                        subtotal:ko.observable(valor),
                        color:ko.observable(color),
                        habilitar:ko.observable(sw)
                    });
                    self.valor_total(parseFloat(obj.sumaPresupuesto));
             });
        return lista;
    }

    self.busquedaVO.hito_id.subscribe(function(value ){

             if(value!=0){
                path = path_principal+'/api/avanceObraLiteEsquemaCapitulosActividades/?sin_paginacion';
                parameter = {padre_id:value};
                RequestGet(function (datos, estado, mensage) {

                    self.listado_actividades(datos);
                }, path, parameter,function(){
                    // self.disenoVO.municipio_id(0);
                    // self.disenoVO.municipio_id(self.municipio());
                }
                );
            }else{
                self.listado_actividades([]);
                self.busquedaVO.actividad_id('')
            }
    });


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
                valorUC:obj.valorUC(),
                cantidad:obj.cantidad()
            });
        });

        return lista;
    }

    self.guardar_presupuesto=function(){
        var lista=[];
        var sw=0;
        var mensaje="";

        ko.utils.arrayForEach(self.listado_detalles(), function(obj) {
                
                if(obj.codigoUC()=='' || obj.codigoUC() == null){
                    sw=1
                }
        });

        if(sw==1){
            mensaje="¿Esta seguro que desea guardar el presupuesto con codigo UUCC vacio?, no podra ser modificado";
        }else{
            mensaje="¿Esta seguro que desea guardar el presupuesto?, no podra ser modificado";
        }

        $.confirm({
            title: 'Confirmar!',
            content: "<h4>"+mensaje+"</h4>",
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {                
                var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.select_presupuestoVO.cerrar_presupuesto(true);
                            // self.cerrado_presupuesto(true);
                            self.consultar(1);
                            self.consultar_detalles(1);
                        }                        
                        
                    },//funcion para recibir la respuesta 
                    url:path_principal+'/avanceObraLite/cierre_presupuesto/',//url api
                    parametros:{ lista: self.listado_cantidad(),id_presupuesto:self.select_presupuestoVO.id() }                         
                };
                Request(parametros);
            }
        });

    }




}



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance_presupuesto"));
$('#txtBuscar_detalles').val(sessionStorage.getItem("filtro_avance_detalle"));
index.cargar(1);//iniciamos la primera funcion
IndexViewModel.errores_cronograma = ko.validation.group(index.presupuestoVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);


