function PuntosGPSViewModel(){
  
  var self = this;
  self.listado_gps=ko.observableArray([]);
    self.titulo=ko.observable('');
    self.macrocontrato_select=ko.observable('');
    self.departamento=ko.observable('');
    self.municipio=ko.observable('');
    self.contratoobra=ko.observable('');
    self.lista_obra=ko.observableArray([]);
    self.contratista=ko.observableArray([]);
    self.listado_contratista=ko.observableArray([]);
    self.departamento_select=ko.observableArray([]);
    self.listado_municipio=ko.observableArray([]);

    self.estado_proyecto=ko.observable('');
    self.proyecto=ko.observable('');
    self.proyectonombre=ko.observable('');


    self.cambiar_contratista=ko.observable(0);
    self.cambiar_departamento=ko.observable(0);
    self.cambiar_municipio=ko.observable(0);


  // self.url=path_principal+'api/PuntosGPSViewModel';
  //Representa un modelo de la tabla persona

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

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }

    //Funcion para crear la paginacion
    self.abrir_filtro = function () {
        $('#modal_filtro').modal('show');
        self.titulo('Filtro');
        self.filtros('','','','');


    }

        self.filtros=function(contrato,contratista,departamento,municipio){

             path =path_principal+'/api/Proyecto/?filtros=1';
             parameter='';
             if (contrato!='') {
                parameter+='contrato_id='+contrato;
             }
             if (contratista!='') {
                parameter+='&id_contratista='+contratista;
             }
             if (departamento!='') {
                parameter+='&departamento_id='+departamento;
             }
             if (municipio!='') {
                parameter+='&municipio_id='+municipio;
             }                         
             RequestGet(function (results,count) {

            if(self.cambiar_contratista() == 0){ 

                self.listado_contratista(results.data.contratistas)
                $("#contratista").append(self.listado_contratista()).multiselect("destroy").multiselect({
                    includeSelectAllOption: true,
                    selectAllText:'Seleccionar todo',
                    nonSelectedText: 'Ninguno seleccionado',
                    nSelectedText: 'Seleccionado',
                    allSelectedText: 'Todo seleccionado'    
                });                
            }

            if (self.cambiar_departamento()==0) {

                self.departamento_select(results.data.departamentos);

                $("#departamento").append(self.departamento_select()).multiselect("destroy").multiselect({
                    includeSelectAllOption: true,
                    selectAllText:'Seleccionar todo',
                    nonSelectedText: 'Ninguno seleccionado',
                    nSelectedText: 'Seleccionado',
                    allSelectedText: 'Todo seleccionado'    
                });                


            }

            if (self.cambiar_municipio()==0) {

                self.listado_municipio(results.data.municipios)

                $("#municipio").append(self.listado_municipio()).multiselect("destroy").multiselect({
                    includeSelectAllOption: true,
                    selectAllText:'Seleccionar todo',
                    nonSelectedText: 'Ninguno seleccionado',
                    nSelectedText: 'Seleccionado',
                    allSelectedText: 'Todo seleccionado'    
                });

            }

             }, path, parameter,undefined,false,false);
             
        }


        //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
        self.macrocontrato_select.subscribe(function (value) {

            if(value.length >0){

                self.cambiar_contratista(0);

                self.cambiar_departamento(0);

                self.cambiar_municipio(0);

                self.filtros(value,'','','');

            }else{
                self.filtros('','','','');

            }
        });    


        self.contratista.subscribe(function (value) {

            
            if(value.length >0){
                console.log(value)
                self.cambiar_contratista(1);
                self.cambiar_departamento(0);
                self.cambiar_departamento(0);

                self.filtros(self.macrocontrato_select(),value,'','');

            }else{
                self.cambiar_contratista(0);
                self.cambiar_departamento(0);
                self.cambiar_departamento(0);
                self.filtros('','','','');
            }

        });  

        self.departamento.subscribe(function (value) {

            
            if(value.length >0){
                console.log(value)
                self.cambiar_contratista(1);
                self.cambiar_departamento(1);
                self.cambiar_departamento(0);

                self.filtros(self.macrocontrato_select(),self.contratista(),value,'');

            }else{
                self.cambiar_contratista(0);
                self.cambiar_departamento(0);
                self.cambiar_departamento(0);
                self.filtros('','','','');
            }

        });             

    self.consultar_puntos_gps=function(){
         //path =path_principal+'/contrato/list_contrato_select/?mcontrato='+value+'&contratista=0';
        path =path_principal+'/api/Puntos_gps/?sin_paginacion&puntosgpslite=0&mcontrato='+self.macrocontrato_select()+'&contratista='+self.contratista()
                              +'&departamento='+self.departamento()+'&municipio='+self.municipio()+'&estado_proyecto='+self.estado_proyecto()+'&proyectonombre='+self.proyectonombre();
         parameter=''
         // parameter={mcontrato: self.macrocontrato_select(),
         //            contratista:self.contratista(),
         //            departamento: self.departamento(),

          RequestGet(function (results,count) {
            
            self.listado_gps(results);
            self.initialize();
             $('#modal_filtro').modal('hide');
             cerrarLoading();

  
         }, path, parameter,undefined, false);
         
    }

    self.initialize=function() {


      var map = new google.maps.Map(document.getElementById('mapa'), {
        zoom: 7,
        center: new google.maps.LatLng(10.684568, -74.295508),
        mapTypeId: google.maps.MapTypeId.ROADMAP,
      });

      var infowindow = new google.maps.InfoWindow();
      var marker, i;

      for (i = 0; i < PuntosGPS.listado_gps().length; i++) {

          ruta =  'https://s3-us-west-2.amazonaws.com/source-sinin-prueba/media/plantillas/ubicacion/'

        marker = new google.maps.Marker({
          position: new google.maps.LatLng(PuntosGPS.listado_gps()[i].latitud, PuntosGPS.listado_gps()[i].longitud),
          map: map,
          //icon:ruta+PuntosGPS.listado_gps()[i].proyecto.estado_proyecto.icono
        });

        google.maps.event.addListener(marker, 'click', (function(marker, i) {
          return function() {

               path =path_principal+'/api/Puntos_gps/'+PuntosGPS.listado_gps()[i].id+'/?format=json';
               RequestGet(function (results,count) {


                   if (results.proyecto.contratistaObra=='') {contratista = 'No asignado'} else { contratista = results.proyecto.contratistaObra}
                  var contentString ='<div id="siteNotice">'+
                                              '</div>'+
                                                '<h5><p>'+results.proyecto.mcontrato.nombre+'</p></h5>'+
                                                '<h5 id="firstHeading" class="firstHeading">'+results.proyecto.nombre+'</h5>'+
                                                '<div id="bodyContent">'+
                                               '<p><b>Contratista:</b> '+contratista+'</p>'+
                                              '<p><b>Departamento:</b> '+results.proyecto.municipio.departamento.nombre+'</p>'+
                                              '<p><b>Municipio:</b> '+results.proyecto.municipio.nombre+'</p>'+
                                              '<p><b>Estado del proyecto:</b> '+ results.proyecto.estado_proyecto.nombre +'</p>'+
                                              '<p><b>No usuarios:</b> '+ results.proyecto.no_usuarios +'</p>'+
                                              '<p><b>Valor adjudicado:</b> $ '+ results.proyecto.valor_adjudicado +'</p>'+
                                              '<p><b>Nombre del punto:</b> '+ results.nombre +'</p>'+
                                              '<p><a href="../../proyecto/hoja_proyecto/'+results.proyecto.id+'">Ver mas</a></p>'+
                                              '</div>';

                  // infowindow.setContent(PuntosGPS.listado_gps()[i].nombre);
                  infowindow.setContent(contentString);
                  infowindow.open(map, marker);
               }, path, parameter);
            
           
          }
        })(marker, i));

      }

    }    



    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


 



}

