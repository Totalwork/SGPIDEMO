function CorrespondenciaEnviadaViewModel() {

  administraccion_de_recurso = 12;

	var self = this;

    self.url=path_principal+'/api/'; 
    self.listado=ko.observableArray([]);
	  self.mensaje=ko.observable('');
    self.mensajePorAsignar=ko.observable('');
    self.mensajeAsignados=ko.observable('');
    self.titulo=ko.observable('');
    self.titulo_btn=ko.observable('');
    self.filtro=ko.observable('');
    self.url_app_correspondencia = '/correspondencia/'
    self.url_app_parametrizacion = path_principal+'/parametrizacion/';
    self.url_app_proyecto = '/proyecto/';
    self.app_contrato = 'contrato';
    self.contratista_id_filtro =ko.observable('');
    self.mcontrato_id_filtro =ko.observable('');
    self.mcontrato_id_filtroContrato =ko.observable('');
    self.estado_id_filtro =ko.observable('');

    self.filtro_contrato = ko.observable('');
    self.filtro_contrato_correspondencia = ko.observable('');
    self.filtro_proyecto = ko.observable('');
    self.filtro_proyecto_correspondencia = ko.observable('');

    /* destinatario correspondencia 1 es copia ; 0 es propietario*/
    self.usuarioCopiado=ko.observable(1);
    self.usuarioRecibecarta=ko.observable(0);
    self.usuarioPropietario=ko.observable(0);

    self.newArray = ko.observableArray([]);
    self.arrayUsuario = ko.observableArray([]);

    //LISTADOS   
  	self.listado_correspondencias=ko.observableArray([]);

    self.listado_departamentosEmpresa = ko.observableArray([]);
    self.listado_municipiosEmpresa = ko.observableArray([]);

  	self.listado_departamentos = ko.observableArray([]);
    self.listado_municipios = ko.observableArray([]);
	  self.listado_prefijos = ko.observableArray([]);
	  self.listado_funcionarios = ko.observableArray([]);
    self.listado_funcionarios_firma = ko.observableArray([]);
    self.listado_funcionarios_copia = ko.observableArray([]);
    self.listado_empresas = ko.observableArray([]);

    self.listado_destinatarios_copia = ko.observableArray([]); //manejo de datos
    self.listado_destinatarios_con_copia = ko.observableArray([]);// manejo de datos
    self.listado_funcionarios_elaboran = ko.observableArray([]);


    self.listado_contratos_tabla = ko.observableArray([]);
    self.listado_proyectos_tabla = ko.observableArray([]);

    self.listado_correspondencia_contratos = ko.observableArray([]);
    self.listado_correspondencia_proyectos = ko.observableArray([]);

    self.listado_correspondencia_soportes = ko.observableArray([]);

    self.listado_macro_contrato_filtro = ko.observableArray([]);
    self.listado_contratista_filtro = ko.observableArray([]);

    self.listado_estados_contrato = ko.observableArray([]);



    //FILTRO  DE CORRESPONDENCIA
    self.filtro_desde=ko.observable('');
    self.filtro_hasta=ko.observable('');
    self.filtro_firma=ko.observable(0);
    self.filtro_elaboradoPor=ko.observable(0);
    self.filtro_soporte=ko.observable(0);

    self.checkall = ko.observable(false);
    self.checkallContratos=ko.observable(false);
    self.checkallProyectos=ko.observable(false);
    self.checkallCorrespondenciaContratos = ko.observable(false);
    self.checkallCorrespondenciaProyectos = ko.observable(false);
    self.checkallSoportes = ko.observable(false);


    // variables empresa destinatario filtro 
    self.filtro_empresaDestinatario = ko.observable('');
    self.filtro_empresaDestinatarioCopia = ko.observable('');

    self.filtro_Destinatario = ko.observable('');
    self.filtro_DestinatarioCopia = ko.observable('');

    self.departamentoEmpresa_id =ko.observable('');

    //Representa un modelo de la tabla correspoondenciaEnviada
    self.correspondenciaEnviadaVO={
      id:ko.observable(0),
      consecutivo:ko.observable('').extend({ validation: { validator: validar_consecutivo, message: '(*) Digite el consecutivo.' } }),
      anoEnvio:ko.observable(0),
      fechaEnvio:ko.observable('').extend({ required: { message: ' Digite la fecha de envio.' } }),
      departamento_id:ko.observable('').extend({ required: { message: ' Seleccione el departamento.' } }),
      ciudad_id:ko.observable('').extend({ required: { message: ' Seleccione la ciudad.' } }),
      prefijo_id:ko.observable('').extend({ required: { message: ' Seleccione el prefijo.' } }),
      asunto:ko.observable('').extend({ required: { message: ' Digite el asunto de la carta.' } }),
      referencia:ko.observable('').extend({ required: { message: ' Digite la referencia de la carta.' } }),        
      contenido:ko.observable(''),
      contenidoHtml:ko.observable(''),
      firma_id:ko.observable('').extend({ required: { message: ' Seleccione el funcionario a firmar.' } }), 
      privado:ko.observable('').extend({ required: { message: ' Seleccione el permiso.' } }),
      grupoSinin:ko.observable('0'),
      destinatario:ko.observable(0), 
      destinatarioCopia:ko.observableArray([]),        
      empresa_destino:ko.observable(''),
      cargo_persona:ko.observable(''),
      persona_destino:ko.observable(''),
      direccion:ko.observable(''),
      telefono:ko.observable(''),
      municipioEmpresa_id:ko.observable('').extend({ required: { message: ' Seleccione la ciudad del destinatario.' } }),
      usuarioSolicitante_id:ko.observable($("#user").val()),
      empresa_id:ko.observable($("#company").val()),
      proyecto_id:ko.observable(0),
    };

    self.correspondenciaEnviadaVO_filtro={
      firma:ko.observable(''),
      usuarioElaboro:ko.observable(''),
      soporte_si:ko.observable(1),
      soporte_no:ko.observable(1),
      asunto:ko.observable(1),
      referencia:ko.observable(1),
      consecutivo:ko.observable(1),
      destinatario:ko.observable(1),
      fechaDesde:ko.observable(''),//.extend({ validation: { validator: validar_fecha_inicio, message: '(*) La fecha desde no puede ser mayor que la fecha hasta.' } }),
      fechaHasta:ko.observable('')//.extend({ validation: { validator: validar_fecha_final, message: '(*) La fecha hasta no puede ser menor que la fecha desde.' } }),

    }
   //INFORMACION DE LOS CONTRATOS
   self.correspondenciaEnviada_contratoVO = {
        id: ko.observable(0),
        correspondenciaenviada_id: ko.observable(''),
        contrato_id: ko.observableArray([]),
   
    };

    //INFORMACION DE LOS PROYECTOS
   self.correspondenciaEnviada_proyectoVO = {
        id: ko.observable(0),
        correspondenciaenviada_id: ko.observable(''),
        proyecto_id: ko.observableArray([]),
   
    };

   //INFORMACION DE LOS SOPORTES
   self.correspondencia_soporteVO = {
        id: ko.observable(0),
        correspondencia_id: ko.observable(''),
        soporte: ko.observable(''),
        validaNombre : ko.observable(0),
        nombre : ko.observable(''),
        soporte_id: ko.observableArray([]),/* SE USA ESTA LISTA PARA ELIMINAR VARIOS SOPORTES A LA VES*/   

    };

    function validar_consecutivo(val){
      consecutivo = $("#consecutivoHabilitado").val();
      return consecutivo=="False" || (consecutivo=="True" && val!=null && val!='');
    }

    // //limpiar el modelo 
     self.limpiar_correspondencia_soporteVO=function(){      
            self.correspondencia_soporteVO.id(0);
            /*self.correspondencia_soporteVO.correspondencia(0);*/
            self.correspondencia_soporteVO.soporte('');
            self.correspondencia_soporteVO.validaNombre(0);
            self.correspondencia_soporteVO.nombre('');
            self.correspondencia_soporteVO.soporte_id([]);

            $('#archivo').fileinput('reset');
            $('#archivo').val('');
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

    self.correspondenciaEnviadaVO.grupoSinin.subscribe(function(value ){
            if(value == '1'){
                self.correspondenciaEnviadaVO.empresa_destino('');
                self.correspondenciaEnviadaVO.cargo_persona('');
                self.correspondenciaEnviadaVO.persona_destino('');
                self.correspondenciaEnviadaVO.direccion('');
                self.correspondenciaEnviadaVO.telefono('');
            }else{
                self.correspondenciaEnviadaVO.destinatario(0);
            }
    });

    self.correspondenciaEnviadaVO.departamento_id.subscribe(function (val) {
        if(val!=""){
            self.consultar_municipios(val)   
        }else{
            self.listado_municipios([]);
        }   
    });

    self.departamentoEmpresa_id.subscribe(function (val) {
        if(val!=""){
            self.consultar_municipiosEmpresa(val)   
        }else{
            self.listado_municipiosEmpresa([]);
        }   
    });

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
          /*console.log(self.listado_destinatarios_con_copia().length);*/
        }        
    }
	   // //limpiar el modelo 
     self.limpiar_correspondencia_enviada=function(){      
        self.correspondenciaEnviadaVO.id(0);
        self.correspondenciaEnviadaVO.consecutivo('');
        self.correspondenciaEnviadaVO.fechaEnvio('');
        self.correspondenciaEnviadaVO.departamento_id('');
        self.correspondenciaEnviadaVO.ciudad_id('');
        self.correspondenciaEnviadaVO.prefijo_id('');
        self.correspondenciaEnviadaVO.asunto('');
        self.correspondenciaEnviadaVO.referencia('');
        self.correspondenciaEnviadaVO.contenido('');
        self.correspondenciaEnviadaVO.contenidoHtml('');
        self.correspondenciaEnviadaVO.firma_id('');
        self.correspondenciaEnviadaVO.privado('');
        self.correspondenciaEnviadaVO.grupoSinin('0');
        self.correspondenciaEnviadaVO.destinatario(0);
        self.correspondenciaEnviadaVO.destinatarioCopia([]);
        self.correspondenciaEnviadaVO.empresa_destino('');
        self.correspondenciaEnviadaVO.cargo_persona('');
        self.correspondenciaEnviadaVO.persona_destino('');
        self.correspondenciaEnviadaVO.direccion('');
        self.correspondenciaEnviadaVO.telefono('');
        self.correspondenciaEnviadaVO.municipioEmpresa_id('');

        self.listado_destinatarios_con_copia([]);
        self.correspondenciaEnviadaVO.consecutivo.isModified(false);
        self.correspondenciaEnviadaVO.fechaEnvio.isModified(false);
        self.correspondenciaEnviadaVO.departamento_id.isModified(false);
        self.correspondenciaEnviadaVO.ciudad_id.isModified(false);
        self.correspondenciaEnviadaVO.prefijo_id.isModified(false);
        self.correspondenciaEnviadaVO.asunto.isModified(false);
        self.correspondenciaEnviadaVO.referencia.isModified(false);
        self.correspondenciaEnviadaVO.privado.isModified(false);
        self.correspondenciaEnviadaVO.firma_id.isModified(false);
        self.correspondenciaEnviadaVO.municipioEmpresa_id.isModified(false);
        
        if(tinymce.activeEditor==null)
        {
         $("#contenido").html('');
        }
        else{
          tinymce.activeEditor.setContent('')
          tinymce.activeEditor.execCommand('mceCleanup'); 
        }    
        
     }

     self.llenar_datos_correspondencia_enviada=function(results){

        self.correspondenciaEnviadaVO.id(results.id),
        self.correspondenciaEnviadaVO.consecutivo(results.consecutivo)
        self.correspondenciaEnviadaVO.fechaEnvio(results.fechaEnvio)
        self.correspondenciaEnviadaVO.anoEnvio(results.anoEnvio)
        self.correspondenciaEnviadaVO.departamento_id(results.ciudad.departamento.id)
            
        self.correspondenciaEnviadaVO.prefijo_id(results.prefijo.id)

        self.correspondenciaEnviadaVO.asunto(results.asunto)
        self.correspondenciaEnviadaVO.referencia(results.referencia)
        self.correspondenciaEnviadaVO.contenido(results.contenido)
        self.correspondenciaEnviadaVO.contenidoHtml(results.contenidoHtml)
            
        tinymce.activeEditor.setContent('')
        tinymce.activeEditor.execCommand('mceCleanup');
        tinymce.activeEditor.execCommand('mceInsertContent', false, results.contenidoHtml ) 

        self.correspondenciaEnviadaVO.firma_id(results.firma.id)

        self.correspondenciaEnviadaVO.privado('false') 
        if (results.privado==true){
          self.correspondenciaEnviadaVO.privado('true') 
        }          
            
        self.correspondenciaEnviadaVO.grupoSinin('0')
        if (results.grupoSinin==true){
          self.correspondenciaEnviadaVO.grupoSinin('1') 
        }

        setTimeout(function(){ 
          self.correspondenciaEnviadaVO.ciudad_id(results.ciudad.id)
          self.correspondenciaEnviadaVO.empresa_destino(results.empresa_destino)
          self.correspondenciaEnviadaVO.cargo_persona(results.cargo_persona)
          self.correspondenciaEnviadaVO.persona_destino(results.persona_destino)
          self.correspondenciaEnviadaVO.direccion(results.direccion)
          self.correspondenciaEnviadaVO.telefono(results.telefono)
         
          if(results.municipioEmpresa!=null){
            self.correspondenciaEnviadaVO.municipioEmpresa_id(results.municipioEmpresa.id)  
          }else{
            self.correspondenciaEnviadaVO.municipioEmpresa_id('') 
          }
            
        }, 2000);                 

     }
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }
    self.abrir_modal_busqueda = function () {
        self.titulo('Consulta de correspondencia');
        $('#modal_busqueda').modal('show');
    }
	  self.abrir_modal = function () {
        self.limpiar_correspondencia_enviada();
        self.titulo('Datos de la carta a enviar');
        self.titulo_btn('Generar Consecutivo');
     }

    self.abrir_modal_soporte_ver = function (obj) {
        self.titulo('Soportes del Consecutivo No. '+obj.consecutivo);
        self.consultar_soportes(obj.id)
        $('#modal_acciones_soporte_ver').modal('show');
    }
    //exportar excel    
    self.exportar_excel=function(){
        location.href= path_principal+"/correspondencia/reporte_correspondenciaEnviada?dato="+self.filtro();
    } 
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }
    //funcion consultar correspondencia enviadas que puede  ver la empresa
    self.consultar = function (pagina) {
        if (pagina > 0) {    
            fecha_inicio = self.correspondenciaEnviadaVO_filtro.fechaDesde();
            fecha_final =  self.correspondenciaEnviadaVO_filtro.fechaHasta();
            /*if (fecha_inicio!=null && fecha_inicio!='' && fecha_final!=null && fecha_final!='') { 
              var result= new Date(fecha_final) < new Date(fecha_inicio);
              if (result) {
                $('#valDesde').show();
                return false;
              };              
            }  */  
          
            if (fecha_inicio!=null && fecha_inicio!='' && fecha_final!=null && fecha_final!='') { 
              var result= new Date(fecha_final) < new Date(fecha_inicio);
              if (result) {
                $('#valHasta').show();
                return false;
              }else{
                $('#valHasta').hide();
              }   
            }    

            if (self.correspondenciaEnviadaVO_filtro.asunto()==false){
                self.correspondenciaEnviadaVO_filtro.asunto(0)
            }else{
                self.correspondenciaEnviadaVO_filtro.asunto(1)
            }
            if (self.correspondenciaEnviadaVO_filtro.referencia()==false){
                self.correspondenciaEnviadaVO_filtro.referencia(0)
            }else{
              self.correspondenciaEnviadaVO_filtro.referencia(1)
            }
            if (self.correspondenciaEnviadaVO_filtro.consecutivo()==false){
                self.correspondenciaEnviadaVO_filtro.consecutivo(0)
            }else{
                self.correspondenciaEnviadaVO_filtro.consecutivo(1)
            }
            if (self.correspondenciaEnviadaVO_filtro.destinatario()==false){
                self.correspondenciaEnviadaVO_filtro.destinatario(0)
            }else{
                self.correspondenciaEnviadaVO_filtro.destinatario(1)
            }

            if (self.correspondenciaEnviadaVO_filtro.soporte_si()==false){
                self.correspondenciaEnviadaVO_filtro.soporte_si(0)
            }else{
                self.correspondenciaEnviadaVO_filtro.soporte_si(1)
            }
            if (self.correspondenciaEnviadaVO_filtro.soporte_no()==false){
                self.correspondenciaEnviadaVO_filtro.soporte_no(0)
            }else{
                self.correspondenciaEnviadaVO_filtro.soporte_no(1)
            }

            self.filtro($('#txtBuscar').val());

            // PARAMETROS DE BUSQUEDA DE LA CORRESPONDENCIA
            sessionStorage.setItem("app_correspondencia_filtro", self.filtro() || '');
            sessionStorage.setItem("app_correspondencia_firma", self.correspondenciaEnviadaVO_filtro.firma() || '');      
            sessionStorage.setItem("app_correspondencia_usuarioElaboro", self.correspondenciaEnviadaVO_filtro.usuarioElaboro() || '');
            sessionStorage.setItem("app_correspondencia_soporte_si", self.correspondenciaEnviadaVO_filtro.soporte_si() || 1);
            sessionStorage.setItem("app_correspondencia_soporte_no", self.correspondenciaEnviadaVO_filtro.soporte_no() || 1);
            sessionStorage.setItem("app_correspondencia_asunto", self.correspondenciaEnviadaVO_filtro.asunto() || 1);
            sessionStorage.setItem("app_correspondencia_referencia", self.correspondenciaEnviadaVO_filtro.referencia() || 1);
            sessionStorage.setItem("app_correspondencia_consecutivo", self.correspondenciaEnviadaVO_filtro.consecutivo() || 1);
            sessionStorage.setItem("app_correspondencia_destinatario", self.correspondenciaEnviadaVO_filtro.destinatario() || 1);      
            sessionStorage.setItem("app_correspondencia_fechaDesde", self.correspondenciaEnviadaVO_filtro.fechaDesde() || '');
            sessionStorage.setItem("app_correspondencia_fechaHasta", self.correspondenciaEnviadaVO_filtro.fechaHasta() || '');

            path = self.url+'CorrespondenciaEnviada/';
            parameter = {  dato: self.filtro()
                          , page: pagina 
                          ,firma : self.correspondenciaEnviadaVO_filtro.firma()
                          ,usuarioElaboro : self.correspondenciaEnviadaVO_filtro.usuarioElaboro()
                          ,soporte_si : self.correspondenciaEnviadaVO_filtro.soporte_si()
                          ,soporte_no : self.correspondenciaEnviadaVO_filtro.soporte_no()
                          ,asunto : self.correspondenciaEnviadaVO_filtro.asunto()
                          ,referencia : self.correspondenciaEnviadaVO_filtro.referencia()
                          ,consecutivo : self.correspondenciaEnviadaVO_filtro.consecutivo()
                          ,destinatario : self.correspondenciaEnviadaVO_filtro.destinatario()
                          ,fechaDesde : self.correspondenciaEnviadaVO_filtro.fechaDesde()
                          ,fechaHasta : self.correspondenciaEnviadaVO_filtro.fechaHasta()
                          ,parametro_select : 1

                        };
            RequestGet(function (datos, estado, mensage) {

                self.listado_funcionarios_firma(datos.data.funcionarios);
                self.listado_funcionarios_elaboran(datos.data.usuarios);
                self.listado_macro_contrato_filtro(datos.data.mcontratos);
                if (estado == 'ok' && datos.data.correspondencias!=null && datos.data.correspondencias.length > 0) {
                    self.mensaje('');
                    self.listado_correspondencias(agregarOpcionesObservable(datos.data.correspondencias));  

                } else {
                    self.listado_correspondencias([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }

     self.consultar_por_id = function (correspondencia_id) {
       self.limpiar_correspondencia_enviada();
       path = self.url+'CorrespondenciaEnviada/'+correspondencia_id+'/?format=json';
        parameter = {};
         RequestGet(function (results,count) {
            self.titulo('Actualizar Correspondencia Consecutivo No. '+results.consecutivo);            
            $('#modal_acciones').modal('show');
            self.titulo_btn('Actualizar Consecutivo No. '+results.consecutivo);

            if(results.municipioEmpresa!=null){
              self.departamentoEmpresa_id(results.municipioEmpresa.departamento.id)
            }else{
              self.departamentoEmpresa_id('')
            }    
       
            self.llenar_datos_correspondencia_enviada(results);
         }, path, parameter);
     } 

    // //funcion guardar
     self.guardar=function(){
      if (CorrespondenciaEnviadaViewModel.errores_correspondencia().length == 0) {//se activa las validaciones*/
            self.correspondenciaEnviadaVO.destinatarioCopia([])
            if(self.listado_destinatarios_con_copia().length>0){
               ko.utils.arrayForEach(self.listado_destinatarios_con_copia(), function(d,index) {
                      self.correspondenciaEnviadaVO.destinatarioCopia.push(d.id)
                });
            }
            self.correspondenciaEnviadaVO.contenido(tinyMCE.activeEditor.getContent({ format: 'text' }))
            self.correspondenciaEnviadaVO.contenidoHtml(tinyMCE.activeEditor.getContent())
          
            if(self.correspondenciaEnviadaVO.id()==0){
                self.correspondenciaEnviadaVO.proyecto_id($("#proyecto_id").val());
                peticion = 'POST';
                url_api  = path_principal+'/api/CorrespondenciaEnviada/';
            }else{                 
                peticion = 'PUT';  
                url_api  = path_principal+'/api/CorrespondenciaEnviada/'+ self.correspondenciaEnviadaVO.id()+'/';
            }

            var parametros={     
                metodo: peticion,                
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        /* IF SI ES GUARDAR O SINO SE ACTUALIZA*/
                        if(self.correspondenciaEnviadaVO.id()==0){

                          if ($("#consecutivoHabilitado").val()=="False"){
                            self.descargar_carta(datos);  
                          }
                          
                          self.limpiar_correspondencia_enviada();
                        }
                    } 
                },//funcion para recibir la respuesta 
                url: url_api,
                parametros:self.correspondenciaEnviadaVO                        
            };
            Request(parametros);
        } else {
             CorrespondenciaEnviadaViewModel.errores_correspondencia.showAllMessages();
        }
     }

    //funcion consultar departamentos
    self.consultar_usuariosCopiado = function (correspondencia_id) {                
            path = self.url+'CorrespondenciaEnviadaDestinatario/';
            parameter = { copia : self.usuarioCopiado() , correspondencia : correspondencia_id  , ignorePagination : 1};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {

                    ko.utils.arrayForEach(datos, function(d,index) {
                      // alert(d.usuario.id)
                        self.arrayUsuario.push({"id":d.usuario.id , "nombres" : d.usuario.persona.nombres+' '+d.usuario.persona.apellidos})  
                        self.correspondenciaEnviadaVO.destinatarioCopia.push(d.usuario.id)
                    });

                    self.listado_destinatarios_con_copia(self.arrayUsuario());
                } else {
                    self.listado_destinatarios_con_copia([]);
                }            
            }, path, parameter);        
    }   
    //funcion consultar municipios
    self.consultar_municipiosEmpresa = function () {                
            path = self.url+'Municipio/';
            parameter = { ignorePagination : 1  , id_departamento : self.departamentoEmpresa_id() };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_municipiosEmpresa(datos);
                } else {
                    self.listado_municipiosEmpresa([]);
                }             
            }, path, parameter);        
    }
   
    //funcion consultar municipios
    self.consultar_municipios = function (departamento_id) {                
            path = self.url+'Municipio/';
            parameter = { ignorePagination : 1 , id_departamento :  departamento_id };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_municipios(datos);
                } else {
                    self.listado_municipios([]);
                }             
            }, path, parameter);        
    }

    self.filtro_empresaDestinatario.subscribe(function (val) {
        self.consultar_funcionarios();
    });

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
            path = path_principal+'/correspondencia/usuariosCorrespondencia/';
            parameter = { empresa : self.filtro_empresaDestinatario() , dato : filtro };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_funcionarios(datos);
                } else {
                    self.listado_funcionarios([]);
                }             
            }, path, parameter);        
    }

    self.filtro_empresaDestinatarioCopia.subscribe(function (val) {
        self.consultar_funcionarios_copia();
    });

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
    
