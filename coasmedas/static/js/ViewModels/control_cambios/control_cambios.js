
function ControlCambioViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

    self.macrocontrato_select=ko.observable(0);
    self.lista_contrato=ko.observableArray([]);
    self.contratista=ko.observable(0);
    self.listado_contratista=ko.observableArray([]); 
    self.listado_departamento=ko.observableArray([]);
    self.listado_municipio=ko.observableArray([]);
    self.departamento=ko.observable(0);
    self.municipio=ko.observable(0);


     //paginacion de control de cambio
     self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(5),
        directiones: ko.observable(true),
        limite: ko.observable(true),
        cantidad_por_paginas: ko.observable(0),
        text: {
            first: ko.observable('Inicio'),
            last: ko.observable('Fin'),
            back: ko.observable('<'),
            forward: ko.observable('>')
        },
        totalRegistrosBuscados:ko.observable(0)
    }

    //paginacion
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }


    //funcion para filtrar en el cambio obra
    self.filtrar_proyecto = function () {
        self.titulo('Filtrar proyectos');
        self.consultar_macrocontrato();
        $('#modal_filtro_proyecto').modal('show');
    }


    //consultar los macrocontrato
    self.consultar_macrocontrato=function(){

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_contrato(datos.macrocontrato);

         }, path, parameter,function(){
                 self.macrocontrato_select(sessionStorage.getItem("mcontrato_filtro_control_cambio"));       
             },false,false);

    }


    //funcion que se ejecuta cuando se cambia en el select de contrato 
    self.macrocontrato_select.subscribe(function (value) {

        if(value >0){
            self.consultar_contratista(value);
            self.filtros_departamento(value,0);

        }else{

            self.listado_contratista([]);
            self.listado_departamento([]);
            self.listado_municipio([]);

        }
    });


    //consultar los nombre de los contratista segun el macrocontrato 
    self.consultar_contratista=function(value){

        if (value>0) {
             path =path_principal+'/proyecto/filtrar_proyectos/';
             parameter={ mcontrato:value, tipo:'8'};
             RequestGet(function (datos, estado, mensaje) {
              
                self.listado_contratista(datos.contratista);
               
             }, path, parameter,function(){
                         self.contratista(sessionStorage.getItem("contratista_filtro_control_cambio"));       
                     });
        }
         
    }


    //funcion que se ejecuta cuando se cambia en el select de contratista 
    self.contratista.subscribe(function (value) {
       
        if(value >0){
            self.filtros_departamento(self.macrocontrato_select(),value);

        }else{

            self.listado_departamento([]);
            self.listado_municipio([]);

        }
    });


    //consulta los departamentos por contrato y contratista
    self.filtros_departamento=function(contrato,contratista){

        if (contrato>0) {
             path =path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+contrato+'&contratista='+contratista;
             parameter='';
             RequestGet(function (results,count) {

                self.listado_departamento(results.departamento);    
                   
             }, path, parameter,function(){
                     self.departamento(sessionStorage.getItem("departamento_control_cambio"));       
                 });
        }
         
    }



    //funcion que se ejecuta cuando se cambia en el select de departamento
    self.departamento.subscribe(function (value) {

        if(value >0){

            self.filtros_municipio(self.macrocontrato_select(),self.contratista(),value);

        }else{
            self.listado_municipio([]);

        }
    });


    //consulta los municipios por contrato, contratista y departamento
    self.filtros_municipio=function(contrato,contratista,departamento){

        if (departamento>0) {
             path =path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+contrato+'&contratista='+contratista+'&departamento='+departamento;
             parameter='';
             RequestGet(function (results,count) {

                self.listado_municipio(results.municipio);       
                   
             }, path, parameter,function(){
                     self.municipio(sessionStorage.getItem("municipio_control_cambio"));       
                 });
        }
         
    }


    //funcion consultar 
    self.consultar = function (pagina) {
        
        //alert($('#mcontrato_filtro').val())
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("dato_control_cambio", $('#txtBuscar').val() || '');
            sessionStorage.setItem("municipio_control_cambio", $('#municipio_filtro').val() || '');
            sessionStorage.setItem("departamento_control_cambio", $('#departamento_filtro').val() || '');
            sessionStorage.setItem("contratista_filtro_control_cambio", $('#contratista_filtro').val() || '');            
            sessionStorage.setItem("mcontrato_filtro_control_cambio", $('#mcontrato_filtro').val() || '');

            self.cargar(pagina);
            
        }
    }

    self.cargar = function(pagina){

        let filtro = sessionStorage.getItem("dato_control_cambio");
        let municipio = sessionStorage.getItem("municipio_control_cambio");
        let departamento = sessionStorage.getItem("departamento_control_cambio");
        let contratista_filtro = sessionStorage.getItem("contratista_filtro_control_cambio") 
        let mcontrato_filtro = sessionStorage.getItem("mcontrato_filtro_control_cambio");

        var empresa=$("#empresa").val();

        path = path_principal+'/api/Proyecto_empresas_lite?format=json';
        parameter = { dato: filtro, page: pagina,
                        mcontrato:mcontrato_filtro,contratista:contratista_filtro, 
                        departamento:departamento, municipio:municipio,empresa:empresa};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)
                    cerrarLoading();

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter,undefined, false);

    }


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

}

var control_cambio = new ControlCambioViewModel();
ko.applyBindings(control_cambio);
