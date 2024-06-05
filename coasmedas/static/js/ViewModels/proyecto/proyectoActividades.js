function proyectoActividadesViewModel(){
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	self.num_registro=ko.observable('');

	self.id_proyecto=ko.observable(0);

	self.departamento_p=ko.observable('');
	self.municipio_c=ko.observable('');
	self.nombre_p=ko.observable('');
	self.tituloPanel=ko.observable('');

	self.proyectoActividadesVO={
		id:ko.observable(0),
		proyecto_id:ko.observable(0),
		fecha:ko.observable('').extend({ required: { message: '(*)Seleccione una fecha' } }),
		descripcion:ko.observable('').extend({ required: { message: '(*)Digite una descripción' } }),
	}

	self.detalle={
		proyecto_nombre:ko.observable(''),
		fecha:ko.observable(''),
		descripcion:ko.observable('')
	}

	// //limpiar el modelo
	self.limpiar=function(){
		self.proyectoActividadesVO.id(0);
		self.proyectoActividadesVO.proyecto_id(0);
		self.proyectoActividadesVO.fecha('');
		self.proyectoActividadesVO.descripcion('');
		// check_eliminar(false)

		self.proyectoActividadesVO.fecha.isModified(false);
		self.proyectoActividadesVO.descripcion.isModified(false);
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
		self.consultar(pagina, self.id_proyecto());
	});
	//Funcion para crear la paginacion
	self.llenar_paginacion = function (data,pagina) {
		self.paginacion.pagina_actual(pagina);
		self.paginacion.total(data.count);
		self.paginacion.cantidad_por_paginas(resultadosPorPagina);
	}

	self.abrir_modal = function () {
		self.limpiar();
		self.titulo('Registrar Actividades');
		$('#modal_acciones').modal('show');
	}

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			// self.filtro($('#txtBuscar').val());
			self.consultar(1, self.id_proyecto() );
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}

	// Consultar descuento
	self.consultar = function (pagina, proyecto_id) {
		if (pagina > 0) {
			self.filtro($('#txtBuscar').val());

			path = path_principal+'/api/Proyecto_actividades/?format=json&id_proyecto='+proyecto_id;
			parameter = {dato: self.filtro(),
									// numero_contrato: self.filtro_descuento.num_contrato(),
									// concepto: self.filtro_descuento.concepto(),
									page: pagina
									};
			RequestGet(function (datos, estado, mensage) {

				if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
					self.mensaje('');
					self.num_registro("- N° de Registos: "+datos.data.length);
					self.listado(agregarOpcionesObservable(datos.data));
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
				
			}, path, parameter,function(){cerrarLoading(); self.consultar_proyecto(self.id_proyecto());},false);
		}
	}

	self.guardar=function(){
		if (proyectoActividadesViewModel.errores_actividades().length == 0){ //se activa las validaciones

			// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
			if(self.proyectoActividadesVO.id()==0){
				
				self.proyectoActividadesVO.proyecto_id(self.id_proyecto());
				// console.log("nom:"+self.proyectoActividadesVO.nombre()); return false;
				var parametros={
					callback:function(datos, estado, mensaje){

						if (estado=='ok') {

							$('#modal_acciones').modal('hide');
							self.limpiar();
							self.consultar(1, self.id_proyecto());
						}else{
							mensajeError(mensaje);
						}
					}, //funcion para recibir la respuesta 
					url:path_principal+'/api/Proyecto_actividades/',//url api
					parametros:self.proyectoActividadesVO
					//alerta:false                       
				};

				//parameter =ko.toJSON(self.proyectoActividadesVO);
				Request(parametros);
				// RequestFormData(parametros);
			}else{

				var parametros={
					metodo:'PUT',
					callback:function(datos, estado, mensaje){

						if (estado=='ok') {
							self.filtro("");
							self.consultar(self.paginacion.pagina_actual(), self.id_proyecto());
							$('#modal_acciones').modal('hide');
							self.limpiar();
						}

					},//funcion para recibir la respuesta 
					url:path_principal+'/api/Proyecto_actividades/'+self.proyectoActividadesVO.id()+'/',
					parametros:self.proyectoActividadesVO                        
				};
				Request(parametros);
			}
		} else {
			proyectoActividadesViewModel.errores_actividades.showAllMessages();
		}
	}

	// Para editar
	self.consultar_por_id = function (obj) {

		//alert(obj.id); return false;
		path =path_principal+'/api/Proyecto_actividades/'+obj.id+'/?format=json';
		parameter = {};
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar Actividades');
			//console.log("asas: "+datos.tipo.id);

			self.proyectoActividadesVO.id(datos.id);
			self.proyectoActividadesVO.fecha(datos.fecha);
			self.proyectoActividadesVO.proyecto_id(datos.proyecto.id);
			self.proyectoActividadesVO.descripcion(datos.descripcion);

			$('#modal_acciones').modal('show');
		}, path, parameter);
	}

	// Para var el detalle de la responsabilidad
	self.consultar_por_id_detalle = function (obj) {

		path =path_principal+'/api/Proyecto_actividades/'+obj.id+'/?format=json';
		parameter = {};
		// self.limpiar();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.detalle.fecha(datos.fecha);
			self.detalle.proyecto_nombre(datos.proyecto.nombre);
			self.detalle.descripcion(datos.descripcion);

			$('#detalle_actividades').modal('show');
		}, path, parameter);
	}

	// Para editar
	self.consultar_proyecto = function (id) {

		//alert(obj.id); return false;
		path =path_principal+'/api/Proyecto/'+id+'/?format=json';
		parameter = {};
		RequestGet(function (datos, estado, mensaje) {

			self.nombre_p(datos.nombre);
			self.municipio_c(datos.municipio.nombre);
			self.departamento_p(datos.municipio.departamento.nombre);

			// self.proyectoActividadesVO.id(datos.id);
			// self.proyectoActividadesVO.fecha(datos.fecha);
			// self.proyectoActividadesVO.proyecto_id(datos.proyecto.id);
			// self.proyectoActividadesVO.descripcion(datos.descripcion);
		}, path, parameter);
	}

	// Eliminar Acividades
	self.eliminar = function () {
		var lista_id=[];
		var count=0;
		ko.utils.arrayForEach(self.listado(), function(d) {

			if(d.eliminado()==true){
				count=1;

				lista_id.push(
					d.id
				)

				// if(lista_id != ''){
				// 	lista_id = lista_id + ',' + d.id
				// }else{
				// 	lista_id = lista_id+d.id
				// }
				
				// lista_id.push({
				// 	id:d.id
				// })
			}
		});
		//console.log("asas:"+lista_id[0].id+" - "+lista_id[1].id);

		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una actividad para eliminarla.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});

		}else{
			var path =path_principal+'/proyecto/destroy_proyecto_actividades/';
			var parameter = { lista: lista_id};
			RequestAnularOEliminar("Esta seguro que desea eliminar las actividades seleccionadas?", path, parameter, function () {
				self.consultar(self.paginacion.pagina_actual(), self.id_proyecto());
				self.checkall(false);
			})
		}
	}

	self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado(), function(d) {

			d.eliminado(value);
		});
	});
}

var proyectoActividades = new proyectoActividadesViewModel();
proyectoActividadesViewModel.errores_actividades = ko.validation.group(proyectoActividades.proyectoActividadesVO);

// proyectoActividades.consultar(1);//iniciamos la primera funcion
// proyectoActividades.empresa('esContratista');

ko.applyBindings(proyectoActividades);