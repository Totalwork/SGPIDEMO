function FacturaViewModel(){
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.num_registro=ko.observable('');
	self.checkall=ko.observable(false);
	self.checkall_factura=ko.observable(false);
	self.id_factura=ko.observable('');

	//self.listado_empresa_contratista=ko.observableArray([]);

	// self.lista_sub_contratista=ko.observableArray([]);
	self.mensaje_cont=ko.observable('');//mensaje para el modal de contrato
	self.lista_contrato=ko.observableArray([]);
	self.lista_mcontrato=ko.observableArray([]);

	self.lista_factura_proyecto=ko.observableArray([]);
	self.mensaje_factura_proyecto=ko.observable('');

	self.nombre=ko.observable('');
	self.mc_nombre=ko.observable('');
	self.meses=ko.observable('');
	self.soporte=ko.observable('');
	self.ano=ko.observable();
	self.mes_causado_array=ko.observableArray([]);

	self.mensaje_nueva_factura=ko.observable('');
	self.lista_proyecto=ko.observableArray([]);

	// self.dysplay_giro_checkbox=ko.observable(false);
	// self.checkall_giro=ko.observable(false);

	// Local
	/*self.estado={
		activa:ko.observable(2002),
		anulada:ko.observable(2003),
		compensada:ko.observable(2004)
	};*/
	// Maquina Virtual
	self.estado={
		activa:ko.observable(52),
		anulada:ko.observable(53),
		compensada:ko.observable(54)
	};

	self.tipoContrato={
		contratoProyecto:ko.observable(8),
		interventoria:ko.observable(9),
		medida:ko.observable(10),
		retie:ko.observable(11),
		m_contrato:ko.observable(12),
		suministros:ko.observable(13),
		obra:ko.observable(14),
		otros:ko.observable(15)
	};

	self.buscar_contrato={
		tipo_contrato:ko.observable(''),
		nom_num_contrato:ko.observable('')//.extend({ required: { message: '(*)Digite nombre o número del contrato' } })
	}

	self.buscar_mcontrato={
		tipo_contrato:ko.observable(''),
		nom_num_contrato:ko.observable('')//.extend({ required: { message: '(*)Digite nombre o número del contrato' } })
	}

	self.buscar_platilla={
		mcontrato:ko.observable('').extend({ required: { message: '(*)Seleccione el M-Contrato.' } }),
		soporte:ko.observable('')//.extend({ required: { message: '(*)Digite nombre o número del contrato' } })
	}

	self.facturaVO={
		id:ko.observable(0),
		referencia:ko.observable(''),
		contrato_id:ko.observable().extend({ required: { message: '(*)Seleccione un contrato' } }),
		estado_id:ko.observable(0),
		numero:ko.observable('').extend({ required: { message: '(*)Digite el numero de la factura' } }),
		fecha:ko.observable('').extend({ required: { message: '(*)Seleccione una fecha' } }),
		concepto:ko.observable('').extend({ required: { message: '(*)Digite el concepto de la factura' } }),
		valor_factura:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor de la factura' } }),
		valor_contable:ko.observable(0).money(),
		valor_subtotal:ko.observable(0),
		soporte:ko.observable(''),
		meses:ko.observable(''),
		ano:ko.observable(''),
		codigo_op_id:ko.observable(''),
		proyecto:ko.observableArray([]),
		mes_causado:ko.observableArray([]),
		factura_final:ko.observable(),
		recursos_propios:ko.observable(),
		fecha_pago:ko.observable(''),
		motivo_anulacion:ko.observable(''),
		radicado:ko.observable(''),
		mcontrato_id:ko.observable()
	}

	self.filtro_factura={
		mcontrato:ko.observable(''),
		tipo:ko.observable(''),
		contratista_lista:ko.observableArray([]),
		contratista_nom:ko.observable(''),
		contratista:ko.observable(),
		numero_c:ko.observable(''),
		referencia:ko.observable(''),
		desde:ko.observable(''),
		hasta:ko.observable(''),
		numero_f:ko.observable(''),
		radicado:ko.observable('')
	}

	self.detalle={
		referencia:ko.observable(''),
		numero:ko.observable(''),
		contrato_num:ko.observable(''),
		estado:ko.observable(''),
		fecha:ko.observable(''),
		concepto:ko.observable(''),
		valor_factura:ko.observable(''),
		valor_contable:ko.observable(''),
		valor_subtotal:ko.observable(''),
		radicado:ko.observable(''),
		soporte:ko.observable(''),
		meses:ko.observable('')
	}

	self.fac_proy={
		ref_factura:ko.observable(''),
		num_factura:ko.observable(''),
		num_contrato:ko.observable(''),
		nom_proyecto:ko.observable(''),
		valor:ko.observable('')
	}

	self.mes_causado={
		id:ko.observable(0),
		mes:ko.observable('').extend({ required: { message: '(*)Seleccione un mes.' } }),
		ano:ko.observable('').extend({ required: { message: '(*)Ingrese el año.' } })
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

	self.paginacion3 = {
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
	self.paginacion3.pagina_actual.subscribe(function (pagina) {
		self.buscarContrato(pagina);
	});

	//Funcion para crear la paginacion
	self.llenar_paginacion3 = function (data,pagina) {
		self.paginacion3.pagina_actual(pagina);
		self.paginacion3.total(data.count);
		self.paginacion3.cantidad_por_paginas(resultadosPorPagina);
	}
	// Fin de Paginacion

	self.abrir_modal = function () {
		self.limpiar();
		self.titulo('Registrar una Factura');
		//alert(self.buscar_contrato.tipo_contrato());
		if((self.buscar_contrato.tipo_contrato()==12) || (self.buscar_contrato.tipo_contrato()=='')){
			$("#validacionMcontrato").hide();
		}else{
			$("#validacionMcontrato").show();
		}
		$('#modal_acciones').modal('show');
	}
	self.abrir_modal_contrato = function () {
		$('#modal_contrato').modal('show');
	}
	self.abrir_modal_Mcontrato = function () {
		$('#modal_Mcontrato').modal('show');
	}
	self.abrir_filtro = function () {

		$('#modal_filtro').modal('show');
	}
	self.abrir_proyecto_factura = function () {
		$('#modal_proyecto_factura').modal('show');
	}


	//funcion para abri el mnodal de pagar la factura
    self.pagar_factura = function () {
        self.titulo('Pagar Factura');
        self.limpiar();
        $('#modal_pagar_factura').modal('show');
    }


    self.anular_facturas = function (obj) {

    	self.id_factura(obj.id);
    	self.titulo('Anular Factura');
    	self.limpiar();
		$('#modal_anular').modal('show');
	}

	//limpiar el modelo
	self.limpiar=function(){
		self.facturaVO.id(0);
		self.facturaVO.referencia('');
		self.facturaVO.contrato_id(0);
		self.facturaVO.mcontrato_id('');
		self.facturaVO.estado_id(0);
		self.facturaVO.numero('');
		self.facturaVO.fecha('');
		self.facturaVO.concepto('');
		self.facturaVO.valor_factura(0);
		self.facturaVO.valor_contable(0);
		self.facturaVO.valor_subtotal(0);
		self.facturaVO.soporte('');
		self.facturaVO.meses('');
		self.facturaVO.ano('');
		self.facturaVO.mes_causado([]);
		self.facturaVO.fecha_pago('');
		self.facturaVO.motivo_anulacion('');
		self.facturaVO.radicado('');
		self.facturaVO.recursos_propios(false);
		self.nombre('');
		self.mc_nombre('');
		self.mes_causado_array([]);
		self.lista_proyecto([]);
		$('#multiselect').multiselect('clearSelection');
		$('#archivo').fileinput('reset');
		$('#archivo').val('');

		self.facturaVO.numero.isModified(false);
		self.facturaVO.fecha.isModified(false);
		self.facturaVO.concepto.isModified(false);
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
		self.filtro_factura.tipo('');
		self.filtro_factura.contratista_lista([]);
		self.filtro_factura.contratista_nom('');
		self.filtro_factura.contratista('');
		self.filtro_factura.numero_c('');
		self.filtro_factura.referencia('');
		self.filtro_factura.desde('');
		self.filtro_factura.hasta('');
		self.filtro_factura.numero_f('');
		self.filtro_factura.radicado('');
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

	/*self.list_sub_contratista2=function(){
		path =path_principal+'/api/Cesion_economica/?id_contrato='+self.contrato_id();

		// var nom_nit = $('#nom_nit2').val();
		// if(nom_nit){
		// 	parameter = {dato:nom_nit};
		// }else{
		// 	parameter = {dato:""};
		// }
		parameter={};

		RequestGet(function (results,success,message) {
			
			if (success == 'ok' && results.data!=null && results.data.length > 0) {
				self.mensaje('');
				self.lista_sub_contratista2(agregarOpcionesObservable(results.data));
			} else {
				self.lista_sub_contratista2([]);
				self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				//self.mensaje2('No se encontraron registros');
			}
			//self.llenar_paginacion(datos,pagina);
		}, path, parameter);
	}*/

	//consultar contratista y contratante selects
	/*self.empresa=function(dato){
		parameter='';
		path =path_principal+'/api/empresa/?sin_paginacion&'+dato+'=1&format=json';

		RequestGet(function (results,count) {

			if(dato == 'esContratista'){
				self.listado_empresa_contratista(results);

			}else if(dato == 'esContratante'){
				self.listado_empresa_contratante(results);
			}
		}, path, parameter);
	}*/

	//Buscar Contrato
	self.buscarContrato=function(pagina){

		parameter={id_tipo:self.buscar_contrato.tipo_contrato(),
									dato:self.buscar_contrato.nom_num_contrato(),
									lite:3,
									page: pagina};
		path =path_principal+'/api/Contrato/?format=json';

		if (FacturaViewModel.errores_bus_contrato().length == 0){ //se activa las validaciones
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
				//console.log("f_i:"+self.lista_contrato());
			}, path, parameter, function(){cerrarLoading();},false);
		} else {
			FacturaViewModel.errores_bus_contrato.showAllMessages();
		}
	}

	//Buscar Macro Contrato
	self.buscarMContrato=function(pagina){

		parameter={id_tipo:self.buscar_mcontrato.tipo_contrato(),
					dato:self.buscar_mcontrato.nom_num_contrato(),
					lite:3,
					page: pagina};
		path =path_principal+'/api/Contrato/?format=json';

		if (FacturaViewModel.errores_bus_Mcontrato().length == 0){ //se activa las validaciones
			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
					self.mensaje_cont('');
					self.lista_mcontrato(agregarOpcionesObservable(datos.data));
				} else {
					self.lista_mcontrato([]);
					self.mensaje_cont(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				}
				if(datos.count > 10){
					self.llenar_paginacion3(datos,pagina);
					$('#paginacion3').show();
				}else{
					$('#paginacion3').hide();
				}
				//console.log("f_i:"+self.lista_mcontrato());
			}, path, parameter, function(){cerrarLoading();},false);
		} else {
			FacturaViewModel.errores_bus_Mcontrato.showAllMessages();
		}
	}

	self.ponerContrato = function (obj) {
		if(self.buscar_contrato.tipo_contrato()==12){
			$("#validacionMcontrato").hide();
		}else{
			$("#validacionMcontrato").show();
		}
		// $('#idcontrato'+obj.id).
		$("#validacionContrato").hide();
		//self.facturaVO.contrato_id(obj.id);
		self.nombre(obj.nombre);
		//self.habilitar_campos(true);
		$('#modal_contrato').modal('hide');
		self.buscarProyecto(obj.id);
		self.consultar_contrato(obj.id);
		return true;
	}

	self.ponerMContrato = function (obj) {

		//self.facturaVO.mcontrato_id(obj.id);
		self.mc_nombre(obj.nombre);
		$('#modal_Mcontrato').modal('hide');
		// self.buscarProyecto(obj.id);
		return true;
	}

	//Buscar Proyectos del contrato
	self.buscarProyecto=function(id_contrato){

		parameter={contrato_obra:id_contrato,
									ignorePagination: 0};
		path =path_principal+'/api/Proyecto/?format=json&lite=1';

		RequestGet(function (datos, estado, mensage) {

			if (estado == 'ok' && datos!=null && datos.length > 0) {
				self.mensaje_nueva_factura('');
				self.lista_proyecto(agregarOpcionesObservable(datos));
			} else {
				self.lista_proyecto([]);
				self.mensaje_nueva_factura(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}
			//console.log("f_i:"+self.lista_contrato());
		}, path, parameter, function(){cerrarLoading();},false);
	}

	// Para buscar contrato por id
	self.consultar_contrato = function (id) {

		path =path_principal+'/api/Contrato/'+id+'/?lite_editar=1&format=json';
		parameter = {};
		RequestGet(function (results,success) {

			if(results.tipo_contrato.id != self.tipoContrato.m_contrato()){ //&& (results.tipo_contrato.id != self.tipoContrato.otros())

				if(results.mcontrato){
					self.facturaVO.mcontrato_id(results.mcontrato.id);
					self.mc_nombre(results.mcontrato.nombre);
				}else{
					self.facturaVO.mcontrato_id('');
					self.mc_nombre('');
				}
			}
		}, path, parameter);
	}

	// Agregar Mes causado
	self.agregarMesCausado=function(){

		if (FacturaViewModel.errores_mes_causado().length==0) {

			self.mes_causado_array.push({
				id:0,
				mes:self.mes_causado.mes(),
				ano:self.mes_causado.ano()
			});

			self.mes_causado.mes(0);
			self.mes_causado.ano('');
			self.mes_causado.ano.isModified(false);
			self.mes_causado.mes.isModified(false);
		}else{
			FacturaViewModel.errores_mes_causado.showAllMessages();
		}
	}

	self.removerMesCausado=function(obj) { 
		self.mes_causado_array.remove(obj);
	}

	self.guardar=function(){
		//console.log('g_m:'+self.facturaVO.meses());
		if ((FacturaViewModel.errores_factura().length == 0) && (self.facturaVO.contrato_id()!=0) && (self.facturaVO.contrato_id()!='')){ //se activa las validaciones

			// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
			if(self.facturaVO.id()==0){

				if((self.facturaVO.meses() == '' && self.facturaVO.ano() == '') || (self.facturaVO.meses() != '' && self.facturaVO.ano() != '')){
					
					// VALIDAR SOPORTE
					var soporte = true;
					if($('#archivo')[0].files.length==0){
						// self.cesionVO.soporte('');
						soporte = false;
					}

					// Validar valor contable
					var val_contable = true;
					if((self.facturaVO.valor_contable() != '') && (self.facturaVO.valor_contable() >= self.facturaVO.valor_factura())){
						val_contable = false;
					}

					// Guardar Proyectos
					var lista_id=[];
					var count=0;
					ko.utils.arrayForEach(self.lista_proyecto(), function(d) {

						if(d.eliminado()==true){
							count=1;
							lista_id.push([d.id])
							/*if(lista_id == ''){
								lista_id = lista_id+d.id;
								}else{
									lista_id = lista_id+','+d.id;
								}*/
						}
					});

					//console.log("val:"+self.cesionVO.valor());
					// if(count != 0){
						self.facturaVO.proyecto(lista_id);

						// Guardar Mes causado
						var lista_mes_causado=[];
						var count2=0;
						ko.utils.arrayForEach(self.mes_causado_array(), function(d) {

								count2=1;
								lista_mes_causado.push({
									id:0,
									mes:d.mes,
									ano:d.ano
								})
						});
						// self.facturaVO.mes_causado([]);
						if(count2 > 0){
							self.facturaVO.mes_causado.push(ko.toJSON(lista_mes_causado));
						}

						if(soporte && val_contable){
							if((self.facturaVO.valor_factura() != 0) && (self.facturaVO.valor_factura() != '')){
								self.facturaVO.estado_id(self.estado.activa());
								var parametros={
									callback:function(datos, estado, mensaje){

										if (estado=='ok') {

											$('#modal_acciones').modal('hide');
											self.limpiar();
											self.limpiar_contrato();
											self.consultar(1);
										}else{
											mensajeError(mensaje);
										}
									}, //funcion para recibir la respuesta 
									url:path_principal+'/api/Factura/',//url api
									parametros:self.facturaVO
								};
								//parameter =ko.toJSON(self.facturaVO);
								//Request(parametros);
								RequestFormData(parametros);
							}else{
								mensajeInformativo('Falta por ingresar el valor de la factura.','Información');
							}
						}else{
							if(!val_contable){
								mensajeInformativo('El valor contabilizado no puede ser mayor que el valor de la factura.','Información');
							}else{
								mensajeInformativo('Falta por seleccionar el soporte.','Información');
							}
						}
					// }else{
					// 	$.confirm({
					// 		title:'Informativo',
					// 		content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un proyecto para guardar la factura.<h4>',
					// 		cancelButton: 'Cerrar',
					// 		confirmButton: false
					// 	});
					// }
				}else{
					mensajeInformativo('Falta por ingresar el mes o el año de causación.','Información');
				}
			}else{

				if($('#archivo')[0].files.length==0){
					self.facturaVO.soporte('');
				}

				// Validar valor contable
				var val_contable = true;
				if((self.facturaVO.valor_contable() != '') && (self.facturaVO.valor_contable() >= self.facturaVO.valor_factura())){
					val_contable = false;
				}

				// Guardar Mes causado
				var lista_mes_causado=[];
				var count2=0;
				ko.utils.arrayForEach(self.mes_causado_array(), function(d) {

						count2=1;
						lista_mes_causado.push({
							id:d.id,
							mes:d.mes,
							ano:d.ano
						})
				});
				self.facturaVO.mes_causado([]);
				if(count2 > 0){
					self.facturaVO.mes_causado.push(ko.toJSON(lista_mes_causado));
				}

				if(val_contable){
					if((self.facturaVO.meses() == '' && self.facturaVO.ano() == '') || (self.facturaVO.meses() != '' && self.facturaVO.ano() != '')){
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
							url:path_principal+'/api/Factura/'+self.facturaVO.id()+'/',
							parametros:self.facturaVO                        
						};
						RequestFormData(parametros);
					}else{
						mensajeInformativo('Falta por ingresar el mes o el año de causación.','Información');
					}
				}else{
					mensajeInformativo('El valor contabilizado no puede ser mayor que el valor de la factura.','Información');
				}
			}

		} else {
			FacturaViewModel.errores_factura.showAllMessages();
		}
	}

	// Consultar factura
	self.consultar = function (pagina) {
		if (pagina > 0) {
			self.filtro($('#txtBuscar').val());

			sessionStorage.setItem("fac_fac_filtro_factura",self.filtro() || '');
			sessionStorage.setItem("fac_fac_mcontrato",self.filtro_factura.mcontrato() || '');
			sessionStorage.setItem("fac_fac_tipo_factura",self.filtro_factura.tipo() || '');
			sessionStorage.setItem("fac_fac_contratista_lista",self.filtro_factura.contratista_lista() || []);
			sessionStorage.setItem("fac_fac_contratista_nom",self.filtro_factura.contratista_nom() || '');
			sessionStorage.setItem("fac_fac_contratista",self.filtro_factura.contratista() || '');
			sessionStorage.setItem("fac_fac_numero_c",self.filtro_factura.numero_c() || '');
			sessionStorage.setItem("fac_fac_referencia",self.filtro_factura.referencia() || '');
			sessionStorage.setItem("fac_fac_numero_f",self.filtro_factura.numero_f() || '');
			sessionStorage.setItem("fac_fac_desde",self.filtro_factura.desde() || '');
			sessionStorage.setItem("fac_fac_hasta",self.filtro_factura.hasta() || '');
			sessionStorage.setItem("fac_fac_radicado",self.filtro_factura.radicado() || '');

			path = path_principal+'/api/Factura/?format=json';
			parameter = {dato: self.filtro(),
									id_mcontrato:self.filtro_factura.mcontrato(),
									tipo_contrato:self.filtro_factura.tipo(),
									id_contratista: self.filtro_factura.contratista(),
									numero_contrato: self.filtro_factura.numero_c(),
									referencia: self.filtro_factura.referencia(),
									numero: self.filtro_factura.numero_f(),
									fecha_desde: self.filtro_factura.desde(),
									fecha_hasta: self.filtro_factura.hasta(),
									radicado: self.filtro_factura.radicado(),
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
				cerrarLoading();
			}, path, parameter, function(){factura.empresa();}, true);
		}
	}

	// Para editar
	self.consultar_por_id = function (obj) {

		path =path_principal+'/api/Factura/'+obj.id+'/?format=json';
		parameter = {};
		self.limpiar();
		self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar Factura');

			self.facturaVO.id(datos.id);
			self.facturaVO.referencia(datos.referencia);
			self.facturaVO.contrato_id(datos.contrato.id);
			self.nombre(datos.contrato.nombre);
			self.facturaVO.estado_id(datos.estado.id);
			self.facturaVO.numero(datos.numero);
			self.facturaVO.fecha(datos.fecha);
			self.facturaVO.concepto(datos.concepto);
			self.facturaVO.valor_factura(datos.valor_factura);
			self.facturaVO.valor_contable(datos.valor_contable);
			self.facturaVO.radicado(datos.radicado);
			self.facturaVO.recursos_propios(datos.recursos_propios);

			if(datos.mcontrato != null){
				self.mc_nombre(datos.mcontrato.nombre);
				self.facturaVO.mcontrato_id(datos.mcontrato.id);
			}

			self.facturaVO.soporte(datos.soporte);
			self.soporte(datos.soporte);
			//self.habilitar_campos(true);
			$('#modal_acciones').modal('show');

			// mes causado
			/*str_meses = '';
			str_ano = '';
			ko.utils.arrayForEach(datos.mes_causado, function(d) {

				if(str_meses != ''){str_meses = str_meses+','}

				str_meses = str_meses+d.mes;
				str_ano		= d.ano;
			});
			str_meses = String(str_meses);
			// console.log("qw:"+str_meses);
			self.facturaVO.meses(str_meses);
			self.facturaVO.ano(str_ano);

			$('#multiselect').multiselect('select', str_meses.split(','), true);*/
			self.mes_causado_array([]);
			ko.utils.arrayForEach(datos.mes_causado, function(d) {

				self.mes_causado_array.push({
					id:d.id,
					mes:d.mes,
					ano:d.ano
				});
			});
		}, path, parameter);
	}

	// Para var el detalle de la factura
	self.consultar_por_id_detalle = function (obj) {

		path =path_principal+'/api/Factura/'+obj.id+'/?format=json';
		parameter = {};
		// self.limpiar();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.detalle.referencia(datos.referencia);
			self.detalle.contrato_num(datos.contrato.numero);
			//self.nombre(datos.contrato.nombre);
			self.detalle.estado(datos.estado.nombre);
			self.detalle.numero(datos.numero);
			self.detalle.fecha(datos.fecha);
			self.detalle.concepto(datos.concepto);
			self.detalle.valor_factura(datos.valor_factura);
			self.detalle.valor_contable(datos.valor_contable);
			self.detalle.valor_contable(datos.valor_contable);
			self.detalle.valor_subtotal(datos.valor_subtotal);
			self.detalle.radicado(datos.radicado);
			self.detalle.soporte(datos.soporte);

			$('#detalle_factura').modal('show');

			// mes causado
			str_meses = '';
			ko.utils.arrayForEach(datos.mes_causado, function(d) {

				if(str_meses != ''){str_meses = str_meses+', '}

				str_meses = str_meses+d.mes+'-'+d.ano;
			});
			str_meses = String(str_meses);
			//console.log("detalle_meses:"+str_meses);
			self.detalle.meses(str_meses);
		}, path, parameter);
	}

	// Buscar el contratista
	self.empresa=function(){
		// parameter={dato:$("#contratista_nom").val() };
		if(self.filtro_factura.contratista_nom() != ''){

			parameter={dato: self.filtro_factura.contratista_nom() };
			path =path_principal+'/api/empresa/?sin_paginacion&esContratista=1&format=json';

			RequestGet(function (results,count) {

				self.filtro_factura.contratista_lista(results);
			}, path, parameter, function(){self.filtro_factura.contratista(sessionStorage.getItem("fac_fac_contratista"));}, true);
		}
	}

	// Cambiar el estado de la factura
	self.anularFactura=function(obj){

		$.confirm({
	        title: 'Confirmar!',
	        content: "<h4>Esta seguro que desea anular la factura?</h4>",
	        confirmButton: 'Si',
	        confirmButtonClass: 'btn-info',
	        cancelButtonClass: 'btn-danger',
	        cancelButton: 'No',
	        confirm: function() {

				parameter={};
				path =path_principal+'/factura/cambiar_estado_factura/?id='+self.id_factura()+'&estado='+self.estado.anulada()+'&motivo='+self.facturaVO.motivo_anulacion();

				RequestGet(function (datos, estado, mensaje) {
					if (estado == 'ok') {

						self.mensaje('');
						self.consultar(self.paginacion.pagina_actual());
						mensajeExitoso(mensaje);
					} else {
						self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
					}
					console.log(estado+":resul:"+mensaje);
				}, path, parameter);
			}
		});
	}

  // Guardar Factura-Proyecto
	self.guardarFacturaProyecto=function(){
		//console.log('g_m:'+self.facturaVO.meses());

		// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
		var soporte = true;
		if($('#plantilla')[0].files.length==0){
			soporte = false;
		}
		if(soporte){
			//console.log("val:"+self.cesionVO.valor());

			var parametros={
				callback:function(datos, estado, mensaje){

					if (estado=='ok') {

						$('#modal_acciones').modal('hide');
						self.limpiar();
						//self.consultar(1);
					}else{
						mensajeError(mensaje);
					}
				}, //funcion para recibir la respuesta 
				url:path_principal+'/factura/guardar_planilla/',//url api
				parametros:self.buscar_platilla
			};
			//parameter =ko.toJSON(self.facturaVO);
			//Request(parametros);
			RequestFormData(parametros);
		}else{
			mensajeInformativo('Falta por seleccionar la planilla.','Información');
		}
	}

	// Consultar las facturaProyecto por factura
	self.consultarFacturaProyecto = function (obj) {

		path =path_principal+'/api/FacturaProyecto/?format=json';
		parameter = {id_factura:obj.id};
		// self.limpiar();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensage) {
			if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
				self.mensaje_factura_proyecto('');

				self.lista_factura_proyecto(agregarOpcionesObservable(datos.data));

			} else {
				self.lista_factura_proyecto([]);
				self.mensaje_factura_proyecto(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}
			// self.fac_proy.ref_factura(datos.factura.referencia);
			// self.fac_proy.num_factura(datos.factura.numero);
			// self.fac_proy.num_contrato(datos.factura.contrato.numero);
			// self.fac_proy.nom_proyecto(datos.proyecto.nombre);
			// self.fac_proy.valor(datos.valor);

			$('#detalle_factura_proyecto').modal('show');

		}, path, parameter);
	}

	// Validar valor contable
	self.validarValorContable = function(){
		alert("asas");
	}

	//exportar excel
	self.exportar_excel=function(){
		self.filtro($('#txtBuscar').val());
		location.href=path_principal+"/factura/excel_factura?dato="+self.filtro()+
																							"&tipo_contrato="+(self.filtro_factura.tipo() || '') +
																						 "&id_contratista="+(self.filtro_factura.contratista() || '')+
																						"&numero_contrato="+(self.filtro_factura.numero_c() || '')+
																								 "&referencia="+ (self.filtro_factura.referencia() || '')+
																										 "&numero="+(self.filtro_factura.numero_f() || '')+
																										"&radicado="+(self.filtro_factura.radicado() || '')+
																								"&fecha_desde="+(self.filtro_factura.desde() || '')+
																								"&fecha_hasta="+(self.filtro_factura.hasta() || '');
	}

	// Descargar la planilla de FacturaProyecto
	self.descargarPlantilla=function(){
		if (FacturaViewModel.errores_facturaProyecto().length == 0){
			location.href=path_principal+"/factura/excel_planilla?mcontrato="+self.buscar_platilla.mcontrato();
		}else{
			FacturaViewModel.errores_facturaProyecto.showAllMessages();
		}
	}

	self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.lista_proyecto(), function(d) {

			d.eliminado(value);
		});
	});


		//check para la vista de factura
	self.checkall_factura.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado(), function(d) {

			d.eliminado(value);
		});
	});

	//guarda los pagos de las facturas
    self.guardar_pago = function () {

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

        if(count==0){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las facturas para guardar el pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false  
        }


        if(self.facturaVO.fecha_pago()==''){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Digite la fecha del pago.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

            return false  
        }


        if(self.facturaVO.fecha_pago()!='' && count>0){

             var path =path_principal+'/factura/pago_factura/';
             var parameter = { lista: lista_id,fecha_pago:self.facturaVO.fecha_pago() };
             RequestAnularOEliminar("Esta seguro que desea guardar los pagos de las facturas seleccionadas?", path, parameter, function () {
                 self.consultar(self.paginacion.pagina_actual());
                 self.checkall_factura(false);
                 $('#modal_pagar_factura').modal('hide');
             })

         } 
    
        
    }//cierra pago factura

	// Factura Recursos Propios
	self.recursos_propios = function () {
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
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una factura para que sea pagada con recursos propios.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});

		}else{
			var path =path_principal+'/factura/recursos_propios/';
			var parameter = { lista: lista_id};
			RequestAnularOEliminar("Esta seguro que desea pagar esta factura seleccionadas con recursos propios?", path, parameter, function () {
				self.consultar(self.paginacion.pagina_actual());
				self.checkall(false);
			})
		}
	}

	 self.ver_soporte = function(obj) {
	  window.open(path_principal+"/factura/ver-soporte/?id="+ obj.id, "_blank");
	 }
}

