
    function Encabezado_giroViewModel() {
        
        var self = this;
        self.listado=ko.observableArray([]);
        self.listado2=ko.observableArray([]);
        self.listado_no_radicado=ko.observableArray([]);
        self.mensaje=ko.observable('');
        self.mensaje_no_radicado=ko.observable('');
        self.mensajeDetalleAnticipos=ko.observable('');
        self.banco=ko.observable('');
        self.titulo=ko.observable('');
        self.filtro=ko.observable('');
        self.checkall=ko.observable(false);
        self.detalleanticipo=ko.observable(true);
        self.soporte_arriba=ko.observable('');
        self.idProcesoRelacion =ko.observable(0);
        self.cambiar_contratista=ko.observable(0);

        self.encabezado_detalle_id=ko.observable('');

        self.porcentajeliquidacion=ko.observable(0);

        self.listado_tipo_pago_recurso = ko.observableArray([]);
        
        self.fechaestimada_desde=ko.observable(''); 
        self.fechaestimada_hasta=ko.observable('');

        self.test_activo=ko.observable(false)


        self.fechaestimada=ko.observable('');
        self.testop=ko.observable('');

        self.macrocontrato_select=ko.observable('');
        self.lista_contrato=ko.observableArray([]);
        self.contratista=ko.observable('');
        self.listado_contratista=ko.observableArray([]);
        self.contratoobra=ko.observable('');  
        self.lista_obra=ko.observableArray([]);
        self.lista_contrato_select=ko.observableArray([]);
        self.referencia=ko.observable('');    

        //observables del encabezado del detalle del giro
        self.contratista_encabezado=ko.observable('');
        self.contratante_encabezado=ko.observable('');
        self.numero_contrato_encabezado=ko.observable('');
        self.nombre_anticipo_encabezado=ko.observable('');
        self.nombre_proyecto_encabezado=ko.observable('');
        self.suma_valor_detalles=ko.observable('');
        self.encabezado_del_detalle=ko.observable(''); 
        
        //Representa un modelo de la tabla giro
        self.encabezado_giroVO={
            id:ko.observable(0),
            nombre_id:ko.observable('').extend({ required: { message: '(*)Seleccione el nombre del anticipo' } }),
            contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contrato' } }),
            soporte:ko.observable(''),
            referencia:ko.observable(''),
            num_causacion:ko.observable(''),
            fecha_conta:ko.observable(''),
            disparar_flujo:ko.observable(0),
            numero_radicado:ko.observable(''),
            referencia:ko.observable(''),
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

        //funcion para abrir modal de registrar encabezado giro
        self.abrir_modal = function () {
            self.limpiar();
            self.titulo('Registrar Giro');
            $('#modal_acciones').modal('show');
        }


        self.abrir_filtro = function (){
            // self.limpiar();
            self.consultar_contratistas(); 
            self.titulo('Filtrar referencia');
            $('#modal_referencia').modal('show');
        }

        self.abrir_detalle = function (value){
            // self.limpiar();
            self.titulo('Detalle de anticipo');
            $('#modal_detalle').modal('show');
            self.encabezado_detalle_id(value.id)
            self.encabezado_detalle(value.id);
            self.consultar_detalle(1,value.id);
            // self.porcentajeliquidacion(value.porcentaje)
        }        

    //funcion para exportar a excel el encabezado del giro
    self.exportar_excel = function (obj) {
        self.consultar_contratistas(); 
        self.titulo('Generar reporte TEST-OP realizadas');
        $('#generar_informe').modal('show');
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

         self.encabezado_giroVO.nombre_id.isModified(false);
         self.encabezado_giroVO.contrato_id.isModified(false);      
     }


    self.consultar_contratistas = function(){

        path =path_principal+'/proyecto/select-filter-proyecto/';
        parameter = { consulta_contratista : 1 
                            ,mcontrato: self.macrocontrato_select() };         
               
        RequestGet(function (results,count) {
                                 
            self.listado_contratista(results.contratistas)
            cerrarLoading();
        }, path, parameter,undefined, false);  

    }

    //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
    self.macrocontrato_select.subscribe(function (value) {
        self.consultar_contratistas();
        self.consultar(1);        
    }); 

    self.contratista.subscribe(function (value) {            
        self.consultar(1)
    }); 


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

            } else {
                 Encabezado_giroViewModel.errores_giros.showAllMessages();//mostramos las validacion
            }
    }

    //funcion consultar tap de consultar y modificar de encabezado giro
    self.consultar = function (pagina) {
            //alert($('#mcontrato_filtro').val())
            if (pagina > 0) {            
                self.filtro($('#txtBuscar').val());
                path = path_principal+'/api/Encabezado_solicitud_giro/?format=json&flujotest=1';
                parameter = { dato: self.filtro(), 
                              page: pagina,
                              detallescompletos: self.test_activo()
                            };
                parameter.referencia = self.referencia() == '' ? 1 : 
                                       self.referencia() == 1 ? 3:
                                       1;

                parameter.pago_recurso = self.banco();
                parameter.solsintestop = 1;
                if (self.macrocontrato_select()!='') {
                    parameter.mcontrato_filtro=self.macrocontrato_select()
                }
                if (self.contratista()!='') {
                    parameter.contratista_filtro=self.contratista()
                }
                if (self.contratoobra()!='') {
                    parameter.dato=self.contratoobra()
                }                 
                // parameter.detallescompletos=self.test_activo()  

                sessionStorage.setItem("solicitud_giro_soltestop_dato", self.filtro() || '');               
                sessionStorage.setItem("solicitud_giro_soltestop_referencia", self.referencia() || '');
                sessionStorage.setItem("solicitud_giro_soltestop_macrocontrato", self.macrocontrato_select() || '');               
                sessionStorage.setItem("solicitud_giro_soltestop_contratista", self.contratista() || '');
                sessionStorage.setItem("solicitud_giro_soltestop_contrato_obra", self.contratoobra() || '');     

                RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                        self.mensaje('');
                        // $('#modal_referencia').modal('hide'); 
                        self.listado(agregarOpcionesObservable(datos.data));
                    } else {
                        self.listado([]);
                        // $('#modal_referencia').modal('hide'); 
                        self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    }
                    self.llenar_paginacion(datos,pagina);
                    cerrarLoading();
            }, path, parameter,undefined, false);
        }
    }
    //consultar los encabezado del giro
    self.encabezado_detalle=function(encabezado){

         path =path_principal+'/api/Encabezado_giro/'+encabezado+'/?format=json';
         parameter={ sol_giro_solicitados_autorizado : 1 };
         RequestGet(function (datos, estado, mensaje) {
            if(datos){
                self.contratista_encabezado(datos.contrato.contratista.nombre);
                self.contratante_encabezado(datos.contrato.contratante.nombre);
                self.numero_contrato_encabezado(datos.contrato.numero);
                self.nombre_anticipo_encabezado(datos.nombre.nombre);
                self.nombre_proyecto_encabezado(datos.contrato.nombre);
                // self.suma_valor_detalles(datos.suma_detalle);
            }
         }, path, parameter,undefined,false,false);
    } 
    //funcion consultar y traer los datos del detalle del giro
    self.consultar_detalle = function (pagina,encabezado) {
        var encabezado_id=encabezado
        //alert(encabezado_id)
        if (pagina > 0) {            

            self.filtro($('#txtBuscar').val());

            path = path_principal+'/api/Detalle_giro/?format=json';
            parameter = { dato: self.filtro(), page: pagina, encabezado_id:encabezado_id 
                        , sin_paginacion: 1  };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensajeDetalleAnticipos('');
                    self.listado2(agregarOpcionesObservable(datos)); 
                    //detalle_giro.encabezado_detalle(encabezado_id);
                    cerrarLoading();  

                } else {
                    self.listado2([]);
                    self.mensajeDetalleAnticipos(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading(); 
                }

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
    self.reversar=function(obj){ 
          var parametros={

            callback:function(datos, estado, mensaje){

              if (estado=='ok') {
                self.filtro("");
                self.consultar(self.paginacion.pagina_actual());
                //mensajeExitoso(estado);
                self.limpiar();
              }                                                
            },
            url:path_principal+'/solicitud_giro/actualizar_flujotest/',//url api
            parametros:{id:obj.id,flujo_test:0}
          };                    
        Request(parametros);                
    }        
    //funcion para seleccionar que reporte de encabezado del giro se generara
    self.generar_reporte_giro=function(){
            // var con_ref = ( self.referencia()=='' ) ? 1 : 0;
            var dato = ''
            var referencia = self.referencia() == '' ? 1 : 
                                    self.referencia() == 1 ? 3:
                                    1;
            var pago_recurso = self.banco();
            var detallescompletos= self.test_activo();

            if (self.contratoobra()!='') {
                dato=self.contratoobra()
            }

            filtros='?'
            filtros = filtros+"mcontrato_filtro="+self.macrocontrato_select();
            filtros = filtros+"&contratista_filtro="+self.contratista(); 
            filtros = filtros+"&referencia="+referencia;
            filtros = filtros+"&pago_recurso="+pago_recurso;
            filtros = filtros+"&detallescompletos="+detallescompletos;
            filtros = filtros+"&dato="+dato; 
            location.href=path_principal+"/solicitud_giro/testop_reporte/"+filtros;
    }

    //funcion para seleccionar que reporte de encabezado del giro se generara
    self.generar_reporte_testop=function(){
            filtros='?'

            if (self.macrocontrato_select()!='') {
                filtros=filtros+"mcontrato="+self.macrocontrato_select()
            }

            if (self.contratista()!='') {
                filtros=filtros+"contratista="+self.contratista()
            }

            if (self.fechaestimada_desde()!='') {
                filtros=filtros+"fecha_e_desde="+self.fechaestimada_desde()
            }

            if (self.fechaestimada_hasta()!='') {
                filtros=filtros+"fecha_e_hasta="+self.fechaestimada_hasta()
            }                        


            location.href=path_principal+"/solicitud_giro/reporte_test_realizados/"+filtros;
        }

    self.exportaranticipo = function (){
         var lista_id=[];
         var count=0;
         var test=0
         ko.utils.arrayForEach(self.listado2(), function(d) {

                if(d.eliminado()==true){
                   count=1;
                   lista_id.push(d.id)                   
                   if (d.test_op==null || d.test_op=='') {
                        test=1;
                    }
                }                
         });

        if(count==0){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe seleccionar un anticipo.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        // }else if(self.porcentajeliquidacion()!=100){
        //     $.confirm({
        //         title:'Informativo',
        //         content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>El porcentaje de liquidacion debe estar al 100%.<h4>',
        //         cancelButton: 'Cerrar',
        //         confirmButton: false
        //     });

        }else if(test==1){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe registar la TEST/OP y fecha estimada de pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{

            path = "http://caribemar.sinin.co:8080/exportar/orden-operacion-test-op?encabezado_id="+self.encabezado_detalle_id()+"&detalles="+btoa(lista_id)+"&valida=1";
            //path = "http://localhost:51149/exportar/orden-operacion-test-op?encabezado_id="+self.encabezado_detalle_id()+"&detalles="+btoa(lista_id)+"&valida=1";
            parameter = {};
            RequestGet(function (datos, estado, mensage) {

                console.log(datos)
                if(datos.fiduciaria=="FIDUBOGOTA"){
                    location.href = path_principal+"/solicitud_giro/reporte_anticipo/?encabezado_id="+self.encabezado_detalle_id()+"&detalles="+lista_id;
                }else{
                    location.href = "http://caribemar.sinin.co:8080/exportar/orden-operacion-test-op?encabezado_id="+self.encabezado_detalle_id()+"&detalles="+btoa(lista_id)+"&valida=";
                    //location.href = "http://localhost:51149/exportar/orden-operacion-test-op?encabezado_id="+self.encabezado_detalle_id()+"&detalles="+btoa(lista_id)+"&valida=";
                }

            }, path, parameter);            
        }   
    }
    //funcion para seleccionar los datos a eliminar del detalle del giro
    self.checkall.subscribe(function(value){
            ko.utils.arrayForEach(self.listado2(), function(d) {
                if( (d.estado.id == 1 || d.estado.id == 2) && (d.contratista.id!=39 && d.contratista.id!=115 ) ){
                    d.eliminado(value);
                }   
            }); 
    });    

    self.EstablecerTestOP = function () {
         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado2(), function(d) {

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

         // }else if(self.porcentajeliquidacion()!=100){
         //        $.confirm({
         //        title:'Informativo',
         //        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>No se puede establecer la TEST - OP y la fecha estimada de pago, el proceso de liquidacion no esta al 100%.<h4>',
         //        cancelButton: 'Cerrar',
         //        confirmButton: false
         //    });

          }else if(self.fechaestimada()=='' && self.testop()!=''){
                $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe digitar la fecha de pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

          }else if(self.fechaestimada()!='' && self.testop()==''){
                $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe digitar la TEST/OP.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });                

          }else{
             var path =path_principal+'/solicitud_giro/detalletestop/';
             var parameter = { lista: lista_id,fecha_pago_esperada:self.fechaestimada(),
             test_op:self.testop()};
             RequestAnularOEliminar("Esta seguro que desea guardar los datos?", path, parameter, function () {
                 self.consultar_detalle(1,self.encabezado_detalle_id());
                 self.checkall(false);
                 self.fechaestimada('');
                 self.testop('')
             })

         } 
    }    

    self.consultar_lista_tipo_pago=function(){

         path =path_principal+'/api/Tipos/';
         parameter = { ignorePagination : 1 , aplicacion : 'encabezadoGiro_pago_recurso' };

         RequestGet(function (datos, estado, mensaje) {          
            
            self.listado_tipo_pago_recurso(datos);

        }, path, parameter ,undefined, false);
    }


}

var encabezado_giro = new Encabezado_giroViewModel();

$('#txtBuscar').val(sessionStorage.getItem("solicitud_giro_soltestop_dato"))   
encabezado_giro.referencia(sessionStorage.getItem("solicitud_giro_soltestop_referencia"));
encabezado_giro.macrocontrato_select(sessionStorage.getItem("solicitud_giro_soltestop_macrocontrato"));
encabezado_giro.contratista(sessionStorage.getItem("solicitud_giro_soltestop_contratista"));
encabezado_giro.contratoobra(sessionStorage.getItem("solicitud_giro_soltestop_contrato_obra"));



Encabezado_giroViewModel.errores_giros = ko.validation.group(encabezado_giro.encabezado_giroVO);

ko.applyBindings(encabezado_giro);
