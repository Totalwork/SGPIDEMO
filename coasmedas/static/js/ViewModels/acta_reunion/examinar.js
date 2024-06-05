var mensajeNoConclusiones='<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>El acta no tiene conclusiones</div>';
var mensajeNoContrato = '<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>El acta no tiene contratos asociados</div>';
var mensajeNoProyecto = '<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>El acta no tiene proyectos asociados</div>';
var mensajeNoCompromisos = '<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>El acta no tiene compromisos asociados</div>';

function ActaViewModel() {

	var self = this;
	self.listado=ko.observableArray([]);
	self.mensajeActasPrevias=ko.observable('');
    self.mensajeActasPreviasCrear=ko.observable('');
    self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.listado_actasPrevias = ko.observable([]);
    self.listado_actasPreviasCrear = ko.observable([]);
    self.listado_contratos_asignados = ko.observable([]);
    self.listado_contratos_por_asignar = ko.observable([]);
    self.listado_proyectos_asignados = ko.observable([]);
    self.listado_proyectos_por_asignar = ko.observable([]);
    self.listado_actasHistorial = ko.observable([]); 
    self.listado_participantes= ko.observable([]); 
    self.listado_compromisos = ko.observable([]); 
    self.listado_responsable = ko.observable([]); 
    self.listado_compromisoHistorial = ko.observable([]);

    self.mensajecompromisoHistorial = ko.observable([]);
    self.mensajeContrato = ko.observable('');
    self.mensajeContratoSinDatos = ko.observable('');
    self.mensajePorAsignar = ko.observable('');
    self.mensajeAsignados = ko.observable('');
    self.mensajeProyecto = ko.observable('');
    self.mensajeActasHistorial = ko.observable('');
    self.mensajeProyectoSinDatos = ko.observable('');
    self.mensajePorAsignarProyecto = ko.observable('');
    self.mensajeAsignadosProyecto = ko.observable('');   
    self.mensajeConclusiones = ko.observable('');  
    self.mensajeAsistencia = ko.observable('');  
    self.mensajeCompromisos = ko.observable('');
    self.mensajeCompromisos2 = ko.observable('');  
    self.porcentaje = ko.observable(0); 

	self.url=path_principal+'/api/';
    self.id_acta = ko.observable('');
    self.url_funcion=path_principal+'/actareunion/'; 

    self.checkContrato = ko.observable(false);
    self.checkProyecto = ko.observable(false); 
    self.checkConclusiones = ko.observable(false); 
    self.checkCompromiso= ko.observable(false); 
    self.checkallContratosDisponibles = ko.observable(false);
    self.checkallContratosAsignados = ko.observable(false);
    self.checkallProyectosDisponibles = ko.observable(false);
    self.checkallProyectosAsignados = ko.observable(false);
    self.fecha_limite = ko.observable();
    self.fecha_proximidad = ko.observable();
    self.cancelarCompromiso = {
        id: ko.observable(0),
        motivo: ko.observable(''),
    };

    self.actaVO ={
    	id:ko.observable($('#acta_id').val()),
    	consecutivo:ko.observable(''),
    	controlador_actual_id:ko.observable(''),
    	controlador_actual_nombre:ko.observable(''),
        conclusiones:ko.observable(''),

    	estado_id:ko.observable(''),
    	estado_nombre:ko.observable(''),
    	estado_color:ko.observable(''),
    	estado_icono:ko.observable(''),
    	
    	soporte:ko.observable(''),
    	tiene_contrato:ko.observable(false),
		tiene_proyecto:ko.observable(false),
		tiene_conclusiones:ko.observable(false),
		tiene_compromisos:ko.observable(false),
    };

    self.compromisoVO ={
        id:ko.observable(0),
        acta_id:ko.observable($('#acta_id').val()),
        
        descripcion:ko.observable('').extend({ required: { message: ' Ingrese una descripcion' } }),
        fecha_compromiso:ko.observable('').extend({ required: { message: ' Ingrese una fecha.' } }),
        fecha_proximidad:ko.observable('').extend({ required: { message: ' Ingrese una fecha de proximidad.' } }),
        
        responsable_id:ko.observable('').extend({ required: { message: ' Seleccione un responsable' } }),
        supervisor_id:ko.observable('').extend({ required: { message: ' Seleccione un supervisor' } }),

        responsable_interno:ko.observable(false),
        requiere_soporte:ko.observable(false),  

        participante_responsable_id:ko.observable(''),
        usuario_responsable_id:ko.observable(''),

        notificar_organizador:ko.observable(false),
        notificar_controlador:ko.observable(false),

    };


    self.reasignacioncompromisoVO ={
        id:ko.observable(0),
     
        
        motivo:ko.observable('').extend({ required: { message: ' Ingrese un motivo' } }),
        
        responsable_id:ko.observable('').extend({ required: { message: ' Seleccione un responsable' } }),
        responsable_interno:ko.observable(false),

        supervisor_id:ko.observable(''),

    };


    self.filtro_acta_compromisoVO = {        
        acta_id:ko.observable($('#acta_id').val()),        
        descripcion:ko.observable(''),
        desde:ko.observable(''),
        hasta:ko.observable(''),
        supervisor_id:ko.observable(''),
        responsable_id:ko.observable(false),
        prorroga:ko.observable(false)
    }

    self.cumplimientoVO = {
        id:ko.observable(0),
        requiere_soporte:ko.observable(''),
        motivo:ko.observable(''),
        soporte:ko.observable(''),

    };

    self.prorrogacompromisoVO = {
        id:ko.observable(0),
        fecha:ko.observable('').extend({ required: { message: ' Ingrese una fecha.' } }),
        fecha_proximidad:ko.observable('').extend({ required: { message: ' Ingrese una fecha de proximidad.' } }),
        motivo:ko.observable('').extend({ required: { message: ' Ingrese un motivo.' } }),
    };

    self.actaPrevia = {
        consecutivo:ko.observable('').extend({ required: { message: ' Ingrese un consecutivo.' } }),
    }

    self.paginacionActaPrevia = {
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

    self.paginacionContratosDisponibles = {
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

    self.paginacionContratosAsignados = {
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
    
    self.paginacionProyectosDisponibles = {
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

    self.paginacionProyectosAsignados = {
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
    
    self.paginacionHistorial = {
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
    
    self.paginacionParticipantes = {
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
    
    self.paginacionConclusiones = {
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
    
    self.paginacionCompromisos = {
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

    self.anulacionactaVO={
    	id:ko.observable($('#acta_id').val()),
    	motivo:ko.observable('').extend({ required: { message: ' Ingrese un motivo para la anulación' } }),
    }

    self.cerraractaVO={
    	id:ko.observable($('#acta_id').val()),
    	motivo:ko.observable(''),
    }

    
    self.transferenciaactaVO={
    	id:ko.observable($('#acta_id').val()),
    	motivo:ko.observable('').extend({ required: { message: ' Ingrese un motivo para la transferencia' } }),
    }

    self.consultar_acta = function (sin_tiene_conlcusiones){
    	path = path_principal + '/api/actareunion-acta/'+self.actaVO.id()+'/?format=json';
        parameter = {
        	lite:1,
        };
        RequestGet(function(datos,mensaje,estado) {
          	
            if(datos!=null){
            	
            	self.actaVO.controlador_actual_id(datos.controlador_actual.id);
            	self.actaVO.controlador_actual_nombre(datos.controlador_actual.persona.nombres+' '+datos.controlador_actual.persona.apellidos)
                
                self.actaVO.estado_id(datos.estado.id);
                self.actaVO.estado_nombre(datos.estado.nombre);
                self.actaVO.estado_color(datos.estado.color);
                self.actaVO.estado_icono(datos.estado.icono);

                self.actaVO.conclusiones(datos.conclusiones);

                self.actaVO.tiene_contrato(datos.tiene_contrato);
                //alert(self.actaVO.tiene_contrato());
                self.actaVO.tiene_proyecto(datos.tiene_proyecto);
                //alert(self.actaVO.tiene_proyecto());
                
                self.actaVO.tiene_compromisos(datos.tiene_compromisos);

                if(sin_tiene_conlcusiones==undefined){
                    self.actaVO.tiene_conclusiones(datos.tiene_conclusiones);
                }

                if(datos.soporte==null || datos.soporte==''){                
                    $('#detalle_soporte_archivo').hide();                   
                }else{
                    $('#detalle_soporte_archivo').show();
                }

                self.actaVO.consecutivo(datos.consecutivo);

                self.checkContrato(true);
                self.checkProyecto(true);
                self.checkConclusiones(true);
                self.checkCompromiso(true);
                //alert(self.actaVO.tiene_compromisos());
            }else{                
                mensajeError(mensaje);
            }            
            cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.ver_soporte = function(acta_id){
    
        window.open(path_principal+"/actareunion/ver-soporte-acta/?id="+ self.actaVO.id(), "_blank");
       
    }


    self.transferircontrol_acta = function(acta_id){
    	self.titulo('Transferir control del acta No. '+self.actaVO.consecutivo());
        $('#modal_transferir_acta').modal('show');
    }

    self.transferir = function(){
        if (ActaViewModel.errores_transferencia().length == 0 ) {
            var path =path_principal+'/actareunion/transferir-acta/';
            var parameter = {
                acta_id:self.transferenciaactaVO.id(),
                controlador_id:self.actaVO.controlador_actual_id(),
                motivo:self.transferenciaactaVO.motivo(),
            };
            RequestAnularOEliminar("Desea transferir el control del acta No. "+self.actaVO.consecutivo()+"?", path, parameter, 
                function(datos, estado, mensaje){
                    if (estado=='ok') {
                        $('#modal_transferir_acta').modal('hide');
                        self.consultar_acta();
                        self.consultar_historial(1);
                        self.consultar_compromisos(self.paginacionCompromisos.pagina_actual());
                        self.transferenciaactaVO.motivo('');
                        self.transferenciaactaVO.motivo.isModified(false);
                    }
            
            });
    
        }else{
            ActaViewModel.errores_transferencia.showAllMessages();
        }
    }

	self.anular_acta = function(){
		$.confirm({
            title:'Informativo',
            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Desea anular el acta No. '+self.actaVO.consecutivo()+'?<h4>',
            cancelButton: 'No',
            confirmButton: 'Si',
            confirm: function() {
            	self.titulo('Anulación del acta No. '+self.actaVO.consecutivo());
            	$('#modal_anular_acta').modal('show');
            }
        });
	}	

	self.anular =function(){
		if (ActaViewModel.errores_acta_anulacion().length == 0 ) {
			var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            $('#modal_anular_acta').modal('hide');
                            self.consultar_acta();
                            self.consultar_historial(1);                  
                            mensajeExitoso(mensaje);                            
                        }else{
                            $('#modal_anular_acta').modal('hide');
                            mensajeError(mensaje);                            
                        }
                        self.anulacionactaVO.motivo('');
                        self.anulacionactaVO.motivo.isModified(false);

                     },//funcion para recibir la respuesta 
                     alerta:false,
                     url:path_principal+'/actareunion/anularActa/',//url api
                     parametros:{
                        acta_id:self.anulacionactaVO.id(),
                        motivo_anular:self.anulacionactaVO.motivo(),
                    }                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
		}else{
             ActaViewModel.errores_acta_anulacion.showAllMessages();
        }
	}

    self.cerrar_acta_modal = function(){
        self.cerraractaVO.motivo('');
        self.titulo('Cerrar acta No. '+self.actaVO.consecutivo());
        $('#modal_cerrar_acta').modal('show');
	}

	self.cerrar_acta = function(){
        if (ActaViewModel.errores_cerrar().length == 0 ) {
            var path =path_principal+'/actareunion/cerrar-acta/';
            var parameter = {acta_id:self.actaVO.id(),motivo:self.cerraractaVO.motivo()};
            RequestAnularOEliminar("Está seguro que desea cerrar el acta?", path, parameter, 
                function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.consultar_acta();
                        self.consultar_historial(1);
                        $('#modal_cerrar_acta').modal('hide'); 
                    }else{
                         mensajeError(mensaje);
                    }
            
            });
        }else{
            ActaViewModel.errores_cerrar.showAllMessages();
        }
	}

	self.abrir_modal_soporte= function(){
		$('#modal_soporte').modal('show');
		self.titulo('Subir soporte el Acta No.'+self.actaVO.consecutivo())
	}

	self.subir_soporte= function(){
		if(self.actaVO.soporte()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un soporte para cargar a SININ.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{			

			var parametros={                     
	                 callback:function(datos, estado, mensaje){
                        self.consultar_porcentaje();
                        self.consultar_acta();
                        
	                    $('#modal_soporte').modal('hide');
	                    $('#archivo').fileinput('reset');
	                    $('#archivo').val('');
	                    self.actaVO.soporte('');
                        
	                    
	                 },//funcion para recibir la respuesta 
	                 url:path_principal+'/actareunion/subirsoporte-acta/',//url api
	                 parametros:self.actaVO                       
	            };
	            //parameter =ko.toJSON(self.contratistaVO);
	        RequestFormData(parametros);
	    }
	}

    self.exportar_excel = function(){                                                                                                                                                 
                           
    } 
    
    self.abrir_modal_actas_previas = function (){
        self.titulo('Registrar Acta Previa');
        $('#modal_actas_previas').modal('show');
    }    

    self.paginacionActaPrevia.pagina_actual.subscribe(function (pagina) {    
       self.cargar_actas_previas(pagina,0);
    });

    self.paginacionContratosDisponibles.pagina_actual.subscribe(function (pagina) {    
        self.consultar_contratos_disponibles(pagina);
     });

     self.paginacionContratosAsignados.pagina_actual.subscribe(function (pagina) {    
        self.consultar_contratos_disponibles(pagina);
     });     
     
     self.paginacionProyectosAsignados.pagina_actual.subscribe(function (pagina) {    
        self.consultar_proyectos_asignados(pagina);
     });

     self.paginacionProyectosDisponibles.pagina_actual.subscribe(function (pagina) {    
        self.consultar_proyectos_disponibles(pagina);
     });     
     
     self.paginacionHistorial.pagina_actual.subscribe(function (pagina) {    
        self.consultar(pagina);
     });
     
     self.paginacionParticipantes.pagina_actual.subscribe(function (pagina) {    
        self.consultar(pagina);
     });     

     self.paginacionConclusiones.pagina_actual.subscribe(function (pagina) {    
        self.consultar(pagina);
     });

     self.paginacionCompromisos.pagina_actual.subscribe(function (pagina) {    
        self.consultar_compromisos(pagina);
     });


    self.consultar_contratos_disponibles = function (pagina){
	    if(pagina>0){

	        path = path_principal + '/api/actareunion-acta/?format=json';        
	        parameter = {
	        	page:pagina,
	        	ListcontratosDisponibles:1,
                id: self.actaVO.id(),
                datoContratoDisponible: $('#txtContratosDisponibles').val()
	        };
	        RequestGet(function(datos,estado,mensaje) {      
	    		if(estado=='ok' && datos.data!=null && datos.data.length>0){    			
	    			self.listado_contratos_por_asignar(agregarOpcionesObservable(datos.data));
	    			self.mensajePorAsignar('');
		        }else{
		        	self.mensajePorAsignar(mensajeNoFound);
		        	self.listado_contratos_por_asignar([]);
		        }                
		        self.llenar_paginacionContratosDisponibles(datos,pagina);
	    		cerrarLoading();
	        }, path, parameter,undefined,false);
	    }      
    }

    self.consultar_contratos_asignados = function (pagina){
	    if(pagina>0){

	        path = path_principal + '/api/actareunion-acta/?format=json';        
	        parameter = {
	        	page:pagina,
	        	ListcontratosAsignados:1,
                id: self.actaVO.id(),
                datoContratoAsignado: $('#txtContratosAsignados').val()
	        };
	        RequestGet(function(datos,estado,mensaje) {      
	    		if(estado=='ok' && datos.data!=null && datos.data.length>0){    			
	    			self.listado_contratos_asignados(agregarOpcionesObservable(datos.data));
	    			self.mensajeAsignados('');
		        }else{
		        	self.mensajeAsignados(mensajeNoFound);
		        	self.listado_contratos_asignados([]);
		        }                
		        self.llenar_paginacionContratosAsignados(datos,pagina);
	    		cerrarLoading();
	        }, path, parameter,undefined,false);
	    }
    }    
    
    self.consultar_contratos_disponibles_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_contratos_disponibles(1)
        }
        return true;
    }

    self.consultar_contratos_asignados_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_contratos_asignados(1)
        }
        return true;
    } 
    
    self.consultar_proyectos_disponibles = function (pagina){
	    if(pagina>0){

	        path = path_principal + '/api/actareunion-acta/?format=json';        
	        parameter = {
	        	page:pagina,
	        	ListproyectosDisponibles:1,
                id: self.actaVO.id(),
                datoProyectoDisponible: $('#txtproyectosDisponibles').val()
	        };
	        RequestGet(function(datos,estado,mensaje) {      
	    		if(estado=='ok' && datos.data!=null && datos.data.length>0){    			
	    			self.listado_proyectos_por_asignar(agregarOpcionesObservable(datos.data));
	    			self.mensajePorAsignarProyecto('');
		        }else{
		        	self.mensajePorAsignarProyecto(mensajeNoFound);
		        	self.listado_proyectos_por_asignar([]);
		        }                
		        self.llenar_paginacionProyectosDisponibles(datos,pagina);
	    		cerrarLoading();
	        }, path, parameter,undefined,false);
	    }      
    }

    self.consultar_proyectos_asignados = function (pagina){
	    if(pagina>0){

	        path = path_principal + '/api/actareunion-acta/?format=json';        
	        parameter = {
	        	page:pagina,
	        	ListproyectosAsignados:1,
                id: self.actaVO.id(),
                datoProyectoAsignado: $('#txtproyectosAsignados').val()
	        };
	        RequestGet(function(datos,estado,mensaje) {      
	    		if(estado=='ok' && datos.data!=null && datos.data.length>0){    			
	    			self.listado_proyectos_asignados(agregarOpcionesObservable(datos.data));
	    			self.mensajeAsignadosProyecto('');
		        }else{
		        	self.mensajeAsignadosProyecto(mensajeNoFound);
		        	self.listado_proyectos_asignados([]);
		        }                
		        self.llenar_paginacionProyectosAsignados(datos,pagina);
	    		cerrarLoading();
	        }, path, parameter,undefined,false);
	    }
    }    
    
    self.consultar_proyectos_disponibles_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_contratos_disponibles(1)
        }
        return true;
    }

    self.consultar_proyectos_asignados_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_contratos_asignados(1)
        }
        return true;
    }     

    self.consultar_actas_previas_btn = function (){
        self.cargar_actas_previas(1,1)
    }
    
    self.consultar_actas_previas_enter = function (d,e) {
        if (e.which == 13) {
            self.cargar_actas_previas(1,1)
        }
        return true;
    }

    self.consultar_contratos_disponibles_btn = function (){
        self.consultar_contratos_disponibles(1)
    }    

    self.consultar_contratos_asignados_btn = function (){
        self.consultar_contratos_asignados(1)
    }        

    self.consultar_proyectos_disponibles_btn = function (){
        self.consultar_proyectos_disponibles(1)
    }    

    self.consultar_proyectos_asignados_btn = function (){
        self.consultar_proyectos_asignados(1)
    }            

    self.cargar_actas_previas = function (pagina,listActasPrevias){
	    if(pagina>0){
	        path = path_principal + '/api/actareunion-acta/?format=json';
	        if (listActasPrevias == 1){
                parameter = {
                    id : $('#acta_id').val(),
                    acta_previa : 1,
                    listActasPrevias: 1,
                    datoBusqueda: $('#txtBuscarActas').val()
                };
                RequestGet(function(datos,estado,mensaje) {      
                    if(estado=='ok' && datos.length>0){    			
                        self.listado_actasPreviasCrear(datos);
                        self.mensajeActasPreviasCrear('');
                    }else{
                        self.mensajeActasPreviasCrear(mensajeNoFound);
                        self.listado_actasPreviasCrear([]);
                    }                    
                    self.llenar_paginacionActasPrevias(datos,pagina);
                    cerrarLoading();
                }, path, parameter,undefined,false);  

            }else{

                parameter = {
                    id : $('#acta_id').val(),
                    acta_previa : 1                    
                };
                RequestGet(function(datos,estado,mensaje) {      
                    if(estado=='ok' && datos.data!=null && datos.data.length>0){    			
                        self.listado_actasPrevias(datos.data);
                        self.mensajeActasPrevias('');
                    }else{
                        self.mensajeActasPrevias(mensajeNoFound);
                        self.listado_actasPrevias([]);
                    }                    
                    self.llenar_paginacionActasPrevias(datos,pagina);
                    cerrarLoading();
                }, path, parameter,undefined,false);                
            }
	        
	    }
    }    
    
    self.guardar_contratos=function(obj){ 
        self.proyecto_responsableVO.funcionario_id([]);           
        ko.utils.arrayForEach(self.listado_responsables_tabla(),function(p){
            if (p.procesar()) {
                self.proyecto_responsableVO.funcionario_id.push(p.id);
            };
        });
   
        var parametros={                     
             callback:function(datos, estado, mensaje){
                if (estado=='ok') {
                    self.consultar_responsables(self.proyecto_responsableVO.proyecto_id())                      
                    self.consultar_responsables_proyecto(self.proyecto_responsableVO.proyecto_id());
                    // self.checkallResponsables(false);
                }                     
             },//funcion para recibir la respuesta 
             url: self.url_funcion+'create_proyecto_funcionario/',//url api
             parametros: self.proyecto_responsableVO                         
        };
        RequestFormData(parametros);            
    }

    self.llenar_paginacionContratosAsignados = function (data,pagina) {

        self.paginacionContratosAsignados.pagina_actual(pagina);
        self.paginacionContratosAsignados.total(data.count);       
        self.paginacionContratosAsignados.cantidad_por_paginas(resultadosPorPagina);
    }

    self.llenar_paginacionContratosDisponibles = function (data,pagina) {

        self.paginacionContratosDisponibles.pagina_actual(pagina);
        self.paginacionContratosDisponibles.total(data.count);       
        self.paginacionContratosDisponibles.cantidad_por_paginas(resultadosPorPagina);
    }
    
    self.llenar_paginacionActasPrevias = function (data,pagina) {

        self.paginacionActaPrevia.pagina_actual(pagina);
        self.paginacionActaPrevia.total(data.count);       
        self.paginacionActaPrevia.cantidad_por_paginas(resultadosPorPagina);
    }
    
    self.llenar_paginacionProyectosDisponibles = function (data,pagina) {

        self.paginacionProyectosDisponibles.pagina_actual(pagina);
        self.paginacionProyectosDisponibles.total(data.count);       
        self.paginacionProyectosDisponibles.cantidad_por_paginas(resultadosPorPagina);
    }

    self.llenar_paginacionProyectosAsignados = function (data,pagina) {

        self.paginacionProyectosAsignados.pagina_actual(pagina);
        self.paginacionProyectosAsignados.total(data.count);       
        self.paginacionProyectosAsignados.cantidad_por_paginas(resultadosPorPagina);
    }    
    
    self.llenar_paginacionHistorial = function (data,pagina) {

        self.paginacionHistorial.pagina_actual(pagina);
        self.paginacionHistorial.total(data.count);       
        self.paginacionHistorial.cantidad_por_paginas(resultadosPorPagina);
    }
    
    self.llenar_paginacionParticipantes = function (data,pagina) {

        self.paginacionParticipantes.pagina_actual(pagina);
        self.paginacionParticipantes.total(data.count);       
        self.paginacionParticipantes.cantidad_por_paginas(resultadosPorPagina);
    }
    
    self.llenar_paginacionCompromisos = function (data,pagina) {

        self.paginacionCompromisos.pagina_actual(pagina);
        self.paginacionCompromisos.total(data.count);       
        self.paginacionCompromisos.cantidad_por_paginas(resultadosPorPagina);
    }    
    
    self.guardar_acta_previa = function (){        
        if(self.id_acta()!=''){
            var parametros={
                metodo:'PUT',
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {                        
                        self.cargar_actas_previas(1,0);                        
                        $('#modal_actas_previas').modal('hide');                        
                    }else{
                        mensajeError(mensaje);
                    }
                    cerrarLoading();
                }, //funcion para recibir la respuesta 
                url:path_principal+'/api/actareunion-acta/'+self.actaVO.id()+'/',//url api
                parametros:{id_acta_previa: self.id_acta},
            };
            RequestFormData(parametros);        
        }else{
            mensajeInformativo('Se debe de seleccionar una acta previa.');
        }      
    }

    self.ver_examinar_acta = function (id_acta){
        location.href=path_principal+"/actareunion/acta-examinar/"+id_acta;
    }
    
    self.checkallContratosDisponibles.subscribe(function(value){
		ko.utils.arrayForEach(self.listado_contratos_por_asignar(), function(d) {
			d.eliminado(value);
		});        
    });

    self.checkallContratosAsignados.subscribe(function(value){
		ko.utils.arrayForEach(self.listado_contratos_asignados(), function(d) {
			d.eliminado(value);
		});        
    });
    
    self.checkallProyectosAsignados.subscribe(function(value){
		ko.utils.arrayForEach(self.listado_proyectos_asignados(), function(d) {
			d.eliminado(value);
		});        
    });    

    self.checkallProyectosDisponibles.subscribe(function(value){
		ko.utils.arrayForEach(self.listado_proyectos_por_asignar(), function(d) {
			d.eliminado(value);
		});        
    });        

	self.asignar_contrato = function () {
		var lista_id=[];
		var count=0;
		ko.utils.arrayForEach(self.listado_contratos_por_asignar(), function(d) {
			if(d.eliminado()==true){
				count=1;				
				lista_id.push({id:d.id})
			}
		});
		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contrato para asignar.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else{
			var path =path_principal+'/actareunion/asignar-contrato-acta/';
			var parameter = { lista: lista_id, id:self.actaVO.id()};
			RequestAnularOEliminar("Esta seguro que desea asignar los contratos seleccionados?", path, parameter, function () {
				//self.list_proyecto();
				self.consultar_contratos_disponibles(1);
                self.consultar_contratos_asignados(1);
				self.checkallContratosDisponibles(false);
                self.consultar_porcentaje();
			})
		}
	}

	self.desasignar_contrato = function () {
		var lista_id=[];
		var count=0;
		ko.utils.arrayForEach(self.listado_contratos_asignados(), function(d) {
			if(d.eliminado()==true){
				count=1;				
				lista_id.push({id:d.id})
			}
		});
		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contrato para asignar.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else{
			var path =path_principal+'/actareunion/desasignar-contrato-acta/';
			var parameter = { lista: lista_id, id:self.actaVO.id()};
			RequestAnularOEliminar("Esta seguro que desea desasignar los contratos seleccionados?", path, parameter, function () {
				//self.list_proyecto();
				self.consultar_contratos_disponibles(1);
                self.consultar_contratos_asignados(1);
				self.checkallContratosAsignados(false);
                self.consultar_porcentaje();
			})
		}
	}
    
	self.asignar_proyecto = function () {
		var lista_id=[];
		var count=0;
		ko.utils.arrayForEach(self.listado_proyectos_por_asignar(), function(d) {
			if(d.eliminado()==true){
				count=1;				
				lista_id.push({id:d.id})
			}
		});
		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contrato para asignar.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else{
			var path =path_principal+'/actareunion/asignar-proyecto-acta/';
			var parameter = { lista: lista_id, id:self.actaVO.id()};
			RequestAnularOEliminar("Esta seguro que desea asignar los proyectos seleccionados?", path, parameter, function () {
				//self.list_proyecto();
				self.consultar_proyectos_disponibles(1);
                self.consultar_proyectos_asignados(1);
				self.checkallProyectosDisponibles(false);
                self.consultar_porcentaje();
			})
		}
	}

	self.desasignar_proyecto = function () {
		var lista_id=[];
		var count=0;
		ko.utils.arrayForEach(self.listado_proyectos_asignados(), function(d) {
			if(d.eliminado()==true){
				count=1;				
				lista_id.push({id:d.id})
			}
		});
		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contrato para asignar.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else{
			var path =path_principal+'/actareunion/desasignar-proyecto-acta/';
			var parameter = { lista: lista_id, id:self.actaVO.id()};
			RequestAnularOEliminar("Esta seguro que desea desasignar los proyectos seleccionados?", path, parameter, function () {
				//self.list_proyecto();
				self.consultar_proyectos_disponibles(1);
                self.consultar_proyectos_asignados(1);
				self.checkallProyectosAsignados(false);
                self.consultar_porcentaje();
			})
		}
	}
    
    self.consultar_historial = function(pagina){
	    if(pagina>0){
	        path = path_principal + '/api/actareunion-actahistorial/?format=json';        
	        parameter = {
	        	page:pagina,	        	
                acta_id: self.actaVO.id() ,
                lite:1,             
	        };
	        RequestGet(function(datos,estado,mensaje) {      
	    		if(estado=='ok' && datos.data!=null && datos.data.length>0){    			
	    			self.listado_actasHistorial(agregarOpcionesObservable(datos.data));
	    			self.mensajeActasHistorial('');
		        }else{
		        	self.mensajeActasHistorial(mensajeNoFound);
		        	self.listado_actasHistorial([]);
		        }                
		        self.llenar_paginacionHistorial(datos,pagina);
	    		cerrarLoading();
	        }, path, parameter,undefined,false);
	    }      

    }

    
    

    self.guardar_conclusiones=function(){
        if(self.actaVO.conclusiones()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Digite las conclusiones del acta No.'+self.actaVO.consecutivo()+'<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{          

            var parametros={                     
                     callback:function(datos, estado, mensaje){
                        self.consultar_porcentaje();
                        self.consultar_acta(true);                        
                                                
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/actareunion/subirconclusiones-acta/',//url api
                     parametros:self.actaVO                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData(parametros);
        }
    }

    self.consultar_participantes = function(){
        path = path_principal + '/actareunion/obtener-participantes/';
        parameter = {
            acta_id: self.actaVO.id(),
        }
        RequestGet(function(datos,estado,mensaje) {
            if(estado=='ok' && datos!=null && datos.length>0){
                self.listado_participantes(agregarOpcionesObservable(datos));
                self.mensajeAsistencia('');
                  
            }else{
                self.mensaje_participantes(mensajeNoFound);
                self.mensajeAsistencia([]);
            }

            
            cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.guardar_asistencia = function(){
         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_participantes(), function(d) {                
                lista_id.push({
                    id:d.id,
                    tipo:d.tipo,
                    asistio:d.asistio,
                })
              
         });
         
         var path =path_principal+'/actareunion/asistencia-acta/';
         var parameter = { lista: lista_id };
         RequestAnularOEliminar("Esta seguro que desea guardar los cambios en la asistencia?", path, parameter, function () {
             self.consultar_participantes();
         })

      
    }

    self.actaVO.tiene_contrato.subscribe(function (val) {
        if (self.checkContrato()==true) {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Está seguro que quiere asociar/desasociar el acta con contratos? <br> (En caso de tener contratos asociados, estos se veran afectados)<h4>',
                cancelButton: 'No',
                confirmButton: 'Si',
                confirm: function() {
                    self.guardar_cambios_boolean('tiene_contrato',val);
                    self.checkContrato(true);
                    
                },
                cancel: function(){
                    self.checkContrato(false);
                    if(val==true){
                        self.actaVO.tiene_contrato(false);
                        
                    }else{
                        if(val==false){
                            self.actaVO.tiene_contrato(true);
                        }
                    } 
                    
                    
                }
            });

        }else{
            self.checkContrato(true);
            if(val){            
                self.consultar_contratos_disponibles(1);
                self.consultar_contratos_asignados(1);            
                $('#panel_contratos').show();
                $('#mensajeContrato').hide();       

            }else{            
                $('#panel_contratos').hide();
                $('#mensajeContrato').show();
            }
        }
        


    });

    self.actaVO.tiene_proyecto.subscribe(function (val) {

        if (self.checkProyecto()==true) {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Está seguro que quiere asociar/desasociar el acta con proyectos? <br> (En caso de tener proyectos asociados, estos se veran afectados)<h4>',
                cancelButton: 'No',
                confirmButton: 'Si',
                confirm: function() {
                    self.guardar_cambios_boolean('tiene_proyecto',val);
                    self.checkProyecto(true);
                    
                },
                cancel: function(){
                    self.checkProyecto(false);
                    if(val==true){
                        self.actaVO.tiene_proyecto(false);
                        
                    }else{
                        if(val==false){
                            self.actaVO.tiene_proyecto(true);
                        }
                    } 
                    
                    
                }
            });

        }else{
            self.checkProyecto(true);
            if(val){            
                self.consultar_proyectos_disponibles(1);
                self.consultar_proyectos_asignados(1);            
                $('#panel_proyectos').show();
                $('#mensajeProyecto').hide();              
                //self.mensajeContrato('');

            }else{            
                $('#panel_proyectos').hide();
                $('#mensajeProyecto').show();
            }
        }
        
    }); 

    self.actaVO.tiene_conclusiones.subscribe(function (val) {

        if (self.checkConclusiones()==true) {
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Está seguro que quiere asociar/desasociar conclusiones para el acta? <h4>',
                cancelButton: 'No',
                confirmButton: 'Si',
                confirm: function() {
                    self.guardar_cambios_boolean('tiene_conclusiones',val);
                    self.checkConclusiones(true);
                    
                },
                cancel: function(){
                    self.checkConclusiones(false);
                    if(val==true){
                        self.actaVO.tiene_conclusiones(false);
                        
                    }else{
                        if(val==false){
                            self.actaVO.tiene_conclusiones(true);
                        }
                    } 
                    
                    
                }
            });

        }else{
            self.checkConclusiones(true);
            if(val){                
                self.consultar_acta(true);
                $('#mensajeConclusiones').hide(); 
                $('#panel_conclusiones').show();
            }else{            
                $('#mensajeConclusiones').show();
                $('#panel_conclusiones').hide();
            }
           
        }

        
    });


    self.actaVO.tiene_compromisos.subscribe(function (val) { 
        if (self.checkCompromiso()==true) {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Está seguro que quiere asociar/desasociar compromisos para el acta? <br> (En caso de tener compromisos asociados, estos pueden llegar a cancelarse) <h4>',
                cancelButton: 'No',
                confirmButton: 'Si',
                confirm: function() {
                    self.guardar_cambios_boolean('tiene_compromisos',val);
                    self.checkCompromiso(true);
                    

                },
                cancel: function(){
                    self.checkCompromiso(false);
                    if(val==true){
                        self.actaVO.tiene_compromisos(false);
                        
                    }else{
                        if(val==false){
                            self.actaVO.tiene_compromisos(true);
                        }
                    } 
                    
                    
                }
            });

        }else{
            self.checkCompromiso(true);

        } 

    });

    self.guardar_cambios_boolean= function(boolean,value){
        var parametros={                     
                callback:function(datos, estado, mensaje){   
                    self.consultar_porcentaje();
                    if(boolean=='tiene_compromisos'){
                        self.consultar_compromisos(1);

                    }else if(boolean=='tiene_contrato'){
                        if(value){
                            self.consultar_contratos_disponibles(1);
                            self.consultar_contratos_asignados(1);            
                            $('#panel_contratos').show();
                            $('#mensajeContrato').hide();   

                        }else{
                            $('#panel_contratos').hide();
                            $('#mensajeContrato').show();
                        }

                    }else if (boolean=='tiene_proyecto'){
                        if(value){
                            self.consultar_proyectos_disponibles(1);
                            self.consultar_proyectos_asignados(1);            
                            $('#panel_proyectos').show();
                            $('#mensajeProyecto').hide();       

                        }else{
                            $('#panel_proyectos').hide();
                            $('#mensajeProyecto').show();
                        }

                    }else if (boolean=='tiene_conclusiones') {
                        if(value){
                            self.consultar_acta(true);
                            $('#mensajeConclusiones').hide(); 
                            $('#panel_conclusiones').show();
                        }else{            
                            $('#mensajeConclusiones').show();
                            $('#panel_conclusiones').hide();
                        }
                    }
                    
                },
                url:path_principal+'/actareunion/actualizar-tienes-acta/',//url api
                parametros:{
                    id:self.actaVO.id(),
                    tipo:boolean,
                    valor:value,
                }                     
            };
        Request(parametros);
    }

    self.consultar_porcentaje = function(){
        path = path_principal + '/actareunion/obtener-porcentaje-acta/';
        parameter = {
            acta_id: self.actaVO.id(),
        }
        RequestGet(function(datos,estado,mensaje) {
            if(estado=='ok'){
                // alert(self.actaVO.estado_id());
                // alert(self.actaVO.estado_icono());
                // alert(self.actaVO.estado_nombre());

                self.porcentaje(datos.porcentaje);

                if(self.actaVO.estado_id()!=datos.estado.id){
                    self.consultar_historial(1);
                    //alert(self.actaVO.estado_id()+'-'+datos.estado.id)
                    self.actaVO.estado_id(datos.estado.id);
                    self.actaVO.estado_icono(datos.estado.icono);
                    self.actaVO.estado_nombre(datos.estado.nombre);
                    self.actaVO.estado_color(datos.estado.color);
                }

                

            }else{
                self.porcentaje(0);
            }

            
            cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.setColorIconoFiltro = function (){
    	
        var supervisor_id = sessionStorage.getItem('compromiso_supervisor_id')||'';
        var responsable_id = sessionStorage.getItem('compromiso_responsable_id')||'';
        var desde = sessionStorage.getItem('compromiso_desde')||'';
        var hasta = sessionStorage.getItem('compromiso_hasta')||'';
        var prorroga = sessionStorage.getItem('compromiso_prorroga')||'';
        var descripcion = sessionStorage.getItem('compromiso_descripcion')||'';

        if (supervisor_id != '' || responsable_id != '' || prorroga != ''  || descripcion != '' || desde != '' || hasta != '') {
            //alert('filtro');
            $('#iconoFiltro2').addClass("filtrado");
        }else{
            //alert('no filtro');
            $('#iconoFiltro2').removeClass("filtrado");
        }
    }

    self.consultar_compromisos = function(pagina){
        if (pagina>0){
            sessionStorage.setItem('compromiso_supervisor_id', self.filtro_acta_compromisoVO.supervisor_id()||'');
            sessionStorage.setItem('compromiso_responsable_id', self.filtro_acta_compromisoVO.responsable_id()||'');
            sessionStorage.setItem('compromiso_desde', self.filtro_acta_compromisoVO.desde()||'');
            sessionStorage.setItem('compromiso_hasta', self.filtro_acta_compromisoVO.hasta()||'');
            sessionStorage.setItem('compromiso_prorroga', self.filtro_acta_compromisoVO.prorroga()||'');
            sessionStorage.setItem('compromiso_descripcion', self.filtro_acta_compromisoVO.descripcion()||'');        
            self.cargar_compromisos(pagina);
        }
        
    }

    self.cargar_compromisos = function(pagina){
        if(pagina>0){
            var supervisor_id =  sessionStorage.getItem('compromiso_supervisor_id')||'';
            var responsable_id =  sessionStorage.getItem('compromiso_responsable_id')||'';
            var desde =  sessionStorage.getItem('compromiso_desde')||'';
            var hasta =  sessionStorage.getItem('compromiso_hasta')||'';
            var prorroga = sessionStorage.getItem('compromiso_prorroga')||'';
            var descripcion = sessionStorage.getItem('compromiso_descripcion')||'';


            path = path_principal + '/api/actareunion-compromiso/?format=json';  
            if (self.compromisoVO.responsable_interno() == true){
                parameter = {
                    acta_id: self.actaVO.id(),
                    page: pagina,
                    lite:1,
                    supervisor_id: supervisor_id,
                    usuario_responsable_id: responsable_id,
                    fecha_compromiso_desde: desde,
                    fecha_compromiso_hasta: hasta,
                    prorroga: prorroga,
                    dato: descripcion
                };            
            }else{
                parameter = {
                    acta_id: self.actaVO.id(),
                    page:pagina,
                    lite:1,
                    supervisor_id: supervisor_id,
                    participante_responsable_id: responsable_id,
                    fecha_compromiso_desde: desde,
                    fecha_compromiso_hasta: hasta,
                    prorroga: prorroga,
                    dato: descripcion
                };                
            }                      
            RequestGet(function(datos,estado,mensaje) {      
                if(estado=='ok' && datos.data!=null && datos.data.length>0){                
                    self.listado_compromisos(datos.data);
                    self.mensajeCompromisos('');                 
                }else{
                    self.mensajeCompromisos(mensajeNoFound);
                    self.listado_compromisos([]);
                }
                $('#modal_filtro_compromisos').modal('hide');
                self.llenar_paginacionCompromisos(datos,pagina);
                cerrarLoading();
                self.setColorIconoFiltro();
            }, path, parameter,undefined,false);
        }
    }
    self.limpiarCompromiso = function(){
        self.compromisoVO.id(0);
        self.compromisoVO.acta_id($('#acta_id').val());
        
        self.compromisoVO.descripcion('');
        self.compromisoVO.fecha_compromiso('');
        
        self.compromisoVO.responsable_id('');
        self.compromisoVO.supervisor_id('');

        self.compromisoVO.responsable_interno(false);
        self.compromisoVO.requiere_soporte(false);

        
        self.compromisoVO.descripcion.isModified(false);
        self.compromisoVO.fecha_compromiso.isModified(false);
        
        self.compromisoVO.responsable_id.isModified(false);
        self.compromisoVO.supervisor_id.isModified(false);



    }

    self.compromisoVO.responsable_interno.subscribe(function (val) {
        self.compromisoVO.responsable_id('');
        self.compromisoVO.responsable_id.isModified(false);
    });

    self.reasignacioncompromisoVO.responsable_interno.subscribe(function (val) {
        self.reasignacioncompromisoVO.responsable_id('');
        self.reasignacioncompromisoVO.responsable_id.isModified(false);
    });

    self.abrir_modal_compromisos = function(){
        self.titulo('Nuevo compromiso en el acta No. '+self.actaVO.consecutivo());
        self.limpiarCompromiso();
        $('#modal_acciones').modal('show');
    }

    self.guardar_compromiso = function(){
        //alert(ActaViewModel.errores_compromiso);
        if (ActaViewModel.errores_compromiso().length == 0 ) {
            var validation = true
            if(self.compromisoVO.responsable_interno()==true){
                if(self.compromisoVO.supervisor_id()==self.compromisoVO.responsable_id()){
                    validation = false
                }else{
                    self.compromisoVO.participante_responsable_id('');
                    self.compromisoVO.usuario_responsable_id(self.compromisoVO.responsable_id());
                }
                
            }else{
                self.compromisoVO.participante_responsable_id(self.compromisoVO.responsable_id());
                self.compromisoVO.usuario_responsable_id(self.compromisoVO.supervisor_id());
            }

            if(self.compromisoVO.fecha_compromiso()<self.compromisoVO.fecha_proximidad()){
                validation = false
            }
            if(validation==true){
                if(self.compromisoVO.id()==0){
                    var parametros={
                        metodo:'POST',
                        callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                                
                                self.consultar_porcentaje();                        
                                self.consultar_compromisos(1);
                                $('#modal_acciones').modal('hide');
                                self.limpiarCompromiso();
                                //alert('entro');
                                
                            }else{
                                 mensajeError(mensaje);
                            }
                            cerrarLoading();
                        }, //funcion para recibir la respuesta 
                        url:path_principal+'/api/actareunion-compromiso/',//url api
                        parametros:self.compromisoVO,                      
                    };
                    RequestFormData(parametros);
                }else{
                    var parametros={
                        metodo:'PUT',
                        callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                                self.consultar_compromisos(1);
                                $('#modal_acciones').modal('hide');
                                self.limpiarCompromiso();
                            }else{
                                 mensajeError(mensaje);
                            }
                            cerrarLoading();
                        }, //funcion para recibir la respuesta 
                        url:path_principal+'/api/actareunion-compromiso/'+self.compromisoVO.id()+'/',//url api
                        parametros:self.compromisoVO                  
                    };
                    RequestFormData(parametros);
                }
            }else{
                if(self.compromisoVO.fecha_compromiso()<self.compromisoVO.fecha_proximidad()){                
                    $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>La fecha de proximidad debe ser menor que el plazo del compromiso.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });
                }
                if(self.compromisoVO.responsable_interno()==true){
                    if(self.compromisoVO.supervisor_id()==self.compromisoVO.responsable_id()){
                        $.confirm({
                            title:'Informativo',
                            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>El supervisor no puede ser el mismo responsable.<h4>',
                            cancelButton: 'Cerrar',
                            confirmButton: false
                        });
                    }
                }

                
            }
        }else{
             ActaViewModel.errores_compromiso.showAllMessages();
        }
    }

    self.consultar_por_id = function(obj){
        path = path_principal + '/api/actareunion-compromiso/'+obj.id+'/?format=json';
        parameter = {
            lite:1,
        };
        RequestGet(function(datos,mensaje,estado) {
          
            if(datos!=null){
                self.listado_compromisos();

                self.compromisoVO.id(datos.id);
                self.compromisoVO.acta_id(datos.acta.id);        
                self.compromisoVO.descripcion(datos.descripcion);
                self.compromisoVO.fecha_compromiso(datos.fecha_compromiso);
                self.compromisoVO.fecha_proximidad(datos.fecha_proximidad);

                
                self.compromisoVO.responsable_interno(datos.responsable_interno);
                self.compromisoVO.requiere_soporte(datos.requiere_soporte);

                // if (datos.responsable_interno){
                //     self.compromisoVO.responsable_id(datos.);
                // }else{
                //     self.compromisoVO.responsable_id(datos.);
                // }

                if (self.compromisoVO.responsable_interno()==true){
                    self.compromisoVO.responsable_id(datos.usuario_responsable.id);
                }else{
                    self.compromisoVO.responsable_id(datos.participante_responsable.id);
                }
                //alert(self.compromisoVO.responsable_id());
                //alert(self.compromisoVO.responsable_id());
                self.compromisoVO.supervisor_id(datos.supervisor.id);
               
                
                self.compromisoVO.notificar_organizador(datos.notificar_organizador);
                self.compromisoVO.notificar_controlador(datos.notificar_controlador);


                self.titulo('Editar compromiso en el acta No. '+self.actaVO.consecutivo());
                $('#modal_acciones').modal('show');

            }else{                
                mensajeError(mensaje);
            }            
            cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.abrir_modal_busqueda_compromisos=function(){
        self.titulo('Filtro Compromisos');
        $('#modal_filtro_compromisos').modal('show');
    }

    self.consultarFiltroCompromiso = function () {
        sessionStorage.setItem('app_compromisos_supervisor_id',self.filtro_acta_compromisoVO.supervisor_id());
        sessionStorage.setItem('app_compromisos_responsable_id',self.filtro_acta_compromisoVO.responsable_id());
        sessionStorage.setItem('app_compromisos_desde',self.filtro_acta_compromisoVO.desde());
        sessionStorage.setItem('app_compromisos_hasta',self.filtro_acta_compromisoVO.hasta());
        sessionStorage.setItem('app_compromisos_prorroga',self.filtro_acta_compromisoVO.prorroga());
        sessionStorage.setItem('app_compromisos_descripcion',self.filtro_acta_compromisoVO.descripcion());
        self.consultar_compromisos(1);   
    }

    
    
    self.limpiarCumplimiento = function(obj){
        if(obj){
            self.cumplimientoVO.id(obj.id);
            self.cumplimientoVO.requiere_soporte(obj.requiere_soporte);
            self.cumplimientoVO.motivo('');
            $('#archivo_cumplimiento').fileinput('reset');
            $('#archivo_cumplimiento').val('');
            self.cumplimientoVO.soporte('');
        }else{
            self.cumplimientoVO.id(0);
            self.cumplimientoVO.requiere_soporte(false);
            self.cumplimientoVO.motivo('');
            self.cumplimientoVO.soporte('');
        }
    }
    self.registrar_cumplimiento_compromiso = function(obj){
        self.titulo('Registrar cumplimiento del compromiso');
        self.limpiarCumplimiento(obj); 
        $('#modal_acciones_cumplimiento').modal('show');

        $('#label_fecha_limite').text(obj.fecha_compromiso);
        $('#label_fecha_proxima').text(obj.fecha_proximidad);
        $('#label_descripcion').text(obj.descripcion);
    }

    self.guardar_cumplimiento = function(){

        if(self.cumplimientoVO.id()!=0){
            var validation = false
            if(self.cumplimientoVO.requiere_soporte()==true){
                if(self.cumplimientoVO.soporte()!=''){
                    validation = true
                }else{
                    validation = false
                }
            }else{
                validation = true
            }
            
            if (validation){
                var parametros={
                    metodo:'POST',
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            //alert('entro');                         
                            self.consultar_compromisos(1);
                            $('#modal_acciones_cumplimiento').modal('hide');
                            self.limpiarCumplimiento();
                            if(self.actaVO.estado_id()!=datos.estado.id){
                                self.consultar_historial(1);
                                
                                self.actaVO.estado_id(datos.estado.id);
                                self.actaVO.estado_icono(datos.estado.icono);
                                self.actaVO.estado_nombre(datos.estado.nombre);
                                self.actaVO.estado_color(datos.estado.color);
                            }
                        }else{
                            mensajeError(mensaje);
                        }
                        cerrarLoading();
                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/actareunion/guardar-cumplimiento/',//url api
                    parametros:self.cumplimientoVO,                      
                };
                RequestFormData(parametros);
            }else{
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Ingrese un soporte.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }
        }
    }

    self.ver_cumplimientos_compromiso = function(obj){
        self.titulo('Consulta de cumplimiento del compromiso');
        self.compromisoVO.id(obj.id);
        $('#modal_ver_cumplimiento').modal('show');
        
        if(obj.soporte!='' && obj.soporte!=undefined && obj.soporte!=null){
            $('#soporte_cumplimiento').show();
        }else{
            $('#soporte_cumplimiento').hide();
        }
        if (obj.cumplimiento){
            $('#cumplimiento_observacion').text(obj.cumplimiento.motivo);
            $('#label_fecha_cumplimiento').text(obj.cumplimiento.fecha_cumplimiento);
        }else{
            $('#cumplimiento_observacion').text('');
            $('#label_fecha_cumplimiento').text('');
        }
        

        $('#label_fecha_limite4').text(obj.fecha_compromiso);
        $('#label_fecha_proxima4').text(obj.fecha_proximidad);
        $('#label_descripcion4').text(obj.descripcion);
    }

    self.ver_soporte_cumplimiento = function(){
        window.open(path_principal+"/actareunion/ver-soporte-compromiso/?id="+ self.compromisoVO.id(), "_blank");
    }


    self.historial_compromiso = function(obj){
      
        path = path_principal + '/api/actareunion-compromisohistorial/?format=json';        
        parameter = {                     
            compromiso_id: obj.id,
            lite:1,
            ignorePagination:true,          
        };
        $('#historial_descripcion').text(obj.descripcion);
        $('#historial_supervisor').text(obj.supervisor.persona.nombres+' '+obj.supervisor.persona.apellidos);
        $('#historial_fecha_compromiso').text(obj.fecha_compromiso);

        if(obj.responsable_interno){
            $('#historial_responsable').text(obj.usuario_responsable.persona.nombres+' '+obj.usuario_responsable.persona.apellidos);
        }else{
            $('#historial_responsable').text(obj.participante_responsable.persona.nombres+' '+obj.participante_responsable.persona.apellidos);
        }

        $('#modal_ver_historial').modal('show');
        self.titulo('Historial del compromiso');
        RequestGet(function(datos,estado,mensaje) {      
            if(estado=='ok' && datos!=null && datos.length>0){                
                self.listado_compromisoHistorial(agregarOpcionesObservable(datos));
                self.mensajecompromisoHistorial('');
            }else{
                self.mensajecompromisoHistorial(mensajeNoFound);
                self.listado_compromisoHistorial([]);
            }                
            //self.llenar_paginacionHistorial(datos,pagina);
            cerrarLoading();
        }, path, parameter,undefined,false);
          
    }
    self.abrir_cancelar_compromiso = function(obj){
        $('#cancelar_descripcion').text(obj.descripcion);
        $('#cancelar_supervisor').text(obj.supervisor.persona.nombres+' '+obj.supervisor.persona.apellidos);
        $('#cancelar_fecha_compromiso').text(obj.fecha_compromiso);

        if(obj.responsable_interno){
            $('#cancelar_responsable').text(obj.usuario_responsable.persona.nombres+' '+obj.usuario_responsable.persona.apellidos);
        }else{
            $('#cancelar_responsable').text(obj.participante_responsable.persona.nombres+' '+obj.participante_responsable.persona.apellidos);
        }

        self.cancelarCompromiso.id(obj.id);
        self.titulo('Cancelar compromiso');
        $('#modal_cancelar_compromiso').modal('show');
        
    }

    self.cancelar_compromiso = function(obj){
        if(self.cancelarCompromiso.motivo()){
            var path =path_principal+'/actareunion/cancelar-compromiso/';
            var parameter = {
                compromiso_id: self.cancelarCompromiso.id(),
                motivo: self.cancelarCompromiso.motivo()
            };
            RequestAnularOEliminar("Está seguro que desea cancelar el compromiso?", path, parameter, 
                function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.cancelarCompromiso.id(0);
                        self.cancelarCompromiso.motivo('');
                        $('#modal_cancelar_compromiso').modal('hide');
                        self.consultar_compromisos(self.paginacionCompromisos.pagina_actual());
                    }
            
            });
        }else{
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Se debe ingresar un motivo para cancelar este compromiso<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false,                
                
            });
        }
    }

    self.restablecer_compromiso = function (obj){
        var path =path_principal+'/actareunion/restablecer-compromiso/';
        var parameter = {
            compromiso_id: obj.id,           
        };
        RequestAnularOEliminar("Está seguro que desea restablecer el compromiso?", path, parameter, 
            function(datos, estado, mensaje){
                if (estado=='ok') {                    
                    self.consultar_compromisos(self.paginacionCompromisos.pagina_actual());
                }
        
        });
    }

    

    self.historial_compromiso_prorrogas = function(obj){
      
        path = path_principal + '/api/actareunion-compromisohistorial/?format=json';        
        parameter = {                     
            compromiso_id: obj.id,
            lite:1,
            ignorePagination:true,          
        };
        $('#historial_descripcion').text(obj.descripcion);
        $('#historial_supervisor').text(obj.supervisor.persona.nombres+' '+obj.supervisor.persona.apellidos);
        $('#historial_fecha_compromiso').text(obj.fecha_compromiso);

        if(obj.responsable_interno){
            $('#historial_responsable').text(obj.usuario_responsable.persona.nombres+' '+obj.usuario_responsable.persona.apellidos);
        }else{
            $('#historial_responsable').text(obj.participante_responsable.persona.nombres+' '+obj.participante_responsable.persona.apellidos);
        }

        $('#modal_ver_historial').modal('show');
        self.titulo('Historial del compromiso');
        RequestGet(function(datos,estado,mensaje) {      
            if(estado=='ok' && datos!=null && datos.length>0){                
                self.listado_compromisoHistorial(agregarOpcionesObservable(datos));
                self.mensajecompromisoHistorial('');
            }else{
                self.mensajecompromisoHistorial(mensajeNoFound);
                self.listado_compromisoHistorial([]);
            }                
            //self.llenar_paginacionHistorial(datos,pagina);
            cerrarLoading();
        }, path, parameter,undefined,false);
          
    }


    self.prorrogas_compromiso = function(obj){
        self.titulo('Prorrogas');
        self.fecha_limite(obj.fecha_compromiso);
        self.fecha_proximidad(obj.fecha_proximidad);
        self.prorrogacompromisoVO.id(obj.id);
        $('#label_fecha_limite3').text(obj.fecha_compromiso);
        $('#label_fecha_proxima3').text(obj.fecha_proximidad);
        $('#label_descripcion3').text(obj.descripcion);

        self.prorrogacompromisoVO.fecha(obj.fecha_compromiso);
        self.prorrogacompromisoVO.fecha_proximidad(obj.fecha_proximidad);

        $('#modal_acciones_prorrogas').modal('show');

        path = path_principal + '/api/actareunion-compromisohistorial/?format=json';        
        parameter = {                     
            compromiso_id: obj.id,
            lite:1,
            ignorePagination:true,    
            tipo_operacion_id: 125,      
        };

        RequestGet(function(datos,estado,mensaje) {      
            if(estado=='ok' && datos!=null && datos.length>0){                
                self.listado_compromisoHistorial(datos);
                self.mensajecompromisoHistorial('');
            }else{
                self.mensajecompromisoHistorial(mensajeNoFound);
                self.listado_compromisoHistorial([]);
            }                
            //self.llenar_paginacionHistorial(datos,pagina);
            cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.guardar_prorroga = function(){
        if (ActaViewModel.errores_prorrogar().length == 0 ) {
            if(self.prorrogacompromisoVO.fecha()<self.prorrogacompromisoVO.fecha_proximidad()){                
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>La fecha de proximidad debe ser menor que la fecha de la proroga.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }
            else if(self.fecha_proximidad()>self.prorrogacompromisoVO.fecha_proximidad()){
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una fecha proxima posterior a la fecha proxima ya ingresada<h4>',
                    cancelButton: false,
                    confirmButton: 'Cerrar',                    
                });
            }
            else if(self.fecha_limite()>self.prorrogacompromisoVO.fecha()){
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una fecha posterior a la fecha limite ya ingresada<h4>',
                    cancelButton: false,
                    confirmButton: 'Cerrar',                    
                });
            }else{
                var parametros={
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            //alert('entro');                         
                            self.consultar_compromisos(1);
                            $('#modal_acciones_prorrogas').modal('hide');
                            self.prorrogacompromisoVO.id(0);
                            self.prorrogacompromisoVO.fecha('');
                            self.prorrogacompromisoVO.motivo('');
                        }else{
                            mensajeError(mensaje);
                        }
                        cerrarLoading();
                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/actareunion/prorrogar-compromiso/',//url api
                    parametros:self.prorrogacompromisoVO,                      
                };
                RequestFormData(parametros);
            }
        }else{
             ActaViewModel.errores_prorrogar.showAllMessages();
        }
    }

    self.reasignar_compromiso = function(obj){

        self.reasignacioncompromisoVO.id(obj.id);
        self.reasignacioncompromisoVO.responsable_interno(obj.responsable_interno);

        if (self.reasignacioncompromisoVO.responsable_interno()==true){
            self.reasignacioncompromisoVO.responsable_id(obj.usuario_responsable.id);
        }else{
            self.reasignacioncompromisoVO.responsable_id(obj.participante_responsable.id);
        }
        self.reasignacioncompromisoVO.supervisor_id(obj.supervisor.id);


        self.titulo('Reasignación del compromiso');
        //self.fecha_limite(obj.fecha_compromiso);
        //self.prorrogacompromisoVO.id(obj.id);
        //alert(obj.fecha_compromiso);
        $('#label_fecha_limite2').text(obj.fecha_compromiso);
        $('#label_fecha_proxima2').text(obj.fecha_proximidad);
        $('#label_descripcion2').text(obj.descripcion);

        $('#modal_acciones_reasignaciones').modal('show');

        path = path_principal + '/api/actareunion-compromisohistorial/?format=json';        
        parameter = {                     
            compromiso_id: obj.id,
            lite:1,
            ignorePagination:true,    
            tipo_operacion_id: 127,      
        };

        RequestGet(function(datos,estado,mensaje) {      
            if(estado=='ok' && datos!=null && datos.length>0){                
                self.listado_compromisoHistorial(datos);
                self.mensajecompromisoHistorial('');
            }else{
                self.mensajecompromisoHistorial(mensajeNoFound);
                self.listado_compromisoHistorial([]);
            }                
            //self.llenar_paginacionHistorial(datos,pagina);
            cerrarLoading();
        }, path, parameter,undefined,false);
    }




    self.guardar_reasignacion = function(){
        if (ActaViewModel.errores_reasignar().length == 0 ) {
            validation = true

            //alert(self.reasignacioncompromisoVO.supervisor_id());
            //alert(self.reasignacioncompromisoVO.responsable_id());
            if(self.reasignacioncompromisoVO.supervisor_id()==self.reasignacioncompromisoVO.responsable_id()){
                validation = false
            }


            if(validation == false){
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>El responsable no puede ser el mismo supervisor.<h4>',
                    cancelButton: false,
                    confirmButton: 'Cerrar',                    
                });
            }else{
                var parametros={
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            //alert('entro');                         
                            self.consultar_compromisos(1);
                            $('#modal_acciones_reasignaciones').modal('hide');
                            self.reasignacioncompromisoVO.id(0);
                            self.reasignacioncompromisoVO.motivo('');
                            self.reasignacioncompromisoVO.responsable_interno('');
                            self.reasignacioncompromisoVO.responsable_id('');
                            self.reasignacioncompromisoVO.supervisor_id('');
                        }else{
                            mensajeError(mensaje);
                        }
                        cerrarLoading();
                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/actareunion/reasignar-compromiso/',//url api
                    parametros:self.reasignacioncompromisoVO,                      
                };
                RequestFormData(parametros);
            }
        }else{
             ActaViewModel.errores_reasignar.showAllMessages();
        }
    };

    

}    
var acta = new ActaViewModel();
ActaViewModel.errores_acta_anulacion = ko.validation.group(acta.anulacionactaVO);
ActaViewModel.errores_compromiso = ko.validation.group(acta.compromisoVO);
ActaViewModel.errores_transferencia = ko.validation.group(acta.transferenciaactaVO);
ActaViewModel.errores_cerrar = ko.validation.group(acta.cerraractaVO);
ActaViewModel.errores_prorrogar = ko.validation.group(acta.prorrogacompromisoVO);
ActaViewModel.errores_reasignar = ko.validation.group(acta.reasignacioncompromisoVO);


acta.consultar_acta();
acta.consultar_porcentaje();
// acta.actaVO.tiene_contrato($('#tiene_contrato').val());
// acta.actaVO.tiene_proyecto($('#tiene_proyecto').val());
// acta.actaVO.tiene_conclusiones($('#tiene_conclusiones').val());
// acta.actaVO.tiene_compromisos($('#tiene_compromisos').val());

//alert(acta.actaVO.tiene_compromisos());
ko.applyBindings(acta);