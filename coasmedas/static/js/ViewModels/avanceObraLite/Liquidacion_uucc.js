function LiquidacionuuccViewModel(){
	var self = this;
	self.titulo=ko.observable('');
	self.mensaje=ko.observable('');
	self.mensaje_ejecutado=ko.observable('');
	self.listado=ko.observableArray([]);
	self.listado_detalle=ko.observableArray([]);
	self.listado_ejecucion=ko.observableArray([]);
	self.url=path_principal+'/api/';
    self.url_funcion=path_principal+'/avanceObraLite/';
    self.checkall2=ko.observable(false);
    self.checkall=ko.observable(false);
    self.mensaje_guardando=ko.observable('');

	self.presupuesto_id= ko.observable($('#id_presupuesto').val());
    self.liquidacion_id=ko.observable(0);
    

	self.liquidacionVO={
		id: ko.observable(0),
		estado: ko.observable(1),	
	};

    self.liquidacionAnular={
        id: ko.observable(0),
        motivo_anular:ko.observable('').extend({ required: { message: '(*)Digite el motivo de la anulación' } }),
    }
	//paginacion de la liquidacion de uucc
    self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(5),
        directiones: ko.observable(true),
        limite: ko.observable(true),
        cantidad_por_paginas: ko.observable(0),
        // totalRegistrosBuscados:ko.observable(0),
        text: {
            first: ko.observable('Inicio'),
            last: ko.observable('Fin'),
            back: ko.observable('<'),
            forward: ko.observable('>')
        }
    };

    //paginacion
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.cargar(pagina);
    });

    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }

    self.limpiar=function(){

    }

    self.checkall2.subscribe(function(value ){
         ko.utils.arrayForEach(self.listado_ejecucion(), function(d) {
            d.eliminado(value);
         }); 
    });

    

    self.guardar=function(){
        $.confirm({
            title:'Confirmar!',
            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Esta seguro que desea guardar la liquidación?</h4> <h4>Posteriormente no se podrá modificar</h4> ',
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {
                self.mensaje_guardando('');
                var lista_id=[];
                var count=0;
                ko.utils.arrayForEach(self.listado_ejecucion(), function(d) {
                    if(d.eliminado()==true){
                        count=1;
                       lista_id.push({
                            id:d.detallepresupuesto__id
                       })
                    }
                });

                if(count==0){
                    self.mensaje_guardando('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>Seleccione al menos una UUCC de un apoyo.</div>');

                 }else{
                    var parametros={                     
                             callback:function(datos, estado, mensaje){
                                //alert('algo')
                                if (estado=='ok') {
                                    self.cargar(1);
                                    mensajeExitoso(mensaje);                            
                                }else{
                                    mensajeError(mensaje);                            
                                }  

                             },//funcion para recibir la respuesta 
                             alerta:false,
                             url:path_principal+'/avanceObraLite/guardar_liquidacionuucc/',//url api
                             parametros:{
                                lista:lista_id,
                                presupuesto_id:self.presupuesto_id()
                            }                       
                        };
                        //parameter =ko.toJSON(self.contratistaVO);
                        Request(parametros);
                 }
            }
        });

    }

    

	self.abrir_modal = function () {

        self.limpiar();
        self.consultar_uucc_ejecutadas(1);
    }    

    self.abrir_detalle_cambio = function (liquidacion_id,estado) {
        
        self.liquidacionVO.id(liquidacion_id || null);
        self.liquidacionVO.estado(estado||1);
        

        self.consultar_detallereportetrabajo();
        self.titulo('Detalle de la liquidacion ');                
        $('#modal_detalle_cambio').modal('show');
        
    }

    self.mostrar_movtivo_anulación=function(liquidacion_id){
        self.liquidacionAnular.id(liquidacion_id);
        //alert(self.liquidacionAnular.id());
        path = path_principal+'/avanceObraLite/consultarmotivoanulacion/';
        parameter={
                liquidacion_id:self.liquidacionAnular.id(),
            };
        //alert(self.liquidacion_id());
        RequestGet(function (datos, estado, mensage) {
            if (estado=='ok') {
                self.titulo('Motivo de anulación');
                $('#motivo_anulacion').modal('show');
                self.liquidacionAnular.id(datos[0].id);
                self.liquidacionAnular.motivo_anular(datos[0].motivo_anulacion);                                             
            }else{                
                self.liquidacionAnular.id(0);
                self.liquidacionAnular.motivo_anular(''); 
                mensajeError(mensajeNoFound);                           
            }
            cerrarLoading();
        }, path, parameter,undefined, false);
    }

    self.consultar_detallereportetrabajo = function(){
        path = path_principal+'/avanceObraLite/consultar_detallereporte_liquidacion/';
        parameter={
                liquidacion_id:self.liquidacionVO.id(),
            };
        //alert(self.liquidacion_id());
        RequestGet(function (datos, estado, mensage) {
            if (estado=='ok') {
                self.listado_detalle(datos);                                             
            }else{
                self.listado_detalle([]);
                mensajeError(mensajeNoFound);                            
            }
            cerrarLoading();
        }, path, parameter,undefined, false);

    }
    

    self.consultar_uucc_ejecutadas = function(opcion,liq_id){

    	path = path_principal+'/avanceObraLite/consultarcantidadesaliquidarlite/';

        //alert(liq_id)
        self.liquidacionVO.id(liq_id || null);
        parameter = {            
            presupuesto_id: self.presupuesto_id(), 
        };

        RequestGet(function (datos, estado, mensage) {
            //alert('algo');
        	if (estado == 'ok' && datos.length > 0) {
                self.mensaje_ejecutado('');                
                self.listado_ejecucion(agregarOpcionesObservable(datos));

                self.titulo('Registrar Liquidacion UUCC');
        		$('#modal_registro_liquidacion').modal('show');



            } else {
                $('#modal_registro_liquidacion').modal('show');
                self.titulo('Registrar Liquidacion UUCC');
                self.listado_ejecucion([]);
                self.mensaje_ejecutado(mensajeNoFound);
            }                        
            cerrarLoading();
        }, path, parameter,undefined, false);
    }

    self.cargar = function (pagina) {   

        path = path_principal+'/api/liquidacionuucc/?format=json';
        parameter = {
            page: pagina,
            presupuesto_id: self.presupuesto_id(),      
            pagina: pagina          
        };
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje('');
                //self.listado(results); 
                self.listado(agregarOpcionesObservable(datos.data));
                $('#modal_registro_liquidacion').modal('hide');
                $('#modal_detalle_cambio').modal('hide');
                self.liquidacionVO.id(0);
            } else {
                self.listado([]);
                self.mensaje(mensajeNoFound);
            }
            self.llenar_paginacion(datos,pagina);            
            cerrarLoading();
        }, path, parameter,undefined, false);
        
    }

    self.exportar_excel = function (liquidacion_id) {        
        
        location.href=path_principal+"/avanceObraLite/exportReporteLiquidacion?liquidacion_id="+liquidacion_id
   
    }
    self.anular_abrir_modal=function(liquidacion_id){
        self.liquidacionAnular.id(liquidacion_id);

        $.confirm({
            title:'Confirmar!',
            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Esta seguro que desea anular la liquidación con el codigo No. '+liquidacion_id+' ?<h4>',
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {
                self.titulo('Anular liquidación');
                $('#anular').modal('show');             
                $('#confirm').hide();
            }
        });
    }

    self.anular_liquidacion=function(){
        //alert(self.liquidacionAnular.id());
        //alert(self.liquidacionAnular.motivo_anular());
         if (LiquidacionuuccViewModel.errores_liquidacion().length == 0) {
                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#anular').modal('hide');
                            self.cargar(1);                    
                            mensajeExitoso(mensaje);                            
                        }else{
                            $('#anular').modal('hide');
                            mensajeError(mensaje);                            
                        }
                        self.liquidacionAnular.id(0);
                        self.liquidacionAnular.motivo_anular('');

                     },//funcion para recibir la respuesta 
                     alerta:false,
                     url:path_principal+'/avanceObraLite/anularReporteLiquidacion/',//url api
                     parametros:{
                        liquidacion_id:self.liquidacionAnular.id(),
                        motivo_anular:self.liquidacionAnular.motivo_anular(),
                    }                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
        } else {
             LiquidacionuuccViewModel.errores_liquidacion.showAllMessages();//mostramos las validacion
        }

    }

    self.cerrar_liquidacion = function(){
        var parametros={
             callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                    $('#modal_detalle_cambio').modal('hide');
                    self.cargar(1);
                    mensajeExitoso(mensaje);                            
                }else{
                    $('#modal_detalle_cambio').modal('hide');
                    mensajeError(mensaje);                            
                }  

             },//funcion para recibir la respuesta 
             alerta:false,
             url:path_principal+'/avanceObraLite/cerrar_liquidacionuucc/',//url api
             parametros:{
                liquidacion_id:self.liquidacionVO.id()
            }                       
        };
        //parameter =ko.toJSON(self.contratistaVO);
        Request(parametros);
            
    }
    
}
var liquidacion = new LiquidacionuuccViewModel();
liquidacion.cargar(1);
LiquidacionuuccViewModel.errores_liquidacion = ko.validation.group(liquidacion.liquidacionAnular);
// ko.applyBindings(liquidacion);
ko.applyBindings(liquidacion);