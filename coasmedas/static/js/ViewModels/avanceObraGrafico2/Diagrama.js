function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   

    self.id_capitulo=ko.observable(0);
    self.id_actividad=ko.observable(0);
    self.listado_actividades=ko.observableArray([]);
    self.archivo_carga=ko.observable('');
    self.cierre_programacion=ko.observable(0);

    self.cronogramaVO = {
        id_cronograma: ko.observable(0)
    }

    self.diagramaVO={
        id:ko.observable(0),
        fechaInicio:ko.observable('').extend({ required: { message: '(*)Digite la fecha de inicio' } }),
        fechaFinal:ko.observable('').extend({ required: { message: '(*)Digite la fecha de final' } }),
        actividad_id:ko.observable('').extend({ required: { message: '(*)Seleccione la actividad' } }),
        actividad_inicial:ko.observable(false),
        cronograma_id:ko.observable($('#cronograma_id').val())
     };

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
        self.titulo('Registrar');
        $('#modal_acciones').modal('show');
    }

    self.abrir_carga_masiva = function () {
        self.limpiar();
        self.titulo('Carga masiva de Programación');
        $('#modal_acciones_carga_masiva').modal('show');
    }
     

    self.descargar_plantilla=function(){
        // $.confirm({
        //     title:'Informativo',
        //     content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Tenga en cuenta que en la columna D, debe señalar la actividad inicial con un "Si", para cargar la programación.<h4>',
        //     cancelButton: 'Cerrar',
        //     confirmButton: false
        // });
        location.href=path_principal+"/avanceObraGrafico2/descargar-plantilla-programacion?esquema_id="+$('#id_esquema').val();
    }

    self.guardar_carga_masiva=function(){

         if(self.archivo_carga()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar la programación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('cronograma_id',$('#id_cronograma').val());
            data.append('esquema_id',$('#id_esquema').val());
            data.append('archivo',self.archivo_carga());

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        //if (estado=='ok') {
                        self.consultar(1);
                        //}
                        $('#modal_acciones_carga_masiva').modal('hide');
                        $('#archivo').fileinput('reset');
                        $('#archivo').val('');
                        self.archivo_carga('');
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico2/guardar-programacion-archivo/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
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

    self.limpiar=function(){

        self.diagramaVO.id(0);
        self.id_capitulo(0);
        self.diagramaVO.fechaInicio('');
        self.diagramaVO.fechaFinal('');
        self.diagramaVO.actividad_id('');
        self.diagramaVO.actividad_inicial(false);
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
        
            if($('#programacion_cierre').val()=='True'){
                self.cierre_programacion(1);
            }
            let filtro_avance=sessionStorage.getItem("filtro_avance");

            path = path_principal+'/api/avanceGraficoD2iagramaGrahm/?format=json&page='+pagina;
            parameter = {dato: filtro_avance, pagina: pagina,cronograma_id:$('#cronograma_id').val()};
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


    self.id_capitulo.subscribe(function (value) {
            
             if(value!=0){
                path = path_principal+'/api/avanceGrafico2EsquemaCapitulosActividades/?sin_paginacion';
                parameter = {padre_id:value};
                RequestGet(function (datos, estado, mensage) {

                    self.listado_actividades(datos);
                }, path, parameter,function(){
                    self.diagramaVO.actividad_id(self.id_actividad());
                    // self.disenoVO.municipio_id(self.municipio());
                }
                );
            }else{
                self.listado_actividades([]);
            }

    });



    self.guardar=function(){

        if (IndexViewModel.errores_diagrama().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.diagramaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            //self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceGraficoD2iagramaGrahm/',//url api
                     parametros:self.diagramaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
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
                       url:path_principal+'/api/avanceGraficoD2iagramaGrahm/'+self.diagramaVO.id()+'/',
                       parametros:self.diagramaVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             IndexViewModel.errores_diagrama.showAllMessages();//mostramos las validacion
        }

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una actividad para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraGrafico2/eliminar_diagrama/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las actividades del diagrama seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }  

    }


     self.cerrar_programacion=function(){

            $.confirm({
                title: 'Cerrar Programacion!',
                content: "<h4>Esta seguro que desea cerrar la programacion? una vez cerrada no podrá modificar la programación de este cronograma.</h4>",
                confirmButton: 'Si',
                confirmButtonClass: 'btn-info',
                cancelButtonClass: 'btn-danger',
                cancelButton: 'No',
                confirm: function() {
                        self.cronogramaVO.id_cronograma($('#cronograma_id').val());
                        var parametros={     
                        metodo:'POST',                
                        callback:function(datos, estado, mensaje){

                                if (estado=='ok') {
                                    self.cierre_programacion(1);
                                }                        
                                
                             },//funcion para recibir la respuesta 
                             url:path_principal+'/avanceObraGrafico2/cierre_programacion/',//url api
                             parametros:{ id_cronograma: $('#cronograma_id').val() }
                             //parametros: self.cronogramaVO
                          };
                        Request(parametros);
                    
                }
            });

    }


     self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
        path =path_principal+'/api/avanceGraficoD2iagramaGrahm/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
           
             self.titulo('Actualizar Diagrama');

             self.diagramaVO.id(results.id);
             self.id_capitulo(results.actividad.padre);
             self.id_actividad(results.actividad.id);
             self.diagramaVO.fechaInicio(results.fechaInicio);
             self.diagramaVO.fechaFinal(results.fechaFinal);
             self.diagramaVO.fechaFinal(results.fechaFinal);
             self.diagramaVO.cronograma_id(results.cronograma.id);
             self.diagramaVO.actividad_inicial(results.actividad_inicial);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }



   self.exportar_excel=function(){

        location.href=path_principal+"/avanceObraGrafico2/informe_diagrama?cronograma_id="+$('#cronograma_id').val();

   }

   

 }



var index = new IndexViewModel();
IndexViewModel.errores_diagrama = ko.validation.group(index.diagramaVO);
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

