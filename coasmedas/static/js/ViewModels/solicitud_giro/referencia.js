function Encabezado_giroViewModel() {
        
    var self = this;
    self.listado=ko.observableArray([]);
    self.listado_no_radicado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.mensaje_no_radicado=ko.observable('');
    self.mensaje_soportes=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.soporte_arriba=ko.observable('');
    self.idProcesoRelacion =ko.observable(0);
    self.cambiar_contratista=ko.observable(0);
    self.soporte=ko.observable('');
    self.listado_soporte=ko.observableArray([]);

    self.macrocontrato_select=ko.observable('');
    self.lista_contrato=ko.observableArray([]);
    self.contratista=ko.observable('');
    self.listado_contratista=ko.observableArray([]);
    self.contratoobra=ko.observable('');  
    self.lista_obra=ko.observableArray([]);
    self.lista_contrato_select=ko.observableArray([]);
    self.referencia=ko.observable('');

    self.anticipo_id=ko.observable('');
    self.mcontrato_id=ko.observable('');
    self.contrato_obra=ko.observable('');       

    //Representa un modelo de la tabla giro
    self.encabezado_giroVO={
        id:ko.observable(0),
        nombre_id:ko.observable('').extend({ required: { message: '(*)Seleccione el nombre del anticipo' } }),
        contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contrato' } }),
        soporte:ko.observable(''),
        referencia:ko.observable(''),
        num_causacion:ko.observable(''),
        fecha_conta:ko.observable(''),
        disparar_flujo:ko.observable(0),
        numero_radicado:ko.observable(''),
        referencia:ko.observable(''),
        texto_documento_sap:ko.observable('')
     };
     //paginacion de tab consultar y modificar
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
    //paginacion de tab consultar y modificar
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });
    //Funcion para crear la paginacion de tab consultar y modificar
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }
    //paginacion de tab no radicado
    self.paginacion_radicado = {
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
    //paginacion de tab no radicado
    self.paginacion_radicado.pagina_actual.subscribe(function (pagina) {
        self.consultar_no_radicado(pagina);
    });
    //Funcion para crear la paginacion de tan no radicado
    self.llenar_paginacion_radicado = function (data,pagina) {
        self.paginacion_radicado.pagina_actual(pagina);
        self.paginacion_radicado.total(data.count);       
        self.paginacion_radicado.cantidad_por_paginas(resultadosPorPagina);
    }
    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){
        ko.utils.arrayForEach(self.listado(), function(d) {
            d.eliminado(value);
        }); 
    });
    //funcion para abrir modal de registrar encabezado giro
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Giro');
        $('#modal_acciones').modal('show');
    }

    self.abrir_filtro = function (){
        self.titulo('Filtrar referencia');
        $('#modal_referencia').modal('show');
    }

    self.abrir_descarga = function (proyecto,nombregiro,encabezado_id){
        self.titulo('Soportes proyecto: '+proyecto+'-'+nombregiro);

        path = path_principal+'/api/soporteProcesoRelacionDato/?format=json&giro='+encabezado_id;
        parameter = {  };

        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje_soportes('');
                $('#reporte_descarga').modal('show');  
                self.listado_soporte(agregarOpcionesObservable(datos.data));                       
            }else{
                self.mensaje_soportes(mensajeNoFound);
                self.listado_soporte([]);
            } 

            cerrarLoading();
        }, path, parameter,undefined, false);      
    }    
     //limpiar el modelo 
     self.limpiar=function(){        
         
             self.encabezado_giroVO.id(0);
             self.encabezado_giroVO.contrato_id('');
             self.encabezado_giroVO.nombre_id('');
             self.encabezado_giroVO.soporte('');
             self.encabezado_giroVO.referencia('');
             self.encabezado_giroVO.num_causacion('');
             self.encabezado_giroVO.fecha_conta('')
             self.encabezado_giroVO.disparar_flujo(0);
             self.encabezado_giroVO.numero_radicado('');

             self.contratista(0);
             self.macrocontrato_select(0);
             self.lista_contrato_select([]);
             self.listado_contratista([]);

             self.encabezado_giroVO.nombre_id.isModified(false);
             self.encabezado_giroVO.contrato_id.isModified(false);      
     }

        self.filtros=function(contrato,contratista,departamento,municipio){

             path =path_principal+'/api/Proyecto/?filtros=1';
             parameter='';
             if (contrato!='') {
                parameter+='contrato_id='+contrato;
             }
             if (contratista!='') {
                parameter+='&id_contratista='+contratista;
             }
             if (departamento!='') {
                parameter+='&departamento_id='+departamento;
             }
             if (municipio!='') {
                parameter+='&municipio_id='+municipio;
             }                         
             RequestGet(function (results,count) {

            if(self.cambiar_contratista() == 0){
                    
                self.listado_contratista(results.data.contratistas)

            }            

            self.lista_obra(results.data.contratosobra)
            //self.proyecto_select(results.data.proyectos);
             }, path, parameter,undefined,false,false);             
        }

        //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
        self.macrocontrato_select.subscribe(function (value) {
            if(value >0){
                self.filtros(value,self.contratista(),0,0);
            }else{
                self.filtros('','','','');
            }
        });

        self.contratista.subscribe(function (value) {            
            if(value >0){
                self.cambiar_contratista(1);
                self.filtros(self.macrocontrato_select(),value,'','');
            }
        }); 

        //funcion guardar y actualizar el encabezado del giro
         self.guardar=function(){

            if (Encabezado_giroViewModel.errores_giros().length == 0) {//se activa las validaciones

                if(self.encabezado_giroVO.id()==0){

                    var parametros={                     
                         callback:function(datos, estado, mensaje){

                            if (estado=='ok') {
                                self.filtro("");
                                self.limpiar();
                                self.consultar(self.paginacion.pagina_actual());
                                self.consultar_no_radicado(1);
                                $('#modal_acciones').modal('hide');
                            }                        
                            
                         },//funcion para recibir la respuesta 
                         url:path_principal+'/api/Encabezado_giro/',//url api
                         parametros:self.encabezado_giroVO                        
                    };
                    //parameter =ko.toJSON(self.contratistaVO);
                    RequestFormData(parametros);
                }else{

                     if($('#archivo2')[0].files.length==0){
                        self.encabezado_giroVO.soporte('');
                    }                 

                      var parametros={     
                            metodo:'PUT',                
                           callback:function(datos, estado, mensaje){

                            if (estado=='ok') {
                              self.filtro("");
                              self.limpiar();
                              self.consultar(self.paginacion.pagina_actual());
                              self.consultar_no_radicado(1);
                              $('#modal_acciones').modal('hide');
                            }  

                           },//funcion para recibir la respuesta 
                           url:path_principal+'/api/Encabezado_giro/'+self.encabezado_giroVO.id()+'/',
                           parametros:self.encabezado_giroVO                        
                      };
                      RequestFormData(parametros);
                }

            } else {
                 Encabezado_giroViewModel.errores_giros.showAllMessages();//mostramos las validacion
            }
         }

        //funcion consultar tap de consultar y modificar de encabezado giro
        self.consultar = function (pagina) {
            
            //alert($('#mcontrato_filtro').val())
            if (pagina > 0) {            
                self.filtro($('#txtBuscar').val());

                path = path_principal+'/api/Encabezado_solicitud_giro/?format=json';
                parameter = { dato: self.filtro(), 
                              page: pagina,
                              disparar_flujo : 1,
                              flujotest : 0
                            };
                  
                // sin referencia = 1
                // con referencia = 2
                // todo igual a vacio     

                parameter.referencia = self.referencia() == '' ? 3 : 
                                       self.referencia() == 1 ? 1:
                                       self.referencia() == 2 ? 2:
                                       1;

                if (self.macrocontrato_select()!='') {
                    parameter.mcontrato_filtro=self.macrocontrato_select()
                }
                if (self.contratista()!='') {
                    parameter.contratista_filtro=self.contratista()
                }
                if (self.contratoobra()!='') {
                    parameter.contrato_filtro=self.contratoobra()
                }          

                sessionStorage.setItem("solicitud_giro_referencia_dato", self.filtro() || '');               
                // sessionStorage.setItem("solicitud_giro_referencia_referencia", self.referencia() || '');
                sessionStorage.setItem("solicitud_giro_referencia_macrocontrato", self.macrocontrato_select() || '');               
                sessionStorage.setItem("solicitud_giro_referencia_contratista", self.contratista() || '');
                sessionStorage.setItem("solicitud_giro_referencia_contrato_obra", self.contratoobra() || '');               

                RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                        self.mensaje('');
                        $('#modal_referencia').modal('hide'); 
                        self.listado(agregarOpcionesObservable(datos.data));                        

                    } else {
                        self.listado([]);
                        $('#modal_referencia').modal('hide'); 
                        self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    }

                    self.llenar_paginacion(datos,pagina);
                    cerrarLoading();
                }, path, parameter,undefined, false);
            }
        }

    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    //guardar la fecha del radicado o numero de radicado en el tan no radicado
    self.guardar_no_referencia=function(obj){ 

            if (  ( (obj.referencia!='') && (obj.fecha_conta==null || obj.fecha_conta=='') && (obj.texto_documento_sap=='') ) || ( (obj.referencia=='') && (texto_documento_sap!='') && (obj.fecha_conta=='' || obj.fecha_conta==null) )  || ( (obj.referencia=='') && (texto_documento_sap=='') && (obj.fecha_conta!='' || obj.fecha_conta!=null) ) ) {
                // alert("referecia="+obj.referencia+" fecha ="+obj.fecha_conta)
                mensajeInformativo('Debe registrar fecha, texto documento y numero de referencia','Mensaje')
            }else{
                $('input:focus').blur()
                var parametros={

                        callback:function(datos, estado, mensaje){

                           if (estado=='ok') {
                               self.filtro("");
                               self.consultar(self.paginacion.pagina_actual());
                                //mensajeExitoso(estado);
                               self.limpiar();
                           }                      
                           
                        },//funcion para recibir la respuesta 
                        url:path_principal+'/solicitud_giro/actualizar_referencia/',//url api
                        parametros:{id:obj.id,referencia:obj.referencia,fecha_conta:obj.fecha_conta,texto_documento_sap:obj.texto_documento_sap}
                   };                    

                   Request(parametros);
            }
            //parameter =ko.toJSON(self.contratistaVO);
     }
    //funcion para seleccionar que reporte generar en el encabezado giro
    self.reporte_de_giro = function (obj) {
        
        self.anticipo_id(obj.id);
        if(obj.contrato.mcontrato){
          self.mcontrato_id(obj.contrato.mcontrato.id);
        }
        
        self.contrato_obra(obj.contrato.id);
        self.titulo('Reporte de giro');
        $('#reporte_giro').modal('show');
    }    
    //funcion para seleccionar que reporte de encabezado del giro se generara
    self.generar_reporte_giro=function(){

        var opcion = $("input[name='reporteGiro']:checked").val();
        //var id = $("#id_anticipo").val();
        if(opcion=="solicitudAnticipo"){
          location.href=path_principal+"/giros/reporte_anticipo2/?encabezado_id="+self.anticipo_id();
        }else{            
          location.href=path_principal+"/giros/reporte_giro_exportar/?encabezado_id="+self.anticipo_id();
        }
    }           

}

var encabezado_giro = new Encabezado_giroViewModel();

$('#txtBuscar').val(sessionStorage.getItem("solicitud_giro_referencia_dato"))   
// encabezado_giro.referencia(sessionStorage.getItem("solicitud_giro_referencia_referencia"));
encabezado_giro.macrocontrato_select(sessionStorage.getItem("solicitud_giro_referencia_macrocontrato"));
encabezado_giro.contratista(sessionStorage.getItem("solicitud_giro_referencia_contratista"));
encabezado_giro.contratoobra(sessionStorage.getItem("solicitud_giro_referencia_contrato_obra"));

Encabezado_giroViewModel.errores_giros = ko.validation.group(encabezado_giro.encabezado_giroVO);
ko.applyBindings(encabezado_giro);
