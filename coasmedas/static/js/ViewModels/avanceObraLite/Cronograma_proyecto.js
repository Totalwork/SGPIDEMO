function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);
    self.porcentajes = ko.observableArray([]);
    self.listadoCurvaAvanceObra = ko.observableArray([]);
    self.listadoCurvaAvanceFinanciero = ko.observableArray([]);
    self.programacion = ko.observableArray([]);
   // self.url=path_principal+'api/Banco';   

    self.seguimiento_contratual=ko.observableArray([]);
    self.porcentajes_conceptuales=ko.observable([]);


   self.valor_total=ko.observable(0);
   self.valor_directo=ko.observable(0);

    self.cronogramaVO={
        id:ko.observable(0),
        proyecto_id:ko.observable($('#id_proyecto').val()),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre' } }),
        periodicidad_id:ko.observable('').extend({ required: { message: '(*)Seleccione la periodicidad' } }),
        esquema_id:ko.observable('').extend({ required: { message: '(*)Seleccione el esquema' } }),
        fechaFinal:ko.observable('').extend({ required: { message: 'Ingrese una fecha de inicio' } }),
        fechaInicio:ko.observable('').extend({ required: { message: 'Ingrese una fecha final' } }),
     };



     self.listado_estado=ko.observableArray([]);
     self.id_estado=ko.observable();


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

    self.abrir_modal = function () {
        //self.limpiar();
        if (self.listado().length == 0) {

            self.titulo('Registrar');
            $('#modal_acciones').modal('show');

        }else{
              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Solo se admite un cronograma por proyecto.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
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

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.eliminar=function(){
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

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un cronograma para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraLite/eliminar_id_cronograma/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los cronogramas seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    }


    self.exportar_excel=function(){
        
    }

    // //limpiar el modelo 
     self.limpiar=function(){   
           self.cronogramaVO.nombre('');
           self.cronogramaVO.periodicidad_id('');
           self.cronogramaVO.esquema_id('');

     }



    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

             self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_avance_cronograma",self.filtro() || '');

            self.cargar(pagina);

        }


    }




    self.cargar =function(pagina){           


            let filtro_avance_cronograma=sessionStorage.getItem("filtro_avance_cronograma");

            path = path_principal+'/api/avanceObraLiteCronograma/?format=json&page='+pagina;
            parameter = {dato: filtro_avance_cronograma, pagina: pagina,proyecto_id:$("#id_proyecto").val()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));
                    self.cargarGrafica(datos.data[0].id);
                    self.seguimientoContratual(datos.data[0].id);
                    $('#modal_acciones').modal('hide');

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
            
    }

    self.seguimientoContratual = function(id) {
        path = path_principal+'/avanceObraLite/seguimientoContratual/'+id+'/';
        parameter = {}
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null) {
                self.seguimiento_contratual(datos.seguimiento);
                self.porcentajes_conceptuales(datos.porcentajes);
                demoCircleGraphs2();
            }else{
                self.seguimiento_contratual([]);
                self.porcentajes_conceptuales([]);
            }
        }, path, parameter,undefined, false);

    }


    self.cargarGrafica = function(id) {
        path = path_principal+'/avanceObraLite/graficacronograma/'+id+'/';
        parameter = {}
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null) {
                self.mensaje('');
                //self.listado(results); 
                self.porcentajes (agregarOpcionesObservable(datos.porHito));
                // self.listadoCurvaAvanceObra (agregarOpcionesObservable(datos.curvaAvanceObra));
                self.listadoCurvaAvanceFinanciero(agregarOpcionesObservable(datos.curvaAvanceFinanciero));
                // self.programacion (agregarOpcionesObservable(datos.curvaProgramada));
                self.valor_directo(datos.sumaPresupuestoDirecto);
                self.valor_total(datos.sumaPresupuesto);

            } else {
                self.porcentajes([]);
                self.listadoCurvaAvanceObra([]);
                self.listadoCurvaAvanceFinanciero([]);
            }
            demoCircleGraphs();
            demoHighLines();
            cerrarLoading();
        }, path, parameter,undefined, false);

    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            //self.limpiar();
            self.consultar(1);
        }
        return true;
    }


    self.guardar=function(){

         if (IndexViewModel.errores_cronograma().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            if(self.cronogramaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/avanceObraLiteCronograma/',//url api
                     parametros:self.cronogramaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData(parametros);
            }else{

                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                          self.limpiar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/avanceObraLiteCronograma/'+self.cronogramaVO.id()+'/',
                       parametros:self.cronogramaVO                        
                  };

                  RequestFormData(parametros);

            }

        } else {
             IndexViewModel.errores_cronograma.showAllMessages();//mostramos las validacion
        }
    }



    self.abrir_programacion=function(obj){
        path =path_principal+'/api/avanceObraLitePresupuesto/?format=json&cerrar_presupuesto=True&cronograma_id='+obj.id;
        RequestGet(function (datos, estado, mensage) {
           
            if (estado == 'ok' && datos.data!=null) {

                location.href=path_principal+"/avanceObraLite/programacion/"+obj.id+"/";
   
            }else{

                  $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe cerrar el presupuesto para cargar la progrmación.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });

            }

         }, path, parameter);
       
    }


    

    self.abrir_presupuesto=function(obj){

        location.href=path_principal+"/avanceObraLite/presupuesto/"+obj.id+"/";         
             
    }
    

    self.reporte_trabajo=function(obj){
        path =path_principal+'/api/avanceObraLiteCronograma/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
           
            if (results.programacionCerrada) {

                location.href=path_principal+"/avanceObraLite/reporte_trabajo/"+obj.id+"/";
   
            }else{

                  $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe cerrar la programacion para reportar el trabajo de campo.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });

            }

        }, path, parameter);
        
    }

    self.seguimientos=function(obj,tipo){
        path =path_principal+'/api/avanceObraLiteCronograma/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
           
            if (results.programacionCerrada) {
                if (tipo==1){
                    location.href=path_principal+"/avanceObraLite/seguimientoSemanal/?cronograma_id="+obj.id;
   
                }else if (tipo==2){
                    location.href=path_principal+"/avanceObraLite/seguimientoDiario/?cronograma_id="+obj.id;   
                }
                
            }else{

                  $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe cerrar la programacion para reportar el trabajo de campo.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });

            }

        }, path, parameter);
        
    }

    self.estudio_fecha_fin = ko.observable('');

    self.estudio={
        fecha_inicio:ko.observable('').extend({ required: { message: '(*)Seleccione fecha' } }),
        fecha_fin:ko.observable('').extend({ required: { message: '(*)Seleccione fecha' } }),
     };


    self.abrir_modal_exportar=function(){
        self.estudio.fecha_inicio('');
        self.estudio.fecha_fin('');
        $('#modal_export').modal('show');
    }

    self.exportar_seguimiento_contractual=function(){
        // alert('algo');
        if (IndexViewModel.errores_estudio().length == 0) {
            if(self.estudio.fecha_inicio()<self.estudio.fecha_fin()){
                var validate = false

                ko.utils.arrayForEach(self.listado(), function(d) {
                    // alert(d.fechaInicio);
                    // alert(d.fechaFinal);

                    if (d.fechaInicio<=self.estudio.fecha_inicio()){
                        // alert('1');
                        validate = true
                    }else{
                        validate = false
                    }

                    if (d.fechaFinal>=self.estudio.fecha_inicio()){
                        // alert('2');
                        validate = true
                    }else{
                        validate = false
                    }

                    if (d.fechaInicio<self.estudio.fecha_fin()){
                        // alert('3');
                        validate = true
                    }else{
                        validate = false
                    }

                    if (d.fechaFinal>=self.estudio.fecha_fin()){
                        // alert('4');
                        validate = true
                    }else{
                        validate = false
                    }
                }); 


                

                if (validate){
                    location.href=path_principal+"/avanceObraLite/excel-seguimiento-contractual/"+
                    "?fecha_inicio="+self.estudio.fecha_inicio()+
                    "&fecha_fin="+self.estudio.fecha_fin()+
                    "&id_proyecto="+$('#id_proyecto').val();
                }else{
                    $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Alguna fecha del estudio está fuera del rango del cronograma.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });
                }

            }else{
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>La fecha fin no puede ser menor que la fecha de inicio.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }
            
        }else{
            IndexViewModel.errores_estudio.showAllMessages();//mostramos las validacion
        }
    }

 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance_cronograma"));