// -------- ESTABLECER CARTA -----------// // -------- ESTABLECER CARTA -----------// // -------- ESTABLECER CARTA -----------//
    self.establecer = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_correspondencias(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                   lista_id.push(d.id)
                }
         });
         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione una carta para establecer.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path = path_principal+'/correspondencia/establish_correspondenciaEnviada/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar(" Esta seguro que desea establecer las cartas seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })
         }    
    }
// -------- ANULAR CARTA -----------// // -------- ANULAR CARTA -----------// // -------- ANULAR CARTA -----------//
    self.eliminar = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_correspondencias(), function(d) {
                if(d.eliminado()==true){
                  count=1;
                  lista_id.push(d.id)
                }
         });
         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione una carta para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path = path_principal+'/correspondencia/destroy_correspondenciaEnviada/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar(" Esta seguro que desea anular las cartas seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })
         }    
    }

    self.checkall.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado_correspondencias(), function(d) {
                if(d.usuarioSolicitante.id == $("#user").val()){
                    d.eliminado(value);
                }                  
            }); 
    });

// -------- ASOCIAR CONTRATO -----------// // -------- ASOCIAR CONTRATO -----------// // -------- ASOCIAR CONTRATO -----------//
  
    self.abrir_modal_asociarContrato = function (obj) {
        self.titulo('Asociar contratos al consecutivo  No. '+obj.consecutivo);
        $('#modal_acciones_contrato').modal('show');

        self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id(obj.id)
        /*self.consultar_contratos(obj.id)*/
        self.listado_contratos_tabla([]);  
        self.consultar_contratos_correspondenciaEnviada(obj.id)

        self.consultar_estados_contrato();
        self.mensajePorAsignar(mensajeInformativoBusuqeda)
    }

    self.mcontrato_id_filtroContrato.subscribe(function (val) {
        if(val!=undefined){
          self.consultar_contratos(self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id())
        }
        
    });

    self.estado_id_filtro.subscribe(function (val) {
        if(val!=undefined){
          self.consultar_contratos(self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id())
        }
        
    });

    /* ------- BLOQUE DE CONTRATOS ------- ------- BLOQUE DE CONTRATOS ------- ------- BLOQUE DE CONTRATOS ------- */
            // //funcion para guardar contratistas del proyecto 
        self.guardar_contratos_correspondencia=function(obj){ 
            self.correspondenciaEnviada_contratoVO.contrato_id([]);           
            ko.utils.arrayForEach(self.listado_contratos_tabla(),function(p){
                if (p.procesar()) {
                    self.correspondenciaEnviada_contratoVO.contrato_id.push(p.id);
                };
            });
       
            var parametros={                     
                 callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.filtro("");  
                        self.consultar_contratos(self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id());                      
                        self.consultar_contratos_correspondenciaEnviada(self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id());
                        self.checkallContratos(false);
                    }                     
                 },//funcion para recibir la respuesta 
                 url: path_principal+'/correspondencia/create_correspondenciaEnviada_contrato/',//url api
                 parametros: self.correspondenciaEnviada_contratoVO                         
            };
            //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData(parametros);            
         }
         self.eliminar_contratos_proyecto = function () {
                 self.correspondenciaEnviada_contratoVO.contrato_id([]);  
                 var count=0;
                 ko.utils.arrayForEach(self.listado_correspondencia_contratos(), function(d) {
                        if(d.eliminado()==true){
                           count=1;
                           self.correspondenciaEnviada_contratoVO.contrato_id.push(d.id);
                        }
                 });

                if(count==0){

                        $.confirm({
                            title:'Informativo',
                            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contrato para la eliminacion.<h4>',
                            cancelButton: 'Cerrar',
                            confirmButton: false
                        });
                }else{
                     var path = path_principal+'/correspondencia/destroy_correspondenciaEnviadaContrato/';
                     var parameter = self.correspondenciaEnviada_contratoVO
                     RequestAnularOEliminar("Esta seguro que desea denegar los contratos seleccionados?", path, parameter, function () {
                         self.consultar_contratos(self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id()); 
                         self.consultar_contratos_correspondenciaEnviada(self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id());
                         self.checkallCorrespondenciaContratos(false);
                     })
                 }          
            }

           //consultar los tipos de contrato
        self.consultar_tipos_contrato=function(){
             path = self.url+'Tipos/';
             parameter = { ignorePagination : 1 , aplicacion : self.app_contrato };
                RequestGet(function (datos, estado, mensage) {
                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                        self.listado_tipos_contrato(datos);
                    } else {
                        self.listado_tipos_contrato([]);
                    }             
                }, path, parameter); 
        }
        self.consultar_contratos_enter = function (d,e) {
            if (e.which == 13) {
                self.consultar_contratos(self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id())
            }
            return true;
        }

        self.consultar_contratos_btn = function (){
            self.consultar_contratos(self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id())
        }
         //funcion consultar contratos
        self.consultar_contratos = function (correspondencia_id) {

                self.filtro_contrato($('#txtBuscarContrato').val());        
                path = path_principal+'/correspondencia/list_contratosSinCorrespondenciaEnviada/';
                parameter = { dato : self.filtro_contrato() 
                              , correspondencia : correspondencia_id 
                              , estado : self.estado_id_filtro()
                              , mcontrato : self.mcontrato_id_filtroContrato() };
                RequestGet(function (datos, estado, mensage) {
                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                         self.mensajePorAsignar('')
                        self.listado_contratos_tabla(agregarOpcionesObservable(datos));                        
                    } else {
                        self.listado_contratos_tabla([]);   
                         self.mensajePorAsignar(mensajeNoFound)                    
                    }                
                }, path, parameter);        
        } 

        self.consultar_contratos_correspondenciaEnviada_enter = function (d,e) {
            if (e.which == 13) {
                self.consultar_contratos_correspondenciaEnviada(self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id())
            }
            return true;
        }
        self.consultar_contratos_correspondenciaEnviada_filtro  = function(){
            self.consultar_contratos_correspondenciaEnviada(self.correspondenciaEnviada_contratoVO.correspondenciaenviada_id())
        }
        //funcion consultar contratos asociados a las cartas
         self.consultar_contratos_correspondenciaEnviada = function (correspondencia_id) {
                self.filtro_contrato_correspondencia($('#txtBuscarContratoCorrespondenciaEnviada').val());                
                path = path_principal+'/correspondencia/list_correspondenciaEnviadaContrato/';
                parameter = { dato : self.filtro_contrato_correspondencia() , correspondencia_id : correspondencia_id  };
                RequestGet(function (results,count) {
                    if (results.length>0){
                        self.mensajeAsignados('')
                        self.listado_correspondencia_contratos(agregarOpcionesObservable(results));
                    }else{
                        self.listado_correspondencia_contratos([]);
                        self.mensajeAsignados(mensajeNoFound)
                    }
                   
                }, path, parameter);       
        }

        self.checkallContratos.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado_contratos_tabla(), function(d) {
                    d.procesar(value);
            }); 
        });
        self.checkallCorrespondenciaContratos.subscribe(function(value ){
                ko.utils.arrayForEach(self.listado_correspondencia_contratos(), function(d) {
                        d.eliminado(value);
                }); 
        }); 
    /* -------FINALIZA BLOQUE DE CONTRATOS ------- -------FINALIZA BLOQUE DE CONTRATOS ------- -------FINALIZA BLOQUE DE CONTRATOS ------- */


