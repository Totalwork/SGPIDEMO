

function FotosProyectoViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.lista_carpeta_foto = ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.lista_tipo_select=ko.observableArray([]);
    self.desde_filtro=ko.observable('');
    self.hasta_filtro=ko.observable('');
    self.tipo_foto=ko.observable(0);
    self.asociado=ko.observable(2);

    self.archivo1=ko.observable('');
    self.valida_foto=ko.observable(0);
    self.asociar=ko.observable('');
    self.comentario=ko.observable('');


    //var num=0;
    //self.url=path_principal+'api/empresa'; 

     //Representa un modelo de las fotos del proyecto
    self.fotosProyectoVO={
        id:ko.observable(0),
        fecha:ko.observable('').extend({ required: { message: '(*)Seleccione la fecha' } }),
        ruta:ko.observable('').extend({ required: { message: '(*)Seleccione el archivo' } }),
        comentarios:ko.observable(''),
        asociado_reporte:ko.observable(0),
        proyecto_id:ko.observable(0),
        tipo_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de fotos' } }),

     };

     //paginacion de la fotos del proyecto
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

    //paginacion
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

  
    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });

    //funcion para abrir modal de registrar fotos del proyecto
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Fotos');
        $('#modal_acciones').modal('show');
    }

    //funcion para abri el mnodal de actualizar fecha
    self.actualizaFecha = function () {
        self.titulo('Actualizar fecha');
        self.limpiar();
        $('#modalActualizarFecha').modal('show');
    }


    //funcion para guardar seleccion
    self.asociar_fotos_reporte = function () {
        self.titulo('Asociar y Desasociar');
        $('#modalGuardarSeleccion').modal('show');
    }

        //funcion para filtrar las fotos
    self.filtrar_fotos = function () {
        self.titulo('Filtrar Fotos');
        $('#modal_filtro_fotos').modal('show');
    }


        //funcion para ver los comentarios de la foto
    self.ver_comentario = function (obj) {
        self.titulo('Comentario');
        self.Vercomentario(obj);
        $('#vercomentario').modal('show');
    }

     //limpiar el modelo de la fotos del proyecto
     self.limpiar=function(){     
         
        self.fotosProyectoVO.id(0);
        self.fotosProyectoVO.fecha('');
        self.fotosProyectoVO.ruta('');
        self.fotosProyectoVO.comentarios('');  
        self.fotosProyectoVO.asociado_reporte(0);
        self.fotosProyectoVO.tipo_id('');

        self.fotosProyectoVO.fecha.isModified(false);
        self.fotosProyectoVO.comentarios.isModified(false);
        self.fotosProyectoVO.tipo_id.isModified(false);
        self.fotosProyectoVO.ruta.isModified(false);

        $('#archivo').fileinput('reset');
        $('#archivo').val('');
      
     }


    //funcion para exportar a excel las fotos del proyecto
    self.exportar_excel = function (obj) {
        //self.titulo('Generar informe');
        //$('#generar_informe').modal('show');
    }


    //consultar los tipos para llenar un select
    self.consultar_lista_tipo=function(){
        
         path =path_principal+'/api/Tipos?ignorePagination';
         parameter={ dato: 'administradorFotos' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_tipo_select(datos);

         }, path, parameter,undefined,false,false);

    }


        //consultar los encabezado del giro
    self.carpeta_foto=function(){

         path =path_principal+'/administrador_fotos/carpetas/';
         parameter={ proyecto_id: self.fotosProyectoVO.proyecto_id()};
         RequestGet(function (datos, estado, mensaje) {

            if(datos.length>0){

                self.lista_carpeta_foto(datos);
            }

         }, path, parameter); 

    }


    //funcion guardar las fotos del proyecto
     self.guardar=function(){
        var data = new FormData();

        if (FotosProyectoViewModel.errores().length == 0) {//se activa las validaciones

            var proyecto=self.fotosProyectoVO.proyecto_id();
            var fecha=self.fotosProyectoVO.fecha();
            var comentarios=self.fotosProyectoVO.comentarios();
            var tipo=self.fotosProyectoVO.tipo_id();
            var asociado_reporte=self.fotosProyectoVO.asociado_reporte();

            data.append('proyecto_id',proyecto);
            data.append('fecha',fecha);
            data.append('comentarios',comentarios);
            data.append('tipo_id',tipo);

            for (var i = 0; i <  $('#archivo')[0].files.length; i++) {
                data.append('archivo[]', $('#archivo')[0].files[i]); 
             };

            var parametros={                     
                callback:function(datos, estado, mensaje){

                    if (estado=='ok') {
                        self.filtro("");
                        self.limpiar();
                        self.consultar(self.paginacion.pagina_actual());
                        $('#modal_acciones').modal('hide');
                        self.carpeta_foto();
                    }                        
                        
                },//funcion para recibir la respuesta 
                url:path_principal+'/api/fotos_proyecto/',//url api
                parametros:data                        
            };
            RequestFormData2(parametros);

        } else {
             FotosProyectoViewModel.errores.showAllMessages();//mostramos las validacion
        }  
    }


    //funcion consultar las fotos del proyecto
    self.consultar = function (pagina,valida_carpeta) {

       
        if (pagina > 0) {

            var id_tipo= $('#tipo_fot').val();           
            var proyecto=self.fotosProyectoVO.proyecto_id();
            var tipo_contrato='8';
        
            path = path_principal+'/api/fotos_proyecto/?format=json';
            parameter = { dato: '', page: pagina, proyecto_id:proyecto, tipo_id:id_tipo, desde:self.desde_filtro(), hasta:self.hasta_filtro(), tipo_foto:self.tipo_foto(), asociado:self.asociado()};
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


   
    //eliminar las fotos del proyecto
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las fotos del proyecto para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/administrador_fotos/eliminar_fotos_proyecto/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las fotos del proyecto seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.carpeta_foto();
                 self.checkall(false);
             })

         }     
    
        
    }


    //actualiza las fechas de las fotos
    self.actualizar_fecha = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las fotos para actualizar las fechas.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false 

        }


        if(self.fotosProyectoVO.fecha()==''){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione la fecha.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false  
        }

        if(self.fotosProyectoVO.fecha()!='' && count>0){

             var path =path_principal+'/administrador_fotos/actualizar_fecha/';
             var parameter = { lista: lista_id,fecha:self.fotosProyectoVO.fecha() };
             RequestAnularOEliminar("Esta seguro que desea actualizar las fechas de las fotos seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
                 $('#modalActualizarFecha').modal('hide');
             })

         }
    }



     //funcion para guardar si las fotos estan asociadas a reportes oh no
    self.guardar_seleccion = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las fotos.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false 

        }

        
        if(self.asociar()==''){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione la opcion a guardar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false  
        }

        if(self.asociar()!='' && count>0){
            //alert(self.asociar())
             var path =path_principal+'/administrador_fotos/asociar_reporte/';
             var parameter = { lista: lista_id,asociar:self.asociar() };
             RequestAnularOEliminar("Esta seguro que desea realizar esta accion en las fotos seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 $('#modalGuardarSeleccion').modal('hide');
             })

         }
    } 


        //Trae los comentarios de la foto segun id
    self.Vercomentario=function(obj){

         path =path_principal+'/api/fotos_proyecto/?sin_paginacion=';
         parameter={ id: obj.id, proyecto_id:self.fotosProyectoVO.proyecto_id()};
         RequestGet(function (datos, estado, mensaje) {

            self.comentario(datos[0].comentarios);

         }, path, parameter);

    } 

    
}

var fotosProyecto = new FotosProyectoViewModel();
FotosProyectoViewModel.errores = ko.validation.group(fotosProyecto.fotosProyectoVO);
ko.applyBindings(fotosProyecto);

