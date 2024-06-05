function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   

   self.habilitar_motivo=ko.observable(false);

   self.mensaje_sin_avance=ko.observable('');

   self.mensaje_rechazo=ko.observable('');
   self.listado_rechazo=ko.observableArray([]);


    self.reporteVO={
        id:ko.observable(0),
        presupuesto_id:ko.observable($('#presupuesto_id').val()),
        estado_id:ko.observable($('#estado_id_procesado').val()),
        usuario_registro_id:ko.observable($("#usuario_id").val()),
        fechaTrabajo:ko.observable('').extend({ required: { message: '(*)Digite la fecha de trabajo' } }),
        valor_ganando_acumulado:ko.observable(0),
        avance_obra_acumulado:ko.observable(0),
        sinAvance:ko.observable(false),
        motivoSinAvance:ko.observable(''),
        soporteAprobacion:ko.observable(''),
        fecharevision:ko.observable(''),
        usuario_aprueba_id:ko.observable(''),
        motivoRechazo:ko.observable(''),
        empresa_id:ko.observable($('#id_empresa').val())
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
        self.limpiar();
        self.titulo('Registrar');
        $('#modal_acciones').modal('show');
    }

    self.abrir_modal_rechazo = function (obj) {
        //self.limpiar();
        self.titulo('Motivo de Rechazo');
        self.consultar_mensaje(obj.id);
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


    self.consultar_mensaje=function(id){

         path =path_principal+'/api/avanceGrafico2MensajeRechazoReporte/?format=json&sin_paginacion=0';
         parameter={reporte_trabajo_id:id}
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado_rechazo(agregarOpcionesObservable(datos));

                } else {
                    self.listado_rechazo([]);
                    self.mensaje_rechazo(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
           
            $('#modal_rechazo').modal('show');
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un reporte para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraGrafico2/eliminar_id_reportetrabajo/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los reportes seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    }


    self.exportar_excel=function(){
        
    }

    // //limpiar el modelo 
     self.limpiar=function(){   
           self.reporteVO.fechaTrabajo('');
           self.reporteVO.sinAvance(false);
           self.reporteVO.motivoSinAvance('');
           self.habilitar_motivo(false);
           self.reporteVO.usuario_aprueba_id('');

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

            path = path_principal+'/api/avanceGrafico2ReporteTrabajo/?format=json&page='+pagina;
            parameter = {dato: filtro_avance, pagina: pagina,presupuesto_id:$("#presupuesto_id").val(),empresa_id:$('#id_empresa').val()};
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


    self.reporteVO.sinAvance.subscribe(function (valor) {
        if(valor==true){
            self.habilitar_motivo(true);
        }else{
            self.habilitar_motivo(false);
        }
    });


    self.guardar=function(){

        if(self.reporteVO.sinAvance()==true){
            self.reporteVO.estado_id($('#estado_id_registrado').val());
        }else{
            self.reporteVO.estado_id($('#estado_id_procesado').val());
        }

         if (IndexViewModel.errores_cronograma().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.reporteVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceGrafico2ReporteTrabajo/',//url api
                     parametros:self.reporteVO                        
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
                       url:path_principal+'/api/avanceGrafico2ReporteTrabajo/'+self.reporteVO.id()+'/',
                       parametros:self.reporteVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             IndexViewModel.errores_cronograma.showAllMessages();//mostramos las validacion
        }
    }



    self.abrir_avance_con_gps=function(obj){

        if(self.habilitar_motivo()==true){
               $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>En este reporte de trabajo no hay avance.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{

            path =path_principal+"/avanceObraGrafico2/menu_gps/"+obj.presupuesto.id+"/";
            parameter='';
            RequestGet(function (datos, estado, mensage) {
                   
               if (estado == 'ok') {


                    if(datos=='2'){
                        sessionStorage.setItem("ubicacionActual", 'null');
                        location.href=path_principal+"/avanceObraGrafico2/avance_con_gps/"+obj.id+"/";    

                    }else if(datos=='3'){
                        
                        location.href=path_principal+"/avanceObraGrafico2/avance_sin_gps/"+obj.id+"/";
                    }else{
                         $.confirm({
                            title:'Informativo',
                            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>En este avance no tiene ningun punto de gps registrado.<h4>',
                            cancelButton: 'Cerrar',
                            confirmButton: false
                        });
                    }
                }

             }, path, parameter);
            
        }
        
       
    }

    //  self.abrir_avance_sin_gps=function(obj){

    //      if(self.habilitar_motivo()==true){
    //            $.confirm({
    //             title:'Informativo',
    //             content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>En este reporte de trabajo no hay avance.<h4>',
    //             cancelButton: 'Cerrar',
    //             confirmButton: false
    //         });
    //     }else{
            
    //     }
        
       
    // }

    self.abrir_modal_sin_avance=function(obj){

        self.titulo('Motivo de Sin Avance');
        self.mensaje_sin_avance(obj.motivoSinAvance);
        $('#modal_sin_avance').modal('show');
    }


    self.abrir_grafico=function(){

             location.href=path_principal+"/avanceObraGrafico2/grafico/"+$('#presupuesto_id').val()+"/";

    }
     


 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
index.cargar(1);//iniciamos la primera funcion
IndexViewModel.errores_cronograma = ko.validation.group(index.reporteVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

