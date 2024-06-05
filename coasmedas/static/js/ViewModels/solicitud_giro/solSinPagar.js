
    function Encabezado_giroViewModel() {
        
        var self = this;
        self.listado=ko.observableArray([]);
        self.listado2=ko.observableArray([]);
        self.listado_no_radicado=ko.observableArray([]);
        self.mensaje=ko.observable('');
        self.mensaje_no_radicado=ko.observable('');
        self.titulo=ko.observable('');
        self.filtro=ko.observable('');
        self.checkall=ko.observable(false);
        self.soporte_arriba=ko.observable('');
        self.idProcesoRelacion =ko.observable(0);
        self.cambiar_contratista=ko.observable(0);
        
        self.fecha_pago=ko.observable('');
        self.cuenta_id=ko.observable('');
        self.rechazo=ko.observable('');
        self.motivo=ko.observable('');


        self.lista_contrato=ko.observableArray([]);
        self.listado_contratista=ko.observableArray([]);
         
        self.lista_obra=ko.observableArray([]);
        self.lista_contrato_select=ko.observableArray([]);
        self.referencia=ko.observable('');  

        self.lista_cuenta_select=ko.observableArray([]);  

        //Representa un modelo de la tabla giro
        self.encabezado_giroVO={
            id:ko.observable(0),
            nombre_id:ko.observable('').extend({ required: { message: '(*)Seleccione el nombre del anticipo' } }),
            contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contrato' } }),
            soporte:ko.observable(''),
            num_causacion:ko.observable(''),
            fecha_conta:ko.observable(''),
            disparar_flujo:ko.observable(0),
            numero_radicado:ko.observable(''),
            referencia:ko.observable(''),
         };

         self.filtro_encabezado_giroVO = {
            macrocontrato_select: ko.observable(''),
            contratista: ko.observable(''),
            test_op_busqueda: ko.observable(''),
            contratoobra: ko.observable(''),
            referencia_contrato: ko.observable(''),
            desde: ko.observable(''),
            hasta: ko.observable(''),

         }

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
            }
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
            }
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
        }

        //funcion para seleccionar los datos a eliminar
        self.checkall.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado(), function(d) {
                d.eliminado(value);
            }); 
        });

        self.abrir_establecer = function () {
            self.fecha_pago('');
            self.titulo('Establecer pago');
            self.consultar_lista_cuenta();
            $('#modal_establecer').modal('show');
        }

        self.abrir_rechazo = function () {
            self.rechazo('');
            self.motivo('');
            self.titulo('Rechazar pago');
            $('#modal_rechazar').modal('show');
        }        

        self.abrir_filtro = function (){
            self.titulo('Filtrar referencia');
            self.consultar_contratistas();
            $('#modal_referencia').modal('show');
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

             self.encabezado_giroVO.contratista(0);
             self.macrocontrato_select(0);
             self.lista_contrato_select([]);
             self.listado_contratista([]);

             self.encabezado_giroVO.nombre_id.isModified(false);
             self.encabezado_giroVO.contrato_id.isModified(false);      
         }

        
        self.consultar_contratistas = function(){

            path =path_principal+'/proyecto/select-filter-proyecto/';         
            parameter = { consulta_proveedores : 1 
                            ,mcontrato: self.filtro_encabezado_giroVO.macrocontrato_select() };

            RequestGet(function (results,count) {                                     
                self.listado_contratista(results.proveedores)
                cerrarLoading();
            }, path, parameter,undefined, false);
        } 
 

        //funcion consultar tap de consultar y modificar de encabezado giro
        self.consultar = function (pagina) {            
            //alert($('#mcontrato_filtro').val())
            if (pagina > 0) {            
                self.filtro($('#txtBuscar').val());

                path = path_principal+'/api/Detalle_giro_solicitud_giro/?lite=1&sinpago=1&fechapago=1';
                parameter = { dato: self.filtro(), 
                              page: pagina,
                              sol_giro_solicitados_autorizado:1
                            };
                if (self.referencia()=='') {
                    parameter.referencia=1
                }
                if (self.referencia()==1) {
                    parameter.referencia=3
                }                        
                if (self.filtro_encabezado_giroVO.macrocontrato_select()!='') {
                    parameter.mcontrato_filtro=self.filtro_encabezado_giroVO.macrocontrato_select()
                }
                if (self.filtro_encabezado_giroVO.contratista()!='') {
                    parameter.contratista_filtro=self.filtro_encabezado_giroVO.contratista()
                }
                if (self.filtro_encabezado_giroVO.contratoobra()!='') {
                    parameter.dato=self.filtro_encabezado_giroVO.contratoobra()
                }
                if (self.filtro_encabezado_giroVO.desde()!='') {
                    parameter.fechadesde=self.filtro_encabezado_giroVO.desde()
                } 
                if (self.filtro_encabezado_giroVO.hasta()!='') {
                    parameter.fechahasta=self.filtro_encabezado_giroVO.hasta()
                } 

                if (self.filtro_encabezado_giroVO.referencia_contrato()!='') {
                    parameter.referencia_contrato_busqueda = self.filtro_encabezado_giroVO.referencia_contrato()
                }

                if (self.filtro_encabezado_giroVO.test_op_busqueda()!='') {
                    parameter.test_op_busqueda= self.filtro_encabezado_giroVO.test_op_busqueda()
                } 

                RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                        self.mensaje('');
                        $('#modal_referencia').modal('hide'); 
                        self.listado(agregarOpcionesObservable(datos.data));
                    } else {
                        self.listado([]);
                        $('#modal_referencia').modal('hide'); 
                        self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    }

                    self.llenar_paginacion(datos,pagina);
                    cerrarLoading();
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

        //guardar la fecha del radicado o numero de radicado en el tan no radicado
        self.guardar_fechadepago=function(obj){ 
          var parametros={

            callback:function(datos, estado, mensaje){
            
              if (estado=="ok") {
                self.filtro("");
                self.consultar(self.paginacion.pagina_actual());
                //mensajeExitoso(estado);
                self.limpiar();
              }                
                               
            },
            url:path_principal+'/solicitud_giro/fechapago/',//url api
            parametros:{id:obj,fechapago:self.fecha_pago() , cuenta: self.cuenta_id() }
          };                    

          Request(parametros);                
        }

        //guardar la fecha del radicado o numero de radicado en el tan no radicado
        self.pagorechazado=function(obj){ 
          var parametros={

            callback:function(datos, estado, mensaje){

              if (estado=='ok') {
                self.filtro("");
                self.consultar(self.paginacion.pagina_actual());
                //mensajeExitoso(estado);
                self.limpiar();
              }                      
                               
            },
            url:path_principal+'/solicitud_giro/rechazopago/',//url api
            parametros:{id:obj,rechazo:self.rechazo(),motivo:self.motivo()}
          };                    

          Request(parametros);
                
        }


    self.establecerrechazo = function () {
         var lista_id=[];
         var count=0;

         if (self.rechazo()!='' || self.motivo()!='') {
            ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id.push(d.id)
                }
            });
            if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe seleccionar un anticipo.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
                });

            }else{
            self.pagorechazado(lista_id);
            self.consultar(1)
            }   
         }else{
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Indique la fecha de pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
                });
         }
        
    } 

    self.establecerfecha = function () {
         var lista_id=[];
         var count=0;
         var sw = 0;
         var lista_test = [];
         var c = 0;

         if (self.fecha_pago()!='') {
            ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id.push(d.id)
                   var codigo_test_op = d.test_op;

                   if(c==0){
                        lista_test.push(codigo_test_op);    

                    }else if(lista_test.indexOf(codigo_test_op)>-1){
                        
                        lista_test.push(codigo_test_op);                            
                    }else{
                        
                        sw = 1;
                    }
                    c+=1;

                }
            });


            if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe seleccionar un anticipo.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
                });

            }else if(sw==1){
                
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione los giros de un mismo grupo de TEST/OP.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });

            }else{
                self.guardar_fechadepago(lista_id);
            }   

         }else{
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Indique la fecha de pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
                });
         }
        
    }  

    //consultar las cuenta por tipo por contrato y por empresa para llenar un select
    self.consultar_lista_cuenta=function(){
        
         path =path_principal+'/api/Financiero_cuenta/?sin_paginacion&format=json';

         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_cuenta_select(datos);
            cerrarLoading();
        }, path, parameter,undefined,false);   
    }        

}

var encabezado_giro = new Encabezado_giroViewModel();
Encabezado_giroViewModel.errores_giros = ko.validation.group(encabezado_giro.encabezado_giroVO);

ko.applyBindings(encabezado_giro);
