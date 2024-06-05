function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   

   self.archivo_carga=ko.observable('');
   self.motivo_rechazo=ko.observable('');


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
        self.titulo('Soporte de Aprobacion');
        self.archivo_carga('');
        $('#modal_acciones').modal('show');
    }


     self.abrir_modal_correcion = function () {
        //self.limpiar();
        self.titulo('Motivo de Rechazo');
        $('#modal_rechazo').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    self.guardar_aprobacion=function(){

        if(self.archivo_carga()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar la aprobacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('reporte_id',$('#reporte_id').val());
            data.append('archivo',self.archivo_carga());

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            location.reload();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico2/guardar_archivo_aprobacion/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }

    }


     self.guardar_rechazo=function(){

        if(self.motivo_rechazo()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Escriba un motivo del rechazo.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                           location.reload();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico2/guardar_rechazo_reporte/',//url api
                     parametros:{reporte_id:$('#reporte_id').val(),mensaje:self.motivo_rechazo()}                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData(parametros);
        }

    }


  
    // //limpiar el modelo 
     self.limpiar=function(){   
         

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

            path = path_principal+'/api/avanceGrafico2DetalleReporteTrabajo/?format=json&page='+pagina;
            parameter = {dato: filtro_avance, pagina: pagina,reporte_id:$("#reporte_id").val()};
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


   

    self.detalle_reporte=function(obj){

        location.href=path_principal+"/avanceObraGrafico2/detalle_registrado/"+obj.id+"/"; 
    }
   


 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

