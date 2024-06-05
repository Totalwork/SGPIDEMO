function MisCompromisosViewModel() {

	var self = this;
	self.listado_compromisos=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');

    self.url=path_principal+'/api/';
    self.url_funcion=path_principal+'/actareunion-compromiso/'; 

    self.mensajecompromisoHistorial = ko.observable([]);
    self.listado_compromisoHistorial = ko.observable([]);
    self.participantes_internos = ko.observable([]);

    self.cumplimientoVO = {
        id:ko.observable(0),
        requiere_soporte:ko.observable(''),
        motivo:ko.observable(''),
        soporte:ko.observable(''),

    };

    self.estado = {
        true:ko.observable(true),
        false:ko.observable(false),
    };

    self.actaVO ={
        id: ko.observable(0),
        consecutivo: ko.observable(''),
        tema_principal: ko.observable(''),
        controlador_actual_nombre: ko.observable(''),
        usuario_organizador_nombre: ko.observable(''),
        fecha: ko.observable(''),

        estado_nombre: ko.observable(''),
        estado_color: ko.observable(''),
        estado_icono: ko.observable(''),
        
    };

    self.compromisoVO ={
        id:ko.observable(0),
        acta_id:ko.observable($('#acta_id').val()),
        descripcion:ko.observable(''),
        supervisor:ko.observable(''),
        fecha_compromiso:ko.observable(''),
        fecha_cumplimiento:ko.observable(''),        
        responsable:ko.observable(''),        
        responsable_interno:ko.observable(''),
        estado_icono:ko.observable(''),
        estado_color:ko.observable(''),
        estado_nombre:ko.observable(''),

    };

    self.filtro_acta_compromisoVO = {            
        dato:ko.observable(''),
        desde:ko.observable(''),
        hasta:ko.observable(''),
        supervisor_id:ko.observable(''),
        estado_id:ko.observable(''),
        prorroga:ko.observable(false)
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
        },
        totalRegistrosBuscados:ko.observable(0)
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {    
       self.consultar(pagina);
    });    

    self.abrir_modal = function(){
        self.titulo('Registrar miscompromisos');
        self.limpiar();
        $('#modal_acciones').modal('show');
    }


    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }

    self.abrir_modal_busqueda=function(){
        self.titulo('Filtro Compromisos');


        self.filtro_acta_compromisoVO.supervisor_id(sessionStorage.getItem("mis_compromiso_supervisor_id"));             
        self.filtro_acta_compromisoVO.estado_id(sessionStorage.getItem("mis_compromiso_estado_id"));
        self.filtro_acta_compromisoVO.desde(sessionStorage.getItem("mis_compromiso_desde"));    
        self.filtro_acta_compromisoVO.hasta(sessionStorage.getItem("mis_compromiso_hasta"));                
        self.filtro_acta_compromisoVO.prorroga(sessionStorage.getItem("mis_compromiso_prorroga"));       
        $('#modal_filtro').modal('show');
    }

    self.setColorIconoFiltro = function (){        
        var supervisor_id = sessionStorage.getItem('mis_compromiso_supervisor_id')||'';
        var estado_id = sessionStorage.getItem('mis_compromiso_estado_id')||'';
        var desde = sessionStorage.getItem('mis_compromiso_desde')||'';
        var hasta = sessionStorage.getItem('mis_compromiso_hasta')||'';
        var prorroga = sessionStorage.getItem('mis_compromiso_prorroga')||'';

        if (supervisor_id != '' || prorroga != ''  || estado_id !='' || desde != '' || hasta != '') {
            //alert('filtro');
            $('#iconoFiltro').addClass("filtrado");
        }else{
            //alert('no filtro');
            $('#iconoFiltro').removeClass("filtrado");
        }
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro_acta_compromisoVO.dato($('#txtBuscar').val());
            self.cargar(1);
        }
        return true;
    }
    
    self.consultar = function(pagina){
        // alert(pagina);
        if (pagina>0){
            // alert(self.filtro_acta_compromisoVO.prorroga());
            sessionStorage.setItem('mis_compromiso_supervisor_id', self.filtro_acta_compromisoVO.supervisor_id()||'');
            sessionStorage.setItem('mis_compromiso_estado_id', self.filtro_acta_compromisoVO.estado_id()||'');
            sessionStorage.setItem('mis_compromiso_desde', self.filtro_acta_compromisoVO.desde()||'');
            sessionStorage.setItem('mis_compromiso_hasta', self.filtro_acta_compromisoVO.hasta()||'');
            sessionStorage.setItem('mis_compromiso_prorroga', self.filtro_acta_compromisoVO.prorroga()||'');       
            self.cargar(pagina);
        }
        
    }

    self.cargar = function(pagina){
        if(pagina>0){
            self.filtro_acta_compromisoVO.dato($('#txtBuscar').val())
            sessionStorage.setItem("mis_compromiso_busqueda", self.filtro_acta_compromisoVO.dato() || '');

            var supervisor_id =  sessionStorage.getItem('mis_compromiso_supervisor_id')||'';
            var estado_id = sessionStorage.getItem('mis_compromiso_estado_id')||'';
            var desde =  sessionStorage.getItem('mis_compromiso_desde')||'';
            var hasta =  sessionStorage.getItem('mis_compromiso_hasta')||'';
            var prorroga = sessionStorage.getItem('mis_compromiso_prorroga')||'';

            path = path_principal + '/api/actareunion-compromiso/?format=json';
            parameter = {
                usuario_responsable_id:$('#usuario_id').val(),
                page:pagina,
                lite:1,
                supervisor_id: supervisor_id,
                fecha_compromiso_desde: desde,
                fecha_compromiso_hasta: hasta,
                prorroga: prorroga,
                estado_id: estado_id,
                dato: self.filtro_acta_compromisoVO.dato(),
            };
            RequestGet(function(datos,estado,mensaje) {
                    if(estado=='ok' && datos.data!=null && datos.data.length>0){                                    
                        self.listado_compromisos(datos.data);
                        self.mensaje('');
                    }else{
                        self.mensaje(mensajeNoFound);
                        self.listado_compromisos([]);
                    }
                    $('#modal_filtro').modal('hide');                   
                    self.llenar_paginacion(datos,pagina);
                    self.setColorIconoFiltro();
                    cerrarLoading();
            }, path, parameter,undefined,false);
        }
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
                            self.consultar(1);
                            $('#modal_acciones_cumplimiento').modal('hide');
                            self.limpiarCumplimiento();
                            
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
    
    self.registrar_cumplimiento_compromiso = function(obj){
        self.titulo('Registrar cumplimiento del compromiso');
        self.limpiarCumplimiento(obj); 
        $('#modal_acciones_cumplimiento').modal('show');

        $('#label_fecha_limite').text(obj.fecha_compromiso);
        $('#label_fecha_proxima').text(obj.fecha_proximidad);
        $('#label_descripcion').text(obj.descripcion);
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
    
    self.ver_soporte_cumplimiento = function(){
        window.open(path_principal+"/actareunion/ver-soporte-compromiso/?id="+ self.compromisoVO.id(), "_blank");
    }

    self.consultar_por_detalles = function(obj){
        $('#modal_ver_detalles').modal('show');
        self.titulo('Ver detalles');
        self.compromisoVO.descripcion(obj.descripcion);
        self.compromisoVO.supervisor(obj.supervisor.persona.nombres+' '+obj.supervisor.persona.apellidos);

        if(obj.responsable_interno){
            self.compromisoVO.responsable(obj.usuario_responsable.persona.nombres+' '+obj.usuario_responsable.persona.apellidos)
        }else{
            self.compromisoVO.responsable(obj.participante_responsable.persona.nombres+' '+obj.participante_responsable.persona.apellidos)
        }       

        self.compromisoVO.responsable_interno(obj.responsable_interno);
        self.compromisoVO.fecha_compromiso(obj.fecha_compromiso);
        if (obj.cumplimiento){
            self.compromisoVO.fecha_cumplimiento(obj.cumplimiento.fecha_cumplimiento);
        }else{
            self.compromisoVO.fecha_cumplimiento(null);
        }
        

        self.compromisoVO.estado_icono(obj.estado.icono);
        self.compromisoVO.estado_color(obj.estado.color);
        self.compromisoVO.estado_nombre(obj.estado.nombre);

        path = path_principal + '/api/actareunion-acta/'+obj.acta.id+'/?format=json';
        parameter = {
            lite:1,
        };
        RequestGet(function(datos,mensaje,estado) {
                // alert(estado);
                if(datos!=null){  
                    self.actaVO.id(datos.id);                               
                    self.actaVO.consecutivo(datos.consecutivo);
                    self.actaVO.tema_principal(datos.tema_principal);
                    self.actaVO.usuario_organizador_nombre(datos.usuario_organizador.persona.nombres+' '+datos.usuario_organizador.persona.apellidos);
                    self.actaVO.controlador_actual_nombre(datos.controlador_actual.persona.nombres+' '+datos.controlador_actual.persona.apellidos);
                    self.actaVO.estado_icono(datos.estado.icono);
                    self.actaVO.estado_color(datos.estado.color);
                    self.actaVO.estado_nombre(datos.estado.nombre);
                    self.actaVO.fecha(datos.fecha);
                    if(datos.soporte){
                        $('#detalle_soporte_archivo').show();
                        
                    }
                }                
                cerrarLoading();
        }, path, parameter,undefined,false);


        
    }

    self.ver_soporte = function(){    
        window.open(path_principal+"/actareunion/ver-soporte-acta/?id="+ self.actaVO.id(), "_blank");       
    }

    self.exportar_excel = function(){
    }

    // self.url_pagina_anterior=ko.observable(true);
    // self.url_session =  function () { 
    //     var urlanterior = ""+document.referrer;  
    //     if(urlanterior==''){
    //         self.url_pagina_anterior(true);
    //     }else{            
    //         self.url_pagina_anterior(false);
    //     }   
    //     // alert(urlanterior);    
    // };


    
}

var miscompromisos = new MisCompromisosViewModel();
$('#txtBuscar').val(sessionStorage.getItem("app_acta_reunion_dato"))
miscompromisos.cargar(1);
// miscompromisos.url_session();
// MisCompromisosViewModel.errores_compromisos = ko.validation.group(miscompromisos.compromisoVO);
ko.applyBindings(miscompromisos);