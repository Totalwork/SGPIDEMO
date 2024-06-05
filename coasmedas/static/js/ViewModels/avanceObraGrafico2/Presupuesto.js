function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   


    self.presupuestoVO={
        id:ko.observable(0),
        cronograma_id:ko.observable($('#cronograma_id').val()),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre' } }),
        cerrar_presupuesto:ko.observable(false)
     };



     self.listado_estado=ko.observableArray([]);
     self.id_estado=ko.observable();


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
        //self.limpiar();
        self.titulo('Registrar');
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

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.liquidacionuucc=function(obj){

        location.href=path_principal+"/avanceObraGrafico2/ver-liquidacionuucc/"+obj.id+"/";
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
             var path =path_principal+'/avanceObraGrafico2/eliminar_id_presupuesto/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los presupuestos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    }


    self.exportar_excel=function(){
        
    }

    // //limpiar el modelo 
     self.limpiar=function(){   
           self.presupuestoVO.nombre('');

     }



    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

             self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_avance_presupuesto",self.filtro() || '');

            self.cargar(pagina);

        }


    }


    self.cargar =function(pagina){           


            let filtro_avance_presupuesto=sessionStorage.getItem("filtro_avance_presupuesto");

            path = path_principal+'/api/avanceGrafico2Presupuesto/?format=json&page='+pagina;
            parameter = {dato: filtro_avance_presupuesto, pagina: pagina,cronograma_id:$("#cronograma_id").val()};
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
            //self.limpiar();
            self.consultar(1);
        }
        return true;
    }


    self.guardar=function(){

         if (IndexViewModel.errores_cronograma().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.presupuestoVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceGrafico2Presupuesto/',//url api
                     parametros:self.presupuestoVO                        
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
                       url:path_principal+'/api/avanceGrafico2Presupuesto/'+self.presupuestoVO.id()+'/',
                       parametros:self.presupuestoVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             IndexViewModel.errores_cronograma.showAllMessages();//mostramos las validacion
        }
    }



    self.abrir_detalle_presupuesto=function(obj){
        
       location.href=path_principal+"/avanceObraGrafico2/detalle_presupuesto/"+obj.id+"/";
    }


    self.abrir_apoyo_con_gps=function(obj){
        sessionStorage.setItem("ubicacionActual",null);
        path =path_principal+"/avanceObraGrafico2/menu_gps/"+obj.id+"/";
        parameter='';
        RequestGet(function (datos, estado, mensage) {
               
           if (estado == 'ok') {

                if(datos=='1'){

                         $.confirm({
                            title: 'Confirmar!',
                            content: "<h4>Tiene los puntos de localizacion?</h4>",
                            confirmButton: 'Si',
                            confirmButtonClass: 'btn-info',
                            cancelButtonClass: 'btn-danger',
                            cancelButton: 'No',
                            confirm: function() {

                                location.href=path_principal+"/avanceObraGrafico2/apoyo_con_gps/"+obj.id+"/";                               
                            },
                            cancel: function() {
                                location.href=path_principal+"/avanceObraGrafico2/apoyo_sin_gps/"+obj.id+"/";
                            }
                        });
                
                }else if(datos=='2'){

                    location.href=path_principal+"/avanceObraGrafico2/apoyo_con_gps/"+obj.id+"/";     

                }else if(datos=='3'){
                    
                    location.href=path_principal+"/avanceObraGrafico2/apoyo_sin_gps/"+obj.id+"/";
                }
            }

         }, path, parameter);


        
    }

       self.cantidad_apoyo=function(obj){

        location.href=path_principal+"/avanceObraGrafico2/cantidad_apoyo/"+obj.id+"/";
    }


    self.reporte_trabajo=function(obj){

        location.href=path_principal+"/avanceObraGrafico2/reporte_trabajo/"+obj.id+"/";
    }

    self.reformado=function(obj){

        location.href=path_principal+"/avanceObraGrafico2/reformado/"+obj.id+"/";
    } 

    self.seguimiento_cantidades=function(obj){

        location.href=path_principal+"/avanceObraGrafico2/seguimientocantidades/"+obj.id+"/";
    }    

    self.seguimiento_materiales=function(obj){

        location.href=path_principal+"/avanceObraGrafico2/seguimientomateriales/"+obj.id+"/";
    } 
 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance_presupuesto"));
index.cargar(1);//iniciamos la primera funcion
IndexViewModel.errores_cronograma = ko.validation.group(index.presupuestoVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);
