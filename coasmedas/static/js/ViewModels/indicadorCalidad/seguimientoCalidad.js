
function SeguimientoViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.desde=ko.observable('');
    self.hasta=ko.observable('');
    self.valor_total=ko.observable('');
    self.objectivo_anual=ko.observable('');

     //Representa un modelo del seguimiento
    self.seguimientoVO={
        id:ko.observable(0),
        indicador_id:ko.observable(''),
        inicioPeriodo:ko.observable('').extend({ required: { message: '(*)Seleccione la fecha de inicio' } }),
        finPeriodo:ko.observable('').extend({ required: { message: '(*)Seleccione la fecha fin' } }),
        valor:ko.observable('').extend({ required: { message: '(*)Digite el valor' } }),

     };

     //paginacion de seguimiento
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

    //funcion para abrir modal de registrar seguimiento
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Segumiento');
        $('#modal_acciones').modal('show');
    }


    //funcion para filtrar los seguimientos
    self.filtrar_seguimiento = function () {
        self.titulo('Filtrar Movimiento');
        $('#modal_filtro_seguimiento').modal('show');
    }


     //limpiar el modelo de seguimiento
     self.limpiar=function(){     
         
             self.seguimientoVO.id(0);
             self.seguimientoVO.inicioPeriodo('');
             self.seguimientoVO.finPeriodo('');
             self.seguimientoVO.valor('');
      
     }


    //funcion guardar y actualizar el seguimiento
     self.guardar=function(){

        if (SeguimientoViewModel.errores_seguimiento().length == 0) {//se activa las validaciones

             if(self.seguimientoVO.id()==0){

                // var sum_total = parseInt(self.seguimientoVO.valor()) + parseInt(self.valor_total());

                // if(sum_total<= self.objectivo_anual()){

                    var parametros={                     
                         callback:function(datos, estado, mensaje){

                            if (estado=='ok') {
                                self.filtro("");
                                self.limpiar();
                                self.consultar(self.paginacion.pagina_actual());
                                $('#modal_acciones').modal('hide');
                            }                        
                            
                         },//funcion para recibir la respuesta 
                         url:path_principal+'/api/SeguimientoIndicador/',//url api
                         parametros:self.seguimientoVO                   
                    };
                    RequestFormData(parametros);
                // }else{

                //     $.confirm({
                //         title:'Informativo',
                //         content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>La suma total del valor del seguimiento no puede ser mayor al objectivo anual.<h4>',
                //         cancelButton: 'Cerrar',
                //         confirmButton: false
                //     });
                // }
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
                       url:path_principal+'/api/SeguimientoIndicador/'+self.seguimientoVO.id()+'/',
                       parametros:self.seguimientoVO                        
                  };

                  RequestFormData(parametros);
            }

        } else {
             SeguimientoViewModel.errores_seguimiento.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar 
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            
           
            self.cargar(pagina);          
        }
    }


    self.cargar = function(pagina){

        var indicador_id=self.seguimientoVO.indicador_id();
        var desde=self.desde();
        var hasta=self.hasta();

        path = path_principal+'/api/SeguimientoIndicador?format=json';
            parameter = { page: pagina, indicador: indicador_id, desde:desde, hasta:hasta};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
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

    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    //consultar por id del seguimiento
    self.consultar_por_id = function (obj) {
       
       path =path_principal+'/api/SeguimientoIndicador/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar indicador');

            self.seguimientoVO.id(datos.id);
            self.seguimientoVO.inicioPeriodo(datos.inicioPeriodo);
            self.seguimientoVO.finPeriodo(datos.finPeriodo);
            self.seguimientoVO.valor(datos.valor);
            self.seguimientoVO.indicador_id(datos.indicador.id);
             
             $('#modal_acciones').modal('show');

         }, path, parameter);

     }

   
    //eliminar los seguimiento
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los seguimientos para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/indicadorCalidad/eliminar_seguimiento/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los seguimientos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }


    //exportar excel la tabla del listado de los seguimiento
   self.exportar_excel=function(){

         location.href=path_principal+"/indicadorCalidad/exportar_seguimiento/";
     } 


}

var seguimiento = new SeguimientoViewModel();
SeguimientoViewModel.errores_seguimiento = ko.validation.group(seguimiento.seguimientoVO);
ko.applyBindings(seguimiento);
