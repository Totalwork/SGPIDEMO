function EmpleadoViewModel(argument) {

  var self=this;

  self.listado=ko.observableArray([]);
  self.mensaje=ko.observable('');
  self.titulo=ko.observable('');
  self.filtro=ko.observable('');
  self.checkall=ko.observable(false);
  self.listado_persona=ko.observableArray([]);
  self.filtro_persona=ko.observable('');
  self.url=path_principal+'/api/Empleado/'; 
  self.id_persona=ko.observable(0);
  self.nombre_persona=ko.observable(''); 
  self.soporte_tsa=ko.observable('');
  self.soporte_matricula=ko.observable('');
  self.hoja_de_vida=ko.observable('');
  self.foto=ko.observable('');
  self.id_empleado=ko.observable(0);
  self.obj_empleado=ko.observable({});
  self.nombre_contratista=ko.observable('');
  self.matricula=ko.observable('');
  self.tipo_matricula=ko.observable('');
  self.nombre_cargo=ko.observable('');
  self.nombres_persona=ko.observable('');
  self.apellidos_persona=ko.observable('');
  self.buscado_rapido=ko.observable(sessionStorage.getItem("buscado_rapido"));
  self.listado_cargos=ko.observableArray([]);
  self.cargo_id=ko.observable('');
  self.estado_novedad_id=ko.observable(0);
  self.nombres_estado=ko.observable('');
  self.matricula_id=ko.observable();
  self.cedula_persona=ko.observable('');
  self.foto_perfil=ko.observable('');
  self.requiere_soporte_tsa=ko.observable(true);
  self.requiere_soporte_matricula=ko.observable(true);
  self.requiere_hoja_de_vida=ko.observable(true);
  self.soporte_licencia=ko.observable('');
  self.tiene_licencia=ko.observable('');
  self.obj_soporte_tsa=ko.observable('');
  self.contratista_id = ko.observable('');

  /*parametros de busqueda*/
    
    self.filtros={
      contratista_id:ko.observable(''),//.extend({ required: { message: '(*)Seleccione' } }),
      estado_id:ko.observable(''),
      criterio:ko.observable('')
    }

     self.personaVO={
        id:ko.observable(0),
        cedula:ko.observable('').extend({ required: { message: '(*)Digite la cédula de la persona' } }),
        nombres:ko.observable('').extend({ required: { message: '(*)Digite el nombre de la persona' } }),
        apellidos:ko.observable('').extend({ required: { message: '(*)Digite el apellidos de la persona' } }),
        direccion:ko.observable(''),//.extend({ required: { message: '(*)Digite la dirección de la persona' } }),
        correo:ko.observable('')//.extend({required: { message: '(*)Digite el correo de la persona' }}).extend({ email: { message: '(*)Ingrese un correo valido' } })
     };

    self.empleadoVO={
      id:ko.observable(0),
      persona_id:ko.observable('').extend({ required: { message: '(*) Seleccione la persona.' } }),
      fecha_nacimiento:ko.observable('').extend({ required: { message: '(*) Ingrese la fecha de nacimiento del empleado.' } }),
      escolaridad_id:ko.observable('').extend({ required: { message: '(*) Seleccione la escolaridad.' } }),
      contratista_id:ko.observable('').extend({ required: { message: '(*) Seleccione el contratista.' } }),           
      fecha_tsa:ko.observable('').extend({ validation: { validator: validar_fecha_tsa, message: '(*) Seleccione la fecha de vencimiento de trabajo en altura.' } }),
      soporte_tsa:ko.observable('').extend({ validation: { validator: validar_soporte_tsa, message: '(*) Seleccione el soporte en pdf de trabajo en altura.' } }),               
      matricula_id:ko.observable('').extend({ required: { message: '(*) Seleccione la matricula.' } }),
      tipo_matricula_id:ko.observable(''),
      soporte_matricula:ko.observable(''),
      cargo_id:ko.observable('').extend({ required: { message: '(*) Seleccione el cargo' } }),
      hoja_de_vida:ko.observable('').extend({ validation: { validator: validar_hoja_de_vida, message: '(*) Seleccione la hoja de vida(.doc, .docx, .pdf).' } }),        
      apto:ko.observable('1'),
      observacion:ko.observable(''),
      foto:ko.observable(''), 
      estado_id:ko.observable(5),
      fecha_ingreso: ko.observable('').extend({ required: { message: '(*) Seleccione la fecha de ingreso al proyecto.' } }),
      tiene_licencia: ko.observable('').extend({ required: { message: '(*) Seleccione si tiene licencia.' } }),
      vencimiento_licencia: ko.observable('').extend({ validation: { validator: validar_vencimiento_licencia, message: '(*) Seleccione la fecha de vencimiento de la licencia.' } }),
      soporte_licencia: ko.observable('').extend({ validation: { validator: validar_soporte_licencia, message: '(*) Seleccione el soporte(.pdf).' } })
    };

    self.novedadVO={
      id:ko.observable(0),
      fecha:ko.observable('').extend({ required: { message: '(*) Seleccione la fecha de la novedad' } }),
      empleado_id:ko.observable(''),
      estado_id:ko.observable('').extend({ required: { message: '(*) Seleccione el estado' } }),
      descripcion:ko.observable(''),
    };

    self.empleado_actoVO={
      id:ko.observable(0),
      apto:ko.observable('').extend({ required: { message: '(*) Seleccione si el empleado es apto.' } }),
      observacion:ko.observable('').extend({ required: { message: '(*) Ingrese una observación para continuar.' } })
    };
   
    function validar_soporte_tsa(val) {

      if ((val=='' || val==null) && 
        (self.soporte_tsa()==null || self.soporte_tsa()=='') 
        && self.requiere_soporte_tsa()) {
        return false;
      }

      if (self.id_empleado()>0 || !self.requiere_soporte_tsa())  
          return true;
      else
        return self.id_empleado()==0 && val!='' && val!=null;      

    }

    function validar_fecha_tsa(val) {

      if ((val=='' || val==null) && self.requiere_soporte_tsa()) {
        return false;
      }

      if (self.id_empleado()>0 || !self.requiere_soporte_tsa())  
          return true;
      else
        return self.id_empleado()==0 && val!='' && val!=null;      

    }

    function validar_soporte_matricula(val) {

      if ((val=='' || val==null) && 
        (self.soporte_matricula()==null || self.soporte_matricula()=='') 
        && self.requiere_soporte_matricula()) {
        return false;
      }

      if (self.id_empleado()>0 || !self.requiere_soporte_matricula())  
          return true;
      else
        return self.id_empleado()==0 && val!='' && val!=null;

    }

    function validar_hoja_de_vida(val) {

      if (self.id_empleado()>0 && (val=='' || val==null) && 
        (self.hoja_de_vida()==null || self.hoja_de_vida()=='') 
        && self.requiere_hoja_de_vida()) {
        return false;
      }

      if (self.id_empleado()>0 || !self.requiere_hoja_de_vida())  
          return true;
      else
        return self.id_empleado()==0 && val!='' && val!=null;
       

    }

    function validar_vencimiento_licencia(val) {
     
      if (self.tiene_licencia()>0 && (val=='' || val==null)) 
          return false;      
      else if (self.tiene_licencia()>0 && val!='' && val!=null)  
          return true;
      else if (self.tiene_licencia()=='0')  
          return true;      
          
    }

    function validar_soporte_licencia(val) {

      if (self.id_empleado()>0 && self.tiene_licencia()>0 && 
        (val=='' || val==null) && (self.soporte_licencia()=='' || self.soporte_licencia()==null)) {
          return false;  
      }
      if (self.id_empleado()>0 && self.tiene_licencia()>0 && 
        ((val!='' && val!=null) || (self.soporte_licencia()!='' && 
        self.soporte_licencia()!=null))) {
          return true;  
      }
      if (self.id_empleado()>0 && self.tiene_licencia()=='0') {
          return true;  
      }

      if (self.tiene_licencia()>0 && (val=='' || val==null)) 
          return false;      
      else if (self.tiene_licencia()>0 && val!='' && val!=null)  
          return true;
      else if (self.tiene_licencia()=='0')  
          return true;      
          
    }

    self.empleadoVO.tiene_licencia.subscribe(function(val) {
      self.tiene_licencia(val);
    });

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

    self.abrir_modal = function() {
        self.limpiar();
        window.location.href='../crear-empleado';
        /*self.titulo('Registrar Empleado');
        $('#modal_acciones').modal('show');*/
    }

     self.abrir_modal_ver_mas = function (obj) {
        
        path =self.url+obj.id+'/?format=json';
        RequestGet(function (datos, estado, mensage) {  
           
            self.obj_empleado(datos);
            self.obj_soporte_tsa(datos.soporte_tsa);
            self.nombre_persona(datos.persona.nombres + ' ' + datos.persona.apellidos);
            self.cedula_persona(datos.persona.cedula);
            self.nombre_contratista(datos.contratista.nombre);
            self.matricula(datos.matricula ? datos.matricula.nombre : ''); 
            self.matricula_id(datos.matricula ? datos.matricula.id : '');          
            self.tipo_matricula(datos.tipo_matricula!=null ? datos.tipo_matricula.nombre : '');
            self.nombre_cargo(datos.cargo.nombre);
            self.nombres_estado(obj.estado.nombre);
            self.foto_perfil(obj.foto_publica);
            $('#modal_ver_mas').modal('show');
        }, path, null, function(){
            cerrarLoading();
        });

    }

    self.abrir_crear_novedad=function(obj){     
      self.nombres_persona(obj.persona.nombres + ' ' + obj.persona.apellidos);
      self.nombre_contratista(obj.contratista.nombre);
      self.estado_novedad_id(obj.estado.id==5 ? 7 : obj.estado.id);
      self.novedadVO.empleado_id(obj.id.toString());
      $('#modal_novedad').modal('show');
    }

    self.abrir_filtros=function(){
      $('#modal_filtros').modal('show');
    }

    self.abrir_empleado_apto=function(obj){
      self.empleado_actoVO.id(obj.id);      
      self.nombres_persona(obj.persona.nombres + ' ' + obj.persona.apellidos);
      self.nombre_contratista(obj.contratista.nombre);
      $('#modal_empleado_apto').modal('show');
    }
     //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);
        self.paginacion.cantidad_por_paginas(30);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }
           
    //exportar excel    
    self.exportar_excel=function(){
      // if (self.buscado_rapido()) {
      //   location.href=path_principal+"/seguridad-social/exportar-empleados/?dato=" + self.filtro();
      // }else{
        location.href=path_principal+"/seguridad-social/exportar-empleados/?contratista_id="+self.filtros.contratista_id()+'&estado_id='+self.filtros.estado_id()+'&dato='+self.filtro()
      // } 
    }

     // //limpiar el modelo 
     self.limpiar=function(){      
         
        self.empleadoVO.id(0);
        self.empleadoVO.persona_id('');
        self.empleadoVO.fecha_nacimiento('');
        self.empleadoVO.escolaridad_id('');
        self.empleadoVO.contratista_id('');
        self.empleadoVO.fecha_tsa('');
        
        self.empleadoVO.matricula_id('');
        self.empleadoVO.tipo_matricula_id('');
        
        self.empleadoVO.cargo_id('');
        self.empleadoVO.hoja_de_vida('');
        self.empleadoVO.apto(true);
        self.empleadoVO.observacion('');
        self.empleadoVO.foto('');
        self.empleadoVO.fecha_ingreso('');
        self.nombre_persona('');
        self.id_persona('');

        self.soporte_tsa('');
        self.soporte_matricula('');
        self.hoja_de_vida('');
        self.foto('');

        self.requiere_soporte_tsa(true);
        self.requiere_soporte_matricula(true);
        self.requiere_hoja_de_vida(true);

        $('#soporte_matricula, #soporte_tsa, #hoja_de_vida').fileinput('reset');
        $('#soporte_matricula, #soporte_tsa, #hoja_de_vida, #foto').val('');
        $('img.file-preview-image').attr('src', '../../static/images/default_avatar_male.jpg');
        $('div.file-footer-caption').html('');  

        self.empleadoVO.persona_id.isModified(false);
        self.empleadoVO.fecha_nacimiento.isModified(false);
        self.empleadoVO.escolaridad_id.isModified(false);
        self.empleadoVO.contratista_id.isModified(false);
        self.empleadoVO.fecha_tsa.isModified(false);
        self.empleadoVO.soporte_tsa.isModified(false);
        self.empleadoVO.matricula_id.isModified(false);
        self.empleadoVO.cargo_id.isModified(false);
        self.empleadoVO.hoja_de_vida.isModified(false);
        self.empleadoVO.fecha_ingreso.isModified(false);
        self.empleadoVO.tiene_licencia.isModified(false);
        self.empleadoVO.vencimiento_licencia.isModified(false);
              
     }

     self.limpiar_persona=function () {
         
        self.personaVO.id(0);
        self.personaVO.cedula('');
        self.personaVO.nombres('');
        self.personaVO.apellidos('');
        self.personaVO.direccion('');
        self.personaVO.correo('');

        self.personaVO.cedula.isModified(false);
        self.personaVO.nombres.isModified(false);
        self.personaVO.apellidos.isModified(false);
        self.personaVO.direccion.isModified(false);
                
     };
    
     self.limpiar_novedad=function(){
      self.novedadVO.id(0);
      self.novedadVO.fecha('');
      self.novedadVO.empleado_id('');
      self.novedadVO.estado_id('');
      self.novedadVO.descripcion('');   

      self.novedadVO.fecha.isModified(false);
      self.novedadVO.estado_id.isModified(false);

     } 

      self.guardar=function(){
        
         EmpleadoViewModel.errores_empleado.showAllMessages();

         if (self.empleadoVO.matricula_id()==2 && 
          (self.empleadoVO.soporte_matricula()=='' || self.empleadoVO.soporte_matricula()==null) &&
          (self.soporte_matricula()=='' || self.soporte_matricula()==null) && !self.requiere_soporte_matricula()) {
            $('#validacion_soporte_matricula').show();
            return;
        }else{
            $('#validacion_soporte_matricula').hide();
        }

        if (self.empleadoVO.matricula_id()==2 && self.empleadoVO.tipo_matricula_id()=='') {
          $('#validacion_tipo_matricula').show();
          return;
        }else{
          $('#validacion_tipo_matricula').hide();
        }

        if (self.empleadoVO.tiene_licencia()=='0') {
            self.empleadoVO.soporte_licencia('');
            self.empleadoVO.vencimiento_licencia('');
        }

        self.empleadoVO.observacion(self.empleadoVO.observacion() || '');
        
        if (EmpleadoViewModel.errores_empleado().length == 0) {//se activa las validaciones

        if (self.empleadoVO.matricula_id()!=2){
            self.empleadoVO.tipo_matricula_id('');
            self.empleadoVO.soporte_matricula('');
            $('#soporte_matricula').fileinput('reset');
        }
        if (self.empleadoVO.id()==0) {

             var parametros={                     
                   callback:function(datos, estado, mensaje){
                      if (estado=='ok') {
                             self.filtro("");                             
                             //self.consultar(self.paginacion.pagina_actual());
                             //$('#modal_acciones').modal('hide');
                             self.limpiar();

                      }                        
                      
                   },//funcion para recibir la respuesta 
                   url:self.url,
                   parametros:self.empleadoVO,
                   completado:function(){
                    cerrarLoading();
                   }                   
             };
                        
             RequestFormData(parametros);

        }else{
          
            var parametros={      
                   metodo:'PUT',    
                   alerta:false,            
                   callback:function(datos, estado, mensaje){
                      if (estado=='ok') {
                             self.filtro("");                                  
                             $.confirm({
                                title: 'Confirmación',
                                content: '<h4><i class="text-success fa fa-check-circle-o fa-2x"></i> ' + mensaje + '<h4>',
                                cancelButton: 'Cerrar',
                                confirmButton: false,
                                cancel:function(){
                                  window.location.href='../../empleados';
                                }                                 
                            }); 

                      } else{
                        mensajeError(mensaje, 'Error');
                      }                       
                      
                   },//funcion para recibir la respuesta 
                   url:self.url+self.empleadoVO.id()+'/',
                   parametros:self.empleadoVO,
                   completado:function(){
                    cerrarLoading();
                   }
             };
                        
             RequestFormData(parametros);

        }

        } else {
             EmpleadoViewModel.errores_empleado.showAllMessages();//mostramos las validacion
        }
      }

       self.guardar_persona=function(){

        if (EmpleadoViewModel.errores_persona().length == 0) {//se activa las validaciones
         var parametros={                     
               callback:function(datos, estado, mensaje){
                  if (estado=='ok') {                        
                      self.consultar(self.paginacion.pagina_actual());
                      self.nombre_persona(datos.nombres + ' ' + datos.apellidos);  
                      self.empleadoVO.persona_id(datos.id);
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
             EmpleadoViewModel.errores_persona.showAllMessages();//mostramos las validacion
        }
      }

      //registrar novedad
       self.guardar_novedad=function(){

        if (EmpleadoViewModel.errores_novedad().length == 0) {//se activa las validaciones

         var parametros={                     
               callback:function(datos, estado, mensaje){
                  if (estado=='ok') { 
                      $('#modal_novedad').modal('hide');
                      self.limpiar_novedad();
                      self.consultar(self.paginacion.pagina_actual());
                  }                        
                  
               },//funcion para recibir la respuesta 
               url:path_principal+'/api/Novedad/',
               parametros:ko.toJS(self.novedadVO),
               completado:function(){
                  cerrarLoading();
               }
         };
                    
         Request(parametros);

        } else {
             EmpleadoViewModel.errores_novedad.showAllMessages();//mostramos las validacion
        }
      }

       //registrar si el empleado es apto
       self.actualizar_empleado_apto=function(){

        if (EmpleadoViewModel.errores_aptos().length == 0) {//se activa las validaciones

         var parametros={                     
               callback:function(datos, estado, mensaje){
                  if (estado=='ok') { 
                      $('#modal_empleado_apto').modal('hide'); 
                      self.consultar(1);                    
                  }                        
                  
               },//funcion para recibir la respuesta 
               url:path_principal+'/seguridad-social/actualizar_empleado_acto/',
               parametros:ko.toJS(self.empleado_actoVO),
               completado:function(){
                 cerrarLoading();
               }
         };
                    
         Request(parametros);

        } else {
             EmpleadoViewModel.errores_aptos.showAllMessages();//mostramos las validacion
        }
      }

       //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) { 

            sessionStorage.setItem("dato_empleado", $('#txtBuscar').val() || '');
            sessionStorage.setItem("buscado_rapido", 'true');  
            sessionStorage.setItem("estado_id", self.filtros.estado_id() || '');
            sessionStorage.setItem("contratista_id", self.filtros.contratista_id() || '');           
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            // self.buscado_rapido(true);
            self.filtro($('#txtBuscar').val());
            path = self.url + '?lite2=1&format=json&page=' + pagina;
            parameter = {
                contratista_id:self.filtros.contratista_id(), 
                estado_id:self.filtros.estado_id(),
                dato: self.filtro()
            };
            RequestGet(function(datos, estado, mensage) {

                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {

                    self.mensaje('');
                    //self.listado(results);
                    self.listado(datos.data);

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos, pagina);
                cerrarLoading();
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter, undefined, false);
        }
    }

    self.consulta_enter = function(d, e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        // if (self.buscado_rapido()) {
            self.consultar(pagina);
          // }else{
            // self.consultar_por_filtros(pagina);
          // }       
    });

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

            cerrarLoading();
        }, path, parameter, undefined, false);
    }

    self.consultar_por_filtros=function(pagina){
      if (EmpleadoViewModel.errores_filtros().length==0) {   
            // self.buscado_rapido(false); 
                        
            sessionStorage.setItem("estado_id", self.filtros.estado_id() || '');
            sessionStorage.setItem("contratista_id", self.filtros.contratista_id() || '');
            sessionStorage.setItem("dato_empleado", self.filtro() || '');
            sessionStorage.setItem("buscado_rapido", 'false'); 

            self.filtro($('#txtBuscar').val());
            path =self.url + '?lite2=1&format=json&page='+pagina;
            parameter = {contratista_id:self.filtros.contratista_id(), 
                        estado_id:self.filtros.estado_id(), dato:self.filtro()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                  
                    self.mensaje('');
                    //self.listado(results);  
                    self.listado(datos.data);  
                    $('#modal_filtros').modal('hide');

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos, pagina);
                cerrarLoading();
            }, path, parameter, undefined, false);
        
      }else{
        EmpleadoViewModel.errores_filtros.showAllMessages();
      }      
    }

    self.eliminar = function() {}
 
    self.consultar_por_id = function (id) {
       
      // alert(obj.id)
       path =self.url+id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
            self.limpiar();
            self.titulo('Actualizar Empleado');
            
            self.id_empleado(datos.id);
            self.empleadoVO.id(datos.id);
            self.empleadoVO.persona_id(datos.persona.id);
            self.empleadoVO.fecha_nacimiento(datos.fecha_nacimiento);
            self.empleadoVO.escolaridad_id(datos.escolaridad!=null ? datos.escolaridad.id : '');
            self.empleadoVO.contratista_id(datos.contratista!=null ? datos.contratista.id : '');
            self.empleadoVO.fecha_tsa(datos.fecha_tsa || '');            
            self.empleadoVO.matricula_id(datos.matricula!=null ? datos.matricula.id : '');
            self.empleadoVO.tipo_matricula_id(datos.tipo_matricula!=null ? datos.tipo_matricula.id : '');             
            self.empleadoVO.cargo_id(datos.cargo!=null ? datos.cargo.id : ''); 
            //self.cargo_id(datos.cargo!=null ? datos.cargo.id : '');            
            self.empleadoVO.apto(datos.apto ? '1' : '0');
            self.empleadoVO.observacion(datos.observacion);             
            self.empleadoVO.fecha_ingreso(datos.fecha_ingreso);
            self.soporte_tsa(datos.soporte_tsa);
            self.soporte_matricula(datos.soporte_matricula);
            self.hoja_de_vida(datos.hoja_de_vida);
            self.foto(datos.foto);
            self.nombre_persona(datos.persona.nombres + ' ' + datos.persona.apellidos);
            self.id_persona(datos.id_persona);
            self.empleadoVO.tiene_licencia(datos.tiene_licencia==true ? '1' : '0');
            self.empleadoVO.vencimiento_licencia(datos.vencimiento_licencia);
            self.soporte_licencia(datos.soporte_licencia);
            self.contratista_id(datos.contratista!=null ? datos.contratista.id : '');
             
             $('#modal_acciones').modal('show');
             cerrarLoading();
         }, path, {}, undefined, false);

     }
     
     self.consultar_cargos=function(){        
                   
        path =path_principal + '/api/CargosSeguridadSocial/?sin_paginacion=&format=json';
        parameter = {};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) { 
                self.listado_cargos(datos);                      
            } else {
                self.listado_cargos([]);                    
            }

        }, path, parameter,function(){             
          self.empleadoVO.cargo_id(self.cargo_id());
          cerrarLoading();               
        });        
          
    }

    self.abrir_buscar_persona=function(){
        $('#modal_buscar_persona').modal('show');
    }

    self.abrir_crear_persona = function() {
        $('#modal_crear_persona').modal('show');
    }

    self.seleccionar_persona = function() {

        var conteo = 0;
        ko.utils.arrayForEach(self.listado_persona(), function(p) {
            if (p.id == self.id_persona()) {
                self.nombre_persona(p.nombres + ' ' + p.apellidos);
                conteo++;
                return;
            }
        });
        if (conteo == 0) {
            return false;
        }
        self.empleadoVO.persona_id(self.id_persona());
        $('#modal_buscar_persona').modal('hide');

    }

    self.empleadoVO.cargo_id.subscribe(function(val){

      if (val>0) {
          var data=self.listado_cargos();
          for (var i = 0; i < data.length; i++) {
             if (val==data[i].id){
              self.requiere_soporte_tsa(data[i].soporte_tsa);
              self.requiere_soporte_matricula(data[i].soporte_matricula);
              self.requiere_hoja_de_vida(data[i].hoja_de_vida);             
              break;
             }        
          }  
      }

    });

    self.limpiarFiltros=function(){
      self.filtros.estado_id('');
      self.filtros.contratista_id('');
    }

    self.ver_soporte = function(id, tipo) {
      window.open(path_principal+"/seguridad-social/ver-soporte/?id="+ id + '&tipo=' + tipo, "_blank");
    }


}

var empleado = new EmpleadoViewModel();
// empleado.consultar(1); //iniciamos la primera funcion
empleado.filtros.contratista_id(sessionStorage.getItem("contratista_id"));
empleado.filtros.estado_id(sessionStorage.getItem("estado_id"));
empleado.filtros.criterio(sessionStorage.getItem("criterio"));    
$('#txtBuscar').val(sessionStorage.getItem("dato_empleado"));
empleado.buscado_rapido(sessionStorage.getItem("buscado_rapido")=='true');

EmpleadoViewModel.errores_empleado = ko.validation.group(empleado.empleadoVO);
EmpleadoViewModel.errores_persona = ko.validation.group(empleado.personaVO);
EmpleadoViewModel.errores_novedad = ko.validation.group(empleado.novedadVO);
EmpleadoViewModel.errores_filtros = ko.validation.group(empleado.filtros);
EmpleadoViewModel.errores_aptos = ko.validation.group(empleado.empleado_actoVO);
ko.applyBindings(empleado);