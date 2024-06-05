var highColors = ['#228BF5','#B522F5','#0EC11D'];

        // Color Library we used to grab a random color
var sparkColors = {
            "primary": [bgPrimary, bgPrimaryLr, bgPrimaryDr],
            "info": [bgInfo, bgInfoLr, bgInfoDr],
            "warning": [bgWarning, bgWarningLr, bgWarningDr],
            "success": [bgSuccess, bgSuccessLr, bgSuccessDr],
            "alert": [bgAlert, bgAlertLr, bgAlertDr]
};

function IndexViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
   // self.url=path_principal+'api/Banco';  


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {  


            self.cargar(pagina);

        }

    }

    self.cargar =function(pagina){     

            path = path_principal+'/avanceObraGrafico/consultar_graficos/';
            parameter = {cronograma_id:$('#id_cronograma').val()};
            RequestGet(function (datos, estado, mensage) {

                self.mostrar_grafica_linea(datos.linea_base,'#high-line1','Linea Base');
                self.mostrar_grafica_linea(datos.programada,'#high-line2','Linea Programada');
                self.mostrar_grafica_linea(datos.avance,'#high-line3','Linea Avance');
                self.mostrar_grafica_presupuesto(datos.presupuesto,'#high-line4','Valor Ganando');
                cerrarLoading();
            }, path, parameter,undefined, false);
    }

    self.array_porcentaje=function(data){
        var lista=[];
        ko.utils.arrayForEach(data, function(d) { 
                if(d['fecha']!='' && d['fecha']!=null){ 
                    var res=d['fecha'].split('-');
                    fecha_intervalo= new Date(res[0],res[1]-1,res[2]);
                    var anno=fecha_intervalo.getFullYear();
                    var mes= fecha_intervalo.getMonth();
                    var dia= fecha_intervalo.getDate();
                    mes = (mes < 10) ? ("0" + mes) : mes;
                    dia = (dia < 10) ? ("0" + dia) : dia;
                    var lista2=[];
                    lista2.push(Date.UTC(anno, mes, dia),d['porcentaje']);
                    lista.push(lista2);

                }
        });
        return lista

    }

     self.array_presupuesto=function(data){
        var lista=[];
        ko.utils.arrayForEach(data, function(d) { 
                if(d['fecha']!='' && d['fecha']!=null){ 
                    var res=d['fecha'].split('-');
                    fecha_intervalo= new Date(res[0],res[1]-1,res[2]);
                    var anno=fecha_intervalo.getFullYear();
                    var mes= fecha_intervalo.getMonth();
                    var dia= fecha_intervalo.getDate();
                    mes = (mes < 10) ? ("0" + mes) : mes;
                    dia = (dia < 10) ? ("0" + dia) : dia;
                    var lista2=[];
                    lista2.push(Date.UTC(anno, mes, dia),d['valor_ganando']);
                    lista.push(lista2);

                }
        });
        return lista

    }


    self.mostrar_grafica_linea=function(data,nombre_etiqueta,nombre){

            datos_porcentaje=self.array_porcentaje(data);
                  
             $(nombre_etiqueta).highcharts({
                        credits: false,
                        colors: highColors,
                        chart: {
                            backgroundColor: '#f9f9f9',
                            className: 'br-r',
                            type: 'line',
                            zoomType: 'x',
                            panning: true,
                            panKey: 'shift',
                            marginTop: 25,
                            marginRight: 1,
                        },
                        title: {
                            text: null
                        },
                        xAxis: {
                            type: 'datetime',
                            dateTimeLabelFormats: { // don't display the dummy year
                                month: '%b %e, %Y',
                                year: '%b'
                            },
                            title: {
                                text: 'Fechas'
                            },
                        },
                        yAxis: {
                            min: 0,
                            gridLineColor: '#EEE',
                            tickInterval:20,
                            offset: 1,
                            categories: ['0','10','20','30','40','50','60','70','80','90','100'],
                            title: {
                                text: 'Porcentajes %'
                            },
                        },
                        plotOptions: {
                            spline: {
                                lineWidth: 3,
                            },
                            area: {
                                fillOpacity: 0.2
                            }
                        },                      
                        tooltip: {
                            headerFormat: '<span style="font-size:10px">{point.x:%Y-%b-%e}</span><table>',
                            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                                '<td style="padding:0"><b>{point.y:.1f} %</b></td></tr>',
                            footerFormat: '</table>',
                            shared: true,
                            useHTML: true
                        },
                        plotOptions: {
                            column: {
                                colorByPoint: true,
                                colors: ['#00000', bgPrimary,
                                    bgInfo
                                ],
                                groupPadding: 0,
                                pointPadding: 0.24,
                                borderWidth: 0
                            }
                        },
                        legend: {
                            enabled: true,
                        },
                        series: [{
                            name: nombre,
                            data: datos_porcentaje
                        }]
                    });




       
    }



      self.mostrar_grafica_presupuesto=function(data,nombre_etiqueta,nombre){

            datos_porcentaje=self.array_presupuesto(data);
                  
             $(nombre_etiqueta).highcharts({
                        credits: false,
                        colors: highColors,
                        chart: {
                            backgroundColor: '#f9f9f9',
                            className: 'br-r',
                            type: 'line',
                            zoomType: 'x',
                            panning: true,
                            panKey: 'shift',
                            marginTop: 25,
                            marginRight: 1,
                        },
                        title: {
                            text: null
                        },
                        xAxis: {
                            type: 'datetime',
                            dateTimeLabelFormats: { // don't display the dummy year
                                month: '%b %e, %Y',
                                year: '%b'
                            },
                            title: {
                                text: 'Fechas'
                            },
                        },
                        yAxis: {
                            min: 0,
                            gridLineColor: '#EEE',
                            tickInterval:10000,
                            offset: 1,
                            title: {
                                text: 'Valores'
                            },
                        },
                        plotOptions: {
                            spline: {
                                lineWidth: 3,
                            },
                            area: {
                                fillOpacity: 0.2
                            }
                        },                      
                        tooltip: {
                            headerFormat: '<span style="font-size:10px">{point.x:%Y-%b-%e}</span><table>',
                            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                                '<td style="padding:0"><b>${point.y:.1f} </b></td></tr>',
                            footerFormat: '</table>',
                            shared: true,
                            useHTML: true
                        },
                        plotOptions: {
                            column: {
                                colorByPoint: true,
                                colors: ['#00000', bgPrimary,
                                    bgInfo
                                ],
                                groupPadding: 0,
                                pointPadding: 0.24,
                                borderWidth: 0
                            }
                        },
                        legend: {
                            enabled: true,
                        },
                        series: [{
                            name: nombre,
                            data: datos_porcentaje
                        }]
                    });




       
    }

   

 }



var index = new IndexViewModel();
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

