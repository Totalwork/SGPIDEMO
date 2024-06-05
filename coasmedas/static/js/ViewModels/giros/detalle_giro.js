
function Detalle_giroViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.contrato_contratista=ko.observable(false);
    self.check_contratista=ko.observable(false);
    self.lista_proyecto=ko.observableArray([]);

    self.lista_select_contratista=ko.observableArray([]);
    self.lista_banco=ko.observableArray([]);
    self.lista_tipo_select=ko.observableArray([]);
    self.id_contrato=ko.observable('');
    self.lista_cuenta_select=ko.observableArray([]);
    self.lista_soporte_correspondencia=ko.observableArray([]);
    self.mcontrato=ko.observable(0);

    //observables del encabezado del detalle del giro
    self.contratista_encabezado=ko.observable('');
    self.contratante_encabezado=ko.observable('');
    self.contrato_id=ko.observable('');
    self.numero_contrato_encabezado=ko.observable('');
    self.nombre_anticipo_encabezado=ko.observable('');
    self.nombre_proyecto_encabezado=ko.observable('');
    self.suma_valor_detalles=ko.observable('');

    self.nombre_contratista_obra=ko.observable('');
    self.id_contratista_obra=ko.observable(0);
    self.nombre_banco_proyecto=ko.observable('');
    self.nombre_cuenta=ko.observable('');

    //Asociar autorizacion
    self.listado_prefijos = ko.observableArray([]);
    self.prefijo=ko.observable('');
    self.consecutivo=ko.observable('');
    self.ano=ko.observable(new Date().getFullYear());
    self.soporte_empresa_validacion=ko.observable('');
    
    //var num=0;
    //self.url=path_principal+'api/empresa';

    //funcion para ver mas de los proyectos
    self.ver_mas_proyectos = function (mcontrato,empresa,contrato_id) {

        self.titulo('Listado de los proyectos');
        self.listado_proyecto(mcontrato ,empresa ,contrato_id);
        $('#vermas_proyectos').modal('show');
    }  

     //Representa un modelo de la tabla detalle giro
    self.detalle_giroVO={
        id:ko.observable(0),
        no_cuenta:ko.observable('').extend({ required: { message: '(*)Digite el numero de la cuenta' } }),
        tipo_cuenta_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de cuenta' } }),
        valor_girar:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor a girar' } }),
        carta_autorizacion_id:ko.observable(''),
        fecha_pago:ko.observable(''),
        cuenta_id:ko.observable(''),
        test_op:ko.observable(''),
        fecha_pago_esperada:ko.observable(''),
        //soporte_autorizacion:ko.observable(''),
        codigo_pago:ko.observable(''),
        banco_id:ko.observable('').extend({ required: { message: '(*)Seleccione el banco' } }),
        contratista_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contratista' } }),
        encabezado_id:ko.observable(0),
        estado_id:ko.observable(1),
        cesion_id:ko.observable(''),
        cruce_id:ko.observable('')
     };

     //paginacion de detella del giro
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

    //Funcion para crear la paginacion del detalle del giro
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    //funciona para la paginacion del detalle del giro
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    //funcion para abri el modal detalle del giro
    self.abrir_modal = function () {

        self.limpiar();
        self.titulo('Registrar datos del giro');
        $('#modal_acciones').modal('show');
    }


    //funcion para abri el modal de aurotizacion del giro
    self.autorizacion_giro = function (empresa) {
        self.titulo('Asociar autorización del giro');
        self.consultar_prefijos_correspondencia(empresa);
        $('#modal_autorizacion').modal('show');
    }


    //funcion para abrir el modal de ver autorizacion
    self.abrir_ver_autorizacion = function (obj) {

        self.titulo('Soporte del consecutivo');

        self.consultar_listado_consecutivo_soporte(obj.carta_autorizacion.id);
        $('#modal_ver_autorizacion').modal('show');

    }


    //funcion para abri el mnodal de pagar el giro
    self.pagar_giro = function () {
        self.titulo('Pagar giro');
        self.limpiar();
        self.consultar_lista_cuenta();
        $('#modal_pagar_giro').modal('show');
    }


    // //limpiar el modelo 
     self.limpiar=function(){        
         
        self.detalle_giroVO.id(0);
        self.detalle_giroVO.no_cuenta('');
        self.detalle_giroVO.tipo_cuenta_id('');
        self.detalle_giroVO.valor_girar(0);
        self.detalle_giroVO.carta_autorizacion_id('');
        self.detalle_giroVO.fecha_pago('')
        self.detalle_giroVO.cuenta_id('');
        self.detalle_giroVO.test_op('');
        self.detalle_giroVO.fecha_pago_esperada('');
        //self.detalle_giroVO.soporte_autorizacion('');
        self.detalle_giroVO.codigo_pago('');
        self.detalle_giroVO.banco_id('');
        self.detalle_giroVO.contratista_id('');
        self.detalle_giroVO.estado_id(1);

        self.contrato_contratista(false);
        self.check_contratista(false); 

        self.detalle_giroVO.contratista_id.isModified(false);
        self.detalle_giroVO.banco_id.isModified(false);
        self.detalle_giroVO.no_cuenta.isModified(false);
        self.detalle_giroVO.tipo_cuenta_id.isModified(false);

        $('#archivo').fileinput('reset');
        $('#archivo').val('');      
     }


     //funcion para consultar presionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    //funcion consultar y traer los datos del detalle del giro
    self.consultar = function (pagina) {

        var encabezado_id=self.detalle_giroVO.encabezado_id();
        //alert(encabezado_id)

        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());

            path = path_principal+'/api/Detalle_giro/?format=json&page='+pagina;
            parameter = { dato: self.filtro(), pagina: pagina, encabezado_id:encabezado_id};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data)); 
                    //detalle_giro.encabezado_detalle(encabezado_id);
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

    //funcion para seleccionar los datos a eliminar del detalle del giro
    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    //funcion para consultar por id el detalle del giro
    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/Detalle_giro/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
             self.titulo('Actualizar Datos del giro');

            self.detalle_giroVO.id(datos.id);
            self.detalle_giroVO.contratista_id(datos.contratista.id);
            self.detalle_giroVO.banco_id(datos.banco.id);
            self.detalle_giroVO.no_cuenta(datos.no_cuenta);
            self.detalle_giroVO.tipo_cuenta_id(datos.tipo_cuenta.id);
            self.detalle_giroVO.valor_girar(datos.valor_girar);
            self.detalle_giroVO.encabezado_id(datos.encabezado.id);
            self.detalle_giroVO.estado_id(datos.estado.id);
            //self.detalle_giroVO.soporte_autorizacion(results.soporte_autorizacion);

             $('#modal_acciones').modal('show');

         }, path, parameter);

     }

    //funcion para eliminar el detalle del giro
    self.eliminar = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id.push({
                        id:d.id,
                        estado_id:d.estado.id
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un detalle del giro para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/giros/eliminar_id_detalle/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los detalles giros seleccionados?", path, parameter, function () {
                 self.encabezado_detalle();
                 self.consultar(1);
                 self.checkall(false);
             })

         }    
    }

   //exportar excel del detalle del giro
   self.exportar_excel=function(){
        var encabezado_id=detalle_giro.detalle_giroVO.encabezado_id();
        var contrato=0;
        var proyecto=0;
        location.href=path_principal+"/giros/exportar_detalle_giro?encabezado_id="+encabezado_id+"&contrato="+contrato+"&proyecto="+proyecto;
    }

    //funcion para seleccionar el contratista del contrato de la obra que se guardara el detalle del giro
    self.contrato_contratista.subscribe(function(value ){

        if(value==true){
            self.check_contratista(false);
            self.consultar_lista_contratista(false,value) 
        }else{
            self.detalle_giroVO.contratista_id('');
            self.detalle_giroVO.banco_id('');
            self.detalle_giroVO.no_cuenta('');
            self.detalle_giroVO.tipo_cuenta_id('');
        }
    });

    //funcion para seleccionar otro contratista
    self.check_contratista.subscribe(function(value ){

        if(value==true){
            self.contrato_contratista(false); 
        }

        self.consultar_lista_contratista(value,false)
        
    });

    //consultar los contratista para llenar el select
    self.consultar_lista_contratista=function(validacion,validacion2){

        if (validacion==true){

            path =path_principal+'/api/empresa/?esContratista=1&sin_paginacion&format=json';
             parameter='';
             RequestGet(function (datos, estado, mensaje) {
               
                self.lista_select_contratista(datos);

             }, path, parameter,undefined,false,false); 


        }else if ((validacion==false || validacion==undefined) && (validacion2==false || validacion2==undefined)){

             path =path_principal+'/api/empresa/?esProveedor=1&sin_paginacion&format=json';
             parameter='';
             RequestGet(function (datos, estado, mensaje) {
               
                self.lista_select_contratista(datos);

             }, path, parameter,undefined,false,false); 
        }

        if(validacion2 ==true){

            path =path_principal+'/api/Encabezado_giro/?sin_paginacion&format=json';
            parameter = {encabezado_id:self.detalle_giroVO.encabezado_id()};
             RequestGet(function (datos, estado, mensaje) {
               
                self.nombre_contratista_obra(datos[0].contrato.contratista.nombre);
                self.detalle_giroVO.contratista_id(datos[0].contrato.contratista.id);

             }, path, parameter,undefined,false,false);


            path =path_principal+'/proyecto/list_proyecto_contrato/';
            parameter = {contrato_id:self.id_contrato(),encabezado_id:self.detalle_giroVO.encabezado_id()};
             RequestGet(function (datos, estado, mensaje) {
               
                self.nombre_banco_proyecto(datos[0].entidad_bancaria__nombre);
                self.detalle_giroVO.banco_id(datos[0].entidad_bancaria__id);
                self.detalle_giroVO.no_cuenta(datos[0].No_cuenta);
                self.detalle_giroVO.tipo_cuenta_id(datos[0].tipo_cuenta__id);

             }, path, parameter,undefined,false,false);  
        }
    
    }

    //consultar los banco para llenar un select
    self.consultar_lista_banco=function(){
        
         path =path_principal+'/api/Banco/?ignorePagination';
         parameter='';
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_banco(datos);

         }, path, parameter,undefined,false,false);
    }

    //consultar los tipos para llenar un select
    self.consultar_lista_tipo=function(){
        
         path =path_principal+'/api/Tipos/?ignorePagination=1';
         parameter={ aplicacion: 'cuenta' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_tipo_select(datos);

         }, path, parameter,undefined,false,false);
    }

    // //funcion guardar y actualizar el detalle del giro
     self.guardar=function(){

        if (Detalle_giroViewModel.errores_giros_detalle().length == 0) {//se activa las validaciones

            if(self.detalle_giroVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Detalle_giro/',//url api
                     parametros:self.detalle_giroVO,
                     completado:function(){
                         self.encabezado_detalle();
                       }                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{

                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.limpiar();
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Detalle_giro/'+self.detalle_giroVO.id()+'/',
                        parametros:self.detalle_giroVO,
                        completado:function(){
                         self.encabezado_detalle();
                       }                           
                  };

                  RequestFormData(parametros);
            }

        } else {
             Detalle_giroViewModel.errores_giros_detalle.showAllMessages();//mostramos las validacion
        }
     }

    //consultar los encabezado del giro
    self.encabezado_detalle=function(){

        var encabezado_id=self.detalle_giroVO.encabezado_id();

         path =path_principal+'/giros/encabezado_detalle/';
         parameter={ encabezado_id: encabezado_id ,contrato:0, proyecto:0};
         RequestGet(function (datos, estado, mensaje) {

            if(datos.length>0){

                self.contratista_encabezado(datos[0].nombre_contratista);
                self.contratante_encabezado(datos[0].nombre_contratante);
                self.numero_contrato_encabezado(datos[0].numero_contrato);
                self.nombre_anticipo_encabezado(datos[0].giro_nombre);
                self.nombre_proyecto_encabezado(datos[0].nombre_proyecto);
                self.suma_valor_detalles(datos[0].suma_valor_detalles);
                // alert(datos[0].contrato_id)
                self.contrato_id(datos[0].contrato_id);
            }

         }, path, parameter,undefined,false,false);
    }

    //consultar las cuenta por tipo por contrato y por empresa para llenar un select
    self.consultar_lista_cuenta=function(){

        //var tipo='cuenta';  
         path =path_principal+'/api/Financiero_cuenta/?mcontrato='+self.mcontrato()+'&sin_paginacion&format=json';

         RequestGet(function (datos, estado, mensaje) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
       
                self.lista_cuenta_select(datos);

            } else {
                self.lista_cuenta_select([]);
                
            }         
            // self.detalle_giroVO.cuenta_id(datos[0].id);
            // self.nombre_cuenta(datos[0].nombre)

         }, path, parameter,undefined,false,false); 
    }

    //guarda los pagos de los detalle del giro
    self.guardar_pago = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las transacciones para guardar el pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false  
        }


        if(self.detalle_giroVO.cuenta_id()==0 || self.detalle_giroVO.fecha_pago()==''){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Digite la fecha del pago y seleccione la cuenta.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false  
        }


        if(self.detalle_giroVO.cuenta_id()!=0 && self.detalle_giroVO.fecha_pago()!='' && count>0){

             var path =path_principal+'/giros/pago_detalle/';
             var parameter = { lista: lista_id,cuenta:self.detalle_giroVO.cuenta_id()
                ,fecha_pago:self.detalle_giroVO.fecha_pago(),numero_contrato:self.numero_contrato_encabezado(), 
                anticipo:self.nombre_anticipo_encabezado()  };
             RequestAnularOEliminar("Esta seguro que desea guardar los pagos de las transacciones seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
                 $('#modal_pagar_giro').modal('hide');
             })

         }   
    }

    //reversar los detalles del giros
    self.reversar_giros = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las transacciones.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/giros/reversar_giros/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea reversar las transacciones seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }    
    }

    //Autorizacion del giro
    self.autorizar_giros = function () {

        var empresa=$("#empresa").val();

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las transacciones.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false 
        }


        if((self.consecutivo()==0 || self.consecutivo()=='') || (self.ano()==0 || self.ano()=='') || (self.prefijo()==0 || self.prefijo()=='') ){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Todos los campos son requeridos.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false  
        }


        if(self.consecutivo()!='' && self.ano()!='' && count>0 && (self.prefijo()!=0 && self.prefijo()!='') ){

             var path =path_principal+'/giros/autorizar_giros/';
             var parameter = { lista: lista_id, numero:self.consecutivo(), ano:self.ano(), empresa:empresa , prefijo:self.prefijo() };
             RequestAnularOEliminar("Esta seguro que desea autorizar las transacciones seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
                 $('#modal_autorizacion').modal('hide');
                 self.limpiar();
                 self.consecutivo('');
             })
        }   
    }

    //desautorizar los giros
    self.desautorizar_giros = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las transacciones.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/giros/desautorizar_giros/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea desautorizar las transacciones seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }   
    }

    //funcion consultar y traer los datos del detalle del giro
    self.consultar_listado_consecutivo_soporte = function (correspondencia_id) {

        path =path_principal+'/api/CorrespondenciaSoporte/?correspondencia='+correspondencia_id+'&ignorePagination&format=json';
        parameter='';
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                $("#mensajeListadoSoporte").html('');
                self.lista_soporte_correspondencia(datos);

            } else {
                self.lista_soporte_correspondencia([]);
                $("#mensajeListadoSoporte").html('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning fa-2x"></i>No se encontraron soportes relacionados con el consecutivo.</div>');
            }

        }, path, parameter);
    }

    self.autorizar_giros_sin_consecutivos=function(){

        var empresa=$("#empresa").val();

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {

            if(d.eliminado()==true){
                if(lista_id==''){
                    lista_id=d.id;
                }else{
                    lista_id=lista_id+','+d.id;
                }
            }

         });


        if(self.soporte_empresa_validacion()==undefined || self.soporte_empresa_validacion()=='' || lista_id==''){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione el soporte y la transaccion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false  
        }

        var data = new FormData();

            data.append('archivo', $('#archivo')[0].files[0]);
            data.append('lista',lista_id);
         
            var parametros={ 

                url:path_principal+'/giros/actualizar_estado_detalle/',//url api 
                parametros:data,

                callback:function(datos, estado, mensaje){

                    if (estado=='ok') {
                        self.consultar(1);
                        self.checkall(false);
                        $('#modal_autorizacion').modal('hide');
                        self.limpiar();
                        mensajeExitoso(mensaje); 
                    }                    
                        
                },alerta:false

            };
            
            RequestFormData2(parametros);
    }       

    //ver mas proyectos
    self.listado_proyecto=function(mcontrato,empresa,contrato_id){
        
        path = path_principal+'/api/Proyecto_empresas/?format=json';
        parameter={ mcontrato: mcontrato, empresa:empresa , parametro_consulta_giro : 1 , contrato:contrato_id};
        RequestGet(function (datos, estado, mensaje) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje('');
                self.lista_proyecto(datos.data); 

            } else {
                self.lista_proyecto([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
            
        }, path, parameter);
    }


    //correspondencia - prefijos de la empresa
    self.consultar_prefijos_correspondencia=function(empresa) {
    
        path = path_principal+'/api/CorrespondenciaPrefijo/?format=json';
        parameter = { empresa: empresa, dato: self.filtro() , ignorePagination:1 , estado:1/*estado true:1 - false:0*/};
        RequestGet(function (datos, estado, mensaje) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.listado_prefijos(datos); 
            } else {
                self.listado_prefijos([]);
            }
            
        }, path, parameter);

    }

    self.ver_soporte = function(obj) {
      window.open(path_principal+"/correspondencia/ver-soporte/?id="+ obj.id, "_blank");
    }


}

var detalle_giro = new Detalle_giroViewModel();
Detalle_giroViewModel.errores_giros_detalle = ko.validation.group(detalle_giro.detalle_giroVO);
ko.applyBindings(detalle_giro);

