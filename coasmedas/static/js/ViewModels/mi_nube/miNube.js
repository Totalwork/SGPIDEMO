function MiNubeViewModel() {
	administraccion_de_recurso = 12;
    var self = this;
    self.app_contrato = "contrato"
    self.url=path_principal+'/api/'; 
    self.url_app_miNube = path_principal+'/miNube/';
    self.url_funcion_proyecto=path_principal+'/proyecto/'; 
    self.listado = ko.observableArray([]);
    self.listado_id = ko.observableArray([]);
    self.mensaje = ko.observable('');
    self.mensajeAsignados = ko.observable('');
    self.mensajePorAsignar = ko.observable('');
    self.mensajeContratosAsignados = ko.observable('');
    self.mensajeContratosPorAsignar = ko.observable('');
    self.titulo = ko.observable('');
    self.filtro = ko.observable('');
    self.proyectoContrato = ko.observable("true"); 

    self.listado_estados_contrato = ko.observableArray([]);
    self.estado_id_filtro =ko.observable('');

    self.espacioTotal = ko.observable('');  
    self.espacioUtilizado = ko.observable(''); 
    self.porcentajeUsado = ko.observable('');    

    self.propietario = ko.observable('');
    self.usuarioModificado = ko.observable('');  
    self.tipoArchivo = ko.observable('');  
    //LISTADO
    self.listado_mcontratos = ko.observableArray([]);
    self.listado_departamentos = ko.observableArray([]);
    self.listado_municipios = ko.observableArray([]);
    self.listado_municipios_proyecto = ko.observableArray([]);
    self.listado_proyecto_filtro = ko.observableArray([]);
    self.listado_empresas = ko.observableArray([]);

    //LISTADO CONTRATO ARCHIVO
    self.listado_contrato = ko.observableArray([]);
    self.listado_contrato_archivo = ko.observableArray([]);

    //LISTADO PROYECTO ARCHIVO
    self.listado_proyecto = ko.observableArray([]);
    self.listado_proyecto_archivo = ko.observableArray([]);

    //LISTADO USUARIO ARCHIVO
    self.listado_usuario = ko.observableArray([]);
    self.listado_usuario_archivo = ko.observableArray([]);

    self.checkall=ko.observable(false);
    self.checkallUsuario=ko.observable(false);
    self.checkallUsuarioArchivo=ko.observable(false);

    self.checkallUsuarioEscritura=ko.observable(false);
    self.checkallUsuarioArchivoEscritura=ko.observable(false);

    self.checkallProyecto=ko.observable(false);
    self.checkallProyectoArchivo=ko.observable(false);

    self.checkallContrato=ko.observable(false);
    self.checkallContratoArchivo=ko.observable(false);

    //VARIABLES
    self.mcontrato_id=ko.observable('');
    self.departamento_id=ko.observable('');
    self.municipio_id=ko.observable('');
    self.proyecto_id=ko.observable('');

    // VAR USUARIO ARCHIVO
    self.empresaUsuario_filtro=ko.observable('');
    self.empresaUsuarioArchivo_filtro=ko.observable('');

    //VARIABLES ARCHIVO PROYECTO
    self.proyecto_mcontrato_id=ko.observable('');
    self.proyecto_departamento_id=ko.observable('');
    self.proyecto_municipio_id=ko.observable('');
    self.proyecto_filtro=ko.observable('');
    self.proyecto_archivo_filtro=ko.observable('');
    
    //Representa un modelo de la tabla proyecto
    self.mi_nubeVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*) Digite el nombre.' } }),
        nombreActual:ko.observable(''),
        padre:ko.observable(''),
        destino:ko.observable(''),        
        tipoArchivo_id:ko.observable(''),
        eliminado:ko.observable(0),
        peso:ko.observable(''),
        propietario_id:ko.observable($("#user").val()),
        validaNombre:ko.observable(false),
        usuario_id:ko.observable($("#user").val()),
        empresa_id:ko.observable($("#company").val()),
        usuarioModificado_id : ko.observable($("#user").val()),
        fechaModificado:ko.observable(''),
     };
    // //limpiar el modelo 
    self.limpiar=function(){           
        self.mi_nubeVO.id(0);
        self.mi_nubeVO.nombre('');
        self.mi_nubeVO.nombreActual('');
        self.mi_nubeVO.padre('');
        self.mi_nubeVO.destino('');
        self.mi_nubeVO.tipoArchivo_id('');
        self.mi_nubeVO.eliminado(0);
        self.mi_nubeVO.peso('');
        self.mi_nubeVO.propietario_id($("#user").val());
        self.mi_nubeVO.validaNombre(false);
        self.mi_nubeVO.fechaModificado('');

        self.mi_nubeVO.nombre.isModified(false);
        self.mi_nubeVO.nombreActual.isModified(false);

        $('#archivo').fileinput('reset');
    }
    //funcion consultar los contratos que tienen proyecto
    self.consultar_mcontratos_filtro = function () {                
            path = self.url_funcion_proyecto+'select-filter-proyecto/';
            parameter = { tipo : administraccion_de_recurso, consulta_departamento : 1 };// 1 indica True
            RequestGet(function (datos, estado, mensage) {

                self.listado_departamentos(datos.departamentos)
                if (estado == 'ok' && datos.mcontratos!=null && datos.mcontratos.length > 0) {
                    self.listado_mcontratos(datos.mcontratos);
                } else {
                    self.listado_mcontratos([]);
                }          
            }, path, parameter);        
    }

    self.consultar_departamento = function (mcontrato){
        self.departamento_id('');
        if (mcontrato != ""){            
            path = self.url_funcion_proyecto+'filtrar_proyectos/';       
            parameter = {mcontrato:mcontrato};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos.departamento!=null && datos.departamento.length > 0) {                
                    self.listado_departamentos(datos.departamento);                                                                    
                } else {
                    self.listado_departamentos([]);
                }          
            }, path, parameter); 
        }else{            
            self.listado_departamentos([]);
        }
       
    } 

    //funcion consultar municipios
    self.consultar_municipios = function (departamento) {                
            path = self.url+'Municipio/';
            parameter = { ignorePagination : 1 , id_departamento : departamento };       
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_municipios(datos);                    
                } else {
                    self.listado_municipios([]);
                }             
            }, path, parameter);           
    }
    //funcion consultar proyectos que ppuede  ver la empresa
    self.consultar_proyectos = function () {              
            path = self.url+'Proyecto_empresas/?format=json';
            parameter = {  ignorePagination: 1 , empresa : self.mi_nubeVO.empresa_id() 
                            , mcontrato : self.mcontrato_id()
                            , departamento : self.departamento_id()
                            , municipio : self.municipio_id() 
                            , consulta_lite_nombre : 1
                             };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_proyecto_filtro(datos);  

                } else {
                    self.listado_proyecto_filtro([]);
                }
            }, path, parameter);
    }    

    //funcion consultar estados del contrato 
    self.consultar_estados_contrato = function () {                
        path = self.url+'Estados/';
        parameter = { ignorePagination : 1 , aplicacion : self.app_contrato };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.listado_estados_contrato(datos);
            } else {
                self.listado_estados_contrato([]);
            }            
        }, path, parameter);        
    }

    self.mcontrato_id.subscribe(function (val) {
        if (val != ''){      
            self.mcontrato_id(val);        
            self.consultar_departamento(val);
            self.consultar_proyectos();
        }else{
            self.mcontrato_id('');            
            self.listado_proyecto_filtro([]);
            self.departamento_id('');
        }
    });

    self.departamento_id.subscribe(function (val) {
        if(val!=""){
            self.departamento_id(val);            
            self.consultar_municipios(val);
            self.consultar_proyectos();
        }else{
            self.departamento_id('');  
            self.consultar_proyectos(); 
            self.listado_municipios([]);
        }   
    });

    self.municipio_id.subscribe(function (val) {
        if(val!=""){
            self.municipio_id(val);
            self.consultar_proyectos()     
        }else{
            self.municipio_id('');
            self.consultar_proyectos();
        }

    });

    //funcion consultar municipios
    self.consultar_municipios_proyecto = function (departamento) {                
            path = self.url+'Municipio/';
            parameter = { ignorePagination : 1 , id_departamento : departamento };            
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_municipios_proyecto(datos);                    
                } else {
                    self.listado_municipios_proyecto([]);
                }             
            }, path, parameter);           
    }

    self.proyecto_departamento_id.subscribe(function (val) {
        if(val!=""){
            self.consultar_municipios_proyecto(val)   
        }else{
            self.listado_municipios_proyecto([]);
            self.proyecto_municipio_id('');
        }   
    });   

    self.consultarContratoProyecto_btn = function (d,e) {
        if(($("#txtBuscarContratoProyecto").val() == undefined || $("#txtBuscarContratoProyecto").val() == "") && self.proyecto_id() == ""){            
            mensajeInformativo('Debe de seleccionar un proyecto ó digitar el nombre del carpeta o archivo.','Mi Nube');
        }else{
            self.consultarContratoProyecto();
        }     
    }     
            
    //funcion consultar archivos que puede ver la persona
    self.consultarContratoProyecto = function () {  
        padre_id = 0
        self.filtro($('#txtBuscarContratoProyecto').val());
        path = self.url_app_miNube+'list_archivo_ContratoProyecto/';
        parameter = { dato: self.filtro()  , usuario : self.mi_nubeVO.usuario_id , mcontrato:self.mcontrato_id() , departamento:self.departamento_id() , municipio:self.municipio_id() , proyecto:self.proyecto_id() };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensaje('');
                self.listado(agregarOpcionesObservable(datos))
            } else {
                self.listado([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);   
        $('#modal_acciones_filtro').modal('hide');
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.consultarGeneral();
        }
        return true;
    } 
    //funcion consultar archivos que puede ver la persona
    self.consultarGeneral = function () {  
        padre_id = 0
        self.filtro($('#txtBuscar').val());
        path = self.url_app_miNube+'list_archivo/';
        parameter = { dato: self.filtro()  , padre : padre_id , usuario : self.mi_nubeVO.usuario_id};
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensaje('');
                self.listado(agregarOpcionesObservable(datos))
            } else {
                self.listado([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
            cerrarLoading();
        }, path, parameter,undefined,false); 
    }

    self.cancelar_busqueda = function (){
        $('#txtBuscar').val('')
        self.filtro('');

        padre_id = parseInt($("#jstree").jstree("get_selected")) ; 
        if(isNaN(padre_id)) {
            $("#jstree").jstree("select_node",'#1');
        }else{
            $("#jstree").jstree("select_node",'#'+padre_id);
        }  

    }
    self.subir_nivel = function (){
        padre_id = parseInt($("#jstree").jstree("get_selected")) ; 
        if(padre_id!=1){
            var inst = $('#jstree').jstree(true);
            parent = inst.get_node(padre_id).parent;
            /*alert(parent)*/
            $("#jstree").jstree("deselect_all");
            $("#jstree").jstree("select_node",'#'+parent);
        }
        /*alert(padre_id)*/
    } 


    //funcion consultar archivos que puede ver la persona
    self.consultar = function () {  
        padre_id = parseInt($("#jstree").jstree("get_selected")) ; 
        if(!isNaN(padre_id)){

            self.filtro($('#txtBuscar').val());
            path = self.url_app_miNube+'list_archivo/';
            parameter = { dato: self.filtro()  , padre : padre_id , usuario : self.mi_nubeVO.usuario_id};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos))
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
                cerrarLoading();
            }, path, parameter,undefined,false);
        }   
    }
    //consulta para crear el arbol solo consulta carpetas
    self.consultar_arbol = function (){       

            self.filtro($('#txtBuscar').val());
            path = self.url_app_miNube+'list_archivo_carpeta/';
            parameter = {  };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {                       
                    $('#Rmover-archivo').jstree({
                        'core': {
                         'data':  datos,
                         "check_callback" : true
                        },                      
                        "state" : { "key" : "state_demo" },                     
                        "plugins" : [ "sort","state"]
                    });

                    $('#jstree').jstree({  
                          'core': {
                           'data':  datos,
                           "check_callback" : true
                          },           
                          "state" : { "key" : "state_demo" },           
                          "plugins" : [ "sort","state"]
                    });  

                    $('#Rmover-archivo').jstree(true).refresh();
                    /*$('#jstree').jstree(true).refresh();*/

                    self.mensaje('');         
                } else {
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }         

            }, path, parameter);
    }    

    self.abrir_modal_asociar = function () {
        var id=0;
        var count=0;
        ko.utils.arrayForEach(self.listado(), function(d) {
            if(d.eliminado()==true){
                count= 1;
                id=d.id                   
            }
        });
        if(count==1){
            self.mensajePorAsignar(mensajeInformativoBusuqeda)
            self.mensajeContratosPorAsignar(mensajeInformativoBusuqeda)            
            $('#modal_acciones_asociar').modal('show');
            /*self.consultar_contratosSin_archivo();*/
            self.consultar_contratosCon_archivo();
            /*self.consultar_proyectosSin_archivo();*/
            self.consultar_proyectosCon_archivo();  
            self.listado_contrato([]);
            self.listado_proyecto([]);

        }else{
           mensajeInformativo('Se debe seleccionar un archivo para asociar a proyectos o contratos.','Mi Nube');
        }             
    }

    self.abrir_modal_cargarArchivo = function () {
        self.limpiar();
        $('#modal_acciones_cargarArchivo').modal('show');        
    }
    self.abrir_modal_filtro = function () {
        $('#modal_acciones_filtro').modal('show');
    }
    self.abrir_modal = function () {
        self.limpiar();
        $('#modal_acciones_carpeta').modal('show');
    }
    self.guardar_carpeta_enter = function (d,e) {
        if (e.which == 13) {
            self.guardar_carpeta();
        }
        return true;
    } 

    // //funcion guardar
     self.guardar_carpeta=function(){
        padre = $("#jstree").jstree("get_selected") ;
        if(padre=="" || padre==undefined){
            $("#jstree").jstree("deselect_all");
            $("#jstree").jstree("select_node",'#1');
            padre = 1;
        }
        self.mi_nubeVO.nombre($("#nombre").val());
        self.mi_nubeVO.padre(parseInt(padre))
        self.mi_nubeVO.tipoArchivo_id(58)
        valida_caracter = false;

        var miArray = ['\\' ,'/' ,':' ,'*' ,'?' ,'"' ,'<' ,'>' ,'|'];
        for (var i in miArray) {
            if (self.mi_nubeVO.nombre().indexOf(miArray[i]) != -1){
                valida_caracter = true;
                texto = self.mi_nubeVO.nombre()
                self.mi_nubeVO.nombre(texto.replace(miArray[i] , ""))
            }            
        }
        
        if (MiNubeViewModel.errores_carpeta().length == 0 && valida_caracter==false) {//se activa las validaciones
            if(self.mi_nubeVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.filtro("");
                            $('#modal_acciones_carpeta').modal('hide');
                            self.consultar();
                            self.mi_nubeVO.nombre('')
                            
                            path = self.url_app_miNube+'list_archivo_carpeta/';
                            parameter = {  };
                            RequestGet(function (datos, estado, mensage) {
                                if (estado == 'ok' && datos!=null && datos.length > 0) {                       
                                    $('#jstree').jstree(true).settings.core.data = datos;
                                    $('#jstree').jstree(true).refresh(); 
                                }
                            }, path, parameter); 
                        }
                     },//funcion para recibir la respuesta 
                     url: self.url+'MiNubeArchivo/',//url api
                     parametros:self.mi_nubeVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
            }
        } else {
            if (valida_caracter){
                mensajeInformativo('Los nombres de archivo no pueden contener ninguno de los siguientes caracteres: \\ / : * ? " < > |','Mi Nube');
             
            }else{
                MiNubeViewModel.errores_carpeta.showAllMessages();//mostramos las validacion
            }
        }
     }
     
     // //funcion subir archivo
     self.guardar_archivo=function(){
            padre = $("#jstree").jstree("get_selected");

            if(padre=="" || padre==undefined){
                $("#jstree").jstree("deselect_all");
                $("#jstree").jstree("select_node",'#1');
                padre=1
            }
            self.mi_nubeVO.padre(parseInt(padre))
            self.mi_nubeVO.tipoArchivo_id(0);
            if (self.mi_nubeVO.destino() != '') {//se activa las validaciones
                if(self.mi_nubeVO.id()==0){

                    valida_caracter = false;

                    if (self.mi_nubeVO.validaNombre() == true && self.mi_nubeVO.nombreActual()!='' ){
                        var miArray = ['\\' ,'/' ,':' ,'*' ,'?' ,'"' ,'<' ,'>' ,'|'];
                        for (var i in miArray) {
                            if (self.mi_nubeVO.nombreActual().indexOf(miArray[i]) != -1){
                                valida_caracter = true;
                                texto = self.mi_nubeVO.nombreActual()
                                self.mi_nubeVO.nombreActual(texto.replace(miArray[i] , ""))
                            }            
                        }
                    }

                    if( (self.mi_nubeVO.validaNombre() == true && self.mi_nubeVO.nombreActual()!='' ) || (self.mi_nubeVO.validaNombre()==false) ){

                        var parametros={                     
                            callback:function(datos, estado, mensaje){
                                if (estado=='ok') {
                                    self.filtro("");
                                    $('#modal_acciones_cargarArchivo').modal('hide');
                                    self.limpiar(); 
                                    self.consultar();
                                    self.consultar_espacio();
                                }                     
                             },//funcion para recibir la respuesta 
                             url: self.url+'MiNubeArchivo/',//url api
                             parametros:self.mi_nubeVO                       
                        };
                        RequestFormData(parametros);

                    }else{
                        if(valida_caracter){
                            mensajeInformativo('Los nombres de archivo no puedes contener ninguno de los siguientes caracteres: \\ / : * ? " < > |','Mi Nube');
                        }else{
                            mensajeInformativo('El nombre del archivo no puede estar vacio.','Mi Nube');    
                        }
                        
                    }                
                } 
            }else{
                mensajeInformativo('Seleccione un archivo.','Mi Nube');
            }       
     } 
     // //funcion subir archivo
     self.asociar_proyectos=function(){
            padre = $("#jstree").jstree("get_selected") ;
            self.mi_nubeVO.padre_id(parseInt(padre))
            if(self.mi_nubeVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.filtro("");
                            $('#modal_acciones_carpeta').modal('hide');

                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url_app_miNube+'createArchivo/',//url api
                     parametros:self.mi_nubeVO                        
                };
                RequestFormData(parametros);
            }        
     } 

     self.checkall.subscribe(function(value ){
         ko.utils.arrayForEach(self.listado(), function(d) { d.eliminado(value); }); 
    });
