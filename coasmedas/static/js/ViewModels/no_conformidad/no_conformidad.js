function NoConformidadViewModel(){
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
	self.checkall=ko.observable(false);
	self.num_registro=ko.observable('');
    self.soporte=ko.observable('');

	self.estado=ko.observable(0);
	self.soporte_corregida=ko.observable('');
	self.titulo_correccion=ko.observable('');

	// self.mensaje_cont=ko.observable('');//mensaje para el modal de contrato
	// self.lista_contrato=ko.observableArray([]);
	// self.mensaje_beneficiario=ko.observable('');//mensaje para el modal de beneficiario
	// self.lista_beneficiario=ko.observableArray([]);

	// self.nombre_beneficiario=ko.observable('');

	// self.listado_cesion_c=ko.observableArray([]);

	// self.listado_nombre_giro=ko.observableArray([]);
	// self.listado_tipo_cuenta=ko.observableArray([]);
	// self.dysplay_giro=ko.observable(false);
	// self.dysplay_giro_checkbox=ko.observable(false);
	// self.checkall_giro=ko.observable(false);
	self.mensaje_guardar=ko.observable('');

	// Filtro de Proyecto
	self.macrocontrato_select=ko.observable(0);
	self.contratista_select=ko.observable(0);
	self.departamento_select=ko.observable(0);
	self.municipio_select=ko.observable(0);
	self.proyecto_select=ko.observable(0);
	self.macrocontrato_list=ko.observable([]);
	self.contratista_list=ko.observable([]);
	self.departamento_list=ko.observable([]);
	self.municipio_list=ko.observable([]);
	self.proyecto_list=ko.observable([]);
	self.showRow = ko.observable(false);
	self.nombre_proyecto = ko.observable('');
	self.cambiar_contratista=ko.observable(0);
	self.cambiar_departamento=ko.observable(0);
	self.cambiar_municipio=ko.observable(0);

	// Filtro Usuario
	self.listado_empresa_contratante=ko.observable([]);
	self.id_empresa = ko.observable(0);
	self.nombre_usuario = ko.observable('');
	self.nom_usuario = ko.observable('');
	self.list_usuario=ko.observable([]);
	self.id_detectada=ko.observable(0);
	self.ver_usuario=ko.observable(false);
	self.mensaje_usuario=ko.observable('');

	/*self.buscar_contrato={
		tipo_contrato:ko.observable('').extend({ required: { message: '(*)Seleccione un tipo' } }),
		nom_num_contrato:ko.observable('')//.extend({ required: { message: '(*)Digite nombre o número del contrato' } })
	}*/
	/*self.buscar_beneficiario={
		nit_nom:ko.observable('').extend({ required: { message: '(*)Digite un nombre o nit' } }),
		tipo:ko.observable('esContratista')//.extend({ required: { message: '(*)Digite nombre o número del contrato' } })
	}*/

	// Local
	/*self.tablaForanea={
		encabezadoGiros:ko.observable(20),
		factura:ko.observable(1086),
		cesion:ko.observable(1088),
		descuento:ko.observable(1089)
	};*/
	// Maquina Virtual
	/*self.tablaForanea={
		encabezadoGiros:ko.observable(38),
		factura:ko.observable(140),
		cesion:ko.observable(142),
		descuento:ko.observable(143)
    };*/

	self.NoConformidadVO={
		id:ko.observable(0),
		proyecto_id:ko.observable().extend({ required: { message: '(*)Seleccione un Proyecto' } }),
		usuario_id:ko.observable(0),
		estado_id:ko.observable(self.estado()),
		detectada_id:ko.observable().extend({ required: { message: '(*)Seleccione un funcionario' } }),
		descripcion_no_corregida:ko.observable('').extend({ required: { message: '(*)Digite la descripcion de la No Conformidad' } }),
		descripcion_corregida:ko.observable(''),
		fecha_no_corregida:ko.observable('').extend({ required: { message: '(*)Seleccione una fecha' } }),
		fecha_corregida:ko.observable(''),
		terminada:ko.observable(0),
		estructura:ko.observable('').extend({ required: { message: '(*)Digite la estructura de la No Conformidad' } }),
		primer_correo:ko.observable(''),
        segundo_correo:ko.observable(''),
        tercer_correo:ko.observable(''),
		foto_no_corregida:ko.observable(),//.extend({ required: { message: '(*)Seleccione una foto de la No Conformidad' } }),
		foto_corregida:ko.observable('')
	}

	self.filtro_no_conformidad={
		id_proyecto:ko.observable(''),
		id_estado:ko.observable(''),
		estructura:ko.observable(''),
		desde:ko.observable(''),
		hasta:ko.observable('')
	}

	//self.detalle.id(datos.id);
	self.detalle={
		id: ko.observable(0),
		nom_proyecto:ko.observable(''),
		nom_usuario:ko.observable(''),
		nom_estado:ko.observable(''),
		nom_detectada:ko.observable(''),
		descripcion_no_corregida:ko.observable(''),
		descripcion_corregida:ko.observable(''),
		fecha_no_corregida:ko.observable(''),
		fecha_corregida:ko.observable(''),
		estructura:ko.observable(''),
		primer_correo:ko.observable(''),
        segundo_correo:ko.observable(''),
        tercer_correo:ko.observable(''),
		foto_no_corregida:ko.observable(''),
		foto_corregida:ko.observable('')
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

	/*self.paginacion2 = {
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
	}*/
	/*self.paginacion2.pagina_actual.subscribe(function (pagina) {
		self.buscarContrato(pagina);
	});
	//Funcion para crear la paginacion
	self.llenar_paginacion2 = function (data,pagina) {
		self.paginacion2.pagina_actual(pagina);
		self.paginacion2.total(data.count);
		self.paginacion2.cantidad_por_paginas(resultadosPorPagina);
	}*/
	// Fin de Paginacion

	self.abrir_modal = function () {
		self.limpiar();
		self.titulo('Registrar una No Conformidad');
		$('#modal_acciones').modal('show');

		// self.dysplay_giro_checkbox(true);
	}
	self.abrir_modal_proyecto = function () {
		$('#modal_proyecto').modal('show');
	}
	self.abrir_modal_usuario = function () {
		$('#modal_usuario').modal('show');
	}
	self.abrir_filtro = function () {
		$('#modal_filtro').modal('show');
	}

	//limpiar el modelo
	self.limpiar=function(){
        self.NoConformidadVO.id(0);
		self.NoConformidadVO.proyecto_id(0);
		self.NoConformidadVO.usuario_id(0);
		self.NoConformidadVO.estado_id(self.estado());
		self.NoConformidadVO.detectada_id(0);
		self.NoConformidadVO.descripcion_no_corregida('');
		self.NoConformidadVO.descripcion_corregida('');
		self.NoConformidadVO.fecha_no_corregida('');
		self.NoConformidadVO.fecha_corregida('');
		self.NoConformidadVO.terminada(0);
		self.NoConformidadVO.estructura('');
		self.NoConformidadVO.primer_correo('');
        self.NoConformidadVO.segundo_correo('');
        self.NoConformidadVO.tercer_correo('');
		self.NoConformidadVO.foto_no_corregida('');
		self.NoConformidadVO.foto_corregida('');
		self.filtro_no_conformidad.id_proyecto('');
		self.filtro_no_conformidad.id_estado('');				
		self.filtro_no_conformidad.estructura('');
		self.filtro_no_conformidad.desde('');
		self.filtro_no_conformidad.hasta('');		
		self.soporte('');
		self.soporte_corregida('');
		self.nombre_proyecto('');
		self.nom_usuario('');
		$('#archivo').fileinput('reset');
		$('#archivo').val('');
		$('#archivo_corregido').fileinput('reset');
		$('#archivo_corregido').val('');

		self.mensaje_guardar('');

		self.NoConformidadVO.fecha_no_corregida.isModified(false);
		self.NoConformidadVO.descripcion_no_corregida.isModified(false);
		self.NoConformidadVO.estructura.isModified(false);
	}
	//limpiar el filtro de contrato
	self.limpiar_contrato=function(){
		/*self.buscar_contrato.tipo_contrato('');
		self.buscar_contrato.nom_num_contrato('');
		self.mensaje_cont('');
		self.lista_contrato([]);*/
	}
	// Limpiar filtro
	self.limpiar_filtro=function(){
		self.filtro_no_conformidad.id_proyecto('');
		self.filtro_no_conformidad.id_estado('');
		self.filtro_no_conformidad.estructura('');
		self.filtro_no_conformidad.desde('');
		self.filtro_no_conformidad.hasta('');

		self.nombre_proyecto('');
	}

	self.consulta_enter = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.consultar(1);
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}
	self.consulta_enter_usuario = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.listar_usuario();
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}
	/*self.consulta_enter_beneficiario = function (d,e) {
		if (e.which == 13) {
			self.buscarBeneficiario(1);
		}
		return true;
	}*/
	/*self.consulta_enter_beneficiario_filtro = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.buscarBeneficiarioFiltro();
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}*/
	/*self.consulta_enter_contrato = function (d,e) {
		if (e.which == 13) {
			//self.filtro($('#txtBuscar').val());
			self.buscarContrato(1);
			//console.log("asa;"+$('#nom_nit1').val());
		}
		return true;
	}*/

	//Buscar Contrato
	/*self.buscarContrato=function(pagina){

		parameter={id_tipo:self.buscar_contrato.tipo_contrato(),
									dato:self.buscar_contrato.nom_num_contrato(),
									lite:1,
									page: pagina};
		path =path_principal+'/api/Contrato/?format=json';

		if (NoConformidadViewModel.errores_bus_contrato().length == 0){ //se activa las validaciones
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
			}, path, parameter, function(){cerrarLoading();},false);
		} else {
			NoConformidadViewModel.errores_bus_contrato.showAllMessages();
		}
	}*/

	// INICIO Filtro de proyecto
	//funcion que se ejecuta cuando se cambia en el select de M-Contrato de Filtro de Proyecto
    self.macrocontrato_select.subscribe(function (value) {

        if (value > 0) {
            // self.consultar_contratista(value);
            self.filtros(value, 0, 0, 0);
        } else {
			self.contratista_list([]);
			self.departamento_list([]);
			self.municipio_list([]);
			self.proyecto_list([]);
        }
    });

	self.contratista_select.subscribe(function (value) {

        if (value > 0) {
            self.cambiar_contratista(1);
            // self.cambiar_departamento(0);
            // self.departamento('');
            // self.municipio(0);
            // self.descargoVO.proyecto_id(0);
            self.showRow(true);
            self.filtros(self.macrocontrato_select(), value, 0, 0);
            // self.proyecto_combo(self.macrocontrato_select(),value,self.departamento(),self.municipio());
        } else {
            self.cambiar_contratista(0);
            self.showRow(false);
            self.departamento_list([]);
			self.municipio_list([]);
			self.proyecto_list([]);
        }
    });

	self.departamento_select.subscribe(function (value) {

        if (value > 0) {
			self.cambiar_departamento(1);
			self.showRow(true);
            self.filtros(self.macrocontrato_select(), self.contratista_select(), value, 0);
        } else {
			self.cambiar_departamento(0);
			self.showRow(false);
			self.municipio_list([]);
			self.proyecto_list([]);
        }
	});

	self.municipio_select.subscribe(function (value) {

        if (value > 0) {
			self.cambiar_municipio(1);
			self.showRow(true);
            self.filtros(self.macrocontrato_select(), self.contratista_select(), self.departamento_select(), value);
        } else {
			self.cambiar_municipio(0);
			self.showRow(false);
			self.proyecto_list([]);
        }
    });

	// Filtro de proyecto
	self.filtros = function (contrato, contratista, departamento, municipio) {

        path = path_principal + '/api/Proyecto/?filtros=1';
        parameter = '';
        if (contrato != 0) {
            parameter += 'contrato_id=' + contrato;
        }
        if (contratista != 0) {
            parameter += '&id_contratista=' + contratista;
        }

        if (departamento != '') {
            parameter += '&departamento_id=' + departamento;
        }

        if (municipio != 0) {
            parameter += '&municipio_id=' + municipio;
        }
        RequestGet(function (results, count) {

            //self.listado_contratista(results.descargoVO.contratista_id);
            if (self.cambiar_contratista() == 0) {
                self.contratista_list(results.data.contratistas);
                // console.log("contra"+self.cambiar_contratista());
            }
            if (self.cambiar_departamento() == 0) {
                self.departamento_list(results.data.departamentos);
                // alert("as");
            }
            if (self.cambiar_municipio() == 0) {
                self.municipio_list(results.data.municipios);
                // alert("as");
			}
			self.proyecto_list(results.data.proyectos);
        }, path, parameter, undefined, true, true);
    }

	self.agregar_proyecto = function (valor) {

		self.NoConformidadVO.proyecto_id(self.proyecto_select());
		self.filtro_no_conformidad.id_proyecto(self.proyecto_select());
		self.nombre_proyecto($('#nom_proyecto option:selected').text());
		$('#modal_proyecto').modal('hide');
		// alert('id_proy:'+self.proyecto_select());
		// alert('nom_proy:'+$('#nom_proyecto option:selected').text());
    }
	// FIN Filtro de proyecto

	// INICIO Filtro de usuario
	//consultar contratista, contratante y MContratos selects
	self.llenarSelect=function(dato){
		parameter={};
		path = path_principal+'/api/Contrato/?format=json';
		parameter = {sin_list_contrato:1,//tipo:1,
					 contratante:1};
		RequestGet(function (datos, estado, mensage) {
			// LLENAR CONTRATISTA
			// self.listado_empresa_contratista(datos.contratista);
			// LLENAR CONTRATANTE
			self.listado_empresa_contratante(datos.contratante);
			// LLENAR MACRO-CONTRATOS
			// self.lista_contrato(convertToObservableArray(datos.mcontrato));
		}, path, parameter,function(){},false,false);
	}

	self.listar_usuario=function(){
        path =path_principal+'/api/usuario/?lite=1&sin_paginacion=1';
		parameter = '';
		faltante = 0;
		// alert('ola:'+self.nombre_usuario());
		if(self.id_empresa() != 0){
			parameter = 'empresa_id='+ self.id_empresa();
			faltante = 1;
		}
        if($('#id_nombre_usuario').val() != ''){
			parameter = parameter+'&dato='+ $('#id_nombre_usuario').val();
		}
		if(faltante == 1){
			RequestGet(function (results,success,message) {

				if (success == 'ok' && results!=null && results.length > 0) {
					self.mensaje('');
					self.list_usuario(agregarOpcionesObservable(results));
					self.ver_usuario(true);
				} else {
					self.list_usuario([]);
					self.ver_usuario(false);
					self.mensaje_usuario(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
					//mensajeInformativo('No se encontraron registros');
				}
				//self.llenar_paginacion(datos,pagina);
			}, path, parameter);
		}else{
			mensajeInformativo('Seleccione una Empresa.','Información');return false;
		}
	}

	self.agregar_usuario = function () {

        self.NoConformidadVO.detectada_id(self.id_detectada());
		self.nom_usuario($('#nom_usuario option:selected').text());
		$('#modal_usuario').modal('hide');
		// alert('id_proy:'+self.usuario_select());
		// alert('nom_proy:'+$('#nom_usuario option:selected').text());
    }
	// FIN Filtro de Usuario

	// Buscar el Beneficiario
	//self.buscarBeneficiario=function(pagina){

		// console.log("nom_nit:"+self.buscar_beneficiario.nit_nom());
		// console.log("tipo:"+self.buscar_beneficiario.tipo());
		/*self.buscar_beneficiario.nit_nom($("#nit_nom").val());

		parameter={dato:self.buscar_beneficiario.nit_nom() };
		path =path_principal+'/api/empresa/?sin_paginacion&'+self.buscar_beneficiario.tipo()+'=1&format=json&';

		RequestGet(function (results,success) {
			if (success == 'ok' && results.length > 0) {
				self.mensaje_beneficiario('');
				self.lista_beneficiario(results);
			}else {
				self.lista_beneficiario([]);
				self.mensaje_beneficiario(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}

			// console.log("success:"+success);
			cerrarLoading();
		}, path, parameter,function(){},false);*/
	//}

	// Buscar el Beneficiario para el filtro
	//self.buscarBeneficiarioFiltro=function(){

		// console.log("nom_nit:"+self.filtro_cesion.nit_nom());
		// console.log("tipo:"+self.filtro_cesion.tipo());
		/*self.filtro_cesion.nom_beneficiario($("#nom_beneficiario").val());

		parameter={dato:self.filtro_cesion.nom_beneficiario()
							 // esProveedor:1
							// esContratista:1
							};
		path =path_principal+'/api/empresa/?sin_paginacion&'+self.filtro_cesion.tipo()+'=1&format=json';

		RequestGet(function (results,success) {
			if (success == 'ok' && results.length > 0) {
				//self.mensaje_beneficiario('');
				self.filtro_cesion.beneficiario_lista(results);
			}else {
				self.filtro_cesion.beneficiario_lista([]);
				//self.mensaje_beneficiario(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
			}

			// console.log("success:"+success);
		}, path, parameter,function(){self.filtro_cesion.beneficiario(sessionStorage.getItem("fac_cs_beneficiario"));},true);*/
	//}

	// Buscar Nombre de giro
	//self.buscarNombreGiro=function(mcontrato, nombre){

		// console.log("nom_nit:"+self.buscar_beneficiario.nit_nom());
		// console.log("tipo:"+self.buscar_beneficiario.tipo());
		// self.buscar_beneficiario.nit_nom($("#nit_nom").val());

		/*parameter={contrato:mcontrato };
		path =path_principal+'/api/Nombre_giro/?sin_paginacion&format=json';

		RequestGet(function (results,success) {
			if (success == 'ok' && results.length > 0) {
				self.mensaje_guardar('');
				self.listado_nombre_giro(results);
				self.dysplay_giro_checkbox(true);
			}else {
				self.listado_nombre_giro([]);
				self.mensaje_guardar('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i> No se encontraron nombres de giro, para este MContrato: '+nombre+' </div>');
				self.dysplay_giro_checkbox(false);
				self.dysplay_giro(false);
			}

			// console.log("success:"+success);
		}, path, parameter,function(){});*/
	//}

	//consultar los tipos para llenar un select
	//self.consultar_lista_tipo=function(){

		/*path =path_principal+'/api/Tipos?ignorePagination';
		parameter={ aplicacion: 'cuenta' };
		RequestGet(function (datos, estado, mensaje) {

			self.listado_tipo_cuenta(datos);

		}, path, parameter,undefined,false,false);*/
	//}

	//self.ponerContrato = function (obj) {

		//alert(obj.id); return false;
		
		//self.NoConformidadVO.contrato_id(obj.id);
		/*self.nombre_proyecto(obj.nombre);
		if(obj.mcontrato){
			self.dysplay_giro_checkbox(true);
			self.dysplay_giro(false);
			self.buscarNombreGiro(obj.mcontrato.id, obj.mcontrato.nombre);
		}else{
			self.dysplay_giro_checkbox(false);
			self.dysplay_giro(false);
			self.mensaje_guardar('<div class="alert alert-info alert-dismissable"><i class="fa fa-info-circle"></i> El Contrato '+obj.nombre+', no tiene un M-Contrato asignado. </div>');
		}

		$('#modal_contrato').modal('hide');
		return true;*/
	//}
	//self.ponerBeneficiario = function (obj) {

		//alert(obj.id); return false;
		
		// self.NoConformidadVO.beneficiario_id(obj.id);
		/*self.nombre_beneficiario(obj.nombre);
		$('#modal_beneficiario').modal('hide');
		return true;*/
	//}

	self.guardar=function(){

		if (NoConformidadViewModel.errores_no_conformidad().length == 0){ //se activa las validaciones

			// self.sub_contratistaVO.soporte($('#archivo')[0].files[0]);
			if(self.NoConformidadVO.id()==0){
				var soporte = true;
				if($('#archivo')[0].files.length==0){
					//self.NoConformidadVO.soporte('');
					soporte = false;
				}
				//console.log("val:"+self.NoConformidadVO.valor());
				if(soporte){
					if((self.NoConformidadVO.proyecto_id() != 0) && (self.NoConformidadVO.detectada_id() != 0)){
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
							url:path_principal+'/api/no_conformidad/',//url api
							parametros:self.NoConformidadVO
						};
						//parameter =ko.toJSON(self.NoConformidadVO);
						//Request(parametros);
						RequestFormData(parametros);
					}else{
						mensajeInformativo('Falta por ingresar proyecto o el usuario.','Información');
					}
				}else{
					mensajeInformativo('Falta por seleccionar la Foto.','Información');
				}
			}else{
				if($('#archivo')[0].files.length==0){
					self.NoConformidadVO.foto_no_corregida('');
				}
				if($('#archivo_corregido')[0].files.length==0){
					self.NoConformidadVO.foto_corregida('');
				}
				//console.log("val:"+self.NoConformidadVO.valor());
				if((self.NoConformidadVO.proyecto_id() != 0) && (self.NoConformidadVO.detectada_id() != 0)){
					var parametros={
						metodo:'PUT',
						callback:function(datos, estado, mensaje){

							if (estado=='ok') {
								self.filtro("");
								self.consultar(self.paginacion.pagina_actual());
								$('#modal_acciones').modal('hide');
								$('#modal_correccion').modal('hide');
								self.limpiar();
							}

						},//funcion para recibir la respuesta 
						url:path_principal+'/api/no_conformidad/'+self.NoConformidadVO.id()+'/',
						parametros:self.NoConformidadVO
					};
					RequestFormData(parametros);
				}else{
					mensajeInformativo('Falta por ingresar proyecto o el usuario.','Información');
				}
			}
		} else {
			NoConformidadViewModel.errores_no_conformidad.showAllMessages();
		}
	}

	// Consultar No Conformidad
	self.consultar = function (pagina) {
		if (pagina > 0) {
			self.filtro($('#txtBuscar').val());
			// alert("qwqw:"+self.filtro_no_conformidad.beneficiario());
			// alert("qwqw:"+sessionStorage.getItem("fac_cs_beneficiario"));

			// sessionStorage.setItem("fac_cs_filtro_cesion",self.filtro() || '');
			// sessionStorage.setItem("fac_cs_nom_beneficiario",self.filtro_no_conformidad.nom_beneficiario() || '');
			// sessionStorage.setItem("fac_cs_beneficiario_lista",self.filtro_no_conformidad.beneficiario_lista() || []);
			// sessionStorage.setItem("fac_cs_beneficiario",self.filtro_no_conformidad.beneficiario() || '');
			// sessionStorage.setItem("fac_cs_tipo_contratista",self.filtro_no_conformidad.tipo() || '');
			// sessionStorage.setItem("fac_cs_referencia",self.filtro_no_conformidad.referencia() || '');
			// sessionStorage.setItem("fac_cs_num_contrato",self.filtro_no_conformidad.num_contrato() || '');
			// sessionStorage.setItem("fac_cs_desde",self.filtro_no_conformidad.desde() || '');
			// sessionStorage.setItem("fac_cs_hasta",self.filtro_no_conformidad.hasta() || '');

			path = path_principal+'/api/no_conformidad/?format=json';
			parameter = {dato: self.filtro(),
									id_proyecto: self.filtro_no_conformidad.id_proyecto(),
									id_estado: self.filtro_no_conformidad.id_estado(),
									estructura: self.filtro_no_conformidad.estructura(),
									fecha_desde: self.filtro_no_conformidad.desde(),
									fecha_hasta: self.filtro_no_conformidad.hasta(),
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
				// self.llenar_paginacion2(datos,pagina);
				$('#modal_filtro').modal('hide');
				cerrarLoading();
			}, path, parameter,function(){
				self.llenarSelect();
			}, true);
		}
	}

	// Buscar los registrar compensados
	//self.buscarRegistrosCompensados=function(){

		/*parameter2={//id_contrato:self.cruceVO.contrato_id(),
								id_tablaForanea:self.tablaForanea.cesion()};
		path2 =path_principal+'/api/FacturaDetalleCompensacion/?format=json&sin_paginacion';

		RequestGet(function (datos, estado, mensage) {

			if (estado == 'ok' && datos!=null && datos.length > 0) {
				
				// console.log(datos);

				var lista_ids=[];
				ko.utils.arrayForEach(datos, function(d) {

					lista_ids.push(
						d.id_registro
					);
				});
				// console.log("ids:"+lista_ids);

				self.listado_cesion_c(agregarOpcionesObservable(lista_ids));
			} else {
				//console.log("Nooo");
				self.listado_cesion_c([]);
			}
		}, path2, parameter2, function(){
			self.consultar(1);
		},false);*/
	//}

	// Para Editar la No Conformidad
	self.consultar_por_id = function (obj) {

		path =path_principal+'/api/no_conformidad/'+obj.id+'/?format=json';
		parameter = {};
		self.limpiar();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.titulo('Actualizar No Conformidad');

			self.NoConformidadVO.id(datos.id);
			self.NoConformidadVO.proyecto_id(datos.proyecto.id);
			self.NoConformidadVO.usuario_id(datos.usuario.id);
			self.NoConformidadVO.estado_id(datos.estado.id);
			self.NoConformidadVO.detectada_id(datos.detectada.id);
			self.NoConformidadVO.descripcion_no_corregida(datos.descripcion_no_corregida);
			self.NoConformidadVO.descripcion_corregida(datos.descripcion_corregida);
			self.NoConformidadVO.fecha_no_corregida(datos.fecha_no_corregida);
			((datos.fecha_corregida == null) ? self.NoConformidadVO.fecha_corregida('') : self.NoConformidadVO.fecha_corregida(datos.fecha_corregida));
			self.NoConformidadVO.terminada(datos.terminada);
			self.NoConformidadVO.estructura(datos.estructura);
			// self.NoConformidadVO.primer_correo(datos.primer_correo);
			((datos.primer_correo == null) ? self.NoConformidadVO.primer_correo('') : self.NoConformidadVO.primer_correo(datos.primer_correo));
			// self.NoConformidadVO.segundo_correo(datos.segundo_correo);
			((datos.segundo_correo == null) ? self.NoConformidadVO.segundo_correo('') : self.NoConformidadVO.segundo_correo(datos.segundo_correo));
			// self.NoConformidadVO.tercer_correo(datos.tercer_correo);
			((datos.tercer_correo == null) ? self.NoConformidadVO.tercer_correo('') : self.NoConformidadVO.tercer_correo(datos.tercer_correo));
			self.NoConformidadVO.foto_no_corregida(datos.foto_no_corregida);
			// self.NoConformidadVO.foto_corregida(datos.foto_corregida);
			((datos.foto_corregida == null) ? self.NoConformidadVO.foto_corregida('') : self.NoConformidadVO.foto_corregida(datos.foto_corregida));
			self.soporte(datos.foto_no_corregida);
			self.nombre_proyecto(datos.proyecto.nombre);
			self.nom_usuario(datos.detectada.persona.nombres+' '+datos.detectada.persona.apellidos);

			$('#modal_acciones').modal('show');
			cerrarLoading();
		}, path, parameter,function(){},false);
	}

	// Para var el detalle de la No Conformidad
	self.consultar_por_id_detalle = function (obj) {

		path =path_principal+'/api/no_conformidad/'+obj.id+'/?format=json';
		parameter = {};
		// self.limpiar();
		// self.limpiar_contrato();
		RequestGet(function (datos, estado, mensaje) {

			self.detalle.id(datos.id);
			self.detalle.nom_proyecto(datos.proyecto.nombre);
			self.detalle.nom_usuario(datos.usuario.persona.nombres+' '+datos.usuario.persona.apellidos);
			self.detalle.nom_estado(datos.estado.nombre);
			self.detalle.nom_detectada(datos.detectada.persona.nombres+' '+datos.detectada.persona.apellidos);
			self.detalle.descripcion_no_corregida(datos.descripcion_no_corregida);
			self.detalle.descripcion_corregida(datos.descripcion_corregida);
			self.detalle.fecha_no_corregida(datos.fecha_no_corregida);
			self.detalle.fecha_corregida(datos.fecha_corregida);
			self.detalle.estructura(datos.estructura);
			self.detalle.primer_correo(datos.primer_correo);
			self.detalle.segundo_correo(datos.segundo_correo);
			self.detalle.tercer_correo(datos.tercer_correo);
			self.detalle.foto_no_corregida(datos.foto_no_corregida);
			self.detalle.foto_corregida(datos.foto_corregida);

			$('#detalle_no_conformidad').modal('show');

			// mes causado
			// str_meses = '';
			// ko.utils.arrayForEach(datos.mes_causado, function(d) {

			// 	if(str_meses != ''){str_meses = str_meses+', '}

			// 	str_meses = str_meses+d.mes+'-'+d.ano;
			// });
			// str_meses = String(str_meses);
			// //console.log("detalle_meses:"+str_meses);
			// self.detalle.meses(str_meses);
		}, path, parameter);
	}

	// Para subir la correccion la No Conformidad
	self.subir_correccion = function (obj) {

		path =path_principal+'/api/no_conformidad/'+obj.id+'/?format=json';
		parameter = {};
		self.limpiar();
		RequestGet(function (datos, estado, mensaje) {

			self.titulo_correccion('Registrar Correccion');

			self.NoConformidadVO.id(datos.id);
			self.NoConformidadVO.proyecto_id(datos.proyecto.id);
			self.NoConformidadVO.usuario_id(datos.usuario.id);
			self.NoConformidadVO.estado_id(datos.estado.id);
			self.NoConformidadVO.detectada_id(datos.detectada.id);
			self.NoConformidadVO.descripcion_no_corregida(datos.descripcion_no_corregida);
			self.NoConformidadVO.descripcion_corregida(datos.descripcion_corregida);
			self.NoConformidadVO.fecha_no_corregida(datos.fecha_no_corregida);
			((datos.fecha_corregida == null) ? self.NoConformidadVO.fecha_corregida('') : self.NoConformidadVO.fecha_corregida(datos.fecha_corregida));
			self.NoConformidadVO.terminada(datos.terminada);
			self.NoConformidadVO.estructura(datos.estructura);
			// self.NoConformidadVO.primer_correo(datos.primer_correo);
			((datos.primer_correo == null) ? self.NoConformidadVO.primer_correo('') : self.NoConformidadVO.primer_correo(datos.primer_correo));
			// self.NoConformidadVO.segundo_correo(datos.segundo_correo);
			((datos.segundo_correo == null) ? self.NoConformidadVO.segundo_correo('') : self.NoConformidadVO.segundo_correo(datos.segundo_correo));
			// self.NoConformidadVO.tercer_correo(datos.tercer_correo);
			((datos.tercer_correo == null) ? self.NoConformidadVO.tercer_correo('') : self.NoConformidadVO.tercer_correo(datos.tercer_correo));
			self.NoConformidadVO.foto_no_corregida(datos.foto_no_corregida);
			// self.NoConformidadVO.foto_corregida(datos.foto_corregida);
			((datos.foto_corregida == null) ? self.NoConformidadVO.foto_corregida('') : self.NoConformidadVO.foto_corregida(datos.foto_corregida));
			self.soporte_corregida(datos.foto_corregida);
			//self.nombre_proyecto(datos.proyecto.nombre);
			//self.nom_usuario(datos.detectada.persona.nombres+' '+datos.detectada.persona.apellidos);

			$('#modal_correccion').modal('show');
			cerrarLoading();
		}, path, parameter,function(){},false);
	}

	// Eliminar la No Conformidad
	self.eliminar = function () {
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
				content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una No Conformidad para su eliminación.<h4>',
				cancelButton: 'Cerrar',
				confirmButton: false
			});
		}else{
			var path =path_principal+'/no_conformidad/eliminar_no_conformidad/';
			var parameter = { lista: lista_id};
			RequestAnularOEliminar("Esta seguro que desea eliminar las No Conformidades seleccionadas?", path, parameter, function () {
				self.consultar(self.paginacion.pagina_actual());
				self.checkall(false);
			});
		}
	}

	self.checkall.subscribe(function(value ){

		ko.utils.arrayForEach(self.listado(), function(d) {

			d.eliminado(value);
        });
	});

	// PONER NOMBRE DE GIROS
	/*self.NoConformidadVO.checkall_giro.subscribe(function(value ){

		// ko.utils.arrayForEach(self.listado(), function(d) {
		if(value == true){
			self.dysplay_giro(true);
			// self.NoConformidadVO.checkall_giro(true);
		}else{
			self.dysplay_giro(false);
			self.NoConformidadVO.nombre_giro(0);
			// self.NoConformidadVO.checkall_giro(false);
        }
		// d.eliminado(value);
		// });
	});*/

	//exportar excel
	self.exportar_excel=function(){
	    self.filtro($('#txtBuscar').val());
		location.href=path_principal+"/no_conformidad/excel_no_conformidad?dato="+self.filtro()+
                                                    "&id_proyecto="+self.filtro_no_conformidad.id_proyecto()+
                                               "&id_estado="+self.filtro_no_conformidad.id_estado()+
                                               "&estructura="+self.filtro_no_conformidad.estructura()+
                                                   "&fecha_desde="+self.filtro_no_conformidad.desde()+
                                                   "&fecha_hasta="+self.filtro_no_conformidad.hasta();
	}
	//exportar Word
	self.exportar_word=function(){
	    self.filtro($('#txtBuscar').val());
		location.href=path_principal+"/no_conformidad/word_no_conformidad?dato="+self.filtro()+
                                                    "&id_proyecto="+self.filtro_no_conformidad.id_proyecto()+
                                               "&id_estado="+self.filtro_no_conformidad.id_estado()+
                                               "&estructura="+self.filtro_no_conformidad.estructura()+
                                                   "&fecha_desde="+self.filtro_no_conformidad.desde()+
                                                   "&fecha_hasta="+self.filtro_no_conformidad.hasta();
	}
}
var no_conformidad = new NoConformidadViewModel();
NoConformidadViewModel.errores_no_conformidad = ko.validation.group(no_conformidad.NoConformidadVO);
// NoConformidadViewModel.errores_bus_contrato = ko.validation.group(no_conformidad.buscar_contrato);
// alert("1:"+sessionStorage.getItem("fac_cs_beneficiario"));

