var highColors = ['#228BF5','#B522F5','#0EC11D'
    ];
    
function ResumenViewModel() {
    
    
    var self = this;
    self.parametro_registro = ko.observable('');         
    self.listado_proyecto=ko.observableArray([]);
    self.mensaje_proyecto=ko.observable('');
    self.titulo=ko.observable('');
    self.url=path_principal+'/api/'; 
    self.listado_macro_contrato_filtro = ko.observableArray([]);
    self.listado_contratista_filtro = ko.observableArray([]);
    self.listado_departamentos_filtro = ko.observableArray([]);    
    self.listado_municipios_filtro = ko.observableArray([]);    
    self.filtro=ko.observable('');
    self.listado=ko.observableArray([]);
    self.macrocontrato_select=ko.observable(0);
    self.lista_contrato=ko.observableArray([]);
    self.contratista=ko.observable(0);
    self.listado_contratista=ko.observableArray([]); 
    self.listado_departamento=ko.observableArray([]);
    self.listado_municipio=ko.observableArray([]);
    self.departamento=ko.observable(0);
    self.listado_contrato=ko.observableArray([]);
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


    //funcion para filtrar los encabezado giros del tab consultar y modificar
    self.filtrar_proyecto = function () {
        self.titulo('Filtrar proyectos');
        $('#modal_filtro_proyecto').modal('show');
        self.consultar_select_filter_proyecto();
        // self.consultar_macrocontrato();
        // self.consultar_contratista(0);
        // self.filtros_departamento(0,0);        
    }

    self.consultar_select_filter_proyecto = function (pagina) { 

        path = path_principal+'/proyecto/select-filter-proyecto/';
        parameter = {consulta_departamento:1 };
        RequestGet(function (datos, estado, mensage) {

            self.listado_macro_contrato_filtro(datos.mcontratos);
            self.listado_contratista_filtro(datos.contratistas);            
            self.listado_departamentos_filtro(datos.departamentos);                         
                        
            self.macrocontrato_select(sessionStorage.getItem("mcontrato_filtro_resumen")|| "");
            self.contratista(sessionStorage.getItem("contratista_filtro_resumen")|| "");   
            self.departamento(sessionStorage.getItem("departamento_resumen")|| "");
            self.municipio(sessionStorage.getItem("municipio_resumen")|| "");                     
            cerrarLoading();
        }, path, parameter,undefined,false);                
    }    
    //funcion consultar los contratos que tienen proyecto
    self.consultar_mcontratos_filtro = function () {                
            path = path_principal+'/proyecto/filtrar_proyectos/';
            parameter = { tipo : 12 };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.macrocontrato!=null && datos.macrocontrato.length > 0) {
                    self.listado_macro_contrato_filtro(datos.macrocontrato);
                } else {
                    self.listado_macro_contrato_filtro([]);
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
                self.listado_macro_contrato_filtro(datos.mcontratos);
                self.listado_contratista_filtro(datos.contratistas);
                self.listado_departamentos_filtro(datos.departamentos);
                self.listado_municipios_filtro([]);
                self.macrocontrato_select("");
                self.contratista("");     
                self.departamento("");
           
            }else{
                //self.listado_contratista_filtro(datos.contratistas);
                self.listado_departamentos_filtro(datos.departamentos);
                self.contratista("");          
                self.departamento("");
       
            }                                            
            
                                  
            cerrarLoading();
        }, path, parameter,undefined,false);                
    }
    self.limpiar_filtro_proyecto=function(){        
        self.filtro('');
        self.macrocontrato_select('');
        self.contratista('');
        self.departamento('');
        self.municipio('');

        //self.filtro_proyectoVO.dato.isModified(false);
        // self.filtro_proyectoVO.mcontrato_id.isModified(false);
        // self.filtro_proyectoVO.contratista_id.isModified(false);
        // self.filtro_proyectoVO.departamento_id.isModified(false);
        // self.filtro_proyectoVO.municipio_id.isModified(false);
     } 



    //funcion que se ejecuta cuando se cambia en el select de contratos
    self.macrocontrato_select.subscribe(function (val) {
        if(val!=""){
          self.consultar_contratistas_filtro();    
          self.consultar_departamento_filtro();
        }else{
            self.consultar_select_filter_proyecto_filtro();             
            self.listado_municipios_filtro(null);
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
            self.listado_municipios_filtro(null);
            self.municipio(0);                                                
        }
        
            
    }); 


    self.departamento.subscribe(function (val) {
        if((val!="") || (val!='')){          
          self.consultar_municipios_filtro();  
        }else{      
            self.listado_municipios_filtro([]);
            self.municipio(0);
        }          
      });


    //funcion consultar los contratistas que tienen proyectos 
    self.consultar_contratistas_filtro = function () {                
            path = path_principal+'/proyecto/filtrar_proyectos/';
            parameter = { mcontrato : self.macrocontrato_select() || 0, tipo :8, tipo_contratista: true};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos.contratista!=null && datos.contratista.length > 0) {                    
                    self.listado_contratista_filtro(datos.contratista);                    
                    //self.contratista(sessionStorage.getItem("contratista_filtro_resumen")|| "");            
                    if( sessionStorage.getItem("contratista_filtro_resumen") != "" || sessionStorage.getItem("contratista_filtro_resumen") != null || sessionStorage.getItem("contratista_filtro_resumen") != undefined){
                        $('#contratista_filtro').val(sessionStorage.getItem("contratista_filtro_resumen"))
                    }                    
                } else {                    
                    self.listado_contratista_filtro([]);
                }          
            }, path, parameter);        
    }
    
    self.consultar_departamento_filtro = function (no_cargar) {                
        path = path_principal+'/proyecto/filtrar_proyectos/';
        
        parameter = {
            mcontrato:self.macrocontrato_select() || 0, 
            contratista:self.contratista() || 0
        };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos.departamento!=null && datos.departamento.length > 0) {                
                self.listado_departamentos_filtro(datos.departamento);
                //self.departamento_id(sessionStorage.getItem("departamento_resumen")|| "");
                if(no_cargar==undefined){
                    if( sessionStorage.getItem("departamento_resumen") != "" || sessionStorage.getItem("departamento_resumen") != null || sessionStorage.getItem("departamento_resumen") != undefined){
                    $('#departamento_filtro').val(sessionStorage.getItem("departamento_resumen"))
                    }
                }
                                
            } else {
                self.listado_departamentos_filtro([]);
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
                self.listado_municipios_filtro(datos.municipio);  
                self.municipio(sessionStorage.getItem("municipio_resumen")|| "");      
                if( self.municipio() != "" || self.municipio() != null || self.municipio() != undefined){
                    $('#municipio_filtro').val(self.municipio())
                }                                   
            } else {
                self.listado_municipios_filtro([]);
            }             
            cerrarLoading();
        }, path, parameter);          
    } 

    //funcion consultar proyectos que ppuede  ver la empresa
    self.consultar = function (pagina) {
        if (pagina > 0) {
            filtro = sessionStorage.getItem("dato_resumen"); 
            mcontrato_filtro_resumen = sessionStorage.getItem("mcontrato_filtro_resumen")||self.macrocontrato_select();
            contratista_filtro_resumen = sessionStorage.getItem("contratista_filtro_resumen")||self.contratista();
            departamento_resumen = sessionStorage.getItem("departamento_resumen")||self.departamento();
            municipio_resumen = sessionStorage.getItem("municipio_resumen")||self.municipio();
            self.filtro($('#txtBuscar').val());            
            path = self.url+'Proyecto_empresas/?format=json';
            var empresa=$("#empresa").val();
            parameter = { dato: filtro
                          , page: pagina 
                          , empresa : empresa /*variable de la empresa actual del usuario */
                          , mcontrato : mcontrato_filtro_resumen || 0
                          , departamento : departamento_resumen || 0
                          , municipio : municipio_resumen || 0
                          , contratista : contratista_filtro_resumen || 0
                          , parametro_consulta_general : self.parametro_registro() };
            RequestGet(function (datos, estado, mensage) { 
                //self.listado_proyecto(datos.data.tipoContratos);               
                if (estado == 'ok' && datos.data.proyectos!=null && datos.data.proyectos.length > 0) {
                    self.mensaje_proyecto('');                    
                    self.listado(agregarOpcionesObservable(datos.data.proyectos));                     
                } else {
                    //self.listado_proyecto([]);
                    self.mensaje_proyecto(mensajeNoFound);//mensaje_proyecto not found se encuentra el el archivo call-back.js
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
            sessionStorage.setItem("mcontrato_filtro_resumen",self.macrocontrato_select() || '');
            sessionStorage.setItem("departamento_resumen",self.departamento() || '');
            sessionStorage.setItem("municipio_resumen",self.municipio() || '');
            sessionStorage.setItem("contratista_filtro_resumen",self.contratista() || '');
            sessionStorage.setItem("dato_resumen", $('#txtBuscar').val() || '');
            self.consultar(pagina);
        }              
    }    

    self.borrar = function (pagina){
        sessionStorage.setItem("mcontrato_filtro_resumen", '');
        sessionStorage.setItem("departamento_resumen", '');
        sessionStorage.setItem("municipio_resumen", '');
        sessionStorage.setItem("contratista_filtro_resumen", '');
        sessionStorage.setItem("dato_resumen", '');  
        location.reload(); 
        self.consultar(pagina);                             
    }
    self.setColorIconoFiltro = function (){
    	
        municipio_resumen = sessionStorage.getItem("municipio_resumen");
        departamento_resumen = sessionStorage.getItem("departamento_resumen");
        contratista_filtro_resumen = sessionStorage.getItem("contratista_filtro_resumen");
        mcontrato_filtro_resumen = sessionStorage.getItem("mcontrato_filtro_resumen");        

    	

        if ((municipio_resumen!='' && municipio_resumen != 0 && municipio_resumen != null) || 
        	(departamento_resumen != '' && departamento_resumen !=0 && departamento_resumen != null) || 
        	(contratista_filtro_resumen != '' && contratista_filtro_resumen !=0 && contratista_filtro_resumen != null) ||
        	(mcontrato_filtro_resumen!='' && mcontrato_filtro_resumen!=null)
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

var resumen = new ResumenViewModel();
$('#txtBuscar').val(sessionStorage.getItem("dato_resumen"))
ko.applyBindings(resumen);