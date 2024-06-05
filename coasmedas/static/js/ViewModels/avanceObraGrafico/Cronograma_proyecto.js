function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   


    self.cronogramaVO={
        id:ko.observable(0),
        presupuesto_id:ko.observable($('#id_presupuesto').val()),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre' } }),
        fechaInicio:ko.observable('').extend({ required: { message: '(*)Digite la fecha de inicio del cronograma' } }),
        estado_id:ko.observable(0)
     };



     self.listado_estado=ko.observableArray([]);
     self.id_estado=ko.observable();


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

    self.abrir_modal = function () {
        //self.limpiar();
        self.titulo('Registrar');
        $('#modal_acciones').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un cronograma para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraGrafico/eliminar_id_cronograma/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los cronogramas seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    }


    self.exportar_excel=function(){
        
    }

    // //limpiar el modelo 
     self.limpiar=function(){   
           self.cronogramaVO.nombre('');
           self.cronogramaVO.fechaInicio('');
     }



    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

             self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_avance",self.filtro() || '');

            self.cargar(pagina);

        }


    }


    self.cargar =function(pagina){           


            let filtro_avance=sessionStorage.getItem("filtro_avance");

            path = path_principal+'/api/avanceObraGraficoCronograma/?format=json&page='+pagina;
            parameter = {dato: filtro_avance, pagina: pagina,presupuesto_id:$("#id_presupuesto").val()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));
                     $('#modal_acciones').modal('hide');

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

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            //self.limpiar();
            self.consultar(1);
        }
        return true;
    }


    self.guardar=function(){

         if (IndexViewModel.errores_cronograma().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.cronogramaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceObraGraficoCronograma/',//url api
                     parametros:self.cronogramaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
            }else{

                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                          self.limpiar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/avanceObraGraficoCronograma/'+self.cronogramaVO.id()+'/',
                       parametros:self.cronogramaVO                        
                  };

                  Request(parametros);

            }

        } else {
             IndexViewModel.errores_cronograma.showAllMessages();//mostramos las validacion
        }
    }



    self.abrir_hitos=function(obj){
        
       location.href=path_principal+"/avanceObraGrafico/actividades_lectura/"+obj.presupuesto.id+"/"+obj.presupuesto.proyecto.id+"/"+obj.presupuesto.esquema.id+"/";
    }


    self.abrir_cantidad_ejecutar=function(obj){
             
       location.href=path_principal+"/avanceObraGrafico/cantidad_ejecutar/"+obj.presupuesto.id+"/"+obj.presupuesto.proyecto.id+"/";
    }

    self.abrir_linea_base=function(obj){
             
       location.href=path_principal+"/avanceObraGrafico/linea_base/"+obj.presupuesto.id+"/"+obj.presupuesto.proyecto.id+"/"+obj.id+"/";
    }


    self.abrir_cambio=function(obj){
             
       location.href=path_principal+"/avanceObraGrafico/cambio/"+obj.presupuesto.id+"/"+obj.presupuesto.proyecto.id+"/"+obj.id+"/";
    }


    self.abrir_programacion=function(obj){

        path =path_principal+'/api/avanceObraGraficoCronograma/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
           
            if(results.programacionCerrada==true){

                location.href=path_principal+"/avanceObraGrafico/programacion/"+obj.presupuesto.id+"/"+obj.presupuesto.proyecto.id+"/"+obj.id+"/";
   
            }else{

                  $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe cerrar la linea base para ingresar a la programacion.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });

            }

         }, path, parameter);
             
       }


    self.abrir_avance_obra=function(obj){

        path =path_principal+'/api/avanceObraGraficoCronograma/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
           
            if(results.programacionCerrada==true){

                location.href=path_principal+"/avanceObraGrafico/avance_obra/"+obj.presupuesto.id+"/"+obj.presupuesto.proyecto.id+"/"+obj.id+"/";
   
            }else{

                  $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe cerrar la linea base para ingresar al avance de obra.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });

            }

         }, path, parameter);
             
       }



    self.abrir_avance_obra_sin_gps=function(obj){

        path =path_principal+'/api/avanceObraGraficoCronograma/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
           
            if(results.programacionCerrada==true){

                location.href=path_principal+"/avanceObraGrafico/avance_obra_sin_gps/"+obj.presupuesto.id+"/"+obj.presupuesto.proyecto.id+"/"+obj.id+"/";
   
            }else{

                  $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe cerrar la linea base para ingresar al avance de obra.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });

            }

         }, path, parameter);
             
       }


 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
index.cargar(1);//iniciamos la primera funcion
IndexViewModel.errores_cronograma = ko.validation.group(index.cronogramaVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

