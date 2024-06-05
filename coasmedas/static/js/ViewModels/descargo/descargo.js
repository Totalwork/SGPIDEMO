function DescargoViewModel() {

    var self = this;
    self.listado = ko.observableArray([]);
    self.listadofotos = ko.observableArray([]);
    self.listadofotos2 = ko.observableArray([]);
    self.listadofotos3 = ko.observableArray([]);
    self.listadofotos4 = ko.observableArray([]);
    self.listadofotos5 = ko.observableArray([]);
    self.listado_gps = ko.observableArray([]);
    self.listadosinpaginacion = ko.observableArray([]);
    self.macrocontrato_select = ko.observable(0);
    self.macrocontratofiltro = ko.observable(0);
    self.lista_contrato = ko.observableArray([]);
    self.listado_contratista = ko.observableArray([]);
    self.departamento_select = ko.observableArray([]);
    self.listado_municipio = ko.observableArray([]);
    self.lista_maniobra = ko.observableArray([]);
    self.lista_subcontratista = ko.observableArray([]);
    self.lista_trabajo = ko.observableArray([]);
    self.lista_jefe = ko.observableArray([]);
    self.lista_agente = ko.observableArray([]);
    self.proyecto_select = ko.observableArray([]);
    self.proyecto_select_filtro = ko.observableArray([]);
    self.listado_contratista_proyecto = ko.observableArray([]);
    self.habilitar_campos = ko.observable(true);
    self.contratista = ko.observable(0);
    self.contratistafiltro = ko.observable(0);
    self.departamento = ko.observable('');
    self.departamentofiltro = ko.observable(0);
    self.proyectofiltro = ko.observable(0);
    self.municipio = ko.observable(0);
    self.municipiofiltro = ko.observable(0);
    self.estado_cambio = ko.observable(0);
    self.desde = ko.observable('');
    self.hasta = ko.observable('');
    self.bdi = ko.observable('');
    self.perdida = ko.observable('');
    self.proyectoid = ko.observable('');
    self.nombreproyecto = ko.observable('');
    self.nombremaniobra = ko.observable('');
    self.observacion = ko.observable('');
    self.num_registro = ko.observable('');
    //self.proyecto=ko.observable('');
    self.maniobra = ko.observable('');
    self.trabajo = ko.observable('');
    self.jefe = ko.observable('');
    self.agente = ko.observable('');
    self.estado = ko.observable('');
    self.cambio_estado = ko.observable('');
    self.contratista_proyecto = ko.observable('');
    self.mensaje = ko.observable('');
    self.titulo = ko.observable('');
    self.filtro = ko.observable('');
    self.checkall = ko.observable(false);
    self.correo_bdi = ko.observable('');
    self.soporte_protocolo = ko.observable('');
    self.soporte_ops = ko.observable('');
    self.lista_chequeo = ko.observable('');
    self.regla = ko.observable('');
    self.rutafoto = ko.observable('');
    self.nombretrabajos = ko.observable('');
    self.jefedetrabajo = ko.observable('');
    self.agentedescargo = ko.observable('');
    self.subcontratista = ko.observable('');
    self.guardaractivo = ko.observable(false);

    self.id_interno_vermas = ko.observable('');
    self.no_descargo_vermas = ko.observable('');
    self.estado_vermas = ko.observable('');
    self.fecha_fin_vermas = ko.observable('');
    self.hora_inicio_vermas = ko.observable('');
    self.hora_fin_vermas = ko.observable('');
    self.contrato_vermas = ko.observable('');
    self.maniobra_vermas = ko.observable('');
    self.trabajo_vermas = ko.observable('');
    self.soporteops_vermas = ko.observable('');
    self.soporteprotocolo_vermas = ko.observable('');
    self.proyecto_vermas = ko.observable('');
    self.cambiar_contratista = ko.observable(0);
    self.cambiar_departamento = ko.observable(0);
    self.cambiar_municipio = ko.observable(0);
    self.descargo_id = ko.observable(0);

    self.estadoD = {
        solicitado: ko.observable(12),
        rechazado: ko.observable(11),
        finalizado: ko.observable(10),
        aprobado: ko.observable(9),
        aplazado_previamente: ko.observable(8),
        aplazado: ko.observable(7),
        activado: ko.observable(6),
        revisado: ko.observable(5),
        anulado: ko.observable(3)
    }

    // DEFINIR FECHA INICIO DEL FILTRO
    var date = new Date();

    // date.setMonth(date.getMonth() + 1);
    self.desde(date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + (date.getDate()));

    self.showRow = ko.observable(false);

    self.mostrarSGI = ko.observable(false);

    self.mostrarobservacionsgi = ko.observable(false);

    self.mostrarobservacioninterventor = ko.observable(false);

    self.showBusqueda = ko.observable(false);

    self.habilitar_mcontrato = ko.observable(false);

    self.url = path_principal + 'api/descargo';
    //Representa un modelo de la tabla persona
    self.descargoVO = {
        id: ko.observable(0),
        id_interno: ko.observable(''),
        numero: ko.observable(''),
        estado_id: ko.observable(12),
        // estado_id:ko.observable(37),
        proyecto_id: ko.observable(''),
        barrio: ko.observable('').extend({ required: { message: '(*)Digite el número del contrato' } }),
        direccion: ko.observable(''),
        bdi: ko.observable(false),
        perdida_mercado: ko.observable(false),
        area_afectada: ko.observable('').extend({ required: { message: '(*)Digite el contratante ' } }),
        elemento_intervenir: ko.observable('NA'),
        maniobra_id: ko.observable('').extend({ required: { message: '(*)Seleccione una opcion' } }),
        trabajo_id: ko.observableArray(''),//.extend({ required: { message: '(*)Seleccione una opcion' } }),
        fecha: ko.observable('').extend({ required: { message: '(*)Ingrese una fecha' } }),
        hora_inicio: ko.observable('').extend({ required: { message: '(*)Ingrese hora de inicio' } }),
        hora_fin: ko.observable('').extend({ required: { message: '(*)Ingrese hora final' } }),
        jefe_trabajo_id: ko.observable('').extend({ required: { message: '(*)Seleccione una opcion' } }),
        contratista_id: ko.observable('').extend({ required: { message: '(*)Seleccione una opcion' } }),
        agente_descargo_id: ko.observable('').extend({ required: { message: '(*)Seleccione una opcion' } }),
        correo_bdi: ko.observable(''),
        soporte_protocolo: ko.observable(''),
        soporte_ops: ko.observable(''),
        lista_chequeo: ko.observable(''),
        numero_requerimiento: ko.observable(''),
        departamento_proyecto: ko.observable(''),
        motivo_sgi: ko.observable(''),
        motivo_interventor: ko.observable(''),
        observacion: ko.observable(''),
        convenio_proyecto: ko.observable(''),
        observacion_interventor: ko.observable('')
    };

    self.limpiar = function () {
        self.macrocontrato_select(0);
        self.contratista(0);
        self.descargoVO.id(0);
        self.descargoVO.id_interno('');
        self.descargoVO.numero('');
        self.descargoVO.proyecto_id('');
        self.descargoVO.barrio('');
        self.descargoVO.direccion('');
        self.descargoVO.bdi(0);
        self.descargoVO.perdida_mercado(0);
        self.descargoVO.trabajo_id('');
        self.descargoVO.area_afectada('');
        self.descargoVO.elemento_intervenir('NA');
        self.descargoVO.maniobra_id('');
        self.descargoVO.fecha('');
        self.descargoVO.hora_inicio('');
        self.descargoVO.hora_fin('');
        self.descargoVO.jefe_trabajo_id(0);
        self.descargoVO.contratista_id('');
        self.descargoVO.agente_descargo_id(0);
        self.descargoVO.soporte_protocolo('');
        self.descargoVO.soporte_ops('');
        self.descargoVO.lista_chequeo('');
        self.descargoVO.motivo_sgi('');
        self.descargoVO.motivo_interventor('');
        self.descargoVO.observacion('');
        self.descargoVO.convenio_proyecto('');
        self.descargoVO.departamento_proyecto('');
        self.nombreproyecto('');
        $('#archivo').fileinput('reset');
        $('#archivo').val('');
        $('#archivo2').fileinput('reset');
        $('#archivo2').val('');
        self.showRow(false);
        $('#multiselect2').multiselect('clearSelection');
        // check_eliminar(false)         
    }

    self.limpiarfoto = function () {
        self.fotodescargoVO.regla('');
        self.fotodescargoVO.ruta();
        $('#archivo3').fileinput('reset');
        $('#archivo3').val('');
        // check_eliminar(false)         
    }

    self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(5),
        directiones: ko.observable(true),
        limite: ko.observable(true),
        cantidad_por_paginas: ko.observable(0),
        totalRegistrosBuscados: ko.observable(0),
        text: {
            first: ko.observable('Inicio'),
            last: ko.observable('Fin'),
            back: ko.observable('<'),
            forward: ko.observable('>')
        }
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data, pagina) {
        var buscados = (resultadosPorPagina) > data.count ? data.count : (resultadosPorPagina);
        self.paginacion.totalRegistrosBuscados(buscados);
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }

    self.abrir_modal = function () {
        //self.limpiar();
        location.href = path_principal + "/descargo/registrar";
    }

    self.abrir_proyecto = function () {
        //self.limpiar();
        self.titulo('Buscar proyecto');
        $('#proyecto').modal('show');
    }

    self.abrir_filtro = function () {
        self.filtros(0, 0, 0, 0);
        self.titulo('filtrar descargo');
        $('#modal_filtro_descargo').modal('show');
    }

    self.abrir_cambio = function () {
        //self.limpiar();
        self.titulo('Cambio de estado');
        $('#modal_cambio_estado').modal('show');
    }

    //funcion para ver mas detalle del encabezado 
    self.ver_mas_detalle = function (obj) {
        self.titulo('Detalle del descargo');
        self.ver_mas_descargo(obj);
        $('#vermas_descargo').modal('show');

    }

    self.mostrarmotivosgi = function () {
        setTimeout(function () {
            if (ver_div) {
                self.mostrarSGI(ver_div);
            } else {
                self.mostrarSGI(ver_div);
            }
        }, 500)

    }

    self.agregar_proyecto = function (valor) {

        ko.utils.arrayForEach(self.proyecto_select(), function (p) {

            if (self.proyectoid() == p.id) {
                self.descargoVO.proyecto_id(p.id)
                self.nombreproyecto(p.nombre);
            }

        });
        self.descargoVO.proyecto_id()
        self.titulo('Registrar descargo');
        $('#proyecto').modal('hide');
        self.consultar_agente(self.contratista());
        self.consultar_jefe(self.contratista());
        self.consultar_proyecto(self.proyectoid());

        // self.showBusqueda(!valor);
        // if(self.showBusqueda()==false){
        //     self.departamento_select([]);
        //     self.listado_municipio([]);
        //     self.proyecto_select([]);
        // }
    }

    self.consultar_jefe = function (contratist) {

        path = path_principal + '/api/empleado/?sin_paginacion&contratista_id=' + contratist;
        parameter = '';
        RequestGet(function (results, count) {

            self.lista_jefe(results);

        }, path, parameter);
        $('#loading').hide();
    }

    self.consultar_agente = function (contratist) {

        path = path_principal + '/api/empleado/?sin_paginacion&contratista_id=' + contratist;
        parameter = '';
        RequestGet(function (results, count) {

            self.lista_agente(results);

        }, path, parameter);
        $('#loading').hide();
    }

    self.consultar_maniobra = function () {

        path = path_principal + '/api/Maniobra/?ignorePagination';
        parameter = '';
        RequestGet(function (results, count) {

            self.lista_maniobra(results);

        }, path, parameter);
    }

    self.consultar_proyecto = function (proyecto) {
        var id_contrato = 0;
        path = path_principal + '/api/Proyecto/' + proyecto;
        parameter = '';
        RequestGet(function (results, count) {
            if (proyecto != '') {
                ko.utils.arrayForEach(results.contrato, function (p) {
                    if (p.tipo_contrato.id == 1 && p.contratista.id == self.contratista()) {
                        id_contrato = p.id;
                    }

                });
            }
            self.proyecto_select_filtro(results.data)

        }, path, parameter, function () {
            self.consultar_sub_contratista(id_contrato);
        });
        $('#loading').hide();
    }

    self.consultar_sub_contratista = function (contratist) {

        path = path_principal + '/api/Sub_contratista/?sin_paginacion&id_contrato=' + contratist;
        parameter = '';
        RequestGet(function (results, count) {

            self.lista_subcontratista(results);

        }, path, parameter);
        $('#loading').hide();
    }

    self.consultar_trabajo = function () {

        path = path_principal + '/api/DescargoTrabajo/?ignorePagination';
        parameter = '';
        RequestGet(function (results, count) {

            self.lista_trabajo(results);

        }, path, parameter);
    }

    //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
    self.estado_cambio.subscribe(function (value) {

        if (value == 40) {

            self.mostrarSGI(true);
            self.mostrarinterventor(true);

        } else if (value == 44) {

            self.mostrarinterventor(true);
            self.mostrarSGI(true);
        } else {
            self.mostrarSGI(false);
            self.mostrarinterventor(false);
        }
    });

    //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
    self.macrocontrato_select.subscribe(function (value) {

        if (value > 0) {

            // self.consultar_contratista(value);
            self.filtros(value, self.contratista(), self.departamento(), self.municipio());
        } else {
            self.contratista(0);
            self.departamento('');
            self.municipio(0);
            self.proyectoid(0);
            self.filtros(0, 0, '', 0);
        }
    });

    //funcion que se ejecuta cuando se cambia en el select de contratista
    self.contratista.subscribe(function (value) {

        if (value > 0) {
            self.cambiar_contratista(1);
            self.cambiar_departamento(0);
            self.cambiar_municipio(0);
            self.filtros(self.macrocontrato_select(), value, 0, 0);
            // self.proyecto_combo(self.macrocontrato_select(),value,self.departamento(),self.municipio());

        } else {
            self.cambiar_contratista(0);
            self.showRow(false);
            self.departamento_select([]);
            self.listado_municipio([]);
            self.proyecto_select([]);
        }
    });

    self.descargoVO.contratista_id.subscribe(function (value) {
        if (value > 0) {
            self.consultar_agente(value);
        }
    });

    //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
    self.departamento.subscribe(function (value) {
        if (value > 0) {
            self.cambiar_departamento(1);
            self.cambiar_municipio(0);
            self.filtros(self.macrocontrato_select(), self.contratista(), value, 0);
        } else {
            self.cambiar_departamento(0);
            self.listado_municipio([]);
            self.proyecto_select([]);
        }
    });

    //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
    self.municipio.subscribe(function (value) {
        if (value > 0) {
            self.cambiar_municipio(1);
            self.filtros(self.macrocontrato_select(), self.contratista(), self.departamento(), value);
        } else {
            self.cambiar_municipio(0);
            self.proyecto_select([]);
        }
    });

    self.filtros = function (contrato, contratista, departamento, municipio) {

        path = path_principal + '/api/Proyecto/?filtros=1';
        parameter = '';

        if (contrato != 0) {
            parameter += 'contrato_id=' + contrato;
        }
        if (contratista != 0) {
            parameter += '&id_contratista=' + contratista;
        }
        if (departamento != '' || departamento != 0) {
            parameter += '&departamento_id=' + departamento;
        }
        if (municipio != 0) {
            parameter += '&municipio_id=' + municipio;
        }
        RequestGet(function (results, count) {

            if (self.cambiar_contratista() == 0) {
                self.listado_contratista(results.data.contratistas);
                // console.log("contra"+self.cambiar_contratista());
            }
            if (self.cambiar_departamento() == 0) {
                self.departamento_select(results.data.departamentos);
                // alert("as");
            }

            if (self.cambiar_municipio() == 0) {
                self.listado_municipio(results.data.municipios);
                // alert("as");
            }
            self.proyecto_select(results.data.proyectos);
        }, path, parameter, function () {
            // if (municipio==0 && departamento==0 && contratista==0 && contrato==0) {
            // descargo.contratista(sessionStorage.getItem("desg_desg_contratista"));
            //     descargo.municipio(sessionStorage.getItem("desg_desg_municipio"));
            //     descargo.departamento(sessionStorage.getItem("desg_desg_departamento"));
            //     descargo.proyectoid(sessionStorage.getItem("desg_desg_proyectoid"));
            // }
        }, false, false);
    }

    //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
    self.descargoVO.proyecto_id.subscribe(function (value) {

        if (value > 0) {
            self.consultar_contratista_proyecto();
        } else {
            self.listado_contratista_proyecto([]);
        }
    });

    self.consultar_contratista_proyecto = function () {

        //path =path_principal+'/contrato/list_contrato_select/?mcontrato='+value+'&contratista=0';
        path = path_principal + '/api/empresa/?sin_paginacion&esContratista=1';
        parameter = '';
        RequestGet(function (results, count) {

            self.listado_contratista_proyecto(results);

        }, path, parameter);
        $('#loading').hide();

    }

    self.consultar_puntos_gps = function () {

        //path =path_principal+'/contrato/list_contrato_select/?mcontrato='+value+'&contratista=0';
        path = path_principal + '/api/Puntos_gps/?sin_paginacion';
        parameter = {
            mcontrato: self.macrocontrato_select(),
            departamento: self.departamento(),
            municipio: self.municipio()
        }
        RequestGet(function (results, count) {

            self.listado_gps(results);

        }, path, parameter, function () {
            initialize();
        });
        $('#loading').hide();

    }

    //trae los datos para la opcion ver mas del encabezado del giro
    self.ver_mas_descargo = function (obj) {

        //path =path_principal+'/api/Encabezado_giro/?encabezado_id='+obj.id+'&sin_paginacion&format=json';
        path = path_principal + '/api/Descargo/' + obj.id();
        parameter = {};
        RequestGet(function (datos, estado, mensaje) {

            self.descargo_id(datos.id);
            self.id_interno_vermas(datos.id_interno);
            self.no_descargo_vermas(datos.numero);
            self.estado_vermas(datos.estado.nombre);
            self.fecha_fin_vermas(datos.fecha);
            self.contrato_vermas(datos.proyecto.mcontrato.nombre);
            self.maniobra_vermas(datos.maniobra.nombre);
            self.hora_inicio_vermas(datos.hora_inicio);
            self.hora_fin_vermas(datos.hora_fin);
            self.proyecto_vermas(datos.proyecto.nombre);

            var nombretrabajo = '';
            ko.utils.arrayForEach(datos.trabajo, function (p) {
                nombretrabajo += p.nombre + ',';
            });

            self.trabajo_vermas(nombretrabajo.substr(0, nombretrabajo.length - 1));

            self.soporteops_vermas(datos.soporte_ops);
            self.soporteprotocolo_vermas(datos.soporte_protocolo);
            //self.maniobra_vermas(datos.maniobra.nombre);
            $('#loading').hide();

        }, path, parameter);
        $('#loading').hide();
    }

    // // //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
    // self.descargoVO.agente_descargo_id.subscribe(function (value) {

    //     if(value >0){
    //         self.consultarsinpaginacion(value,self.descargoVO.fecha(),self.descargoVO.hora_inicio(),self.descargoVO.hora_fin());
    //     }
    // });

    // //funcion consultar sin paginacion
    self.consultarsinpaginacion = function (agente, fecha, hora_inicio, hora_fin) {

        //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
        path = path_principal + '/api/Descargo/?format=json&dato=' + fecha + '&agente=' + agente + '&hora_inicio=' + hora_inicio + '&hora_fin=' + hora_fin + '&ignorePagination';
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos != null && datos.length > 0) {
                self.listadosinpaginacion(datos);
                self.guardaractivo(true);

                //$('#modal_filtro_giro').modal('hide'); 
                //self.listadosinpaginacion(agregarOpcionesObservable(datos));  
            } else {
                self.listadosinpaginacion([]);
                self.guardaractivo(false)
            }
        }, path);
        $('#loading').hide();
    }

    // //funcion consultar sin paginacion
    self.consultarjefedescargo = function (jefe_trabajo, fecha, hora_inicio, hora_fin) {

        //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
        path = path_principal + '/api/Descargo/?format=json&dato=' + fecha + '&jefe_trabajo=' + jefe_trabajo + '&hora_inicio=' + hora_inicio + '&hora_fin=' + hora_fin + '&ignorePagination';
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos != null && datos.length > 0) {

                self.listadosinpaginacion(datos);
                self.guardaractivo(true);
            } else {
                self.listadosinpaginacion([]);
                self.guardaractivo(false)
            }
        }, path);
        $('#loading').hide();
    }

    // funcion guardar
    self.guardar = function () {

        if (Date.parse(self.descargoVO.hora_inicio()) > Date.parse(self.descargoVO.hora_fin())) {

            $.confirm({
                title: 'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>La hora inicial no puede ser mayor a la hora final.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        } else {
            if (DescargoViewModel.errores_descargo().length == 0) {//se activa las validaciones

                if (self.descargoVO.id() == 0) {
                    var parametros = {
                        metodo: 'POST',
                        callback: function (datos, estado, mensaje) {

                            if (estado == 'ok') {
                                self.filtro("");
                                //self.consultar(self.paginacion.pagina_actual());
                                //$('#modal_acciones').modal('hide');
                                self.limpiar();
                            }

                        },//funcion para recibir la respuesta 
                        url: path_principal + '/api/Descargo/',//url api
                        parametros: self.descargoVO
                    };
                    RequestFormData(parametros);
                } else {
                    var parametros = {
                        metodo: 'PUT',
                        callback: function (datos, estado, mensaje) {

                            if (estado == 'ok') {
                                self.filtro("");
                                //self.consultar(self.paginacion.pagina_actual());
                                //$('#modal_acciones').modal('hide');
                                //self.limpiar();
                            }
                        },//funcion para recibir la respuesta 
                        url: path_principal + '/api/Descargo/' + self.descargoVO.id() + '/',
                        parametros: self.descargoVO
                    };
                    RequestFormData(parametros);
                }
            } else {
                if (DescargoViewModel.errores_descargo().length > 0) {
                    DescargoViewModel.errores_descargo.showAllMessages();
                }
            }
        }
    }

    //guardar la fecha del radicado o numero de radicado en el tan no radicado
    self.guardar_no_descargo = function (obj) {

        if (obj.numero() == '') {

            $.confirm({
                title: 'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe ingresar un numero de descargo.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        } else {
            var parametros = {
                callback: function (datos, estado, mensaje) {

                    if (estado == 'ok' || estado == 'warning') {
                        // self.filtro("");
                        self.consultar(self.paginacion.pagina_actual());
                        //mensajeExitoso(estado);
                        // self.limpiar();
                    }
                },//funcion para recibir la respuesta 
                url: path_principal + '/descargo/actualizarnodescargo/',//url api
                parametros: { id: obj.id(), numero: obj.numero() }
            };
            //parameter =ko.toJSON(self.contratistaVO);
            Request(parametros);
        }
    }

    self.fotodescargoVO = {
        id: ko.observable(0),
        regla: ko.observable('').extend({ required: { message: '(*)Seleccione una opcion' } }),
        ruta: ko.observable('').extend({ required: { message: '(*)Seleccione una opcion' } }),
        descargo_id: ko.observable(self.descargoVO.id())
    };

    //guardar la fecha del radicado o numero de radicado en el tan no radicado
    self.guardarfoto = function () {

        var parametros = {
            callback: function (datos, estado, mensaje) {

                if (estado == 'ok') {
                    self.filtro("");
                    self.consultarfotoregla(self.fotodescargoVO.descargo_id(), 1);
                    self.limpiarfoto();
                    //mensajeExitoso(estado);
                }
            },//funcion para recibir la respuesta 
            url: path_principal + '/api/FotoDescargo/',//url api
            parametros: self.fotodescargoVO
        };
        //parameter =ko.toJSON(self.contratistaVO);
        RequestFormData(parametros);
    }

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {

        //var descargo_id=self.descargoVO.id();
        //alert(self.bdi);

        if (pagina > 0) {
            self.filtro($('#txtBuscar').val());

            sessionStorage.setItem("desg_desg_filtro", self.filtro() || '');
            sessionStorage.setItem("desg_desg_macrocontrato_select", self.macrocontrato_select() || 0);
            sessionStorage.setItem("desg_desg_contratista", self.contratista() || 0);
            sessionStorage.setItem("desg_desg_municipio", self.municipio() || 0);
            sessionStorage.setItem("desg_desg_departamento", self.departamento() || 0);
            sessionStorage.setItem("desg_desg_proyectoid", self.proyectoid() || 0);
            sessionStorage.setItem("desg_desg_estado", self.estado() || '');
            sessionStorage.setItem("desg_desg_desde", self.desde() || '');
            sessionStorage.setItem("desg_desg_hasta", self.hasta() || '');
            sessionStorage.setItem("desg_desg_bdi", self.bdi() || '');
            sessionStorage.setItem("desg_desg_perdida", self.perdida() || '');

            path = path_principal + '/api/Descargo/?format=json&page=' + pagina;
            parameter = {
                dato: self.filtro(),
                agente: self.descargoVO.agente_descargo_id(),
                // mcontrato: self.macrocontratofiltro,
                mcontrato: self.macrocontrato_select,
                contratista: self.contratista,
                municipio: self.municipio,
                departamento: self.departamento,
                proyecto: self.proyectoid,
                estado: self.estado,
                fechadesde: self.desde,
                fechahasta: self.hasta,
                bdi: self.bdi,
                perdida: self.perdida,
                pagina: pagina,
                lite: 1
            };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    $('#modal_filtro_descargo').modal('hide');
                    self.listado(agregarOpcionesObservable(convertToObservableArray(datos.data)));
                    self.num_registro("- N° de Registos: " + datos.count);
                    // $('#loading').hide();

                } else {
                    self.num_registro("");
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    // $('#loading').hide();
                }
                $('#loading').hide();

                self.llenar_paginacion(datos, pagina);

            }, path, parameter, function () { cerrarLoading(); }, false);
        }
    }

    self.consultarfotoregla = function (descargo, pagina) {

        if (pagina > 0) {

            path = path_principal + '/api/FotoDescargo/?format=json&page=' + pagina;
            parameter = {
                descargo: descargo,
                pagina: pagina
            };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    //$('#modal_filtro_giro').modal('hide'); 
                    self.listadofotos(agregarOpcionesObservable(convertToObservableArray(datos.data)));
                } else {
                    self.listadofotos([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
                self.llenar_paginacion(datos, pagina);

            }, path, parameter);
            $('#loading').hide();
        }
    }

    self.consultar_por_id = function (id_descargo) {
        self.consultar_contratista_proyecto();
        //alert(obj.id); return false;
        path = path_principal + '/api/Descargo/' + id_descargo + '/?format=json';
        parameter = {};
        RequestGet(function (datos, estado, mensage) {

            self.titulo('Actualizar Contrato');
            self.descargoVO.id(datos.id);
            self.descargoVO.contratista_id(datos.contratista.id);
            self.consultar_jefe(datos.jefe_trabajo.contratista.id);
            self.descargoVO.id_interno(datos.id_interno);
            self.descargoVO.numero(datos.numero);
            self.descargoVO.estado_id(datos.estado.id);
            self.nombreproyecto(datos.proyecto.nombre);
            self.descargoVO.proyecto_id(datos.proyecto.id);
            self.descargoVO.barrio(datos.barrio);
            self.descargoVO.bdi(datos.bdi);
            self.descargoVO.perdida_mercado(datos.perdida_mercado);
            self.descargoVO.area_afectada(datos.area_afectada);
            self.descargoVO.elemento_intervenir(datos.elemento_intervenir);
            self.descargoVO.maniobra_id(datos.maniobra.id);
            self.nombremaniobra(datos.maniobra.nombre);
            self.descargoVO.fecha(datos.fecha);
            self.descargoVO.hora_inicio(datos.hora_inicio);
            self.descargoVO.hora_fin(datos.hora_fin);
            var ids = '';
            var nombredetrabajos = '';
            ko.utils.arrayForEach(datos.trabajo, function (p) {
                ids += p.id + ',';
                nombredetrabajos += p.nombre + ',';
            });
            var idcadena = ids.substring(0, ids.length - 1);
            var nombredelostrabajos = nombredetrabajos.substring(0, nombredetrabajos.length - 1)
            self.nombretrabajos(nombredelostrabajos);
            self.descargoVO.trabajo_id(idcadena);
            self.descargoVO.direccion(datos.direccion);

            if (datos.correo_bdi == null) {
                self.correo_bdi('Por subir');
                self.descargoVO.correo_bdi('')
            } else {
                self.correo_bdi('Con soporte');
                self.descargoVO.correo_bdi(datos.correo_bdi);
            }

            if (datos.soporte_ops == null) {
                self.soporte_ops('Por subir');
                self.descargoVO.soporte_ops('');
            } else {
                self.soporte_ops('Con soporte');
                self.descargoVO.soporte_ops(datos.soporte_ops);
            }
            $('#multiselect2').multiselect('select', ids.split(','), true);

            if (datos.soporte_protocolo == null) {
                self.soporte_protocolo('Por subir');
                self.descargoVO.soporte_protocolo('');
            } else {
                self.soporte_protocolo('Con soporte');
                self.descargoVO.soporte_protocolo(datos.soporte_protocolo);
            }
            if (datos.lista_chequeo == null) {
                self.lista_chequeo('Por subir');
                self.descargoVO.lista_chequeo('');
            } else {
                self.lista_chequeo('Con soporte');
                self.descargoVO.lista_chequeo(datos.lista_chequeo);
            }
            self.descargoVO.numero_requerimiento(datos.numero_requerimiento);
            self.descargoVO.motivo_sgi('');
            self.descargoVO.motivo_interventor('');
            self.descargoVO.observacion_interventor(datos.observacion_interventor);
            setTimeout(function () {
                self.descargoVO.jefe_trabajo_id(datos.jefe_trabajo.id);
                self.jefedetrabajo(datos.jefe_trabajo.persona.nombres + ' ' + datos.jefe_trabajo.persona.apellidos);
                self.descargoVO.agente_descargo_id(datos.agente_descargo.id);
                self.agentedescargo(datos.agente_descargo.persona.nombres + ' ' + datos.agente_descargo.persona.apellidos);
            }, 2000);
            //self.habilitar_campos(true);
            //$('#modal_acciones').modal('show');
        }, path, parameter);
    }

    self.checkall.subscribe(function (value) {

        ko.utils.arrayForEach(self.listado(), function (d) {

            d.eliminado(value);
        });
    });

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d, e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    //exportar excel
    self.exportar_excel = function () {
        location.href = path_principal + "/descargo/excel_descargo?dato=" + self.filtro() +
            "&id_estado=" + self.estado() +
            "&mcontrato=" + self.macrocontrato_select() +
            "&departamento=" + self.departamentofiltro() +
            "&contratista=" + self.contratistafiltro() +
            "&municipio=" + self.municipiofiltro() +
            "&fechadesde=" + self.desde() +
            "&fechahasta=" + self.hasta() +
            "&bdi=" + self.bdi() +
            "&perdida=" + self.perdida();
    }

    self.CambiarEstado = function () {

        var lista_id = [];
        var count = 0;
        ko.utils.arrayForEach(self.listado(), function (d) {

            if (d.eliminado() == true) {
                count = 1;
                lista_id.push(d.id)
            }
        });
        if (count == 0) {

            $.confirm({
                title: 'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un descargo para el cambio de estado.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        } else {
            var path = path_principal + '/descargo/actualizarestado/';
            var parameter = {
                lista: lista_id, estado: $('#id_estado').val(),
                motivo_sgi: $('#id_motivo_sgi').val(), motivo_interventor: $('#id_motivo_interventor').val()
            };
            RequestAnularOEliminar("Esta seguro que desea cambiar los estados de los descargos seleccionados?", path, parameter, function () {
                self.consultar(1);
                self.checkall(false);
                $('#modal_cambio_estado').modal('hide');
            })
        }
    }

    self.Cambioestadocompletar = function (caso) {

        if (caso == 1) {
            var parametros = {
                callback: function (datos, estado, mensaje) {

                    if (estado == 'ok') {
                        self.filtro("");
                        self.consultar(self.paginacion.pagina_actual());
                        $('#modal_acciones').modal('hide');
                        //mensajeExitoso(estado);
                    }
                },//funcion para recibir la respuesta 
                url: path_principal + '/descargo/completarestado/',//url api
                parametros: {
                    id: self.descargoVO.id(),
                    estado: self.descargoVO.estado_id(),
                    observacion: self.descargoVO.observacion_interventor(),
                    caso: caso
                }
            };
            //parameter =ko.toJSON(self.contratistaVO);
            Request(parametros);

        } else if (caso == 2) {
            var parametros = {
                callback: function (datos, estado, mensaje) {

                    if (estado == 'ok') {
                        self.filtro("");
                        self.consultar(self.paginacion.pagina_actual());
                        $('#modal_acciones').modal('hide');
                        //mensajeExitoso(estado);
                    }
                },//funcion para recibir la respuesta 
                url: path_principal + '/descargo/completarestado/',//url api
                parametros: {
                    id: self.descargoVO.id(),
                    numero_requerimiento: self.descargoVO.numero_requerimiento(),
                    caso: caso
                }
            };
            //parameter =ko.toJSON(self.contratistaVO);
            Request(parametros);
        } else if (caso == 3) {
            var parametros = {
                callback: function (datos, estado, mensaje) {

                    if (estado == 'ok') {
                        self.filtro("");
                        self.consultar(self.paginacion.pagina_actual());
                        $('#modal_acciones').modal('hide');
                        //mensajeExitoso(estado);
                    }
                },//funcion para recibir la respuesta 
                url: path_principal + '/descargo/completarestado/',//url api
                parametros: {
                    id: self.descargoVO.id(),
                    soporte_protocolo: self.descargoVO.soporte_protocolo(),
                    lista_chequeo: self.descargoVO.lista_chequeo(),
                    caso: caso
                }
            };
            //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData(parametros);
        }
    }

    self.eliminar = function () {

        var lista_id = [];
        var count = 0;
        ko.utils.arrayForEach(self.listado(), function (d) {

            if (d.eliminado() == true) {
                count = 1;
                lista_id.push({
                    id: d.id
                })
            }
        });
        if (count == 0) {

            $.confirm({
                title: 'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un funcionario para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        } else {
            var path = path_principal + '/parametrizacion/eliminar_id_funcionario/';
            var parameter = { lista: lista_id };
            RequestAnularOEliminar("Esta seguro que desea eliminar los funcionarios seleccionados?", path, parameter, function () {
                self.consultar(1);
                self.checkall(false);
            })
        }
    }
}

jQuery(document).ready(function () {
    $('#multiselect2').multiselect({
        includeSelectAllOption: false,
        nonSelectedText: 'Ninguno seleccionado',
        nSelectedText: 'Seleccionado',
        allSelectedText: 'Todo seleccionado'
    });
});

function initialize() {

    var map = new google.maps.Map(document.getElementById('mapa'), {
        zoom: 6,
        center: new google.maps.LatLng(5.684568, -74.295508),
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var infowindow = new google.maps.InfoWindow();
    var marker, i;

    for (i = 0; i < descargo.listado_gps().length; i++) {
        marker = new google.maps.Marker({
            position: new google.maps.LatLng(descargo.listado_gps()[i].latitud, descargo.listado_gps()[i].longitud),
            map: map
        });

        google.maps.event.addListener(marker, 'click', (function (marker, i) {
            return function () {
                infowindow.setContent(descargo.listado_gps()[i].nombre);
                infowindow.open(map, marker);
            }
        })(marker, i));
    }
}
//google.maps.event.addDomListener(window, 'load', initialize);   

var descargo = new DescargoViewModel();
DescargoViewModel.errores_descargo = ko.validation.group(descargo.descargoVO);

$('#txtBuscar').val(sessionStorage.getItem("desg_desg_filtro"));

// alert(sessionStorage.getItem("desg_desg_macrocontrato_select"));
if (sessionStorage.getItem("desg_desg_macrocontrato_select") != null) {
    descargo.macrocontrato_select(sessionStorage.getItem("desg_desg_macrocontrato_select"));
}
// descargo.contratista(sessionStorage.getItem("desg_desg_contratista"));
// descargo.municipio(sessionStorage.getItem("desg_desg_municipio"));
// descargo.departamento(sessionStorage.getItem("desg_desg_departamento"));
// descargo.proyectoid(sessionStorage.getItem("desg_desg_proyectoid"));
if (sessionStorage.getItem("desg_desg_estado") != null) {
    descargo.estado(sessionStorage.getItem("desg_desg_estado"));
}

if (sessionStorage.getItem("desg_desg_desde") != null) {
    descargo.desde(sessionStorage.getItem("desg_desg_desde"));
}

if (sessionStorage.getItem("desg_desg_hasta") != null) {
    descargo.hasta(sessionStorage.getItem("desg_desg_hasta"));
}

if (sessionStorage.getItem("desg_desg_bdi") != null) {
    descargo.bdi(sessionStorage.getItem("desg_desg_bdi"));
}

if (sessionStorage.getItem("desg_desg_perdida") != null) {
    descargo.perdida(sessionStorage.getItem("desg_desg_perdida"));
}

descargo.consultar(1);//iniciamos la primera funcion
// descargo.filtros(0,0,0,0);

ko.applyBindings(descargo);


