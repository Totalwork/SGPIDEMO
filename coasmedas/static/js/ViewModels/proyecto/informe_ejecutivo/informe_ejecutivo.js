function InformeEjecutivoViewModel() {
        
        var self = this;
        self.listado=ko.observableArray([]);
        self.mensaje=ko.observableArray([]);
        self.listado_mcontratos=ko.observableArray([]);
        self.listado_tipos_proyecto=ko.observableArray([]);
        self.listado_fondos=ko.observableArray([]);
        self.listado_departamentos=ko.observableArray([]);
        self.listado_municipios=ko.observableArray([]);
        self.seleccionar_fondos=ko.observable(false);
        self.seleccionar_tipo_proyectos=ko.observable(false);
        self.seleccionar_mcontratos=ko.observable(false);
        self.departamento_id=ko.observable('');
        self.municipio_id=ko.observable('');
        self.texto_fondo=ko.observable('');
        self.texto_tipos_proyecto=ko.observable('');
        self.texto_contrato=ko.observable('');
        self.texto_municipio=ko.observable('');
        self.texto_departamento=ko.observable('');
        self.listado_balance_fininaciero=ko.observableArray([]);
        self.listado_contratos_mme=ko.observableArray([]);
        self.contrato_id=ko.observable(0);
        self.listado_fondo_giro_contratista=ko.observableArray([]);
        self.suma_prones = ko.observable(0);
        self.suma_faer = ko.observable(0);

        self.filtros={
            fondo_id:ko.observable(''),
            contrato_id:ko.observable(''),
            departamento_id:ko.observable(''),
            municipio_id:ko.observable(''),
            tipo_proyecto_id:ko.observable('')
        };

        self.filtros_contratistas={
            fondo_id:ko.observable(''),
            contrato_id:ko.observable(''),
            contratista_id:ko.observable('')
        };

        self.consultar=function () {
          
          var numFondo=0;
          var fondos='';
          ko.utils.arrayForEach(self.listado_fondos(), function (p) {
             if (p.procesar()) {
                fondos+=p.id+',';
                numFondo++;
             }
          });

          var numTipos=0;
          var tipos='';
          ko.utils.arrayForEach(self.listado_tipos_proyecto(), function (p) {
             if (p.procesar()) {
                tipos+=p.id+',';   
                numTipos++;             
             }
          });

          var numMcont=0;
          var mcontratos='';
          ko.utils.arrayForEach(self.listado_mcontratos(), function (p) {
             if (p.procesar()) {
                mcontratos+=p.id+',';
                numMcont++;
             }
          });

          fondos=fondos.slice(0,-1);
          tipos=tipos.slice(0,-1);
          mcontratos=mcontratos.slice(0,-1);
         
         self.texto_fondo(self.listado_fondos().length==numFondo ? '[Todos...]' : numFondo+' Seleccionados.');
         self.texto_contrato(self.listado_mcontratos().length==numMcont ? '[Todos...]' : numMcont+' Seleccionados.');
         self.texto_tipos_proyecto(self.listado_tipos_proyecto().length==numTipos ? '[Todos...]' : numTipos+' Seleccionados.');
         self.texto_departamento($('#departamento option:selected').text());
         self.texto_municipio($('#municipio option:selected').text());

          var parametros={
                          fondos:fondos,
                          contratos:mcontratos,
                          departamento_id:self.departamento_id(),
                          municipio_id:self.municipio_id(),
                          tipos_proyecto:tipos
                        };
          var path=path_principal+'/proyecto/consulta_fondo_proyecto/'
          RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    
                    self.mensaje('');
                    //self.listado(results);  
                    self.listado(datos);  

                    if (datos.length>0) {
                        $('#modal_filtros').modal('hide');
                    }

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                //self.llenar_paginacion(datos,pagina);
                
            }, path, self.filtros , function(){
                    cerrarLoading();
            });

        }  


        self.abrir_filtros = function () {
          $('#modal_filtros').modal('show');
        }   

        self.consultar_filtros_proyecto=function() {
          
           path = path_principal + '/proyecto/filtrar_proyectos/';
           RequestGet(function (datos, estado, mensage) {         
              self.listado_departamentos(datos['departamento']);
              self.listado_municipios(datos['municipio']);
              self.listado_mcontratos(agregarOpcionesObservable(datos['macrocontrato']));
              ko.utils.arrayForEach(self.listado_mcontratos(), function (p) {             
                p.procesar(true);             
              });
           }, path, {}, function(){
              cerrarLoading();
           },false, false);

        }

        self.consultar_tipos_y_fondos=function() {
          
           path = path_principal + '/api/Proyecto_tipos/?ignorePagination=';
           RequestGet(function (datos, estado, mensage) {         
              self.listado_tipos_proyecto(agregarOpcionesObservable(datos));
              ko.utils.arrayForEach(self.listado_tipos_proyecto(), function (p) {             
                p.procesar(true);             
              });
           }, path, {}, function(){
              cerrarLoading();
           },false, false);

           path = path_principal + '/api/Proyecto_fondos/?ignorePagination=';
           RequestGet(function (datos, estado, mensage) {         
              self.listado_fondos(agregarOpcionesObservable(datos));
              ko.utils.arrayForEach(self.listado_fondos(), function (p) {            
                p.procesar(true);            
              });
           }, path, {}, function(){
              cerrarLoading();
           },false, false);

        }


        self.seleccionar_fondos.subscribe(function(val) {
          ko.utils.arrayForEach(self.listado_fondos(), function (p) {            
              p.procesar(val);            
          });
        });

        self.seleccionar_tipo_proyectos.subscribe(function(val) {
          ko.utils.arrayForEach(self.listado_tipos_proyecto(), function (p) {             
              p.procesar(val);             
          });
        });

        self.seleccionar_mcontratos.subscribe(function(val) {
          ko.utils.arrayForEach(self.listado_mcontratos(), function (p) {             
              p.procesar(val);             
          });
        });


         self.exportar_resumen_proyecto=function () {
          
          var fondos='';
          ko.utils.arrayForEach(self.listado_fondos(), function (p) {
             if (p.procesar()) {
                fondos+=p.id+','
             }
          });

          var tipos='';
          ko.utils.arrayForEach(self.listado_tipos_proyecto(), function (p) {
             if (p.procesar()) {
                tipos+=p.id+','
             }
          });

          var mcontratos='';
          ko.utils.arrayForEach(self.listado_mcontratos(), function (p) {
             if (p.procesar()) {
                mcontratos+=p.id+','
             }
          });

          fondos=fondos.slice(0,-1);
          tipos=tipos.slice(0,-1);
          mcontratos=mcontratos.slice(0,-1);
               
          var path='fondo_id='+fondos+'&contrato_id='+mcontratos+'&departamento_id='+self.departamento_id()+'&municipio_id='+self.municipio_id()+'&tipo_proyecto_id='+tipos;
          
          window.location.href=path_principal + '/proyecto/exportar_resumen_por_fondo_proyecto/?'+path;
        }  


         self.consultar_balance_financiero=function(contrato_id) {
          
           path = path_principal + '/proyecto/consulta_balance_financiero/';
           RequestGet(function (datos, estado, mensage) {         
              self.listado_balance_fininaciero(datos);
           }, path, {contrato_id:contrato_id});

        }

        self.consultar_contratos=function() {
          
           path = path_principal + '/api/Contrato/?sin_paginacion=';
           RequestGet(function (datos, estado, mensage) {         
              self.listado_contratos_mme(datos);              
           }, path, {},undefined ,false, false);

        }


        self.contrato_id.subscribe(function(val){

          self.consultar_balance_financiero(val);

        });

        self.exportar_balance_financiero=function() {
          window.location.href=path_principal + '/proyecto/exportar_balance_financiero/?contrato_id='+self.contrato_id()
        }
        
        self.consultar_fondo_giro_contratista=function() {
          
           path = path_principal + '/proyecto/consultar_fondo_giro_contratista/';
           RequestGet(function (datos, estado, mensage) { 

              self.listado_fondo_giro_contratista(datos);  
              
              var total=0;
              var total2=0;
              ko.utils.arrayForEach(datos, function (p) {               
                if (p.id==1)
                   total+=parseFloat(p.valor);
                if (p.id==2)
                   total2+= parseFloat(p.valor);
              });

              self.suma_prones(total);              
              self.suma_faer(total2);
              
           }, path, self.filtros_contratistas);

        }

        self.filtros_contratistas.contratista_id.subscribe(function(val) {          
          self.consultar_fondo_giro_contratista();
        });

        self.filtros_contratistas.fondo_id.subscribe(function(val) {
          self.consultar_fondo_giro_contratista();
        });

        self.filtros_contratistas.contrato_id.subscribe(function(val) {
          self.consultar_fondo_giro_contratista();
        });

        self.exportar_fondo_giro_contratista=function() {
          window.location.href=path_principal + '/proyecto/exportar_fondo_giro_contratista/?contrato_id='+self.filtros_contratistas.contrato_id()+'contratista_id='+self.filtros_contratistas.contratista_id()+'&fondo_id='+ self.filtros_contratistas.fondo_id();
        }
}

var viewModel = new InformeEjecutivoViewModel();      
ko.applyBindings(viewModel);