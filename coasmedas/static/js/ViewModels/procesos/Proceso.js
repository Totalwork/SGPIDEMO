function ProcesoViewModel(argument) {
	var self=this;
	self.listado=ko.observableArray([]);
	self.url=path_principal+'/api/Procesos/';
	self.filtro=ko.observable('');
	self.mensaje=ko.observable('');
	self.buscado_rapido=ko.observable(false);
    self.empresa=ko.observable('');

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina,empresa) {
        if (pagina > 0) { 
            self.buscado_rapido(true);
            self.filtro($('#txtBuscar').val());
            self.empresa(empresa);
            path = self.url + '?format=json&page=' + pagina;
            parameter = {
                dato: self.filtro(),
                empresa:self.empresa()
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
            self.consultar(pagina,$('#idEmpresa').val());
          }else{
            self.consultar_por_filtros(pagina);
          }       
    });

    self.abrir_modal = function() {}
	self.eliminar = function() {}
	//exportar excel
    
    self.exportar_excel=function(idProceso){

        location.href=path_principal+"proceso/exportarxls?id="+idProceso;
    }


}
var proceso = new ProcesoViewModel();
// proceso.consultar(1,$('#idEmpresa').val())
ko.applyBindings(proceso);