index.cargar(1);//iniciamos la primera funcion
IndexViewModel.errores_cronograma = ko.validation.group(index.cronogramaVO);
IndexViewModel.errores_estudio = ko.validation.group(index.estudio);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

function demoCircleGraphs2() {
    var colors = {
        "primary": [bgPrimary, bgPrimaryLr,
            bgPrimaryDr
        ],
        "info": [bgInfo, bgInfoLr, bgInfoDr],
        "warning": [bgWarning, bgWarningLr,
            bgWarningDr
        ],
        "success": [bgSuccess, bgSuccessLr,
            bgSuccessDr
        ],
        "//alert": [bgAlert, bgAlertLr, bgAlertDr]
    };
    var infoCircle2 = $('.info-circle2');
    if (infoCircle2.length) {
        // Color Library we used to grab a random color    
        // Store all circles
        var circles2 = [];
        infoCircle2.each(function(i, e) {
            //alert($(e).attr('title')+' '+$(e).attr('value'));
            ////alert($(e).attr('title'));
            // Define default color
            var color = ['#DDD', bgPrimary];
            // Modify color if user has defined one
            var targetColor = $(e).data(
                'circle-color');
            if (targetColor) {
                var color = ['#DDD', colors[
                    targetColor][0]]
            }
            // Create all circles
            var circle2 = Circles.create({
                id: $(e).attr('id'),
                value: $(e).attr('value'),
                radius: $(e).width() / 2,
                width: 14,
                colors: color,
                text: function(value) {
                    var title = $(e).attr('title');
                    if (title) {
                        return '<h2 class="circle-text-value">'+ title+'%'+ '</h2>'
                    } 
                    else {
                        return '<h2 class="circle-text-value mb5">' + title+'%'+ '</h2>'
                    }
                }
            });
            circles2.push(circle2);
        });      
    }
}

