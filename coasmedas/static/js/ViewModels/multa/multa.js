function MultaViewModel() {
    administraccion_de_recurso = 12
    /*ESTADOS DE LAS MULTA*/
    Solicitada = 74;
    Generada = 75;
    Elaborada = 82;
    Confirmada = 78;
    

	var self = this;
    self.app_multa = 'multa';
    self.empresaActual = $("#company").val();
    self.usuarioActual = $("#user").val();
	self.titulo=ko.observable('');
    self.titulo_btn=ko.observable('Guardar');
    self.filtro=ko.observable('');
    self.estado_multa=ko.observable('');
    self.mensaje=ko.observable('');
    self.mensajePorAsignar=ko.observable('');
    self.mensajeAsignados=ko.observable('');
    self.mensajeListadoContrato=ko.observable('');
    self.conjunto_id =ko.observable('');

    self.solicitudes_elaboradas = ko.observable('');
    self.solicitudes_solicitadas = ko.observable('');
    self.solicitudes_consulta = ko.observable(1);
    
	self.url=path_principal+'/api/'; 
    self.url_app_parametrizacion = path_principal+'/parametrizacion/';
    self.url_funcion_proyecto = path_principal+'/proyecto/'; 
    self.url_funcion_multa = path_principal+'/multa/';
    self.url_app_correspondencia = '/correspondencia/';   
 
	self.listado = ko.observableArray([]);
	self.listado_mcontrato = ko.observableArray([]);
    self.listado_contratista = ko.observableArray([]);
    self.listado_solicitante = ko.observableArray([]);	
    self.listado_estado = ko.observableArray([]); 

    self.listado_estado_posibles = ko.observableArray([]); 

    self.listado_eventos_asignados = ko.observableArray([]);

    /*--- CORRESPONDENCIA-----------------------------*/
    self.listado_municipiosEmpresa = ko.observableArray([]);
    self.listado_departamentos = ko.observableArray([]);
    self.listado_municipios = ko.observableArray([]);
    self.listado_prefijos = ko.observableArray([]);
    self.listado_funcionarios = ko.observableArray([]);
    self.listado_funcionarios_firma = ko.observableArray([]); 
    self.departamentoEmpresa_id =ko.observable('');
    self.listado_empresas = ko.observableArray([]);
    self.filtro_empresaDestinatario = ko.observable('');
    self.filtro_empresaDestinatarioCopia = ko.observable('');
    self.listado_funcionarios_copia = ko.observableArray([]);
    self.listado_destinatarios_con_copia = ko.observableArray([]);// manejo de datos
    self.listado_funcionarios_elaboran = ko.observableArray([]);

    /*----CONTRATO -----------------------------------*/
    self.estado={
        vigente:ko.observable(28),
        liquidado:ko.observable(29),
        suspendido:ko.observable(30),
        porVencer:ko.observable(31),
        vencido:ko.observable(32)
    };

    self.listado_contrato = ko.observableArray([]);
    self.listado_estados_contrato = ko.observableArray([]);
    self.app_contrato = 'contrato';
    self.filtro_contratoVO={
        filtro:ko.observable(''), 
        id_tipo:ko.observable(''),
        id_estado:ko.observable(''),      
    };

	self.checkall=ko.observable(false);

    /* LISTADO DE LAS PRUEBAS DE LA SOLICITUD */
    self.listado_solicitud_pruebas = ko.observableArray([]);

	self.multaVO={
	 	id:ko.observable(0),
        consecutivo:ko.observable(''),
	 	diasApelar:ko.observable(5),
	 	fechaDiligencia:ko.observable(''), 
        soporte:ko.observable(''), 
        valorSolicitado:ko.observable('0').extend({ required: { message: ' Digite el valor a solicitar.' } }), 
        valorImpuesto:ko.observable(''), 
        contrato_id:ko.observable('').extend({ required: { message: ' Seleccione el contrato.' } }),  
        correspondenciadescargo_id:ko.observable(''),
        correspondenciasolicita_id:ko.observable(0),
        firmaImposicion_id:ko.observable(''),
	    /*CORRESPONDENCIA*/
        fechaEnvio:ko.observable('').extend({ required: { message: ' Digite la fecha de solicitud.' } }), 
        contenido:ko.observable(''),
        consecutivo_carta:ko.observable(''),
        contenidoHtml:ko.observable(''),
        clausula_afectada:ko.observable(''),
        clausula_afectadaHtml:ko.observable(''),
        departamento_id:ko.observable('').extend({ required: { message: ' Seleccione el departamento de envio.' } }),
        ciudad_id:ko.observable('').extend({ required: { message: 'Seleccione la ciudad de envio.' } }),
        prefijo_id:ko.observable('').extend({ required: { message: 'Seleccione el prefijo.' } }),
        firmaSolicitud_id:ko.observable('').extend({ required: { message: ' Seleccione el funcionario.' } }),
        destinatario_id:ko.observable('').extend({ required: { message: ' Seleccione el destinatario.' } }),
        ciudad_destinatario_id:ko.observable('').extend({ required: { message: 'Seleccione la ciudad del destinatario.' } }),
        usuarioSolicitante_id:ko.observable(self.usuarioActual).extend({ required: { message: ' Seleccione el usuario solicitante.' } }),
        listado_eventos_asignados_id:ko.observableArray([]),
        listado_eventos_asignados_dia:ko.observableArray([]),

    };
    self.generate_multaVO={
        fechaDiligencia:ko.observable('').extend({ required: { message: ' Digite la fecha de diligencia.' } }),
        firmaImposicion_id:ko.observable('').extend({ required: { message: ' Seleccione el funcionario.' } }),
    }
    self.codigo_multaVO={
        fechaDiligencia:ko.observable('').extend({ required: { message: ' Digite la fecha de diligencia.' } }),
        codigo:ko.observable('').extend({ required: { message: ' Digite el codigo .' } }),
    }

    self.actualizar_valor_multaVO={
        valor_imposicion:ko.observable('').extend({ required: { message: ' Digite el nuevo valor .' } }),
    }

    self.filtro_multaVO={
        id:ko.observable(0),
        mcontrato:ko.observable(''),
        estado:ko.observable(''),
        consecutivo:ko.observable(''), 
        desde:ko.observable(''), 
        hasta:ko.observable(''),
        numerocontrato:ko.observable(''),
        contratista_id:ko.observable(''),
        solicitante_id:ko.observable(''),
    };
    /* MOSTRAR DATOS */
    self.historial_multaVO={
        consecutivo:ko.observable(''),
        no_contrato:ko.observable(''),
        nombre:ko.observable(''),
        estado_contrato:ko.observable(''), 
        fecha_solicitud:ko.observable(''), 
        contratista:ko.observable(''),
        estado_solicitud:ko.observable(''),
        valor_solicitado:ko.observable(''),
        valor_imposicion:ko.observable(''),
    };

    self.multa_solicitud_historialVO={
        fecha:ko.observable('').extend({ required: { message: ' Indique la fecha.' } }), 
        soporte:ko.observable(''),
        comentarios:ko.observable('').extend({ required: { message: ' Digite el comentario.' } }), 
        estado_id:ko.observable('').extend({ required: { message: ' Seleccione el nuevo estado.' } }), 
        solicitud_id:ko.observable(''), 
        usuario_id:ko.observable(''),
    };

    self.respuesta_descargoVO={
        id:ko.observable(0),
        estado_id:ko.observable(0),
        correspondenciadescargo_id:ko.observable(0),
        consecutivo:ko.observable('').extend({ validation: { validator: validar_consecutivo, message: '(*) Digite el consecutivo.' } }),

        fechaEnvio:ko.observable('').extend({ required: { message: ' Digite la fecha de envio.' } }),
        departamento_id:ko.observable('').extend({ required: { message: ' Seleccione el departamento.' } }),
        ciudad_id:ko.observable('').extend({ required: { message: ' Seleccione la ciudad.' } }),
        prefijo_id:ko.observable('').extend({ required: { message: ' Seleccione el prefijo.' } }),
        asunto:ko.observable(''),
        referencia:ko.observable(''),        
        contenido:ko.observable(''),
        contenidoHtml:ko.observable(''),
        firma_id:ko.observable('').extend({ required: { message: ' Seleccione el funcionario a firmar.' } }), 
        privado:ko.observable(0),
        grupoSinin:ko.observable('0'),
        destinatario:ko.observable(0), 
        destinatarioCopia:ko.observableArray([]),        
        empresa_destino:ko.observable(''),
        cargo_persona:ko.observable(''),
        persona_destino:ko.observable(''),
        direccion:ko.observable(''),
        telefono:ko.observable(''),
        municipioEmpresa_id:ko.observable('').extend({ required: { message: ' Seleccione la ciudad del destinatario.' } }),
    };

    function validar_consecutivo(val){
      consecutivo = $("#consecutivoHabilitado").val();
      return consecutivo=="False" || (consecutivo=="True" && val!=null && val!='');
    }

    self.limpiar_multa_solicitud_historialVO=function(){  
        self.multa_solicitud_historialVO.fecha('');
        self.multa_solicitud_historialVO.soporte('');
        self.multa_solicitud_historialVO.comentarios('');
        self.multa_solicitud_historialVO.estado_id('');
        self.multa_solicitud_historialVO.fecha.isModified(false);
        self.multa_solicitud_historialVO.comentarios.isModified(false);
        self.multa_solicitud_historialVO.estado_id.isModified(false);

    }
    //INFORMACION DE LOS SOPORTES
    self.multa_soporteVO = {
        id: ko.observable(0),
        nombre : ko.observable(''),
        soporte: ko.observable(''),
        anulado: ko.observable(0),
        solicitud_id: ko.observable(0),
        soporte_id: ko.observableArray([]),
    };

    //INFORMACION DE LOS SOPORTES
    self.correspondencia_soporteVO = {
        id: ko.observable(0),
        correspondencia_id: ko.observable(''),
        soporte: ko.observable(''),
        validaNombre : ko.observable(0),
        nombre : ko.observable(''),
        soporte_id: ko.observableArray([]),/* SE USA ESTA LISTA PARA ELIMINAR VARIOS SOPORTES A LA VES*/   
        solicitud_id: ko.observable(0),
    };

    self.llenar_datos_historial = function(obj){

        path =path_principal+'/api/MultaSolicitud/'+obj.solicitud.id+'/?format=json';
        parameter = { };
        RequestGet(function (results,count) {

            // DATOS PARA MOSTRAR
            self.historial_multaVO.consecutivo(results.consecutivo);
            self.historial_multaVO.no_contrato(results.contrato.numero);
            self.historial_multaVO.nombre(results.contrato.nombre);
            self.historial_multaVO.estado_contrato(results.contrato.estado.nombre);
            self.historial_multaVO.fecha_solicitud(results.fechasolicitud);
            self.historial_multaVO.contratista(results.contrato.contratista.nombre);
            self.historial_multaVO.estado_solicitud(results.estado.nombre);
            self.historial_multaVO.valor_solicitado(results.valorSolicitado);
            self.historial_multaVO.valor_imposicion(results.valorImpuesto);
        
             
            cerrarLoading();
        }, path, parameter,undefined,false);
        
    }
	// //limpiar el modelo 
     self.limpiar=function(){   
        tinymce.get('clausulas').setContent('')
        tinymce.get('clausulas').execCommand('mceCleanup');

        tinymce.get('echos').setContent('')
        tinymce.get('echos').execCommand('mceCleanup');

        self.multaVO.consecutivo('');
        self.multaVO.diasApelar(5);
        self.multaVO.fechaDiligencia('');
        self.multaVO.soporte('');
        self.multaVO.valorSolicitado('0');
        self.multaVO.valorImpuesto('');
        self.multaVO.contrato_id('');
        self.multaVO.correspondenciadescargo_id('');
        self.multaVO.correspondenciasolicita_id(0);
        self.multaVO.firmaImposicion_id('');

        /*CORRESPONDENCIA*/
        self.multaVO.fechaEnvio('');
        self.multaVO.contenido('');
        self.multaVO.contenidoHtml('');
        self.multaVO.departamento_id('');
        self.multaVO.ciudad_id('');
        self.multaVO.prefijo_id('');
        self.multaVO.firmaSolicitud_id('');
        self.multaVO.destinatario_id('');
        self.multaVO.ciudad_destinatario_id('');

        $("#contratoAsignado").val('');
        self.multaVO.contrato_id.isModified(false);
        self.multaVO.valorSolicitado.isModified(false);
        self.multaVO.fechaEnvio.isModified(false);
        self.multaVO.departamento_id.isModified(false);
        self.multaVO.ciudad_id.isModified(false);
        self.multaVO.prefijo_id.isModified(false);
        self.multaVO.firmaSolicitud_id.isModified(false);
        self.multaVO.destinatario_id.isModified(false);
        self.multaVO.ciudad_destinatario_id.isModified(false);
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

    self.paginacion.pagina_actual.subscribe(function (pagina) {    
       self.consultar(pagina);
    });

    self.consultar_select_filter_multa = function () { 

            path = path_principal+'/multa/select-filter-multa/';
            parameter = { };
            RequestGet(function (datos, estado, mensage) {

                self.listado_estado(datos.estados_solicitudes); 
                self.listado_solicitante(datos.solicitantes);
                self.listado_mcontrato(datos.macro_contratos);
                self.listado_contratista(datos.contratistas);

                cerrarLoading();
            }, path, parameter,undefined,false);
    }
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }
    self.abrir_modal_contratos = function(){
        self.listado_contrato([]);
        self.mensajeListadoContrato(mensajeInformativoBusuqeda)
        self.titulo('Contratos de obra');
        $('#modal_contratos').modal('show');
    }
    self.abrir_modal_eventos = function(){
        self.titulo('Eventos');
        $('#modal_eventos').modal('show');
    }
    self.abrir_modal = function () {
        self.titulo('Registrar Solicitud');
        $('#modal_acciones').modal('show');
    }
    self.abrir_modal_busqueda = function () {
        self.titulo('Consultar Solicitudes ');
        $('#modal_busqueda').modal('show');
        self.consultar_select_filter_multa();
    }
    self.abrir_modal_historial = function (obj) {
        self.llenar_datos_historial(obj); 
        self.titulo('Historial de la  Solicitud');
        $('#modal_historial').modal('show');               
    }
    self.abrir_modal_generar = function (obj) {
        self.llenar_datos_historial(obj); 
        self.multaVO.id(obj.solicitud.id)
        self.titulo('Generar Solicitud');
        $('#modal_generar').modal('show');
    }
    self.abrir_modal_codigo_of = function (obj) {

        self.llenar_datos_historial(obj); 
        self.multaVO.id(obj.solicitud.id)
        self.titulo('Registrar codigo OF');
        $('#modal_codigo_of').modal('show');
    }
    self.abrir_modal_codigo_referencia = function (obj) {
        self.llenar_datos_historial(obj); 
        self.multaVO.id(obj.solicitud.id)
        self.titulo('Registrar codigo de referencia');
        $('#modal_codigo_referencia').modal('show');
    }
    self.abrir_modal_admin_soporte = function (obj) {
        self.multa_soporteVO.solicitud_id(obj.solicitud.id);
        self.titulo('Administrar pruebas de la solicitud');
        $('#modal_admin_soporte').modal('show');
        self.consultar_pruebas(obj.solicitud.id); 
        $('#soportes_multa').fileinput('reset');
        $('#soportes_multa').val('');
    }
    self.abrir_modal_admin_soporte_ver = function (obj) {
        self.multa_soporteVO.solicitud_id(obj.solicitud.id);
        self.titulo('Pruebas de la solicitud');
        $('#modal_admin_soporte_ver').modal('show');
        self.consultar_pruebas(obj.solicitud.id); 
    }
    self.abrir_modal_carta_solicitud = function (obj) {
        self.correspondencia_soporteVO.correspondencia_id(obj.solicitud.correspondenciasolicita.id);
        self.correspondencia_soporteVO.solicitud_id(obj.solicitud.id);
        self.titulo('Carta de la solicitud');
        $('#modal_carta_solicitud').modal('show');
        $('#soportes').fileinput('reset');
        $('#soportes').val('');
    } 

    self.abrir_modal_actualizar_estado = function (obj) {
        self.limpiar_multa_solicitud_historialVO();
        self.llenar_datos_historial(obj);
        self.multa_solicitud_historialVO.solicitud_id(obj.solicitud.id)
        self.consultar_solicitud_estado_posible(obj.estado.id);
        self.titulo('Actualizar estado de la multa');
        $('#modal_actualizar_estado').modal('show');
        $('#soportes').fileinput('reset');
        $('#soportes').val('');
    }   

    self.abrir_modal_actualizar_valor = function (obj) {
        self.limpiar_multa_solicitud_historialVO();
        self.llenar_datos_historial(obj);
        self.multaVO.id(obj.solicitud.id)
        self.titulo('Actualizar valor de la Imposicion');
        $('#modal_actualizar_valor_solicitud').modal('show');
    }   
    
    //exportar excel    
    self.exportar_excel=function(){

        // operador ternario
        var is_owner = self.solicitudes_elaboradas() == 1 ? 1 :
                self.solicitudes_solicitadas() == 1 ? 0 :
                self.solicitudes_consulta() == 1 ? 0 :
                0;

        location.href= path_principal+'/multa/'+"reporte_multa?dato="+self.filtro()
                                                    +"&estado="+self.estado_multa()
                                                    +"&solicitudes_elaboradas="+self.solicitudes_elaboradas()
                                                    +"&solicitudes_solicitadas="+self.solicitudes_solicitadas()
                                                    +"&solicitudes_consulta="+self.solicitudes_consulta()
                                                    +"&propietario="+is_owner
                                                    +"&macro_contrato="+(self.filtro_multaVO.mcontrato() || '')
                                                    +"&consecutivo="+(self.filtro_multaVO.consecutivo() || '')
                                                    +"&fecha_desde="+(self.filtro_multaVO.desde() || '')
                                                    +"&fecha_hasta="+(self.filtro_multaVO.hasta() || '')
                                                    +"&numero_contrato_obra="+(self.filtro_multaVO.numerocontrato() || '')
                                                    +"&contratista="+(self.filtro_multaVO.contratista_id() || '')
                                                    +"&solicitante="+(self.filtro_multaVO.solicitante_id() || '');
    } 
    // -------- DESCARGAR CARTA -------- // //
    self.descargar_carta=function(obj){
        console.log(obj)
            location.href=self.url_funcion_multa+"createWordSolicitud?correspondencia_id="+obj.solicitud.correspondenciasolicita.id;
    } 
    self.consultar_por_id = function (obj) {
        alert(obj.solicitud.correspondenciasolicita.id)
        /*path =path_principal+'/api/MultaSolicitud/'+proyecto_id+'/?format=json';
        RequestGet(function (results,count) {           
             
        }, path, parameter);*/     
     }   

    self.consultar_multas = function (pagina){
        self.estado_multa(self.filtro_multaVO.estado());
        self.consultar(pagina);
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }

	//funcion consultar multas que puede  ver la empresa
    self.consultar = function (pagina) {
        if (pagina > 0) {        

            // operador ternario
            var is_owner = self.solicitudes_elaboradas() == 1 ? 1 :
                    self.solicitudes_solicitadas() == 1 ? 0 :
                    self.solicitudes_consulta() == 1 ? 0 :
                    0;


            self.filtro($('#txtBuscar').val());

            sessionStorage.setItem("app_multa_filtro", self.filtro() || '');
            sessionStorage.setItem("app_multa_estado_multa", self.estado_multa() || '');
            // sessionStorage.setItem("solicitudes_elaboradas", self.solicitudes_elaboradas() || '');
            // sessionStorage.setItem("solicitudes_solicitadas", self.solicitudes_solicitadas() || '');
            // sessionStorage.setItem("solicitudes_consulta", self.solicitudes_consulta() || '');
            sessionStorage.setItem("is_owner", is_owner || '');


            // PARAMETROS DE BUSQUEDA DE LA MULTA
            sessionStorage.setItem("app_multa_mcontrato", self.filtro_multaVO.mcontrato() || '');      
            sessionStorage.setItem("app_multa_consecutivo", self.filtro_multaVO.consecutivo() || '');
            sessionStorage.setItem("app_multa_desde", self.filtro_multaVO.desde() || '');
            sessionStorage.setItem("app_multa_hasta", self.filtro_multaVO.hasta() || '');
            sessionStorage.setItem("app_multa_numerocontrato", self.filtro_multaVO.numerocontrato() || '');
            sessionStorage.setItem("app_multa_contratista_id", self.filtro_multaVO.contratista_id() || '');
            sessionStorage.setItem("app_multa_solicitante_id", self.filtro_multaVO.solicitante_id() || '');


            path = self.url+'MultaSolicitudEmpresa/';
            parameter = {   dato: self.filtro(), 
                            estado : self.estado_multa() ,
                            page: pagina , 
                            solicitudes_elaboradas : self.solicitudes_elaboradas() , 
                            solicitudes_solicitadas: self.solicitudes_solicitadas() , 
                            solicitudes_consulta: self.solicitudes_consulta() ,
                            propietario : is_owner,
                            // parametros del modal de busqueda
                            macro_contrato : self.filtro_multaVO.mcontrato() ,
                            consecutivo : self.filtro_multaVO.consecutivo() ,
                            fecha_desde : self.filtro_multaVO.desde() ,
                            fecha_hasta : self.filtro_multaVO.hasta() ,
                            numero_contrato_obra : self.filtro_multaVO.numerocontrato() ,
                            contratista : self.filtro_multaVO.contratista_id() ,
                            solicitante : self.filtro_multaVO.solicitante_id() ,
                        };

            RequestGet(function (datos, estado, mensage) {
                
                if (estado == 'ok' && datos.data.solicitudes!=null && datos.data.solicitudes.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data.solicitudes));
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }
    //funcion consultar proyectos que ppuede  ver la empresa
    self.consultar_elaboradas = function (pagina) {
        self.estado_multa(Elaborada);
        self.solicitudes_elaboradas(1);
        self.solicitudes_consulta('');
        self.consultar(pagina);
    }
    self.consultar_solicitadas = function (pagina) {
        self.estado_multa(Solicitada);
        self.solicitudes_solicitadas(1);
        self.solicitudes_consulta('');
        self.consultar(pagina);
    }	
    self.consultar_confirmadas = function (pagina) {
        self.estado_multa(Confirmada);
        self.consultar(pagina);
    }
    // //funcion guardar
     self.guardar=function(){

    	if (MultaViewModel.errores_multa().length == 0) {//se activa las validaciones
            if(self.multaVO.correspondenciasolicita_id()==0){
                peticion = 'POST';
                url_peticion = self.url+'MultaSolicitud/';
            }else{       
                peticion = 'PUT'; 
                url_peticion = self.url+'MultaSolicitud/'+ self.multaVO.correspondenciasolicita_id()+'/';         
            }

            self.multaVO.contenido(tinyMCE.get('echos').getContent({ format: 'text' }))
            self.multaVO.contenidoHtml(tinyMCE.get('echos').getContent())

            self.multaVO.clausula_afectada(tinyMCE.get('clausulas').getContent({ format: 'text' }))
            self.multaVO.clausula_afectadaHtml(tinyMCE.get('clausulas').getContent())


            self.multaVO.listado_eventos_asignados_id([]);
            self.multaVO.listado_eventos_asignados_dia([]);

            ko.utils.arrayForEach(self.listado_eventos_asignados(), function(d,index) {
                self.multaVO.listado_eventos_asignados_id.push(d.id);
                self.multaVO.listado_eventos_asignados_dia.push(d.dia);
            });


            if(self.multaVO.listado_eventos_asignados_id().length>0){
                var parametros={     
                        metodo: peticion,                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                              self.limpiar();
                              self.listado_eventos_asignados([]);
                            } 
                       },//funcion para recibir la respuesta 
                       url: url_peticion,
                       parametros:self.multaVO                        
                };
                RequestFormData(parametros);
            }else{

                 $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione un  evento para crear la solicitud.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }

         

            
        } else {
             MultaViewModel.errores_multa.showAllMessages();//mostramos las validacion
        }
     }
    self.generate_solicitud = function () { 
        if (MultaViewModel.errores_multa_generate().length == 0) {//se activa las validaciones
                $.confirm({
                    title: 'Confirmar!',
                    content: "<h4>Esta seguro que desea generar la solicitud seleccionada ?</h4>",
                    confirmButton: 'Si',
                    confirmButtonClass: 'btn-info',
                    cancelButtonClass: 'btn-danger',
                    cancelButton: 'No',
                    confirm: function() {

                        var parametros={     
                                metodo: 'POST',                
                               callback:function(datos, estado, mensaje){
                                    if (estado=='ok') {
                                        location.target='_blank';
                                        location.href="http://caribemar.sinin.co:8080/exportar/imposicion-multas?solicitud_id="+self.multaVO.id();
                                        self.consultar_solicitadas(1);
                                        $('#modal_generar').modal('hide');
                                    } 
                               },//funcion para recibir la respuesta 
                               url: path_principal+'/multa/generate_solicitud/' ,
                               parametros: { funcionario : self.generate_multaVO.firmaImposicion_id() 
                                            ,fechaDiligencia : self.generate_multaVO.fechaDiligencia()
                                            ,solicitud : self.multaVO.id() 
                                            ,usuario : self.usuarioActual }                       
                        };                        
                        Request(parametros);
                    }
                });
        }else{
           MultaViewModel.errores_multa_generate.showAllMessages();//mostramos las validacion 
        }        
    } 

    self.guardar_codigo_of = function () {
        if (MultaViewModel.errores_multa_codigo().length == 0) {//se activa las validaciones
                $.confirm({
                    title: 'Confirmar!',
                    content: "<h4>Esta seguro que desea registrar el codigo OF digitado ?</h4>",
                    confirmButton: 'Si',
                    confirmButtonClass: 'btn-info',
                    cancelButtonClass: 'btn-danger',
                    cancelButton: 'No',
                    confirm: function() {

                        var parametros={     
                                metodo: 'POST',                
                               callback:function(datos, estado, mensaje){
                                    if (estado=='ok') {
                                      self.consultar_confirmadas(1);
                                      $('#modal_codigo_of').modal('hide');
                                    } 
                               },//funcion para recibir la respuesta 
                               url: path_principal+'/multa/register_codigo_of/' ,
                               parametros: { codigoOF : self.codigo_multaVO.codigo() 
                                            ,fechaDiligencia : self.codigo_multaVO.fechaDiligencia()
                                            ,solicitud : self.multaVO.id() 
                                            ,usuario : self.usuarioActual }                       
                        };                        
                        Request(parametros);
                    }
                });
        }else{
           MultaViewModel.errores_multa_codigo.showAllMessages();//mostramos las validacion 
        } 
    } 

    self.guardar_codigo_referencia = function () {
        if (MultaViewModel.errores_multa_codigo().length == 0) {//se activa las validaciones
                $.confirm({
                    title: 'Confirmar!',
                    content: "<h4>Esta seguro que desea registrar el codigo de referencia digitado ?</h4>",
                    confirmButton: 'Si',
                    confirmButtonClass: 'btn-info',
                    cancelButtonClass: 'btn-danger',
                    cancelButton: 'No',
                    confirm: function() {

                        var parametros={     
                                metodo: 'POST',                
                               callback:function(datos, estado, mensaje){
                                    if (estado=='ok') {
                                      self.consultar(1);
                                      $('#modal_codigo_referencia').modal('hide');
                                    } 
                               },//funcion para recibir la respuesta 
                               url: path_principal+'/multa/register_codigo_referencia/' ,
                               parametros: { codigo : self.codigo_multaVO.codigo() 
                                            ,fechaDiligencia : self.codigo_multaVO.fechaDiligencia()
                                            ,solicitud : self.multaVO.id() 
                                            ,usuario : self.usuarioActual }                       
                        };                        
                        Request(parametros);
                    }
                });
        }else{
           MultaViewModel.errores_multa_codigo.showAllMessages();//mostramos las validacion 
        } 
    } 

    // se usa para subir el soporte de la carta de la solicitud
    self.guardar_carta_soporte_solicitud =function(){
        if(self.correspondencia_soporteVO.id()==0){

            if( (self.correspondencia_soporteVO.validaNombre() == true && self.correspondencia_soporteVO.nombre()!='' ) || (self.correspondencia_soporteVO.validaNombre()==false) ){

                if (self.correspondencia_soporteVO.soporte() != '') {//se activa las validaciones
                    var parametros={                     
                        callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                              self.consultar_elaboradas(self.paginacion.pagina_actual()); 
                              $('#modal_carta_solicitud').modal('hide');                             
                            }                     
                         },//funcion para recibir la respuesta 
                         url: path_principal+'/multa/upload-CartaSolicitudSoporte/',//url api
                         parametros:self.correspondencia_soporteVO                        
                    };
                    RequestFormData(parametros);
                }else{
                    mensajeInformativo('Seleccione un archivo.','Multa');
                }

            }else{
                mensajeInformativo('El nombre del archivo no puede estar vacio.','Soporte Correspondencia');
            }                
        }    
    }

     // //funcion subir archivo
    self.guardar_archivo_pruebas=function(){    

        var files=$('input[name="soportes_multa[]"]')[0].files;

        if(files.length>0){

            var formData= new FormData();
            formData.append('solicitud_id',ko.toJSON(self.multa_soporteVO.solicitud_id()));
            formData.append('nombre', '' );
            
            for (var i = 0; i < files.length ; i++) {      
                formData.append('soporte[]', files[i]);                     
            }

            var parametros={                     
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.consultar_pruebas(self.multa_soporteVO.solicitud_id()); 
                        $('#soportes_multa').fileinput('reset');
                        $('#soportes_multa').val('');                            
                    }                     
                 },//funcion para recibir la respuesta 
                 url: self.url+'MultaSolicitudSoporte/',//url api
                 parametros: formData                        
            };
            RequestFormData2(parametros);     

        }else{
            mensajeInformativo('Seleccione un archivo.','Solicitudes elaboradas');  
        }                                    
    }

    self.actualizar_estado_solicitud = function(){

        if (MultaViewModel.errores_multa_solicitud_historial().length == 0) {//se activa las validaciones
            var parametros={                     
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.consultar(1);
                        $('#modal_actualizar_estado').modal('hide');                     
                    }                     
                 },//funcion para recibir la respuesta 
                 url: self.url+'MultaSolicitudHistorial/',//url api
                 parametros:self.multa_solicitud_historialVO                        
            };
            RequestFormData(parametros);

        }else{
            MultaViewModel.errores_multa_solicitud_historial.showAllMessages();//mostramos las validacion 
        }
    }

    self.actualizar_valor_solicitud = function(){

        if (MultaViewModel.errores_multa_actualizar_valor().length == 0) {//se activa las validaciones
                $.confirm({
                    title: 'Confirmar!',
                    content: "<h4>Esta seguro que desea actualizar el valor de la imposición ?</h4>",
                    confirmButton: 'Si',
                    confirmButtonClass: 'btn-info',
                    cancelButtonClass: 'btn-danger',
                    cancelButton: 'No',
                    confirm: function() {

                        var parametros={     
                                metodo: 'POST',                
                               callback:function(datos, estado, mensaje){
                                    if (estado=='ok') {
                                      self.consultar(1);
                                      $('#modal_actualizar_valor_solicitud').modal('hide');
                                    } 
                               },//funcion para recibir la respuesta 
                               url: path_principal+'/multa/update-valorimpuesto/' ,
                               parametros: { valor : self.actualizar_valor_multaVO.valor_imposicion() 
                                            ,solicitud : self.multaVO.id() 
                                            ,usuario : self.usuarioActual 
                                            }                       
                        };                        
                        Request(parametros);
                    }
                });
        }else{
           MultaViewModel.errores_multa_actualizar_valor.showAllMessages();//mostramos las validacion 
        } 
    }

    self.consultar_solicitud_estado_posible = function (estado_actual) {
            path = self.url+'EstadosPosibles/';
            parameter = {  ignorePagination : 1 , actual : estado_actual  };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_estado_posibles(agregarOpcionesObservable(datos));                        
                } else {
                    self.listado_estado_posibles([]);                     
                }                
            }, path, parameter);        
    }
    //funcion consultar soportes
    self.consultar_pruebas = function (solicitud_id) {
                  
            path = self.url+'MultaSolicitudSoporte/';
            parameter = {  ignorePagination : 1 , solicitud : solicitud_id  };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                     self.mensajePorAsignar('')
                    self.listado_solicitud_pruebas(agregarOpcionesObservable(datos));                        
                } else {
                    self.listado_solicitud_pruebas([]);   
                    self.mensajePorAsignar(mensajeNoFound)                    
                }                
            }, path, parameter);        
    }
    self.eliminar_pruebas = function () {
         self.multa_soporteVO.soporte_id([]);  
         var count=0;
         ko.utils.arrayForEach(self.listado_solicitud_pruebas(), function(d) {
                if(d.eliminado()==true){
                   count=1;
                   self.multa_soporteVO.soporte_id.push(d.id);
                }
         });

        if(count==0){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione un soporte para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{
             var path = path_principal+'/multa/destroy-SolicitudSoporte/';
             var parameter = self.multa_soporteVO
             RequestAnularOEliminar("Esta seguro que desea eliminar los soportes seleccionados?", path, parameter, function () {
                 self.consultar_pruebas(self.multa_soporteVO.solicitud_id())
                 self.checkallSoportes(false);
             })
         }          
    }

    self.checkallSoportes = ko.observable(false);
    self.checkallSoportes.subscribe(function(value ){
        ko.utils.arrayForEach(self.listado_solicitud_pruebas(), function(d) {
                d.eliminado(value);
        }); 
    });

    //funcion consultar macro contratos
    self.consultar_macro_contrato = function () {                
            path = self.url_funcion_proyecto+'filtrar_proyectos/';
            parameter = { tipo : administraccion_de_recurso };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos.macrocontrato!=null && datos.macrocontrato.length > 0) {
                    self.listado_mcontrato(datos.macrocontrato);
                } else {
                    self.listado_mcontrato([]);
                }          
            }, path, parameter);       
    }
    self.filtro_multaVO.mcontrato.subscribe(function (val) {
        if(val!=""){
            self.consultar_contratista()
        }else{
            self.listado_contratista([]);
        }
    });
    //funcion consultar contratistas relacionados con el conttrato
    self.consultar_contratista = function () {                
            path = self.url_funcion_proyecto+'filtrar_proyectos/';
            if (self.filtro_multaVO.mcontrato()!= "" && self.filtro_multaVO.mcontrato()!= undefined ){
                parameter = { mcontrato : self.filtro_multaVO.mcontrato() };    
            }else{
                parameter = {};
            }            
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos.contratista!=null && datos.contratista.length > 0) {
                    self.listado_contratista(datos.contratista);
                } else {
                    self.listado_contratista([]);
                }          
            }, path, parameter);        
    }
    //funcion consultar solicitante de las multas
    self.consultar_solicitante = function () {                
            path = self.url+'empresa/';
            parameter = { sin_paginacion : 1 };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_solicitante(datos);
                } else {
                    self.listado_solicitante([]);
                }          
            }, path, parameter);        
    }
    //funcion consultar estados de las multas
    self.consultar_estado = function () {                
            path = self.url+'Estados/';
            parameter = { ignorePagination : 1 , aplicacion : self.app_multa};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_estado(datos);
                } else {
                    self.listado_estado([]);
                }          
            }, path, parameter);        
    }
    //funcion consultar departamentos
    self.consultar_parameter_select_registro = function () {                
        path = path_principal+'/correspondencia/parameter_select/';
        parameter = {  };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok') {
                self.listado_departamentos(datos.departamentos);
                self.listado_prefijos(datos.prefijos);
                self.listado_funcionarios_firma(datos.funcionarios_firman);
                self.listado_empresas(datos.empresas);
            }           
        }, path, parameter);        
    }
    self.departamentoEmpresa_id.subscribe(function (val) {
        if(val!=""){
            self.consultar_municipios(val , 2)   
        }else{
            self.listado_municipiosEmpresa([]);
        }   
    });
    self.multaVO.departamento_id.subscribe(function (val) {
        if(val!=""){
            self.consultar_municipios(val, 1)   
        }else{
            self.listado_municipios([]);
        }   
    });
    //funcion consultar municipios
    self.consultar_municipios = function (departamento_id, opcion) { 
        path = self.url+'Municipio/';
        parameter = { ignorePagination : 1 , id_departamento :  departamento_id };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {                    
                opcion==1?self.listado_municipios(datos):self.listado_municipiosEmpresa(datos);
            } else {
                self.listado_municipios([]);
                self.listado_municipiosEmpresa([]);
            }             
            cerrarLoading();
        }, path, parameter,undefined,false);         
    }

     //funcion consultar funcionario que elaboran la carta
    self.consultar_funcionarios_elaboran = function () {                
            path = self.url_app_parametrizacion+'usuarios_conFuncionariosEmpresa/';
            parameter = {  };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_funcionarios_elaboran(datos);
                } else {
                    self.listado_funcionarios_elaboran([]);
                }             
            }, path, parameter);        
    } 
    
    self.consultar_funcionariosCopia_enter = function (d,e) {
      if (e.which == 13) {
         self.consultar_funcionarios_copia();
      }
      return true;
    }
    self.consultar_funcionariosCopia_btn = function (d,e) {
         self.consultar_funcionarios_copia();
    }

    //funcion consultar funcionarios a copiar
    self.consultar_funcionarios_copia = function () {  
            var filtro = $("#filtro_DestinatarioCopia").val();                
            path = path_principal+'/correspondencia/usuariosCorrespondencia/';
            parameter = { empresa : self.filtro_empresaDestinatarioCopia() , dato : filtro };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_funcionarios_copia(datos);
                } else {
                    self.listado_funcionarios_copia([]);
                }             
            }, path, parameter);        
    }   

    self.asignar_copia = function(){
        id = $('#destinatarioCopia').val();
        text = $('#destinatarioCopia option:selected').text();

        if(id!=null){
            cont = 0;
            ko.utils.arrayForEach(self.listado_destinatarios_con_copia(), function(d,index) {
                  if(d.id==id){
                    cont = 1;
                  }
            });
            if(cont==0){
                self.listado_destinatarios_con_copia.push({"id":id , "nombres" : text})  
            }else{
               /*alert('ya existe registrado')*/
            }            
        }        
    }
    self.quitar_copia = function(){
        id = $('#destinatarioConCopia').val();
        text = $('#destinatarioConCopia option:selected').text();

        if(id!=null){
          ko.utils.arrayForEach(self.listado_destinatarios_con_copia(), function(d,index) {                  
                  if(d.id==id){
                    self.listado_destinatarios_con_copia().splice(index, 1);
                  }else{
                    self.newArray.push({"id":d.id , "nombres" : d.nombres})
                  }                
          });
          self.listado_destinatarios_con_copia([]);
          self.listado_destinatarios_con_copia(self.newArray());
        }        
    } 
    //funcion consultar proyectos que ppuede  ver la empresa
    self.consultar_contratos = function () {       
        self.filtro_contratoVO.filtro($('#filtroContrato').val());
        path = path_principal+'/api/Contrato/?format=json';
        parameter = {dato: self.filtro_contratoVO.filtro(),
                                /* id = 8 ; es un contrato de obra asociado a proyectos*/
                                id_tipo:self.filtro_contratoVO.id_tipo(8),
                                id_estado:self.filtro_contratoVO.id_estado(),
                                sin_paginacion : 1,
                                liteD : 3 ,
                                noAsignado : 1
                     };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensajeListadoContrato('');
                self.listado_contrato(agregarOpcionesObservable(datos));  

            } else {
                self.listado_contrato([]);
                self.mensajeListadoContrato(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);       
    } 
    self.consultar_contratos_btn = function(){
        self.consultar_contratos();
    }
    self.consultar_contratos_enter = function(d,e){
        if (e.which == 13) {
            self.consultar_contratos();
        }
        return true;
    }
    self.filtro_contratoVO.id_estado.subscribe(function (val) {
        self.consultar_contratos();
    });

    self.asignar_contrato = function(obj){
        if(obj.contratante){
            self.multaVO.contrato_id(obj.id);
            $("#contratoAsignado").val(obj.numero+' - '+obj.nombre)
            $('#modal_contratos').modal('hide');
            self.filtro_empresaDestinatario(obj.contratante.id);
            self.consultar_funcionarios();
        }       
    }
    self.consultar_funcionarios_enter = function (d,e) {
      if (e.which == 13) {
         self.consultar_funcionarios();
      }
      return true;
    }
    self.consultar_funcionarios_btn = function (d,e) {
      self.consultar_funcionarios();
    }
    //funcion consultar funcionario a enviar carta
    self.consultar_funcionarios = function () {  
            var filtro = $("#filtro_Destinatario").val();              
            path = self.url_app_parametrizacion+'usuariosConFuncionarios/';
            parameter = { empresa : self.filtro_empresaDestinatario() , dato : filtro };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_funcionarios(datos);
                } else {
                    self.listado_funcionarios([]);
                }             
            }, path, parameter);        
    }

    /*------- EVENTOS DE LA MULTA-----------------------------------------------*/
    self.listado_eventos = ko.observableArray([]);
    self.conjunto_evento = ko.observable('');
    self.mensajeListadoEventos=ko.observable('');

    self.conjunto_evento.subscribe(function (val) {
        self.consultar_eventos();
    });

    self.consultar_eventos = function () {       
        self.filtro_contratoVO.filtro($('#filtroContrato').val());
        path = path_principal+'/api/MultaEvento/?format=json';
        parameter = { conjunto:self.conjunto_evento() , ignorePagination : 1 };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensajeListadoEventos('');
                self.listado_eventos(agregarOpcionesObservable(datos));  

            } else {
                self.listado_eventos([]);
                self.mensajeListadoEventos(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);       
    } 

    self.asignar_evento = function(obj){

        id = obj.id;
        evento = obj.nombre;
        valor = obj.valor;
        dia = $("#D"+id).val();

        if(id!=null){
            cont = 0;
            ko.utils.arrayForEach(self.listado_eventos_asignados(), function(d,index) {
                  if(d.id==id){
                    cont = 1;
                  }
            });
            if(cont==0){
                oldValue = self.multaVO.valorSolicitado();

                if(self.multaVO.valorSolicitado()==""){
                    self.multaVO.valorSolicitado('0');
                }

                newValue = parseInt(self.multaVO.valorSolicitado())+(parseInt(valor)*parseInt(dia));
                self.multaVO.valorSolicitado(newValue);

                self.listado_eventos_asignados.push({"id":id , "nombre" : evento , "valor" : valor , "dia" : dia})  
            }else{
              /*alert('ya existe registrado')*/
            }            
        }    
    }

    self.eliminar_evento =function(obj){
        self.newArray = ko.observableArray([]);
        id = obj.id;

        if(id!=null){
          ko.utils.arrayForEach(self.listado_eventos_asignados(), function(d,index) {
                  
                  if(d.id==id){
                    oldValue = self.multaVO.valorSolicitado();
                    
                    if(self.multaVO.valorSolicitado()==""){
                        self.multaVO.valorSolicitado('0');
                    }


                    newValue = parseInt(self.multaVO.valorSolicitado())-(parseInt(obj.valor)*parseInt(obj.dia));
                    self.multaVO.valorSolicitado(newValue);

                    self.listado_eventos_asignados().splice(index, 1);
                  }else{
                    self.newArray.push({"id":d.id , "nombre" : d.nombre , "valor" : d.valor , "dia" : d.dia})
                  }                
          });
          self.listado_eventos_asignados([]);
          self.listado_eventos_asignados(self.newArray());
        }
    }
    /* PRESENTAR RESPUESTA A DESCARGO */
    self.respuesta_descargoVO.departamento_id.subscribe(function (val) {
        if(val!=""){
            self.consultar_municipios(val, 1)   
        }else{
            self.listado_municipios([]);
        }   
    });

    self.set_respuesta_descargo_id = function (solicitud_id) {
        self.respuesta_descargoVO.id(solicitud_id)
    }

    self.guardar_respuesta_descargo = function () {

        if (MultaViewModel.errores_multa_respuesta_descargo().length == 0) {//se activa las validaciones*/

            self.respuesta_descargoVO.destinatarioCopia([])
            if(self.listado_destinatarios_con_copia().length>0){
               ko.utils.arrayForEach(self.listado_destinatarios_con_copia(), function(d,index) {
                      self.respuesta_descargoVO.destinatarioCopia.push(d.id)
                });
            }
            self.respuesta_descargoVO.contenido(tinyMCE.activeEditor.getContent({ format: 'text' }))
            self.respuesta_descargoVO.contenidoHtml(tinyMCE.activeEditor.getContent())
          
            peticion = '';
            url_api = '';
            if(self.respuesta_descargoVO.id()>0){
                peticion = 'POST';
                url_api  = self.url_funcion_multa+'create-respuesta-descargo/';
            }

            var parametros={     
                metodo: peticion,                
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        /*console.log(datos)*/
                        self.respuesta_descargoVO.correspondenciadescargo_id(datos.correspondenciadescargo_id);
                        /* IF SI ES GUARDAR O SINO SE ACTUALIZA*/

                    } 
                },//funcion para recibir la respuesta 
                url: url_api,
                parametros:self.respuesta_descargoVO                        
            };
            RequestFormData(parametros);
        } else {
             MultaViewModel.errores_multa_respuesta_descargo.showAllMessages();
        }
    }

    self.descargar_carta_respuesta_descargo=function(solicitud_id){
        location.href=self.url_funcion_multa+"generate-format-respuestaDescargo?solicitud_id="+solicitud_id;
    } 

    self.descargar_formato_of = function(solicitud_id){
        location.href=self.url_funcion_multa+"generate-format-OF?solicitud_id="+solicitud_id;
    }


}

