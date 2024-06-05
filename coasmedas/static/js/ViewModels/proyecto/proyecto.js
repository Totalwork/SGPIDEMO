function ProyectoViewModel() {
	
    administraccion_de_recurso = 12;
    usuarioActual = $("#user").val();
    empresaActual = $("#company").val();

    var self = this;
    self.parametro_registro = ko.observable('');

    self.cargo_id = ko.observable('');
    self.cargo_responsable_id = ko.observable('');

    self.empresa_id = ko.observable('');
    self.empresaAsignada_id =ko.observable('');
    self.municipio_id =ko.observable(0);
    self.tipoContrato_id =ko.observable('');
    self.tipoContratoAsignados_id =ko.observable('');
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.mensajePorAsignar=ko.observable('');
    self.mensajeAsignados=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.contratista_id_filtro =ko.observable('');
    self.mcontrato_id_filtro =ko.observable('');
 
    self.filtro_contratista_proyecto = ko.observable('');
    self.filtro_empresa = ko.observable('');
    self.filtro_empresa_proyecto = ko.observable('');
    self.filtro_contrato = ko.observable('');
    self.filtro_contrato_proyecto = ko.observable('');
    self.filtro_funcionario = ko.observable('');
    self.filtro_funcionario_proyecto = ko.observable('');

    self.checkall=ko.observable(false);
    self.checkallEmpresas=ko.observable(false);
    self.checkallContratos=ko.observable(false);
    self.checkallResponsables=ko.observable(false);

    self.checkallProyectoEmpresas=ko.observable(false);
    self.checkallProyectoContratos=ko.observable(false);
    self.checkallProyectoContratistas=ko.observable(false);
    self.checkallProyectoResponsables=ko.observable(false);
    self.url=path_principal+'/api/';  
    self.url_funcion=path_principal+'/proyecto/';  
    self.list_contratistas = ko.observable('');

    //VARIABLES
    self.app_proyecto = 'proyecto';
    self.app_cuenta = 'cuenta';
    self.app_proyecto_obra = 'proyecto_obra';
    self.app_contratista = 'contratista';
    self.app_contrato = 'contrato';

    //DATOS arrays
    self.listado_bancos = ko.observableArray([]);
    
    self.listado_departamentos = ko.observableArray([]);
    self.listado_departamentos_filtro = ko.observableArray([]);
    self.listado_municipios_filtro = ko.observableArray([]);
    self.listado_municipios = ko.observableArray([]);
    
    self.listado_cargos = ko.observableArray([]);
    self.listado_campo_info_tecnica = ko.observableArray([]);
    self.listado_empresas_tabla = ko.observableArray([]);
    self.listado_contratos_tabla = ko.observableArray([]);
    self.listado_responsables_tabla = ko.observableArray([]);
    self.listado_cargos_select = ko.observableArray([]);
    self.listado_macro_contrato = ko.observableArray([]);

    self.listado_macro_contrato_filtro = ko.observableArray([]);
    self.listado_contratista_filtro = ko.observableArray([]);

    self.listado_tipos_cuenta = ko.observableArray([]);
    self.listado_tipos_proyecto = ko.observableArray([]);
    self.listado_tipos_contrato = ko.observableArray([]);

    self.listado_estados_proyecto = ko.observableArray([]);
    self.listado_estados_obra = ko.observableArray([]);
    
    self.listado_proyecto_contratistas = ko.observableArray([]);
    self.listado_proyecto_empresas = ko.observableArray([]);
    self.listado_proyecto_empresas_select = ko.observableArray([]);

    self.listado_proyecto_responsables = ko.observableArray([]);
    self.listado_proyecto_contratos = ko.observableArray([]);
    self.listado_proyecto_info_tecnica = ko.observableArray([]);
    
	 //Representa un modelo de la tabla proyecto
    self.proyectoVO={
	 	id:ko.observable(0),
	 	nombre:ko.observable('').extend({ required: { message: ' Digite el nombre del proyecto.' } }),
        mcontrato_id:ko.observable(''),
        No_cuenta:ko.observable(''),        
        tipo_cuenta_id:ko.observable(''),
        estado_proyecto_id:ko.observable('').extend({ required: { message: ' Seleccione el estado del proyecto.' } }),
        valor_adjudicado:ko.observable(0).money().extend({ required: { message: ' Digite el valor adjudicado.' } }),
        tipo_proyecto_id:ko.observable('').extend({ required: { message: ' Seleccione el tipo de proyecto.' } }),
        entidad_bancaria_id:ko.observable(''),
        municipio_id:ko.observable('').extend({ required: { message: ' Seleccione el municipio del proyecto.' } }),
        departamento_id:ko.observable('').extend({ required: { message: ' Seleccione el departamento del proyecto.' } }),

        fecha_inicio:ko.observable(''),
        fecha_fin:ko.observable(''),

	 };
   //INFORMACION DE LAS EMPRESAS
   self.proyecto_empresaVO = {
        id: ko.observable(0),
        propietario: ko.observable(0),
        proyecto_id: ko.observable(''), 
        empresa_id: ko.observableArray([]),            
    };
   //INFORMACIONES DE RESPONSABLES
   self.proyecto_responsableVO = {
        id: ko.observable(0),
        proyecto_id: ko.observable(''),
        funcionario_id: ko.observableArray([]),   
    }; 
   //INFORMACION DE LOS CONTRATOS
   self.proyecto_contratoVO = {
        id: ko.observable(0),
        proyecto_id: ko.observable(''),
        contrato_id: ko.observableArray([]),   
    };

   self.filtro_proyectoVO={
        dato:ko.observable(''),
        mcontrato_id:ko.observable(''),
        contratista_id:ko.observable(''),
        departamento_id:ko.observable(''),
        municipio_id:ko.observable(''),
    };

   //INFORMACION TECNICA DEL PROYECTO
   self.proyecto_info_tecnicaVO = {
        id: ko.observable(0),
        campo_id: ko.observable('').extend({ required: { message: ' Seleccione el campo tecnico.' } }),
        proyecto_id: ko.observable(''),
        valor_diseno: ko.observable('').extend({ required: { message: ' Digite el valor del diseño.' } }),
        valor_ejecucion: ko.observable('').extend({ required: { message: ' Digite el valor de ejecucion.' } }),
        valor_replanteo: ko.observable('').extend({ required: { message: ' Digite el valor de replanteo.' } }),
    };

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
        }
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {    
       self.cargar(pagina);
    });

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Proyecto');
        $('#modal_acciones').modal('show');
        /*self.consultar_macro_contrato(0,0);*/
        self.consultar_select_create_update_proyecto();
    }

    self.abrir_modal_busqueda = function () {
        self.consultar_select_filter_proyecto();
        $('#modal_acciones_busqueda').modal('show');        
    }

    self.consultar_select_create_update_proyecto = function (pagina) {
 
            path = path_principal+'/proyecto/select-create-update-proyecto/';
            parameter = { };
            RequestGet(function (datos, estado, mensage) {

                self.listado_macro_contrato(datos.mcontratos);
                self.listado_contratista_filtro(datos.contratistas);
                self.list_contratistas(datos.contratistas);
                self.listado_bancos(datos.bancos);
                self.listado_tipos_cuenta(datos.tipoCuentas);
                self.listado_tipos_proyecto(datos.tipoProyectos);
                self.listado_estados_proyecto(datos.estadoProyectos);
                self.listado_departamentos(datos.departamentos);
                self.listado_tipos_contrato(datos.tipoContratos);

                cerrarLoading();
            }, path, parameter,undefined,false);        
    }

    self.consultar_select_filter_proyecto = function (pagina) { 

        path = path_principal+'/proyecto/select-filter-proyecto/';
        parameter = {consulta_departamento:1 };
        RequestGet(function (datos, estado, mensage) {

            self.listado_macro_contrato_filtro(datos.mcontratos);
            self.listado_contratista_filtro(datos.contratistas);
            //self.list_contratistas(datos.contratistas);
            self.listado_departamentos_filtro(datos.departamentos);                         
                        
            self.mcontrato_id_filtro(sessionStorage.getItem("app_mcontrato")|| "");
            // if( self.mcontrato_id_filtro() != "" || self.mcontrato_id_filtro() != null || self.mcontrato_id_filtro() != undefined){
            //     $('#mcontrato_id_select').val(self.mcontrato_id_filtro());            
            // }

            self.filtro_proyectoVO.contratista_id(sessionStorage.getItem("app_proyecto_contratista")|| "");            
            // if( self.filtro_proyectoVO.contratista_id() != "" || self.filtro_proyectoVO.contratista_id() != null || self.filtro_proyectoVO.contratista_id() != undefined){
            //     $('#contratista_id_select').val(self.filtro_proyectoVO.contratista_id())
            // } 
            
            self.filtro_proyectoVO.departamento_id(sessionStorage.getItem("app_departamento")|| "");
            // if( self.filtro_proyectoVO.departamento_id() != "" || self.filtro_proyectoVO.departamento_id() != null || self.filtro_proyectoVO.departamento_id() != undefined){
            //     $('#departamento_id_select').val(self.filtro_proyectoVO.departamento_id())
            // }

            self.filtro_proyectoVO.municipio_id(sessionStorage.getItem("app_municipio")|| "");      
            // if( self.filtro_proyectoVO.municipio_id() != "" || self.filtro_proyectoVO.municipio_id() != null || self.filtro_proyectoVO.municipio_id() != undefined){
            //     $('#municipio_id_select').val(self.filtro_proyectoVO.municipio_id())
            // }                       
            cerrarLoading();
        }, path, parameter,undefined,false);                
    }

    self.consultar_select_filter_proyecto_filtro = function (val_mcontrato) { 

        path = path_principal+'/proyecto/select-filter-proyecto/';
        parameter = {consulta_departamento:1 };
        RequestGet(function (datos, estado, mensage) {


            if(val_mcontrato==undefined){
                self.listado_macro_contrato_filtro(datos.mcontratos);
                self.listado_contratista_filtro(datos.contratistas);
                self.listado_departamentos_filtro(datos.departamentos);
                self.mcontrato_id_filtro("");
                self.filtro_proyectoVO.contratista_id("");     
  
                self.filtro_proyectoVO.departamento_id("");
            }else{
                //self.listado_contratista_filtro(datos.contratistas);
                self.listado_departamentos_filtro(datos.departamentos);
                self.filtro_proyectoVO.contratista_id("");          
  
                self.filtro_proyectoVO.departamento_id("");
            }                                            
            
 
            
                      
            cerrarLoading();
        }, path, parameter,undefined,false);                
    }    

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }
    //exportar excel    
    self.exportar_excel=function(){
        location.href=self.url_funcion+"reporte_proyecto?dato="+self.filtro_proyectoVO.dato()+"&mcontrato="+self.mcontrato_id_filtro()+"&contratista="+self.filtro_proyectoVO.contratista_id()+"&empresa_id="+empresaActual;
    }   
    // //limpiar el modelo 
     self.limpiar=function(){    	 
         
        self.proyectoVO.id(0);
        self.proyectoVO.nombre('');
        self.proyectoVO.No_cuenta('');
        self.proyectoVO.valor_adjudicado('');
        self.proyectoVO.fecha_inicio('');    
        self.proyectoVO.fecha_fin('');                  
        self.proyectoVO.mcontrato_id('');
        self.proyectoVO.tipo_proyecto_id('');             
        self.proyectoVO.departamento_id('');
        self.proyectoVO.municipio_id('');            
        self.proyectoVO.entidad_bancaria_id('');      
        self.proyectoVO.tipo_cuenta_id('');
        self.proyectoVO.estado_proyecto_id('');

        self.proyectoVO.tipo_proyecto_id.isModified(false);
        self.proyectoVO.nombre.isModified(false);
        self.proyectoVO.No_cuenta.isModified(false);
        self.proyectoVO.estado_proyecto_id.isModified(false);
        self.proyectoVO.tipo_cuenta_id.isModified(false);
        self.proyectoVO.mcontrato_id.isModified(false);
        self.proyectoVO.departamento_id.isModified(false);
        self.proyectoVO.municipio_id.isModified(false);
        self.proyectoVO.valor_adjudicado.isModified(false);
     }
     self.limpiar_filtro_proyecto=function(){    	 
        self.filtro_proyectoVO.dato('');
        self.filtro_proyectoVO.mcontrato_id('');
        self.filtro_proyectoVO.contratista_id('');
        self.filtro_proyectoVO.departamento_id('');
        self.filtro_proyectoVO.municipio_id('');

        //self.filtro_proyectoVO.dato.isModified(false);
        // self.filtro_proyectoVO.mcontrato_id.isModified(false);
        // self.filtro_proyectoVO.contratista_id.isModified(false);
        // self.filtro_proyectoVO.departamento_id.isModified(false);
        // self.filtro_proyectoVO.municipio_id.isModified(false);
     }     
    // //funcion guardar
     self.guardar=function(){

    	if (ProyectoViewModel.errores_proyecto().length == 0) {//se activa las validaciones
            if(self.proyectoVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.filtro("");
                            self.cargar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url+'Proyecto/',//url api
                     parametros:self.proyectoVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                              self.filtro("");
                              self.cargar(self.paginacion.pagina_actual());
                              $('#modal_acciones').modal('hide');
                              self.limpiar();
                            } 
                       },//funcion para recibir la respuesta 
                       url: self.url+'Proyecto/'+ self.proyectoVO.id()+'/',
                       parametros:self.proyectoVO                        
                  };
                  RequestFormData(parametros);
            }
        } else {
             ProyectoViewModel.errores_proyecto.showAllMessages();//mostramos las validacion
        }
     }
    //funcion consultar proyectos que ppuede  ver la empresa
    self.consultar = function (pagina) {
        if (pagina > 0) { 
            app_mcontrato = sessionStorage.getItem("app_mcontrato")||self.mcontrato_id_filtro();
            app_proyecto_contratista = sessionStorage.getItem("app_proyecto_contratista")||self.filtro_proyectoVO.contratista_id();
            app_departamento = sessionStorage.getItem("app_departamento")||self.filtro_proyectoVO.departamento_id();
            app_municipio = sessionStorage.getItem("app_municipio")||self.filtro_proyectoVO.municipio_id();            
            self.filtro_proyectoVO.dato($('#txtBuscar').val())
            sessionStorage.setItem("app_proyecto_dato", self.filtro_proyectoVO.dato() || '');                        
            path = self.url+'Proyecto_empresas/?format=json';
            parameter = { dato: self.filtro_proyectoVO.dato()
                          , page: pagina 
                          , empresa : empresaActual /*variable de la empresa actual del usuario */
                          , mcontrato : app_mcontrato
                          , departamento : app_departamento
                          , municipio : app_municipio
                          , contratista : app_proyecto_contratista
                          , parametro_consulta_general : self.parametro_registro() };
            RequestGet(function (datos, estado, mensage) {

                self.listado_tipos_contrato(datos.data.tipoContratos);


                if (estado == 'ok' && datos.data.proyectos!=null && datos.data.proyectos.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data.proyectos));                     
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);                
                cerrarLoading();
                self.setColorIconoFiltro();
                $('#modal_acciones_busqueda').modal('hide');                
            }, path, parameter,undefined,false);
        }        
    }
    self.borrar = function (pagina){
        sessionStorage.setItem("app_mcontrato", '');
        sessionStorage.setItem("app_departamento", '');
        sessionStorage.setItem("app_municipio", '');
        sessionStorage.setItem("app_proyecto_contratista", '');  
        location.reload(); 
        self.consultar(pagina);                             
    }
    self.cargar = function(pagina){      
        sessionStorage.setItem("app_mcontrato", self.mcontrato_id_filtro() || '');
        sessionStorage.setItem("app_departamento", self.filtro_proyectoVO.departamento_id() || '');
        sessionStorage.setItem("app_municipio", self.filtro_proyectoVO.municipio_id() || '');
        sessionStorage.setItem("app_proyecto_contratista", self.filtro_proyectoVO.contratista_id() || '');  
        self.consultar(pagina);              
    }
    self.checkall.subscribe(function(value ){
             ko.utils.arrayForEach(self.listado(), function(d) {
                    d.eliminado(value);
             }); 
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.cargar(1);
        }
        return true;
    }

    // select para actualizar un proyecto
    self.modificar_proyecto = function (proyecto_id , opcion) {
  
        self.limpiar();

        path = path_principal+'/proyecto/select-create-update-proyecto/';
        parameter = { };
        RequestGet(function (datos, estado, mensage) {

            self.listado_estados_proyecto(datos.estadoProyectos);
            self.listado_tipos_proyecto(datos.tipoProyectos);            
            self.listado_macro_contrato(datos.mcontratos);  
            self.listado_departamentos(datos.departamentos);        
            self.listado_bancos(datos.bancos);
            self.listado_tipos_cuenta(datos.tipoCuentas);      
            self.consultar_por_id(proyecto_id , opcion );

        }, path, parameter,undefined,false);        
    }

    self.ver_detalles_proyecto = function (proyecto_id , opcion){

        self.limpiar();

        path = path_principal+'/proyecto/select-create-update-proyecto/';
        parameter = { };
        RequestGet(function (datos, estado, mensage) {

            self.listado_estados_proyecto(datos.estadoProyectos);
            self.listado_tipos_proyecto(datos.tipoProyectos);            
            self.listado_macro_contrato(datos.mcontratos);
            self.listado_departamentos(datos.departamentos);        
            self.listado_bancos(datos.bancos);
            self.listado_tipos_cuenta(datos.tipoCuentas);      
            self.consultar_por_id(proyecto_id , opcion );

        }, path, parameter,undefined,false);        
    }

    self.consultar_por_id = function (proyecto_id , opcion ) {

      path =path_principal+'/api/Proyecto/'+proyecto_id+'/?format=json';
         RequestGet(function (results,count) {

            // if(results.mcontrato){
            //   self.consultar_macro_contrato(results.id , results.mcontrato.id); 
            // }             

             self.proyectoVO.id(results.id);
             self.proyectoVO.nombre(results.nombre);
             self.proyectoVO.No_cuenta(results.No_cuenta);
             self.proyectoVO.valor_adjudicado(results.valor_adjudicado);
             self.proyectoVO.mcontrato_id(results.mcontrato.id); 

             if(results.fecha_inicio != null){
             self.proyectoVO.fecha_inicio(results.fecha_inicio);
             }
             if(results.fecha_fin != null){
                self.proyectoVO.fecha_fin(results.fecha_fin);
             }              
             
             self.proyectoVO.tipo_proyecto_id(results.tipo_proyecto.id);
             
             self.proyectoVO.departamento_id(results.municipio.departamento.id);             

             setTimeout(function(){ self.proyectoVO.municipio_id(results.municipio.id) }, 1400);


             if(results.entidad_bancaria != null){
                self.proyectoVO.entidad_bancaria_id(results.entidad_bancaria.id);
             }

             if(results.tipo_cuenta != null){
                self.proyectoVO.tipo_cuenta_id(results.tipo_cuenta.id);
             }           

             self.proyectoVO.estado_proyecto_id(results.estado_proyecto.id);
             if(opcion == 1){
                self.titulo('Detalle del Proyecto'); 
                $('#modal_acciones_detalle').modal('show');
             }else if(opcion == 2){
                self.titulo('Actualizar Proyecto'); 
                $('#modal_acciones').modal('show');
             }

             cerrarLoading();
         }, path, parameter,undefined,false);
     }   
    
    self.eliminar = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                   lista_id.push(d.proyecto.id)
                }
         });
         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un proyecto para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =self.url_funcion+'destroy_proyecto/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los proyectos seleccionados?", path, parameter, function () {
                 self.cargar(1);
                 self.checkall(false);
             })

         }    
    } 
    
    self.setColorIconoFiltro = function (){
    	
        app_mcontrato = sessionStorage.getItem("app_mcontrato");
        app_proyecto_contratista = sessionStorage.getItem("app_proyecto_contratista");
        app_departamento = sessionStorage.getItem("app_departamento");
        app_municipio = sessionStorage.getItem("app_municipio");        
      
        //alert(" color, tipo_contrato : " + tipo_contrato);
    	//alert(" color, estado_id : " + estado_id);
    	//alert(" color, contratista_id : " + contratista_id);
    	//alert(" color, mcontrato: "+mcontrato);

    	

        if ((app_mcontrato!='' && app_mcontrato != 0 && app_mcontrato != null) || 
        	(app_proyecto_contratista != '' && app_proyecto_contratista !=0 && app_proyecto_contratista != null) || 
        	(app_departamento != '' && app_departamento !=0 && app_departamento != null) ||
        	(app_municipio!='' && app_municipio!=null)
        	){

            $('#iconoFiltro').addClass("filtrado");
        }else{
            $('#iconoFiltro').removeClass("filtrado");
        }
    }    
    //funcion consultar los contratos que tienen proyecto
    self.consultar_mcontratos_filtro = function () {                
            path = self.url_funcion+'filtrar_proyectos/';
            parameter = { tipo : administraccion_de_recurso };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.macrocontrato!=null && datos.macrocontrato.length > 0) {
                    self.listado_macro_contrato_filtro(datos.macrocontrato);
                } else {
                    self.listado_macro_contrato_filtro([]);
                }          
            }, path, parameter, undefined , false , false);        
    }

    self.mcontrato_id_filtro.subscribe(function (val) {
      if(val!=""){
        self.consultar_contratistas_filtro();    
        self.consultar_departamento_filtro();
      }else{
          self.consultar_select_filter_proyecto_filtro();          
          self.listado_municipios_filtro(null);
          self.filtro_proyectoVO.municipio_id("")
          self.limpiar_filtro_proyecto();
              
      }          
    });

    self.filtro_proyectoVO.contratista_id.subscribe(function (val) {        
        if(val!=""){     
            self.consultar_departamento_filtro();
        }else{
            if (self.mcontrato_id_filtro()==""){
                self.consultar_select_filter_proyecto_filtro(1); 
                
            }else{
                self.consultar_departamento_filtro(1);
                self.filtro_proyectoVO.departamento_id("");
            }                     
            
            self.listado_municipios_filtro(null);
            self.filtro_proyectoVO.municipio_id(0);   
        }
        
            
    }); 


    self.filtro_proyectoVO.departamento_id.subscribe(function (val) {
        if((val!="") & (val!='')){          
          self.consultar_municipios_filtro();  
        }else{            
            self.listado_municipios_filtro(null);
            self.filtro_proyectoVO.municipio_id(0);
        }          
      });    

    //funcion consultar los contratistas que tienen proyectos 
    self.consultar_contratistas_filtro = function () {                
            path = self.url_funcion+'filtrar_proyectos/';
            parameter = { mcontrato : self.mcontrato_id_filtro() || 0, tipo :8, tipo_contratista: true};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos.contratista!=null && datos.contratista.length > 0) {                    
                    self.listado_contratista_filtro(datos.contratista);
                    //self.filtro_proyectoVO.contratista_id(sessionStorage.getItem("app_proyecto_contratista")|| "");            
                    if( sessionStorage.getItem("app_proyecto_contratista") != "" || sessionStorage.getItem("app_proyecto_contratista") != null || sessionStorage.getItem("app_proyecto_contratista") != undefined){
                        $('#contratista_id_select').val(sessionStorage.getItem("app_proyecto_contratista"))
                    }                    
                } else {
                    self.listado_contratista_filtro([]);
                }          
            }, path, parameter);        
    }
    
    self.consultar_departamento_filtro = function (no_cargar) {                
        path = self.url_funcion+'filtrar_proyectos/';
        
        parameter = {
            mcontrato:self.mcontrato_id_filtro() || 0, 
            contratista:self.filtro_proyectoVO.contratista_id() || 0
        };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos.departamento!=null && datos.departamento.length > 0) {                
                self.listado_departamentos_filtro(datos.departamento);
                //self.filtro_proyectoVO.departamento_id(sessionStorage.getItem("app_departamento")|| "");
                if(no_cargar==undefined){
                    if( sessionStorage.getItem("app_departamento") != "" || sessionStorage.getItem("app_departamento") != null || sessionStorage.getItem("app_departamento") != undefined){
                    $('#departamento_id_select').val(sessionStorage.getItem("app_departamento"))
                    }
                }
                                
            } else {
                self.listado_departamentos_filtro([]);
            }          
        }, path, parameter);        
    }  

    //funcion consultar municipios
    self.consultar_municipios_filtro = function () {                
        path = self.url_funcion+'filtrar_proyectos/';     
        parameter = { 
            mcontrato : self.mcontrato_id_filtro() || 0,
            departamento : self.filtro_proyectoVO.departamento_id() || 0,
            contratista : self.filtro_proyectoVO.contratista_id() || 0
        };        
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos.municipio!=null && datos.municipio.length > 0) {
                self.listado_municipios_filtro(datos.municipio);  
                self.filtro_proyectoVO.municipio_id(sessionStorage.getItem("app_municipio")|| "");      
                if( self.filtro_proyectoVO.municipio_id() != "" || self.filtro_proyectoVO.municipio_id() != null || self.filtro_proyectoVO.municipio_id() != undefined){
                    $('#municipio_id_select').val(self.filtro_proyectoVO.municipio_id())
                }                                   
            } else {
                self.listado_municipios_filtro([]);
            }             
            cerrarLoading();
        }, path, parameter);          
    }     

    //consultar los macrocontrato
    self.consultar_macro_contrato=function(proyecto,mcontrato){
        
         path = self.url_funcion+'listar_macroContrato_Proyectos/';
         parameter = { proyecto_id :proyecto };
         RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.listado_macro_contrato(datos);
                if(mcontrato>0){
                   self.proyectoVO.mcontrato_id(mcontrato); 
                }                
            }else{
                self.listado_macro_contrato([]);
            }
         }, path, parameter , undefined , false , false);
    }

    
    self.consultar_municipios = function (departamento) {                
        path = self.url+'Municipio/';
        parameter = { ignorePagination : 1 , id_departamento : departamento };
        
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_municipios(datos);                    
                } else {
                    self.listado_municipios([]);
                }             
                cerrarLoading();
            }, path, parameter,undefined,false);          
    }


    self.proyectoVO.departamento_id.subscribe(function (val) {
        if(val!=""){
            self.consultar_municipios(val)   
        }else{
            self.listado_municipios([]);
        }   
    });
     
