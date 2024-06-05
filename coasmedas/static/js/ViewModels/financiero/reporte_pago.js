
function CuentaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

    self.lista_contrato=ko.observableArray([]);
    self.macrocontrato_select=ko.observable(0);

    self.fecha_desde=ko.observable('');
    self.fecha_hasta=ko.observable('');


    self.exportar_informe=function(){

        if(self.fecha_desde()=='' || self.fecha_hasta()==''){
                 $.confirm({
                    title: 'Información',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione una fecha desde y fecha hasta para exportar el reporte<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
        }else{
            location.href=path_principal+"/financiero/descargar_reporte_pago/?fecha_desde="+self.fecha_desde()+"&fecha_hasta="+self.fecha_hasta();
        }

        

    }


 

 

}

var cuenta = new CuentaViewModel();
ko.applyBindings(cuenta);
