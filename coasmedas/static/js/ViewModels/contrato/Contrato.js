function ContratoViewModel(){
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.mensajeAdjudicacionRecursos=ko.observable('');

	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	self.num_registro=ko.observable('');

	self.listado_tipo_contrato=ko.observableArray([]);
	self.listado_empresa_contratista=ko.observableArray([]);
	self.listado_empresa_contratante=ko.observableArray([]);
	self.lista_contrato=ko.observableArray([]);
	self.lista_Mcontrato=ko.observableArray([]);
	self.lista_proyecto=ko.observableArray([]);
	self.lista_rubro=ko.observableArray([]);
	self.lista_proy_contrato=ko.observableArray([]);
	self.lista_m_contrato=ko.observableArray([]);

	self.habilitar_mcontrato=ko.observable(false);
	//self.habilitar_proyecto=ko.observable(false);
	self.habilitar_rubro=ko.observable(false);
	self.habilitar_campos=ko.observable(true);
	self.id_contrato=ko.observable(true);
	self.listMcontrato=ko.observableArray([]);

	self.clase_table=ko.observable(true);
	self.tipo_secion=ko.observable('');
	self.saldo_factura=ko.observable('');
	self.saldo_vigencia=ko.observable('');

	// Datos del contrato
	self.detalle={
		contratante:ko.observable(''),
		contratista:ko.observable(''),
		numero:ko.observable(''),
		nombre:ko.observable(''),
		tipo:ko.observable(''),
		estado_c:ko.observable(''),
		descripcion:ko.observable(''),
		m_contrato:ko.observable(''),
		f_inicio:ko.observable(''),
		f_fin:ko.observable(''),
		valor:ko.observable(''),
		valor_total:ko.observable(''),
		liquidacion:ko.observable(''),
		a_inicio:ko.observable(''),
		a_reinicio:ko.observable(''),
		interventor:ko.observable('')
	}

	self.tipo={
		contratoProyecto:ko.observable(8),
		interventoria:ko.observable(9),
		medida:ko.observable(10),
		retie:ko.observable(11),
		m_contrato:ko.observable(12),
		suministros:ko.observable(13),
		obra:ko.observable(14),
		otros:ko.observable(15)
	};
	self.estado={
		vigente:ko.observable(28),
		liquidado:ko.observable(29),
		suspendido:ko.observable(30),
		porVencer:ko.observable(31),
		vencido:ko.observable(32)
	};
	self.tipoV={
		contrato:ko.observable(16),
		otrosi:ko.observable(17),
		actaSuspension:ko.observable(18),
		actaReinicio:ko.observable(19),
		replanteo:ko.observable(20),
		liquidacion:ko.observable(21),
		actaInicio:ko.observable(22),
		actaAmpliacion:ko.observable()
	};

	self.actaAsignacionVO = {
		id:ko.observable(0),
		nombre:ko.observable(''),
		fechafirma:ko.observable(''),
		contrato: ko.observable(''),
	}

	///self.url=path_principal+'api/contrato';
	//Representa un modelo de la tabla persona
	self.contratoVO={
		id:ko.observable(0),
		nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del contrato' } }),
		numero:ko.observable('').extend({ required: { message: '(*)Digite el número del contrato' } }),
		estado_id:ko.observable(self.estado.vigente()),
		contratante_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contratante ' } }),
		contratista_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contratista' } }),
		tipo_contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de contrato ' } }),
		descripcion:ko.observable('').extend({ required: { message: '(*)Digite una breve descripción del contrato' } }),
		mcontrato_id:ko.observable(''),//.extend({ required: { message: '(*)Seleccione el M-Contrato' } }),
		activo:ko.observable(),
		rubros:ko.observableArray([])
		/*vigencia:{
			nombre:ko.observable('Contrato'),
			contrato_id:ko.observable(0),
			tipo_id:ko.observable(9),
			fecha_inicio:ko.observable('').extend({ required: { message: '(*)Digite la fecha inicio del contrato' } }),
			fecha_fin:ko.observable('').extend({ required: { message: '(*)Digite la fecha fin del contrato' } }),
			valor:ko.observable('').extend({ required: { message: '(*)Digite el valor del contrato' } }),
			soporte:ko.observable('')
		}*/
	}

	self.vigenciaVO={
			nombre:ko.observable('Contrato'),
			contrato_id:ko.observable(0),
			tipo_id:ko.observable(self.tipoV.contrato()),
			fecha_inicio:ko.observable('').extend({ required: { message: '(*)Digite la fecha inicio del contrato' } }),
			fecha_fin:ko.observable('').extend({ required: { message: '(*)Digite la fecha fin del contrato' } }),
			valor:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor del contrato' } }),
			soporte:ko.observable(''),
	}

	self.filtroC={
		tipo_contrato:ko.observable(''),
		estado:ko.observable(''),
		contratista_id:ko.observable(''),
		mcontrato:ko.observableArray([])
	};

	self.changedTipoContrato = function () {
		var id_tipo = self.contratoVO.tipo_contrato_id();

		if (id_tipo == self.tipo.interventoria() || id_tipo == self.tipo.medida() || id_tipo == self.tipo.retie() || id_tipo == self.tipo.suministros() || id_tipo == self.tipo.obra() || id_tipo == self.tipo.otros()) {
			self.habilitar_mcontrato(true);
			//self.habilitar_proyecto(false);
			self.habilitar_rubro(false);
			
		} else if (id_tipo == self.tipo.contratoProyecto()) {
			
			self.habilitar_mcontrato(true);
			self.habilitar_rubro(false);
		}else if (id_tipo == self.tipo.m_contrato()) {

			if(self.contratoVO.id()==0){

				self.contratoVO.rubros([]);
				self.list_rubro(0);

				setTimeout(function(){
					ko.utils.arrayForEach(self.lista_rubro(),function(p){

						self.contratoVO.rubros.push({procesar:ko.observable(p.tiene_rubro()),id:ko.observable(p.id()),nombre:p.nombre() });
					});
				}, 1000);
			}
			self.habilitar_rubro(true);
			self.habilitar_mcontrato(false);
			//self.habilitar_proyecto(false);
			self.contratoVO.mcontrato_id(0);
			//self.contratoVO.proyecto(0);
		}else{
			self.habilitar_mcontrato(false);
			//self.habilitar_proyecto(false);
			self.habilitar_rubro(false);
			//self.contratoVO.proyecto(0);
		}
	}

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

	self.abrir_modal = function () {
		self.limpiar();
		//self.habilitar_campos(true);
		self.titulo('Registrar Contrato');
		$('#modal_acciones').modal('show');
		self.habilitar_campos(true);
	}
	//funcion para cambiar de color el icono
    self.setColorIconoFiltro = function (){
    	

        tipo_contrato = sessionStorage.getItem("cto_cto_tipo_contrato");
        estado_id = sessionStorage.getItem("cto_cto_estado");
        contratista_id = sessionStorage.getItem("cto_cto_contratista_id");
        mcontrato = sessionStorage.getItem("cto_cto_mcontrato");
      
        //alert(" color, tipo_contrato : " + tipo_contrato);
    	//alert(" color, estado_id : " + estado_id);
    	//alert(" color, contratista_id : " + contratista_id);
    	//alert(" color, mcontrato: "+mcontrato);

    	

        if ((tipo_contrato!='' && tipo_contrato != 0 && tipo_contrato != null) || 
        	(estado_id != '' && estado_id !=0 && estado_id != null) || 
        	(contratista_id != '' && contratista_id !=0 && contratista_id != null) ||
        	(mcontrato!='' && mcontrato!=null)
        	){

            $('#iconoFiltro').addClass("filtrado");
        }else{
            $('#iconoFiltro').removeClass("filtrado");
        }
    }
	self.abrir_filtro = function () {

		//alert(" abrir_filtro, contratista_id : " + sessionStorage.getItem("cto_cto_contratista_id"));

		if (sessionStorage.getItem("cto_cto_contratista_id") != ''){ 
                $('#contratista_filtro').val(sessionStorage.getItem("cto_cto_contratista_id"));
                self.filtroC.contratista_id( $('#contratista_filtro').val());
            } 
		//self.titulo('Registrar Contrato');
		$('#filtro_contrato').modal('show');

	}
	self.abrir_cesion = function (obj) {

		self.id_contrato(obj.id);
		$('#cesion').modal('show');
	}

	//exportar excel
	self.exportar_excel=function(){
		location.href=path_principal+"/contrato/excel_contrato?dato="+self.filtro()+
																"&id_tipo="+self.filtroC.tipo_contrato()+
																"&id_estado="+self.filtroC.estado()+
																"&mcontrato="+self.listMcontrato().toString()+
																"&contratista_id="+self.filtroC.contratista_id();
	}
   
	// //limpiar el modelo
	self.limpiar=function(){
		self.contratoVO.id(0);
		self.contratoVO.nombre('');
		self.contratoVO.numero('');
		self.contratoVO.contratante_id('');
		self.contratoVO.contratista_id('');
		self.contratoVO.tipo_contrato_id(0)
		self.contratoVO.descripcion('');
		self.vigenciaVO.fecha_inicio('');
		self.vigenciaVO.fecha_fin('');
		self.vigenciaVO.valor(0);
		self.vigenciaVO.soporte('');
		self.contratoVO.mcontrato_id('');
		self.contratoVO.activo();
		//self.contratoVO.grupo_empresa(1);
		//self.contratoVO.proyecto(0);
		// self.contratoVO.rubros('');
		$('#archivo').fileinput('reset');
		$('#archivo').val('');
		// check_eliminar(false)

		self.contratoVO.contratante_id.isModified(false);
		self.contratoVO.contratista_id.isModified(false);
		self.contratoVO.tipo_contrato_id.isModified(false);
	}

	// funcion guardar
	self.guardar=function(){

		if (ContratoViewModel.errores_contrato().length == 0 && ContratoViewModel.errores_vigencia().length == 0 ) { //se activa las validaciones

			// self.contratoVO.soporte($('#archivo')[0].files[0]);
			if(self.contratoVO.id()==0){
				
				var id_tipo = self.contratoVO.tipo_contrato_id();
				self.contratoVO.activo(true);
				
				if(id_tipo == self.tipo.m_contrato()){
					// Buscarlo los rubros Seleccionados
					var lista=[];
					ko.utils.arrayForEach(self.contratoVO.rubros(),function(p){
						if (p.procesar()) {
							lista.push(p.id());
						}
					});
					self.contratoVO.rubros(lista);
					// console.log(lista);return false;
				}
				console.log("fecha_ini");
				var f_inicio = new Date(self.vigenciaVO.fecha_inicio()+" 00:00:00");
				var f_fin = new Date(self.vigenciaVO.fecha_fin()+" 00:00:00");
				if(f_inicio > f_fin){
					mensajeInformativo('La fecha inicio no puede ser mayor que la fecha fin.','Información');return false;
				}
				//console.log(self.contratoVO.rubros()); return false;
				var parametros={
					callback:function(datos, estado, mensaje){

						if (estado=='ok') {
							self.vigenciaVO.contrato_id(datos.id);

								var parametros={
									callback:function(datos, estado, mensaje){

										if (estado=='ok') {
											self.vigenciaVO.contrato_id(datos.id);

											self.filtro("");
											self.consultar(self.paginacion.pagina_actual());
											$('#modal_acciones').modal('hide');
											self.limpiar();
											//alert("id contrato nuevo: "+datos.id);
										}
									}, //funcion para recibir la respuesta 
									url:path_principal+'/api/Vigencia_contrato/',//url api
									parametros:self.vigenciaVO                        
								};

								//parameter =ko.toJSON(self.contratoVO);
								RequestFormData(parametros);

						}else{
							 mensajeError(mensaje);
						}
					}, //funcion para recibir la respuesta 
					url:path_principal+'/api/Contrato/',//url api
					parametros:self.contratoVO,
					alerta:false                       
				};

				//parameter =ko.toJSON(self.contratoVO);
				Request(parametros);
			}else{

				var id_tipo = self.contratoVO.tipo_contrato_id();
				/*if(id_tipo==self.tipo.contratoProyecto()){
					// Buscarlo el M-Contrato del proyecto
					ko.utils.arrayForEach(self.lista_proyecto(),function (p) {
						if (self.contratoVO.proyecto()==p.id) {
							//alert(p.id+' mcnontrato:'+p.mcontrato);
							self.contratoVO.mcontrato(p.mcontrato);
						}
					});
					//alert(self.contratoVO.proyecto()+' - '+self.contratoVO.mcontrato());
				}else */
				if(id_tipo == self.tipo.m_contrato()){
					// Buscarlo los rubros Seleccionados
					var lista=[];
					ko.utils.arrayForEach(self.contratoVO.rubros(),function(p){
						if (p.procesar()) {
							lista.push(p.id());
						}
					});
					self.contratoVO.rubros(lista);
					// console.log(lista);return false;
				}

				if($('#archivo')[0].files.length==0){
					self.vigenciaVO.soporte('');
				}

				var parametros={
					metodo:'PUT',
					callback:function(datos, estado, mensaje){

						if (estado=='ok') {
							self.filtro("");
							self.consultar(self.paginacion.pagina_actual());
							$('#modal_acciones').modal('hide');
							self.limpiar();
						}

					},//funcion para recibir la respuesta 
					url:path_principal+'/api/Contrato/'+self.contratoVO.id()+'/',
					parametros:self.contratoVO                        
				};
				RequestFormData(parametros);
			}

		} else {
			if (ContratoViewModel.errores_contrato().length > 0 ) {
				ContratoViewModel.errores_contrato.showAllMessages();
			}
			if(ContratoViewModel.errores_vigencia().length > 0 ){
				ContratoViewModel.errores_vigencia.showAllMessages();
			}
		}
	}

	//funcion consultar de tipo get recibe un parametro
	self.consultar = function (pagina) {
		if (pagina > 0) {
			//console.log(self.filtroC.mcontrato());
			//path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
			
			//alert(" consultar1, tipo_contrato : " + sessionStorage.getItem("cto_cto_tipo_contrato"));
			//alert(" consultar1, contratista_id : " + sessionStorage.getItem("cto_cto_contratista_id"));
			
			sessionStorage.setItem("cto_cto_tipo_contrato",self.filtroC.tipo_contrato() || '');
			sessionStorage.setItem("cto_cto_estado",self.filtroC.estado() || '');
			sessionStorage.setItem("cto_cto_contratista_id",self.filtroC.contratista_id() || '');
			sessionStorage.setItem("cto_cto_mcontrato",self.listMcontrato() || '');

			
			
			
			//alert(" consultar2, tipo_contrato : " + sessionStorage.getItem("cto_cto_tipo_contrato"));
			//alert(" consultar2, contratista_id : " + sessionStorage.getItem("cto_cto_contratista_id"));
			self.setColorIconoFiltro();
			self.cargar(pagina);
			/*var lista=[];
			ko.utils.arrayForEach(self.listMcontrato(),function(p){
				lista.push(p);
			});*/
			//console.log("ids:"+lista);
		}
	}


    self.cargar = function(pagina){
    		self.filtro($('#txtBuscar').val());
    		sessionStorage.setItem("cto_cto_filtro_contrato",self.filtro() || '');
			path = path_principal+'/api/Contrato/?format=json';
			parameter = {dato: self.filtro(),
									id_tipo:self.filtroC.tipo_contrato(),
									id_estado:self.filtroC.estado(),
									contratista_id:self.filtroC.contratista_id(),
									// mcontrato:lista.toString(),
									mcontrato:self.listMcontrato().toString(),
									lite:2,noAsignado:1,
									//otros:1,contratante:1,contratista:1,tipo:1,list_mcontrato:1,
									page: pagina };
			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
					self.mensaje('');
					self.num_registro("- N° de Registros: "+datos.count);
					//self.listado(results);
					self.listado(agregarOpcionesObservable(datos.data));					

				} else {
					self.listado([]);
					self.num_registro("");
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

			}, path, parameter, function(){self.llenarSelect();},false);
		}
	

	//consultar contratista, contratante y MContratos selects
	self.llenarSelect=function(dato){
		parameter={};
		path = path_principal+'/api/Contrato/?format=json';
		parameter = {sin_list_contrato:1,//tipo:1,
					 contratante:1,contratista:1,list_mcontrato:1,};

		RequestGet(function (datos, estado, mensage) {

			// LLENAR CONTRATISTA
			self.listado_empresa_contratista(datos.contratista);
			// LLENAR CONTRATANTE
			self.listado_empresa_contratante(datos.contratante);
			// LLENAR MACRO-CONTRATOS
			self.lista_contrato(convertToObservableArray(datos.mcontrato));
		}, path, parameter,function(){},false,false);
	}

	self.checkall.subscribe(function(valor){

		ko.utils.arrayForEach(self.lista_Mcontrato(), function(d) {

			d.procesar(valor);
		});
	});

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			self.filtro($('#txtBuscar').val());
			self.consultar(1);
		}
		return true;
	}

	// Para editar el contrato
	self.consultar_por_id = function (obj) {

		//alert(obj.id); return false;
		path =path_principal+'/api/Contrato/'+obj.id+'/?lite_editar=1&format=json';
		parameter = {};
		RequestGet(function (results,success) {

			self.habilitar_campos(false);
			self.limpiar();

			self.titulo('Actualizar Contrato');
			//console.log("asas: "+results.vigencia_contrato[0].id);

			self.contratoVO.id(results.id);
			self.contratoVO.estado_id(results.estado.id);
			self.contratoVO.nombre(results.nombre);
			self.contratoVO.numero(results.numero);
			self.contratoVO.contratante_id(results.contratante.id);
			self.contratoVO.contratista_id(results.contratista.id);
			self.contratoVO.tipo_contrato_id(results.tipo_contrato.id);
			self.contratoVO.descripcion(results.descripcion);
			self.contratoVO.activo(results.activo);
			//console.log(results.activo+"act");
			
			if(results.mcontrato){
				self.contratoVO.mcontrato_id(results.mcontrato.id);
			}

			// Buscar la vigencia tipo contrato
			self.vigenciaVO.fecha_inicio('9999-99-99');
			self.vigenciaVO.fecha_fin('9999-99-99');
			self.vigenciaVO.valor(1);

			if(results.tipo_contrato.id == self.tipo.m_contrato()){
				
				self.list_rubro(results.id);
				self.contratoVO.rubros([]);

				setTimeout(function(){

					ko.utils.arrayForEach(self.lista_rubro(),function(p){
						self.contratoVO.rubros.push({procesar:ko.observable(p.tiene_rubro()),id:ko.observable(p.id()),nombre:p.nombre() });
					});
				}, 2000);
			}/*else if(results.contrato.tipo_contrato.id == self.tipo.contratoProyecto()){
				setTimeout(function(){
					self.list_proy_contrato(results.contrato.id);
				}, 1200);
			}*/

			//self.habilitar_campos(true);
			$('#modal_acciones').modal('show');
		}, path, parameter);
	}

	// consulta el detalle del contrato
	self.consultar_por_id_detalle = function (obj) {

		//console.log("id:"+obj.id)
		path = path_principal+'/api/Contrato/'+obj.id+'/?lite_detalle=1&format=json';
		parameter = {};

		RequestGet(function (data, estado, mensage) {

			//console.log(data.contratante.nombre)

			self.detalle.contratante(data.contratante.nombre);
			self.detalle.contratista(data.contratista.nombre);
			self.detalle.numero(data.numero);
			self.detalle.nombre(data.nombre);
			self.detalle.tipo(data.tipo_contrato.nombre);
			self.detalle.estado_c(data.estado.nombre);
			self.detalle.descripcion(data.descripcion);
			self.detalle.f_inicio(data.fecha_inicio);
			self.detalle.f_fin(data.fecha_fin);
			self.detalle.valor_total(data.valor_actual);
			self.detalle.interventor(data.interventoresContrato);
			self.saldo_factura(data.totalFactura);
			self.saldo_vigencia(data.suma_vigencia_contrato.valor__sum);

			self.detalle.m_contrato('');
			if(data.mcontrato){
				self.detalle.m_contrato(data.mcontrato.nombre);
			}/*else{
				self.detalle.m_contrato('');
			}*/
			
			ko.utils.arrayForEach(data.vigencia_contrato,function(p){

				if (p.tipo.id == self.tipoV.contrato()) {
					// self.detalle.f_inicio(p.fecha_inicio);
					self.detalle.valor(p.valor);
					// self.detalle.f_fin(p.fecha_fin);
					//console.log(p.)
				}
				if (p.tipo.id == self.tipoV.liquidacion()){
					self.detalle.liquidacion(p.valor);
				}
			});
			// ko.utils.arrayForEach(data.vigencia_contrato,function(p){

			// 	if ((p.tipo.id == self.tipoV.replanteo()) && (p.fecha_inicio)) {
			// 		// self.detalle.f_inicio(p.fecha_inicio);
			// 		self.detalle.valor(p.valor);
			// 		// self.detalle.f_fin(p.fecha_fin);
			// 	}
			// });
			//ko.utils.arrayForEach(data.vigencia_contrato,function(p){

				
				// if (p.tipo.id == self.tipoV.otrosi()){
				// 	if (p.fecha_fin) {
				// 		self.detalle.f_fin(p.fecha_fin);
				// 	}
				// }
			//});
			/*var cont = 0;
			ko.utils.arrayForEach(data.vigencia_contrato,function(p){
				if (p.tipo.id == self.tipoV.actaSuspension()){
					self.detalle.a_inicio(p.fecha_inicio);
				}
				if (p.tipo.id == self.tipoV.actaReinicio()){
					self.detalle.a_reinicio(p.fecha_inicio);
					cont = cont+1;
				}
				// Sacar los dias que duro suspendidos
				if((self.detalle.a_inicio() != '') && (self.detalle.a_reinicio() != '')){
					var inicio = new Date(self.detalle.a_inicio()+" 00:00:00");
					var fin = new Date(self.detalle.a_reinicio()+" 00:00:00");
					var f_fin = new Date(self.detalle.f_fin()+" 00:00:00");
					var fechaResta = fin - inicio;
					var fechaResta = (((fechaResta / 1000) / 60) / 60) / 24;
					//console.log("fechaResta: "+fechaResta);
					f_fin.setDate (f_fin.getDate() + fechaResta);
					self.detalle.f_fin( f_fin.getFullYear()+'-'+(f_fin.getMonth()+1)+'-'+f_fin.getDate() );
					self.detalle.a_inicio('');
					self.detalle.a_reinicio('');
				}
			});
			var cont2 = 0;
			ko.utils.arrayForEach(data.vigencia_contrato,function(p){
				// Busca si el Acta de Reinicio tiene fecha_fin
				if (p.tipo.id == self.tipoV.actaReinicio()){
					cont2 = cont2+1;
					if ((p.fecha_fin) && (cont2 == cont)) {
						self.detalle.f_fin(p.fecha_fin);
					}
				}
			});*/
		}, path, parameter,function() {
			$('#detalle_contrato').modal('show');
		});
	}

	/*
		var date = new Date("2017-02-01 00:00:00");
		var date2 = new Date("2017-03-01 00:00:00");
		var fechaResta = date2 - date;
		console.log(date);
		console.log(date2);
		date2.setMonth (date2.getMonth() + 1);
		console.log(date2.getFullYear()+'-'+date2.getMonth()+'-'+(date2.getDate()));
		
		console.log( (((fechaResta / 1000) / 60) / 60) / 24 );
		self.eliminar = function () {
			var lista_id=[];
			var count=0;
	*/

	//consultar contratista y contratante selects
	/*self.empresa=function(dato){
		parameter={};
		path =path_principal+'/api/empresa/?sin_paginacion&'+dato+'=1&format=json';
		RequestGet(function (results,count) {
			if(dato == 'esContratista'){
				self.listado_empresa_contratista(results);
			}else if(dato == 'esContratante'){
				self.listado_empresa_contratante(results);
			}
		}, path, parameter,function(){},false);
	}*/

	//consultar los macrocontrato
	/*self.filtrar_macrocontrato=function(){
		parameter={};
		path =path_principal+'/proyecto/filtrar_proyectos/?tipo='+self.tipo.m_contrato();
		RequestGet(function (results,count) {
			self.lista_contrato(convertToObservableArray(results.macrocontrato));
		}, path, parameter, function(){
			ko.utils.arrayForEach(self.lista_contrato(),function(p){
				self.lista_Mcontrato.push({procesar:ko.observable(false),id:ko.observable(p.id()),nombre:p.nombre() });
			});
		},false);
	}*/

	//consultar los rubros por contrato
	self.list_rubro=function(contrato){
		parameter={};
		path =path_principal+'/contrato/list_contrato_rubro/?id_contrato='+contrato;
		RequestGet(function (datos,estado,mensaje) {

			self.lista_rubro(convertToObservableArray(datos));

		}, path, parameter);
	}

	self.cesion_pagina=function(){
		if(self.tipo_secion() == 1){
			location.href=path_principal+"/contrato/sub_contratista/"+self.id_contrato()+"/";
		}else if (self.tipo_secion() == 2) {
			location.href=path_principal+"/contrato/contrato_cesion/"+self.id_contrato()+"/";
		}else if (self.tipo_secion() == 3) {
			location.href=path_principal+"/contrato/cesion_economica/"+self.id_contrato()+"/";
		}
	}

	self.abrir_actaAdjudicacion = function (obj) {
		parameter={};
		path =path_principal+'/api/actaasignacionrecursoscontrato/?contrato='+obj.id;
		RequestGet(function (datos,estado,mensaje) {
			$('#adjudicacionRecursos').modal('show');
			if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
				self.actaAsignacionVO.id(datos.data[0].actaAsignacion.id);
				self.actaAsignacionVO.nombre(datos.data[0].actaAsignacion.nombre);
				self.actaAsignacionVO.fechafirma(datos.data[0].actaAsignacion.fechafirma);
				self.actaAsignacionVO.contrato(datos.data[0].contrato.nombre);
			}else{
				self.actaAsignacionVO.id(0);
				self.actaAsignacionVO.nombre('No definido');
				self.actaAsignacionVO.fechafirma('No definido');

			}

		}, path, parameter);		
		
	}

	self.descargarSoporteActaAdjudicacion = function () {
		if ($('#idActa').val() != '0'){
			//alert('descargando documento.... ' + $('#idActa').val().toString());	
			window.open(path_principal+"/contrato/ver-soporte-acta-adjudicacion/?id=" + $('#idActa').val().toString(), "_blank");
		}
		
	}

	
     
}

