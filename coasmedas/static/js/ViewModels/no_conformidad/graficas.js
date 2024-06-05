function GraficasNoconformidadViewModel() {
	var self = this;
	self.listado=ko.observableArray([]);
	self.porcentajes_tipos=ko.observableArray([]);
	self.porcentajes_valoracion=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.url=path_principal;

	

	self.consultar_graficas = function(){

        path = self.url+'../../no_conformidad/obtenerdatosgraficas/?format=json';
        parameter =  {};
        RequestGet(function (datos, estado, mensaje) {
            if (estado == 'ok' && datos != null && datos.length > 0) {

            	var columnsNoconformidades = [];
            	var columnsPredios = [];
            	self.mensaje('');

            	self.listado(agregarOpcionesObservable(datos));
            	for (var i=0; i < self.listado().length; i++){
            		if (self.listado()[i].grafica == 'Graficas no conformidades'){
			    		columnsNoconformidades = self.listado()[i].datagrafica;
			    	}			    	

            	}

            	self.porcentajes_tipos(agregarOpcionesObservable(datos[1].datagrafica));
            	self.porcentajes_valoracion(agregarOpcionesObservable(datos[2].datagrafica));


            	if (columnsNoconformidades){
		        	var chart14 = c3.generate({
				        bindto: '#pie-chartNoConformidades',
				        color: {
				          pattern: [bgSuccess,bgDanger,bgWarning,bgAlert,],
				        },
				        data: {
				            // iris data from R
				            columns: columnsNoconformidades,
				            type : 'pie',
				            onclick: function (d, i) { console.log("onclick", d, i); },
				            onmouseover: function (d, i) { console.log("onmouseover", d, i); },
				            onmouseout: function (d, i) { console.log("onmouseout", d, i); }
				        }
				    });
				}else{
					$('#pchart11').hide()
				}

				demoCircleGraphs();
        	}else{
        		self.listado([]);
                self.mensaje(mensajeNoFound);
                $('#pchart11').hide()
                $('#pchart12').hide()
                $('#pchart13').hide()
        	}

    	}, path, parameter);
   
	}
}

var grafica= new GraficasNoconformidadViewModel();
grafica.consultar_graficas();
ko.applyBindings(grafica);

function demoCircleGraphs() {
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
        "//alert": [bgAlert, bgAlertLr, bgAlertDr]
    };
    var infoCircle = $('.info-circle');
    if (infoCircle.length) {
        // Color Library we used to grab a random color
        
        // Store all circles
        var circles = [];
        infoCircle.each(function(i, e) {
        	//alert($(e).attr('title')+' '+$(e).attr('value'));
            ////alert($(e).attr('title'));
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
                        return '<h2 class="circle-text-value">' + value+'%'+ '</h2><p>' + title + '</p>' 
                    } 
                    else {
                        return '<h2 class="circle-text-value mb5">' + value+'%'+ '</h2>'
                    }
                }
            });
            circles.push(circle);
        });      
    }

    var infoCircle2 = $('.info-circle2');
    if (infoCircle2.length) {
        // Color Library we used to grab a random color    
        // Store all circles
        var circles2 = [];
        infoCircle2.each(function(i, e) {
        	//alert($(e).attr('title')+' '+$(e).attr('value'));
            ////alert($(e).attr('title'));
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
            var circle2 = Circles.create({
                id: $(e).attr('id'),
                value: $(e).attr('value'),
                radius: $(e).width() / 2,
                width: 14,
                colors: color,
                text: function(value) {
                    var title = $(e).attr('title');
                    if (title) {
                        return '<h2 class="circle-text-value">'+ value+'%'+ '</h2><p>' + title + '</p>' 
                    } 
                    else {
                        return '<h2 class="circle-text-value mb5">' + value+'%'+ '</h2>'
                    }
                }
            });
            circles2.push(circle2);
        });      
    }
} 