// DOWNLOAD FILE ---- DOWNLOAD FILE //// DOWNLOAD FILE ---- DOWNLOAD FILE //// DOWNLOAD FILE ---- DOWNLOAD FILE 
    //descargar archivos 
    self.descarga_archivo = function () { 
        var lista_id=[];
        var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                    lista_id.push(d.id)                 
                }
         });             

        if(lista_id.length>0){
            location.href=path_principal+"/miNube/download_file?archivo="+ lista_id;
        }else{
            mensajeInformativo('Debe seleccionar un archivo o carpeta.','Mi Nube');
        } 
    }

//CONTRATOS ARCHIVOS ---- CONTRATOS ARCHIVOS // CONTRATOS ARCHIVOS ---- CONTRATOS ARCHIVOS // CONTRATOS ARCHIVOS ---- CONTRATOS ARCHIVOS //
    self.estado_id_filtro.subscribe(function(value ){
        self.consultar_contratosSin_archivo();
    }); 

    self.consulta_enter_contrato = function (d,e) {
        if (e.which == 13) {
            self.consultar_contratosSin_archivo();
        }
        return true;
    }

    self.consulta_btn_contrato = function (d,e) {
        self.consultar_contratosSin_archivo();        
    }

    self.consulta_enter_contrato_archivo = function (d,e) {
        if (e.which == 13) {
            self.consultar_contratosCon_archivo();
        }
        return true;
    }

    self.consulta_btn_contrato_archivo = function (d,e) {
        self.consultar_contratosCon_archivo();        
    }

    //contratos que no estan asociados al archivo
    self.consultar_contratosSin_archivo = function () { 

        var lista_id=[];
        var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                   lista_id = lista_id+d.id+','                 
                }
         }); 
            
        path = self.url_app_miNube+'list_contratosSin_archivo/';
        parameter = { archivo : lista_id.substring(0,lista_id.length-1) , dato : $("#txtBuscarContrato").val(), estado : self.estado_id_filtro()  };
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensajeContratosPorAsignar('');
                self.listado_contrato(agregarOpcionesObservable(datos))
            } else {
                self.listado_contrato([]);
                self.mensajeContratosPorAsignar(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);   
    }
    //contratos que estan asociados al archivo
    self.consultar_contratosCon_archivo = function () { 
        var lista_id='';
        var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                   lista_id = lista_id+d.id+','                 
                }
         }); 
            
        path = self.url_app_miNube+'list_contratosCon_archivo/';
        parameter = { archivo : lista_id.substring(0,lista_id.length-1) , dato : $("#txtBuscarContratoArchivo").val() };
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensajeContratosAsignados('');
                self.listado_contrato_archivo(agregarOpcionesObservable(datos))
            } else {
                self.listado_contrato_archivo([]);
                self.mensajeContratosAsignados(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);   
    }
    // //funcion asociar contrato a los archivos seleccionados
    self.asociar_contrato = function(){
             var lista_id=[];
             var lista_archivo = [];
             var count=0;
             ko.utils.arrayForEach(self.listado_contrato(), function(d) {
                    if(d.procesar()==true){
                        count=1;
                       lista_id.push(d.id)
                    }
             });

             ko.utils.arrayForEach(self.listado(), function(d) {
                    if(d.eliminado()==true){
                       lista_archivo.push(d.id)
                    }
             });

            if(count==0){
                 $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione un usuario para compartir los archivos seleccionados.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }else{
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.consultar_contratosSin_archivo();
                            self.consultar_contratosCon_archivo();
                            self.checkallContrato(false);
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url_app_miNube+'create_contratoCon_archivo/',//url api
                     parametros: { archivo : lista_archivo , contrato : lista_id }                         
                };
                Request(parametros);
            }        
    }

    self.quitar_contrato = function(){
             var lista_id=[];
             var lista_archivo = [];
             var count=0;
             ko.utils.arrayForEach(self.listado_contrato_archivo(), function(d) {
                    if(d.eliminado()==true){
                        count=1;
                       lista_id.push(d.id)
                    }
             });

             ko.utils.arrayForEach(self.listado(), function(d) {
                    if(d.eliminado()==true){
                       lista_archivo.push(d.id)
                    }
             });

             if(count==0){

                  $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un usuario para quitarlo.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });

             }else{
                 var path = self.url_app_miNube+'destroy_contratoCon_archivo/';
                 var parameter = { archivo : lista_archivo , contrato : lista_id };
                 RequestAnularOEliminar("Esta seguro que desea quitar los usuarios seleccionados?", path, parameter, function () {
                    self.consultar_contratosSin_archivo();
                    self.consultar_contratosCon_archivo();
                    self.checkallContratoArchivo(false);
                 })

             }        
    }

