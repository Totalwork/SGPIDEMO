function ItemViewModel(argument) {
	var self=this;

	self.listado=ko.observableArray([]);
	self.url=path_principal+'/api/Items/';
	self.filtro=ko.observable('');
	self.mensaje=ko.observable('');
	self.buscado_rapido=ko.observable(false);

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (id) {
    	
        if (id > 0) { 
            self.buscado_rapido(true);
            self.filtro($('#txtBuscar').val());
            path = self.url + '?format=json&proceso=' + id +'&ignorePagination=1';
            parameter = {
                dato: self.filtro()
            };
            RequestGet(function(datos, estado, mensage) {
            	//alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado(datos.data);
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }

    self.abrir_modal = function() {}
	self.eliminar = function() {}
	self.exportar_excel = function() {}

    self.guardarCambiosResponsables=function(){
        var datos=[];
        var strid;
        var id;
        $('.responsableUsuario').each(function(){
            //id.push($(this).attr('id'));
            strid=$(this).attr('id');
            id=strid.replace('cmbResponsable','').trim();
            datos.push('{\'id\':'+id+',\'responsable\':' + $(this).val()+'}')
        });
        path =path_principal+'/proceso/responsables/guardarCambios/';
        parameter = { lista: datos };
        var parametros = {
            callback:function(datos, estado, mensaje){
                if (estado =='ok'){
                    self.consultar($('#txtProcesoId').val());                    
                }else{
                    self.mensaje('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>Se presentaron errores al guardar los cambios.</div>');
                }
            },
            url:path,
            parametros:parameter
        };
        Request(parametros);
    }

}
var item = new ItemViewModel();
item.consultar(0)
ko.applyBindings(item);