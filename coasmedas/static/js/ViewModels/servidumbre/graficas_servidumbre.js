function GraficasServidumbreViewModel() {
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.url=path_principal;

	

	self.consultar_graficas = function(){

        path = self.url+'../../servidumbre/obtenerdatosgraficas/?format=json';
        parameter =  {};
        RequestGet(function (datos, estado, mensaje) {
            if (estado == 'ok' && datos != null && datos.length > 0) {

            	var columnsExpedientes = [];
            	var columnsPredios = [];
            	self.mensaje('');

            	self.listado(agregarOpcionesObservable(datos));
            	for (var i=0; i < self.listado().length; i++){
            		if (self.listado()[i].grafica == 'Graficas expedientes'){
			    		columnsExpedientes = self.listado()[i].datagrafica;
			    	}
			    	if (self.listado()[i].grafica == 'Graficas predios'){
			    		columnsPredios = self.listado()[i].datagrafica;
			    	}
            	}

            	if (columnsExpedientes){
		        	var chart14 = c3.generate({
				        bindto: '#pie-chartExpedientes',
				        color: {
				          pattern: [bgSuccess,bgDanger,bgWarning,bgAlert,],
				        },
				        data: {
				            // iris data from R
				            columns: columnsExpedientes,
				            type : 'pie',
				            onclick: function (d, i) { console.log("onclick", d, i); },
				            onmouseover: function (d, i) { console.log("onmouseover", d, i); },
				            onmouseout: function (d, i) { console.log("onmouseout", d, i); }
				        }
				    });
				}else{
					$('#pchart11').hide()
				}


				if (columnsPredios){
				    var chart13 = c3.generate({
				        bindto: '#pie-chartPredios',
				        color: {
				          pattern: [bgSuccess,bgDanger,bgWarning,bgAlert,],
				        },
				        data: {
				            // iris data from R
				            columns: columnsPredios,
				            type : 'pie',
				            onclick: function (d, i) { console.log("onclick", d, i); },
				            onmouseover: function (d, i) { console.log("onmouseover", d, i); },
				            onmouseout: function (d, i) { console.log("onmouseout", d, i); }
				        }
				    });
				}else{
					$('#pchart12').hide()
				}



        	}else{
        		self.listado([]);
                self.mensaje(mensajeNoFound);
                $('#pchart11').hide()
                $('#pchart12').hide()
        	}

    	}, path, parameter);
   
	}
}

var grafica= new GraficasServidumbreViewModel();
grafica.consultar_graficas();
ko.applyBindings(grafica);

