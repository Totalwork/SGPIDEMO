
function FuncionarioViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.habilitar_campos=ko.observable(true);

    self.showRow=ko.observable(false);
    self.showBusqueda=ko.observable(true);
    self.notificaciones=ko.observableArray([]);

    self.url=path_principal+'api/empresa'; 
    self.mensaje_notificaciones=ko.observable('');
    self.seleccionar_notificaciones = ko.observable(false);
     //Representa un modelo de la tabla persona
    self.personaVO={
        id:ko.observable(0),
        cedula:ko.observable('').extend({ required: { message: '(*)Digite la cédula de la persona' } }),
        nombres:ko.observable('').extend({ required: { message: '(*)Digite el nombre de la persona' } }),
        apellidos:ko.observable('').extend({ required: { message: '(*)Digite el apellidos de la persona' } }),
        direccion:ko.observable('').extend({ required: { message: '(*)Digite la dirección de la persona' } }),
        correo:ko.observable('').extend({
            required: { message: '(*)Digite el correo de la persona' }
         }).extend({ email: { message: '(*)Ingrese un correo valido' } })
     };

    self.funcionarioVO={
        id:ko.observable(0),
        persona:{},
        iniciales:ko.observable(''),
        persona_id:ko.observable(0),
        cargo_id:ko.observable(0).extend({ required: { message: '(*)Seleccione un cargo' } }),
        nombre_persona:ko.observable('').extend({ required: { message: '(*)Seleccione una persona' } }),
        notificaciones:ko.observableArray([]),
        activo: ko.observable(true)
    }

    self.busqueda_persona=ko.observable('');
    self.listado_persona=ko.observableArray([]);

    self.listado_cargo=ko.observableArray([]);


     self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
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
        self.habilitar_campos(true);
        self.titulo('Registrar Funcionario');
        self.showRow(false);
        self.showBusqueda(true);
        $('#modal_acciones').modal('show');
    }

    
    
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    //exportar excel
    
    self.exportar_excel=function(){

        location.href=path_principal+"/parametrizacion/export_funcionario?dato="+self.filtro();
    }
   
    // //limpiar el modelo 
     self.limpiar=function(){        
         
            self.funcionarioVO.iniciales('');
            self.funcionarioVO.persona_id(0);
            self.funcionarioVO.cargo_id('');
            self.funcionarioVO.nombre_persona('');
            self.funcionarioVO.activo(false);
            self.listado_persona([]);
            self.busqueda_persona('');
            self.limpiar_persona();   
            self.funcionarioVO.persona={};    
     }

     self.limpiar_persona=function(){

        self.personaVO.id(0);
        self.personaVO.nombres('');
        self.personaVO.apellidos('');
        self.personaVO.direccion('');
        self.personaVO.correo('');
        self.personaVO.cedula('');
     }

        
    // //funcion guardar
     self.guardar=function(){

            if(self.funcionarioVO.persona_id()==0 && self.showRow()==true){
                 if (FuncionarioViewModel.errores_persona().length > 0) {               
                     FuncionarioViewModel.errores_persona.showAllMessages();//mostramos las validacion
                }
            }else{                

                if (FuncionarioViewModel.errores_persona_id().length > 0) {               
                    FuncionarioViewModel.errores_persona_id.showAllMessages();//mostramos las validacion
                }

            }

            var lista=[];

            ko.utils.arrayForEach(self.notificaciones(),function(p){
                if (p.procesar()) {
                    lista.push(p.id);
                }
            });
            self.funcionarioVO.notificaciones(lista);
           // alert(self.funcionarioVO.iniciales())
            if (FuncionarioViewModel.errores_cargo()==0) {

                if(self.funcionarioVO.persona_id()==0){
                    self.funcionarioVO.persona=self.personaVO;
                }

                if(self.funcionarioVO.id()==0){

                    var parametros={                     
                          callback:function(datos, estado, mensaje){
                             if (estado=='ok') {
                                    self.filtro("");
                                    self.consultar(self.paginacion.pagina_actual());
                                    $('#modal_acciones').modal('hide');
                                    self.limpiar();

                             }                        
                             
                          },//funcion para recibir la respuesta 
                          url:path_principal+'/api/Funcionario/',//url api
                          parametros:ko.toJS(self.funcionarioVO)                        
                    };
                    
                    Request(parametros);

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
                       url:path_principal+'/api/Funcionario/'+self.funcionarioVO.id()+'/',
                       parametros:ko.toJS(self.funcionarioVO)                       
                  };

                  Request(parametros);
               }

            }else{
                
                 FuncionarioViewModel.errores_iniciales.showAllMessages();// no sirve
                 FuncionarioViewModel.errores_cargo.showAllMessages();
            }
       
 
     }

     self.agregar_persona=function(valor){

        self.showRow(valor);
        self.showBusqueda(!valor);
        if(self.showRow()==false){
            self.limpiar_persona();
        }
        self.funcionarioVO.persona_id(0);
        self.busqueda_persona('');
        self.funcionarioVO.nombre_persona('');
        self.listado_persona([]);


    }



    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/Funcionario?format=json&page='+pagina;
            parameter = { dato: self.filtro(), pagina: pagina };
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

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    //consultar persona
    self.consulta_enter_persona = function (d,e) {
        if (e.which == 13) {
            self.funcionarioVO.persona_id(0);
            self.funcionarioVO.nombre_persona('');
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



    self.seleccionar_persona=function(obj){

        self.funcionarioVO.persona_id(obj.id);
        self.funcionarioVO.nombre_persona(obj.nombres+" "+obj.apellidos);
        self.consultar_notificacion(obj.id);
        return true;
    }

  
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/Funcionario/'+obj.id+'/?format=json';
       parameter='';
         RequestGet(function (results,count) {
           
            self.titulo('Actualizar Funcionario');

            self.funcionarioVO.id(results.id); 
            self.funcionarioVO.persona_id(results.persona.id); 
            self.funcionarioVO.nombre_persona(results.persona.nombres+" "+results.persona.apellidos); 
            self.funcionarioVO.iniciales(results.iniciales);
            self.funcionarioVO.cargo_id(results.cargo.id);
            self.funcionarioVO.activo(results.activo);  
            self.funcionarioVO.notificaciones(agregarOpcionesObservable(results.notificaciones));      

            self.habilitar_campos(true);
            self.showRow(false);
            self.showBusqueda(true);
            $('#modal_acciones').modal('show');
         }, path, parameter, function(){
            self.consultar_notificacion(self.funcionarioVO.persona_id());
         });

     }

     self.consultar_notificacion = function (persona_id) {
      
       path =path_principal+'/parametrizacion/obtener_notificaciones_por_persona/';
       parameter={'persona_id': persona_id};
       RequestGet(function (datos, estado, mensage) {

            if (estado=='ok') {
                self.notificaciones(agregarOpcionesObservable(datos));   

                if (self.funcionarioVO.notificaciones()!=null && self.funcionarioVO.notificaciones().length>0) {
                    ko.utils.arrayForEach(self.funcionarioVO.notificaciones(),function(notificacion_id){
                        ko.utils.arrayForEach(self.notificaciones(),function(p){
                           if (notificacion_id==p.id) {
                                p.procesar(true);
                           }
                        });
                    });
                }
            }else{
                self.notificaciones([]);
                self.mensaje_notificaciones(mensageNoFound(mensage));
            }
            

       }, path, parameter);

     }

    

     self.consultar_por_id_detalle = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/Funcionario/'+obj.id+'/?format=json';
       parameter='';
         RequestGet(function (results,count) {
           
             self.titulo('Funcionario');

             self.funcionarioVO.id(results.id); 
             self.funcionarioVO.persona_id(results.persona.id); 
             self.funcionarioVO.nombre_persona(results.persona.nombres+" "+results.persona.apellidos); 
             self.funcionarioVO.iniciales(results.iniciales);
             self.funcionarioVO.cargo_id(results.cargo.id); 
             self.habilitar_campos(false);
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un funcionario para la desactivación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/parametrizacion/eliminar_id_funcionario/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea desactivar los funcionarios seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

    self.seleccionar_notificaciones.subscribe(function(val){

         ko.utils.arrayForEach(self.notificaciones(),function(p){              
            p.procesar(val);               
        });

    });

    

 }

var funcionario = new FuncionarioViewModel();
FuncionarioViewModel.errores_persona = ko.validation.group(funcionario.personaVO);
FuncionarioViewModel.errores_persona_id = ko.validation.group(funcionario.funcionarioVO.nombre_persona);
FuncionarioViewModel.errores_iniciales = ko.validation.group(funcionario.funcionarioVO.iniciales);
FuncionarioViewModel.errores_cargo = ko.validation.group(funcionario.funcionarioVO.cargo_id);
funcionario.consultar(1);//iniciamos la primera funcion
// funcionario.consultar_notificacion();
ko.applyBindings(funcionario);
