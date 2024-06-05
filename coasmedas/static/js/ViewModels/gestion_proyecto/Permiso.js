
function PermisoViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>Indique parametro de filtro.</div>');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall_consultar=ko.observable(false); 
    self.checkall_editar=ko.observable(false); 

    self.listado_municipio=ko.observableArray([]);

    self.filterVO={
	 	empresa_id:ko.observable(0),
	 	departamento_id:ko.observable(0),
        municipio_id:ko.observable(0),
        fondo_id:ko.observable(0)
	 };

    self.abrir_modal = function () {
        self.titulo('Filtro');
        $('#modal_acciones').modal('show');
    }

   
    // //limpiar el modelo 
     self.limpiar=function(){    	 
         
             self.filterVO.municipio_id(0);
             self.filterVO.departamento_id(0);
             self.filterVO.fondo_id(0);
             self.filtro('');
             $('#txtBuscar').val('');
             self.listado([]);
     }
    // //funcion guardar
     self.guardar=function(){

    	var lista_id=[];
        ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.consultar()==true || d.editar()==true){
                   lista_id.push({
                        id_diseno:d.id(),
                        consultar:d.consultar(),
                        editar:d.editar()
                   })
                }
        });
            
            var parametros={                     
            callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        
                    }                        
                    
                 },//funcion para recibir la respuesta 
                 url:path_principal+'/gestion_proyecto/guardar_permisos/',//url api
                 parametros:{lista: lista_id,id_empresa:self.filterVO.empresa_id()}                    
            };
                //parameter =ko.toJSON(self.contratistaVO);
            Request(parametros);

    }

    self.filtrar=function(){
        if(self.filterVO.empresa_id()==0){
            $.confirm({
                title: 'Error',
                content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Seleccione la empresa para filtrar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else if(self.filterVO.departamento_id()==0 && self.filterVO.municipio_id()==0 && self.filterVO.fondo_id()==0){
            $.confirm({
                title: 'Error',
                content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Seleccione algun criterio para filtrar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{            
                self.filtro($('#txtBuscar').val());
                path = path_principal+'/api/GestionProyectoDiseno?sin_paginacion&filtro_permiso';
                parameter = { departamento_id:self.filterVO.departamento_id(),municipio_id:self.filterVO.municipio_id(),
                    fondo_id:self.filterVO.fondo_id(),dato:self.filtro(),empresa_id:self.filterVO.empresa_id()};
                RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                        self.mensaje('');
                        //self.listado(results); 
                        self.listado(convertToObservableArray(datos));  
                        self.checkall_consultar(false);
                        self.checkall_editar(false);

                    } else {
                        self.listado([]);
                        self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    }

                    $('#modal_acciones').modal('hide');

                    //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                    //    $('#paginacion').show();
                    //    self.llenar_paginacion(results,pagina);
                    //}
                }, path, parameter);
            
        }
    }

    self.checkall_consultar.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {
                    d.consultar(value);
             }); 
    });


    self.checkall_editar.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.editar(value);
             }); 
    });


    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    self.filterVO.departamento_id.subscribe(function (value) {
            
            if(value>0){
                path = path_principal+'/api/Municipio?ignorePagination';
                parameter = { id_departamento: value};
                RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                       
                        self.listado_municipio(datos);  

                    } else {
                        self.listado_municipio([]);
                    }

                }, path, parameter);
            }else{
                self.listado_municipio([]);
            }
    });


 }

var permiso = new PermisoViewModel();
PermisoViewModel.errores_filtro = ko.validation.group(permiso.filterVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(permiso,content);
ko.applyBindings(permiso,header);