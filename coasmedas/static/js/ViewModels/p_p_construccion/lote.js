
function LoteViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.listado_estructura=ko.observableArray([]);
    self.listado_soporte=ko.observableArray([]);
    self.listado_soporte_foto=ko.observableArray([]);     
    self.mensaje=ko.observable('');
    self.mensaje_estructura=ko.observable('');
    self.mensaje_soporte=ko.observable('');
    self.mensaje_soporte_foto=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.checkall2=ko.observable(false);
    self.checkall3=ko.observable(false);
    self.checkall4=ko.observable(false);


     //Representa el modelo de lote
    self.loteVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del lote' } }),
        direccion:ko.observable('').extend({ required: { message: '(*)Digite la direccion del lote' } }),
        cantidad_estructura:ko.observable(0).extend({ required: { message: '(*)Digite la cantidad de estructuras' } }),
        proyecto_id:ko.observable(0),

     };

    //Representa el modelo de estructura
    self.estructuraVO={
        id:ko.observable(0),
        codigo:ko.observable('').extend({ required: { message: '(*)Digite el codigo de la estructura' } }),
        lote_id:ko.observable(0),

     };


    //Representa el modelo de soporte
    self.soporteVO={
        id:ko.observable(0),
        nombre:ko.observable(''),
        soporte:ko.observable(''),
        proyecto_id:ko.observable(0),
        tipo_id:ko.observable(0),

     };


     //paginacion de lote
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


    //funcion para seleccionar los datos a eliminar estructuras
    self.checkall2.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado_estructura(), function(d) {

            d.eliminado(value);
        }); 
    });


            //funcion para seleccionar los datos a eliminar
    self.checkall3.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado_soporte(), function(d) {

            d.eliminado(value);
        }); 
    });


    //funcion para seleccionar los datos a eliminar
    self.checkall4.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado_soporte_foto(), function(d) {

            d.eliminado(value);
        }); 
    });



    //funcion para abrir modal de lote
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Lote');
        $('#modal_acciones').modal('show');
    }


    //funcion para abrir modal de las estructuras
    self.abrir_modal_estructuras = function (obj) {

        self.estructuraVO.lote_id(obj.id);
        self.limpiar_estructura();
        self.titulo('Registrar Estructura');
        $('#modal_estructuras').modal('show');
    }


    //funcion para abrir modal de ver las estructuras
    self.abrir_modal_ver_estructuras = function (obj) {

        self.consultar_estructura(obj.id);
        self.titulo('Listado Estructura');
        $('#modal_ver_estructuras').modal('show');
    }


        //funcion para abrir modal para las actas
    self.abrir_modal_ver_actas = function () {

        // alert()
        self.consultar_soporte(94);
        self.titulo('Acta de reunion');
        $('#modal_abrir_acta').modal('show');
    }


    //funcion para abrir modal para las fotos
    self.abrir_modal_ver_fotos = function () {

        // alert()
        self.consultar_soporte(95);
        self.titulo('Administrar fotos');
        $('#modal_ver_foto').modal('show');
    }


     //limpiar el modelo del lote 
     self.limpiar=function(){     
         
        self.loteVO.id(0);
        self.loteVO.nombre('');
        self.loteVO.direccion('');
        self.loteVO.cantidad_estructura(0);
   
     }

    //limpiar el modelo de la estructura 
     self.limpiar_estructura=function(){     
         
        self.estructuraVO.id(0);
        self.estructuraVO.codigo('');
     }


    //limpiar el modelo del soporte 
     self.limpiar_soporte=function(){     
         
        self.soporteVO.id(0);
        self.soporteVO.nombre('');
        self.soporteVO.tipo_id(0);
        self.soporteVO.soporte('');

        $('#archivo2').fileinput('reset');
        $('#archivo2').val(''); 

        $('#archivo').fileinput('reset');
        $('#archivo').val(''); 
   
     }



    //funcion guardar y actualizar los lote
     self.guardar=function(){

        if (LoteViewModel.errores_lote().length == 0) {//se activa las validaciones


            if (self.loteVO.cantidad_estructura()==0){

                $.confirm({
                      title:'Informativo',
                      content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>La cantidad de estructuras debe ser mayor a 0.<h4>',
                      cancelButton: 'Cerrar',
                      confirmButton: false
                });

                return false
            }


            if(self.loteVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Lote/',//url api
                     parametros:self.loteVO                        
                };
                Request(parametros);
            }else{              

                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.limpiar();
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Lote/'+self.loteVO.id()+'/',
                       parametros:self.loteVO                        
                  };

                  Request(parametros);

            }

        } else {
             LoteViewModel.errores_lote.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar los lote
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            

            self.filtro($('#txtBuscar').val());

            path = path_principal+'/api/Lote?format=json';
            parameter = { dato: self.filtro(), page: pagina, proyecto_id:self.loteVO.proyecto_id()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data));
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


    //consultar por id de los lote
    self.consultar_por_id = function (obj) {
       
       path =path_principal+'/api/Lote/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar Lote');

            self.loteVO.id(datos.id);
            self.loteVO.nombre(datos.nombre);
            self.loteVO.direccion(datos.direccion);
            self.loteVO.cantidad_estructura(datos.cantidad_estructura);
             
             $('#modal_acciones').modal('show');

         }, path, parameter);

     }

   
    //eliminar los lote
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los lote para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/p_p_construccion/eliminar_lote/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los lote seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
         
    }


        //exportar excel la tabla lote
    self.exportar_excel=function(){


         location.href=path_principal+"/lote/exportar/?proyecto_id="+self.loteVO.proyecto_id();
    }



    //funcion guardar y actualizar la estructura
     self.guardar_codigo=function(){

        if ( LoteViewModel.errores_estructura().length == 0) {//se activa las validaciones

            if(self.estructuraVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar_estructura();
                            self.consultar();
                            $('#modal_estructuras').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Estructura/',//url api
                     parametros:self.estructuraVO                        
                };
                Request(parametros);
            }else{              

                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.limpiar_estructura();
                          self.consultar();
                          $('#modal_estructuras').modal('hide');
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Estructura/'+self.estructuraVO.id()+'/',
                       parametros:self.estructuraVO                        
                  };

                  Request(parametros);

            }

        } else {
             LoteViewModel.errores_estructura.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar las estructuras
    self.consultar_estructura = function (lote_id) {

        path = path_principal+'/api/Estructura?format=json';
        parameter = {lote_id:lote_id};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje_estructura('');
                self.listado_estructura(agregarOpcionesObservable(datos.data));
                cerrarLoading();  

            } else {
                self.listado_estructura([]);
                self.mensaje_estructura(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                cerrarLoading();
            }

        }, path, parameter,undefined, false);
    }



    //eliminar las estructuras
    self.eliminar_estructura = function () {

         var lista_id2=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_estructura(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id2.push({
                        id:d.id
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las estructuras para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/p_p_construccion/eliminar_estrucura/';
             var parameter = { lista: lista_id2 };
             RequestAnularOEliminar("Esta seguro que desea eliminar las estructuras seleccionadas?", path, parameter, 
                function (datos, estado, mensage) {
                    
                    if (estado=='ok') {
                     $.confirm({
                        title:'Confirmación',
                        content: '<h4><i class="text-success fa fa-check-circle-o fa-2x"></i> ' + mensage + '<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false,
                        cancel:function(){
                            $('#modal_ver_estructuras').modal('hide');
                            self.checkall(false);
                        }
                        
                    });
                  
                 }else{
                    mensajeError(mensage);
                 }

             }, undefined, false)

         }     
         
    }


         //funcion guardar los soportes
     self.guardar_soporte=function(){
        var data = new FormData();

        if (LoteViewModel.errores_soporte().length == 0) {//se activa las validaciones

            if ($('#archivo2').val()=='' || self.soporteVO.nombre()=='') {

                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe digitar el nombre del documento y cargar el soporte.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
                return false
            }


            var tipo=94;
            var proyecto=self.loteVO.proyecto_id();
            var nombre=self.soporteVO.nombre();

            data.append('proyecto_id',proyecto);
            data.append('nombre',nombre);
            data.append('tipo_id',tipo);

            for (var i = 0; i <  $('#archivo2')[0].files.length; i++) {
                data.append('archivo[]', $('#archivo2')[0].files[i]); 
             };

            var parametros={                     
                callback:function(datos, estado, mensaje){

                    if (estado=='ok') {
                        self.filtro("");
                        self.limpiar_soporte();
                        self.consultar_soporte(94);
                        $('#modal_acciones').modal('hide');
                    }                        
                        
                },//funcion para recibir la respuesta 
                url:path_principal+'/api/SoporteReunion/',//url api
                parametros:data                        
            };
            RequestFormData2(parametros);

        } else {
             LoteViewModel.errores_soporte.showAllMessages();//mostramos las validacion
        }  
    }


         //funcion consultar los soportes
    self.consultar_soporte = function (tipo) {

        var proyecto=self.loteVO.proyecto_id();

        path = path_principal+'/api/SoporteReunion?format=json&sin_paginacion=1';
        parameter = {proyecto_id:proyecto,tipo:tipo};
        RequestGet(function (datos, estado, mensage) {


            if (estado == 'ok' && datos!=null && datos.length > 0) {

                if (tipo==94){
                    self.mensaje_soporte('');
                    self.listado_soporte(agregarOpcionesObservable(datos));

                }else{

                    self.mensaje_soporte_foto('');
                    self.listado_soporte_foto(agregarOpcionesObservable(datos));  
                }
                cerrarLoading();  

            } else {

                if (tipo==94){
                    self.listado_soporte([]);
                    self.mensaje_soporte(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js

                }else{
                  
                    self.mensaje_soporte_foto(mensajeNoFound);
                    self.listado_soporte_foto([]);
                }
                cerrarLoading();
            }

        }, path, parameter,undefined, false);
    }



         //funcion guardar los soportes fotos
    self.guardar_soporte_foto=function(){
        var data = new FormData();

        if (LoteViewModel.errores_soporte().length == 0) {//se activa las validaciones

            if ($('#archivo').val()=='') {

                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe cargar las fotos.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
                return false
            }

            var tipo=95;
            var proyecto=self.loteVO.proyecto_id();
            var nombre=self.soporteVO.nombre();

            data.append('proyecto_id',proyecto);
            data.append('tipo_id',tipo);

            for (var i = 0; i <  $('#archivo')[0].files.length; i++) {
                data.append('archivo[]', $('#archivo')[0].files[i]); 
             };

            var parametros={                     
                callback:function(datos, estado, mensaje){

                    if (estado=='ok') {
                        self.filtro("");
                        self.limpiar_soporte();
                        self.consultar_soporte(95);
                        $('#modal_acciones').modal('hide');
                    }                        
                        
                },//funcion para recibir la respuesta 
                url:path_principal+'/api/SoporteReunion/',//url api
                parametros:data                        
            };
            RequestFormData2(parametros);

        } else {
             LoteViewModel.errores_soporte.showAllMessages();//mostramos las validacion
        } 
     }


         //eliminar los documentos
    self.eliminar_documento = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los documentos para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/p_p_construccion/eliminar_documento/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los documentos seleccionados?", path, parameter, function () {
                 self.consultar_soporte(94);
                 self.checkall3(false);
             })

        }     
         
    }



    //eliminar las fotos
    self.eliminar_fotos = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_soporte_foto(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las fotos para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/p_p_construccion/eliminar_documento/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las fotos seleccionadas?", path, parameter, function () {
                 self.consultar_soporte(95);
                 self.checkall4(false);
             })

        }     
         
    }

}

var lote = new LoteViewModel();
LoteViewModel.errores_lote = ko.validation.group(lote.loteVO);
LoteViewModel.errores_estructura = ko.validation.group(lote.estructuraVO);
LoteViewModel.errores_soporte = ko.validation.group(lote.soporteVO);
ko.applyBindings(lote);
