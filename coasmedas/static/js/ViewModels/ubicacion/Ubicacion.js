function ubicacionViewModel() {

    var self = this;
    self.listado = ko.observableArray([]);
    self.mensaje = ko.observable('');
    self.titulo = ko.observable('');
    self.filtro = ko.observable('');
    self.checkall = ko.observable(false);
    self.habilitar_campos = ko.observable(true);
    self.url = path_principal + 'api/ubicacion';
    //Representa un modelo de la tabla persona
    self.ubicacionVO = {
        id: ko.observable(0),
        nombre: ko.observable('').extend({
            required: {
                message: '(*)Digite la ubicación'
            }
        }),
        longitud: ko.observable('').extend({
            required: {
                message: '(*)Digite la longitud'
            }
        }),
        latitud: ko.observable('').extend({
            required: {
                message: '(*)Digite la latitud'
            }
        })
    };


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

    self.abrir_modal = function() {
        self.limpiar();
        self.titulo('Registrar ubicacion');
        self.habilitar_campos(true);
        $('#modal_acciones').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function(data, pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

    //exportar excel

    self.exportar_excel = function() {

        location.href = path_principal + "/ubicacion/export_ubicacion?dato=" + self.filtro();
    }

    // //limpiar el modelo
    self.limpiar = function() {

            self.ubicacionVO.id(0);
            self.ubicacionVO.nombre('');
            self.ubicacionVO.longitud('');
            self.ubicacionVO.latitud('');
        }
        // //funcion guardar
    self.guardar = function() {

            if (ubicacionViewModel.errores_ubicacion().length == 0) { //se activa las validaciones

                // self.contratistaVO.logo($('#archivo')[0].files[0]);

                if (self.ubicacionVO.id() == 0) {

                    var parametros = {
                        callback: function(datos, estado, mensaje) {

                            if (estado == 'ok') {
                                self.filtro("");
                                self.consultar(self.paginacion.pagina_actual());
                                $('#modal_acciones').modal('hide');
                                self.limpiar();
                            }

                        }, //funcion para recibir la respuesta
                        url: path_principal + '/api/ubicacion/', //url api
                        parametros: self.ubicacionVO
                    };
                    //parameter =ko.toJSON(self.contratistaVO);
                    Request(parametros);
                } else {


                    var parametros = {
                        metodo: 'PUT',
                        callback: function(datos, estado, mensaje) {

                            if (estado == 'ok') {
                                self.filtro("");
                                self.consultar(self.paginacion.pagina_actual());
                                $('#modal_acciones').modal('hide');
                                self.limpiar();
                            }

                        }, //funcion para recibir la respuesta
                        url: path_principal + '/api/ubicacion/' + self.ubicacionVO.id() + '/',
                        parametros: self.ubicacionVO
                    };

                    Request(parametros);

                }

            } else {
                ubicacionViewModel.errores_ubicacion.showAllMessages(); //mostramos las validacion
            }
        }
        //funcion consultar de tipo get recibe un parametro
    self.consultar = function(pagina) {
        if (pagina > 0) {
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal + '/api/ubicacion?format=json&page=' + pagina;
            parameter = {
                dato: self.filtro(),
                pagina: pagina
            };
            RequestGet(function(datos, estado, mensage) {

                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results);
                    self.listado(agregarOpcionesObservable(datos.data));

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos, pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
        }


    }

    self.checkall.subscribe(function(value) {

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        });
    });

    self.paginacion.pagina_actual.subscribe(function(pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function(d, e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    self.consultar_por_id = function(obj) {

        // alert(obj.id)
        path = path_principal + '/api/ubicacion/' + obj.id + '/?format=json';
        RequestGet(function(results, count) {

            self.titulo('Actualizar ubicacion');

            self.ubicacionVO.id(results.id);
            self.ubicacionVO.nombre(results.nombre);
            self.habilitar_campos(true);
            self.ubicacionVO.longitud(results.longitud);
            self.ubicacionVO.latitud(results.latitud);
            $('#modal_acciones').modal('show');
        }, path, parameter);

    }


    self.consultar_por_id_detalle = function(obj) {

        // alert(obj.id)
        path = path_principal + '/api/ubicacion/' + obj.id + '/?format=json';
        RequestGet(function(results, count) {

            self.titulo('Actualizar ubicacion');

            self.ubicacionVO.id(results.id);
            self.ubicacionVO.nombre(results.nombre);
            self.ubicacionVO.longitud(results.longitud);
            self.ubicacionVO.latitud(results.latitud);
            self.habilitar_campos(false);
            $('#modal_acciones').modal('show');
        }, path, parameter);

    }



    self.eliminar = function() {

        var lista_id = [];
        var count = 0;
        ko.utils.arrayForEach(self.listado(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un registro.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        } else {
            var path = path_principal + '/ubicacion/eliminar_id_ubicacion/';
            var parameter = {
                lista: lista_id
            };
            RequestAnularOEliminar("Esta seguro que desea eliminar los registros seleccionados?", path, parameter, function() {
                self.consultar(1);
                self.checkall(false);
            })

        }


    }

}

var Ubicacion = new ubicacionViewModel();
ubicacionViewModel.errores_ubicacion = ko.validation.group(Ubicacion.ubicacionVO);
Ubicacion.consultar(1); //iniciamos la primera funcion
var content = document.getElementById('content_wrapper');
var header = document.getElementById('header');
ko.applyBindings(Ubicacion, content);
ko.applyBindings(Ubicacion, header);