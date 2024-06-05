function SolicitudViewModel(){
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	self.num_registro=ko.observable('');

	self.mensaje_cont=ko.observable('');//mensaje para el modal de contrato
	self.lista_contrato=ko.observableArray([]);
	// self.mensaje_beneficiario=ko.observable('');//mensaje para el modal de beneficiario
	// self.lista_beneficiario=ko.observableArray([]);
	self.listado_tipo=ko.observableArray([]);
	self.listado_estado=ko.observableArray([]);
	self.listado_tipo_contrato=ko.observableArray([]);

	self.mensaje_poliza=ko.observable('');
	self.mensaje_tipo_poliza=ko.observable('');
	self.num_registro_poliza=ko.observable('');

	self.lista_juridico=ko.observableArray([]);
	self.lista_compras=ko.observableArray([]);
	self.lista_tecnica=ko.observableArray([]);
	self.lista_poliza=ko.observableArray([]);
	self.lista_poliza_requisito=ko.observableArray([]);
	self.lista_requisito_poliza=ko.observableArray([]);

	self.nombre_contrato=ko.observable('');
	// self.nombre_beneficiario=ko.observable('');
	self.soporte=ko.observable('');
	self.soporteJuridico=ko.observable('');
	self.soporteCompras=ko.observable('');
	self.soporteTecnico=ko.observable('');
	self.soportePoliza=ko.observable('');
	// self.listado_descuento_c=ko.observableArray([]);

	self.titulo_tab=ko.observable('');

	self.buscar_contrato={
		tipo_contrato:ko.observable('').extend({ required: { message: '(*)Seleccione un tipo' } }),
		nom_num_contrato:ko.observable('')//.extend({ required: { message: '(*)Digite nombre o número del contrato' } })
	}

	self.estado={
		en_estudio:ko.observable(0),
		aprobada:ko.observable(0),
		rechazada:ko.observable(0),
	};
	self.num_estado={
		en_estudio:ko.observable(0),
		aprobada:ko.observable(0),
		rechazada:ko.observable(0),
	};

	// Local
	/*self.tablaForanea={
		encabezadoGiros:ko.observable(20),
		factura:ko.observable(1086),
		cesion:ko.observable(1088),
		descuento:ko.observable(1089)
	};*/
	// Maquina Virtual
	/*self.tablaForanea={
		encabezadoGiros:ko.observable(38),
		factura:ko.observable(140),
		cesion:ko.observable(142),
		descuento:ko.observable(143)
	};*/

	self.solicitudVO={
		id:ko.observable(0),
		tipo_id:ko.observable().extend({ required: { message: '(*)Seleccione un tipo' } }),
		estado_id:ko.observable(4002),
		contrato_id:ko.observable().extend({ required: { message: '(*)Seleccione un contrato' } }),
		fecha:ko.observable('').extend({ required: { message: '(*)Seleccione una fecha' } }),
		observacion:ko.observable('').extend({ required: { message: '(*)Digite el concepto del descuento' } }),
		carta_aceptacion:ko.observable(''),
		soporte:ko.observable('')
	}

	self.filtro_solicitud={
		contratista_nom:ko.observable(''),
		contratista_lista:ko.observableArray([]),
		tipo:ko.observable(''),
		estado:ko.observable(''),
		contratista:ko.observable(''),
		desde:ko.observable(''),
		hasta:ko.observable('')
	}

	self.detalle={
		tipo:ko.observable(''),
		estado:ko.observable(''),
		contrato:ko.observable(''),
		fecha:ko.observable(''),
		observacion:ko.observable(''),
		soporte:ko.observable(''),
		soporte_carta:ko.observable(''),
	}

	self.favorabilidadJuridicaVO={
		id:ko.observable(0),
		solicitud_id:ko.observable(0),
		observacion:ko.observable(''),
		sb_soporte:ko.observable(0),
		soporte:ko.observable(''),
		requisitos:ko.observableArray([])
	}

	self.favorabilidadComprasVO={
		id:ko.observable(0),
		solicitud_id:ko.observable(0),
		observacion:ko.observable(''),
		sb_soporte:ko.observable(0),
		soporte:ko.observable(''),
		requisitos:ko.observableArray([])
	}

	self.favorabilidadTecnicaVO={
		id:ko.observable(0),
		solicitud_id:ko.observable(0),
		observacion:ko.observable(''),
		sb_soporte:ko.observable(0),
		soporte:ko.observable(''),
		requisitos:ko.observableArray([])
	}

	self.validarPolizaVO={
		id:ko.observable(0),
		solicitud_id:ko.observable(0),
		sb_soporte:ko.observable(0),
		soporte:ko.observable(''),
		requisitos:ko.observableArray([])
	}

	// Inicio de Paginacion
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

	self.paginacion2 = {
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
	self.paginacion2.pagina_actual.subscribe(function (pagina) {
		self.buscarContrato(pagina);
	});
	//Funcion para crear la paginacion
	self.llenar_paginacion2 = function (data,pagina) {
		self.paginacion2.pagina_actual(pagina);
		self.paginacion2.total(data.count);
		self.paginacion2.cantidad_por_paginas(resultadosPorPagina);
	}
	// Fin de Paginacion

	self.abrir_modal = function () {
		self.limpiar();
		self.titulo('Registrar una Solicitud');
		$('#modal_acciones').modal('show');
	}
	self.abrir_modal_contrato = function () {
		$('#modal_contrato').modal('show');
	}
	/*self.abrir_modal_beneficiario = function () {
		$('#modal_beneficiario').modal('show');
	}*/
	self.abrir_filtro = function () {
		$('#modal_filtro').modal('show');
	}

	//limpiar el modelo
	self.limpiar=function(){
		self.solicitudVO.id(0);
		self.solicitudVO.tipo_id(0);
		self.solicitudVO.estado_id(0);
		self.solicitudVO.contrato_id(0);
		self.solicitudVO.fecha('');
		self.solicitudVO.observacion('');
		self.solicitudVO.carta_aceptacion('');
		self.solicitudVO.soporte('');
		self.nombre_contrato('');
		// self.nombre_beneficiario('');
		$('#archivo').fileinput('reset');
		$('#archivo').val('');
		$('#archivo_carta').fileinput('reset');
		$('#archivo_carta').val('');
		// $('#archivo_carta').fileinput('reset');
		// $('#archivo_carta').val('');

		self.solicitudVO.tipo_id.isModified(false);
		self.solicitudVO.fecha.isModified(false);
		self.solicitudVO.observacion.isModified(false);
	}
	//limpiar el filtro de contrato
	self.limpiar_contrato=function(){
		self.buscar_contrato.tipo_contrato('');
		self.buscar_contrato.nom_num_contrato('');
		self.mensaje_cont('');
		self.lista_contrato([]);

		self.buscar_contrato.tipo_contrato.isModified(false);
	}
	//limpiar el modelo - validarPolizaVO
	self.limpiar_poliza=function(){
		// self.validarPolizaVO.id(0);
		// self.validarPolizaVO.solicitud_id(0);
		self.validarPolizaVO.requisitos([]);
		self.validarPolizaVO.soporte('');
		self.soportePoliza('');
		// self.nombre_beneficiario('');
		$('#archivo_poliza').fileinput('reset');
		$('#archivo_poliza').val('');

		// self.validarPolizaVO.observacion.isModified(false);
	}
	self.limpiar_tecnica=function(){
		// self.favorabilidadTecnicaVO.id(0);
		// self.favorabilidadTecnicaVO.solicitud_id(0);
		// self.favorabilidadTecnicaVO.observacion('');
		self.favorabilidadTecnicaVO.requisitos([]);
		self.favorabilidadTecnicaVO.soporte('');
		self.soporteTecnico('');

		$('#archivo_tecnico').fileinput('reset');
		$('#archivo_tecnico').val('');

		// self.favorabilidadTecnicaVO.observacion.isModified(false);
	}
	self.limpiar_compras=function(){
		// self.favorabilidadComprasVO.id(0);
		// self.favorabilidadComprasVO.solicitud_id(0);
		// self.favorabilidadComprasVO.observacion('');
		self.favorabilidadComprasVO.requisitos([]);
		self.favorabilidadComprasVO.soporte('');
		self.soporteCompras('');

		$('#archivo_compras').fileinput('reset');
		$('#archivo_compras').val('');

		// self.favorabilidadComprasVO.observacion.isModified(false);
	}
	self.limpiar_juridica=function(){
		// self.favorabilidadJuridicaVO.id(0);
		// self.favorabilidadJuridicaVO.solicitud_id(0);
		// self.favorabilidadJuridicaVO.observacion('');
		self.favorabilidadJuridicaVO.requisitos([]);
		self.favorabilidadJuridicaVO.soporte('');
		self.soporteJuridico('');

		$('#archivo_juridico').fileinput('reset');
		$('#archivo_juridico').val('');

		// self.favorabilidadJuridicaVO.observacion.isModified(false);
	}
	// Limpiar filtro
	self.limpiar_filtro=function(){
		self.filtro_solicitud.contratista_nom(''),
		self.filtro_solicitud.contratista_lista([]),
		self.filtro_solicitud.tipo(''),
		self.filtro_solicitud.estado(''),
		self.filtro_solicitud.contratista(''),
		self.filtro_solicitud.desde(''),
		self.filtro_solicitud.hasta('')
	}

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.consultar(1);
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}
	self.consulta_enter_filtro = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.empresa();
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}
	/*self.consulta_enter_beneficiario = function (d,e) {
		if (e.which == 13) {
			self.buscarBeneficiario(1);
		}
		return true;
	}
	self.consulta_enter_beneficiario_filtro = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.buscarBeneficiarioFiltro();
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}*/

	//Buscar Contrato
	self.buscarContrato=function(pagina){

		parameter={id_tipo:self.buscar_contrato.tipo_contrato(),
									dato:self.buscar_contrato.nom_num_contrato(),
									lite:'1',
									page: pagina};
		path =path_principal+'/api/Contrato/?format=json';

		if (SolicitudViewModel.errores_bus_contrato().length == 0){ //se activa las validaciones
			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
					self.mensaje_cont('');
					self.lista_contrato(agregarOpcionesObservable(datos.data));
				} else {
					self.lista_contrato([]);
					self.mensaje_cont(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				}
				if(datos.count > 10){
					self.llenar_paginacion2(datos,pagina);
					$('#paginacion2').show();
				}else{
					$('#paginacion2').hide();
				}
				cerrarLoading();
			}, path, parameter, function(){},false);
		} else {
			SolicitudViewModel.errores_bus_contrato.showAllMessages();
		}
	}

	// Buscar el Beneficiario
	/*self.buscarBeneficiario=function(pagina){

		// console.log("nom_nit:"+self.buscar_beneficiario.nit_nom());
		// console.log("tipo:"+self.buscar_beneficiario.tipo());
		self.buscar_beneficiario.nit_nom($("#nit_nom").val());

		parameter={dato:self.buscar_beneficiario.nit_nom() };
		path =path_principal+'/api/empresa/?sin_paginacion&'+self.buscar_beneficiario.tipo()+'=1&format=json&';

		RequestGet(function (results,success) {
			if (success == 'ok' && results.length > 0) {
				self.mensaje_beneficiario('');
				self.lista_beneficiario(results);
			}else {
				self.lista_beneficiario([]);
				self.mensaje_beneficiario(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}

			// console.log("success:"+success);
		}, path, parameter);
	}*/

	// Buscar el Beneficiario para el filtro
	/*self.buscarBeneficiarioFiltro=function(){

		// console.log("nom_nit:"+self.filtro_descuento.nit_nom());
		// console.log("tipo:"+self.filtro_descuento.tipo());
		self.filtro_descuento.nom_beneficiario($("#nom_beneficiario").val());

		parameter={dato:self.filtro_descuento.nom_beneficiario()
							 // esProveedor:1
							// esContratista:1
							};
		path =path_principal+'/api/empresa/?sin_paginacion&'+self.filtro_descuento.tipo()+'=1&format=json';

		RequestGet(function (results,success) {
			if (success == 'ok' && results.length > 0) {
				//self.mensaje_beneficiario('');
				self.filtro_descuento.beneficiario_lista(results);
			}else {
				self.filtro_descuento.beneficiario_lista([]);
				//self.mensaje_beneficiario(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}

			// console.log("success:"+success);
		}, path, parameter);
	}*/

	self.ponerContrato = function (obj) {

		//alert(obj.id); return false;
		
		// self.solicitudVO.contrato_id(obj.id);
		self.nombre_contrato(obj.nombre);
		//self.habilitar_campos(true);
		$('#modal_contrato').modal('hide');
		return true;
	}
	// Buscar el contratista
	self.empresa=function(){
		parameter={dato:$("#contratista_nom").val() };
		path =path_principal+'/api/empresa/?sin_paginacion&esContratista=1&format=json';

		RequestGet(function (results,count) {

			self.filtro_solicitud.contratista_lista(results);
		}, path, parameter);
	}

	self.guardar=function(){
		//console.log('g_m:'+self.solicitudVO.meses());
		if (SolicitudViewModel.errores_solicitud().length == 0){ //se activa las validaciones

			// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
			if(self.solicitudVO.id()==0){
				// alert("guardar la solicitud nueva");
				// self.solicitudVO.estado_id(4002);
				self.solicitudVO.estado_id(self.estado.en_estudio());
				// alert(self.estado.en_estudio());
				// return false;

				var soporte = true;
				if($('#archivo')[0].files.length==0){
					self.solicitudVO.soporte('');
					soporte = false;
				}

				if(soporte){
					// if((self.solicitudVO.valor() != 0) && (self.solicitudVO.valor() != '')){
						var parametros={
							callback:function(datos, estado, mensaje){

								if (estado=='ok') {

									$('#modal_acciones').modal('hide');
									self.limpiar();
									self.consultar(1);
								}else{
									mensajeError(mensaje);
								}
							}, //funcion para recibir la respuesta 
							url:path_principal+'/api/Solicitud/',//url api
							parametros:self.solicitudVO
						};
						//parameter =ko.toJSON(self.solicitudVO);
						//Request(parametros);
						RequestFormData(parametros);
					// }else{
					// 	mensajeInformativo('Falta por ingresar un valor.','Información');
					// }
				}else{
					mensajeInformativo('Falta por seleccionar el soporte.','Información');
				}
			}else{
				// alert("editar las solicitud");
				if($('#archivo')[0].files.length==0){
					self.solicitudVO.soporte('');
				}
				// console.log("val:"+self.solicitudVO.valor());
				// if((self.solicitudVO.valor() != 0) && (self.solicitudVO.valor() != '')){
					var parametros={
						metodo:'PUT',
						callback:function(datos, estado, mensaje){

							if (estado=='ok') {
								self.filtro("");
								self.consultar(self.paginacion.pagina_actual());
								$('#modal_acciones').modal('hide');
								$('#editar_solicitud_requisitos').modal('hide');
								self.limpiar();
								self.limpiar_contrato();
							}

						},//funcion para recibir la respuesta 
						url:path_principal+'/api/Solicitud/'+self.solicitudVO.id()+'/',
						parametros:self.solicitudVO
					};
					RequestFormData(parametros);
				// }else{
				// 	mensajeInformativo('Falta por ingresar un valor.','Información');
				// }
			}
		} else {
			// alert("capos por llenar");
			SolicitudViewModel.errores_solicitud.showAllMessages();
		}
	}

	self.guardarJuridico=function(){
		//console.log('g_m:'+self.favorabilidadJuridicaVO.meses());
		//if (SolicitudViewModel.errores_solicitud().length == 0){ //se activa las validaciones

			if(self.favorabilidadJuridicaVO.id()==0){
				
			}else{

				if($('#archivo_juridico')[0].files.length==0){
					self.favorabilidadJuridicaVO.soporte('');
				}
				// Buscarlo los rubros Seleccionados
				var lista=[];
				ko.utils.arrayForEach(self.lista_juridico(),function(p){
					if (p.estado) {
						lista.push(p.id);
					}
				});
				self.favorabilidadJuridicaVO.requisitos(lista);
				var parametros={
					metodo:'PUT',
					callback:function(datos, estado, mensaje){

						if (estado=='ok') {
							self.limpiar_juridica();
							$('#editar_solicitud_requisitos').modal('hide');
						}

					},//funcion para recibir la respuesta 
					url:path_principal+'/api/SolicitudFavorabilidadJuridica/'+self.favorabilidadJuridicaVO.id()+'/',
					parametros:self.favorabilidadJuridicaVO
				};
				RequestFormData(parametros);
			}
		/*} else {
			SolicitudViewModel.errores_solicitud.showAllMessages();
		}*/
	}

	self.guardarCompras=function(){
		//console.log('g_m:'+self.favorabilidadComprasVO.meses());
		//if (SolicitudViewModel.errores_solicitud().length == 0){ //se activa las validaciones

			if(self.favorabilidadComprasVO.id()==0){

			}else{

				if($('#archivo_compras')[0].files.length==0){
					self.favorabilidadComprasVO.soporte('');
				}
				// Buscarlo los rubros Seleccionados
				var lista=[];
				ko.utils.arrayForEach(self.lista_compras(),function(p){
					if (p.estado) {
						lista.push(p.id);
					}
				});
				self.favorabilidadComprasVO.requisitos(lista);
				var parametros={
					metodo:'PUT',
					callback:function(datos, estado, mensaje){

						if (estado=='ok') {
							self.limpiar_compras();
							$('#editar_solicitud_requisitos').modal('hide');
						}

					},//funcion para recibir la respuesta 
					url:path_principal+'/api/SolicitudFavorabilidadCompras/'+self.favorabilidadComprasVO.id()+'/',
					parametros:self.favorabilidadComprasVO
				};
				RequestFormData(parametros);
			}
		/*} else {
			SolicitudViewModel.errores_solicitud.showAllMessages();
		}*/
	}

	self.guardarTecnico=function(){
		//console.log('g_m:'+self.favorabilidadTecnicaVO.meses());
		//if (SolicitudViewModel.errores_solicitud().length == 0){ //se activa las validaciones

		if(self.favorabilidadTecnicaVO.id()==0){

		}else{

			if($('#archivo_tecnico')[0].files.length==0){
				self.favorabilidadTecnicaVO.soporte('');
			}
			// Buscarlo los rubros Seleccionados
			var lista=[];
			ko.utils.arrayForEach(self.lista_tecnica(),function(p){
				if (p.estado) {
					lista.push(p.id);
				}
			});
			self.favorabilidadTecnicaVO.requisitos(lista);
			var parametros={
				metodo:'PUT',
				callback:function(datos, estado, mensaje){

					if (estado=='ok') {
						self.limpiar_tecnica();
						$('#editar_solicitud_requisitos').modal('hide');
					}
				},//funcion para recibir la respuesta 
				url:path_principal+'/api/SolicitudFavorabilidadTecnica/'+self.favorabilidadTecnicaVO.id()+'/',
				parametros:self.favorabilidadTecnicaVO
			};
			RequestFormData(parametros);
		}
		/*} else {
			SolicitudViewModel.errores_solicitud.showAllMessages();
		}*/
	}

	self.guardarPoliza=function(){
		//console.log('g_m:'+self.validarPolizaVO.meses());
		//if (SolicitudViewModel.errores_solicitud().length == 0){ //se activa las validaciones

		if(self.validarPolizaVO.id()==0){

		}else{

			if($('#archivo_poliza')[0].files.length==0){
				self.validarPolizaVO.soporte('');
			}
			var parametros={
				metodo:'PUT',
				callback:function(datos, estado, mensaje){

					if (estado=='ok') {
						self.limpiar_poliza();
						$('#editar_solicitud_requisitos').modal('hide');
					}
				},//funcion para recibir la respuesta 
				url:path_principal+'/api/SolicitudValidarPoliza/'+self.validarPolizaVO.id()+'/',
				parametros:self.validarPolizaVO
			};
			RequestFormData(parametros);
		}
		/*} else {
			SolicitudViewModel.errores_solicitud.showAllMessages();
		}*/
	}

	self.guardarRequisitoPoliza=function(){
		//console.log('g_m:'+self.favorabilidadTecnicaVO.meses());
		//if (SolicitudViewModel.errores_solicitud().length == 0){ //se activa las validaciones

		// Buscarlo los rubros Seleccionados
		var lista_id=[];
		ko.utils.arrayForEach(self.lista_requisito_poliza(),function(p){
			poliza_tipo = p.poliza_tipo;
			if (p.estado) {
				lista_id.push(p.id);
				//alert("actv.");
			}
		});

		var parametros={
			callback:function(datos, estado, mensaje){
				if (estado=='ok'){
					$('#detalle_tipo_poliza').modal('hide');
					$('#editar_solicitud_requisitos').modal('hide');
				}
			},//funcion para recibir la respuesta 
			url:path_principal+'/solicitud/update_requisitos_poliza/',
			parametros:ko.toJS({lista:lista_id, id_poliza_tipo:poliza_tipo})
			//completado:function(){
				// cerrarLoading();
			//}
		};
		Request(parametros);

		// lista.push({csrfmiddlewaretoken:getCookie('csrftoken')});
		// // var data = ; csrfmiddlewaretoken: getCookie('csrftoken')
		// $.post(path_principal+"/solicitud/update_requisitos_poliza/", ko.toJSON(lista), function(returnedData) {
		// 	// This callback is executed if the post was successful
		// 	alert(returnedData);
		// })
	}

	self.guardarCartaAceptacion=function(){

		self.solicitudVO.estado_id(self.estado.aprobada());
		self.guardar();
	}

	// Consultar solicitud
	self.consultar = function (pagina) {
		if (pagina > 0) {
			self.filtro($('#txtBuscar').val());

			sessionStorage.setItem("sol_cto_filtro",self.filtro() || '');
			sessionStorage.setItem("sol_cto_estado",self.filtro_solicitud.estado() || '');
			sessionStorage.setItem("sol_cto_tipo",self.filtro_solicitud.tipo() || '');
			sessionStorage.setItem("sol_cto_contratista",self.filtro_solicitud.contratista() || '');
			sessionStorage.setItem("sol_cto_contratista_nom",self.filtro_solicitud.contratista_nom() || '');
			sessionStorage.setItem("sol_cto_contratista_lista",self.filtro_solicitud.contratista_lista() || []);
			sessionStorage.setItem("sol_cto_desde",self.filtro_solicitud.desde() || '');
			sessionStorage.setItem("sol_cto_hasta",self.filtro_solicitud.hasta() || '');

			path = path_principal+'/api/Solicitud/?format=json';
			parameter = {dato: self.filtro(),
									id_estado: self.filtro_solicitud.estado(),
									id_tipo: self.filtro_solicitud.tipo(),
									id_contratista: self.filtro_solicitud.contratista(),
									desde: self.filtro_solicitud.desde(),
									hasta: self.filtro_solicitud.hasta(),
									tipo:'1',
									num_estado:'1',
									page: pagina };
			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos.data.listado!=null && datos.data.listado.length > 0) {
					self.mensaje('');
					self.num_registro("- N° de Registos: "+datos.count);
					self.listado(agregarOpcionesObservable(datos.data.listado));

					self.listado_tipo(agregarOpcionesObservable(datos.data.tipo));
					self.listado_estado(agregarOpcionesObservable(datos.data.estado));
					self.listado_tipo_contrato(agregarOpcionesObservable(datos.data.tipo_contrato));

					// Numero de Solicitudes por estado
					self.num_estado.en_estudio(datos.data.num_estado.enEstudio);
					self.num_estado.aprobada(datos.data.num_estado.aprobada);
					self.num_estado.rechazada(datos.data.num_estado.rechazada);

					if(sessionStorage.getItem("sol_cto_estado") != null ){
						solicitud.filtro_solicitud.estado(sessionStorage.getItem("sol_cto_estado"));
					}
					if(sessionStorage.getItem("sol_cto_tipo") != null ){
						solicitud.filtro_solicitud.tipo(sessionStorage.getItem("sol_cto_tipo"));
					}
				}else if(datos.data.tipo!=null && datos.data.tipo.length > 0){
					self.listado_tipo(agregarOpcionesObservable(datos.data.tipo));
					self.listado_estado(agregarOpcionesObservable(datos.data.estado));
					self.listado_tipo_contrato(agregarOpcionesObservable(datos.data.tipo_contrato));

					self.listado([]);
					self.num_registro("");
					self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js

					if(sessionStorage.getItem("sol_cto_estado") != null ){
						solicitud.filtro_solicitud.estado(sessionStorage.getItem("sol_cto_estado"));
					}
					if(sessionStorage.getItem("sol_cto_tipo") != null ){
						solicitud.filtro_solicitud.tipo(sessionStorage.getItem("sol_cto_tipo"));
					}
				} else {
					self.listado([]);
					self.num_registro("");
					self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				}
				if(datos.count > 10){
					self.llenar_paginacion(datos,pagina);
					$('#paginacion').show();
				}else{
					$('#paginacion').hide();
				}
				self.llenar_paginacion(datos,pagina);
				$('#modal_filtro').modal('hide');
				
			}, path, parameter,function(){cerrarLoading();},false);
		}
	}

	// Buscar los registrar compensados
	/*self.buscarRegistrosCompensados=function(){

		parameter2={//id_contrato:self.cruceVO.contrato_id(),
								id_tablaForanea:self.tablaForanea.descuento()};
		path2 =path_principal+'/api/FacturaDetalleCompensacion/?format=json&sin_paginacion';

		RequestGet(function (datos, estado, mensage) {

			if (estado == 'ok' && datos!=null && datos.length > 0) {
				
				console.log(datos);

				var lista_ids=[];
				ko.utils.arrayForEach(datos, function(d) {

					lista_ids.push(
						d.id_registro
					);
				});
				console.log("ids:"+lista_ids);

				self.listado_descuento_c(agregarOpcionesObservable(lista_ids));
			} else {
				console.log("Nooo");
				self.listado_descuento_c([]);
			}
		}, path2, parameter2, function(){
			self.consultar(1);
		},false);
	}*/

	// Para editar
	self.consultar_por_id = function (obj) {

		path =path_principal+'/api/Solicitud/'+obj.id+'/?format=json';
		parameter = {};
		self.limpiar();
		self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar Solicitud');

			self.solicitudVO.id(datos.id);
			self.solicitudVO.tipo_id(datos.tipo.id);
			self.solicitudVO.estado_id(datos.estado.id);
			self.solicitudVO.contrato_id(datos.contrato.id);
			self.nombre_contrato(datos.contrato.nombre);
			self.solicitudVO.fecha(datos.fecha);
			self.solicitudVO.observacion(datos.observacion);

			self.solicitudVO.soporte(datos.soporte);
			self.soporte(datos.soporte);

			$('#modal_acciones').modal('show');
		}, path, parameter);
	}

	// Para var el detalle
	self.consultar_por_id_detalle = function (obj) {

		path =path_principal+'/api/Solicitud/'+obj.id+'/?format=json';
		parameter = {};
		// self.limpiar();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.detalle.tipo(datos.tipo.nombre);
			self.detalle.estado(datos.estado.nombre);
			self.detalle.contrato(datos.contrato.numero);
			self.detalle.fecha(datos.fecha);
			self.detalle.observacion(datos.observacion);
			self.detalle.soporte(datos.soporte);
			self.detalle.soporte_carta(datos.carta_aceptacion);

			// JURIDICO
			self.limpiar_juridica();
			self.lista_juridico(datos.juridico.requisito);

			// self.favorabilidadJuridicaVO.id(datos.juridico.id);
			// self.favorabilidadJuridicaVO.solicitud_id(datos.id);
			self.favorabilidadJuridicaVO.observacion(datos.juridico.observacion);
			self.favorabilidadJuridicaVO.soporte(datos.juridico.soporte);

			self.soporteJuridico(datos.juridico.soporte);

			// TECNICA
			self.lista_tecnica(datos.tecnica.requisito);

			// self.favorabilidadTecnicaVO.id(datos.tecnica.id);
			// self.favorabilidadTecnicaVO.solicitud_id(datos.id);
			self.favorabilidadTecnicaVO.observacion(datos.tecnica.observacion);
			self.favorabilidadTecnicaVO.soporte(datos.tecnica.soporte);

			self.soporteTecnico(datos.tecnica.soporte);

			// COMPRAS
			self.lista_compras(datos.compras.requisito);

			// self.favorabilidadComprasVO.id(datos.compras.id);
			// self.favorabilidadComprasVO.solicitud_id(datos.id);
			self.favorabilidadComprasVO.observacion(datos.compras.observacion);
			self.favorabilidadComprasVO.soporte(datos.compras.soporte);

			self.soporteCompras(datos.compras.soporte);

			// POLIZA
			self.lista_poliza(datos.poliza.tipo_poliza);
			self.soportePoliza(datos.poliza.soporte);

			// self.validarPolizaVO.id(datos.poliza.id);
			// self.validarPolizaVO.solicitud_id(datos.id);
			// self.validarPolizaVO.sb_soporte(datos.poliza.sb_soporte);
			self.validarPolizaVO.soporte(datos.poliza.soporte);

			$('#detalle_solicitud').modal('show');
		}, path, parameter);
	}

	// Para Editar los requisitos de la Solicitud
	self.editarSolicitudRequisitos = function(obj){
		$('#editar_solicitud_requisitos').modal('show');

		path =path_principal+'/api/Solicitud/'+obj.id+'/?format=json';
		parameter = {};
		// self.limpiar();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			// SOLICITUD
			self.detalle.tipo(datos.tipo.nombre);
			// self.detalle.estado(datos.estado.nombre);
			self.detalle.contrato(datos.contrato.numero);
			// self.detalle.fecha(datos.fecha);
			// self.detalle.observacion(datos.observacion);
			self.detalle.soporte(datos.soporte);
			self.detalle.soporte_carta(datos.carta_aceptacion);

			self.solicitudVO.id(datos.id);
			self.solicitudVO.tipo_id(datos.tipo.id);
			self.solicitudVO.estado_id(datos.estado.id);
			self.solicitudVO.contrato_id(datos.contrato.id);
			self.solicitudVO.fecha(datos.fecha);
			self.solicitudVO.observacion(datos.observacion);
			self.solicitudVO.soporte('');
			self.solicitudVO.carta_aceptacion('');

			// Validar si puede guardar Carta de Aceptacion
			if(datos.juridico.soporte == '' || datos.compras.soporte == '' || datos.tecnica.soporte == '' ||  datos.poliza.soporte == null || datos.poliza.soporte == ''){
				$('#btn_guardar_carta').attr('disabled','disabled');
				$('#archivo_carta').attr('disabled','disabled');
				$('#archivo_carta_d .file-input-new .kv-fileinput-caption').attr('disabled','disabled');
				$('#archivo_carta_d .file-caption-main .input-group-btn .btn-file').attr('disabled','disabled');
			}else{
				$('#btn_guardar_carta').removeAttr('disabled','disabled');
				$('#archivo_carta').removeAttr('disabled');
				$('#archivo_carta_d .file-input-new .kv-fileinput-caption').removeAttr('disabled');
				$('#archivo_carta_d .file-caption-main .input-group-btn .btn-file').removeAttr('disabled');
			}

			// JURIDICO
			self.limpiar_juridica();
			self.lista_juridico(datos.juridico.requisito);

			self.favorabilidadJuridicaVO.id(datos.juridico.id);
			self.favorabilidadJuridicaVO.solicitud_id(datos.id);
			self.favorabilidadJuridicaVO.observacion(datos.juridico.observacion);
			self.favorabilidadJuridicaVO.sb_soporte(datos.juridico.sb_soporte);
			// self.favorabilidadJuridicaVO.soporte(datos.juridico.soporte);

			if(datos.juridico.sb_soporte != 1){
				$('#archivo_juridico').attr('disabled','disabled');
				$('#archivo_juridico_d .file-input-new .kv-fileinput-caption').attr('disabled','disabled');
				$('#archivo_juridico_d .file-caption-main .input-group-btn .btn-file').attr('disabled','disabled');
			}else{
				$('#archivo_juridico').removeAttr('disabled');
				$('#archivo_juridico_d .file-input-new .kv-fileinput-caption').removeAttr('disabled');
				$('#archivo_juridico_d .file-caption-main .input-group-btn .btn-file').removeAttr('disabled');
			}
			self.soporteJuridico(datos.juridico.soporte);

			// COMPRAS
			self.limpiar_compras();
			self.lista_compras(datos.compras.requisito);

			self.favorabilidadComprasVO.id(datos.compras.id);
			self.favorabilidadComprasVO.solicitud_id(datos.id);
			self.favorabilidadComprasVO.observacion(datos.compras.observacion);
			self.favorabilidadComprasVO.sb_soporte(datos.compras.sb_soporte);
			self.favorabilidadComprasVO.soporte(datos.compras.soporte);

			if(datos.compras.sb_soporte != 1){
				$('#archivo_compras').attr('disabled','disabled');
				$('#archivo_compras_d .file-input-new .kv-fileinput-caption').attr('disabled','disabled');
				$('#archivo_compras_d .file-caption-main .input-group-btn .btn-file').attr('disabled','disabled');
			}else{
				$('#archivo_compras').removeAttr('disabled');
				$('#archivo_compras_d .file-input-new .kv-fileinput-caption').removeAttr('disabled');
				$('#archivo_compras_d .file-caption-main .input-group-btn .btn-file').removeAttr('disabled');
			}
			self.soporteCompras(datos.compras.soporte);

			// TECNICA
			self.limpiar_tecnica();
			self.lista_tecnica(datos.tecnica.requisito);

			self.favorabilidadTecnicaVO.id(datos.tecnica.id);
			self.favorabilidadTecnicaVO.solicitud_id(datos.id);
			self.favorabilidadTecnicaVO.observacion(datos.tecnica.observacion);
			self.favorabilidadTecnicaVO.sb_soporte(datos.tecnica.sb_soporte);
			self.favorabilidadTecnicaVO.soporte(datos.tecnica.soporte);

			if(datos.tecnica.sb_soporte != 1){
				$('#archivo_tecnico').attr('disabled','disabled');
				$('#archivo_tecnico_d .file-input-new .kv-fileinput-caption').attr('disabled','disabled');
				$('#archivo_tecnico_d .file-caption-main .input-group-btn .btn-file').attr('disabled','disabled');
			}else{
				$('#archivo_tecnico').removeAttr('disabled');
				$('#archivo_tecnico_d .file-input-new .kv-fileinput-caption').removeAttr('disabled');
				$('#archivo_tecnico_d .file-caption-main .input-group-btn .btn-file').removeAttr('disabled');
			}
			self.soporteTecnico(datos.tecnica.soporte);

			// POLIZA
			self.lista_poliza(datos.poliza.tipo_poliza);
			self.soportePoliza(datos.poliza.soporte);

			self.validarPolizaVO.id(datos.poliza.id);
			self.validarPolizaVO.solicitud_id(datos.id);
			self.validarPolizaVO.sb_soporte(datos.poliza.sb_soporte);
			self.validarPolizaVO.soporte(datos.poliza.soporte);
		}, path, parameter);
	}

	// Para buscar los requisitoa de la poliza
	self.consultarRequisitosPoliza = function(obj){
		$('#detalle_tipo_poliza').modal('show');

		self.mensaje_tipo_poliza("Tipo de Poliza: "+obj.tipo__nombre);
		self.lista_requisito_poliza(obj.requisito);
		$('#guardar_requisito_poliza').show();

		$('.riquisito_poliza').removeAttr('disabled','disabled');
	}
	// Para buscar los requisitoa de la poliza para el detalle
	self.consultarRequisitosPolizaDetalle = function(obj){
		$('#guardar_requisito_poliza').hide();

		self.mensaje_tipo_poliza("Tipo de Poliza: "+obj.tipo__nombre);
		self.lista_requisito_poliza(obj.requisito);
		$('#detalle_tipo_poliza').modal('show');

		$('.riquisito_poliza').attr('disabled','disabled');
	}

	// Buscar si el id fue compensados
	/*self.buscarId = function myFunction(listaC, id) {
		var r = listaC.indexOf(id);
		if (r >= 0){
			return true;
		}else{
			return false;
		}
	}*/

	// Eliminar la solicitud
	self.eliminar = function () {
		var lista_id=[];
		var count=0;
		ko.utils.arrayForEach(self.listado(), function(d) {

			if(d.eliminado()==true){
				count=1;
				lista_id.push({
					id:d.id
				})
			}
		});
		//console.log("asas:"+lista_id[0].id+" - "+lista_id[1].id);

		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una solicitud para la eliminacion.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});

		}else{
			var path =path_principal+'/solicitud/eliminar_solicitud/';
			var parameter = { lista: lista_id};
			RequestAnularOEliminar("Esta seguro que desea eliminar las solicitudes seleccionadas?", path, parameter, function () {
				self.consultar(self.paginacion.pagina_actual());
				self.checkall(false);
			})
		}
	}

	self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado(), function(d) {

			d.eliminado(value);
		});
	});

	//exportar excel
	self.exportar_excel=function(){
		// self.filtro($('#txtBuscar').val());
		// location.href=path_principal+"/factura/excel_descuento?dato="+self.filtro()+
		// 																							 "&referencia="+self.filtro_descuento.referencia()+
		// 																					"&numero_contrato="+self.filtro_descuento.num_contrato()+
		// 																								 "&concepto="+self.filtro_descuento.concepto();
	}
}
var solicitud = new SolicitudViewModel();
SolicitudViewModel.errores_solicitud = ko.validation.group(solicitud.solicitudVO);
SolicitudViewModel.errores_bus_contrato = ko.validation.group(solicitud.buscar_contrato);

