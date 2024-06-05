function CuentaViewModel() {

	var self = this;
	self.url=path_principal+'/api/';
  self.app_cuenta = 'cuenta';
  self.app_cuenta_movimiento = 'cuenta_movimiento';

	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.checkall=ko.observable(false);

	//LISTADOS   
	self.listado_cuenta=ko.observableArray([]);
	self.listado_cuenta_movimiento=ko.observableArray([]);
	self.listado_tipos_cuenta=ko.observableArray([]);
  self.listado_tipos_movimiento=ko.observableArray([]);
	self.listado_contratos=ko.observableArray([]);
    //FILTROS
    self.filtro_cuenta=ko.observable('');
    self.filtro_cuenta_movimiento=ko.observable('');


	 //Representa un modelo de la tabla cuenta
    self.cuentaVO={
	 	id:ko.observable(0),
	 	nombre:ko.observable('').extend({ required: { message: '(*) Digite el nombre de la cuenta.' } }),
        numero:ko.observable('').extend({ required: { message: '(*) Digite el numero de la cuenta.' } }),
        valor:ko.observable(0).extend({ required: { message: '(*) Digite el valor de ingreso.' } }),        
        contrato_id:ko.observable('').extend({ required: { message: '(*) Seleccione el macro contrato.' } }),
        fiduciaria:ko.observable('').extend({ required: { message: '(*) Digite la fiduciaria bancaria.' } }),
        tipo_id:ko.observable('').extend({ required: { message: '(*) Digite el tipo de cuenta bancaria.' } }),
        codigo_fidecomiso:ko.observable(''),
        codigo_fidecomiso_a:ko.observable(''),
        empresa_id:ko.observable(''),
	 };

	 self.cuenta_movimientoVO={
	 	    id:ko.observable(0),
	 	    cuenta_id:ko.observable('').extend({ required: { message: '(*) Seleccione la cuenta.' } }),
        tipo_id:ko.observable(0).extend({ required: { message: '(*) Seleccione el tipo de movimiento.' } }),
        valor:ko.observable('').extend({ required: { message: '(*) Digite el valor del movimiento.' } }),        
        descripcion:ko.observable('').extend({ required: { message: '(*) Digite la descripcion del movimiento.' } }),
        fecha:ko.observable('').extend({ required: { message: '(*) Seleccione la fecha del movimiento.' } }),
        periodo_inicial:ko.observable('').extend({ required: { message: '(*) Seleccione el mes inicial' } }),
        periodo_final:ko.observable('').extend({ required: { message: '(*) Seleccione el mes final.' } }),
        ano:ko.observable('').extend({ required: { message: '(*) Digite el año del periodo.' } }),
	 };

	 self.paginacion = {
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
    // //limpiar el modelo 
     self.limpiar_cuenta=function(){        
        self.cuentaVO.id(0);
        self.cuentaVO.nombre('');
        self.cuentaVO.numero('');
        self.cuentaVO.valor(0);
        self.cuentaVO.contrato_id(0);
        self.cuentaVO.fiduciaria('');
        self.cuentaVO.tipo_id('');
        self.cuentaVO.codigo_fidecomiso('');
        self.cuentaVO.codigo_fidecomiso_a('');
        self.cuentaVO.empresa_id('');
     }

     self.limpiar_cuenta_movimiento=function(){        
        self.cuentaVO.id(0);
        self.cuentaVO.nombre('');
        self.cuentaVO.numero('');
        self.cuentaVO.valor(0);
        self.cuentaVO.contrato_id(0);
        self.cuentaVO.fiduciaria('');
        self.cuentaVO.tipo_id('');
        self.cuentaVO.codigo_fidecomiso('');
        self.cuentaVO.codigo_fidecomiso_a('');
        self.cuentaVO.empresa_id('');
     }

    self.abrir_modal = function () {
        self.limpiar_cuenta();
        self.titulo('Registrar Cuenta');
        $('#modal_acciones').modal('show');
    }
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }
    //FUNCION PARA INABIHILITAR LA CUENTA
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un banco para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/empresa/eliminar_id/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los bancos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }    
    }  
    //consultar los macrocontrato
    self.consultar_contratos=function(){        
         path ='/contrato/list_contrato';
         parameter = { tipo : 1 };
         RequestGet(function (results,count) {
            self.listado_contratos(results);
         }, path, parameter);
    }
    //funcion consultar tipos de cuentas bancarias 
    self.consultar_tipos_cuenta = function () {                
            path = '/api/Tipos?format=json';
            parameter = { ignorePagination : 1 , aplicacion : self.app_cuenta };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_tipos_cuenta(datos);
                } else {
                    self.listado_tipos_cuenta([]);                    
                }             
            }, path, parameter);        
    }
	 // //funcion guardar
     self.guardar_cuenta=function(){

    	if (CuentaViewModel.errores_cuenta().length == 0) {//se activa las validaciones
            if(self.cuentaVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.filtro_cuenta("");
                            self.consultar_cuenta(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar_cuenta();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url+'Cuenta/',//url api
                     parametros : self.cuentaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                              self.filtro_cuenta("");
                              self.consultar_cuenta(self.paginacion.pagina_actual());
                              $('#modal_acciones').modal('hide');
                              self.limpiar_cuenta();
                            } 
                       },//funcion para recibir la respuesta 
                       url: self.url+'Cuenta/'+ self.cuentaVO.id()+'/',
                       parametros : self.cuentaVO                        
                  };
                  RequestFormData(parametros);
            }
        } else {
             CuentaViewModel.errores_cuenta.showAllMessages();//mostramos las validacion
        }
     }
    //funcion consultar proyectos que ppuede  ver la empresa
    self.consultar_cuenta = function (pagina) {
        if (pagina > 0) {            
            self.filtro_cuenta($('#txtBuscar').val());
            path = '/api/Cuenta'+'?format=json&page='+pagina;
            parameter = { dato: self.filtro_cuenta(), pagina: pagina };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado_cuenta(agregarOpcionesObservable(datos.data));  
                } else {
                    self.listado_cuenta([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
            }, path, parameter);
        }
    }
    //exportar excel    
    self.exportar_excel=function(){
        location.href=path_principal+"/parametrizacion/export_banco?dato="+self.filtro();
    }

    self.consultar_por_id = function (obj) {

       path =path_principal+'/api/Cuenta/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
            self.titulo('Actualizar Cuenta');
            self.cuentaVO.id(results.id);
            self.cuentaVO.nombre(results.nombre);
            self.cuentaVO.numero(results.numero);
            self.cuentaVO.valor(results.valor);             
            self.cuentaVO.contrato_id(results.contrato.id);
            self.cuentaVO.fiduciaria(results.fiduciaria);
            self.cuentaVO.tipo_id(results.tipo.id);
            self.cuentaVO.codigo_fidecomiso(results.codigo_fidecomiso);
            self.cuentaVO.codigo_fidecomiso_a(results.codigo_fidecomiso_a);
            self.cuentaVO.empresa_id(results.empresa_id);

             $('#modal_acciones').modal('show');
         }, path, parameter);
     }   

