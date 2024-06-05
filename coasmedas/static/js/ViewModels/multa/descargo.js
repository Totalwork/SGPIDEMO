function SolicitudApelacionViewModel() {

	var self = this;
	self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.mensaje=ko.observable('');
    self.mensajePorAsignar=ko.observable('');
    self.conjunto_id =ko.observable('');
    
	self.url=path_principal+'/api/'; 
	self.listado = ko.observableArray([]);
    self.listado_mcontrato = ko.observableArray([]);
    self.listado_contratista = ko.observableArray([]);
    self.listado_solicitante = ko.observableArray([]);  
    self.listado_estado = ko.observableArray([]); 
    self.listado_correspondencia_soportes = ko.observableArray([]);


	self.checkall=ko.observable(false);

	self.solicitudApelacionVO={
	 	id:ko.observable(0),
	 	fecha:ko.observable('').extend({ required: { message: ' Indique la fecha.' } }),
	 	comentarios:ko.observable('').extend({ required: { message: ' Indique los comentarios.' } }),
	   	fecha_transacion:ko.observable(''),
        soporte:ko.observable('').extend({ required: { message: ' Seleccione un soporte.' } }),
        solicitud_id:ko.observable('').extend({ required: { message: ' Seleccione una solicitud.' } }),    
	};

    self.solicitudPronunciamientoVO={
        id:ko.observable(0),
        apelacion_id:ko.observable('').extend({ required: { message: ' Indique el descargo.' } }),
        comentarios:ko.observable('').extend({ required: { message: ' Indique los comentarios.' } }),
        fecha_transacion:ko.observable(''),
    };

    self.filtro_solicitudApelacionVO={
        mcontrato:ko.observable(''),
        estado:ko.observable(''),
        consecutivo:ko.observable(''), 
        desde:ko.observable(''), 
        hasta:ko.observable(''),
        numerocontrato:ko.observable(''),
        contratista_id:ko.observable(''),
        solicitante_id:ko.observable(''),
    };

    self.limpiar_pronunciamiento=function(){      
        self.solicitudPronunciamientoVO.id(0);
        self.solicitudPronunciamientoVO.apelacion_id(0);
        self.solicitudPronunciamientoVO.comentarios('');
        self.solicitudPronunciamientoVO.fecha_transacion('');  
        self.solicitudPronunciamientoVO.comentarios.isModified(false);   
     }

	// //limpiar el modelo 
     self.limpiar=function(){      
        self.solicitudApelacionVO.id(0);
        self.solicitudApelacionVO.fecha('');
        self.solicitudApelacionVO.comentarios('');
        self.solicitudApelacionVO.fecha_transacion('');  
        self.solicitudApelacionVO.soporte(''); 
        self.solicitudApelacionVO.solicitud_id(''); 
        self.solicitudApelacionVO.fecha.isModified(false);
        self.solicitudApelacionVO.comentarios.isModified(false);
        self.solicitudApelacionVO.soporte.isModified(false);   

        $('#soportes').fileinput('reset');
        $('#soportes').val('');    
     }

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
    self.paginacion.pagina_actual.subscribe(function (pagina) {       
       self.consultar(pagina);
    });

    self.abrir_modal = function (obj) {
        self.titulo('Presentar Descargo');
        $('#modal_acciones').modal('show');
        $('#soportes').fileinput('reset');
        $('#soportes').val('');
    } 

    self.abrir_modal_pronunciar = function (obj) {
        self.limpiar_pronunciamiento();
        self.solicitudPronunciamientoVO.apelacion_id(obj.id);
        self.titulo('Pronunciar Descargo');
        $('#modal_acciones').modal('show');
    }

    self.abrir_modal_busqueda = function (obj) {
        self.titulo('Consultar descargos');
        $('#modal_busqueda').modal('show');
    }

    self.abrir_modal_ver_pronunciamiento = function (obj) { 
        self.limpiar_pronunciamiento();    
        path =path_principal+'/api/MultaSolicitudPronunciamiento/';
        parameter = { apelacion : obj.id , ignorePagination : 1}
        RequestGet(function (results,count) {
            self.titulo('Ver pronunciamiento');
            $('#modal_acciones').modal('show');
            self.solicitudPronunciamientoVO.comentarios(results[0].comentarios);     
        }, path, parameter);
    }

    //exportar excel    
    self.exportar_excel=function(){
        location.href=self.url_funcion+"reporte_proyecto?dato="+self.filtro()+"&mcontrato="+self.mcontrato_id_filtro()+"&contratista="+self.contratista_id_filtro();
    } 
    self.consultar = function (pagina) {
        if (pagina > 0) {        
            self.filtro($('#txtBuscar').val());
            path = self.url+'MultaSolicitudApelacion/';
            parameter = { dato: self.filtro(), pagina: pagina 
                            , macro_contrato: self.filtro_solicitudApelacionVO.mcontrato()
                            , contratista: self.filtro_solicitudApelacionVO.contratista_id()
                            , numero_contrato_obra: self.filtro_solicitudApelacionVO.numerocontrato()
                            , solicitante: self.filtro_solicitudApelacionVO.solicitante_id()
                            , estado: self.filtro_solicitudApelacionVO.estado()
                            , desde: self.filtro_solicitudApelacionVO.desde()
                            , hasta: self.filtro_solicitudApelacionVO.hasta()
                        };
            RequestGet(function (datos, estado, mensage) {

                self.listado_estado(datos.data.estados_solicitudes); 
                self.listado_solicitante(datos.data.solicitantes);
                self.listado_mcontrato(datos.data.macro_contratos);

                if (estado == 'ok' && datos.data.descargos!=null && datos.data.descargos.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data.descargos)); 
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
                self.llenar_paginacion(datos,pagina);
            }, path, parameter);
        }
    }
    self.consultar_apelacion = function () {
            path = self.url+'MultaSolicitudApelacion/';
            parameter = { ignorePagination : 1 , solicitud : self.solicitudApelacionVO.solicitud_id() };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos));  

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
            }, path, parameter);
    }
    // //funcion guardar
     self.guardar=function(){

    	if (SolicitudApelacionViewModel.errores_descargo().length == 0) {//se activa las validaciones
            if(self.solicitudApelacionVO.id()==0){
                peticion = 'POST';
                url_peticion = self.url+'MultaSolicitudApelacion/';
            }else{       
                peticion = 'PUT'; 
                url_peticion = self.url+'MultaSolicitudApelacion/'+ self.solicitudApelacionVO.id()+'/';         
            }

            var parametros={     
                    metodo: peticion,                
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                          self.consultar_apelacion();
                          self.limpiar();
                          $('#modal_acciones').modal('hide');
                        } 
                    },//funcion para recibir la respuesta 
                    url: url_peticion,
                    parametros:self.solicitudApelacionVO                        
            };
            RequestFormData(parametros);
        } else {
            SolicitudApelacionViewModel.errores_descargo.showAllMessages();//mostramos las validacion
        }
     }

    self.guardar_pronunciamiento=function(){
        if (SolicitudApelacionViewModel.errores_pronuciamiento().length == 0) {//se activa las validaciones
            peticion = 'POST';
            url_peticion = self.url+'MultaSolicitudPronunciamiento/';
            
            var parametros={     
                metodo: peticion,                
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                      self.consultar(1);
                      self.limpiar_pronunciamiento();
                      $('#modal_acciones').modal('hide');
                    } 
                },//funcion para recibir la respuesta 
                url: url_peticion,
                parametros:self.solicitudPronunciamientoVO                        
            };
            RequestFormData(parametros);
        } else {
            SolicitudApelacionViewModel.errores_pronuciamiento.showAllMessages();//mostramos las validacion
        }
    }
    // consultar historial por id
    self.descargar_soporte_historial_por_id = function (id) {
      path =path_principal+'/api/MultaSolicitudHistorial/'+id+'/?format=json';
         RequestGet(function (results,count) {
            if (results.soporte){
                window.open(results.soporte,'_blank');
            }else{
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> No se han encontrado soportes.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }
            
            cerrarLoading();
         }, path, parameter,undefined,false);
     }  

    // soportes multa solicitada
    self.consultar_soportes_solicitadas = function (correspondencia_id) {
    
        path = path_principal+'/api/CorrespondenciaSoporte/';
        parameter = {  ignorePagination : 1 , correspondencia : correspondencia_id};
        RequestGet(function (datos, estado, mensage) {
            if (datos!=null && datos.length > 0) {
                if (datos[0].soporte){
                    window.open('/correspondencia/ver-soporte/?id=' + datos[0].id,'_blank');
                }else{
                    $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> No se han encontrado soportes.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });
                }
                
            }else{
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> No se han encontrado soportes.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }            
            cerrarLoading();
        }, path, parameter,undefined,false);       
    } 

    self.abrir_modal_soporte_ver_correspondencia = function (correspondencia_id ,consecutivo) {
        self.titulo('Soportes del Consecutivo No. '+consecutivo);
        self.consultar_soportes(correspondencia_id)
        $('#modal_acciones_soporte_ver').modal('show');
    }


    //funcion consultar soportes
    self.consultar_soportes = function (correspondencia_id) {
                  
            path = self.url+'CorrespondenciaSoporte/';
            parameter = {  ignorePagination : 1 , correspondencia : correspondencia_id , estado : 1 };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                     self.mensajePorAsignar('')
                    self.listado_correspondencia_soportes(agregarOpcionesObservable(datos));                        
                } else {
                    self.listado_correspondencia_soportes([]);   
                    self.mensajePorAsignar(mensajeNoFound)                    
                }                
                cerrarLoading();
            }, path, parameter,undefined,false);      
    }


}

var descargo = new SolicitudApelacionViewModel();
SolicitudApelacionViewModel.errores_descargo = ko.validation.group(descargo.solicitudApelacionVO);
SolicitudApelacionViewModel.errores_pronuciamiento = ko.validation.group(descargo.solicitudPronunciamientoVO);
ko.applyBindings(descargo);