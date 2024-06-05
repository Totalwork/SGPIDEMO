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
            sessionStorage.setItem("filtro_avance_cambio",self.filtro() || '');

            self.cargar(pagina);

        }


    }


    self.cargar =function(pagina){           


            let filtro_avance_cambio=sessionStorage.getItem("filtro_avance_cambio");

            path = path_principal+'/api/avanceGrafico2DetalleCambio/?format=json&page='+pagina;
            parameter = {dato: filtro_avance_cambio, pagina: pagina,cambio_id:$("#cambio_id").val()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(self.llenar_datos(datos.data)));
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

    self.llenar_datos=function(data){

      var lista=[];
        ko.utils.arrayForEach(data, function(d) {
                descripcion="";
                codigo="";
                nombre_operacion="";

                if(d.detallepresupuesto!=null){
                    descripcion=d.detallepresupuesto.descripcionUC;
                    codigo=d.detallepresupuesto.codigoUC;
                }else{
                    descripcion=d.descripcionUC;
                    codigo=d.codigoUC;
                }

                if(d.operacion==1){
                    nombre_operacion="Agregar";
                }else{
                    nombre_operacion="Eliminar";
                }

                lista.push({
                        id:ko.observable(d.id),
                        descripcionUC:ko.observable(descripcion),
                        codigoUC:ko.observable(codigo),
                        nodo:ko.observable(d.nodo.nombre),
                        operacion:ko.observable(nombre_operacion),
                        cantidad_propuesta:ko.observable(d.cantidadPropuesta)
                })
        }); 

        


        return lista;

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


    // self.eliminar = function () {

    //      var lista_id=[];
    //      var count=0;
    //      ko.utils.arrayForEach(self.listado(), function(d) {

    //             if(d.eliminado()==true){
    //                 count=1;
    //                lista_id.push({
    //                     id:d.id
    //                })
    //             }
    //      });

    //      if(count==0){

    //           $.confirm({
    //             title:'Informativo',
    //             content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un detalle de cambio para la eliminacion.<h4>',
    //             cancelButton: 'Cerrar',
    //             confirmButton: false
    //         });

    //      }else{
    //          var path =path_principal+'/avanceObraGrafico2/eliminar_detalle_cambio/';
    //          var parameter = { lista: lista_id,cambio_id:$('#cambio_id').val()};
    //          RequestAnularOEliminar("Esta seguro que desea eliminar los detalle de cambios seleccionados?", path, parameter, function () {
    //              self.consultar(1);
    //              self.checkall(false);
    //          })

    //      }     
    
        
    // }

    self.abrir_agregar=function(){

        location.href=path_principal+"/avanceObraGrafico2/agregar_detalle/"+$('#cambio_id').val()+"/"; 
    }


    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

   


 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance_cambio"));
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

