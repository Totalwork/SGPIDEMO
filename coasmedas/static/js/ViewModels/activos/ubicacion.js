function UbicacionViewModel() {

	var self = this;
	var map;
  	var lat;
	self.listado=ko.observableArray([]);
	self.listado_activos=ko.observableArray([]);
	self.listado_tipo=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.titulo2=ko.observable('');
    self.filtro=ko.observable('');

    self.url=path_principal+'/api/';
    self.url_funcion=path_principal+'/activos/'; 

    self.archivo_carga=ko.observable('');

    self.nombre_apoyo=ko.observable('');
    self.cambio_crea=ko.observable(false);

    self.editar_mapa = ko.observable(false);

    self.filtro=ko.observable('');
    
    self.filtrado={
        categoria:ko.observable(''),
        tipo:ko.observable(''),
        estado:ko.observable(''),
        funcionario:ko.observable(''),
    };


    self.puntosGPSVO ={
    	id:ko.observable(0),
    	nombre:ko.observable('').extend({ required: { message: '(*)Digite nombre del punto' } }),
    	activo_id:ko.observable(''),
        longitud:ko.observable(''),
        latitud:ko.observable(''),
    }
   
   self.detalle={
        id:ko.observable(''),
        categoria:ko.observable(''),
        tipo:ko.observable(''),
        identificacion:ko.observable(''),
        serial_placa:ko.observable(''),
        descripcion:ko.observable(''),
        contrato:ko.observable(''),
        contrato_id:ko.observable(''),
        valor_compra:ko.observable(0).money(),
        responsable:ko.observable(''),
        vida_util_dias:ko.observable(''),
        periodicidad_mantenimiento:ko.observable(''),
        fecha_baja:ko.observable(''),
        fecha_alta:ko.observable(''),
        debaja:ko.observable(false),
        debaja_color:ko.observable(''),
        debaja_estado:ko.observable(''),
        motivo_debaja:ko.observable(''),

    };

    // self.consultar = function (editar_mapa){
    // 	path = path_principal+'/api/activospuntosgps/?format=json';
    //     parameter = {
    //     	//activo:,
    //     	ignorePagination:true,

    //     };
    //     RequestGet(function (datos, estado, mensage) {

	   //      if (estado=='ok' && datos!=null && datos.length > 0) {
    //     	 	//alert('3');        	 	
	   //      	    self.mensaje('');
    //             self.listado(datos);
    //             self.initMap();
    //             $('#content_map').show();       
    //             //ocultarNuevoRegistro();
    //             //self.limpiar();
	   //      }else{
	   //      	//alert('4');        	 
	   //        	self.mensaje(mensajeNoFound);
	   //        	self.listado([]);
    //           $('#content_map').hide();
	   //      }

	   //      cerrarLoading();
    //     }, path, parameter, undefined, false, false);
    // }
	
self.initMap = function(){
  // defino el mapa con estilo nocturno
  	var center = {lat: 10.9494272, lng: -74.801152}
	var zoom = 6
  	if ((sessionStorage.getItem("ubicacionActual") != null) && (sessionStorage.getItem("ubicacionActual") != 'null')) {
      array = sessionStorage.getItem("ubicacionActual").split(",");
      center = {lat: parseFloat(array[0]), lng: parseFloat(array[1])}
      zoom = parseInt(array[2]);
    }


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

  
    var markers = []
  
  	ko.utils.arrayForEach(self.listado(), function(d) {
        // alert(d.nombre) 
        var marker = new google.maps.Marker({
          position: {
              lat: parseFloat(d.latitud),
              lng:  parseFloat(d.longitud)
          },         
          map: map,
          //title: d.nombre,
          draggable:false
        });

        marker.addListener('click', function(e) {

           // self.nombre_apoyo(d.nombre);


            var contentStringOrg = '<div id="bodyContent">'+
            '<div id="siteNotice">'+
            '<h4 id="firstHeading">'+'Nombre del punto: </h4>'+d.nombre+
            '<br><hr style="margin-bottom: 5px; margin-top: 5px;">'+        
		    '<h4 id="firstHeading">'+'Numero contrato de adquisición: </h4>'+d.activo.num_contrato+
		    '<h4 id="firstHeading">'+'Tipo: </h4>'+d.activo.tipo.categoria+
            '<h4 id="firstHeading">'+'Categoria: </h4>'+d.activo.tipo.nombre+
		    '<br><br><p>'+
	        '<button class="btn btn-primary" onclick="llamarVerDetalles('+d.activo.id+')">Ver detalles del activo</button>'+
	        '&nbsp;'+
	        '<button class="btn btn-primary" onclick="llamarMantenimientos('+d.activo.id+')">Mantenimientos</button>'+ 
	        '</p>'+ 
            '</div>';
            

            contentStringOrg=contentStringOrg+'</div>';           
            var infowindow = new google.maps.InfoWindow({
              content: contentStringOrg
            });
          infowindow.open(map, marker);


        });

   		
        markers.push(marker);
  	}); 

    var markerCluster = new MarkerClusterer(map, markers, {    		
    		imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'
    	}
    );

  	// map.addListener('click', function(e) {	      
   //    	lat=e.latLng;
   //    	map=map;
   //   	self.abrir_modal_registro();	      
  	// });

  	google.maps.event.addListener(map, 'zoom_changed', function() {
    var c = map.getCenter();
    sessionStorage.setItem("ubicacionActual", c.lat() + ',' 
                                  + c.lng() + ',' + map.getZoom()); 
    });

  	
}

	self.abrir_modal_registro = function(latLng){

	
		$.confirm({
            title:'Informativo',
            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Quiere registrar otro punto?<h4>',
            cancelButton: 'No',
            confirmButton: 'Si',
            confirm: function() {
            	self.titulo('Registrar punto GPS');
            	self.consultar_activos();
            	$('#modal_registro_gps').modal('show');
                    
            }
        });
	    
	}

	self.consultar_activos = function(){
		path = path_principal+'/api/activosactivo/?format=json';
        parameter = {
        	ignorePagination:true,

        };
        RequestGet(function (datos, estado, mensage) {

	        if (estado=='ok' && datos!=null && datos.length > 0) {
                self.listado_activos(datos);
	        }else{
	          	self.listado_activos([]);
	        }
	        cerrarLoading();
        }, path, parameter, undefined, false, false);
	}


	self.guardar_punto = function(){
		self.puntosGPSVO.id(0);
        self.puntosGPSVO.latitud(lat.lat());
        self.puntosGPSVO.longitud(lat.lng());
		if (UbicacionViewModel.errores_puntos().length == 0 ) {
			
	   		alert(self.puntosGPSVO.longitud());
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
					$('#modal_registro_gps').modal('hide');
	            },//funcion para recibir la respuesta 
	            url:path_principal+'/api/activospuntosgps/',//url api
				parametros:self.puntosGPSVO,
				alerta:false    
	            //parametros: self.cronogramaVO
	        };
	        RequestFormData(parametros);

        }else{
            UbicacionViewModel.errores_puntos.showAllMessages();
            self.puntosGPSVO.latitud('');
        	self.puntosGPSVO.longitud('');
        }
	}


	self.abrir_modal_busqueda = function(){
		self.filtrado.categoria(sessionStorage.getItem("app_activo_ubicacion_categoria")); 

        if (sessionStorage.getItem("app_activo_ubicacion_tipo")!='' && sessionStorage.getItem("app_activo_ubicacion_categoria")==''){
            self.filtrado.tipo(sessionStorage.getItem("app_activo_ubicacion_tipo"));
        }

        self.filtrado.estado(sessionStorage.getItem("app_activo_ubicacion_estado"));    
        self.filtrado.funcionario(sessionStorage.getItem("app_activo_ubicacion_funcionario"));

        $('#modal_busqueda').modal('show');
	}

	self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    self.setColorIconoFiltro = function (){
        
        var categoria= sessionStorage.getItem("app_activo_ubicacion_categoria")||'';
        var tipo = sessionStorage.getItem("app_activo_ubicacion_tipo")||'';
        var estado = sessionStorage.getItem("app_activo_ubicacion_estado")||'';    
        var funcionario = sessionStorage.getItem("app_activo_ubicacion_funcionario")||'';    

        

        if (categoria != '' || tipo != '' || estado != '' && estado != 2 || funcionario != ''){

            $('#iconoFiltro').addClass("filtrado");
        }else{
            $('#iconoFiltro').removeClass("filtrado");
        }
    }

	self.consultar = function (editar_mapa){
        sessionStorage.setItem("app_activo_ubicacion_categoria", self.filtrado.categoria() || '');
        sessionStorage.setItem("app_activo_ubicacion_tipo", self.filtrado.tipo() || '');
        sessionStorage.setItem("app_activo_ubicacion_estado", self.filtrado.estado() || '');
        sessionStorage.setItem("app_activo_ubicacion_funcionario", self.filtrado.funcionario() || '');
        

        
        self.cargar(editar_mapa);
    }

    self.cargar = function (editar_mapa){
    	path = path_principal+'/api/activospuntosgps/?format=json';

    	self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("app_activo_ubicacion_dato", self.filtro() || '');

            var categoria= sessionStorage.getItem("app_activo_ubicacion_categoria")||'';
            var tipo = sessionStorage.getItem("app_activo_ubicacion_tipo")||'';
            var estado = sessionStorage.getItem("app_activo_ubicacion_estado")||'';    
            var funcionario = sessionStorage.getItem("app_activo_ubicacion_funcionario")||'';


        parameter = {
        	//activo:,
        	dato: self.filtro(),
            categoria: categoria,
            tipo: tipo,
            estado: estado,
            funcionario: funcionario,
        	ignorePagination:true,

        };
        RequestGet(function (datos, estado, mensage) {

	        if (estado=='ok' && datos!=null && datos.length > 0) {
        	 	//alert('3');        	 	
	        	    self.mensaje('');
                self.listado(datos);
                self.setColorIconoFiltro();
                self.initMap();
                $('#content_map').show();      
                //ocultarNuevoRegistro();
                //self.limpiar();
	        }else{
	        	//alert('4');	        	 
	          	self.mensaje(mensajeNoFound);
	          	self.listado([]);
               $('#content_map').hide();
	        }
	        
	       	
	       
	        
	        
	        cerrarLoading();
        }, path, parameter, undefined, false, false);
    }



    self.filtrado.categoria.subscribe(function (val) {       
        self.consultar_tipos(1,val);
    });

    self.consultar_tipos = function (pagina,categoria_id){
        path = self.url+'activostipo_Activo/?format=json';
        if (pagina > 0){
            parameter = {
                categoria:categoria_id
            };
            RequestGet(function (datos, estado, mensage) {
                
                if (estado == 'ok' && datos != null && datos.count > 0) {                 
                   
                    self.listado_tipo(agregarOpcionesObservable(datos.data));

                     self.listado_tipo.sort(function (a, b) {
                      if (a.nombre > b.nombre) {
                        return 1;
                      }
                      if (a.nombre < b.nombre) {
                        return -1;
                      }
                      // a must be equal to b
                      return 0;
                    }); 

                    if (sessionStorage.getItem("app_activo_ubicacion_tipo")!=''){
                        self.filtrado.tipo(sessionStorage.getItem("app_activo_ubicacion_tipo"));
                    }
                    

                }else{                  
                    self.listado_tipo([]);        
                    
                }
    
                cerrarLoading();
            }, path, parameter,undefined,false);
        }else{
            self.mensaje('no se encontro la aplicación y/o el modulo');
        }
    }

	self.redirigir_a_mantenimientos=function(id){
		location.href=path_principal+'/activos/mantenimientos/'+id+'/'
	}

	self.abrir_modal_detalles = function(id){
		path =self.url+'activosactivo/'+id+'/?format=json';
        parameter = {};

        RequestGet(function (data, estado, mensage) {
            self.detalle.id(data.id);
            self.detalle.tipo(data.tipo.nombre);
            self.detalle.categoria(data.tipo.categoria.nombre);
            self.detalle.identificacion(data.identificacion);
            self.detalle.serial_placa(data.serial_placa);
            self.detalle.descripcion(data.descripcion);
            self.detalle.contrato(data.contrato.numero);
            self.detalle.contrato_id(data.contrato.id);
            self.detalle.valor_compra(data.valor_compra);
            self.detalle.responsable(data.responsable.persona.nombres+' '+data.responsable.persona.apellidos);
            self.detalle.vida_util_dias(data.vida_util_dias);
            self.detalle.periodicidad_mantenimiento(data.periodicidad_mantenimiento);            
            self.detalle.fecha_alta(data.fecha_alta);

            if (data.debaja){
                self.detalle.debaja(true);
                self.detalle.debaja_color('#FF0000');
                self.detalle.debaja_estado('De baja');
                self.detalle.fecha_baja(data.fecha_baja);
                self.detalle.motivo_debaja(data.motivo_debaja)
      
            }
            else{
                self.detalle.debaja(false);
                self.detalle.debaja_color('#008000');
                self.detalle.debaja_estado('De alta');
                self.detalle.fecha_baja('');
                self.detalle.motivo_debaja('')
  
            }            
            cerrarLoading();
        },path, parameter,function() {
            self.titulo('Información detalle del activo No. '+self.detalle.id());
            $('#detalle_activo').modal('show');
        });
    }

    self.ver_soporte = function() {
      window.open(path_principal+"/activos/ver-soporte/?id="+ self.detalle.id(), "_blank");
    }

    self.ver_soporte_contrato = function() {
      window.open(path_principal+"/activos/ver-soporte-activos/?id="+ self.detalle.contrato_id(), "_blank");
    }

    //GESTION DOCUMENTAL
    self.archivoFisicoBaja = function() {
        window.open('../../../gestiondocumental/archivofisico/Activos soportes de baja/' + 
            self.quitarTildes(self.detalle.tipo().toString()) + ' - ' + self.quitarTildes(self.detalle.descripcion().toString()) + '/' + 
            self.quitarTildes(self.detalle.id().toString())  + '/', '_blank');
    }
    self.archivoFisicoAlta = function() {
        window.open('../../../gestiondocumental/archivofisico/Contrato/contrato No. ' + 
            self.detalle.contrato().toString() + '/' + 
            self.detalle.contrato_id().toString()  + '/', '_blank');
    }
    self.archivoFisicoMantenimiento = function () {
        window.open('../../../gestiondocumental/archivofisico/Activos soportes de mantenimiento/activo id No.' + 
            self.quitarTildes(self.detalle.tipo().toString()) + ' - ' + self.quitarTildes(self.detalle.descripcion().toString()) + '/' + 
            self.quitarTildes(self.detalle.id().toString())  + '/', '_blank');       
    }

    self.quitarTildes = function (cadena) {
        cadena = cadena.replace("á","a");
        cadena = cadena.replace("é","e");
        cadena = cadena.replace("í","i");
        cadena = cadena.replace("ó","o");
        cadena = cadena.replace("ú","u");

        return cadena;
    }

}

var ubicacion= new UbicacionViewModel();
$('#txtBuscar').val(sessionStorage.getItem("app_activo_ubicacion_dato"))
ubicacion.cargar(false);
UbicacionViewModel.errores_puntos = ko.validation.group(ubicacion.puntosGPSVO);
ko.applyBindings(ubicacion);





function llamarVerDetalles(id){
    //Mostrar el popup con las propiedades
    ubicacion.abrir_modal_detalles(id);
}

function llamarMantenimientos(id){
    //Mostrar el popup con las propiedades
    ubicacion.redirigir_a_mantenimientos(id);
}