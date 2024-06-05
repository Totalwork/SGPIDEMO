
function Detalle_giroViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.contrato_contratista=ko.observable(false);
    self.check_contratista=ko.observable(false);

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
    self.numero_contrato_encabezado=ko.observable('');
    self.nombre_anticipo_encabezado=ko.observable('');
    self.nombre_proyecto_encabezado=ko.observable('');
    self.suma_valor_detalles=ko.observable('');

    self.nombre_contratista_obra=ko.observable('');
    self.id_contratista_obra=ko.observable(0);
    self.nombre_banco_proyecto=ko.observable('');

    //Asociar autorizacion
    self.consecutivo=ko.observable('');
    self.ano=ko.observable(new Date().getFullYear());
    self.soporte_empresa_validacion=ko.observable('');
    
    //var num=0;
    //self.url=path_principal+'api/empresa'; 

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
        soporte_autorizacion:ko.observable(''),
        codigo_pago:ko.observable(''),
        banco_id:ko.observable('').extend({ required: { message: '(*)Seleccione el banco' } }),
        contratista_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contratista' } }),
        encabezado_id:ko.observable(0),
        estado_id:ko.observable(1),

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
        }
    }

    //Funcion para crear la paginacion del detalle del giro
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

    //funciona para la paginacion del detalle del giro
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


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
        self.detalle_giroVO.soporte_autorizacion('');
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


    //consultar los encabezado del giro
    self.encabezado_detalle=function(encabezado){

        /*var encabezado_id=self.detalle_giroVO.encabezado_id();*/

         path =path_principal+'/api/Encabezado_giro/'+encabezado+'/?format=json';
         parameter = { };
         RequestGet(function (datos, estado, mensaje) {
            if(datos){
                self.contratista_encabezado(datos.contrato.contratista.nombre);
                self.contratante_encabezado(datos.contrato.contratante.nombre);
                self.numero_contrato_encabezado(datos.contrato.numero);
                self.nombre_anticipo_encabezado(datos.nombre.nombre);
                self.nombre_proyecto_encabezado(datos.contrato.nombre);
                self.suma_valor_detalles(datos.suma_detalle);
            }

         }, path, parameter,undefined,false,false);

    }    


    //funcion consultar y traer los datos del detalle del giro
    self.consultar = function (pagina) {

        var encabezado_id=self.detalle_giroVO.encabezado_id();
        //alert(encabezado_id)

        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());

            path = path_principal+'/api/Detalle_giro/';
            parameter = { dato: self.filtro(), page: pagina, encabezado_id:encabezado_id , sin_paginacion : 1};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos)); 
                    //detalle_giro.encabezado_detalle(encabezado_id);
                    cerrarLoading();  

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading(); 
                }

                // self.llenar_paginacion(datos,pagina);

            }, path, parameter,undefined, false);
        }
    }

    //funcion para seleccionar los datos a eliminar del detalle del giro
    self.checkall.subscribe(function(value ){
         ko.utils.arrayForEach(self.listado(), function(d) {
                d.eliminado(value);
         }); 
    });




}

var detalle_giro = new Detalle_giroViewModel();
Detalle_giroViewModel.errores_giros_detalle = ko.validation.group(detalle_giro.detalle_giroVO);
ko.applyBindings(detalle_giro);

