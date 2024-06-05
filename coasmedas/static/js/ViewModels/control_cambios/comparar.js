
function CompararViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.listado_encabezado=ko.observableArray([]);
    self.lista_soporte=ko.observableArray([]);
    self.listado_soporte=ko.observableArray([]);
    
    self.mensaje=ko.observable('');
    self.mensaje_listado_soportes=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.proyecto_id=ko.observable(0);
    self.motivo=ko.observable('');


    //funcion para abrir modal de ver soportes
    self.soporte_cambio = function (cambio_id,motivo) {

        self.motivo(motivo);
        self.consultar_soporte(cambio_id)
        self.titulo('Archivos del cambio');
        $('#soporte_cambio').modal('show');
    }



    //funcion consultar el listado de control de cambio
    self.consultar = function () {

        self.filtro($('#txtBuscar').val());

        path = path_principal+'/control_cambios/lista_comparar/?format=json';
        parameter = { dato:self.filtro(),proyecto_id:self.proyecto_id()};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' ) {
                self.mensaje('');
                self.listado_encabezado(datos['encabezados']);
                self.listado(datos['lista']);
                self.lista_soporte(datos['soportes']);      
                cerrarLoading();

            } else {
                self.listado_encabezado([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                cerrarLoading();
            }

        }, path, parameter,undefined, false);
    }


    //funcion consultar el listado de control de cambio
    self.consultar_soporte=function(cambio_id){

        path = path_principal+'/api/Soporte_cambio/?format=json';
        parameter={ cambio_id: cambio_id};
        RequestGet(function (datos, estado, mensaje) {

            if (datos.data!=null && datos.data.length > 0) {

                self.listado_soporte(datos.data);

            } else {
                self.listado_soporte([]);
                self.mensaje_listado_soportes(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
            
        }, path, parameter);

    } 


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar();
        }
        return true;
    }


    //exportar excel la tabla del listado de las nuevas unidades constructivas
    self.exportar_excel=function(){

        self.filtro($('#txtBuscar').val());

        location.href=path_principal+"/control_cambios/exportar_reporte_comparar/?dato="+self.filtro()+"&proyecto_id="+self.proyecto_id();
    } 


}

var comparar = new CompararViewModel();
//AdministrarUUCCViewModel.errores_administrar= ko.validation.group(administrar_uucc.AdministrarUUCCVO);
ko.applyBindings(comparar);
