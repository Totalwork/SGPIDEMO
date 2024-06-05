
    function Encabezado_giroViewModel() {
        
        var self = this;
        self.listado=ko.observableArray([]);
        self.mensaje=ko.observable('');
        self.sinreferencia=ko.observable('');
        self.sin_flujo=ko.observable('');
        self.por_actualizar=ko.observable('');
        self.sol_sinpagar=ko.observable('');
        self.sol_codigo=ko.observable('');


        //funcion consultar tap de consultar y modificar de encabezado giro
        self.consultar = function (pagina) {
            
            //alert($('#mcontrato_filtro').val())
            if (pagina > 0) {            

                path = path_principal+'/solicitud_giro/countsolicitudes/';
                parameter = { dato: '', 
                              page: pagina,
                            };                       
                RequestGet(function (results,count) {
                        self.mensaje('');
                        //self.listado(results);
                        self.sinreferencia(results.data.sinreferencia);
                        self.sin_flujo(results.data.por_revisar);
                        self.por_actualizar(results.data.actualizar);
                        self.sol_sinpagar(results.data.sol_sinpagar);
                        self.sol_codigo(results.data.sol_codigo);
                        cerrarLoading();

                }, path, parameter,undefined, false);
            }
        }





    }



    var encabezado_giro = new Encabezado_giroViewModel();
  

    ko.applyBindings(encabezado_giro);
