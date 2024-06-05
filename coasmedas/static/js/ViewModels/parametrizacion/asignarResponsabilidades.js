function responsabilidadesFuncionarioViewModel(){
	
	var self = this;
	// self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.mensaje2=ko.observable('');
	// self.titulo=ko.observable('');
	// self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	//self.titulo_tab=ko.observable('');
	self.checkall2=ko.observable(false);

	self.id_empresa=ko.observable();
	self.funcionario_id=ko.observable(0);
	self.lista_funcionario=ko.observableArray([]);

	self.lista_responsabilidades=ko.observableArray([]);
	self.lista_responsabilidades2=ko.observableArray([]);

	self.guardar_responsabilidades = function () {
		var lista_id='';
		var count=0;
		ko.utils.arrayForEach(self.lista_responsabilidades(), function(d) {

			if(d.eliminado()==true){
				count=1;
				if(lista_id != ''){
					lista_id=lista_id+','+d.id;
				}else{
					lista_id=lista_id+d.id;
				}
			}
		});
		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione una responsabilidad para agregarla.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else if(self.funcionario_id() != 0){
			parameter={ responsabilidades_id: lista_id, funcionario_id:self.funcionario_id()};
			path =path_principal+'/parametrizacion/create_responsabilidades_funcionario/';

			RequestGet(function (data,success,message) {
				if (success=='ok') {
					mensajeExitoso(message);
					self.list_responsabilidades2();
					self.checkall(false);
				}else{
					mensajeError(message);
				}
				//console.log("nom:"+results);
			}, path, parameter);
		}else{
			mensajeInformativo('Seleccione un Funcionario.');
		}
	}

	self.eliminar_responsabilidades = function () {
		var lista_id=[];
		var count=0;
		ko.utils.arrayForEach(self.lista_responsabilidades2(), function(d) {

			if(d.eliminado()==true){
				count=1;
				//lista_id=lista_id+d.id+',';
				lista_id.push(d.id)
			}
		});
		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una responsabilidad para eliminarla.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else{
			var path =path_principal+'/parametrizacion/destroy_responsabilidades_funcionario/';
			var parameter = { lista: lista_id, id_funcionario:self.funcionario_id()};
			RequestAnularOEliminar("Esta seguro que desea eliminar las Responsabilidades seleccionadas?", path, parameter, function () {
				self.list_responsabilidades2();
				self.checkall2(false);
			})
		}
	}

	// OnChange de empresa_id
	/*self.empresa_id.subscribe(function (value) {
		
		if(value >0){
			self.list_funcionario(value);
			self.list_responsabilidades(value);
		}else{
			self.lista_funcionario([]);
			self.lista_responsabilidades([]);
			self.lista_responsabilidades2([]);
		}
	});*/

	// OnChange de funcionario_id
	self.funcionario_id.subscribe(function (value) {
		if(value >0){

			// self.list_responsabilidades(self.id_empresa());
			self.list_responsabilidades2();
		}else{
			self.lista_responsabilidades2([]);
		}
	});

	self.list_funcionario=function(empresa){
		path =path_principal+'/api/Funcionario/?empresa_filtro='+empresa;
		parameter={};
		RequestGet(function (results,success,message) {
			
			if (success == 'ok' && results.data!=null && results.data.length > 0) {
				self.mensaje('');
				self.lista_funcionario(agregarOpcionesObservable(results.data));
				self.lista_responsabilidades2([]);
			} else {
				self.lista_funcionario([]);
				self.lista_responsabilidades2([]);
				self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				//mensajeInformativo('No se encontraron registros');
			}
		}, path, parameter);
	}

  self.list_responsabilidades=function(empresa){
		path = path_principal+'/api/Responsabilidades/?sin_paginacion=1&id_empresa='+empresa;

		// Buscar las responsabilidades asignadas
		lista_id = ''
		ko.utils.arrayForEach(self.lista_responsabilidades2(), function(d) {
			if(lista_id == ''){
				lista_id = d.id;
			}else{
				lista_id = lista_id + ',' + d.id;
			}
		});
		//alert(lista_id);

		if(lista_id != ''){
			path += '&listado='+lista_id;
		}

		parameter = {};

		RequestGet(function (results,success,message) {

			if (success == 'ok' && results!=null && results.length > 0) {
				self.mensaje('');
				self.lista_responsabilidades(agregarOpcionesObservable(results));
			} else {
				self.lista_responsabilidades([]);
				self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
				//mensajeInformativo('No se encontraron registros');
			}
			//self.llenar_paginacion(datos,pagina);
		}, path, parameter,function(){cerrarLoading();},false);
	}

	self.list_responsabilidades2=function(){
		path =path_principal+'/api/Funcionario/'+self.funcionario_id()+'/';

		if (self.funcionario_id() != 0){

			parameter = {};
			RequestGet(function (results,success,message) {
				
				if (results.responsabilidades!=null && results.responsabilidades.length > 0) {
					self.mensaje2('');
					self.lista_responsabilidades2(agregarOpcionesObservable(results.responsabilidades));
				} else {
					self.lista_responsabilidades2([]);
					self.mensaje2(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
					//mensajeInformativo('No se encontraron registros');
				}
				//self.llenar_paginacion(datos,pagina);
			}, path, parameter,function(){cerrarLoading();self.list_responsabilidades(self.id_empresa());},false);
		}
	}

	self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.lista_responsabilidades(), function(d) {

			d.eliminado(value);
		});
	});

	self.checkall2.subscribe(function(value ){

		ko.utils.arrayForEach(self.lista_responsabilidades2(), function(d) {

			d.eliminado(value);
		});
	});
	// FIN - GESTION DE PROYECTO

	//consultar el contrato actual
	/*self.contrato=function(dato){
		parameter={};
		path =path_principal+'/api/Contrato/'+dato+'/?format=json';

		RequestGet(function (results,count) {

			self.numero_c(results.numero);
			self.nombre_c(results.nombre);
			self.lista_contrato(results.mcontrato);

			self.tituloPanel('Contrato N° '+self.numero_c()+' - '+self.nombre_c());
			//console.log("f_i:"+self.lista_contrato());
			self.macrocontrato_select(results.mcontrato.id);
			self.macrocontrato_select2(results.mcontrato.id);
		}, path, parameter, function(){});
	}*/
}

var responsabilidadesFuncionario = new responsabilidadesFuncionarioViewModel();
//responsabilidadesFuncionarioViewModel.errores_vigencia = ko.validation.group(responsabilidadesFuncionario.vigenciaVO);

// responsabilidadesFuncionario.list_funcionario();//iniciamos la primera funcion

ko.applyBindings(responsabilidadesFuncionario);