/* ------- BLOQUE DE CONTRATISTA ------- ------- BLOQUE DE CONTRATISTA ------- ------- BLOQUE DE CONTRATISTA ------- */
    self.consultar_contratistas_opcion = function(proyecto_id) {
        self.proyecto_empresaVO.proyecto_id(proyecto_id) 
        self.consultar_contratistas_proyecto(proyecto_id)
    }
   
    //funcion consultar contratistas del proyecto
    self.consultar_contratistas_proyecto = function (proyecto_id) {
            self.filtro_contratista_proyecto($('#txtBuscarContratistaProyecto').val());                      
            path = self.url+'Proyecto_empresas/';
            parameter = {proyecto : proyecto_id, proyecto_empresa_por_id:true };
            RequestGet(function (datos, estado, mensage) {
                $('#modal_acciones_contratista').modal('show');
                if (estado == 'ok' && datos.data[0].proyecto.contrato!=null && datos.data[0].proyecto.contrato.length > 0) { 
                    self.mensajeAsignados('');                   
                    self.listado_proyecto_contratistas(agregarOpcionesObservable(datos.data[0].proyecto.contrato));
                } else {
                    self.listado_proyecto_contratistas([]);
                    self.mensajeAsignados(mensajeNoFound);
                }                
             
            }, path, parameter);        
    }

