var choices = [
    { id: 'Vacio', name:"[Seleccione...]"},
    { id: 'Si', name: "Si" },
    { id: 'No', name: "No"},
    { id: 'No aplica', name: "No aplica"}
    ];

function ProcesoRelacionDatosViewModel(){
	var self=this;
	self.listado=ko.observableArray([]);
    self.listadoSoporte=ko.observableArray([]);
    self.listadoVinculados=ko.observable([]);
    self.listadoResponsables = ko.observable([]);
    self.listadoResponsablesDisponibles = ko.observable([]);
	self.listadoResponsablesAsignados = ko.observable([]);
    self.listadoEmpresas = ko.observable([]);
    self.url=path_principal+'/api/procesoRelacionDato/';
	
	self.filtro=ko.observable('');
    self.choices= ko.observableArray(choices);
	self.etiquetaAvanceKo = ko.observable('');
    self.avanceKo = ko.observable('');
    self.titulo=ko.observable('');
    self.habilitar_campos=ko.observable(true);
	
	
	self.mensaje=ko.observable('');
    self.mensajeSoporte=ko.observable('');  
    self.mensajeResponsables = ko.observable('');  
    self.mensajeResponsablesDisponibles = ko.observable('');  
	self.mensajeResponsablesAsignados = ko.observable('');
	self.buscado_rapido=ko.observable(false);
    self.id=ko.observable(0);

    self.soporteVO={
        id:ko.observable(0),
        procesoRelacionDato_id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del soporte por favor' } }),
        documento:ko.observable('').extend({ validation: { validator: validar_soporte, message: '(*) Seleccione el archivo por favor.' } })
    }

    function validar_soporte(val) {

     if(self.id() > 0)
      return true;
     else
      return self.id() == 0 && val!=null && val!='';
    }
	

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (id) {

        if (id > 0) {
        	//alert('entre aqui' + pagina); 
            self.buscado_rapido(true);
            path = self.url + '?format=json&ignorePagination=1';
            parameter = {
                procesoRelacion: id,
                vinculados: 1
            };

            RequestGet(function(datos, estado, mensage) {
            	//alert(datos.listado);
                if (estado == 'ok' && datos.listado != null && datos.listado.length > 0) {
                    self.mensaje('');
                    self.listado(datos.listado);
                    
                    if (datos.vinculados != null && datos.vinculados.length > 0){
                        self.listadoVinculados(datos.vinculados);
                    }else{
                        self.listadoVinculados([]);    
                    }
                    self.etiquetaAvanceKo(datos.etiquetaPorcentaje);
                    self.avanceKo(datos.porcentaje);

                } else {
                    self.listado([]);
                    //self.proveedores([]);
                    self.listadoVinculados([]);
                    self.mensaje(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                    self.etiquetaAvanceKo('0');
                    self.avanceKo(0.0);

                }
                //self.llenar_paginacion(datos, pagina);

                cerrarLoading();
            }, path, parameter,undefined,false);
        }

    }
    self.consultarSoportes = function (procesoRelacionDato) {

        if (procesoRelacionDato > 0) {
            //alert('entre aqui' + pagina); 
            //self.buscado_rapido(true);
            path = path_principal+'/api/soporteProcesoRelacionDato/' + '?format=json';
            parameter = {
                procesoRelacionDato: procesoRelacionDato,
            };
            RequestGet(function(datos, estado, mensage) {
                //alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensajeSoporte('');
                    self.listadoSoporte(datos.data);
                } else {
                    self.listadoSoporte([]);
                    self.mensajeSoporte('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron soportes cargados al item.</div>'); //mensaje not found se encuentra el el archivo call-back.js
                }
                //self.llenar_paginacion(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }

    }
    self.consultarResponsablesProyecto = function (procesoRelacion) {

        if (procesoRelacion > 0) {
            //alert('entre aqui' + pagina); 
            //self.buscado_rapido(true);
            path = path_principal+'/api/procesoRelacion/' + '?format=json';
            parameter = {
                procesoRelacionId: procesoRelacion,
                responsables:1
            };
            RequestGet(function(datos, estado, mensage) {
                //alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensajeResponsables('');
                    self.listadoResponsables(datos.data);
                } else {
                    self.listadoResponsables([]);
                    self.mensajeResponsables('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron soportes cargados al item.</div>'); //mensaje not found se encuentra el el archivo call-back.js
                }
                //self.llenar_paginacion(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }

    }
    self.cambioEmpresa = function(){
        self.consultarFuncionariosDisponibles($('#txtProcesoRelacionDatoId').val());
    }
    self.asignarNotificacion = function(){
        var selected=[];
        $('#divResponsablesDisponibles input:checked').each(function(){
            selected.push($(this).attr('id'));
        });        
        if (selected.length>0){
            self.mensajeResponsablesDisponibles('');
            var path =path_principal+'/proceso/detalleSeguimientoProcesoDatos/asignarNotificacion/';
            var parameter = { 
                lista: selected, 
                procesoRelacionDatoId: $('#txtProcesoRelacionDatoId').val() 
            };
            var parametros = {
                callback:function(datos, estado, mensaje){
                    if (estado =='ok'){
                        self.consultarFuncionariosDisponibles($('#txtProcesoRelacionDatoId').val());
                        self.consultarFuncionariosAsignados($('#txtProcesoRelacionDatoId').val(),'',$('#txtBuscarAsignados').val());
                    }
                },
                url:path,
                parametros:parameter
            };
            Request(parametros);
        }else{
            self.mensajeResponsablesDisponibles('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>Debe seleccionar los funcionarios que se requiere notificar</div>');
        }        
    }

    self.cambioEmpresaAsignados = function(){
        self.consultarFuncionariosAsignados($('#txtProcesoRelacionDatoId').val(),'',$('#txtBuscarAsignados').val());

    }
    self.quitarNotificacion = function(){
        var selected=[];
        $('#divResponsablesAsignados input:checked').each(function(){
            selected.push($(this).attr('id'));
        });        
        if (selected.length>0){
            self.mensajeResponsablesAsignados('');
            var path =path_principal+'/proceso/detalleSeguimientoProcesoDatos/quitarNotificacion/';
            var parameter = { 
                lista: selected, 
                procesoRelacionDatoId: $('#txtProcesoRelacionDatoId').val() 
            };
            var parametros = {
                callback:function(datos, estado, mensaje){
                    if (estado =='ok'){
                        if ($('#txtBuscarDisponibles').val()!='' || $('#cmbEmpresas').val()!=''){
                            self.consultarFuncionariosDisponibles($('#txtProcesoRelacionDatoId').val());
                        }
                        self.consultarFuncionariosAsignados($('#txtProcesoRelacionDatoId').val(),'',$('#txtBuscarAsignados').val());
                    }
                },
                url:path,
                parametros:parameter
            };
            Request(parametros);
        }else{
            self.mensajeResponsablesAsignados('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>Debe seleccionar los funcionarios que se requiere quitar de la notificar</div>');
        }        
    }
    self.consultarFuncionariosDisponibles = function (procesoRelacionDato){
        if (procesoRelacionDato > 0){
           path = path_principal+'/api/NotificacionVencimiento/' + '?format=json';
            parameter = {
                procesoRelacionDatoId: procesoRelacionDato,
                funcionariosNoAsignados: 1,
                empresaId: $('#cmbEmpresas').val(),
                nombreFuncionario: $('#txtBuscarDisponibles').val()
            };
            RequestGet(function(datos, estado, mensage) {
                
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensajeResponsablesDisponibles('');
                    self.listadoResponsablesDisponibles(datos.data);
                } else {
                    self.listadoResponsablesDisponibles([]);
                    self.mensajeResponsablesDisponibles('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron funcionarios disponibles para asignar la notificacion.</div>'); //mensaje not found se encuentra el el archivo call-back.js
                }
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }
    self.consultarFuncionariosAsignados = function (procesoRelacionDato,empresas,nombreFuncionario){
        if (procesoRelacionDato > 0) {
            //alert('entre aqui' + pagina); 
            //self.buscado_rapido(true);
            path = path_principal+'/api/NotificacionVencimiento/' + '?format=json';
            parameter = {
                procesoRelacionDatoId: procesoRelacionDato,
                empresas:empresas,
                empresaId: $('#cmbEmpresasAsignados').val(),
                nombreFuncionario: nombreFuncionario
            };
            RequestGet(function(datos, estado, mensage) {
                
                if (estado == 'ok' && datos.data.notificaciones != null && datos.data.notificaciones.length > 0) {
                    self.mensajeResponsablesAsignados('');
                    self.listadoResponsablesAsignados(datos.data.notificaciones);
                } else {
                    self.listadoResponsablesAsignados([]);
                    self.mensajeResponsablesAsignados('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron notificaciones configuradas.</div>'); //mensaje not found se encuentra el el archivo call-back.js
                }
                //alert('valor del cmb: ' + empresas);
                if (empresas == 1){
                    if (estado == 'ok' && datos.data.empresas != null && datos.data.empresas.length > 0){
                        self.listadoEmpresas(datos.data.empresas);
                    }else{
                        self.listadoEmpresas([]);
                    }
                }
                //self.llenar_paginacion(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }       
    }
    self.consulta_enter = function (d, e){
        if (e.which == 13) { 
            self.consultarFuncionariosDisponibles($('#txtProcesoRelacionDatoId').val());
        }
        return true;
    }
    self.cmdConsultarFuncionariosDisponibles = function(){
        self.consultarFuncionariosDisponibles($('#txtProcesoRelacionDatoId').val());    
    }
    self.consulta_enter_asignados = function (d, e){
        if (e.which == 13) { 
            self.consultarFuncionariosAsignados($('#txtProcesoRelacionDatoId').val(),'',$('#txtBuscarAsignados').val());
        }
        return true;
    } 
    self.cmdConsultarFuncionariosAsignados = function(){
        self.consultarFuncionariosAsignados($('#txtProcesoRelacionDatoId').val(),'',$('#txtBuscarAsignados').val());
    }   



    self.consultarSoporte_por_id = function (id,nombre,procesoRelacionDato) {
       self.soporteVO.id(id);
       self.soporteVO.nombre(nombre);
       self.soporteVO.procesoRelacionDato_id(procesoRelacionDato);
       self.soporteVO.documento('');
       self.id(id);
     }


    self.guardarCambios = function (procesoRelacion){
        var id=[];
        var valor;
        var observacion;
        var vencimiento;
        var datos=[];
        $('.id').each(function(){
            id.push($(this).attr('value'));
        });
       
        for (var i=0;i<id.length;i++){
            if ($("#txtValor"+id[i]).val() ==''){
                valor='Vacio';
            }else{
                valor=$("#txtValor"+id[i]).val();
            }
            if ($("#txtObservacion"+id[i]).val()==''){
                observacion=null;
            }else{
                observacion=$("#txtObservacion"+id[i]).val();
            }
            if ($("#txtVencimiento"+id[i]).val()==''){
                vencimiento=null;
            }else{
                vencimiento=$("#txtVencimiento"+id[i]).val()
            }

            datos.push('{\'id\':'+id[i]+',\'fechaVencimiento\':\''+vencimiento+'\',\'valor\':\''+valor+
                '\',\'observacion\':\''+observacion+'\',\'soporteObligatorio\':'+
                $("#txtSoporteObligatorio"+id[i]).val()+'}');
            
        }
        path =path_principal+'/proceso/detalleSeguimientoProcesoDatos/guardarCambios/';
        parameter = { lista: datos, procesoRelacion: procesoRelacion };
        var parametros = {
            callback:function(datos, estado, mensaje){
                if (estado =='ok'){
                    self.consultar(procesoRelacion);                    
                }else{
                    self.mensaje('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>Se presentaron errores al guardar los cambios.</div>');
                }
            },
            url:path,
            parametros:parameter
        };
        Request(parametros);

    }
    self.guardarSoporte=function(){
        if (ProcesoRelacionDatosViewModel.errores_soporte().length == 0) {
            // self.soporteVO.documento($('#archivo')[0].files[0]);
            if(self.soporteVO.id()==0){
                var parametros={                     
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultarSoportes($('#txtProcesoRelacionDato').val());
                            self.limpiar();
                            self.consultar($('#txtProcesoRelacionId').val());
                        }else{
                            self.mensajeSoporte('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>Se presentaron errores al guardar el soporte.</div>'); //mensaje not found se encuentra el el archivo call-back.js                           
                        }                        
                                
                    },//funcion para recibir la respuesta 
                             url:path_principal+'/api/soporteProcesoRelacionDato/',//url api
                             parametros:self.soporteVO                        
                };
                        //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);

            }else{
                var parametros={     
                    metodo:'PUT',                
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultarSoportes($('#txtProcesoRelacionDato').val());
                            self.limpiar();
                        }  
                    },//funcion para recibir la respuesta 
                    url:path_principal+'/api/soporteProcesoRelacionDato/'+self.soporteVO.id()+'/',
                    parametros:self.soporteVO                        
                };

                RequestFormData(parametros);
                
            }
        }else{
            ProcesoRelacionDatosViewModel.errores_soporte.showAllMessages();//mostramos las validacion
        }

    }


   self.paginacion = {
        pagina_actual: ko.observable(0),
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
        if (self.buscado_rapido()) {
            self.consultar($('#txtProcesoRelacionId').val());
          }
          // else{
          //   self.consultar_por_filtros(pagina);
          // }       
    });

    self.abrir_modal = function(procesoRelacionDato,usuarioEditor) {
        self.titulo('Soportes del item');
        self.habilitar_campos(true);
        $('#modal_soportes').modal('show');
        //$('#txtProcesoRelacionDato').val(procesoRelacionDato);
        self.soporteVO.procesoRelacionDato_id(procesoRelacionDato);
        self.consultarSoportes(procesoRelacionDato);
        self.id(0);

    }
    self.abrir_modal_soloLectura = function(procesoRelacionDato) {
        self.titulo('Soportes del item');
        //self.habilitar_campos(true);
        $('#modal_soportes_soloLectura').modal('show');
        //$('#txtProcesoRelacionDato').val(procesoRelacionDato);
        self.soporteVO.procesoRelacionDato_id(procesoRelacionDato);
        self.consultarSoportes(procesoRelacionDato);
        self.id(0);

    }

    self.abrir_modal_responsablesProyecto = function(procesoRelacion) {
        self.titulo('Responsables del proyecto/contrato');
        $('#modal_soportes_responsablesProyecto').modal('show');
        self.consultarResponsablesProyecto(procesoRelacion);
        //self.id(0);

    }
    

    self.abrir_modal_defineResponsablesProyecto = function(procesoRelacionDato,escritura) {
        self.titulo('Definir los funcionarios a los cuales se les notifica por vencimiento y/o cumplimiento');
        $('#modal_defineResponsablesProyecto').modal('show');
        self.consultarFuncionariosAsignados(procesoRelacionDato,1,'');
        $('#txtProcesoRelacionDatoId').val(procesoRelacionDato);
        if (escritura == true) {
            //ocultar div con controles para agregar y quitar funcionarios asignados 
            $("#divDisponibles").show()
        }else{
            //mostrar div con controles para agregar y quitar funcionarios asignados 
            $("#divDisponibles").hide()
        }
        //self.id(0);

    }

    self.limpiar = function(){
        self.soporteVO.id(0);
        self.soporteVO.nombre('');
        self.soporteVO.documento('');
        $('#archivo').fileinput('reset');
        $('#archivo').val('');  
        self.id(0);  

        self.soporteVO.nombre.isModified(false);
        self.soporteVO.documento.isModified(false);
    }
	self.eliminar = function(id) {
        var path =path_principal+'/api/soporteProcesoRelacionDato/'+id+'/';
        var parameter = {metodo:'DELETE'};
        RequestAnularOEliminar("Esta seguro que desea eliminar el soporte?", path, parameter, function () {
            self.consultarSoportes($('#txtProcesoRelacionDato').val());
            self.consultar($('#txtProcesoRelacionId').val());
        });

    }
	self.exportar_excel = function() {}	

    self.ver_soporte = function(obj) {
        window.open(path_principal+"/proceso/ver-soporte/?id="+ obj.id, "_blank");
    }
	
}

var procesoRelacionDatos = new ProcesoRelacionDatosViewModel();
ProcesoRelacionDatosViewModel.errores_soporte = ko.validation.group(procesoRelacionDatos.soporteVO);
ko.applyBindings(procesoRelacionDatos);