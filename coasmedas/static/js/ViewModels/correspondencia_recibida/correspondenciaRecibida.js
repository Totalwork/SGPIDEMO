function CorrespondenciaRecibidaViewModel() {
  	/*ESTADOS DE LA CORRESPONDENCIA RECIBIDA*/
    var estado_por_revisar = 33;
    var estado_revisada = 34;
    var estado_respondida = 35;
    var estado_reasignada = 36;

    var self = this;
    self.filtro=ko.observable('');
    self.url=path_principal+'/api/'; 
  	self.mensaje=ko.observable('');
    self.mensajeAsignados=ko.observable('');
    self.mensajePorAsignar=ko.observable('');
    self.mensajePorAsignarSinin=ko.observable('');
    self.parametro_select = ko.observable(1);

    self.titulo=ko.observable('');
    self.app_correspondencia = 'correspondencia_recibida'
    self.app_parametrizacion = '/parametrizacion/'
    self.url_app_correspondencia = path_principal+'/correspondencia_recibida/';
    self.url_app_parametrizacion = path_principal+'/parametrizacion/';

    self.listado_funcionarios_elaboran = ko.observableArray([]);
    self.listado_historial_carta = ko.observableArray([]);

  	//LISTADOS   
  	self.listado_correspondencias = ko.observableArray([]);
    self.listado_destinatarios = ko.observableArray([]);
    self.listado_destinatarios_copia = ko.observableArray([]);
    self.listado_correspondencia_soportes = ko.observableArray([]);

    self.listado_correspondencia_soportes_sinin = ko.observableArray([]);

    self.listado_destinatarios_con_copia = ko.observableArray([]);

    self.listado_estados_correspondencia_recibida = ko.observableArray([]);

    self.newArray = ko.observableArray([]);
	 
    self.usuarioRecibecarta=ko.observable(0);
    self.usuarioAsignarCarta = ko.observable(0);

    self.validaSoporteGrupo = ko.observable(0);/*valida si la carta recibida fue por el grupo sinin*/
  

    self.checkall = ko.observable(false);
    self.checkallSoportes = ko.observable(false);

    //Representa un modelo de la tabla correspoondenciaRecibida
    self.correspondenciaRecibidaVO={
      id:ko.observable(0),
      radicado:ko.observable(null),
      fechaRecibida:ko.observable('').extend({ required: { message: ' Digite la fecha en la que se recibe la correspondencia . ' } }),
      anoRecibida:ko.observable(''),
      remitente:ko.observable('').extend({ required: { message: ' Digite el remitente de la correspondencia.' } }),        
      asunto:ko.observable('').extend({ required: { message: ' Digite el asunto de la correspondencia.' } }),
      fechaRegistro:ko.observable(''),

      privado:ko.observable('false'),
      radicadoPrevio:ko.observable(''),
    
      destinatario:ko.observable(0).extend({ required: { message: ' Seleccione el destinatario.' } }),
      destinatarioCopia:ko.observableArray([]),

      usuarioSolicitante_id:ko.observable($("#user").val()),
      empresa_id:ko.observable($("#company").val()),

      fechaRespuesta:ko.observable(''),
      soporte: ko.observable(''),
    };  
  //INFORMACION DE LOS RADICADOS
   self.correspondencia_recibida_asignadaVO = {
        id: ko.observable(0),
        correspondenciaRecibida_id: ko.observableArray([]),
        usuario_id: ko.observable('').extend({ required: { message: ' Seleccione el usuario para asignar la carta.' } }),
        fechaAsignacion: ko.observable(''), // CARTA RECIBIDA 
        estado_id : ko.observable(0),
        respuesta_id : ko.observable(0),
        copia: ko.observable(0),/* SE USA ESTA LISTA PARA ELIMINAR VARIOS SOPORTES A LA VES*/   
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

    self.correspondenciaRecibidaVO_filtro={
      estado:ko.observable(''),
      usuarioElaboro:ko.observable(''),
      asunto:ko.observable(1),
      radicado:ko.observable(1),
      remitente:ko.observable(1),
      fechaDesde:ko.observable('')/*.extend({ validation: { validator: validar_fecha_inicio, message: '(*) La fecha desde no puede ser mayor que la fecha hasta.' } })*/,
      fechaHasta:ko.observable('')/*.extend({ validation: { validator: validar_fecha_final, message: '(*) La fecha hasta no puede ser menor que la fecha desde.' } })*/,
      mis_correspondencias:ko.observable(0),
      soporte_si:ko.observable(1),
      soporte_no:ko.observable(1),
      radicado_previo:ko.observable(''),
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

    self.fecha_inicio=ko.observable(self.correspondenciaRecibidaVO_filtro.fechaHasta());
    self.fecha_final=ko.observable(self.correspondenciaRecibidaVO_filtro.fechaDesde());

    function validar_fecha_inicio(fecha_inicio){
      var fecha_final=self.fecha_final();///$('#fecha_final').val();
      if (fecha_inicio!=null && fecha_inicio!='' && fecha_final!=null && fecha_final!='') { 
        return  new Date(fecha_final) >= new Date(fecha_inicio);
      }else{
        return true;
      }      
    }

    function validar_fecha_final(fecha_final){
      
      var fecha_inicio = self.fecha_inicio();//$('#fecha_inicio').val();
      if (fecha_inicio!=null && fecha_inicio!='' && fecha_final!=null && fecha_final!='') { 
        return  new Date(fecha_final) >= new Date(fecha_inicio);
      }else{
        return true;
      }      
    }

    self.asignar_copia_radicado = function(){

        id = $('#destinatarioCopia option:selected').val();
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

    self.quitar_copia_radicado = function(){

        id = $('#destinatarioConCopia option:selected').val();
        text = $('#destinatarioConCopia option:selected').text();
         
        if(id!=null){
          self.newArray([]);
          ko.utils.arrayForEach(self.listado_destinatarios_con_copia(), function(d,index) {
                  
                  if(d.id==id){
                    /*self.listado_destinatarios_con_copia().splice(index, 1);*/
                    self.listado_destinatarios_con_copia.remove(d);
                  }else{
                    self.newArray.push({"id":d.id , "nombres" : d.nombres})
                  }                
          });
          self.listado_destinatarios_con_copia([]);
          self.listado_destinatarios_con_copia(self.newArray());
          console.log(self.listado_destinatarios_con_copia().length);
        }        
    }

    // //limpiar el modelo 
    self.limpiar_correspondencia_recibida=function(){      
        self.correspondenciaRecibidaVO.id(0);
        self.correspondenciaRecibidaVO.radicado(null);
        self.correspondenciaRecibidaVO.fechaRecibida('');
        self.correspondenciaRecibidaVO.remitente('');
        self.correspondenciaRecibidaVO.asunto('');
        self.correspondenciaRecibidaVO.fechaRegistro('');
        self.correspondenciaRecibidaVO.privado('false');
        self.correspondenciaRecibidaVO.radicadoPrevio('');
        self.correspondenciaRecibidaVO.destinatario(0);
        self.correspondenciaRecibidaVO.destinatarioCopia([]);
        self.correspondenciaRecibidaVO.fechaRecibida.isModified(false);
        self.correspondenciaRecibidaVO.remitente.isModified(false);
        self.correspondenciaRecibidaVO.asunto.isModified(false);
        self.correspondenciaRecibidaVO.destinatario.isModified(false);
    }
    self.llenar_correspondencia_recibida=function(results){
        self.correspondenciaRecibidaVO.id(results.id);
        self.correspondenciaRecibidaVO.radicado(results.radicado);
        self.correspondenciaRecibidaVO.fechaRecibida(results.fechaRecibida);
        self.correspondenciaRecibidaVO.anoRecibida(results.anoRecibida);
        self.correspondenciaRecibidaVO.remitente(results.remitente);
        self.correspondenciaRecibidaVO.asunto(results.asunto);
        self.correspondenciaRecibidaVO.destinatario(results.asignacion.usuario_id);
        self.correspondenciaRecibidaVO.privado('false')
        if(results.privado==true){
          self.correspondenciaRecibidaVO.privado('true')
        }    
        self.correspondenciaRecibidaVO.radicadoPrevio(results.radicadoPrevio); 
        self.correspondenciaRecibidaVO.fechaRespuesta(results.fechaRespuesta); 
    }
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }

    self.abrir_modal_busqueda = function () {
        self.titulo('Consulta de correspondencia recibida');
        $('#modal_busqueda').modal('show');
    }

	  self.abrir_modal = function () {
        self.limpiar_correspondencia_recibida();
        self.titulo('Radicar Correspondencia');
        $('#modal_acciones').modal('show');
        self.listado_destinatarios_con_copia([]);
        self.consultar_destinatarios();
        self.consultar_destinatarios_copia();
        $('input[name="soportes[]"]').fileinput('reset');
        $('input[name="soportes[]"]').val('');
    }
    
    // //funcion guardar
     self.guardar=function(){

      // alert(CorrespondenciaRecibidaViewModel.errores_correspondencia().length)
      if (CorrespondenciaRecibidaViewModel.errores_correspondencia().length == 0) {//se activa las validaciones*/

            self.correspondenciaRecibidaVO.destinatarioCopia([])

          
            if(self.correspondenciaRecibidaVO.id()==0){

                var formData= new FormData();

                if(self.listado_destinatarios_con_copia().length>0){
                   ko.utils.arrayForEach(self.listado_destinatarios_con_copia(), function(d,index) {
                        formData.append('destinatarioCopia[]', d.id );
                    });
                }

                (self.correspondenciaRecibidaVO.privado()==true)?self.correspondenciaRecibidaVO.privado(1):self.correspondenciaRecibidaVO.privado(0);
                formData.append('privado', parseInt(self.correspondenciaRecibidaVO.privado()) );
                formData.append('fechaRecibida', self.correspondenciaRecibidaVO.fechaRecibida() );
                formData.append('remitente', self.correspondenciaRecibidaVO.remitente() );
                formData.append('asunto', self.correspondenciaRecibidaVO.asunto() );
                formData.append('radicadoPrevio', self.correspondenciaRecibidaVO.radicadoPrevio() );
                formData.append('usuarioSolicitante_id', parseInt(self.correspondenciaRecibidaVO.usuarioSolicitante_id()) );
                formData.append('empresa_id', parseInt(self.correspondenciaRecibidaVO.empresa_id()) );
                formData.append('destinatario', parseInt(self.correspondenciaRecibidaVO.destinatario()) );

                var files=$('input[name="soportes[]"]')[0].files;
                for (var i = 0; i < files.length ; i++) {      
                    formData.append('soporte[]', files[i]);                     
                }

                var parametros={                     
                  callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.filtro("");
                        self.consultar(self.paginacion.pagina_actual());
                        $('#modal_acciones').modal('hide');
                        self.limpiar_correspondencia_recibida();
                    }                     
                  },//funcion para recibir la respuesta 
                  url: path_principal+'/api/CorrespondenciaRecibida/',//url api
                  parametros: formData                        
                };

                RequestFormData2(parametros); 
            }else{       
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                              self.filtro("");
                              self.consultar(self.paginacion.pagina_actual());
                              $('#modal_acciones').modal('hide');
                              self.limpiar_correspondencia_recibida();
                            } 
                       },//funcion para recibir la respuesta 
                       url: path_principal+'/api/CorrespondenciaRecibida/'+ self.correspondenciaRecibidaVO.id()+'/',
                       parametros:self.correspondenciaRecibidaVO                        
                  };
                  Request(parametros);
            }
        } else {
             CorrespondenciaRecibidaViewModel.errores_correspondencia.showAllMessages();
        }
     }
    //FUNCION PARA INABIHILITAR LA CUENTA
    self.eliminar = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un banco para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
         }else{
             var path =path_principal+'/empresa/eliminar_id/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los bancos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })
         }    
    }

    self.modificar_carta = function (obj) {
        self.consultar_por_id(obj);
        $('#modal_acciones').modal('show');        
    }

    self.consultar_por_id = function (obj) {
       self.limpiar_correspondencia_recibida();
       path = self.url+'CorrespondenciaRecibida/'+obj.correspondenciaRecibida.id+'/';
       parameter = {  };
         RequestGet(function (results,count) {            
            self.titulo('Actualizar Correspondencia Radicado No. '+obj.correspondenciaRecibida.radicado);             
            self.llenar_correspondencia_recibida(results)
         }, path, parameter);
     } 

    //exportar excel       
    self.exportar_excel=function(){
        location.href=self.url_app_correspondencia+"reporte_correspondenciaRecibida?dato="+self.filtro()+"&usuarioElaboro="+self.correspondenciaRecibidaVO_filtro.usuarioElaboro()+"&soporte_no="+self.correspondenciaRecibidaVO_filtro.soporte_no()+"&soporte_si="+self.correspondenciaRecibidaVO_filtro.soporte_si()+"&remitente="+self.correspondenciaRecibidaVO_filtro.remitente()+"&radicado="+self.correspondenciaRecibidaVO_filtro.radicado()+"&asunto="+self.correspondenciaRecibidaVO_filtro.asunto()+"&fechaDesde"+self.correspondenciaRecibidaVO_filtro.fechaDesde()+"&fechaHasta="+self.correspondenciaRecibidaVO_filtro.fechaHasta();
    } 

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }
    //funcion consultar correspondencia 
    self.consultar = function (pagina) {

        fecha_inicio = self.correspondenciaRecibidaVO_filtro.fechaDesde();
        fecha_final =  self.correspondenciaRecibidaVO_filtro.fechaHasta();
       
        if (fecha_inicio!=null && fecha_inicio!='' && fecha_final!=null && fecha_final!='') { 
          var result= new Date(fecha_final) < new Date(fecha_inicio);
          if (result) {
            $('#valHasta').show();
            return false;
          }else{
            $('#valHasta').hide();
          }
        }    

        if (self.correspondenciaRecibidaVO_filtro.asunto()==false){
            self.correspondenciaRecibidaVO_filtro.asunto(0)
        }else{
            self.correspondenciaRecibidaVO_filtro.asunto(1)
        }
        if (self.correspondenciaRecibidaVO_filtro.remitente()==false){
            self.correspondenciaRecibidaVO_filtro.remitente(0)
        }else{
          self.correspondenciaRecibidaVO_filtro.remitente(1)
        }
        if (self.correspondenciaRecibidaVO_filtro.radicado()==false){
            self.correspondenciaRecibidaVO_filtro.radicado(0)
        }else{
            self.correspondenciaRecibidaVO_filtro.radicado(1)
        }

        if (self.correspondenciaRecibidaVO_filtro.soporte_si()==false){
            self.correspondenciaRecibidaVO_filtro.soporte_si(0)
        }else{
            self.correspondenciaRecibidaVO_filtro.soporte_si(1)
        }
        if (self.correspondenciaRecibidaVO_filtro.soporte_no()==false){
            self.correspondenciaRecibidaVO_filtro.soporte_no(0)
        }else{
            self.correspondenciaRecibidaVO_filtro.soporte_no(1)
        }
        

        if (CorrespondenciaRecibidaViewModel.errores_correspondencia_filtro().length == 0) {
          if (pagina > 0) {            
              self.filtro($('#txtBuscar').val());

              // PARAMETROS DE BUSQUEDA DE LA CORRESPONDENCIA
              sessionStorage.setItem("app_correspondenciaRecibida_filtro", self.filtro() || '');
              sessionStorage.setItem("app_correspondenciaRecibida_usuarioElaboro", self.correspondenciaRecibidaVO_filtro.usuarioElaboro() || '');
              sessionStorage.setItem("app_correspondenciaRecibida_soporte_si", self.correspondenciaRecibidaVO_filtro.soporte_si() || 1);
              sessionStorage.setItem("app_correspondenciaRecibida_soporte_no", self.correspondenciaRecibidaVO_filtro.soporte_no() || 1);
              sessionStorage.setItem("app_correspondenciaRecibida_remitente", self.correspondenciaRecibidaVO_filtro.remitente() || 1);
              sessionStorage.setItem("app_correspondenciaRecibida_radicado", self.correspondenciaRecibidaVO_filtro.radicado() || 1);
              sessionStorage.setItem("app_correspondenciaRecibida_asunto", self.correspondenciaRecibidaVO_filtro.asunto() || 1);  
              sessionStorage.setItem("app_correspondenciaRecibida_fechaDesde", self.correspondenciaRecibidaVO_filtro.fechaDesde() || '');
              sessionStorage.setItem("app_correspondenciaRecibida_fechaHasta", self.correspondenciaRecibidaVO_filtro.fechaHasta() || '');
              sessionStorage.setItem("app_correspondenciaRecibida_radicado_previo", self.correspondenciaRecibidaVO_filtro.radicado_previo() || ''); 

              path = self.url+'CorrespondenciaRecibidaAsignada/?format=json&page='+pagina;
              parameter = { dato: self.filtro(), pagina: pagina  
                            ,estado : self.correspondenciaRecibidaVO_filtro.estado()
                            ,usuarioElaboro : self.correspondenciaRecibidaVO_filtro.usuarioElaboro()
                            ,soporte_si : self.correspondenciaRecibidaVO_filtro.soporte_si()
                            ,soporte_no : self.correspondenciaRecibidaVO_filtro.soporte_no()
                            ,remitente : self.correspondenciaRecibidaVO_filtro.remitente()
                            ,radicado : self.correspondenciaRecibidaVO_filtro.radicado()
                            ,asunto : self.correspondenciaRecibidaVO_filtro.asunto()
                            ,fechaDesde : self.correspondenciaRecibidaVO_filtro.fechaDesde()
                            ,fechaHasta : self.correspondenciaRecibidaVO_filtro.fechaHasta()
                            ,mis_correspondencias : self.correspondenciaRecibidaVO_filtro.mis_correspondencias()
                            ,parametro_select : self.parametro_select()
                            ,radicado_previo : self.correspondenciaRecibidaVO_filtro.radicado_previo()
                           };
              RequestGet(function (datos, estado, mensage) {

                  self.listado_funcionarios_elaboran(datos.data.usuarios);
                  self.listado_estados_correspondencia_recibida(datos.data.estados);

                  if (estado == 'ok' && datos.data.correspondencias_asignadas!=null && datos.data.correspondencias_asignadas.length > 0) {
                      self.mensaje('');
                      self.listado_correspondencias(agregarOpcionesObservable(datos.data.correspondencias_asignadas));  
                  } else {
                      self.listado_correspondencias([]);
                      self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                  }

                self.llenar_paginacion(datos,pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
          }
        }else{
          CorrespondenciaRecibidaViewModel.errores_correspondencia_filtro.showAllMessages();
        }
    }  

    //funcion consultar destinatario de una carta  enviada
    self.consultar_DestinatarioCorrespondencia = function (correspondencia_id) {                
            path = self.url+'CorrespondenciaRecibidaAsignada/';
            parameter = { ignorePagination : 1 , correspondencia : correspondencia_id , copia : self.usuarioRecibecarta() };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    /*self.correspondenciaEnviadaVO.destinatario(datos[0].usuario.id)*/
                }            
            }, path, parameter);        
    }

    self.consultar_destinatarios_enter = function (d,e) {
      if (e.which == 13) {
         self.consultar_destinatarios();
      }
      return true;
    }
    self.consultar_destinatarios_btn = function (d,e) {
         self.consultar_destinatarios();
    }

    //funcion consultar funcionarios para agregar el destinatario
    self.consultar_destinatarios = function () {
            var filtro = $("#filtro_Destinatario").val();  
            path = path_principal+self.app_parametrizacion+'usuarios_conFuncionariosEmpresa/';
            parameter = { empresa : 1 , dato : filtro };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_destinatarios(datos);
                } else {
                    self.listado_destinatarios([]);
                }          
            }, path, parameter);        
    }

    self.consultar_destinatarios_copia_enter = function (d,e) {
      if (e.which == 13) {
         self.consultar_destinatarios_copia();
      }
      return true;
    }
    self.consultar_destinatarios_copia_btn = function (d,e) {
         self.consultar_destinatarios_copia();
    }

    //funcion consultar funcionarios para agregar el destinatario copia
    self.consultar_destinatarios_copia = function () {
            var filtro = $("#filtro_DestinatarioCopia").val();    
            path = path_principal+self.app_parametrizacion+'usuarios_conFuncionariosEmpresa/';
            parameter = { empresa : 1 , dato : filtro };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_destinatarios_copia(datos);
                } else {
                    self.listado_destinatarios_copia([]);
                }          
            }, path, parameter);        
    }

   // FUNCION PARA FILTRAR --- // FUNCION PARA FILTRAR --- // FUNCION PARA FILTRAR --- // FUNCION PARA FILTRAR --- 
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

