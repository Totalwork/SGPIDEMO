function AdministrarViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   


    self.etiquetaVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre' } }),
        macrocontrato_id:ko.observable(0).extend({ min: {params:1,message:"(*)Digite el intervalo del cronograma"}})
     };

     self.clonaVO={
        id_macrocontrato:ko.observable('').extend({ required: { message: '(*)Seleccione el macrocontrato' } }),
        nombre_esquema:ko.observable('').extend({ required: { message: '(*)Digite el esquema' } }),
        id_etiqueta:ko.observable(0)
     }
     
     self.listado_esquema=ko.observableArray([]);


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
        self.titulo('Agregar Esquema');
        $('#modal_acciones').modal('show');
    }

    self.abrir_modal_clonacion = function (obj) {
        self.limpiar();
        self.titulo('Clonar Esquema');
        self.clonaVO.id_etiqueta(obj.id);
        $('#modal_clonacion').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }


    // //limpiar el modelo 
     self.limpiar=function(){   
             
            self.etiquetaVO.macrocontrato_id(0);
            self.etiquetaVO.nombre('');
            self.clonaVO.id_macrocontrato('');
            self.clonaVO.id_etiqueta(0);
            self.clonaVO.nombre_esquema('');
     }


    self.checkall.subscribe(function(value){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.clonar_esquema=function(){

        if (AdministrarViewModel.errores_clonacion().length == 0) {//se activa las validaciones
                self.clonaVO.nombre_esquema($('#id_empresa').val()+' - '+self.clonaVO.nombre_esquema());
                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_clonacion').modal('hide');
                            self.consultar(self.paginacion.pagina_actual());

                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico2/clonacion_esquema/',//url api
                     parametros:self.clonaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
        }else{
            AdministrarViewModel.errores_clonacion.showAllMessages();//mostramos las validacion
        }
    }

    self.agregar_capitulos=function(obj){
        
        location.href=path_principal+"/avanceObraGrafico2/actividades/"+obj.id;
    }

    self.regla_estado=function(obj){
        
        location.href=path_principal+"/avanceObraGrafico2/regla_estado/"+obj.id;
    }


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("dato_esquema_capitulog",self.filtro() || '');
            path = path_principal+'/api/avanceGrafico2EsquemaCapitulos/?format=json&page='+pagina;
            parameter = { dato: self.filtro(), pagina: pagina};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));
                     $('#modal_acciones').modal('hide');

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
            }, path, parameter);
        }


    }

    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/avanceGrafico2EsquemaCapitulos/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Esquema de Capitulos');

             self.etiquetaVO.id(results.id);
             self.etiquetaVO.nombre(results.nombre);
             self.etiquetaVO.macrocontrato_id(results.macrocontrato.id);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }

    self.guardar=function(){

        if (AdministrarViewModel.errores_etiquetas().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

            if(self.etiquetaVO.id()==0){
                self.etiquetaVO.nombre($('#id_empresa').val()+' - '+self.etiquetaVO.nombre());
                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceGrafico2EsquemaCapitulos/',//url api
                     parametros:self.etiquetaVO                        
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
                       url:path_principal+'/api/avanceGrafico2EsquemaCapitulos/'+self.etiquetaVO.id()+'/',
                       parametros:self.etiquetaVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             AdministrarViewModel.errores_etiquetas.showAllMessages();//mostramos las validacion
        }
     }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.limpiar();
            self.consultar(1);
        }
        return true;
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un esquema para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraGrafico2/eliminar_esquema/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los esquemas seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

   

 }

var administrar = new AdministrarViewModel();

$('#txtBuscar').val(sessionStorage.getItem("dato_esquema_capitulog"));
AdministrarViewModel.errores_etiquetas = ko.validation.group(administrar.etiquetaVO);
AdministrarViewModel.errores_clonacion = ko.validation.group(administrar.clonaVO);
administrar.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(administrar,content);
ko.applyBindings(administrar,header);