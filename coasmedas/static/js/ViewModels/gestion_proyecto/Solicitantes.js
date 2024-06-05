
function SolicitantesViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false); 

    self.solicitanteVO={
	 	id:ko.observable(0),
	 	nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del solicitante' } })
	 };


	 self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
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
        self.titulo('Registrar Solicitante');
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

        location.href=path_principal+"/gestion_proyecto/export_excel_solicitante?dato="+self.filtro();
    }
   
    // //limpiar el modelo 
     self.limpiar=function(){    	 
         
             self.solicitanteVO.id(0);
             self.solicitanteVO.nombre('');
     }
    // //funcion guardar
     self.guardar=function(){

    	if (SolicitantesViewModel.errores_solicitante().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

            if(self.solicitanteVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/GestionProyectoSolicitante/',//url api
                     parametros:self.solicitanteVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
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
                       url:path_principal+'/api/GestionProyectoSolicitante/'+self.solicitanteVO.id()+'/',
                       parametros:self.solicitanteVO                        
                  };

                  Request(parametros);

            }

        } else {
             SolicitantesViewModel.errores_solicitante.showAllMessages();//mostramos las validacion
        }
     }
    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/GestionProyectoSolicitante?format=json&page='+pagina;
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
       path =path_principal+'/api/GestionProyectoSolicitante/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Solicitante');

             self.solicitanteVO.id(results.id);
             self.solicitanteVO.nombre(results.nombre);
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un solicitante para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/gestion_proyecto/eliminar_solicitantes/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los solicitantes seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

 }

var solicitante = new SolicitantesViewModel();
SolicitantesViewModel.errores_solicitante = ko.validation.group(solicitante.solicitanteVO);
solicitante.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(solicitante,content);
ko.applyBindings(solicitante,header);