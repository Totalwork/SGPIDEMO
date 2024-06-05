
function Encabezado_giroViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.listado_no_radicado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.mensaje_no_radicado=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.soporte_arriba=ko.observable('');
    self.idProcesoRelacion =ko.observable(0);

    self.macrocontrato_select=ko.observable(0);
    self.lista_contrato=ko.observableArray([]);
    self.contratista=ko.observable('');
    self.listado_contratista=ko.observableArray([]);  
    self.nombre_giros=ko.observableArray([]);
    self.lista_contrato_select=ko.observableArray([]);
    self.detalle_vermas = ko.observable({});
    self.lista_cuenta_select=ko.observableArray([]);

    // tipos con que se va a pagar el giro
    self.pago_recurso_id =ko.observable(0);
    self.listado_tipo_pago_recurso = ko.observableArray([]);
    
    //para filtrar tab consultar y modificar
    self.macontrato_filtro_select=ko.observable(0);
    self.contratista_filtro_select=ko.observable(0);
    self.listado_contratista_filtro=ko.observableArray([]);
    self.listado_contrato_filtro=ko.observableArray([]);


    //para filtrar tab numero radicado
    self.macontrato_filtro_select_radicado=ko.observable(0);
    self.contratista_filtro_select_radicado=ko.observable(0);
    self.listado_contratista_filtro_radicado=ko.observableArray([]);
    self.listado_contrato_filtro_radicado=ko.observableArray([]);
    self.listado_errores=ko.observableArray([]);

     

    //observables para el ver mas de el encabezado giro
    self.id_vermas=ko.observable(0);
    self.soporte_vermas=ko.observable('');
    self.numero_contrato_vermas=ko.observable('');
    self.nombre_giro_vermas=ko.observable('');
    self.total_giro_vermas=ko.observable('');
    self.nombre_contrato_vermas=ko.observable('');
    self.nombre_proyecto_vermas=ko.observable('');
    self.nombre_contratista_vermas=ko.observable('');
    self.anticipo_id=ko.observable('');
    self.soporte_ve=ko.observable('');
    self.mcontrato_id=ko.observable('');
    self.contrato_obra=ko.observable('');
    
    self.procesoRelacionId=ko.observable(0);
    self.procesoRelacionDatoId=ko.observable(0);
    self.mensaje_listado_seguimiento=ko.observable('');
    self.listado_soportes=ko.observableArray([]);
    self.mensaje_listado_soportes=ko.observable('');
    self.archivo1=ko.observable('');
    self.nombre_documento=ko.observable('');

    self.listadoPoliza=ko.observableArray([]);
    self.mensajePoliza=ko.observable('');
    self.nombre_giro=ko.observable('');

    //var num=0;
    //self.url=path_principal+'api/empresa'; 

     //Representa un modelo de la tabla giro
    self.encabezado_giroVO={
        id:ko.observable(0),
        nombre_id:ko.observable('').extend({ required: { message: '(*)Seleccione el nombre del anticipo' } }),
        contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contrato' } }),
        soporte:ko.observable('').extend({ required: { message: '(*)Ingrese el soporte' } }),
        referencia:ko.observable(''),
        num_causacion:ko.observable(''),
        fecha_conta:ko.observable(''),
        disparar_flujo:ko.observable(0),
        numero_radicado:ko.observable(''),
     };


         //modelo para verificar el giro
    self.verificar_giroVO={
        fecha_ini:ko.observable('').extend({ required: { message: 'Seleccione la fecha de inicio' } }),
        fecha_fin:ko.observable('').extend({ required: { message: 'Seleccione la fecha fin' } }),
        cuenta_verif:ko.observable('').extend({ required: { message: 'Seleccione la cuenta' } }),
        soporte_verif:ko.observable('').extend({ required: { message: 'Seleccione el documento' } }),
     };

    //modelo para actualizar el tipo de pago del giro
    self.tipo_pago_del_giroVO={
        id:ko.observableArray([]), 
        pago_recurso_id:ko.observable('').extend({ required: { message: 'Seleccione el tipo de pago' } }),
    };

    //modelo para actualizar el tipo de pago del giro
    self.disparar_flujoVO={
        id:ko.observable(0), 
        disparar_flujo:ko.observable(0),
    };

     //paginacion de tab consultar y modificar
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
        },
        totalRegistrosBuscados:ko.observable(0)
    }

    //paginacion de tab consultar y modificar
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    //Funcion para crear la paginacion de tab consultar y modificar
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    //paginacion de tab no radicado
    self.paginacion_radicado = {
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
        },
        totalRegistrosBuscados2:ko.observable(0),
    }

    //paginacion de tab no radicado
    self.paginacion_radicado.pagina_actual.subscribe(function (pagina) {
        self.consultar_no_radicado(pagina);
    });


        //Funcion para crear la paginacion de tan no radicado
    self.llenar_paginacion_radicado = function (data,pagina) {

        self.paginacion_radicado.pagina_actual(pagina);
        self.paginacion_radicado.total(data.count);       
        self.paginacion_radicado.cantidad_por_paginas(resultadosPorPagina);
        var buscados2 = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion_radicado.totalRegistrosBuscados2(buscados2);

    }

    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });

    //funcion para abrir modal de registrar encabezado giro
    self.abrir_modal = function () {
        self.limpiar();
        self.consultar_macrocontrato();
        self.titulo('Registrar Giro');
        $('#modal_acciones').modal('show');
    }

    //funcion para filtrar los pagos del giros
    self.filtrar_verificar_giro_modal = function () {
        self.titulo('Verificar pagos de giros');
        self.consultar_lista_cuenta();
        $('#modal_filtro').modal('show');
    }

    //funcion para filtrar los encabezado giros del tab consultar y modificar
    self.filtrar_consultar_modificar_modal = function () {
        self.titulo('Filtrar giros');
        //self.limpiar();
        self.consultar_select_filter_proyecto();
        self.consultar_contrato_select_filtro(0,0);
        $('#modal_filtro_giro').modal('show');
    }

    self.consultar_select_filter_proyecto = function (pagina) { 

        path = path_principal+'/proyecto/select-filter-proyecto/';
        parameter = { };
        RequestGet(function (datos, estado, mensage) {

            self.lista_contrato(datos.mcontratos);
            self.listado_contratista_filtro(datos.contratistas);
            
            if (sessionStorage.getItem("dato_encabezado_giro") != '' && sessionStorage.getItem("dato_encabezado_giro") != null){
                $('#txtBuscar').val(sessionStorage.getItem("dato_encabezado_giro"));
            }            

            if (sessionStorage.getItem("mcontrato_filtro_encabezado_giro") != '' && sessionStorage.getItem("mcontrato_filtro_encabezado_giro") != null){
                $('#mcontrato_filtro').val(sessionStorage.getItem("mcontrato_filtro_encabezado_giro"));
            }
            if (sessionStorage.getItem("contratista_filtro_encabezado_giro") != '' && sessionStorage.getItem("contratista_filtro_encabezado_giro") != null){
                $('#contratista_filtro').val(sessionStorage.getItem("contratista_filtro_encabezado_giro"));
            } 
            if (sessionStorage.getItem("contrato_filtro_encabezado_giro") != '' && sessionStorage.getItem("contrato_filtro_encabezado_giro") !=null){ 
                $('#contrato_filtro').val(sessionStorage.getItem("contrato_filtro_encabezado_giro"));
            }  


            cerrarLoading();
        }, path, parameter,undefined,false);        
    }

    //funcion para cambiar de color el icono
    self.setColorIconoFiltro = function (){
        dato = sessionStorage.getItem("dato_encabezado_giro");
        mcontrato = sessionStorage.getItem("mcontrato_filtro_encabezado_giro");
        contratista = sessionStorage.getItem("contratista_filtro_encabezado_giro");
        contrato = sessionStorage.getItem("contrato_filtro_encabezado_giro");
       
        if ((dato != '' && dato!=null) || 
            (mcontrato!='' && mcontrato != 0 && mcontrato !=null ) || 
            (contratista != '' && contratista !=0 && contratista !=null) || 
            (contrato != '' && contrato !=0 && contrato !=null)){
            
            $('#iconoFiltro').addClass("filtrado");
        }else{
            $('#iconoFiltro').removeClass("filtrado");
        }
    }

    //funcion para filtrar en el tan no radicado
    self.filtrar_no_radicado_modal = function () {
        self.titulo('Filtrar no. radicado');
        //self.limpiar();
        self.consultar_macrocontrato();
        $('#modal_no_radicado').modal('show');
    }


    //funcion para abrir modal de subir soporte en el tab no radicado
    self.documento_no_radicado = function (item) {

        self.procesoRelacion(item.contrato.id(),item.id());
        self.titulo('Soporte de solicitud');
        //self.limpiar();
        $('#soporte_solicitud').modal('show');
    }

    //funcion para ver mas detalle del encabezado 
    self.ver_mas_detalle = function (obj) {
        self.titulo('Resumen del encabezado');
        self.ver_mas_encabezado(obj);
        $('#vermas_encabezado').modal('show');
    }

    //funcion para exportar a excel el encabezado del giro
    self.exportar_excel = function (obj) {
        self.titulo('Generar informe');
        self.consultar_macrocontrato();
        $('#generar_informe').modal('show');
    }

    //funcion para seleccionar que reporte generar en el encabezado giro
    self.reporte_de_giro = function (obj) {
        
        self.anticipo_id(obj.id);
        self.mcontrato_id(obj.contrato.mcontrato.id);
        self.contrato_obra(obj.contrato.id);

        self.titulo('Reporte de giro');
        $('#reporte_giro').modal('show');
    }

    // funcion para actualizar forma de pago
    self.abrir_modal_forma_pago = function () {
        self.titulo('Actualizar forma de pago');
        $('#modal_actualizar_forma_pago_giro').modal('show');
    }


    //consultar la api proceso relacion
    self.procesoRelacion=function(contratoId,anticipoId){

        path = path_principal+'/api/procesoRelacion/?format=json';
        parameter={ proceso: 1, verDetalle:1, apuntador:2, idApuntador:contratoId, idTablaReferencia:anticipoId };
        RequestGet(function (datos, estado, mensaje) {
            
            self.procesoRelacionId(datos.data[0].id);
            self.list_seguimiento();

        }, path, parameter);

    }


        //listado de seguimiento de liquidacion
    self.list_seguimiento=function(){

         path = path_principal+'/api/procesoRelacionDato/?format=json';
         parameter={ procesoRelacion:self.procesoRelacionId(),item:5 };
         RequestGet(function (datos, estado, mensaje) {
            
            if (datos.data.listado[0]!=null && datos.data.listado.length > 0) {

                self.mensaje_listado_seguimiento('');
                self.procesoRelacionDatoId(datos.data.listado[0].id);
                self.consultar_soportes();

            } else {
                    self.procesoRelacionDatoId(0)
                    self.mensaje_listado_seguimiento(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }

         }, path, parameter);

    }


    //consultar la api de soporte proceso relacion dato para traerme los soportes
    self.consultar_soportes=function(){

        path = path_principal+'/api/soporteProcesoRelacionDato/?format=json';
        parameter={ procesoRelacionDato: self.procesoRelacionDatoId()};
        RequestGet(function (datos, estado, mensaje) {

            if (datos.data!=null && datos.data.length > 0) {

                self.listado_soportes(datos.data);

            } else {
                self.listado_soportes([]);
                self.mensaje_listado_soportes(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
            
        }, path, parameter);

    } 


     //funcion guardar soprotes de proceso
    self.guardar_soporte=function(){
        var data = new FormData();

        if (self.archivo1()=='' || self.nombre_documento()=='') {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe digitar el nombre del documento y cargar el soporte.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false
        }

        data.append('procesoRelacionDato_id',self.procesoRelacionDatoId());
        data.append('nombre_documento',self.nombre_documento());
        data.append('archivo', self.archivo1());

        var parametros={                     
            callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                    self.consultar_soportes();
                }                        
                            
            },//funcion para recibir la respuesta 
                url:path_principal+'/giros/cargar_soporte/',//url api
                parametros:data,
                completado:function(){}                          
            };
        RequestFormData2(parametros);
    }


     //limpiar el modelo 
     self.limpiar=function(){        
         
             self.encabezado_giroVO.id(0);
             self.encabezado_giroVO.contrato_id('');
             self.encabezado_giroVO.nombre_id('');
             self.encabezado_giroVO.soporte('');
             self.encabezado_giroVO.referencia('');
             self.encabezado_giroVO.num_causacion('');
             self.encabezado_giroVO.fecha_conta('')
             self.encabezado_giroVO.disparar_flujo(0);
             self.encabezado_giroVO.numero_radicado('');

             self.contratista(0);
             self.macrocontrato_select(0);
             self.lista_contrato_select([]);
             self.listado_contratista([]);

             self.macontrato_filtro_select(0);
             self.contratista_filtro_select(0);

             self.macontrato_filtro_select_radicado(0);
             self.contratista_filtro_select_radicado(0);

             self.encabezado_giroVO.nombre_id.isModified(false);
             self.encabezado_giroVO.contrato_id.isModified(false);

             $('#archivo2').fileinput('reset');
             $('#archivo2').val('');
            // check_eliminar(false)         
     }


     //limpiar el modelo de verificar giros
     self.limpiar_verificar_giro=function(){        
         
             self.verificar_giroVO.fecha_ini('');
             self.verificar_giroVO.fecha_fin('');
             self.verificar_giroVO.cuenta_verif('');
             self.verificar_giroVO.soporte_verif('');

             self.verificar_giroVO.fecha_ini.isModified(false);          
             self.verificar_giroVO.fecha_fin.isModified(false);
             self.verificar_giroVO.cuenta_verif.isModified(false);             
             self.verificar_giroVO.soporte_verif.isModified(false);

             $('#archivo').fileinput('reset');
             $('#archivo').val('');    
     }

    //consultar los macrocontrato para registrar el giro
    self.consultar_macrocontrato=function(){

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_contrato(datos.macrocontrato);

         }, path, parameter,function(){
             self.macontrato_filtro_select(sessionStorage.getItem("mcontrato_filtro_encabezado_giro"));
         },false,false);

    }

     //funcion que se ejecuta cuando se cambia en el select de contrato para obtener los contratista y contrato de obra para registrar el giro
    self.macrocontrato_select.subscribe(function (value) {

        if(value >0){
            self.consultar_nombre_giros(value);
            self.consultar_contratista(value);
            self.consultar_contrato_select(value,0);

        }else{

            self.nombre_giros([]);
            self.listado_contratista([]);
            self.lista_contrato_select([]);

        }
    });


    //consultar los nombre de los contratista segun el macrocontrato para registrar el giro
    self.consultar_contratista=function(value){                  
         //path =path_principal+'/contrato/list_contrato_select/?mcontrato='+value+'&contratista=0';
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter = { mcontrato : value, tipo :8, tipo_contratista: true};
         //parameter={ mcontrato:value, tipo:'8'};
         RequestGet(function (datos, estado, mensaje) {
          
            self.listado_contratista(datos.contratista);
           
         }, path, parameter);
         
    }


    //funcion que se ejecuta cuando se cambia en el select de contratista para filtrar los contrato de obra segun macrocontrato y contratista para registrar el giro
    self.contratista.subscribe(function (value) {
       
        if(value >0){
            self.consultar_contrato_select(self.macrocontrato_select(),value);

        }
    });


    //consultar los contrato de obra segun el macro y segun contratista para registrar el giro
    self.consultar_contrato_select=function(value1,value2){

        
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ mcontrato: value1, contratista:value2, tipo:'8,9,10,11,13,14,15',contratos_asociados:1};
         RequestGet(function (datos, estado, mensaje) {
            
            self.lista_contrato_select(datos.contrato);

         }, path, parameter);

    }


    //consultar los nombre de los giros segun macrocontrato para registrar el giro
    self.consultar_nombre_giros=function(value){
           
         path =path_principal+'/api/Nombre_giro/?sin_paginacion=';
         parameter={ contrato: value};
         RequestGet(function (datos, estado, mensaje) {
          
             self.nombre_giros(datos);
             /*sw=0;
             ko.utils.arrayForEach(self.nombre_giros(), function(d) {
                   
                    if(d.id==self.encabezado_giroVO.nombre_id()){
                            sw=1;
                    }
             });
             if(sw==0){
                self.encabezado_giroVO.nombre_id('');
             }*/

         }, path, parameter);
         
    }

    self.validacion_giro=function(){
        if(self.encabezado_giroVO.id()==0){
            parameter = {contrato_id:self.encabezado_giroVO.contrato_id(),mcontrato_id:self.macrocontrato_select()};
            path = path_principal+'/giros/validacion_giro/?format=json';
            RequestGet(function (data,success,message) { 
                if(success=='ok'){
                    self.guardar();
                }else{
                    mensajeError(message);
                }                 
            }, path, parameter);
        }else{
            self.guardar();
        }
    }

    //funcion guardar y actualizar el encabezado del giro
     self.guardar=function(){

        if (Encabezado_giroViewModel.errores_giros().length == 0) {//se activa las validaciones

            if(self.encabezado_giroVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            self.consultar_no_radicado(1);
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Encabezado_giro/',//url api
                     parametros:self.encabezado_giroVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{                 
                if($('#archivo2')[0].files.length==0){
                    mensajeInformativo('Debe cargar el documento.','Información');
                }else{
                    var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.limpiar();
                          self.consultar(self.paginacion.pagina_actual());
                          self.consultar_no_radicado(1);
                          $('#modal_acciones').modal('hide');
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Encabezado_giro/'+self.encabezado_giroVO.id()+'/',
                       parametros:self.encabezado_giroVO                        
                  };

                  RequestFormData(parametros);

                }
            }
                  

        } else {
            if($('#archivo2')[0].files.length==0){
                mensajeInformativo('Debe cargar el documento.','Información');
            }            
             Encabezado_giroViewModel.errores_giros.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar tap de consultar y modificar de encabezado giro
    self.consultar = function (pagina) {
        
        //alert($('#mcontrato_filtro').val())
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("dato_encabezado_giro", $('#txtBuscar').val() || '');
            sessionStorage.setItem("contrato_filtro_encabezado_giro", $('#contrato_filtro').val() || '');
            sessionStorage.setItem("contratista_filtro_encabezado_giro", $('#contratista_filtro').val() || '');            
            sessionStorage.setItem("mcontrato_filtro_encabezado_giro", $('#mcontrato_filtro').val() || '');
            self.setColorIconoFiltro();
            self.cargar(pagina);
            
        }
    }


    self.cargar = function(pagina){


        let filtro = sessionStorage.getItem("dato_encabezado_giro");
        let contrato_filtro = sessionStorage.getItem("contrato_filtro_encabezado_giro");
        let contratista_filtro = sessionStorage.getItem("contratista_filtro_encabezado_giro");
        let mcontrato_filtro = sessionStorage.getItem("mcontrato_filtro_encabezado_giro");

            path = path_principal+'/api/Encabezado_giro/?format=json';
            parameter = { dato: filtro, 
                page: pagina, 
                contrato_filtro:contrato_filtro, 
                contratista_filtro:contratista_filtro, 
                mcontrato_filtro:mcontrato_filtro};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    $('#modal_filtro_giro').modal('hide'); 
                    self.listado(agregarOpcionesObservable(datos.data));
                    cerrarLoading();

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter,undefined, false);

    }


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    //consultar por id el encabezado del giro
    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/Encabezado_giro/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar Giro');

            self.consultar_nombre_giros(datos.nombre.contrato.id);

            self.encabezado_giroVO.id(datos.id);
            self.encabezado_giroVO.contrato_id(datos.contrato.id);
            self.encabezado_giroVO.soporte(datos.soporte);
            self.encabezado_giroVO.nombre_id(datos.nombre.id);
            self.soporte_arriba(datos.soporte);
             
             $('#modal_acciones').modal('show');

         }, path, parameter);

     }

   
    //eliminar los encabezados del giros
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un giro para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/giros/eliminar_id/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los giros seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.consultar_no_radicado(1);
                 self.checkall(false);
             })

         }     
    
        
    }


    //exportar excel general la tabla de consultar y modificar por contrato
   self.exportar_excel_contrato=function(){

        var contrato=$("#mcontrato").val();

        // if(contrato==0){

        //     $.confirm({
        //         title:'Informativo',
        //         content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione el contrato.<h4>',
        //         cancelButton: 'Cerrar',
        //         confirmButton: false
        //      });
        //     return false;
        // }   

        location.href=path_principal+"/giros/exportar_encabezado_giro/?contrato="+contrato;
    } 




    //funcion consultar el tab no radicado
    self.consultar_no_radicado = function (pagina) {
        //alert()
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar2').val());
            path = path_principal+'/api/Encabezado_giro/?format=json'; 
            parameter = { dato: self.filtro(), page: pagina, contrato_filtro:$('#contrato_filtro_radicado').val(), contratista_filtro:$('#contratista_filtro_radicado').val(), mcontrato_filtro:$('#mcontrato_filtro_radicado').val() };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje_no_radicado('');
                    $('#modal_no_radicado').modal('hide'); 
                    self.listado_no_radicado(convertToObservableArray(datos.data));
                    cerrarLoading();

                } else {

                    self.listado_no_radicado([]);
                    self.mensaje_no_radicado(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
                }

                self.llenar_paginacion_radicado(datos,pagina);

            }, path, parameter,undefined, false);
        }
    }


    //guardar la fecha del radicado o numero de radicado en el tan no radicado
    self.guardar_no_radicado=function(obj){            

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar_no_radicado(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                             //mensajeExitoso(estado);
                            self.limpiar();
                        }                      
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/giros/actualizar_no_radicado/',//url api
                     parametros:{id:obj.id,numero_radicado:obj.numero_radicado,fecha_conta:obj.fecha_conta}
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);    

     }


      //funcion que se ejecuta cuando se cambia en el select de contrato para filtrar en el tab consultar y modificar
    self.macontrato_filtro_select.subscribe(function (value) {

        if(value >0){
            self.consultar_contratista_filtro(value);
            self.consultar_contrato_select_filtro(value,0);

        }else{

            self.listado_contratista_filtro([]);
            self.listado_contrato_filtro([]);
        }

    });


    //funcion que se ejecuta cuando se cambia en el select de contratista para filtrar en el tab consultar y modificar
    self.contratista_filtro_select.subscribe(function (value) {

        if(value >0){

            self.consultar_contrato_select_filtro(self.macontrato_filtro_select(),value);
        
        }
    });


    //consultar los nombre de los contratista segun el contrato para filtrar en el tab consultar y modificar
    self.consultar_contratista_filtro=function(value){

        if (value>0) {
             path =path_principal+'/proyecto/filtrar_proyectos/';
             parameter={ mcontrato:value, tipo:'8', tipo_contratista:true};
             RequestGet(function (datos, estado, mensaje) {
              
                self.listado_contratista_filtro(datos.contratista);
               
             }, path, parameter, function(){
                 self.contratista_filtro_select(sessionStorage.getItem("contratista_filtro_encabezado_giro"));       
             });
        }
         
    }


        //consultar los contrato de obra segun el macro y segun contratista para filtrar en el tab consultar y modificar
    self.consultar_contrato_select_filtro=function(value1,value2){

        if (value1>0) {
             path =path_principal+'/proyecto/filtrar_proyectos/';
             parameter={ mcontrato: value1, contratista:value2, tipo:'8,9,10,11,13,14,15'};
             RequestGet(function (datos, estado, mensaje) {
                
                self.listado_contrato_filtro(datos.contrato);

            }, path, parameter, function(){
                 $('#contrato_filtro').val(sessionStorage.getItem("contrato_filtro_encabezado_giro"));        
             });
        }
    }


    //trae los datos para la opcion ver mas del encabezado del giro
    self.ver_mas_encabezado=function(obj){
        
         //path =path_principal+'/api/Encabezado_giro/?encabezado_id='+obj.id+'&sin_paginacion&format=json';
         path =path_principal+'/giros/encabezado_detalle/';
         parameter={ encabezado_id: obj.id, contrato:0, proyecto:0};
         RequestGet(function (datos, estado, mensaje) {
            
            self.id_vermas(obj.id);
            self.soporte_vermas(datos[0].soporte_giro);
            self.numero_contrato_vermas(datos[0].numero_contrato);
            self.nombre_giro_vermas(datos[0].giro_nombre);
            self.total_giro_vermas(datos[0].suma_valor_detalles);
            self.nombre_contrato_vermas(datos[0].nombre_contrato);
            self.nombre_proyecto_vermas(datos[0].nombre_proyecto);
            self.nombre_contratista_vermas(datos[0].nombre_contratista);
            self.soporte_ve(datos[0].soporte);


         }, path, parameter);

    }

    //funcion para seleccionar que reporte de encabezado del giro se generara
    self.generar_reporte_giro=function(){

        var opcion = $("input[name='reporteGiro']:checked").val();
        //var id = $("#id_anticipo").val();

        if(opcion=="solicitudAnticipo"){

            path = path_principal+"/giros/validar_estado_cuenta/?encabezado_id="+self.anticipo_id();
            
            parameter = {};
            RequestGet(function (datos, estado, mensage) {

                console.log(datos)
                if(datos.total>0){
                    location.href=path_principal+"/giros/reporte_anticipo2/?encabezado_id="+self.anticipo_id();
                }else{
                    $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> La cuenta '+datos.cuenta+' no tiene saldo para tramitar el anticipo.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });
                }

            }, path, parameter);     

        }else{
            
            location.href=path_principal+"/giros/reporte_giro_exportar/?encabezado_id="+self.anticipo_id();
            //location.assign("reporteGiro.php?id_anticipo="+id+"&reporteGiro="+opcion);
        }

    }



        //funcion que se ejecuta cuando se cambia en el select de contrato para filtrar en el tab no radicado
    self.macontrato_filtro_select_radicado.subscribe(function (value) {

        if(value >0){
            self.consultar_contratista_filtro_radicado(value);
            self.consultar_contrato_select_filtro_radicado(value,0);

        }else{

            self.listado_contratista_filtro_radicado([]);
            self.listado_contrato_filtro_radicado([]);
        }

    });



        //funcion que se ejecuta cuando se cambia en el select de contrato para filtrar en el tab no radicado
    self.contratista_filtro_select_radicado.subscribe(function (value) {

        if(value >0){

            self.consultar_contrato_select_filtro_radicado(self.macontrato_filtro_select_radicado(),value);
        
        }
    });


    //consultar los nombre de los contratista segun el contrato para filtrar en el tab no radicado
    self.consultar_contratista_filtro_radicado=function(value){

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ mcontrato:value, tipo:'8'};
         RequestGet(function (datos, estado, mensaje) {
          
            self.listado_contratista_filtro_radicado(datos.contratista);
           
         }, path, parameter);
         
    }


    //consultar los contrato de obra segun el macro y segun contratista para filtrar en el tab no radicado
    self.consultar_contrato_select_filtro_radicado=function(value1,value2){

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ mcontrato: value1, contratista:value2, tipo:'8,9,10,11,13,14,15'};
         RequestGet(function (datos, estado, mensaje) {
            
            self.listado_contrato_filtro_radicado(datos.contrato);

         }, path, parameter);

    }

    //consultar las cuenta por tipo por contrato y por empresa para llenar un select
    self.consultar_lista_cuenta=function(){
        
         path =path_principal+'/api/Financiero_cuenta/?sin_paginacion&format=json';

         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_cuenta_select(datos);
            cerrarLoading();
        }, path, parameter,undefined,false);   
    }

    //consultar en el modelo detalle giro para comparar con el archivo
    self.consulta_excel=function(){

        if (Encabezado_giroViewModel.error_validacion().length == 0) {//se activa las validaciones

            var data = new FormData();

                data.append('fecha_inicio',self.verificar_giroVO.fecha_ini());
                data.append('fecha_fin',self.verificar_giroVO.fecha_fin());
                data.append('cuenta',self.verificar_giroVO.cuenta_verif());

                for (var i = 0; i <  $('#archivo')[0].files.length; i++) {
                    data.append('archivo', $('#archivo')[0].files[i]); 
                    };
             
            var parametros={ 

                url:path_principal+'/giros/consultar_excel/',//url api 
                parametros:data,

                callback:function(datos, estado, mensaje){

                    self.listado_errores(datos); 
                    mensajeError(mensaje);                   
                        
                },alerta:false

            };
            
            self.limpiar_verificar_giro();
            RequestFormData2(parametros);

        }else{
            Encabezado_giroViewModel.error_validacion.showAllMessages();//mostramos las validacion

        }
    }



        //consultar proceso relacion
    self.consultar_idProcesoRelacion =function(obj){

        var idTablaReferencia=obj.id;
        var idApuntador=obj.contrato.id;
        var idProceso=0;

        path =path_principal+'/giros/consultar_procesos/';
        parameter={ idApuntador:idApuntador};
        RequestGet(function (datos, estado, mensaje) {

            if (datos!=null) {
                idProceso = datos
                //alert(idProceso);
                path = path_principal+'/api/procesoRelacion/?format=json'; 
                parameter={ proceso:idProceso, idApuntador:idApuntador, idTablaReferencia:idTablaReferencia };
                RequestGet(function (datos, estado, mensaje) {

                    //console.log(datos.data[0])

                    if (datos.data!=null && datos.data.length > 0) {
                  
                        self.idProcesoRelacion(datos.data[0].id);
                        location.href=path_principal+"/proceso/detalleSeguimientoProcesoDatos/"+self.idProcesoRelacion();

                    }else{

                         var path =path_principal+'/giros/guardar_procesos/';
                         var parameter = { proceso:idProceso, idApuntador:idApuntador, idTablaReferencia:idTablaReferencia, idProcesoRelacion:0};
                         RequestAnularOEliminar("El proceso no se encuentra implementado para este elemento, desea implementarlo ?", path, parameter, function (datos, estado, mensaje) {

                            //alert(datos)
                            location.href=path_principal+"/proceso/detalleSeguimientoProcesoDatos/"+datos;

                         })

                    }
                   
                }, path, parameter);
            }

        }, path, parameter);
         
    }

    self.consultar_lista_tipo_pago=function(){

         path =path_principal+'/api/Tipos/';
         parameter = { ignorePagination : 1 , aplicacion : 'encabezadoGiro_pago_recurso' };

         RequestGet(function (datos, estado, mensaje) {          
            
            self.listado_tipo_pago_recurso(datos);

        }, path, parameter ,undefined, false);
    }

    //actualizar tipo de pago del giro
    self.actualizar_tipo_de_pago_del_giro=function(obj){ 
        var count=0;
        // id del encabezado giro
        self.tipo_pago_del_giroVO.id([]); 

        ko.utils.arrayForEach(self.listado(),function(p){
            if (p.eliminado()) {
                count=1;
                self.tipo_pago_del_giroVO.id.push(p.id);
            };
        });

        if(count==0){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un giro para actualizar su tipo de pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
   
            var parametros={                     
                 callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.cargar(self.paginacion.pagina_actual())                      
                        self.checkall(false);
                    }                     
                 },//funcion para recibir la respuesta 
                 url: path_principal+'/giros/update_tipo_pago_del_giro/',//url api
                 parametros: self.tipo_pago_del_giroVO                         
            };
            RequestFormData(parametros);
        }            
     }


     self.actualizar_disparar_flujo_activo = function(obj){
        self.actualizar_disparar_flujo(obj,1);
     }

     self.actualizar_disparar_flujo_inactivo = function(obj){
        self.actualizar_disparar_flujo(obj,0);
     }


    //actualizar disparar_flujo
    self.actualizar_disparar_flujo = function(obj, disparar_flujo){ 

        // id del encabezado giro
        self.disparar_flujoVO.id(obj.id);
        self.disparar_flujoVO.disparar_flujo(disparar_flujo);

        string = 'disparar';
        if (disparar_flujo==0)
            string = 'detener'

        contenido = "Esta seguro que desea "+string+" el flujo del giro seleccionados?"

        $.confirm({
            title: 'Confirmar!',
            content: "<h4>" + contenido + "</h4>",
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {

                    var parametros={                     
                         callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                                self.cargar(self.paginacion.pagina_actual())                      
                                self.checkall(false);
                            }                     
                         },//funcion para recibir la respuesta 
                         url: path_principal+'/giros/update_disparar_flujo/',//url api
                         parametros: self.disparar_flujoVO                         
                    };
                    RequestFormData(parametros);
                
            }
        });
        
    }   


    // consulta polizas
    self.consultarPoliza = function (obj) {

        //console.log("id:"+obj.id)
        path = path_principal+'/api/VigenciaPoliza/?sin_paginacion=0&tipo_documento=giros&id_documento='+obj.id+'&lite=1&format=json';
        // path = path_principal+'/api/VigenciaPoliza/?sin_paginacion=0&id_documento=1&lite=1&format=json';
        parameter = {};

        RequestGet(function (datos, estado, mensage) {
            $('#modal_polizas').modal('show');

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensajePoliza('');
                self.listadoPoliza(agregarOpcionesObservable(datos));                   
                self.nombre_giro(obj.nombre.nombre)
            } else {
                self.listadoPoliza([]);
                self.nombre_giro(obj.nombre.nombre);
                self.mensajePoliza(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);
    }         
    



}



var encabezado_giro = new Encabezado_giroViewModel();
Encabezado_giroViewModel.errores_giros = ko.validation.group(encabezado_giro.encabezado_giroVO);
Encabezado_giroViewModel.error_validacion= ko.validation.group(encabezado_giro.verificar_giroVO);
Encabezado_giroViewModel.error_tipo_pago_del_giro = ko.validation.group(encabezado_giro.tipo_pago_del_giroVO);

ko.applyBindings(encabezado_giro);