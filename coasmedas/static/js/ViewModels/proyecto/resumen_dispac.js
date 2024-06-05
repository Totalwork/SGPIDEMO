
var highColors = ['#228BF5','#B522F5','#0EC11D'
    ];
    
function ResumenViewModel() {
    
    
    var self = this;
    self.listado_proyecto=ko.observableArray([]);
    self.mensaje_proyecto=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');

    self.macrocontrato_select=ko.observable(0);
    self.lista_contrato=ko.observableArray([]);
    self.contratista=ko.observable(0);
    self.listado_contratista=ko.observableArray([]); 
    self.listado_departamento=ko.observableArray([]);
    self.listado_municipio=ko.observableArray([]);
    self.departamento=ko.observable(0);
    self.proyecto=ko.observable(0);
    self.listado_contrato=ko.observableArray([]);

    self.valordepantiguio=ko.observable(0);
    self.valorcontrantiguo=ko.observable(0);
    self.macrovalorantiguo=ko.observable(0);
   
     //paginacion de cuenta
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
        self.consultar_proyectos_dispac(pagina);        
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }


        //funcion para filtrar los encabezado giros del tab consultar y modificar
    self.filtrar_proyecto = function () {
        self.titulo('Filtrar proyectos');
        $('#modal_filtro_proyecto').modal('show');
        self.consultar_macrocontrato_dispac();
        self.consultar_contratista(0);
        self.filtros_departamento(0,0);    
    }


    //funcion que se ejecuta cuando se cambia en el select de contrato 
    self.macrocontrato_select.subscribe(function (value) {

        // if(value >0){
        //     self.consultar_contratista(value);
        //     self.filtros_departamento(value,0);

        // }else{

        //     self.listado_contratista([]);
        //     self.listado_departamento([]);
        //     self.listado_municipio([]);

        // }

        if (value!=self.macrovalorantiguo()) {

            self.macrovalorantiguo(value)

            if(self.macrovalorantiguo() >0){
                self.consultar_contratista(value);
                self.filtros_departamento(value,0);

            }else{

                self.consultar_contratista(0);
                self.filtros_departamento(0,0);
                self.listado_municipio([]);

            }



        }   
    });


    //consultar los nombre de los contratista segun el macrocontrato 
    self.consultar_contratista=function(value){

         var empresa=$("#empresa").val();

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ mcontrato:value, tipo:'8', empresa_sin_logueo:empresa};
         RequestGetAutenticacion(function (datos, estado, mensaje) {
          
            self.listado_contratista(datos.contratista);
           
         }, path, parameter);
         
    }


    //funcion que se ejecuta cuando se cambia en el select de contratista 
    self.contratista.subscribe(function (value) {
       
        // if(value >0){
        //     self.filtros_departamento(self.macrocontrato_select(),value);

        // }else{

        //     self.listado_departamento([]);
        //     self.listado_municipio([]);

        // }

        if (value!=self.valorcontrantiguo()) {

            self.valorcontrantiguo(value)
       
            if( self.valorcontrantiguo() >0){
                self.filtros_departamento(self.macrocontrato_select(),value);

            }else{

                self.filtros_departamento(0,0);
                self.listado_municipio([]);

            }            
        }  

    });


    //consulta los departamentos por contrato y contratista
    self.filtros_departamento=function(contrato,contratista){

         var empresa=$("#empresa").val();

         path =path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+contrato+'&contratista='+contratista+'&empresa_sin_logueo='+empresa;
         parameter='';
         RequestGetAutenticacion(function (results,count) {

            self.listado_departamento(results.departamento);    
               
         }, path, parameter);
         
    }



    //funcion que se ejecuta cuando se cambia en el select de departamento
    self.departamento.subscribe(function (value) {

        // if(value >0){

        //     self.filtros_municipio(self.macrocontrato_select(),self.contratista(),value);

        // }else{
        //     self.listado_municipio([]);

        // }

        if (value!=self.valordepantiguio()) {

            self.valordepantiguio(value)

            if(self.valordepantiguio() >0){

                self.filtros_municipio(self.macrocontrato_select(),self.contratista(),value);

            }else{
                self.filtros_municipio(0,0,0);

            }         
        }

    });


    //consulta los municipios por contrato, contratista y departamento
    self.filtros_municipio=function(contrato,contratista,departamento){

         var empresa=$("#empresa").val();
         
         path =path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+contrato+'&contratista='+contratista+'&departamento='+departamento+'&empresa_sin_logueo='+empresa;
         parameter='';
         RequestGetAutenticacion(function (results,count) {

            self.listado_municipio(results.municipio);       
               
         }, path, parameter);
         
    }

    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar_proyectos_dispac(1);            
        }
        return true;
    }

        //funcion consultar los proyecto de dispac sin logueo
    self.consultar_proyectos_dispac = function (pagina) {

        var empresa=$("#empresa").val();

        if (pagina > 0) { 
            
            self.filtro($('#txtBuscar').val());

            path = path_principal+'/api/Proyecto_empresas_lite?format=json';
            parameter = { dato: self.filtro(), page: pagina, 
                mcontrato:self.macrocontrato_select(), 
                contratista:self.contratista(), departamento:self.departamento(), 
                municipio:$("#municipio_filtro").val(),empresa:empresa};

            RequestGetAutenticacion(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje_proyecto('');
                    self.listado_proyecto(agregarOpcionesObservable(datos.data));
                    cerrarLoading();    

                } else {
                    self.listado_proyecto([]);
                    self.mensaje_proyecto(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();  
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter,undefined, false);
        } 
    }



    //consultar los macrocontrato de dispac sin logueo
    self.consultar_macrocontrato_dispac=function(){

         var empresa=$("#empresa").val();

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12', empresa_sin_logueo:empresa };
         RequestGetAutenticacion(function (datos, estado, mensaje) {
           
            self.lista_contrato(datos.macrocontrato);

         }, path, parameter,undefined,false,false);

    }

}

var resumen = new ResumenViewModel();
ko.applyBindings(resumen);
