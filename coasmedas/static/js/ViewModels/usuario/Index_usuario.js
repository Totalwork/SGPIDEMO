
function UsuarioViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);    
    self.habilitar_campos=ko.observable(true);
    self.url=path_principal+'api/usuario'; 

    self.showRow=ko.observable(false);
    self.showBusqueda=ko.observable(true);
    self.showclave=ko.observable(true);
     //Representa un modelo de la tabla persona
    self.usuarioVO={
        id:ko.observable(0),
        persona:{},
        iniciales:ko.observable(''),
        persona_id:ko.observable(0),
        user_id:ko.observable(0),
        empresa_id:ko.observable(0),
        foto:ko.observable(''),
        iniciales:ko.observable(''),
        nombre_persona:ko.observable('').extend({ required: { message: '(*)Seleccione una persona' } }),
        usuario:ko.observable('').extend({ required: { message: '(*)Digite el usuario de la persona' } }),
        clave:ko.observable('').extend({ required: { message: '(*)Digite la clave de la persona' } })
    }

    self.busqueda_persona=ko.observable('');
    self.listado_persona=ko.observableArray([]);

    self.personaVO={
        id:ko.observable(0),
        cedula:ko.observable('').extend({ required: { message: '(*)Digite la cédula de la persona' } }),
        nombres:ko.observable('').extend({ required: { message: '(*)Digite el nombre de la persona' } }),
        telefono:ko.observable(0),
        apellidos:ko.observable('').extend({ required: { message: '(*)Digite el apellidos de la persona' } }),
        direccion:ko.observable('').extend({ required: { message: '(*)Digite la dirección de la persona' } }),
        correo:ko.observable('').extend({
            required: { message: '(*)Digite el correo de la persona' }
         }).extend({ email: { message: '(*)Ingrese un correo valido' } })
     };



     self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(5),
        directiones: ko.observable(true),
        limite: ko.observable(true),
        cantidad_por_paginas: ko.observable(0),
        totalRegistrosBuscados:ko.observable(0),
        text: {
            first: ko.observable('Inicio'),
            last: ko.observable('Fin'),
            back: ko.observable('<'),
            forward: ko.observable('>')
        }
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Usuario');
        self.habilitar_campos(true);
        self.showclave(true);
        $('#modal_acciones').modal('show');
    }

    self.abrir_modal_clave = function (obj) {
        self.limpiar();
        self.usuarioVO.id(obj.id);
        self.titulo('Registrar Nueva Clave');
        $('#modal_clave').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }


    self.guardar_clave=function(){

            if(self.usuarioVO.clave()!=''){

                 var parametros={                     
                          callback:function(datos, estado, mensaje){
                             if (estado=='ok') {
                                    $('#modal_clave').modal('hide');
                                    self.limpiar();

                             }                        
                             
                          },//funcion para recibir la respuesta 
                          url:path_principal+'/usuario/cambiar_clave_usuario/',
                          parametros:{'password':self.usuarioVO.clave(),'usuario_id':self.usuarioVO.id()}                       
                    };
                    
                    Request(parametros);

            }else{
                mensajeError('Llenar el campo de nueva clave','Nueva Clave');
            }

    }

  
   
    // //limpiar el modelo 
     self.limpiar=function(){   

            self.usuarioVO.id(0);
            self.usuarioVO.clave('');
            self.usuarioVO.nombre_persona('');
            self.usuarioVO.persona_id(0);
            self.usuarioVO.usuario('');
            self.listado_persona([]);
            self.busqueda_persona('');
            self.limpiar_persona();   
            self.usuarioVO.persona={}; 
     }


     self.limpiar_persona=function(){

        self.personaVO.id(0);
        self.personaVO.nombres('');
        self.personaVO.apellidos('');
        self.personaVO.direccion('');
        self.personaVO.correo('');
        self.personaVO.cedula('');
     }


     self.seleccionar_persona=function(obj){

        self.usuarioVO.persona_id(obj.id);
        self.usuarioVO.nombre_persona(obj.nombres+" "+obj.apellidos);
        return true;
    }

    // //funcion guardar
     // //funcion guardar
     self.guardar=function(){

            if(self.usuarioVO.persona_id()==0 && self.showRow()==true){
                 if (UsuarioViewModel.errores_persona().length > 0) {               
                     UsuarioViewModel.errores_persona.showAllMessages();//mostramos las validacion
                }
            }else{                

                if (UsuarioViewModel.errores_persona_id().length > 0) {               
                    UsuarioViewModel.errores_persona_id.showAllMessages();//mostramos las validacion
                }

            }


            self.usuarioVO.persona=self.personaVO;

            if(self.usuarioVO.id()==0){


                    var parametros={                     
                          callback:function(datos, estado, mensaje){
                             if (estado=='ok') {
                                    self.filtro("");
                                    self.consultar(self.paginacion.pagina_actual());
                                    $('#modal_acciones').modal('hide');
                                    self.limpiar();

                             }                        
                             
                          },//funcion para recibir la respuesta 
                          url:path_principal+'/api/usuario/',//url api
                          parametros:self.usuarioVO                       
                    };
                    
                    RequestFormData(parametros);

                }else{

                    var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/usuario/'+self.usuarioVO.id()+'/',
                       parametros:self.usuarioVO                        
                  };

                  RequestFormData(parametros);
               }
       
 
     }


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/usuario?format=json&page='+pagina;
            parameter = { dato: self.filtro(), pagina: pagina};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));  

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
        }


    }

    self.agregar_persona=function(valor){

        self.showRow(valor);
        self.showBusqueda(!valor);
        if(self.showRow()==false){
            self.limpiar_persona();
        }
        self.usuarioVO.persona_id(0);
        self.busqueda_persona('');
        self.usuarioVO.nombre_persona('');
        self.listado_persona([]);


    }


     //consultar persona
    self.consulta_enter_persona = function (d,e) {
        if (e.which == 13) {
            self.usuarioVO.persona_id(0);
            self.usuarioVO.nombre_persona('');
            self.busqueda_persona($('#persona').val());
            self.consultar_persona();
        }
        return true;
    }

     self.consultar_persona=function(){

        if(self.busqueda_persona()!=''){


            ruta =path_principal+'/api/persona/?sin_paginacion&dato='+self.busqueda_persona()+'&format=json';
            parameter='';

             RequestGet(function (results,count) {

                if(self.listado().length>0){
                    var lista=[];
                    ko.utils.arrayForEach(results, function(d) {
                        var sw=0;
                        ko.utils.arrayForEach(self.listado(), function(x) {
                            
                            if(d['id']==x.persona.id){
                               sw=1;
                            }
                        });

                        if(sw==0){
                             lista.push(d);
                        }

                    });
                    self.listado_persona(agregarOpcionesObservable(lista));
                     

                }else{
                    self.listado_persona(agregarOpcionesObservable(results)); 
                    
                }
                 $('.panel-scroller').scroller("reset");

             }, ruta, parameter); 

          

        }else{
            self.listado_persona([]);
        }
    }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/usuario/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Usuario');

             self.usuarioVO.id(results.id); 
             self.usuarioVO.persona_id(results.persona.id); 
             self.usuarioVO.user_id(results.user.id); 
             self.usuarioVO.nombre_persona(results.persona.nombres+" "+results.persona.apellidos); 
             self.usuarioVO.usuario(results.user.username);
             self.usuarioVO.empresa_id(results.empresa.id);
             self.usuarioVO.iniciales(results.iniciales);


             self.personaVO.cedula(results.persona.cedula);
             self.personaVO.nombres(results.persona.nombres);
             self.personaVO.telefono(results.persona.telefono);
             self.personaVO.apellidos(results.persona.apellidos);
             self.personaVO.direccion('');
             self.personaVO.correo(results.persona.correo);

            self.habilitar_campos(true);
            self.showRow(false);
            self.showBusqueda(true);
            self.showclave(false);
            $('#modal_acciones').modal('show');
         }, path, parameter);

     }



     self.consultar_por_id_detalle = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/usuario/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Usuario');

             self.usuarioVO.id(results.id); 
             self.usuarioVO.persona_id(results.persona.id); 
             self.usuarioVO.nombre_persona(results.persona.nombres+" "+results.persona.apellidos); 
             self.usuarioVO.usuario(results.user.username);
             self.usuarioVO.empresa_id(results.empresa.id);
             self.habilitar_campos(false);
             self.showclave(false);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }

   
    
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un usuario para desactivar/activar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/usuario/eliminar_varios_usuarios/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea desactivar los usuarios seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

 }

var usuario = new UsuarioViewModel();
UsuarioViewModel.errores_usuario = ko.validation.group(usuario.usuarioVO);
UsuarioViewModel.errores_persona = ko.validation.group(usuario.personaVO);
UsuarioViewModel.errores_persona_id = ko.validation.group(usuario.usuarioVO.nombre_persona);
usuario.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(usuario,content);
ko.applyBindings(usuario,header);