
    function Encabezado_giroViewModel() {
        
        var self = this;
        self.listado=ko.observableArray([]);
        self.listado2=ko.observableArray([]);
        self.listado_no_radicado=ko.observableArray([]);
        self.mensaje=ko.observable('');
        self.mensaje_no_radicado=ko.observable('');
        self.mensajeDetalleAnticipos=ko.observable('');
        self.titulo=ko.observable('');
        self.filtro=ko.observable('');
        self.checkall=ko.observable(false);
        self.soporte_arriba=ko.observable('');
        self.idProcesoRelacion =ko.observable(0);
        self.cambiar_contratista=ko.observable(0);
        self.avanceKo=ko.observable('');
        self.banco=ko.observable('')

        self.macrocontrato_select=ko.observable('');
        self.lista_contrato=ko.observableArray([]);
        self.contratista=ko.observable('');
        self.listado_contratista=ko.observableArray([]);
        self.contratoobra=ko.observable('');  
        self.lista_obra=ko.observableArray([]);
        self.lista_contrato_select=ko.observableArray([]);
        self.referencia=ko.observable(''); 

        self.listado_tipo_pago_recurso = ko.observableArray([]);

        self.fechaestimada_desde=ko.observable(''); 
        self.fechaestimada_hasta=ko.observable('');

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
            pagina_actual: ko.observable(0),
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

        //funcion para abrir modal de registrar encabezado giro
        self.abrir_modal = function () {
            self.limpiar();
            self.titulo('Registrar Giro');
            $('#modal_acciones').modal('show');
        }

        self.abrir_filtro = function (){
            // self.limpiar();
            self.titulo('Filtrar referencia');
            $('#modal_referencia').modal('show');
            self.consultar_contratistas(); 
        }

        self.abrir_detalle = function (value){
            // self.limpiar();
            self.titulo('Detalle de anticipo');
            $('#modal_detalle').modal('show');
            self.encabezado_detalle(value);
            self.consultar_detalle(1,value)

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

                 self.contratista('');
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
            // if(value >0){
            //     // self.filtros(value,'','','');
                
            // }else{
            //     // self.filtros('','','','');
            //     // self.listado_contratista([])
            // }
            self.consultar_contratistas();
            self.consultar(1);
        });    

        self.contratista.subscribe(function (value) {            
            // if(value >0){
            //     self.cambiar_contratista(1);
            //     self.filtros(self.macrocontrato_select(),value,'','');
            // }
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

                     if($('#archivo2')[0].files.length==0){
                        self.encabezado_giroVO.soporte('');
                    }                 

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

                path = path_principal+'/api/Encabezado_solicitud_giro/?format=json';
                parameter = { flujotest : 0 ,
                              dato: self.filtro(), 
                              page: pagina,
                            };

                parameter.referencia = self.referencia() == '' ? 1 : 
                                       self.referencia() == 1 ? 3:
                                       1;

                parameter.pago_recurso = self.banco();

                if (self.macrocontrato_select()!='') {
                    parameter.mcontrato_filtro=self.macrocontrato_select()
                }
                if (self.contratista()!='') {
                    parameter.contratista_filtro=self.contratista()
                }
                if (self.contratoobra()!='') {
                    parameter.dato=self.contratoobra()
                } 
     

                sessionStorage.setItem("solicitud_giro_solrevisar_dato", self.filtro() || '');               
                sessionStorage.setItem("solicitud_giro_solrevisar_referencia", self.referencia() || '' );
                sessionStorage.setItem("solicitud_giro_solrevisar_macrocontrato", self.macrocontrato_select() || '');               
                sessionStorage.setItem("solicitud_giro_solrevisar_contratista", self.contratista() || '');
                sessionStorage.setItem("solicitud_giro_solrevisar_contrato_obra", self.contratoobra() || '');     


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

        /*var encabezado_id=self.detalle_giroVO.encabezado_id();*/

         path =path_principal+'/api/Encabezado_giro/'+encabezado+'/?format=json';
         parameter={};
         RequestGet(function (datos, estado, mensaje) {
            if(datos){
                self.contratista_encabezado(datos.contrato.contratista.nombre);
                self.contratante_encabezado(datos.contrato.contratante.nombre);
                self.numero_contrato_encabezado(datos.contrato.id);
                self.nombre_anticipo_encabezado(datos.nombre.nombre);
                self.nombre_proyecto_encabezado(datos.contrato.nombre);
                self.suma_valor_detalles(datos.suma_detalle);
                
            }

         }, path, parameter,undefined,false,false);

    } 


    //funcion consultar y traer los datos del detalle del giro
    self.consultar_detalle = function (pagina,encabezado) {

        var encabezado_id=encabezado
        //alert(encabezado_id)

        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());

            path = path_principal+'/api/Detalle_giro/?format=json';
            parameter = { dato: self.filtro(), page: pagina, encabezado_id:encabezado_id , sin_paginacion : 1};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensajeDetalleAnticipos('');
                    self.listado2(agregarOpcionesObservable(datos)); 
                    //detalle_giro.encabezado_detalle(encabezado_id);
                } else {
                    self.listado2([]);
                    self.mensajeDetalleAnticipos(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js 
                }

                // self.llenar_paginacion(datos,pagina);
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
    self.guardar_testOP=function(obj){ 
      console.log(obj)
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
        parametros:{id:obj.id,flujo_test:1}
      };                    

      Request(parametros);            
    }

    //funcion para seleccionar que reporte de encabezado del giro se generara
    self.generar_reporte_giro=function(){
        location.href=path_principal+"/solicitud_giro/testop_reporte/";
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

    //funcion para exportar a excel el encabezado del giro
    self.exportar_excel = function (obj) {
        self.titulo('Generar reporte TEST-OP realizadas');
        $('#generar_informe').modal('show');
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

$('#txtBuscar').val(sessionStorage.getItem("solicitud_giro_solrevisar_dato"))   
encabezado_giro.referencia(sessionStorage.getItem("solicitud_giro_solrevisar_referencia"));
encabezado_giro.macrocontrato_select(sessionStorage.getItem("solicitud_giro_solrevisar_macrocontrato"));
encabezado_giro.contratista(sessionStorage.getItem("solicitud_giro_solrevisar_contratista"));
encabezado_giro.contratoobra(sessionStorage.getItem("solicitud_giro_solrevisar_contrato_obra"));


Encabezado_giroViewModel.errores_giros = ko.validation.group(encabezado_giro.encabezado_giroVO);
ko.applyBindings(encabezado_giro);
