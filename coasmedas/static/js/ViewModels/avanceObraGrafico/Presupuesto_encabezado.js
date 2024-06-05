function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false); 
   // self.url=path_principal+'api/Banco';   



     self.listado_esquema=ko.observableArray([]);

     self.presupuestoVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del presupuesto' } }),
        esquema_id:ko.observable(0).extend({ required: { message: '(*)Seleccione el esquema' } }),
        proyecto_id:ko.observable($('#id_proyecto').val())
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
        self.titulo('Registrar');
        $('#modal_acciones').modal('show');
    }


     self.limpiar=function(){   
           
           self.presupuestoVO.id(0);
           self.presupuestoVO.nombre('');
           self.presupuestoVO.esquema_id(0);
     }



     self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });



    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    self.detalle_presupuesto=function(obj){
        
       location.href=path_principal+"/avanceObraGrafico/presupuesto_detalle/"+obj.id;
    }


    self.ver_detalle_presupuesto=function(obj){
        
       location.href=path_principal+"/avanceObraGrafico/presupuesto_vista_detalle/"+obj.id;
    }


    self.diagrama_gramh=function(obj){
        
       location.href=path_principal+"/avanceObraGrafico/digrama_grahm/"+obj.id;
    }




    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

             self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_avance",self.filtro() || '');

            self.cargar(pagina);

        }


    }


    self.cargar =function(pagina){           


            let filtro_avance=sessionStorage.getItem("filtro_avance");

            path = path_principal+'/api/avanceObraGraficoPresupuesto/?format=json&page='+pagina;
            parameter = {dato: filtro_avance, pagina: pagina,proyecto_id:$('#id_proyecto').val()};
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
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
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

    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/avanceObraGraficoPresupuesto/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Presupuesto');

             self.presupuestoVO.id(results.id);
             self.presupuestoVO.nombre(results.nombre);
             self.habilitar_campos(true);
             self.presupuestoVO.esquema_id(results.esquema.id);
             self.presupuestoVO.proyecto_id(results.proyecto.id);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }


    self.eliminar=function(){

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un presupuesto para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraGrafico/eliminar_id_presupuesto/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los presupuestos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }  

    }

    self.guardar=function(){

        if (IndexViewModel.errores_presupuesto().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.presupuestoVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceObraGraficoPresupuesto/',//url api
                     parametros:self.presupuestoVO                        
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
                       url:path_principal+'/api/avanceObraGraficoPresupuesto/'+self.presupuestoVO.id()+'/',
                       parametros:self.presupuestoVO                        
                  };

                  Request(parametros);

            }

        } else {
             IndexViewModel.errores_presupuesto.showAllMessages();//mostramos las validacion
        }

    }

 

 }



var index = new IndexViewModel();
IndexViewModel.errores_presupuesto = ko.validation.group(index.presupuestoVO);
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