// -------- ASOCIAR PROYECTO -----------// // -------- ASOCIAR PROYECTO -----------// // -------- ASOCIAR PROYECTO -----------//

    self.abrir_modal_asociarProyecto = function (obj) {
        self.titulo('Asociar proyectos al consecutivo  No. '+obj.consecutivo);
        $('#modal_acciones_proyecto').modal('show');
        self.correspondenciaEnviada_proyectoVO.correspondenciaenviada_id(obj.id)
        /*self.consultar_proyectos(obj.id)*/
        self.consultar_proyectos_correspondenciaEnviada(obj.id)
        self.listado_proyectos_tabla([]);
        self.mensajePorAsignar(mensajeInformativoBusuqeda)
    }

    self.mcontrato_id_filtro.subscribe(function (val) {     
        if(val!=undefined){
          self.consultar_contratistas_filtro()
          self.consultar_proyectos(self.correspondenciaEnviada_proyectoVO.correspondenciaenviada_id())
        }else{
          self.listado_contratista_filtro([]);
        }
        
    });
    //funcion consultar los contratistas que tienen proyectos 
    self.consultar_contratistas_filtro = function () {              
            path = self.url_app_proyecto+'filtrar_proyectos/';
            parameter = { mcontrato : self.mcontrato_id_filtro() };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos.contratista!=null && datos.contratista.length > 0) {
                    self.listado_contratista_filtro(datos.contratista);
                } else {
                    self.listado_contratista_filtro([]);
                }          
            }, path, parameter);        
    }

    self.guardar_proyectos_correspondencia=function(obj){ 
            self.correspondenciaEnviada_proyectoVO.proyecto_id([]);           
            ko.utils.arrayForEach(self.listado_proyectos_tabla(),function(p){
                if (p.procesar()) {
                    self.correspondenciaEnviada_proyectoVO.proyecto_id.push(p.id);
                };
            });
       
            var parametros={                     
                 callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.filtro("");  
                        self.consultar_proyectos(self.correspondenciaEnviada_proyectoVO.correspondenciaenviada_id());                      
                        self.consultar_proyectos_correspondenciaEnviada(self.correspondenciaEnviada_proyectoVO.correspondenciaenviada_id());
                        self.checkallProyectos(false);
                    }                     
                 },//funcion para recibir la respuesta 
                 url: path_principal+'/correspondencia/create_correspondenciaEnviada_proyecto/',//url api
                 parametros: self.correspondenciaEnviada_proyectoVO                         
            };
            //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData(parametros);            
         }

     self.eliminar_proyectos_correspondencia = function () {
             self.correspondenciaEnviada_proyectoVO.proyecto_id([]);  
             var count=0;
             ko.utils.arrayForEach(self.listado_correspondencia_proyectos(), function(d) {
                    if(d.eliminado()==true){
                       count=1;
                       self.correspondenciaEnviada_proyectoVO.proyecto_id.push(d.id);
                    }
             });

            if(count==0){

                    $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contrato para la eliminacion.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });
            }else{
                 var path = path_principal+'/correspondencia/destroy_correspondenciaEnviadaProyecto/';
                 var parameter = self.correspondenciaEnviada_proyectoVO
                 RequestAnularOEliminar("Esta seguro que desea denegar los contratos seleccionados?", path, parameter, function () {
                     self.consultar_proyectos(self.correspondenciaEnviada_proyectoVO.correspondenciaenviada_id()); 
                     self.consultar_proyectos_correspondenciaEnviada(self.correspondenciaEnviada_proyectoVO.correspondenciaenviada_id());
                     self.checkallCorrespondenciaProyectos(false);
                 })
            }          
        }

    self.consultar_proyectos_btn = function (){
            self.consultar_proyectos(self.correspondenciaEnviada_proyectoVO.correspondenciaenviada_id())
    }

    self.consultar_proyectos_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_proyectos(self.correspondenciaEnviada_proyectoVO.correspondenciaenviada_id())
        }
        return true;
    }

    //funcion consultar contratos
    self.consultar_proyectos = function (correspondencia_id) {
            self.filtro_proyecto($('#txtBuscarProyecto').val());        
            path = path_principal+'/correspondencia/list_proyectosSinCorrespondenciaEnviada/';
            parameter = { dato : self.filtro_proyecto() , correspondencia : correspondencia_id , mcontrato : self.mcontrato_id_filtro() };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                     self.mensajePorAsignar('')
                    self.listado_proyectos_tabla(agregarOpcionesObservable(datos));                        
                } else {
                    self.listado_proyectos_tabla([]);   
                     self.mensajePorAsignar(mensajeNoFound)                    
                }                
            }, path, parameter);        
    } 

    self.consultar_proyectos_correspondenciaEnviada_btn = function (){
            self.consultar_proyectos_correspondenciaEnviada(self.correspondenciaEnviada_proyectoVO.correspondenciaenviada_id())
    }

    self.consultar_proyectos_correspondenciaEnviada_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_proyectos_correspondenciaEnviada(self.correspondenciaEnviada_proyectoVO.correspondenciaenviada_id())
        }
        return true;
    }

    //funcion consultar proyectos asociados a las cartas
     self.consultar_proyectos_correspondenciaEnviada = function (correspondencia_id) {
            self.filtro_proyecto_correspondencia($('#txtBuscarProyectoCorrespondenciaEnviada').val());                
            path = path_principal+'/correspondencia/list_correspondenciaEnviadaProyecto/';
            parameter = { dato : self.filtro_proyecto_correspondencia() , correspondencia_id : correspondencia_id  };
            RequestGet(function (results,count) {
                if (results.length>0){
                    self.mensajeAsignados('')
                    self.listado_correspondencia_proyectos(agregarOpcionesObservable(results));
                }else{
                    self.listado_correspondencia_proyectos([]);
                    self.mensajeAsignados(mensajeNoFound)
                }
               
            }, path, parameter);       
    }

    self.checkallProyectos.subscribe(function(value ){
        ko.utils.arrayForEach(self.listado_proyectos_tabla(), function(d) {
                d.procesar(value);
        }); 
    });
    self.checkallCorrespondenciaProyectos.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado_correspondencia_proyectos(), function(d) {
                    d.eliminado(value);
            }); 
    }); 