self.checkallContrato.subscribe(function(value ){
     ko.utils.arrayForEach(self.listado_contrato(), function(d) { d.procesar(value); }); 
}); 

self.checkallContratoArchivo.subscribe(function(value ){
     ko.utils.arrayForEach(self.listado_contrato_archivo(), function(d) { d.eliminado(value); }); 
});

//PROYECTOS ARCHIVOS ---- PROYECTOS ARCHIVOS // PROYECTOS ARCHIVOS ---- PROYECTOS ARCHIVOS // PROYECTOS ARCHIVOS ---- PROYECTOS ARCHIVOS //
    self.proyecto_mcontrato_id.subscribe(function(value ){
        self.consultar_proyectosSin_archivo();
    }); 

    self.proyecto_departamento_id.subscribe(function(value ){
        self.consultar_proyectosSin_archivo();
    }); 

    self.proyecto_municipio_id.subscribe(function(value ){
        self.consultar_proyectosSin_archivo();
    }); 

    self.consulta_enter_proyecto = function (d,e) {
        if (e.which == 13) {
            self.consultar_proyectosSin_archivo();
        }
        return true;
    }

    self.consulta_btn_proyecto = function (d,e) {
        self.consultar_proyectosSin_archivo();        
    }

    self.consulta_enter_proyecto_archivo = function (d,e) {
        if (e.which == 13) {
            self.consultar_proyectosCon_archivo();
        }
        return true;
    }

    self.consulta_btn_proyecto_archivo = function (d,e) {
        self.consultar_proyectosCon_archivo();        
    }

    //proyectos que no estan asociados al archivo
    self.consultar_proyectosSin_archivo = function () { 

        var lista_id=[];
        var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                   lista_id = lista_id+d.id+','                 
                }
         }); 
            
        path = self.url_app_miNube+'list_proyectosSin_archivo/';
        parameter = { archivo : lista_id.substring(0,lista_id.length-1) 
                    , mcontrato : self.proyecto_mcontrato_id() 
                    , departamento: self.proyecto_departamento_id() 
                    , municipio: self.proyecto_municipio_id()
                    , dato : $('#txtBuscarProyecto').val()  };
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensajePorAsignar('');
                self.listado_proyecto(agregarOpcionesObservable(datos))
            } else {
                self.listado_proyecto([]);
                self.mensajePorAsignar(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);   
    }
    //proyectos que estan asociados al archivo
    self.consultar_proyectosCon_archivo = function () { 
        var lista_id='';
        var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                   lista_id = lista_id+d.id+','                 
                }
         }); 
            
        path = self.url_app_miNube+'list_proyectosCon_archivo/';
        parameter = { archivo : lista_id.substring(0,lista_id.length-1)
                     ,dato :  $('#txtBuscarProyectoArchivo').val() };
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensajeAsignados('');
                self.listado_proyecto_archivo(agregarOpcionesObservable(datos))
            } else {
                self.listado_proyecto_archivo([]);
                self.mensajeAsignados(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);   
    }
    // //funcion asociar proyectos a los archivos seleccionados
    self.asociar_proyecto=function(){
             var lista_id=[];
             var lista_archivo = [];
             var count=0;
             ko.utils.arrayForEach(self.listado_proyecto(), function(d) {
                    if(d.procesar()==true){
                        count=1;
                       lista_id.push(d.proyecto__id)
                    }
             });

             ko.utils.arrayForEach(self.listado(), function(d) {
                    if(d.eliminado()==true){
                       lista_archivo.push(d.id)
                    }
             });

            if(count==0){
                 $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione un proyecto para compartir los archivos seleccionados.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }else{
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.consultar_proyectosSin_archivo();
                            self.consultar_proyectosCon_archivo();
                            self.checkallProyecto(false);
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url_app_miNube+'create_proyectoCon_archivo/',//url api
                     parametros: { archivo : lista_archivo , proyecto : lista_id }                         
                };
                Request(parametros);
            }        
    }

    self.quitar_proyecto=function(){
             var lista_id=[];
             var lista_archivo = [];
             var count=0;
             ko.utils.arrayForEach(self.listado_proyecto_archivo(), function(d) {
                    if(d.eliminado()==true){
                        count=1;
                       lista_id.push(d.id)
                    }
             });

             ko.utils.arrayForEach(self.listado(), function(d) {
                    if(d.eliminado()==true){
                       lista_archivo.push(d.id)
                    }
             });

            if(count==0){

                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un usuario para quitarlo.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });

            }else{
                 var path = self.url_app_miNube+'destroy_proyectoCon_archivo/';
                 var parameter = { archivo : lista_archivo , proyecto : lista_id };
                 RequestAnularOEliminar("Esta seguro que desea quitar los usuarios seleccionados?", path, parameter, function () {
                    self.consultar_proyectosSin_archivo();
                    self.consultar_proyectosCon_archivo();
                    self.checkallProyectoArchivo(false);
                 })

             }       
    }

    self.checkallProyecto.subscribe(function(value ){
         ko.utils.arrayForEach(self.listado_proyecto(), function(d) { d.procesar(value); }); 
    }); 

    self.checkallProyectoArchivo.subscribe(function(value ){
         ko.utils.arrayForEach(self.listado_proyecto_archivo(), function(d) { d.eliminado(value); }); 
    });

