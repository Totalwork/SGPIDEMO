 var highColors = [bgWarning, bgPrimary, bgInfo, bgAlert,
            bgDanger, bgSuccess, bgSystem, bgDark
        ];

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
    self.mensaje_grafica=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

    self.id_campana=ko.observable('');


    self.todos=function(){
        self.id_campana('');
        self.consultar();
    }

    self.consultar=function(){

            path = path_principal+'/gestion_proyecto/cantidades_estado';
            parameter = '';
            RequestGet(function (datos, estado, mensage) {
                self.mensaje('');
                    
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    //self.listado(results); 
                    self.listado(self.llenar_datos(datos));  

                    if(self.listado().length==0){
                        self.mensaje(mensajeNoFound);
                     }

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.grafica();

                //}
            }, path, parameter);

    }



    self.id_campana.subscribe(function(value ){

            if(value>0){

                path = path_principal+'/gestion_proyecto/cantidades_estado';
                parameter = {campana_id:self.id_campana()};
                RequestGet(function (datos, estado, mensage) {
                    self.mensaje('');
                        
                    if (estado == 'ok' && datos!=null && datos.length > 0) {
                        //self.listado(results); 
                        self.listado(self.llenar_datos(datos));  

                        if(self.listado().length==0){
                            self.mensaje(mensajeNoFound);
                        }

                    } else {
                        self.listado([]);
                        self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    }

                    self.grafica();

                    //}
                }, path, parameter);

            }else{
                self.consultar();
            }

            
    });


    self.llenar_datos=function(data){

            var lista=[];   

            ko.utils.arrayForEach(data, function(d) {
                      
                 if(d.cantidad_diseno>0){

                     lista.push({
                         id:d.id,
                         name:d.nombre,
                         drilldown:d.nombre,
                         y:d.cantidad_diseno
                     });
                 }  

            });

            return lista;

    }

    self.grafica=function(){

            self.mensaje_grafica('');
            if(self.listado().length>0){
                 $('#high-column3').highcharts({
                        credits: false,
                        colors: highColors,
                        chart: {
                            type: 'column',
                            padding: 0,
                            spacingTop: 10,
                            marginTop: 100,
                            marginLeft: 30,
                            marginRight: 30
                        },
                        legend: {
                            enabled: false
                        },
                        title: {
                            text: null,
                        },
                        yAxis: {
                            showEmpty: false,
                            tickLength: 100,
                            lineColor: '#EEE',
                            tickColor: '#EEE',
                            tickInterval:20,
                            offset: 1,
                            categories: ['0','10','20','30','40','50','60','70','80','90','100'],
                            title: {
                                text: null
                            },
                            labels: {
                                align: 'center',
                            }
                        },
                        xAxis: {
                                type: 'category',
                                title: {
                                    text: null
                                }
                        },
                        tooltip: {
                            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                            pointFormat: '<tr><td style="padding:0"><b>No Proyecto:{point.y} </b></td></tr>',
                            footerFormat: '</table>',
                            shared: true,
                            useHTML: true
                        },
                        plotOptions: {
                            column: {
                                colorByPoint: false,
                                colors: [bgInfo
                                ],
                                groupPadding: 0,
                                pointPadding: 0.24,
                                borderWidth: 0
                            }
                        }, series: [{
                                name: 'Estado',
                                colorByPoint: true,
                                data: self.listado()
                            }],
                        dataLabels: {
                            enabled: true,
                            rotation: 0,
                            color: '#AAA',
                            align: 'center',
                            x: 0,
                            y: -8,
                        }
                    });
            }else{

                 self.mensaje_grafica('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No hay registro para graficar.</div>');
            }
            
    }

 }

var index = new IndexViewModel();
index.consultar();
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);