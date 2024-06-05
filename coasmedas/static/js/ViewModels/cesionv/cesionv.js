
function CesionVViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.listado_mcontrato=ko.observableArray([]);
    self.listado_contrato_select=ko.observableArray([]);
    self.select_nombregiro=ko.observableArray([]);
    self.listado_contrato_select=ko.observableArray([]);

    self.listado_contratista=ko.observableArray([]);
    self.listado_banco=ko.observableArray([]);
    self.listado_tipo_cuenta=ko.observableArray([]);
    self.listado_nombre_giro=ko.observableArray([]);
    self.listado_estado=ko.observableArray([]);
    self.listado_contrato=ko.observableArray([]);
    self.listado_mcontrato2=ko.observableArray([]);
    self.listado_beneficiario=ko.observableArray([]);
    self.listado_agregar=ko.observableArray([]);

    self.mcontrato_fil=ko.observable(0);
    self.contratista_fil=ko.observable(0);
    self.desde=ko.observable('');
    self.hasta=ko.observable('');
    self.contrato_registrar=ko.observable(0);
    self.mcontrato_fil2=ko.observable(0);
    self.archivo2=ko.observable('');
    self.valor_registra=ko.observable('');
    self.checkall=ko.observable(false);
    

     //Representa el modelo de cesion
    self.cesionv_VO={
        id:ko.observable(0),
        contratista_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contratista' } }),
        estado_id:ko.observable(147),
        fecha_carta:ko.observable('').extend({ required: { message: '(*)Seleccione la fecha' } }),
        soporte_solicitud:ko.observable('').extend({ required: { message: '(*)Seleccione el soporte' } }),

     };


    //Representa el modelo de detalle de la cesion
    self.detallecesion_VO={
        id:ko.observable(0),
        cesion_id:ko.observable(0),
        contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contrato' } }),
        nombre_giro_id:ko.observable('').extend({ required: { message: '(*)Seleccione el giro' } }),
        beneficiario_id:ko.observable('').extend({ required: { message: '(*)Seleccione el beneficiario' } }),
        banco_id:ko.observable('').extend({ required: { message: '(*)Seleccione el banco' } }),
        tipo_cuenta_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de cuenta' } }),
        estado_id:ko.observable(0),
        numero_cuenta:ko.observable('').extend({ required: { message: '(*)Digite el numero de la cuenta' } }),
        valor:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor' } }),
        correo_verificacion:ko.observable(''),
        carta_rechazo_aprobacion:ko.observable(''),
     };

     //paginacion de la cesion
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


    //funcion para abrir modal de cesion
    self.abrir_modal = function () {
        self.limpiar();
        //self.consultar_macrocontrato2();
        self.select_beneficiario();
        self.select_banco();
        self.select_tipocuenta();
        self.listado_agregar([]);
        self.titulo('Registrar Cesion');
        $('#modal_acciones').modal('show');
    }


    //funcion para filtrar 
    self.filtrar_cesion = function () {
        self.limpiar();
        self.titulo('Filtrar Cesion');
        self.consultar_macrocontrato();
        self.consultar_lista_estado();
        $('#modal_filtro').modal('show');
    }



     //limpiar el modelo de la cesion
    self.limpiar=function(){     
         
         self.cesionv_VO.id(0);
         self.cesionv_VO.contratista_id('');
         self.cesionv_VO.fecha_carta('');
         self.cesionv_VO.estado_id(0);
         self.cesionv_VO.soporte_solicitud('');


        self.detallecesion_VO.contrato_id('');
        self.detallecesion_VO.nombre_giro_id('');
        self.detallecesion_VO.beneficiario_id('');
        self.detallecesion_VO.banco_id('');
        self.detallecesion_VO.tipo_cuenta_id('');
        self.detallecesion_VO.estado_id(0);
        self.detallecesion_VO.numero_cuenta('');
        self.detallecesion_VO.valor(0);
        self.detallecesion_VO.correo_verificacion('');
        self.detallecesion_VO.carta_rechazo_aprobacion('');
              
        $('#archivo').fileinput('reset');
        $('#archivo').val('');

        $('#archivo2').fileinput('reset');
        $('#archivo2').val('');      
    }

    self.limpiarDetalle=function(){
        self.detallecesion_VO.contrato_id('');
        self.detallecesion_VO.nombre_giro_id('');
        self.detallecesion_VO.beneficiario_id('');
        self.detallecesion_VO.banco_id('');
        self.detallecesion_VO.tipo_cuenta_id('');
        self.detallecesion_VO.estado_id(0);
        self.detallecesion_VO.numero_cuenta('');
        self.detallecesion_VO.valor(0);
        self.detallecesion_VO.correo_verificacion('');
        self.detallecesion_VO.carta_rechazo_aprobacion('');
        self.mcontrato_fil2(0);
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
         parameter={ mcontrato:value, tipo_contratista:'1'};
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


        //consultar los estados para llenar un select
    self.consultar_lista_estado=function(){
        
         path =path_principal+'/api/Estados?ignorePagination';
         parameter={ dato: 'CesionV2' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.listado_estado(datos);

         }, path, parameter,undefined,false,false);

    }


    //funcion que se ejecuta cuando se cambia el contratista
    self.cesionv_VO.contratista_id.subscribe(function (value) {

        if(value >0){
            self.select_contrato(value);

        }
    });

    // funciones para el agregar
    //consultar los contrato para llenar un select
    self.consultar_macrocontrato2=function(){
        
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12' };
         RequestGet(function (datos, estado, mensaje) {
            self.listado_mcontrato2(datos.macrocontrato);

         }, path, parameter,undefined,false,false);
    }


    //funcion que se ejecuta cuando se cambia en el select de contrato 
    // self.mcontrato_fil2.subscribe(function (value) {

    //     if(value >0){
    //         self.select_contrato(value);
    //         //self.select_nombregiro(value);

    //     }else{
    //         self.listado_contrato_select([]);
    //     }
    // });


        //funcion que se ejecuta cuando se cambia en el select de contrato 
    // self.mcontrato_fil2.subscribe(function (value) {

    //     if(value >0){
    //         self.select_contrato(self.cesionv_VO.contratista_id(),value);
    //         //self.select_nombregiro(value);

    //     }else{

    //         if(self.cesionv_VO.contratista_id()>0){
    //            self.select_contrato(self.cesionv_VO.contratista_id()); 
    //         }
            
    //     }
    // });



        //consultar los contrato para llenar un select
    self.select_contrato=function(contratista){

        if(contratista!=''){
            var contr=contratista;
        }else{
            var contr=0;
        }

        // if(value!=''){
        //     var con=value;
        // }else{
        //     var con=0;
        // }
        
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={tipo:'8,9,10,11,13,14,15', valida:1, contratista:contr};
         RequestGet(function (datos, estado, mensaje) {
           
            self.listado_contrato_select(datos.contrato);

         }, path, parameter,undefined,false,false);
    }


    //funcion que se ejecuta cuando se cambia en el select de contrato 
    self.detallecesion_VO.contrato_id.subscribe(function (value) {

        if(value >0){
            //self.select_idcontrato(value);
            self.select_nombregiro(value);
        }else{
            self.listado_nombre_giro([]);
        }
    });

        //para obtener el macrocontrato del contrato
    // self.select_idcontrato=function(idcontrato){
        
    //      path =path_principal+'/proyecto/filtrar_proyectos/';
    //      parameter={ idcontrato: idcontrato};
    //      RequestGet(function (datos, estado, mensaje) {

    //         //self.macroid(datos.contrato[0].mcontrato_id);

    //         self.select_nombregiro(datos.contrato[0].mcontrato_id);

    //      }, path, parameter,undefined,false,false);
    // }


    //consultar los nombre del giro para llenar un select
    self.select_nombregiro=function(contrato){
        
         path =path_principal+'/cesion_v2/listado_nombre_giro/';
         parameter={contrato:contrato };
         RequestGet(function (datos, estado, mensaje) {

            self.listado_nombre_giro(datos);

         }, path, parameter,undefined,false,false);
    }

    //consultar los beneficiario para llenar un select
    self.select_beneficiario=function(){
        
         path =path_principal+'/api/empresa/?sin_paginacion';
         parameter={ esProveedor: '1' };
         RequestGet(function (datos, estado, mensaje) {

            self.listado_beneficiario(datos);

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



    //funcion consultar las cesiones 
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            
            self.filtro($('#txtBuscar').val());
            var estado=$("#estado_filtrar").val();
            var contratista=$("#contratista_filtro").val();
            var mcontrato=$("#mcontrato_filtro").val();
            var contrato=$("#contrato_filtro").val();
            var desde=$("#desde").val();
            var hasta=$("#hasta").val();

            path = path_principal+'/api/CesionV2?format=json';
            parameter = { dato: self.filtro(), page: pagina, desde:desde, hasta:hasta, estado:estado, contratista:contratista,
                mcontrato:mcontrato, contrato:contrato};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.limpiar();
                    self.mensaje('');
                    $('#modal_filtro').modal('hide'); 
                    self.listado(agregarOpcionesObservable(datos.data));  
                    cerrarLoading();

                } else {
                    self.limpiar();
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
       
       path =path_principal+'/api/CesionV2/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {

            self.titulo('Actualizar Cesion');

            self.cesionv_VO.id(datos.id);
            self.cesionv_VO.contratista_id(datos.contratista.id);
            self.cesionv_VO.fecha_carta(datos.fecha_carta);
            self.cesionv_VO.estado_id(datos.estado.id);
            self.cesionv_VO.soporte_solicitud(datos.soporte_solicitud);

             $('#modal_editar').modal('show');

         }, path, parameter);

     }


    //funcion actualiza la cesion
     // self.actualizar_cesion=function(){

     //    var parametros={     
     //        metodo:'PUT',                
     //       callback:function(datos, estado, mensaje){

     //        if (estado=='ok') {
     //          self.filtro("");
     //          self.limpiar();
     //          self.consultar(self.paginacion.pagina_actual());
     //          $('#modal_acciones').modal('hide');
     //        }  

     //       },//funcion para recibir la respuesta 
     //       url:path_principal+'/api/CesionV2/'+self.cesionv_VO.id()+'/',
     //       parametros:self.cesionv_VO,
     //       completado:function(){

     //       }                          
     //    };

     //    Request(parametros);

     // }


      //funcion guardar y actualizar el movimiento de la cuenta
     self.actualizar_cesion=function(){

        var data = new FormData();

        data.append('contratista_id',self.cesionv_VO.contratista_id());
        data.append('estado_id',self.cesionv_VO.estado_id());
        data.append('fecha_carta',self.cesionv_VO.fecha_carta());
       // data.append('estado_id',estado);
        data.append('archivo[]',self.cesionv_VO.soporte_solicitud());

       // data.append('archivo[]', $('#archivo')[0].files[0]);

          var parametros={     
                metodo:'PUT',                
               callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                  self.limpiar();
                  self.consultar(self.paginacion.pagina_actual());
                  $('#modal_editar').modal('hide');
                }  

               },//funcion para recibir la respuesta 
               url:path_principal+'/api/CesionV2/'+self.cesionv_VO.id()+'/',
               parametros:data                      
          };

          RequestFormData2(parametros);        

     }


    self.agregar_cesion=function(){

        if (CesionVViewModel.errores_detallecesion_v().length==0) {

            path =path_principal+'/cesion_v2/validacion_cesion/';
            parameter = {contrato:self.detallecesion_VO.contrato_id(), valor:self.detallecesion_VO.valor()};
            RequestGet(function (datos, estado, mensage) {

                if (datos<=0){

                    var mensaje= 'El contrato no tiene el saldo suficiente para ejecutar la cesion,¿esta seguro que desea continuar?';

                    $.confirm({
                        title: 'Confirmar!',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>'+mensaje+'<h4>',
                        confirmButton: 'Si',
                        confirmButtonClass: 'btn-info',
                        cancelButtonClass: 'btn-danger',
                        cancelButton: 'No',
                        confirm: function() {

                            self.listado_agregar.push({
                    
                                eliminado:ko.observable(false),
                                contrato:{id:self.detallecesion_VO.contrato_id(),nombre:$('#contrato_registrar option:selected').text()},
                                nombre_giro:{id:self.detallecesion_VO.nombre_giro_id(),nombre:$('#nombre_giro option:selected').text()},
                                beneficiario:{id:self.detallecesion_VO.beneficiario_id()},
                                banco:{id:self.detallecesion_VO.banco_id()} ,
                                numero_cuenta:{numero:self.detallecesion_VO.numero_cuenta()},
                                tipo_cuenta:{id:self.detallecesion_VO.tipo_cuenta_id()},
                                estado:{id:147},
                                valor_cesion:{valor:self.detallecesion_VO.valor()},
                                
                            });

                            self.limpiarDetalle();
                                    
                        }
                    });
                    
                }else{

                        self.listado_agregar.push({
                    
                            eliminado:ko.observable(false),
                            contrato:{id:self.detallecesion_VO.contrato_id(),nombre:$('#contrato_registrar option:selected').text()},
                            nombre_giro:{id:self.detallecesion_VO.nombre_giro_id(),nombre:$('#nombre_giro option:selected').text()},
                            beneficiario:{id:self.detallecesion_VO.beneficiario_id()},
                            banco:{id:self.detallecesion_VO.banco_id()} ,
                            numero_cuenta:{numero:self.detallecesion_VO.numero_cuenta()},
                            tipo_cuenta:{id:self.detallecesion_VO.tipo_cuenta_id()},
                            estado:{id:147},
                            valor_cesion:{valor:self.detallecesion_VO.valor()},
                                
                        });

                        self.limpiarDetalle();

                }

            }, path, parameter);
        }
        else{
          CesionVViewModel.errores_detallecesion_v.showAllMessages();
        }    

    }


    //remueve regstros del array
    self.remover_cesion=function(obj) { 
        self.listado_agregar.remove(obj);
    }

    
    //para guardar la cesion
    self.guardar=function(){

        if (CesionVViewModel.errores_cesion_v().length==0) {

            var data = new FormData();

            data.append('lista',ko.toJSON(self.listado_agregar()));
            data.append('contratista',self.cesionv_VO.contratista_id());
            data.append('fecha_carta',self.cesionv_VO.fecha_carta());
            data.append('estado',147);
            data.append('archivo', $('#archivo2')[0].files[0]);
            

            var parametros={                     
                callback:function(datos, estado, mensaje){

                    if (estado=='ok') {
                        self.limpiar();
                        self.consultar(self.paginacion.pagina_actual());
                        $('#modal_acciones').modal('hide');
                    }                        
                            
                },//funcion para recibir la respuesta 
                    url:path_principal+'/cesion_v2/guardar_cesion/',//url api
                    parametros:data,
                    completado:function(){
                    }                          
            };
            RequestFormData2(parametros);
        }
        else{
          CesionVViewModel.errores_cesion_v.showAllMessages();
        }    
    }


    //exportar excel las cesiones
   self.exportar_excel=function(){

         location.href=path_principal+"/cesion_v2/export_excel_cesiones/";
    } 



}

var cesion_v = new CesionVViewModel();
CesionVViewModel.errores_cesion_v = ko.validation.group(cesion_v.cesionv_VO);
CesionVViewModel.errores_detallecesion_v = ko.validation.group(cesion_v.detallecesion_VO);
ko.applyBindings(cesion_v);
