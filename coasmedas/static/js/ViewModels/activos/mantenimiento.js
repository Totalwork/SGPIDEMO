
function ActivoViewModel() {

	var self = this;
	self.listado=ko.observableArray([]);
	self.listadosoportesmantenimientos=ko.observableArray([]);
	self.listadomotivos=ko.observableArray([]);
	self.listadocontratos=ko.observableArray([]);

	self.titulo=ko.observable('');
	self.titulo_activo=ko.observable('');
	self.titulo_asignarcontrato=ko.observable('');

	self.url=path_principal+'/api/';
	self.url_funcion=path_principal+'/activos/'; 

	self.mensaje=ko.observable('');
	self.mensajesoportemantenimiento=ko.observable('');
	self.mensajecontrato=ko.observable('');

	self.filtro=ko.observable('');
	self.filtro_contrato=ko.observable('');

	self.aux_mantenimiento_id=ko.observable(0);
	self.activo=ko.observable($("#activo_id").val());
	self.tipo_activo=ko.observable($("#tipo_id").val());

	self.soporteaux=ko.observable('');

	self.mantenimientoSoporteVO={
		id:ko.observable(0),
		nombre:ko.observable('').extend({ required: { message: ' Digite el nombre del archivo' } }),
		archivo:ko.observable('').extend({ required: { message: ' Ingrese un archivo' } }),
		mantenimiento_id:ko.observable(0),
	};

	self.mantenimientoVO={
		id:ko.observable(0),
		activo_id:ko.observable(0),
		motivo_id:ko.observable(0).extend({ required: { message: ' Seleccione un motivo' } }),
		fecha:ko.observable('').extend({ required: { message: ' Ingrese una fecha' } }),
		hora:ko.observable(''),
		observaciones:ko.observable(''),
		contrato_id:ko.observable(0),
	};

	self.soportes={
		listado_archivo:ko.observableArray([{
            'soporte':ko.observable('').extend({ required: { message: ' Cargo el soporte' } }),
            'nombre':ko.observable('').extend({ required: { message: ' Digite el nombre' } }),
        }]),        
	};



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
    };

    self.limpiar= function(){
		self.mantenimientoVO.id(0);
		self.mantenimientoVO.activo_id(self.activo());
		self.mantenimientoVO.motivo_id(0);
		self.mantenimientoVO.fecha('');
		self.mantenimientoVO.hora('');
		self.mantenimientoVO.observaciones('');
		self.mantenimientoVO.contrato_id(0);

		$("#activo_contrato_numero").val('');

		self.mantenimientoVO.motivo_id.isModified(false);
		self.mantenimientoVO.fecha.isModified(false);
		
	}

    self.limpiarSoporte = function(){
    	self.mantenimientoSoporteVO.id(0);
    	self.mantenimientoSoporteVO.nombre('');
    	self.mantenimientoSoporteVO.mantenimiento_id(0);
    	self.mantenimientoSoporteVO.archivo('');

        self.mantenimientoSoporteVO.nombre.isModified(false);
        self.mantenimientoSoporteVO.archivo.isModified(false);
    	$("#soporte_mantenimiento").fileinput('reset');
        $("#soporte_mantenimiento").val('');
    	
    }

	self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
       // var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
       // self.paginacion.totalRegistrosBuscados(buscados);

    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {    
       self.cargar(pagina);
    });

    self.paginacion_contratos = {
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
    };

    self.llenar_paginacion_contratos = function (data,pagina) {        
        self.paginacion_contratos.pagina_actual(pagina);
        self.paginacion_contratos.total(data.count);       
        self.paginacion_contratos.cantidad_por_paginas(resultadosPorPagina);
       // var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
       // self.paginacion.totalRegistrosBuscados(buscados);

    }


    self.paginacion_contratos.pagina_actual.subscribe(function (pagina) {    
       self.consultar_contratos(pagina);
    });


	self.abrir_nuevo_mantenimiento = function(){
		self.limpiar();
		self.consultar_motivos(1);
		self.titulo_activo('Registrar Mantenimiento para el activo No. '+self.activo());
		$('#nuevo_activo').modal('show');
	}

	self.agregar_soporte=function(){
        self.soportes.listado_archivo.push({
        	'soporte':ko.observable('').extend({ required: { message: ' Cargo el soporte' } }),
            'nombre':ko.observable('').extend({ required: { message: ' Digite el nombre' } })
        });
    }


    self.eliminar_soporte=function(val){
        // alert(val.nombre());
        self.soportes.listado_archivo.remove(val);
    }

    self.utilizarContrato = function(obj){
        $("#activo_contrato_numero").val(obj.numero);
        $('#asginar_contrato').modal('hide');
        $("#validacionContrato").hide();

        self.mantenimientoVO.contrato_id(obj.id)
    }

  
    self.guardar=function(){

    	if ((ActivoViewModel.errores_mantenimientos().length == 0) && (ActivoViewModel.errores_mantenimientos_soportes().length == 0)){  
            $("#validacionContrato").hide();

            
            if (self.mantenimientoVO.id() == 0){       
                self.mantenimientoVO.activo_id(self.activo());


                var data = new FormData();           
            	data.append('activo_id',self.mantenimientoVO.activo_id());
            	data.append('motivo_id',self.mantenimientoVO.motivo_id());
            	data.append('fecha',self.mantenimientoVO.fecha());
            	data.append('hora',self.mantenimientoVO.hora());
            	data.append('observaciones',self.mantenimientoVO.observaciones());
            	data.append('contrato_id',self.mantenimientoVO.contrato_id());

            	ko.utils.arrayForEach(self.soportes.listado_archivo(), function(d) {

                    if(d.soporte()!=''){
                         data.append('soporte[]',d.soporte());
                    }
             	}); 


             	ko.utils.arrayForEach(self.soportes.listado_archivo(), function(d) {

                    if(d.nombre()!=''){
                         data.append('nombre[]',d.nombre());
                    }
             	});

                var parametros={
                        
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        //self.consultar_documentos(self.paginacion_tipos.pagina_actual());
                        $('#nuevo_activo').modal('hide');
                        self.limpiar();
                        self.cargar(1);

                    }else{
                        self.mensaje_activo('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>Se presentaron errores al guardar el archivo.</div>'); //mensaje not found se encuentra el el archivo call-back.js                           
                         
                    }                     
                },//funcion para recibir la respuesta 
                url: self.url+'activosmantenimiento/',//url api
                parametros:data                       
                };
                RequestFormData2(parametros);

            }
            
 
        }else{
        	if(self.mantenimientoVO.contrato_id()==0){
                $("#validacionContrato").show();
            }
            ActivoViewModel.errores_mantenimientos_soportes.showAllMessages();
            ActivoViewModel.errores_mantenimientos.showAllMessages();
        }
    }

    self.guardarDocumento =function(){
    	if (ActivoViewModel.errores_soportes().length == 0){
            
            
            if (self.mantenimientoSoporteVO.id() == 0){                
                self.mantenimientoSoporteVO.mantenimiento_id(self.aux_mantenimiento_id());

  

                var parametros={
                        
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {                        
                      
                        self.consultar_soportes_mantenimientos(self.aux_mantenimiento_id());
                        self.limpiarSoporte();                     
                        
                    }
                    cerrarLoading()
                },//funcion para recibir la respuesta 
                url: self.url+'activossoporte_mantenimiento/',//url api
                parametros:self.mantenimientoSoporteVO                       
                };
                RequestFormData(parametros);
            }
        }
    }

    self.eliminar_soporte_mantenimiento =function(id,id_mantenimiento){
    	var path =self.url+'activossoporte_mantenimiento/'+id+'/';
        var parameter = {};
        RequestAnularOEliminar("Esta seguro que desea eliminar el soporte del mantenimiento?", path, parameter, 
            function(){                 
              self.consultar_soportes_mantenimientos(id_mantenimiento);
              self.limpiarSoporte();
        }); 
    }
  

	self.abrir_modal_contrato =function(){
        $('#asginar_contrato').modal('show');
        self.consultar_contratos(1);
        self.titulo_asignarcontrato('Asignar un contrato');
    }

	self.consultar_motivos = function (pagina){
        path = self.url+'activosmotivo/?format=json';
        if (pagina > 0){
            parameter = {
                tipo_activo:self.tipo_activo(),
            };
            RequestGet(function (datos, estado, mensage) {
                
                if (estado == 'ok' && datos != null && datos.count > 0) {                 
                   
                    self.listadomotivos(agregarOpcionesObservable(datos.data));

                    self.listadomotivos.sort(function (a, b) {
                      if (a.nombre > b.nombre) {
                        return 1;
                      }
                      if (a.nombre < b.nombre) {
                        return -1;
                      }
                      // a must be equal to b
                      return 0;
                    });
                }else{
                  
                    self.listadomotivos([]);         
                    
                }
    
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }

    self.consultar_contratos = function (pagina){
        path = self.url+'Contrato/?format=json';
        if (pagina > 0){
            parameter = {
                dato: self.filtro_contrato(),
                parametro_consulta_activos: true,
                id_tipo_codigo:221,
            };
            RequestGet(function (datos, estado, mensage) {
                
                if (estado == 'ok' && datos != null) {   
                    self.mensajecontrato('');                
                    self.listadocontratos(agregarOpcionesObservable(datos.data));
                    
                }else{
                	self.mensajecontrato(mensajeNoFound);              
                    self.listadocontratos([]);                    
                }
                self.llenar_paginacion_contratos(datos,pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }

    self.buscarContrato=function(d,e){
        if (e.which == 13) {
            self.filtro_contrato($('#txtBuscarContrato').val());
            self.consultar_contratos(1);
        }
        return true;
    }


    self.get_Contrato = function(){
        self.filtro_contrato($('#txtBuscarContrato').val());
        self.consultar_contratos(1);
    }

	self.cargar = function (pagina) {
        path =self.url+'activosmantenimiento/?format=json';
        
        if (pagina > 0){ 
         
            parameter = {
            	activo: self.activo(),
            	page: pagina,
        	};
            RequestGet(function (datos, estado, mensage) {
              

                if (estado == 'ok' && datos != null && datos.count > 0) {
                    
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data));
                    
                }else{
                  
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    
                }
                self.llenar_paginacion(datos,pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }else{
            self.mensaje('no se encontro la aplicación y/o el modulo');
        }   
    }

    self.ver_soporte_mantenimiento = function(obj){
   
      window.open(path_principal+"/activos/ver-soporte-mantenimiento/?id="+ obj.id, "_blank");
    }

    self.exportar_excel=function(){        
        location.href=self.url_funcion+"reporte_mantenimientos/?activo="+self.activo();    
    
        return true;
    }


    self.consultar_soportes_mantenimientos = function(id){
        path =self.url+'activossoporte_mantenimiento/?format=json';
        parameter = {
            mantenimiento: id,
        };

        RequestGet(function (data, estado, mensage) {

            if (estado == 'ok' && data != null && data.count > 0) {
                
                self.mensajesoportemantenimiento('');
                self.listadosoportesmantenimientos(agregarOpcionesObservable(data.data));
                    
            }else{
                  
                self.listadosoportesmantenimientos([]);
                self.mensajesoportemantenimiento(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    
            }

        },path, parameter,function() {            
        });
    }


    self.abrir_modal_soportes_mantenimientos =function (obj){
        self.consultar_soportes_mantenimientos(obj.id);
        self.aux_mantenimiento_id(obj.id);
        $('#MotivoSoporteMantenimiento').text(obj.motivo.nombre);
        $('#ActivoSoporteMantenimiento').text(obj.activo.id);
        $('#modal_soportes_mantenimientos').modal('show');

    }


}
var mantenimiento = new  ActivoViewModel();         
ActivoViewModel.errores_mantenimientos = ko.validation.group(mantenimiento.mantenimientoVO);
ActivoViewModel.errores_mantenimientos_soportes = ko.validation.group(mantenimiento.soportes);
ActivoViewModel.errores_soportes = ko.validation.group(mantenimiento.mantenimientoSoporteVO);
ko.applyBindings(mantenimiento);