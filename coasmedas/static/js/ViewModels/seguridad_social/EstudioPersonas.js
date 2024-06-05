function EstudioPersonasViewModel() {
	var self=this;

	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
  self.checkall=ko.observable(false);
  self.listado_persona=ko.observableArray([]);
  self.listado_requermientos=ko.observableArray([]);
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
  self.cedula_persona=ko.observable('');
  self.apellidos_persona=ko.observable('');
  self.buscado_rapido=ko.observable(false);

  /*parametros de busqueda*/
    self.filtros={
      dato:ko.observable(''),
      apto:ko.observable(false),
      estudio_personas:true
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
    	escolaridad_id:ko.observable(''),
    	contratista_id:ko.observable(''),    	    	
    	fecha_tsa:ko.observable(''),
    	soporte_tsa:ko.observable(''),               
    	matricula_id:ko.observable(''),
    	tipo_matricula_id:ko.observable(''),
    	soporte_matricula:ko.observable(''),
    	cargo_id:ko.observable(''),
    	hoja_de_vida:ko.observable(''),        
    	apto:ko.observable(true),
    	observacion:ko.observable(''),
    	foto:ko.observable(''), 
      estado_id:ko.observable(''),
      fecha_ingreso: ko.observable(''),
    };

    self.novedadVO={
      id:ko.observable(0),
      fecha:ko.observable('').extend({ required: { message: '(*) Ingrese la fecha de la novedad' } }),
      empleado_id:ko.observable(''),
      estado_id:ko.observable('').extend({ required: { message: '(*) Seleccione el estado' } }),
      descripcion:ko.observable(''),
    };

    self.empleado_actoVO={
      id:ko.observable(0),
      apto:ko.observable('').extend({ required: { message: '(*) Seleccione si el empleado esta apto.' } }),
      observacion:ko.observable('').extend({ required: { message: '(*) Ingrese una observacion para continuar.' } })
    };

    function validar_soporte(val) {
       if (self.id_empleado()>0) {
            return true;
       }else if(self.id_empleado()==0 && (val=='' || val==null)){
            return false;
       }else if(self.id_empleado()==0 && val!='' && val!=null){
            return true;
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
        },
        totalRegistrosBuscados:ko.observable(0)
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.consultar_requerimientos(0);
        self.titulo('Registrar Estudio de Empleado');
        $('#modal_acciones').modal('show');
    }

     self.abrir_modal_ver_mas = function (obj) {
        
        path =self.url+obj.id+'/?format=json';
        RequestGet(function (datos, estado, mensage) {  
           
            self.obj_empleado(datos);
            self.nombre_persona(datos.persona.nombres + ' ' + datos.persona.apellidos);      
            self.cedula_persona(datos.persona.cedula);     
            $('#modal_ver_mas').modal('show');
        }, path, null, function(){
                    cerrarLoading();
                   });

    }

    self.abrir_crear_novedad=function(obj){     
      self.nombres_persona(obj.persona.nombres + ' ' + obj.persona.apellidos);
      self.nombre_contratista(obj.contratista.nombre);
      self.novedadVO.empleado_id(obj.id.toString());
      $('#modal_novedad').modal('show');
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
      self.paginacion.cantidad_por_paginas(resultadosPorPagina);
      var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
      self.paginacion.totalRegistrosBuscados(buscados);
    }

    self.abrir_filtros=function(){
      $('#modal_filtros').modal('show');
    }

    //exportar excel    
    self.exportar_excel=function(){
      if (self.buscado_rapido()) {
        location.href=path_principal+"/seguridad-social/exportar-empleados/?estudio_personas=true&dato=" + self.filtro();
      }else{
        location.href=path_principal+"/seguridad-social/exportar-empleados/?estudio_personas=true&apto="+self.filtros.apto()+'&dato='+self.filtros.dato()        
      } 
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

            $('#soporte_matricula, #soporte_tsa, #hoja_de_vida').fileinput('reset');
            $('#soporte_matricula, #soporte_tsa, #hoja_de_vida, #foto').val('');
            $('img.file-preview-image').attr('src', '../../static/images/default_avatar_male.jpg');
            $('div.file-footer-caption').html('');    

            self.empleadoVO.fecha_nacimiento.isModified(false);              
     }

     self.limpiar_persona=function () {
         
        self.personaVO.id(0);
        self.personaVO.cedula('');
        self.personaVO.nombres('');
        self.personaVO.apellidos('');
        self.personaVO.direccion('');
        self.personaVO.correo('');

        self.personaVO.id.isModified(false);
        self.personaVO.cedula.isModified(false);
        self.personaVO.nombres.isModified(false);
        self.personaVO.apellidos.isModified(false);        

     };
    
     self.limpiar_novedad=function(){
      self.novedadVO.id(0);
      self.novedadVO.fecha('');
      self.novedadVO.empleado_id('');
      self.novedadVO.estado_id('');
      self.novedadVO.descripcion('');    

      self.novedadVO.estado_id.isModified(false);
      self.novedadVO.fecha.isModified(false);
      
     } 

      self.guardar=function(){
        
        
        if (EstudioPersonasViewModel.errores_empleado().length == 0) {//se activa las validaciones

        if (self.empleadoVO.id()==0) {

             var formData= new FormData();

             formData.append('foto', self.empleadoVO.foto());
             formData.append('persona_id', self.empleadoVO.persona_id());
             formData.append('fecha_nacimiento', self.empleadoVO.fecha_nacimiento());
             formData.append('apto', self.empleadoVO.apto());
             formData.append('observacion', self.empleadoVO.observacion());
             var lista=[];
             ko.utils.arrayForEach(self.listado_requermientos(),function(p){                
                if (p.requerimiento_valor_id()>0) {                   
                    lista.push({requerimiento_id:p.requerimiento_id(),requerimiento_valor_id:p.requerimiento_valor_id()});
                }
             });

             formData.append('lista',ko.toJSON(lista));
             
             var parametros={                     
                   callback:function(datos, estado, mensaje){
                      if (estado=='ok') {
                             self.filtro("");
                             self.consultar(self.paginacion.pagina_actual());
                             $('#modal_acciones').modal('hide');
                             self.limpiar();

                      }                        
                      
                   },//funcion para recibir la respuesta 
                   url:path_principal+'/seguridad-social/guardar_estudio_personas/',
                   parametros:formData,
                    completado:function(){
                    cerrarLoading();
                   }                  
             };
                        
             RequestFormData2(parametros);

        }else{
            
            var formData= new FormData();

             formData.append('id', self.empleadoVO.id());             
             formData.append('foto', self.empleadoVO.foto());
             formData.append('persona_id', self.empleadoVO.persona_id());
             formData.append('fecha_nacimiento', self.empleadoVO.fecha_nacimiento());
             formData.append('apto', self.empleadoVO.apto());
             formData.append('observacion', self.empleadoVO.observacion());
             var lista=[];
             ko.utils.arrayForEach(self.listado_requermientos(),function(p){                
                if (p.requerimiento_valor_id()>0) {                   
                    lista.push({requerimiento_id:p.requerimiento_id(),requerimiento_valor_id:p.requerimiento_valor_id()});
                }
             });

             formData.append('lista',ko.toJSON(lista));

            var parametros={ 
                   callback:function(datos, estado, mensaje){
                      if (estado=='ok') {                             
                        self.consultar(self.paginacion.pagina_actual());
                        $('#modal_acciones').modal('hide');
                        self.limpiar();
                      }                        
                      
                   },//funcion para recibir la respuesta 
                   url:path_principal+'/seguridad-social/actualizar_estudio_personas/',
                   parametros:formData,
                    completado:function(){
                    cerrarLoading();
                   }
             };
                        
             RequestFormData2(parametros);

        }

        } else {
             EstudioPersonasViewModel.errores_empleado.showAllMessages();//mostramos las validacion
        }
      }

       self.guardar_persona=function(){

        if (EstudioPersonasViewModel.errores_persona().length == 0) {//se activa las validaciones
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
             EstudioPersonasViewModel.errores_persona.showAllMessages();//mostramos las validacion
        }
      }

      //registrar novedad
       self.guardar_novedad=function(){

        if (EstudioPersonasViewModel.errores_novedad().length == 0) {//se activa las validaciones

         var parametros={                     
               callback:function(datos, estado, mensaje){
                  if (estado=='ok') { 
                      $('#modal_novedad').modal('hide');
                      self.limpiar_novedad();
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
             EstudioPersonasViewModel.errores_novedad.showAllMessages();//mostramos las validacion
        }
      }

       //registrar si el empleado es apto
       self.actualizar_empleado_apto=function(){

        if (EstudioPersonasViewModel.errores_aptos().length == 0) {//se activa las validaciones

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
             EstudioPersonasViewModel.errores_aptos.showAllMessages();//mostramos las validacion
        }
      }

       //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.buscado_rapido(true);
            self.filtro($('#txtBuscar').val());
            path =self.url + '?lite2=1&format=json&page='+pagina;
            parameter = { dato: self.filtro(),estudio_personas:true};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                	
                    self.mensaje('');
                    //self.listado(results);  
                    self.listado(datos.data);  

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                
            }, path, parameter, function(){
                    cerrarLoading();
                   });
        }
    }

    self.consultar_por_filtros=function(pagina){
       
        path =self.url + '?format=json&page='+pagina;
        parameter = self.filtros;
        RequestGet(function (datos, estado, mensage) {

           if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
             
               self.mensaje('');               
               self.listado(datos.data);  
               $('#modal_filtros').modal('hide');

           } else {
               self.listado([]);
               self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
           }

           self.llenar_paginacion(datos,pagina);
              
        }, path, parameter, function(){
                    cerrarLoading();
                   });
        
         
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }

     self.consultar_requerimientos = function (empleado_id) {
          
        self.buscado_rapido(true);
        self.filtro($('#txtBuscar').val());
        path =path_principal + '/seguridad-social/consultar_requerimientos_empleado/'
        parameter = { empleado_id:empleado_id };
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {                                 
                self.listado_requermientos(convertToObservableArray(datos));                
            } else {
                self.listado_requermientos([]);                    
            }
            
        }, path, parameter, function(){
                    cerrarLoading();
                   });      
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        if (self.buscado_rapido()) {
            self.consultar(pagina);
          }else{
            self.consultar_por_filtros(pagina);
          }       
    });

    //consultar persona
    self.consulta_enter_persona = function (d,e) {
        if (e.which == 13) {           
            self.consultar_persona();
        }
        return true;
    }

    self.consultar_persona = function () {
       
            path =path_principal + '/api/persona/?format=json&sin_paginacion=';
            parameter = { dato: self.filtro_persona()};
            RequestGet(function (datos, estado, mensage) {

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
 
    
    self.eliminar = function () {}

    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =self.url+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
             self.titulo('Actualizar Empleado');
            
            self.id_empleado(datos.id);
            self.empleadoVO.id(datos.id);
            self.empleadoVO.persona_id(datos.persona.id);
            self.empleadoVO.fecha_nacimiento(datos.fecha_nacimiento);
            
            self.empleadoVO.apto(datos.apto==true ? '1' : '0');
            self.empleadoVO.observacion(datos.observacion);             
            self.empleadoVO.fecha_ingreso(datos.fecha_ingreso);
            
            self.foto(datos.foto);
            self.nombre_persona(datos.persona.nombres + ' ' + datos.persona.apellidos);
            self.id_persona(datos.id_persona);
            
            self.consultar_requerimientos(datos.id);

            $('#modal_acciones').modal('show');
         }, path, parameter, function(){
                    cerrarLoading();
                   });

     }
     
    self.abrir_buscar_persona=function(){
        $('#modal_buscar_persona').modal('show');
    }

     self.abrir_crear_persona=function(){
        $('#modal_crear_persona').modal('show');
    }

    self.seleccionar_persona=function() {

        var conteo=0;
        ko.utils.arrayForEach(self.listado_persona(), function (p) {            
            if (p.id==self.id_persona()) {
                 self.nombre_persona(p.nombres + ' ' + p.apellidos);  
                 conteo++;
                return;
            }
        });
        if (conteo==0) {
            return false;
        }
        self.empleadoVO.persona_id(self.id_persona()); 
        $('#modal_buscar_persona').modal('hide');
       
    }
}

var estudio = new EstudioPersonasViewModel();
EstudioPersonasViewModel.errores_empleado = ko.validation.group(estudio.empleadoVO);
EstudioPersonasViewModel.errores_persona = ko.validation.group(estudio.personaVO);
EstudioPersonasViewModel.errores_filtros = ko.validation.group(estudio.filtros);
EstudioPersonasViewModel.errores_aptos = ko.validation.group(estudio.empleado_actoVO);
estudio.consultar(1);//iniciamos la primera funcion
ko.applyBindings(estudio);