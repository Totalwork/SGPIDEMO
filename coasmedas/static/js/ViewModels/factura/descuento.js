function DescuentoViewModel(){
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	self.num_registro=ko.observable('');

	self.mensaje_cont=ko.observable('');//mensaje para el modal de contrato
	self.lista_contrato=ko.observableArray([]);
	self.mensaje_beneficiario=ko.observable('');//mensaje para el modal de beneficiario
	self.lista_beneficiario=ko.observableArray([]);

	self.nombre_contrato=ko.observable('');
	self.nombre_beneficiario=ko.observable('');
	self.soporte=ko.observable('');
	self.listado_descuento_c=ko.observableArray([]);

	self.buscar_contrato={
		tipo_contrato:ko.observable('').extend({ required: { message: '(*)Seleccione un tipo' } }),
		nom_num_contrato:ko.observable('')//.extend({ required: { message: '(*)Digite nombre o número del contrato' } })
	}
	self.buscar_beneficiario={
		nit_nom:ko.observable('').extend({ required: { message: '(*)Digite un nombre o nit' } }),
		tipo:ko.observable('esContratista')//.extend({ required: { message: '(*)Digite nombre o número del contrato' } })
	}

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
		descuento:ko.observable(143)
	};

	self.descuentoVO={
		id:ko.observable(0),
		referencia:ko.observable(''),
		contrato_id:ko.observable().extend({ required: { message: '(*)Seleccione un contrato' } }),
		banco_id:ko.observable(''),
		numero_cuenta:ko.observable(''),
		concepto:ko.observable('').extend({ required: { message: '(*)Digite el concepto del descuento' } }),
		valor:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor del descuento' } }),
		soporte:ko.observable('')
	}

	self.filtro_descuento={
		num_contrato:ko.observable(''),
		referencia:ko.observable(''),
		concepto:ko.observable('')
	}

	self.detalle={
		referencia:ko.observable(''),
		num_contrato:ko.observable(''),
		banco:ko.observable(''),
		numero_cuenta:ko.observable(''),
		concepto:ko.observable(''),
		valor:ko.observable(''),
		soporte:ko.observable('')
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
		self.titulo('Registrar un Descuento');
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
		self.descuentoVO.id(0);
		self.descuentoVO.referencia('');
		self.descuentoVO.contrato_id(0);
		self.descuentoVO.banco_id(0);
		self.descuentoVO.numero_cuenta('');
		self.descuentoVO.concepto('');
		self.descuentoVO.valor(0);
		self.descuentoVO.soporte('');
		self.nombre_contrato('');
		self.nombre_beneficiario('');
		$('#archivo').fileinput('reset');
		$('#archivo').val('');
	}
	//limpiar el filtro de contrato
	self.limpiar_contrato=function(){
		self.buscar_contrato.tipo_contrato('');
		self.buscar_contrato.nom_num_contrato('');
		self.mensaje_cont('');
		self.lista_contrato([]);
	}
	// Limpiar filtro
	self.limpiar_filtro=function(){
		self.filtro_descuento.num_contrato(''),
		self.filtro_descuento.referencia(''),
		self.filtro_descuento.concepto('')
	}

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.consultar(1);
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
									page: pagina};
		path =path_principal+'/api/Contrato/?format=json';

		if (DescuentoViewModel.errores_bus_contrato().length == 0){ //se activa las validaciones
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
			DescuentoViewModel.errores_bus_contrato.showAllMessages();
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
		
		// self.descuentoVO.contrato_id(obj.id);
		self.nombre_contrato(obj.nombre);
		//self.habilitar_campos(true);
		$('#modal_contrato').modal('hide');
		return true;
	}
	/*self.ponerBeneficiario = function (obj) {

		//alert(obj.id); return false;
		
		self.descuentoVO.beneficiario_id(obj.id);
		self.nombre_beneficiario(obj.nombre);
		$('#modal_beneficiario').modal('hide');
	}*/

	self.guardar=function(){
		//console.log('g_m:'+self.descuentoVO.meses());
		if (DescuentoViewModel.errores_descuento().length == 0){ //se activa las validaciones

			// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
			if(self.descuentoVO.id()==0){

				var soporte = true;
				if($('#archivo')[0].files.length==0){
					// self.cesionVO.soporte('');
					soporte = false;
				}

				if(soporte){
					if((self.descuentoVO.valor() != 0) && (self.descuentoVO.valor() != '')){
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
							url:path_principal+'/api/FacturaDescuento/',//url api
							parametros:self.descuentoVO
						};
						//parameter =ko.toJSON(self.descuentoVO);
						//Request(parametros);
						RequestFormData(parametros);
					}else{
						mensajeInformativo('Falta por ingresar un valor.','Información');
					}
				}else{
					mensajeInformativo('Falta por seleccionar el soporte.','Información');
				}
			}else{

				if($('#archivo')[0].files.length==0){
					self.descuentoVO.soporte('');
				}
				console.log("val:"+self.descuentoVO.valor());
				if((self.descuentoVO.valor() != 0) && (self.descuentoVO.valor() != '')){
					var parametros={
						metodo:'PUT',
						callback:function(datos, estado, mensaje){

							if (estado=='ok') {
								self.filtro("");
								self.consultar(self.paginacion.pagina_actual());
								$('#modal_acciones').modal('hide');
								self.limpiar();
								self.limpiar_contrato();
							}

						},//funcion para recibir la respuesta 
						url:path_principal+'/api/FacturaDescuento/'+self.descuentoVO.id()+'/',
						parametros:self.descuentoVO                        
					};
					RequestFormData(parametros);
				}else{
					mensajeInformativo('Falta por ingresar un valor.','Información');
				}
			}
		} else {
			DescuentoViewModel.errores_descuento.showAllMessages();
		}
	}

	// Consultar descuento
	self.consultar = function (pagina) {
		if (pagina > 0) {
			self.filtro($('#txtBuscar').val());

			sessionStorage.setItem("fac_dec_filtro",self.filtro() || '');
			sessionStorage.setItem("fac_dec_num_contrato",self.filtro_descuento.num_contrato() || '');
			sessionStorage.setItem("fac_dec_referencia",self.filtro_descuento.referencia() || '');
			sessionStorage.setItem("fac_dec_concepto",self.filtro_descuento.concepto() || '');

			path = path_principal+'/api/FacturaDescuento/?format=json';
			parameter = {dato: self.filtro(),
									referencia: self.filtro_descuento.referencia(),
									numero_contrato: self.filtro_descuento.num_contrato(),
									concepto: self.filtro_descuento.concepto(),
									page: pagina };
			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
					self.mensaje('');
					self.num_registro("- N° de Registos: "+datos.count);
					self.listado(agregarOpcionesObservable(datos.data));

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
	self.buscarRegistrosCompensados=function(){

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
	}

	// Para editar
	self.consultar_por_id = function (obj) {

		path =path_principal+'/api/FacturaDescuento/'+obj.id+'/?format=json';
		parameter = {};
		self.limpiar();
		self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar Descuento');

			self.descuentoVO.id(datos.id);
			self.descuentoVO.referencia(datos.referencia);
			self.descuentoVO.contrato_id(datos.contrato.id);
			self.nombre_contrato(datos.contrato.nombre);
			self.descuentoVO.banco_id(datos.banco.id);
			self.descuentoVO.numero_cuenta(datos.numero_cuenta);
			self.descuentoVO.concepto(datos.concepto);
			self.descuentoVO.valor(datos.valor);

			self.descuentoVO.soporte(datos.soporte);
			self.soporte(datos.soporte);

			$('#modal_acciones').modal('show');
		}, path, parameter);
	}

	// Para var el detalle del descuento
	self.consultar_por_id_detalle = function (obj) {

		path =path_principal+'/api/FacturaDescuento/'+obj.id+'/?format=json';
		parameter = {};
		// self.limpiar();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.detalle.referencia(datos.referencia);
			self.detalle.num_contrato(datos.contrato.numero);
			//self.nombre_contrato(datos.contrato.nombre);
			self.detalle.banco(datos.banco.nombre);
			self.detalle.numero_cuenta(datos.numero_cuenta);
			self.detalle.concepto(datos.concepto);
			self.detalle.valor(datos.valor);
			self.detalle.soporte(datos.soporte);

			$('#detalle_descuento').modal('show');
		}, path, parameter);
	}

	// Buscar si el id fue compensados
	self.buscarId = function myFunction(listaC, id) {
		var r = listaC.indexOf(id);
		if (r >= 0){
			return true;
		}else{
			return false;
		}
	}

	// Eliminar la descuento
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
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un descuento para la eliminacion.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});

		}else{
			var path =path_principal+'/factura/eliminar_descuento/';
			var parameter = { lista: lista_id};
			RequestAnularOEliminar("Esta seguro que desea eliminar los descuentos seleccionados?", path, parameter, function () {
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
		self.filtro($('#txtBuscar').val());
		location.href=path_principal+"/factura/excel_descuento/?dato="+self.filtro()+
													   "&referencia="+self.filtro_descuento.referencia()+
												  "&numero_contrato="+self.filtro_descuento.num_contrato()+
														 "&concepto="+self.filtro_descuento.concepto();
	}
}
var descuento = new DescuentoViewModel();
DescuentoViewModel.errores_descuento = ko.validation.group(descuento.descuentoVO);
DescuentoViewModel.errores_bus_contrato = ko.validation.group(descuento.buscar_contrato);

$('#txtBuscar').val(sessionStorage.getItem("fac_dec_filtro"));
descuento.filtro_descuento.num_contrato(sessionStorage.getItem("fac_dec_num_contrato"));
descuento.filtro_descuento.referencia(sessionStorage.getItem("fac_dec_referencia"));
descuento.filtro_descuento.concepto(sessionStorage.getItem("fac_dec_concepto"));

descuento.buscarRegistrosCompensados();//iniciamos la primera funcion

ko.applyBindings(descuento);