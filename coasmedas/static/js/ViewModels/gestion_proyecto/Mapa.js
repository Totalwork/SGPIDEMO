
function MapaViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
    self.listado_proyectos=ko.observableArray([]);
	self.mensaje=ko.observable('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>Indique parametro de filtro.</div>');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false); 

    self.checkall2=ko.observable(false); 

    self.fondo_id=ko.observable('');
    self.departamento_id=ko.observable('');
    self.municipio_id=ko.observable('');


    self.listado_municipio=ko.observableArray([]);

    self.listado_proyectos=ko.observableArray([]);


	 self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
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

    self.abrir_modal = function () {
        //self.limpiar();
        self.titulo('Filtro de Proyecto');
        $('#modal_filter').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

     self.departamento_id.subscribe(function(value){

        if(value!=0){
                path = path_principal+'/api/Municipio/?ignorePagination&id_departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                    self.listado_municipio(datos);
                }, path, parameter);
        }else{
            self.listado_municipio([]);
        }

    });


     self.agregar=function(){

        ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                    
                    var match = ko.utils.arrayFirst(self.listado_proyectos(), function(item) {
                    return d.id === item.id();
                     })

                    if(match==null){
                        self.listado_proyectos.push({
                            'id':ko.observable(d.id),
                            'nombre':ko.observable(d.nombre),
                            'departamento':ko.observable(d.municipio.departamento.nombre),
                            'municipio':ko.observable(d.municipio.nombre),
                            'fondo':ko.observable(d.fondo.nombre),
                            'check':ko.observable(true)
                        });
                    }
                }
         });
        self.checkall(false);
        if(self.listado_proyectos().length>0){
            self.consultar_gps(self.listado_proyectos());
        }

     }

     self.limpiar=function(){
        self.listado_proyectos([]);
        self.checkall2(false);
     }


      self.eliminar_punto=function(obj){

          self.consultar_gps(self.listado_proyectos());
          return true;
      }



    self.consultar_gps=function(data){

        if(data.length>0){
            var lista='';
            ko.utils.arrayForEach(data, function(d) {
                  if(d.check()==true){                  
                      if(lista!=''){                        
                            lista=lista+','+d.id();
                        }else{
                            lista=d.id();
                        }
                  }
            }); 

            if(lista!=''){
                path = path_principal+'/api/GestionProyectoMapaDiseno?format=json&sin_paginacion';
                parameter = {lista_diseno:lista};
                RequestGet(function (datos, estado, mensage) {

                        if (estado == 'ok') {
                                
                                newposition(datos);  

                        }
                    }, path, parameter);
            }else{
               newposition([]); 
            }
            
        }else{
            newposition([]);
        }
        

    }

    self.cargar_mapa=function(){
     
         newposition([]);
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



    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {  
            self.filtro($('#txtBuscar').val());
             if (self.departamento_id()==0 && self.municipio_id()==0 && self.fondo_id()==0 && self.filtro()=='') {
                        $.confirm({
                            title: 'Error',
                            content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Ingrese algun criterio para la busqueda. <h4>',
                            cancelButton: 'Cerrar',
                            confirmButton: false
                        }); 
            }else{
                 //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
                    
                    path = path_principal+'/api/GestionProyectoDiseno?format=json&page='+pagina;
                    parameter = { dato: self.filtro(), pagina: pagina,fondo_id:self.fondo_id(),departamento_id:self.departamento_id(),municipio_id:self.municipio_id()};
                    RequestGet(function (datos, estado, mensage) {

                        if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                            self.mensaje('');
                            //self.listado(results); 
                            self.listado(agregarOpcionesObservable(datos.data));  

                        } else {
                            self.listado([]);
                            self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                        }

                        $('#modal_filter').modal('hide');
                        self.llenar_paginacion(datos,pagina);
                        //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                        //    $('#paginacion').show();
                        //    self.llenar_paginacion(results,pagina);
                        //}
                    }, path, parameter);
            }         
            
        }


    }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.checkall2.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_proyectos(), function(d) {

                    d.check(value);
             }); 

             if(value==true){
                self.consultar_gps(self.listado_proyectos());
             }else{
                self.consultar_gps([]);
             }
             
    });

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/GestionProyectoFondo/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Tipo de Fondo');

             self.mapaVO.id(results.id);
             self.mapaVO.nombre(results.nombre);
             self.mapaVO.estado_id(results.estado.id);
             self.mapaVO.empresa_id(results.empresa.id);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }




 }

var mapa = new MapaViewModel();
mapa.cargar_mapa();
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(mapa,content);
ko.applyBindings(mapa,header);