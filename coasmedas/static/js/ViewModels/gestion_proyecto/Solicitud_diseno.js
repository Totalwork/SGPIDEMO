
function SolicitudDisenoViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>Indique parametro de filtro.</div>');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false); 

    self.listado_municipio=ko.observableArray([]);
    self.id_departamento=ko.observable(0);
    self.id_fondo=ko.observable(0);
    self.id_municipio=ko.observable(0);
    self.nombre_diseno=ko.observable('');

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Filtrar Diseños');
        $('#modal_filter').modal('show');
    }
   
    // //limpiar el modelo 
     self.limpiar=function(){ 

        self.id_departamento(0);
        self.id_municipio(0);
        self.id_fondo(0);
        self.nombre_diseno('');
     }
    // //funcion guardar
     self.guardar=function(){

    	
     }
    //funcion consultar de tipo get recibe un parametro
    self.consultar = function () {  
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

            if(self.id_departamento()==0 && self.id_municipio()==0 && self.id_fondo()==0 && self.nombre_diseno()==''){
                $.confirm({
                title: 'Error',
                content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Seleccione un parametro para filtrar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
                });
            }else{

                path = path_principal+'/api/GestionProyectoDiseno?sin_paginacion';
                parameter = { dato: self.nombre_diseno(), departamento_id:self.id_departamento(),
                    municipio_id:self.id_municipio(),fondo_id:self.id_fondo(),filtro_solicitud:$('#id_solicitud').val() };
                RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                        self.mensaje('');
                        //self.listado(results); 
                        self.listado(agregarOpcionesObservable(datos));  

                    } else {
                        self.listado([]);
                        self.mensaje('');
                        self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    }
                    $('#modal_filter').modal('hide');

                    //}
                }, path, parameter);

            }

    }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });


    self.id_departamento.subscribe(function(value ){

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

    
    self.agregar = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un diseño para la agregac a la solicitud.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/gestion_proyecto/agregar_solicitudes/';
             var parameter = { lista: lista_id,id_solicitud:$('#id_solicitud').val() };
             RequestAnularOEliminar("Esta seguro que desea agregar los diseños seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

 }

var solicitudiseno = new SolicitudDisenoViewModel();
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(solicitudiseno,content);
ko.applyBindings(solicitudiseno,header);