function ActivoViewModel() {

    usuarioActual = $("#user").val();
    empresaActual = $("#company").val();

    var self = this;
    self.listado=ko.observableArray([]);
    self.listado_tipo=ko.observableArray([]);
    self.listado_categoria=ko.observableArray([]);
    self.listadocontratos=ko.observableArray([]);
    self.listadoresponsables=ko.observableArray([]);
    self.listadofuncionarios=ko.observableArray([]);
    self.listadomantenimientos=ko.observableArray([]);
    self.listadosoportesmantenimientos=ko.observableArray([]);
    self.listado_activoatributos=ko.observableArray([]);
    self.listadopuntosgps=ko.observableArray([]);    
    self.listadosoportes_atributo=ko.observableArray([]);

    self.titulo=ko.observable('');
    self.titulo_activo=ko.observable('');
    self.titulo_asignarcontrato=ko.observable('');
    self.titulo_asignarresponsable=ko.observable('');
    self.titulo_dar_debaja=ko.observable('');
    self.titulo_punto_gps=ko.observable('');
    self.titulo_soporte_atributo=ko.observable('');

    self.estado_atributos = ko.observable(false);
    self.aux_nombre_atributo = ko.observable('');
    self.aux_activo_atributo_id = ko.observable(0);

    self.url2=path_principal;
    self.url=path_principal+'/api/';
    self.url_funcion=path_principal+'/activos/'; 

    self.mensaje=ko.observable('');
    self.mensaje_activo=ko.observable('');
    self.mensajecontrato=ko.observable('');
    self.mensajeresponsable=ko.observable('');
    self.mensaje_dar_debaja_activo=ko.observable('');
    self.mensajesoportemantenimiento=ko.observable('');
    self.mensajepuntosgps=ko.observable('');
    self.mensaje_activo_atributo=ko.observable('');
    self.mensajesoporte_atributo=ko.observable('');

    self.filtro=ko.observable('');
    self.filtro_responsable=ko.observable('');
    self.filtro_contrato=ko.observable('');
  
    self.categoria=ko.observable(0).extend({ required: { message: ' Seleccione una categoria' } });


    self.filtrado={
        categoria:ko.observable(''),
        tipo:ko.observable(''),
        estado:ko.observable(''),
        funcionario:ko.observable(''),
    };

    self.activoVO={
        id:ko.observable(0),
        tipo_id:ko.observable('').extend({ required: { message: ' Seleccione un tipo' } }),
        identificacion:ko.observable('').extend({ required: { message: ' Digite una identificacion.' } }),
        serial_placa:ko.observable('').extend({ required: { message: 'Digite un numero de serial o placa.' } }),
        descripcion:ko.observable('').extend({ required: { message: ' Digite una descripción' } }),
        contrato_id:ko.observable(0),
        valor_compra:ko.observable(0).money().extend({ required: { message: ' Digite el valor de compra' } }),
        responsable_id:ko.observable(0),
        vida_util_dias:ko.observable('').extend({ required: { message: ' Digite la vida util' } }),
        periodicidad_mantenimiento:ko.observable(0),
        fecha_alta:ko.observable('').extend({ required: { message: ' Ingrese una fecha' } }),

    };



   self.puntosgps={
        listado:ko.observableArray([{
            'nombre':ko.observable(''),
            'longitud':ko.observable(''),
            'latitud':ko.observable(''),
        }]),        
    };


    


    self.atributos={
        listado:ko.observableArray([{      
        'nombre':ko.observable(''),
        'atributo':ko.observable(''),
        'valor':ko.observable(''),
        'estado':ko.observable(false),
        'lista_soportes':ko.observableArray([]),
        }]),        
    };

    self.activoVO_editar={
        id:ko.observable(0),
        tipo_id:ko.observable(0).extend({ required: { message: ' Seleccione un tipo' } }),
        identificacion:ko.observable('').extend({ required: { message: ' Digite una identificacion.' } }),
        serial_placa:ko.observable('').extend({ required: { message: 'Digite un numero de serial o placa.' } }),
        descripcion:ko.observable('').extend({ required: { message: ' Digite una descripción' } }),
        contrato_id:ko.observable(0),
        valor_compra:ko.observable(0).money().extend({ required: { message: ' Digite el valor de compra' } }),
        responsable_id:ko.observable(0),
        vida_util_dias:ko.observable(0).extend({ required: { message: ' Digite la vida util' } }),
        periodicidad_mantenimiento:ko.observable(0),
        fecha_baja:ko.observable('').extend({ required: { message: ' Ingrese una fecha' } }),
        fecha_alta:ko.observable('').extend({ required: { message: ' Ingrese una fecha' } }),
        motivo_debaja:ko.observable(''),
        soportedebaja:ko.observable(''),
        debaja:ko.observable(false),
        debaja_2:ko.observable(''),
    };

    self.puntosgpsVO={
        id:ko.observable(0),
        activo_id:ko.observable(0),
        nombre:ko.observable(''),
        latitud:ko.observable(''),
        longitud:ko.observable(''),
    };

    self.activo_atributoVO={
        id:ko.observable(0),
        activo_atributo_id:ko.observable(0),
        documento:ko.observable('').extend({ required: { message: ' Ingrese un documento' } }),
    };

    self.detalle={
        id:ko.observable(''),
        categoria:ko.observable(''),
        tipo:ko.observable(''),
        identificacion:ko.observable(''),
        serial_placa:ko.observable(''),
        descripcion:ko.observable(''),
        contrato:ko.observable(''),
        contrato_id:ko.observable(''),
        valor_compra:ko.observable(0).money(),
        responsable:ko.observable(''),
        vida_util_dias:ko.observable(''),
        periodicidad_mantenimiento:ko.observable(''),
        fecha_baja:ko.observable(''),
        fecha_alta:ko.observable(''),
        debaja:ko.observable(false),
        debaja_color:ko.observable(''),
        debaja_estado:ko.observable(''),
        motivo_debaja:ko.observable(''),

    };


    self.dar_debaja_activo={
        id:ko.observable(0),
        debaja:ko.observable(true),
        motivo_debaja:ko.observable('').extend({ required: { message: ' Ingrese un motivo' } }),
        soportedebaja:ko.observable('').extend({ required: { message: ' Ingrese un documento' } }),
        fecha_baja:ko.observable(''),
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
        },
        totalRegistrosBuscados:ko.observable(0)
    };

    self.llenar_paginacion = function (data,pagina) {        
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
       // var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
       // self.paginacion.totalRegistrosBuscados(buscados);

    }
    self.paginacion.pagina_actual.subscribe(function (pagina) {    
       self.consultar(pagina);
    });

    self.paginacion_contratos = {
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
    };

    self.llenar_paginacion_contratos = function (data,pagina) {        
        self.paginacion_contratos.pagina_actual(pagina);
        self.paginacion_contratos.total(data.count);       
        self.paginacion_contratos.cantidad_por_paginas(resultadosPorPagina);
       // var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
       // self.paginacion.totalRegistrosBuscados(buscados);

    }


    self.paginacion_contratos.pagina_actual.subscribe(function (pagina) {    
       self.consultar_contratos(pagina);
    });


    self.paginacion_responsables = {
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
    };

    self.llenar_paginacion_responsables = function (data,pagina) {        
        self.paginacion_responsables.pagina_actual(pagina);
        self.paginacion_responsables.total(data.count);       
        self.paginacion_responsables.cantidad_por_paginas(resultadosPorPagina);
       // var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
       // self.paginacion.totalRegistrosBuscados(buscados);

    }


    self.paginacion_responsables.pagina_actual.subscribe(function (pagina) {    
       self.consultar_responsables(pagina);
    });



    self.filtrado.categoria.subscribe(function (val) {       
        self.consultar_tipos(1,val);
    });



    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    self.buscarResponsable=function(d,e){
        if (e.which == 13) {
            self.filtro_responsable($('#txtBuscarResponsable').val());
            self.consultar_responsables(1);
        }
        return true;
    }

    self.get_Responsable = function(){
        self.filtro_responsable($('#txtBuscarResponsable').val());
        self.consultar_responsables(1);
    }


    self.buscarContrato=function(d,e){
        if (e.which == 13) {
            self.filtro_contrato($('#txtBuscarContrato').val());
            self.consultar_contratos(1);
        }
        return true;
    }

    self.get_Contrato = function(){
        self.filtro_contrato($('#txtBuscarContrato').val());
        self.consultar_contratos(1);
    }

    self.setColorIconoFiltro = function (){
        
        var categoria= sessionStorage.getItem("app_activo_categoria")||'';
        var tipo = sessionStorage.getItem("app_activo_tipo")||'';
        var estado = sessionStorage.getItem("app_activo_estado")||'';    
        var funcionario = sessionStorage.getItem("app_activo_funcionario")||'';    

        

        if (categoria != '' || tipo != '' || estado != '' && estado != 2 || funcionario != ''){

            $('#iconoFiltro').addClass("filtrado");
        }else{
            $('#iconoFiltro').removeClass("filtrado");
        }
    }

    self.abrir_modal_busqueda = function() {      
        self.filtrado.categoria(sessionStorage.getItem("app_activo_categoria")); 

        if (sessionStorage.getItem("app_activo_tipo")!='' && sessionStorage.getItem("app_activo_categoria")==''){
            self.filtrado.tipo(sessionStorage.getItem("app_activo_tipo"));
        }

        self.filtrado.estado(sessionStorage.getItem("app_activo_estado"));    
        self.filtrado.funcionario(sessionStorage.getItem("app_activo_funcionario"));
        
        $('#modal_busqueda').modal('show');

    }

    self.consultar = function (pagina){
        sessionStorage.setItem("app_activo_categoria", self.filtrado.categoria() || '');
        sessionStorage.setItem("app_activo_tipo", self.filtrado.tipo() || '');
        sessionStorage.setItem("app_activo_estado", self.filtrado.estado() || '');
        sessionStorage.setItem("app_activo_funcionario", self.filtrado.funcionario() || '');
        

        
        self.cargar(pagina);
    }

    self.cargar = function (pagina) {
        path = self.url+'activosactivo/?format=json';
        if (pagina > 0){
            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("app_activo_dato", self.filtro() || '');

            var categoria= sessionStorage.getItem("app_activo_categoria")||'';
            var tipo = sessionStorage.getItem("app_activo_tipo")||'';
            var estado = sessionStorage.getItem("app_activo_estado")||'';    
            var funcionario = sessionStorage.getItem("app_activo_funcionario")||'';


            parameter = {
                dato: self.filtro(),
                categoria: categoria,
                tipo: tipo,
                estado: estado,
                funcionario: funcionario,
                page: pagina
            };
            RequestGet(function (datos, estado, mensage) {               

                
                if (estado == 'ok' && datos != null && datos.count > 0) {                    
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data));
                }else{                  
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
                $('#modal_busqueda').modal('hide');
                self.llenar_paginacion(datos,pagina);
                self.setColorIconoFiltro();
                cerrarLoading();
            }, path, parameter,undefined,false);
        }else{
            self.mensaje('no se encontro la aplicación y/o el modulo');
        }   
    }

    self.consultar_activo_por_id= function(id){
      
        path =self.url+'activosactivo/'+id+'/?format=json';
        parameter = {};

        RequestGet(function (data, estado, mensage) {  
      
            self.activoVO_editar.id(data.id);
            self.activoVO.id(data.id);
            self.categoria(data.tipo.categoria.id);
            self.activoVO_editar.tipo_id(data.tipo.id);
            sessionStorage.setItem("activo_tipo", data.tipo.id || '');            
            self.activoVO_editar.identificacion(data.identificacion);
            self.activoVO_editar.serial_placa(data.serial_placa);
            self.activoVO_editar.descripcion(data.descripcion);
            self.activoVO_editar.contrato_id(data.contrato.id);
            $("#activo_contrato_numero_editar").val(data.contrato.numero);
            self.activoVO_editar.valor_compra(data.valor_compra);
            self.activoVO_editar.responsable_id(data.responsable.id);            
            $("#activo_responsable_nombre_editar").val(data.responsable.persona.nombres+' '+data.responsable.persona.apellidos);
            self.activoVO_editar.vida_util_dias(data.vida_util_dias);
            self.activoVO_editar.periodicidad_mantenimiento(data.periodicidad_mantenimiento);
            self.activoVO_editar.fecha_alta(data.fecha_alta);
           

            if(data.motivo_debaja){
                self.activoVO_editar.motivo_debaja(data.motivo_debaja);
                self.activoVO_editar.debaja_2(data.debaja);
            }else{
                self.activoVO_editar.motivo_debaja('');
            }

            if(data.soportedebaja){
                self.activoVO_editar.soportedebaja(data.soportedebaja);
                self.activoVO_editar.debaja_2(data.debaja);
            }else{
                self.activoVO_editar.soportedebaja('');
            }

            if(data.fecha_baja){
                self.activoVO_editar.fecha_baja(data.fecha_baja);
                self.activoVO_editar.debaja_2(data.debaja);
            }else{
                self.activoVO_editar.fecha_baja('1900-01-01');
            }


            cerrarLoading();
        },path, parameter,function() {
            
            ;
        });
    }

    self.consultar_activo = function (id) {      
        path =self.url+'activosactivo/'+id+'/?format=json';
        parameter = {};

        RequestGet(function (data, estado, mensage) {
            self.detalle.id(data.id);
            self.detalle.tipo(data.tipo.nombre);
            self.detalle.categoria(data.tipo.categoria.nombre);
            self.detalle.identificacion(data.identificacion);
            self.detalle.serial_placa(data.serial_placa);
            self.detalle.descripcion(data.descripcion);
            self.detalle.contrato(data.contrato.numero);
            self.detalle.contrato_id(data.contrato.id);
            self.detalle.valor_compra(data.valor_compra);
            self.detalle.responsable(data.responsable.persona.nombres+' '+data.responsable.persona.apellidos);
            self.detalle.vida_util_dias(data.vida_util_dias);
            self.detalle.periodicidad_mantenimiento(data.periodicidad_mantenimiento);            
            self.detalle.fecha_alta(data.fecha_alta);

            if (data.debaja){
                self.detalle.debaja(true);
                self.detalle.debaja_color('#FF0000');
                self.detalle.debaja_estado('De baja');
                self.detalle.fecha_baja(data.fecha_baja);
                self.detalle.motivo_debaja(data.motivo_debaja)
      
            }
            else{
                self.detalle.debaja(false);
                self.detalle.debaja_color('#008000');
                self.detalle.debaja_estado('De alta');
                self.detalle.fecha_baja('');
                self.detalle.motivo_debaja('')
  
            }            
            cerrarLoading();
        },path, parameter,function() {
            self.titulo('Información detalle del activo No. '+self.detalle.id());
            self.consultar_hoja_devida(self.detalle.id());
            self.consultar_puntos_gps(self.detalle.id());
            self.consultar_activo_atributo(self.detalle.id());
            $('#detalle_activo').modal('show');
        });
    }




    self.consultar_punto_gps = function(id){
        path =self.url+'activospuntosgps/'+id+'/?format=json';
        parameter = {            
        };

        RequestGet(function (data, estado, mensage) {
            
            self.puntosgpsVO.id(data.id);
            self.puntosgpsVO.nombre(data.nombre);
            self.puntosgpsVO.activo_id(data.activo.id);
            self.puntosgpsVO.latitud(data.latitud);
            self.puntosgpsVO.longitud(data.longitud);
           
            cerrarLoading();
        },path, parameter,function() {             
        });
    }


    self.consultar_activo_atributo = function(id){
        path =self.url+'activosactivo_atributo/?format=json';
        parameter = {
            activo: id,
        };

        RequestGet(function (data, estado, mensage) {
            if (estado=='ok' && data != null && data.count > 0){
                self.mensaje_activo_atributo('');
                self.listado_activoatributos(agregarOpcionesObservable(data.data));
            }else{
                self.listado_activoatributos([]);
                self.mensaje_activo_atributo(mensajeNoFound);
            }
           
        },path, parameter,function() {            
        });
    }
    self.consultar_puntos_gps = function(id){
        path =self.url+'activospuntosgps/?format=json';
        parameter = {
            activo: id,
        };

        RequestGet(function (data, estado, mensage) {
            if (estado=='ok' && data != null && data.count > 0){
                self.mensajepuntosgps('');
                self.listadopuntosgps(agregarOpcionesObservable(data.data));
            }else{
                self.listadopuntosgps([]);
                self.mensajepuntosgps(mensajeNoFound);
            }
            
        },path, parameter,function() {            
        });
    }

    self.consultar_hoja_devida = function(id){
        path =self.url+'activosmantenimiento/?format=json';
        parameter = {
            activo: id,
        };

        RequestGet(function (data, estado, mensage) {
            self.listadomantenimientos(agregarOpcionesObservable(data.data));
        },path, parameter,function() {            
        });
    }

    self.ver_soporte_mantenimiento = function(obj){

      window.open(path_principal+"/activos/ver-soporte-mantenimiento/?id="+ obj.id, "_blank");
    }

    self.ver_soporte_atributo = function(obj){

      window.open(path_principal+"/activos/ver-soporte-atributo/?id="+ obj.id, "_blank");
    }


    self.ver_soporte = function() {
      window.open(path_principal+"/activos/ver-soporte/?id="+ self.detalle.id(), "_blank");
    }

    self.ver_soporte_contrato = function() {
      window.open(path_principal+"/activos/ver-soporte-activos/?id="+ self.detalle.contrato_id(), "_blank");
    }

    self.abrir_soportes_atributos = function(iteraccion_activo_atributo,iteraccion_soporte) {
        var soporte_id = self.atributos.listado()[iteraccion_activo_atributo].lista_soportes()[iteraccion_soporte].soporte_id();
        //alert(soporte_id);       
        window.open(path_principal+"/activos/ver-soporte-atributo/?id="+ soporte_id, "_blank");
    }
    



    self.consultar_soportes_mantenimientos = function(id){
        path =self.url+'activossoporte_mantenimiento/?format=json';
        parameter = {
            mantenimiento: id,
        };

        RequestGet(function (data, estado, mensage) {

            if (estado == 'ok' && data != null && data.count > 0) {
                
                self.mensajesoportemantenimiento('');
                self.listadosoportesmantenimientos(agregarOpcionesObservable(data.data));
                    
            }else{
                  
                self.listadosoportesmantenimientos([]);
                self.mensajesoportemantenimiento(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    
            }

        },path, parameter,function() {            
        });
    }


    self.abrir_modal_soportes_mantenimientos =function (obj){
        self.consultar_soportes_mantenimientos(obj.id);
        $('#MotivoSoporteMantenimiento').text(obj.motivo.nombre);
        $('#ActivoSoporteMantenimiento').text(obj.activo.id);
        $('#modal_soportes_mantenimientos').modal('show');

    }

    self.abrir_nuevo_activo = function(){
        
        self.titulo_activo('Registrar activo');
        //self.consultar_categoria(1);
        self.consultar_tipos(1,undefined);
        self.limpiarActivo();
        $('#nuevo_activo').modal('show');
       
    }
    self.categoria.subscribe(function (val) {
        self.consultar_tipos(1,val);
    });

   

    self.consultar_tipos = function (pagina,categoria_id){
        path = self.url+'activostipo_Activo/?format=json';
        if (pagina > 0){
            parameter = {
                categoria:categoria_id
            };
            RequestGet(function (datos, estado, mensage) {
                
                if (estado == 'ok' && datos != null && datos.count > 0) {                 
                   
                    self.listado_tipo(agregarOpcionesObservable(datos.data));

                     self.listado_tipo.sort(function (a, b) {
                      if (a.nombre > b.nombre) {
                        return 1;
                      }
                      if (a.nombre < b.nombre) {
                        return -1;
                      }
                      // a must be equal to b
                      return 0;
                    });

                    if (self.activoVO_editar.id()!=0){                                       
                        self.activoVO_editar.tipo_id(sessionStorage.getItem("activo_tipo"));
     
                    }else{                              
                        self.activoVO_editar.tipo_id(0);
                        sessionStorage.setItem("activo_tipo", '');
                    }


                    
                    if (sessionStorage.getItem("app_activo_tipo")!=''){
                        self.filtrado.tipo(sessionStorage.getItem("app_activo_tipo"));
                    }
                    

                }else{
                  
                    self.listado_tipo([]);
         
                    
                }
    
                cerrarLoading();
            }, path, parameter,undefined,false);
        }else{
            self.mensaje('no se encontro la aplicación y/o el modulo');
        }
    }

    // self.consultar_categoria = function (pagina){
    //     path = self.url+'activoscategoria/?format=json';
    //     if (pagina > 0){
    //         parameter = {};
    //         RequestGet(function (datos, estado, mensage) {
                
    //             if (estado == 'ok' && datos != null && datos.count > 0) {                
            
    //                 self.listado_categoria(agregarOpcionesObservable(datos.data));

    //                 self.listado_categoria.sort(function (a, b) {
    //                   if (a.nombre > b.nombre) {
    //                     return 1;
    //                   }
    //                   if (a.nombre < b.nombre) {
    //                     return -1;
    //                   }
    //                   // a must be equal to b
    //                   return 0;
    //                 });
                    
    //             }else{                  
    //                 self.listado_categoria([]);                    
    //             }

    //             cerrarLoading();
    //         }, path, parameter,undefined,false);
    //     }else{
    //         self.mensaje('no se encontro la aplicación y/o el modulo');
    //     }
    // }

    self.consultar_responsables = function (pagina){
        path = self.url+'Funcionario/?format=json';
        if (pagina > 0){
            parameter = {
                dato: self.filtro_responsable(),
                page: pagina,
                ignorePagination:1,
            };
            RequestGet(function (datos, estado, mensage) {
           
                if (estado == 'ok' && datos != null) {         
                    
                    self.mensajeresponsable('');
                    self.listadoresponsables(agregarOpcionesObservable(datos));

                    self.listadoresponsables.sort(function (a, b) {
                      if (a.persona.nombres > b.persona.nombre) {
                        return 1;
                      }
                      if (a.persona.nombres < b.persona.nombres) {
                        return -1;
                      }
                      // a must be equal to b
                      return 0;
                    });
                    
                }else{                  
                    self.mensajeresponsable(mensajeNoFound);
                    self.listadoresponsables([]);                    
                }
                self.llenar_paginacion_responsables(datos,pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }else{
            self.mensaje('no se encontro la aplicación y/o el modulo');
        }
    }


    self.consultar_contratos = function (pagina){
        path = self.url+'Contrato/?format=json';
        if (pagina > 0){
            parameter = {
                dato: self.filtro_contrato(),
                parametro_consulta_activos: true,
                id_tipo_codigo:220,
                page: pagina,
            };
            RequestGet(function (datos, estado, mensage) {
                
                if (estado == 'ok' && datos.data != null && datos.count>0) {

                    self.mensajecontrato('');
                    self.listadocontratos(agregarOpcionesObservable(datos.data));
                    
                }else{     
                    self.mensajecontrato(mensajeNoFound);             
                    self.listadocontratos([]);   
                                     
                }
                self.llenar_paginacion_contratos(datos,pagina)
                cerrarLoading();
            }, path, parameter,undefined,false);
        }else{
            self.mensaje('no se encontro la aplicación y/o el modulo');
        }
    }

    

    self.limpiarActivo =function(){
        self.activoVO.id(0);
        self.activoVO.tipo_id(0);
        self.activoVO_editar.tipo_id(0);
        self.activoVO.identificacion('');
        self.activoVO.serial_placa('');
        self.activoVO.descripcion('');
        self.activoVO.contrato_id(0);
        self.activoVO.valor_compra(0);
        self.activoVO.responsable_id(0);
        self.activoVO.vida_util_dias('');
        self.activoVO.periodicidad_mantenimiento('');
        self.activoVO.fecha_alta('');
        self.categoria(0);
        $("#activo_contrato_numero").val('');
        $("#activo_responsable_nombre").val('');



        
        self.activoVO.tipo_id.isModified(false);
        self.activoVO.identificacion.isModified(false);
        self.activoVO.serial_placa.isModified(false);
        self.activoVO.descripcion.isModified(false);
        self.activoVO.contrato_id(false);
        self.activoVO.valor_compra.isModified(false);
        self.activoVO.vida_util_dias.isModified(false);
        self.activoVO.fecha_alta.isModified(false);
        self.categoria.isModified(false);

    }

    self.limpiarPunto = function(){
        self.puntosgpsVO.id(0);
        self.puntosgpsVO.activo_id(0);
        self.puntosgpsVO.nombre('');
        self.puntosgpsVO.latitud('');
        self.puntosgpsVO.longitud('');
    }


    self.limpiarSoporte = function(){
        self.activo_atributoVO.id(0);
        self.activo_atributoVO.activo_atributo_id(0);
        self.activo_atributoVO.documento('');

        self.activo_atributoVO.documento.isModified(false);
        $("#soporte_atributo_documento").fileinput('reset');
        $("#soporte_atributo_documento").val('');
    }

    self.agregar_punto_gps = function(){
        self.limpiarPunto();
        self.titulo_punto_gps('Ingresar punto GPS')
        $("#puntos_gps").modal('show');
    }

    


    self.agregar_gps=function(){
        self.puntosgps.listado.push({
            'nombre':ko.observable(''),
            'longitud':ko.observable(''),
            'latitud':ko.observable(''),
        });
    }

    self.agregar_gps_editar=function(){
        self.puntosgps.listado.push({
            'id':ko.observable(0),
            'nombre':ko.observable(''),
            'longitud':ko.observable(''),
            'latitud':ko.observable(''),
        });
    }


    self.eliminar_gps=function(val){
                      
        self.puntosgps.listado.remove(val);
     
       
    }

    self.eliminar_gps_editar=function(val){

        var obj = self.puntosgps.listado()[val];

        var id_obj = obj.id();
        if(id_obj>0){
            var path =self.url+'activospuntosgps/'+id_obj+'/';
            var parameter = {};
            RequestAnularOEliminar("Esta seguro que desea eliminar el punto GPS?", path, parameter, 
                function(){                 
                    self.puntosgps.listado.remove(obj);
            }); 
        }else{
            self.puntosgps.listado.remove(obj);
        }
        
       
    }



  


    self.guardar=function(){

        var validacion_ingreso = true


        if (ActivoViewModel.errores_activos().length > 0){

            ActivoViewModel.errores_activos.showAllMessages();
            validacion_ingreso = false;
        }


         if(self.activoVO.contrato_id()==0){
            $("#validacionContrato").show();
            validacion_ingreso = false;
        }

        if(self.activoVO.responsable_id()==0){
            $("#validacionResponsable").show();
            validacion_ingreso = false;
        }
            
        if(self.activoVO.valor_compra()==0){
            $("#validacionValor").show();
            validacion_ingreso = false;
        }else{
            $("#validacionValor").hide();
        }


       
        if (validacion_ingreso){

            $("#validacionContrato").hide();
            $("#validacionResponsable").hide();

            sessionStorage.setItem("activoVO_tipo_id", self.activoVO.tipo_id() || ''); 
            sessionStorage.setItem("activoVO_identificacion", self.activoVO.identificacion() || ''); 
            sessionStorage.setItem("activoVO_serial_placa", self.activoVO.serial_placa() || ''); 
            sessionStorage.setItem("activoVO_descripcion", self.activoVO.descripcion() || ''); 
            sessionStorage.setItem("activoVO_contrato_id", self.activoVO.contrato_id() || ''); 
            sessionStorage.setItem("activoVO_valor_compra", self.activoVO.valor_compra() || ''); 
            sessionStorage.setItem("activoVO_responsable_id", self.activoVO.responsable_id() || ''); 
            sessionStorage.setItem("activoVO_vida_util_dias", self.activoVO.vida_util_dias() || ''); 
            sessionStorage.setItem("activoVO_periodicidad_mantenimiento", self.activoVO.periodicidad_mantenimiento() || ''); 
            sessionStorage.setItem("activoVO_fecha_alta", self.activoVO.fecha_alta() || ''); 

            self.cargar_atributos();
            $("#nuevo_atributo").modal('show');
        }else{

            
            
        }

        
        
    }

    self.ver_soportes_atributo=function(id,nombre_atributo){
        self.aux_nombre_atributo(nombre_atributo);
        self.aux_activo_atributo_id(id);        
        self.titulo_soporte_atributo('Soportes del atributo : '+nombre_atributo+' | Activo No.'+self.detalle.id());
        $("#ver_soportes_atributo").modal('show');
        $("#soporte_atributo_documento").val('');
        self.consultar_soportes_atributos(id);
    }


    self.consultar_soportes_atributos =function(id){
        path =self.url+'activosactivo_atributo_soporte/?format=json';
        parameter = {
            activo_atributo: id,
        };

        RequestGet(function (data, estado, mensage) {
            if (estado=='ok' && data != null && data.count > 0){
                self.mensajesoporte_atributo('');
                self.listadosoportes_atributo(agregarOpcionesObservable(data.data));
            }else{
                self.listadosoportes_atributo([]);
                self.mensajesoporte_atributo(mensajeNoFound);
            }
            
        },path, parameter,function() {            
        });
    }

    self.agregar_soporte_atributo = function(val){
        self.atributos.listado()[val].lista_soportes.push({
            'soporte':ko.observable(''),
        })
    }

    self.agregar_soporte_atributo_editar = function(val){
        self.atributos.listado()[val].lista_soportes.push({
            'soporte_id':ko.observable(''),
            'soporte':ko.observable(''),
        })
    }


    self.eliminar_soporte_atributo_ultimo = function(val){     
        var lista = self.atributos.listado()[val];
        var ultimo = lista.lista_soportes().length;
        ultimo = ultimo -1

        if(ultimo>0){

            self.atributos.listado()[val].lista_soportes.remove(
                self.atributos.listado()[val].lista_soportes()[ultimo]
                );
        }else{
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe haber minimo 1 archivo para este atributo.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }

    }


    self.eliminar_soporte_atributo_select = function(val_atributo,val_soporte){    
     
      
        if(val_soporte>0){

            self.atributos.listado()[val_atributo].lista_soportes.remove(
                self.atributos.listado()[val_atributo].lista_soportes()[val_soporte]
                );
        }else{
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe haber minimo 1 archivo para este atributo.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }

    }


    self.eliminar_soporte_atributo_ultimo_editar = function(val){     
        var lista = self.atributos.listado()[val];
        var ultimo = lista.lista_soportes().length;
        ultimo = ultimo -1

        if(self.atributos.listado()[val].lista_soportes()[ultimo].soporte_id()==''){

            self.atributos.listado()[val].lista_soportes.remove(
                self.atributos.listado()[val].lista_soportes()[ultimo]
                );
        }else{
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Por este medio no se puede retirar archivos previamente registrados en este atributo.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }

    }

    self.eliminar_soporte_atributo_editar = function(val_atributo,val_soporte){     
      

        if(self.atributos.listado()[val_atributo].lista_soportes()[val_soporte].soporte_id()==''){

            self.atributos.listado()[val_atributo].lista_soportes.remove(
                self.atributos.listado()[val_atributo].lista_soportes()[val_soporte]
                );
        }else{
            var length = 0;
           
            for (var i = 0; i < self.atributos.listado()[val_atributo].lista_soportes().length; i++) {                
                if(self.atributos.listado()[val_atributo].lista_soportes()[i].soporte_id()>0){
                    length = length + 1;
                }
            }
          
            if(length >1){

                var id_activo_atributo = self.atributos.listado()[val_atributo].lista_soportes()[val_soporte].soporte_id();
                var path =self.url+'activosactivo_atributo_soporte/'+id_activo_atributo+'/';
                var parameter = {};
                RequestAnularOEliminar("Esta seguro que desea eliminar el soporte del atributo?", path, parameter, 
                    function(){
                     self.atributos.listado()[val_atributo].lista_soportes.remove(
                        self.atributos.listado()[val_atributo].lista_soportes()[val_soporte]
                        );
                      
                });

            }else{
                $.confirm({
                    title:'Error',
                    content: '<h4><i class="text-warning fa fa-warning fa-2x"></i>No se puede eliminar el unico archivo cargado a este atributo.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });

            }

            


        }           
            
    }

 
    self.cargar_atributos=function(tipo_id){
        
        path = self.url+'activosatributo/?format=json';
        
            if (tipo_id){
                parameter = {                
                    tipo_id: tipo_id,                
                };  
            }else{
                parameter = {                
                    tipo_id: self.activoVO.tipo_id(),                
                };
            }
            
            RequestGet(function (datos, estado, mensage) {                
                if (estado == 'ok' && datos != null) {  

                    if (tipo_id){
                        self.atributos.listado([]);
                    

                        for (var i = 0; i < datos.count; i++) {
                        

                            self.atributos.listado.push({
                                'id':ko.observable(i),
                                'nombre':ko.observable(datos.data[i].nombre),
                                'atributo':ko.observable(datos.data[i].id),
                                'valor':ko.observable(''),
                                'estado':ko.observable(datos.data[i].requiere_soporte),
                                'lista_soportes':ko.observableArray([{
                                    'soporte':ko.observable(''),
                                    }]),
                
                            });

                            
                        
                        }
                    }else{
                        self.atributos.listado([]);
                    

                        for (var i = 0; i < datos.count; i++) {
                        

                            self.atributos.listado.push({
                                'id_aux':ko.observable(i),
                                'nombre':ko.observable(datos.data[i].nombre),
                                'atributo':ko.observable(datos.data[i].id),
                                'valor':ko.observable(''),
                                'estado':ko.observable(datos.data[i].requiere_soporte),
                                'lista_soportes':ko.observableArray([{
                                    'soporte':ko.observable(''),
                                    }]),
                
                            });

                            
                        
                        }
                    }

                    
                }

                cerrarLoading();
            }, path, parameter,undefined,false);
   
    }



    self.guardar_atributos=function(){
       
        var validacion_ingreso = true;

         for (var i = 0; i < self.atributos.listado().length; i++) {
                    if(self.atributos.listado()[i].valor()!=''){
                        $('#validacionATRIBUTOSvalor'+i).modal('hide');
                       
                    }else{
                         $('#validacionATRIBUTOSvalor'+i).modal('show');
                         validacion_ingreso = false
                    }

                    

        };

  
        for (var i = 0; i < self.atributos.listado().length; i++) {
            var segunda_lista = self.atributos.listado()[i];
            for (var j = 0; j < segunda_lista.lista_soportes().length; j++) {

                if(self.atributos.listado()[i].estado()){
                    if(segunda_lista.lista_soportes()[j].soporte()!=''){
                            $('#validacionATRIBUTOSsoporte'+i+'_'+j).modal('hide');
                           
                    }else{  
                           
                                $('#validacionATRIBUTOSsoporte'+i+'_'+j).modal('show');                            
                                validacion_ingreso = false
                          
                            
                    }
                }

            }
        };

    
        if(validacion_ingreso){
            self.puntosgps.listado([{
                'nombre':ko.observable(''),
                'longitud':ko.observable(''),
                'latitud':ko.observable(''),
            }]);
            $("#nuevo_gps").modal('show');
        }else{
            ActivoViewModel.errores_activos_atributos.showAllMessages();
        }
        
        
    }


    self.guardar_punto_gps = function(id){

         if (ActivoViewModel.errores_puntos_gps().length == 0){
            
            self.puntosgpsVO.activo_id(self.detalle.id());
            if (self.puntosgpsVO.id() == 0){ 
                var parametros={
                        
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {                        
                        
                        self.consultar_activo(self.detalle.id());
                        self.limpiarPunto();
                        // $("#detalle_activo").modal('hide');
                        $("#puntos_gps").modal('hide');
                        $("#nuevo_atributo").modal('hide');
                    }
                    cerrarLoading()
                },//funcion para recibir la respuesta 
                url: self.url+'activospuntosgps/',//url api
                parametros:self.puntosgpsVO                       
                };
                RequestFormData(parametros);
            }else{
                var parametros={
                metodo:'PUT', 
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {                        
                        self.consultar_activo(self.detalle.id());
                        self.limpiarPunto();
                        // $("#detalle_activo").modal('hide');
                        $("#puntos_gps").modal('hide');
                    }
                    cerrarLoading()
                },//funcion para recibir la respuesta 
                url: self.url+'activospuntosgps/'+self.puntosgpsVO.id()+'/?format=json',//url api
                parametros:self.puntosgpsVO                       
                };
                RequestFormData(parametros);
            }
         }else{
            ActivoViewModel.errores_puntos_gps.showAllMessages();
         }
        
    }

    

    self.guardar_activo = function(){
            var validacion_ingreso = true;

            $("#validacionContrato").hide();
            $("#validacionResponsable").hide();

             if(self.activoVO.valor_compra()==0){
                $("#validacionValor").show();return false;
             }
            
            if (self.activoVO.id() == 0){  

             
              
                var data = new FormData();           
                data.append('tipo_id', sessionStorage.getItem("activoVO_tipo_id")); 
                data.append('identificacion', sessionStorage.getItem("activoVO_identificacion")); 
                data.append('serial_placa', sessionStorage.getItem("activoVO_serial_placa")); 
                data.append('descripcion', sessionStorage.getItem("activoVO_descripcion")); 
                data.append('contrato_id', sessionStorage.getItem("activoVO_contrato_id")); 
                data.append('valor_compra', sessionStorage.getItem("activoVO_valor_compra")); 
                data.append('responsable_id', sessionStorage.getItem("activoVO_responsable_id")); 
                data.append('vida_util_dias', sessionStorage.getItem("activoVO_vida_util_dias")); 
                data.append('periodicidad_mantenimiento', sessionStorage.getItem("activoVO_periodicidad_mantenimiento")); 
                data.append('fecha_alta', sessionStorage.getItem("activoVO_fecha_alta")); 
            
                


                for (var i = 0; i < self.puntosgps.listado().length; i++) {
                    // alert(self.puntosgps.listado()[i].nombre());
                    // alert(self.puntosgps.listado()[i].latitud());
                    // alert(self.puntosgps.listado()[i].longitud());

                    var validacion_ingreso_gps = 0;

                        if(self.puntosgps.listado()[i].nombre()!=''){
                            $('#validacionGPSnombre'+i).modal('hide');
                             data.append('nombre[]',self.puntosgps.listado()[i].nombre());
                            
                        }else{
                            $('#validacionGPSnombre'+i).modal('show');
                            validacion_ingreso = false
                            validacion_ingreso_gps = validacion_ingreso_gps + 1
                        }


                        if(self.puntosgps.listado()[i].latitud()!=''){
                            $('#validacionGPSlatitud'+i).modal('hide');
                             data.append('latitud[]',self.puntosgps.listado()[i].latitud());
                            
                        }else{
                             $('#validacionGPSlatitud'+i).modal('show');
                             validacion_ingreso = false
                             validacion_ingreso_gps = validacion_ingreso_gps + 1
                        }


                        if(self.puntosgps.listado()[i].longitud()!=''){
                             $('#validacionGPSlongitud'+i).modal('hide');
                             data.append('longitud[]',self.puntosgps.listado()[i].longitud());
                             
                        }else{
                             $('#validacionGPSlongitud'+i).modal('show');
                             validacion_ingreso = false
                             validacion_ingreso_gps = validacion_ingreso_gps + 1
                        }

                        if ((validacion_ingreso_gps == 3) || (validacion_ingreso_gps == 0)){
                            $('#validacionGPSnombre'+i).modal('hide');
                            $('#validacionGPSlatitud'+i).modal('hide');
                            $('#validacionGPSlongitud'+i).modal('hide');
                            validacion_ingreso = true
                        }else{
                            validacion_ingreso = false
                        }

                    
                    
                }; 
                



                for (var i = 0; i < self.atributos.listado().length; i++) {
                    if(self.atributos.listado()[i].valor()!=''){
                        $('#validacionATRIBUTOSvalor'+i).modal('hide');
                        data.append('atributo[]',self.atributos.listado()[i].atributo());
                        data.append('estado_atributo[]',self.atributos.listado()[i].estado());
                        data.append('valor[]',self.atributos.listado()[i].valor());
                    }else{
                         $('#validacionATRIBUTOSvalor'+i).modal('show');
                         validacion_ingreso = false
                    }
                   

                };

                for (var i = 0; i < self.atributos.listado().length; i++) {
                    var segunda_lista = self.atributos.listado()[i];
                    for (var j = 0; j < segunda_lista.lista_soportes().length; j++) {

                        if(self.atributos.listado()[i].estado()){
                            if(segunda_lista.lista_soportes()[j].soporte()!=''){
                                $('#validacionATRIBUTOSsoporte'+i+'_'+j).modal('hide');
                                    

                                data.append('id_atributo[]',self.atributos.listado()[i].atributo());
                                data.append('soporte_atributo[]',self.atributos.listado()[i].lista_soportes()[j].soporte());
                            }else{
                                if(j==0){
                                    $('#validacionATRIBUTOSsoporte'+i+'_'+j).modal('show');
                                    validacion_ingreso = false
                                }
                                
                            }
                        }
                    }
                }

         
            if (validacion_ingreso){  
                var parametros={
                        
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        //self.consultar_documentos(self.paginacion_tipos.pagina_actual());                        
                        $('#nuevo_activo').modal('hide');
                        $('#nuevo_atributo').modal('hide');
                        $('#nuevo_gps').modal('hide');
                        self.limpiarActivo();
                        self.consultar(1);
                        self.consultar_activo(datos.id);

                    }else{
                        self.mensaje_activo('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>Se presentaron errores al guardar el archivo.</div>'); //mensaje not found se encuentra el el archivo call-back.js                           
                         
                    }                     
                },//funcion para recibir la respuesta 
                url: self.url+'activosactivo/',//url api
                parametros:data                       
                };
                RequestFormData2(parametros);

            }
            else{
 
            }
 


        }else{
            if(self.activoVO.contrato_id()==0){
                $("#validacionContrato").show();
            }

            if(self.activoVO.responsable_id()==0){
                $("#validacionResponsable").show();
            }
            
            if(self.activoVO.valor_compra()==0){
                $("#validacionValor").show();
            }
            
            ActivoViewModel.errores_activos_puntosgps.showAllMessages();
        }
    }


    self.cargar_puntos_gps = function (id){
        path = self.url+'activospuntosgps/?format=json';
        
            parameter = {                
                activo: id,                
            };
            RequestGet(function (datos, estado, mensage) {                
                if (estado == 'ok' && datos.count != 0) { 
               
                    for (var i = 0; i < datos.count; i++) {
                        if(i==0){
                           self.puntosgps.listado([]);
                        }    
                        

                        self.puntosgps.listado.push({
                            'id':ko.observable(datos.data[i].id),
                            'nombre':ko.observable(datos.data[i].nombre),
                            'longitud':ko.observable(datos.data[i].longitud),
                            'latitud':ko.observable(datos.data[i].latitud),
                        });

                    }

                }else{
               
                    self.puntosgps.listado([]);
                }
            
            cerrarLoading();
            }, path, parameter,undefined,false);

    }

    self.cargar_activo_atributos = function (id){
        path = self.url+'activosactivo_atributo/?format=json';
        
            parameter = {                
                activo: id,                
            };
            RequestGet(function (datos, estado, mensage) {                
                if (estado == 'ok' && datos != null) { 

                    for (var i = 0; i < datos.count; i++) {

                        if(i==0){
                           self.atributos.listado([]);
                        }    
                    

                        self.atributos.listado.push({
                            'id':ko.observable(datos.data[i].id),
                            'nombre':ko.observable(datos.data[i].atributo.nombre),
                            'atributo':ko.observable(datos.data[i].atributo.id),                  
                            'valor':ko.observable(datos.data[i].valor),
                            'estado':ko.observable(datos.data[i].atributo.requiere_soporte),
                            'lista_soportes':ko.observableArray([]),
                        });
                        if(datos.data[i].atributo.requiere_soporte){
                           self.cargar_activo_atributos_soportes(i,datos.data[i].id); 
                        }
                        
                    }

                }
            
            cerrarLoading();
            }, path, parameter,undefined,false);

    }

     self.cargar_activo_atributos_soportes = function(iteraccion,id_aux){
     path = self.url+'activosactivo_atributo_soporte/?format=json';
        
            parameter = {                
                activo_atributo: id_aux,                
            };
            RequestGet(function (datos, estado, mensage) {                
                if (estado == 'ok' && datos != null) { 
                    
                    for (var i = 0; i < datos.count; i++) {
                        

                        if(i==0){
                           self.atributos.listado()[iteraccion].lista_soportes([]);
                        }    
                    

                        self.atributos.listado()[iteraccion].lista_soportes.push({                           
                            'soporte_id':ko.observable(datos.data[i].id),
                            'soporte':ko.observable(''),                                
                        });
                        //alert("activo_atributo_id"+self.atributos.listado()[iteraccion].id()+"/soporte_id: "+self.atributos.listado()[iteraccion].lista_soportes()[i].soporte_id());
                       
                    }

                }
            
            cerrarLoading();
            }, path, parameter,undefined,false);

    }

    self.editar_activo_data = function(){
        //alert(ActivoViewModel.errores_activos_editar().length);

        var validacion_ingreso = true
        if (ActivoViewModel.errores_activos_editar().length != 0){
            ActivoViewModel.errores_activos_editar.showAllMessages();
            validacion_ingreso = false
        } 


        if(self.activoVO_editar.contrato_id()==0){
            $("#validacionContrato_editar").show();
             validacion_ingreso = false
        }

        if(self.activoVO_editar.responsable_id()==0){
            $("#validacionResponsable_editar").show();
             validacion_ingreso = false
        }
            
        if(self.activoVO_editar.valor_compra()==0){
             $("#validacionValor_editar").show();
              validacion_ingreso = false
        }else{
            $("#validacionValor_editar").hide();
        }





        if (validacion_ingreso){
            var tipo_id = sessionStorage.getItem("activo_tipo"); 

            if(tipo_id!=self.activoVO_editar.tipo_id()){
                 self.cargar_atributos(self.activoVO_editar.tipo_id());
            }else{
                self.cargar_activo_atributos(self.activoVO_editar.id());
            }
           
            
            $("#editar_atributo").modal('show');

        }

    }

    self.editar_atributos = function(){
        var validacion_ingreso = true;
        var tipo_id = sessionStorage.getItem("activo_tipo"); 

        if(tipo_id!=self.activoVO_editar.tipo_id()){

            for (var i = 0; i < self.atributos.listado().length; i++) {
                    if(self.atributos.listado()[i].valor()!=''){
                        $('#validacionATRIBUTOSvalor'+i).modal('hide');
                       
                    }else{
                         $('#validacionATRIBUTOSvalor'+i).modal('show');
                         validacion_ingreso = false
                    }

                    

            };

      
            for (var i = 0; i < self.atributos.listado().length; i++) {
                var segunda_lista = self.atributos.listado()[i];
                for (var j = 0; j < segunda_lista.lista_soportes().length; j++) {

                    if(self.atributos.listado()[i].estado()){
                        if(segunda_lista.lista_soportes()[j].soporte()!=''){
                                $('#validacionATRIBUTOSsoporte'+i+'_'+j).modal('hide');
                               
                        }else{  
                               
                                    $('#validacionATRIBUTOSsoporte'+i+'_'+j).modal('show');                            
                                    validacion_ingreso = false
                              
                                
                        }
                    }

                }
            };

            if(validacion_ingreso){
                self.cargar_puntos_gps(self.activoVO_editar.id());
                $("#editar_gps").modal('show');
            }else{
                ActivoViewModel.errores_activos_atributos.showAllMessages();
            }


             

        }else{
            for (var i = 0; i < self.atributos.listado().length; i++) {
                    if(self.atributos.listado()[i].valor()!=''){
                        $('#validacionATRIBUTOSvalor_editar'+i).modal('hide');
                       
                    }else{
                         $('#validacionATRIBUTOSvalor_editar'+i).modal('show');
                         validacion_ingreso = false
                    }
            };
            

            for (var i = 0; i < self.atributos.listado().length; i++) {
                if(self.atributos.listado()[i].estado()){   
                    var segunda_lista = self.atributos.listado()[i];
                    for (var j = 0; j < segunda_lista.lista_soportes().length; j++) {

                                    
                        if(segunda_lista.lista_soportes()[j].soporte_id()==0){
                            if(segunda_lista.lista_soportes()[j].soporte()!=''){
                                    $('#validacionATRIBUTOSsoporte_editar'+i+'_'+j).modal('hide');
                                   
                            }else{
                                    $('#validacionATRIBUTOSsoporte_editar'+i+'_'+j).modal('show');
                                                            
                                    validacion_ingreso = false
                            }
                        }                        


                    }

                }
            };
            
            
            if (validacion_ingreso){ 

                self.cargar_puntos_gps(self.activoVO_editar.id());
                $("#editar_gps").modal('show'); 

            }else{
                // self.cargar_activo_atributos(self.activoVO_editar.id());
                for (var i = 0; i < self.atributos.listado().length; i++) {
                        if(self.atributos.listado()[i].valor()!=''){
                            $('#validacionATRIBUTOSvalor_editar'+i).modal('hide');
                           
                        }else{
                            $('#validacionATRIBUTOSvalor_editar'+i).modal('show');
                             
                        }
                };

                for (var i = 0; i < self.atributos.listado().length; i++) {
                    if(self.atributos.listado()[i].estado()){   
                        var segunda_lista = self.atributos.listado()[i];
                        for (var j = 0; j < segunda_lista.lista_soportes().length; j++) {

                                        
                            if(segunda_lista.lista_soportes()[j].soporte_id()==0){
                                if(segunda_lista.lista_soportes()[j].soporte()!=''){
                                        $('#validacionATRIBUTOSsoporte_editar'+i+'_'+j).modal('hide');
                                       
                                }else{
                                        $('#validacionATRIBUTOSsoporte_editar'+i+'_'+j).modal('show');
                                                                
                                        validacion_ingreso = false
                                }
                            }                        


                        }

                    }
                };




            }
        }
        

        

    }

    self.guardar_activo_editar = function(){
        var validacion_ingreso = true;
    
            

            var data = new FormData();      
            data.append('id',self.activoVO_editar.id());
            data.append('tipo_id',self.activoVO_editar.tipo_id());
            data.append('identificacion',self.activoVO_editar.identificacion());
            data.append('serial_placa',self.activoVO_editar.serial_placa());
            data.append('descripcion',self.activoVO_editar.descripcion());
            data.append('contrato_id',self.activoVO_editar.contrato_id());
            data.append('valor_compra',self.activoVO_editar.valor_compra());
            data.append('responsable_id',self.activoVO_editar.responsable_id());
            data.append('vida_util_dias',self.activoVO_editar.vida_util_dias());
            data.append('periodicidad_mantenimiento',self.activoVO_editar.periodicidad_mantenimiento());
            data.append('fecha_baja',self.activoVO_editar.fecha_baja());
            data.append('fecha_alta',self.activoVO_editar.fecha_alta());
            data.append('motivo_debaja',self.activoVO_editar.motivo_debaja());
            data.append('soportedebaja',self.activoVO_editar.soportedebaja());
            data.append('debaja',self.activoVO_editar.debaja());

            for (var i = 0; i < self.puntosgps.listado().length; i++) {
                    

                    var validacion_ingreso_gps = 0;
                    
                    if((self.puntosgps.listado()[i].id()!='') || (self.puntosgps.listado()[i].id() == 0)){    
                 
                        if ((self.puntosgps.listado()[i].id() == 0)){
                            data.append('id_puntosgps[]',0);
                        }else{
                            data.append('id_puntosgps[]',self.puntosgps.listado()[i].id());
                        }               
                        
                        
                    }else{                                                
                        validacion_ingreso = false
               
                        
                    }


                    if(self.puntosgps.listado()[i].nombre()!=''){
                        $('#validacionGPSnombre_editar'+i).modal('hide');
                         data.append('nombre[]',self.puntosgps.listado()[i].nombre());
                        
                    }else{
                        $('#validacionGPSnombre_editar'+i).modal('show');
                        validacion_ingreso = false
                        validacion_ingreso_gps = validacion_ingreso_gps + 1
                      
                    }

                    

                    if(self.puntosgps.listado()[i].latitud()!=''){
                        $('#validacionGPSlatitud_editar'+i).modal('hide');
                         data.append('latitud[]',self.puntosgps.listado()[i].latitud());
                        
                    }else{
                         $('#validacionGPSlatitud_editar'+i).modal('show');
                         validacion_ingreso = false
                         validacion_ingreso_gps = validacion_ingreso_gps + 1
                      
                    }


                    if(self.puntosgps.listado()[i].longitud()!=''){
                         $('#validacionGPSlongitud_editar'+i).modal('hide');
                         data.append('longitud[]',self.puntosgps.listado()[i].longitud());
                         
                    }else{
                         $('#validacionGPSlongitud_editar'+i).modal('show');
                         validacion_ingreso = false
                         validacion_ingreso_gps = validacion_ingreso_gps + 1

                    }

                    

                    if ((validacion_ingreso_gps == 3) || (validacion_ingreso_gps == 0)){
                        $('#validacionGPSnombre_editar'+i).modal('hide');
                        $('#validacionGPSlatitud_editar'+i).modal('hide');
                        $('#validacionGPSlongitud_editar'+i).modal('hide');
                        validacion_ingreso = true
                    }else{
                        validacion_ingreso = false
                    }
            };




            for (var i = 0; i < self.atributos.listado().length; i++) {
                    if(self.atributos.listado()[i].valor()!=''){                       
                        data.append('atributo[]',self.atributos.listado()[i].atributo());
                        data.append('estado_atributo[]',self.atributos.listado()[i].estado());
                        data.append('valor[]',self.atributos.listado()[i].valor());
                        data.append('activo_atributo_id[]',self.atributos.listado()[i].id());
                    }else{                       
                         validacion_ingreso = false
                    }
                   

                };

                for (var i = 0; i < self.atributos.listado().length; i++) {
                    if(self.atributos.listado()[i].estado()){
                        var segunda_lista = self.atributos.listado()[i];

                        for (var j = 0; j < segunda_lista.lista_soportes().length; j++) {

                            
                                if(segunda_lista.lista_soportes()[j].soporte()!=''){                                   

                                    
                                    data.append('id_atributo[]',self.atributos.listado()[i].atributo());
                                    data.append('soporte_atributo[]',self.atributos.listado()[i].lista_soportes()[j].soporte());
                                    var tipo_id= sessionStorage.getItem("activo_tipo");
                                    if(tipo_id!=self.activoVO_editar.tipo_id()){
                                        data.append('soporte_id[]',0);
                                    }else{
                                        data.append('soporte_id[]',self.atributos.listado()[i].lista_soportes()[j].soporte_id());
                                    }
                                    

                                }else{    
                                    //alert("id:"+segunda_lista.lista_soportes()[j].soporte_id()+"/ i:"+i+"/ j:"+j)                                  
                                    
                                }



                        }
                    }
                }




     
            if (validacion_ingreso){ 

                  
                var parametros={
                    metodo:'PUT',                
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#editar_activo').modal('hide');
                            $('#editar_atributo').modal('hide');
                            $('#editar_gps').modal('hide');

                            self.consultar(1); 
                            self.consultar_activo(self.activoVO_editar.id()); 
                            self.limpiarActivo();

                        }else{
                        self.mensaje_activo('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>Se presentaron errores al guardar el archivo.</div>'); //mensaje not found se encuentra el el archivo call-back.js                           
                         
                        }
                    },
                    url: self.url+'activosactivo/'+self.activoVO_editar.id()+'/?format=json', //url api
                    parametros:data
                };
                RequestFormData2(parametros);
                cerrarLoading();
            }else{

                for (var i = 0; i < self.puntosgps.listado().length; i++) {
                    
                    if(self.puntosgps.listado()[i].nombre()!=''){                       
                        data.append('id_puntosgps[]',self.puntosgps.listado()[i].id());
                       
                    }


                    if(self.puntosgps.listado()[i].nombre()!=''){
                        $('#validacionGPSnombre_editar'+i).modal('hide');
                         data.append('nombre[]',self.puntosgps.listado()[i].nombre());
                        
                    }else{
                        $('#validacionGPSnombre_editar'+i).modal('show');
                       
                    }


                    if(self.puntosgps.listado()[i].latitud()!=''){
                        $('#validacionGPSlatitud_editar'+i).modal('hide');
                         data.append('latitud[]',self.puntosgps.listado()[i].latitud());
                     
                    }else{
                         $('#validacionGPSlatitud_editar'+i).modal('show');
                        
                    }


                    if(self.puntosgps.listado()[i].longitud()!=''){
                         $('#validacionGPSlongitud_editar'+i).modal('hide');
                         data.append('longitud[]',self.puntosgps.listado()[i].longitud());
                 
                    }else{
                         $('#validacionGPSlongitud_editar'+i).modal('show');                         
                    }
                };
               

            }
    }



    self.abrir_modal_contrato =function(){
        $('#asginar_contrato').modal('show');
        self.consultar_contratos(1);
        self.titulo_asignarcontrato('Asignar un contrato');
    }



    
    self.abrir_modal_responsable=function(){
        $('#asginar_responsable').modal('show');    
        self.consultar_responsables(1);
        self.titulo_asignarresponsable('Asignar un responsable');


    }

     self.utilizarContrato = function(obj){
        $("#activo_contrato_numero").val(obj.numero);
        $("#activo_contrato_numero_editar").val(obj.numero);        
        $('#asginar_contrato').modal('hide');
        $("#validacionContrato").hide();

        self.activoVO.contrato_id(obj.id)
        self.activoVO_editar.contrato_id(obj.id)
    }


           

    self.utilizarResponsable=function(obj){
        $("#activo_responsable_nombre").val(obj.persona.nombres+' '+obj.persona.apellidos);
        $("#activo_responsable_nombre_editar").val(obj.persona.nombres+' '+obj.persona.apellidos);
        $('#asginar_responsable').modal('hide');
        $("#validacionResponsable").hide();

        self.activoVO.responsable_id(obj.id)
        self.activoVO_editar.responsable_id(obj.id)
    }

    self.dar_debaja = function (obj){

         $.confirm({
                title:'Confirmar!',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Esta seguro que desea dar de baja al activo No. '+obj.id+' ?<h4>',
                confirmButton: 'Si',
                confirmButtonClass: 'btn-info',
                cancelButtonClass: 'btn-danger',
                cancelButton: 'No',
                confirm: function() {

                self.cambiar_estado_activo(obj);                
                $('#confirm').hide();
                }
            });
    }

    self.actualizar_dar_debaja = function(){
      
 


        if (ActivoViewModel.errores_activos_dar_debaja().length==0){
        if (self.dar_debaja_activo.id()>0){
     
        var parametros={ 
                    metodo:'PUT',                
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            
                            $('#dar_debaja').modal('hide');
                            self.consultar(1);  
                            self.limpiarActivo();
                            self.dar_debaja_activo.id('');
                            self.dar_debaja_activo.debaja(true);
                            self.dar_debaja_activo.motivo_debaja('');
                            self.dar_debaja_activo.soportedebaja('');
                            self.dar_debaja_activo.fecha_baja('');

                            self.dar_debaja_activo.motivo_debaja.isModified(false);
                            self.dar_debaja_activo.soportedebaja.isModified(false);

                            $("#soporte_debja").fileinput('reset');
                            $("#soporte_debja").val('');

                        }else{
                        self.mensaje_dar_debaja_activo('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>Se presentaron errores al guardar el archivo.</div>'); //mensaje not found se encuentra el el archivo call-back.js                           
                         
                        }
                    },
                    url: self.url+'activosactivo/'+self.dar_debaja_activo.id()+'/?format=json', //url api
                    parametros:self.dar_debaja_activo    
                };
                RequestFormData(parametros);
                cerrarLoading();
        }
    }
        ActivoViewModel.errores_activos_dar_debaja.showAllMessages();
    }

    self.cambiar_estado_activo =function(obj){

        $('#dar_debaja').modal('show');
        self.titulo_dar_debaja('Dar de baja al activo No. '+obj.id);
        self.dar_debaja_activo.id(obj.id);

    }

    self.editar_activo = function(id){
        self.limpiarActivo();        
        self.consultar_activo_por_id(id);
        self.titulo_activo('Editar un activo');
        $("#editar_activo").modal('show');
 
    }

    self.editar_punto = function(id){
        self.limpiarPunto();
        self.consultar_punto_gps(id);
        self.titulo_punto_gps('Edición del punto GPS')
        $("#puntos_gps").modal('show');
    }

    self.eliminar_punto=function(id){
        var path =self.url+'activospuntosgps/'+id+'/';
        var parameter = {};
        RequestAnularOEliminar("Esta seguro que desea eliminar el punto GPS?", path, parameter, 
            function(){                 
              self.consultar_activo(self.detalle.id());
              self.limpiarPunto();
        });      
    }

    self.eliminar_soporte_atributo=function(id,atributo_id){
        if(self.listadosoportes_atributo().length >1){
            var path =self.url+'activosactivo_atributo_soporte/'+id+'/';
            var parameter = {};
            RequestAnularOEliminar("Esta seguro que desea eliminar el soporte del atributo?", path, parameter, 
                function(){
                    if(atributo_id){
                        self.consultar_soportes_atributos(atributo_id);            
                        self.limpiarPunto();
                    }else{
                        return true;
                    }
                  
            });
        }else{
            $.confirm({
                    title:'Error',
                    content: '<h4><i class="text-warning fa fa-warning fa-2x"></i>No se puede eliminar el unico archivo cargado a este atributo.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
        }
         
    }


    self.guardarDocumento = function(){
        if (ActivoViewModel.errores_activo_atributo().length == 0){
            
            
            if (self.activo_atributoVO.id() == 0){                
                self.activo_atributoVO.activo_atributo_id(self.aux_activo_atributo_id());

             
                var parametros={
                        
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {                        
                      
                        self.ver_soportes_atributo(self.aux_activo_atributo_id(),self.aux_nombre_atributo());
                        self.limpiarSoporte();                     
                        
                    }
                    cerrarLoading()
                },//funcion para recibir la respuesta 
                url: self.url+'activosactivo_atributo_soporte/',//url api
                parametros:self.activo_atributoVO                       
                };
                RequestFormData(parametros);
            }
        }
    }

    self.exportar_excel=function(){        
        location.href=self.url_funcion+"reporte_activos/";
    
    
        return true;
    }
    //UBICACION GPS
    self.observar_punto_gps=function(){        
        
        
    }


    self.observar_punto_gps = function(obj){
        path =self.url+'activosactivo/'+obj.id+'/?format=json';
        parameter = {};

        RequestGet(function (data, estado, mensage) {
            sessionStorage.setItem("app_activo_ubicacion_categoria", data.tipo.categoria.id || '');
            sessionStorage.setItem("app_activo_ubicacion_tipo", data.tipo.id || '');
            var estado = 0
            if(data.debaja==true){
                estado = 1
            }
            // sessionStorage.setItem("app_activo_ubicacion_estado", estado);
            sessionStorage.setItem("app_activo_ubicacion_dato", data.serial_placa || '');
            sessionStorage.setItem("app_activo_ubicacion_funcionario", data.responsable.id || '');

        },path, parameter,function() {
            ruta = self.url+'../../activos/ubicacion/';
            window.location.href = ruta
        });
    }

    //GESTION DOCUMENTAL
    self.archivoFisicoBaja = function() {
        window.open('../../../gestiondocumental/archivofisico/Activos soportes de baja/' + 
            self.quitarTildes(self.detalle.tipo().toString()) + ' - ' + self.quitarTildes(self.detalle.descripcion().toString()) + '/' + 
            self.quitarTildes(self.detalle.id().toString())  + '/', '_blank');
    }
    self.archivoFisicoAlta = function() {
        window.open('../../../gestiondocumental/archivofisico/Contrato/contrato No. ' + 
            self.detalle.contrato().toString() + '/' + 
            self.detalle.contrato_id().toString()  + '/', '_blank');
    }
    self.archivoFisicoMantenimiento = function () {
        window.open('../../../gestiondocumental/archivofisico/Activos soportes de mantenimiento/activo id No.' + 
            self.quitarTildes(self.detalle.tipo().toString()) + ' - ' + self.quitarTildes(self.detalle.descripcion().toString()) + '/' + 
            self.quitarTildes(self.detalle.id().toString())  + '/', '_blank');       
    }

    self.quitarTildes = function (cadena) {
        cadena = cadena.replace("á","a");
        cadena = cadena.replace("é","e");
        cadena = cadena.replace("í","i");
        cadena = cadena.replace("ó","o");
        cadena = cadena.replace("ú","u");

        return cadena;
    }

}
var activo = new  ActivoViewModel();

$('#txtBuscar').val(sessionStorage.getItem("app_activo_dato"))
activo.cargar(1);

ActivoViewModel.errores_activos = ko.validation.group(activo.activoVO);
ActivoViewModel.errores_activos_puntosgps = ko.validation.group(activo.puntosgps);
ActivoViewModel.errores_activos_atributos = ko.validation.group(activo.atributos);
ActivoViewModel.errores_activos_dar_debaja = ko.validation.group(activo.dar_debaja_activo);
ActivoViewModel.errores_detalle = ko.validation.group(activo.detalle);
ActivoViewModel.errores_activos_editar = ko.validation.group(activo.activoVO_editar);
ActivoViewModel.errores_puntos_gps = ko.validation.group(activo.puntosgpsVO);
ActivoViewModel.errores_activo_atributo = ko.validation.group(activo.activo_atributoVO);
ko.applyBindings(activo);