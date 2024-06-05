
function CuentaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.macrocontrato_select=ko.observable(0);
    self.lista_contrato=ko.observableArray([]);
    self.lista_tipo_select=ko.observableArray([]);
    self.lista_estado=ko.observableArray([]);
    self.estadocuenta=ko.observable('');
    self.macrocontrato_select=ko.observable(0);
    self.estado_select=ko.observable(0);

    self.listado_extracto=ko.observableArray([]);
    self.mensaje_soporte=ko.observable('');

    //observables para el ver mas de las cuentas
    self.nombre_contrato=ko.observable('');
    self.nombre_cuenta=ko.observable('');
    self.numero_cuenta=ko.observable('');
    self.fiduciaria=ko.observable('');
    self.saldo=ko.observable('');
    self.nombreFidecomiso=ko.observable('');
    
    //var num=0;
    //self.url=path_principal+'api/empresa'; 

     //Representa un modelo de la cuenta
    self.cuentaVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre de la cuenta' } }),
        numero:ko.observable(''),
        valor:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor de la cuenta' } }),
        fiduciaria:ko.observable(''),
        codigo_fidecomiso:ko.observable(''),
        codigo_fidecomiso_a:ko.observable(''),
        nombre_fidecomiso:ko.observable(''),
        contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contrato' } }),
        tipo_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo' } }),
        empresa_id:ko.observable(0),
        estado_id:ko.observable(''),

     };

    self.extractoVO={
        id:ko.observable(0),
        cuenta_id:ko.observable(0),
        mes:ko.observable('').extend({ required: { message: '(*)Seleccione el mes' } }),
        ano:ko.observable('').extend({ required: { message: '(*)Seleccione el año' } }),
        soporte:ko.observable('').extend({ required: { message: '(*)Seleccione un soporte' } }),
     };

     self.busquedaextractoVO={
        mes:ko.observable(''),
        ano:ko.observable('')
     };

     //paginacion de cuenta
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


    self.paginacion_extracto = {
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

    self.paginacion_extracto.pagina_actual.subscribe(function (pagina) {
        self.consultar_extracto(pagina);
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }



    self.llenar_paginacion_extracto = function (data,pagina) {

        self.paginacion_extracto.pagina_actual(pagina);
        self.paginacion_extracto.total(data.count);       
        self.paginacion_extracto.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion_extracto.totalRegistrosBuscados(buscados);

    }

  
    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });

    //funcion para abrir modal de registrar cuenta
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Cuenta');
        $('#modal_acciones').modal('show');
    }


    //funcion para filtrar las cuentas
    self.filtrar_cuenta = function () {
        self.titulo('Filtrar cuenta');
        //self.limpiar();
        self.consultar_macrocontrato();
        self.consultar_estado();
        $('#modal_filtro_cuenta').modal('show');
    }

    //funcion para ver mas detalle de la cuenta
    self.ver_mas_cuenta = function (obj) {
        self.titulo('Ver mas de la cuenta');
        self.ver_mas_detalle_cuenta(obj);
        $('#vermas_cuenta').modal('show');
    }

    //funcion para exportar a excel las cuenta
    self.exportar_excel = function (obj) {
        self.titulo('Generar informe');
        $('#generar_informe').modal('show');
    }


    //funcion para abri el mnodal de actualizar estado
    self.cambiar_estado = function () {
        self.titulo('Actualizar estado');
        self.consultar_estado();
        $('#modal_estado').modal('show');
    }


    self.modal_extracto = function (obj) {
        self.titulo('Extracto');
        self.extractoVO.cuenta_id(obj.id);
        self.consultar_extracto(1);
    }


     //limpiar el modelo de la cuenta
     self.limpiar=function(){     
         
             self.cuentaVO.id(0);
             self.cuentaVO.contrato_id('');
             self.cuentaVO.tipo_id('');
             self.cuentaVO.nombre('');
             self.cuentaVO.numero('');
             self.cuentaVO.valor(0);
             self.cuentaVO.fiduciaria('')
             self.cuentaVO.codigo_fidecomiso('');
             self.cuentaVO.codigo_fidecomiso_a('');
             self.cuentaVO.nombre_fidecomiso('');
             self.cuentaVO.estado_id('');

             self.cuentaVO.contrato_id.isModified(false);
             self.cuentaVO.nombre.isModified(false);
      
     }

     //limpiar el modelo de la cuenta
     self.limpiar_extracto=function(){     
         
             self.extractoVO.id(0);
             self.extractoVO.mes(0);
             self.extractoVO.ano(0);
             self.extractoVO.soporte('');

             $('#archivo').fileinput('reset');
             $('#archivo').val('');

             self.extractoVO.mes.isModified(false);
             self.extractoVO.ano.isModified(false);
             self.extractoVO.soporte.isModified(false);
      
     }

     self.editar_extracto =function(obj){
            self.extractoVO.id(obj.id);
            self.extractoVO.mes(obj.mes);
            self.extractoVO.ano(obj.ano);
            self.extractoVO.soporte(obj.soporte);
            self.extractoVO.cuenta_id(obj.cuenta.id);
     }

     self.eliminar_extracto=function(obj){

             var path =path_principal+'/api/Financiero_extracto/'+obj.id+'/';
             var parameter ='';
             RequestAnularOEliminar("Esta seguro que desea eliminar el extracto seleccionado?", path, parameter, function () {
                 self.consultar_extracto(1);
             })


     }

     self.limpiar_filtro_extrato=function(){
        self.busquedaextractoVO.mes(0);
        self.busquedaextractoVO.ano(0);
        self.consultar_extracto(1);
     }

     self.filtrar_extracto=function(){
         if(self.busquedaextractoVO.mes()==0 && self.busquedaextractoVO.ano()==0){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un criterio para busqueda.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
         }else{
            self.consultar_extracto(1);
         }

     }


     self.consultar_extracto = function(pagina){

        path = path_principal+'/api/Financiero_extracto?format=json';
            parameter = {page: pagina,cuenta_id:self.extractoVO.cuenta_id(),mes:self.busquedaextractoVO.mes(),ano:self.busquedaextractoVO.ano()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje_soporte('');
                    //self.listado(results); 
                   self.listado_extracto(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)
                    cerrarLoading();

                    $('#modal_extracto').modal('show');

                } else {
                    self.listado_extracto([]);
                    self.mensaje_soporte(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();

                    $('#modal_extracto').modal('show');
                }

                self.llenar_paginacion_extracto(datos,pagina);

            }, path, parameter,undefined, false);

    }


    //funcion guardar y actualizar el extracto
     self.guardar_extracto=function(){

        if (CuentaViewModel.errores_extracto().length == 0) {//se activa las validaciones

            if(self.extractoVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar_extracto();
                            self.consultar_extracto(self.paginacion_extracto.pagina_actual());
                           
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Financiero_extracto/',//url api
                     parametros:self.extractoVO                        
                };
                RequestFormData(parametros);
            }else{              

                  if($('#archivo').val()==''){
                    self.extractoVO.soporte('');
                  }
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar_extracto();
                          self.consultar_extracto(self.paginacion_extracto.pagina_actual());
                         
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Financiero_extracto/'+self.extractoVO.id()+'/',
                       parametros:self.extractoVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             CuentaViewModel.errores_extracto.showAllMessages();//mostramos las validacion
        }
     }


    //consultar los macrocontrato para registrar la cuenta
    self.consultar_macrocontrato=function(){

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_contrato(datos.macrocontrato);

         }, path, parameter,function(){
                 self.macrocontrato_select(sessionStorage.getItem("mcontrato_filtro_financiero"));       
             },false,false);

    }


        //consultar los tipos para llenar un select
    self.consultar_lista_tipo=function(){
        
         path =path_principal+'/api/Tipos?ignorePagination';
         parameter={ aplicacion: 'cuenta' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_tipo_select(datos);

         }, path, parameter,undefined,false,false);

    }


    //funcion guardar y actualizar la cuenta
     self.guardar=function(){

        if (CuentaViewModel.errores_cuenta().length == 0) {//se activa las validaciones

            if(self.cuentaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Financiero_cuenta/',//url api
                     parametros:self.cuentaVO                        
                };
                Request(parametros);
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
                       url:path_principal+'/api/Financiero_cuenta/'+self.cuentaVO.id()+'/',
                       parametros:self.cuentaVO                        
                  };

                  Request(parametros);

            }

        } else {
             CuentaViewModel.errores_cuenta.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar 
    self.consultar = function (pagina) {
        
        //alert($('#mcontrato_filtro').val())
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("dato_financiero", $('#txtBuscar').val() || '');
            sessionStorage.setItem("estado_financiero", $('#tipo_estado2').val() || '');           
            sessionStorage.setItem("mcontrato_filtro_financiero", $('#mcontrato_filtro').val() || '');

            self.cargar(pagina);
            
        }
    }


        self.cargar = function(pagina){

        let filtro = sessionStorage.getItem("dato_financiero");
        let estado = sessionStorage.getItem("estado_financiero");
        let mcontrato_filtro = sessionStorage.getItem("mcontrato_filtro_financiero");

        path = path_principal+'/api/Financiero_cuenta/?format=json';
            parameter = { dato: filtro, page: pagina, mcontrato:mcontrato_filtro, estado:estado};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    $('#modal_filtro_cuenta').modal('hide'); 
                    self.listado(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)
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


    //consultar por id de la cuenta
    self.consultar_por_id = function (obj) {
       
       path =path_principal+'/api/Financiero_cuenta/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar Cuenta');

            self.cuentaVO.id(datos.id);
            self.cuentaVO.contrato_id(datos.contrato.id);
            self.cuentaVO.nombre(datos.nombre);
            self.cuentaVO.numero(datos.numero);
            self.cuentaVO.valor(datos.valor);
            self.cuentaVO.fiduciaria(datos.fiduciaria);
            self.cuentaVO.tipo_id(datos.tipo.id);
            self.cuentaVO.estado_id(datos.estado.id);
             
             $('#modal_acciones').modal('show');

         }, path, parameter);

     }

   
    //eliminar las cuentas
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las cuenta para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/financiero/eliminar_cuenta/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las cuentas seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }


      //trae los datos para la opcion ver mas de las cuentas
    self.ver_mas_detalle_cuenta=function(obj){
        
         path =path_principal+'/api/Financiero_cuenta?sin_paginacion&format=json';
         parameter={ cuenta_id: obj.id};
         RequestGet(function (datos, estado, mensaje) {
            
            self.nombre_contrato(datos[0].contrato.nombre);
            self.nombre_cuenta(datos[0].nombre);
            self.numero_cuenta(datos[0].numero);
            self.fiduciaria(datos[0].fiduciaria);
            self.nombreFidecomiso(datos[0].nombre_fidecomiso);
            valor=datos[0].suma_ingreso+datos[0].suma_rendimiento-datos[0].suma_egreso;
            self.saldo(valor);

         }, path, parameter);

    }



    //exportar excel la tabla del listado de las cuentas
   self.exportar_excel_cuenta=function(){

         var contrato=$("#mcontrato_exportar").val();
         location.href=path_principal+"/financiero/exportar/?mcontrato="+contrato;
     } 



      //Actualiza el campo orden pago de las facturas
    self.desabilitar_cuenta = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las cuentas a deshabilitar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/financiero/deshabilitar-cuenta/';
             var parameter = { lista: lista_id, estado:self.estadocuenta()};
             RequestAnularOEliminar("Esta seguro que desea actualizar el estado de las cuentas seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
                 $('#modal_estado').modal('hide');
             })

         }     
        
    }

    //consultar los estados
    self.consultar_estado=function(){
        
         path =path_principal+'/api/Estados/?ignorePagination';
         var parameter = { aplicacion: 'EstadoCuenta'};
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_estado(datos);

         }, path, parameter,function(){
                 self.estado_select(sessionStorage.getItem("estado_financiero"));       
             });

    }

     self.ver_soporte = function(obj) {
      window.open(path_principal+"/financiero/ver-soporte/?id="+ obj.id, "_blank");
     }
    

}

var cuenta = new CuentaViewModel();
CuentaViewModel.errores_cuenta = ko.validation.group(cuenta.cuentaVO);
CuentaViewModel.errores_extracto = ko.validation.group(cuenta.extractoVO);
ko.applyBindings(cuenta);
