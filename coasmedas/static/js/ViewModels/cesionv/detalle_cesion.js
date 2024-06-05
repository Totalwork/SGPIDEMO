
function DetalleCesionViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.contratista_encabezado=ko.observable('');
    self.soporte_solicitud_encabezado=ko.observable('');
    self.fecha_solicitud_encabezado=ko.observable('');
    self.evidencia_verificacion_encabezado=ko.observable('');
    self.aprobacion_encabezado=ko.observable('');
    self.checkall=ko.observable(false);
    self.correo_veri=ko.observable('');
    self.aprobacio_rech=ko.observable('');
    self.select_aprobar=ko.observable('');
    self.idcesion2=ko.observable(0);

     //paginacion de la cesion
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
        },
        totalRegistrosBuscados:ko.observable(0)
    }

    //paginacion
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina)
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }


        //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });

     //limpiar el modelo de la cesion
    self.limpiar=function(){     
         
        $('#archivo').fileinput('reset');
        $('#archivo').val(''); 

        $('#archivo2').fileinput('reset');
        $('#archivo2').val('');

        self.select_aprobar(0);     
    }


        //funcion para abri el modal verificacion
    self.cverificacion = function () {
        self.titulo('Correo de verificacion');
        self.limpiar();
        $('#modal_verificacion').modal('show');
    }


    //funcion para abri el modal aprobacion
    self.aprobacion = function () {
        self.titulo('Correo de verificacion');
        self.limpiar();
        $('#modal_aprobacion').modal('show');
    }

    //funcion consultar las cesiones 
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            

            path = path_principal+'/api/DetalleCesion?format=json';
            parameter = { page: pagina, idcesion:self.idcesion2()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data));  
                    cerrarLoading();

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter,undefined, false);
        }
    }


    //consultar encabezado del detalle de cesion
    self.encabezado_detalle=function(){

         path =path_principal+'/api/DetalleCesion/?sin_paginacion&format=json';
         parameter={ idcesion: self.idcesion2()};
         RequestGet(function (datos, estado, mensaje) {

                self.detalleCesionId
                self.contratista_encabezado(datos[0].cesion.contratista.nombre);
                self.soporte_solicitud_encabezado(datos[0].cesion.soporte_solicitud);
                self.fecha_solicitud_encabezado(datos[0].cesion.fecha_carta);
                self.evidencia_verificacion_encabezado(datos[0].correo_verificacion);
                self.aprobacion_encabezado(datos[0].carta_rechazo_aprobacion);

         }, path, parameter,undefined,false,false);

    }


    //para colocar verificacion de la solicitud
    self.verificar_solicitud=function(){

        var data = new FormData();

        if (self.correo_veri()=='') {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione el soporte.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false
        }

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los detalles de la solicitud.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{

            data.append('lista',ko.toJSON(lista_id));
            data.append('estado',148);
            data.append('cesion_id',self.idcesion2());
            data.append('archivo', $('#archivo')[0].files[0]);

            $.confirm({
                title: 'Confirmar!',
                content: "<h4>¿Esta seguro que desea cargar el archivo seleccionado?</h4>",
                confirmButton: 'Si',
                confirmButtonClass: 'btn-info',
                cancelButtonClass: 'btn-danger',
                cancelButton: 'No',
                confirm: function() {

                    var parametros={                     
                        callback:function(datos, estado, mensaje){

                            if (estado=='ok') {
                                self.encabezado_detalle();
                                self.consultar(self.paginacion.pagina_actual());
                                $('#modal_verificacion').modal('hide');
                                self.limpiar();
                            }                        
                                    
                        },//funcion para recibir la respuesta 
                            url:path_principal+'/cesion_v2/verificacion_correo/',//url api
                            parametros:data,
                            completado:function(){
                                //self.encabezado();
                            }                          
                    };
                    RequestFormData2(parametros);
                    
                }
            });
        } 


    }



    //para colocar aprobacion de la solicitud
    self.aprobacion_rechazo=function(){

        var data = new FormData();

        if (self.aprobacio_rech()=='') {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione el soporte.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false
        }

        if (self.select_aprobar()==0) {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione si aprueba o rechaza.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false
        }

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los detalles de la solicitud.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{

            data.append('lista',ko.toJSON(lista_id));
            data.append('estado',$("#aproba_recha").val());
            data.append('idcesion',self.idcesion2());
            data.append('archivo', $('#archivo2')[0].files[0]);

            $.confirm({
                title: 'Confirmar!',
                content: "<h4>Esta seguro que desea procesar de esta manera la solicitud?</h4>",
                confirmButton: 'Si',
                confirmButtonClass: 'btn-info',
                cancelButtonClass: 'btn-danger',
                cancelButton: 'No',
                confirm: function() {

                    var parametros={                     
                        callback:function(datos, estado, mensaje){

                            if (estado=='ok') {
                                self.encabezado_detalle();
                                self.consultar(self.paginacion.pagina_actual());
                                $('#modal_aprobacion').modal('hide');
                                self.limpiar();
                            }                        
                                    
                        },//funcion para recibir la respuesta 
                            url:path_principal+'/cesion_v2/aprobacion_rechazo/',//url api
                            parametros:data,
                            completado:function(){
                                //self.encabezado();
                            }                          
                    };
                    RequestFormData2(parametros);
                            
                }
            });
        }
    }




}

var detalle = new DetalleCesionViewModel();
ko.applyBindings(detalle);