// -------- ESTABLECER CARTA -----------// // -------- ESTABLECER CARTA -----------// // -------- ESTABLECER CARTA -----------//
    self.establecer = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_correspondencias(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                   lista_id.push(d.correspondenciaRecibida.id)
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
             var path =self.url_app_correspondencia+'establish_correspondenciaRecibida/';
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
                   lista_id.push(d.correspondenciaRecibida.id)
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
             var path =self.url_app_correspondencia+'destroy_correspondenciaRecibida/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar(" Esta seguro que desea anular las cartas seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })
         }   
    }

    self.checkall.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado_correspondencias(), function(d) {
                  if( (d.correspondenciaRecibida.usuarioSolicitante.id == $("#user").val()) || (d.destinatario == $("#user").val()) ){
                      d.eliminado(value);
                  }  
            }); 
    });

// -------- SUBIR SOPORTE -----------// // -------- SUBIR SOPORTE -----------// // -------- SUBIR SOPORTE -----------//
    self.abrir_modal_soporte = function (obj) {
        self.titulo('Administrar Soportes del Radicado No. '+obj.correspondenciaRecibida.radicado);
        

        self.correspondencia_soporteVO.correspondencia_id(obj.correspondenciaRecibida.id)
        self.consultar_soportes(obj.correspondenciaRecibida.id)

        if(obj.correspondenciaRecibida.correspondenciaEnviada!=null){
          self.validaSoporteGrupo(1);  
          self.consultar_soportes_eviados_por_sinin(obj.correspondenciaRecibida.correspondenciaEnviada.id)
        }else{
          self.validaSoporteGrupo(0);
        }
        $('#modal_acciones_soporte').modal('show');        
    }

    self.correspondencia_soporteVO.validaNombre.subscribe(function(value ){
          self.correspondencia_soporteVO.nombre('')
    });

    self.abrir_modal_soporte_ver = function (obj) {
        self.titulo('Soportes del Radicado No. '+obj.correspondenciaRecibida.radicado);
        self.consultar_soportes(obj.correspondenciaRecibida.id)
        $('#modal_acciones_soporte_ver').modal('show');
    }
    // //funcion subir archivo
     self.guardar_archivo=function(){
           
            if(self.correspondencia_soporteVO.id()==0){

                if( (self.correspondencia_soporteVO.validaNombre() == true && self.correspondencia_soporteVO.nombre()!='' ) || (self.correspondencia_soporteVO.validaNombre()==false) ){

                    var parametros={                     
                        callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                              self.consultar_soportes(self.correspondencia_soporteVO.correspondencia_id())
                              self.consultar(self.paginacion.pagina_actual());
                              self.limpiar_correspondencia_soporteVO();
                            }                     
                         },//funcion para recibir la respuesta 
                         url: self.url+'CorrespondenciaRecibidaSoporte/',//url api
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
                  
            path = self.url+'CorrespondenciaRecibidaSoporte/';
            parameter = {  ignorePagination : 1 , correspondencia : correspondencia_id , anulado : 0 };
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

    //funcion consultar soportes
    self.consultar_soportes_eviados_por_sinin = function (correspondencia_id) {
                  
            path = self.url+'CorrespondenciaSoporte/';
            parameter = {  ignorePagination : 1 , correspondencia : correspondencia_id , anulado : 0 };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                     self.mensajePorAsignarSinin('')
                    self.listado_correspondencia_soportes_sinin(agregarOpcionesObservable(datos));                        
                } else {
                    self.listado_correspondencia_soportes_sinin([]);   
                    self.mensajePorAsignarSinin(mensajeNoFound)                    
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
             var path = path_principal+'/correspondencia_recibida/'+'destroy-correspondenciaRecibidaSoporte/';
             var parameter = self.correspondencia_soporteVO
             RequestAnularOEliminar("Esta seguro que desea eliminar los soportes seleccionados?", path, parameter, function () {
                 self.consultar_soportes(self.correspondencia_soporteVO.correspondencia_id())
                 self.consultar(self.paginacion.pagina_actual());
                 self.checkallSoportes(false);
             })
         }          
    }

    self.checkallSoportes.subscribe(function(value ){
        ko.utils.arrayForEach(self.listado_correspondencia_soportes(), function(d) {
                d.eliminado(value);
        }); 
    });


// -- HISTORIAL DE LA CARTA -- // // -- HISTORIAL DE LA CARTA -- // // -- HISTORIAL DE LA CARTA -- //
  self.abrir_modal_historial = function (obj) {
        $('#modal_acciones_historial').modal('show');
        self.consultar_historial(obj.correspondenciaRecibida.id)
        self.consultar_por_id_historial(obj)
       
  }

  self.consultar_por_id_historial = function (obj) {
       self.limpiar_correspondencia_recibida();
       path = self.url+'CorrespondenciaRecibida/'+obj.correspondenciaRecibida.id+'/';
       parameter = {  };
         RequestGet(function (results,count) {
            
            self.titulo('Historial del radicado No. '+obj.correspondenciaRecibida.radicado);             
            self.correspondenciaRecibidaVO.id(results.id);
            self.correspondenciaRecibidaVO.radicado(results.radicado);
            self.correspondenciaRecibidaVO.fechaRecibida(results.fechaRecibida);
            self.correspondenciaRecibidaVO.anoRecibida(results.anoRecibida);
            self.correspondenciaRecibidaVO.remitente(results.remitente);
            self.correspondenciaRecibidaVO.asunto(results.asunto);

            self.correspondenciaRecibidaVO.destinatario(results.destinatario);

            self.correspondenciaRecibidaVO.privado('false')
            if(results.privado==true){
              self.correspondenciaRecibidaVO.privado('true')
            }    

            self.correspondenciaRecibidaVO.radicadoPrevio(results.radicadoPrevio);         
            
         }, path, parameter);
  } 

  self.consultar_historial = function (correspondenciaId) {                
            path = self.url+'CorrespondenciaRecibidaAsignada/';
            parameter = { ignorePagination : 1 , correspondencia : correspondenciaId , copia : 0};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensajeAsignados('')
                    self.listado_historial_carta(datos);
                } else {
                    self.listado_historial_carta([]);
                    self.mensajeAsignados(mensajeNoFound)
                }             
            }, path, parameter);        
    }

