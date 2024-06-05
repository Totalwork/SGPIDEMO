
function CuentaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

    self.lista_contrato=ko.observableArray([]);
    self.contratista_select=ko.observable(0);

    self.fecha=ko.observable('');
    self.bdi_contratista=ko.observable(0);

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
        },
        totalRegistrosBuscados:ko.observable(0)
    }


      //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    self.limpiar_seleccion=function(){
        self.bdi_contratista(0);
        self.contratista_select(0);

    }

    self.bdi_contratista.subscribe(function (value) {
        self.contratista_select(value);
        return true;
    });   
   

    //consultar los macrocontrato para registrar la cuenta
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            //path = path_principal+'/api/Empresa/?format=json&page='+pagina;
            //parameter = { dato: self.filtro()};
            path = path_principal+'/api/contratistaContratoInforme?format=json&page='+pagina;
            parameter = { dato: self.filtro(), pagina: pagina,contratante_id:$('#id_empresa').val() };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results);  
                    self.listado(agregarOpcionesObservable(datos.data));  

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
        }
    }

     self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    self.exportar_informe=function(){

        if(self.contratista_select()==0){
                 $.confirm({
                    title: 'Información',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i> Seleccione un contratista para exportar el informe<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
        }else{
            location.href=path_principal+"/financiero/descargar_informe_financiero_contratista/?contratista_id="+self.contratista_select()+"&fecha="+self.fecha();
        }

        

    }


 

 

}

var cuenta = new CuentaViewModel();
ko.applyBindings(cuenta);
