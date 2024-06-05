function CesionViewModel(){
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

	self.listado_cesion_c=ko.observableArray([]);

	self.listado_nombre_giro=ko.observableArray([]);
	self.listado_tipo_cuenta=ko.observableArray([]);
	self.dysplay_giro=ko.observable(false);
	self.dysplay_giro_checkbox=ko.observable(false);
	self.checkall_giro=ko.observable(false);
	self.mensaje_guardar=ko.observable('');

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

	self.cesionVO={
		id:ko.observable(0),
		referencia:ko.observable(''),
		contrato_id:ko.observable().extend({ required: { message: '(*)Seleccione un contrato' } }),
		beneficiario_id:ko.observable().extend({ required: { message: '(*)Seleccione un beneficiario' } }),
		banco_id:ko.observable('0').extend({ required: { message: '(*)Seleccione el banco de la cuenta' } }),
		proceso_soporte_id:ko.observable(''),
		numero_cuenta:ko.observable(''),
		tipo_cuenta_id:ko.observable('0').extend({ required: { message: '(*)Seleccione un tipo de cuenta' } }),
		descripcion:ko.observable('').extend({ required: { message: '(*)Digite la descripcion de la cesión' } }),
		fecha:ko.observable('').extend({ required: { message: '(*)Seleccione una fecha' } }),
		valor:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor de la factura' } }),
		nombre_giro:ko.observable(0).extend({ required: { message: '(*)Indique el nombre del giro para aplicar la cesión' } }),
		checkall_giro:ko.observable(),
		soporte:ko.observable('')//.extend({ required: { message: '(*)Debe seleccionar el archivo soporte de la cesión' } })
	}

	self.filtro_cesion={
		num_contrato:ko.observable(''),
		nom_beneficiario:ko.observable(''),
		beneficiario:ko.observable(),
		tipo:ko.observable('esContratista'),
		beneficiario_lista:ko.observableArray([]),
		referencia:ko.observable(''),
		desde:ko.observable(''),
		hasta:ko.observable('')
	}

	self.detalle={
		id: ko.observable(''),
		referencia:ko.observable(''),
		num_contrato:ko.observable(''),
		beneficiario:ko.observable(''),
		banco:ko.observable(''),
		numero_cuenta:ko.observable(''),
		descripcion:ko.observable(''),
		fecha:ko.observable(''),
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
		self.titulo('Registrar una Autorización de Giro');
		$('#modal_acciones').modal('show');

		self.dysplay_giro_checkbox(true);
	}
	self.abrir_modal_contrato = function () {
		$('#modal_contrato').modal('show');
	}
	self.abrir_modal_beneficiario = function () {
		$('#modal_beneficiario').modal('show');
	}
	self.abrir_filtro = function () {
		$('#modal_filtro').modal('show');
	}

	//limpiar el modelo
	self.limpiar=function(){
		self.cesionVO.id(0);
		self.cesionVO.referencia('');
		self.cesionVO.contrato_id(0);
		self.cesionVO.beneficiario_id(0);
		self.cesionVO.banco_id('');
		self.cesionVO.numero_cuenta('');
		self.cesionVO.tipo_cuenta_id('');
		self.cesionVO.descripcion('');
		self.cesionVO.fecha('');
		self.cesionVO.valor(0);
		self.cesionVO.nombre_giro(0);
		self.cesionVO.checkall_giro(false);
		self.cesionVO.soporte('');
		self.nombre_contrato('');
		self.nombre_beneficiario('');
		$('#archivo').fileinput('reset');
		$('#archivo').val('');

		self.mensaje_guardar('');

		self.cesionVO.fecha.isModified(false);
		self.cesionVO.descripcion.isModified(false);
		self.cesionVO.banco_id.isModified(false);
		self.cesionVO.tipo_cuenta_id.isModified(false);
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
		self.filtro_cesion.num_contrato('');
		self.filtro_cesion.nom_beneficiario('');
		self.filtro_cesion.beneficiario('');
		self.filtro_cesion.tipo('esContratista');
		self.filtro_cesion.beneficiario_lista([]);
		self.filtro_cesion.referencia('');
		self.filtro_cesion.desde('');
		self.filtro_cesion.hasta('');
	}

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.consultar(1);
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}
	self.consulta_enter_beneficiario = function (d,e) {
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
	}
	self.consulta_enter_contrato = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.buscarContrato(1);
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}

	//Buscar Contrato
	self.buscarContrato=function(pagina){

		parameter={id_tipo:self.buscar_contrato.tipo_contrato(),
									// dato:self.buscar_contrato.nom_num_contrato(),
									dato:$('#nom_num_contrato').val(),
									lite:1,
									page: pagina};
		path =path_principal+'/api/Contrato/?format=json';

		if (CesionViewModel.errores_bus_contrato().length == 0){ //se activa las validaciones
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
			CesionViewModel.errores_bus_contrato.showAllMessages();
		}
	}

	// Buscar el Beneficiario
	self.buscarBeneficiario=function(pagina){

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
			cerrarLoading();
		}, path, parameter,function(){},false);
	}

	// Buscar el Beneficiario para el filtro
	self.buscarBeneficiarioFiltro=function(){

		// console.log("nom_nit:"+self.filtro_cesion.nit_nom());
		// console.log("tipo:"+self.filtro_cesion.tipo());
		self.filtro_cesion.nom_beneficiario($("#nom_beneficiario").val());

		parameter={dato:self.filtro_cesion.nom_beneficiario()
							 // esProveedor:1
							// esContratista:1
							};
		path =path_principal+'/api/empresa/?sin_paginacion&'+self.filtro_cesion.tipo()+'=1&format=json';

		RequestGet(function (results,success) {
			if (success == 'ok' && results.length > 0) {
				//self.mensaje_beneficiario('');
				self.filtro_cesion.beneficiario_lista(results);
			}else {
				self.filtro_cesion.beneficiario_lista([]);
				//self.mensaje_beneficiario(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}

			// console.log("success:"+success);
		}, path, parameter,function(){self.filtro_cesion.beneficiario(sessionStorage.getItem("fac_cs_beneficiario"));},true);
	}

	// Buscar Nombre de giro
	self.buscarNombreGiro=function(mcontrato, nombre){

		// console.log("nom_nit:"+self.buscar_beneficiario.nit_nom());
		// console.log("tipo:"+self.buscar_beneficiario.tipo());
		// self.buscar_beneficiario.nit_nom($("#nit_nom").val());

		parameter={contrato:mcontrato };
		path =path_principal+'/api/Nombre_giro/?sin_paginacion&format=json';

		RequestGet(function (results,success) {
			if (success == 'ok' && results.length > 0) {
				self.mensaje_guardar('');
				self.listado_nombre_giro(results);
				self.dysplay_giro_checkbox(true);
			}else {
				self.listado_nombre_giro([]);
				self.mensaje_guardar('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i> No se encontraron nombres de giro, para este MContrato: '+nombre+' </div>');
				self.dysplay_giro_checkbox(false);
				self.dysplay_giro(false);
			}

			// console.log("success:"+success);
		}, path, parameter,function(){});
	}

	//consultar los tipos para llenar un select
	self.consultar_lista_tipo=function(){

		path =path_principal+'/api/Tipos?ignorePagination';
		parameter={ aplicacion: 'cuenta' };
		RequestGet(function (datos, estado, mensaje) {

			self.listado_tipo_cuenta(datos);

		}, path, parameter,undefined,false,false);
	}

	self.ponerContrato = function (obj) {

		//alert(obj.id); return false;
		
		//self.cesionVO.contrato_id(obj.id);
		self.nombre_contrato(obj.nombre);
		if(obj.mcontrato){
			self.dysplay_giro_checkbox(true);
			self.dysplay_giro(false);
			self.buscarNombreGiro(obj.mcontrato.id, obj.mcontrato.nombre);
		}else{
			self.dysplay_giro_checkbox(false);
			self.dysplay_giro(false);
			self.mensaje_guardar('<div class="alert alert-info alert-dismissable"><i class="fa fa-info-circle"></i> El Contrato '+obj.nombre+', no tiene un M-Contrato asignado. </div>');
		}

		$('#modal_contrato').modal('hide');
		return true;
	}
	self.ponerBeneficiario = function (obj) {

		//alert(obj.id); return false;
		
		// self.cesionVO.beneficiario_id(obj.id);
		self.nombre_beneficiario(obj.nombre);
		$('#modal_beneficiario').modal('hide');
		return true;
	}

	self.guardar=function(){
		//console.log('g_m:'+self.cesionVO.meses());

		if (CesionViewModel.errores_cesion().length == 0){ //se activa las validaciones

			// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
			if(self.cesionVO.id()==0){
				var soporte = true;
				if($('#archivo')[0].files.length==0){
					// self.cesionVO.soporte('');
					soporte = false;
				}
				//console.log("val:"+self.cesionVO.valor());

				//Validamos que la cesion beneficie solo a ENERGIA Y CONTROLES o VEGA ENERGY
				if ((self.cesionVO.beneficiario_id()== 39) || (self.cesionVO.beneficiario_id()== 7)){
					if(soporte){
						if ((self.cesionVO.nombre_giro()!=0) && (self.cesionVO.nombre_giro()!='')){					
							if (self.cesionVO.valor() != '' || self.cesionVO.valor() == '0'){
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
									url:path_principal+'/api/FecturaCesion/',//url api
									parametros:self.cesionVO
								};
								//parameter =ko.toJSON(self.cesionVO);
								//Request(parametros);
								RequestFormData(parametros);
							}else{
								mensajeInformativo('Debe ingresar el valor de la cesión.','Información');
							}
						}else{
							mensajeInformativo('Debe especificar el giro donde se espera aplicar la cesión.','Información');	
						}
            
					}else{
						mensajeInformativo('Debe cargar el archivo soporte de la cesión.','Información');
					}
				}else{
					mensajeInformativo('No tiene permisos para crear autorizaciones de giro \
					con beneficiarios diferentes a VEGA ENERGY y ENERGIA Y CONTROLES.','Información');	
				}
			}else{
				var soporte = true;
				if($('#archivo')[0].files.length==0){
					self.cesionVO.soporte('');
					soporte = false;
				}
				//console.log("val:"+self.cesionVO.valor());
				if(self.cesionVO.valor() != '' || self.cesionVO.valor() == '0'){
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
						url:path_principal+'/api/FecturaCesion/'+self.cesionVO.id()+'/',
						parametros:self.cesionVO                        
					};
					RequestFormData(parametros);
				}else{
					mensajeInformativo('Falta por ingresar un valor.','Información');
				}
			}
		} else {
			CesionViewModel.errores_cesion.showAllMessages();
		}
	}

	// Consultar cesion
	self.consultar = function (pagina) {
		if (pagina > 0) {
			self.filtro($('#txtBuscar').val());
			// alert("qwqw:"+self.filtro_cesion.beneficiario());
			// alert("qwqw:"+sessionStorage.getItem("fac_cs_beneficiario"));

			sessionStorage.setItem("fac_cs_filtro_cesion",self.filtro() || '');
			sessionStorage.setItem("fac_cs_nom_beneficiario",self.filtro_cesion.nom_beneficiario() || '');
			sessionStorage.setItem("fac_cs_beneficiario_lista",self.filtro_cesion.beneficiario_lista() || []);
			sessionStorage.setItem("fac_cs_beneficiario",self.filtro_cesion.beneficiario() || '');
			sessionStorage.setItem("fac_cs_tipo_contratista",self.filtro_cesion.tipo() || '');
			sessionStorage.setItem("fac_cs_referencia",self.filtro_cesion.referencia() || '');
			sessionStorage.setItem("fac_cs_num_contrato",self.filtro_cesion.num_contrato() || '');
			sessionStorage.setItem("fac_cs_desde",self.filtro_cesion.desde() || '');
			sessionStorage.setItem("fac_cs_hasta",self.filtro_cesion.hasta() || '');

			path = path_principal+'/api/FecturaCesion/?format=json';
			parameter = {dato: self.filtro(),
									referencia: self.filtro_cesion.referencia(),
									id_beneficiario: self.filtro_cesion.beneficiario(),
									numero_contrato: self.filtro_cesion.num_contrato(),
									fecha_desde: self.filtro_cesion.desde(),
									fecha_hasta: self.filtro_cesion.hasta(),
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
				self.llenar_paginacion2(datos,pagina);
				$('#modal_filtro').modal('hide');
				cerrarLoading();
			}, path, parameter,function(){
				self.buscarBeneficiarioFiltro();
			}, true);
		}
	}

	// Buscar los registrar compensados
	self.buscarRegistrosCompensados=function(){

		parameter2={//id_contrato:self.cruceVO.contrato_id(),
								id_tablaForanea:self.tablaForanea.cesion()};
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

				self.listado_cesion_c(agregarOpcionesObservable(lista_ids));
			} else {
				//console.log("Nooo");
				self.listado_cesion_c([]);
			}
		}, path2, parameter2, function(){
			self.consultar(1);
		},false);
	}

	// Para editar
	self.consultar_por_id = function (obj) {

		path =path_principal+'/api/FecturaCesion/'+obj.id+'/?format=json';
		parameter = {};
		self.limpiar();
		self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar Autorización de Giro');

			self.cesionVO.id(datos.id);
			self.cesionVO.referencia(datos.referencia);
			self.cesionVO.contrato_id(datos.contrato.id);
			self.nombre_contrato(datos.contrato.nombre);
			self.cesionVO.beneficiario_id(datos.beneficiario.id);
			self.nombre_beneficiario(datos.beneficiario.nombre);
			if(datos.banco != null){
				self.cesionVO.banco_id(datos.banco.id);
			}
			if(datos.proceso_soporte){
				self.cesionVO.proceso_soporte_id(datos.proceso_soporte.id);
			}
			if(datos.tipo_cuenta){
				self.cesionVO.tipo_cuenta_id(datos.tipo_cuenta.id);
			}
			self.cesionVO.numero_cuenta(datos.numero_cuenta);
			self.cesionVO.descripcion(datos.descripcion);
			self.cesionVO.fecha(datos.fecha);
			self.cesionVO.valor(datos.valor);

			self.cesionVO.soporte(datos.soporte);
			self.soporte(datos.soporte);
			//self.habilitar_campos(true);
			$('#modal_acciones').modal('show');

			self.dysplay_giro_checkbox(false);

			cerrarLoading();
		}, path, parameter,function(){},false);
	}

	// Para var el detalle de la cesion
	self.consultar_por_id_detalle = function (obj) {

		path =path_principal+'/api/FecturaCesion/'+obj.id+'/?format=json';
		parameter = {};
		// self.limpiar();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.detalle.id(datos.id);
			self.detalle.referencia(datos.referencia);
			self.detalle.num_contrato(datos.contrato.numero);
			//self.nombre_contrato(datos.contrato.nombre);
			self.detalle.beneficiario(datos.beneficiario.nombre);
			if(datos.banco != null){
				self.detalle.banco(datos.banco.nombre);
			}
			self.detalle.numero_cuenta(datos.numero_cuenta);
			self.detalle.descripcion(datos.descripcion);
			self.detalle.fecha(datos.fecha);
			self.detalle.valor(datos.valor);
			self.detalle.soporte(datos.soporte);

			$('#detalle_cesion').modal('show');

			// mes causado
			// str_meses = '';
			// ko.utils.arrayForEach(datos.mes_causado, function(d) {

			// 	if(str_meses != ''){str_meses = str_meses+', '}

			// 	str_meses = str_meses+d.mes+'-'+d.ano;
			// });
			// str_meses = String(str_meses);
			// //console.log("detalle_meses:"+str_meses);
			// self.detalle.meses(str_meses);
		}, path, parameter);
	}

	// Buscar si el id fue compensados
	self.buscarId = function myFunction(id) {
		//var fruits = ["Banana", "Orange", "Apple", "Mango"];
		var r = self.listado_cesion_c().indexOf(id);
		if (r >= 0){
			return true;
		}else{
			return false;
		}
	}

	// Eliminar la cesion
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
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una Autorización de Giro para su eliminación.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});

		}else{
			var path =path_principal+'/factura/eliminar_cesion/';
			var parameter = { lista: lista_id};
			RequestAnularOEliminar("Esta seguro que desea eliminar las Autorización de Giro seleccionadas?", path, parameter, function () {
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

	// PONER NOMBRE DE GIROS
	self.cesionVO.checkall_giro.subscribe(function(value ){

		// ko.utils.arrayForEach(self.listado(), function(d) {
		if(value == true){
			self.dysplay_giro(true);
			// self.cesionVO.checkall_giro(true);
		}else{
			self.dysplay_giro(false);
			self.cesionVO.nombre_giro(0);
			// self.cesionVO.checkall_giro(false);
		}
		// d.eliminado(value);
		// });
	});

	//exportar excel
	self.exportar_excel=function(){
		self.filtro($('#txtBuscar').val());
		location.href=path_principal+"/factura/excel_cesion?dato="+self.filtro()+
																								"&referencia="+self.filtro_cesion.referencia()+
																					 "&id_beneficiario="+self.filtro_cesion.beneficiario()+
																					 "&numero_contrato="+self.filtro_cesion.num_contrato()+
																							 "&fecha_desde="+self.filtro_cesion.desde()+
																							 "&fecha_hasta="+self.filtro_cesion.hasta();
	}
}
var cesion = new CesionViewModel();
CesionViewModel.errores_cesion = ko.validation.group(cesion.cesionVO);
CesionViewModel.errores_bus_contrato = ko.validation.group(cesion.buscar_contrato);
// alert("1:"+sessionStorage.getItem("fac_cs_beneficiario"));

$('#txtBuscar').val(sessionStorage.getItem("fac_cs_filtro_cesion"));
cesion.filtro_cesion.nom_beneficiario(sessionStorage.getItem("fac_cs_nom_beneficiario"));
// cesion.filtro_cesion.beneficiario_lista(sessionStorage.getItem("fac_cs_beneficiario_lista") || []);
cesion.filtro_cesion.beneficiario(sessionStorage.getItem("fac_cs_beneficiario"));
cesion.filtro_cesion.tipo(sessionStorage.getItem("fac_cs_tipo_contratista"));
cesion.filtro_cesion.referencia(sessionStorage.getItem("fac_cs_referencia"));
cesion.filtro_cesion.num_contrato(sessionStorage.getItem("fac_cs_num_contrato"));
cesion.filtro_cesion.desde(sessionStorage.getItem("fac_cs_desde"));
cesion.filtro_cesion.hasta(sessionStorage.getItem("fac_cs_hasta"));

// alert("2:"+cesion.filtro_cesion.beneficiario());

cesion.buscarRegistrosCompensados();//iniciamos la primera funcion
cesion.consultar_lista_tipo();
ko.applyBindings(cesion);
