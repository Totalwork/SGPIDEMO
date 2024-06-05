function Encabezado_giroViewModel() {
        
        var self = this;
        self.listado=ko.observableArray([]);
        self.listado2=ko.observableArray([]);
        self.listado_no_radicado=ko.observableArray([]);
        self.mensaje=ko.observable('');
        self.mensaje_no_radicado=ko.observable('');
        self.titulo=ko.observable('');
        self.filtro=ko.observable('');
        self.checkall=ko.observable(false);
        self.soporte_arriba=ko.observable('');
        self.idProcesoRelacion =ko.observable(0);
        self.cambiar_contratista=ko.observable(0);
        self.desde=ko.observable('');
        self.hasta=ko.observable('');


        self.macrocontrato_select=ko.observable('');
        self.lista_contrato=ko.observableArray([]);
        self.contratista=ko.observable('');
        self.listado_contratista=ko.observableArray([]);
        self.contratoobra=ko.observable('');  
        self.lista_obra=ko.observableArray([]);
        self.lista_contrato_select=ko.observableArray([]);
        self.referencia=ko.observable('');    

        //observables del encabezado del detalle del giro
        self.contratista_encabezado=ko.observable('');
        self.contratante_encabezado=ko.observable('');
        self.numero_contrato_encabezado=ko.observable('');
        self.nombre_anticipo_encabezado=ko.observable('');
        self.nombre_proyecto_encabezado=ko.observable('');
        self.suma_valor_detalles=ko.observable('');
        self.encabezado_del_detalle=ko.observable('');  
        
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

        //funcion para seleccionar los datos a eliminar
        self.checkall.subscribe(function(value ){
            ko.utils.arrayForEach(self.listado(), function(d) {
                d.eliminado(value);
            }); 
        });

        self.abrir_filtro = function (){
            self.consultar_contratistas();
            self.titulo('Filtrar Giros');
            $('#modal_referencia').modal('show');
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

        self.consultar_contratistas = function(){

            path =path_principal+'/proyecto/select-filter-proyecto/';         
            parameter = { consulta_contratista : 1 
                            ,mcontrato: self.macrocontrato_select() };

            RequestGet(function (results,count) {                                     
                self.listado_contratista(results.contratistas)
                cerrarLoading();
            }, path, parameter,undefined, false);
        }
        //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
        self.macrocontrato_select.subscribe(function (value) {
            self.consultar_contratistas();
            self.consultar(1);
        });    

        self.contratista.subscribe(function (value) {            
            self.consultar();
        });

        //funcion guardar y actualizar el encabezado del giro
         self.guardar=function(){
            
         }


        //funcion consultar tap de consultar y modificar de encabezado giro
        self.consultar = function (pagina) {
            
            //alert($('#mcontrato_filtro').val())
            if (pagina > 0) {            
                self.filtro($('#txtBuscar').val());

                path = path_principal+'/api/Detalle_giro/?lite=1&sinpago=1';
                parameter = { dato: self.filtro(), 
                              page: pagina,
                            };
                if (self.referencia()=='') {
                    parameter.referencia=1
                }
                if (self.referencia()==1) {
                    parameter.referencia=3
                }                        
                if (self.macrocontrato_select()!='') {
                    parameter.mcontrato_filtro=self.macrocontrato_select()
                }
                if (self.contratista()!='') {
                    parameter.contratista_filtro=self.contratista()
                }
                if (self.contratoobra()!='') {
                    parameter.dato=self.contratoobra()
                }
                if (self.desde()!='') {
                    parameter.fechadesde=self.desde()
                } 
                if (self.hasta()!='') {
                    parameter.fechahasta=self.hasta()
                }                                                        
                RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                        self.mensaje('');                        
                        self.listado(agregarOpcionesObservable(datos.data));
                    } else {
                        self.listado([]);
                        self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js     
                    }
                    // $('#modal_referencia').modal('hide'); 
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
        self.guardar_no_codigo_pago=function(obj){ 

            if (obj.codigo_pago=='') {
                    
                mensajeInformativo('Debe llenar los datos seleccionados','Mensaje')
            }else{
                console.log(obj.fecha_conta)
                var parametros={

                        callback:function(datos, estado, mensaje){

                           if (estado=='ok') {
                               self.filtro("");
                               self.consultar(1);
                           }                      
                           
                        },//funcion para recibir la respuesta 
                        url:path_principal+'/solicitud_giro/registrar_codigo/',//url api
                        parametros:{id:obj.id,codigo_pago:obj.codigo_pago}
                   };                    

                   Request(parametros);
            }
            //parameter =ko.toJSON(self.contratistaVO);     
         }     
        
}


var encabezado_giro = new Encabezado_giroViewModel();
Encabezado_giroViewModel.errores_giros = ko.validation.group(encabezado_giro.encabezado_giroVO);

ko.applyBindings(encabezado_giro);