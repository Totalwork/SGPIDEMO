function SeguimientoDelContratoViewModel(){
    var self = this;
    self.datosSeguimiento = ko.observable()
    self.nombreEsquemaCronograma = ko.observable('');
    self.nombreContrato = ko.observable('');
    self.nombreCapitulo = ko.observable('');
    self.avanceGralCronograma  = ko.observable('');
    self.contrato_id = ko.observable($('#id_contrato').val());
    self.actividad_id = ko.observable('');
    
    self.url=path_principal+'/api/';

    self.estadosInicio = ko.observableArray([]);
    self.mensajeEstadoInicio = ko.observable('');
    self.estadosFin = ko.observableArray([]);
    self.mensajeEstadoFin = ko.observable('');

    self.listado_contratos = ko.observableArray([]);
    self.listado_soportes = ko.observableArray([]);

    self.titulo = ko.observable('');

    self.ActivitiesMessage = ko.observable('');

    self.ActividadContratoVO = {
    	id: ko.observable(0),
        actividad_id: ko.observable(''),
        contrato_id: ko.observable(''),
    	estadoinicio_id: ko.observable('').extend({ required: { message: 'Selecione uno de los estados' } }),
    	inicioprogramado: ko.observable(''),
        finprogramado: ko.observable(''),
        estadofin_id: ko.observable('').extend({required: { message: 'Selecione uno de los estados' }}),
        inicioejecutado: ko.observable(''),
        finejecutado: ko.observable(''),
        observaciones: ko.observable('')
    }


    self.limpiar = function(){
        self.ActividadContratoVO.id(0);
        self.ActividadContratoVO.actividad_id('');
        self.ActividadContratoVO.contrato_id('');
        self.ActividadContratoVO.estadofin_id('');
        self.ActividadContratoVO.inicioprogramado('');
        self.ActividadContratoVO.finprogramado('');
        self.ActividadContratoVO.estadofin_id('');
        self.ActividadContratoVO.inicioejecutado('');
        self.ActividadContratoVO.finejecutado('');
        self.ActividadContratoVO.observaciones('');

    }
    self.id=ko.observable(0);
    self.soporteVO={
        id:ko.observable(0),
        actividadcontrato_id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del soporte por favor' } }),
        archivo:ko.observable('').extend({ validation: { validator: validar_soporte, message: '(*) Seleccione el archivo por favor.' } })
    }
    self.programacionVO = {
        actividadcontrato_id: ko.observable(0),
        inicioprogramado: ko.observable('').extend({ required: { message: '(*)Debe indicar la fecha de inicio' } }),
        finprogramado:ko.observable('').extend({ required: { message: '(*)Debe indicar la fecha de finalización' } }),
        descripcion: ko.observable('')
    }
    self.inicioVO = {
       descripcion : ko.observable(''),
       actividadcontrato_id: ko.observable(0),
       fecha: ko.observable('').extend({ required: { message: '(*)Debe indicar la fecha de inicio de ejecucion de la actividad' } }), 
       observaciones : ko.observable(''),
    }
    self.finVO = {
       descripcion : ko.observable(''),
       actividadcontrato_id: ko.observable(0),
       fecha: ko.observable('').extend({ required: { message: '(*)Debe indicar la fecha de finalización de ejecucion de la actividad' } }), 
       observaciones : ko.observable(''),
    }


    function validar_soporte(val) {

     if(self.id() > 0)
      return true;
     else
      return self.id() == 0 && val!=null && val!='';
    }

    self.mensajeSoporte = ko.observable('');



    self.fillGraphById = function(){
        path = path_principal + '/cronogramacontrato/getdatagraphbyid/?id='+self.contrato_id();
        parameter = {};
        
        RequestGet(function (datos, success, massage){
            if (success == 'ok' && datos != null && datos.length > 0) {
                var dataGrafica = datos;
                for (i=0; i<dataGrafica.length; i++){
                    if (dataGrafica[i].nombre == 'estados de inicio'){
                        if (dataGrafica[i].data.length > 0){
                            self.estadosInicio(dataGrafica[i].data);
                            // self.mensajeEstadoInicio('');
                        }else{
                            self.estadosInicio([]);
                            self.mensajeEstadoInicio(mensajeNoFound);

                        }
                    }

                    if(dataGrafica[i].nombre == 'estados de fin'){
                        if(dataGrafica[i].data.length>0){
                            self.estadosFin(dataGrafica[i].data);
                            // self.mensajeEstadoFin('');
                        }else{
                            self.estadosFin([]);
                            self.mensajeEstadoFin(mensajeNoFound)
                        }
                    }

                }

                //Grafica de estados de inicio
                var patronColoresInicio = [];
                colors = [bgWarning, bgPrimary, bgInfo, bgAlert,
                    bgDanger, bgSuccess, bgSystem, bgDark
                ]
                columnsContratos = self.estadosInicio();
                for (var x = 0; x < columnsContratos.length; x++) {
                    if (columnsContratos[x][0] == 'Proximo a iniciar'){
                        patronColoresInicio.push(bgWarning);
                    }
                    if (columnsContratos[x][0] == 'Inició a tiempo'){
                        patronColoresInicio.push(bgSuccess);
                    }
                    if (columnsContratos[x][0] == 'Inició retrasado'){
                        patronColoresInicio.push(bgInfo);
                    }
                    if (columnsContratos[x][0] == 'Por iniciar'){
                        patronColoresInicio.push(bgAlert);
                    }
                    if (columnsContratos[x][0] == 'Retrasado'){
                        patronColoresInicio.push(bgDanger);
                    }



                }
                var chart14 = c3.generate({
                    bindto: '#estadosInicio',
                    color: {
                      pattern: colors,
                    },
                    data: {
                        // iris data from R
                        columns: self.estadosInicio(),
                        type : 'pie',
                        onclick: function (d, i) { console.log("onclick", d, i); },
                        onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                        onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                    }
                });
                
                
                //Grafica de estados de fin
                var patronColoresFin = [];
                columnsContratos = self.estadosFin();
                colors = [bgWarning, bgPrimary, bgInfo, bgAlert,
                    bgDanger, bgSuccess, bgSystem, bgDark
                ]
                for (var x = 0; x < columnsContratos.length; x++) {
                    if (columnsContratos[x][0] == 'Por vencer'){
                        patronColoresFin.push(bgWarning);
                    }
                    if (columnsContratos[x][0] == 'Cumplida a tiempo'){
                        patronColoresFin.push(bgSuccess);
                    }
                    if (columnsContratos[x][0] == 'Cumplida retrasada'){
                        patronColoresFin.push(bgInfo);
                    }
                    if (columnsContratos[x][0] == 'Por cumplir'){
                        patronColoresFin.push(bgAlert);
                    }
                    if (columnsContratos[x][0] == 'Vencida'){
                        patronColoresFin.push(bgDanger);
                    }



                }
                var chart15 = c3.generate({
                    bindto: '#estadosFin',
                    color: {
                      pattern:  colors,
                    },
                    data: {
                        // iris data from R
                        columns: self.estadosFin(),
                        type : 'pie',
                        onclick: function (d, i) { console.log("onclick", d, i); },
                        onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                        onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                    }
                });

            }

        }, path, parameter);

    }


    self.getInfoCronograma = function(){
        // alert(self.contrato_id());
        path =path_principal + '/api/Contrato/?cronogramaContrato=1&format=json&id='+self.contrato_id();
        parameter = {};
        RequestGet(function (datos, success, massage){
            if(success == 'ok' && datos!=null && datos.data.length > 0){
                self.nombreEsquemaCronograma( datos.data[0].fondo.nombre + ' ' +datos.data[0].ano);
                self.nombreContrato (datos.data[0].nombre);
                self.avanceGralCronograma (datos.data[0].avance);
            } else{
                self.datosSeguimiento('');
            }
        }, path, parameter);

    }

    self.getListSoportes = function(pagina){
        path = path_principal + '/cronogramacontrato/getslistbyid/?format=json&id='+self.actividad_id(); 
        paremeter = {};

        RequestGet(function (datos, success, massage){
            if(success == 'ok' && datos!=null && datos.length > 0){
                self.listado_soportes(datos);
                self.mensajeSoporte('');
            } else{
                self.listado_soportes([]);   
                self.mensajeSoporte(mensajeNoFound);
            }
        }, path,parameter);

    }

    self.getDataTable = function(pagina){
        path = path_principal + '/api/CActividad_contrato/?listbyid=1&idcontrato='+self.contrato_id(); 
        // path = path_principal + '/api/CActividad_contrato/';
        parameter = {};

        RequestGet(function (datos, success, massage){
            if(success == 'ok' && datos!=null){
                self.listado_contratos(datos);
            } else{
                self.listado_contratos(['']);   
                alert('false')
            }
        }, path,parameter);        
    }

    self.getActivities = function () {
        path = path_principal + '/../../cronogramacontrato/getactivities/?contrato_id='+self.contrato_id()+
        '&cronogramacontrato_id='+$('#esquemaId').val();
        RequestGet(function (datos, success, massage){
            if(success == 'ok' && datos!=null){
                self.listado_contratos(datos);
                self.ActivitiesMessage('');
                // $("#demo-accordion").zozoAccordion({
                //     theme: "blue"
                //  });
            } else{
                self.listado_contratos(['']);
                self.ActivitiesMessage(mensajeNoFound);
            }
        }, path,parameter);         
    }

    self.versoportes = function(obj){
        self.titulo('['+obj.actividad.capitulo.nombre + ' - '  + obj.actividad.descripcion + '] soportes');
        self.actividad_id(obj.id)
        self.getListSoportes();
        $('#modal_soportes').modal('show');
        self.id(0);
    }

    self.editar = function(obj){
        // alert('editando ' + id);
        self.titulo(obj.actividad.capitulo.nombre + ' - '  + obj.actividad.descripcion);
        self.ActividadContratoVO.id(obj.id);
        self.ActividadContratoVO.actividad_id(obj.actividad.id);
        self.ActividadContratoVO.contrato_id(obj.contrato.id)
        self.ActividadContratoVO.estadoinicio_id(obj.estadoinicio.id);
        self.ActividadContratoVO.inicioprogramado(obj.inicioprogramado);
        self.ActividadContratoVO.finprogramado(obj.finprogramado);
        self.ActividadContratoVO.inicioejecutado(obj.inicioejecutado);
        self.ActividadContratoVO.finejecutado(obj.finejecutado);
        self.ActividadContratoVO.observaciones(obj.observaciones);
        self.ActividadContratoVO.estadofin_id(obj.estadofin.id);
        $('#modal_editar').modal('show');
    }

    self.guardar = function(){
        //  alert(self.ActividadContratoVO.id());
        // if (CapitulosEsquemaViewModel.errores_capitulo().length == 0) {//se activa las validaciones
        // if(self.ActividadContratoVO.id()==0){
        //     self.ActividadContratoVO.id(self.idCapitulo());
        //     var parametros={                     
        //          callback:function(datos, estado, mensaje){
        //             if (estado=='ok') {
        //                 self.getDataTable(1);
        //                 $('#modal_capitulo').modal('hide');
        //                 self.limpiar();
        //             }                     
        //          },//funcion para recibir la respuesta 
        //          url: self.url+'CCapitulo/',//url api
        //          parametros:self.actividadVO                        
        //     };
            
        //     RequestFormData(parametros);
        // }else{        
              var parametros={     
                    metodo:'PUT',                
                   callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.getDataTable(1);
                            $('#modal_editar').modal('hide');
                            self.limpiar();
                        } 
                   },//funcion para recibir la respuesta 
                   url: self.url+'CActividad_contrato/'+ self.ActividadContratoVO.id()+'/',
                   parametros:self.ActividadContratoVO                        
              };
              RequestFormData(parametros);
        // }
    // } else {
    //     CapitulosEsquemaViewModel.errores_capitulo.showAllMessages();//mostramos las validacion
    //     alert('else ' + CapitulosEsquemaViewModel.errores_capitulo.showAllMessages());
        
    // }
    }
    self.toogle = function(id){
        var clase = $('#btn'+id).attr('class');
        //alert(clase);
        if (clase.includes('fa-caret-square-o-up')){
            $('#panel'+id).hide();
            $('#btn'+id).attr('class','fa fa-caret-square-o-down fa-2x')
        }
        if (clase.includes('fa-caret-square-o-down')){
            $('#panel'+id).show();
            $('#btn'+id).attr('class','fa fa-caret-square-o-up fa-2x')
        }
    }
    self.verSoportesActividad = function(id){
        self.actividad_id(id);
        self.soporteVO.actividadcontrato_id(id);
        self.getListSoportes(1);
        self.titulo('Lista de documentos asociados al cumplimiento de la actividad');
        $('#modal_soportes').modal('show');
    }
    self.guardarSoporte = function () {
        if (SeguimientoDelContratoViewModel.errores_soporte().length == 0) {
            if(self.soporteVO.id()==0){
                var parametros={                     
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.getListSoportes(1);
                            self.limpiarFormGuardarSoporte();
                            self.getActivities();
                            self.mensajeSoporte('');
                        }else{
                            self.mensajeSoporte('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>Se presentaron errores al guardar el soporte.</div>'); //mensaje not found se encuentra el el archivo call-back.js                           
                        }                        
                                
                    },//funcion para recibir la respuesta 
                             url:path_principal+'/api/CActividad_contrato_soporte/',//url api
                             parametros:self.soporteVO                        
                };
                        //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{
                var parametros={     
                    metodo:'PUT',                
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.getListSoportes(1);
                            self.limpiarFormGuardarSoporte();
                        }  
                    },//funcion para recibir la respuesta 
                    url:path_principal+'/api/CActividad_contrato_soporte/'+self.soporteVO.id()+'/',
                    parametros:self.soporteVO                        
                };

                RequestFormData(parametros);                

            }
        }else{
            SeguimientoDelContratoViewModel.errores_soporte.showAllMessages();//mostramos las validacion
        }


    }
    self.limpiarFormGuardarSoporte = function () {
        self.soporteVO.id(0);
        self.soporteVO.nombre('');
        self.soporteVO.archivo('');
        $('#archivo').fileinput('reset');
        $('#archivo').val(''); 
        self.id(0);       
    }
    self.consultarSoportePorId = function (id,nombre,contratoActividad){
        self.id(id);
        self.soporteVO.id(id);
        self.soporteVO.nombre(nombre);
        self.soporteVO.actividadcontrato_id(contratoActividad);
        self.soporteVO.archivo('');
    }
    self.eliminarSoporte = function(id) {
        var path =path_principal+'/api/CActividad_contrato_soporte/'+id+'/';
        var parameter = {metodo:'DELETE'};
        RequestAnularOEliminar("Esta seguro que desea eliminar el soporte?", path, parameter, function () {
            self.getListSoportes(1);
            self.getActivities();
        });        
    }
    self.programar = function(id,inicio,fin,descripcion){
        self.programacionVO.descripcion(descripcion);
        self.programacionVO.actividadcontrato_id(id);
        self.programacionVO.inicioprogramado(inicio);
        self.programacionVO.finprogramado(fin);
        self.titulo('Programación de inicio y finalización de la actividad');
        $('#modal_programacion').modal('show');
    }
    self.actualizarProgramacion = function() {
        if (SeguimientoDelContratoViewModel.errores_programacion().length == 0) {
                var parametros={     
                    metodo:'POST',                
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_programacion').modal('hide');
                            self.getInfoCronograma();
                            self.fillGraphById();
                            self.getActivities();                            
                        }  
                    },//funcion para recibir la respuesta 
                    url:path_principal+'/../../cronogramacontrato/programar/',
                    parametros:self.programacionVO                        
                };

                RequestFormData(parametros);  

        }else{
            SeguimientoDelContratoViewModel.errores_programacion.showAllMessages();//mostramos las validacion
        }
    }
    self.IniciarRegistroInicio = function (id,fecha,observaciones, descripcion){
        self.titulo('Registro de la fecha de inicio de ejecucion de la actividad');
        self.inicioVO.actividadcontrato_id(id);
        self.inicioVO.fecha(fecha);
        self.inicioVO.observaciones(observaciones);
        self.inicioVO.descripcion(descripcion);
        $('#modal_registarInicio').modal('show');
    }
    self.actualizarRegistroInicio = function(){
       if (SeguimientoDelContratoViewModel.errores_registroInicio().length == 0) {
                var parametros={     
                    metodo:'POST',                
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_registarInicio').modal('hide');
                            self.getInfoCronograma();
                            self.fillGraphById();
                            self.getActivities();                            
                        }  
                    },//funcion para recibir la respuesta 
                    url:path_principal+'/../../cronogramacontrato/registroinicio/',
                    parametros:self.inicioVO                        
                };

                RequestFormData(parametros);              

       }else{
         SeguimientoDelContratoViewModel.errores_registroInicio.showAllMessages();//mostramos las validacion
       }
    }
    self.IniciarRegistroFinalizacion = function (id,fecha,observaciones, descripcion){
        self.titulo('Registro de la fecha de finalización de ejecucion de la actividad');
        self.finVO.actividadcontrato_id(id);
        self.finVO.fecha(fecha);
        self.finVO.observaciones(observaciones);
        self.finVO.descripcion(descripcion);
        $('#modal_registarFin').modal('show');
    }

    self.actualizarRegistroFin = function(){
        if (SeguimientoDelContratoViewModel.errores_registroFin().length == 0) {
                var parametros={     
                    metodo:'POST',                
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_registarFin').modal('hide');
                            self.getInfoCronograma();
                            self.fillGraphById();
                            self.getActivities();                            
                        }  
                    },//funcion para recibir la respuesta 
                    url:path_principal+'/../../cronogramacontrato/registrofin/',
                    parametros:self.finVO                        
                };

                RequestFormData(parametros);   

        }else{
            SeguimientoDelContratoViewModel.errores_registroFin.showAllMessages();//mostramos las validacion
        }

    }
    self.mensajeRestriccion = function () {
        mensajeInformativo('Debe cargar los archivos soporte antes de establecer la finalización de la actividad', 'Cronograma de contratos');
    }



}

var seguimientodelcontrato = new SeguimientoDelContratoViewModel();
SeguimientoDelContratoViewModel.errores_soporte = ko.validation.group(seguimientodelcontrato.soporteVO);
SeguimientoDelContratoViewModel.errores_programacion = ko.validation.group(seguimientodelcontrato.programacionVO);
SeguimientoDelContratoViewModel.errores_registroInicio = ko.validation.group(seguimientodelcontrato.inicioVO);
SeguimientoDelContratoViewModel.errores_registroFin = ko.validation.group(seguimientodelcontrato.finVO);
ko.applyBindings(seguimientodelcontrato);
seguimientodelcontrato.getInfoCronograma();
seguimientodelcontrato.fillGraphById();
//seguimientodelcontrato.getDataTable();
seguimientodelcontrato.getActivities();
