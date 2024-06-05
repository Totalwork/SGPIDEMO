
function CesionEconomicaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.listado_estado=ko.observableArray([]);
    self.listado_contratista=ko.observableArray([]);
    self.listado_mcontrato=ko.observableArray([]);
    self.listado_contrato=ko.observableArray([]);
    self.mcontrato_fil=ko.observable(0);
    self.contratista_fil=ko.observable(0);
    self.mcontrato_fil2=ko.observable(0);
    self.mcontrato_guar=ko.observable(0);
    self.archivo1=ko.observable('');
    self.contrato_comparar=ko.observable(0);
    self.listado_mcontrato2=ko.observableArray([]);
    self.validacion_aprovada=ko.observable(0);

    self.listado_contrato_select=ko.observableArray([]);
    self.listado_proveedor=ko.observableArray([]);
    self.listado_banco=ko.observableArray([]);
    self.listado_tipo_cuenta=ko.observableArray([]);
    self.listado_nombre_giro=ko.observableArray([]);
    self.macroid=ko.observable(0);
    self.nombregiro=ko.observable(0);


    //observables para el ver mas de la cesion
    self.contrato_vermas=ko.observable('');
    self.proveedor_vermas=ko.observable('');
    self.tipo_cuenta_vermas=ko.observable('');
    self.estado_vermas=ko.observable('');
    self.banco_vermas=ko.observable('');
    self.nombre_giro_vermas=ko.observable('');
    self.valor_vermas=ko.observable('');
    self.numero_cuenta_vermas=ko.observable('');
    self.motivo_rechazo=ko.observable('');
    self.fecha_tramite_vermas=ko.observable('');
    self.fecha_enaprobacion_vermas=ko.observable('');
    self.fecha_aprobada_vermas=ko.observable('');
    self.soporte_vermas_tramite=ko.observable('');
    self.soporte_vermas_enaprobacion=ko.observable('');
    self.soporte_vermas_aprobado=ko.observable('');
    

     //Representa el modelo de cesion economica
    self.cesion_economicaVO={
        id:ko.observable(0),
        contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contrato' } }),
        proveedor_id:ko.observable('').extend({ required: { message: '(*)Seleccione el proveedor' } }),
        tipo_cuenta_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de cuenta' } }),
        estado_id:ko.observable(112),
        banco_id:ko.observable('').extend({ required: { message: '(*)Seleccione el banco' } }),
        nombre_giro_id:ko.observable('').extend({ required: { message: '(*)Seleccione el nombre del giro' } }),
        valor:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor' } }),
        numero_cuenta:ko.observable('').extend({ required: { message: '(*)Digite el numero de la cuenta' } }),
        motivo_rechazo:ko.observable(''),
        observacion:ko.observable(''),      
        fecha_tramite:ko.observable(''),
        fecha_enaprobacion:ko.observable(''),
        fecha_aprobada:ko.observable(''),
        soporte_tramite:ko.observable(''),
        soporte_enaprobacion:ko.observable(''),
        soporte_aprobado:ko.observable(''),

     };

     //paginacion de la cesion economica
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

    //paginacion
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina)
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }


    //funcion para abrir modal de cesion economica
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Cesion');
        $('#modal_acciones').modal('show');
    }


    //funcion para filtrar las cesiones
    self.filtrar_cesion = function () {
        self.titulo('Filtrar Cesion');
        //self.limpiar();
        self.consultar_macrocontrato();
        self.consultar_lista_estado();
        $('#modal_filtro').modal('show');
    }


    //funcion para ver mas detalle de la cesion 
    self.ver_mas_detalle = function (obj) {
        self.titulo('Detalle de la cesion');
        self.ver_mas_cesion(obj);
        $('#vermas_detalle').modal('show');
    }


     //limpiar el modelo de la cesion economica
     self.limpiar=function(){     
         
         self.cesion_economicaVO.id(0);
         self.cesion_economicaVO.valor(0);
         self.cesion_economicaVO.contrato_id(0);
         self.cesion_economicaVO.proveedor_id(0);
         self.cesion_economicaVO.tipo_cuenta_id(0);
         //self.cesion_economicaVO.estado_id(0);
         self.cesion_economicaVO.banco_id(0)
         self.cesion_economicaVO.nombre_giro_id(0);
         self.cesion_economicaVO.numero_cuenta('');
         self.cesion_economicaVO.soporte_tramite('');
         self.cesion_economicaVO.soporte_enaprobacion('');
         self.cesion_economicaVO.soporte_aprobado('');
         self.cesion_economicaVO.fecha_tramite('');
         self.cesion_economicaVO.fecha_enaprobacion('');
         self.cesion_economicaVO.fecha_aprobada('');
         self.cesion_economicaVO.motivo_rechazo('');
         self.cesion_economicaVO.observacion('');
         self.nombregiro(0);
         
         
        $('#archivo').fileinput('reset');
        $('#archivo').val('');  

        $('#archivo2').fileinput('reset');
        $('#archivo2').val('');

        $('#archivo3').fileinput('reset');
        $('#archivo3').val('');       
     }


    //consultar los contrato para llenar un select
    self.consultar_macrocontrato2=function(){
        
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12' };
         RequestGet(function (datos, estado, mensaje) {
            self.listado_mcontrato2(datos.macrocontrato);

         }, path, parameter,undefined,false,false);
    }


    //funcion que se ejecuta cuando se cambia en el select de contrato 
    self.mcontrato_fil2.subscribe(function (value) {

        if(value >0){
            self.select_contrato(value);
            //self.select_nombregiro(value);

        }
    });


    //consultar los contrato para llenar un select
    self.select_contrato=function(value){
        
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ mcontrato: value,tipo:'8,9,10,11,13,14,15', valida:1};
         RequestGet(function (datos, estado, mensaje) {
           
            self.listado_contrato_select(datos.contrato);

         }, path, parameter,undefined,false,false);
    }


    //funcion que se ejecuta cuando se cambia en el select de contrato 
    self.cesion_economicaVO.contrato_id.subscribe(function (value) {

        if(value >0){
            self.select_idcontrato(value);
        }
    });


    //para obtener el macrocontrato del contrato
    self.select_idcontrato=function(idcontrato){
        
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ idcontrato: idcontrato};
         RequestGet(function (datos, estado, mensaje) {

            //self.macroid(datos.contrato[0].mcontrato_id);

            self.select_nombregiro(datos.contrato[0].mcontrato_id);

         }, path, parameter,undefined,false,false);
    }


    // self.macroid.subscribe(function (value) {

    //     alert(value)

    //     if(value >0){
    //         self.select_nombregiro(value);

    //     }else{
    //         self.listado_nombre_giro([]);
    //     }

    // });



    //consultar los proveedor para llenar un select
    self.select_proveedor=function(){
        
         path =path_principal+'/api/empresa/?sin_paginacion';
         parameter={ esProveedor: '1' };
         RequestGet(function (datos, estado, mensaje) {

            self.listado_proveedor(datos);

         }, path, parameter,undefined,false,false);
    }


    //consultar los banco para llenar un select
    self.select_banco=function(){
        
         path =path_principal+'/api/Banco/?ignorePagination';
         parameter={ };
         RequestGet(function (datos, estado, mensaje) {
           
            self.listado_banco(datos);

         }, path, parameter,undefined,false,false);
    }


        //consultar los tipo de cuenta para llenar un select
    self.select_tipocuenta=function(){
        
         path =path_principal+'/api/Tipos/';
         parameter={ aplicacion: 'cuenta' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.listado_tipo_cuenta(datos.data);

         }, path, parameter,undefined,false,false);
    }

        //consultar los nombre del giro para llenar un select
    self.select_nombregiro=function(contrato){
        
         path =path_principal+'/api/Nombre_giro/';
         parameter={contrato:contrato };
         RequestGet(function (datos, estado, mensaje) {

            console.log(datos.data)
           
            self.listado_nombre_giro(datos.data);

         }, path, parameter,function(){

          self.cesion_economicaVO.nombre_giro_id(self.nombregiro());


         });
    }


    //consultar los estados para llenar un select
    self.consultar_lista_estado=function(){
        
         path =path_principal+'/api/Estados?ignorePagination';
         parameter={ dato: 'CesionEconomica' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.listado_estado(datos);

         }, path, parameter,undefined,false,false);

    }


    //consultar los contrato para llenar un select
    self.consultar_macrocontrato=function(){
        
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12' };
         RequestGet(function (datos, estado, mensaje) {
            self.listado_mcontrato(datos.macrocontrato);

         }, path, parameter,undefined,false,false);
    }


    //funcion que se ejecuta cuando se cambia en el select de contrato 
    self.mcontrato_fil.subscribe(function (value) {

        if(value >0){
            self.consultar_contratista(value);
            self.consultar_contrato(value,0);

        }else{

            self.listado_contratista([]);
            self.listado_contrato([]);
        }
    });

    //consultar los nombre de los contratista segun el macrocontrat
    self.consultar_contratista=function(value){

         //path =path_principal+'/contrato/list_contrato_select/?mcontrato='+value+'&contratista=0';
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ mcontrato:value, tipo:'8'};
         RequestGet(function (datos, estado, mensaje) {
          
            self.listado_contratista(datos.contratista);
           
         }, path, parameter);
         
    }


    //funcion que se ejecuta cuando se cambia en el select de contratista para filtrar los contrato de obra segun macrocontrato y contratista
    self.contratista_fil.subscribe(function (value) {
       
        if(value >0){
            self.consultar_contrato(self.mcontrato_fil(),value);

        }
    });



    //consultar los contrato de obra segun el macro y segun contratista
    self.consultar_contrato=function(value1,value2){
       
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ mcontrato: value1, contratista:value2, tipo:'8,9,10,11,13,14,15'};
         RequestGet(function (datos, estado, mensaje) {
            
            self.listado_contrato(datos.contrato);

         }, path, parameter);

    }


        //funcion para abrir modal en aprobacion
    self.abrir_modal_enaprobacion = function (obj) {

        self.limpiar();
        self.cesion_economicaVO.id(obj.id);
        self.titulo('Generar formato en aprobacion');
        $('#modal_enaprobacion').modal('show');
    }


            //funcion para abrir modal en aprobacion
    self.abrir_modal_aprobacion = function (obj) {

        //self.limpiar();

        self.validacion_aprovada(0);

        self.cesion_economicaVO.id(obj.id);
        self.cesion_economicaVO.contrato_id(obj.contrato.id);
        self.cesion_economicaVO.proveedor_id(obj.proveedor.id);
        self.cesion_economicaVO.tipo_cuenta_id(obj.tipo_cuenta.id);
        self.cesion_economicaVO.banco_id(obj.banco.id);
        self.cesion_economicaVO.numero_cuenta(obj.numero_cuenta);
        self.cesion_economicaVO.valor(obj.valor);

        self.nombregiro(obj.nombre_giro.id);

        self.titulo('Aprobar o Rechazar');
        $('#modal_aprobacion').modal('show');
    }


      self.guardar=function(){

        if (CesionEconomicaViewModel.errores_cesion_economica().length == 0) {//se activa las validaciones

            if(self.cesion_economicaVO.id()==0){

                var data = new FormData();

                data.append('valor',self.cesion_economicaVO.valor());
                data.append('contrato_id',self.cesion_economicaVO.contrato_id());
                data.append('proveedor_id',self.cesion_economicaVO.proveedor_id());
                data.append('tipo_cuenta_id',self.cesion_economicaVO.tipo_cuenta_id());
               // data.append('estado_id',estado);
                data.append('banco_id',self.cesion_economicaVO.banco_id());
                data.append('nombre_giro_id',self.cesion_economicaVO.nombre_giro_id());
                data.append('numero_cuenta',self.cesion_economicaVO.numero_cuenta());

                data.append('archivo', $('#archivo')[0].files[0]);


                var parametros={                     
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                                
                    },//funcion para recibir la respuesta 
                        url:path_principal+'/api/CesionEconomica/',//url api
                        parametros:data,
                        completado:function(){
                            //self.encabezado();
                        }                          
                };
                RequestFormData2(parametros);

            }else{

                var data = new FormData();

                data.append('valor',self.cesion_economicaVO.valor());
                data.append('contrato_id',self.cesion_economicaVO.contrato_id());
                data.append('proveedor_id',self.cesion_economicaVO.proveedor_id());
                data.append('tipo_cuenta_id',self.cesion_economicaVO.tipo_cuenta_id());
               // data.append('estado_id',estado);
                data.append('banco_id',self.cesion_economicaVO.banco_id());
                data.append('nombre_giro_id',self.cesion_economicaVO.nombre_giro_id());
                data.append('numero_cuenta',self.cesion_economicaVO.numero_cuenta());

                data.append('archivo[]', $('#archivo')[0].files[0]);

                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.limpiar();
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/CesionEconomica/'+self.cesion_economicaVO.id()+'/',
                       parametros:data                      
                  };

                  RequestFormData2(parametros);
            }

         } else {
            CesionEconomicaViewModel.errores_cesion_economica.showAllMessages();//mostramos las validacion
         } 
    }
    

    //funcion consultar las cesiones economica
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            
            self.filtro($('#txtBuscar').val());
            var estado=$("#estado_filtrar").val();
            var contratista=$("#contratista_filtro").val();
            var mcontrato=$("#mcontrato_filtro").val();
            var contrato=$("#contrato_filtro").val();

            path = path_principal+'/api/CesionEconomica?format=json';
            parameter = { dato: self.filtro(), page: pagina,estado:estado, contratista:contratista, contrato:contrato, mcontrato:mcontrato};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    $('#modal_filtro').modal('hide'); 
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
    }


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    //consultar por id de la cesion
    self.consultar_por_id = function (obj) {
       
       path =path_principal+'/api/CesionEconomica/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar Movimiento');

           // self.mcontrato_fil2(datos.contrato.mcontrato.id);

            self.cesion_economicaVO.id(datos.id);
            self.cesion_economicaVO.valor(datos.valor);
            self.cesion_economicaVO.contrato_id(datos.contrato.id);
            self.cesion_economicaVO.proveedor_id(datos.proveedor.id);
            self.cesion_economicaVO.tipo_cuenta_id(datos.tipo_cuenta.id);
            self.cesion_economicaVO.estado_id(datos.estado.id);
            self.cesion_economicaVO.banco_id(datos.banco.id);
            //self.cesion_economicaVO.nombre_giro_id(datos.nombre_giro.id);

            //alert(datos.nombre_giro.id)
            
            self.nombregiro(datos.nombre_giro.id);

            self.cesion_economicaVO.numero_cuenta(datos.numero_cuenta);
            self.cesion_economicaVO.fecha_tramite(datos.fecha_tramite);
            self.cesion_economicaVO.fecha_enaprobacion(datos.fecha_enaprobacion);
            self.cesion_economicaVO.fecha_aprobada(datos.fecha_aprobada);
            self.cesion_economicaVO.soporte_tramite(datos.soporte_tramite);
            self.cesion_economicaVO.soporte_enaprobacion(datos.soporte_enaprobacion);
            self.cesion_economicaVO.soporte_aprobado(datos.soporte_aprobado);
             
             $('#modal_acciones').modal('show');

         }, path, parameter);

     }


     //para colocar en estado en aprobacion
    self.guardar_enaprobacion=function(){

        var data = new FormData();

        if (self.cesion_economicaVO.soporte_enaprobacion()=='' || self.cesion_economicaVO.soporte_enaprobacion()=='') {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione el soporte.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false
        }

        data.append('id',self.cesion_economicaVO.id());
        data.append('archivo', $('#archivo2')[0].files[0]);

        var parametros={                     
            callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                    self.consultar(self.paginacion.pagina_actual());
                    $('#modal_enaprobacion').modal('hide');
                }                        
                        
            },//funcion para recibir la respuesta 
                url:path_principal+'/cesion_economica/actualizar_enaprobacion/',//url api
                parametros:data,
                completado:function(){
                    //self.encabezado();
                }                          
        };
        RequestFormData2(parametros);
    }


    self.actualizar_cesion_estado = function(obj){

        self.actualizar_anulada(obj);
     } 


    //actualizar anulada
    self.actualizar_anulada=function(obj){

        $.confirm({
            title: 'Confirmar!',
            content: "<h4>Esta seguro que desea anular esta cesion?</h4>",
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {

                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.consultar(self.paginacion.pagina_actual());
                        }                     
                     },//funcion para recibir la respuesta 
                     url: path_principal+'/cesion_economica/actualizar_anulada/',//url api
                     parametros:{id:obj.id,nombregiro:obj.nombre_giro.id,contratoid:obj.contrato.id,proveedor:obj.proveedor.id,
                        tipo_cuenta:obj.tipo_cuenta.id,banco:obj.banco.id,numero_cuenta:obj.numero_cuenta}                        
                };
                Request(parametros);
                
            }
        });            

     }


    //trae los datos para la opcion ver mas de la cesion
    self.ver_mas_cesion=function(obj){
        
         path =path_principal+'/api/CesionEconomica?sin_paginacion&format=json';
         parameter={ idcesion: obj.id};
         RequestGet(function (datos, estado, mensaje) {
            
            self.contrato_vermas(datos[0].contrato.nombre);
            self.proveedor_vermas(datos[0].proveedor.nombre);
            self.tipo_cuenta_vermas(datos[0].tipo_cuenta.nombre);
            self.estado_vermas(datos[0].estado.nombre);
            self.banco_vermas(datos[0].banco.nombre);
            self.nombre_giro_vermas(datos[0].nombre_giro.nombre);
            self.valor_vermas(datos[0].valor);
            self.numero_cuenta_vermas(datos[0].numero_cuenta);
            self.motivo_rechazo(datos[0].motivo_rechazo);           
            self.fecha_tramite_vermas(datos[0].fecha_tramite);
            self.fecha_enaprobacion_vermas(datos[0].fecha_enaprobacion);
            self.fecha_aprobada_vermas(datos[0].fecha_aprobada);
            self.soporte_vermas_tramite(datos[0].soporte_tramite);
            self.soporte_vermas_enaprobacion(datos[0].soporte_enaprobacion);
            self.soporte_vermas_aprobado(datos[0].soporte_aprobado);


         }, path, parameter);

    }


   self.guardar_aprobacion=function(){

        if (self.cesion_economicaVO.soporte_aprobado()=='') {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione el soporte.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false
        }

       $.confirm({
            title: 'Confirmar!',
            content: "<h4>Desea aprobar esta cesion economica?</h4>",
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {

                path =path_principal+'/cesion_economica/validacion_aprobada/';
                parameter = {contrato:self.cesion_economicaVO.contrato_id()};
                RequestGet(function (datos, estado, mensage) {

                    if (datos<=0){

                        if (self.cesion_economicaVO.observacion()=='') {

                             var mensaje= 'El contrato no tiene el saldo suficiente para ejecutar la cesion,¿esta seguro que desea continuar? en caso que su respuesta sea afirmativa, por favor digite la observacion';

                            $.confirm({
                                title:'Informativo',
                                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>'+mensaje+'<h4>',
                                cancelButton: 'Cerrar',
                                confirmButton: false
                            });
                            return false
                        }


                        var data = new FormData();

                        data.append('id',self.cesion_economicaVO.id());
                        data.append('archivo', $('#archivo3')[0].files[0]);
                        data.append('nombregiro',self.nombregiro()); 
                        data.append('contratoid',self.cesion_economicaVO.contrato_id());
                        data.append('proveedor',self.cesion_economicaVO.proveedor_id());   
                        data.append('tipo_cuenta',self.cesion_economicaVO.tipo_cuenta_id());   
                        data.append('banco',self.cesion_economicaVO.banco_id());   
                        data.append('numero_cuenta',self.cesion_economicaVO.numero_cuenta());   
                        data.append('valor',self.cesion_economicaVO.valor());      
                        data.append('observacion',self.cesion_economicaVO.observacion());

                        var parametros={                     
                             callback:function(datos, estado, mensaje){
                                if (estado=='ok') {
                                console.log(datos.file);
                                    self.consultar(1);
                                    $('#modal_aprobacion').modal('hide');
                                    self.limpiar(); 
                                   
                                }                     
                             },//funcion para recibir la respuesta 
                             url: path_principal+'/cesion_economica/actualizar_aprobada/',//url api
                             parametros: data                         
                        };
                        RequestFormData2(parametros);

                    }else{

                        var data = new FormData();

                        data.append('id',self.cesion_economicaVO.id());
                        data.append('archivo', $('#archivo3')[0].files[0]);
                        data.append('nombregiro',self.nombregiro());
                        data.append('contratoid',self.cesion_economicaVO.contrato_id()); 
                        data.append('observacion',self.cesion_economicaVO.observacion());

                        var parametros={                     
                             callback:function(datos, estado, mensaje){
                                if (estado=='ok') {
                                console.log(datos.file);
                                    self.consultar(1);
                                    $('#modal_aprobacion').modal('hide');
                                    self.limpiar(); 
                                   
                                }                     
                             },//funcion para recibir la respuesta 
                             url: path_principal+'/cesion_economica/actualizar_aprobada/',//url api
                             parametros: data                         
                        };
                        RequestFormData2(parametros);
                    }

                }, path, parameter);
      
            }
        });    
     }



    //actualizar a rechazado
    self.guardar_rechazo=function(){

        if (self.cesion_economicaVO.motivo_rechazo()=='') {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Digite el motivo del rechazo.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false
        }

        $.confirm({
            title: 'Confirmar!',
            content: "<h4>Esta seguro que desea rechazar esta cesion?</h4>",
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {

                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_aprobacion').modal('hide');
                            self.limpiar(); 
                        }                     
                     },//funcion para recibir la respuesta 
                     url: path_principal+'/cesion_economica/actualizar_rechazado/',//url api
                     parametros:{id:self.cesion_economicaVO.id(), motivo:self.cesion_economicaVO.motivo_rechazo()}                        
                };
                Request(parametros);
                
            }
        });            

     } 

}

var cesion_economica = new CesionEconomicaViewModel();
CesionEconomicaViewModel.errores_cesion_economica = ko.validation.group(cesion_economica.cesion_economicaVO);
ko.applyBindings(cesion_economica);