/* -------FINALIZA BLOQUE DE CONTRATISTA ------- -------FINALIZA BLOQUE DE CONTRATISTA ------- -------FINALIZA BLOQUE DE CONTRATISTA ------- */

/* ------- BLOQUE DE EMPRESAS ------- ------- BLOQUE DE EMPRESAS ------- ------- BLOQUE DE EMPRESAS ------- */
    // //funcion para guardar empresas del proyecto 
         self.guardar_empresas_proyecto=function(obj){ 
            self.proyecto_empresaVO.empresa_id([]);           
            ko.utils.arrayForEach(self.listado_empresas_tabla(),function(p){
                if (p.procesar()) {
                    self.proyecto_empresaVO.empresa_id.push(p.id);
                };
            });
       
            var parametros={                     
                 callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.filtro(""); 
                        self.consultar_empresas(self.proyecto_empresaVO.proyecto_id())                       
                        self.consultar_empresas_proyecto(self.proyecto_empresaVO.proyecto_id());
                        self.checkallEmpresas(false);
                    }                     
                 },//funcion para recibir la respuesta 
                 url: self.url_funcion+'create_proyecto_empresa/',//url api
                 parametros: self.proyecto_empresaVO                         
            };
            //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData(parametros);            
         }
         self.eliminar_empresas_proyecto = function () {
                 self.proyecto_empresaVO.empresa_id([]);  
                 var count=0;
                 ko.utils.arrayForEach(self.listado_proyecto_empresas(), function(d) {
                        if(d.eliminado()==true){
                           count=1;
                           self.proyecto_empresaVO.empresa_id.push(d.id);
                        }
                 });

                if(count==0){
                        $.confirm({
                            title:'Informativo',
                            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una empresa para la eliminacion.<h4>',
                            cancelButton: 'Cerrar',
                            confirmButton: false
                        });
                }else{
                     var path =path_principal+'/proyecto/destroy_proyecto_empresa/';
                     var parameter = self.proyecto_empresaVO
                     RequestAnularOEliminar("Esta seguro que desea denegar las empresas seleccionadas?", path, parameter, function () {
                         //self.consultar(1);
                         self.consultar_empresas(self.proyecto_empresaVO.proyecto_id()) 
                         self.consultar_empresas_proyecto(self.proyecto_empresaVO.proyecto_id());
                         self.checkallProyectoEmpresas(false);
                     })
                 }          
            }
    self.consultar_empresas_opcion = function (proyecto_id) {
        self.consultar_empresas(proyecto_id)
        self.consultar_empresas_proyecto(proyecto_id)
        self.proyecto_empresaVO.proyecto_id(proyecto_id) 
    }
    self.consultar_empresas_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_empresas(self.proyecto_empresaVO.proyecto_id() )
        }
        return true;
    }

    self.consultar_empresas_btn = function (d,e) {
      self.consultar_empresas(self.proyecto_empresaVO.proyecto_id() )
    }
    //funcion consulta todas las empresas 
    self.consultar_empresas = function (proyecto_id) {  
            self.filtro_empresa($('#txtBuscarEmpresa').val());                
            path = self.url_funcion+'listEmpresasSinProyecto?format=json';
            parameter = { dato : self.filtro_empresa() , 
                proyecto_id : proyecto_id};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensajePorAsignar(''); 
                    self.listado_empresas_tabla(agregarOpcionesObservable(datos));
                } else {
                    self.listado_empresas_tabla([]);
                    self.mensajePorAsignar(mensajeNoFound); 
                }             
            }, path, parameter);        
    }

    self.consultar_empresas_proyecto_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_empresas_proyecto(self.proyecto_empresaVO.proyecto_id());
        }
        return true;
    }
    self.consultar_empresas_proyecto_filtro = function(){        
        self.consultar_empresas_proyecto(self.proyecto_empresaVO.proyecto_id());
    }
    //funcion consultar empresas que pueden ver el proyecto
    self.consultar_empresas_proyecto = function (proyecto_id) {
            self.filtro_empresa_proyecto($('#txtBuscarEmpresaProyecto').val());            
            path = self.url_funcion+'listEmpresasDelProyecto/';
            parameter = { dato : self.filtro_empresa_proyecto() , proyecto_id : proyecto_id , propietario : 0 };
            RequestGet(function (datos, estado, mensage) {    
                $('#modal_acciones_empresa').modal('show');            
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensajeAsignados('');   
                    self.listado_proyecto_empresas(agregarOpcionesObservable(datos)); 
                } else {
                    self.listado_proyecto_empresas([]);  
                    self.mensajeAsignados(mensajeNoFound);                     
                }         
            }, path, parameter);        
    }
    self.checkallEmpresas.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado_empresas_tabla(), function(d) {
                    d.procesar(value);
            }); 
    });
    self.checkallProyectoEmpresas.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado_proyecto_empresas(), function(d) {
                    d.eliminado(value);
            }); 
    });
