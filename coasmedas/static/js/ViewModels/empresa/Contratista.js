
function ContratistaViewModel() {
    
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
    self.contratistaVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del contratista' } }),
        nit:ko.observable('').extend({ required: { message: '(*)Digite el nit del contratista' } }),
        direccion:ko.observable('').extend({ required: { message: '(*)Digite la direccion del contratista' } }),
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
        self.habilitar_campos(true);
        self.titulo('Registrar Contratista');
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

        location.href=path_principal+"/empresa/export?dato="+self.filtro()+"&esContratista=1&esContratante=0&esProveedor=0&esDisenador=0";
    }
   
    // //limpiar el modelo 
     self.limpiar=function(){        
         
             self.contratistaVO.id(0);
             self.contratistaVO.nombre('');
             self.contratistaVO.nit('');
             self.contratistaVO.direccion('');
             self.contratistaVO.logo('');
             self.contratistaVO.esDisenador(0)
             self.contratistaVO.esContratista(1);
             self.contratistaVO.esContratante(0);;
             self.contratistaVO.esProveedor(0);
             self.contratistaVO.abreviatura('');
             self.contratistaVO.codigo_acreedor('');
             self.actualizar_datos(0);
             self.desahabilitar_nit(true);
             $('#archivo').fileinput('reset');
             $('#archivo').val('');
            // check_eliminar(false)         
     }
    // //funcion guardar
     self.guardar=function(){

        if (ContratistaViewModel.errores_contratista().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

            if(self.contratistaVO.id()==0){

                if(self.habilitar_confirmacion_nit()==0){                        

                        self.contratistaVO.esContratista(1); 
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
                             parametros:self.contratistaVO                        
                        };
                        //parameter =ko.toJSON(self.contratistaVO);
                        RequestFormData(parametros);
                }else{
                    mensajeError('El nit ya existe.');
                }
            }else{

                 if(self.habilitar_confirmacion_nit()==0){ 

                     if($('#archivo')[0].files.length==0){
                        self.contratistaVO.logo('');
                    }                 

                     self.contratistaVO.esContratista(1); 
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
                           url:path_principal+'/api/empresa/'+self.contratistaVO.id()+'/',
                           parametros:self.contratistaVO                        
                      };

                      RequestFormData(parametros);
                 }else{
                    mensajeError('El nit ya existe.');
                }      
            }

        } else {
             ContratistaViewModel.errores_contratista.showAllMessages();//mostramos las validacion
        }
     }
    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            //path = path_principal+'/api/Empresa/?format=json&page='+pagina;
            //parameter = { dato: self.filtro()};
            path = path_principal+'/api/empresa?esContratista=1&format=json&page='+pagina;
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
           
             self.titulo('Actualizar Contratista');

             self.contratistaVO.id(results.id);
             self.contratistaVO.nombre(results.nombre);
             self.contratistaVO.direccion(results.direccion);
             self.contratistaVO.logo(results.logo);
             self.contratistaVO.nit(results.nit);
             self.contratistaVO.abreviatura(results.abreviatura);
             self.contratistaVO.codigo_acreedor(results.codigo_acreedor);
             self.habilitar_campos(true);
             self.desahabilitar_nit(false);
             self.actualizar_datos(1);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }

     // consultar el nit

    self.focus_nit.subscribe(function(newValue) {

            if(newValue==false && self.contratistaVO.nit()!='' && self.actualizar_datos()==0){
                    self.consultar_datos_por_nit();
            }
    });

   /* self.consulta_enter_nit = function (d,e) {
        if (e.which == 13) {
           self.consultar_datos_por_nit();
        }
        return true;
    }*/

    self.consultar_datos_por_nit=function(){

        if(self.contratistaVO.id()==0){           

            self.contratistaVO.id(0);
            self.contratistaVO.nombre('');
            self.contratistaVO.direccion('');
            self.contratistaVO.logo('');
            self.habilitar_confirmacion_nit(0);
        }

        if(self.contratistaVO.nit()!=''){

                 path =path_principal+'/empresa/consultar_datos_nit/';
                 parameter={nit:self.contratistaVO.nit(),tipo_empresa:'esContratista'};
                 RequestGet(function (results,count,mensaje) {
                    
                   if(results.length>0){
                        self.contratistaVO.id(results[0].id);
                        self.contratistaVO.nombre(results[0].nombre);
                        self.contratistaVO.direccion(results[0].direccion);
                        self.contratistaVO.nit(results[0].nit);
                        self.contratistaVO.logo(results[0].logo);
                        self.contratistaVO.abreviatura(results[0].abreviatura);
                        self.contratistaVO.codigo_acreedor(results[0].codigo_acreedor);
                   }else{
                        if(mensaje!=''){
                            self.habilitar_confirmacion_nit(1);
                            mensajeError(mensaje);
                        }else if(results.length==0 && mensaje==""){
                            self.contratistaVO.id(0);
                            self.contratistaVO.nombre('');
                            self.contratistaVO.direccion('');
                            self.contratistaVO.logo('');
                            self.contratistaVO.abreviatura('');
                            self.contratistaVO.codigo_acreedor('');
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
           
             self.titulo('Contratista');

             self.contratistaVO.id(results.id);
             self.contratistaVO.nombre(results.nombre);
             self.contratistaVO.direccion(results.direccion);
             self.contratistaVO.logo(results.logo);
             self.contratistaVO.nit(results.nit);
             self.contratistaVO.abreviatura(results.abreviatura);
             self.contratistaVO.codigo_acreedor(results.codigo_acreedor);
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contratista para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/empresa/actualizar_estado/';
             var parameter = { lista: lista_id, tipo_empresa:'esContratista'};
             RequestAnularOEliminar("Esta seguro que desea eliminar los contratistas seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

 }

var contratista = new ContratistaViewModel();
ContratistaViewModel.errores_contratista = ko.validation.group(contratista.contratistaVO);
contratista.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(contratista,content);
ko.applyBindings(contratista,header);