// USUARIO ARCHIVO --- USUARIO ARCHIVO // USUARIO ARCHIVO --- USUARIO ARCHIVO // USUARIO ARCHIVO --- USUARIO ARCHIVO// USUARIO ARCHIVO --- USUARIO ARCHIVO
    self.abrir_modal_compartir = function () {
        var lista_id='';
        var count=0;

         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count = count + 1;              
                }
                return false;
         }); 

        if(count==1){
            self.consultar_empresas();
            self.consultar_usuarioCon_archivo();
            self.consultar_usuarioSin_archivo();
            $('#modal_acciones_compartir').modal('show');     
        }else if(count>1){
            mensajeInformativo(' Señor(a) usuario solo se puede compartir un archivo o carpeta.','Mi Nube');
        }else{
            mensajeInformativo(' Se debe seleccionar un archivo o carpeta para compartirlo con los usuarios.','Mi Nube');
        }        
    }

     //funcion consultar empresas
    self.consultar_empresas = function () {                
            path = self.url+'empresaAcceso/';
            parameter = { ignorePagination : 1 , empresa : self.mi_nubeVO.empresa_id() };
            
                RequestGet(function (datos, estado, mensage) {
                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                        self.listado_empresas(datos);                    
                    } else {
                        self.listado_empresas([]);
                    }             
                }, path, parameter);           
    }

    self.empresaUsuario_filtro.subscribe(function(value ){
        self.consultar_usuarioSin_archivo();
    }); 

    self.consultar_usuarioSin_archivo_btn = function () {
        self.consultar_usuarioSin_archivo();
    }
    self.consultar_usuarioSin_archivo_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_usuarioSin_archivo();
        }
        return true;
    }

    //usuarios que no estan asociados al archivo
    self.consultar_usuarioSin_archivo = function () { 
        filtro_usuario = $('#txtBuscarUsuario').val()
        var lista_id=[];
        var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                   lista_id = lista_id+d.id+','                 
                }
         }); 
            
        path = self.url_app_miNube+'list_usuarioSin_archivo/';
        parameter = { archivo : lista_id.substring(0,lista_id.length-1) 
                    , empresa : self.empresaUsuario_filtro() 
                    , dato : filtro_usuario };
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensajePorAsignar('');
                self.listado_usuario(agregarOpcionesObservable(datos))
            } else {
                self.listado_usuario([]);
                self.mensajePorAsignar(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);   
    }

    self.empresaUsuarioArchivo_filtro.subscribe(function(value ){
        self.consultar_usuarioCon_archivo();
    });

     self.consultar_usuarioCon_archivo_btn = function () {
        self.consultar_usuarioCon_archivo();
    }
    self.consultar_usuarioCon_archivo_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_usuarioCon_archivo();
        }
        return true;
    }

    //usuarios que estan asociados al archivo
    self.consultar_usuarioCon_archivo = function () { 
        filtro_usuario = $('#txtBuscarUsuarioArchivo').val() 

        var lista_id='';
        var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                   lista_id = lista_id+d.id+','                 
                }
         }); 
            
        path = self.url_app_miNube+'list_usuarioCon_archivo/';
        parameter = { archivo : lista_id.substring(0,lista_id.length-1) 
                    , empresa : self.empresaUsuarioArchivo_filtro()  
                    , dato : filtro_usuario };
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensajeAsignados('');
                self.listado_usuario_archivo(agregarOpcionesObservable(convertToObservableArray(datos)));

                ko.utils.arrayForEach(self.listado_usuario_archivo(), function(d) {
                        d.eliminado(true)
                 }); 

                self.checkallUsuarioArchivo(true);


            } else {
                self.listado_usuario_archivo([]);
                self.mensajeAsignados(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);   
    }
    // //funcion asociar usuarios a los archivos seleccionados
    self.asociar_usuario=function(){
             var lista_id=[];
             var lista_archivo = [];
             var count=0;
             ko.utils.arrayForEach(self.listado_usuario(), function(d) {
                    if(d.procesar()==true){
                        count=1;
                       lista_id.push({'id': d.id , 'escritura': d.valor_generico()==true})
                    }
             });

             ko.utils.arrayForEach(self.listado(), function(d) {
                    if(d.eliminado()==true){                       
                        lista_archivo.push(d.id);                
                    }
             });

            if(count==0){
                 $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione un usuario para compartir los archivos seleccionados.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }else{
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.consultar_usuarioSin_archivo();
                            self.consultar_usuarioCon_archivo();
                            self.checkallUsuario(false);
                            self.consultar();

                            setTimeout(function(){ 
                                ko.utils.arrayForEach(self.listado(), function(d) {
                                    if(lista_archivo.includes(d.id)){                       
                                        d.eliminado(true);                
                                    }
                                });
                            }, 2000);                            
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url_app_miNube+'create_usuarioCon_archivo/',//url api
                     parametros: { archivo : lista_archivo , usuario : lista_id }                         
                };
                Request(parametros);
            }        
    }

    self.quitar_usuario=function(){
             var lista_id=[];
             var lista_update=[];
             var lista_archivo = [];
             var count=0;
             ko.utils.arrayForEach(self.listado_usuario_archivo(), function(d) {
                    if(d.eliminado()==false){
                        count=1;
                       lista_id.push(d.usuario_id)
                    }
                    if(d.escritura()==true){
                        lista_update.push({'id' : d.usuario_id , 'escritura' : 1})
                    }else if(d.escritura()==false && d.eliminado()==true){
                        lista_update.push({'id' : d.usuario_id , 'escritura' : 0})
                    }
             });

             ko.utils.arrayForEach(self.listado(), function(d) {
                    if(d.eliminado()==true){
                       lista_archivo.push(d.id)
                    }
             });

                 var path =self.url_app_miNube+'destroy_usuarioCon_archivo/';
                 var parameter = { archivo : lista_archivo , usuario : lista_id 
                                 , listaUpdate : lista_update 
                                 };
                 RequestAnularOEliminar("Esta seguro que desea actualizar los permisos de los usuarios?", path, parameter, function () {
                    self.consultar_usuarioSin_archivo();
                    self.consultar_usuarioCon_archivo();
                    self.checkallUsuarioArchivo(false);
                    self.consultar();
                        setTimeout(function(){ 
                            ko.utils.arrayForEach(self.listado(), function(d) {
                                if(lista_archivo.includes(d.id)){                       
                                    d.eliminado(true);                
                                }
                            });
                        }, 2000); 
                 })     
    }

    self.checkallUsuario.subscribe(function(value ){
         ko.utils.arrayForEach(self.listado_usuario(), function(d) {
                d.procesar(value);
                if(value==false){
                    d.valor_generico(false);
                }
         }); 
    });
    self.checkallUsuarioEscritura.subscribe(function(value ){
         ko.utils.arrayForEach(self.listado_usuario(), function(d) {
                d.valor_generico(value);
                if(value==true){
                    d.procesar(true)
                }
         }); 
    }); 
    self.checkallUsuarioArchivo.subscribe(function(value ){
         ko.utils.arrayForEach(self.listado_usuario_archivo(), function(d) {
                d.eliminado(value);
                if(value==false){
                    d.escritura(false)
                }
         }); 
    });
    self.checkallUsuarioArchivoEscritura.subscribe(function(value ){
         ko.utils.arrayForEach(self.listado_usuario_archivo(), function(d) {
                d.escritura(value);
                if(value==true){
                    d.eliminado(true)
                }
         }); 
    });
    self.escrituraUsuario = function(obj){
        if(obj.valor_generico()==true){
            obj.procesar(obj.valor_generico())   
        }         
    }
    self.lecturaUsuario = function(obj){
        if(obj.procesar()==false){
            obj.valor_generico(obj.procesar())   
        }         
    }
    self.escrituraUsuarioConArchivo = function(obj){
        if(obj.escritura()==true){
            obj.eliminado(obj.escritura())   
        }         
    }
    self.lecturaUsuarioConArchivo = function(obj){
        if(obj.eliminado()==false){
            obj.escritura(obj.eliminado())   
        }         
    }