/* -------FINALIZA BLOQUE DE EMPRESAS ------- -------FINALIZA BLOQUE DE EMPRESAS ------- -------FINALIZA BLOQUE DE EMPRESAS ------- */


/* ------- BLOQUE DE RESPONSABLES ------- ------- BLOQUE DE RESPONSABLES ------- ------- BLOQUE DE RESPONSABLES ------- */
        self.cambio_empresa=function(obj){
          self.consultar_empresas_cargo_select(); 
          self.consultar_responsables(self.proyecto_responsableVO.proyecto_id())  
        }
        self.cambio_empresa_asignada=function(obj){ 
          self.consultar_empresas_cargos_asignados();
          self.consultar_responsables_proyecto(self.proyecto_responsableVO.proyecto_id() )   
        }
        // //funcion para guardar contratistas del proyecto 
         self.guardar_responsables_proyecto=function(obj){ 
            self.proyecto_responsableVO.funcionario_id([]);           
            ko.utils.arrayForEach(self.listado_responsables_tabla(),function(p){
                if (p.procesar()) {
                    self.proyecto_responsableVO.funcionario_id.push(p.id);
                };
            });
       
            var parametros={                     
                 callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.consultar_responsables(self.proyecto_responsableVO.proyecto_id())                      
                        self.consultar_responsables_proyecto(self.proyecto_responsableVO.proyecto_id());
                        self.checkallResponsables(false);
                    }                     
                 },//funcion para recibir la respuesta 
                 url: self.url_funcion+'create_proyecto_funcionario/',//url api
                 parametros: self.proyecto_responsableVO                         
            };
            RequestFormData(parametros);            
         }
         self.eliminar_responsables_proyecto = function () {
                 self.proyecto_responsableVO.funcionario_id([]);  
                 var count=0;
                 ko.utils.arrayForEach(self.listado_proyecto_responsables(), function(d) {
                        if(d.eliminado()==true){
                           count=1;
                           self.proyecto_responsableVO.funcionario_id.push(d.id);
                        }
                 });

                if(count==0){

                        $.confirm({
                            title:'Informativo',
                            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un funcionario para la eliminacion.<h4>',
                            cancelButton: 'Cerrar',
                            confirmButton: false
                        });
                }else{
                     var path =path_principal+'/proyecto/destroy_proyecto_funcionario/';
                     var parameter = self.proyecto_responsableVO
                     RequestAnularOEliminar("Esta seguro que desea denegar los funcionarios seleccionados?", path, parameter, function () {
                         self.consultar_responsables(self.proyecto_responsableVO.proyecto_id())
                         self.consultar_responsables_proyecto(self.proyecto_responsableVO.proyecto_id());
                         self.checkallProyectoResponsables(false);
                     })
                 }          
            }

    self.consultar_responsables_proyecto_opcion = function (obj) {
        self.consultar_empresas_proyecto_select(obj.proyecto.id)
        self.consultar_responsables(obj.proyecto.id)
        self.consultar_responsables_proyecto(obj.proyecto.id)
        $('#modal_acciones_responsable').modal('show');
        self.proyecto_responsableVO.proyecto_id(obj.proyecto.id)
    }
    //funcion consultar empresas del proyecto para mostrar enn el select
    self.consultar_empresas_proyecto_select = function (proyecto_id) {
            path = self.url_funcion+'listEmpresasDelProyecto/';
            parameter = { proyecto_id : proyecto_id };
            RequestGet(function (datos, estado, mensage) {                
                if (estado == 'ok' && datos!=null && datos.length > 0) {                  
                    self.listado_proyecto_empresas_select(datos); 
                } else {
                    self.listado_proyecto_empresas_select([]);
                }             
            }, path, parameter);        
    }
    //funcion consultar responsables del proyecto 
    self.consultar_empresas_cargos_asignados = function () {
          
            path = self.url+'Cargo/';
            parameter = { empresa_filtro : self.empresaAsignada_id() , sin_paginacion : 1 };
            if(self.empresaAsignada_id()!=""){
                 RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                        self.listado_cargos(datos);
                    } else {
                        self.listado_cargos([]);
                    }          
                }, path, parameter); 
            }else{
                self.listado_cargos([]);
            }                  
    } 

    //funcion consultar cargos de las empresas que pueden ver el proyecto para mostrar en el select
    self.consultar_empresas_cargo_select = function () {

            path = self.url+'Cargo/';
            parameter = { sin_paginacion : 1 , empresa_filtro : self.empresa_id()};
            if(self.empresa_id()!=""){
                RequestGet(function (datos, estado, mensage) {                
                    if (estado == 'ok' && datos!=null && datos.length > 0) {                  
                        self.listado_cargos_select(datos); 
                    } else {
                        self.listado_cargos_select([]);
                    }       
                }, path, parameter); 
            }else{
                self.listado_cargos_select([]);
            }
    }

    self.consultar_responsables_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar_responsables(self.proyecto_responsableVO.proyecto_id() )
        }
        return true;
    }
    self.consultar_responsables_btn = function (d,e) {
        self.consultar_responsables(self.proyecto_responsableVO.proyecto_id() )
    }
    //funcion consultar funcionarios para agregar al proyecto como responsables 
    self.consultar_responsables = function (proyecto_id) {
            self.filtro_funcionario($('#txtBuscarFuncionario').val());  
            path = self.url_funcion+'listFuncionariosSinProyecto/?format=json';
            parameter = { proyecto_id : proyecto_id , dato : self.filtro_funcionario()  , empresa_id : self.empresa_id() , cargo_id : self.cargo_id() , active: true};
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensajePorAsignar('')
                    self.listado_responsables_tabla(agregarOpcionesObservable(datos));
                } else {
                    self.listado_responsables_tabla([]);
                    self.mensajePorAsignar(mensajeNoFound)
                }          
            }, path, parameter);        
    }

    self.consultar_responsables_proyecto_enter = function (d,e) {
            if (e.which == 13) {
                self.consultar_responsables_proyecto(self.proyecto_responsableVO.proyecto_id() )
            }
            return true;
        }
    self.consultar_responsables_proyecto_btn = function (d,e) {
                self.consultar_responsables_proyecto(self.proyecto_responsableVO.proyecto_id() )
        }
    //funcion consultar responsables del proyecto 
    self.consultar_responsables_proyecto = function (proyecto_id) {

            self.filtro_funcionario_proyecto($('#txtBuscarFuncionarioProyecto').val()); 
            path = self.url_funcion+'list_proyecto_funcionario/';
            parameter = { proyecto_id : proyecto_id , dato : self.filtro_funcionario_proyecto() , empresa_id: self.empresaAsignada_id() , cargo_id: self.cargo_responsable_id() , active: true};
            RequestGet(function (results,count) {

                if(results.length>0){
                    self.mensajeAsignados('')
                    self.listado_proyecto_responsables(agregarOpcionesObservable(results));
                }else{
                    self.listado_proyecto_responsables([]);
                    self.mensajeAsignados(mensajeNoFound)
                }
               
            }, path, parameter);        
    }  
    self.checkallResponsables.subscribe(function(value ){
        ko.utils.arrayForEach(self.listado_responsables_tabla(), function(d) {
                d.procesar(value);
        }); 
    });
    self.checkallProyectoResponsables.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado_proyecto_responsables(), function(d) {
                    d.eliminado(value);
            }); 
    }); 
