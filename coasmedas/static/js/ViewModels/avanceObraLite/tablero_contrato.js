function TableroViewModel(){
	var self = this;
	self.avanceObra=ko.observable(0);
	self.listadoPorHito=ko.observableArray([]);
	self.listadoCurvaAvanceObra = ko.observableArray([]);
	self.listadoCurvaAvanceFinanciero = ko.observableArray([]);
	self.listadoObrasPorEstado = ko.observableArray([]);
	self.url=path_principal;

	self.consultar = function () {
		path = path_principal+'/avanceObraLite/graficatablero/'+ 
		$('#contrato_id').val()+'/';
		parameter = {}
		RequestGet(function (datos, estado, mensage) {
			if (datos != null ){
				self.avanceObra(datos.avanceObra);
				self.listadoPorHito(datos.porHito);
				// self.listadoCurvaAvanceObra(agregarOpcionesObservable(datos.curvaAvanceObra));
				// self.listadoCurvaAvanceFinanciero(agregarOpcionesObservable(datos.curvaAvanceFinanciero));
				// self.listadoObrasPorEstado(datos.obrasPorEstado);
			}
			cerrarLoading();
			demoCircleGraphs();
			demoHighLines();
		}, path, parameter);
	}
}

var tablero = new TableroViewModel();
tablero.consultar();
ko.applyBindings(tablero);

