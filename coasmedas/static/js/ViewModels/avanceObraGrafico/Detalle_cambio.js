function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco'; 

     // ko.validation.rules['dateGreaterThen'] = {
     //        validator: function (val, otherVal) {
     //            console.log(val)
     //            console.log(otherVal)
     //        },
     //        message: 'The date must be greater then or equal to '
     //    };

     //    ko.validation.registerExtenders();


     self.listado_estado=ko.observableArray([]);
     self.id_estado=ko.observable();


     self.id_estado=ko.observable(0);
     self.motivo=ko.observable('');


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

    self.abrir_modal = function (estado) {
        //self.limpiar();
        self.titulo('Motivo');
        self.id_estado(estado);
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

            path = path_principal+'/avanceObraGrafico/consultar_detalle_cambio/';
            parameter = {dato: filtro_avance,detalle_cambio:$("#id_cambio").val()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos));
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

    self.cambio_estado=function(estado){
        self.id_estado(estado);
        self.guardar();
    }

    self.guardar=function(){

            if(self.id_estado()==5 || self.id_estado()==6 || self.id_estado()==4){

                    if(self.motivo()==""){
                         $.confirm({
                            title: 'Error',
                            content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Digite un motivo<h4>',
                            cancelButton: 'Cerrar',
                            confirmButton: false
                        });
                        return false;
                    }

            }

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            location.reload();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/cambio_estado/',//url api
                     parametros:{id_cambio:$('#id_cambio').val(),id_estado:self.id_estado(),motivo:self.motivo()},
                     alerta:false                    
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

    }
   

 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

