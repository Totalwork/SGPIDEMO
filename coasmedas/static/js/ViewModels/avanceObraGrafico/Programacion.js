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

   self.archivo_carga=ko.observable(''); 
   self.valor_total=ko.observable(0);

     self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
        directiones: ko.observable(true),
        limite: ko.observable(true),
        cantidad_por_paginas: ko.observable(0),
        totalRegistrosBuscados:ko.observable(0),
        text: {
            first: ko.observable('Inicio'),
            last: ko.observable('Fin'),
            back: ko.observable('<'),
            forward: ko.observable('>')
        }
    }

     //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

     self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });



    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Fecha realizacion de actividad / postes');
        $('#modal_acciones').modal('show');
    }


     self.limpiar=function(){   
           
         
     }


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {  


            self.cargar(pagina);

        }

    }

    self.cargar =function(pagina){     

            path = path_principal+'/api/avanceObraGraficoLinea/?format=json&page='+pagina;
            parameter = {cronograma_id:$('#id_cronograma').val(),tipo_linea:2,pagina: pagina,filtro_porcentaje:1};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data.datos!=null && datos.data.datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data.datos));
                    self.mostrar_grafica_linea(datos.data.porcentajes);
                    //self.cargar_total_presupuesto(datos);
                     $('#modal_acciones').modal('hide');

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);

                //self.llenar_paginacion(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
    }


     self.array_porcentaje=function(data){
        var lista=[];
        ko.utils.arrayForEach(data, function(d) { 
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
        });
        return lista

    }


    self.mostrar_grafica_linea=function(data){

            datos_porcentaje=self.array_porcentaje(data);
                  
             $('#high-line3').highcharts({
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
                            name: 'Linea Programada',
                            data: datos_porcentaje
                        }]
                    });
       
    }


    self.guardar=function(){

         if(self.archivo_carga()==''){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo para cargar las fechas.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('archivo',self.archivo_carga());
            data.append('id_cronograma',$('#id_cronograma').val());
            data.append('tipo_linea',2);

            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar(1);
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/guardar_lineabase_fecha_archivo/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }
   
    }


    self.guardar_linea=function(){
     
        var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.cerrado_cronograma(true);
                            self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraGrafico/guardar_linea/',//url api
                     parametros:{id_cronograma:$('#id_cronograma').val() }                         
                  };
                Request(parametros);


    }



    self.descargar_plantilla=function(){

             location.href=path_principal+"/avanceObraGrafico/descargar_plantilla_lineabase?cronograma_id="+$('#id_cronograma').val()+"&tipo_linea=2";

    }


   

 }



var index = new IndexViewModel();
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