//---- MENU CONTEXTUAL ---- // ---- MENU CONTEXTUAL ----//    
    self.abrir_menu_contextual = function(d,e){
        /*console.log(d.id+' '+d.nombre)*/

        tipo = d.tipoArchivo_id;

        if (e.button == 2){
            $("#menuCapa").css("top", e.pageY - 20);
            $("#menuCapa").css("left", e.pageX - 230);
            $("#menuCapa").show('fast');
            self.mi_nubeVO.id(d.id);
            self.mi_nubeVO.nombre(d.nombre);
            self.mi_nubeVO.nombreActual(d.nombre);

            self.propietario(d.propietario)
            self.usuarioModificado(d.usuarioModificado)

            self.tipoArchivo(d.tipoArchivo)
            self.mi_nubeVO.fechaModificado(d.fechaModificado)
            self.mi_nubeVO.peso(d.peso);

            if(tipo==2 || tipo==3 || tipo==4){
                    $("#item7presentation").show();
            }else{
                    $("#item7presentation").hide();
            }
            self.consultar_arbol();           
        }
    }

// EDITAR ---- EDITAR ----- EDITAR ------ EDITAR ----- EDITAR
    self.consultar_por_id = function(){
        path =self.url+'MiNubeArchivo/'+self.mi_nubeVO.id()+'/';
         RequestGet(function (results,count) {           
            self.mi_nubeVO.id(results.id);
            self.mi_nubeVO.nombre(results.nombre);
            self.mi_nubeVO.nombreActual(results.nombre);
            self.mi_nubeVO.padre(results.padre);
            
            destino = results.destino
            if(destino == null){
                destino = '';
            }
            self.mi_nubeVO.destino(destino);
            self.mi_nubeVO.tipoArchivo_id(results.tipoArchivo.id);
            self.mi_nubeVO.eliminado(results.eliminado);
            self.mi_nubeVO.peso(results.peso);
            self.mi_nubeVO.propietario_id(results.propietario.id);
            self.mi_nubeVO.validaNombre(results.validaNombre); 
            $('#modal_acciones_editar').modal('show');      
         }, path, parameter);            
    }
    self.abrir_modal_editar = function () {
         var id=0;
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count= count+1;
                    id=d.id                   
                }
         });

         if(count==1){
            self.mi_nubeVO.id(id);
            self.consultar_por_id();    
         }else if(count<1){
           mensajeInformativo('Se debe seleccionar un archivo o carpeta para modificar el nombre.','Mi Nube');
         }else if(count>1){
           mensajeInformativo('Se debe seleccionar solo un archivo para modificar el nombre.','Mi Nube');
         }        
    }
    // //funcion actualizar nombre del archivo
     self.actualizar_nombre_archivo=function(){

        valida_caracter = false;

        var miArray = ['\\' ,'/' ,':' ,'*' ,'?' ,'"' ,'<' ,'>' ,'|'];
        for (var i in miArray) {
            if (self.mi_nubeVO.nombre().indexOf(miArray[i]) != -1){
                valida_caracter = true;
                texto = self.mi_nubeVO.nombre()
                self.mi_nubeVO.nombre(texto.replace(miArray[i] , ""))
            }            
        }


            if(self.mi_nubeVO.id()>0 && self.mi_nubeVO.nombre()!='' && valida_caracter==false){
                var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {

                                path = self.url_app_miNube+'list_archivo_carpeta/';
                                parameter = {  };
                                RequestGet(function (datos, estado, mensage) {
                                    if (estado == 'ok' && datos!=null && datos.length > 0) {                       
                                        $('#jstree').jstree(true).settings.core.data = datos;
                                        $('#jstree').jstree(true).refresh(); 
                                        self.consultar();
                                    }
                                }, path, parameter);                               
                              
                              $('#modal_acciones_editar').modal('hide');
                              self.checkall(false)
                            } 
                       },//funcion para recibir la respuesta 
                       url: self.url+'MiNubeArchivo/'+self.mi_nubeVO.id()+'/',
                       parametros:self.mi_nubeVO                        
                  };
                Request(parametros);
            }else{
                if(valida_caracter){
                    mensajeInformativo('Los nombres de archivo no puedes contener ninguno de los siguientes caracteres: \\ / : * ? " < > |','Mi Nube');
                }else{
                    mensajeInformativo('El campo nombre no puede estar vacio.','Mi Nube');    
                }                
            }        
     }

