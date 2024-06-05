function ContratoVigenciaViewModel(){
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	self.num_registro=ko.observable('');
	
	self.tipos=ko.observableArray([]);
	self.lista_tipos=ko.observableArray([]);
	self.lista_otrosi_contrato=ko.observableArray([]);

	self.dis_f_inicio=ko.observable(true);
	self.dis_f_fin=ko.observable(true);
	self.soporte=ko.observable('');
	self.soporte_acta_compra=ko.observable('');

	self.habilitar_alcance=ko.observable(false);
	self.alcance=ko.observable(false);

	self.numero_c=ko.observable('');
	self.nombre_c=ko.observable('');
	self.tipo_c=ko.observable('');
	self.fecha_inicio=ko.observable('');
	self.fecha_fin=ko.observable('');
	self.f_fin_otrosi=ko.observable('');

	self.listadoPoliza=ko.observableArray([]);
	self.mensajePoliza=ko.observable('');
	self.nombre_vigencia=ko.observable('');

	self.soloLectura = ko.observable(null);

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
		actaCesion:ko.observable(120),
		actaAmpliacion:ko.observable()
	};

	//Representa un modelo de la tabla xxxx
	self.vigenciaVO={
		id:ko.observable(0),
		nombre:ko.observable(),
		contrato_id:ko.observable(0),
		tipo_id:ko.observable('').extend({ required: { message: '(*)Seleccione el valor del contrato' } }),
		fecha_inicio:ko.observable(''),
		fecha_fin:ko.observable(''),
		valor:ko.observable(0).money().extend({ required: { message: '(*)Digite el valor' } }),
		soporte:ko.observable(''),
		acta_id: ko.observable(''),
		acta_compra:ko.observable(''),
		soloLectura:ko.observable(null)
	}

	self.changedTipoVigencia = function () {
		var id_tipo = self.vigenciaVO.tipo_id();

		if(id_tipo == self.tipoV.otrosi()){
			self.alcance(false);
			self.habilitar_alcance(true);
			self.dis_f_inicio(true);
			self.dis_f_fin(true);
		}
		if(id_tipo == self.tipoV.liquidacion()){
			self.dis_f_inicio(true);
			self.dis_f_fin(false);
			self.habilitar_alcance(false);
			self.vigenciaVO.fecha_inicio('');
			self.vigenciaVO.fecha_fin('');
		}
		if(id_tipo == self.tipoV.replanteo()){
			self.dis_f_inicio(false);
			self.dis_f_fin(false);
			self.habilitar_alcance(false);
			self.vigenciaVO.fecha_inicio('');
			self.vigenciaVO.fecha_fin('');
		}
		if(id_tipo == self.tipoV.contrato()){
			self.habilitar_alcance(false);
			self.alcance(false);
		}
		if(id_tipo == self.tipoV.actaAmpliacion()){
			self.alcance(false);
			self.habilitar_alcance(false);
			self.dis_f_inicio(true);
			self.dis_f_fin(true);
		}
	}

	self.alcance.subscribe(function (value) {
		//console.log("asas"+value);
		if(value){
			self.dis_f_inicio(false);
			self.dis_f_fin(false);
			self.vigenciaVO.fecha_inicio('');
			self.vigenciaVO.fecha_fin('');
		}else{
			self.dis_f_inicio(true);
			self.dis_f_fin(true);
		}
	});

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

	//Funcion para crear la paginacion
	self.llenar_paginacion = function (data,pagina) {
		self.paginacion.pagina_actual(pagina);
		self.paginacion.total(data.count);       
		self.paginacion.cantidad_por_paginas(resultadosPorPagina);
	}

	self.paginacion.pagina_actual.subscribe(function (pagina) {
		self.consultar(pagina);
	});

	self.abrir_modal = function () {
		self.limpiar();
		//self.habilitar_campos(true);
		self.titulo('Registrar Vigencia');
		$('#modal_acciones').modal('show');
		self.lista_tipos([]);

		if(self.listado().length > 0){
			ko.utils.arrayForEach(self.tipos(),function(p){

				// if(p.id == self.tipoV.otrosi() || p.id == self.tipoV.liquidacion() || p.id == self.tipoV.replanteo() ){
				if(p.id != self.tipoV.contrato() && p.id != self.tipoV.actaSuspension() && p.id != self.tipoV.actaReinicio() && p.id != self.tipoV.actaInicio() ){
					//console.log("qwqw:"+p.nombre);
					self.lista_tipos.push({"id":p.id,"nombre":p.nombre});
				}
			});
		}else{
			ko.utils.arrayForEach(self.tipos(),function(p){

				// if(p.id == self.tipoV.otrosi() || p.id == self.tipoV.liquidacion() || p.id == self.tipoV.replanteo() || p.id == self.tipoV.contrato() ){
				if(p.id != self.tipoV.actaSuspension() && p.id != self.tipoV.actaReinicio() && p.id != self.tipoV.actaInicio() ){
					//console.log("qwqw:"+p.nombre);
					self.lista_tipos.push({"id":p.id,"nombre":p.nombre});
				}
			});
		}
	}
   
	// limpiar el modelo 
	self.limpiar=function(){
		self.vigenciaVO.id(0);
		self.vigenciaVO.tipo_id('');
		self.vigenciaVO.fecha_inicio('');
		self.vigenciaVO.fecha_fin('');
		self.vigenciaVO.valor(0);
		self.vigenciaVO.soporte('');
		$('#archivo').fileinput('reset');
		$('#archivo').val('');
		// check_eliminar(false)

		self.vigenciaVO.tipo_id.isModified(false);
	}

	// //exportar excel
	// self.exportar_excel=function(){
	// 	location.href=path_principal+"/empresa/export?dato="+self.filtro()+"&esContratista=1&esContratante=0&esProveedor=0&esDisenador=0";
	// }
	self.exportar_excel=function(id_contrato){
		location.href=path_principal+"/contrato/excel_vigenciacontrato?id_contrato="+self.vigenciaVO.contrato_id();
		//alert('id'+self.vigenciaVO.contrato_id());
	}
	
	// funcion guardar
	self.guardar=function(){

		if (ContratoVigenciaViewModel.errores_vigencia().length == 0){ //se activa las validaciones

			// self.vigenciaVO.soporte($('#archivo')[0].files[0]);
			if(self.vigenciaVO.id()==0){
				var liquidacion = true;
				var validar_fecha = true;

				if($('#archivo')[0].files.length==0){
					self.vigenciaVO.soporte('');
					liquidacion = false;
					//console.log("iddd:"+self.vigenciaVO.id());
					mensajeInformativo('Seleccione un soporte','Información');
					return false;
				}
				// if($('#acta_compra')[0].files.length==0){
				// 	self.vigenciaVO.acta_compra('');
				// 	liquidacion = false;
				// 	//console.log("iddd:"+self.vigenciaVO.id());
				// 	mensajeInformativo('Seleccione un soporte','Información');
				// 	return false;
				// }

				if(self.vigenciaVO.tipo_id() == self.tipoV.otrosi()){

					var num = self.lista_otrosi_contrato().length;
					self.vigenciaVO.nombre('OtroSi No. '+(num+1));

					// Validar rango de fechas
					if(!self.alcance()){
						if((self.vigenciaVO.fecha_inicio() > self.fecha_inicio()) && (self.vigenciaVO.fecha_inicio() > self.fecha_fin())){
							validar_fecha = true;
							// console.log("okk:"+validar_fecha);

						}else{
							validar_fecha = false;
							mensajeInformativo('La fecha inicio esta por fuera del rango','Información');
							//console.log("Noo:"+validar_fecha);
							return false;
						}
						if(self.vigenciaVO.fecha_fin() > self.vigenciaVO.fecha_inicio()){
							validar_fecha = true;
							// console.log("okk:"+validar_fecha);

						}else{
							validar_fecha = false;
							mensajeInformativo('La fecha fin es menor que la fecha inicio','Información');
							//console.log("Noo:"+validar_fecha);
						}
					}
				}else if(self.vigenciaVO.tipo_id() == self.tipoV.replanteo()){
					self.vigenciaVO.nombre('Replanteo');
				}else if(self.vigenciaVO.tipo_id() == self.tipoV.liquidacion()){

					if(self.vigenciaVO.fecha_inicio() == ''){
						liquidacion = false;
						mensajeInformativo('Seleccione la fecha de Liquidación','Información');
						return false;
					}
					self.vigenciaVO.nombre('Liquidación');
				}else if(self.vigenciaVO.tipo_id() == self.tipoV.contrato()){

					if(self.vigenciaVO.fecha_inicio() == '' || self.vigenciaVO.fecha_fin() == ''){
						liquidacion = false;
						mensajeInformativo('Seleccione las fechas del Contrato','Información');
						return false;
					}
					self.vigenciaVO.nombre('Contrato');
				}else if(self.vigenciaVO.tipo_id() == self.tipoV.actaAmpliacion()){
					self.vigenciaVO.nombre('Acta de ampliación');
				}else if(self.vigenciaVO.tipo_id() == self.tipoV.actaCesion()){
					self.vigenciaVO.nombre('Acta de cesión');
				}
				
				// console.log("num_otro si:"+num);
				// console.log("nom:"+self.vigenciaVO.nombre()); return false;
				if((liquidacion) && (validar_fecha)){
					var parametros={
						callback:function(datos, estado, mensaje){

							if (estado=='ok') {

								$('#modal_acciones').modal('hide');
								self.limpiar();
								self.consultar(self.vigenciaVO.contrato_id());
							}else{
								mensajeError(mensaje);
							}
						}, //funcion para recibir la respuesta 
						url:path_principal+'/api/Vigencia_contrato/',//url api
						parametros:self.vigenciaVO
						//alerta:false                       
					};
					//parameter =ko.toJSON(self.vigenciaVO);
					//Request(parametros);
					RequestFormData(parametros);
				}
			}else{
				var liquidacion = true;
				if($('#archivo')[0].files.length==0){
					self.vigenciaVO.soporte('');
				}
				if(self.tipo_c() == self.tipo.interventoria()){
					if($('#acta_compra')[0].files.length==0){
						self.vigenciaVO.acta_compra('');
					}
				}else{
					self.vigenciaVO.acta_compra('');
				}
				if(self.vigenciaVO.tipo_id() == self.tipoV.liquidacion()){

					if((self.vigenciaVO.fecha_inicio() == '') || (self.vigenciaVO.fecha_inicio() == null)){
						liquidacion = false;
						mensajeError('Seleccione la fecha de Liquidación');
					}
				}
				if(self.vigenciaVO.fecha_fin() == null){
					self.vigenciaVO.fecha_fin('')
				}
				if(self.vigenciaVO.fecha_inicio() == null){
					self.vigenciaVO.fecha_inicio('')
				}

				if(liquidacion){
					var parametros={
						metodo:'PUT',
						callback:function(datos, estado, mensaje){

							if (estado=='ok') {
								self.filtro("");
								self.consultar(self.vigenciaVO.contrato_id());
								$('#modal_acciones').modal('hide');
								self.limpiar();
							}

						},//funcion para recibir la respuesta 
						url:path_principal+'/api/Vigencia_contrato/'+self.vigenciaVO.id()+'/',
						parametros:self.vigenciaVO                        
					};
					RequestFormData(parametros);
				}
			}
		} else {
			ContratoVigenciaViewModel.errores_vigencia.showAllMessages();
		}
	}

	//funcion consultar de tipo get recibe un parametro
	self.consultar = function (id_contrato) {
		
		//path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
		self.filtro($('#txtBuscar').val());
		sessionStorage.setItem("filtro",self.filtro() || '');

		lista=self.tipoV.contrato();
		lista=lista+','+self.tipoV.otrosi()+','+self.tipoV.replanteo()+','+self.tipoV.liquidacion()+','+self.tipoV.actaCesion();
		

		if (self.filtro()){
			parameter = {id_contrato: id_contrato, nombre: self.filtro(), sin_paginacion: '', id_tipo: lista };
		}else{
			parameter = {id_contrato: id_contrato, sin_paginacion: '', id_tipo: lista };
		}

		path = path_principal+'/api/Vigencia_contrato/?format=json&lite_list=1';
		RequestGet(function (data, success, mensage) {

			if (success == 'ok' && data!=null && data.length > 0) {
				self.mensaje('');
				//self.listado(results);
				// self.listado(agregarOpcionesObservable(data.sort(function(a, b) {
				// 	if (a.value > b.value) {
				// 	  return 1;
				// 	}
				// 	if (a.value < b.value) {
				// 	  return -1;
				// 	}
				// 	return 0;
				//   })));
				//ordenarAsc(data, 'num');
				self.listado(agregarOpcionesObservable(data));
				// self.num_registro("- N° de Registros: "+data.count);

				self.numero_c(data[0].contrato.numero);
				self.nombre_c(data[0].contrato.nombre);
				self.tipo_c(data[0].contrato.tipo_contrato.id);

				self.fecha_inicio(fechasInicio(data));
				self.fecha_fin(fechasFin(data));

				// Buscar fecha fin de OtroSi
				// ko.utils.arrayForEach(data,function(p){
				// 	if ((p.tipo.id == self.tipoV.otrosi()) && (p.fecha_fin)){
				// 		self.f_fin_otrosi(p.fecha_fin);
				// 	}
				// });

				// console.log("f_i:"+self.fecha_inicio());
				// console.log("f_f:"+self.fecha_fin());

			} else {
				self.listado([]);
				self.num_registro("");
				self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}
			//self.llenar_paginacion(data,pagina);
		}, path, parameter,function(){
			cerrarLoading();
			self.listaTipo('VigenciaContrato');
		},true);
	}

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.consultar(self.vigenciaVO.contrato_id());
		}
		return true;
	}

	// Para editar la vigencia
	self.consultar_por_id = function (obj) {

		//alert(obj.id); return false;
		path =path_principal+'/api/Vigencia_contrato/'+obj.id+'/?format=json';
		parameter = {};
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar Vigencia Contrato');
			//console.log("asas: "+datos.tipo.id);

			self.vigenciaVO.id(datos.id);
			//self.vigenciaVO.tipo_id(datos.tipo.id);
			self.vigenciaVO.nombre(datos.nombre);
			self.vigenciaVO.fecha_inicio(datos.fecha_inicio);
			self.vigenciaVO.fecha_fin(datos.fecha_fin);
			self.vigenciaVO.valor(datos.valor);
			self.vigenciaVO.soporte(datos.soporte);
			self.vigenciaVO.acta_compra(datos.acta_compra);
			self.vigenciaVO.soloLectura(datos.soloLectura);
			self.soporte(datos.soporte);
			self.soporte_acta_compra(datos.acta_compra);
			//self.habilitar_campos(true);
			$('#modal_acciones').modal('show');

			if (datos.tipo.id == self.tipoV.contrato()) {
				self.lista_tipos([]);
				ko.utils.arrayForEach(self.tipos(),function(p){

					if(p.id == self.tipoV.contrato() ){
						//console.log("qwqw:"+p.nombre);
						self.lista_tipos.push({"id":p.id,"nombre":p.nombre});
					}
				});
				setTimeout(function(){ self.vigenciaVO.tipo_id(datos.tipo.id); }, 1500);
			}else{
				self.lista_tipos([]);
				ko.utils.arrayForEach(self.tipos(),function(p){

					// if(p.id == self.tipoV.otrosi() || p.id == self.tipoV.liquidacion() || p.id == self.tipoV.replanteo() ){
					if(p.id != self.tipoV.contrato() && p.id != self.tipoV.actaSuspension() && p.id != self.tipoV.actaReinicio() && p.id != self.tipoV.actaInicio() ){
						//console.log("qwqw:"+p.nombre);
						self.lista_tipos.push({"id":p.id,"nombre":p.nombre});
					}
				});
				setTimeout(function(){ self.vigenciaVO.tipo_id(datos.tipo.id); }, 1500);
			}
		}, path, parameter);
	}

	// 
	/*self.consultar_por_id_detalle = function (obj) {

		// alert(obj.id)
		//path = path_principal+'/api/Vigencia_contrato/'+obj.id+'/?format=json';
		path = path_principal+'/api/Vigencia_contrato/?format=json';
		parameter = {dato: self.filtro(), pagina: pagina };

		RequestGet(function (results,count) {

			self.titulo('Contratista');

			self.contratoVO.id(results.id);
			self.contratoVO.nombre(results.nombre);
			self.contratoVO.direccion(results.direccion);
			self.contratoVO.soporte(results.soporte);
			self.contratoVO.nit(results.nit);
			//self.habilitar_campos(false);
			$('#modal_acciones').modal('show');
		}, path, parameter);
	}*/

	self.eliminar = function (obj) {

		// var path =path_principal+'/api/eliminar_id/';
		// var parameter = { lista: lista_id };
		// RequestAnularOEliminar("Esta seguro que desea eliminar los contratistas seleccionados?", path, parameter, function () {
		// 	self.consultar(1);
		// 	//self.checkall(false);
		// })

		var parametros={
			metodo:'DELETE',
			callback:function(data, success, mensaje){

				if (success=='ok') {
					self.filtro("");
					self.consultar(self.vigenciaVO.contrato_id());
				}
			},//funcion para recibir la respuesta 
			url:path_principal+'/api/Vigencia_contrato/'+obj.id+'/'
			//parametros:obj.id
		};
		Request(parametros);
	}

	//consultar tipos de vigencia del contrato
	self.listaTipo=function(dato){
		parameter='';
		path =path_principal+'/api/Tipos/?aplicacion='+dato+'&format=json&ignorePagination=1&lite=1';

		RequestGet(function (results,count) {

			self.tipos(results);
			
		}, path, parameter, function(){
			ko.utils.arrayForEach(self.tipos(),function(p){

				// if(p.id == self.tipoV.otrosi() || p.id == self.tipoV.liquidacion() || p.id == self.tipoV.replanteo() ){
				if(p.id != self.tipoV.contrato() && p.id != self.tipoV.actaSuspension() && p.id != self.tipoV.actaReinicio() && p.id != self.tipoV.actaInicio() ){
					//console.log("qwqw:"+p.nombre);
					self.lista_tipos.push({"id":p.id,"nombre":p.nombre});
				}
			});
		},false,false);
	}


	//consultar otroSi del contrato actual
	self.list_otrosi_contrato=function(){

		if(self.vigenciaVO.tipo_id() == self.tipoV.otrosi()){
			parameter = {id_contrato:self.vigenciaVO.contrato_id(), id_tipo:self.tipoV.otrosi(), sin_paginacion:1 };
			path = path_principal+'/api/Vigencia_contrato/?format=json';
			RequestGet(function (data,success,message) {
				//console.log(data);
				self.lista_otrosi_contrato(convertToObservableArray(data));

			}, path, parameter,function() {
				self.guardar();
			});
		}else{
			if((self.vigenciaVO.tipo_id() == self.tipoV.actaCesion()) && (self.vigenciaVO.id() == 0)){
				parameter = {id_contrato:self.vigenciaVO.contrato_id(), id_tipo:self.tipoV.actaCesion(), sin_paginacion:1 };
				path = path_principal+'/api/Vigencia_contrato/?format=json';
				RequestGet(function (data,success,message) {
					//console.log(data);
					if(data.length>0){
						mensajeInformativo('Solo se puede ingresar una acta de cesión por contrato','Información');
						return false;
					}else{
						self.guardar();
					}
					
					
				
				}, path, parameter);
			}else{ self.guardar(); }
		}
		
	}

	// consulta polizas
	self.consultarPoliza = function (obj) {

		//console.log("id:"+obj.id)
		path = path_principal+'/api/VigenciaPoliza/?sin_paginacion=0&tipo_documento=vigencia&id_documento='+obj.id+'&lite=1&format=json';
		// path = path_principal+'/api/VigenciaPoliza/?sin_paginacion=0&id_documento=1&lite=1&format=json';
		parameter = {};

		RequestGet(function (datos, estado, mensage) {
			$('#modal_polizas').modal('show');

			if (estado == 'ok' && datos!=null && datos.length > 0) {
				self.mensajePoliza('');
				self.listadoPoliza(agregarOpcionesObservable(datos));					
				self.nombre_vigencia(obj.nombre)
			} else {
				self.listadoPoliza([]);
				self.nombre_vigencia(obj.nombre);
				self.mensajePoliza(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}
		}, path, parameter);
	}

	function ordenarAsc(p_array_json, p_key) {
		p_array_json.sort(function (a, b) {
			return a[p_key] < b[p_key];
		});
	}

	 self.ver_soporte = function(obj) {
      window.open(path_principal+"/contrato/ver-soporte/?id="+ obj.id, "_blank");
     }

  	self.ver_soporte_acta = function(obj) {
      window.open(path_principal+"/contrato/ver-soporte-acta-compra/?id="+ obj.id, "_blank");
     }

     // consulta polizas
	self.consultarContratoSoloLectura = function (contrato_id) {

		path = path_principal+`/contrato/validar-permiso/?contrato_id=${contrato_id}&format=json`;
		parameter = {};

		RequestGet(function (datos, estado, mensage) {
			
			if (estado == 'ok' && datos != null) {
				self.soloLectura(datos.solo_lectura)	
			}
		}, path, parameter);
	}
     
}

var contratoVigencia = new ContratoVigenciaViewModel();
ContratoVigenciaViewModel.errores_vigencia = ko.validation.group(contratoVigencia.vigenciaVO);

$('#txtBuscar').val(sessionStorage.getItem("filtro"));

// contratoVigencia.listaTipo('VigenciaContrato');//iniciamos la primera funcion

var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(contratoVigencia,content);
ko.applyBindings(contratoVigencia,header);