function demoCircleGraphs() {
    var infoCircle = $('.info-circle');
    if (infoCircle.length) {
        // Color Library we used to grab a random color
        var colors = {
            "primary": [bgPrimary, bgPrimaryLr,
                bgPrimaryDr
            ],
            "info": [bgInfo, bgInfoLr, bgInfoDr],
            "warning": [bgWarning, bgWarningLr,
                bgWarningDr
            ],
            "success": [bgSuccess, bgSuccessLr,
                bgSuccessDr
            ],
            "alert": [bgAlert, bgAlertLr, bgAlertDr]
        };
        // Store all circles
        var circles = [];
        infoCircle.each(function(i, e) {
            //alert($(e).attr('title'));
            // Define default color
            var color = ['#DDD', bgPrimary];
            // Modify color if user has defined one
            var targetColor = $(e).data(
                'circle-color');
            if (targetColor) {
                var color = ['#DDD', colors[
                    targetColor][0]]
            }
            // Create all circles
            var circle = Circles.create({
                id: $(e).attr('id'),
                value: $(e).attr('value'),
                radius: $(e).width() / 2,
                width: 14,
                colors: color,
                text: function(value) {
                    var title = $(e).attr('title');
                    if (title) {
                        return '<h2 class="circle-text-value">' + value+ '%' + '</h2><p>' + title + '</p>' 
                    } 
                    else {
                        return '<h2 class="circle-text-value mb5">' + value + '%' + '</h2>'
                    }
                }
            });
            circles.push(circle);
        });
        // Add debounced responsive functionality
        // var rescale = function() { 
        //     infoCircle.each(function(i, e) {
        //         var getWidth = $(e).width() / 2;
        //         circles[i].updateRadius(
        //             getWidth);
        //     });
        //     setTimeout(function() {
        //         // Add responsive font sizing functionality
        //         $('.info-circle').find('.circle-text-value').fitText(0.4);
        //     },50);
        // } 
        // var lazyLayout = _.debounce(rescale, 300);
        // $(window).resize(lazyLayout);
      
    }


    

} // End Circle Graphs Demo

