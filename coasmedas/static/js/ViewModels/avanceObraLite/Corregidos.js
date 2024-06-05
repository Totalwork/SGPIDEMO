$('.datepicker').datepicker();
function IndexViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';   


     self.id_macrocontrato=ko.observable(0);
     self.listado_contratista=ko.observableArray([]);
     self.id_contratista=ko.observable(0);
     self.listado_departamento=ko.observableArray([]);
     self.id_departamento=ko.observable(0);
     self.listado_municipio=ko.observableArray([]);
     self.id_municipio=ko.observable(0);

     self.listado_esquema=ko.observableArray([]);

     self.aprobado=ko.observable(false);
     self.registrado=ko.observable(true);

    self.busqueda={
        id_macrocontrato_excel:ko.observable(0).extend({ required: { message: '(*)Seleccione una macrocontrato' }}),
        id_opcion:ko.observable(0).extend({ required: { message: '(*)Seleccione un tipo' }}),
        desde:ko.observable('').extend({fechaMenor: ''}),
        hasta:ko.observable('').extend({fechaMayor: ''}),
        id_esquema:ko.observable(0).extend({ required: { message: '(*)Seleccione un esquema' }})
     }

     self.habilitar_fecha=ko.observable(false);

     self.listado_estado=ko.observableArray([]);
     self.id_estado=ko.observable();


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
        self.titulo('Filtrar');
        $('#modal_acciones').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.length);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.length ? data.length : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }


    self.busqueda.id_opcion.subscribe(function(value){

            if(value==2){
                self.habilitar_fecha(true);
            }else{
                self.habilitar_fecha(false);
            }
    });


    self.busqueda.hasta.subscribe(function(value){

        self.validador_hasta(value);
    });

     self.busqueda.desde.subscribe(function(value){

        self.validador_desde(value);
    });


    self.busqueda.id_macrocontrato_excel.subscribe(function(value){

          if(value!=0){

            path = path_principal+'/api/Esquema_Capitulos_avance_obra/?format=json&sin_paginacion';
            parameter = {macrocontrato_id:value};
            RequestGet(function (datos, estado, mensage) {

                        self.listado_esquema(datos);
            }, path, parameter);
        }
    });

    //exportar excel
    
    self.cronograma=function(obj){
        
        location.href=path_principal+"/avanceObraLite/cronograma_proyecto/"+obj.proyecto.id;
    }


    self.limpiar_informe=function(){

        self.habilitar_fecha(false);
        self.validador_hasta('');
        self.validador_desde('');
        self.busqueda.id_macrocontrato_excel(0);
        self.busqueda.id_opcion(0);
        self.busqueda.desde('');
        self.busqueda.hasta('');
        self.busqueda.id_esquema(0);

    }
   
    // //limpiar el modelo 
     self.limpiar=function(){   
           /* self.id_macrocontrato(0);
             self.id_contratista(0);
             self.id_departamento(0);
             self.id_municipio(0);*/
     }


    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

             self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_avance",self.filtro() || '');
            sessionStorage.setItem("departamento_id_avance",self.id_departamento() || 0);
            sessionStorage.setItem("municipio_id_avance",self.id_municipio() || 0);
            sessionStorage.setItem("macrocontrato_id_avance",self.id_macrocontrato() || 0);
            sessionStorage.setItem("contratista_id_avance",self.id_contratista() || 0);

            self.cargar(pagina);

        }


    }


     self.llenar_datos=function(data){
         var lista=[];
        ko.utils.arrayForEach(data, function(obj) {
                             
              lista.push({
                            id:ko.observable(obj.proyecto.id),
                            macrocontrato:ko.observable(obj.proyecto.mcontrato.nombre),
                            departamento:ko.observable(obj.proyecto.municipio.departamento.nombre),
                            municipio:ko.observable(obj.proyecto.municipio.nombre),
                            proyecto:ko.observable(obj.proyecto.nombre),
                            totalCorrregidos:ko.observable(obj.totalCorrregidos)                        
                        });
                    
                   
        });
        return lista;
    }


    self.cargar =function(pagina){           


            let filtro_avance=sessionStorage.getItem("filtro_avance");
            let departamento_id_avance=sessionStorage.getItem("departamento_id_avance");
            let municipio_id_avance=sessionStorage.getItem("municipio_id_avance");
            let macrocontrato_id_avance=sessionStorage.getItem("macrocontrato_id_avance");
            let contratista_id_avance=sessionStorage.getItem("contratista_id_avance");

            path = path_principal+'/api/avanceGrafico2ProyectoReporte/?format=json&page='+pagina;
            parameter = { empresa:$('#id_empresa').val(),dato: filtro_avance, pagina: pagina, departamento:departamento_id_avance,
                municipio:municipio_id_avance,mcontrato:macrocontrato_id_avance, contratista:contratista_id_avance,corregido:0};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(self.llenar_datos(datos.data)));
                     $('#modal_acciones').modal('hide');

                     if(self.listado().length==0){
                         self.listado([]);
                        self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                     }

                     self.llenar_paginacion(self.listado(),pagina);

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.limpiar();
            self.consultar(1);
        }
        return true;
    }

    self.id_macrocontrato.subscribe(function(value){

        var tipo='1';
        if(value!=0 && value!='' && value!=null){

            path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+value+'&tipo='+tipo;
            parameter = '';
            RequestGet(function (datos, estado, mensage) {
                
                if (estado=='ok') {
                    self.listado_contratista(datos.contratista);
                    self.listado_departamento(datos.departamento);
                    self.listado_municipio(datos.municipio);

                }
            }, path, parameter,function(){
                    self.id_contratista(sessionStorage.getItem("contratista_id_avance"));       
            });
        }else{
            self.listado_contratista([]);
            self.consultar_departamento();
            self.listado_municipio([]);
        }

    });


    self.id_departamento.subscribe(function(value){


        if(value!=0 && value!='' && value!=null){

            if(self.id_macrocontrato()>0 || self.id_contratista()>0){                

                path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+self.id_macrocontrato()+'&contratista='+self.id_contratista()+'&departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                        self.listado_municipio(datos.municipio);

                }, path, parameter, function(){
                    self.id_municipio(sessionStorage.getItem("municipio_id_avance"));       
                });
            }else{
                path = path_principal+'/api/Municipio/?ignorePagination&id_departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                    self.listado_municipio(datos);

                }, path, parameter, function(){
                    self.id_municipio(sessionStorage.getItem("municipio_id_avance"));       
                });
            }
        }

    });


    self.id_contratista.subscribe(function(value){


        if(value!=0 && value!='' && value!=null){
                path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+self.id_macrocontrato()+'&contratista='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                        self.listado_departamento(datos.departamento);
                        self.listado_municipio(datos.municipio);

                }, path, parameter, function(){
                    self.id_departamento(sessionStorage.getItem("departamento_id_avance"));       
                });
           
        }

    });


    self.consultar_departamento=function(){

            path = path_principal+'/api/departamento/?ignorePagination';
            parameter = '';
            RequestGet(function (datos, estado, mensage) {

                if (datos.length > 0) {
                    self.listado_departamento(datos);
                }
            }, path, parameter, function(){
                    self.id_departamento(sessionStorage.getItem("departamento_id_avance"));       
                }, false, false);
    }


    self.reporte=function(obj){
        location.href=path_principal+"/avanceObraLite/reporte_trabajo_corregido/"+obj.id()+"/";
    }

   

 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance"));
index.id_macrocontrato(sessionStorage.getItem("macrocontrato_id_avance"));
IndexViewModel.errores_busqueda = ko.validation.group(index.busqueda);
index.cargar(1);//iniciamos la primera funcion
index.consultar_departamento();
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