jQuery(document).ready(function() {

	$('#multiselect').multiselect({
		nonSelectedText: 'Ninguno seleccionado',
		nSelectedText: 'Seleccionado',
		allSelectedText: 'Todo seleccionado',
		includeSelectAllOption: false      
	});
});

var factura = new FacturaViewModel();
FacturaViewModel.errores_factura = ko.validation.group(factura.facturaVO);
FacturaViewModel.errores_bus_contrato = ko.validation.group(factura.buscar_contrato);
FacturaViewModel.errores_bus_Mcontrato = ko.validation.group(factura.buscar_mcontrato);
FacturaViewModel.errores_facturaProyecto = ko.validation.group(factura.buscar_platilla);
FacturaViewModel.errores_mes_causado = ko.validation.group(factura.mes_causado);

$('#txtBuscar').val(sessionStorage.getItem("fac_fac_filtro_factura"));
factura.filtro_factura.mcontrato(sessionStorage.getItem("fac_fac_mcontrato"));
factura.filtro_factura.tipo(sessionStorage.getItem("fac_fac_tipo_factura"));
factura.filtro_factura.contratista_lista(sessionStorage.getItem("fac_fac_contratista_lista") || []);
factura.filtro_factura.contratista_nom(sessionStorage.getItem("fac_fac_contratista_nom"));
factura.filtro_factura.contratista(sessionStorage.getItem("fac_fac_contratista"));
factura.filtro_factura.numero_c(sessionStorage.getItem("fac_fac_numero_c"));
factura.filtro_factura.referencia(sessionStorage.getItem("fac_fac_referencia"));
factura.filtro_factura.numero_f(sessionStorage.getItem("fac_fac_numero_f"));
factura.filtro_factura.desde(sessionStorage.getItem("fac_fac_desde"));
factura.filtro_factura.hasta(sessionStorage.getItem("fac_fac_hasta"));
factura.filtro_factura.radicado(sessionStorage.getItem("fac_fac_radicado"));

factura.consultar(1);//iniciamos la primera funcion

ko.applyBindings(factura);