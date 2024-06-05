function ContratoVigenciaViewModel(){
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.mensaje2=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	//self.titulo_tab=ko.observable('');
	self.checkall2=ko.observable(false);

	self.macrocontrato_select=ko.observable(0);
	//self.contratista=ko.observable(0);
	self.departamento=ko.observable(0);
	self.municipio=ko.observable(0);

	self.macrocontrato_select2=ko.observable(0);
	self.contratista2=ko.observable(0);
	self.departamento2=ko.observable(0);
	self.municipio2=ko.observable(0);
	
	self.validacion_mcontrato=ko.observable(false);
	//self.tipos=ko.observableArray([]);
	//self.lista_otrosi_contrato=ko.observableArray([]);

	self.lista_contrato=ko.observableArray([]);
	//self.listado_contratista=ko.observableArray([]);
	self.departamento_select=ko.observableArray([]);
	self.listado_municipio=ko.observableArray([]);
	self.lista_proyecto=ko.observableArray([]);

	self.listado_contratista2=ko.observableArray([]);
	self.departamento_select2=ko.observableArray([]);
	self.listado_municipio2=ko.observableArray([]);
	self.lista_proyecto2=ko.observableArray([]);

	self.numero_c=ko.observable('');
	self.nombre_c=ko.observable('');
	self.tituloPanel=ko.observable('');
	self.contrato_id=ko.observable(0);

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

	self.guardar_proyecto = function () {
		var lista_id='';
		var count=0;
		ko.utils.arrayForEach(self.lista_proyecto(), function(d) {

			if(d.eliminado()==true){
				count=1;
				lista_id=lista_id+d.id+',';
			}
		});
		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un proyecto para agregarlo.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else{
			parameter={ proyecto_id: lista_id, contrato_id:self.contrato_id()};
			path =path_principal+'/contrato/create_proyecto_contrato/';

			RequestGet(function (data,success,message) {
				if (success=='ok') {
					mensajeExitoso(message);
					self.list_proyecto2(1);
					self.checkall(false);
				}else{
					mensajeError(message);
				}
				//console.log("nom:"+results);
			}, path, parameter, function(){});
		}
	}

	self.eliminar_proyecto = function () {
		var lista_id=[];
		var count=0;
		ko.utils.arrayForEach(self.lista_proyecto2(), function(d) {

			if(d.eliminado()==true){
				count=1;
				//lista_id=lista_id+d.id+',';
				lista_id.push({id:d.id})
			}
		});
		if(count==0){

			$.confirm({
				title:'Informativo',
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un proyecto para eliminarlo.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else{
			var path =path_principal+'/contrato/eliminar_proyecto/';
			var parameter = { lista: lista_id, contrato:self.contrato_id()};
			RequestAnularOEliminar("Esta seguro que desea eliminar los proyectos seleccionados?", path, parameter, function () {
				//self.list_proyecto();
				self.list_proyecto2(1);
				self.checkall2(false);
			})
		}
	}

	/*self.consultar_macrocontrato=function(){
		path =path_principal+'/proyecto/filtrar_proyectos/?tipo='+self.tipo.m_contrato();
		parameter={};
		RequestGet(function (results,count) {
			self.lista_contrato(results.macrocontrato);
		}, path, parameter);
	}*/

	// INICIO - GESTION DE PROYECTO
	// OnChange de m-contrato1
	self.macrocontrato_select.subscribe(function (value) {
		if(value >0){

			self.filtros3(value,0,self.departamento(),1);
		}else{
			//self.listado_contratista([]);
			self.departamento_select([]);
			self.listado_municipio([]);
		}
	});

	// OnChange de m-contrato2
	self.macrocontrato_select2.subscribe(function (value) {
		if(value >0){

			self.filtros3(value,self.contratista2(),self.departamento2(),2);
		}else{
			self.listado_contratista2([]);
			self.departamento_select2([]);
			self.listado_municipio2([]);
		}
	});

	// OnChange de contratista2
	self.contratista2.subscribe(function (value) {
		if(value >0){

			self.filtros(self.macrocontrato_select2(),value,2);
		}else{

			self.departamento_select2([]);
			self.listado_municipio2([]);
		}
	});

	// OnChange de departamento1
	self.departamento.subscribe(function (value) {
		if(value >0){

			self.filtros2(self.macrocontrato_select(),value,1);
		}else{
			self.listado_municipio([]);
		}
	});

	// OnChange de departamento2
	self.departamento2.subscribe(function (value) {
		if(value >0){

			self.filtros2(self.macrocontrato_select2(),self.contratista2(),value,2);
		}else{
			self.listado_municipio2([]);
		}
	});

	self.filtros=function(contrato,contratista,num){
		tipos=self.tipo.contratoProyecto();
		path =path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+contrato+'&contratista='+contratista+'&tipo='+tipos;
		parameter='';
		RequestGet(function (results,count) {
			// num = 1 igual al buscador de proyectos de la izquierda y 2 = de la derecha
			if(num == 1){
				self.departamento_select(results.departamento);
				self.listado_municipio(results.municipio);
				//self.descargoVO.proyecto(results.proyecto);
			}else if(num == 2){
				self.departamento_select2(results.departamento);
				self.listado_municipio2(results.municipio);
			}
		}, path, parameter);
	}

	self.filtros2=function(contrato,contratista,departamento,num){
		tipos=self.tipo.contratoProyecto();
		path =path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+contrato+'&contratista='+contratista+'&departamento='+departamento+'&tipo='+tipos;
		parameter='';
		RequestGet(function (results,count) {

			if(num == 1){
				//self.listado_contratista(results.contratista);
				self.listado_municipio(results.municipio);
				//self.descargoVO.proyecto(results.proyecto);
			}else if(num == 2){

				self.listado_municipio2(results.municipio);
			}
		}, path, parameter);
	}

	self.filtros3=function(contrato,contratista,departamento,num){
		tipos=self.tipo.contratoProyecto();

		path =path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+contrato+'&departamento='+departamento+'&tipo='+tipos;
		if(contratista != 0){
			path += '&contratista='+contratista;
		}
		parameter={};

		RequestGet(function (results,count) {
			// num = 1 igual al buscador de proyectos de la izquierda y 2 = de la derecha
			if(num == 1){
				//self.listado_contratista(results.contratista);
				self.departamento_select(results.departamento);
				self.listado_municipio(results.municipio);
			}else if(num == 2){
				self.listado_contratista2(results.contratista);
				self.departamento_select2(results.departamento);
				self.listado_municipio2(results.municipio);
			}
			//self.descargoVO.proyecto(results.proyecto);
		}, path, parameter);
	}

  self.list_proyecto=function(){
		path =path_principal+'/api/Proyecto/?';
		var lista_id = '';

		var contrato = self.macrocontrato_select();
		//var contratista = self.contratista();
		var departamento = self.departamento();
		var municipio = self.municipio();

		if(contrato == 0){
			//if(n == 0){
				mensajeInformativo('Seleccione un M-Contrato');
			//}
		}else{
			path += 'contrato='+contrato;

			if(departamento != 0){
				path += '&departamento_id='+departamento;
			}
			if(municipio != 0){
				path += '&municipio_id='+municipio;
			}

			// Buscar los proyectos asignados
			ko.utils.arrayForEach(self.lista_proyecto2(), function(d) {
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

			parameter = {
				ignorePagination:true,
				lite:2
			};

			RequestGet(function (results,success,message) {

				if (success == 'ok' && results!=null && results.length > 0) {
					self.mensaje('');
					self.lista_proyecto(agregarOpcionesObservable(results));
				} else {
					self.lista_proyecto([]);
					self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
					//mensajeInformativo('No se encontraron registros');
				}
				//self.llenar_paginacion(datos,pagina);
			}, path, parameter,function(){cerrarLoading();},false);
		}
	}

	self.list_proyecto2=function(v){
		path =path_principal+'/api/Proyecto/?format=json';

		var contrato = self.macrocontrato_select2();
		var contratista = self.contratista2();
		var departamento = self.departamento2();
		var municipio = self.municipio2();
		var contrato_obra = self.contrato_id();

		//if(contrato == 0 || contratista == 0){
			//mensajeError('Seleccione un M-Contrato y un contratista');
		//}else{
			//path += 'contrato='+contrato+'&id_contratista='+contratista;
			if(contrato != 0){
				path += '&contrato='+contrato;
			}
			if(contratista != 0){
				path += '&id_contratista='+contratista;
			}
			if(departamento != 0){
				path += '&departamento_id='+departamento;
			}
			if(municipio != 0){
				path += '&municipio_id='+municipio;
			}
			if(contrato_obra != 0){
				path += '&contrato_obra='+contrato_obra;
			}

			parameter = {
				ignorePagination:true,
				lite:2
			};
			RequestGet(function (results,success,message) {
				
				if (success == 'ok' && results!=null && results.length > 0) {
					self.mensaje2('');
					self.lista_proyecto2([]);
					self.lista_proyecto2(agregarOpcionesObservable(results));
				} else {
					self.lista_proyecto2([]);
					self.mensaje2(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
					//mensajeInformativo('No se encontraron registros');
				}
				//self.llenar_paginacion(datos,pagina);
			}, path, parameter,function(){
					cerrarLoading();
					if(v == 1){
						self.list_proyecto();
					}
			},false);
		//}
	}

	self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.lista_proyecto(), function(d) {

			d.eliminado(value);
		});
	});

	self.checkall2.subscribe(function(value ){

		ko.utils.arrayForEach(self.lista_proyecto2(), function(d) {

			d.eliminado(value);
		});
	});
	// FIN - GESTION DE PROYECTO

	//consultar el contrato actual
	self.contrato=function(dato){
		parameter={
			lite:2,
			sin_paginacion:true
		};
		path =path_principal+'/api/Contrato/'+dato+'/?format=json';

		var id_mcontrato = 0;
		RequestGet(function (results,count) {

			self.numero_c(results.numero);
			self.nombre_c(results.nombre);

			self.tituloPanel('Contrato N° '+self.numero_c()+' - '+self.nombre_c());
			//console.log("f_i:"+self.lista_contrato());

			if(results.mcontrato){
				self.validacion_mcontrato(true);
				id_mcontrato = results.mcontrato.id;
				self.lista_contrato(results.mcontrato);
			}
		}, path, parameter, function(){
			// self.macrocontrato_select(id_mcontrato);
			// self.macrocontrato_select2(id_mcontrato);
		},false);
	}
}

var contratoVigencia = new ContratoVigenciaViewModel();
// ContratoVigenciaViewModel.errores_vigencia = ko.validation.group(contratoVigencia.vigenciaVO);

//contratoVigencia.consultar_macrocontrato();//iniciamos la primera funcion

ko.applyBindings(contratoVigencia);