// -- CUENTA MOVIMIENTO -- -- CUENTA MOVIMIENTO ---- CUENTA MOVIMIENTO ---- CUENTA MOVIMIENTO ---- CUENTA MOVIMIENTO --
    //funcion consultar tipos de cuentas bancarias 
    self.consultar_tipos_movimientos = function () {                
            path = '/api/Tipos?format=json';
            parameter = { ignorePagination : 1 , aplicacion : self.app_cuenta_movimiento };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_tipos_movimiento(datos);
                } else {
                    self.listado_tipos_movimiento([]);                    
                }             
            }, path, parameter);        
    }
    self.abrir_modal_movimiento = function () {
        self.limpiar_cuenta_movimiento();
        self.titulo('Registrar Movimiento');
        $('#modal_acciones_form_movimientos').modal('show');
    }

    self.ver_movimientos = function (cuenta_id) {
        $('#modal_acciones_movimientos').modal('show');  
        self.consultar_cuenta_movimiento(1 , cuenta_id); 
        self.cuenta_movimientoVO.cuenta_id(cuenta_id);
    }

    self.consultar_cuenta_movimiento = function (pagina , cuenta_id) {                     
          
          path = self.url+'Cuenta_movimiento'+'?format=json&page='+pagina;
          parameter = { dato: self.filtro_cuenta_movimiento(), pagina: pagina };
          RequestGet(function (datos, estado, mensage) {

              if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                  self.mensaje('');
                  //self.listado(results); 
                  self.listado_cuenta_movimiento(agregarOpcionesObservable(datos.data));  

              } else {
                  self.listado_cuenta_movimiento([]);
                  self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
              }

              self.llenar_paginacion(datos,pagina);
          }, path, parameter);
    } 

    // //funcion guardar
     self.guardar_cuenta_movimiento=function(){

      if (CuentaViewModel.errores_cuenta_movimiento().length == 0) {//se activa las validaciones
            if(self.cuenta_movimientoVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.filtro_cuenta("");
                            self.consultar_cuenta_movimiento(self.paginacion.pagina_actual() , self.cuenta_movimientoVO.cuenta_id());
                            $('#modal_acciones_form_movimientos').modal('hide');
                            self.limpiar_cuenta_movimiento();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url+'Cuenta_movimiento/',//url api
                     parametros : self.cuenta_movimientoVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                              self.filtro_cuenta("");
                              self.consultar_cuenta_movimiento(self.paginacion.pagina_actual());
                              $('#modal_acciones_form_movimientos').modal('hide');
                              self.limpiar_cuenta_movimiento();
                            } 
                       },//funcion para recibir la respuesta 
                       url: self.url+'Cuenta_movimiento/'+ self.cuenta_movimientoVO.id()+'/',
                       parametros : self.cuenta_movimientoVO                        
                  };
                  RequestFormData(parametros);
            }
        } else {
             CuentaViewModel.errores_cuenta_movimiento.showAllMessages();//mostramos las validacion
        }
     }   
    // --FINALIZA  CUENTA MOVIMIENTO -- --FINALIZA CUENTA MOVIMIENTO ----FINALIZA CUENTA MOVIMIENTO ----FINALIZA CUENTA MOVIMIENTO ----FINALIZA CUENTA MOVIMIENTO --

}

var cuenta = new CuentaViewModel();
CuentaViewModel.errores_cuenta = ko.validation.group(cuenta.cuentaVO);
CuentaViewModel.errores_cuenta_movimiento = ko.validation.group(cuenta.cuenta_movimientoVO);
cuenta.consultar_contratos();
cuenta.consultar_tipos_cuenta();
cuenta.consultar_tipos_movimientos();
cuenta.consultar_cuenta(1);//iniciamos la primera funcion

ko.applyBindings(cuenta);