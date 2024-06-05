function ContratoVigenciaViewModel(){
	var self = this;
	//self.listado=ko.observableArray([]);
	self.mensaje1=ko.observable('');
	self.mensaje2=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	self.tituloPanel=ko.observable('');
	self.checkall2=ko.observable(false);

	self.listado_empresa_contratista=ko.observableArray([]);

	self.lista_sub_contratista=ko.observableArray([]);
	self.lista_sub_contratista2=ko.observableArray([]);

	self.datos1=ko.observable('');
	self.datos2=ko.observable('');

	self.numero_c=ko.observable('');
	self.nombre_c=ko.observable('');
	self.contrato_id=ko.observable(0);
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

	self.sub_contratistaVO={
		id:ko.observable(0),
		contrato_id:ko.observable(),
		empresa_id:ko.observable().extend({ required: { message: '(*)Seleccione un contratista' } }),
		soporte:ko.observable('')
	}

	self.abrir_modal = function () {
		self.limpiar();
		self.titulo('Registrar Sub-Contratista');
		$('#modal_acciones').modal('show');
	}

	// //limpiar el modelo
	self.limpiar=function(){
		self.sub_contratistaVO.id(0);
		self.sub_contratistaVO.contrato_id('');
		self.sub_contratistaVO.empresa_id('');
		self.sub_contratistaVO.soporte('');
		$('#archivo').fileinput('reset');
		$('#archivo').val('');
		// check_eliminar(false)

		self.sub_contratistaVO.empresa_id.isModified(false);
	}

	/*self.consulta_enter2 = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#nom_nit1').val());
			self.list_sub_contratista();
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}*/

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#nom_nit1').val());
			self.list_sub_contratista2();
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}

	self.guardar_sub_contratista = function () {
		var lista_id='';
		var count=0;
		ko.utils.arrayForEach(self.lista_sub_contratista(), function(d) {

			if(d.eliminado()==true){
				count=1;
				lista_id=lista_id+d.id+',';
			}
		});
		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un contratista para agregarlo.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else{
			parameter={ empresa_id: lista_id, contrato_id:self.contrato_id()};
			path =path_principal+'/contrato/create_sub_contratista/';

			RequestGet(function (data,success,message) {
				if (success=='ok') {
					mensajeExitoso(message);
					self.list_sub_contratista2();
					self.checkall(false);
				}else{
					mensajeError(message);
				}
				//console.log("nom:"+results);
			}, path, parameter);
		}
	}

	/*self.eliminar_sub_contratista = function () {
		var lista_id=[];
		var count=0;
		ko.utils.arrayForEach(self.lista_sub_contratista2(), function(d) {

			if(d.eliminado()==true){
				count=1;

				// lista_id=lista_id+d.id;
				lista_id.push(d.id)
				//lista_id.push({id:d.id})
			}
		});
		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un Subcontratista para eliminarlo.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else{
			var path =path_principal+'/contrato/eliminar_sub_contratista/';
			var parameter = { lista: lista_id, contrato:self.contrato_id()};
			RequestAnularOEliminar("Esta seguro que desea eliminar los Subcontratista seleccionados?", path, parameter, function () {
				self.list_sub_contratista2();
				self.checkall2(false);
			})
		}
	}*/

	// 
  	/*self.list_sub_contratista=function(){
		path =path_principal+'/api/empresa/?format=json';

		//var contrato = self.macrocontrato_select();
		var nom_nit = $('#nom_nit1').val();
		
		if(nom_nit){
			parameter = {esContratista:1, dato:nom_nit};
		}else{
			parameter = {esContratista:1};
		}
		

		RequestGet(function (results,success,message) {
			//console.log("ddd;"+$('#nom_nit1').val());
			if (success == 'ok' && results.data!=null && results.data.length > 0) {
				self.mensaje1('');
				self.lista_sub_contratista(agregarOpcionesObservable(results.data));
			} else {
				self.lista_sub_contratista([]);
				self.mensaje1(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}
			//self.llenar_paginacion(datos,pagina);
		}, path, parameter);
	}*/

	self.list_sub_contratista2=function(){
		path =path_principal+'/api/Sub_contratista/?id_contrato='+self.contrato_id();

		self.filtro($('#txtBuscar').val());
		parameter={};
		if(self.filtro()){
			parameter = {dato:self.filtro()};
		}

		RequestGet(function (results,success,message) {
			
			if (success == 'ok' && results.data!=null && results.data.length > 0) {
				self.mensaje2('');
				self.lista_sub_contratista2(agregarOpcionesObservable(results.data));
			} else {
				self.lista_sub_contratista2([]);
				self.mensaje2(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				//self.mensaje2('No se encontraron registros');
			}
			//self.llenar_paginacion(datos,pagina);
		}, path, parameter,function(){cerrarLoading();},false);
	}

	self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.lista_sub_contratista2(), function(d) {

			d.eliminado(value);
		});
	});

	/*self.checkall2.subscribe(function(value ){

		ko.utils.arrayForEach(self.lista_sub_contratista2(), function(d) {

			d.eliminado(value);
		});
	});*/
	// FIN - GESTION DE PROYECTO

	//consultar contratista y contratante selects
	self.empresa=function(dato){
		parameter='';
		path =path_principal+'/api/empresa/?sin_paginacion&'+dato+'=1&format=json';

		// path =path_principal+'/api/Empresa_contrato/?sin_paginacion&format=json';
		parameter = { contrato_contratista:true};

		RequestGet(function (results,success,message) {

			// alert(results);
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

			self.tituloPanel('Contrato N° '+self.numero_c()+' - '+self.nombre_c());
			//console.log("f_i:"+self.lista_contrato());
		}, path, parameter, function(){},false);
	}

	self.guardar=function(){
		if (ContratoVigenciaViewModel.errores_vigencia().length == 0){ //se activa las validaciones

			// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
			if(self.sub_contratistaVO.id()==0){

				self.sub_contratistaVO.contrato_id(self.contrato_id());
				
				// console.log("num_otro si:"+num);
				// console.log("nom:"+self.sub_contratistaVO.nombre()); return false;
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
					url:path_principal+'/api/Sub_contratista/',//url api
					parametros:self.sub_contratistaVO
					//alerta:false                       
				};

				//parameter =ko.toJSON(self.sub_contratistaVO);
				//Request(parametros);
				RequestFormData(parametros);
			}else{

				if($('#archivo')[0].files.length==0){
					self.sub_contratistaVO.soporte('');
				}
				self.sub_contratistaVO.contrato_id(self.contrato_id());

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
					url:path_principal+'/api/Sub_contratista/'+self.sub_contratistaVO.id()+'/',
					parametros:self.sub_contratistaVO                        
				};
				RequestFormData(parametros);
			}
		} else {
			ContratoVigenciaViewModel.errores_vigencia.showAllMessages();
		}
	}

	/*self.eliminar = function (obj) {

		var path =path_principal+'/api/Sub_contratista/'+ obj.id + '/';
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
			var path =path_principal+'/contrato/eliminar_sub_contratista/';
			var parameter = { lista: lista_id};
			RequestAnularOEliminar("Esta seguro que desea eliminar los contratistas seleccionados?", path, parameter, function () {
				self.list_sub_contratista2();
				//self.checkall(false);
			})
		}
	}

	// Para editar
	self.consultar_por_id = function (obj) {

		//alert(obj.id); return false;
		path =path_principal+'/api/Sub_contratista/'+obj.id+'/?format=json';
		parameter = {};
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar Sub-Contratista');
			//console.log("asas: "+datos.tipo.id);

			self.sub_contratistaVO.id(datos.id);
			//self.sub_contratistaVO.tipo_id(datos.tipo.id);
			self.sub_contratistaVO.empresa_id(datos.empresa.id);
			self.sub_contratistaVO.soporte(datos.soporte);
			self.soporte(datos.soporte);
			//self.habilitar_campos(true);
			$('#modal_acciones').modal('show');
		}, path, parameter);
	}
}

var contratoVigencia = new ContratoVigenciaViewModel();
ContratoVigenciaViewModel.errores_vigencia = ko.validation.group(contratoVigencia.sub_contratistaVO);

//contratoVigencia.list_sub_contratista2();//iniciamos la primera funcion
contratoVigencia.empresa('esContratista');

ko.applyBindings(contratoVigencia);