// -------- SUBIR SOPORTE -----------// // -------- SUBIR SOPORTE -----------// // -------- SUBIR SOPORTE -----------//

    self.abrir_modal_soporte = function (obj) {
        self.titulo('Administrar Soportes del Consecutivo No. '+obj.consecutivo);
        $('#modal_acciones_soporte').modal('show');

        self.correspondencia_soporteVO.correspondencia_id(obj.id)
        self.consultar_soportes(obj.id)
    }

    self.correspondencia_soporteVO.validaNombre.subscribe(function(value ){
          self.correspondencia_soporteVO.nombre('')
    });

    // //funcion subir archivo
     self.guardar_archivo=function(){
           
            if(self.correspondencia_soporteVO.id()==0){

                if( (self.correspondencia_soporteVO.validaNombre() == true && self.correspondencia_soporteVO.nombre()!='' ) || (self.correspondencia_soporteVO.validaNombre()==false) ){

                    var parametros={                     
                        callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                              self.limpiar_correspondencia_soporteVO();
                              self.consultar_soportes(self.correspondencia_soporteVO.correspondencia_id())
                              self.consultar(self.paginacion.pagina_actual());                              
                            }                     
                         },//funcion para recibir la respuesta 
                         url: self.url+'CorrespondenciaSoporte/',//url api
                         parametros:self.correspondencia_soporteVO                        
                    };
                    RequestFormData(parametros);

                }else{
                    mensajeInformativo('El nombre del archivo no puede estar vacio.','Soporte Correspondencia');
                }                
            }        
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
            }, path, parameter);        
    }
    self.eliminar_soportes = function () {
         self.correspondencia_soporteVO.soporte_id([]);  
         var count=0;
         ko.utils.arrayForEach(self.listado_correspondencia_soportes(), function(d) {
                if(d.eliminado()==true){
                   count=1;
                   self.correspondencia_soporteVO.soporte_id.push(d.id);
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
             var path = path_principal+'/correspondencia/destroy_correspondenciaSoporte/';
             var parameter = self.correspondencia_soporteVO
             RequestAnularOEliminar("Esta seguro que desea eliminar los soportes seleccionados?", path, parameter, function () {
                 self.consultar_soportes(self.correspondencia_soporteVO.correspondencia_id())
                 self.checkallSoportes(false);
                 self.consultar(self.paginacion.pagina_actual()); 
             })
         }          
    }

    self.checkallSoportes.subscribe(function(value ){
        ko.utils.arrayForEach(self.listado_correspondencia_soportes(), function(d) {
                d.eliminado(value);
        }); 
    });

// -------- DESCARGAR CARTA -------- // //
self.descargar_carta=function(obj){
        location.href=path_principal+'/correspondencia/'+"createWord?correspondencia_id="+obj.id;
  } 
// -------- COPIAR CARTA -----------// // -------- COPIAR CARTA -----------// // -------- COPIAR CARTA -----------//

    self.abrir_modal_copiarCarta = function (obj) {
        self.consultar_por_idCopia(obj);
        self.titulo_btn('Generar Consecutivo');
        setTimeout(function(){  
            /*self.consultar_DestinatarioCorrespondencia(self.correspondenciaEnviadaVO.id())*/
            self.correspondenciaEnviadaVO.id(0) 
          }, 2000);
        self.consultar_funcionarios()        
    }
    //funcion consultar destinatario de una carta  enviada
    self.consultar_DestinatarioCorrespondencia = function (correspondencia_id) {                
            path = self.url+'CorrespondenciaEnviadaDestinatario/';
            parameter = { ignorePagination : 1 , correspondencia : correspondencia_id , copia : self.usuarioRecibecarta() , usuarioSolicitante : 0 /*BOOLEAN  CERO ES EL NO SOLICITANTE*/};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.correspondenciaEnviadaVO.destinatario(datos[0].usuario.id)
                }            
            }, path, parameter);        
    }

    self.consultar_por_idCopia = function (id) {
        self.limpiar_correspondencia_enviada();
        path = self.url+'CorrespondenciaEnviada/'+id+'/?format=json';
        RequestGet(function (results,count) {
            self.titulo_btn('Generar Consecutivo');
            self.titulo('Copiar carta del consecutivo No. '+results.consecutivo);
            self.correspondenciaEnviadaVO.id(0),
            self.correspondenciaEnviadaVO.fechaEnvio(results.fechaEnvio)
            self.correspondenciaEnviadaVO.departamento_id(results.ciudad.departamento.id)
            
            self.correspondenciaEnviadaVO.prefijo_id(results.prefijo.id)

            self.correspondenciaEnviadaVO.asunto(results.asunto)
            self.correspondenciaEnviadaVO.referencia(results.referencia)
            self.correspondenciaEnviadaVO.contenido(results.contenido)
            self.correspondenciaEnviadaVO.contenidoHtml(results.contenidoHtml)
            
            tinymce.activeEditor.execCommand('mceInsertContent', false, results.contenidoHtml )

            self.correspondenciaEnviadaVO.firma_id(results.firma.id)

            self.correspondenciaEnviadaVO.privado('false')
            if(results.privado==true){
              self.correspondenciaEnviadaVO.privado('true')
            } 

            self.correspondenciaEnviadaVO.grupoSinin('0')
            if (results.grupoSinin==true){
              self.correspondenciaEnviadaVO.grupoSinin('1') 
            }                
            
            $('#modal_acciones').modal('show');
            setTimeout(function(){ self.correspondenciaEnviadaVO.ciudad_id(results.ciudad.id) }, 1000);
        }, path, parameter);
     } 
    //GENERAR CONSECUTIVOS // GENERAR CONSECUTIVOS //GENERAR CONSECUTIVOS // GENERAR CONSECUTIVOS
    self.correspondenciaEnviadaConsecutivoVO={
      id:ko.observable(0),
      numeroConsecutivo:ko.observable('').extend({ required: { message: '# de consecutivos.' } }),
      fechaEnvio:ko.observable('').extend({ required: { message: ' Digite la fecha.' } }),
      departamento_id:ko.observable('').extend({ required: { message: ' Seleccione el departamento.' } }),
      ciudad_id:ko.observable('').extend({ required: { message: ' Seleccione la ciudad.' } }),
      prefijo_id:ko.observable('').extend({ required: { message: ' Seleccione el prefijo.' } }),
     
      firma_id:ko.observable('').extend({ required: { message: ' Seleccione el funcionario a firmar.' } }), 
      privado:ko.observable('1').extend({ required: { message: ' Seleccione el permiso.' } }),

      municipioEmpresa_id:ko.observable(''),
      usuarioSolicitante_id:ko.observable($("#user").val()),
      empresa_id:ko.observable($("#company").val()),
    };

    self.correspondenciaEnviadaConsecutivoVO.departamento_id.subscribe(function (val) {
        if(val!=""){
            self.consultar_municipios(val)   
        }else{
            self.listado_municipios([]);
        }   
    });

      // //funcion guardar
     self.generar_consecutivos=function(){  
          
            if(self.correspondenciaEnviadaConsecutivoVO.id()==0 & CorrespondenciaEnviadaViewModel.errores_correspondencia_generar_consecutivo().length==0){

                if(self.correspondenciaEnviadaConsecutivoVO.numeroConsecutivo()>1){

                    var parametros={                     
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                          self.url_descarga(datos)
                        }                     
                    },//funcion para recibir la respuesta 
                      url: path_principal+'/correspondencia/generar_consecutivos/',//url api
                      parametros:self.correspondenciaEnviadaConsecutivoVO                        
                    };
                    //parameter =ko.toJSON(self.contratistaVO);
                    RequestFormData(parametros);

                }else{
                  mensajeInformativo('Solo se puede generar mas de un consecutivo');
                }
                
            }else{
              CorrespondenciaEnviadaViewModel.errores_correspondencia_generar_consecutivo.showAllMessages();//mostramos las validacion
            }        
     }

     self.descargar_consecutivos = function(){
        location.href= path_principal+"/correspondencia/export_consecutivos_excel?nombre="+self.url_descarga();
     }

     self.url_descarga=ko.observable('');

     self.ver_soporte = function(obj) {
      window.open(path_principal+"/correspondencia/ver-soporte/?id="+ obj.id, "_blank");
     }

