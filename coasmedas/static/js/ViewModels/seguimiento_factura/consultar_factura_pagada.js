
function FacturaPagadaViewModel() {
    
    var self = this;
    self.listado_factura=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.mensajeModal = ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.listado_pago=ko.observableArray([]);
    self.listado_factura_pagada=ko.observableArray([]);
    self.id_editar=ko.observable();
    self.listado_pago_factura=ko.observableArray([]);
    self.lista_contrato=ko.observableArray([]);
    self.lista_contratista=ko.observableArray([]);
    self.lista_cuenta=ko.observableArray([]);
    self.desde=ko.observable('');
    self.hasta=ko.observable('');
    self.test_op_id=ko.observable('');

    //Representa un modelo de la gestion_op
    self.test_opVO={
        id:ko.observable(0),
        valor:ko.observable(0),
        codigo:ko.observable(''),      
        fecha_registro:ko.observable(''),
        fecha_pago:ko.observable(''),   
        soporte:ko.observable(''),
        beneficiario_id:ko.observable(''),
        contrato_id:ko.observable(''),
        pagado_recursos_propios:ko.observable(''),
        soporte_pago:ko.observable('')
        
     };


    //paginacion de la funcion consultar_pago_factura
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
        self.consultar_pago_factura(pagina);
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    //funcion para filtrar las facturas pagadas sin recursos propios
    self.filtrar_facturas_pagadas_sin_recursos = function (recursos) {
        self.titulo('Filtrar');
         self.consultar_cuenta();
        self.consultar_macrocontrato(recursos);
        self.consultar_contratista(recursos);
        $('#modal_factura_pagadas').modal('show');
    }


    //funcion consultar las facturas pagadas
    self.consultar = function () {
        
        self.filtro($('#busqueda_factura').val());
        var bloqueo_factura=0;
        var recursos_propios=0;
        var pagada=1;
        
        path = path_principal+'/api/Factura?format=json';
        parameter = { numero: self.filtro(),bloqueo_factura:bloqueo_factura,recursos_propios:recursos_propios, pagada:pagada};
        RequestGet(function (datos, estado, mensage) {

            console.log(datos.data)

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje('');
                self.listado_factura(agregarOpcionesObservable(datos.data));  

            } else {
                self.listado_factura([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }

        }, path, parameter);
    }

        //funcion consultar las facturas pagadas
    self.consultar_listado_pago = function (id) {


        path = path_principal+'/api/gestion_op?format=json&sin_paginacion=';
        parameter = { id_pago:id};
        RequestGet(function (datos, estado, mensage) {

            console.log(datos)

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensaje('');
                self.listado_pago(agregarOpcionesObservable(datos));  

            } else {
                self.listado_pago([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }

        }, path, parameter);
    }


        //funcion consultar las facturas pagadas
    self.consultar_factura_pagada = function (obj) {
        
        self.filtro($('#busqueda_factura').val());
        self.test_op_id(obj.id);
        var bloqueo_factura=0;
        var recursos_propios=0;
        var pagada=1;
        
        path = path_principal+'/api/Factura?format=json';
        parameter = {bloqueo_factura:bloqueo_factura,recursos_propios:recursos_propios, pagada:pagada,codigo_op:obj.id};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {

                self.titulo('Listado de facturas');

                self.mensajeModal('');
                self.listado_factura_pagada(agregarOpcionesObservable(datos.data));

            } else {
                self.listado_factura_pagada([]);
                self.mensajeModal(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
            $('#modalFactura').modal('show');  

        }, path, parameter);
    }


    self.consultar_facturas = function (obj) {
        
        self.filtro($('#busqueda_factura').val());
        self.test_op_id(obj.id);
        var bloqueo_factura=0;
        var recursos_propios=0;
        var pagada=1;
        
        path = path_principal+'/api/Factura?format=json';
        parameter = {bloqueo_factura:bloqueo_factura,recursos_propios:recursos_propios, codigo_op:obj.id};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {

                self.titulo('Listado de facturas');

                self.mensajeModal('');
                self.listado_factura_pagada(agregarOpcionesObservable(datos.data));

            } else {
                self.listado_factura_pagada([]);
                self.mensajeModal(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
            $('#modalFactura').modal('show');  

        }, path, parameter);
    }


        //funcion para consultar por id el detalle del giro
    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/gestion_op/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Establecer fecha de pago');

            self.test_opVO.id(datos.id);
            self.test_opVO.valor(datos.valor);
            self.test_opVO.codigo(datos.codigo);
            self.test_opVO.fecha_registro(datos.fecha_registro==null ? '' : datos.fecha_registro);
            self.test_opVO.fecha_pago(datos.fecha_pago);
            self.test_opVO.soporte('');
            self.test_opVO.beneficiario_id(datos.beneficiario.id);
            self.test_opVO.contrato_id(datos.contrato.id);
            self.test_opVO.pagado_recursos_propios(datos.pagado_recursos_propios);

             $('#modalfecha').modal('show');

         }, path, parameter);

     }


    //funcion actualizar gestion_op
    self.guardar=function(){

        if(self.test_opVO.fecha_pago()==''){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione la fecha de pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false
        }

        var parametros={     
             metodo:'PUT',                
            callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                    $('#modalfecha').modal('hide');
                }  

            },//funcion para recibir la respuesta 
            url:path_principal+'/api/gestion_op/'+self.test_opVO.id()+'/',
            parametros:self.test_opVO,
            completado:function(){
             self.consultar_pago_factura(1,0);
            }                         
        };

        RequestFormData(parametros);

    }


    //funcion consultar las test op de la facturas pagadas
    self.consultar_pago_factura = function (pagina) {
    
        if (pagina > 0) { 

            self.filtro($('#txtBuscar').val());
            var contrato=$('#mcontrato_filtro').val();
            var contratista=$('#contratista_filtro').val();
            var cuenta=$('#cuenta_filtro').val();
    
            path = path_principal+'/api/gestion_op?format=json';
            parameter = { dato: self.filtro(), page: pagina, contrato:contrato, contratista:contratista, 
                            cuenta:cuenta, desde:self.desde(), hasta:self.hasta(), recursos:0};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado_pago_factura(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)

                } else {
                    self.listado_pago_factura([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter);
        }
    }


     //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar_pago_factura(1);
        }
        return true;
    }


    //consultar los macrocontrato, contratista y cuenta para filtrar facturas pagadas
    self.consultar_cuenta=function(){

         path = path_principal+'/api/gestion_op?format=json&sin_paginacion=';
         parameter={ recursos:0 };
         RequestGet(function (datos, estado, mensaje) {
            self.lista_cuenta(datos);

         }, path, parameter);

    }

    self.consultar_macrocontrato=function(recursos){

         path = path_principal+'/seguimiento_factura/filtro_contrato_pago/?recursos='+recursos;
         RequestGet(function (datos, estado, mensaje) { 
            self.lista_contrato(datos);

         }, path, parameter);

    }


    self.consultar_contratista=function(recursos){

         path = path_principal+'/seguimiento_factura/filtro_contratista_pago/?recursos='+recursos;
         RequestGet(function (datos, estado, mensaje) { 
            self.lista_contratista(datos);
         }, path, parameter);

    }

       //exportar excel del detalle del giro
   self.exportar_excel_gestion=function(){
        var recursos=0;
        location.href=path_principal+"/seguimiento_factura/exportar_gestion_op/?recursos="+recursos;
    }


    self.exportar_facturas_pagadas=function(){
        self.test_op_id();
        var bloqueo_factura=0;
        var recursos_propios=0;
        var pagada=1;

        location.href=path_principal+"/seguimiento_factura/export-factura-pagadas/?bloqueo_factura="+bloqueo_factura+"&recursos_propios="+recursos_propios+"&pagada="+pagada+"&codigo_op="+self.test_op_id();
    }

    self.exportar_facturas = function(){
        self.test_op_id();
        var bloqueo_factura=0;
        var recursos_propios=0;

        location.href=path_principal+"/seguimiento_factura/export-factura/?bloqueo_factura="+bloqueo_factura+"&recursos_propios="+recursos_propios+"&codigo_op="+self.test_op_id();
    }


    //exportar excel
   self.generar_reporte=function(obj){

        var orden_pago=1;
        var bloqueo_factura=0;
        var pagada=1;

        
        path = "http://caribemar.sinin.co:8080/exportar/factura-orden-operacion-test-op?codigo_op_id="+obj.id+"&valida=1";
        //path = "http://localhost:51149/exportar/factura-orden-operacion-test-op?codigo_op_id="+obj.id+"&valida=1";
        parameter = {};
        RequestGet(function (datos, estado, mensage) {

            console.log(datos)
            if(datos.fiduciaria=="FIDUBOGOTA"){
                location.href=path_principal+"/seguimiento_factura/generar-reporte/?bloqueo_factura="+bloqueo_factura+"&orden_pago="+orden_pago+"&testop_id="+obj.id;
            }else{
                location.href = "http://caribemar.sinin.co:8080/exportar/factura-orden-operacion-test-op?codigo_op_id="+obj.id+"&valida=";
                //location.href = "http://localhost:51149/exportar/factura-orden-operacion-test-op?codigo_op_id="+obj.id+"&valida=";
            }

        }, path, parameter);   

    }



}

var factura_pagada = new FacturaPagadaViewModel();
ko.applyBindings(factura_pagada);
