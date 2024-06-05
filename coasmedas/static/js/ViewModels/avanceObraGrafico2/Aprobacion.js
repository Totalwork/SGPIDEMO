function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);

    self.registrado=ko.observable(0);
    self.corregidos=ko.observable(0);
    self.rechazados=ko.observable(0);



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

            path = path_principal+'/avanceObraGrafico2/consultar_cantidad_reportes/';
            parameter = '';
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.registrado(datos.cantidad_registrado);
                    self.corregidos(datos.cantidad_corregidos);
                    self.rechazados(datos.cantidad_rechazados);
                } 
                cerrarLoading();
            }, path, parameter,undefined, false);
    }

 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

