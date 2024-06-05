function NovedadViewModel(argument) {
	var self=this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.buscado_rapido=ko.observable(false);
	self.url=path_principal+'/api/Novedad/'; 
	self.novedadVO=ko.observable({});
    self.nombre_contratista=ko.observable('');
    self.nombre_empleado=ko.observable('');
    self.cedula_empleado=ko.observable('');
    self.nombre_estado=ko.observable('');

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
    }

      self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

     self.abrir_modal = function () {
       /* self.limpiar();
        self.titulo('Registrar Empleado');
        $('#modal_acciones').modal('show');*/
    }

    self.abrir_filtros=function(){
      $('#modal_filtros').modal('show');
    }

    self.abrir_ver_mas=function(obj){
        self.novedadVO(obj);
        self.nombre_contratista(obj.empleado.contratista.nombre);
        self.nombre_empleado(obj.empleado.persona.nombres + ' ' + obj.empleado.persona.apellidos);
        self.cedula_empleado(obj.empleado.persona.cedula);
        self.nombre_estado(obj.estado.nombre);
      $('#modal_ver_mas').modal('show');
    }

    //exportar excel    
    self.exportar_excel=function(){
        if ( self.buscado_rapido()) {
            location.href=path_principal+"/seguridad-social/exportar-novedades?dato="+self.filtro();    
        }else{
            location.href=path_principal+"/seguridad-social/exportar-novedades?contratista_id="+self.filtros.contratista_id()+"&fecha_inicio="+self.filtros.fecha_inicio()+"&fecha_final="+self.filtros.fecha_final()
        }
        
    }

    self.filtros={
      contratista_id:ko.observable(''),//.extend({ required: { message: '(*)Seleccione el contratista' } }),
      fecha_inicio:ko.observable(''),//.extend({ required: { message: '(*) Seleccione la fecha inicio para continuar.' } }),
      fecha_final:ko.observable('')//.extend({ required: { message: '(*) Seleccione la fecha final para continuar.' } })
    }

    self.consultar = function (pagina) {
        if (pagina > 0) { 
            self.buscado_rapido(true);
            self.filtro($('#txtBuscar').val());
            path =self.url + '?format=json&page='+pagina;
            parameter = { dato: self.filtro()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                	
                    self.mensaje('');                     
                    self.listado(datos.data);  

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                
            }, path, parameter, function(){
                    cerrarLoading();
                   });
        }
    }

    self.consultar_por_filtros = function (pagina) {
        if (pagina > 0) { 
            if (NovedadViewModel.errores_filtros().length==0) {
            
                self.buscado_rapido(false);
                self.filtro($('#txtBuscar').val());
                path =self.url + '?format=json&page='+pagina;
                parameter = {dato: self.filtro(),contratista_id:self.filtros.contratista_id(),
                            fecha_inicio:self.filtros.fecha_inicio(), fecha_final:self.filtros.fecha_final()};
                RequestGet(function (datos, estado, mensage) {

                    if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                        
                        self.mensaje('');                     
                        self.listado(datos.data);  

                    } else {
                        self.listado([]);
                        self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    }

                    self.llenar_paginacion(datos,pagina);
                    
                }, path, parameter, function(){
                    cerrarLoading();
                   });
            }else{
                NovedadViewModel.errores_filtros.showAllMessages();
            }    
        }
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            if (self.buscado_rapido()) {
               self.consultar(1); 
           }else{
            self.consultar_por_filtros(1);
           }
            
        }
        return true;
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        
       self.consultar(pagina);
              
    });

	self.eliminar = function () {}
}

var novedad = new NovedadViewModel();
novedad.consultar(1);
NovedadViewModel.errores_filtros = ko.validation.group(novedad.filtros);
ko.applyBindings(novedad);