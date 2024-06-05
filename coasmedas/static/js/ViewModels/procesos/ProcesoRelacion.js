function ProcesoRelacionViewModel(){
	var self=this;
	self.listadoDisponibles=ko.observableArray([]);
	self.url=path_principal+'/api/procesoRelacion/';
	self.urlContrato = path_principal+'/api/Contrato/';
	self.filtro=ko.observable('');
	self.filtroImplementados=ko.observable('');
	self.mContrato=ko.observable('');
	self.mContratoDisponibles=ko.observable('');
	self.listadoMContrato=ko.observable([]);
	self.mensaje=ko.observable('');
	self.mensajeDisponibles = ko.observable('');
	self.buscado_rapido=ko.observable(false);
	self.listadoImplementados=ko.observableArray([]);
	self.mensajeImplementados=ko.observable('');

    //funcion consultar de tipo get recibe un parametro
    self.consultarDisponibles = function (pagina,id,apuntador) {

        if (pagina > 0) {
        	//alert('entre aqui' + pagina); 
            self.buscado_rapido(true);
            self.filtro($('#txtBuscarDisponibles').val());
            self.mContrato($('#cmbMacroContratoDisponibles').val());
            path = self.url + '?format=json&page=' + pagina;
            parameter = {
                dato: self.filtro(),
                mcontrato: self.mContrato(),
                noImplementado:1,
                proceso:id,
                apuntador:apuntador
            };
            RequestGet(function(datos, estado, mensage) {
            	//alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensajeDisponibles('');
                    self.listadoDisponibles(datos.data);
                } else {
                    self.listadoDisponibles([]);
                    self.mensajeDisponibles(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                self.llenar_paginacion(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }

    }
    //llenar select de macrocontratos
    self.llenarSelectMacrocontratos = function(){

    	path = self.urlContrato + '?format=json';
    	parameter={
    		sin_paginacion:1,
    		id_tipo:12,
            liteD:1
    	};
        RequestGet(function(datos, estado, mensage) {
	        //alert(datos);
	        if (estado == 'ok' && datos != null && datos.length > 0) {
	        	//self.mensaje('');
	            self.listadoMContrato(datos);
	        } else {
	            self.listadoMContrato([]);
	            //self.mensaje(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
	        }
        
        }, path, parameter);    	
        //alert(self.listadoMContrato);
    }

    self.consultarImplementados = function (pagina,id, apuntador) {
        if (pagina > 0) { 
            //self.buscado_rapido(true);
            self.filtroImplementados($('#txtBuscarImplementados').val());
            self.mContratoDisponibles($('#cmbMacroContratoImplementados').val());
            path = self.url + '?format=json&page=' + pagina;
            parameter = {
                proceso: id,
                apuntador: apuntador,
                dato: self.filtroImplementados(),
                mcontrato:self.mContratoDisponibles()
            };
            RequestGet(function(datos, estado, mensage) {
            	//alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensajeImplementados('');
                    self.listadoImplementados(datos.data);
                } else {
                    self.listadoImplementados([]);
                    self.mensajeImplementados(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                self.llenar_paginacionImplementados(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }

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

   self.paginacionImplementados = {
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
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
		self.paginacion.pagina_actual(pagina);
		self.paginacion.total(data.count);
		self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }
    //Funcion para crear la paginacion
    self.llenar_paginacionImplementados = function (data,pagina) {
		self.paginacionImplementados.pagina_actual(pagina);
		self.paginacionImplementados.total(data.count);
		self.paginacionImplementados.cantidad_por_paginas(resultadosPorPagina);
	}


    self.paginacion.pagina_actual.subscribe(function (pagina) {
        if (self.buscado_rapido()) {
            self.consultarDisponibles(pagina,$('#txtIdProceso').val(),$('#txtIdApuntador').val());
          }
          // else{
          //   self.consultar_por_filtros(pagina);
          // }       
    });
    self.paginacionImplementados.pagina_actual.subscribe(function (pagina) {
        //if (self.buscado_rapido()) {
            self.consultarImplementados(pagina,$('#txtIdProceso').val(),$('#txtIdApuntador').val());
         // }
          // else{
          //   self.consultar_por_filtros(pagina);
          // }       
    });

    self.abrir_modal = function() {}
	self.eliminar = function() {}
	self.exportar_excel = function() {}	

	self.cambioMContrato = function(){
		self.consultarDisponibles(1,$('#txtIdProceso').val(),$('#txtIdApuntador').val());
	}
	self.cambioMContratoImplementado = function(){
		self.consultarImplementados(1,$('#txtIdProceso').val(),$('#txtIdApuntador').val());
	}
	
    self.consulta_enter = function(d, e) {
        if (e.which == 13) {
            self.consultarDisponibles(1,$('#txtIdProceso').val(),$('#txtIdApuntador').val());
        }
        return true;
    }
    self.consulta_enterImplementados = function(d, e) {
        if (e.which == 13) {
            self.consultarImplementados(1,$('#txtIdProceso').val(),$('#txtIdApuntador').val());
        }
        return true;
    }
    self.implementar = function(proceso){
    	var selected=[];
    	$('#divDisponibles input:checked').each(function(){
    		selected.push($(this).attr('id'));
    	});
    	//alert(selected);
    	if (selected.length>0){
    		self.mensajeImplementados('');
    		var path =path_principal+'/proceso/implementacion/implementar/';
    		var parameter = { lista: selected, 'proceso': proceso };
    		var parametros = {
    			callback:function(datos, estado, mensaje){
    				if (estado =='ok'){
    					self.consultarDisponibles(self.paginacion.pagina_actual(),$('#txtIdProceso').val(),$('#txtIdApuntador').val());
    					self.consultarImplementados(self.paginacion.pagina_actual(),$('#txtIdProceso').val(),$('#txtIdApuntador').val());
    				}
    			},
    			url:path,
    			parametros:parameter
    		};
    		Request(parametros);
    	}else{
    		self.mensajeDisponibles('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>Debe seleccionar los elementos a implementar</div>');
    	}
    }
    self.quitarImplementacion = function(){
    	var selected=[];
    	$('#divImplementados input:checked').each(function(){
    		selected.push($(this).attr('id'));
    	});
    	if (selected.length>0){
    		self.mensajeImplementados('');
    		var path = path_principal + '/proceso/implementacion/quitarImplementacion/';
            var parameter = { lista: selected, proceso: $('#txtIdProceso').val() };
             RequestAnularOEliminar("Esta seguro que desea dejar de implementar los elementos seleccionados?", path, parameter, function () {
				//self.consultarDisponibles(self.paginacion.pagina_actual(),$('#txtIdProceso').val(),$('#txtIdApuntador').val());
				self.consultarImplementados(self.paginacion.pagina_actual(),$('#txtIdProceso').val(),$('#txtIdApuntador').val());
             });
    	}

    }
}

var procesoRelacion = new ProcesoRelacionViewModel();
//contrato.consultarDisponibles(1);
procesoRelacion.llenarSelectMacrocontratos();
ko.applyBindings(procesoRelacion);
