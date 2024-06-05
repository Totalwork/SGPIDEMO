function EmpresasEmpleadosViewModel(argument) {

var self=this;
self.listado_empresas=ko.observableArray([]);
self.listado_empresas_empleados=ko.observableArray([]);
self.mensaje_empresas=ko.observable(''); 
self.mensaje_empresas_empleados=ko.observable(''); 
self.check_empresas=ko.observable(false);
self.check_empresas_permiso=ko.observable(false);

self.consultar_empresas = function () {       
    
     path =path_principal + '/seguridad-social/consultar_empresa/';
     parameter = {dato:$('#txtBuscarE').val()};
     RequestGet(function (datos, estado, mensage) {

         if (estado == 'ok' && datos!=null && datos.length > 0) {
         	
             self.mensaje_empresas('');                     
             self.listado_empresas(agregarOpcionesObservable(datos));  

         } else {
             self.listado_empresas([]);
             self.mensaje_empresas(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
         }
       
     }, path, parameter, function(){
                    cerrarLoading();
                   });
}


self.consultar_empresas_empleados = function () {       
          
     path =path_principal + '/seguridad-social/consultar_empresa_permisos/';
     parameter = {dato:$('#txtBuscarEE').val()};
     RequestGet(function (datos, estado, mensage) {

         if (estado == 'ok' && datos!=null && datos.length > 0) {
         	
             self.mensaje_empresas_empleados('');                     
             self.listado_empresas_empleados(agregarOpcionesObservable(datos));  

         } else {
             self.listado_empresas_empleados([]);
             self.mensaje_empresas_empleados(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
         }
                
     }, path, parameter, function(){
        cerrarLoading();
     });
}

self.guardar=function(){

	var lista=[];

	ko.utils.arrayForEach(self.listado_empresas(),function(p){
		if (p.procesar()) {
			lista.push(p.id);
		}
	});

	if (lista.length==0) { return false; }

	var parametros={           
          callback:function(datos, estado, mensaje){
             if (estado=='ok') {                
                self.consultar_empresas();
                self.consultar_empresas_empleados();
             }
          },//funcion para recibir la respuesta 
          url:path_principal+'/seguridad-social/guardar_empresa_permisos/',
          parametros:ko.toJS({lista_empresas:lista}),
          completado:function(){
                    cerrarLoading();
                   }
    };
           
    Request(parametros);

}

self.eliminar=function(){

	var lista=[];

	ko.utils.arrayForEach(self.listado_empresas_empleados(),function(p){
		if (p.procesar()) {
			lista.push(p.id);
		}
	});

	if (lista.length==0) { return false; }

	var parametros={           
          callback:function(datos, estado, mensaje){
             if (estado=='ok') {                
                self.consultar_empresas();
                self.consultar_empresas_empleados();
             }
          },//funcion para recibir la respuesta 
          url:path_principal+'/seguridad-social/eliminar_empresa_permisos/',
          parametros:ko.toJS({lista:lista}),
          completado:function(){
                    cerrarLoading();
                   }
    };
           
    Request(parametros);

}

self.check_empresas.subscribe(function(val){
	ko.utils.arrayForEach(self.listado_empresas(),function(p){
		p.procesar(val);
	});
});

self.check_empresas_permiso.subscribe(function(val){
	ko.utils.arrayForEach(self.listado_empresas_empleados(),function(p){
		p.procesar(val);
	});
});

}

var empresasEmpleados = new EmpresasEmpleadosViewModel();
empresasEmpleados.consultar_empresas();
empresasEmpleados.consultar_empresas_empleados();
ko.applyBindings(empresasEmpleados);