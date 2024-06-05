
function ProveedorViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.habilitar_campos=ko.observable(true);
    self.focus_nit = ko.observable();
    self.habilitar_confirmacion_nit=ko.observable(0);
    self.actualizar_datos=ko.observable(0);
    self.desahabilitar_nit=ko.observable(true);

    self.url=path_principal+'api/empresa';   
     //Representa un modelo de la tabla persona
    self.proveedorVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del proveedor' } }),
        nit:ko.observable('').extend({ required: { message: '(*)Digite el nit del proveedor' } }),
        direccion:ko.observable('').extend({ required: { message: '(*)Digite la direccion del proveedor' } }),
        logo:ko.observable(''),
        esDisenador:ko.observable(0),
        esProveedor: ko.observable(0),
        esContratista: ko.observable(1),
        esContratante: ko.observable(0),
        abreviatura:ko.observable(''),
        codigo_acreedor:ko.observable(0)
     };


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
        self.titulo('Registrar Proveedor');
        self.habilitar_campos(true);
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

        location.href=path_principal+"/empresa/export?dato="+self.filtro()+"&esContratista=0&esContratante=0&esProveedor=1&esDisenador=0";
    }
   
    // //limpiar el modelo 
     self.limpiar=function(){        
         
             self.proveedorVO.id(0);
             self.proveedorVO.nombre('');
             self.proveedorVO.nit('');
             self.proveedorVO.direccion('');
             self.proveedorVO.logo('');
             self.proveedorVO.esDisenador(0)
             self.proveedorVO.esContratista(0);
             self.proveedorVO.esContratante(0);;
             self.proveedorVO.esProveedor(1);
             self.proveedorVO.abreviatura('');
             self.actualizar_datos(0);
             self.desahabilitar_nit(true);
             $('#archivo').fileinput('reset');
             $('#archivo').val('');
            // check_eliminar(false)         
     }
    // //funcion guardar
     self.guardar=function(){

        if (ProveedorViewModel.errores_proveedor().length == 0) {//se activa las validaciones

           // self.proveedorVO.logo($('#archivo')[0].files[0]);

            if(self.proveedorVO.id()==0){

                if(self.habilitar_confirmacion_nit()==0){ 

                    self.proveedorVO.esProveedor(1); 
                    var parametros={                     
                         callback:function(datos, estado, mensaje){

                            if (estado=='ok') {
                                self.filtro("");
                                self.consultar(self.paginacion.pagina_actual());
                                $('#modal_acciones').modal('hide');
                                self.limpiar();
                            }                        
                            
                         },//funcion para recibir la respuesta 
                         url:path_principal+'/api/empresa/',//url api
                         parametros:self.proveedorVO                        
                    };
                    //parameter =ko.toJSON(self.proveedorVO);
                    RequestFormData(parametros);
                }else{
                    mensajeError('El nit ya existe.');
                }
            }else{

                if(self.habilitar_confirmacion_nit()==0){ 

                     if($('#archivo')[0].files.length==0){
                        self.proveedorVO.logo('');
                    }                 

                     self.proveedorVO.esProveedor(1); 
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
                           url:path_principal+'/api/empresa/'+self.proveedorVO.id()+'/',
                           parametros:self.proveedorVO                        
                      };

                      RequestFormData(parametros);
                }else{
                    mensajeError('El nit ya existe.');
                }

            }

        } else {
             ProveedorViewModel.errores_proveedor.showAllMessages();//mostramos las validacion
        }
     }
    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/empresa?esProveedor=1&format=json&page='+pagina;
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

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/empresa/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Proveedor');

             self.proveedorVO.id(results.id);
             self.proveedorVO.nombre(results.nombre);
             self.proveedorVO.direccion(results.direccion);
             self.proveedorVO.logo(results.logo);
             self.proveedorVO.nit(results.nit);
             self.proveedorVO.abreviatura(results.abreviatura);
             self.habilitar_campos(true);
             self.actualizar_datos(1);             
             self.desahabilitar_nit(false);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }

     self.focus_nit.subscribe(function(newValue) {
            if(newValue==false && self.proveedorVO.nit()!='' && self.actualizar_datos()==0){
                    self.consultar_datos_por_nit();
            }
    });

    self.consultar_datos_por_nit=function(){

        if(self.proveedorVO.id()==0){           

            self.proveedorVO.id(0);
            self.proveedorVO.nombre('');
            self.proveedorVO.direccion('');
            self.proveedorVO.logo('');
            self.habilitar_confirmacion_nit(0);
        }

        if(self.proveedorVO.nit()!=''){

                 path =path_principal+'/empresa/consultar_datos_nit/';
                 parameter={nit:self.proveedorVO.nit(),tipo_empresa:'esProveedor'};
                 RequestGet(function (results,count,mensaje) {
                    
                   if(results.length>0){
                        self.proveedorVO.id(results[0].id);
                        self.proveedorVO.nombre(results[0].nombre);
                        self.proveedorVO.direccion(results[0].direccion);
                        self.proveedorVO.nit(results[0].nit);
                        self.proveedorVO.logo(results[0].logo);
                        self.proveedorVO.abreviatura(results[0].abreviatura);
                   }else{
                        if(mensaje!=''){
                            self.habilitar_confirmacion_nit(1);
                            mensajeError(mensaje);
                        }else if(results.length==0 && mensaje==""){
                            self.proveedorVO.id(0);
                            self.proveedorVO.nombre('');
                            self.proveedorVO.direccion('');
                            self.proveedorVO.logo('');
                            self.proveedorVO.abreviatura('');
                            self.habilitar_confirmacion_nit(0);
                        }
                   }
                    
                 }, path, parameter);
        }
    }

     self.consultar_por_id_detalle = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/empresa/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Proveedor');

             self.proveedorVO.id(results.id);
             self.proveedorVO.nombre(results.nombre);
             self.proveedorVO.direccion(results.direccion);
             self.proveedorVO.logo(results.logo);
             self.proveedorVO.nit(results.nit);
             self.proveedorVO.abreviatura(results.abreviatura);
             self.habilitar_campos(false);
             self.desahabilitar_nit(false);
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un proveedor para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/empresa/actualizar_estado/';
             var parameter = { lista: lista_id, tipo_empresa:'esProveedor' };
             RequestAnularOEliminar("Esta seguro que desea eliminar los proveedores seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

 }

var proveedor = new ProveedorViewModel();
ProveedorViewModel.errores_proveedor = ko.validation.group(proveedor.proveedorVO);
proveedor.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(proveedor,content);
ko.applyBindings(proveedor,header);