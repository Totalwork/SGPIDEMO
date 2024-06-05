
function CuentaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

    self.lista_contrato=ko.observableArray([]);
    self.macrocontrato_select=ko.observable(0);

    self.fecha=ko.observable('');

    self.listado_contrato=ko.observableArray([]);
    self.contrato_select=ko.observable(0);

    self.activar=ko.observable(0);
   
   

    //consultar los macrocontrato para registrar la cuenta
    self.consultar_macrocontrato=function(){

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_contrato(datos.macrocontrato);
            cerrarLoading();

         }, path, parameter,undefined,false);

    }

    self.macrocontrato_select.subscribe(function (valor) {
        
            if(valor>0){

                 path =path_principal+'/api/Contrato/?sin_paginacion';
                 parameter={ mcontrato: valor,liteD:'5' };
                 RequestGet(function (datos, estado, mensaje) {
                   
                    self.listado_contrato(datos);
                    cerrarLoading();

                 }, path, parameter,undefined,false);

            }
    });


    self.contrato_select.subscribe(function (valor) {
        
            if(valor>0){
                self.activar(1);
            }else{
                self.activar(0);
            }
    });



    self.exportar_informe=function(){

        if(self.macrocontrato_select()==0){
                 $.confirm({
                    title: 'Información',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione un macrocontrato para exportar el informe<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
        }else{

            location.href=path_principal+"/financiero/descargar_informe_financiero_origen/?macrocontrato_id="+self.macrocontrato_select()+"&fecha="+self.fecha()+"&activar="+self.activar()+"&contrato_id="+self.contrato_select();
        }

        

    }


 

 

}

var cuenta = new CuentaViewModel();
ko.applyBindings(cuenta);
