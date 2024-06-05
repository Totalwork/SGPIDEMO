function SeguimientoMaterialesViewModel() {
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');

    self.cargar =function(presupuesto_id){           
        
        path = path_principal+'/avanceObraLite/consultarmaterialesaliquidarlite/' + presupuesto_id + '/';
        parameter = {};
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensaje('');
                //self.listado(results); 
                self.listado(agregarOpcionesObservable(datos));
                 
            } else {
                self.listado([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
            cerrarLoading();
        }, path, parameter,undefined, false);
    }	

    self.exportar_excel=function(presupuesto_id,proyecto_nombre){
        //alert(presupuesto_id);
        location.href=path_principal+"/avanceObraLite/exportarmaterialesaliquidar?presupuesto_id="+presupuesto_id+"&proyecto="+proyecto_nombre
                                                                         
                                                                         
    }

}
var seguimiento = new SeguimientoMaterialesViewModel();
ko.applyBindings(seguimiento);