/* -------FINALIZA BLOQUE DE RESPONSABLES ------- -------FINALIZA BLOQUE DE RESPONSABLES ------- -------FINALIZA BLOQUE DE RESPONSABLES ------- */

/* ------- BLOQUE DE CONTRATOS ------- ------- BLOQUE DE CONTRATOS ------- ------- BLOQUE DE CONTRATOS ------- */
            // //funcion para guardar contratistas del proyecto 
         self.guardar_contratos_proyecto=function(obj){ 
            self.proyecto_contratoVO.contrato_id([]);           
            ko.utils.arrayForEach(self.listado_contratos_tabla(),function(p){
                if (p.procesar()) {
                    self.proyecto_contratoVO.contrato_id.push(p.id);
                };
            });
       
            var parametros={                     
                 callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.filtro("");  
                        self.consultar_contratos(self.proyecto_contratoVO.proyecto_id());                      
                        self.consultar_contratos_proyecto(self.proyecto_contratoVO.proyecto_id());
                        self.checkallContratos(false);
                    }                     
                 },//funcion para recibir la respuesta 
                 url: self.url_funcion+'create_proyecto_contrato/',//url api
                 parametros: self.proyecto_contratoVO                         
            };
            //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData(parametros);            
         }
         self.eliminar_contratos_proyecto = function () {
                 self.proyecto_contratoVO.contrato_id([]);  
                 var count=0;
                 ko.utils.arrayForEach(self.listado_proyecto_contratos(), function(d) {
                        if(d.eliminado()==true){
                           count=1;
                           self.proyecto_contratoVO.contrato_id.push(d.id);
                        }
                 });

                if(count==0){

                        $.confirm({
                            title:'Informativo',
                            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contrato para la eliminacion.<h4>',
                            cancelButton: 'Cerrar',
                            confirmButton: false
                        });
                }else{
                     var path =path_principal+'/proyecto/destroy_proyecto_contrato/';
                     var parameter = self.proyecto_contratoVO
                     RequestAnularOEliminar("Esta seguro que desea denegar los contratos seleccionados?", path, parameter, function () {
                         self.consultar_contratos(self.proyecto_contratoVO.proyecto_id()); 
                         self.consultar_contratos_proyecto(self.proyecto_contratoVO.proyecto_id());
                         self.checkallProyectoContratos(false);
                     })
                 }          
            }

           //consultar los tipos de contrato
        self.consultar_tipos_contrato=function(){
             path = self.url+'Tipos/';
             parameter = { ignorePagination : 1 , aplicacion : self.app_contrato };
                RequestGet(function (datos, estado, mensage) {
                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                        self.listado_tipos_contrato(datos);
                    } else {
                        self.listado_tipos_contrato([]);
                    }             
                }, path, parameter); 
        }
        self.consultar_contratos_enter = function (d,e) {
            if (e.which == 13) {
                self.consultar_contratos(self.proyecto_contratoVO.proyecto_id())
            }
            return true;
        }

        self.consultar_contratos_btn = function (){
            self.consultar_contratos(self.proyecto_contratoVO.proyecto_id())
        }
         //funcion consultar contratos
        self.consultar_contratos = function (proyecto_id) {
                self.filtro_contrato($('#txtBuscarContrato').val());        
                path = self.url_funcion+'listContratosSinProyecto/?format=json';
                parameter = { dato : self.filtro_contrato() , proyecto_id : proyecto_id , tipoContrato : self.tipoContrato_id() };
                RequestGet(function (datos, estado, mensage) {
                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                         self.mensajePorAsignar('')
                        self.listado_contratos_tabla(agregarOpcionesObservable(datos));                        
                    } else {
                        self.listado_contratos_tabla([]);   
                         self.mensajePorAsignar(mensajeNoFound)                    
                    }                
                }, path, parameter);        
        } 

        self.consultar_contratos_opcion = function (proyecto_id){
            $('#modal_acciones_contrato').modal('show');
            self.proyecto_contratoVO.proyecto_id(proyecto_id)
            self.consultar_contratos_proyecto(proyecto_id)
            self.consultar_contratos(proyecto_id);
        }
        self.consultar_contratos_proyecto_enter = function (d,e) {
            if (e.which == 13) {
                self.consultar_contratos_proyecto(self.proyecto_contratoVO.proyecto_id())
            }
            return true;
        }
        self.consultar_contratos_proyecto_filtro  = function(){
            self.consultar_contratos_proyecto(self.proyecto_contratoVO.proyecto_id())
        }
         //funcion consultar contratos asociados a los proyecto
        self.consultar_contratos_proyecto = function (proyecto_id) {
                self.filtro_contrato_proyecto($('#txtBuscarContratoProyecto').val());                
                path = self.url_funcion+'list_proyecto_contrato/?format=json';
                parameter = { dato : self.filtro_contrato_proyecto() , proyecto_id : proyecto_id , tipoContrato : self.tipoContratoAsignados_id() };
                RequestGet(function (results,count) {
                    if (results.length>0){
                        self.mensajeAsignados('')
                        self.listado_proyecto_contratos(agregarOpcionesObservable(results));
                    }else{
                        self.listado_proyecto_contratos([]);
                        self.mensajeAsignados(mensajeNoFound)
                    }
                   
                }, path, parameter);       
        } 
        self.checkallContratos.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado_contratos_tabla(), function(d) {
                    d.procesar(value);
            }); 
        });
        self.checkallProyectoContratos.subscribe(function(value ){
                ko.utils.arrayForEach(self.listado_proyecto_contratos(), function(d) {
                        d.eliminado(value);
                }); 
        }); 