var multa = new MultaViewModel();

$('#txtBuscar').val(sessionStorage.getItem("app_multa_filtro"));
multa.filtro_multaVO.mcontrato(sessionStorage.getItem("app_multa_mcontrato"));      
multa.filtro_multaVO.consecutivo(sessionStorage.getItem("app_multa_consecutivo"));
multa.filtro_multaVO.desde(sessionStorage.getItem("app_multa_desde"));
multa.filtro_multaVO.hasta(sessionStorage.getItem("app_multa_hasta"));
multa.filtro_multaVO.numerocontrato(sessionStorage.getItem("app_multa_numerocontrato"));
multa.filtro_multaVO.contratista_id(sessionStorage.getItem("app_multa_contratista_id"));
multa.filtro_multaVO.solicitante_id(sessionStorage.getItem("app_multa_solicitante_id"));


MultaViewModel.errores_multa = ko.validation.group(multa.multaVO);
MultaViewModel.errores_multa_generate = ko.validation.group(multa.generate_multaVO);
MultaViewModel.errores_multa_codigo = ko.validation.group(multa.codigo_multaVO);
MultaViewModel.errores_multa_solicitud_historial = ko.validation.group(multa.multa_solicitud_historialVO);
MultaViewModel.errores_multa_actualizar_valor = ko.validation.group(multa.actualizar_valor_multaVO);
MultaViewModel.errores_multa_respuesta_descargo = ko.validation.group(multa.respuesta_descargoVO);
ko.applyBindings(multa);