$('#txtBuscar').val(sessionStorage.getItem("sol_cto_filtro"));

if(sessionStorage.getItem("sol_cto_estado") != null ){
    solicitud.filtro_solicitud.estado(sessionStorage.getItem("sol_cto_estado"));
}
if(sessionStorage.getItem("sol_cto_tipo") != null ){
    solicitud.filtro_solicitud.tipo(sessionStorage.getItem("sol_cto_tipo"));
}
if(sessionStorage.getItem("sol_cto_contratista") != null ){
    solicitud.filtro_solicitud.contratista(sessionStorage.getItem("sol_cto_contratista"));
}
if(sessionStorage.getItem("sol_cto_contratista_nom") != null ){
    solicitud.filtro_solicitud.contratista_nom(sessionStorage.getItem("sol_cto_contratista_nom"));
}
if(sessionStorage.getItem("sol_cto_contratista_lista") != null ){
    solicitud.filtro_solicitud.contratista_lista(agregarOpcionesObservable(sessionStorage.getItem("sol_cto_contratista_lista")));
}
if(sessionStorage.getItem("sol_cto_desde") != null ){
    solicitud.filtro_solicitud.desde(sessionStorage.getItem("sol_cto_desde"));
}
if(sessionStorage.getItem("sol_cto_hasta") != null ){
    solicitud.filtro_solicitud.hasta(sessionStorage.getItem("sol_cto_hasta"));
}

solicitud.consultar(1);//iniciamos la primera funcion

ko.applyBindings(solicitud);