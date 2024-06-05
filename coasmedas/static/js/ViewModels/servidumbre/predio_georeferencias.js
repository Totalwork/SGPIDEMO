function GeoreferenciasViewModel() {

	var self = this;
	var map;
  	var lat;
	self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.titulo2=ko.observable('');
    self.filtro=ko.observable('');

    self.url=path_principal+'/api/';
    self.url_funcion=path_principal+'/servidumbre/'; 

    self.archivo_carga=ko.observable('');

    self.nombre_apoyo=ko.observable('');
    self.cambio_crea=ko.observable(false);

    self.editar_mapa = ko.observable(false);

    self.georeferenciaVO = {
        id: ko.observable(0),
        longitud: ko.observable(0),
        latitud: ko.observable(0),
        orden: ko.observable(0),
        predio_id: ko.observable($('#id_predio').val()),
    }

  

    self.predioVO ={
    	id: ko.observable(0),
    	expediente_id:ko.observable(0),
    	nombre_predio: ko.observable(''),
    	propietario:ko.observable(''),
    	tipo_predio:ko.observable(''),
    	grupo_documento:ko.observable(''),
    	porcentaje_documentos:ko.observable(''),
    }


    self.descargar_plantilla=function(){
        
       location.href=path_principal+"/servidumbre/descargar-plantilla-georeferencias/";
    }

    

    self.abrir_registro = function () {
   
        self.titulo('Lista de Georeferencias');
      
        $('#modal_acciones').modal('show');
    }

    self.abrir_carga_masiva = function () {
      
        self.titulo('Carga masiva de Georeferencias');
        $('#modal_acciones_carga_masiva').modal('show');
    }

    self.cambiar_orden = function(){
    	self.titulo('Cambiar el orden de las Georeferencias');
    	
    	$('#modal_change').modal('show');
    	
    }

    self.guardar_cambios = function(){
   		var lista=[];
   		var validacion_listado = true
	      ko.utils.arrayForEach(self.listado(), function(d) {
	            if(d.orden>0 && d.orden!=''){

	                lista.push({
	                   id:d.id,
	                   orden:d.orden
	                })

	            }else{	   
	            validacion_listado = false         	
	            	
	            }
	      });
	  	if(validacion_listado){
		  	var parametros={                     
	             callback:function(datos, estado, mensaje){

	                if (estado=='ok') {
	                    $('#modal_change').modal('hide');
	                    if (self.editar_mapa()){
	                    	self.consultar(true);
	                    }else{
	                    	self.consultar();
	                    }
	                    
	                    $('#modal_acciones').modal('show');
	                }                        
	                
	             },//funcion para recibir la respuesta 
	             url:path_principal+'/servidumbre/guardar-cambio-cantidades/',//url api
	             parametros:{
	             	lista:lista,
	             	predio_id:$('#id_predio').val()
	             }                     
	        };
	        //parameter =ko.toJSON(self.contratistaVO);
	        Request(parametros);
	    }else{
	    	$.confirm({
		        title:'Informativo',
		        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Algunas de las coordenadas no cuentan con un numero de orden<h4>',
		        cancelButton: 'Cerrar',
		        confirmButton: false
		    });
	    }
      
                
    }

    self.consultar_predio = function (expediente) {

        	//alert('entre aqui' + pagina);             
            path = path_principal+'/api/servidumbrepredio/'+self.georeferenciaVO.predio_id()+'/?format=json';
            
            parameter = undefined;
            RequestGet(function(datos, estado, mensage) {
            	//alert(datos.data);
                if (datos != null) {
                	//alert('entro');
                    self.predioVO.id(datos.id);
                    self.predioVO.propietario(datos.persona_aux);
                    self.predioVO.nombre_predio(datos.nombre_direccion);
                    self.predioVO.tipo_predio(datos.tipo.nombre);
                    self.predioVO.grupo_documento(datos.grupo_documento.nombre);
                    self.predioVO.porcentaje_documentos(datos.porcentajedocumentos);
                    self.predioVO.expediente_id(datos.expediente_aux);
                } else {
                    // self.listado([]);
                    // self.mensaje(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                
              
                cerrarLoading();
            }, path, parameter,undefined,false);
 	
	}
    self.guardar_nodo_por_nodo = function(){
    	if (GeoreferenciasViewModel.errores_coordenadas().length == 0 && GeoreferenciasViewModel.errores_coordenadas().length == 0 ) {
    		if(self.georeferenciaVO.id()==0){
    			//alert('longitud: '+self.georeferenciaVO.longitud());
    			//alert('latitud: '+self.georeferenciaVO.latitud());
    			//alert('orden: '+self.georeferenciaVO.orden());
    			var parametros={
					callback:function(datos, estado, mensaje){
						if (estado=='ok') {	
							if (self.editar_mapa()){
		                    	self.consultar(true);
		                    }else{
		                    	self.consultar();
		                    }
							mensajeExitoso(mensaje);
						}else{
							mensajeError(mensaje);
						}
					}, //funcion para recibir la respuesta 
					url:path_principal+'/api/servidumbregeoreferencia/',//url api
					parametros:self.georeferenciaVO,
					alerta:false                       
				};
				RequestFormData(parametros);
    		}else{
    			var parametros={
    				metodo:'PUT',
					callback:function(datos, estado, mensaje){
						if (estado=='ok') {	
							if (self.editar_mapa()){
	                    	self.consultar(true);
		                    }else{
		                    	self.consultar();
		                    }
							mensajeExitoso(mensaje);
						}else{
							mensajeError(mensaje);
						}
					}, //funcion para recibir la respuesta 
					url:path_principal+'/api/servidumbregeoreferencia/'+self.georeferenciaVO.id()+'/',//url api
					parametros:self.georeferenciaVO,
					alerta:false                       
				};
				RequestFormData(parametros);
    		}
    	}else {
			if (GeoreferenciasViewModel.errores_coordenadas().length > 0 ) {
				GeoreferenciasViewModel.errores_coordenadas.showAllMessages();
			}			
		}
    }

    self.guardar_carga_masiva = function(){
    	if(self.archivo_carga()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar las Georeferencias.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
        	var data= new FormData();
            data.append('predio_id',$('#id_predio').val());
            data.append('archivo',self.archivo_carga());

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        //if (estado=='ok') {
                        if (self.editar_mapa()){
	                    	self.consultar(true);
	                    }else{
	                    	self.consultar();
	                    }
                        //}
                        $('#modal_acciones_carga_masiva').modal('hide');
                        $('#archivo').fileinput('reset');
                        $('#archivo').val('');
                        self.archivo_carga('');
                        $('#modal_acciones').modal('show');
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/servidumbre/guardar-coordenadas-archivo/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }
    }

    self.limpiar = function(){
    	self.georeferenciaVO.id(0);
    	self.georeferenciaVO.longitud(0);
    	self.georeferenciaVO.latitud(0);
    	self.georeferenciaVO.orden(0);
    	self.georeferenciaVO.predio_id($('#id_predio').val());

    	self.georeferenciaVO.id.isModified(false);
    	self.georeferenciaVO.longitud.isModified(false);
    	self.georeferenciaVO.latitud.isModified(false);
    	self.georeferenciaVO.orden.isModified(false);
    	self.georeferenciaVO.predio_id.isModified(false);



    }

    

    self.eliminar_coordenada = function(id) {
        var path =path_principal+'/api/servidumbregeoreferencia/'+id+'/';
        var parameter = {metodo:'DELETE'};
        RequestAnularOEliminar("Esta seguro que desea eliminar la referencia?", path, parameter, 
            function(datos, estado, mensaje){
	            if (estado=='ok') {	
					if (self.editar_mapa()){
						//alert('true');
                    	self.consultar(true);
                    }else{
                    	self.consultar();
                    }
					//mensajeExitoso(mensaje);
				}
        
        });

    }

    self.abrir_edicion = function(obj){
    	nuevaRegistro();

    	path = path_principal+'/api/servidumbregeoreferencia/?format=json';
        parameter = {
        	ID:obj.id,
        	ignorePagination:true
        };
        RequestGet(function (datos, estado, mensage) {
	        if (estado=='ok' && datos!=null && datos.length > 0) {
	        	self.georeferenciaVO.id(datos[0].id);
	        	self.georeferenciaVO.orden(datos[0].orden);
	        	self.georeferenciaVO.latitud(datos[0].latitud);
	        	self.georeferenciaVO.longitud(datos[0].longitud);
                self.titulo2('Edición')
	        }else{
	        	mensajeError(mensaje);
	        }
	        cerrarLoading();
        }, path, parameter, undefined, false, false);

    }

    self.consultar = function (editar_mapa){
    	path = path_principal+'/api/servidumbregeoreferencia/?format=json';
        parameter = {
        	predio_id:$('#id_predio').val(),
        	ignorePagination:true,

        };
        RequestGet(function (datos, estado, mensage) {

	        if (estado=='ok' && datos!=null && datos.length > 0) {
        	 	//alert('3');        	 	
	        	self.mensaje('');
                self.listado(datos);          
                ocultarNuevoRegistro();
                self.limpiar();
	        }else{
	        	//alert('4');	        	 
	          	self.mensaje(mensajeNoFound);
	          	self.listado([]);
	        }
	        
	        if(editar_mapa){
	        	self.initMap();
	        	$('#content_map').show();
	        }else{
	        	if(self.listado()!=null && self.listado().length!=0){
	        		self.initMap_noeditable();
	  				$('#content_map').show()
	  			}else{
	  				$('#content_map').hide()
  				}
	        }
	        
	        
	        cerrarLoading();
        }, path, parameter, undefined, false, false);
    }


    self.actualizar_nodo=function(datos){

          	self.georeferenciaVO.id(datos.id);
	    	self.georeferenciaVO.orden(datos.orden);
	    	self.georeferenciaVO.latitud(datos.latitud);
	    	self.georeferenciaVO.longitud(datos.longitud);

          var parametros={     
                metodo:'PUT',                
               callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                  if (self.editar_mapa()){
                    	self.consultar(true);
                    }else{
                    	self.consultar();
                    }
                }  

               },//funcion para recibir la respuesta 
               url:path_principal+'/api/servidumbregeoreferencia/'+self.georeferenciaVO.id()+'/',
               parametros:self.georeferenciaVO,
               alerta:false                    
          };

          RequestFormData(parametros);
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

	
    self.initMap = function(){
    	
	  // defino el mapa con estilo nocturno
	    center = {lat: 10.9494272, lng: -74.801152}
	    zoom = 6
	    //alert(sessionStorage.getItem("ubicacionActual"));
	    if ((sessionStorage.getItem("ubicacionActual") != null) && (sessionStorage.getItem("ubicacionActual") != 'null')) {
	      array = sessionStorage.getItem("ubicacionActual").split(",");
	      center = {lat: parseFloat(array[0]), lng: parseFloat(array[1])}
	      zoom = parseInt(array[2]);
	    }

	    var qurl = ""; 
	    qurl = "http://maps.google.com/mapfiles/kml/pal5/icon31l.png";

	    var count = 1;
		var flightPlanCoordinates = [];
		ko.utils.arrayForEach(self.listado(), function(d) {
	               
	        if(count==1){
	        	center = {lat: parseFloat(d.latitud), lng: parseFloat(d.longitud)}
	        	zoom = 17
	        }
	        
	        count=count+1
	          
	          flightPlanCoordinates.push(
	        {
	        	lat:parseFloat(d.latitud), 
	        	lng: parseFloat(d.longitud)
	        }
	        );        

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

	  	if(self.predioVO.porcentaje_documentos()==100){
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

		ko.utils.arrayForEach(self.listado(), function(d) {
		  //alert(d.latitud);
	        var marker = new google.maps.Marker({
	          position: {
	                      lat: parseFloat(d.latitud),
	                      lng:  parseFloat(d.longitud)
	          },
	          map: map,
	          title: d.nombre,
	          draggable:true,
	          icon: {
	            url: qurl,
	            scaledSize : new google.maps.Size(15,15)
	          }
	        });

	        marker.addListener('dragend', function(event) {
	            d.latitud=event.latLng.lat();
	            d.longitud=event.latLng.lng();
	            self.actualizar_nodo(d);
	            var c = map.getCenter();
	            sessionStorage.setItem("ubicacionActual", c.lat() + ',' 
	                                  + c.lng() + ',' + map.getZoom()); 
	    });


	    marker.addListener('click', function(e) {
	            self.nombre_apoyo('['+d.longitud+','+d.latitud+']');
	            var contentStringOrg = '<div id="bodyContent" >'+
	            '<div id="siteNotice">'+            
	            '<h4 id="firstHeading">'+'Vertice: '+d.orden+'</h4></div>'+       
	            '<p><button onclick="eliminarpunto('+d.id+')">Eliminar Punto...</button></p></div>';
	                      
	            var infowindow = new google.maps.InfoWindow({
	              content: contentStringOrg
	            });
	          infowindow.open(map, marker);
	        });

	    });
    	


	    var infowindow_polyon = new google.maps.InfoWindow();
		
		google.maps.event.addListener(flightPath, 'click', function(event) {
			var id_expediente = self.predioVO.expediente_id();
			var id_predio = self.predioVO.id();
			var nombre_predio = self.predioVO.nombre_predio();
			var nombre_propietario =self.predioVO.propietario();
			var tipo_predio = self.predioVO.tipo_predio();
			var grupo_documento = self.predioVO.grupo_documento();
			var porcentaje_documentos = self.predioVO.porcentaje_documentos();


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
	        '<p>'+
	        '<button class="btn btn-primary" onclick="llamarEdicion('+id_expediente+','+id_predio+')">Editar predio</button>'+
	        ';&nbsp;'+
	        '<button class="btn btn-primary" onclick="llamarDocumentos('+id_expediente+','+id_predio+')">Documentos</button>'+ 
	        '</p>'+  


	        '</div></div>';


		    infowindow_polyon.setContent(contentStringOrg);
		    infowindow_polyon.setPosition(event.latLng);
		    infowindow_polyon.open(map);
		});




		flightPath.setMap(map);

	    map.addListener('click', function(e) {
		      
	      lat=e.latLng;
	      map=map;
	      self.abrir_modal_registro(lat);

		     
		  });

		google.maps.event.addListener(map, 'zoom_changed', function() {
	    var c = map.getCenter();
	    sessionStorage.setItem("ubicacionActual", c.lat() + ',' 
	                                  + c.lng() + ',' + map.getZoom()); 
	    });



	}


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
	    var qurl = "";
	    qurl = "http://maps.google.com/mapfiles/kml/pal5/icon31l.png";

	    var count = 1;
		ko.utils.arrayForEach(self.listado(), function(d) {
	                
	        if(count==1){
	        	center = {lat: parseFloat(d.latitud), lng: parseFloat(d.longitud)}
	        	zoom = 17
	        }
	        count=count+1
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

		var flightPlanCoordinates = [];
		ko.utils.arrayForEach(self.listado(), function(d) {

	          flightPlanCoordinates.push(
	        {
	        	lat:parseFloat(d.latitud), 
	        	lng: parseFloat(d.longitud)
	        }
	        );     

	        
		});

		if(self.predioVO.porcentaje_documentos()==100){
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
			var id_expediente = self.predioVO.expediente_id();
			var id_predio = self.predioVO.id();
			var nombre_predio = self.predioVO.nombre_predio();
			var nombre_propietario =self.predioVO.propietario();
			var tipo_predio = self.predioVO.tipo_predio();
			var grupo_documento = self.predioVO.grupo_documento();
			var porcentaje_documentos = self.predioVO.porcentaje_documentos();


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
	        '<p>'+
	        '<button class="btn btn-primary" onclick="llamarDocumentos('+id_expediente+','+id_predio+')">Documentos</button>'+ 
	        '</p>'+ 
	        '</div></div>';


		    infowindow_polyon.setContent(contentStringOrg);
		    infowindow_polyon.setPosition(event.latLng);
		    infowindow_polyon.open(map);
		});


		flightPath.setMap(map);

		google.maps.event.addListener(map, 'zoom_changed', function() {
	    var c = map.getCenter();
	    sessionStorage.setItem("ubicacionActual", c.lat() + ','+ c.lng() + ',' + map.getZoom()); 
	    });



	}

	self.abrir_modal_registro = function(latLng){

	
		$.confirm({
            title:'Informativo',
            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Quiere fijar la proxima coordenada?<h4>',
            cancelButton: 'No',
            confirmButton: 'Si',
            confirm: function() {
            	self.georeferenciaVO.id(0);
                self.georeferenciaVO.predio_id($('#id_predio').val());
                self.georeferenciaVO.orden(0);
                self.georeferenciaVO.latitud(latLng.lat());
                self.georeferenciaVO.longitud(latLng.lng());
           
                var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){
						if (estado=='ok') {	
							if (self.editar_mapa()){
		                    	self.consultar(true);
		                    }else{
		                    	self.consultar();
		                    }
							mensajeExitoso(mensaje);
						}else{
							mensajeError(mensaje);
						}
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/servidumbregeoreferencia/',//url api
					 parametros:self.georeferenciaVO,
					 alerta:false    
                     //parametros: self.cronogramaVO
                  };
                RequestFormData(parametros);
                    
            }
        });
	    
	}

	self.redirigir_a_documentos=function(expediente_id,predio_id){
		location.href=path_principal+'/servidumbre/documentos/'+expediente_id+'/'+predio_id
	}

	self.redirigir_a_editar_predio=function(expediente_id,predio_id){
		location.href=path_principal+'/servidumbre/editarpredio/'+expediente_id+'/'+predio_id
	}

}

var georeferencias= new GeoreferenciasViewModel();
georeferencias.consultar_predio();
georeferencias.consultar(false);
georeferencias.editar_mapa(false);
GeoreferenciasViewModel.errores_coordenadas = ko.validation.group(georeferencias.georeferenciaVO);
ko.applyBindings(georeferencias);


function eliminarpunto(id){
    //Mostrar el popup con las propiedades
    //alert('algo');
    georeferencias.eliminar_coordenada(id);
}

function nuevaRegistro() {
	georeferencias.limpiar();
	$("#nuevoRegistro").show();
	$("#divNuevoRegistro").hide();
	$("#divOcultarRegistro").show();
	georeferencias.titulo2('Registro')
}

function ocultarNuevoRegistro() {
	georeferencias.limpiar();
	$("#nuevoRegistro").hide();
	$("#divNuevoRegistro").show();
	$("#divOcultarRegistro").hide();
}

function llamarDocumentos(expediente_id,predio_id){
    //Mostrar el popup con las propiedades
    georeferencias.redirigir_a_documentos(expediente_id,predio_id);
}

function llamarEdicion(expediente_id,predio_id){
    //Mostrar el popup con las propiedades
    georeferencias.redirigir_a_editar_predio(expediente_id,predio_id);
}