// -- CODIGO DE BARRA -- // // -- CODIGO DE BARRA -- // // -- CODIGO DE BARRA -- //
  self.dowloadCodeBar = function (obj) {
        location.href=self.url_app_correspondencia+"createBarCodes?correspondencia="+obj.correspondenciaRecibida.id;
  }

  // --- MIS CORRESONDENCIAS --- // --- MIS CORRESPONDENCIAS // --- MIS CORRESPONDENCIAS // --- MIS CORRESPONDENCIAS
  //funcion consultar correspondencia 
    self.consultar_mis_correspondencias = function (pagina) {
      self.correspondenciaRecibidaVO_filtro.mis_correspondencias(1);
      self.consultar(pagina)
    }


  // --- RESPONDER RADICADO --- // --- RESPONDER RADICADO --- //
  //Representa un modelo de la tabla correspondenciaEnviada
    self.listado_departamentos = ko.observableArray([]);
    self.listado_municipios = ko.observableArray([]);
    self.listado_prefijos = ko.observableArray([]);
    self.listado_funcionarios = ko.observableArray([]);
    self.listado_funcionarios_firma = ko.observableArray([]);
    self.listado_funcionarios_copia = ko.observableArray([]);
    self.listado_empresas = ko.observableArray([]);
    self.departamentoEmpresa_id =ko.observable('');


    self.filtro_empresaDestinatario = ko.observable('');
    self.filtro_empresaDestinatarioCopia = ko.observable('');

    self.filtro_Destinatario = ko.observable('');
    self.filtro_DestinatarioCopia = ko.observable('');

    self.listado_departamentosEmpresa = ko.observableArray([]);
    self.listado_municipiosEmpresa = ko.observableArray([]);

    self.correspondenciaEnviadaVO={
      id:ko.observable(0),
      consecutivo:ko.observable(0),
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
      correspondencia_respuesta_id:ko.observable(''),
      municipioEmpresa_id:ko.observable('').extend({ required: { message: ' Seleccione la ciudad del destinatario.' } }),
      usuarioSolicitante_id:ko.observable($("#user").val()),
      empresa_id:ko.observable($("#company").val()),
    };
  self.abrir_modal_respuesta_radicado = function (obj) {
    self.titulo('Responder radicado No. '+obj.correspondenciaRecibida.radicado); 
    $('#modal_acciones').modal('show');  
    self.correspondenciaEnviadaVO.correspondencia_respuesta_id(obj.correspondenciaRecibida.id);  
    self.listado_destinatarios_con_copia([]);  


    /* CONSULTA DE LOS SELECT DE LA CORRESPONDENCIA QUE SE VA ENVIAR*/
      self.consultar_destinatarios();
      self.consultar_funcionarios();
      self.consultar_funcionarios_firma();
      self.consultar_funcionarios_copia();
      self.consultar_empresas();
      self.consultar_departamentos();
      self.consultar_municipios();
      self.consultar_prefijos();
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
            path = self.url_app_parametrizacion+'usuariosConFuncionarios/';
            parameter = { empresa : self.filtro_empresaDestinatarioCopia() , dato : filtro };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_funcionarios_copia(datos);
                } else {
                    self.listado_funcionarios_copia([]);
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
    //funcion consultar departamentos
    self.consultar_departamentos = function () {                
            path = self.url+'departamento/';
            parameter = { ignorePagination : 1 };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_departamentos(datos);
                    self.listado_departamentosEmpresa(datos);
                } else {
                    self.listado_departamentos([]);
                    self.listado_departamentosEmpresa([]);
                }            
            }, path, parameter);        
    }
    //funcion consultar municipios
    self.consultar_municipios = function () {                
            path = self.url+'Municipio/';
            parameter = { ignorePagination : 1 , id_departamento :  self.correspondenciaEnviadaVO.departamento_id() };
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

    self.filtro_empresaDestinatarioCopia.subscribe(function (val) {
        self.consultar_funcionarios_copia();
    });

    //funcion consultar funcionarios a firmar carta
    self.consultar_funcionarios_firma = function () {                
            path = self.url+'Funcionario/';
            parameter = { ignorePagination : 1 };
            RequestGet(function (datos, estado, mensage) {                           
                if (estado == 'ok' && datos!=null) {                    
                    self.listado_funcionarios_firma(datos);
                } else {
                    self.listado_funcionarios_firma([]);
                }             
            }, path, parameter);        
    }
    //funcion consultar funcionarios a firmar carta
    self.consultar_prefijos = function () {                
            path = self.url+'CorrespondenciaPrefijo/';
            parameter = { ignorePagination : 1 , empresa : self.correspondenciaEnviadaVO.empresa_id()};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_prefijos(datos);
                } else {
                    self.listado_prefijos([]);
                }             
            }, path, parameter);        
    }
    //funcion consultar empresas
    self.consultar_empresas = function () {                
            path = self.url+'empresa/';
            parameter = { ignorePagination : 1 };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.listado_empresas(datos.data);
                } else {
                    self.listado_empresas([]);
                }             
            }, path, parameter);        
    }

    self.asignar_copia = function(){
        id = $('#destinatarioCopia option:selected').val();
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
        id = $('#destinatarioConCopia option:selected').val();
        text = $('#destinatarioConCopia option:selected').text();

        if(id!=null){
          self.newArray([]);
          ko.utils.arrayForEach(self.listado_destinatarios_con_copia(), function(d,index) {                  
                  if(d.id==id){
                    /*self.listado_destinatarios_con_copia().splice(index, 1);*/
                    self.listado_destinatarios_con_copia.remove(d);
                  }else{
                    self.newArray.push({"id":d.id , "nombres" : d.nombres})
                  }                
          });
          self.listado_destinatarios_con_copia([]);
          self.listado_destinatarios_con_copia(self.newArray());
        }        
    }

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

     // //funcion guardar
     self.guardar_correspondenciaEnviada=function(){
   
      if (CorrespondenciaRecibidaViewModel.errores_correspondencia_enviada().length == 0) {//se activa las validaciones*/
            self.correspondenciaEnviadaVO.destinatarioCopia([])
            if(self.listado_destinatarios_con_copia().length>0){
               ko.utils.arrayForEach(self.listado_destinatarios_con_copia(), function(d,index) {
                      self.correspondenciaEnviadaVO.destinatarioCopia.push(d.id)
                });
            }

            self.correspondenciaEnviadaVO.contenido(tinyMCE.activeEditor.getContent({ format: 'text' }))
            self.correspondenciaEnviadaVO.contenidoHtml(tinyMCE.activeEditor.getContent())
          
            if(self.correspondenciaEnviadaVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar_correspondencia_enviada();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: path_principal+'/api/CorrespondenciaEnviada/',//url api
                     parametros:self.correspondenciaEnviadaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
            }else{                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                              self.filtro("");
                              self.consultar(self.paginacion.pagina_actual());
                              $('#modal_acciones').modal('hide');
                              self.limpiar_correspondencia_enviada();
                            } 
                       },//funcion para recibir la respuesta 
                       url: path_principal+'/api/CorrespondenciaEnviada/'+ self.correspondenciaEnviadaVO.id()+'/',
                       parametros:self.correspondenciaEnviadaVO                        
                  };
                  Request(parametros);
            }
        } else {
             CorrespondenciaRecibidaViewModel.errores_correspondencia_enviada.showAllMessages();
        }
     }

     // //limpiar el modelo 
     self.limpiar_correspondencia_enviada=function(){      
            self.correspondenciaEnviadaVO.id(0);
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
            tinymce.activeEditor.setContent('')
            tinymce.activeEditor.execCommand('mceCleanup');
            self.listado_destinatarios_con_copia([]);
     }


  // --- TIEMPO DE RESPUESTA --- // --- TIEMPO DE RESPUESTA --- //
  self.abrir_modal_respuesta = function (obj) {
    $('#modal_acciones_respuesta').modal('show');
    self.consultar_por_id_respuesta(obj);    
  } 

  self.consultar_por_id_respuesta = function (obj) {
     self.limpiar_correspondencia_recibida();
     path = self.url+'CorrespondenciaRecibida/'+obj.correspondenciaRecibida.id+'/';
     parameter = {  };
       RequestGet(function (results,count) {            
          self.titulo('Configurar tiempo de respuesta Radicado No. '+obj.correspondenciaRecibida.radicado);             
          self.llenar_correspondencia_recibida(results)
       }, path, parameter);
   }  

  self.guardar_fecha_respuesta=function(){
    if (CorrespondenciaRecibidaViewModel.errores_correspondencia().length == 0) {//se activa las validaciones*/
          if(self.correspondenciaRecibidaVO.id()>0){

            var parametros={     
                  metodo:'PUT',                
                 callback:function(datos, estado, mensaje){
                      if (estado=='ok') {
                        self.filtro("");
                        self.consultar_mis_correspondencias(self.paginacion.pagina_actual());
                        $('#modal_acciones_respuesta').modal('hide');
                        self.checkall(false);
                      } 
                 },//funcion para recibir la respuesta 
                 url: path_principal+'/api/CorrespondenciaRecibida/'+ self.correspondenciaRecibidaVO.id()+'/',
                 parametros:self.correspondenciaRecibidaVO                        
            };
            /*Request(parametros);*/
            RequestFormData(parametros);
          }

      } else {
           CorrespondenciaRecibidaViewModel.errores_correspondencia.showAllMessages();
      }
   } 

  //funcion consultar estados del proyectos 
    self.consultar_estados_correspondencia = function () {                
            path = self.url+'Estados/';
            parameter = { ignorePagination : 1 , aplicacion : self.app_correspondencia };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_estados_correspondencia_recibida(datos);
                } else {
                    self.listado_estados_correspondencia_recibida([]);
                }            
            }, path, parameter);        
    }
  // --- REASIGNAR CORRESPONDENCIA --- // --- REASIGNAR CORRESPONDENCIA --- // --- REASIGNAR CORRESPONDENCIA ---
  self.abrir_modal_reasignar = function (obj) {
    self.titulo('Reasignar la correspondencia con el radicado No. '+obj.correspondenciaRecibida.radicado); 
    $('#modal_acciones_reasignar').modal('show');   
    self.correspondencia_recibida_asignadaVO.correspondenciaRecibida_id([]);
    self.correspondencia_recibida_asignadaVO.estado_id(estado_reasignada);
    self.correspondencia_recibida_asignadaVO.correspondenciaRecibida_id.push(obj.correspondenciaRecibida.id);     
  } 
  self.asignar_carta = function(){
    self.correspondencia_recibida_asignadaVO.usuario_id(self.usuarioAsignarCarta());
    self.guardar_asignacion();
  }  

  self.listado_usuarios_reasignar = ko.observableArray([]);

  self.consultar_usuarios_reasignar_enter = function (d,e) {
      if (e.which == 13) {
         self.consultar_usuarios_reasignar();
      }
      return true;
    }
    self.consultar_usuarios_reasignar_btn = function (d,e) {
         self.consultar_usuarios_reasignar();
    }

    //funcion consultar funcionarios para agregar el destinatario
    self.consultar_usuarios_reasignar = function () {
            var filtro = $("#filtro_Destinatario").val();  
            path = path_principal+self.app_parametrizacion+'usuariosConFuncionarios/';
            parameter = { empresa : self.correspondenciaRecibidaVO.empresa_id() , dato : filtro };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_usuarios_reasignar(datos);
                } else {
                    self.listado_usuarios_reasignar([]);
                }          
            }, path, parameter,undefined,false);      
    } 
     // //funcion guardar
     self.guardar_asignacion=function(){
      if (CorrespondenciaRecibidaViewModel.errores_correspondencia_asignacion().length == 0) {//se activa las validaciones*/
            if(self.correspondencia_recibida_asignadaVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.consultar_mis_correspondencias(self.paginacion.pagina_actual());
                            $('#modal_acciones_reasignar').modal('hide');
                            self.checkall(false);
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url_app_correspondencia+'create_asignar_correspondencia/',//url api
                     parametros:self.correspondencia_recibida_asignadaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }

        } else {
             CorrespondenciaRecibidaViewModel.errores_correspondencia_asignacion.showAllMessages();
        }
     } 
  // --- ASIGNAR ESTADO POR REVISAR O ESTADO REVISADA --- // --- ASIGNAR ESTADO POR REVISAR O ESTADO REVISADA  
  self.asignar_revisada = function(){

        var usuario = $("#user").val();
        self.correspondencia_recibida_asignadaVO.usuario_id(usuario);
        self.correspondencia_recibida_asignadaVO.estado_id(estado_revisada);
        self.correspondencia_recibida_asignadaVO.correspondenciaRecibida_id([]);
        var count=0;
         ko.utils.arrayForEach(self.listado_correspondencias(), function(d) {
            if(d.eliminado()==true){
                count=1;
               self.correspondencia_recibida_asignadaVO.correspondenciaRecibida_id.push(d.correspondenciaRecibida.id)
            }
         });
         if(count==0){
              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione una carta para establecer a estado revisada.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
         }else{
             self.guardar_asignacion();
         } 
  }

  self.asignar_por_revisar = function(){
    
        var usuario = $("#user").val();
        self.correspondencia_recibida_asignadaVO.usuario_id(usuario);
        self.correspondencia_recibida_asignadaVO.estado_id(estado_por_revisar);
        self.correspondencia_recibida_asignadaVO.correspondenciaRecibida_id([]);
         var count=0;
         ko.utils.arrayForEach(self.listado_correspondencias(), function(d) {
            if(d.eliminado()==true){
                count=1;
               self.correspondencia_recibida_asignadaVO.correspondenciaRecibida_id.push(d.correspondenciaRecibida.id)
            }
         });
         if(count==0){
              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione una carta para establecer a estado por revisar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
         }else{
             self.guardar_asignacion();
         } 
  }
  
  self.ver_soporte = function(obj) {
    window.open(path_principal+"/correspondencia_recibida/ver-soporte/?id="+ obj.id, "_blank");
  }

}

