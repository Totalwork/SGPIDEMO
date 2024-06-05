function DescargoViewModel() {

    var self = this;
    self.macrocontrato_select = ko.observable(0);
    self.lista_contrato = ko.observableArray([]);
    self.listado_contratista = ko.observableArray([]);
    self.departamento_select = ko.observableArray([]);
    self.listado_municipio = ko.observableArray([]);
    self.lista_maniobra = ko.observableArray([]);
    self.lista_subcontratista = ko.observableArray([]);
    self.lista_trabajo = ko.observableArray([]);
    self.lista_jefe = ko.observableArray([]);
    self.lista_agente = ko.observableArray([]);
    self.lista_jefe2 = ko.observableArray([]);
    self.lista_agente2 = ko.observableArray([]);
    self.proyecto_select = ko.observableArray([]);
    self.listado_contratista_proyecto = ko.observableArray([]);
    self.proyecto_select_filtro = ko.observableArray([]);
    self.nombremaniobra = ko.observable('');
    self.nombretrabajos = ko.observable('');
    self.jefedetrabajo = ko.observable('');
    self.agentedescargo = ko.observable('');
    self.correo_bdi = ko.observable('');
    self.soporte_protocolo = ko.observable('');
    self.soporte_ops = ko.observable('');
    self.lista_chequeo = ko.observable('');
    self.listavigencia = ko.observable('');

    self.contratista = ko.observable(0);
    self.contratistafiltrobusqueda = ko.observable(0);
    self.departamento = ko.observable('');
    self.municipio = ko.observable(0);
    self.proyectoid = ko.observable('');
    self.nombreproyecto = ko.observable('');
    self.repetido = ""
    self.repetido2 = ""

    //self.proyecto=ko.observable('');

    self.subcontratista = ko.observable('');

    self.cambiar_contratista = ko.observable(0);
    self.cambiar_departamento = ko.observable(0);
    self.cambiar_municipio = ko.observable(0);
    self.agenteid = "";
    self.jefeid = ko.observable(0);

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

    self.showRow = ko.observable(false);

    self.habilitar_mcontrato = ko.observable(false);

    self.url = path_principal + 'api/descargo';
    //Representa un modelo de la tabla persona
    self.descargoVO = {
        id: ko.observable(0),
        id_interno: ko.observable(''),
        numero: ko.observable(''),
        // estado_id:ko.observable(12),
        estado_id: ko.observable(37),
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
        contratista_id: ko.observable(0).extend({ required: { message: '(*)Seleccione una opcion' } }),
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
        self.descargoVO.contratista_id(0);
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
        // self.descargoVO.proyecto.isModified(false);
        self.descargoVO.barrio.isModified(false);
        self.descargoVO.direccion.isModified(false);
        self.descargoVO.elemento_intervenir.isModified(false);
        self.descargoVO.area_afectada.isModified(false);
        self.descargoVO.maniobra_id.isModified(false);
        self.descargoVO.fecha.isModified(false);
        self.descargoVO.hora_inicio.isModified(false);
        self.descargoVO.hora_fin.isModified(false);
        self.descargoVO.jefe_trabajo_id.isModified(false);
        self.descargoVO.contratista_id.isModified(false);
        self.descargoVO.agente_descargo_id.isModified(false);


        // check_eliminar(false)         
    }

    self.abrir_proyecto = function () {
        //self.limpiar();
        $('#proyecto').modal('show');
    }

    self.agregar_proyecto = function (valor) {

        self.descargoVO.proyecto_id();
        self.consultar_proyecto(self.proyectoid());
    }

    self.consultar_proyecto = function (proyecto) {
        var id_contrato = 0;
        path = path_principal + '/api/Proyecto/' + proyecto + "/?descargo=1&format=json";
        parameter = {};
        RequestGet(function (results, count) {
            if (proyecto != '') {
                ko.utils.arrayForEach(results.contrato, function (p) {
                    if (p.tipo_contrato.id == 8 && p.contratista.id == self.contratistafiltrobusqueda()) {
                        id_contrato = p.id;
                    }
                });
            }
            // self.proyecto_select_filtro(results.data)

        }, path, parameter, function () {

            self.consultar_vigencia_poliza(id_contrato, function () {

                cerrarLoading();

                if (self.listavigencia() != '') {

                    $.confirm({
                        title: 'Confirmar!',
                        content: "<h4>El contrato numero: " + self.listavigencia() + " tiene una poliza vencida. ¿Desea seguir con el descargo?</h4>",
                        confirmButton: 'Si',
                        confirmButtonClass: 'btn-info',
                        cancelButtonClass: 'btn-danger',
                        cancelButton: 'No',
                        confirm: function () {
                            self.consultar_sub_contratista(id_contrato);
                            $('#proyecto').modal('hide');
                            self.descargoVO.contratista_id(self.descargoVO.contratista_id());
                            // self.consultar_agente(self.contratistafiltrobusqueda());
                            // self.consultar_jefe(self.contratistafiltrobusqueda());
                            self.list_jefe_agente(self.contratistafiltrobusqueda(),1,1);
                            ko.utils.arrayForEach(self.proyecto_select(), function (p) {

                                if (self.proyectoid() == p.id) {
                                    self.descargoVO.proyecto_id(p.id)
                                    self.nombreproyecto(p.nombre);
                                }
                            });
                        }
                    });
                    // RequestAnularOEliminar("El contrato numero: "+self.listavigencia()+" tiene una poliza vencida. ¿Desea seguir con el descargo?", path, parameters, function () {
                    //  })
                } else {
                    self.consultar_sub_contratista(id_contrato);
                    $('#proyecto').modal('hide');
                    self.descargoVO.contratista_id(self.descargoVO.contratista_id());
                    // self.consultar_agente(self.contratistafiltrobusqueda());
                    // self.consultar_jefe(self.contratistafiltrobusqueda());
                    self.list_jefe_agente(self.contratistafiltrobusqueda(),1,1);
                    ko.utils.arrayForEach(self.proyecto_select(), function (p) {

                        if (self.proyectoid() == p.id) {
                            self.descargoVO.proyecto_id(p.id)
                            self.nombreproyecto(p.nombre);
                        }
                    });
                }
            });
        }, false);
    }

    self.consultar_vigencia_poliza = function (contratist, completado) {

        var hoy = new Date()
        var dia = hoy.getDate();
        var mes = hoy.getMonth();
        var anio = hoy.getFullYear();
        var fecha_actual = String(anio + "-" + mes + "-" + dia);

        path = path_principal + '/api/VigenciaPoliza/?&contrato_id=' + contratist + '&fecha=' + fecha_actual;
        parameter = '';
        RequestGet(function (results, count) {

            if (results.data != '') {
                console.log("asas");
                self.listavigencia(results.data[0].poliza.contrato.numero);
            }

        }, path, parameter, completado, false);
    }

    self.consultar_jefe = function (contratist) {

        path = path_principal + '/api/empleado/?sin_paginacion&lite=1&contratista_id=' + contratist;
        parameter = '';
        RequestGet(function (results, count) {

            self.lista_jefe(results);

        }, path, parameter, function () {
            self.descargoVO.jefe_trabajo_id(self.jefeid());
        });
    }

    self.consultar_agente = function (contratist) {

        path = path_principal + '/api/empleado/?sin_paginacion&lite=1&contratista_id=' + contratist;
        parameter = '';
        RequestGet(function (results, count) {

            self.lista_agente(results);

        }, path, parameter, function () {
            self.descargoVO.agente_descargo_id(self.agenteid);
        });
    }

    //consultar los jefeas y agentes de Descargo
    self.list_jefe_agente=function(contratist, jefe, agente){
        parameter={};
        path =path_principal+'/seguridad-social/list_empleados_con_seguridad_social/?id_contratista='+contratist;
        
        RequestGet(function (datos,estado,mensaje) {

            if (estado=='ok' && datos != null && datos.length > 0) {
                
                if(jefe == 1){
                    self.lista_jefe2(datos);
                }
                if(agente == 1){
                    self.lista_agente2(datos);
                }
            }else{
                if(jefe == 1){
                    self.lista_jefe2([]);
                }
                if(agente == 1){
                    self.lista_agente2([]);
                }
            }
            //self.lista_rubro(convertToObservableArray(datos));
        }, path, parameter);
    }

    self.consultar_sub_contratista = function (contratist) {


        path = path_principal + '/api/Sub_contratista/?sin_paginacion&id_contrato=' + contratist;
        parameter = '';
        RequestGet(function (results, count) {

            self.lista_subcontratista(results);

        }, path, parameter, function () {

            // self.descargoVO.jefe_trabajo_id(self.jefeid())
        });
    }

    //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
    self.subcontratista.subscribe(function (value) {

        if (value > 0) {
            // self.consultar_contratista(value);
            self.list_jefe_agente(value,1,0);
        } else {
            self.list_jefe_agente(self.contratistafiltrobusqueda(),1,0)
        }
    });

    //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
    self.macrocontrato_select.subscribe(function (value) {

        if (value > 0) {
            // self.consultar_contratista(value);
            self.filtros(value, 0, 0, 0);
        } else {
            self.listado_contratista([]);
            self.departamento_select([]);
            self.listado_municipio([]);
            self.proyecto_select([]);
        }
    });

    //funcion que se ejecuta cuando se cambia en el select de descargoVO.contratista_id
    self.contratistafiltrobusqueda.subscribe(function (value) {

        if (value > 0) {
            self.cambiar_contratista(1);
            self.cambiar_departamento(0);
            self.departamento('');
            self.municipio(0);
            self.descargoVO.proyecto_id(0);
            self.showRow(true);
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

    self.contratista.subscribe(function (value) {
        if (value > 0 && self.repetido != value) {
            self.repetido = value
            self.list_jefe_agente(value,0,1);
        }
    });

    //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
    self.departamento.subscribe(function (value) {
        if (value > 0) {
            self.cambiar_departamento(1);
            self.municipio(0);
            self.descargoVO.proyecto_id(0);
            self.filtros(self.macrocontrato_select(), self.contratistafiltrobusqueda(), value, 0);
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
            self.descargoVO.proyecto_id(0);
            self.filtros(self.macrocontrato_select(), self.contratistafiltrobusqueda(), self.departamento(), value);
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

        if (departamento != '') {
            parameter += '&departamento_id=' + departamento;
        }

        if (municipio != 0) {
            parameter += '&municipio_id=' + municipio;
        }
        RequestGet(function (results, count) {

            //self.listado_contratista(results.descargoVO.contratista_id);
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
        }, path, parameter, undefined, true, true);
    }

    //funcion que se ejecuta cuando se cambia en el select de contrato para guardar
        // self.descargoVO.proyecto_id.subscribe(function (value) {

        //     if(value >0){
        //         self.consultar_contratista_proyecto();
        //     }else{
        //         self.listado_contratista_proyecto([]);
        //     }
    // });

    self.consultar_contratista_proyecto = function () {

        //path =path_principal+'/contrato/list_contrato_select/?mcontrato='+value+'&descargoVO.contratista_id=0';
        path = path_principal + '/api/empresa/?sin_paginacion&esContratista=1';
        parameter = '';
        RequestGet(function (results, count) {

            self.listado_contratista_proyecto(results);

        }, path, parameter);
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
            self.descargoVO.contratista_id(self.contratistafiltrobusqueda());

            if (DescargoViewModel.errores_descargo().length == 0) {//se activa las validaciones

                if (self.descargoVO.id() == 0) {

                    var parametros = {
                        metodo: 'POST',
                        alerta: false,
                        callback: function (datos, estado, mensaje) {

                            if (estado == 'ok') {
                                //self.consultar(self.paginacion.pagina_actual());
                                //$('#modal_acciones').modal('hide');
                                $.confirm({
                                    title: 'Confirmar!',
                                    content: "<h4><i class='text-success fa fa-check-circle-o fa-2x'></i> " + mensaje + ".</h4><br><h5>¿Desea copiarlo para crear otro descargo nuevo?</h5>",
                                    confirmButton: 'Si',
                                    confirmButtonClass: 'btn-info',
                                    cancelButtonClass: 'btn-danger',
                                    cancelButton: 'No',
                                    confirm: function () {

                                        // window.location.href = '/descargo/registrarcopia/' + datos.id + '/';
                                        self.descargoVO.jefe_trabajo_id(0);
                                        self.descargoVO.agente_descargo_id(0);
                                    },
                                    cancel: function () {
                                        window.location.href = '/descargo/registroconsulta/';
                                        // alert("Ley");
                                    }
                                });
                                //self.limpiar();
                            } else {
                                mensajeInformativo(mensaje);
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

    self.consultar_por_id = function (id_descargo) {
        var jefe = ""
        var agente = ""
        var agenteid = ""
        var contratista_id = '';
        var contratistadescargo = "";
        // self.consultar_contratista_proyecto();
        //alert(obj.id); return false;
        path = path_principal + '/api/Descargo/' + id_descargo + '/?format=json';
        parameter = {};
        RequestGet(function (datos, estado, mensage) {

            self.descargoVO.id(datos.id);
            self.descargoVO.contratista_id(datos.contratista.id);

            self.descargoVO.id_interno(datos.id_interno);
            self.descargoVO.numero(datos.numero);
            self.contratista(datos.agente_descargo.contratista.id);
            self.descargoVO.estado_id(datos.estado.id);
            self.nombreproyecto(datos.proyecto.nombre);
            self.descargoVO.proyecto_id(datos.proyecto.id);
            self.descargoVO.jefe_trabajo_id(datos.jefe_trabajo.id);
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

            self.jefeid(datos.jefe_trabajo.id);
            self.agenteid = datos.agente_descargo.id;
            // self.descargoVO.jefe_trabajo_id(datos.jefe_trabajo.id);

            ko.utils.arrayForEach(self.lista_subcontratista(), function (p) {
                if (p.empresa.id == datos.jefe_trabajo.contratista.id) {
                    self.subcontratista(datos.jefe_trabajo.contratista.id);
                }
            });

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

            jefe = datos.jefe_trabajo.persona.nombres + ' ' + datos.jefe_trabajo.persona.apellidos

            agente = datos.agente_descargo.persona.nombres + ' ' + datos.agente_descargo.persona.apellidos
            agenteid = datos.agente_descargo.id
            contratista_id = datos.jefe_trabajo.contratista.id;
            contratistadescargo = datos.contratista.id

            // self.habilitar_campos(true);
            // $('#modal_acciones').modal('show');
        }, path, parameter);
    }

    self.consultar_por_id_cc = function (id_descargo) {
        var jefe = ""
        var agente = ""
        var agenteid = ""
        var contratista_id = '';
        var contratistadescargo = "";
        // self.consultar_contratista_proyecto();
        //alert(obj.id); return false;
        path = path_principal + '/api/Descargo/' + id_descargo + '/?format=json';
        parameter = {};
        RequestGet(function (datos, estado, mensage) {

            self.descargoVO.contratista_id(datos.contratista.id);
            self.descargoVO.id_interno(datos.id_interno);
            self.contratista(datos.agente_descargo.contratista.id);
            self.descargoVO.estado_id(datos.estado.id);
            self.nombreproyecto(datos.proyecto.nombre);
            self.descargoVO.proyecto_id(datos.proyecto.id);

            self.descargoVO.jefe_trabajo_id(datos.jefe_trabajo.id);

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

            self.jefeid(datos.jefe_trabajo.id);
            self.agenteid = datos.agente_descargo.id;
            // self.descargoVO.jefe_trabajo_id(datos.jefe_trabajo.id);

            ko.utils.arrayForEach(self.lista_subcontratista(), function (p) {
                if (p.empresa.id == datos.jefe_trabajo.contratista.id) {
                    self.subcontratista(datos.jefe_trabajo.contratista.id);
                }
            });

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

            $('#multiselect2').multiselect('select', ids.split(','), true);

            jefe = datos.jefe_trabajo.persona.nombres + ' ' + datos.jefe_trabajo.persona.apellidos

            agente = datos.agente_descargo.persona.nombres + ' ' + datos.agente_descargo.persona.apellidos
            agenteid = datos.agente_descargo.id
            contratista_id = datos.jefe_trabajo.contratista.id;
            contratistadescargo = datos.contratista.id
            // self.habilitar_campos(true);
            // $('#modal_acciones').modal('show');
        }, path, parameter);
    }
}
var descargo = new DescargoViewModel();
DescargoViewModel.errores_descargo = ko.validation.group(descargo.descargoVO);

//descargo.consultar(1);//iniciamos la primera funcion
//DescargooViewModel.errores_vigencia = ko.validation.group(contrato.vigenciaVO);

/*contrato.empresa('esContratante');
contrato.empresa('esContratista');
contrato.filtrar_macrocontrato();*/

/*var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(descargo,content);
ko.applyBindings(descargo,header);*/
ko.applyBindings(descargo);

jQuery(document).ready(function () {
    $('#multiselect2').multiselect({
        includeSelectAllOption: false,
        nonSelectedText: 'Ninguno seleccionado',
        nSelectedText: 'Seleccionado',
        allSelectedText: 'Todo seleccionado'
    });
});