// ELIMINAR ARCHIVO ---- ELIMINAR ARCHIVO ---- ELIMINAR ARCHIVO ---- 
    self.eliminar = function () {
         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                     
                    if (self.mi_nubeVO.usuario_id() == d.propietario_id){
                        count=1;
                        lista_id.push(d.id)
                    }else{
                      count = 2
                    }
                }
         }); 
         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });              
         }else if(count==1){
             var path =self.url_app_miNube+'destroyArchivo/';
             var parameter = { lista: lista_id , usuario : self.mi_nubeVO.usuario_id() };
             RequestAnularOEliminar("Esta seguro que desea eliminar los archivos seleccionados?", path, parameter, function () {
                 
                 path = self.url_app_miNube+'list_archivo_carpeta/';
                 parameter = {  };
                 RequestGet(function (datos, estado, mensage) {
                    if (estado == 'ok' && datos!=null && datos.length > 0) {                    
                        $('#jstree').jstree(true).settings.core.data = datos;
                        $('#jstree').jstree(true).refresh(); 
                        $('#Rmover-archivo').jstree(true).settings.core.data = datos;
                        $('#Rmover-archivo').jstree(true).refresh(); 
                        self.consultar();
                    }
                }, path, parameter); 
                
                self.checkall(false);
             })

         }else{
            mensajeInformativo(' Esta intentando eliminar archivos que no son de su propiedad.','Mi Nube');
         }    
    } 
    // eliminar opcion del menu contextual
    self.eliminar2 = function(){
        lista_id = []
        id = self.mi_nubeVO.id()
        lista_id.push(id)
        var path =self.url_app_miNube+'destroyArchivo/';
        var parameter = { lista: lista_id , usuario : self.mi_nubeVO.usuario_id() };
        RequestAnularOEliminar("Esta seguro que desea eliminar el archivo seleccionado?", path, parameter, function () {
             
             path = self.url_app_miNube+'list_archivo_carpeta/';
             parameter = {  };
             RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {                    
                    $('#jstree').jstree(true).settings.core.data = datos;
                    $('#jstree').jstree(true).refresh(); 
                    $('#Rmover-archivo').jstree(true).settings.core.data = datos;
                    $('#Rmover-archivo').jstree(true).refresh(); 
                    self.consultar();
                }
            }, path, parameter); 
             self.checkall(false);
        })
    }

