function RetieViewModel() {
	var self=this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');    
    self.url=path_principal+'/api/Retie/'; 
    self.filtro=ko.observable('');
    self.seleccionar=ko.observable(false);
    self.listado_historial=ko.observableArray([]);    
    self.listado_persona = ko.observableArray([]);
    self.filtro_persona=ko.observable('');
    self.es_ejecucion=ko.observable(false);
    self.mcontrato_id=ko.observable('');
    self.listado_contratistas=ko.observableArray([]);
    self.listado_proyectos=ko.observableArray([]);
    self.listado_departamentos=ko.observableArray([]);
    self.listado_municipios=ko.observableArray([]);

    self.filtrosVO={
      dato:ko.observable(''),
    	contrato_id:ko.observable(''),
      proyecto_id:ko.observable(''),
      departamento_id:ko.observable(''),
      municipio_id:ko.observable(''),
      estado_id:ko.observable(''),
      fecha_inicio_programada:ko.observable(''),
      fecha_final_programada:ko.observable(''),
      fecha_inicio_ejecutada:ko.observable(''),
      fecha_final_ejecutada:ko.observable(''),
    }

    self.asistenteVO={
      nombre_persona:ko.observable('').extend({ required: { message: '(*)Seleccione la persona' } }),
      apellido_persona:ko.observable(''),
      rol_id:ko.observable('').extend({ required: { message: '(*)Seleccione el rol' } }),
      persona_id:ko.observable('')
    }

    self.no_conformidadesVO={
      id:ko.observable(0),
      descripcion:ko.observable('').extend({ required: { message: '(*)Ingrese la descripción' } }),
      corregida:ko.observable('')      
    }

    self.soportesVO={
      id:ko.observable(0),
      soporte:ko.observable('').extend({ required: { message: '(*)Seleccione el soporte' } }),
      nombre:ko.observable('').extend({ required: { message: '(*)Ingrese la nombre del soporte' } }),
      eliminado:ko.observable(false)
    }

    self.notificar_correoVO={
      id:ko.observable(0),      
      correo:ko.observable('').extend({ required: { message: '(*)Ingrese el correo de la persona.' } }).extend({ email: { message: '(*)Ingrese un correo valido' } }),
      nombre:ko.observable('').extend({ required: { message: '(*)Ingrese la nombre de la persona' } }),
      eliminado:ko.observable(false)
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

    self.personaVO={
        id:ko.observable(0),
        cedula:ko.observable('').extend({ required: { message: '(*)Digite la cédula de la persona' } }),
        nombres:ko.observable('').extend({ required: { message: '(*)Digite el nombre de la persona' } }),
        apellidos:ko.observable('').extend({ required: { message: '(*)Digite el apellidos de la persona' } }),
        direccion:ko.observable(''),//.extend({ required: { message: '(*)Digite la dirección de la persona' } }),
        correo:ko.observable('').extend({required: { message: '(*)Digite el correo de la persona' }}).extend({ email: { message: '(*)Ingrese un correo valido' } })
     };

    self.retieVO={		    
        id:ko.observable(0),
        fecha_programada:ko.observable('').extend({ required: { message: '(*)Seleccione la fecha de programación' } }),
        fecha_ejecutada:ko.observable('').extend({ validation: { validator: validar_ejecucion, message: '(*) Seleccione la fecha de ejecución.' } }),
        hora:ko.observable('').extend({ required: { message: '(*)Seleccione la hora de la visita' } }),
        observacion:ko.observable(''),
        comentario_cancelado:ko.observable(''),
        estado_id:ko.observable(''),
        proyecto_id:ko.observable(''),
        asistentes:ko.observableArray([]),
        no_conformidades:ko.observableArray([]),
        soportes:ko.observableArray([]),
        notificar_correos:ko.observableArray([])
 	  };

    function validar_ejecucion(val) {

      if(!self.es_ejecucion())
        return true;

      return self.es_ejecucion() && val!=null && val!='';
    }
    
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);
    }

    self.exportar_excel=function(){      
      location.href=path_principal+"/retie/exportar-visitas/?dato="+self.filtro()+"&contrato_id="+self.filtrosVO.contrato_id();     
    }

     self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Configuración');
        $('#modal_acciones').modal('show');
    }

    self.abrir_filtros = function () {      
        $('#modal_filtros').modal('show');
    }

     self.abrir_buscar_persona=function(){
        $('#modal_buscar_persona').modal('show');
    }

    self.abrir_crear_persona = function() {
        $('#modal_crear_persona').modal('show');
    }

    
    self.limpiar_persona=function () {
         
        self.personaVO.id(0);
        self.personaVO.cedula('');
        self.personaVO.nombres('');
        self.personaVO.apellidos('');
        self.personaVO.direccion('');
        self.personaVO.correo('');
     };

     self.limpiar=function(){

      self.retieVO.id(0);
      self.retieVO.fecha_programada('');
      self.retieVO.fecha_ejecutada('');
      self.retieVO.hora('');
      self.retieVO.observacion('');
      self.retieVO.comentario_cancelado('');
      self.retieVO.estado_id('');
      self.retieVO.proyecto_id('');

    }

    self.consultar = function (pagina) {
        if (pagina > 0) {
            //self.buscado_rapido(true);
            self.filtrosVO.dato($('#txtBuscar').val());
            path =self.url + '?format=json&page='+pagina;
            parameter =ko.toJS(self.filtrosVO);
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    
                    self.mensaje('');
                    //self.listado(results);  
                    self.listado(agregarOpcionesObservable(datos.data));  
                    
                    $('#modal_filtros').modal('hide');
                   
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                cerrarLoading();
                
            }, path, parameter, undefined, false);
        }
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }


    self.paginacion.pagina_actual.subscribe(function (pagina) {       
       self.consultar(pagina);
    });


     self.guardar=function(){    	  
       
        if (RetieViewModel.errores().length==0) {
           
          if (self.es_ejecucion()==true) {

            var formData= new FormData();
            formData.append('id',self.retieVO.id());
            formData.append('fecha_programada',self.retieVO.fecha_programada());
            formData.append('fecha_ejecutada',self.retieVO.fecha_ejecutada());
            formData.append('hora',self.retieVO.hora());
            formData.append('observacion',self.retieVO.observacion());
            formData.append('comentario_cancelado',self.retieVO.comentario_cancelado());
            formData.append('estado_id',self.retieVO.estado_id());
            formData.append('proyecto_id',self.retieVO.proyecto_id());
            formData.append('asistentes',ko.toJSON(self.retieVO.asistentes()));
            formData.append('no_conformidades',ko.toJSON(self.retieVO.no_conformidades()));
            formData.append('soportes',ko.toJSON(self.retieVO.soportes()));
            formData.append('notificar_correos',ko.toJSON(self.retieVO.notificar_correos()));

            ko.utils.arrayForEach(self.retieVO.soportes(),function(p){
                if (p.id()==0 && p.soporte()!=null) {//validamos que se un archivo
                  formData.append('soporte[]',p.soporte());
                  formData.append('nombre[]',p.nombre());
                }
            });
            
            var parametros={   
                      metodo:'PUT',                
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {     
                            $('#modal_acciones').modal('hide');
                            self.consultar_por_id($('#retie_id').val());
                         }
                      },//funcion para recibir la respuesta 
                      url: path_principal + '/retie/actualizar_seguimiento/'+self.retieVO.id(),
                      parametros:formData,
                      completado:function(){
                        cerrarLoading();
                       }                
                };
                       
                RequestFormData2(parametros);
            }else{
                var parametros={   
                      metodo:'PUT',                
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {     
                            $('#modal_acciones').modal('hide');            
                            //self.consultar(1);
                            self.consultar_por_id($('#retie_id').val());
                         }
                      },//funcion para recibir la respuesta 
                      url: self.url+ self.retieVO.id() + '/',
                      parametros:self.retieVO,
                      completado:function(){
                        cerrarLoading();
                      }
                      //path_principal + '/retie/actualizar_seguimiento/'+self.retieVO.id(),
                };
                       
                Request(parametros);
            }
          
        } else {
            RetieViewModel.errores.showAllMessages();//mostramos las validacion
        }
    }

     self.guardar_persona=function(){

        if (RetieViewModel.errores_persona().length == 0) {//se activa las validaciones
         var parametros={                     
               callback:function(datos, estado, mensaje){
                  if (estado=='ok') {                        
                      self.consultar(self.paginacion.pagina_actual());
                      self.asistenteVO.nombre_persona(datos.nombres);  
                      self.asistenteVO.apellido_persona(datos.apellidos);
                      self.asistenteVO.persona_id(datos.id);
                      $('#modal_crear_persona').modal('hide');
                      self.limpiar_persona();
                        
                  }                        
                  
               },//funcion para recibir la respuesta 
               url:path_principal+'/api/persona/',
               parametros:ko.toJS(self.personaVO),
               completado:function(){
                 cerrarLoading();
               }
         };
                    
         Request(parametros);

        } else {
             RetieViewModel.errores_persona.showAllMessages();//mostramos las validacion
        }
      }

    self.eliminar_un_registro=function(id){
               
        RequestAnularOEliminar('¿Desea eliminar el registro seleccionado?', 
          self.url + id+'/', 
          function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultar(self.paginacion.pagina_actual());                  
             }
        }, function(){ 
           cerrarLoading();        
        }, false); 	
    }

    self.eliminar=function(){
         var lista=[];
        ko.utils.arrayForEach(self.listado(), function(p){          
          if (p.procesar()) {
            lista.push(p.id);
          }
        });
        
        RequestAnularOEliminar('¿Desea eliminar el(los) registro(s) seleccionado(s)?', 
          path_principal+'/retie/eliminar_configuracion_porcentajes/', {lista:lista}, 
          function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultar(self.paginacion.pagina_actual());                  
             }
        }, function(){           
          cerrarLoading();                   
        }, false); 	
    }


    self.consultar_por_id = function (id) {
       
      // alert(obj.id)
       path =self.url+id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
            //self.limpiar();
            //self.titulo('Actualizar Configuración');
                        
            self.retieVO.id(datos.id);
            self.retieVO.fecha_programada(datos.fecha_programada);
            self.retieVO.fecha_ejecutada(datos.fecha_ejecutada);
            self.retieVO.hora(datos.hora);
            self.retieVO.observacion(datos.observacion);
            self.retieVO.comentario_cancelado(datos.comentario_cancelado);
            self.retieVO.estado_id(datos.estado.id);
            self.retieVO.proyecto_id(datos.proyecto.id);
            self.listado_historial(datos.historial);
            self.retieVO.asistentes(agregarOpcionesObservable(convertToObservableArray(datos.asistentes)));            
            self.retieVO.no_conformidades(convertToObservableArray(datos.no_conformidades));
            self.retieVO.soportes(convertToObservableArray(agregarOpcionesObservable(datos.soportes)));
            self.retieVO.notificar_correos(convertToObservableArray(datos.notificar_correos));
            //$('#modal_acciones').modal('show');

         }, path, {}, function(){
                    cerrarLoading();
                   });

    }

    self.seleccionar.subscribe(function(val){
    	ko.utils.arrayForEach(self.listado(),function(p){
    		p.procesar(val);
    	});
    });

    self.consultar_historial = function () {
     
         path = path_principal + '/api/HistorialVisita/?format=json&sin_paginacion=';
         RequestGet(function (datos, estado, mensage) {
           
            self.listado_historial(datos);

         }, path, {retie_id:$('#retie_id').val()}, 
         function(){
            cerrarLoading();
         });

    }

    //consultar persona
    self.consulta_enter_persona = function(d, e) {
        if (e.which == 13) {
            self.consultar_persona();
        }
        return true;
    }

    self.consultar_persona = function() {

        self.filtro_persona($('#txt_buscar_persona').val());
        path = path_principal + '/api/persona/?format=json&sin_paginacion=';
        parameter = {
            dato: self.filtro_persona()
        };
        RequestGet(function(datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                                  
                self.listado_persona(datos);  
                $('.panel-scroller').scroller('reset');               


            } else {
                self.listado_persona([]);
            }
        }, path, parameter, function(){
                    cerrarLoading();
                   });
    }

    self.seleccionar_persona = function() {

        var conteo = 0;
        ko.utils.arrayForEach(self.listado_persona(), function(p) {
            if (p.id == self.asistenteVO.persona_id()) {
                self.asistenteVO.nombre_persona(p.nombres);
                self.asistenteVO.apellido_persona(p.apellidos);
                conteo++;
                return;
            }
        });
        if (conteo == 0) {
            return false;
        }        
        $('#modal_buscar_persona').modal('hide');

    }

    self.agregar_persona=function(){

        if (RetieViewModel.errores_asistente().length==0) {
            self.retieVO.asistentes.push({
              no_asistio:ko.observable(false),
              eliminado:ko.observable(false),
              id:ko.observable(0),        
              persona:{id:ko.observable(self.asistenteVO.persona_id()),
                nombres:ko.observable(self.asistenteVO.nombre_persona()), 
                apellidos:ko.observable(self.asistenteVO.apellido_persona())},        
              rol:{id:self.asistenteVO.rol_id(),nombre:$('#ddlrol option:selected').text()} ,
              notificacion_enviada:ko.observable(false)     
            });

            self.asistenteVO.rol_id('');
            self.asistenteVO.nombre_persona('');
            self.asistenteVO.apellido_persona('');
            self.asistenteVO.persona_id('');
        }
        else{
          RetieViewModel.errores_asistente.showAllMessages();
        }    

    }

    self.remover_asistente=function(obj) { 
        self.retieVO.asistentes.remove(obj);
    }


    self.remover_soportes=function(obj) { 
        if (obj.id()>0) {
          obj.eliminado(true);
        }else{
          self.retieVO.soportes.remove(obj);
        }
    }

    self.remover_no_conformidades=function(obj) { 
        self.retieVO.no_conformidades.remove(obj);
    }

    self.agregar_no_conformidades=function(){

        if (RetieViewModel.errores_no_conformidades().length==0) {
            self.retieVO.no_conformidades.push({
               id:ko.observable(0),
               descripcion:ko.observable(self.no_conformidadesVO.descripcion()),
               corregida:ko.observable(false)                  
            });

            self.no_conformidadesVO.descripcion('');
        }
        else{
          RetieViewModel.errores_no_conformidades.showAllMessages();
        }    

    }

    self.agregar_soportes=function(){

        if (RetieViewModel.errores_soportes().length==0) {
            self.retieVO.soportes.push({
               id:ko.observable(0),
               soporte:ko.observable(self.soportesVO.soporte()),
               nombre:ko.observable(self.soportesVO.nombre()),
               eliminado:ko.observable(false)             
            });

            self.no_conformidadesVO.descripcion('');
        }
        else{
          RetieViewModel.errores_soportes.showAllMessages();
        }    

    }

    self.agregar_notificar_correo=function(){

        if (RetieViewModel.errores_notificar_correo().length==0) {
            self.retieVO.notificar_correos.push({             
              eliminado:ko.observable(false),
              id:ko.observable(0),        
              correo:ko.observable(self.notificar_correoVO.correo()),
              nombre:ko.observable(self.notificar_correoVO.nombre()),
              notificacion_enviada:ko.observable(false)     
            });

            self.notificar_correoVO.nombre('');
            self.notificar_correoVO.correo('');
        }
        else{
          RetieViewModel.errores_notificar_correo.showAllMessages();
        }    

    }

    self.remover_notificar_correo=function(obj) { 
        self.retieVO.notificar_correos.remove(obj);
    }

    self.cancelar_visita=function(obj){


       $.confirm({
        title: 'Confirmar!',
        content: "<h4>Desea cancelar la visita seleccionada?</h4><br><br>\
        <textarea id='comentario_cancelado' cols='30' rows='5' class='form-control'></textarea> \
        <span id='validar_comentario_cancelado' class='validationMessage' style='display:none;'>(*)Ingrese el comentario</span>",
        confirmButton: 'Si',
        confirmButtonClass: 'btn-info',
        cancelButtonClass: 'btn-danger',
        cancelButton: 'No',
        confirm: function() {

            if ($('#comentario_cancelado').val()==null || $('#comentario_cancelado').val()=='') {
              $('#validar_comentario_cancelado').show();
              return false;
            }
            $('#validar_comentario_cancelado').hide();  
            var parametros={   
                metodo:'PUT',                
                callback:function(datos, estado, mensaje){
                   if (estado=='ok') { 
                      self.consultar(self.paginacion.pagina_actual());
                   }
                },
                url: path_principal + '/retie/cancelar_visita/'+obj.id,
                parametros:{comentario:$('#comentario_cancelado').val()} ,
                 completado:function(){
                    cerrarLoading();
                   }              
            };
                         
            Request(parametros);
           
        }
      });
      
    }

    self.mcontrato_id.subscribe(function (val) {    
        if (val>0) {
           path = path_principal + '/proyecto/filtrar_proyectos/';
           RequestGet(function (datos, estado, mensage) {         
              self.listado_contratistas(datos['contratista']);
           }, path, {mcontrato:val}, function(){
                    cerrarLoading();
                   });

           path = path_principal + '/api/Proyecto/?format=json&ignorePagination=';
           RequestGet(function (datos, estado, mensage) {         
              self.listado_proyectos(datos);
           }, path, {contrato_id:val}, function(){
                    cerrarLoading();
                   });
        }else{
          self.listado_contratistas([]);
          self.listado_proyectos([]);
        }
    });

     self.filtrosVO.contrato_id.subscribe(function (val) {    
        if (val>0) {

           path = path_principal + '/api/Proyecto/?format=json&ignorePagination=';
           RequestGet(function (datos, estado, mensage) {         
              self.listado_proyectos(datos);
           }, path, {contrato_id:val}, function(){
                    cerrarLoading();
                   });

           path = path_principal + '/proyecto/filtrar_proyectos/';
           RequestGet(function (datos, estado, mensage) {         
              self.listado_departamentos(datos['departamento']);
              self.listado_municipios(datos['municipio']);
           }, path, {mcontrato:val}, function(){
                    cerrarLoading();
                   });
           
        }else{
          
           path = path_principal + '/api/departamento/?format=json&ignorePagination=';
           RequestGet(function (datos, estado, mensage) {         
              self.listado_departamentos(datos);              
           }, path, {mcontrato:val}, function(){
                    cerrarLoading();
                   });

            self.listado_contratistas([]);
            self.listado_proyectos([]);

        }
    });

    self.filtrosVO.departamento_id.subscribe(function(val){
        if (val>0) {
            path = path_principal + '/api/Municipio/?format=json&ignorePagination=';
            RequestGet(function (datos, estado, mensage) {         
               self.listado_municipios(datos);
               self.filtrosVO.municipio_id('');                
            }, path, {id_departamento:val}, function(){
                    cerrarLoading();
                   });
        }else{
          self.filtrosVO.municipio_id('');
        }        
    }); 

    self.verificarProceso = function(item){
       path = path_principal + '/api/procesoRelacion/?proceso=10&idApuntador='+ item.proyecto.id +'&idTablaReferencia=' + item.proyecto.id;
       RequestGet(function (datos, estado, mensage) {     
          if (estado=='ok' && datos!=null && datos.data.length > 0) {
              
            window.location.href = '../../proceso/detalleSeguimientoProcesoDatos/' + datos.data[0].id; 

          }else{
             $.confirm({
                title: 'Confirmar!',
                content: "<h4>No se encontro implementado el seguimiento para este proyecto ¿Desea implementarlo?</h4>",
                confirmButton: 'Si',
                confirmButtonClass: 'btn-info',
                cancelButtonClass: 'btn-danger',
                cancelButton: 'No',
                confirm: function() {
                  window.location.href = '../../proceso/implementacion/retiesimple/' + item.proyecto.id;
                }
            });            
          }
       }, path, {}, function(){
          cerrarLoading();
       });
    }

}

var retie = new RetieViewModel();
RetieViewModel.errores=ko.validation.group(retie.retieVO);
RetieViewModel.errores_persona=ko.validation.group(retie.personaVO);
RetieViewModel.errores_asistente=ko.validation.group(retie.asistenteVO);
RetieViewModel.errores_no_conformidades=ko.validation.group(retie.no_conformidadesVO);
RetieViewModel.errores_soportes=ko.validation.group(retie.soportesVO);
RetieViewModel.errores_notificar_correo=ko.validation.group(retie.notificar_correoVO);
ko.applyBindings(retie);