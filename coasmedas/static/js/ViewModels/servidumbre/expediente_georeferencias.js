function GeoreferenciasViewModel() {

	var self = this;
	self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');

    self.url=path_principal+'/api/';
    self.url_funcion=path_principal+'/servidumbre/'; 

    self.editar_mapa = ko.observable(false);

    self.expedienteVO ={
    	id:ko.observable($('#id_expediente').val()),
    }


    self.consultar = function (editar_mapa){    	
        path = path_principal + '/servidumbre/consultar_predios_coordenadas/?format=json&id=' +self.expedienteVO.id();        
        parameter = {              
            expediente_id:self.expedienteVO.id(),               
        };
        RequestGet(function(datos,estado,mensaje) {      
    		if(estado=='ok'){
    			
    			validacion = false
	        	ko.utils.arrayFirst(datos, function(d) {	        		
		        	if(d.georeferencias!=null && d.georeferencias.length!=0){
		        		validacion=true
		        	}
		  		
	  			});

	  			if(validacion==true){
  					self.mensaje('');
	    			self.listado(datos);
	    			self.initMap_noeditable();
	  			}else{
	  				self.mensaje(mensajeNoFound);
    				self.listado([]);
  				}
    		}else{
    			//mensajeError(mensajeNoFound);
    			self.mensaje(mensajeNoFound);
    			self.listado([]);
    		}

    		if(editar_mapa){
	        	self.initMap_noeditable();
	        	$('#content_map').show();
	        }else{
	        	validacion = false
	        	ko.utils.arrayFirst(self.listado(), function(d) {	        		
		        	if(d.georeferencias!=null && d.georeferencias.length!=0){
		        		validacion=true
		        	}
		  		
	  			});

	  			if(validacion==true){
  					self.initMap_noeditable();
	  				$('#content_map').show()
	  			}else{
	  				$('#content_map').hide()
  				}
	        }

    		cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.editar_mapa.subscribe(function (val) {
  		
  		if(val==true){
  			$('#content_map').show();
  		}else{  			
  			if((self.listado()!=null) && (self.listado().length>0)){  		
  				$('#content_map').show();
  			}else{  			
  				$('#content_map').hide();
  			}
  			//alert(val);
  		}
		
	});

    self.initMap_noeditable = function(){
		
	  // defino el mapa con estilo nocturno
	    center = {lat: 10.9494272, lng: -74.801152}
	    zoom = 6
	    //alert(sessionStorage.getItem("ubicacionActual"));
	    if ((sessionStorage.getItem("ubicacionActual") != null) && (sessionStorage.getItem("ubicacionActual") != 'null')) {
	      array = sessionStorage.getItem("ubicacionActual").split(",");
	      center = {lat: parseFloat(array[0]), lng: parseFloat(array[1])}
	      zoom = parseInt(array[2]);
	    }

	    var count = 1;
	    ko.utils.arrayFirst(self.listado(), function(d) {
	    	var flightPlanCoordinates = [];
	    	ko.utils.arrayFirst(d.georeferencias, function(e) {
	    		if(count==1){
		        	center = {lat: parseFloat(e.latitud), lng: parseFloat(e.longitud)}
		        	zoom = 14
		        
		        }
	    		count=count+1
	    	});
	    	
	    });
	    map = new google.maps.Map(document.getElementById('map'), {
		    center: center,
		    zoom: zoom,
		    styles: [
		      {elementType: 'geometry', stylers: [{color: '#242f3e'}]},
		      {elementType: 'labels.text.stroke', stylers: [{color: '#242f3e'}]},
		      {elementType: 'labels.text.fill', stylers: [{color: '#746855'}]},
		      {
		        featureType: 'administrative.locality',
		        elementType: 'labels.text.fill',
		        stylers: [{color: '#d59563'}]
		      },
		      {
		        featureType: 'poi',
		        elementType: 'labels.text.fill',
		        stylers: [{color: '#d59563'}]
		      },
		      {
		        featureType: 'poi.park',
		        elementType: 'geometry',
		        stylers: [{color: '#263c3f'}]
		      },
		      {
		        featureType: 'poi.park',
		        elementType: 'labels.text.fill',
		        stylers: [{color: '#6b9a76'}]
		      },
		      {
		        featureType: 'road',
		        elementType: 'geometry',
		        stylers: [{color: '#38414e'}]
		      },
		      {
		        featureType: 'road',
		        elementType: 'geometry.stroke',
		        stylers: [{color: '#212a37'}]
		      },
		      {
		        featureType: 'road',
		        elementType: 'labels.text.fill',
		        stylers: [{color: '#9ca5b3'}]
		      },
		      {
		        featureType: 'road.highway',
		        elementType: 'geometry',
		        stylers: [{color: '#746855'}]
		      },
		      {
		        featureType: 'road.highway',
		        elementType: 'geometry.stroke',
		        stylers: [{color: '#1f2835'}]
		      },
		      {
		        featureType: 'road.highway',
		        elementType: 'labels.text.fill',
		        stylers: [{color: '#f3d19c'}]
		      },
		      {
		        featureType: 'transit',
		        elementType: 'geometry',
		        stylers: [{color: '#2f3948'}]
		      },
		      {
		        featureType: 'transit.station',
		        elementType: 'labels.text.fill',
		        stylers: [{color: '#d59563'}]
		      },
		      {
		        featureType: 'water',
		        elementType: 'geometry',
		        stylers: [{color: '#17263c'}]
		      },
		      {
		        featureType: 'water',
		        elementType: 'labels.text.fill',
		        stylers: [{color: '#515c6d'}]
		      },
		      {
		        featureType: 'water',
		        elementType: 'labels.text.stroke',
		        stylers: [{color: '#17263c'}]
		      }
		    ]

		  });

	    google.maps.event.addListener(map, 'zoom_changed', function() {
	    var c = map.getCenter();
	    sessionStorage.setItem("ubicacionActual", c.lat() + ','+ c.lng() + ',' + map.getZoom()); 
	    });
	    
	    ko.utils.arrayForEach(self.listado(), function(d) {
	    	var flightPlanCoordinates = [];
	    	ko.utils.arrayForEach(d.georeferencias, function(e) {
	    		
	    		flightPlanCoordinates.push({
		        	lat:parseFloat(e.latitud), 
		        	lng: parseFloat(e.longitud)
	        	});
	    	});

	    	if(d.porcentajedocumentos==100){
		    	var flightPath = new google.maps.Polygon({
			      paths: flightPlanCoordinates,
			      strokeColor:'#2ECC71 ',
			      strokeOpacity:0.8,
			      strokeWeight:2,
			      fillColor: '#2ECC71 ',
			      editable: false,
			      fillOpacity: 0.35,
			      geodesic: true,
			  });
		    }else {
		    	var flightPath = new google.maps.Polygon({
			      paths: flightPlanCoordinates,
			      strokeColor:'#FF0000',
			      strokeOpacity:0.8,
			      strokeWeight:2,
			      fillColor: '#FF0000',
			      editable: false,
			      fillOpacity: 0.35,
			      geodesic: true,
			  });
		    }

		    var infowindow_polyon = new google.maps.InfoWindow();
		
			google.maps.event.addListener(flightPath, 'click', function(event) {
				var id_expediente = d.expediente;
				var id_predio = d.id;
				var nombre_predio = d.nombre_direccion;
				var nombre_propietario =d.persona;
				var tipo_predio = d.tipo.nombre;
				var grupo_documento = d.grupo_documento.nombre;
				var porcentaje_documentos = d.porcentajedocumentos;


			    var contentStringOrg = '<div id="bodyContent" >'+
		        '<div id="siteNotice">'+            
		        '<h4 id="firstHeading">'+'Dirección / nombre del predio: </h4>'+nombre_predio+
		        '<h4 id="firstHeading">'+'Propietario: </h4>'+nombre_propietario+
		        '<h4 id="firstHeading">'+'Tipo de predio: </h4>'+tipo_predio+
		        '<h4 id="firstHeading">'+'Grupo de documento: </h4>'+grupo_documento+
		        '<h4 id="firstHeading">'+'Porcentaje de documentos: </h4>'+

		        '<div class="progress">'+
		        '<div class="progress-bar progress-bar-success" role="progressbar"'+
		        ' aria-valuenow="'+porcentaje_documentos+'" aria-valuemin="0" aria-valuemax="100"'+
		        ' style="width: '+porcentaje_documentos+'%;">'+porcentaje_documentos+'%</div></div>'+
		        '<p>';
		        if($('#estado').val()==159){
			        contentStringOrg=contentStringOrg+'<button class="btn btn-primary" onclick="llamarEdicion('+id_expediente+','+id_predio+')">Editar predio</button>'+
		        	';&nbsp;';
		        }
		        contentStringOrg=contentStringOrg+'<button class="btn btn-primary" onclick="llamarDocumentos('+id_expediente+','+id_predio+')">Documentos</button>'+ 
		        '</p><p>';
		        contentStringOrg=contentStringOrg+'<button class="btn btn-primary" onclick="llamarGeoreferencias('+id_expediente+','+id_predio+')">Georreferencias del predio</button>'+
		        '</p>'+ 
		        '</div></div>';


			    infowindow_polyon.setContent(contentStringOrg);
			    infowindow_polyon.setPosition(event.latLng);
			    infowindow_polyon.open(map);
			});

			flightPath.setMap(map);
	    	
	    });


	}

	self.redirigir_a_documentos=function(expediente_id,predio_id){
		location.href=path_principal+'/servidumbre/documentos/'+expediente_id+'/'+predio_id
	}

	self.redirigir_a_editar_predio=function(expediente_id,predio_id){
		location.href=path_principal+'/servidumbre/editarpredio/'+expediente_id+'/'+predio_id
	}

	self.redirigir_a_georeferencias=function(expediente_id,predio_id){
		location.href=path_principal+'/servidumbre/predio-georeferencias/'+expediente_id+'/'+predio_id
	}
    
}

var georeferencias= new GeoreferenciasViewModel();
georeferencias.consultar();
georeferencias.editar_mapa(false);
ko.applyBindings(georeferencias);


function llamarDocumentos(expediente_id,predio_id){
    //Mostrar el popup con las propiedades
    georeferencias.redirigir_a_documentos(expediente_id,predio_id);
}

function llamarEdicion(expediente_id,predio_id){
    //Mostrar el popup con las propiedades
    georeferencias.redirigir_a_editar_predio(expediente_id,predio_id);
}

function llamarGeoreferencias(expediente_id,predio_id){
    //Mostrar el popup con las propiedades
    georeferencias.redirigir_a_georeferencias(expediente_id,predio_id);
}