// MOVER ARCHIVO ----- MOVER ARCHIVO ----- MOVER ARCHIVO ----- MOVER ARCHIVO
    self.abrir_modal_mover = function(){       
        $('#Rmover-archivo').jstree("close_all");   
        $('#Rmover-archivo').jstree("open_node",1);
        $("#Rmover-archivo").jstree("deselect_all");
        $("#Rmover-archivo").jstree("select_node",'#1');
        var id = self.mi_nubeVO.id()        
        var instance = $('#Rmover-archivo').jstree(true);
        setTimeout(function(){ 
            instance.delete_node(id);
        },300);
        $('#moverArchivo').modal('show');
    }

    self.mover_archivo = function (){

        carpetaSelected = $('#Rmover-archivo').jstree("get_selected");
        archivo_id = self.mi_nubeVO.id();

        if(carpetaSelected==0 || carpetaSelected=='undefined'){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione una carpeta para mover el archivo o carpeta seleccionada.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });              
         }else if(carpetaSelected>0){
             var path =self.url_app_miNube+'move_file/';
             var parameter = { padre_id : parseInt(carpetaSelected) , archivo_id : archivo_id , usuario : parseInt(self.mi_nubeVO.usuario_id()) };
             RequestAnularOEliminar(" Esta seguro que desea mover el archivo o carpeta seleccionada?", path, parameter, function () {

                 path = self.url_app_miNube+'list_archivo_carpeta/';
                 parameter = {  };
                 RequestGet(function (datos, estado, mensage) {
                    if (estado == 'ok' && datos!=null && datos.length > 0) {                       
                        $('#jstree').jstree(true).settings.core.data = datos;
                        $('#jstree').jstree(true).refresh(); 
                        $('#Rmover-archivo').jstree(true).settings.core.data = datos;
                        $('#Rmover-archivo').jstree(true).refresh(); 
                        self.consultar();
                    }
                }, path, parameter); 
                 self.checkall(false);
             })
         } 
    }
