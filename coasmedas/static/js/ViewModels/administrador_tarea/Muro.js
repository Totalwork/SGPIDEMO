 
function MuroViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');

    self.filterVO={
        desde:ko.observable(''),
        hasta:ko.observable('')
    }

    self.lista_macrocontrato=ko.observableArray([]);
    self.id_macrocontrato=ko.observable(0);
    self.listado_contratista=ko.observableArray([]);
    self.id_contratista=ko.observable(0);
    self.listado_departamento=ko.observableArray([]);
    self.id_departamento=ko.observable(0);
    self.listado_municipio=ko.observableArray([]);
    self.id_municipio=ko.observable(0);
    self.listado_proyectos=ko.observableArray([])
    self.id_proyecto=ko.observable(0);

    self.comentarioVO={
        tarea_id:ko.observable(0),
        comentario:ko.observable(''),
        usuario_id:ko.observable(0),
        fecha:ko.observable('')   
    }


    self.abrir_modal_filtro = function () {
        self.titulo('Filtro');
        $('#modal_filter').modal('show');
    }


    self.limpiar_filtro=function(){
        self.id_macrocontrato(0);
        self.listado_contratista([]);
        self.id_contratista(0);
        self.id_departamento(0);
        self.listado_municipio([]);
        self.id_municipio(0);
        self.listado_proyectos([])
        self.id_proyecto(0);
        self.consultar(1);
    }


    self.consultar_id_tarea=function(obj){
       location.href=path_principal+"/administrador_tarea/tarea/"+obj.id();    
    }
    
    self.consultar_filtro=function(){

        self.consultar(1);
    }

     self.limpiar=function(){ 

     }


     self.consultar_macrocontrato=function(){
        
         // path =path_principal+'/proyecto/filtrar_proyectos/?tipo=2';
         path =path_principal+'/proyecto/filtrar_proyectos/?tipo=12';
         parameter='';
         RequestGet(function (results,count) {
           
            self.lista_macrocontrato(results.macrocontrato);

         }, path, parameter,undefined, false,false);
         // $('#loading').hide();
    }

    self.id_macrocontrato.subscribe(function(value){

        var tipo='12';
        if(value!=0){

            path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+value+'&tipo='+tipo;
            parameter = '';
            RequestGet(function (datos, estado, mensage) {
                
                if (estado=='ok') {
                    self.listado_contratista(datos.contratista);
                    self.listado_departamento(datos.departamento);
                    self.listado_municipio(datos.municipio);
                    self.consultar_proyecto();

                }
            }, path, parameter);
        }else{
            self.listado_contratista([]);
            self.consultar_departamento();
            self.listado_municipio([]);
            self.listado_proyectos([]);
        }

    });

 

    self.id_departamento.subscribe(function(value){


        if(value!=0){

            if(self.id_macrocontrato()>0 || self.id_contratista()>0){                

                path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+self.id_macrocontrato()+'&contratista='+self.id_contratista()+'&departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                        self.listado_municipio(datos.municipio);
                        self.consultar_proyecto();
                }, path, parameter);
            }else{
                path = path_principal+'/api/Municipio/?ignorePagination&id_departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                    self.listado_municipio(datos);
                    self.consultar_proyecto();
                }, path, parameter);
            }
        }

    });


    self.id_contratista.subscribe(function(value){


        if(value!=0){
                path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+self.id_macrocontrato()+'&contratista='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                        self.listado_departamento(datos.departamento);
                        self.listado_municipio(datos.municipio);
                        self.consultar_proyecto();

                }, path, parameter);
           
        }

    });


    self.id_municipio.subscribe(function(value){


        if(value!=0){
            
           self.consultar_proyecto();
        }

    });


    self.consultar_proyecto=function(){

        path = path_principal+'/api/Proyecto/?format=json&ignorePagination';
        parameter = {departamento_id:self.id_departamento(),municipio_id:self.id_municipio(),
            contrato:self.id_macrocontrato(), id_contratista:self.id_contratista()};
        RequestGet(function (datos, estado, mensage) {
            self.listado_proyectos(datos);
        }, path, parameter);
    }


     self.consultar_departamento=function(){

            path = path_principal+'/api/departamento/?ignorePagination';
            parameter = '';
            RequestGet(function (datos, estado, mensage) {

                if (datos.length > 0) {
                    self.listado_departamento(datos);
                }
            }, path, parameter,undefined, false,false);
    }

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/Tarea/?sin_paginacion&muro';
            parameter = { dato: self.filtro(), fecha_inicio:self.filterVO.desde(),fecha_final:self.filterVO.hasta(),
                proyecto_id:self.id_proyecto()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.datos!=null && datos.datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(convertToObservableArray(agregarOpcionesObservable(datos.datos)));
                    ko.utils.arrayForEach(self.listado(), function(d) {
                            d.procesar(3);
                    });   

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}

                $('#modal_filter').modal('hide');
                cerrarLoading();
            }, path, parameter,undefined, false);
    }

  self.ver_mar_comentarios=function(value){
        value.procesar(value.procesar()+3);
  }

     //agregar un comentario
  self.addcomentarios = function(d,e) {

    
            if(e.keyCode === 13 || e.keyCode==undefined) {

                if(d.valor_generico()!==''){

                    self.comentarioVO.tarea_id(d.id());
                    self.comentarioVO.comentario(d.valor_generico());
                    self.comentarioVO.usuario_id($('#id_usuario').val());

                    var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            d.valor_generico('');
                            d.comentarios.push(convertToObservable(datos));
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/TareaComentario/',//url api
                     parametros:self.comentarioVO                        
                    };
                    //parameter =ko.toJSON(self.contratistaVO);
                    Request(parametros);

                }else{
                 $("#meg_error").html('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning fa-2x"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>Asegurese de haber agregando algun comentario.</div>');
                
                 }
                return true;

            }
            return true;
        
    };

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.limpiar();
            self.consultar(1);
        }
        return true;
    }
   

 }

var muro = new MuroViewModel();
muro.consultar(1);
muro.consultar_macrocontrato();
//MuroViewModel.errores_tarea = ko.validation.group(muro.comentarioVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(muro,content);
ko.applyBindings(muro,header);