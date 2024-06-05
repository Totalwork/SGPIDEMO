function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false); 

    self.cantidad_total=ko.observable(0);
   // self.url=path_principal+'api/Banco';  




    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registro de Cantidades por Poste');
        $('#modal_acciones').modal('show');
    }



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

            path = path_principal+'/api/avanceGrafico2CantidadNodo/?format=json&sin_paginacion';
            parameter = {dato: filtro_avance,detalle_presupuesto_id:$('#id_detalle_presupuesto').val()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    self.busqueda_total(datos);
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos));
                    //self.cargar_total_presupuesto(datos);
                     $('#modal_acciones').modal('hide');

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                //self.llenar_paginacion(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
    }


    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.limpiar();
            self.consultar(1);
        }
        return true;
    }

    self.guardar=function(){


             var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico2/guardar_cantidad_apoyo/',//url api
                     parametros:{ lista: self.listado_cantidad() }                         
                  };
                Request(parametros);
    }

     self.busqueda_total=function(data){
        var lista=[];
        self.cantidad_total(0);
        ko.utils.arrayForEach(data, function(obj) {
            if(obj.cantidad==''){
                obj.cantidad=0;
            }
            cant=parseFloat(self.cantidad_total())+parseFloat(obj.cantidad);
            self.cantidad_total(cant);
           
        });
    }

    self.listado_cantidad=function(){
        var lista=[];
        ko.utils.arrayForEach(self.listado(), function(obj) {
            if(obj.cantidad==''){
                obj.cantidad=0;
            }
            lista.push({
                id:obj.id,
                cantidad:obj.cantidad
            });
        });

        return lista;
    }

   

 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

