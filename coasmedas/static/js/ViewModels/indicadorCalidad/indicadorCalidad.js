
function IndicadorViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.listado_periodicidad=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

     //Representa un modelo del indicador
    self.indicadorVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del indicador' } }),
        unidadMedida:ko.observable('').extend({ required: { message: '(*)Digite la unidad de medida' } }),
        objetivoAnual:ko.observable('').extend({ required: { message: '(*)Digite el objectivo anual' } }),
        periodicidad_id:ko.observable(0).extend({ required: { message: '(*)Seleccione la periodicidad' } }),

     };

     //paginacion de indicador
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

    //funcion para abrir modal de registrar indicador
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Indicador');
        self.consultar_periodicidad();        
        $('#modal_acciones').modal('show');
    }

    self.consultar_periodicidad=function(){
        path = path_principal+'/api/Indicadores/?format=json';
        parameter = { periodicidad: 1};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {                
                self.listado_periodicidad(datos);  
                //console.log(datos.data)
                cerrarLoading();
            } else {
                self.listado_periodicidad([]);                
                cerrarLoading();
            }            

        }, path, parameter,undefined, false);
    }
     //limpiar el modelo de indicador
     self.limpiar=function(){     
         
             self.indicadorVO.id(0);
             self.indicadorVO.nombre('');
             self.indicadorVO.unidadMedida('');
             self.indicadorVO.objetivoAnual('');
             self.indicadorVO.periodicidad_id(0);
      
     }


    //funcion guardar y actualizar el indicador
     self.guardar=function(){

        if (IndicadorViewModel.errores_indicador().length == 0) {//se activa las validaciones

            if(self.indicadorVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Indicadores/',//url api
                     parametros:self.indicadorVO                   
                };
                RequestFormData(parametros);
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
                       url:path_principal+'/api/Indicadores/'+self.indicadorVO.id()+'/',
                       parametros:self.indicadorVO                        
                  };

                  RequestFormData(parametros);
            }

        } else {
             IndicadorViewModel.errores_indicador.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar 
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            
            //sessionStorage.setItem("dato_indicador", $('#txtBuscar').val() || '');
            
            self.cargar(pagina);          
        }
    }


    self.cargar = function(pagina){

       // let filtro = sessionStorage.getItem("dato_indicador");
       self.filtro($('#txtBuscar').val());

        path = path_principal+'/api/Indicadores/?format=json';
            parameter = { dato: self.filtro, page: pagina};
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


    //consultar por id del indicador
    self.consultar_por_id = function (obj) {
        self.limpiar();
        self.consultar_periodicidad();  
       path =path_principal+'/api/Indicadores/'+obj.id+'/?format=json';        
        RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar indicador');            
            self.indicadorVO.id(datos.id);
            self.indicadorVO.unidadMedida(datos.unidadMedida);
            self.indicadorVO.nombre(datos.nombre);
            self.indicadorVO.objetivoAnual(datos.objetivoAnual);
            self.indicadorVO.periodicidad_id(datos.periodicidad.id);                      
             
             $('#modal_acciones').modal('show');

         }, path, parameter);

     }

   
    //eliminar los indicadores
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los indicadores para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/indicadorCalidad/eliminar_indicador/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los indicadores seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }


    //exportar excel la tabla del listado de los indicadores
   self.exportar_excel=function(){

         location.href=path_principal+"/indicadorCalidad/exportar_indicador/";
     } 


}

var indicador = new IndicadorViewModel();
IndicadorViewModel.errores_indicador = ko.validation.group(indicador.indicadorVO);
ko.applyBindings(indicador);