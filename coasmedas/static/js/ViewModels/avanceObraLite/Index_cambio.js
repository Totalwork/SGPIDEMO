function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';  

   self.motivo_cancelado=ko.observable(''); 
   self.estado_cancelado=ko.observable($('#cancelado').val());


    self.cambioVO={
        id:ko.observable(0),
        presupuesto_id:ko.observable($('#presupuesto_id').val()),
        empresaSolicitante_id:ko.observable($('#id_empresa').val()),
        estado_id:ko.observable($('#estado_id').val()),
        motivo:ko.observable('').extend({ required: { message: '(*)Digite el motivo' } }),
        descripcion:ko.observable(''),
        empresaTecnica_id:ko.observable('').extend({ required: { message: '(*)Seleccione la empresa tecnica' } }),
        empresaFinanciera_id:ko.observable('').extend({ required: { message: '(*)Seleccione la empresa financiera' } })
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

    self.abrir_modal_cancelado = function (obj) {
        //self.limpiar();
        self.titulo('Motivo');
        self.motivo_cancelado(obj.mensajeCancelado);
        $('#modal_mostrar_motivo').modal('show');
    }


    self.abrir_eliminar = function(){
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un cambio para cancelar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
            self.motivo_cancelado('');
            self.titulo('Registrar Motivo');
            $('#modal_motivo').modal('show');
         }     
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

   

    self.cancelar=function(){

        var lista_id=[];
         ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                   lista_id.push({
                        id:d.id
                   })
                }
         });

         var path =path_principal+'/avanceObraLite/actualizar_cancelado/';
             var parameter = { lista: lista_id,motivo:self.motivo_cancelado()};
             RequestAnularOEliminar("Esta seguro que desea cancelar los cambios seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
                $('#modal_motivo').modal('hide');
             })
    }


    self.exportar_excel=function(){
        
    }

    // //limpiar el modelo 
     self.limpiar=function(){   
           self.cambioVO.motivo('');
           self.cambioVO.descripcion('');
           self.cambioVO.empresaFinanciera_id('');
           self.cambioVO.empresaTecnica_id('');

     }



    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

             self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_avance_cambio",self.filtro() || '');

            self.cargar(pagina);

        }


    }


    self.cargar =function(pagina){           


            let filtro_avance_cambio=sessionStorage.getItem("filtro_avance_cambio");

            path = path_principal+'/api/avanceGrafico2Cambio/?format=json&page='+pagina;
            parameter = {dato: filtro_avance_cambio, pagina: pagina,presupuesto_id:$("#presupuesto_id").val()};
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
            if(self.cambioVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceGrafico2Cambio/',//url api
                     parametros:self.cambioVO                        
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
                       url:path_principal+'/api/avanceGrafico2Cambio/'+self.cambioVO.id()+'/',
                       parametros:self.cambioVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             IndexViewModel.errores_cronograma.showAllMessages();//mostramos las validacion
        }
    }



    self.abrir_detalle_cambio=function(obj){
        
       location.href=path_principal+"/avanceObraLite/detalle_cambio/"+obj.id+"/";
    }


 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance_cambio"));
index.cargar(1);//iniciamos la primera funcion
IndexViewModel.errores_cronograma = ko.validation.group(index.cambioVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