function demoCircleGraphs() {
    var infoCircle = $('.info-circle');
    if (infoCircle.length) {
        // Color Library we used to grab a random color
        var colors = {
            "primary": [bgPrimary, bgPrimaryLr,
                bgPrimaryDr
            ],
            "info": [bgInfo, bgInfoLr, bgInfoDr],
            "warning": [bgWarning, bgWarningLr,
                bgWarningDr
            ],
            "success": [bgSuccess, bgSuccessLr,
                bgSuccessDr
            ],
            "alert": [bgAlert, bgAlertLr, bgAlertDr]
        };
        // Store all circles
        var circles = [];
        infoCircle.each(function(i, e) {
            //alert($(e).attr('title'));
            // Define default color
            var color = ['#DDD', bgPrimary];
            // Modify color if user has defined one
            var targetColor = $(e).data(
                'circle-color');
            if (targetColor) {
                var color = ['#DDD', colors[
                    targetColor][0]]
            }
            // Create all circles
            var circle = Circles.create({
                id: $(e).attr('id'),
                value: $(e).attr('value'),
                radius: $(e).width() / 2,
                width: 14,
                colors: color,
                text: function(value) {
                    var title = $(e).attr('title');
                    if (title) {
                        return '<h2 class="circle-text-value">' + value + '</h2><p>' + title + '</p>' 
                    } 
                    else {
                        return '<h2 class="circle-text-value mb5">' + value + '</h2>'
                    }
                }
            });
            circles.push(circle);
        });

    }
}
var demoHighLines = function() {
    // Define chart color patterns
    // var highColors = [bgWarning, bgPrimary, bgInfo, bgAlert,
    //     bgDanger, bgSuccess, bgSystem, bgDark
    // ];
    var highColors = [bgSuccess];
	var line3 = $('#high-line3');
	var line4 = $('#high-line4');
	var line5 = $('#high-line5');
	var categorias = [];
	var porcentajes = [];

	var categoriasF = [];
	var porcentajesF = [];
	var montos = [];
	if (line3.length) {
		//organizar array de categorias
		//var curvaAvanceObra = tablero.listadoCurvaAvanceObra;
		ko.utils.arrayForEach(tablero.listadoCurvaAvanceObra(), function(obj) {
			categorias.push(obj.fecha);
			porcentajes.push(obj.avance);
		});

        $('#high-line3').highcharts({
            credits: false,
            colors: highColors,
            chart: {
                backgroundColor: '#f9f9f9',
                className: 'br-r',
                type: 'line',
                zoomType: 'x',
                panning: true,
                panKey: 'shift',
                marginTop: 25,
                marginRight: 1,
            },
            title: {
                text: null
            },
            xAxis: {
                gridLineColor: '#EEE',
                lineColor: '#EEE',
                tickColor: '#EEE',
                categories: categorias,
                labels: {
                    rotation: -90,
                    style: {
                        fontSize: '10px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            },
            yAxis: {
            	showEmpty: false,
                min: 0,
                tickInterval: 20,
                offset: 1,
                gridLineColor: '#EEE',
                title: {
                    text: '% de avance de obra',
                },
                //categories: categorias//[0,10,20,30,40,50,60,70,80,90,100]//['0','10','20','30','40','50','60','70','80','90','100']
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">Avance: </td>' +
                             '<td style="padding:0"><b>{point.y:.1f} %</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                spline: {
                    lineWidth: 3,
                },
                area: {
                    fillOpacity: 0.2
                }
            },
            legend: {
                enabled: false,
            },
            series: [{
                name: 'Avance fisico',
                data: porcentajes
            }]
        });


	}
	if (line4.length) {
		//organizar array de categorias
		//var curvaAvanceObra = tablero.listadoCurvaAvanceObra;
		ko.utils.arrayForEach(tablero.listadoCurvaAvanceFinanciero(), function(obj) {
			categoriasF.push(obj.fecha);
			porcentajesF.push(obj.avance);
			//montos.push(obj.monto);
		});

        $('#high-line4').highcharts({
            credits: false,
            colors: highColors,
            chart: {
                backgroundColor: '#f9f9f9',
                className: 'br-r',
                type: 'line',
                zoomType: 'x',
                panning: true,
                panKey: 'shift',
                marginTop: 25,
                marginRight: 1,
            },
            title: {
                text: null
            },
            xAxis: {
                gridLineColor: '#EEE',
                lineColor: '#EEE',
                tickColor: '#EEE',
                categories: categorias,
                labels: {
                    rotation: -90,
                    style: {
                        fontSize: '10px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            },
            yAxis: {
            	showEmpty: false,
                min: 0,
                tickInterval: 20,
                offset: 1,
                gridLineColor: '#EEE',
                title: {
                    text: '% de avance financiero',
                },
                //categories: categorias//[0,10,20,30,40,50,60,70,80,90,100]//['0','10','20','30','40','50','60','70','80','90','100']
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">Avance: </td>' +
                             '<td style="padding:0"><b>{point.y:.1f} %</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                spline: {
                    lineWidth: 3,
                },
                area: {
                    fillOpacity: 0.2
                }
            },
            legend: {
                enabled: false,
            },
            series: [{
                name: 'Avance financiero',
                data: porcentajesF
            }]
        });


	}
	if (line5.length) {
		var max = 0;
		intervalo = 1;
		ko.utils.arrayForEach(tablero.listadoCurvaAvanceFinanciero(), function(obj) {
			montos.push(obj.monto);
			if (max < obj.monto){
				max = obj.monto;
			}
		});
		for (let i=1; i<max.toString().length; i++) {
			intervalo = intervalo * 10;
		}
        $('#high-line5').highcharts({
            credits: false,
            colors: highColors,
            chart: {
                backgroundColor: '#f9f9f9',
                className: 'br-r',
                type: 'line',
                zoomType: 'x',
                panning: true,
                panKey: 'shift',
                marginTop: 25,
                marginRight: 1,
            },
            title: {
                text: null
            },
            xAxis: {
                gridLineColor: '#EEE',
                lineColor: '#EEE',
                tickColor: '#EEE',
                categories: categorias,
                labels: {
                    rotation: -90,
                    style: {
                        fontSize: '10px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            },
            yAxis: {
            	showEmpty: false,
                min: 0,
                tickInterval: intervalo,
                offset: 1,
                gridLineColor: '#EEE',
                title: {
                    text: 'valor ganado',
                },
                labels: {
                	formatter: function () {
                		return '$' + this.axis.defaultLabelFormatter.call(this);
                	}
                }
                //categories: categorias//[0,10,20,30,40,50,60,70,80,90,100]//['0','10','20','30','40','50','60','70','80','90','100']
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">vlr. ganado: </td>' +
                             '<td style="padding:0"><b>{point.y}</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                spline: {
                    lineWidth: 3,
                },
                area: {
                    fillOpacity: 0.2
                }
            },
            legend: {
                enabled: false,
            },
            series: [{
                name: 'Valor ganado',
                data: montos,
			      tooltip: {
			        valuePrefix: '$'
			      }
            }]
        });


	}
}