jQuery(document).ready(function() {

	$('#multiselect21').multiselect({
		nonSelectedText: 'Ninguno seleccionado',
		nSelectedText: 'Seleccionado',
		allSelectedText: 'Todos seleccionado',
		selectAllText: 'Seleccionar Todo',
		includeSelectAllOption: true
	});
});

var contrato = new ContratoViewModel();
ContratoViewModel.errores_contrato = ko.validation.group(contrato.contratoVO);
ContratoViewModel.errores_vigencia = ko.validation.group(contrato.vigenciaVO);

$('#txtBuscar').val(sessionStorage.getItem("cto_cto_filtro_contrato"));
contrato.filtroC.tipo_contrato(sessionStorage.getItem("cto_cto_tipo_contrato"));
contrato.filtroC.estado(sessionStorage.getItem("cto_cto_estado"));
contrato.filtroC.contratista_id(sessionStorage.getItem("cto_cto_contratista_id"));

if(sessionStorage.getItem("cto_cto_mcontrato") != null ){
	contrato.listMcontrato(sessionStorage.getItem("cto_cto_mcontrato"));
	$('#multiselect21').multiselect('select', sessionStorage.getItem("cto_cto_mcontrato").split(','), true);
}
contrato.setColorIconoFiltro();
contrato.cargar(1);//iniciamos la primera funcion
// contrato.empresa('esContratante');
// contrato.empresa('esContratista');
// contrato.filtrar_macrocontrato();

// var content= document.getElementById('content_wrapper');
// var header= document.getElementById('header');
// ko.applyBindings(contrato,content);
// ko.applyBindings(contrato,header);
ko.applyBindings(contrato);