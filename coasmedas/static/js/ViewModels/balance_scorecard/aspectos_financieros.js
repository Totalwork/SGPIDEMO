function Aspectos_financierosViewModel() {
	var self=this;
	self.url=path_principal+'/balance_scorecard/'; 
	self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.titulo_tarjeta=ko.observable('');
    self.id=ko.observable('');

    self.tarjeta_id=ko.observable('');

	self.listado_porcentaje_de_ejecución_financiera=ko.observableArray([]);
    self.listado_saldo_cuentas_administración_recursos=ko.observableArray([]);
    self.listado_recursos_adjudicados_faer=ko.observableArray([]);
    self.listado_recursos_adjudicados_prone=ko.observableArray([]);
    self.listado_contratos=ko.observableArray([]);

    self.consultar_tarjeta=function(tarjeta_id){
        path = self.url+'consultar_por_departamento/';
        parameter = { 
            tipo_tarjeta : tarjeta_id             
         };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {
                if(tarjeta_id==1){
                    self.listado_porcentaje_de_ejecución_financiera(datos);
                }else{
                    if(tarjeta_id==2){
                        self.listado_saldo_cuentas_administración_recursos(datos);
                    }else{
                        if(tarjeta_id==3){
                            self.listado_recursos_adjudicados_faer(datos);
                        }else{
                            if(tarjeta_id==4){
                                self.listado_recursos_adjudicados_prone(datos);
                            }
                        }
                    }
                }
                
            }else{
                if(tarjeta_id==1){
                    self.listado_porcentaje_de_ejecución_financiera([]);
                }else{
                    if(tarjeta_id==2){
                        self.listado_saldo_cuentas_administración_recursos([]);
                    }else{
                        if(tarjeta_id==3){
                            self.listado_recursos_adjudicados_faer([]);
                        }else{
                            if(tarjeta_id==4){
                                self.listado_recursos_adjudicados_prone([]);
                            }
                        }
                    }
                }
            }
            cerrarLoading();
        }, path, parameter , undefined , false );
    }

   
    self.consultar_por_id=function(obj,tarjeta_id){   
        self.tarjeta_id(tarjeta_id);
        //alert(self.tarjeta_id());

        path = self.url+'contrato_por_departamento/?format=json';
        parameter = {
            id_departamento: obj.id,
            tipo_tarjeta : tarjeta_id
        };
        RequestGet(function (datos, estado, mensage) {        
            self.titulo('Contratos departamento de '+obj.nombre);     
            if(tarjeta_id==1){
                    self.titulo_tarjeta('Porcentaje de ejecución financiera')
                }else{
                    if(tarjeta_id==2){
                        self.titulo_tarjeta('Saldo en cuentas para administración de recursos')
                    }else{
                        if(tarjeta_id==3){
                            self.titulo_tarjeta('Recursos adjudicados FAER')
                        }else{
                            if(tarjeta_id==4){
                                self.titulo_tarjeta('Recursos adjudicados PRONE')
                            }
                        }
                    }
                }       
            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.listado_contratos(datos);                
                $('#modal_detalle_contrato').modal('show');
                             
        	}else{
        		self.listado_contratos([]);
        	}
        	cerrarLoading();        
        }, path, parameter , undefined , false );
                

        
    }
	
}
var aspectos_financieros = new Aspectos_financierosViewModel();
ko.applyBindings(aspectos_financieros);