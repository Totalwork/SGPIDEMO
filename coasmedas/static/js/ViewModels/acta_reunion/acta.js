function ActaReunionViewModel() {

	var self = this;
	self.listado=ko.observableArray([]);
    self.listado_contratos=ko.observableArray([]);
    self.listado_proyectos=ko.observableArray([]);
    self.listado_participantes=ko.observableArray([]);
    self.listado_no_participantes=ko.observableArray([]);

    self.mensaje=ko.observable('');
    self.mensaje_participantes=ko.observable('');
    self.mensaje_no_participantes=ko.observable('');
    self.mensajeGraficaCompromisos=ko.observable('');
    self.mensajeGraficaMisCompromisos=ko.observable('');    
    self.mensajeGraficaCompromisosSupervisados=ko.observable('');
    self.titulo=ko.observable('');
    self.titulo2=ko.observable('');
    self.filtro=ko.observable('');

    self.acta_estado=ko.observable('');

    self.checkall=ko.observable(false);
    self.check=ko.observable(false);

    self.select_mcontrato=ko.observable('');

    self.detalle_color =ko.observable('');
    self.detalle_icono =ko.observable('');

    self.url=path_principal+'/api/';
    self.url_funcion=path_principal+'/actareunion/'; 

    self.dato_nopartipantes=ko.observable('');

    self.actaVO ={
        id:ko.observable(0),
        usuario_organizador_id:ko.observable('').extend({ required: { message: '(*)Seleccione el organizador' } }),
        controlador_actual_id:ko.observable($('#usuario_id').val()),
        fecha:ko.observable('').extend({ required: { message: '(*)Ingrese la fecha de la reunión' } }),
        tema_principal:ko.observable('').extend({ required: { message: '(*)Ingrese el tema principal' } }),
        consecutivo:ko.observable(''),
        estado_id:ko.observable(''),
        tiene_contrato:ko.observable(true),
        tiene_proyecto:ko.observable(true),
        tiene_conclusiones:ko.observable(true),
        tiene_compromisos:ko.observable(true),
    };

    self.personaVO={
        id:ko.observable(0),
        cedula:ko.observable('').extend({ required: { message: ' Digite el numero de cedula del propietario.' } }),
        nombres:ko.observable('').extend({ required: { message: ' Digite el nombre del participante.' } }),
        apellidos:ko.observable('').extend({ required: { message: ' Digite el apellido del participante.' } }),
        correo:ko.observable('').extend({required: { message: '(*)Ingrese el correo de la persona' }}).extend({ email: { message: '(*)Ingrese un correo valido' } }),
        telefono:ko.observable('')
     }

    self.filtro_actaVO ={
    	dato:ko.observable(''),
    	controlador_id:ko.observable(''),
    	organizador_id:ko.observable(''),
    	macrocontrato_id:ko.observable(''),
    	contrato_id:ko.observable(''),
    	proyecto_id:ko.observable(''),
        estado_id:ko.observable(''),
    	desde:ko.observable(''),
    	hasta:ko.observable(''),
    };

    self.participanteInternoVO ={
        id:ko.observable(0),
        acta_id:ko.observable(0),
        usuario_id:ko.observable(0),
    };

    self.participanteExternoVO={
        id:ko.observable(0),
        acta_id:ko.observable(0),
        persona_id:ko.observable(0),
    };

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

    self.paginacion.pagina_actual.subscribe(function (pagina) {    
       self.consultar(pagina);
    });

    

    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }

    self.paginacionPersona = {
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
    self.llenar_paginacionPersonas = function (data,pagina) {
        self.paginacionPersona.pagina_actual(pagina);
        self.paginacionPersona.total(data.count);
        self.paginacionPersona.cantidad_por_paginas(resultadosPorPagina);

    }
    self.paginacionPersona.pagina_actual.subscribe(function (pagina) {
        self.consultar_no_participantes(pagina);     
    });
   	
   	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			self.filtro_actaVO.dato($('#txtBuscar').val());
			self.cargar(1);
		}
		return true;
	}

    self.buscarPersona = function (d,e) {
        if (e.which == 13) {
            //self.consultar(1);
            self.consultar_no_participantes(1)
        }
        return true;
    }


    self.checkall.subscribe(function(value ){
        ko.utils.arrayForEach(self.listado_participantes(), function(d) {
            if(d.funcion==''){
                d.eliminado(value);
            }
        }); 
    });

   	self.limpiar = function (){
        self.actaVO.id(0);
        self.actaVO.usuario_organizador_id('');
        self.actaVO.controlador_actual_id($('#usuario_id').val());
        self.actaVO.fecha('');
        self.actaVO.tema_principal('');

        self.actaVO.usuario_organizador_id.isModified(false);   
        self.actaVO.fecha.isModified(false);
        self.actaVO.tema_principal.isModified(false);

    }

    self.limpiar_persona = function(){
        self.personaVO.id(0);
        self.personaVO.cedula('');
        self.personaVO.nombres('');
        self.personaVO.apellidos('');
        self.personaVO.correo('');
        self.personaVO.telefono('');

        self.personaVO.cedula.isModified(false);
        self.personaVO.nombres.isModified(false);
        self.personaVO.apellidos.isModified(false);
        self.personaVO.correo.isModified(false);
        self.personaVO.telefono.isModified(false);

     }

    self.abrir_modal = function (){
    	self.titulo('Registrar acta de reunión');
        self.limpiar();
        $('#modal_acciones').modal('show');
    }

    self.abrir_modal_busqueda = function (){
    	self.titulo('Filtro de acta de reunión');
        self.filtro_actaVO.controlador_id(sessionStorage.getItem("app_acta_reunion_controlador_id"));
        self.filtro_actaVO.organizador_id(sessionStorage.getItem("app_acta_reunion_organizador_id"));
        self.filtro_actaVO.macrocontrato_id(sessionStorage.getItem("app_acta_reunion_macrocontrato_id"));    
        self.filtro_actaVO.contrato_id(sessionStorage.getItem("app_acta_reunion_contrato_id"));
        self.filtro_actaVO.estado_id(sessionStorage.getItem("app_acta_reunion_estado_id"));
        self.filtro_actaVO.desde(sessionStorage.getItem("app_acta_reunion_desde"));
        self.filtro_actaVO.hasta(sessionStorage.getItem("app_acta_reunion_hasta"));
 
        $('#modal_filtro').modal('show');
    }
    
    self.filtro_actaVO.macrocontrato_id.subscribe(function (id) {        
        if(id!='' && id!=null && id!=0 && id!=""){
            path = path_principal + '/actareunion/filtrar-proyectoscontratos/';
            parameter = {mcontrato:id,proyecto:''}
            RequestGet(function(datos,estado,mensaje) {      
                if(estado=='ok' && datos.contratos!=null && datos.contratos.length>0 && datos.proyectos!=null && datos.proyectos.length>0){                
                    self.listado_proyectos(datos.proyectos);
                    self.listado_contratos(datos.contratos);

                    self.select_mcontrato(id);
                }else{
                    self.listado_proyectos([]);
                    self.listado_contratos([]);

                    self.filtro_actaVO.proyecto_id('');
                    self.filtro_actaVO.contrato_id('');
                }                
                cerrarLoading();
            }, path, parameter,(function () {

                self.filtro_actaVO.proyecto_id(sessionStorage.getItem("app_acta_reunion_proyecto_id"));                                      
                self.filtro_actaVO.contrato_id(sessionStorage.getItem("app_acta_reunion_contrato_id"));

                //$('#proyecto_id').val(sessionStorage.getItem("app_acta_reunion_contrato_id")||'');
                //$('#contrato_id').val(sessionStorage.getItem("app_acta_reunion_proyecto_id")||'');

            }),false);
        }else{
            self.listado_proyectos([]);
            self.listado_contratos([]);

            self.filtro_actaVO.proyecto_id('');
            self.filtro_actaVO.contrato_id('');
        }
    });

    self.filtro_actaVO.proyecto_id.subscribe(function (id) {
      
        if(id!='' && id!=null && id!=0 && id!=""){
            path = path_principal + '/actareunion/filtrar-proyectoscontratos/';
            parameter = {
                mcontrato: self.select_mcontrato()||sessionStorage.getItem("app_acta_reunion_macrocontrato_id"),
                proyecto: id
            }
            RequestGet(function(datos,estado,mensaje) {
                if(estado=='ok' && datos.contratos!=null && datos.contratos.length>0){
                    self.listado_contratos(datos.contratos);
                    self.filtro_actaVO.contrato_id(sessionStorage.getItem("app_acta_reunion_contrato_id"));
                    //$('#contrato_id').val(sessionStorage.getItem("app_acta_reunion_proyecto_id")||'');                
                }
                cerrarLoading();
            }, path, parameter,undefined,false);

        }else{
            path = path_principal + '/actareunion/filtrar-proyectoscontratos/';
            parameter = {
                mcontrato: self.select_mcontrato()||sessionStorage.getItem("app_acta_reunion_macrocontrato_id"),
                proyecto: ''
            }
            RequestGet(function(datos,estado,mensaje) {
                if(estado=='ok' && datos.contratos!=null && datos.contratos.length>0){
                    self.listado_contratos(datos.contratos);
                    self.filtro_actaVO.contrato_id('');
                }
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    });

    self.consultar = function (pagina){
        if(pagina>0){
            sessionStorage.setItem("app_acta_reunion_controlador_id",self.filtro_actaVO.controlador_id() || '');
            sessionStorage.setItem("app_acta_reunion_organizador_id",self.filtro_actaVO.organizador_id() || '');
            sessionStorage.setItem("app_acta_reunion_macrocontrato_id",self.filtro_actaVO.macrocontrato_id() || '');
            sessionStorage.setItem("app_acta_reunion_contrato_id",self.filtro_actaVO.contrato_id() || '');
            sessionStorage.setItem("app_acta_reunion_proyecto_id",self.filtro_actaVO.proyecto_id() || '');
            sessionStorage.setItem("app_acta_reunion_estado_id",self.filtro_actaVO.estado_id() || '');
            sessionStorage.setItem("app_acta_reunion_desde",self.filtro_actaVO.desde() || '');
            sessionStorage.setItem("app_acta_reunion_hasta",self.filtro_actaVO.hasta() || '');

            self.cargar(pagina);
        }
    }

    self.cargar = function (pagina){
	    if(pagina>0){
	    	self.filtro_actaVO.dato($('#txtBuscar').val())
    		sessionStorage.setItem("app_acta_reunion_dato", self.filtro_actaVO.dato() || '');


	        path = path_principal + '/api/actareunion-acta/?format=json';
            var controlador_id=sessionStorage.getItem("app_acta_reunion_controlador_id")||'';
            var organizador_id = sessionStorage.getItem("app_acta_reunion_organizador_id")||'';
            var macrocontrato_id = sessionStorage.getItem("app_acta_reunion_macrocontrato_id")||'';    
            var contrato_id = sessionStorage.getItem("app_acta_reunion_contrato_id")||'';
            var proyecto_id = sessionStorage.getItem("app_acta_reunion_proyecto_id")||'';
            var estado_id = sessionStorage.getItem("app_acta_reunion_estado_id")||'';
            var desde = sessionStorage.getItem("app_acta_reunion_desde")||'';
            var hasta = sessionStorage.getItem("app_acta_reunion_hasta")||'';

	        parameter = {
	        	dato: self.filtro_actaVO.dato(),
                controlador_id: controlador_id,
                organizador_id: organizador_id,
                macrocontrato_id: macrocontrato_id,
                estado_id: estado_id,
                fecha_desde: desde,
                fecha_hasta: hasta,
                proyecto_id: proyecto_id,
                contrato_id: contrato_id,
	        	page:pagina,
	        	lite:1,
	        };
	        RequestGet(function(datos,estado,mensaje) {      
	    		if(estado=='ok' && datos.data!=null && datos.data.length>0){    				    			
                    self.listado(datos.data);
	    			self.mensaje('');
                    self.llenar_graficas();
		        }else{
		        	self.mensaje(mensajeNoFound);
		        	self.listado([]);
		        }
                $('#modal_filtro').modal('hide');                
		        self.llenar_paginacion(datos,pagina);
                self.setColorIconoFiltro();
	    		cerrarLoading();
	        }, path, parameter,undefined,false);
	    }
    }

    self.llenar_graficas = function (){
        var path = path_principal + '/actareunion/llenar-graficasactas/';
        var parameter = {}                    
        var columnsActas = [];
        var columnsColorsActas = [];
        var columnsCompromisos = [];
        var columnsColorsCompromisos = [];
        var columnsMisCompromisos = [];
        var columnsColorsMisCompromisos = [];                
        var columnsCompromisosSupervisados = [];
        var columnsColorsCompromisosSupervisados = [];                        
        RequestGet(function(datos,estado,mensaje) {                  
            for (var i=0; i < datos.length; i++){
                if (datos[i].grafica == 'Actas por estado'){
                    columnsActas = datos[i].datagrafica;
                    columnsColorsActas = datos[i].datoColores;
                } 
                if (datos[i].grafica == 'Compromisos por estado'){
                    columnsCompromisos = datos[i].datagrafica;
                    columnsColorsCompromisos = datos[i].datoColores;
                }
                if (datos[i].grafica == 'Mis Compromisos por estado'){
                    columnsMisCompromisos = datos[i].datagrafica;
                    columnsColorsMisCompromisos = datos[i].datoColores;
                }
                if (datos[i].grafica == 'Compromisos supervisados por estado'){
                    columnsCompromisosSupervisados = datos[i].datagrafica;
                    columnsColorsCompromisosSupervisados = datos[i].datoColores;
                }                                
                                                            
            }
            //Grafica Actas por Estados
            var chart14 = c3.generate({
                bindto: '#pie-chartActasPorEstado',
                color: {
                    pattern: columnsColorsActas,
                },
                data: {
                    // iris data from R
                    columns: columnsActas,
                    type : 'pie',
                    onclick: function (d, i) { console.log("onclick", d, i); },
                    onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                    onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                },
                tooltip: {
                    format: {                        
                        value: function (value, ratio, id) {                            
                            return 'Cant: '+value;
                        }
                    }
                }
            });	
            
            //Grafica Compromisos por Estados
            if (columnsColorsCompromisos.length==0){
                self.mensajeGraficaCompromisos(mensajeNoFound);
            }else{
                self.mensajeGraficaCompromisos('');
                var chart14 = c3.generate({
                    bindto: '#pie-chartCompromisosPorEstado',
                    color: {
                        pattern: columnsColorsCompromisos,
                    },
                    data: {
                        // iris data from R
                        columns: columnsCompromisos,
                        type : 'pie',
                        onclick: function (d, i) { console.log("onclick", d, i); },
                        onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                        onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                    },
                    tooltip: {
                        format: {                        
                            value: function (value, ratio, id) {                            
                                return 'Cant: '+value;
                            }
                        }
                    }                    
                });
            }

            
            //Grafica Mis Compromisos por Estados
            if (columnsColorsMisCompromisos.length==0){
                self.mensajeGraficaMisCompromisos(mensajeNoFound);
            }else{ 
                self.mensajeGraficaMisCompromisos('');
                var chart14 = c3.generate({
                    bindto: '#pie-chartMisCompromisosPorEstado',
                    color: {
                        pattern: columnsColorsMisCompromisos,
                    },
                    data: {
                        // iris data from R
                        columns: columnsMisCompromisos,
                        type : 'pie',
                        onclick: function (d, i) { consultar_estado(d.name,'compromiso'); },
                        // onclick: function (d, i) { console.log("onclick", d, i); },
                        onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                        onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                    },
                    tooltip: {
                        format: {                        
                            value: function (value, ratio, id) {                            
                                return 'Cant: '+value;
                            }
                        }
                    }                    
                });  
            }
            
            //Grafica Compromisos Supervisados por Estados
            if (columnsColorsCompromisosSupervisados.length==0){
                self.mensajeGraficaCompromisosSupervisados(mensajeNoFound);
            }else{ 
                self.mensajeGraficaCompromisosSupervisados('');
                var chart14 = c3.generate({
                    bindto: '#pie-chartCompromisosSupervisados',
                    color: {
                        pattern: columnsColorsCompromisosSupervisados,
                    },
                    data: {
                        // iris data from R
                        columns: columnsCompromisosSupervisados,
                        type : 'pie',
                        onclick: function (d, i) { console.log("onclick", d, i); },
                        onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                        onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                    },
                    tooltip: {
                        format: {                        
                            value: function (value, ratio, id) {                            
                                return 'Cant: '+value;
                            }
                        }
                    }                    
                });  
            }            
        }, path, parameter,undefined,false);


    }

    self.setColorIconoFiltro = function (){
    	
        var controlador_id=sessionStorage.getItem("app_acta_reunion_controlador_id")||'';
        var organizador_id = sessionStorage.getItem("app_acta_reunion_organizador_id")||'';
        var macrocontrato_id = sessionStorage.getItem("app_acta_reunion_macrocontrato_id")||'';    
        var contrato_id = sessionStorage.getItem("app_acta_reunion_contrato_id")||'';
        var proyecto_id = sessionStorage.getItem("app_acta_reunion_proyecto_id")||'';
        var estado_id = sessionStorage.getItem("app_acta_reunion_estado_id")||'';
        var desde = sessionStorage.getItem("app_acta_reunion_desde")||'';
        var hasta = sessionStorage.getItem("app_acta_reunion_hasta")||'';        

    	

        if (controlador_id != '' || organizador_id != '' || macrocontrato_id != '' || contrato_id != '' 
            || proyecto_id != '' || estado_id != '' || desde != '' || hasta != ''){

            $('#iconoFiltro').addClass("filtrado");
        }else{
            $('#iconoFiltro').removeClass("filtrado");
        }
    }

    
    self.guardar = function(){
        if (ActaReunionViewModel.errores_acta().length == 0 ) {
            if(self.actaVO.id()==0){
                var parametros={
                    metodo:'POST',
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            mensajeExitoso(mensaje+'</br>El No.Acta generado es: '+datos.consecutivo);
                            self.consultar(1);
                            self.participantes(datos);
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }else{
                             mensajeError(mensaje);
                        }
                        cerrarLoading();
                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/actareunion-acta/',//url api
                    parametros:self.actaVO,
                    alerta:false                       
                };
                RequestFormData(parametros);
            }else{
                var parametros={
                    metodo:'PUT',
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.consultar(1);
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }else{
                             mensajeError(mensaje);
                        }
                        cerrarLoading();
                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/actareunion-acta/'+self.actaVO.id()+'/',//url api
                    parametros:self.actaVO                  
                };
                RequestFormData(parametros);
            }
        }else{
             ActaReunionViewModel.errores_acta.showAllMessages();
        }
    }

    self.participantes= function(obj){
        
        self.consultar_participantes(obj.id);
        self.titulo('Participantes');
        self.acta_estado(obj.estado.id);
        $('#modal_acciones_participantes').modal('show');
        $('#acta_id').val(obj.id);
        $('#txtBuscarPersona').val('');
        
    }

    self.consultar_participantes = function(acta_id){
        path = path_principal + '/actareunion/obtener-participantes/';
        parameter = {
            acta_id: acta_id,
            asistencia: false,
        }
        RequestGet(function(datos,estado,mensaje) {
            if(estado=='ok' && datos!=null && datos.length>0){
                self.listado_participantes(agregarOpcionesObservable(datos));
                self.mensaje_participantes('');
                  
            }else{
                self.mensaje_participantes(mensajeNoFound);
                self.listado_participantes([]);
            }

            
            cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.consultar_por_id = function(obj){
        path = path_principal + '/api/actareunion-acta/'+obj.id+'/?format=json';
        parameter = {
            lite:1,
        };
        RequestGet(function(datos,mensaje,estado) {
          
            if(datos!=null){
                self.actaVO.id(datos.id);
                self.actaVO.usuario_organizador_id(datos.usuario_organizador.id);
                self.actaVO.controlador_actual_id(datos.controlador_actual.id);
                self.actaVO.fecha(datos.fecha);
                self.actaVO.tema_principal(datos.tema_principal);
                self.actaVO.consecutivo(datos.consecutivo);
                self.actaVO.estado_id(datos.estado.id);

                 self.titulo('Editar acta de reunión');
                $('#modal_acciones').modal('show');

            }else{                
                mensajeError(mensaje);
            }            
            cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.eliminar_participantes = function () {
         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_participantes(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id.push({
                        id:d.id,
                        tipo:d.tipo,
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un giro para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/actareunion/eliminar-participantes/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los participantes seleccionados?", path, parameter, function () {
                 self.consultar_participantes($('#acta_id').val());
                 self.checkall(false);
             })

         }     
    
        
    }

    self.cerrar_acta = function(obj) {
        var path =path_principal+'/actareunion/cerrar-acta/';
        var parameter = {acta_id:obj.id,motivo:''};
        RequestAnularOEliminar("Esta seguro que desea cerrar el acta?", path, parameter, 
            function(datos, estado, mensaje){
                if (estado=='ok') {
                    self.cargar(self.paginacion.pagina_actual());
                }
        
        });

    }

    self.ver_detalle = function(obj){
        path = path_principal + '/api/actareunion-acta/'+obj.id+'/?format=json';
        parameter = {
            lite:1,
        };
        RequestGet(function(datos,mensaje,estado) {
       
            if(datos!=null){
                //self.actaVO.id(datos.id);
                $('#detalle_usuario_organizador').text(datos.usuario_organizador.persona.nombres+' '+datos.usuario_organizador.persona.apellidos)
                $('#detalle_controlador_actual').text(datos.controlador_actual.persona.nombres+' '+datos.controlador_actual.persona.apellidos)
                $('#detalle_fecha').text(datos.fecha)
                $('#detalle_tema_principal').text(datos.tema_principal)
                //$('#detalle_consecutivo').val(datos.consecutivo)
                $('#detalle_estado').text(datos.estado.nombre)
                if(datos.soporte==null || datos.soporte==''){
                    $('#detalle_soporte').text('Pendiente')
                    $('#detalle_soporte_archivo').hide();
                }else{
                    $('#detalle_soporte_archivo').show();
                    
                }
                $('#acta_id').val(obj.id);
                self.detalle_color(datos.estado.color);
                self.detalle_icono(datos.estado.icono);
                self.titulo('Detalles Acta de reunión: No.'+datos.consecutivo);
                $('#modal_acciones_detalles').modal('show');

            }else{                
                mensajeError(mensaje);
            }            
            cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.ver_soporte = function(acta_id){
        if(acta_id){
            window.open(path_principal+"/actareunion/ver-soporte-acta/?id="+ acta_id, "_blank");
        }else{
            var acta = $('#acta_id').val();
            window.open(path_principal+"/actareunion/ver-soporte-acta/?id="+ acta, "_blank");
        }
    }

    self.exportar_excel = function(){
        filtro_buscador=sessionStorage.getItem("filtro_avance")  || "";
        departamento_id_avance=sessionStorage.getItem("departamento_id_avance") || 0;
        municipio_id_avance=sessionStorage.getItem("municipio_id_avance") || 0;
        macrocontrato_id_avance=sessionStorage.getItem("macrocontrato_id_avance") || 0;
        contratista_id_avance=sessionStorage.getItem("contratista_id_avance") || 0;

        filtro_buscador =  sessionStorage.getItem("app_acta_reunion_dato")|| "";
        controlador_id= sessionStorage.getItem("app_acta_reunion_controlador_id")|| "";
        organizador_id =  sessionStorage.getItem("app_acta_reunion_organizador_id")|| "";
        macrocontrato_id =  sessionStorage.getItem("app_acta_reunion_macrocontrato_id")|| "";
        contrato_id =  sessionStorage.getItem("app_acta_reunion_contrato_id")|| "";
        proyecto_id =  sessionStorage.getItem("app_acta_reunion_proyecto_id")|| "";
        estado_id =  sessionStorage.getItem("app_acta_reunion_estado_id")|| "";
        desde  = sessionStorage.getItem("app_acta_reunion_desde")|| "";
        hasta =  sessionStorage.getItem("app_acta_reunion_hasta")|| "";


        location.href=path_principal+"/actareunion/exportar-actas/?dato="+filtro_buscador+
                                                                         "&controlador_id="+controlador_id+
                                                                         "&organizador_id="+organizador_id+
                                                                         "&macrocontrato_id="+macrocontrato_id+
                                                                         "&contrato_id="+contrato_id+
                                                                         "&proyecto_id="+proyecto_id+
                                                                         "&estado_id="+estado_id+
                                                                         "&desde="+desde+
                                                                         "&hasta="+hasta;
                                                                         
                                                                         
                   
    }



    self.abrir_modal_participante = function(){
        self.check(false);
        self.titulo2('Invitar participantes');
        $('#modal_acciones_participantes_gestion').modal('show');
        self.consultar_no_participantes(1);
        
    }

    self.check.subscribe(function (val) {
        if(val==true){
            $('#panel_registro_persona').hide();            
        }else{
            $('#panel_registro_persona').show();
        }
        self.consultar_no_participantes(1);
    });

    self.consultar_no_participantes = function(pagina,cedula){
        
        if(pagina>0){
            var validacion_check = self.check();
  
            path = path_principal + '/api/actareunion-noparticipantes/';

            
            if (cedula){
                self.dato_nopartipantes(cedula);
                    parameter = {
                    acta_id: $('#acta_id').val(),
                    dato:'',              
                    solo_internos:validacion_check,
                    cedula:self.dato_nopartipantes(),
                    page:pagina,
                }
            }else{
                self.dato_nopartipantes($('#txtBuscarPersona').val());
                parameter = {
                    acta_id: $('#acta_id').val(),
                    dato:self.dato_nopartipantes(),
                    solo_internos:validacion_check,
                    cedula:'',
                    page:pagina,
                }
            }
          
            RequestGet(function(datos,estado,mensaje) {      
                if(estado=='ok' && datos.data!=null && datos.data.length>0){   
                    self.listado_no_participantes(datos.data);
                    self.mensaje_no_participantes('');
                }else{
                    self.listado_no_participantes([])             
                    self.mensaje_no_participantes(mensajeNoFound);
                }
                self.llenar_paginacionPersonas(datos, pagina);          
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }
   
   self.invitarParticipante = function(obj){
        $.confirm({
            title:'Informativo',
            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Desea invitar a esta persona?<h4>',
            cancelButton: 'No',
            confirmButton: 'Si',
            confirm: function() {

                if(obj.usuario>0){

                    self.participanteInternoVO.acta_id($('#acta_id').val());
                    self.participanteInternoVO.usuario_id(obj.usuario);
                    var parametros={     
                        metodo:'POST',                
                        callback:function(datos, estado, mensaje){
                            if (estado=='ok') { 
                                 self.consultar_participantes($('#acta_id').val());
                                 mensajeExitoso(mensaje);
                                 $('#modal_acciones_participantes_gestion').modal('hide');
                                 
                            }else{
                                mensajeError(mensaje);
                            }
                        },//funcion para recibir la respuesta 
                        url:path_principal+'/api/actareunion-participanteinterno/',//url api
                        parametros:self.participanteInternoVO,
                        alerta:false
                        //parametros: self.cronogramaVO
                    };
                    RequestFormData(parametros);
                    
                }else{

                    self.participanteExternoVO.acta_id($('#acta_id').val());
                    self.participanteExternoVO.persona_id(obj.id);
                    var parametros={     
                        metodo:'POST',                
                        callback:function(datos, estado, mensaje){
                            if (estado=='ok') { 
                                self.consultar_participantes($('#acta_id').val());
                                mensajeExitoso(mensaje);
                                $('#modal_acciones_participantes_gestion').modal('hide');
                            }else{
                                mensajeError(mensaje);
                            }
                        },//funcion para recibir la respuesta 
                        url:path_principal+'/api/actareunion-participanteexterno/',//url api
                        parametros:self.participanteExternoVO,
                        alerta:false
                        //parametros: self.cronogramaVO
                    };
                    RequestFormData(parametros);
                }
            }
        });
   }

    

    self.guardarPersona = function(){
        //alert(ActaReunionViewModel.errores_persona().length);
        if (ActaReunionViewModel.errores_persona().length == 0 ) {
            if(self.personaVO.id()==0){
                var parametros={
                    metodo:'POST',
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            mensajeExitoso(mensaje);
                            
                            $('#txtBuscarPersona').val('')
                            self.consultar_no_participantes(1,datos.cedula);
                            self.limpiar_persona();
                        }else{
                             mensajeError(mensaje);
                        }
                        cerrarLoading();
                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/persona/',//url api
                    parametros:self.personaVO,
                    alerta:false                       
                };
                RequestFormData(parametros);
            }
        }else{
             ActaReunionViewModel.errores_persona.showAllMessages();
        }
    };


    self.generar_qr = function(id){
        window.open(path_principal+"/actareunion/generar-codigo-qr/?acta_id="+ id, "_blank");
    }

}
var acta = new ActaReunionViewModel();

ActaReunionViewModel.errores_acta = ko.validation.group(acta.actaVO);
ActaReunionViewModel.errores_persona = ko.validation.group(acta.personaVO);
$('#txtBuscar').val(sessionStorage.getItem("app_acta_reunion_dato"))
acta.cargar(1);


ko.applyBindings(acta);


function consultar_estado(estado_nombre,app){
    const estados = [{
        name: 'Por cumplir',
        id: 159        
    }, {
        name: 'Por vencer',
        id: 160        
    },{
        name: 'Vencido',
        id: 161        
    },{
        name: 'Cumplido',
        id: 162        
    },{
        name: 'Cumplido despues vencido',
        id: 163        
    },{
        name: 'Cancelado',
        id: 164        
    }]; 


    var estado = estados.find(estado => estado.name === estado_nombre);
    if(estado){
        sessionStorage.setItem('mis_compromiso_estado_id', estado.id||'');
        window.location.href = path_principal+"/actareunion/mis-compromisos/"; 
    }

}

