function PredioViewModel(){
	var self=this;
	self.listado=ko.observableArray([]);
	self.url=path_principal+'/api/servidumbrepredio/';
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	self.mensaje=ko.observable('');
    self.mensajePropietario=ko.observable('');
    self.predio=ko.observable('');
	self.expediente=ko.observable('');
	self.buscado_rapido=ko.observable(false);

    self.porcentajeKo=ko.observable(0);

    self.listado_predio_documentos = ko.observable([]);
    self.filtro_listado_predio_docuemtos = ko.observable('');

    self.tipos_predio = ko.observableArray([]);
    self.grupo_documentos = ko.observableArray([]);
    self.titulo=ko.observable('');
    self.filtroPropietario = ko.observable('');
    self.listadoPropietarios=ko.observableArray([]);

    self.url_funcion=path_principal+'/servidumbre/'; 
    self.url_det=path_principal+'/servidumbre/predio/'
    self.url_edit=path_principal+'/servidumbre/editarpredio/'
    self.url_doc=path_principal+'/servidumbre/documentos/'
    self.urlHOME=path_principal+'/servidumbre/predios/'+($('#idExpediente').val());
    self.urlHOME2=path_principal+'/servidumbre/predios/';
    self.urlHOME3=path_principal+'/servidumbre/predio-georeferencias/';

     //Representa un modelo de la tabla predio
     self.predioVO={
        id:ko.observable(0),
        expediente_id:ko.observable(0),
        persona_id:ko.observable(0).extend({ required: { message: ' Seleccione el propietario del predio.' } }),
        nombre_direccion:ko.observable('').extend({ required: { message: ' Digite la direccion / nombre del predio.' } }),
        tipo_id:ko.observable(0).extend({ required: { message: ' Seleccione el tipo de predio.' } }),
        grupo_documento_id:ko.observable(0).extend({ required: { message: ' Seleccione el grupo de documentos.' } })
     }



     //Representa un modelo ded la tabla propietario
     self.propietarioVO={
        id:ko.observable(0),
        cedula:ko.observable('').extend({ required: { message: ' Digite el numero de cedula del propietario.' } }),
        nombres:ko.observable('').extend({ required: { message: ' Digite el nombre del propietario.' } }),
        apellidos:ko.observable('').extend({ required: { message: ' Digite el apellido del propietario.' } }),
        celular:ko.observable(''),
        telefono:ko.observable('')
     }
     self.limpiarModeloPropietario = function(){
        self.propietarioVO.id(0);
        self.propietarioVO.cedula('');
        self.propietarioVO.nombres('');
        self.propietarioVO.apellidos('');
        self.propietarioVO.celular('');
        self.propietarioVO.telefono('');
     }

     self.limpiarModeloPredio = function(){
        self.predioVO.id(0);
        self.predioVO.expediente_id(0);
        self.predioVO.persona_id(0);
        self.predioVO.nombre_direccion('');
        self.predioVO.tipo_id(0);
        self.predioVO.grupo_documento_id(0);
     }

     self.redireccion = function (obj){
      location.href=self.url_det+$('#idExpediente').val()+'/'+obj.id;
     }

     self.redireccion2 = function (obj){
      location.href=self.url_edit+$('#idExpediente').val()+'/'+obj.id;
     }

     self.redireccion3 = function (obj){    
      location.href=self.url_doc+$('#idExpediente').val()+'/'+obj.id;
     }

     self.guardarPropietario = function(){
        if (PredioViewModel.errores_propietario().length == 0) {//se activa las validaciones
            if(self.propietarioVO.id()==0){
                var parametros={
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.get_propietario(self.paginacionPropietario.pagina_actual());
                            self.limpiarModeloPropietario();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: path_principal + '/api/servidumbrepersona/',//url api
                     parametros:self.propietarioVO                        
                };
                RequestFormData(parametros);
            }else{
                //se utiliza cuando se desea mdificar un registro
                 var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                            self.get_propietario(self.paginacionPropietario.pagina_actual());
                            self.limpiarModeloPropietario();
                            } 
                       },//funcion para recibir la respuesta 
                     url: path_principal + '/api/servidumbrepersona/'+ self.propietarioVO.id()+'/',//url api
                     parametros:self.propietarioVO                        
                  };
                  RequestFormData(parametros);
            }
        }else{
            PredioViewModel.errores_propietario.showAllMessages();//mostramos las validacion
        }
     }
     self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1,$('#idExpediente').val());
        }
        return true;
    }

     self.guardarPredio = function(){
        var predio_id = 0
        if (PredioViewModel.errores_predio().length == 0) {//se activa las validaciones
            if(self.predioVO.id()==0){
                var parametros={
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.consultar(self.paginacion.pagina_actual(),$('#idExpediente').val());
                            self.limpiarModeloPredio();
                            predio_id = datos.id
                           
                            $.confirm({
                                title: 'Confrimación!',
                                content: "<h4>Quiere registrar las Georeferencias?</h4>",
                                confirmButton: 'Si',
                                confirmButtonClass: 'btn-info',
                                cancelButtonClass: 'btn-danger',
                                cancelButton: 'No',
                                confirm: function() {                                        
                                    location.href=self.urlHOME3+$('#idExpedienteActual').val()+'/'+predio_id;
                                },
                                cancel: function() {
                                    location.href=self.urlHOME2+$('#idExpedienteActual').val()+'/';
                                }

                            });               

                        }                     
                     },//funcion para recibir la respuesta 
                     url: path_principal + '/api/servidumbrepredio/',//url api
                     parametros:self.predioVO                        
                };
                RequestFormData(parametros);
                
            }else{
                //se utiliza cuando se desea mdificar un registro
                 var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                            self.consultar(self.paginacion.pagina_actual(),$('#idExpediente').val());
                            self.limpiarModeloPredio();
                            predio_id = datos.id
                            
                            $.confirm({
                                title: 'Confrimación!',
                                content: "<h4>Quiere gestionar las Georeferencias?</h4>",
                                confirmButton: 'Si',
                                confirmButtonClass: 'btn-info',
                                cancelButtonClass: 'btn-danger',
                                cancelButton: 'No',
                                confirm: function() {                                        
                                    location.href=self.urlHOME3+$('#idExpedienteActual').val()+'/'+predio_id;
                                },
                                cancel: function() {
                                    location.href=self.urlHOME2+$('#idExpedienteActual').val()+'/';
                                }

                            });

                            } 
                       },//funcion para recibir la respuesta 
                     url: path_principal + '/api/servidumbrepredio/'+ self.predioVO.id()+'/',//url api
                     parametros:self.predioVO                        
                  };
                  RequestFormData(parametros);                  
            }

        }else{
            PredioViewModel.errores_predio.showAllMessages();//mostramos las validacion
        }
        
     }

     self.consultar_persona = function(obj){
        path =path_principal+'/api/servidumbrepersona/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
            self.propietarioVO.id(results.id);
            self.propietarioVO.cedula(results.cedula);
            self.propietarioVO.nombres(results.nombres);
            self.propietarioVO.apellidos(results.apellidos);
            self.propietarioVO.celular(results.celular);
            self.propietarioVO.telefono(results.telefono);
            cerrarLoading();
        }, path, parameter,undefined,false);

     }

    //funcion consultar de tipo get recibe un parametro
    // self.consultar_id = function (pagina,predio) {
    //     if (pagina > 0) {           
    //         self.predio(predio);
    //         path = self.url + '?format=json&page=' + pagina;
            
    //         parameter = {              
    //             id:self.predio()               
    //         };
    //         RequestGet(function(results,count) {      
    //             self.porcentajeKo(results.porcentajedocumentos);
    //             cerrarLoading();
    //         }, path, parameter,undefined,false);
    //     }       
    // }


	self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.consultar_select_create_update_predio = function () {
         path = path_principal+'/servidumbre/select-create-update-predio/';
         parameter = { };
         RequestGet(function (datos, estado, mensage) {
            self.tipos_predio(datos.tipo_id);
            self.grupo_documentos(datos.grupo_documento_id);            
            cerrarLoading();
         },path, parameter,undefined,false); 

    }
    self.buscarPropietario = function (d,e) {
        if (e.which == 13) {
            //self.consultar(1);
            self.get_propietario(1)
        }
        return true;
    }


    self.get_propietario = function(pagina){        
        //Codigo para consultar los propietarios
        path = path_principal+'/api/servidumbrepersona?lite=1&format=json&page=' + pagina;;
        if (pagina > 0) {
            //alert('entre aqui' + pagina); 
            //self.buscado_rapido(true);
            self.filtroPropietario($('#txtBuscarPropietario').val());
            parameter = {
                dato: self.filtroPropietario(),              
            };
            RequestGet(function(datos, estado, mensage) {
                //alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensajePropietario('');
                    self.listadoPropietarios(datos.data);
                } else {
                    self.listadoPropietarios([]);
                    self.mensajePropietario(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                
                self.llenar_paginacionPropietarios(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        } 
        
    }

	//funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina,expediente) {
        if (pagina > 0) {
        	//alert('entre aqui' + pagina); 
            self.buscado_rapido(true);
            self.filtro($('#txtBuscar').val());
            self.expediente(expediente);
            path = self.url + '?format=json&page=' + pagina;
            
            parameter = {
                dato: self.filtro(),
                expediente:self.expediente()               
            };
            RequestGet(function(datos, estado, mensage) {
            	//alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data));
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                
                self.llenar_paginacion(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
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
        }
    }
    self.paginacionPropietario = {
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
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
		self.paginacion.pagina_actual(pagina);
		self.paginacion.total(data.count);
		self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }
    //Funcion para crear la paginacion
    self.llenar_paginacionPropietarios = function (data,pagina) {
        self.paginacionPropietario.pagina_actual(pagina);
        self.paginacionPropietario.total(data.count);
        self.paginacionPropietario.cantidad_por_paginas(resultadosPorPagina);

    }

   self.paginacion.pagina_actual.subscribe(function (pagina) {
        if (self.buscado_rapido()) {
            self.consultar(pagina,$('#idExpediente').val());
          }else{
            self.consultar_por_filtros(pagina);
          }       
    });

   self.paginacionPropietario.pagina_actual.subscribe(function (pagina) {
        self.get_propietario(pagina);     
    });

    self.abrir_modal = function() {
        self.titulo('Buscar o crear el propietario'); 
        $('#modal_busqueda_propietario').modal('show');
        self.get_propietario(1);
    }

    self.utilizarPropietario = function (obj) {
        $("#txtNombrePropietario").val(obj.nombres + ' ' + obj.apellidos);
        $('#modal_busqueda_propietario').modal('hide');

        self.predioVO.persona_id(obj.id);
        predio.predioVO.expediente_id($('#idExpediente').val());
       
    }

	self.eliminar = function(){
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione predios.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/servidumbre/eliminar_predios/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea cerrar los predios seleccionados?", path, parameter, function () {
                 self.consultar(1,$('#idExpediente').val());
                 self.checkall(false);
             })

         } 


    }

	self.exportar_excel=function(){

        location.href=self.url_funcion+"reporte_predios/";
    
        return true;
    }

    

}
var predio = new PredioViewModel();
PredioViewModel.errores_propietario = ko.validation.group(predio.propietarioVO);
PredioViewModel.errores_predio = ko.validation.group(predio.predioVO);
ko.applyBindings(predio);