function ConfiguracionViewModel (){
	var self=this;
	self.listado=ko.observableArray([]);
	self.url=path_principal+'/api/servidumbreconfiguracion/';
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	self.checkallDocumentos=ko.observable(false);
	self.mensaje=ko.observable('');
    self.mensajeDocumento=ko.observable('');
	self.grupo=ko.observable('');
	self.buscado_rapido=ko.observable(false);

    self.url_funcion=path_principal+'/servidumbre/';    
    self.urlHOME=path_principal+'/servidumbre/configuracion/'

    self.titulo=ko.observable('');
    self.titulo_grupo=ko.observable('');
    self.filtroDocumento = ko.observable('');
    self.listadoDocumentos=ko.observableArray([]);


    self.filtro_GrupoVO={
        dato:ko.observable(''),
        id:ko.observable(''),
        nombre:ko.observable(''),        
        
    };


    self.filtro_DocumentoVO={
        dato:ko.observable(''),
        id:ko.observable(''),
        grupo_documento_id:ko.observable(0),
        nombre:ko.observable(''),        
        
    };

	self.GrupoVO={
		id:ko.observable(0),
		nombre:ko.observable('').extend({ required: { message: ' Digite el nombre del grupo.' } }),
	}

	self.DocumentoVO={
		id:ko.observable(0),
        grupo_documento_id:ko.observable(0).extend(),
		nombre:ko.observable('').extend({ required: { message: ' Digite el nombre del documento.' } }),

	}

    self.limpiarGrupo = function(){
        self.GrupoVO.id(0);
        self.GrupoVO.nombre('');
    }

    
    self.limpiarModeloDocumentos = function(){
        self.DocumentoVO.id(0);
        self.DocumentoVO.nombre('');
        // self.DocumentoVO.grupo_documento_id(0);
    }

	self.buscarGrupo = function (d,e){
	    if (e.which == 13) {
            //self.consultar(1);
            self.get_grupo(1)
        }
        return true;
    }
    self.buscarDocumento = function (d,e){
	    if (e.which == 13) {
            //self.consultar(1);
            self.get_documentos(1,$("#idGrupo").val())
        }
        return true;
    }

    self.get_grupo=function(pagina){
		//Codigo para consultar los grupos
        path = path_principal+'/api/servidumbregrupodocumento?lite=1&format=json&page=' + pagina;;
        if (pagina > 0) {
            //alert('entre aqui' + pagina); 
            //self.buscado_rapido(true);
            self.filtro($('#txtBuscarGrupo').val());
            parameter = {
                dato: self.filtro(),              
            };
            RequestGet(function(datos, estado, mensage) {
                //alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data));
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                
                self.llenar_paginacion(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }

    self.get_documentos=function(pagina,grupo_documento_id){
		path = path_principal+'/api/servidumbredocumento?lite=1&format=json&page=' + pagina; 
        if (pagina > 0) {
            self.buscado_rapido(true);
            self.filtroDocumento($('#txtBuscarDocumento').val());      
           
            // path = self.url_funcion+'listServidumbreDocumentos?format=json&page=' + pagina; 
              

            parameter = {
                dato: self.filtroDocumento(),
                page: pagina,
                grupo_documento_id: grupo_documento_id            
            };
            RequestGet(function(datos, estado, mensage) {
                //alert(datos.data);
                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensajeDocumento('');
                    self.listadoDocumentos(agregarOpcionesObservable(datos.data));
                } else {
                    self.listadoDocumentos([]);
                    self.mensajeDocumento(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                
                self.llenar_paginacionDocumentos(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);

        }
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
    self.paginacionDocumetos = {
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

    self.llenar_paginacion = function (data,pagina) {
		self.paginacion.pagina_actual(pagina);
		self.paginacion.total(data.count);
		self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

    self.llenar_paginacionDocumentos = function (data,pagina) {
		self.paginacionDocumetos.pagina_actual(pagina);
		self.paginacionDocumetos.total(data.count);
		self.paginacionDocumetos.cantidad_por_paginas(resultadosPorPagina);

    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {    
            self.get_grupo(pagina);
             
    });

    self.paginacionDocumetos.pagina_actual.subscribe(function (pagina) {
     
             self.get_documentos(pagina,$('#idGrupo').val());
         
                
    });

    self.checkallDocumentos.subscribe(function(value ){

             ko.utils.arrayForEach(self.listadoDocumentos(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.consultar_documentos_del_grupo = function (obj){     
    	$("#divDocumentos").show(); 
        // self.GrupoVO.id(obj.id);
    	self.titulo_grupo('Documentos del Grupo ['+obj.nombre+']: ');   
        self.DocumentoVO.grupo_documento_id(obj.id);
        $("#txtDocumentoGrupoNombre").val(obj.nombre);     
        self.get_documentos(1,obj.id);     
    	  
             

    }

    self.abrir_modalGrupo = function () {
        self.titulo('Agregar nuevo grupo de documentos'); 
        $('#modal_nuevo_grupo').modal('show');
        return true;
    }

    self.abrir_modalDocumento = function () {
        self.titulo('Agregar nuevo documento'); 
        $('#modal_nuevo_documento').modal('show');
        return true;
    }

    self.guardarGrupo = function(){
        if (ConfiguracionViewModel.errores_grupo().length == 0){
      
            if (self.GrupoVO.id() == 0) {
                var parametros={
                        
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.get_grupo(self.paginacion.pagina_actual());
                        self.limpiarGrupo();
                    }                     
                },//funcion para recibir la respuesta 
                url: path_principal + '/api/servidumbregrupodocumento/',//url api
                parametros:self.GrupoVO                        
                };
                RequestFormData(parametros);

            }else{

                var parametros={ 
                    metodo:'PUT',                
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.cargar(self.paginacion.pagina_actual());
                            self.limpiarGrupo();
                        }
                    },
                    url: path_principal + '/api/servidumbregrupodocumento/'+ self.GrupoVO.id()+'/',//url api
                    parametros:self.GrupoVO  

                };
                RequestFormData(parametros);
            }

            // location.href=self.urlHOME;    
        }else{
            ConfiguracionViewModel.errores_grupo.showAllMessages();
        }
    }




    self.guardarDocumento = function(){
        if (ConfiguracionViewModel.errores_documunento().length == 0){
             
            if (self.DocumentoVO.grupo_documento_id() != 0) {
                $("#validacionGrupoDocumento").hide();

                if(self.DocumentoVO.id() == 0){               
                    var parametros={

                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.get_documentos(self.paginacionDocumetos.pagina_actual(),self.DocumentoVO.grupo_documento_id());
                            self.limpiarModeloDocumentos();
                        }                     
                    },//funcion para recibir la respuesta 
                     url: path_principal + '/api/servidumbredocumento/',//url api
                     parametros:self.DocumentoVO                        
                    };
                    RequestFormData(parametros);

                }else{

                    var parametros={ 
                       metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                                self.cargar(self.paginacionDocumetos.pagina_actual());
                                self.limpiarModeloDocumentos();
                            }
                        },
                        url: path_principal + '/api/servidumbredocumento/'+ self.DocumentoVO.id()+'/',//url api
                        parametros:self.DocumentoVO  
                    };
                    RequestFormData(parametros);
                }  
                // location.href=self.urlHOME;          
            }else{
                $("#validacionGrupoDocumento").show();
            }
        }else{
           ConfiguracionViewModel.errores_documunento.showAllMessages();
        }
    }

    self.eliminarDocumentos = function(){
         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listadoDocumentos(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione documentos.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/servidumbre/eliminar_documentos/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea cerrar los documentos seleccionados?", path, parameter, function () {
                 self.get_documentos(1,$("#idGrupo").val());
                 self.checkallDocumentos(false);
             })

         } 


    }
    self.eliminarGrupos = function(){
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione grupos de documentos.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/servidumbre/eliminar_grupos/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea cerrar los grupos seleccionados?", path, parameter, function () {
                 self.get_grupo(1);
                 self.checkall(false);
             })

         }  



    }





}







var grupo = new ConfiguracionViewModel();

ConfiguracionViewModel.errores_grupo = ko.validation.group(grupo.GrupoVO);
ConfiguracionViewModel.errores_documunento = ko.validation.group(grupo.DocumentoVO);
ko.applyBindings(grupo);