function AdministradorViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.parametro_registro = ko.observable('');
    self.url=path_principal+'/api/'; 
    self.macrocontrato_select=ko.observable(0);
    self.lista_contrato=ko.observableArray([]);
    self.listado_proyecto=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.contratista=ko.observable(0);
    self.listado_contratista=ko.observableArray([]); 
    self.listado_departamento=ko.observableArray([]);
    self.listado_municipio=ko.observableArray([]);
    self.departamento=ko.observable(0);
    self.municipio=ko.observable(0);
    

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

            self.lista_contrato(datos.mcontratos);
            self.listado_contratista(datos.contratistas);            
            self.listado_departamento(datos.departamentos);                         
                        
            self.macrocontrato_select(sessionStorage.getItem("mcontrato_filtro_admin_fotos")|| "");
            self.contratista(sessionStorage.getItem("contratista_filtro_admin_fotos")|| "");   
            self.departamento(sessionStorage.getItem("departamento_admin_fotos")|| "");
            self.municipio(sessionStorage.getItem("municipio_admin_fotos")|| "");                     
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
        if(val>0){
          self.consultar_contratistas_filtro();    
          self.consultar_departamento_filtro();          
        }else{
            self.consultar_select_filter_proyecto_filtro();             
            self.listado_municipio(null);            
            self.municipio("");
            //self.limpiar_filtro_proyecto();                                  
                
        }          
    });


    //funcion consultar los contratistas que tienen proyectos 
    self.consultar_contratistas_filtro = function () {                
            path = path_principal+'/proyecto/filtrar_proyectos/';
            parameter = { mcontrato : self.macrocontrato_select() || 0, tipo :8, tipo_contratista: true};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos.contratista!=null && datos.contratista.length > 0) {                    
                    self.listado_contratista(datos.contratista);                    
                    //self.contratista(sessionStorage.getItem("contratista_filtro_admin_fotos")|| "");            
                    if( sessionStorage.getItem("contratista_filtro_admin_fotos") != "" || sessionStorage.getItem("contratista_filtro_admin_fotos") != null || sessionStorage.getItem("contratista_filtro_admin_fotos") != undefined){
                        $('#contratista_filtro').val(sessionStorage.getItem("contratista_filtro_admin_fotos"))
                    }                    
                } else {                    
                    self.listado_contratista([]);
                }          
            }, path, parameter);        
    }


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
                //self.departamento_id(sessionStorage.getItem("departamento_admin_fotos")|| "");
                if(no_cargar==undefined){
                    if( sessionStorage.getItem("departamento_admin_fotos") != "" || sessionStorage.getItem("departamento_admin_fotos") != null || sessionStorage.getItem("departamento_admin_fotos") != undefined){
                    $('#departamento_filtro').val(sessionStorage.getItem("departamento_admin_fotos"))
                    }
                }
                                
            } else {
                self.listado_departamento([]);
            }          
        }, path, parameter);        
    }



    self.departamento.subscribe(function (val) {
        if((val!="") || (val!='')){            
          self.consultar_municipios_filtro();  
        }else{      
            self.listado_municipio([]);            
            self.municipio(0);           
        }          
    });


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
                self.municipio(sessionStorage.getItem("municipio_admin_fotos")|| "");      
                if( self.municipio() != "" || self.municipio() != null || self.municipio() != undefined){
                    $('#municipio_filtro').val(self.municipio())
                }                                   
            } else {
                self.listado_municipio([]);
            }             
            cerrarLoading();
        }, path, parameter);          
    }

   
       //funcion  consultar los proyecto
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            
            filtro = sessionStorage.getItem("dato_admin_fotos"); 
            mcontrato_filtro_admin_fotos = sessionStorage.getItem("mcontrato_filtro_admin_fotos")||self.macrocontrato_select();
            contratista_filtro_admin_fotos = sessionStorage.getItem("contratista_filtro_admin_fotos")||self.contratista();
            departamento_admin_fotos = sessionStorage.getItem("departamento_admin_fotos")||self.departamento();
            municipio_admin_fotos = sessionStorage.getItem("municipio_admin_fotos")||self.municipio();
            self.filtro($('#txtBuscar').val());            
            path = self.url+'Proyecto_empresas/?format=json';
            var empresa=$("#empresa").val();
            parameter = { dato: filtro
                          , page: pagina 
                          , empresa : empresa /*variable de la empresa actual del usuario */
                          , mcontrato : mcontrato_filtro_admin_fotos || 0
                          , departamento : departamento_admin_fotos || 0
                          , municipio : municipio_admin_fotos || 0
                          , contratista : contratista_filtro_admin_fotos || 0
                          , parametro_consulta_general : self.parametro_registro() };
            RequestGet(function (datos, estado, mensage) { 
                //self.listado_proyecto(datos.data.tipoContratos);               
                if (estado == 'ok' && datos.data.proyectos!=null && datos.data.proyectos.length > 0) {
                    self.mensaje('');                    
                    self.listado(agregarOpcionesObservable(datos.data.proyectos));                     
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
            //self.filtro($('#txtBuscar').val());          
            sessionStorage.setItem("mcontrato_filtro_admin_fotos",self.macrocontrato_select() || '');
            sessionStorage.setItem("departamento_admin_fotos",self.departamento() || '');
            sessionStorage.setItem("municipio_admin_fotos",self.municipio() || '');
            sessionStorage.setItem("contratista_filtro_admin_fotos",self.contratista() || '');
            sessionStorage.setItem("dato_admin_fotos", self.filtro() || '');
            self.consultar(pagina);
        } 

    }

    self.borrar = function (pagina){
        sessionStorage.setItem("mcontrato_filtro_admin_fotos", '');
        sessionStorage.setItem("departamento_admin_fotos", '');
        sessionStorage.setItem("municipio_admin_fotos", '');
        sessionStorage.setItem("contratista_filtro_admin_fotos", '');
        sessionStorage.setItem("dato_admin_fotos", '');  
        location.reload(); 
        self.consultar(pagina);                             
    }    
    self.setColorIconoFiltro = function (){
    	
        municipio_admin_fotos = parseInt(sessionStorage.getItem("municipio_admin_fotos"));
        departamento_admin_fotos = parseInt(sessionStorage.getItem("departamento_admin_fotos"));
        contratista_filtro_admin_fotos = parseInt(sessionStorage.getItem("contratista_filtro_admin_fotos"));
        mcontrato_filtro_admin_fotos = parseInt(sessionStorage.getItem("mcontrato_filtro_admin_fotos"));        

    	

        if ((municipio_admin_fotos!='' && municipio_admin_fotos > 0 && municipio_admin_fotos != null && !isNaN(municipio_admin_fotos)) || 
        	(departamento_admin_fotos != '' && departamento_admin_fotos > 0 && departamento_admin_fotos != null && !isNaN(departamento_admin_fotos)) || 
        	(contratista_filtro_admin_fotos != '' && contratista_filtro_admin_fotos > 0 && contratista_filtro_admin_fotos != null && !isNaN(contratista_filtro_admin_fotos)) ||
        	(mcontrato_filtro_admin_fotos!='' && mcontrato_filtro_admin_fotos!=null && !isNaN(mcontrato_filtro_admin_fotos))
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

var administrador = new AdministradorViewModel();
$('#txtBuscar').val(sessionStorage.getItem("dato_admin_fotos"))
ko.applyBindings(administrador);