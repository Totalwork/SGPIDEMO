function TransaccionesViewModel(){
	var self = this;
	self.titulo=ko.observable('');
	self.mensaje=ko.observable('');
	self.listado=ko.observableArray([]);
	self.listado_usuarios=ko.observableArray([]);	
	self.url=path_principal+'/api/';
	self.desde_filtro=ko.observable('');
    self.hasta_filtro=ko.observable('');

	self.filtro={
		empresa_id: ko.observable(0),
		usuario_id: ko.observable(0),
		fecha_inicio: ko.observable(''),
		fecha_fin: ko.observable(''),
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
		}
	}

	self.paginacion.pagina_actual.subscribe(function (pagina) {
		self.consultar(pagina);
	});

	//Funcion para crear la paginacion
	self.llenar_paginacion = function (data,pagina) {
		self.paginacion.pagina_actual(pagina);
		self.paginacion.total(data.count);
		self.paginacion.cantidad_por_paginas(resultadosPorPagina);
	}



    self.filtro.empresa_id.subscribe(function (empresa_id) {

    	if((empresa_id!=null) & (empresa_id!=undefined) & (empresa_id!=0) & (empresa_id!="")){
    		//alert(empresa_id);
    		self.consultarUsuarios(empresa_id);
    	}else{
    		self.consultarUsuarios();
    	}

	});

	self.consultarUsuarios = function (empresa__id){
		path = path_principal+'/usuario/consultar-usuariosTransaccion/';
		//alert(empresa__id);
		parameter = {empresa_id: empresa__id || "",
					activado: 1
					};
		RequestGet(function (datos, estado, mensage) {
			//alert(empresa__id);
			if (estado == 'ok' && datos!=null && datos.length > 0) {

				self.listado_usuarios(datos);
			}else {
				self.listado_usuarios([]);
				//self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}
			cerrarLoading();
		}, path, parameter,undefined,false);
	}

    self.abrir_filtro = function () {		

		if (sessionStorage.getItem("tran_empresa_id") != ''){
                self.filtro.empresa_id(sessionStorage.getItem("tran_empresa_id"));
            }
        if (sessionStorage.getItem("tran_usuario_id") != ''){
                self.filtro.usuario_id(sessionStorage.getItem("tran_usuario_id"));
            }
        if (sessionStorage.getItem("tran_fecha_inicio") != ''){
                self.filtro.fecha_inicio(sessionStorage.getItem("tran_fecha_inicio"));
            }
        if (sessionStorage.getItem("tran_fecha_fin") != ''){
                self.filtro.fecha_fin(sessionStorage.getItem("tran_fecha_fin"));
            }

		$('#filtro').modal('show');

	}

	self.consultar = function(pagina){
		if (pagina > 0) {
			sessionStorage.setItem("tran_empresa_id",self.filtro.empresa_id() || '');
			sessionStorage.setItem("tran_usuario_id",self.filtro.usuario_id() || '');
			sessionStorage.setItem("tran_fecha_inicio",self.filtro.fecha_inicio() || '');
			sessionStorage.setItem("tran_fecha_fin",self.filtro.fecha_fin() || '');

			self.cargar(pagina);
		}
	}

	self.exportar_excel = function (liquidacion_id) {        
  //       empresa_id= sessionStorage.getItem("tran_empresa_id") || ''
		// usuario_id= sessionStorage.getItem("tran_usuario_id") || ''
		// fecha_inicio= sessionStorage.getItem("tran_fecha_inicio") || ''
		// fecha_fin= sessionStorage.getItem("tran_fecha_fin") || ''					

        location.href=path_principal+"/parametrizacion/exportTransacciones?empresa_id="+self.filtro.empresa_id()+       
        "&usuario_id"+self.filtro.usuario_id()+
        "&fecha_inicio="+self.filtro.fecha_inicio()+
        "&fecha_fin="+self.filtro.fecha_fin();

    }

	self.cargar = function(pagina){
		path = path_principal+'/api/Transacciones/?format=json';
		parameter = {empresa_id: sessionStorage.getItem("tran_empresa_id") || '',
					usuario_id:sessionStorage.getItem("tran_usuario_id") || '',
					fecha_inicio:sessionStorage.getItem("tran_fecha_inicio") || '',
					fecha_fin:sessionStorage.getItem("tran_fecha_fin") || '',					
					page: pagina };
		RequestGet(function (datos, estado, mensage) {

			if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
				self.mensaje('');				
				self.listado(agregarOpcionesObservable(datos.data));					

			} else {
				self.listado([]);
				self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}
			//console.log("pag:"+pagina);
			if(datos.count > 10){
				self.llenar_paginacion(datos,pagina);
				$('#paginacion').show();
			}else{
				$('#paginacion').hide();
			}

			$('#filtro_contrato').modal('hide');
			cerrarLoading();

		}, path, parameter, function(){},false);
	}

}

var transacciones = new TransaccionesViewModel();
transacciones.consultar(1);
ko.applyBindings(transacciones); 