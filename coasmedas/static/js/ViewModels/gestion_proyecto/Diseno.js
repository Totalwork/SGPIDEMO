
function DisenoViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false); 
    self.total=ko.observable(0);
    self.municipio=ko.observable(0);

    self.listado_municipio=ko.observableArray([]);

    self.id_campana_reporte=ko.observable(0);

    self.disenoVO={
	 	id:ko.observable(0),
	 	nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del diseño.' } }),
        solicitante_id:ko.observable('').extend({ required: { message: '(*)Seleccione el solicitante.' } }),
        campana_id:ko.observable('').extend({ required: { message: '(*)Seleccione  la campaña.' } }),
        fondo_id:ko.observable('').extend({ required: { message: '(*)Seleccione el fondo de financiacion.' } }),
        departamento_id:ko.observable('').extend({ required: { message: '(*)Seleccione el departamento.' } }),
        municipio_id:ko.observable('').extend({ required: { message: '(*)Seleccione el municipio.' } }),
        disenadores_id:ko.observable(0),
        costo_proyecto:ko.observable('').extend({ required: { message: '(*)Digite el costo del proyecto.' } }),
        costo_diseno:ko.observable('').extend({ required: { message: '(*)Digite el costo del diseño.' } }),
        propietaria_id:ko.observable($('#id_empresa').val()),
        activado:ko.observable(true),
        solicitudes_id:ko.observable(0)
	 };


     self.filterVO={
        solicitante_id:ko.observable(0),
        campana_id:ko.observable(0),
        fondo_id:ko.observable(0),
        departamento_id:ko.observable(0),
        municipio_id:ko.observable(0),
        disenadores_id:ko.observable(0),
        estado_id:ko.observable(0)
     };


	 self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
        directiones: ko.observable(true),
        limite: ko.observable(true),
        cantidad_por_paginas: ko.observable(0),
        totalRegistrosBuscados:ko.observable(0),
        text: {
            first: ko.observable('Inicio'),
            last: ko.observable('Fin'),
            back: ko.observable('<'),
            forward: ko.observable('>')
        }
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Diseño');
        $('#modal_acciones').modal('show');
    }

    self.abrir_modal_filter = function () {
        self.limpiar();
        self.titulo('Filtro de Diseño');
        $('#modal_filter').modal('show');
    }

    self.abrir_modal_reporte = function () {
        self.id_campana_reporte(0);
        self.titulo('Generacion de informe');
        $('#modal_reporte').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    //exportar excel
    
    self.exportar_excel=function(){

        filtro="dato="+self.filtro();

        if(self.filterVO.fondo_id()>0){
            filtro=filtro+"&fondo_id="+self.filterVO.fondo_id();
        }
        if(self.filterVO.campana_id()>0){
            filtro=filtro+"&campana_id="+self.filterVO.campana_id();
        }
        if(self.filterVO.departamento_id()>0){
            filtro=filtro+"&departamento_id="+self.filterVO.departamento_id();
        }
        if(self.filterVO.municipio_id()>0){
            filtro=filtro+"&municipio_id="+self.filterVO.municipio_id();
        }
        if(self.filterVO.solicitante_id()>0){
            filtro=filtro+"&solicitante_id="+self.filterVO.solicitante_id();
        }
        if(self.filterVO.estado_id()>0){
            filtro=filtro+"&estado_id="+self.filterVO.estado_id();
        }
        if(self.filterVO.disenadores_id()>0){
            filtro=filtro+"&disenadores_id="+self.filterVO.disenadores_id();
        }
        location.href=path_principal+"/gestion_proyecto/export_excel_diseno?"+filtro;
    }


    self.exportar_excel_convocatoria=function(){

        if(self.id_campana_reporte()==0){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una convocatoria para generar el informe.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
             location.href=path_principal+"/gestion_proyecto/export_excel_convocatoria?campana_id="+self.id_campana_reporte();  
        }
    }

    self.version_diseno=function(obj){

        location.href=path_principal+"/gestion_proyecto/version_diseno/"+obj.id+"/";
    }
   
    // //limpiar el modelo 
     self.limpiar=function(){    	 
         
            self.disenoVO.id(0);
            self.disenoVO.nombre('');
            self.disenoVO.solicitante_id('');
            self.disenoVO.campana_id('');
            self.disenoVO.fondo_id('');
            self.disenoVO.departamento_id('');
            self.disenoVO.municipio_id('');
            self.disenoVO.disenadores_id(0);
            self.disenoVO.costo_proyecto(0);
            self.disenoVO.costo_diseno(0);
            self.disenoVO.propietaria_id($('#id_empresa').val());
            self.disenoVO.activado(true);
            self.disenoVO.solicitudes_id(0);
            self.municipio(0);
     }
    // //funcion guardar
     self.guardar=function(){

    	if (DisenoViewModel.errores_diseno().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

            if(self.disenoVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/GestionProyectoDiseno/',//url api
                     parametros:self.disenoVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
            }else{

                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                          self.limpiar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/GestionProyectoDiseno/'+self.disenoVO.id()+'/',
                       parametros:self.disenoVO                        
                  };

                  Request(parametros);

            }

        } else {
             DisenoViewModel.errores_diseno.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) { 

            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("dato_diseno", $('#txtBuscar').val() || '');
            sessionStorage.setItem("departamento_id_diseno", self.filterVO.departamento_id() || '');
            sessionStorage.setItem("municipio_id_diseno", self.filterVO.municipio_id() || '');
            sessionStorage.setItem("fondo_id_diseno", self.filterVO.fondo_id() || '');
            sessionStorage.setItem("campana_id_diseno", self.filterVO.campana_id()|| '');
            sessionStorage.setItem("solicitante_id_diseno", self.filterVO.solicitante_id()|| '');
            sessionStorage.setItem("estado_id_diseno", self.filterVO.estado_id()|| '');
            sessionStorage.setItem("disenadores_id_diseno", self.filterVO.disenadores_id()|| '');


            self.cargar(pagina);           
            
        }


    }


    self.cargar = function(pagina){

        //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            let filtro = sessionStorage.getItem("dato_diseno");
            let departamento_id = sessionStorage.getItem("departamento_id_diseno");
            let municipio_id = sessionStorage.getItem("municipio_id_diseno");
            let fondo_id = sessionStorage.getItem("fondo_id_diseno");
            let campana_id = sessionStorage.getItem("campana_id_diseno");
            let solicitante_id = sessionStorage.getItem("solicitante_id_diseno");
            let estado_id = sessionStorage.getItem("estado_id_diseno");
            let disenadores_id = sessionStorage.getItem("disenadores_id_diseno");
            path = path_principal+'/api/GestionProyectoDiseno?format=json&page='+pagina;
            if (filtro != "" && departamento_id != "" && municipio_id != "" && municipio_id != "" && fondo_id != "" && campana_id != "" && filtro != "" && estado_id != "" && disenadores_id != "" ){
                parameter = { dato: self.filtro(), pagina: pagina,departamento_id:departamento_id,municipio_id:municipio_id,
                    fondo_id:fondo_id,campana_id:campana_id,solicitante_id:solicitante_id,
                    estado_id:estado_id,disenadores_id:disenadores_id };
            }else{
                parameter = {};
            }            

            RequestGet(function (datos, estado, mensage) {

                self.total(datos.count);
                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));  

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                $('#modal_filter').modal('hide');
                self.llenar_paginacion(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
    }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });


    self.disenoVO.departamento_id.subscribe(function(value){

        if(value!=0 && value!=undefined && value!='null' && value!=''){
                path = path_principal+'/api/Municipio/?ignorePagination&id_departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                    self.listado_municipio(datos);
                }, path, parameter,function(){
                    self.disenoVO.municipio_id(0);
                    self.disenoVO.municipio_id(self.municipio());
                }
                );
        }else{
            self.listado_municipio([]);
        }

    });

    self.filterVO.departamento_id.subscribe(function(value){

        if(value!=0 && value!=undefined && value!='null' && value!=''){
                path = path_principal+'/api/Municipio/?ignorePagination&id_departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                    self.listado_municipio(datos);
                }, path, parameter,function(){
                     self.filterVO.municipio_id(sessionStorage.getItem("municipio_id_diseno"));
                 });
        }else{
            self.listado_municipio([]);
        }

    });


    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    self.consultar_por_id = function (obj) {
       
    path =path_principal+'/api/GestionProyectoDiseno/'+obj.id+'/';
    parameter='';
    RequestGet(function (results,count) {
           
             self.titulo('Actualizar Diseño');

             self.disenoVO.id(results.id);
             self.municipio(results.municipio.id);
             self.disenoVO.nombre(results.nombre);
             self.disenoVO.solicitante_id(results.solicitante.id);
             self.disenoVO.campana_id(results.campana.id);
             self.disenoVO.campana_id(results.campana.id);
             self.disenoVO.fondo_id(results.fondo.id);
             self.disenoVO.departamento_id(results.municipio.departamento.id);
             if(results.disenadores.length>0){
                self.disenoVO.disenadores_id(results.disenadores[0].id);
             }else{
                self.disenoVO.disenadores_id(0);
             }
             self.disenoVO.costo_proyecto(results.costo_proyecto);
             self.disenoVO.costo_diseno(results.costo_diseno);
             self.disenoVO.propietaria_id(results.propietaria.id);
             self.disenoVO.activado(results.activado);
             self.disenoVO.solicitudes_id(0);
             $('#modal_acciones').modal('show');
         }, path, parameter);
    }


    self.cambiar_estado=function(valor){

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un tipo de fondo para el cambio de estado.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/gestion_proyecto/cambio_estado/';
             var parameter = { lista: lista_id,estado_id:valor };
             RequestAnularOEliminar("Esta seguro que desea cambiar el estado en los tipos de fondos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }   

    }


    
    self.eliminar = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un diseño para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/gestion_proyecto/deshabilitardiseno/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los diseños seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

    self.limpiar_filtro=function(){

            self.filterVO.solicitante_id(0);
            self.filterVO.campana_id(0);
            self.filterVO.fondo_id(0);
            self.filterVO.departamento_id(0);
            self.filterVO.municipio_id(0);
            self.filterVO.disenadores_id(0);
            self.filterVO.estado_id(0);
            self.filtro('');
            $('#txtBuscar').val('');
            self.consultar(1);
    }

    self.filtrar=function(){
        if (self.filterVO.departamento_id()==0 && self.filterVO.municipio_id()==0 && self.filterVO.fondo_id()==0 && self.filterVO.solicitante_id()==0
            && self.filterVO.estado_id()==0 && self.filterVO.disenadores_id()==0 && self.filterVO.campana_id()==0) {
            $.confirm({
                title: 'Error',
                content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>Ingrese algun criterio para la busqueda. <h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            }); 
        }else{            
            self.consultar(1);
        }
    }

 }

var diseno = new DisenoViewModel();

$('#txtBuscar').val(sessionStorage.getItem("dato_diseno"));
diseno.filterVO.departamento_id(sessionStorage.getItem("departamento_id_diseno"));
diseno.filterVO.fondo_id(sessionStorage.getItem("fondo_id_diseno"));
diseno.filterVO.campana_id(sessionStorage.getItem("campana_id_diseno"));
diseno.filterVO.solicitante_id(sessionStorage.getItem("solicitante_id_diseno"));
diseno.filterVO.estado_id(sessionStorage.getItem("estado_id_diseno"));
diseno.filterVO.disenadores_id(sessionStorage.getItem("disenadores_id_diseno"));


DisenoViewModel.errores_diseno = ko.validation.group(diseno.disenoVO);
diseno.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(diseno,content);
ko.applyBindings(diseno,header);