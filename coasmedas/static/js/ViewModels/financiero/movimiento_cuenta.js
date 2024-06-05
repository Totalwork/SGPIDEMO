
function MovimientoCuentaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.lista_tipo_select=ko.observableArray([]);
    self.desde=ko.observable('');
    self.hasta=ko.observable('');
    self.desde_filtro=ko.observable('');
    self.hasta_filtro=ko.observable('');
    self.validacion_tipo_cuenta=ko.observable(0);

    //encabezado de los movimientos de la cuenta
    self.nombre=ko.observable('');
    self.numero=ko.observable('');
    self.banco = ko.observable('');
    self.tipo = ko.observable('');
    self.cantidad_movimiento=ko.observable('');
    self.suma_egreso=ko.observable('');
    self.suma_ingreso=ko.observable('');
    self.suma_rendimiento=ko.observable('');


     //Representa el modelo del movimiento de la cuenta
    self.movimiento_cuentaVO={
        id:ko.observable(0),
        valor:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor del movimiento' } }),
        descripcion:ko.observable(''),
        fecha:ko.observable('').extend({ required: { message: '(*)Seleccione la fecha' } }),
        periodo_inicio:ko.observable(''),
        periodo_final:ko.observable(''),
        ano:ko.observable(0),
        cuenta_id:ko.observable(''),
        tipo_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de movimiento' } }),
        bloquear:ko.observable(false),
        // desde:ko.observable(''),
        // hasta:ko.observable(''),

     };

     //paginacion del movimiento de la cuenta
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

  
    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });

    //funcion para abrir modal de registrar cuentas
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Movimiento');
        $('#modal_acciones').modal('show');
    }


    //funcion para filtrar los movimientos de las cuentas
    self.filtrar_movimiento = function () {
        self.titulo('Filtrar Movimiento');
        //self.limpiar();
        self.consultar_lista_tipo();
        $('#modal_filtro_movimiento').modal('show');
    }


    //funcion para exportar a excel las cuenta
    self.exportar_excel = function (obj) {
        self.titulo('Generar informe');
        $('#modal_informe').modal('show');
    }


     //limpiar el modelo del movimiento de la cuenta
     self.limpiar=function(){     
         
             self.movimiento_cuentaVO.id(0);
             self.movimiento_cuentaVO.valor(0);
             self.movimiento_cuentaVO.descripcion('');
             self.movimiento_cuentaVO.fecha('');
             self.movimiento_cuentaVO.periodo_inicio('');
             self.movimiento_cuentaVO.periodo_final('');
             self.movimiento_cuentaVO.ano(0)
             //self.movimiento_cuentaVO.cuenta_id('');
             self.movimiento_cuentaVO.tipo_id('');
             // self.movimiento_cuentaVO.desde('');
             // self.movimiento_cuentaVO.hasta('');

             self.movimiento_cuentaVO.fecha.isModified(false);
             self.movimiento_cuentaVO.tipo_id.isModified(false); 
      
     }


    //consultar los tipos para llenar un select
    self.consultar_lista_tipo=function(){
        
         path =path_principal+'/api/Tipos?ignorePagination';
         parameter={ dato: 'TipoFinacieroCuentaMovimiento' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_tipo_select(datos);

         }, path, parameter,undefined,false,false);

    }


    //funcion guardar y actualizar el movimiento de la cuenta
     self.guardar=function(){

        if (MovimientoCuentaViewModel.errores_movimiento().length == 0) {//se activa las validaciones            
            if(self.movimiento_cuentaVO.valor()<0){
                mensajeError('El valor del movimiento debe ser mayor o igual que 0');
                return;
            }
            if(self.movimiento_cuentaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Financiero_cuenta_movimiento/',//url api
                     parametros:self.movimiento_cuentaVO,
                     completado:function(){
                         self.encabezado_movimiento();
                       }                          
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
                       url:path_principal+'/api/Financiero_cuenta_movimiento/'+self.movimiento_cuentaVO.id()+'/',
                       parametros:self.movimiento_cuentaVO,
                       completado:function(){
                         self.encabezado_movimiento();
                       }                          
                  };

                  Request(parametros);

            }

        } else {
             MovimientoCuentaViewModel.errores_movimiento.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar las cuentas
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            
            self.filtro($('#txtBuscar').val());
            var tipo_filtro=$("#tipo_filtro").val();
            var desde=$("#desde_filtro").val();
            var hasta=$("#hasta_filtro").val();
            var cuenta_id=self.movimiento_cuentaVO.cuenta_id();

            path = path_principal+'/api/Financiero_cuenta_movimiento?format=json';
            parameter = { dato: self.filtro(), page: pagina,tipo_filtro:tipo_filtro, desde:desde, hasta:hasta, cuenta_id:cuenta_id};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    $('#modal_filtro_movimiento').modal('hide'); 
                    self.listado(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)
                    cerrarLoading();

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
                }
                self.encabezado_movimiento();
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


    //consultar por id del movimiento
    self.consultar_por_id = function (obj) {
       
       path =path_principal+'/api/Financiero_cuenta_movimiento/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar Movimiento');

            self.movimiento_cuentaVO.id(datos.id);
            self.movimiento_cuentaVO.valor(datos.valor);
            self.movimiento_cuentaVO.descripcion(datos.descripcion);
            self.movimiento_cuentaVO.fecha(datos.fecha);
            self.movimiento_cuentaVO.tipo_id(datos.tipo.id);
            self.movimiento_cuentaVO.bloquear(datos.bloquear);
            // self.movimiento_cuentaVO.desde(datos.desde);
            // self.movimiento_cuentaVO.hasta(datos.hasta);
             
             $('#modal_acciones').modal('show');

         }, path, parameter);

     }

   
    //eliminar los movimientos
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los movimiento para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/financiero/eliminar_movimiento/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los movimientos seleccionads?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
                 self.encabezado_movimiento();
             })

         }     
    
        
    }


    //exportar excel la tabla del listado de las cuentas
   self.exportar_excel_movimiento=function(){

         var desde=$("#desde_filtro").val();
         var hasta=$("#hasta_filtro").val();
         var tipo_filtro=$("#tipo_filtro").val();
         var cuenta_id=self.movimiento_cuentaVO.cuenta_id();

         location.href=path_principal+"/financiero/exportar_movimiento/?desde="+desde+"&hasta="+hasta+"&cuenta_id="+cuenta_id+"&tipo_filtro="+tipo_filtro;
     } 


              //consultar los encabezado del giro
    self.encabezado_movimiento=function(){

        var desde=$("#desde_filtro").val();
        var hasta=$("#hasta_filtro").val();
        var tipo_filtro=$("#tipo_filtro").val();


         path =path_principal+'/financiero/encabezado/';
         parameter={ cuenta_id: self.movimiento_cuentaVO.cuenta_id(), desde:desde, hasta:hasta, tipo_filtro:tipo_filtro};
         RequestGet(function (datos, estado, mensaje) {

                self.numero(datos[0].numero);
                self.nombre(datos[0].nombre);
                self.banco(datos[0].fiduciaria);
                self.tipo(datos[0].tipo_nombre);
                self.cantidad_movimiento(datos[0].cantidad_movimiento);
                self.suma_egreso(datos[0].suma_egreso);
                self.suma_ingreso(datos[0].suma_ingreso);
                self.suma_rendimiento(datos[0].suma_rendimiento);


         }, path, parameter,undefined,false,false);

    }


    //validacion de el formulario
    self.movimiento_cuentaVO.tipo_id.subscribe(function(value ){

        self.validacion_tipo_cuenta(value); 

    });


}

var movimiento = new MovimientoCuentaViewModel();
MovimientoCuentaViewModel.errores_movimiento = ko.validation.group(movimiento.movimiento_cuentaVO);
ko.applyBindings(movimiento);
