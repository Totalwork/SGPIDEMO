
function RegistroGpswModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.archivo=ko.observable('');

    ko.extenders.numeric = function(target, precision) {
        //create a writable computed observable to intercept writes to our observable
        var result = ko.pureComputed({
            read: target,  //always return the original observables value
            write: function(newValue) {
                var current = target(),
                    roundingMultiplier = Math.pow(10, precision),
                    newValueAsNum = isNaN(newValue) ? 0 : +newValue,
                    valueToWrite = Math.round(newValueAsNum * roundingMultiplier) / roundingMultiplier;
     
                //only write if it changed
                if (valueToWrite !== current) {
                    target(valueToWrite);
                } else {
                    //if the rounded value is the same, but a different value was written, force a notification for the current field
                    if (newValue !== current) {
                        target.notifySubscribers(valueToWrite);
                    }
                }
            }
        }).extend({ notify: 'always' });
     
        //initialize with current value to make sure it is rounded appropriately
        result(target());
     
        //return the new computed observable
        return result;
    };

    //Representa el modelo de gps
    self.gpsVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del punto gps' }}),
        longitud:ko.observable('').extend({ required: { message: '(*)Digite la longitud del punto gps' }, numeric: 7}),
        latitud:ko.observable('').extend({ required: { message: '(*)Digite la latitud del punto gps' }, numeric: 7}),
        proyecto_id:ko.observable(0),

     };

     //paginacion de gps
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

    //funcion para abrir modal de carga masiva
    self.carga_masiva = function () {
        self.titulo('Carga masiva');
        $('#modal_carga_masiva').modal('show');
    }

  
    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });

    //funcion para abrir modal de registrar gps
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Gps');
        $('#modal_acciones').modal('show');
    }


     //limpiar el modelo de la cuenta
     self.limpiar=function(){     
         
             self.gpsVO.id(0);
             self.gpsVO.nombre('');
             self.gpsVO.longitud('');
             self.gpsVO.latitud('');

             self.gpsVO.nombre.isModified(false);
             self.gpsVO.longitud.isModified(false);
             self.gpsVO.latitud.isModified(false);     
     }


    //funcion guardar y actualizar los puntos gps
     self.guardar=function(){

        if (RegistroGpswModel.errores_gps().length == 0) {//se activa las validaciones

            if(self.gpsVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Puntos_gps/',//url api
                     parametros:self.gpsVO                        
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
                       url:path_principal+'/api/Puntos_gps/'+self.gpsVO.id()+'/',
                       parametros:self.gpsVO                        
                  };

                  Request(parametros);

            }

        } else {
             RegistroGpswModel.errores_gps.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar los puntos gps
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            

            self.filtro($('#txtBuscar').val());

            path = path_principal+'/api/Puntos_gps?format=json';
            parameter = { dato: self.filtro(), page: pagina, proyecto_id:self.gpsVO.proyecto_id()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    $('#modal_filtro_cuenta').modal('hide'); 
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


    //consultar por id de los puntos gps
    self.consultar_por_id = function (obj) {
       
       path =path_principal+'/api/Puntos_gps/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar Punto gps');

            self.gpsVO.id(datos.id);
            self.gpsVO.nombre(datos.nombre);
            self.gpsVO.longitud(datos.longitud);
            self.gpsVO.latitud(datos.latitud);
             
             $('#modal_acciones').modal('show');

         }, path, parameter);

     }

   
    //eliminar los puntos gps
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los puntos gps para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/puntos_gps/eliminar_gps/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los puntos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
         
    }


        //exportar excel la tabla puntos gps
   self.exportar_excel=function(){


         location.href=path_principal+"/puntos_gps/exportar/?proyecto_id="+self.gpsVO.proyecto_id();
     }


    //funcion para carga masiva
    self.carga_excel=function(){

        var data = new FormData();
         data.append('proyecto',self.gpsVO.proyecto_id());
         data.append('archivo',self.archivo());

        var parametros={                     
            callback:function(datos, estado, mensaje){

                self.consultar(1);
                $('#modal_carga_masiva').modal('hide');                    
                        
            },//funcion para recibir la respuesta 
            url:path_principal+'/puntos_gps/carga_masiva/',//url api
            parametros:data                        
        };
        RequestFormData2(parametros);
    }  

}

var registroGps = new RegistroGpswModel();
RegistroGpswModel.errores_gps = ko.validation.group(registroGps.gpsVO);
ko.applyBindings(registroGps);
