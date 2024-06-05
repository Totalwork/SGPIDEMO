function ContratoVigenciaViewModel() {

    var self = this;
    self.listado = ko.observableArray([]);
    self.mensaje = ko.observable('');
    self.titulo = ko.observable('');
    self.filtro = ko.observable('');
    self.checkall = ko.observable(false);

    self.tipos = ko.observableArray([]);
    self.lista_tipos = ko.observableArray([]);
    self.contrato_actual = ko.observableArray([]);
    self.indefinido = ko.observable();
    self.definido = ko.observable('definido');
    self.dis_f_fin = ko.observable(true);
    self.dis_f_inicio = ko.observable(true);
    self.dis_actas = ko.observable(false);
    self.lista_actas = ko.observableArray([]);
    self.lista_actas_suspension = ko.observableArray([]);
    self.lista_actas_prorrogas = ko.observableArray([]);
    self.tipo_actas = ko.observableArray([]);

    // Datos del contrato
    self.contratante = ko.observable('');
    self.contratista = ko.observable('');
    self.numero = ko.observable('');
    self.nombre = ko.observable('');
    self.estado_c = ko.observable('');
    self.id_estado_c = ko.observable('');

    self.tituloTable = ko.observable('');
    self.length_lista = ko.observable(0);

    self.fecha_inicio = ko.observable('');
    self.fecha_fin = ko.observable('');
    self.a_suspension = ko.observable('');
    self.a_reinicio = ko.observable('');
    self.soporte = ko.observable('');
    // Para validar los radio button, en edicion de actas
    self.reinicio = ko.observable(0);

    self.listadoPoliza = ko.observableArray([]);
    self.mensajePoliza = ko.observable('');
    self.nombre_vigencia = ko.observable('');

    self.tipo = {
        contratoProyecto: ko.observable(8),
        interventoria: ko.observable(9),
        medida: ko.observable(10),
        retie: ko.observable(11),
        m_contrato: ko.observable(12),
        suministros: ko.observable(13),
        obra: ko.observable(14),
        otros: ko.observable(15)
    };
    self.estado = {
        vigente: ko.observable(28),
        liquidado: ko.observable(29),
        suspendido: ko.observable(30),
        porVencer: ko.observable(31),
        vencido: ko.observable(32)
    };
    self.tipoV = {
        contrato: ko.observable(16),
        otrosi: ko.observable(17),
        actaSuspension: ko.observable(18),
        actaReinicio: ko.observable(19),
        replanteo: ko.observable(20),
        liquidacion: ko.observable(21),
        actaInicio: ko.observable(22),
        actaAmpliacion: ko.observable(),
        prorroga: ko.observable(102)
    };

    ///self.url=path_principal+'api/contrato';
    //Representa un modelo de la tabla xxxx
    self.vigenciaVO = {
        id: ko.observable(0),
        nombre: ko.observable(''),
        contrato_id: ko.observable(0),
        tipo_id: ko.observable('').extend({ required: { message: '(*)Seleccione un tipo' } }),
        fecha_inicio: ko.observable(''),//.extend({ required: { message: '(*)Seleccione una fecha' } }),
        fecha_fin: ko.observable(''),
        valor: ko.observable(0),
        soporte: ko.observable('').extend({ required: { message: '(*)Seleccione el soporte' } }),
        acta_id: ko.observable('')
    };

    self.changed_indefinido = function() {

        self.dis_f_fin(false);
        self.vigenciaVO.fecha_fin('');
        self.definido('');
    }
    self.changed_definido = function() {

        self.dis_f_fin(true);
        self.indefinido('');
    }
    self.changed_prorroga = function() {

        self.dis_f_fin(false);
        self.dis_f_inicio(true);
        self.dis_actas(false);
        self.vigenciaVO.acta_id('');
        if (self.vigenciaVO.tipo_id() == self.tipoV.prorroga()) {
            self.dis_f_fin(true);
            self.dis_f_inicio(false);
            self.dis_actas(true);

            self.vigenciaVO.fecha_inicio('');
        }//else if(self.vigenciaVO.tipo_id() == self.tipoV.actaReinicio()){
        //     self.dis_f_inicio(true);
        // }
    }

    self.changed_acta_suspension = function(){

        if(self.vigenciaVO.acta_id() != ''){
            self.list_actas_prorroga(self.vigenciaVO.acta_id());
        }
    }

    self.paginacion = {
        pagina_actual: ko.observable(0),
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

    //Funcion para crear la paginacion
    self.llenar_paginacion = function(data, pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }

    self.paginacion.pagina_actual.subscribe(function(pagina) {
        self.consultar(pagina);
    });

    self.abrir_modal = function() {
        self.limpiar();
        //self.habilitar_campos(true);
        self.titulo('Registrar Actas');
        $('#modal_acciones').modal('show');
        // ko.bindingHandlers.datePicker.init(
        // 				$('#fecha_inicio'),self.fecha_inicio,ko.observable({dateTimePickerOptions:{minDate:self.fecha_inicio()}})
        // );
    }

    /*$('#modal_acciones').on('shown.bs.modal', function () {

    			$('#vigenciaVO.fecha_inicio').datetimepicker('setStartDate', '2017-01-01');
    			// ko.bindingHandlers.datePicker.init(
    			// 	$('#fecha_inicio'),self.fecha_inicio,ko.observable({dateTimePickerOptions:{minDate:self.fecha_inicio()}})
    			// );
    });*/

    // limpiar el modelo 
    self.limpiar = function() {
        self.vigenciaVO.id(0);
        self.vigenciaVO.tipo_id('');
        self.vigenciaVO.fecha_inicio('');
        self.vigenciaVO.fecha_fin('');
        self.vigenciaVO.valor('');
        self.vigenciaVO.soporte('');
        self.vigenciaVO.acta_id('');
        $('#archivo').fileinput('reset');
        $('#archivo').val('');
        // check_eliminar(false)

        self.vigenciaVO.tipo_id.isModified(false);
        self.vigenciaVO.soporte.isModified(false);
    }

    //exportar excel
    self.exportar_excel = function() {
        // location.href=path_principal+"/empresa/export?dato="+self.filtro()+"&esContratista=1&esContratante=0&esProveedor=0&esDisenador=0";
    }

    // funcion guardar
    self.guardar = function() {
        var validar_fecha = false;

        if (ContratoVigenciaViewModel.errores_vigencia().length == 0) { //se activa las validaciones
            if (self.vigenciaVO.id() == 0) {

                if (self.vigenciaVO.tipo_id() != self.tipoV.actaInicio() && self.definido() == 'definido' && self.vigenciaVO.fecha_fin() == '') {

                    mensajeInformativo('Seleccione la fecha fin', 'Información');
                }else if (self.vigenciaVO.tipo_id() == self.tipoV.prorroga() && self.vigenciaVO.fecha_fin() == '') {
                    
                    mensajeInformativo('Seleccione la fecha fin', 'Información');
                }else if (self.vigenciaVO.tipo_id() == self.tipoV.prorroga() && self.vigenciaVO.acta_id() == '') {
                    
                    mensajeInformativo('Seleccione un acta de suspension.', 'Información');
                } else {
                    self.vigenciaVO.soporte($('#archivo')[0].files[0]);

                    if (self.vigenciaVO.tipo_id() == self.tipoV.actaSuspension()) {

                        self.vigenciaVO.nombre('Acta de suspension No. ' + (self.lista_actas().length + 1));

                        // Validar rango de fechas
                        if ((self.vigenciaVO.fecha_inicio() > self.fecha_inicio()) && (self.vigenciaVO.fecha_inicio() > self.a_reinicio())) {
                            validar_fecha = true;
                            //console.log("okk:"+validar_fecha);

                        } else {
                            validar_fecha = false;
                            mensajeInformativo('La fecha inicio esta por fuera del rango', 'Información');
                            //console.log("Noo:"+validar_fecha);
                        }
                    } else if (self.vigenciaVO.tipo_id() == self.tipoV.actaReinicio()) {

                        self.vigenciaVO.nombre('Acta de reinicio No. ' + (self.lista_actas().length + 1));

                        // Validar rango de fechas
                        if (self.vigenciaVO.fecha_inicio() > self.a_suspension()) {
                            validar_fecha = true;
                            //console.log("okk:"+validar_fecha);

                        } else {
                            validar_fecha = false;
                            mensajeInformativo('La fecha inicio esta por fuera del rango', 'Información');
                            //console.log("Noo:"+validar_fecha);
                        }
                    } else if (self.vigenciaVO.tipo_id() == self.tipoV.actaInicio()) {

                        self.vigenciaVO.nombre('Acta de inicio');

                        // Validar rango de fechas
                        if (self.vigenciaVO.fecha_inicio() != '') {
                            validar_fecha = true;
                        } else {
                            validar_fecha = false;
                            mensajeInformativo('Seleccione la fecha inicio', 'Información');
                            //console.log("Noo:"+validar_fecha);
                            return;
                        }
                    } else if (self.vigenciaVO.tipo_id() == self.tipoV.prorroga()) {
                        if (self.vigenciaVO.acta_id() != '') {

                            var nombre_suspension = '';
                            validar_fecha = true;

                            ko.utils.arrayForEach(self.lista_actas_suspension(), function(p) {
                                if (p.id() == self.vigenciaVO.acta_id()) {
                                    nombre_suspension = p.nombre();
                                }
                            });
                            self.vigenciaVO.nombre('Prórroga No.'+(self.lista_actas_prorrogas().length + 1)+' del '+nombre_suspension );
                        }else{
                            console.log("Select de Actas vacio")
                        }
                    }else{
                        validar_fecha = true;
                    }
                    self.vigenciaVO.valor(0);

                    if (validar_fecha) {
                        var parametros = {
                            callback: function(datos, estado, mensaje) {

                                if (estado == 'ok') {

                                    $('#modal_acciones').modal('hide');
                                    self.limpiar();
                                    self.consultar(self.vigenciaVO.contrato_id());
                                } else {
                                    mensajeError(mensaje);
                                }
                            }, //funcion para recibir la respuesta 
                            url: path_principal + '/api/Vigencia_contrato/', //url api
                            parametros: self.vigenciaVO,
                            completado: function() { self.contrato(self.vigenciaVO.contrato_id()); self.list_actas_suspension(); }
                        };

                        //parameter =ko.toJSON(self.vigenciaVO);
                        //Request(parametros);
                        RequestFormData(parametros);
                    }
                }
            } else if (self.definido() == 'definido' && self.vigenciaVO.fecha_fin() == '') {

                mensajeInformativo('Seleccione la fecha fin', 'Información');
            }else if (self.vigenciaVO.tipo_id() == self.tipoV.prorroga() && self.vigenciaVO.fecha_fin() == '') {
                
                mensajeInformativo('Seleccione la fecha fin', 'Información');
            }else if (self.vigenciaVO.tipo_id() == self.tipoV.prorroga() && self.vigenciaVO.acta_id() == '') {
               
                mensajeInformativo('Seleccione un acta de suspension.', 'Información');
            } else {

                if ($('#archivo')[0].files.length == 0) {
                    self.vigenciaVO.soporte('');
                }

                var parametros = {
                    metodo: 'PUT',
                    callback: function(datos, estado, mensaje) {

                        if (estado == 'ok') {
                            self.filtro("");
                            self.consultar(self.vigenciaVO.contrato_id());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }

                    }, //funcion para recibir la respuesta 
                    url: path_principal + '/api/Vigencia_contrato/' + self.vigenciaVO.id() + '/',
                    parametros: self.vigenciaVO
                };
                RequestFormData(parametros);
            }
        } else {
            ContratoVigenciaViewModel.errores_vigencia.showAllMessages();
        }
    }

    //funcion para consultar actas
    self.consultar = function(id_contrato) {

        self.filtro($('#txtBuscar').val());

        //self.tipo_actas([self.tipoV.actaSuspension(),self.tipoV.actaReinicio()]);
        //var lista=[];
        lista = self.tipoV.actaSuspension();
        lista = lista + ',' + self.tipoV.actaReinicio();
        lista = lista + ',' + self.tipoV.prorroga();
        lista = lista + ',' + self.tipoV.actaInicio();

        if (self.filtro()) {
            parameter = { id_contrato: id_contrato, nombre: self.filtro(), id_tipo: lista };
        } else {
            parameter = { id_contrato: id_contrato, id_tipo: lista };
        }

        path = path_principal + '/api/Vigencia_contrato/?format=json&sin_paginacion';
        RequestGet(function(data, success, mensage) {

            if (success == 'ok' && data != null && data.length > 0) {
                self.mensaje('');
                //self.listado(results);
                self.listado(agregarOpcionesObservable(data));
                self.length_lista(self.listado().length);
                //console.log("num:"+self.length_lista());
            } else {
                self.listado([]);
                self.mensaje(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
            }
            //self.llenar_paginacion(data,pagina);
        }, path, parameter, function() { cerrarLoading(); }, false);
    }

    self.consulta_enter = function(d, e) {
        if (e.which == 13) {
            //self.filtro($('#txtBuscar').val());
            self.consultar(self.vigenciaVO.contrato_id());
        }
        return true;
    }

    // Para editar el acta
    self.consultar_por_id = function(obj) {

        //alert(obj.id); return false;
        path = path_principal + '/api/Vigencia_contrato/' + obj.id + '/?format=json';
        parameter = {};
        RequestGet(function(datos, estado, mensaje) {

            self.titulo('Actualizar Vigencia Contrato');
            //console.log("asas: "+results[0].id);

            self.vigenciaVO.id(datos.id);
            self.vigenciaVO.tipo_id(datos.tipo.id);
            self.vigenciaVO.nombre(datos.nombre);

            self.vigenciaVO.valor(datos.valor);
            self.vigenciaVO.soporte(datos.soporte);
            self.soporte(datos.soporte);
            //self.habilitar_campos(true);
            $('#modal_acciones').modal('show');

            self.ponerTipoEditar(datos.tipo.id);

            if (datos.fecha_inicio) {
                self.vigenciaVO.fecha_inicio(datos.fecha_inicio);
            }else{
                self.vigenciaVO.fecha_inicio('');
            }

            if (datos.fecha_fin) {
                self.dis_f_fin(true);
                self.definido('definido');
                self.indefinido('');
                self.vigenciaVO.fecha_fin(datos.fecha_fin);
            } else {
                self.dis_f_fin(false);
                self.indefinido('indefinido');
                self.definido('');
                self.vigenciaVO.fecha_fin('');
            }

            if(datos.acta_id != null){

                self.vigenciaVO.acta_id(datos.acta_id);
                self.dis_actas(true);
            }else{
                self.vigenciaVO.acta_id('');
            }
        }, path, parameter);
    }

    self.eliminar = function(obj) {

        var path = path_principal + '/api/Vigencia_contrato/' + obj.id + '/';
        var parameter = {};
        RequestAnularOEliminar("Esta seguro que desea eliminar el acta?", path, parameter, function() {
            self.consultar(self.vigenciaVO.contrato_id());
            self.contrato(self.vigenciaVO.contrato_id());
        });
    }

    //consultar tipos de vigencia del contrato
    self.listaTipo = function(dato) {
        parameter = '';
        path = path_principal + '/api/Tipos/?aplicacion=' + dato + '&format=json';

        RequestGet(function(results, count) {

            self.tipos(results.data);
        }, path, parameter, function() {
            setTimeout(function() { 
                self.contrato(self.vigenciaVO.contrato_id());
                self.list_actas_suspension();
            }, 1000);
        }, false);
    }

    //consultar actas del contrato actual
    self.list_actas_contrato = function() {

        if (self.vigenciaVO.tipo_id() == self.tipoV.actaSuspension()) {
            parameter = { id_contrato: self.vigenciaVO.contrato_id(), id_tipo: self.tipoV.actaSuspension(), sin_paginacion: 1 };
            path = path_principal + '/api/Vigencia_contrato/?format=json';
            RequestGet(function(data, success, message) {
                //console.log(datos);
                self.lista_actas(convertToObservableArray(data));
                //console.log(self.lista_actas().length);
                // ko.utils.arrayForEach(self.lista_actas(),function (p) {
                // 	console.log(p);
                // });

            }, path, parameter, function() {
                self.guardar();
            });
        } else if (self.vigenciaVO.tipo_id() == self.tipoV.actaReinicio()) {
            parameter = { id_contrato: self.vigenciaVO.contrato_id(), id_tipo: self.tipoV.actaReinicio(), sin_paginacion: 1 };
            path = path_principal + '/api/Vigencia_contrato/?format=json';
            RequestGet(function(data, success, message) {
                //console.log(datos);
                self.lista_actas(convertToObservableArray(data));
                //console.log(self.lista_actas().length);

            }, path, parameter, function() {
                self.guardar();
            });
        } else { self.guardar(); }
    }

    // Consultar todas las actas de Suspension del contrato
    self.list_actas_suspension = function() {

        parameter = { id_contrato: self.vigenciaVO.contrato_id(), id_tipo: self.tipoV.actaSuspension(), sin_paginacion: 1 };
        path = path_principal + '/api/Vigencia_contrato/?format=json';

        RequestGet(function(data, success, message) {

            self.lista_actas_suspension(convertToObservableArray(data));
            // console.log(self.lista_actas_suspension().length);

        }, path, parameter);
    }

    self.list_actas_prorroga = function(dato) {

        parameter = { id_contrato: self.vigenciaVO.contrato_id(), id_tipo: self.tipoV.prorroga(), id_acta:dato, sin_paginacion: 1 };
        path = path_principal + '/api/Vigencia_contrato/?format=json';

        RequestGet(function(data, success, message) {

            self.lista_actas_prorrogas(convertToObservableArray(data));
            // console.log(convertToObservableArray(data).length);
        }, path, parameter);
    }

    //consultar el contrato actual
    self.contrato = function(dato) {
        parameter = {};
        path = path_principal + '/api/Contrato/' + dato + '/?format=json';

        RequestGet(function(results, count) {

            self.contrato_actual(results);

            self.contratante(results.contratante.nombre);
            self.contratista(results.contratista.nombre);
            self.numero(results.numero);
            self.nombre(results.nombre);
            self.estado_c(results.estado.nombre);
            self.id_estado_c(results.estado.id);

            self.tituloTable('Listado Actas - contrato N° ' + self.numero() + ' - ' + self.nombre());

            // Buscar fecha fin y de Inicio del contrato
            /*ko.utils.arrayForEach(results.vigencia_contrato,function(p){
            	if (p.tipo.id == self.tipoV.contrato()) {
            		self.fecha_inicio(p.fecha_inicio);
            		self.fecha_fin(p.fecha_fin);

            		//console.log(p.)
            	}
            });
            ko.utils.arrayForEach(results.vigencia_contrato,function(p){
            	if (p.tipo.id == self.tipoV.replanteo()){
            		//self.fecha_inicio(p.fecha_inicio);
            		self.fecha_fin(p.fecha_fin);
            	}
            });
            ko.utils.arrayForEach(results.vigencia_contrato,function(p){
            	if (p.tipo.id == self.tipoV.otrosi()){
            		if (p.fecha_fin) {
            			self.fecha_fin(p.fecha_fin);
            		}
            	}
            });*/

            // Buscar las fechas de las actas
            self.a_suspension('');
            self.a_reinicio('');
            ko.utils.arrayForEach(results.vigencia_contrato, function(p) {
                if (p.tipo.id == self.tipoV.actaSuspension()) {
                    self.a_suspension(p.fecha_inicio);
                }
                if (p.tipo.id == self.tipoV.actaReinicio()) {
                    self.a_reinicio(p.fecha_inicio);
                }
            });

            self.fecha_inicio(fechasInicio(results.vigencia_contrato));
            self.fecha_fin(fechasFin(results.vigencia_contrato));

            // console.log("f_i:"+self.fecha_inicio());
            // console.log("f_f:"+self.fecha_fin());
            // console.log("a_s:"+self.a_suspension());
            // console.log("a_r:"+self.a_reinicio());
            // alert("f_i:"+self.fecha_inicio());
        }, path, parameter, function() {
            // Llena el select de tipos, dependiendo del estado del contrato actual

            //console.log(self.contrato_actual().estado.id);
            // self.lista_tipos = ko.observableArray([]);
            self.lista_tipos([{}])
            var listaV = [];
            if (self.contrato_actual().estado.id != self.estado.suspendido()) {                
                ko.utils.arrayForEach(self.tipos(), function(p) {
                    if (p.id == self.tipoV.actaSuspension() || p.id == self.tipoV.actaInicio()) {
                        listaV.push(p);
                        self.reinicio(0);
                    }
                });

                self.lista_tipos(listaV);
            } else if (self.contrato_actual().estado.id == self.estado.suspendido()) {
                var listaV = [];
                ko.utils.arrayForEach(self.tipos(), function(p) {

                    if ((p.id == self.tipoV.actaReinicio()) || (p.id == self.tipoV.prorroga() || p.id == self.tipoV.actaInicio())) {
                        listaV.push(p);
                        listaV.push(p);
                        self.reinicio(1);
                    }
                });
                self.lista_tipos(listaV);
                self.dis_f_fin(false);
                self.definido('');
                self.indefinido('indefinido');
            }
            cerrarLoading();
        }, false);
    }

    self.ponerTipoEditar = function(tipoActual) {
        
        ko.utils.arrayForEach(self.tipos(), function(p) {
            if (p.id == tipoActual) {
                self.lista_tipos(p);
                self.vigenciaVO.tipo_id(p.id);

                if (tipoActual == self.tipoV.actaReinicio()) {
                    console.log("editando un acta de reinicio");
                    self.reinicio(1);
                } else {
                    self.reinicio(0);
                }
            }
        });
    }

    // consulta polizas
    self.consultarPoliza = function(obj) {

        //console.log("id:"+obj.id)
        path = path_principal + '/api/VigenciaPoliza/?sin_paginacion=0&id_documento=' + obj.id + '&lite=1&format=json';
        // path = path_principal+'/api/VigenciaPoliza/?sin_paginacion=0&id_documento=1&lite=1&format=json';
        parameter = {};

        RequestGet(function(datos, estado, mensage) {
            $('#modal_polizas').modal('show');

            if (estado == 'ok' && datos != null && datos.length > 0) {
                self.mensajePoliza('');
                self.listadoPoliza(agregarOpcionesObservable(datos));
                self.nombre_vigencia(obj.nombre)
            } else {
                self.listadoPoliza([]);
                self.nombre_vigencia(obj.nombre);
                self.mensajePoliza(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);
    }

     self.ver_soporte = function(obj) {
      window.open(path_principal+"/contrato/ver-soporte/?id="+ obj.id, "_blank");
     }

     self.ver_soporte_poliza = function(obj) {
      window.open(path_principal+"/poliza/ver-soporte/?id="+ obj.id, "_blank");
     }

    /*ko.bindingHandlers.datepicker = {
    init: function(element, valueAccessor, allBindingsAccessor) {
        var $el = $(element);
        
        //initialize datepicker with some optional options
        var options = allBindingsAccessor().datepickerOptions || {};
        $el.datepicker(options);

        //handle the field changing
        ko.utils.registerEventHandler(element, "change", function() {
            var observable = valueAccessor();
            observable($el.datepicker("getDate"));
        });

        //handle disposal (if KO removes by the template binding)
        ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            $el.datepicker("destroy");
        });

    },
    update: function(element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor()),
            $el = $(element),
            current = $el.datepicker("getDate");
        
        if (value - current !== 0) {
            $el.datepicker("setDate", value);   
        }
    }
	};*/
}

var contratoVigencia = new ContratoVigenciaViewModel();
ContratoVigenciaViewModel.errores_vigencia = ko.validation.group(contratoVigencia.vigenciaVO);

contratoVigencia.listaTipo('VigenciaContrato'); //iniciamos la primera funcion

var content = document.getElementById('content_wrapper');
var header = document.getElementById('header');
ko.applyBindings(contratoVigencia, content);
ko.applyBindings(contratoVigencia, header);