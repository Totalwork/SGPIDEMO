function ContratoVigenciaViewModel(){
	var self = this;
	//self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	self.tituloPanel=ko.observable('');

	self.listado_empresa_contratista=ko.observableArray([]);

	// self.lista_sub_contratista=ko.observableArray([]);
	self.lista_sub_contratista2=ko.observableArray([]);

	// self.datos1=ko.observable('');
	// self.datos2=ko.observable('');

	self.numero_c=ko.observable('');
	self.nombre_c=ko.observable('');
	self.contrato_id=ko.observable(0);
	self.antiguo=ko.observable();
	self.soporte=ko.observable('');

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

	self.contratoCesion={
		id:ko.observable(0),
		contrato_id:ko.observable(),
		contratista_nuevo_id:ko.observable().extend({ required: { message: '(*)Seleccione un contratista' } }),
		contratista_antiguo_id:ko.observable(),
		fecha:ko.observable('').extend({ required: { message: '(*)Seleccione una fecha' } }),
		soporte:ko.observable('')
	}

	self.abrir_modal = function () {
		self.limpiar();
		self.titulo('Registrar una Cesión de Contrato');
		$('#modal_acciones').modal('show');
	}

	// //limpiar el modelo
	self.limpiar=function(){
		self.contratoCesion.id(0);
		self.contratoCesion.contrato_id('');
		self.contratoCesion.contratista_nuevo_id('');
		self.contratoCesion.contratista_antiguo_id('');
		self.contratoCesion.fecha('');
		self.contratoCesion.soporte('');
		$('#archivo').fileinput('reset');
		$('#archivo').val('');
		// check_eliminar(false)

		self.contratoCesion.contratista_nuevo_id.isModified(false);
	}

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#nom_nit1').val());
			self.list_sub_contratista2();
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}

	self.list_sub_contratista2=function(){
		path =path_principal+'/api/Contrato_cesion/?id_contrato='+self.contrato_id();

		self.filtro($('#txtBuscar').val());
		parameter={};
		if(self.filtro()){
			parameter = {dato:self.filtro()};
		}

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
		}, path, parameter,function(){cerrarLoading();},false);
	}

	//consultar contratista y contratante selects
	self.empresa=function(dato){
		parameter='';
		// path =path_principal+'/api/empresa/?sin_paginacion&'+dato+'=1&format=json';

		path =path_principal+'/api/Empresa_contrato/?sin_paginacion&format=json';
		parameter = { contrato_contratista:true};

		RequestGet(function (results,success,message) {

			self.listado_empresa_contratista(results);

			/*if(dato == 'esContratista'){
				self.listado_empresa_contratista(results);

			}else if(dato == 'esContratante'){
				self.listado_empresa_contratante(results);
			}*/
		}, path, parameter,function(){},false);
	}

	//consultar el contrato actual
	self.contrato=function(dato){
		parameter={};
		path =path_principal+'/api/Contrato/'+dato+'/?format=json';

		RequestGet(function (results,count) {

			self.numero_c(results.numero);
			self.nombre_c(results.nombre);
			self.antiguo(results.contratista.id);

			self.tituloPanel('Contrato N° '+self.numero_c()+' - '+self.nombre_c());
		}, path, parameter,function(){},false);
	}

	self.guardar=function(){
		if (ContratoVigenciaViewModel.errores_vigencia().length == 0){ //se activa las validaciones

			// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
			if(self.contratoCesion.id()==0){
				self.contratoCesion.contratista_antiguo_id(self.antiguo());
				self.contratoCesion.contrato_id(self.contrato_id());
				
				// console.log("num_otro si:"+num);
				// console.log("nom:"+self.contratoCesion.nombre()); return false;
				var parametros={
					callback:function(datos, estado, mensaje){

						if (estado=='ok') {

							$('#modal_acciones').modal('hide');
							self.limpiar();
							self.list_sub_contratista2();
						}else{
							mensajeError(mensaje);
						}
					}, //funcion para recibir la respuesta 
					url:path_principal+'/api/Contrato_cesion/',//url api
					parametros:self.contratoCesion
					//alerta:false                       
				};

				//parameter =ko.toJSON(self.contratoCesion);
				//Request(parametros);
				RequestFormData(parametros);
			}else{
				//console.log('entro2');
				if($('#archivo')[0].files.length==0){
					self.contratoCesion.soporte('');
				}
				self.contratoCesion.contrato_id(self.contrato_id());

				var parametros={
					metodo:'PUT',
					callback:function(datos, estado, mensaje){

						if (estado=='ok') {
							self.filtro("");
							self.list_sub_contratista2();
							$('#modal_acciones').modal('hide');
							self.limpiar();
						}

					},//funcion para recibir la respuesta 
					url:path_principal+'/api/Contrato_cesion/'+self.contratoCesion.id()+'/',
					parametros:self.contratoCesion
				};
				RequestFormData(parametros);
			}
		} else {
			ContratoVigenciaViewModel.errores_vigencia.showAllMessages();
		}
	}

	/*self.eliminar = function (obj) {

		var path =path_principal+'/api/Contrato_cesion/'+ obj.id + '/';
		var parameter = {};
		RequestAnularOEliminar("Esta seguro que desea eliminar el registro?", path, parameter, function () {
			self.list_sub_contratista2();
		});
	}*/

	self.eliminar = function () {
		var lista_id=[];
		var count=0;
		ko.utils.arrayForEach(self.lista_sub_contratista2(), function(d) {

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
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contratista para la eliminacion.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});

		}else{
			var path =path_principal+'/contrato/eliminar_contrato_cesion/';
			var parameter = { lista: lista_id};
			RequestAnularOEliminar("Esta seguro que desea eliminar los contratistas seleccionados?", path, parameter, function () {
				self.list_sub_contratista2();
				self.checkall(false);
			})
		}
	}

	// Para editar
	self.consultar_por_id = function (obj) {

		//alert(obj.id); return false;
		path =path_principal+'/api/Contrato_cesion/'+obj.id+'/?format=json';
		parameter = {};
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar Cesión de Contrato');
			//console.log("asas: "+datos.tipo.id);

			self.contratoCesion.id(datos.id);
			self.contratoCesion.fecha(datos.fecha);
			self.contratoCesion.contratista_nuevo_id(datos.contratista_nuevo.id);
			self.contratoCesion.contratista_antiguo_id(datos.contratista_antiguo.id);
			self.contratoCesion.soporte(datos.soporte);
			self.soporte(datos.soporte);
			//self.habilitar_campos(true);
			$('#modal_acciones').modal('show');
		}, path, parameter);
	}

	self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.lista_sub_contratista2(), function(d) {

			d.eliminado(value);
		});
	});
}

var contratoVigencia = new ContratoVigenciaViewModel();
ContratoVigenciaViewModel.errores_vigencia = ko.validation.group(contratoVigencia.contratoCesion);

//contratoVigencia.list_sub_contratista2();//iniciamos la primera funcion
contratoVigencia.empresa('esContratista');

ko.applyBindings(contratoVigencia);