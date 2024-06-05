function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   

    self.bdi_actividad=ko.observable(0);

     self.listado_estado=ko.observableArray([]);
     self.id_estado=ko.observable();

     self.validar=ko.observable(true);



     self.detalleVO={
        id:ko.observable(0),
        detallepresupuesto_id:ko.observable(0),
        codigoUC:ko.observable(''),
        descripcionUC:ko.observable(''),
        valorManoObra:ko.observable(0),
        valorMaterial:ko.observable(0),
        valorGlobal:ko.observable(0),
        cambio_id:ko.observable($('#cambio_id').val()),
        nodo_id:ko.observable(0).extend({ required: { message: '(*)Seleccione un apoyo' }}),
        operacion:ko.observable(0).extend({ required: { message: '(*)Seleccione una operacion' }}),
        cantidadPropuesta:ko.observable(0).extend({ required: { message: '(*)Digite la cantidad propuesta' }})
    }


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
         

     }



    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

             self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_avance_actividad",self.filtro() || '');

            self.cargar(pagina);

        }


    }


    self.cargar =function(pagina){           


            let filtro_avance_actividad=sessionStorage.getItem("filtro_avance_actividad");

            path = path_principal+'/api/avanceGrafico2DetallePresupuesto/?format=json&page='+pagina;
            parameter = {dato: filtro_avance_actividad, pagina: pagina,presupuesto_id:$("#presupuesto_id").val()};
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

    self.limpiar_seleccion=function(){
        self.validar(true);
        self.bdi_actividad(0);
        self.detalleVO.detallepresupuesto_id(0);
    }


    self.bdi_actividad.subscribe(function (value) {
            
            if(value>0){
                self.validar(false);
                self.detalleVO.detallepresupuesto_id(value);
                return 1;
            }
             return 1;

    });


   
    self.guardar=function(){

         // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.detalleVO.id()==0){

                self.detalleVO.valorGlobal(self.detalleVO.valorMaterial()+self.detalleVO.valorManoObra());

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            location.href=path_principal+"/avanceObraGrafico2/detalle_cambio/"+$('#cambio_id').val()+"/";

                            //self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceGrafico2DetalleCambio/',//url api
                     parametros:self.detalleVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
            }

    }

 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance_actividad"));
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