$('#txtBuscar').val(sessionStorage.getItem("fac_cs_filtro_cesion"));
// no_conformidad.filtro_cesion.nom_beneficiario(sessionStorage.getItem("fac_cs_nom_beneficiario"));
// // no_conformidad.filtro_cesion.beneficiario_lista(sessionStorage.getItem("fac_cs_beneficiario_lista") || []);
// no_conformidad.filtro_cesion.beneficiario(sessionStorage.getItem("fac_cs_beneficiario"));
// no_conformidad.filtro_cesion.tipo(sessionStorage.getItem("fac_cs_tipo_contratista"));
// no_conformidad.filtro_cesion.referencia(sessionStorage.getItem("fac_cs_referencia"));
// no_conformidad.filtro_cesion.num_contrato(sessionStorage.getItem("fac_cs_num_contrato"));
// no_conformidad.filtro_cesion.desde(sessionStorage.getItem("fac_cs_desde"));
// no_conformidad.filtro_cesion.hasta(sessionStorage.getItem("fac_cs_hasta"));

// alert("2:"+no_conformidad.filtro_cesion.beneficiario());

no_conformidad.consultar(1);
// no_conformidad.buscarRegistrosCompensados();//iniciamos la primera funcion
// no_conformidad.consultar_lista_tipo();
ko.applyBindings(no_conformidad);