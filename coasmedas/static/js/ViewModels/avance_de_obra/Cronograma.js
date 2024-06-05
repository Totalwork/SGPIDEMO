
function CronogramaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco'; 


   self.listado_periodicidad=ko.observableArray([]);

   self.validacion_intervalo=ko.observable(0);


    self.cronogramaVO={
        id:ko.observable(0),
        proyecto_id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre' } }),
        intervalos:ko.observable(0).extend({ min: {params:1,message:"(*)Digite el intervalo del cronograma"}}),
        fecha_inicio_cronograma:ko.observable('').extend({ required: { message: '(*)Digite la fecha de inicio del cronograma' } }),
        periodicidad_id:ko.observable(0).extend({ min: {params:1,message:"(*)Seleccione la periodicidad"}}),
        esquema_id:ko.observable(0).extend({ min: {params:1,message:"(*)Seleccione el esquema"}}),
        estado_id:ko.observable('')
     };


     self.periodicidadVO={
        id:ko.observable(0),
        numero_dias:ko.observable(0).extend({ required: { message: '(*)Digite el numero de dias de periodicidad' } }),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre de la periodicidad' } })        
     }

      ko.validation.rules['fechaMenor'] = {
            validator: function (val, otherVal) {
                return val <= self.validador_hasta();
            },
            message: 'La fecha debe ser menor que la fecha hasta'
        };
    ko.validation.registerExtenders();

    ko.validation.rules['fechaMayor'] = {
            validator: function (val, otherVal) {
                return val >= self.validador_desde();
            },
            message: 'La fecha debe ser mayor que la fecha desde'
        };
    ko.validation.registerExtenders();


    self.validador_hasta=ko.observable('');
    self.validador_desde=ko.observable('');

    self.busqueda={
        id_opcion:ko.observable(0).extend({ required: { message: '(*)Seleccione un tipo' }}),
        desde:ko.observable('').extend({fechaMenor: ''}),
        hasta:ko.observable('').extend({fechaMayor: ''}),
        id_esquema:ko.observable(0).extend({ required: { message: '(*)Seleccione un esquema' }})
     }

     self.habilitar_fecha=ko.observable(false);


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
        self.limpiar();
        self.titulo('Registrar Cronograma'); 
        self.habilitar_campos(true);
        $('#modal_acciones').modal('show');
        
    }

    self.agregar_periodicidad=function(){
        self.limpiar_periodicidad();
       $('#modal_agregar').modal('show');
    }

    self.exportar_excel=function(){
        self.limpiar_informe();
        self.titulo('Informe');
        $('#modal_informe').modal('show');
    }

    self.limpiar_informe=function(){

        self.habilitar_fecha(false);
        self.validador_hasta('');
        self.validador_desde('');
        self.busqueda.id_opcion(0);
        self.busqueda.desde('');
        self.busqueda.hasta('');
        self.busqueda.id_esquema(0);

    }

    self.busqueda.id_opcion.subscribe(function(value){

            if(value==2){
                self.habilitar_fecha(true);
            }else{
                self.habilitar_fecha(false);
            }
    });

    
    self.busqueda.hasta.subscribe(function(value){

        self.validador_hasta(value);
    });

     self.busqueda.desde.subscribe(function(value){

        self.validador_desde(value);
    });


    self.descargar_excel=function(){

        if (CronogramaViewModel.errores_busqueda().length == 0) {//se activa las validaciones


               if((self.busqueda.desde()!='' && self.busqueda.hasta()!='') || self.busqueda.id_opcion()==1){
                     if(self.busqueda.id_opcion()==1){
                        location.href=path_principal+"/avance_de_obra/export_excel_cantidades?id_esquema="+self.busqueda.id_esquema()+'&proyecto_id='+$("#id_proyecto").val();
                    }else if(self.busqueda.id_opcion()==2){
                        location.href=path_principal+"/avance_de_obra/export_excel_resumen?id_esquema="+self.busqueda.id_esquema()+'&hasta='+self.busqueda.hasta()+'&desde='+self.busqueda.desde()+'&proyecto_id='+$("#id_proyecto").val();
                    }
                    
                    
               }else{
                   $.confirm({
                        title: 'Advertencia',
                        content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Debe seleccionar la fecha desde y la fecha hasta<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    }); 
               }

        } else {
             CronogramaViewModel.errores_busqueda.showAllMessages();//mostramos las validacion
        }   
    }

    self.guardar_periodicidad=function(){

            if (CronogramaViewModel.errores_periodicidad().length == 0) {//se activa las validaciones

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_agregar').modal('hide');  
                            self.consultar_periodicidad(); 
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Periodicidad/',//url api
                     parametros:self.periodicidadVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
           
            } else {
                 CronogramaViewModel.errores_periodicidad.showAllMessages();//mostramos las validacion
            }
    }

    self.consultar_periodicidad=function(){

        path = path_principal+'/api/Periodicidad/?sin_paginacion';
            parameter = '';
            RequestGet(function (datos, estado, mensage) {

                if (datos.length > 0) {
                    self.listado_periodicidad(datos);
                }
            }, path, parameter,undefined, false,false);
    }


    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.guardar=function(){

        if (CronogramaViewModel.errores_cronograma().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            self.cronogramaVO.proyecto_id($("#id_proyecto").val());
            if(self.cronogramaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Cronograma/',//url api
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
                       url:path_principal+'/api/Cronograma/'+self.cronogramaVO.id()+'/',
                       parametros:self.cronogramaVO                        
                  };

                  Request(parametros);

            }

        } else {
             CronogramaViewModel.errores_cronograma.showAllMessages();//mostramos las validacion
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


    // //limpiar el modelo 
     self.limpiar=function(){   
           self.cronogramaVO.nombre('');
           self.cronogramaVO.intervalos(0);
           self.cronogramaVO.fecha_inicio_cronograma('');
           self.cronogramaVO.periodicidad_id(0);
           self.validacion_intervalo(0);
           self.cronogramaVO.esquema_id(0);
     }

     // //limpiar el modelo de periodicidad
     self.limpiar_periodicidad=function(){   
           self.periodicidadVO.nombre('');
           self.periodicidadVO.numero_dias(0);
     }

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("dato_cronograma",self.filtro() || '');
            path = path_principal+'/api/Cronograma/?format=json&page='+pagina;
            parameter = { dato: self.filtro(), pagina: pagina,id_proyecto:$("#id_proyecto").val()};
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


    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.limpiar();
            self.consultar(1);
        }
        return true;
    }

    self.actividad=function(obj){
        
        location.href=path_principal+"/avance_de_obra/actividades/"+obj.id+"/"+$("#id_proyecto").val();
    }

    self.metas=function(obj){

        path = path_principal+'/avance_de_obra/listar_actividades/'+obj.id;
        parameter = {};
        RequestGet(function (results,count) {
            
            if(results.length==0){

                $.confirm({
                    title:'Advertencia',
                    content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Debe crear los capitulos y actividades, antes de ingresar las cantidades a ejecutar.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                 });
            }else{
                location.href=path_principal+"/avance_de_obra/metas/"+obj.id+"/"+$("#id_proyecto").val();
            }

        }, path, parameter);
    }


     self.linea_base=function(obj){

        path =path_principal+'/avance_de_obra/listar_metas_actividades/'+obj.id;
        parameter = '';
        RequestGet(function (results,count) {

            var sw=0;

            for(i=0;i<results.length;i++){

                if(results[i].cantidad!=null && results[i].cantidad>0){
                    sw=1;
                }
            }
               
            if(sw==0){

                $.confirm({
                    title:'Advertencia',
                    content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Debe crear los capitulos, actividades y las cantidades a ejecutar, antes de ingresar la linea base.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                 });
            }else{

                window.open(path_principal+"/avance_de_obra/linea_base/"+obj.id+"/"+$("#id_proyecto").val(),'_blank');
            }

        }, path, parameter);
        
    }


     self.linea_programada=function(obj){

        path =path_principal+'/api/Cronograma/'+obj.id;
        parameter = '';
        RequestGet(function (results,count) {
               
            if(results.linea_base_terminada==false){

                $.confirm({
                    title:'Advertencia',
                    content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Debe guardar la linea base, para crear la linea programada.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                 });
            }else{

                window.open(path_principal+"/avance_de_obra/linea_programada/"+obj.id+"/"+$("#id_proyecto").val(),'_blank');
            }

        }, path, parameter);
        
    }


    self.linea_avance=function(obj){

        path =path_principal+'/api/Cronograma/'+obj.id;
        parameter = '';
        RequestGet(function (results,count) {

           if(results.linea_base_terminada==false){

                $.confirm({
                    title:'Advertencia',
                    content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Debe guardar la linea base, para crear la linea de avance.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                 });
            }else{
                
                window.open(path_principal+"/avance_de_obra/linea_avance/"+obj.id+"/"+$("#id_proyecto").val(),'_blank');
            }

        }, path, parameter);
        
    }


    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/Cronograma/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Cronograma');

             self.cronogramaVO.id(results.id);
             self.cronogramaVO.nombre(results.nombre);
             self.cronogramaVO.fecha_inicio_cronograma(results.fecha_inicio_cronograma);
             self.cronogramaVO.periodicidad_id(results.periodicidad.id);
             self.cronogramaVO.intervalos(results.intervalos);
             self.cronogramaVO.esquema_id(results.esquema.id);
             self.validacion_intervalo(1);
             self.habilitar_campos(true);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }

     self.consultar_por_id_detalle = function (obj) {
       
      // alert(obj.id)

        
        path =path_principal+'/api/Cronograma/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
              self.titulo('Cronograma');

             self.cronogramaVO.id(results.id);
             self.cronogramaVO.nombre(results.nombre);
             self.cronogramaVO.fecha_inicio_cronograma(results.fecha_inicio_cronograma);
             self.cronogramaVO.periodicidad_id(results.periodicidad.id);
             self.cronogramaVO.intervalos(results.intervalos);
             self.cronogramaVO.esquema_id(results.esquema.id);
             if(results.estado!=null){
                self.cronogramaVO.estado_id(results.estado.estado);
             }
             self.cronogramaVO.esquema_id(results.esquema.id);
             self.habilitar_campos(false);
             self.validacion_intervalo(0);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }


    self.eliminar = function () {

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
             var path =path_principal+'/avance_de_obra/eliminar_id_cronograma/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los cronogramas seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }





 }

var cronograma = new CronogramaViewModel();

$('#txtBuscar').val(sessionStorage.getItem("dato_cronograma"));

cronograma.consultar(1);//iniciamos la primera funcion
cronograma.consultar_periodicidad();
CronogramaViewModel.errores_periodicidad = ko.validation.group(cronograma.periodicidadVO);
CronogramaViewModel.errores_cronograma = ko.validation.group(cronograma.cronogramaVO);
CronogramaViewModel.errores_busqueda = ko.validation.group(cronograma.busqueda);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(cronograma,content);
ko.applyBindings(cronograma,header);