var correspondencia = new CorrespondenciaRecibidaViewModel();

$('#txtBuscar').val(sessionStorage.getItem("app_correspondenciaRecibida_filtro"));   
correspondencia.correspondenciaRecibidaVO_filtro.usuarioElaboro(sessionStorage.getItem("app_correspondenciaRecibida_usuarioElaboro"));
correspondencia.correspondenciaRecibidaVO_filtro.soporte_si(sessionStorage.getItem("app_correspondenciaRecibida_soporte_si"));
correspondencia.correspondenciaRecibidaVO_filtro.soporte_no(sessionStorage.getItem("app_correspondenciaRecibida_soporte_no"));
correspondencia.correspondenciaRecibidaVO_filtro.remitente(sessionStorage.getItem("app_correspondenciaRecibida_remitente"));
correspondencia.correspondenciaRecibidaVO_filtro.radicado(sessionStorage.getItem("app_correspondenciaRecibida_radicado"));
correspondencia.correspondenciaRecibidaVO_filtro.asunto(sessionStorage.getItem("app_correspondenciaRecibida_asunto"));
correspondencia.correspondenciaRecibidaVO_filtro.fechaDesde(sessionStorage.getItem("app_correspondenciaRecibida_fechaDesde"));
correspondencia.correspondenciaRecibidaVO_filtro.fechaHasta(sessionStorage.getItem("app_correspondenciaRecibida_fechaHasta"));
correspondencia.correspondenciaRecibidaVO_filtro.radicado_previo(sessionStorage.getItem("app_correspondenciaRecibida_radicado_previo"));

CorrespondenciaRecibidaViewModel.errores_correspondencia = ko.validation.group(correspondencia.correspondenciaRecibidaVO);
CorrespondenciaRecibidaViewModel.errores_correspondencia_filtro = ko.validation.group(correspondencia.correspondenciaRecibidaVO_filtro);
CorrespondenciaRecibidaViewModel.errores_correspondencia_asignacion = ko.validation.group(correspondencia.correspondencia_recibida_asignadaVO);

CorrespondenciaRecibidaViewModel.errores_correspondencia_enviada = ko.validation.group(correspondencia.correspondenciaEnviadaVO);
ko.applyBindings(correspondencia);