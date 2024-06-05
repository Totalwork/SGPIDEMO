function UsuarioViewModel() {

    var self=this;
    self.url=path_principal+'/api/usuario/'; 
    self.foto=ko.observable();
    self.listado_opciones=ko.observableArray([]);
    self.listado_opciones_usuario=ko.observableArray([]);
    self.mensaje_opciones=ko.observable('');
    self.mensaje_opciones_usuario=ko.observable('');
    self.seleccionar_opcion=ko.observable(false);
    self.seleccionar_opcion_usuario=ko.observable(false);    
    self.mensaje_notificaciones=ko.observable('');
    self.oldpassword=ko.observable('');
    self.newpassword=ko.observable('');
    self.newpasswordconfirmation=ko.observable('');

    self.usuarioVO={
        id:ko.observable(''),
        user_id:ko.observable(''),
        persona_id:ko.observable(''),
        foto:ko.observable(''),
        foto_publica: ko.observable(''),
        empresa_id:ko.observable(''),
        iniciales:ko.observable(''),
        persona:{
            id:ko.observable(0),            
            cedula:ko.observable('').extend({ required: { message: '(*)Ingrese la cédula de la persona' } }),
            nombres:ko.observable('').extend({ required: { message: '(*)Ingrese el nombre de la persona' } }),
            apellidos:ko.observable('').extend({ required: { message: '(*)Ingrese el apellidos de la persona' } }),
            telefono:ko.observable(''),//.extend({ required: { message: '(*)Ingrese la dirección de la persona' } }),
            correo:ko.observable('').extend({required: { message: '(*)Ingrese el correo de la persona' }}).extend({ email: { message: '(*)Ingrese un correo valido' } })
        },
        notificaciones:ko.observableArray([])
    };

    self.consultar_por_id=function(id){

        path =self.url+id+'/?format=json';
        RequestGet(function (datos, estado, mensage) {
                       
                self.usuarioVO.id(datos.id);
                self.usuarioVO.user_id(datos.user.id);
                self.usuarioVO.persona_id(datos.persona.id);                
                self.foto(datos.foto_publica);

                self.usuarioVO.empresa_id(datos.empresa.id);
                self.usuarioVO.foto_publica(datos.foto_publica);
                self.usuarioVO.iniciales(datos.iniciales);
                self.usuarioVO.persona.id(datos.persona.id);
                self.usuarioVO.persona.cedula(datos.persona.cedula);
                self.usuarioVO.persona.nombres(datos.persona.nombres);
                self.usuarioVO.persona.apellidos(datos.persona.apellidos);
                self.usuarioVO.persona.telefono(datos.persona.telefono);
                self.usuarioVO.persona.correo(datos.persona.correo);    
           
        }, path, {}, function(){
                    cerrarLoading();
                   });

    }

    self.guardar=function(){
        if (UsuarioViewModel.errores().length==0) {

            var formData= new FormData();

            formData.append('id',self.usuarioVO.id());
            formData.append('user_id',self.usuarioVO.user_id());
            formData.append('persona_id',self.usuarioVO.persona_id());
            formData.append('foto',self.usuarioVO.foto());
            formData.append('empresa_id',self.usuarioVO.empresa_id());
            formData.append('iniciales',self.usuarioVO.iniciales());

            formData.append('persona.id',self.usuarioVO.persona.id());
            formData.append('persona.cedula',self.usuarioVO.persona.cedula());
            formData.append('persona.nombres',self.usuarioVO.persona.nombres());
            formData.append('persona.apellidos',self.usuarioVO.persona.apellidos());
            formData.append('persona.telefono',self.usuarioVO.persona.telefono());
            formData.append('persona.correo',self.usuarioVO.persona.correo());
            var notificaciones=[];
            ko.utils.arrayForEach(self.usuarioVO.notificaciones(),function(p){
                if (p.procesar()) {
                    notificaciones.push(p.id());
                }
            });

            formData.append('notificaciones',ko.toJSON(notificaciones));

            var parametros={   
                  metodo:'PUT',                
                  callback:function(datos, estado, mensaje){
                     if (estado=='ok') {
                        self.consultar_por_id(self.usuarioVO.id());
                     }
                  },//funcion para recibir la respuesta 
                  url:self.url+ self.usuarioVO.id() + '/',
                  parametros:formData,
                   completado:function(){
                    cerrarLoading();
                   }
            };
                   
            RequestFormData2(parametros);
        }else {
            UsuarioViewModel.errores.showAllMessages();//mostramos las validacion
        }
    }

    self.cambiarContraseña=function(){
        if (UsuarioViewModel.errores().length==0) {

            if (self.newpasswordconfirmation()!=self.newpassword()) {
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Las contraseñas no coinciden.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });

            }else {

                
                var parametros={   
                      metodo:'POST',     
                      alerta:false,           
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {
                            // self.consultar_por_id(self.usuarioVO.id());
                            $.confirm({
                                title: 'Confirmación',
                                content: '<h4><i class="text-success fa fa-check-circle-o fa-2x"></i> ' + mensaje + '<h4>',
                                cancelButton: 'Cerrar',
                                confirmButton: false,
                                cancel: function() {
                                    window.location.href='/usuario/login/';
                                }
                            });
                         }else{
                            mensajeError(mensaje)
                         }
                      },//funcion para recibir la respuesta 
                      // url:self.url+ self.usuarioVO.id() + '/',
                      url:'/usuario/cambiar_clave/',
                      parametros:{'password':self.oldpassword(), 'passwordnew':self.newpassword()},
                       completado:function(){
                        cerrarLoading();
                       }
                };
                       
                Request(parametros);

            }

        }else {
            UsuarioViewModel.errores.showAllMessages();//mostramos las validacion
        }
    }    

     self.consultar_opciones=function(){

        path =path_principal+'/usuario/obtener_opciones/';
        RequestGet(function (datos, estado, mensage) {
            
            if (estado=='ok' && datos != null && datos.length > 0) {   
                self.mensaje_opciones('');
                self.listado_opciones(agregarOpcionesObservable(datos));
            }else{
                self.mensaje_opciones(mensajeNoFound);
                self.listado_opciones([]);
            }
           
        }, path, {dato:$('#txtBuscarE').val()}, function(){
                    cerrarLoading();
                   });

    }

    self.consultar_opciones_usuario=function(){

        path =path_principal+'/usuario/obtener_opciones_usuario/';
        RequestGet(function (datos, estado, mensage) {
             
            if (estado=='ok' && datos != null && datos.length > 0) {   
                self.mensaje_opciones_usuario('')           ;
                self.listado_opciones_usuario(agregarOpcionesObservable(datos));
            }else{
                self.mensaje_opciones_usuario(mensageNoFound('No tiene accesos directos configurados'));
                self.listado_opciones_usuario([]);
            }
           
        }, path, {dato:$('#txtBuscarEE').val()}, function(){
                    cerrarLoading();
                   });

    }

    self.seleccionar_opcion.subscribe(function(val){

         ko.utils.arrayForEach(self.listado_opciones(), function(p){          
            p.procesar(val);
        });

    });

    self.seleccionar_opcion_usuario.subscribe(function(val){

         ko.utils.arrayForEach(self.listado_opciones_usuario(), function(p){          
            p.procesar(val);
        });

    });

    self.guardar_opciones_usuario=function(){

        var lista=[];

        ko.utils.arrayForEach(self.listado_opciones(),function(p){
            if (p.procesar()) {
                lista.push(p.id);
            }
        });

        if (lista.length==0) { return false; }

        var parametros={           
              callback:function(datos, estado, mensaje){
                 if (estado=='ok') {  
                    self.mensaje_opciones_usuario('');              
                    self.consultar_opciones();
                    self.consultar_opciones_usuario();
                 }
              },//funcion para recibir la respuesta 
              url:path_principal+'/usuario/guardar_opciones_usuario/',
              parametros:ko.toJS({lista_opciones:lista}),
               completado:function(){
                    cerrarLoading();
                   }
        };
               
        Request(parametros);

    }

    self.eliminar_opciones_usuario=function(){

        var lista=[];

        ko.utils.arrayForEach(self.listado_opciones_usuario(),function(p){
            if (p.procesar()) {
                lista.push(p.id_opcion_usuario);
            }
        });

        if (lista.length==0) { return false; }

        var parametros={           
              callback:function(datos, estado, mensaje){
                 if (estado=='ok') {                
                    self.consultar_opciones();
                    self.consultar_opciones_usuario();
                 }
              },//funcion para recibir la respuesta 
              url:path_principal+'/usuario/eliminar_opciones_usuario/',
              parametros:ko.toJS({lista:lista}),
               completado:function(){
                    cerrarLoading();
                   }
        };
               
        Request(parametros);

    }


    self.obtener_notificaciones_autogestionables=function(){

        path =path_principal+'/usuario/obtener_notificaciones_autogestionables/';
        RequestGet(function (datos, estado, mensage) {
           
            if (estado=='ok' && datos != null && datos.length > 0) {   
               self.mensaje_notificaciones('');
               self.usuarioVO.notificaciones(convertToObservableArray(datos));
            }else{
                self.mensaje_notificaciones(mensageNoFound(mensage));
                self.usuarioVO.notificaciones([]);
            }
           
        }, path, {}, function(){
                    cerrarLoading();
                   });

    }    
    

 }   


var usuario = new UsuarioViewModel();
UsuarioViewModel.errores = ko.validation.group(usuario.usuarioVO);
ko.applyBindings(usuario);