// DETALLE DEL ARCHIVO ----- DETALLE DEL ARCHIVO ----- DETALLE DEL ARCHIVO  
    self.detalle_archivo = function(){
        $('#detalleArchivoM').modal('show');  
    }
// VALIDAR ESPACIO ----- VALIDAR ESPACIO ----- VALIDAR ESPACIO
    self.consultar_espacio = function () {                
            path = self.url_app_miNube+'valida_espacio/';
            parameter = { empresa : self.mi_nubeVO.empresa_id() };
            
                RequestGet(function (datos, estado, mensage) {
                    if (estado == 'ok' && datos!=null && datos.length > 0) { 
                        
                        $("#espacioPorcentaje").css( "width", datos[0].porcentajeUsado+"%" );
                        self.espacioUtilizado(datos[0].espacioUtilizado)
                        self.espacioTotal(datos[0].espacioTotal)  

                    } else {
                        
                    }             
                }, path, parameter);           
    }

//-- DRAG AND DROG --- //-- DRAG AND DROG --- //-- DRAG AND DROG --- //-- DRAG AND DROG --- //-- DRAG AND DROG --- //-- DRAG AND DROG ---
    self.dragover = function(e){
        /*console.log('dragOver');*/
        e.stopPropagation();
        e.preventDefault();
    }

    self.drop = function(e, data){
        /*console.log('drop');*/
        e.stopPropagation();
        e.preventDefault();        

        /*if (e.dataTransfer) {
            var files = e.dataTransfer.files;
            //console.log(data)
        }
        else if (e.originalEvent.dataTransfer){
            //console.log(e)
            var files = e.originalEvent.dataTransfer.files;            
        }
        var formData= new FormData();*/

        /*for (var i = 0, f; f = files[i]; i++) {
            //data.elements.push(f.name);
            //console.log(f)
            formData.append("archivos[]",f);
        }*/

        /*var parametros={                     
            callback:function(datos, estado, mensaje){
                if (estado=='ok') {
                  
                }                     
             },
             url: self.url_app_miNube+'subir_archivoAsync/',
             parametros:formData                       
        };
        RequestFormData2(parametros);*/

        /*console.log(files)*/
        /*$('.drop_zone').css('background-color', '#ffffff');*/
    }

    self.dragenter = function(e, index){
        /*console.log('dragEnter');*/
        /*$('.drop_zone').eq(index).css('background-color', '#00ff00');*/
    }

    self.dragleave = function(e, index){
        /*console.log('end');*/
        /*$('.drop_zone').eq(index).css('background-color', '#ffffff');*/
    }
    //DOBLE CLICK IZQUIERDO
    self.dobleclick  = function(d,e){
        /*SI TIPO DE ARCHIVO ES 58 PORQUE ES UNA CARPETA*/
        if(d.tipoArchivo_id==58){
            $('#jstree').jstree("close_all");   
            $('#jstree').jstree("open_node",d.id);
            $("#jstree").jstree("deselect_all");
            $("#jstree").jstree("select_node",'#'+d.id);
            self.consultar();
        }else{
            // window.open(d.destino,"_blank");                       
            // location.href=path_principal+"/miNube/descargar-un-archivo/?archivo="+ d.id;
            window.open(path_principal+"/miNube/descargar-un-archivo/?archivo="+ d.id, "_blank");
        }
    }

}

var mi_nube = new MiNubeViewModel();
MiNubeViewModel.errores_carpeta = ko.validation.group(mi_nube.mi_nubeVO);
MiNubeViewModel.errores_carpeta2 = ko.validation.group(mi_nube.proyecto_id);
mi_nube.consultar_arbol();
mi_nube.consultar();
mi_nube.consultar_mcontratos_filtro();
mi_nube.consultar_espacio();
mi_nube.consultar_estados_contrato();
ko.applyBindings(mi_nube);