/* -------FINALIZA BLOQUE DE CONTRATOS ------- -------FINALIZA BLOQUE DE CONTRATOS ------- -------FINALIZA BLOQUE DE CONTRATOS ------- */

/* ------- BLOQUE DE INFORMACION TECNICA ------- ------- BLOQUE DE INFORMACION TECNICA ------- ------- BLOQUE DE INFORMACION TECNICA ------- */
        // //limpiar el modelo 
         self.limpiar_datos_tecnico=function(){           
           self.proyecto_info_tecnicaVO.id(0);
           self.proyecto_info_tecnicaVO.campo_id('');
           self.proyecto_info_tecnicaVO.valor_diseno('');
           self.proyecto_info_tecnicaVO.valor_ejecucion('');
           self.proyecto_info_tecnicaVO.valor_replanteo('');

           self.proyecto_info_tecnicaVO.campo_id.isModified(false);
           self.proyecto_info_tecnicaVO.valor_diseno.isModified(false);
         }

        self.abrir_modal_datos_tecnico_form = function () {
            self.limpiar_datos_tecnico();
            self.titulo('Registrar Dato tecnico');
            $('#modal_acciones_datos_tecnico_form').modal('show');
        }


        self.consultar_por_id_datos_tecnico_form = function (obj) {

               path = self.url+'Proyecto_info_tecnica/'+obj.id+'/?format=json';
               parameter = {  };
                 RequestGet(function (results,count) {
                   
                    self.titulo('Actualizar Dato tecnico');
                    self.proyecto_info_tecnicaVO.id(results.id),
                    self.proyecto_info_tecnicaVO.campo_id(results.campo.id);
                    self.proyecto_info_tecnicaVO.proyecto_id(results.proyecto.id);

                    if(results.valor_diseno != null){
                      self.proyecto_info_tecnicaVO.valor_diseno(results.valor_diseno);
                    }

                    if(results.valor_ejecucion!= null){
                      self.proyecto_info_tecnicaVO.valor_ejecucion(results.valor_ejecucion);
                    }else{
                      self.proyecto_info_tecnicaVO.valor_ejecucion('0')
                    }                   

                    if(results.valor_replanteo!= null){
                      self.proyecto_info_tecnicaVO.valor_replanteo(results.valor_replanteo);    
                    }else{
                      self.proyecto_info_tecnicaVO.valor_replanteo('0'); 
                    }                   

                     $('#modal_acciones_datos_tecnico_form').modal('show');
                 }, path, parameter);
             }  

        // //funcion para guardar y editar 
         self.guardar_info_tecnica=function(){

          if (ProyectoViewModel.errores_proyecto_info_tecnica().length == 0) {//se activa las validaciones
                if(self.proyecto_info_tecnicaVO.id()==0){

                    var parametros={                     
                         callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                                self.filtro("");                                
                                $('#modal_acciones_datos_tecnico_form').modal('hide');
                                self.limpiar_datos_tecnico();
                                self.consultar_info_tecnica_proyecto(self.proyecto_info_tecnicaVO.proyecto_id())
                            }                     
                         },//funcion para recibir la respuesta 
                         url: self.url+'Proyecto_info_tecnica/',//url api
                         parametros: self.proyecto_info_tecnicaVO                        
                    };
                    //parameter =ko.toJSON(self.contratistaVO);
                    RequestFormData(parametros);
                }else{                     
                      var parametros={     
                            metodo:'PUT',                
                           callback:function(datos, estado, mensaje){
                              if (estado=='ok') {
                                self.filtro("");
                                self.consultar_info_tecnica_proyecto(self.proyecto_info_tecnicaVO.proyecto_id());
                                $('#modal_acciones_datos_tecnico_form').modal('hide');
                                self.limpiar_datos_tecnico();
                              }
                           },//funcion para recibir la respuesta 
                           url: self.url+'Proyecto_info_tecnica/'+ self.proyecto_info_tecnicaVO.id()+'/',
                           parametros: self.proyecto_info_tecnicaVO                       
                      };
                      RequestFormData(parametros);
                }

            } else {
                 ProyectoViewModel.errores_proyecto_info_tecnica.showAllMessages();//mostramos las validacion
            }
         }
         self.eliminar_info_tecnica_proyecto = function (obj) {                 
            self.proyecto_info_tecnicaVO.id(obj.id)
             var path = path_principal+'/proyecto/destroy_proyecto_info_tecnica/';
             var parameter = self.proyecto_info_tecnicaVO
             RequestAnularOEliminar("Esta seguro que desea denegar el campo información tecnica  seleccionados?", path, parameter, function () {
                 self.consultar_info_tecnica_proyecto(self.proyecto_info_tecnicaVO.proyecto_id());

             })
                        
        }
        self.consultar_campos_info_tecnica_opcion = function (obj){
            self.proyecto_info_tecnicaVO.proyecto_id(obj.proyecto.id) 
            self.consultar_campos_info_tecnica(obj.proyecto.tipo_proyecto.id)
            self.consultar_info_tecnica_proyecto(obj.proyecto.id)
        }
        //funcion consultar campos de informacion tecnica del proyecto
        self.consultar_campos_info_tecnica = function (tipo_proyecto) {
                path = self.url+'Proyecto_campo_info_tecnica/';
                parameter = { ignorePagination : 1  , tipo_proyecto : tipo_proyecto};
                RequestGet(function (datos, estado, mensage) {
                    $('#modal_acciones_datos_tecnico').modal('show');
                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                        self.listado_campo_info_tecnica(datos);
                    } else {
                        self.listado_campo_info_tecnica([]);
                    }                
                }, path, parameter);        
        }    
        //funcion consultar informacion tecnica del proyecto
        self.consultar_info_tecnica_proyecto = function (proyecto_id) {
                    
                path = self.url+'Proyecto_info_tecnica/';
                parameter = { ignorePagination : 1 , proyecto : proyecto_id , serializer_super_lite : true/* se usa para el serializador con menos campos*/};
                RequestGet(function (datos, estado, mensage) {
                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                        self.mensajeAsignados('');   
                        self.listado_proyecto_info_tecnica(datos);
                    } else {
                        self.listado_proyecto_info_tecnica([]);
                        self.mensajeAsignados(mensajeNoFound);   
                    }                
                }, path, parameter);        
        }

/* -------- FINALIZA BLOQUE DE INFORMACION TECNICA -------- -------- FINALIZA BLOQUE DE INFORMACION TECNICA -------- */

}

var proyecto = new ProyectoViewModel();

$('#txtBuscar').val(sessionStorage.getItem("app_proyecto_dato"))

ProyectoViewModel.errores_proyecto = ko.validation.group(proyecto.proyectoVO);
ProyectoViewModel.errores_proyecto_info_tecnica = ko.validation.group(proyecto.proyecto_info_tecnicaVO);
ProyectoViewModel.errores_proyecto_contratista = ko.validation.group(proyecto.proyecto_empresaVO);
ko.applyBindings(proyecto);