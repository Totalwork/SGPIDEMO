
function DisenadoresViewModel() {
	
	var self = this;	
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');

	self.filtro_contratista=ko.observable('');

    self.checkall_contratista=ko.observable(false); 
    self.checkall_disenadores=ko.observable(false); 

    self.listado_contratista=ko.observableArray([]);
    self.listado_disenadores=ko.observableArray([]);


    self.habilitar_confirmacion_nit=ko.observable(0);
    self.focus_nit = ko.observable();
    self.desahabilitar_nit=ko.observable(true);

    self.disenadorVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del contratista' } }),
        nit:ko.observable('').extend({ required: { message: '(*)Digite el nit del contratista' } }),
        direccion:ko.observable('').extend({ required: { message: '(*)Digite la direccion del contratista' } }),
        logo:ko.observable(''),
        esDisenador:ko.observable(1),
        esProveedor: ko.observable(0),
        esContratista: ko.observable(0),
        esContratante: ko.observable(0)
     };

     self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Diseñador');
        $('#modal_acciones').modal('show');
    }

   
    // //limpiar el modelo 
     self.limpiar=function(){  

            self.disenadorVO.id(0);
            self.disenadorVO.nombre('');
            self.disenadorVO.nit('');
            self.disenadorVO.direccion('');
            self.disenadorVO.logo('');
            self.desahabilitar_nit(true);
            $('#archivo').fileinput('reset');
            $('#archivo').val('');
     }


       // //funcion guardar
     self.guardar=function(){
        
        if (DisenadoresViewModel.errores_disenadores().length == 0) {//se activa las validaciones


                if(self.habilitar_confirmacion_nit()==0){                        

                        self.disenadorVO.esDisenador(1); 
                        var parametros={                     
                             callback:function(datos, estado, mensaje){

                                if (estado=='ok') {
                                    self.consultar_disenadores();
                                    $('#modal_acciones').modal('hide');
                                    self.limpiar();
                                }                        
                                
                             },//funcion para recibir la respuesta 
                             url:path_principal+'/api/empresa/',//url api
                             parametros:self.disenadorVO                        
                        };
                        //parameter =ko.toJSON(self.contratistaVO);
                        RequestFormData(parametros);
                }else{
                    mensajeError('El nit ya existe.');
                }
          

        } else {
             DisenadoresViewModel.errores_disenadores.showAllMessages();//mostramos las validacion
        }
     }

    //funcion consultar de tipo get recibe un parametro
    self.consultar_disenadores = function () {
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            path = path_principal+'/api/empresa?sin_paginacion&esDisenador=1';
            parameter = '';
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado_disenadores(agregarOpcionesObservable(datos));  

                } else {
                    self.listado_disenadores([]);
                    
                }

            }, path, parameter);

    }


    self.focus_nit.subscribe(function(newValue) {

            if(newValue==false && self.disenadorVO.nit()!=''){
                    self.consultar_datos_por_nit();
            }
    });

    self.consultar_datos_por_nit=function(){

        if(self.disenadorVO.id()==0){           

            self.disenadorVO.id(0);
            self.disenadorVO.nombre('');
            self.disenadorVO.direccion('');
            self.disenadorVO.logo('');
            self.habilitar_confirmacion_nit(0);
        }

        if(self.disenadorVO.nit()!=''){

                 path =path_principal+'/empresa/consultar_datos_nit/';
                 parameter={nit:self.disenadorVO.nit()};
                 RequestGet(function (results,count,mensaje) {
                    
                   if(results.length>0){
                        self.disenadorVO.id(results[0].id);
                        self.disenadorVO.nombre(results[0].nombre);
                        self.disenadorVO.direccion(results[0].direccion);
                        self.disenadorVO.nit(results[0].nit);
                        self.disenadorVO.logo(results[0].logo);
                   }else{
                        if(mensaje!=''){
                            self.habilitar_confirmacion_nit(1);
                            mensajeError(mensaje);
                        }else if(results.length==0 && mensaje==""){
                            self.disenadorVO.id(0);
                            self.disenadorVO.nombre('');
                            self.disenadorVO.direccion('');
                            self.disenadorVO.logo('');
                            self.habilitar_confirmacion_nit(0);
                        }
                   }
                    
                 }, path, parameter);
        }
    }


    self.consultar_contratista = function () {
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro_contratista($('#txtBuscar4').val());
            self.mensaje('');
            self.checkall_contratista(false);

            if(self.filtro_contratista()==undefined || self.filtro_contratista()==""){
                self.mensaje('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>Digite alguna busqueda de un contratista.</div>');
            }else{

                path = path_principal+'/api/empresa?sin_paginacion&esDisenador=0&esContratista=1';
                parameter = { dato: self.filtro_contratista()};
                RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                       self.listado_contratista(agregarOpcionesObservable(datos));  


                    } else {
                        self.listado_contratista([]);
                         self.mensaje(mensajeNoFound);
                        
                    }

                    
                    //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                    //    $('#paginacion').show();
                    //    self.llenar_paginacion(results,pagina);
                    //}
                }, path, parameter); 
            }

    }



    self.checkall_contratista.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_contratista(), function(d) {

                    d.eliminado(value);
             }); 
    });


    self.checkall_disenadores.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_disenadores(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.incluir_disenadores=function(){

        var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_contratista(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contratista para incluirlo como diseñador.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{
              var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar_disenadores();
                            self.checkall_contratista(false);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/gestion_proyecto/incluir_disenadores/',//url api
                     parametros:{ lista: lista_id }                     
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
        }
    }

     self.quitar_disenadores=function(){

        var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_disenadores(), function(d) {

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
                            self.consultar_disenadores();
                            self.checkall_disenadores(false);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/gestion_proyecto/quitar_disenadores/',//url api
                     parametros:{ lista: lista_id }                     
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
        }
    }


    self.consulta_enter_contratista = function (d,e) {
        if (e.which == 13) {
            self.filtro_contratista($('#txtBuscar4').val());
            self.consultar_contratista();
        }
        return true;
    }




 }

var disenadores = new DisenadoresViewModel();
DisenadoresViewModel.errores_disenadores = ko.validation.group(disenadores.disenadorVO);
disenadores.consultar_disenadores();//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(disenadores,content);
ko.applyBindings(disenadores,header);