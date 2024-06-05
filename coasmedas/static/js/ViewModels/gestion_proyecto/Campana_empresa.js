
function CampanaEmpresaViewModel() {
	
	var self = this;	
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');

	self.filtro_sin_permiso=ko.observable('');

    self.checkall_sin_permiso=ko.observable(false); 
    self.checkall_con_permiso=ko.observable(false); 

    self.listado_sin_permiso=ko.observableArray([]);
    self.listado_con_permiso=ko.observableArray([]);


   
    // //limpiar el modelo 
     self.limpiar=function(){  
     }

    //funcion consultar de tipo get recibe un parametro
    self.consultar_campana_empresa = function () {
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            path = path_principal+'/api/GestionProyectoCampanaEmpresa?sin_paginacion';
            parameter = {id_campana:$('#id_campana').val()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado_con_permiso(agregarOpcionesObservable(datos));  

                } else {
                    self.listado_con_permiso([]);
                    
                }

            }, path, parameter);

    }


    self.consultar_empresa = function () {
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro_sin_permiso($('#txtBuscar4').val());
            self.mensaje('');
            self.checkall_sin_permiso(false);

            if(self.filtro_sin_permiso()==undefined || self.filtro_sin_permiso()==""){
                self.mensaje('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>Digite alguna busqueda de un contratista.</div>');
            }else{
                 var lista_id='';
                 ko.utils.arrayForEach(self.listado_con_permiso(), function(d) {

                        if(lista_id==''){
                            lista_id=d.empresa.id;
                        }else{
                            lista_id=lista_id+","+d.empresa.id;
                        }
                 });
                path = path_principal+'/api/empresa?sin_paginacion';
                parameter = { filtro_empresa_campana: lista_id,dato: self.filtro_sin_permiso()};
                RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                       self.listado_sin_permiso(agregarOpcionesObservable(datos));  


                    } else {
                        self.listado_sin_permiso([]);
                         self.mensaje(mensajeNoFound);
                        
                    }

                    
                    //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                    //    $('#paginacion').show();
                    //    self.llenar_paginacion(results,pagina);
                    //}
                }, path, parameter); 
            }

    }



    self.checkall_sin_permiso.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_sin_permiso(), function(d) {

                    d.eliminado(value);
             }); 
    });


    self.checkall_con_permiso.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_con_permiso(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.incluir_empresa=function(){

        var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_sin_permiso(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id.push({
                        id:d.id
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una empresa para incluirlo con permiso.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{
              var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar_campana_empresa();
                            self.checkall_sin_permiso(false);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/gestion_proyecto/incluir_empresas/',//url api
                     parametros:{ lista: lista_id, campana_id:$('#id_campana').val()}                     
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
        }
    }

     self.quitar_empresas=function(){

        var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_con_permiso(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id.push({
                        id:d.id
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contratista para quitarlo como diseñador.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{
              var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar_campana_empresa();
                            self.checkall_con_permiso(false);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/gestion_proyecto/quitar_empresas/',//url api
                     parametros:{ lista: lista_id}                     
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
        }
    }


    self.consulta_enter_empresa = function (d,e) {
        if (e.which == 13) {
            self.filtro_sin_permiso($('#txtBuscar4').val());
            self.consultar_empresa();
        }
        return true;
    }




 }

var campana_empresa = new CampanaEmpresaViewModel();
//CampanaEmpresaViewModel.errores_fondo = ko.validation.group(campana_empresa.fondoVO);
campana_empresa.consultar_campana_empresa();//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(campana_empresa,content);
ko.applyBindings(campana_empresa,header);