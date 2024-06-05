function InformeViewModel() {

	var self = this;

	/* URL*/
	self.url=path_principal+'/api/'; 

	/* ARRAYS */
	self.listado_funcionarios_firma = ko.observableArray([]); 
	self.listado_contrato = ko.observableArray([]);
    self.opcion = ko.observable('');
    self.condicion = ko.observable('');
    self.columnas = ko.observableArray([]);
    self.nombresColumnas = ko.observableArray([]);
	self.interventoriaVO={
	 	contrato:ko.observable('').extend({ required: { message: ' Seleccione el contrato.' } }),
	 	ano:ko.observable('').extend({ required: { message: ' Digite el año.' } }),
	 	fecha:ko.observable('').extend({ required: { message: ' Seleccione el mes.' } }),
	 	firma:ko.observable('').extend({ required: { message: ' Seleccione el funcionario.' } }),    
	};
	//funcion consultar funcionarios a firmar carta
    self.consultar_funcionarios_firma = function () {                
            path = self.url+'Funcionario/';
            parameter = { ignorePagination : 1 };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_funcionarios_firma(datos);
                } else {
                    self.listado_funcionarios_firma([]);
                }             
            }, path, parameter);        
    }

    self.consultar_contratos = function () {       
        path = path_principal+'/proyecto/select-filter-proyecto/';
        parameter = { };
        RequestGet(function (datos, estado, mensage) {
            self.listado_contrato(datos.mcontratos); 
            cerrarLoading();
        }, path, parameter,undefined,false); 
    } 


    //funcion consultar proyectos que ppuede  ver la empresa
    self.consultar_contratos_interventoria = function () {       
        path = path_principal+'/api/Contrato/?format=json';
        parameter = {
                                /* id = 9 ; es un contrato de interventoria tecnica */
                                id_tipo:9,
                                sin_paginacion : 1,
                                liteD : 4 ,
                                noAsignado : 1
                     };
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {
                console.log(datos)
                self.listado_contrato(datos); 
            } else {
                self.listado_contrato([]);
            }
        }, path, parameter);       
    } 

    self.generar_informe_interventoria = function () {

        if (InformeViewModel.errores_informe_interventoria().length == 0) {//se activa las validaciones

            location.href= path_principal+"/informe/informeInterventoriaDispac/?contrato="+self.interventoriaVO.contrato()+"&ano="+self.interventoriaVO.ano()+"&fecha="+self.interventoriaVO.fecha()+"&firma="+self.interventoriaVO.firma();
        }else{
            InformeViewModel.errores_informe_interventoria.showAllMessages();//mostramos las validacion
        }
    }


    self.fotoProyectoVO={
        contrato:ko.observable('').extend({ required: { message: ' Seleccione el contrato.' } }),
        foto:ko.observable('').extend({ required: { message: ' Seleccione el periodo.' } }),
        fechaDesde:ko.observable(''),
        fechaHasta:ko.observable(''),  
    };

    self.generar_informe_foto_proyecto = function () {
        if (InformeViewModel.errores_informe_foto().length == 0) {//se activa las validaciones
            location.href= path_principal+"/informe/generate-informeFotosProyecto/?contrato="+self.fotoProyectoVO.contrato()+"&foto="+self.fotoProyectoVO.foto()+"&fechaDesde="+self.fotoProyectoVO.fechaDesde()+"&fechaHasta="+self.fotoProyectoVO.fechaHasta();
        }else{
            InformeViewModel.errores_informe_foto.showAllMessages();//mostramos las validacion
        }
        
    }

     self.consultar_columnas = function () { 
        if(self.opcion() == '') {
            self.nombresColumnas([]);
            return;
        }      
        path = path_principal+'/informe/obtener-columnas/?opcion=' + self.opcion();
        parameter = { };
        RequestGet(function (datos, estado, mensage) {
            self.columnas(convertToObservableArray(datos));
            var lista = [];
            ko.utils.arrayForEach(datos, function (p) {
                lista.push(p.columna);
            });
            self.nombresColumnas(lista);
            // self.llenarIncluir();
            cerrarLoading();
        }, path, {}); 
    } 

    // self.llenarIncluir = function(){
    //     var o = '';
    //     ko.utils.arrayForEach(self.columnas(), function (p) {
    //         if (p.procesar()) {
    //             o = o + p.columna() + ',';
    //         }
    //     });

    //     $('#incluir').val(o);
    // }

    self.crearCondicion = function(){
        var condicion = '';
        ko.utils.arrayForEach(self.columnas(), function (p) {
            if (p.condicional() != '') {
                condicion = condicion + ' and ' + p.columna + p.condicional() + p.texto();
            }
        });
        
        $('#condicion').val(condicion);
    }

    self.submit = function() {
        $('#incluir').val(JSON.stringify(self.nombresColumnas()));
        var condicion = '';
        ko.utils.arrayForEach(self.columnas(), function (p) {
            if (p.condicional() == '=') {
                condicion = condicion + " and [" + p.columna() + '] ' + p.condicional() + " '" + p.texto() + "'";
            } else if (p.condicional() == 'like') {
                condicion = condicion + " and [" + p.columna() + '] ' + p.condicional() + " '%" + p.texto() + "%'";
            } else if (p.condicional() == 'between') {
                condicion = condicion + " and [" + p.columna() + '] ' + p.condicional() + " '" + p.entre1() + "' and '" + p.entre2() + "'";
            }
        });
        
        $('#condicion').val(condicion);
        return true;   
    }


}

var informe = new InformeViewModel();
InformeViewModel.errores_informe_interventoria = ko.validation.group(informe.interventoriaVO);
InformeViewModel.errores_informe_foto = ko.validation.group(informe.fotoProyectoVO);
ko.applyBindings(informe);