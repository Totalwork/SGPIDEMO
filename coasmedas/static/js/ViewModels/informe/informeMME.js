function InformeMMEViewModel() {

	var self=this;
	self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.titulo2=ko.observable('');
    self.filtro=ko.observable('');
    self.url=path_principal+'/api/'; 
    self.listado_actividades_disponibles = ko.observableArray([]);
    self.listado_actividades_contrato = ko.observableArray([]);
    self.listado_proyectos = ko.observableArray([]);

    self.archivo_carga=ko.observable('');


    self.datoVO={
        proyecto_id: ko.observable('').extend({ required: { message: '(*)Seleccione un proyecto' } }),
        contrato_id: ko.observable('').extend({ required: { message: '(*)Seleccione el contrato' } }),
        ano: ko.observable('').extend({ required: { message: '(*)Seleccione la año' } }),
        mes: ko.observable('').extend({ required: { message: '(*)Seleccione el mes' } }),
    };


    

    self.generar_informe_export=function(){
        if (InformeMMEViewModel.errores().length==0) {
                                    
                location.href=path_principal+'/informe/GenerarinformeMME/?contrato='+self.datoVO.contrato_id()+'&ano='+self.datoVO.ano()+'&mes='+self.datoVO.mes()+'&proyecto_id='+self.datoVO.proyecto_id();
                
                return true;
        }else {
            InformeMMEViewModel.errores.showAllMessages();//mostramos las validacion
        }

    }



    self.generar_informe=function(){
        if (InformeMMEViewModel.errores().length==0) {
            var parametros={                     
                    callback:function(datos, estado, mensaje){
                        
                        if (mensaje=='Este contrato empieza luego de la fecha elegida') {
                            self.mensaje('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>'+mensaje+'</div>');

                        }else if(mensaje=='La fecha elegida todavia aun no pasa'){                            
                            self.mensaje('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>'+mensaje+'</div>');
                            
                             //mensaje not found se encuentra el el archivo call-back.js                           
                        }else{

                            self.generar_informe_export();
                        }
                        
                        cerrarLoading();                     
                                
                    },//funcion para recibir la respuesta 
                        url:path_principal+'/informe/GenerarinformeMME_validar/?contrato='+self.datoVO.contrato_id()+'&ano='+self.datoVO.ano()+'&mes='+self.datoVO.mes(),//url api
                        parametros:undefined                      
            };
            RequestFormData(parametros);
        }else {
            InformeMMEViewModel.errores.showAllMessages();//mostramos las validacion
        }

    }

    



    self.actividadVO={
        id: ko.observable(0),        
        proyecto_id: ko.observable(0),
        actividad_id:ko.observable('').extend({ required: { message: '(*)Seleccione una actividad' } }),
        valor: ko.observable('').extend({ required: { message: '(*)Ingrese el valor de la actividad seleccionada' } }),
    }

    self.limpiar=function(){
        self.actividadVO.id(0);
        self.actividadVO.proyecto_id(self.datoVO.proyecto_id());
        self.actividadVO.actividad_id('');
        self.actividadVO.valor('');

        self.actividadVO.id.isModified(false);
        self.actividadVO.actividad_id.isModified(false);
        self.actividadVO.valor.isModified(false);
    }

    self.abrir_actividades_proyecto=function(){
        if(self.datoVO.proyecto_id()==""){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un proyecto.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false  
        }else{   
            ocultarNuevoRegistro();
            ocultarNuevoCargaMasiva();         
            self.consultar_actividades();            
        }


    }

    self.abrir_edicion = function(obj){
        nuevaRegistro();

        path = path_principal+'/api/proyecto_actividad/'+obj.id+'/?format=json';
        parameter = {
        };
        RequestGet(function (results,success) {           
            
            self.actividadVO.id(results.id);
            self.actividadVO.proyecto_id(results.proyecto.id);
            self.actividadVO.actividad_id(results.actividad.id);
            self.actividadVO.valor(results.valor);
            $('#nombre_actividad').val(results.actividad.nombre);
            self.titulo2('Edición')
            
            $('#nombre_actividad').animate({
                scrollTop: '0px'
            }, 300)
            cerrarLoading();
        }, path, parameter, undefined, false, false);

        // alert(self.actividadVO.id());

    }

    self.consultar_actividades_disponibles=function(){
        path = path_principal+'/api/actividad/?format=json';
        parameter = {
            proyecto_id:self.datoVO.proyecto_id(),
            ignorePagination:true,

        };
        RequestGet(function (datos, estado, mensage) {

            if (estado=='ok' && datos!=null && datos.length > 0) {
                //alert('3');               
                // self.mensaje('');
                self.listado_actividades_disponibles(datos);
                self.limpiar();
            }else{
                //alert('4');                
                // self.mensaje(mensajeNoFound);
                self.listado_actividades_disponibles([]);
            }
            cerrarLoading();
        }, path, parameter, undefined, false, false);
    }


    self.datoVO.contrato_id.subscribe(function (contrato_id) {    
       
        if(contrato_id!='' && contrato_id!=""){
            self.consultar_proyectos(contrato_id);
        }else{
            self.datoVO.proyecto_id("");
            self.listado_proyectos([]);
        }

    });

    self.consultar_proyectos=function(contrato_id){
        path = path_principal+'/api/Proyecto/?format=json';
        parameter = {
            ignorePagination: true,
            contrato: contrato_id,
            proyectos_post_eca: true,
            lite:1,

        };
        RequestGet(function (datos, estado, mensage) {

            if (estado=='ok' && datos!=null && datos.length > 0) {
                //alert('3');   
                self.listado_proyectos(datos);             
            }else{
                self.listado_proyectos([]);
            }
            cerrarLoading();
        }, path, parameter, undefined, false, false);
        
    }




    self.consultar_actividades=function(){
        path = path_principal+'/api/Proyecto/'+self.datoVO.proyecto_id()+'/?format=json';
        parameter = {
            lite_detalle: true,
        };
        RequestGet(function (results,success) {
            $('#modal_contrato_actividades').modal('show');
            if (results.nombre.length<=20){
                self.titulo('Actividades del proyecto: '+results.nombre);
            }else{
                self.titulo('Actividades del proyecto: '+results.municipio);
            }
            $("#departamento_nombre").text(results.departamento);
            $("#municipio_numero").text(results.municipio);
            $("#contrato_descripcion").text(results.mcontrato);
            cerrarLoading();

        }, path, parameter,function() {
            path = path_principal+'/api/proyecto_actividad/?format=json';
            parameter = {
                proyecto_id: self.datoVO.proyecto_id(),
                ignorePagination: true,

            };
            RequestGet(function (datos, estado, mensage) {

                if (estado=='ok' && datos!=null && datos.length > 0) {
                    //alert('3');               
                    self.mensaje('');
                    self.listado_actividades_contrato(datos);          
                    ocultarNuevoRegistro();
                    ocultarNuevoCargaMasiva();
                    self.limpiar();                
                }else{
                    //alert('4');                
                    self.mensaje(mensajeNoFound);
                    self.listado_actividades_contrato([]);
                }
                cerrarLoading();
            }, path, parameter, undefined, false, false);
        }, false, false);


        
    }


    self.descargar_plantilla=function(){        
       location.href=path_principal+"/informe/descargar-plantilla-actividades-contrato/"+self.datoVO.proyecto_id();
    }

    self.guardar_carga_masiva = function(){
        if(self.archivo_carga()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar las Georeferencias.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('proyecto_id',self.datoVO.proyecto_id());
            data.append('archivo',self.archivo_carga());

            var parametros={                     
                     callback:function(datos, estado, mensaje){
                        self.consultar_actividades();  
                        ocultarNuevoRegistro();
                        ocultarNuevoCargaMasiva();                      
                        $('#modal_acciones_carga_masiva').hide();
                        $('#archivo').fileinput('reset');
                        $('#archivo').val('');
                        self.archivo_carga('');
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/informe/guardar-actividades-archivo/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }
    }

    self.guardar_actividad=function(){
        if (InformeMMEViewModel.errores_actividad().length == 0 && InformeMMEViewModel.errores_actividad().length == 0 ) {
            if(self.actividadVO.id()==0){

                var parametros={
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') { 
                            self.consultar_actividades();
                            ocultarNuevoRegistro();
                            ocultarNuevoCargaMasiva();   
                        }

                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/proyecto_actividad/',//url api
                    parametros:self.actividadVO,                     
                };
                RequestFormData(parametros);
            }else{
                var parametros={
                    metodo:'PUT',
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {                             
                            self.consultar_actividades();
                            ocultarNuevoRegistro();
                            ocultarNuevoCargaMasiva();   
                        }

                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/proyecto_actividad/'+self.actividadVO.id()+'/',//url api
                    parametros:self.actividadVO,                 
                };
                RequestFormData(parametros);
            }
        }else {
            if (InformeMMEViewModel.errores_actividad().length > 0 ) {
                InformeMMEViewModel.errores_actividad.showAllMessages();
            }           
        }
    }
    

    self.eliminar_actividad=function(id){
        var path =path_principal+'/api/proyecto_actividad/'+id+'/';
        var parameter = {metodo:'DELETE'};
        RequestAnularOEliminar("Esta seguro que desea eliminar el registro?", path, parameter, 
            function(datos, estado, mensaje){
                if (estado=='ok') { 
                    self.consultar_actividades();
                }        
        });
    }
    
           

}

var informe = new InformeMMEViewModel();
InformeMMEViewModel.errores=ko.validation.group(informe.datoVO);
InformeMMEViewModel.errores_actividad = ko.validation.group(informe.actividadVO);
ko.applyBindings(informe);

function nuevaRegistro() {
    informe.limpiar();
    informe.consultar_actividades_disponibles();
    $("#nuevoRegistro").show();

    $("#divNuevoRegistro").hide();
    $("#divOcultarRegistro").show();

    $("#modal_acciones_carga_masiva").hide();

    $("#divNuevoCarga").show();
    $("#divOcultarCarga").hide();
    informe.titulo2('Registro')
}

function ocultarNuevoRegistro() {
    informe.limpiar();
    $("#nuevoRegistro").hide();

    $("#divNuevoRegistro").show();
    $("#divOcultarRegistro").hide();
}

function nuevaCargaMasiva() {
    $('#archivo').fileinput('reset');
    $('#archivo').val('');
    informe.archivo_carga('');

    $("#modal_acciones_carga_masiva").show();

    $("#divNuevoCarga").hide();
    $("#divOcultarCarga").show();

    $("#nuevoRegistro").hide();

    $("#divNuevoRegistro").show();
    $("#divOcultarRegistro").hide();

    informe.titulo2('Registro')
}

function ocultarNuevoCargaMasiva() {
    $('#archivo').fileinput('reset');
    $('#archivo').val('');
    informe.archivo_carga('');

    $("#modal_acciones_carga_masiva").hide();

    $("#divNuevoCarga").show();
    $("#divOcultarCarga").hide();

}