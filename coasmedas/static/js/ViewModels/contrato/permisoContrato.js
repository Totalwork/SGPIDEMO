function ContratoEmpresaViewModel(){
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	// self.checkall=ko.observable(false);

	self.numero_c=ko.observable('');
	self.nombre_c=ko.observable('');
	self.tituloPanel=ko.observable('');

	self.check_validacion_ver=ko.observable('');
	self.check_validacion_edit=ko.observable('');

	self.lista_empresa=ko.observableArray([]);
	self.lista_contratista=ko.observableArray([]);

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
		actaInicio:ko.observable(22)
	};

	///self.url=path_principal+'api/contrato';
	//Representa un modelo de la tabla xxxx
	self.contratoEmpresaVO={
		id:ko.observable(0),
		contrato_id:ko.observable(0),
		empresa_id:ko.observable(0).extend({ required: { message: '(*)Seleccione el valor del contrato' } }),
		participa:ko.observable(false),
		edita:ko.observable(false)
	}

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

	self.check_validacion_ver.subscribe(function (val) {
		if(val==1){
			self.contratoEmpresaVO.participa(true);
			self.contratoEmpresaVO.edita(false);
			self.check_validacion_edit(0);
		}else{
			self.contratoEmpresaVO.participa(false);
		}
	});

	self.check_validacion_edit.subscribe(function (val) {
		if(val==1){
			self.contratoEmpresaVO.participa(true);
			self.contratoEmpresaVO.edita(true);

			self.check_validacion_ver(0);
		}else{
			self.contratoEmpresaVO.edita(false);
		}
	});

	self.abrir_modal = function () {
		self.limpiar();
		//self.habilitar_campos(true);
		self.titulo('Registrar Empresa');
		$('#modal_acciones').modal('show');
	}
   
	// limpiar el modelo 
	self.limpiar=function(){
		self.contratoEmpresaVO.id(0);
		self.contratoEmpresaVO.empresa_id(0);
		self.contratoEmpresaVO.participa(false);
		self.contratoEmpresaVO.edita(false);
		//check_eliminar(false)

		self.contratoEmpresaVO.empresa_id.isModified(false);

		self.check_validacion_edit('');
		self.check_validacion_ver('');
	}

	//exportar excel
	self.exportar_excel=function(){
		location.href=path_principal+"/empresa/export?dato="+self.filtro()+"&esContratista=1&esContratante=0&esProveedor=0&esDisenador=0";
	}

	// funcion guardar
	self.guardar=function(){

		if (ContratoEmpresaViewModel.errores_contratoEmpresa().length == 0){ //se activa las validaciones

			// self.contratoEmpresaVO.soporte($('#archivo')[0].files[0]);
			if(self.contratoEmpresaVO.id()==0){

				//console.log("nom:"+self.contratoEmpresaVO.participa()); return false;
				if(self.contratoEmpresaVO.edita() == true){
					self.contratoEmpresaVO.participa(true);
				}
				var parametros={
					callback:function(datos, estado, mensaje){

						if (estado=='ok') {

							$('#modal_acciones').modal('hide');
							self.limpiar();
							self.consultar(self.contratoEmpresaVO.contrato_id());
						}else{
							mensajeError(mensaje);
						}
					}, //funcion para recibir la respuesta 
					url:path_principal+'/api/Empresa_contrato/',//url api
					parametros:self.contratoEmpresaVO
					//alerta:false                       
				};

				// parameter =ko.toJSON(self.contratoEmpresaVO);
				Request(parametros);
			}else{

				if(self.contratoEmpresaVO.edita() == true){

					self.contratoEmpresaVO.participa(true);
				}

				var parametros={
					metodo:'PUT',
					callback:function(datos, estado, mensaje){

						if (estado=='ok') {
							self.filtro("");
							self.consultar(self.contratoEmpresaVO.contrato_id());
							$('#modal_acciones').modal('hide');
							self.limpiar();
						}

					},//funcion para recibir la respuesta 
					url:path_principal+'/api/Empresa_contrato/'+self.contratoEmpresaVO.id()+'/',
					parametros:self.contratoEmpresaVO                        
				};
				Request(parametros);
			}
		} else {
			ContratoEmpresaViewModel.errores_contratoEmpresa.showAllMessages();
		}
	}

	//funcion consultar de tipo get recibe un parametro
	self.consultar = function (id_contrato) {
		
		self.filtro($('#txtBuscar').val());

		if (self.filtro()){
			parameter = {id_contrato: id_contrato, dato: self.filtro(), otros:1, contratante:1 };
		}else{
			parameter = {id_contrato: id_contrato, otros:1, contratante:1 };
		}

		path = path_principal+'/api/Empresa_contrato/?format=json';
		RequestGet(function (datos, success, mensage) {

			if (success == 'ok' && datos.data.listado!=null && datos.data.listado.length > 0) {
				self.mensaje('');
				//self.listado(results);
				self.listado(agregarOpcionesObservable(datos.data.listado));

				self.lista_empresa(datos.data.contratante);
				self.lista_contratista(datos.data.contratista);
			} else {
				//console.log("sdsdsd"); self.listado(agregarOpcionesObservable(data));
				self.listado([]);
				self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}
			if(datos.count > 10){
				self.llenar_paginacion(datos,pagina);
				$('#paginacion').show();
			}else{
				$('#paginacion').hide();
			}
		}, path, parameter,function(){cerrarLoading();},false);
	}

	/*self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado(), function(d) {

			d.eliminado(value);
		});
	});*/

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.consultar(self.contratoEmpresaVO.contrato_id());
		}
		return true;
	}

	// Para editar la vigencia
	self.consultar_por_id = function (obj) {

		//alert(obj.id); return false;
		path =path_principal+'/api/Empresa_contrato/'+obj.id+'/?format=json';
		parameter = {};
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar Contrato Empresa');
			//console.log("asas: "+results[0].id);

			self.contratoEmpresaVO.id(datos.id);
			self.contratoEmpresaVO.empresa_id(datos.empresa.id);
			// self.contratoEmpresaVO.participa(datos.participa);
			// self.contratoEmpresaVO.edita(datos.edita);

			if (datos.edita){
				self.check_validacion_edit(1);
			}else{
				if(datos.participa){
					self.check_validacion_ver(1);
				}
			}
			//self.habilitar_campos(true);
			$('#modal_acciones').modal('show');
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

	/*self.eliminar = function (obj) {

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
					self.consultar(self.contratoEmpresaVO.contrato_id());
				}
			},//funcion para recibir la respuesta 
			url:path_principal+'/api/Vigencia_contrato/'+obj.id+'/'
			//parametros:obj.id
		};
		Request(parametros);
	}*/

	self.eliminar = function (obj) {

		var path =path_principal+'/api/Empresa_contrato/'+ obj.id + '/';
		var parameter = {};
		RequestAnularOEliminar("Esta seguro que desea eliminar el registro?", path, parameter, function () {
			self.consultar(self.contratoEmpresaVO.contrato_id());
		});
	}
	
	//consultar empresa selects
	/*self.empresa=function(dato){
		parameter='';
		path =path_principal+'/api/empresa/?sin_paginacion&'+dato+'=1&format=json';

		RequestGet(function (results,count) {

			self.lista_empresa(results);
		}, path, parameter,function(){},false);
	}*/

	//consultar el contrato actual
	self.contrato=function(dato){
		parameter={};
		path =path_principal+'/api/Contrato/'+dato+'/?format=json';

		RequestGet(function (results,count) {

			self.numero_c(results.numero);
			self.nombre_c(results.nombre);

			self.tituloPanel('Contrato N° '+self.numero_c()+' - '+self.nombre_c());
			//console.log("f_i:"+self.lista_contrato());
		}, path, parameter, function(){},false);
	}
}

var contratoEmpresa = new ContratoEmpresaViewModel();
ContratoEmpresaViewModel.errores_contratoEmpresa = ko.validation.group(contratoEmpresa.contratoEmpresaVO);

// contratoEmpresa.empresa('esContratante');//iniciamos la primera funcion

var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(contratoEmpresa,content);
ko.applyBindings(contratoEmpresa,header);
