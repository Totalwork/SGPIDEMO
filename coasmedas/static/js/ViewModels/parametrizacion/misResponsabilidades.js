function misResponsabilidadesViewModel(){
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	// self.checkall=ko.observable(false);
	self.num_registro=ko.observable('');

	/*self.misResponsabilidadesVO={
		id:ko.observable(0),
		nombre:ko.observable('').extend({ required: { message: '(*)Digite un nombre' } }),
		empresa_id:ko.observable().extend({ required: { message: '(*)Seleccione una empresa' } }),
		descripcion:ko.observable('')
	}*/

	self.detalle={
		nombre:ko.observable(''),
		empresa:ko.observable(''),
		descripcion:ko.observable('')
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

	/*self.abrir_modal = function () {
		self.limpiar();
		self.titulo('Registrar Responsabilidades');
		$('#modal_acciones').modal('show');
	}*/

	// //limpiar el modelo
	/*self.limpiar=function(){
		self.misResponsabilidadesVO.id(0);
		self.misResponsabilidadesVO.nombre('');
		self.misResponsabilidadesVO.empresa_id('');
		self.misResponsabilidadesVO.descripcion('');
		// check_eliminar(false)

		self.misResponsabilidadesVO.empresa_id.isModified(false);
	}*/

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			// self.filtro($('#txtBuscar').val());
			self.consultar(1);
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}

	// Consultar descuento
	self.consultar = function (pagina) {
		if (pagina > 0) {
			self.filtro($('#txtBuscar').val());

			path = path_principal+'/parametrizacion/lista_mis_responsabilidades/';
			parameter = {dato: self.filtro()
									// referencia: self.filtro_descuento.referencia(),
									// numero_contrato: self.filtro_descuento.num_contrato(),
									// concepto: self.filtro_descuento.concepto(),
									//page: pagina
									 };
			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos!=null && datos.length > 0) {
					self.mensaje('');
					self.num_registro("- N° de Registos: "+datos.length);
					self.listado(agregarOpcionesObservable(datos));

				} else {
					self.listado([]);
					self.num_registro("");
					self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				}
				/*if(datos.count > 10){
					self.llenar_paginacion(datos,pagina);
					$('#paginacion').show();
				}else{
					$('#paginacion').hide();
				}
				self.llenar_paginacion(datos,pagina);*/
				$('#modal_filtro').modal('hide');
				
			}, path, parameter,function(){cerrarLoading();},false);
		}
	}

	/*self.guardar=function(){
		if (misResponsabilidadesViewModel.errores_responsabilidades().length == 0){ //se activa las validaciones

			// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
			if(self.misResponsabilidadesVO.id()==0){
				
				// console.log("num_otro si:"+num);
				// console.log("nom:"+self.misResponsabilidadesVO.nombre()); return false;
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
					url:path_principal+'/api/Responsabilidades/',//url api
					parametros:self.misResponsabilidadesVO
					//alerta:false                       
				};

				//parameter =ko.toJSON(self.misResponsabilidadesVO);
				Request(parametros);
				// RequestFormData(parametros);
			}else{

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
					url:path_principal+'/api/Responsabilidades/'+self.misResponsabilidadesVO.id()+'/',
					parametros:self.misResponsabilidadesVO                        
				};
				Request(parametros);
			}
		} else {
			misResponsabilidadesViewModel.errores_responsabilidades.showAllMessages();
		}
	}*/

	// Para editar
	/*self.consultar_por_id = function (obj) {

		//alert(obj.id); return false;
		path =path_principal+'/api/Responsabilidades/'+obj.id+'/?format=json';
		parameter = {};
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar Responsabilidades');
			//console.log("asas: "+datos.tipo.id);

			self.misResponsabilidadesVO.id(datos.id);
			self.misResponsabilidadesVO.nombre(datos.nombre);
			self.misResponsabilidadesVO.empresa_id(datos.empresa.id);
			self.misResponsabilidadesVO.descripcion(datos.descripcion);

			$('#modal_acciones').modal('show');
		}, path, parameter);
	}*/

	// Para var el detalle de la responsabilidad
	/*self.consultar_por_id_detalle = function (obj) {

		path =path_principal+'/api/Responsabilidades/'+obj.id+'/?format=json';
		parameter = {};
		// self.limpiar();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.detalle.nombre(datos.nombre);
			self.detalle.empresa(datos.empresa.nombre);
			self.detalle.descripcion(datos.descripcion);

			$('#detalle_responsabilidades').modal('show');
		}, path, parameter);
	}*/

	// Eliminar Responsabilidades
	/*self.eliminar = function () {
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
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una responsabilidad para la eliminacion.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});

		}else{
			var path =path_principal+'/parametrizacion/eliminar_responsabilidades_lista/';
			var parameter = { lista: lista_id};
			RequestAnularOEliminar("Esta seguro que desea eliminar las responsabilidades seleccionadas?", path, parameter, function () {
				self.consultar(self.paginacion.pagina_actual());
				self.checkall(false);
			})
		}
	}*/

	/*self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado(), function(d) {

			d.eliminado(value);
		});
	});*/
}

var responsabilidades = new misResponsabilidadesViewModel();
// misResponsabilidadesViewModel.errores_responsabilidades = ko.validation.group(responsabilidades.misResponsabilidadesVO);

responsabilidades.consultar(1);//iniciamos la primera funcion
// responsabilidades.empresa('esContratista');

ko.applyBindings(responsabilidades);