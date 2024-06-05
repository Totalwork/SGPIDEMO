function CronogramaContratoViewModel(){
    var self = this;
    self.filtroVO = {
        ano: ko.observable(0),
        fondo: ko.observable(0)
    }

    self.actividadContratoVO={
        id: ko.observable(0),
        cronograma_id:ko.observable(0),
        contrato_id: ko.observable(0),
    }

    self.url=path_principal+'/';

    self.listado_contratos_asociar = ko.observableArray([]);
    self.listado_cronogramas_asociar = ko.observableArray([]);

    self.titulo = ko.observable('');

    self.listado_anos = ko.observableArray([]);
    self.listado_fondos = ko.observableArray([]);
    self.listado_contratos = ko.observableArray([]);
    self.mensaje = ko.observable('');

    self.categoriasAvanceContrato = ko.observableArray([]);
    self.seriesAvanceContrato = ko.observableArray([]);
    self.mensajeAvanceContrato = ko.observable('');


    self.estadosInicio = ko.observableArray([]);
    self.mensajeEstadoInicio = ko.observable('');

    self.estadosFin = ko.observableArray([]);
    self.mensajeEstadoFin = ko.observable('');

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
       self.getDataTable(pagina);
    });

    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }

    self.getDataFilter = function() {
        path = path_principal + '/cronogramacontrato/getanosyfondos/?format=json';
        parameter = {}
        RequestGet(function (datos, success, massage){
            if(success == 'ok' && datos!=null && datos.anos.length > 0){
                self.listado_anos(datos.anos);                
            }else{
                self.listado_anos([]);
            }
            if(success == 'ok' && datos!=null && datos.fondos.length > 0){
                self.listado_fondos(datos.fondos)
            }else{
                self.listado_fondos([]);
            }
        }, path, parameter);
    }

    self.goesquemacronograma = function(){
        location.href=path_principal+"/cronogramacontrato/esquemacronograma/";
    }

    self.asociarcronogramas=function(){        
            if(self.actividadContratoVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            $('#modal_cronograma').modal('hide');
                            self.getDataTable(1);
                            self.limpiar();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url+'cronogramacontrato/asociarcronogramacontrato/',//url api
                     parametros:self.actividadContratoVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                                self.getDataTable(1);
                                $('#modal_cronograma').modal('hide');
                                self.limpiar();
                            } 
                       },//funcion para recibir la respuesta 
                       url: self.url+'cronogramacontrato/asociarcronogramacontrato/'+ self.actividadContratoVO.id()+'/',
                       parametros:self.actividadContratoVO                        
                  };
                  RequestFormData(parametros);
            }
        
    }

    self.limpiar = function(){
        self.actividadContratoVO.id(0);
        // self.actividadContratoVO.actividad_id(0);
        self.actividadContratoVO.cronograma_id(0);
        self.actividadContratoVO.contrato_id(0);
        // self.actividadContratoVO.inicioprogramado('');
        // self.actividadContratoVO.finprogramado('');
        // self.actividadContratoVO.finejecutado('');
        // self.actividadContratoVO.estadoinicio_id(0);
        // self.actividadContratoVO.estadofin_id(0);
        // self.actividadContratoVO.observaciones('');
    }

    self.asociarcronogramas_modal = function(){
        self.limpiar();
        self.titulo('Asociar cronograma a contrato');
        self.getListContratos();
        self.getListCronogramas();
        $('#modal_cronograma').modal('show');
    }

    self.getListCronogramas=function(){
        
        path = path_principal + '/api/CronogramaCcontrato/';
        parameter = {};

        RequestGet(function (datos, success, massage){
            if(success == 'ok' && datos!=null){
                // alert(datos.data)
                self.listado_cronogramas_asociar(datos.data);
                self.mensaje('');
            }else{
                self.listado_cronogramas_asociar([]);
                self.mensaje(mensajeNoFound);
            }
            
        }, path,parameter);
    }


    self.getListContratos=function(){
        path = path_principal + '/cronogramacontrato/getslistacontratos/';
        parameter = {};

        RequestGet(function (datos, success, massage){
            if(success == 'ok' && datos!=null){
                // alert(datos)
                self.listado_contratos_asociar(datos);
                self.mensaje('');
            }else{
                self.listado_contratos_asociar([]);
                self.mensaje(mensajeNoFound);
            }
            
        }, path,parameter);

    }

    self.verDetalleCronograma = function(id){
        location.href=path_principal+"/cronogramacontrato/seguimientodelcontrato/"+id+"/";
    }    

    self.getDataTable = function (pagina) {
        path = path_principal + '/api/Contrato/?cronogramaContrato=1&format=json&ano='+
        $('#cmbAno').val()+'&fondo=' + $('#cmbFondo').val() + '&page='+pagina;
        parameter = {};
        RequestGet(function (datos, success, massage){
            if(success == 'ok' && datos!=null && datos.data.length > 0){
                self.listado_contratos(datos.data);
                self.mensaje('');
            }else{
                self.listado_contratos([]);
                self.mensaje(mensajeNoFound);
            }
            self.llenar_paginacion(datos,pagina);
        }, path,parameter);

    }

    self.LoadData = function() {
        self.getDataTable(1);
        //metodo para carga de graficas
        self.fillGraph();
    }

    self.fillGraph = function () {
        //var categoriasAvanceContrato = [];
        //var seriesAvanceContrato = [];
        path = path_principal + '/cronogramacontrato/getdatagraph/?format=json&ano='+
        $('#cmbAno').val()+'&fondo=' + $('#cmbFondo').val();
        
        RequestGet(function (datos, success, massage){
            if (success == 'ok' && datos != null && datos.length > 0) {
                var dataGrafica = datos;
                for (i=0; i<dataGrafica.length; i++){
                    if (dataGrafica[i].nombre == 'avance por contrato'){
                        if (dataGrafica[i].categorias.length > 0){
                            self.categoriasAvanceContrato(dataGrafica[i].categorias);
                            self.seriesAvanceContrato(dataGrafica[i].series);
                            //categoriasAvanceContrato = dataGrafica[i].categorias;
                            //seriesAvanceContrato = dataGrafica[i].series;
                            self.mensajeAvanceContrato('');
                        }else{
                            self.mensajeAvanceContrato(mensajeNoFound);
                            self.categoriasAvanceContrato([]);
                            self.seriesAvanceContrato([]);
                            //categoriasAvanceContrato = [];
                            //seriesAvanceContrato = [];
                        }
                    }
                    if (dataGrafica[i].nombre == 'estados de inicio'){
                        if (dataGrafica[i].data.length > 0){
                            self.estadosInicio(dataGrafica[i].data);
                            self.mensajeEstadoInicio('');
                        }else{
                            self.estadosInicio([]);
                            self.mensajeEstadoInicio(mensajeNoFound);

                        }
                    }

                    if(dataGrafica[i].nombre == 'estados de fin'){
                        if(dataGrafica[i].data.length>0){
                            self.estadosFin(dataGrafica[i].data);
                            self.mensajeEstadoFin('');
                        }else{
                            self.estadosFin([]);
                            self.mensajeEstadoFin(mensajeNoFound)
                        }
                    }
                }

               //Grafica avance de contrato por año y fondo
               $('#high-line').highcharts({
                    credits: false,
                    colors: [bgWarning, bgPrimary, bgInfo, bgAlert,
                                bgDanger, bgSuccess, bgSystem, bgDark
                            ],
                    chart: {
                        type: 'column',
                        zoomType: 'x',
                        panning: true,
                        panKey: 'shift',
                        marginRight: 50,
                        marginTop: -5,
                    },
                    title: {
                        text: null
                    },
                    xAxis: {
                        gridLineColor: '#EEE',
                        lineColor: '#EEE',
                        tickColor: '#EEE',
                        categories: self.categoriasAvanceContrato(),
                    },
                    yAxis: {
                        min: 0,
                        tickInterval: 5,
                        gridLineColor: '#EEE',
                        title: {
                            text: 'Porcentaje (%)',
                            style: {
                                color: bgInfo,
                                fontWeight: '300'
                            }
                        }
                    },
                    plotOptions: {
                        spline: {
                            lineWidth: 3,
                        },
                        area: {
                            fillOpacity: 0.2
                        }
                    },
                    legend: {
                        enabled: true,
                        style : {
                            fontWeight:'300'
                        }
                    },
                    series: self.seriesAvanceContrato()
                    
                });

            //Grafica de estados de inicio
                var patronColoresInicio = [];
                colors = [bgWarning, bgPrimary, bgInfo, bgAlert,
                    bgDanger, bgSuccess, bgSystem, bgDark
                ]
                columnsContratos = self.estadosInicio();
                for (var x = 0; x < columnsContratos.length; x++) {
                    if (columnsContratos[x][0] == 'Proximo a iniciar'){
                        patronColoresInicio.push(bgWarning);
                    }
                    if (columnsContratos[x][0] == 'Inició a tiempo'){
                        patronColoresInicio.push(bgSuccess);
                    }
                    if (columnsContratos[x][0] == 'Inició retrasado'){
                        alert('inicio retrasado')
                        patronColoresInicio.push(bgInfo);
                    }
                    if (columnsContratos[x][0] == 'Por iniciar'){
                        patronColoresInicio.push(bgAlert);
                    }
                    if (columnsContratos[x][0] == 'Retrasado'){
                        patronColoresInicio.push(bgDanger);
                    }



                }
                var chart14 = c3.generate({
                    bindto: '#estadosInicio',
                    color: {
                      pattern: colors,
                    },
                    data: {
                        // iris data from R
                        columns: self.estadosInicio(),
                        type : 'pie',
                        onclick: function (d, i) { console.log("onclick", d, i); },
                        onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                        onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                    }
                });
                
                
                //Grafica de estados de fin
                var patronColoresFin = [];
                columnsContratos = self.estadosFin();
                colors = [bgWarning, bgPrimary, bgInfo, bgAlert,
                    bgDanger, bgSuccess, bgSystem, bgDark
                ]
                for (var x = 0; x < columnsContratos.length; x++) {
                    if (columnsContratos[x][0] == 'Por vencer'){
                        patronColoresFin.push(bgWarning);
                    }
                    if (columnsContratos[x][0] == 'Cumplida a tiempo'){
                        patronColoresFin.push(bgSuccess);
                    }
                    if (columnsContratos[x][0] == 'Cumplida retrasada'){
                        patronColoresFin.push(bgInfo);
                    }
                    if (columnsContratos[x][0] == 'Por cumplir'){
                        patronColoresFin.push(bgAlert);
                    }
                    if (columnsContratos[x][0] == 'Vencida'){
                        patronColoresFin.push(bgDanger);
                    }



                }
                var chart15 = c3.generate({
                    bindto: '#estadosFin',
                    color: {
                      pattern: colors,
                    },
                    data: {
                        // iris data from R
                        columns: self.estadosFin(),
                        type : 'pie',
                        onclick: function (d, i) { console.log("onclick", d, i); },
                        onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                        onmouseout: function (d, i) { console.log("onmouseout", d, i); }
                    }
                });

            }
        },path,{});
    }

    self.getDetailContrato = function (obj) {
        // alert(this.getInfoCronograma(obj.id));
        alert(obj);
    }

}

var cronogramacontrato = new CronogramaContratoViewModel();
ko.applyBindings(cronogramacontrato);
cronogramacontrato.getDataFilter();
cronogramacontrato.LoadData();

