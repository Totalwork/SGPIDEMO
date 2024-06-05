function EnlaceViewModel(){
	var self = this;
  var map;
  var lat;
  self.titulo=ko.observable('');
	self.mensaje=ko.observable('');
	self.nodo=ko.observable('');
	self.capa=ko.observable('');
	self.filtro=ko.observable('');
	self.listado=ko.observableArray([]);
	self.url=path_principal+'/api/';

  self.listadoUc = ko.observableArray([]);
  self.mensajeUc = ko.observable('');
  self.listadoMateriales = ko.observableArray([]);
  self.mensajeMateriales = ko.observable('');

  var currentZoom;

  self.archivo_carga=ko.observable('');


  self.apoyoVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del capitulo' } }),
        longitud:ko.observable(''),
        latitud:ko.observable(''),
        presupuesto_id:ko.observable($("#id_presupuesto").val()),
        capa_id:ko.observable(0)
     };
    //funcion consultar todos los enlaces

    
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Apoyo');
        $('#modal_acciones').modal('show');
        
    }


    self.abrir_modal_carga = function () {
        self.archivo_carga=ko.observable('');
        self.titulo('Cargar Apoyo');
        $('#modal_cargar').modal('show');
        
    }

    self.limpiar=function(){
        self.apoyoVO.nombre('');
    }

    self.consultar=function(){

        self.filtro($('#txtBuscar').val());
        sessionStorage.setItem("filtro_avance",self.filtro() || '');

        self.cargar();

    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            //self.limpiar();
            self.consultar();
        }
        return true;
    }

    self.cargar = function () {

            let filtro_avance=sessionStorage.getItem("filtro_avance");
            path = path_principal+'/api/avanceGrafico2Nodo/?sin_paginacion=1&lite=1';
            parameter = { presupuesto_id:$('#id_presupuesto').val(),dato: filtro_avance,programando:0,eliminado:0};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos));
                    

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.initMap();

               
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
        }


    self.guardar=function(){
        self.guardar_nodo(lat);
    }


   



    self.initMap = function(){
  // defino el mapa con estilo nocturno
    center = {lat: 10.9494272, lng: -74.801152}
    zoom = 6
    if (sessionStorage.getItem("ubicacionActual") != 'null') {
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

  


  ko.utils.arrayForEach(self.listado(), function(d) {
          
        var marker = new google.maps.Marker({
          position: {
                      lat: parseFloat(d.latitud),
                      lng:  parseFloat(d.longitud)
          },
          map: map,
          title: d.nombre,
          draggable:true
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
            var contentStringOrg = '<div id="content">'+
            '<div id="siteNotice">'+
            '</div>'+
            '<h1 id="firstHeading" class="firstHeading">'+d.nombre+'</h1>'+
            '<div id="bodyContent">'+
            '<p><button onclick="eliminarpunto('+d.id+')">Eliminar Punto...</button></p>'+
            '<p><button onclick="verCantidades('+d.id+','+ $('#id_presupuesto').val()+')">Ver cantidades de obra...</button></p>';

            contentStringOrg=contentStringOrg+'</div></div>';           
            var infowindow = new google.maps.InfoWindow({
              content: contentStringOrg
            });
          infowindow.open(map, marker);
        });
  }); 

  map.addListener('click', function(e) {
      lat=e.latLng;
      map=map;
      self.abrir_modal();
  });

google.maps.event.addListener(map, 'zoom_changed', function() {
    var c = map.getCenter();
    sessionStorage.setItem("ubicacionActual", c.lat() + ',' 
                                  + c.lng() + ',' + map.getZoom());   
});
 
  //dibujar los nodos y enlaces
  //console.log(self.listado['0']);
 }


  self.actualizar_nodo=function(data){

                  self.apoyoVO.id(data.id);
                  self.apoyoVO.nombre(data.nombre);
                  self.apoyoVO.presupuesto_id(data.presupuesto.id);
                  self.apoyoVO.longitud(data.longitud);
                  self.apoyoVO.latitud(data.latitud);
                  self.apoyoVO.capa_id(data.capa.id);

                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.consultar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/avanceGrafico2Nodo/'+self.apoyoVO.id()+'/',
                       parametros:self.apoyoVO,
                       alerta:false                    
                  };

                  RequestFormData(parametros);


  }


  self.guardar_nodo=function(latLng){


      if (EnlaceViewModel.errores_apoyo().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);            
            self.apoyoVO.capa_id($('#id_capa_manual').val());
                self.apoyoVO.latitud(latLng.lat());
                self.apoyoVO.longitud(latLng.lng());
                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                            self.consultar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceGrafico2Nodo/',//url api
                     parametros:self.apoyoVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
        } else {
             EnlaceViewModel.errores_apoyo.showAllMessages();//mostramos las validacion
        }
  }


  self.descargar_plantilla=function(){
         location.href=path_principal+"/avanceObraLite/descargar_plantilla_apoyo/";

  }

  self.guardar_datos=function(){

         if(self.archivo_carga()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar los apoyos.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('presupuesto_id',$('#id_presupuesto').val());
            data.append('capa_id',$('#id_capa_archivo').val());
            data.append('archivo',self.archivo_carga());

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar();
                            $('#modal_cargar').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraLite/guardar_apoyo_archivo/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }
  }

  self.eliminar_punto = function (id) {

            var lista_id=[];
        
            lista_id.push({
                 id:id
            })

        
             var path =path_principal+'/avanceObraLite/eliminar_apoyos/';
             var parameter = {lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar el punto?", path, parameter, function () {
                 self.consultar(1);
             })
        
    }
    self.consultarCantidades = function(nodo_id,presupuesto_id) {
      //consume el servicio http://localhost:8000/avanceObraLite/cantidadesnodo/nodo_id/presupuesto_id/
      //alert(nodo_id.toString() + ', ' + presupuesto_id.toString());
      
      path = path_principal+'/avanceObraLite/cantidadesnodo/'+ 
      nodo_id.toString() + '/' + presupuesto_id.toString() + '/';
      parameter = {};
      RequestGet(function (datos, estado, mensage) {
          if (estado == 'ok' && datos!=null) {
            if (datos.unidadesConstructivas!= null && datos.unidadesConstructivas.length > 0) {
              self.listadoUc(agregarOpcionesObservable(datos.unidadesConstructivas));  
              self.mensajeUc('');
            }else{
              self.listadoUc([]);
              self.mensajeUc('<div class="alert alert-warning alert-dismissable">'+
                '<i class="fa fa-warning"></i>No se encontraron Unidades constructivas asociadas al apoyo</div>');
            }
            if (datos.materiales!= null && datos.materiales.length > 0) {
              self.listadoMateriales(agregarOpcionesObservable(datos.materiales));  
              self.mensajeMateriales('');
            }else{
              self.listadoMateriales([]);
              self.mensajeMateriales('<div class="alert alert-warning alert-dismissable">'+
                '<i class="fa fa-warning"></i>No se encontraron materiales asociadas al apoyo</div>');
            }              
          } else {
              self.listadoUc([]);
              self.listadoMateriales([]);
              self.mensajeUc('<div class="alert alert-warning alert-dismissable">'+
                '<i class="fa fa-warning"></i>No se encontraron Unidades constructivas asociadas al apoyo</div>');
              self.mensajeMateriales('<div class="alert alert-warning alert-dismissable">'+
                '<i class="fa fa-warning"></i>No se encontraron materiales asociadas al apoyo</div>');

          }
          $('#modal_cantidades').modal('show'); 
          cerrarLoading();
      }, path, parameter,undefined, false);

    }

}

var enlace = new EnlaceViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
EnlaceViewModel.errores_apoyo = ko.validation.group(enlace.apoyoVO);
enlace.cargar();
ko.applyBindings(enlace);


function eliminarpunto(id){
    //Mostrar el popup con las propiedades
    enlace.eliminar_punto(id);
}

function verCantidades(nodo_id,presupuesto_id){
  enlace.consultarCantidades(nodo_id,presupuesto_id);
}



