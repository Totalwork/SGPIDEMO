
function SubcategoriaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

 
    //var num=0;
    //self.url=path_principal+'api/empresa'; 

     //Representa un modelo de la subcategoria
    self.subcategoriaVO={
        id:ko.observable(0),
        titulo:ko.observable('').extend({ required: { message: '(*)Digite el titulo de la subcategoria' } }),
        contenido:ko.observable('').extend({ required: { message: '(*)Digite el contenido de la subcategoria' } }),
        categoria_id:ko.observable(0),
        proyecto_id:ko.observable(0),

     };

     //paginacion de la subcategoria
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

    //funcion para abrir modal de registrar subcategoria
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Subcategoria');
        $('#modal_acciones').modal('show');
    }


     //limpiar el modelo de la subcategoria
     self.limpiar=function(){     
         
             self.subcategoriaVO.id(0);
             self.subcategoriaVO.titulo('');
             self.subcategoriaVO.contenido('');

             self.subcategoriaVO.titulo.isModified(false);
             self.subcategoriaVO.contenido.isModified(false);
      
     }


    //funcion para exportar a excel las subcategorias
    // self.exportar_excel = function (obj) {
    //     self.titulo('Generar informe');
    //     $('#generar_informe').modal('show');
    // }


    //funcion guardar y actualizar las subcategoria
     self.guardar=function(){


        if (SubcategoriaViewModel.errores_subcategoria().length == 0) {//se activa las validaciones

            if(self.subcategoriaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/subcategoria/',//url api
                     parametros:self.subcategoriaVO                        
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
                       url:path_principal+'/api/subcategoria/'+self.subcategoriaVO.id()+'/',
                       parametros:self.subcategoriaVO                        
                  };

                  Request(parametros);

            }

        } else {
             SubcategoriaViewModel.errores_subcategoria.showAllMessages();//mostramos las validacion
        } 
     }


    //funcion consultar las categorias
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            

            self.filtro($('#txtBuscar').val());
            var categoria=self.subcategoriaVO.categoria_id();
            var proyecto=self.subcategoriaVO.proyecto_id();
            var tipo_contrato='8';

           path = path_principal+'/api/subcategoria?format=json';
            parameter = { dato: self.filtro(), page: pagina, id_categoria:categoria ,id_proyecto:proyecto};
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


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    //consultar por id de la categoria
    self.consultar_por_id = function (obj) {
       
       path =path_principal+'/api/subcategoria/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar Subcategoria');

            self.subcategoriaVO.id(datos.id);
            self.subcategoriaVO.titulo(datos.titulo);
            self.subcategoriaVO.contenido(datos.contenido);
             
             $('#modal_acciones').modal('show');

         }, path, parameter);

     }

   
    //eliminar las categorias
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las subcategorias para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/administrador_fotos/eliminar_subcategoria/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las subcategorias seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }


    //exportar excel la tabla del listado de las subcategorias
   self.exportar_excel=function(){

        var categoria=self.subcategoriaVO.categoria_id();
        var proyecto=self.subcategoriaVO.proyecto_id();

        location.href=path_principal+"/administrador_fotos/exportar_subcategoria/?categoria="+categoria+"&proyecto="+proyecto;
     } 


}

var subcategoria = new SubcategoriaViewModel();
SubcategoriaViewModel.errores_subcategoria= ko.validation.group(subcategoria.subcategoriaVO);
ko.applyBindings(subcategoria);
