
function EmpresaCuentaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.lista_tipo_select=ko.observableArray([]);
    self.lista_empresaselect=ko.observableArray([]);
    self.lista_estado=ko.observableArray([]);
    self.estadocuenta=ko.observable('');


     //Representa un modelo de empresa cuenta
    self.empresaCuentaVO={
        id:ko.observable(0),
        empresa_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contratista' } }),
        tipo_cuenta_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de cuenta' } }),
        entidad_bancaria:ko.observable('').extend({ required: { message: '(*)Digite la entidad bancaria' } }),
        numero_cuenta:ko.observable('').extend({ required: { message: '(*)Digite el numero de la cuenta' } }),
        estado_id:ko.observable(1),

     };

     //paginacion de empresa cuenta
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
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

  
    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });

    //funcion para abrir modal de empresa cuenta
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Cuenta');
        $('#modal_acciones').modal('show');
    }


    //funcion para abri el mnodal de actualizar estado
    self.cambiar_estado = function () {
        self.titulo('Actualizar estado');
        self.consultar_estado();
        $('#modal_estado').modal('show');
    }


     //limpiar el modelo de empresa cuenta
     self.limpiar=function(){     
         
        self.empresaCuentaVO.id(0);
        self.empresaCuentaVO.empresa_id('');
        self.empresaCuentaVO.tipo_cuenta_id('');
        self.empresaCuentaVO.numero_cuenta('');
        self.empresaCuentaVO.entidad_bancaria('');
        self.empresaCuentaVO.estado_id(1);

        self.empresaCuentaVO.empresa_id.isModified(false);
        self.empresaCuentaVO.tipo_cuenta_id.isModified(false);
      
     }

    //consultar los estados
    self.consultar_estado=function(){

         path =path_principal+'/api/Estados/?ignorePagination';
         parameter = { aplicacion: 'EstadoCuenta'};
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_estado(datos);

         }, path, parameter,undefined,false,false);

    }



    //consultar los tipos para llenar un select
    self.consultar_lista_empresa=function(){
        
         path =path_principal+'/api/empresa?sin_paginacion';
         //parameter={ aplicacion: 'cuenta' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_empresaselect(datos);

         }, path, parameter,undefined,false,false);

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

        if (EmpresaCuentaViewModel.errores_empresa_cuenta().length == 0) {//se activa las validaciones

            if(self.empresaCuentaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/empresaCuenta/',//url api
                     parametros:self.empresaCuentaVO                        
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
                       url:path_principal+'/api/empresaCuenta/'+self.empresaCuentaVO.id()+'/',
                       parametros:self.empresaCuentaVO                        
                  };

                  Request(parametros);

            }

        } else {
             EmpresaCuentaViewModel.errores_empresa_cuenta.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar 
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            
            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("dato_cuenta", $('#txtBuscar').val() || '');
            self.cargar(pagina);
            
        }
    }


    self.cargar = function(pagina){

        let filtro = sessionStorage.getItem("dato_cuenta");

        path = path_principal+'/api/empresaCuenta?format=json';
            parameter = { dato: filtro, page: pagina};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
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


    //consultar por id de la cuenta
    self.consultar_por_id = function (obj) {
       
       path =path_principal+'/api/empresaCuenta/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar Empresa Cuenta');

            self.empresaCuentaVO.id(datos.id);
            self.empresaCuentaVO.empresa_id(datos.empresa.id);
            self.empresaCuentaVO.tipo_cuenta_id(datos.tipo_cuenta.id);
            self.empresaCuentaVO.numero_cuenta(datos.numero_cuenta);
            self.empresaCuentaVO.entidad_bancaria(datos.entidad_bancaria);
            self.empresaCuentaVO.estado_id(datos.estado.id);
             
            $('#modal_acciones').modal('show');

         }, path, parameter);

     }

   
    //Actualiza el campo orden pago de las facturas
    self.actualizar_cuenta = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las cuentas a actualizar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/empresa/actualizar-empresa-cuenta/';
             var parameter = { lista: lista_id, estado:self.estadocuenta()};
             RequestAnularOEliminar("Esta seguro que desea actualizar el estado de las cuentas seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
                 $('#modal_estado').modal('hide');
             })

         }     
        
    }


    //exportar excel la tabla del listado de las cuentas
    self.exportar_excel=function(){

        location.href=path_principal+"/empresa/exportar-empresa-cuenta/";
    } 
  

}

var empresa = new EmpresaCuentaViewModel();
EmpresaCuentaViewModel.errores_empresa_cuenta = ko.validation.group(empresa.empresaCuentaVO);
ko.applyBindings(empresa);
