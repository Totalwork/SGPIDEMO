
function MapaGrandeViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false); 


    self.consultar_gps=function(){

        path = path_principal+'/api/GestionProyectoMapaDiseno?format=json&sin_paginacion';
        parameter = {diseno_id:$('#id_diseno').val()};
        RequestGet(function (datos, estado, mensage) {
                self.mensaje('');
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                        
                        newposition(datos);  

                }else{
                     newposition([]);
                     self.mensaje(mensajeNoFound);
                }
            }, path, parameter);

    }

    function newposition(data){


          var place2 = new Array();
          var marker=[];
          var conteo=0;

          ko.utils.arrayForEach(data, function(d) {            
                
                place2[d.nombre]=new google.maps.LatLng(d.latitud, d.longitud);
                conteo=conteo+1;
           });

           
          var mapProp = {
              center:new google.maps.LatLng(10.084631601432866, -73.96812207270507),
              zoom:7,
              mapTypeId:google.maps.MapTypeId.ROADMAP
              };

            map=new google.maps.Map(document.getElementById("googleMap"),mapProp);
            var limits = new google.maps.LatLngBounds();

            if(data.length!=0){
                    for(var i in place2){
             
                        marker=new google.maps.Marker({
                          position:place2[i],
                          title:i
                          });
                        marker.setMap(map);
                         google.maps.event.addListener(marker, 'click', function(){
                            var popup = new google.maps.InfoWindow();
                            var note = this.title;
                            popup.setContent(note);
                            popup.open(map, this);
                        });

                        limits.extend(place2[i]);
                }

          
              
               map.fitBounds(limits);  
                if(conteo==1){
                  
                  zoomChangeBoundsListener = google.maps.event.addListenerOnce(map, 'bounds_changed', function(event) {
                          if (this.getZoom()){
                              this.setZoom(14);
                          }
                  });
              }  
               
               google.maps.event.trigger(map, 'resize');
  
            }else{
              google.maps.event.addDomListener(window, 'load');
            }
  }



 }

var mapa = new MapaGrandeViewModel();
mapa.consultar_gps();
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(mapa,content);
ko.applyBindings(mapa,header);