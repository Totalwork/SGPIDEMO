function ContratoVigenciaViewModel() {

    var self = this;
    self.listado = ko.observableArray([]);
    self.mensaje_vigencia = ko.observable('');
    self.mensaje_proyecto = ko.observable('');
    self.mensaje_actas = ko.observable('');
    self.mensaje_poliza = ko.observable('');
    self.filtro = ko.observable('');

    self.lista_proyecto2 = ko.observableArray([]);
    self.lista_actas = ko.observableArray([]);
    self.lista_poliza = ko.observableArray([]);

    self.numero_c = ko.observable('');
    self.nombre_c = ko.observable('');
    self.titulo_tab = ko.observable('');

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
        prorroga: ko.observable(102)
    };

    //Representa un modelo de la tabla xxxx
    self.vigenciaVO = {
        id: ko.observable(0),
        nombre: ko.observable(),
        contrato_id: ko.observable(0),
        tipo_id: ko.observable('').extend({ required: { message: '(*)Seleccione el valor del contrato' } }),
        fecha_inicio: ko.observable(''),
        fecha_fin: ko.observable(''),
        valor: ko.observable('').extend({ required: { message: '(*)Digite el valor' } }),
        soporte: ko.observable('').extend({ required: { message: '(*)Seleccione el soporte' } })
    }

    // resumen del contrato
    self.detalle = {
        contratante: ko.observable(''),
        contratista: ko.observable(''),
        numero: ko.observable(''),
        nombre: ko.observable(''),
        estado_c: ko.observable(''),
        descripcion: ko.observable(''),
        m_contrato: ko.observable(''),
        f_inicio: ko.observable(''),
        f_fin: ko.observable(''),
        valor: ko.observable(''),
        liquidacion: ko.observable('')
    }

    self.paginacion = {
        pagina_actual: ko.observable(0),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
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
        //self.consultar(pagina);
    });

    // INICIO CONTRATO_RESUMEN
    // consulta el detalle del contrato
    self.list_contrato = function(contrato) {

            path = path_principal + '/api/Contrato/' + contrato + '/?format=json';
            parameter = {};

            RequestGet(function(data, estado, mensage) {

                console.log(data.contratante.nombre)

                self.detalle.contratante(data.contratante.nombre);
                self.detalle.contratista(data.contratista.nombre);
                self.detalle.numero(data.numero);
                self.detalle.nombre(data.nombre);
                self.detalle.estado_c(data.estado.nombre);
                self.detalle.descripcion(data.descripcion);

                self.detalle.m_contrato('');
                if (data.mcontrato) {
                    self.detalle.m_contrato(data.mcontrato.nombre);
                } else {
                    self.detalle.m_contrato('');
                }

                ko.utils.arrayForEach(data.vigencia_contrato, function(p) {

                    if (p.tipo.id == self.tipoV.contrato()) {
                        self.detalle.f_inicio(p.fecha_inicio);
                        self.detalle.valor(p.valor);
                        self.detalle.f_fin(p.fecha_fin);
                        //console.log(p.)
                    }
                    if (p.tipo.id == self.tipoV.replanteo()) {
                        self.detalle.f_inicio(p.fecha_inicio);
                        self.detalle.valor(p.valor);
                        self.detalle.f_fin(p.fecha_fin);
                    }
                    if (p.tipo.id == self.tipoV.liquidacion()) {
                        self.detalle.liquidacion(p.valor);
                    }
                    if (p.tipo.id == self.tipoV.otrosi()) {
                        if (p.fecha_fin) {
                            self.detalle.f_fin(p.fecha_fin);
                        }
                    }
                });
            }, path, parameter, function() {
                $('#detalle_contrato').modal('show');
                cerrarLoading();
            }, false);
        }
        // FIN DE CONTRATO_RESUMEN

    // INICIO VIGENCIAS
    self.list_vigencias = function(id_contrato) {

            lista = self.tipoV.contrato();
            lista = lista + ',' + self.tipoV.otrosi();
            lista = lista + ',' + self.tipoV.replanteo();
            lista = lista + ',' + self.tipoV.liquidacion();

            parameter = { id_contrato: id_contrato, id_tipo: lista };

            path = path_principal + '/api/Vigencia_contrato/?format=json&sin_paginacion';
            RequestGet(function(data, success, mensage) {

                if (success == 'ok' && data != null && data.length > 0) {
                    self.mensaje_vigencia('');
                    //self.listado(results);
                    self.listado(agregarOpcionesObservable(data));

                    self.numero_c(data[0].contrato.numero);
                    self.nombre_c(data[0].contrato.nombre);
                    self.titulo_tab('Contrato N° ' + self.numero_c() + ' - ' + self.nombre_c().substr(0, 50));

                } else {
                    self.listado([]);
                    self.mensaje_vigencia(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                //self.llenar_paginacion(data,pagina);
            }, path, parameter, function() {}, false);
        }
        // FIN VIGENCIAS

    self.consulta_enter = function(d, e) {
        if (e.which == 13) {
            //self.filtro($('#txtBuscar').val());
            //self.consultar(self.vigenciaVO.contrato_id());
        }
        return true;
    }

    // INICIO - GESTION DE PROYECTO
    self.list_proyecto2 = function() {
            path = path_principal + '/api/Proyecto/?';

            /*var contrato = self.macrocontrato_select2();
            var contratista = self.contratista2();
            var departamento = self.departamento2();
            var municipio = self.municipio2();*/
            var contrato_obra = self.vigenciaVO.contrato_id();

            if (contrato_obra != 0) {
                path += 'contrato_obra=' + contrato_obra;
            }

            parameter = {};
            RequestGet(function(results, success, message) {

                if (success == 'ok' && results.data != null && results.data.length > 0) {
                    self.mensaje_proyecto('');
                    self.lista_proyecto2(agregarOpcionesObservable(results.data));
                } else {
                    self.lista_proyecto2([]);
                    self.mensaje_proyecto(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                    //mensajeInformativo('No se encontraron registros');
                }
                //self.llenar_paginacion(datos,pagina);
            }, path, parameter, function() {}, false);
        }
        // FIN - GESTION DE PROYECTO

    // INICIO - ACTAS
    self.list_actas = function(id_contrato) {

            lista = self.tipoV.actaSuspension();
            lista = lista + ',' + self.tipoV.actaReinicio();
            lista = lista + ',' + self.tipoV.prorroga();
            lista = lista + ',' + self.tipoV.actaInicio();

            parameter = { id_contrato: id_contrato, id_tipo: lista };

            path = path_principal + '/api/Vigencia_contrato/?format=json&sin_paginacion';
            RequestGet(function(data, success, mensage) {

                if (success == 'ok' && data != null && data.length > 0) {
                    self.mensaje_actas('');
                    self.lista_actas(agregarOpcionesObservable(data));
                } else {
                    self.lista_actas([]);
                    self.mensaje_actas(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
            }, path, parameter, function() {}, false);
        }
        // FIN - ACTAS

    // INICIO - POLIZA
    self.list_poliza = function(id_contrato) {
            if (id_contrato > 0) {

                path = path_principal + '/api/Poliza/?format=json';
                parameter = { contrato_id: id_contrato };
                RequestGet(function(datos, estado, mensage) {

                    if (estado == 'ok' && datos.data != null && datos.data.length > 0) {

                        self.mensaje_poliza('');
                        self.lista_poliza(agregarOpcionesObservable(datos.data));

                    } else {
                        self.lista_poliza([]);
                        self.mensaje_poliza(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                    }

                    //self.llenar_paginacion(datos,pagina);
                }, path, parameter, function() {}, false);
            }
        }
        // FIN - POLIZA

    self.ver_soporte = function(obj) {
      window.open(path_principal+"/contrato/ver-soporte/?id="+ obj.id, "_blank");
    }

    self.ver_soporte_acta = function(obj) {
      window.open(path_principal+"/contrato/ver-soporte-acta-compra/?id="+ obj.id, "_blank");
    }  
}

var contratoVigencia = new ContratoVigenciaViewModel();
ContratoVigenciaViewModel.errores_vigencia = ko.validation.group(contratoVigencia.vigenciaVO);

//contratoVigencia.listaTipo('VigenciaContrato');//iniciamos la primera funcion

var content = document.getElementById('content_wrapper');
var header = document.getElementById('header');
ko.applyBindings(contratoVigencia, content);
ko.applyBindings(contratoVigencia, header);