//---------- FIN VIWMODEL --------////---------- FIN VIWMODEL --------////---------- FIN VIWMODEL --------////---------- FIN VIWMODEL --------//
}

var correspondencia = new CorrespondenciaEnviadaViewModel();

$('#txtBuscar').val(sessionStorage.getItem("app_correspondencia_filtro"));
correspondencia.correspondenciaEnviadaVO_filtro.firma(sessionStorage.getItem("app_correspondencia_firma"));      
correspondencia.correspondenciaEnviadaVO_filtro.usuarioElaboro(sessionStorage.getItem("app_correspondencia_usuarioElaboro"));
correspondencia.correspondenciaEnviadaVO_filtro.soporte_si(sessionStorage.getItem("app_correspondencia_soporte_si"));
correspondencia.correspondenciaEnviadaVO_filtro.soporte_no(sessionStorage.getItem("app_correspondencia_soporte_no"));
correspondencia.correspondenciaEnviadaVO_filtro.asunto(sessionStorage.getItem("app_correspondencia_asunto"));
correspondencia.correspondenciaEnviadaVO_filtro.referencia(sessionStorage.getItem("app_correspondencia_referencia"));
correspondencia.correspondenciaEnviadaVO_filtro.consecutivo(sessionStorage.getItem("app_correspondencia_consecutivo"));
correspondencia.correspondenciaEnviadaVO_filtro.destinatario(sessionStorage.getItem("app_correspondencia_destinatario"));
correspondencia.correspondenciaEnviadaVO_filtro.fechaDesde(sessionStorage.getItem("app_correspondencia_fechaDesde"));
correspondencia.correspondenciaEnviadaVO_filtro.fechaHasta(sessionStorage.getItem("app_correspondencia_fechaHasta"));

CorrespondenciaEnviadaViewModel.errores_correspondencia = ko.validation.group(correspondencia.correspondenciaEnviadaVO);
CorrespondenciaEnviadaViewModel.errores_correspondencia_generar_consecutivo = ko.validation.group(correspondencia.correspondenciaEnviadaConsecutivoVO);
ko.applyBindings(correspondencia);