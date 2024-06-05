
function GpsViewModel() {
    
    var self = this;
    self.parametro_registro = ko.observable('');
    self.mensaje = ko.observable('');
    self.listado_proyecto=ko.observableArray([]); 
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.url=path_principal+'/api/'; 
    self.macrocontrato_select=ko.observable(0);
    self.lista_contrato=ko.observableArray([]);
    self.contratista=ko.observable(0);
    self.listado_contratista=ko.observableArray([]); 
    self.listado_departamento=ko.observableArray([]);
    self.listado_municipio=ko.observableArray([]);
    self.departamento=ko.observable(0);
    self.municipio=ko.observable(0);

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

            self.cargar(pagina);            
        
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {


        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }


    //funcion para filtrar en los puntos gps    
    self.filtrar_proyecto = function () {
        self.titulo('Filtrar proyectos');        
        self.consultar_select_filter_proyecto();
        $('#modal_filtro_proyecto').modal('show');
        // self.consultar_macrocontrato();
        // self.consultar_contratista(0);
        // self.filtros_departamento(0,0);        
    }


    self.consultar_select_filter_proyecto = function (pagina) { 

        path = path_principal+'/proyecto/select-filter-proyecto/';
        parameter = {consulta_departamento:1 };
        RequestGet(function (datos, estado, mensage) {

            self.lista_contrato(datos.mcontratos);
            self.listado_contratista(datos.contratistas);            
            self.listado_departamento(datos.departamentos);                         
                        
            self.macrocontrato_select(sessionStorage.getItem("mcontrato_filtro_punto_gps")|| "");
            self.contratista(sessionStorage.getItem("contratista_filtro_punto_gps")|| "");   
            self.departamento(sessionStorage.getItem("departamento_punto_gps")|| "");
            self.municipio(sessionStorage.getItem("municipio_punto_gps")|| "");                     
            cerrarLoading();
        }, path, parameter,undefined,false);                
    }
   
   //consultar los macrocontrato
    self.consultar_macrocontrato=function(){
        
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: 12 };
         RequestGet(function (datos, estado, mensaje) {
            if (estado == 'ok' && datos.macrocontrato!=null && datos.macrocontrato.length > 0) {
                self.lista_contrato(datos.macrocontrato);
            } else {
                self.lista_contrato([]);
            }                        

         }, path, parameter, undefined , false , false);

    }

    self.consultar_select_filter_proyecto_filtro = function (val_mcontrato) { 

        path = path_principal+'/proyecto/select-filter-proyecto/';
        parameter = {consulta_departamento:1 };
        RequestGet(function (datos, estado, mensage) {

            // self.listado_contratista_filtro(datos.contratistas);
            // self.listado_departamentos_filtro(datos.departamentos);
            // self.listado_municipios_filtro([]);
            // self.macrocontrato_select(0);
            // self.contratista(0);     
            // self.departamento(0);
            // self.municipio(0);
            if(val_mcontrato==undefined){
                self.lista_contrato(datos.mcontratos);
                self.listado_contratista(datos.contratistas);
                self.listado_departamento(datos.departamentos);
                self.listado_municipio([]);
                self.macrocontrato_select("");
                self.contratista("");     
                self.departamento("");
           
            }else{
                //self.listado_contratista_filtro(datos.contratistas);
                self.listado_departamento(datos.departamentos);
                self.contratista("");          
                self.departamento("");
       
            }                                            
            
                                  
            cerrarLoading();
        }, path, parameter,undefined,false);                
    }
     
     
     //funcion que se ejecuta cuando se cambia en el select de contratos
    self.macrocontrato_select.subscribe(function (val) {

        if(val!=""){
        //alert('+'+val);
          self.consultar_contratistas_filtro();    
          self.consultar_departamento_filtro();          
        }else{
            //alert('-'+val);
            self.consultar_select_filter_proyecto_filtro();             
            self.listado_municipio(null);            
            
            self.municipio("");
            //self.limpiar_filtro_proyecto();                                  
                
        }          
    });

    self.contratista.subscribe(function (val) {        
        if(val!=""){      
            self.consultar_departamento_filtro();
        }else{
            if(self.macrocontrato_select()==""){
                self.consultar_select_filter_proyecto_filtro(1);                              
            }else{
                self.consultar_departamento_filtro(1); 
                self.departamento("");

            }
            self.listado_municipio(null);
            self.departamento(0);                                                                                  
        }
        
            
    }); 

    self.departamento.subscribe(function (val) {
        if((val!="") || (val!='')){            
          self.consultar_municipios_filtro();  
        }else{      
            self.listado_municipio([]);            
            self.municipio(0);           
        }          
    });

    //funcion consultar los contratistas que tienen proyectos 
    self.consultar_contratistas_filtro = function () {                
            path = path_principal+'/proyecto/filtrar_proyectos/';
            parameter = { mcontrato : self.macrocontrato_select() || 0, tipo :8, tipo_contratista: true};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos.contratista!=null && datos.contratista.length > 0) {                    
                    self.listado_contratista(datos.contratista);                    
                    //self.contratista(sessionStorage.getItem("contratista_filtro_punto_gps")|| "");            
                    if( sessionStorage.getItem("contratista_filtro_punto_gps") != "" || sessionStorage.getItem("contratista_filtro_punto_gps") != null || sessionStorage.getItem("contratista_filtro_punto_gps") != undefined){
                        $('#contratista_filtro').val(sessionStorage.getItem("contratista_filtro_punto_gps"))
                    }                    
                } else {                    
                    self.listado_contratista([]);
                }          
            }, path, parameter);        
    }




    //consulta los departamentos por contrato y contratista
    self.consultar_departamento_filtro = function (no_cargar) {                
        path = path_principal+'/proyecto/filtrar_proyectos/';
        
        parameter = {
            mcontrato:self.macrocontrato_select() || 0, 
            contratista:self.contratista() || 0
        };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos.departamento!=null && datos.departamento.length > 0) {                
                self.listado_departamento(datos.departamento);
                //self.departamento_id(sessionStorage.getItem("departamento_punto_gps")|| "");
                if(no_cargar==undefined){
                    if( sessionStorage.getItem("departamento_punto_gps") != "" || sessionStorage.getItem("departamento_punto_gps") != null || sessionStorage.getItem("departamento_punto_gps") != undefined){
                    $('#departamento_filtro').val(sessionStorage.getItem("departamento_punto_gps"))
                    }
                }
                                
            } else {
                self.listado_departamento([]);
            }          
        }, path, parameter);        
    }






    //funcion consultar municipios
    self.consultar_municipios_filtro = function () {                
        path = path_principal+'/proyecto/filtrar_proyectos/';
        parameter = { 
            mcontrato : self.macrocontrato_select() || 0,
            departamento : self.departamento() || 0,
            contratista : self.contratista() || 0
        };        
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos.municipio!=null && datos.municipio.length > 0) {
                self.listado_municipio(datos.municipio);  
                self.municipio(sessionStorage.getItem("municipio_punto_gps")|| "");      
                if( self.municipio() != "" || self.municipio() != null || self.municipio() != undefined){
                    $('#municipio_filtro').val(self.municipio())
                }                                   
            } else {
                self.listado_municipio([]);
            }             
            cerrarLoading();
        }, path, parameter);          
    }

   
    //funcion consultar proyectos que ppuede  ver la empresa
    self.consultar = function (pagina) {
        if (pagina > 0) {
            filtro = sessionStorage.getItem("dato_punto_gps"); 
            mcontrato_filtro_resumen_gps = sessionStorage.getItem("mcontrato_filtro_punto_gps")||self.macrocontrato_select();
            contratista_filtro_resumen_gps = sessionStorage.getItem("contratista_filtro_punto_gps")||self.contratista();
            departamento_resumen_gps = sessionStorage.getItem("departamento_punto_gps")||self.departamento();
            municipio_resumen_gps = sessionStorage.getItem("municipio_punto_gps")||self.municipio();
            self.filtro($('#txtBuscar').val());            
            //path = self.url+'Proyecto_empresas/?format=json';            
            path = path_principal+'/api/Proyecto_empresas/?format=json';
            var empresa=$("#empresa").val();            
            parameter = { dato: filtro, page: pagina, 
                mcontrato:mcontrato_filtro_resumen_gps, 
                contratista:contratista_filtro_resumen_gps, departamento:departamento_resumen_gps, 
                municipio:municipio_resumen_gps,empresa:empresa,superLite:1};            
            RequestGet(function (datos, estado, mensage) { 
                //self.listado_proyecto(datos.data.tipoContratos);                               
                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');                                        
                    self.listado(agregarOpcionesObservable(datos.data));                     
                } else {
                    //self.listado_proyecto([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    self.listado([]);
                }

                self.llenar_paginacion(datos,pagina);                
                cerrarLoading();
                self.setColorIconoFiltro();
                $('#modal_filtro_proyecto').modal('hide');                
            }, path, parameter,undefined,false);
        }        
    }

    
    self.cargar = function(pagina){ 
        if (pagina > 0) {   
            self.filtro($('#txtBuscar').val());          
            sessionStorage.setItem("mcontrato_filtro_punto_gps",self.macrocontrato_select() || '');
            sessionStorage.setItem("departamento_punto_gps",self.departamento() || '');
            sessionStorage.setItem("municipio_punto_gps",self.municipio() || '');
            sessionStorage.setItem("contratista_filtro_punto_gps",self.contratista() || '');
            sessionStorage.setItem("dato_punto_gps", $('#txtBuscar').val() || '');
            self.consultar(pagina);
        }              
    }
    
    self.borrar = function (pagina){
        sessionStorage.setItem("mcontrato_filtro_punto_gps", '');
        sessionStorage.setItem("departamento_punto_gps", '');
        sessionStorage.setItem("municipio_punto_gps", '');
        sessionStorage.setItem("contratista_filtro_punto_gps", '');
        sessionStorage.setItem("dato_punto_gps", '');  
        location.reload(); 
        self.consultar(pagina);                             
    }    
    self.setColorIconoFiltro = function (){
    	
        municipio_resumen_gps = parseInt(sessionStorage.getItem("municipio_punto_gps"));
        departamento_resumen_gps = parseInt(sessionStorage.getItem("departamento_punto_gps"));
        contratista_filtro_resumen_gps = parseInt(sessionStorage.getItem("contratista_filtro_punto_gps"));
        mcontrato_filtro_resumen_gps = parseInt(sessionStorage.getItem("mcontrato_filtro_punto_gps"));        

    	

        if ((municipio_resumen_gps!='' && municipio_resumen_gps > 0 && municipio_resumen_gps != null && !isNaN(municipio_resumen_gps)) || 
        	(departamento_resumen_gps != '' && departamento_resumen_gps > 0 && departamento_resumen_gps != null && !isNaN(departamento_resumen_gps)) || 
        	(contratista_filtro_resumen_gps != '' && contratista_filtro_resumen_gps > 0 && contratista_filtro_resumen_gps != null && !isNaN(contratista_filtro_resumen_gps)) ||
        	(mcontrato_filtro_resumen_gps!='' && mcontrato_filtro_resumen_gps!=null && !isNaN(mcontrato_filtro_resumen_gps))
        	){

            $('#iconoFiltro').addClass("filtrado");
        }else{
            $('#iconoFiltro').removeClass("filtrado");
        }
    }

    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.cargar(1);
        }
        return true;
    }


}

var gps = new GpsViewModel();
$('#txtBuscar').val(sessionStorage.getItem("dato_punto_gps"))
ko.applyBindings(gps);