
function AdministrarUUCCViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.lista_tipo_select=ko.observableArray([]);
    self.lista_solicita=ko.observableArray([]);
    self.lista_empresa=ko.observableArray([]);
    self.lista_usuario_aprueba=ko.observableArray([]);
    self.empresa_select=ko.observable('');
    self.usuario_revisa_select=ko.observable('');
    self.mcontrato=ko.observable('');


     //Representa un modelo de administrar uucc cambio
    self.AdministrarUUCCVO={
        id:ko.observable(0),
        proyecto_id:ko.observable(0),
        tipo_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo' } }),
        usuario_id:ko.observable(0),
        usuario_revisa_id:ko.observable('').extend({ required: { message: '(*)Seleccione el usuario que aprueba' } }),
        solicita_id:ko.observable('').extend({ required: { message: '(*)Seleccione el solicitante' } }),
        fecha:ko.observable(''),
        numero_cambio:ko.observable(0),
        motivo:ko.observable(''),
        

     };

     //paginacion de administrar uucc cambio
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

    //paginacion
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });


    //funcion para abrir modal de administrar uucc cambio
    self.abrir_modal = function () {
        self.limpiar();
        self.consultar_empresa();
        self.titulo('Control de cambios');
        $('#modal_acciones').modal('show');
    }


      //consultar las empresas para llenar un select
    self.consultar_empresa=function(){
        
         path =path_principal+'/api/empresa/?sin_paginacion';
         parameter={esContratante:true};
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_empresa(datos);

         }, path, parameter,undefined,false,false);

    }

    //funcion que se ejecuta cuando se cambia en el select de contrato 
    self.empresa_select.subscribe(function (value) {
        if(value>0){
            self.consultar_usuario_aprueba(value);

        }else{

            self.lista_usuario_aprueba([]);

        }
    });


       //consultar usuario aprueba para llenar un select
    self.consultar_usuario_aprueba=function(empresa){
        
         path =path_principal+'/api/usuario/?sin_paginacion';
         parameter={empresa_id:empresa};
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_usuario_aprueba(datos);

         }, path, parameter,function(){

          self.AdministrarUUCCVO.usuario_revisa_id(self.usuario_revisa_select());


         });

    }


     //limpiar el modelo de administrar uucc cambio
     self.limpiar=function(){     
         
        self.AdministrarUUCCVO.id(0);
        //self.AdministrarUUCCVO.proyecto_id(0);
        self.AdministrarUUCCVO.tipo_id('');
        self.AdministrarUUCCVO.usuario_id(0);
        self.AdministrarUUCCVO.usuario_revisa_id('');
        self.AdministrarUUCCVO.solicita_id('');
        self.AdministrarUUCCVO.fecha('');
        self.AdministrarUUCCVO.numero_cambio(0);
        self.AdministrarUUCCVO.motivo('');
        self.empresa_select('');

        self.AdministrarUUCCVO.tipo_id.isModified(false);
        self.AdministrarUUCCVO.usuario_revisa_id.isModified(false);
        self.AdministrarUUCCVO.solicita_id.isModified(false);

        
     }


    //funcion guardar y actualizar de administrar uucc cambio
     self.guardar=function(){


        if (AdministrarUUCCViewModel.errores_administrar().length == 0) {//se activa las validaciones

            if(self.AdministrarUUCCVO.id()==0){

                var parametros={
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
                                  window.location.href='../../agregar_uucc/'+self.AdministrarUUCCVO.proyecto_id()+'/'+datos.id+'/'+self.mcontrato();
                                }                                 
                            }); 

                        } else{
                            mensajeError(mensaje, 'Error');
                        }       

                        // if (estado=='ok') {
                        //     self.filtro("");
                        //     self.limpiar();
                        //     self.consultar(self.paginacion.pagina_actual());
                        //     $('#modal_acciones').modal('hide');
                        // }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Cambio/',//url api
                     parametros:self.AdministrarUUCCVO                        
                };
                Request(parametros);
            }else{              

                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.limpiar();
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Cambio/'+self.AdministrarUUCCVO.id()+'/',
                       parametros:self.AdministrarUUCCVO                        
                  };

                  Request(parametros);

            }

        } else {
             AdministrarUUCCViewModel.errores_administrar.showAllMessages();//mostramos las validacion
        } 
     }


    //funcion consultar de administrar uucc cambio
    self.consultar = function (pagina) {

        if (pagina > 0) {            

            self.filtro($('#txtBuscar').val());

            path = path_principal+'/api/Cambio/?format=json';
            parameter = { dato: self.filtro(), page: pagina,proyecto:self.AdministrarUUCCVO.proyecto_id()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)
                    cerrarLoading();

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter,undefined, false);
        }
    }


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    //consultar por id  de administrar uucc cambio
    self.consultar_por_id = function (obj) {        
       
        path =path_principal+'/api/Cambio/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar control de cambio');

            self.AdministrarUUCCVO.id(datos.id);
            self.AdministrarUUCCVO.proyecto_id(datos.proyecto.id);
            self.AdministrarUUCCVO.tipo_id(datos.tipo.id);
            self.AdministrarUUCCVO.usuario_id(datos.usuario.id);
            self.AdministrarUUCCVO.usuario_revisa_id(datos.usuario_revisa.id);
            self.AdministrarUUCCVO.solicita_id(datos.solicita.id);
            self.AdministrarUUCCVO.fecha(datos.fecha);
            self.AdministrarUUCCVO.numero_cambio(datos.numero_cambio);
            self.AdministrarUUCCVO.motivo(datos.motivo);
            //self.AdministrarUUCCVO.solicitud_enviada(datos.solicitud_enviada);

            self.empresa_select(datos.usuario_revisa.empresa.id);
            self.usuario_revisa_select(datos.usuario_revisa.id);
            
            $('#modal_acciones').modal('show');

         }, path, parameter);

     }


     //eliminar de administrar uucc cambio
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los cambios para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/control_cambios/eliminar_cambio_uucc/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los cambios seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }
}

var administrar_uucc = new AdministrarUUCCViewModel();
AdministrarUUCCViewModel.errores_administrar= ko.validation.group(administrar_uucc.AdministrarUUCCVO);
ko.applyBindings(administrar_uucc);