var demoHighLines = function() {
    // Define chart color patterns
    // var highColors = [bgWarning, bgPrimary, bgInfo, bgAlert,
    //     bgDanger, bgSuccess, bgSystem, bgDark
    // ];
    //var highColors = [bgSuccess];
    var highColors = [bgSuccess,bgPrimary
    ];
    var line3 = $('#high-line3');
    //var line4 = $('#high-line4');
    var line5 = $('#high-line5');
    var categorias = [];
    var porcentajes = [];
    var programacion = [];

    var categoriasF = [];
    var porcentajesF = [];
    var montos = [];
    var montos_neto = [];
    
    if (line3.length) {
        //organizar array de categorias
        //var curvaAvanceObra = tablero.listadoCurvaAvanceObra;
        ko.utils.arrayForEach(index.listadoCurvaAvanceObra(), function(obj) {
            categorias.push(obj.fecha);
            porcentajes.push(obj.avance);
            programacion.push(obj.avance_proyectado);
        });

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
                gridLineColor: '#EEE',
                lineColor: '#EEE',
                tickColor: '#EEE',
                categories: categorias,
                labels: {
                    rotation: -90,
                    style: {
                        fontSize: '10px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            },
            yAxis: {
                showEmpty: false,
                min: 0,
                tickInterval: 20,
                offset: 1,
                gridLineColor: '#EEE',
                title: {
                    text: '% de avance de obra',
                },
                categories: ['0','10','20','30','40','50','60','70','80','90','100']//['0','10','20','30','40','50','60','70','80','90','100']
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                             '<td style="padding:0"><b>{point.y:.2f} %</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
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
            },
            series: [
            {
                name: 'Avance fisico',
                data: porcentajes
            },
            {
                name: 'Programacion',
                data: programacion
            }
            ]
        });


    }
    // if (line4.length) {
    //     //organizar array de categorias
    //     //var curvaAvanceObra = tablero.listadoCurvaAvanceObra;
    //     ko.utils.arrayForEach(tablero.listadoCurvaAvanceFinanciero(), function(obj) {
    //         categoriasF.push(obj.fecha);
    //         porcentajesF.push(obj.avance);
    //         //montos.push(obj.monto);
    //     });

    //     $('#high-line4').highcharts({
    //         credits: false,
    //         colors: highColors,
    //         chart: {
    //             backgroundColor: '#f9f9f9',
    //             className: 'br-r',
    //             type: 'line',
    //             zoomType: 'x',
    //             panning: true,
    //             panKey: 'shift',
    //             marginTop: 25,
    //             marginRight: 1,
    //         },
    //         title: {
    //             text: null
    //         },
    //         xAxis: {
    //             gridLineColor: '#EEE',
    //             lineColor: '#EEE',
    //             tickColor: '#EEE',
    //             categories: categorias,
    //             labels: {
    //                 rotation: -90,
    //                 style: {
    //                     fontSize: '10px',
    //                     fontFamily: 'Verdana, sans-serif'
    //                 }
    //             }
    //         },
    //         yAxis: {
    //             showEmpty: false,
    //             min: 0,
    //             tickInterval: 20,
    //             offset: 1,
    //             gridLineColor: '#EEE',
    //             title: {
    //                 text: '% de avance financiero',
    //             },
    //             //categories: categorias//[0,10,20,30,40,50,60,70,80,90,100]//['0','10','20','30','40','50','60','70','80','90','100']
    //         },
    //         tooltip: {
    //             headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
    //             pointFormat: '<tr><td style="color:{series.color};padding:0">Avance: </td>' +
    //                          '<td style="padding:0"><b>{point.y:.1f} %</b></td></tr>',
    //             footerFormat: '</table>',
    //             shared: true,
    //             useHTML: true
    //         },
    //         plotOptions: {
    //             spline: {
    //                 lineWidth: 3,
    //             },
    //             area: {
    //                 fillOpacity: 0.2
    //             }
    //         },
    //         legend: {
    //             enabled: false,
    //         },
    //         series: [{
    //             name: 'Avance financiero',
    //             data: porcentajesF
    //         }]
    //     });


    // }
    if (line5.length) {
        var max = 0;
        intervalo = 1;
        ko.utils.arrayForEach(index.listadoCurvaAvanceFinanciero(), function(obj) {
            // montos_neto.push(obj.monto_neto);
            montos.push(obj.monto);
            
            categoriasF.push(obj.fecha);
            if (max < obj.monto){
                max = obj.monto;
            }
        });
        for (let i=1; i<max.toString().length; i++) {
            intervalo = intervalo * 10;
        }
        $('#high-line5').highcharts({
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
                gridLineColor: '#EEE',
                lineColor: '#EEE',
                tickColor: '#EEE',
                categories: categoriasF,
                labels: {
                    rotation: -90,
                    style: {
                        fontSize: '10px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            },
            yAxis: {
                showEmpty: false,
                min: 0,
                tickInterval: intervalo,
                offset: 1,
                gridLineColor: '#EEE',
                title: {
                    text: 'valor ganado',
                },
                labels: {
                    formatter: function () {
                        return '$' + this.axis.defaultLabelFormatter.call(this);
                    }
                }
                //categories: categorias//[0,10,20,30,40,50,60,70,80,90,100]//['0','10','20','30','40','50','60','70','80','90','100']
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                             '<td style="padding:0"><b>{point.y}</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
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
                enabled: false,
            },
            // series: [{
            //     name: 'Total Costos directos del proyecto',
            //     data: montos,
            //       tooltip: {
            //         valuePrefix: '$'
            //       }
            // }] 

            series: [
                {
                    name: 'Vlr. directo del proyecto',
                    data: montos,
                      tooltip: {
                        valuePrefix: '$'
                      }
                }
            ]            

        });


    }
}


