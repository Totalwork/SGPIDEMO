
function AgregarCambioUUCCViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.listado_soporte=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.mensaje2=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.checkall_soporte=ko.observable(false); 
    self.proyecto_id=ko.observable('');
    self.lista_uucc=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.archivo=ko.observable('');
    self.mcontrato=ko.observable('');
    self.usuario_revisa_id=ko.observable('');

     //Representa un modelo de agregar cambio
    self.AgregarCambioUUCCVO={
        id:ko.observable(0),
        uucc_id:ko.observable('').extend({ required: { message: '(*)Seleccione la UUCCC' } }),
        cambio_id:ko.observable(0),
        comentario:ko.observable(''),
        cantidad:ko.observable(0).extend({ required: { message: '(*)Digite la cantidad' } }),
        estado_id:ko.observable(0),

     };


     //Representa un modelo de soporte cambio
    self.SoporteVO={
        id:ko.observable(0),
        cambio_id:ko.observable(''),     
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre' } }),
        ruta:ko.observable(''),

     };


     //paginacion de agregar cambio
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


    //funcion para seleccionar los soportes a eliminar
    self.checkall_soporte.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado_soporte(), function(d) {

            d.eliminado(value);
        }); 
    });


    //funcion para abrir modal de agregar cambio
    self.abrir_modal = function () {
        self.limpiar();
        self.uucc_proyecto();
        self.titulo('Control de cambios');
        $('#modal_acciones').modal('show');
    }


        //funcion para abrir modal de agregar cambio
    self.abrir_guarda_todo = function () {
        self.titulo('Guardar cambios');
        $('#modal_guardar_todo').modal('show');
    }


    //funcion para abrir modal de carga masiva
    self.carga_masiva = function () {
        self.titulo('Carga masiva');
        $('#modal_carga_masiva').modal('show');
    }

    //consultar la lista de uucc segun proyecto
    self.uucc_proyecto=function(){

         path =path_principal+'/api/Unidad_contructiva/';
         parameter={ mcontrato: self.mcontrato()};
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_uucc(datos.data);

         }, path, parameter,undefined,false,false);

    }


     //limpiar el modelo de agregar cambio
     self.limpiar=function(){     
         
        self.AgregarCambioUUCCVO.id(0);
        self.AgregarCambioUUCCVO.cantidad(0);
        self.AgregarCambioUUCCVO.comentario('');
        self.AgregarCambioUUCCVO.estado_id(0);

        self.AgregarCambioUUCCVO.uucc_id.isModified(false);
        self.AgregarCambioUUCCVO.cantidad.isModified(false);

     }

          //limpiar el modelo de agregar cambio
     self.limpiar_archivo=function(){     
         
        self.SoporteVO.id(0);
        self.SoporteVO.cambio_id(0);
        self.SoporteVO.nombre('');
        self.SoporteVO.ruta('');

        self.SoporteVO.nombre.isModified(false);

        $('#archivo2').fileinput('reset');
        $('#archivo2').val('');
     }


    //funcion guardar y actualizar de agregar cambio
     self.guardar=function(){


        if (AgregarCambioUUCCViewModel.errores_agregar().length == 0) {//se activa las validaciones

            if(self.AgregarCambioUUCCVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Cambio_proyecto/',//url api
                     parametros:self.AgregarCambioUUCCVO                        
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
                       url:path_principal+'/api/Cambio_proyecto/'+self.AgregarCambioUUCCVO.id()+'/',
                       parametros:self.AgregarCambioUUCCVO                        
                  };

                  Request(parametros);

            }

        } else {
             AgregarCambioUUCCViewModel.errores_agregar.showAllMessages();//mostramos las validacion
        } 
     }


    //funcion consultar de agregar cambio
    self.consultar = function (pagina) {

        if (pagina > 0) {            

            self.filtro($('#txtBuscar').val());

            path = path_principal+'/api/Cambio_proyecto/?format=json';
            parameter = { dato: self.filtro(), page: pagina, cambio_id:self.AgregarCambioUUCCVO.cambio_id()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(convertToObservableArray(agregarOpcionesObservable(datos.data)));  
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


    //consultar por id  de agregar cambio
    self.consultar_por_id = function (obj) {        
       
        path =path_principal+'/api/Cambio_proyecto/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar control de cambio');

            self.AgregarCambioUUCCVO.id(datos.id);
            self.AgregarCambioUUCCVO.uucc_id(datos.uucc.id);
            self.AgregarCambioUUCCVO.cambio_id(datos.cambio.id);
            self.AgregarCambioUUCCVO.comentario(datos.comentario);
            self.AgregarCambioUUCCVO.cantidad(datos.cantidad);
            self.AgregarCambioUUCCVO.estado_id(datos.estado.id);


            $('#modal_acciones').modal('show');

         }, path, parameter);

     }


     //eliminar de agregar cambio
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las UUCC para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/control_cambios/eliminar_cambio_proyecto/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las UUCC seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }        
    }


    //guardar la cantidad en cambio proyecto
    self.guardar_cantidad=function(obj){            

        var parametros={                     
            callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                    self.filtro("");
                    self.consultar(self.paginacion.pagina_actual());
                }                      
                        
            },//funcion para recibir la respuesta 
            url:path_principal+'/control_cambios/actualizar_cantidad/',//url api
            parametros:{id:obj.id(),cantidad:obj.cantidad()}
        };

        Request(parametros); 

     }

    //Actualiza todo
    self.guardar_todo = function (envio_correo) {

        var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {

                lista_id.push({
                        id:d.id,
                        cantidad:d.cantidad
                   })
         });


        var parametros={     
             metodo:'POST',                
            callback:function(datos, estado, mensaje){

                if (estado=='ok') {

                    self.consultar(self.paginacion.pagina_actual());
                    $('#modal_guardar_todo').modal('hide');  
                }  

            },//funcion para recibir la respuesta 
            url:path_principal+'/control_cambios/actualizar_todo_agregar_uucc/',
           parametros:{lista:lista_id, envio_correo:envio_correo, usuario_revisa:self.usuario_revisa_id(),proyecto_id:self.proyecto_id() }                       
        };

        Request(parametros);         
    }


 //funcion consultar soportes de los cambios
    self.consultar_soportes = function () {         

        path = path_principal+'/api/Soporte_cambio/?format=json';
        parameter = { dato: '',cambio_id:self.AgregarCambioUUCCVO.cambio_id()};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje2('');
                self.listado_soporte(convertToObservableArray(agregarOpcionesObservable(datos.data)));  
                cerrarLoading();

            } else {
                self.listado_soporte([]);
                self.mensaje2(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                cerrarLoading();
            }

        }, path, parameter,undefined, false);
    }


    //funcion guardar soprotes de la vista agregar uucc cambio
    self.guardar_soporte=function(){
        var data = new FormData();

        if (self.SoporteVO.ruta()=='' || self.SoporteVO.nombre()=='') {

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe digitar el nombre del documento y cargar el soporte.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false
        }

        data.append('cambio_id',self.AgregarCambioUUCCVO.cambio_id());
        data.append('nombre_documento',self.SoporteVO.nombre());
        data.append('archivo', self.SoporteVO.ruta());

        var parametros={                     
            callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                    self.limpiar_archivo();
                    self.consultar_soportes();
                }                        
                            
            },//funcion para recibir la respuesta 
                url:path_principal+'/control_cambios/cargar_soporte_uucc/',//url api
                parametros:data,
                completado:function(){}                          
            };
        RequestFormData2(parametros);
    }


    //eliminar soporte de uucc cambio
    self.eliminar_soporte = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_soporte(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los soportes para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/control_cambios/eliminar_soporte_uucc/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los soportes seleccionados?", path, parameter, function () {
                 self.consultar_soportes();
                 self.checkall_soporte(false);
             })

         }        
    }


    //funcion para carga masiva
    self.carga_excel=function(){

        var data = new FormData();
         data.append('cambio_id',self.AgregarCambioUUCCVO.cambio_id());
         data.append('proyecto_id',self.proyecto_id());
         data.append('contrato_id',self.mcontrato());
         data.append('archivo',self.archivo());

        var parametros={                     
            callback:function(datos, estado, mensaje){

                self.consultar(1);
                $('#modal_carga_masiva').modal('hide');                    
                        
            },//funcion para recibir la respuesta 
            url:path_principal+'/control_cambios/carga_masiva_cambio/',//url api
            parametros:data                        
        };
        RequestFormData2(parametros);
    }  

}

var agregar_cambio = new AgregarCambioUUCCViewModel();
AgregarCambioUUCCViewModel.errores_agregar= ko.validation.group(agregar_cambio.AgregarCambioUUCCVO);
ko.applyBindings(agregar_cambio);
