function FacturaPorPagarViewModel() {
	
    var self = this;
    
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.mensajePorAsignar=ko.observable('');
    self.mensajeAsignados=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');


    self.checkall= ko.observable(false);
   
    self.url= path_principal+'/api/';  
 
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

    self.paginacion.pagina_actual.subscribe(function (pagina) {    
       self.consultar(pagina);
    });

    self. factura_por_pagar = {
        id: ko.observable(''),
        fecha_pago: ko.observable(''),
    }


    self.filtro_factura={
        mcontrato:ko.observable(''),
        tipo:ko.observable(''),
        contratista_lista:ko.observableArray([]),
        contratista_nom:ko.observable(''),
        contratista:ko.observable(),
        numero_c:ko.observable(''),
        numero_f:ko.observable('')
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Proyecto');
        $('#modal_acciones').modal('show');
        /*self.consultar_macro_contrato(0,0);*/
        self.consultar_select_create_update_proyecto();
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }
    //exportar excel    
    self.exportar_excel=function(){
        location.href= path_principal+"/seguimiento_factura/exportar-facturas_por-contabilizar/?id_mcontrato="+self.filtro_factura.mcontrato()+
                                                                                        "&tipo_contrato="+self.filtro_factura.tipo()+
                                                                                        "&id_contratista="+self.filtro_factura.contratista()+
                                                                                        "&numero_contrato="+self.filtro_factura.numero_c()+
                                                                                        "&numero="+self.filtro_factura.numero_f();
    }   
    // //limpiar el modelo 
     self.limpiar=function(){    	 

     }
   
    //funcion consultar proyectos que ppuede  ver la empresa
    self.consultar = function (pagina) {
        if (pagina > 0) { 
            self.filtro($('#txtBuscar').val());

            path = self.url+'Factura/?format=json';
            parameter = { dato: self.filtro()
                        , page: pagina
                        ,id_mcontrato:self.filtro_factura.mcontrato()
                        ,tipo_contrato:self.filtro_factura.tipo()
                        ,id_contratista: self.filtro_factura.contratista()
                        ,numero_contrato: self.filtro_factura.numero_c()
                        ,numero: self.filtro_factura.numero_f()
                        ,por_pagar_cuenta_bancaria: true
                                    
                        
                        };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data)); 
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    self.abrir_modal_busqueda = function () {
        self.titulo('Consulta de facturas');
        $("#modal_busqueda").modal("show");
    }

    self.consulta_enter_filtro = function (d,e) {
        if (e.which == 13) {
            //self.filtro($('#txtBuscar').val());
            self.empresa();
            //console.log("asa;"+$('#nom_nit1').val());
        }
        return true;
    }

    // Buscar el contratista
    self.empresa=function(){
        // parameter={dato:$("#contratista_nom").val() };
        if(self.filtro_factura.contratista_nom() != ''){

            parameter={dato: self.filtro_factura.contratista_nom() };
            path =path_principal+'/api/empresa/?sin_paginacion&esContratista=1&format=json';

            RequestGet(function (results,count) {

                self.filtro_factura.contratista_lista(results);
            }, path, parameter, undefined, true);
        }
    }

    //funcion para seleccionar los datos a eliminar
        self.checkall.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado(), function(d) {
                d.eliminado(value);
            }); 
        });

    self.abrir_establecer = function () {
        self.factura_por_pagar.fecha_pago('');
        self.titulo('Establecer pago');
        $('#modal_establecer').modal('show');
    }

    self.establecerpago = function (){

        var lista_id=[];
        var count=0;
        var c = 0;
        var lista_test = [];
        var sw = 0;

         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                    lista_id.push(d.id)
                    var codigo_test_op = d.codigo_op.codigo;
                    if(c==0){
                        lista_test.push(codigo_test_op);                        
                    }
                    else{
                        if(lista_test.indexOf(codigo_test_op)>-1){
                            lista_test.push(codigo_test_op);                            
                        }else{
                            sw = 1;
                        }
                    }
                    c+=1;
                    
                }
         });


         if(self.factura_por_pagar.fecha_pago()=='') {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione una fecha de pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione una factura para establecer su pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else if(sw == 1) {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione las facturas de un mismo grupo de TEST/OP.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
         }
         else{
             var path = path_principal+'/seguimiento_factura/actualizar-pago-factura/';
             var parameter = { lista: lista_id, fecha_pago: self.factura_por_pagar.fecha_pago() };
             RequestAnularOEliminar(" Esta seguro que desea establecer el pago de las facturas seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
                 $('#modal_establecer').modal('hide');
             })
         } 
    }

   


}

var facturas_por_pagar = new FacturaPorPagarViewModel();


ko.applyBindings(facturas_por_pagar);