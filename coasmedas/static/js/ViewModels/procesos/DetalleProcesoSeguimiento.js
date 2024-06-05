function DetalleProcesoSeguimientoViewModel(){
	var self=this;
	self.listado=ko.observableArray([]);
	self.url=path_principal+'/api/procesoRelacion/';
	self.filtro=ko.observable('');
	self.mensaje=ko.observable('');
	self.buscado_rapido=ko.observable(false);

	    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina,proceso,apuntador) {
        if (pagina > 0) {
        	//alert('entre aqui' + pagina); 
            self.buscado_rapido(true);
            self.filtro($('#txtBuscar').val());
            path = self.url + '?format=json&pagina=' + pagina;
            parameter = {
                dato: self.filtro(),
                verDetalle:1,
                proceso:proceso,
                apuntador:apuntador
            };
            RequestGet(function(datos, estado, mensage) {
            	//alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado(datos.data);
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                
                self.llenar_paginacion(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }    	
	}
    
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
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
		self.paginacion.pagina_actual(pagina);
		self.paginacion.total(data.count);
		self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }				
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        if (self.buscado_rapido()) {
            //self.consultar(pagina,$('#txtIdProceso').val(),$('#txtIdApuntador').val());
          }
         self.consultar(pagina,$('#txtIdProceso').val(),$('#txtIdApuntador').val()); 
    });
    self.abrir_modal = function() {}
	self.eliminar = function() {}
	self.exportar_excel = function() {}	

    self.consulta_enter = function(d, e) {
        if (e.which == 13) {
            self.consultar(1,$('#txtIdProceso').val(),$('#txtIdApuntador').val());
        }
        return true;
    }
}
var detalleProcesoSeguimiento = new DetalleProcesoSeguimientoViewModel();
ko.applyBindings(detalleProcesoSeguimiento);