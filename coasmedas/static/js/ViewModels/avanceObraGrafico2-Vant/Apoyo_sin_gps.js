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

  self.archivo_carga=ko.observable('');
  self.checkall=ko.observable(false);

  self.filtro_gps=ko.observable(0);


  self.apoyoVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del capitulo' } }),
        longitud:ko.observable(''),
        latitud:ko.observable(''),
        presupuesto_id:ko.observable($("#id_presupuesto").val()),
        capa_id:ko.observable(0),
        porcentajeAcumulado:ko.observable(0)
     };
    //funcion consultar todos los enlaces


     self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
        directiones: ko.observable(true),
        limite: ko.observable(true),
        cantidad_por_paginas: ko.observable(0),
        totalRegistrosBuscados:ko.observable(0),
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
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

     self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Apoyo');
        $('#modal_acciones').modal('show');
        
    }


     self.abrir_modal_filter = function () {
        self.limpiar();
        self.titulo('Filtro');
        $('#modal_filter').modal('show');
        
    }


    self.abrir_modal_carga = function () {
        self.archivo_carga=ko.observable('');
        self.titulo('Cargar Apoyo');
        $('#modal_cargar').modal('show');
        
    }

    self.limpiar=function(){
        self.apoyoVO.nombre('');
    }

    self.consultar=function(pagina){

        self.filtro($('#txtBuscar').val());
        sessionStorage.setItem("filtro_avance",self.filtro() || '');

        self.cargar(pagina);

    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            //self.limpiar();
            self.consultar(1);
        }
        return true;
    }

    self.eliminar=function(){

       var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id.push({
                        id:d.id
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un apoyo para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraGrafico2/eliminar_apoyos/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los apoyos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }  

    }

    self.busqueda_filtro=function(){
        self.consultar(1);
        $('#modal_filter').modal('hide');
    }

    self.cargar = function (pagina) {

            let filtro_avance=sessionStorage.getItem("filtro_avance");
            path = path_principal+'/api/avanceGrafico2Nodo/?format=json';
            parameter = { presupuesto_id:$('#id_presupuesto').val(),dato: filtro_avance,programando:0,eliminado:0,filtro_gps:self.filtro_gps()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));
                    

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }


               self.llenar_paginacion(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
        }


    
   


     self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
        path =path_principal+'/api/avanceGrafico2Nodo/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
           
             self.titulo('Actualizar Nodo');

             self.apoyoVO.id(results.id);
             self.apoyoVO.nombre(results.nombre);
             self.apoyoVO.capa_id(results.capa.id);
             self.apoyoVO.longitud(results.longitud);
             self.apoyoVO.latitud(results.latitud);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }


     self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });



  self.guardar=function(){


      if (EnlaceViewModel.errores_apoyo().length == 0) {//se activa las validaciones

          if(self.apoyoVO.id()==0){


           // self.contratistaVO.logo($('#archivo')[0].files[0]);            
            self.apoyoVO.capa_id($('#id_capa_manual').val());
                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                            self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceGrafico2Nodo/',//url api
                     parametros:self.apoyoVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

          }else{
              var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                           $('#modal_acciones').modal('hide');
                            self.limpiar();
                            self.consultar(1);
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/avanceGrafico2Nodo/'+self.apoyoVO.id()+'/',
                       parametros:self.apoyoVO        
                  };

                  Request(parametros);
          }

        } else {
             EnlaceViewModel.errores_apoyo.showAllMessages();//mostramos las validacion
        }
  }


  self.descargar_plantilla=function(){
         location.href=path_principal+"/avanceObraGrafico2/descargar_plantilla_apoyo_sinposicion/";

  }

  self.guardar_datos=function(){

         if(self.archivo_carga()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar el presupuesto.<h4>',
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
                     url:path_principal+'/avanceObraGrafico2/guardar_apoyo_archivo_sinposicion/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }
  }

 

}

var enlace = new EnlaceViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
EnlaceViewModel.errores_apoyo = ko.validation.group(enlace.apoyoVO);
enlace.cargar(1);
ko.applyBindings(enlace);



