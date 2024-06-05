
function CargoViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.habilitar_campos=ko.observable(true);

    self.url=path_principal+'api/empresa';   
     //Representa un modelo de la tabla persona
    self.cargoVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del cargo' } }),
        firma_cartas:ko.observable(false)
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
        self.habilitar_campos(true);
        self.titulo('Registrar Cargo');
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

        location.href=path_principal+"/parametrizacion/export_cargo?dato="+self.filtro();
    }
   
    // //limpiar el modelo 
     self.limpiar=function(){        
         
             self.cargoVO.id(0);
             self.cargoVO.nombre('');
             self.cargoVO.firma_cartas(false);

            // check_eliminar(false)         
     }
    // //funcion guardar
     self.guardar=function(){

        if (CargoViewModel.errores_cargo().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

            if(self.cargoVO.id()==0){

                       var parametros={                     
                          callback:function(datos, estado, mensaje){
                             if (estado=='ok') {
                                 self.filtro("");
                                 self.consultar(self.paginacion.pagina_actual());
                                 $('#modal_acciones').modal('hide');
                                 self.limpiar();
                             }                        
                             
                          },//funcion para recibir la respuesta 
                          url:path_principal+'/api/Cargo/',//url api
                          parametros:self.cargoVO                        
                     };
                     //parameter =ko.toJSON(self.contratistaVO);
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
                           url:path_principal+'/api/Cargo/'+self.cargoVO.id()+'/',
                           parametros:self.cargoVO                        
                      };

                      RequestFormData(parametros);
            }

        } else {
             CargoViewModel.errores_cargo.showAllMessages();//mostramos las validacion
        }
     }
    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/Cargo?format=json&page='+pagina;
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
       path =path_principal+'/api/Cargo/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Cargo');

             self.cargoVO.id(results.id);
             self.cargoVO.nombre(results.nombre);
             self.cargoVO.firma_cartas(results.firma_cartas);            
             self.habilitar_campos(true);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }

    

     self.consultar_por_id_detalle = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/Cargo/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Cargo');

             self.cargoVO.id(results.id);
             self.cargoVO.nombre(results.nombre);
             self.cargoVO.firma_cartas(results.firma_cartas);
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un cargo para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/parametrizacion/eliminar_id_cargo/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los cargos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

 }

var cargo = new CargoViewModel();
CargoViewModel.errores_cargo = ko.validation.group(cargo.cargoVO);
cargo.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(cargo,content);
ko.applyBindings(cargo,header);