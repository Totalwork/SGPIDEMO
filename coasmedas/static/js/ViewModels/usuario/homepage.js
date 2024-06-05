function HomePageViewModel() {
	var self = this;
	self.listado=ko.observableArray([]);
	self.url=path_principal;
	self.mensaje=ko.observable('');
	self.avance_de_obra = ko.observableArray([]);

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
        self.consultar_avanceObraGrafico2(pagina);
    });

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }


    self.examinarCronogramas = function (obj) {
        sessionStorage.setItem("macrocontrato_id_avance",obj.mcontrato.id || 0);
        ruta = self.url+'../../avanceObraGrafico2/cronograma/';
        window.location.href = ruta

    }

    self.verTablero = function (obj) {
        //alert(obj.id)
        ruta = self.url+'../../avanceObraGrafico2/tablero/'+obj.mcontrato.id+'/';
        window.location.href = ruta     
    }

    self.consultar_avanceObraGrafico2 = function(pagina){
        path = path_principal+'/api/Proyecto_empresas_lite/?format=json&page='+pagina;
         parameter = {
            empresa:$('#id_empresa').val(),
            pagina:pagina,
            homepage:true,
         }
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos != null && datos.data.length > 0) {
                self.avance_de_obra(agregarOpcionesObservable(datos.data));                
            }
            self.llenar_paginacion(datos,pagina);
            cerrarLoading();

        }, path, parameter,undefined, false);
    }

	self.consultar = function () {
		path = self.url+'../../usuario/obtenerdatosgraficas/?format=json';
		parameter = {
			filtro: $('#cmbano').val()
		}
		RequestGet(function (datos, estado, mensage) {
			if (estado == 'ok' && datos != null && datos.length > 0) {
				//var columns = [];
				//var columnsViviendas = [];
				var columnsContratos = [];
				var categorias = [];
				var girado = [];
				var legalizado = [];

				self.mensaje('');
				self.listado(agregarOpcionesObservable(datos));
				// var total = 0;
				var Colors = [bgPrimary, bgInfo, bgWarning, bgAlert, bgDanger, bgSystem, bgSuccess,];

			    for (var i=0; i < self.listado().length; i++){
			    	if (self.listado()[i].grafica == 'Contratos por estado'){
			    		columnsContratos = self.listado()[i].datagrafica;
			    	}
			    	if (self.listado()[i].grafica == 'Girado y legalizado por Macrocontrato'){
			    		categorias = self.listado()[i].datagrafica.categorias;
			    		girado = self.listado()[i].datagrafica.girado;
			    		legalizado = self.listado()[i].datagrafica.legalizado;
			    	}
			    	// if (self.listado()[i].grafica == 'Avance de obra promedio'){
			    	// 	if (self.listado()[i].datagrafica != null){
			    	// 		self.avance_de_obra(self.listado()[i].datagrafica);                            
			    	// 	}else{
			    	// 		self.avance_de_obra([]);
			    	// 	}
			    	// }
                    


			    }

                self.consultar_avanceObraGrafico2(1);
                var patronColores = [];
                for (var x = 0; x < columnsContratos.length; x++) {
                    if (columnsContratos[x][0] == 'Por Vencer'){
                        patronColores.push(bgWarning);
                    }
                    if (columnsContratos[x][0] == 'Vigente'){
                        patronColores.push(bgSuccess);
                    }
                    if (columnsContratos[x][0] == 'Liquidado'){
                        patronColores.push(bgInfo);
                    }
                    if (columnsContratos[x][0] == 'Suspendido'){
                        patronColores.push(bgSystem);
                    }
                    if (columnsContratos[x][0] == 'Vencido'){
                        patronColores.push(bgDanger);
                    }



                }

			    var chart14 = c3.generate({
			        bindto: '#pie-chartContratos',
			        color: {
			          pattern: patronColores,
			        },
			        data: {
			            // iris data from R
			            columns: columnsContratos,
			            type : 'pie',
			            onclick: function (d, i) { consultar_estado(d.name); },
			            onmouseover: function (d, i) { console.log("onmouseover", d, i); },
			            onmouseout: function (d, i) { console.log("onmouseout", d, i); }
			        }
			    });	

		        // Bar Chart
		        if (categorias.length > 0) {
                    $('#high-bars').highcharts({
                        colors: [bgWarning, bgSuccess],
                        credits: false,
                        legend: {
                            enabled: false,
                            y: -5,
                            verticalAlign: 'top',
                            useHTML: true
                        },
                        chart: {
                            spacingLeft: 30,
                            type: 'bar',
                            marginBottom: 0,
                            marginTop: 0,
                            // spacingTop: 20,
                            // spacingLeft: 45,
                            // spacingRight: 45,
                            // spacingBottom: 20,	                                                     
                        },
                        title: {
                            text: null
                        },
                        xAxis: {
                            showEmpty: false,
                            tickLength: 80,
                            lineColor: '#EEE',
                            tickColor: '#EEE',
                            offset: 1,
                            //categories: ['PRONE 096 2013', 'PRONE 180 2013'],
                            categories: categorias,
                            title: {
                                text: null
                            },
                            labels: {
                                align: 'right',
                            }
                        },
                        yAxis: {
                            min: 0,
                            gridLineWidth: 0,
                            showEmpty: false,
                            title: {
                                text: null
                            },
                            labels: {
                                enabled: false,
                            }
                        },
                        tooltip: {
                            valueSuffix: ' millones'
                        },
                        plotOptions: {
                            bar: {}
                        },
                        series: [{
                            id: 1,
                            name: 'Girado',
                            //data: [36, 55]
                            data: girado
                        }, {
                            id: 2,
                            name: 'Legalizado',
                            //data: [65, 45]
                            data: legalizado
                        }]
                    });
                }else{
                	$('#high-bars').html('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron registros de giros a los contratistas.</div>');
                }    

			}else{
                self.listado([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js

			}
			//alert(self.listado());
			cerrarLoading();
		}, path, parameter,undefined,false);
	}


}

var homepage = new HomePageViewModel();
ko.applyBindings(homepage);
function consultar_estado(estado_nombre){
    const estados = [
        {
            id: 28,
            name: 'Vigente'
        },
        {
            id: 29,
            name: 'Liquidado'
        },
        {
            id: 30,
            name: 'Suspendido'
        },
        {
            id: 31,
            name: 'Por Vencer'
        },
        {
            id: 32,
            name: 'Vencido'
        }
    ];
    var estado = estados.find(estado => estado.name === estado_nombre);
    if (estado) {
        sessionStorage.setItem('cto_cto_estado', estado.id || '');
        window.location.href = path_principal+"/contrato/contrato/"; 
    }
}