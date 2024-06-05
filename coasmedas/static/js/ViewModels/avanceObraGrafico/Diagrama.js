function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   

    self.id_capitulo=ko.observable(0);
    self.id_actividad=ko.observable(0);
    self.listado_actividades=ko.observableArray([]);


    self.diagramaVO={
        id:ko.observable(0),
        fechaInicio:ko.observable('').extend({ required: { message: '(*)Digite la fecha de inicio' } }),
        fechaFinal:ko.observable('').extend({ required: { message: '(*)Digite la fecha de final' } }),
        actividad_id:ko.observable('').extend({ required: { message: '(*)Seleccione la actividad' } }),
        presupuesto_id:ko.observable($('#id_presupuesto').val())
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

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    self.limpiar=function(){

        self.diagramaVO.id(0);
        self.id_capitulo(0);
        self.diagramaVO.fechaInicio('');
        self.diagramaVO.fechaFinal('');
        self.diagramaVO.actividad_id('');
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

            path = path_principal+'/api/avanceObraGraficoDiagramaGrahm/?format=json&page='+pagina;
            parameter = {dato: filtro_avance, pagina: pagina,presupuesto_id:$('#id_presupuesto').val()};
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


    self.id_capitulo.subscribe(function (value) {
            
             if(value!=0){
                path = path_principal+'/api/avanceObraGraficoEsquemaCapitulosActividades/?sin_paginacion';
                parameter = {padre_id:value};
                RequestGet(function (datos, estado, mensage) {

                    self.listado_actividades(datos);
                }, path, parameter,function(){
                    self.diagramaVO.actividad_id(self.id_actividad());
                    // self.disenoVO.municipio_id(self.municipio());
                }
                );
            }else{
                self.listado_actividades([]);
            }

    });



    self.guardar=function(){

        if (IndexViewModel.errores_diagrama().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.diagramaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            //self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceObraGraficoDiagramaGrahm/',//url api
                     parametros:self.diagramaVO                        
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
                       url:path_principal+'/api/avanceObraGraficoDiagramaGrahm/'+self.diagramaVO.id()+'/',
                       parametros:self.diagramaVO                        
                  };

                  Request(parametros);

            }

        } else {
             IndexViewModel.errores_diagrama.showAllMessages();//mostramos las validacion
        }

    }

     self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });


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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una actividad para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraGrafico/eliminar_diagrama/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las actividades del diagrama seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }  

    }


     self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
        path =path_principal+'/api/avanceObraGraficoDiagramaGrahm/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
           
             self.titulo('Actualizar Diagrama');

             self.diagramaVO.id(results.id);
             self.id_capitulo(results.actividad.padre);
             self.id_actividad(results.actividad.id);
             self.diagramaVO.fechaInicio(results.fechaInicio);
             self.diagramaVO.fechaFinal(results.fechaFinal);
             self.diagramaVO.fechaFinal(results.fechaFinal);
             self.diagramaVO.presupuesto_id(results.presupuesto.id);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }



   self.exportar_excel=function(){

        location.href=path_principal+"/avanceObraGrafico/informe_diagrama?presupuesto_id="+$('#id_presupuesto').val();

   }

   

 }



var index = new IndexViewModel();
IndexViewModel.errores_diagrama = ko.validation.group(index.diagramaVO);
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