var PuntosGPS = new PuntosGPSViewModel();


ko.applyBindings(PuntosGPS);

jQuery(document).ready(function() {

    $('#mcontrato').multiselect({

      
      includeSelectAllOption: true,
      selectAllText:'Seleccionar todo',
      nonSelectedText: 'Ninguno seleccionado',
      nSelectedText: 'Seleccionado',
      allSelectedText: 'Todo seleccionado'    
    });

    $('#contratista').multiselect({
      includeSelectAllOption: true,

      selectAllText:'Seleccionar todo',
      nonSelectedText: 'Ninguno seleccionado',
      nSelectedText: 'Seleccionado',
      allSelectedText: 'Todo seleccionado'    
    });

    $('#departamento').multiselect({
      includeSelectAllOption: true,
      selectAllText:'Seleccionar todo',
      nonSelectedText: 'Ninguno seleccionado',
      nSelectedText: 'Seleccionado',
      allSelectedText: 'Todo seleccionado'    
    });    

    $('#municipio').multiselect({
      includeSelectAllOption: true,
      selectAllText:'Seleccionar todo',
      nonSelectedText: 'Ninguno seleccionado',
      nSelectedText: 'Seleccionado',
      allSelectedText: 'Todo seleccionado'    
    });

    $('#estadoP').multiselect({
      includeSelectAllOption: true,
      selectAllText:'Seleccionar todo',
      nonSelectedText: 'Ninguno seleccionado',
      nSelectedText: 'Seleccionado',
      allSelectedText: 'Todo seleccionado'    
    });

    $('#estadoO').multiselect({
      includeSelectAllOption: true,
      selectAllText:'Seleccionar todo',
      nonSelectedText: 'Ninguno seleccionado',
      nSelectedText: 'Seleccionado',
      allSelectedText: 'Todo seleccionado'    
    });           



});


    //google.maps.event.addDomListener(window, 'load', initialize);    
