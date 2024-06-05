function CruceViewModel(){
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);

	self.checkall_anticipo=ko.observable(false);
	self.checkall_factura=ko.observable(false);
	self.checkall_cesion=ko.observable(false);
	self.checkall_descuento=ko.observable(false);
	self.checkall_multa=ko.observable(false);

	self.mensaje_cont=ko.observable('');//mensaje para el modal de contrato
	self.lista_contrato=ko.observableArray([]);
	self.info_contrato=ko.observable('');

	self.mensaje_anticipo=ko.observable('');
	self.listado_anticipo=ko.observableArray([]);
	self.listado_detalla_anticipo=ko.observableArray([]);
	self.mensaje_factura=ko.observable('');
	self.listado_factura=ko.observableArray([]);
	self.mensaje_cesion=ko.observable('');
	self.listado_cesion=ko.observableArray([]);
	self.mensaje_descuento=ko.observable('');
	self.listado_descuento=ko.observableArray([]);
	self.mensaje_multa=ko.observable('');
	self.listado_multa=ko.observableArray([]);

	self.listado_confirmacion_anticipo=ko.observableArray([]);
	self.listado_confirmacion_factura=ko.observableArray([]);
	self.listado_confirmacion_cesion=ko.observableArray([]);
	self.listado_confirmacion_descuento=ko.observableArray([]);
	self.listado_confirmacion_multa=ko.observableArray([]);
	
	self.listado_anticipo_c=ko.observableArray([]);
	self.listado_factura_c=ko.observableArray([]);
	self.listado_cesion_c=ko.observableArray([]);
	self.listado_descuento_c=ko.observableArray([]);
	self.listado_multa_c=ko.observableArray([]);

	self.nombre_contrato=ko.observable('');
	self.valor_total=ko.observable(0);
	self.mensaje_valor=ko.observable('');
	self.visible_table=ko.observable(false);
	self.visible_listado=ko.observable(true);

	// Local
	/*self.tablaForanea={
		encabezadoGiros:ko.observable(20),
		factura:ko.observable(1086),
		cesion:ko.observable(1088),
		descuento:ko.observable(1089)
	};*/
	// Maquina Virtual
	self.tablaForanea={
		encabezadoGiros:ko.observable(38),
		factura:ko.observable(140),
		cesion:ko.observable(142),
		descuento:ko.observable(143),
		multa:ko.observable(161)
	};

	self.buscar_contrato={
		tipo_contrato:ko.observable('').extend({ required: { message: '(*)Seleccione un tipo' } }),
		nom_num_contrato:ko.observable('')//.extend({ required: { message: '(*)Digite nombre o número del contrato' } })
	}

	self.cruceVO={
		id:ko.observable(0),
		referencia:ko.observable(''),
		contrato_id:ko.observable().extend({ required: { message: '(*)Seleccione un contrato' } }),
		fecha:ko.observable('').extend({ required: { message: '(*)Seleccione una fecha' } }),
		descripcion:ko.observable(''),
		valor:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor del cruce' } }),
		ids_anticipo:ko.observable(''),
		ids_factura:ko.observable(''),
		ids_cesion:ko.observable(''),
		ids_descuento:ko.observable(''),
		ids_multa:ko.observable('')
	}

	self.detalleCompensacionVO={
		id:ko.observable(0),
		compensacion_id:ko.observable(),
		tablaForanea_id:ko.observable(),
		id_registro:ko.observable()
	}

	/*self.filtro_cruce={
		num_contrato:ko.observable(''),
		referencia:ko.observable(''),
		concepto:ko.observable('')
	}*/

	self.detalle={
		referencia:ko.observable(''),
		num_contrato:ko.observable(''),
		fecha:ko.observable(''),
		descripcion:ko.observable(''),
		valor:ko.observable(''),
		giro:ko.observableArray(''),
		factura:ko.observableArray(''),
		cesion:ko.observableArray(''),
		descuento:ko.observableArray(''),
		multa:ko.observableArray('')
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

	// Inicio de Modal
	self.abrir_modal = function () {
		self.limpiar_contrato();
		//self.titulo('Registrar un Cruce');
		$('#modal_contrato').modal('show');
	}
	self.abrir_filtro = function () {
		$('#modal_filtro').modal('show');
	}
	// Fin de Modal

	//limpiar el modelo de cruce
	self.limpiar=function(){
		self.cruceVO.id(0);
		self.cruceVO.referencia('');
		self.cruceVO.contrato_id(0);
		self.cruceVO.fecha('');
		self.cruceVO.descripcion('');
		self.cruceVO.valor(0);
		self.nombre_contrato('');

		self.cruceVO.ids_anticipo('');
		self.cruceVO.ids_factura('');
		self.cruceVO.ids_cesion('');
		self.cruceVO.ids_descuento('');
		self.cruceVO.ids_multa('');

		self.cruceVO.fecha.isModified(false);
	}

	//limpiar el modelo de detalle cruce
	self.limpiar_detalle_cruce=function(){
		self.detalleCompensacionVO.id(0);
		self.detalleCompensacionVO.compensacion_id(0);
		self.detalleCompensacionVO.tablaForanea_id(0);
		self.detalleCompensacionVO.id_registro(0);
	}
	//limpiar el filtro de contrato
	self.limpiar_contrato=function(){
		self.buscar_contrato.tipo_contrato('');
		self.buscar_contrato.nom_num_contrato('');
		self.mensaje_cont('');
		//self.lista_contrato([]);

		self.buscar_contrato.tipo_contrato.isModified(false);
	}
	//limpiar el detalle del cruce
	self.limpiar_detalle=function(){
		self.detalle.referencia('');
		self.detalle.num_contrato('');
		self.detalle.fecha('');
		self.detalle.descripcion('');
		self.detalle.valor(0);
	}

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.consultar(1);
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}

	//Buscar Contrato
	self.buscarContrato=function(pagina){

		parameter={id_tipo:self.buscar_contrato.tipo_contrato(),
									dato:self.buscar_contrato.nom_num_contrato(),
									lite:1,
									page: pagina};
		path =path_principal+'/api/Contrato/?format=json';

		if (CruceViewModel.errores_bus_contrato().length == 0){ //se activa las validaciones
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
			}, path, parameter, function(){cerrarLoading();},false);
		} else {
			CruceViewModel.errores_bus_contrato.showAllMessages();
		}
	}

	self.ponerContrato = function (obj) {

		var mcontrato = '';
		
		// self.cruceVO.contrato_id(obj.id);
		self.nombre_contrato(obj.nombre);
		//self.habilitar_campos(true);
		$('#modal_contrato').modal('hide');
		self.visible_table(true);
		self.visible_listado(false);

		if (obj.mcontrato != null){
			mcontrato = obj.mcontrato.nombre;
		}

		self.info_contrato("<b>Contrato</b>: "+obj.nombre+ ", <b>N°</b>: "+obj.numero+", <b>MContrato:</b> "+mcontrato );

		self.buscarAnticipo(obj.id);
		return true;
	}

	//Buscar Anticipo
	self.buscarAnticipo=function(id_contra){

		// Buscar los registrar compensados
		parameter2={id_contrato:id_contra,
		// parameter2={id_contrato:self.cruceVO.contrato_id(),
					id_tablaForanea:self.tablaForanea.encabezadoGiros()};
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

				self.listado_anticipo_c(agregarOpcionesObservable(lista_ids));
			} else {
				console.log("Nooo");
				self.listado_anticipo_c([]);
			}
		}, path2, parameter2, function(){
			parameter={};
			path =path_principal+'/factura/list_anticipo/?format=json&id_contrato='+self.cruceVO.contrato_id();

			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos!=null && datos.length > 0) {
					
					//console.log(datos);

					self.mensaje_anticipo('');
					self.listado_anticipo(agregarOpcionesObservable(datos));
					//self.listado_detalla_anticipo(agregarOpcionesObservable(lista_detalle));
				} else {
					self.listado_anticipo([]);
					self.mensaje_anticipo(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				}
			}, path, parameter, function(){ self.buscarFactura();	},false);
		},false);
	}

	//Buscar Facturas
	self.buscarFactura=function(){

		// Buscar los registrar compensados
		parameter2={id_contrato:self.cruceVO.contrato_id(),
							 id_tablaForanea:self.tablaForanea.factura()};
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

				self.listado_factura_c(agregarOpcionesObservable(lista_ids));
			} else {
				console.log("Nooo");
				self.listado_factura_c([]);
			}
		}, path2, parameter2, function(){

			parameter={id_contrato:self.cruceVO.contrato_id(),
								 valor_cont:0};
			path =path_principal+'/api/Factura/?format=json&sin_paginacion';

			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos!=null && datos.length > 0) {
					self.mensaje_factura('');
					self.listado_factura(agregarOpcionesObservable(datos));
				} else {
					self.listado_factura([]);
					self.mensaje_factura(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				}
			}, path, parameter, function(){ self.buscarCesion(); },false);
		},false);
	}

	//Buscar Cesion
	self.buscarCesion=function(){

		// Buscar los registrar compensados
		parameter2={id_contrato:self.cruceVO.contrato_id(),
							 id_tablaForanea:self.tablaForanea.cesion()};
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

				self.listado_cesion_c(agregarOpcionesObservable(lista_ids));
			} else {
				console.log("Nooo");
				self.listado_cesion_c([]);
			}
		}, path2, parameter2, function(){

			parameter={id_contrato:self.cruceVO.contrato_id()};
			path =path_principal+'/api/FecturaCesion/?format=json&sin_paginacion';

			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos!=null && datos.length > 0) {
					self.mensaje_cesion('');
					self.listado_cesion(agregarOpcionesObservable(datos));
				} else {
					self.listado_cesion([]);
					self.mensaje_cesion(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				}
			}, path, parameter, function(){ self.buscarDescuento(); },false);
		},false);
	}

	//Buscar Descuento
	self.buscarDescuento=function(){

		// Buscar los registrar compensados
		parameter2={id_contrato:self.cruceVO.contrato_id(),
							 id_tablaForanea:self.tablaForanea.descuento()};
		path2 =path_principal+'/api/FacturaDetalleCompensacion/?format=json&sin_paginacion';

		RequestGet(function (datos, estado, mensage) {

			if (estado == 'ok' && datos!=null && datos.length > 0) {
				
				// console.log(datos);

				var lista_ids=[];
				ko.utils.arrayForEach(datos, function(d) {

					lista_ids.push(
						d.id_registro
					);
				});
				// console.log("ids:"+lista_ids);

				self.listado_descuento_c(agregarOpcionesObservable(lista_ids));
			} else {
				// console.log("Nooo");
				self.listado_descuento_c([]);
			}
		}, path2, parameter2, function(){

			parameter={id_contrato:self.cruceVO.contrato_id()};
			path =path_principal+'/api/FacturaDescuento/?format=json&sin_paginacion';

			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos!=null && datos.length > 0) {
					self.mensaje_descuento('');
					self.listado_descuento(agregarOpcionesObservable(datos));
				} else {
					self.listado_descuento([]);
					self.mensaje_descuento(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				}
			}, path, parameter, function(){self.buscarMulta();},false);
		},false);
	}

	//Buscar Multa
	self.buscarMulta=function(){

		// Buscar los registrar compensados
		parameter2={id_contrato:self.cruceVO.contrato_id(),
					id_tablaForanea:self.tablaForanea.multa()};
		path2 =path_principal+'/api/FacturaDetalleCompensacion/?format=json&sin_paginacion';

		RequestGet(function (datos, estado, mensage) {

			if (estado == 'ok' && datos!=null && datos.length > 0) {

				// console.log(datos);

				var lista_ids=[];
				ko.utils.arrayForEach(datos, function(d) {

					lista_ids.push(
						d.id_registro
					);
				});
				// console.log("ids:"+lista_ids);

				self.listado_multa_c(agregarOpcionesObservable(lista_ids));
			} else {
				// console.log("Nooo");
				self.listado_multa_c([]);
			}
		}, path2, parameter2, function(){

			parameter={contrato_id:self.cruceVO.contrato_id()};
			path =path_principal+'/api/MultaSolicitudEmpresa/?format=json&ignorePagination&estado=78&solicitudes_elaboradas=&solicitudes_solicitadas=&solicitudes_consulta=';
			// path =path_principal+'/api/MultaSolicitud/?format=json&ignorePagination';

			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos!=null && datos.length > 0) {
					self.mensaje_multa('');
					self.listado_multa(agregarOpcionesObservable(datos));
				} else {
					self.listado_multa([]);
					self.mensaje_multa(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				}
			}, path, parameter, function(){cerrarLoading();},false);
		},false);
	}

	//Buscar Confirmación de Cruce
	self.confirmarCruce=function(){

		$('#modal_confirmar_cruce').modal('show');

		// Buscar anticipos seleccionados
		var lista_anticipo=[];
		var count_anticipo=0;
		var total_anticipo=0;
		var ids_anticipo='';
		ko.utils.arrayForEach(self.listado_anticipo(), function(d) {

			if(d.eliminado()==true){
				count=1;
				lista_anticipo.push({
					id:d.id,
					tipo:'Anticipo',
					referencia:d.nombre,
					valor:d.valor
				})
				total_anticipo = total_anticipo + d.valor

				// concadenar los ids
				if(ids_anticipo != ''){
					ids_anticipo = ids_anticipo + ',';
				}
				ids_anticipo = ids_anticipo + d.id;
				self.cruceVO.ids_anticipo(ids_anticipo);
			}
		});
		self.listado_confirmacion_anticipo(agregarOpcionesObservable(lista_anticipo));

		// Buscar facturas seleccionadas
		var lista_factura=[];
		var count_factura=0;
		var total_factura=0;
		var ids_factura='';
		ko.utils.arrayForEach(self.listado_factura(), function(d) {

			if(d.eliminado()==true){
				count=1;
				lista_factura.push({
					id:d.id,
					tipo:'Factura',
					referencia:d.referencia,
					valor:d.valor_contable
				})
				total_factura = total_factura + d.valor_contable

				// concadenar los ids
				if(ids_factura != ''){
					ids_factura = ids_factura + ',';
				}
				ids_factura = ids_factura + d.id;
				self.cruceVO.ids_factura(ids_factura);
			}
		});
		self.listado_confirmacion_factura(agregarOpcionesObservable(lista_factura));

		// Buscar cesiones seleccionadas
		var lista_cesion=[];
		var count_cesion=0;
		var total_cesion=0;
		var ids_cesion=0;
		ko.utils.arrayForEach(self.listado_cesion(), function(d) {

			if(d.eliminado()==true){
				count=1;
				lista_cesion.push({
					id:d.id,
					tipo:'Autorización de Giro',
					referencia:d.referencia,
					valor:d.valor
				})
				total_cesion = total_cesion + d.valor

				// concadenar los ids
				if(ids_cesion != ''){
					ids_cesion = ids_cesion + ',';
				}
				ids_cesion = ids_cesion + d.id;
				self.cruceVO.ids_cesion(ids_cesion);
			}
		});
		self.listado_confirmacion_cesion(agregarOpcionesObservable(lista_cesion));

		// Buscar Descuentos seleccionadod
		var lista_descuento=[];
		var count_descuento=0;
		var total_descuento=0;
		var ids_descuento=0;
		ko.utils.arrayForEach(self.listado_descuento(), function(d) {

			if(d.eliminado()==true){
				count_descuento=1;
				lista_descuento.push({
					id:d.id,
					tipo:'Descuento',
					referencia:d.referencia,
					valor:d.valor
				})
				total_descuento = total_descuento + d.valor

				// concadenar los ids
				if(ids_descuento != ''){
					ids_descuento = ids_descuento + ',';
				}
				ids_descuento = ids_descuento + d.id;
				self.cruceVO.ids_descuento(ids_descuento);
			}
		});
		self.listado_confirmacion_descuento(agregarOpcionesObservable(lista_descuento));

		// Buscar Multas seleccionadas
		var lista_multa=[];
		var count_multa=0;
		var total_multa=0;
		var ids_multa='';
		ko.utils.arrayForEach(self.listado_multa(), function(d) {

			if(d.eliminado()==true){
				count_multa=1;
				lista_multa.push({
					id:d.id,
					tipo:'Multa',
					referencia:d.codigoReferencia,
					valor:d.valorImpuesto
				})
				total_multa = total_multa + d.valorImpuesto

				// concadenar los ids
				if(ids_multa != ''){
					ids_multa = ids_multa + ',';
				}
				ids_multa = ids_multa + d.id;
				self.cruceVO.ids_multa(ids_multa);
			}
		});
		self.listado_confirmacion_multa(agregarOpcionesObservable(lista_multa));

		// Sumaoria
		// TOTAL DE (-)
		var total_n = total_factura;
		
		// TOTAL DE (+)
		var total_p = total_anticipo + total_cesion +  total_descuento + total_multa;
		
		var total = total_p - total_n;
		self.valor_total(total);
		self.cruceVO.valor(total);

		// Mensaje del valor total
		if(total < 0){
			self.mensaje_valor('Se está creado un saldo a favor del contratista, esta seguro que desea continuar?');
		}else if(total > 0){
			self.mensaje_valor('Se está creado un saldo en contra del contratista, esta seguro que desea continuar?');
		}else{
			self.mensaje_valor('No hay saldo pendiente, esta seguro que desea continuar?');
		}
	}

	self.guardar=function(){
		//console.log('g_m:'+self.cruceVO.meses());
		if (CruceViewModel.errores_cruce().length == 0){ //se activa las validaciones

			// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
			if(self.cruceVO.id()==0){

				// console.log("val:"+self.cruceVO.valor());
				// if((self.cruceVO.valor() != 0) && (self.cruceVO.valor() != '')){
				// if(self.cruceVO.valor() != ''){
					var parametros={
						callback:function(datos, estado, mensaje){

							if (estado=='ok') {

								$('#modal_confirmar_cruce, #modal_guardar_cruce').modal('hide');
								self.limpiar();
								self.limpiar_detalle_cruce();
								self.visible_table(false);
								self.visible_listado(true);

								self.listado_confirmacion_anticipo([]);
								self.listado_confirmacion_factura([]);
								self.listado_confirmacion_cesion([]);
								self.listado_confirmacion_descuento([]);
								self.listado_confirmacion_multa([]);

								self.consultar(1);
							}else{
								mensajeError(mensaje);
							}
						}, //funcion para recibir la respuesta 
						url:path_principal+'/api/FacturaCompensacion/',//url api
						parametros:self.cruceVO
					};
					//parameter =ko.toJSON(self.cruceVO);
					//Request(parametros);
					RequestFormData(parametros);
				// }else{
				// 	mensajeInformativo('Falta por ingresar un valor.','Información');
				// }
			}else{

				if((self.cruceVO.valor() != 0) && (self.cruceVO.valor() != '')){
					var parametros={
						metodo:'PUT',
						callback:function(datos, estado, mensaje){

							if (estado=='ok') {
								self.filtro("");
								//self.consultar(self.paginacion.pagina_actual());
								//$('#modal_acciones').modal('hide');
								self.limpiar();
								self.limpiar_contrato();
							}

						},//funcion para recibir la respuesta 
						url:path_principal+'/api/FacturaCompensacion/'+self.cruceVO.id()+'/',
						parametros:self.cruceVO                        
					};
					RequestFormData(parametros);
				}else{
					mensajeInformativo('Falta por ingresar un valor.','Información');
				}
			}
		} else {
			CruceViewModel.errores_cruce.showAllMessages();
		}
	}

	// Consultar cruce
	self.consultar = function (pagina) {
		if (pagina > 0) {
			self.filtro($('#txtBuscar').val());

			path = path_principal+'/api/FacturaCompensacion/?format=json';
			parameter = {dato: self.filtro(),
									// referencia: self.filtro_cruce.referencia(),
									// numero_contrato: self.filtro_cruce.num_contrato(),
									// concepto: self.filtro_cruce.concepto(),
									page: pagina };
			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
					self.mensaje('');
					//self.listado(results);
					self.listado(agregarOpcionesObservable(datos.data));

				} else {
					self.listado([]);
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

	self.cancelarCruce = function () {
		self.visible_table(false);
		self.visible_listado(true);
		self.info_contrato("");
	}

	// Eliminar Cruce
	self.eliminar = function(obj){
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
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un registro para eliminarlo.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});

		}else{
			var path =path_principal+'/factura/eliminar_cruce/';
			var parameter = { lista: lista_id};
			RequestAnularOEliminar("Esta seguro que desea eliminar el registro seleccionado?", path, parameter, function () {
				self.consultar(self.paginacion.pagina_actual());
				self.checkall(false);
			})
		}
	}

	// Para editar
	/*self.consultar_por_id = function (obj) {

		path =path_principal+'/api/FacturaCruce/'+obj.id+'/?format=json';
		parameter = {};
		self.limpiar();
		self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar cruce');

			self.cruceVO.id(datos.id);
			self.cruceVO.referencia(datos.referencia);
			self.cruceVO.contrato_id(datos.contrato.id);
			self.nombre_contrato(datos.contrato.nombre);
			self.cruceVO.banco_id(datos.banco.id);
			self.cruceVO.numero_cuenta(datos.numero_cuenta);
			self.cruceVO.concepto(datos.concepto);
			self.cruceVO.valor(datos.valor);

			self.cruceVO.soporte(datos.soporte);
			self.soporte(datos.soporte);

			$('#modal_acciones').modal('show');
		}, path, parameter);
	}*/

	// Para var el detalle del cruce
	self.consultar_por_id_detalle = function (obj) {

		path =path_principal+'/api/FacturaCompensacion/'+obj.id+'/?format=json&lite_detalle=1';
		parameter = {};
		self.limpiar_detalle();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.detalle.referencia(datos.referencia);
			self.detalle.num_contrato(datos.contrato.numero);
			self.detalle.fecha(datos.fecha);
			self.detalle.descripcion(datos.descripcion);
			self.detalle.valor(datos.valor);
			self.detalle.giro(datos.giro);
			self.detalle.factura(datos.factura);
			self.detalle.cesion(datos.cesion);
			self.detalle.descuento(datos.descuento);
			self.detalle.multa(datos.multa);

			$('#detalle_cruce').modal('show');
		}, path, parameter);
	}

	self.checkall_anticipo.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado_anticipo(), function(d) {

			if(self.listado_anticipo_c().indexOf(d.id) < 0){
				d.eliminado(value);
			}
		});
	});
	self.checkall_factura.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado_factura(), function(d) {

			if(self.listado_factura_c().indexOf(d.id) < 0){
				d.eliminado(value);
			}
		});
	});
	self.checkall_cesion.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado_cesion(), function(d) {

			if(self.listado_cesion_c().indexOf(d.id) < 0){
				d.eliminado(value);
			}
		});
	});
	self.checkall_descuento.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado_descuento(), function(d) {

			if(self.listado_descuento_c().indexOf(d.id) < 0){
				d.eliminado(value);
			}
		});
	});
	self.checkall_multa.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado_multa(), function(d) {

			d.eliminado(value);
		});
	});
	self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado(), function(d) {

			d.eliminado(value);
		});
	});

	//exportar excel
	self.exportar_excel=function(){
		self.filtro($('#txtBuscar').val());
		location.href=path_principal+"/factura/excel_cruce?dato="+self.filtro();
	}

	//exportar excel
	self.reporteCruce=function(obj){
		self.filtro($('#txtBuscar').val());
		location.href=path_principal+"/factura/excel_cruce2?dato="+obj.id;
	}
}
var cruce = new CruceViewModel();

CruceViewModel.errores_cruce = ko.validation.group(cruce.cruceVO);
CruceViewModel.errores_bus_contrato = ko.validation.group(cruce.buscar_contrato);

cruce.consultar(1);//iniciamos la primera funcion

ko.applyBindings(cruce);