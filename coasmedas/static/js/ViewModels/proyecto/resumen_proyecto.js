
var highColors = ['#228BF5','#B522F5','#0EC11D'
    ];
    
function HojaResumenViewModel() {
    
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.lista_porcentaje=ko.observableArray([]);
    self.mensaje_descargo=ko.observable('');
    self.mensaje_soporte_correspondencia=ko.observable('');
    self.mensaje_proyecto_contrato=ko.observable('');
    self.mensaje_categoria=ko.observable('');
    self.listado_categoria=ko.observableArray([]);
    self.listado_subcategoria=ko.observableArray([]);
    self.listado_fotos_subcategoria=ko.observableArray([]);  

    self.por_base=ko.observableArray([]);
    self.por_programada=ko.observableArray([]);
    self.por_avance=ko.observableArray([]);
    self.listado_contrato_proyecto=ko.observableArray([]);
    self.mensaje_giros_contrato=ko.observable('');
    self.listado_giros_contrato=ko.observableArray([]);
    self.mensaje_poliza_contrato=ko.observable('');
    self.listado_poliza_contrato=ko.observableArray([]);
    self.mensaje_vigencia_contrato=ko.observable('');
    self.listado_vigencia_contrato=ko.observableArray([]);
    self.mensaje_actas_replanteo=ko.observable('');
    self.listado_actas_replanteo=ko.observableArray([]);

    self.proyecto=ko.observable(0);
    self.lista_estado_select=ko.observableArray([]);
    self.listado_contrato=ko.observableArray([]); 
    self.listado_empresa=ko.observableArray([]);
    self.listado_funcionario_empresa=ko.observableArray([]);
    self.cronograma_select=ko.observable(0);
    self.cantidad_cronograma=ko.observableArray([]);
    self.cronograma_id=ko.observableArray([]);
    self.listado_correspondencia=ko.observableArray([]);
    self.listado_soporte_correspondencia=ko.observableArray([]);

    self.checkallcategoria=ko.observable(false);
    self.checkallSubcategoria=ko.observable(false);
    self.desde=ko.observable('');
    self.hasta=ko.observable('');
    self.procesoRelacionId=ko.observable(0);
    self.listado_seguimiento=ko.observableArray([]);
    self.mensaje_listado_seguimiento=ko.observable('');
    self.porcentaje_seguimiento=ko.observable(0);
    self.porcentaje_se=ko.observable(0);
    self.listado_soportes=ko.observableArray([]);
    self.mensaje_listado_soportes=ko.observable('');
    self.porcentajes=ko.observableArray([]);
    self.listadoCurvaAvanceObra=ko.observableArray([]);
    self.listadoCurvaAvanceFinanciero=ko.observableArray([]);
    self.programacion = ko.observableArray([]);    
    
    
     //paginacion de cuenta
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

    //paginacion
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);        
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }


    //funcion para filtrar los descargos por estado
    self.filtrar_estado = function () {
        self.titulo('Filtrar descargos');
        $('#modal_filtro_descargo').modal('show');
    }


    //funcion para mostrar los contrato
    self.ver_contratos = function (proyecto,empresa) {
        self.titulo('Contratos');
        self.consultar_contrato(proyecto,empresa);
    }


        //funcion para ver funcionarios de la empresa
    self.ver_funcionarios_empresa = function (proyecto,empresa) {
        self.titulo('Responsables');
        self.consultar_funcionario_empresa(proyecto,empresa);
        //$('#ver_funcionarios').modal('show');
    }


        //ver los soportes del consecutivo 
    self.ver_soportes_correspondencia = function (obj) {

        self.titulo('Documentos asociados a la correspondencia');
        self.soportes_correspondencia(obj);
        $('#vermas_soportes_correspondencia').modal('show');
    }


    //funcion para ver mas procesos de liquidacion de contrato
    self.ver_mas_proceso = function (proceso_id,apuntador,proyecto_id) {

        self.procesoRelacion(proceso_id,apuntador,proyecto_id);
        self.titulo('Liquidacion de contrato');
        $('#vermas_liquidacion').modal('show');
    }


    //funcion para mostrar los soportes de cada proceso
    self.ver_soporte_proceso= function (procesoRelacionDato) {
        self.titulo('Soportes');
        self.mensaje_listado_soportes('');
        self.consultar_soportes(procesoRelacionDato);
        $('#vermas_soportes_proceso').modal('show');
    }

    //consultar la api de soporte proceso relacion dato para traerme los soportes
    self.consultar_soportes=function(procesoRelacionDato){

        path = path_principal+'/api/soporteProcesoRelacionDato/?format=json';
        parameter={ procesoRelacionDato: procesoRelacionDato};
        RequestGet(function (datos, estado, mensaje) {

            if (datos.data!=null && datos.data.length > 0) {

                self.listado_soportes(datos.data);

            } else {
                self.listado_soportes([]);
                self.mensaje_listado_soportes(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
            
           

        }, path, parameter);

    } 


   //consultar la api proceso relacion
    self.procesoRelacion=function(proceso_id,apuntador,proyecto_id){

        path = path_principal+'/api/procesoRelacion/?format=json';
        parameter={ proceso: proceso_id, idApuntador:proyecto_id };
        RequestGet(function (datos, estado, mensaje) {
            //alert(datos.data[0].id)
            
            self.procesoRelacionId(datos.data[0].id);
            self.list_seguimiento();

        }, path, parameter);

    }


    //listado de seguimiento de liquidacion
    self.list_seguimiento=function(){

         path = path_principal+'/api/procesoRelacionDato/?format=json';
         parameter={ procesoRelacion:self.procesoRelacionId(),ignorePagination:1 };
         RequestGet(function (datos, estado, mensaje) {
            
            //if (datos.data.listado[0]!=null && datos.data.listado.length > 0) {
            if (datos.listado[0]!=null && datos.listado.length > 0) {

                self.mensaje_listado_seguimiento('');
                self.listado_seguimiento(datos.listado);
                self.porcentaje_seguimiento(datos.etiquetaPorcentaje);
                self.porcentaje_se(datos.porcentaje);

            } else {
                    self.listado_seguimiento([]);
                    self.mensaje_listado_seguimiento(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }

         }, path, parameter);

    }

   
    //funcion para seleccionar las categorias
    self.checkallcategoria.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado_categoria(), function(d) {

            d.eliminado(value);

            if(d.eliminado()==true){

               self.consultar_subcategoria();

            }else{

                self.listado_subcategoria([]);
            }

            
        }); 
    });


    //funcion para seleccionar las subcategorias
    self.checkallSubcategoria.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado_subcategoria(), function(d) {

            d.eliminado(value);

            if(d.eliminado()==true){

                self.consultar_fotos_subcategoria();

            }else{

                self.listado_fotos_subcategoria([]);
            }

        }); 
    });


    //listado de soportes de correspondencia
    self.soportes_correspondencia=function(obj){

         path = path_principal+'/api/CorrespondenciaSoporte/?format=json';
         parameter={ correspondencia:obj.id };
         RequestGet(function (datos, estado, mensaje) {
            
            if (datos.data!=null && datos.data.length > 0) {

                self.mensaje_soporte_correspondencia('');
                self.listado_soporte_correspondencia(datos.data);

            } else {
                    self.listado_soporte_correspondencia([]);
                    self.mensaje_soporte_correspondencia(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }

         }, path, parameter);

    }

    //consultar la cantidad de cronograma y la id del cronograma solo debe traer uno
    self.consultar_cantidad_cronograma=function(proyecto_id){

         path =path_principal+'/api/Cronograma?sin_paginacion&format=json';
         parameter={ id_proyecto:proyecto_id};
         RequestGet(function (datos, estado, mensaje) {
          
            if(datos!=null && datos.length > 0){

                self.cantidad_cronograma(datos[0].proyecto.totalCronograma); //cantidad de cronograma por proyecto

                //alert(datos[0].proyecto.totalCronograma)

                if(self.cantidad_cronograma()==1){

                    self.cronograma_id(datos[0].id); //id_cronograma

                    self.grafica_avance(1,self.cronograma_id());

                }

            }

         }, path, parameter);
         
    }

        //consultar los estados para llenar un select
    self.consultar_lista_estado=function(){
        
         path =path_principal+'/api/Estados?ignorePagination';
         parameter={ dato: 'descargo' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_estado_select(datos);

         }, path, parameter);

    }

   
    //funcion consultar los proyecto
    self.consultar = function (pagina) {

        if (pagina > 0) { 

            var tipo_estado=$("#estado_filtro").val();           

            path = path_principal+'/api/Descargo/?format=json';
            parameter = { dato:'', page: pagina, proyecto:self.proyecto(), estado:tipo_estado};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje_descargo('');
                    self.listado(agregarOpcionesObservable(datos.data));  

                } else {
                    self.listado([]);
                    self.mensaje_descargo(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter);
        } 
    }




    self.consultar_contrato = function (proyecto,empresa) {

       path =path_principal+'/api/Proyecto_empresas/?format=json&ignorePagination';
       parameter = { proyecto: proyecto, empresa: empresa }
         RequestGet(function (datos, estado, mensage) {

            if (datos[0].proyecto.contrato!=null && datos[0].proyecto.contrato.length > 0) {

                $("#mensaje_contrato_validacion").html('');
                self.listado_contrato(datos[0].proyecto.contrato);
                $('#ver_contratos').modal('show');

            } else {

                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>No se encontraron contratos relacionados al proyecto.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }  


         }, path, parameter);
     }


    self.consultar_empresa = function (proyecto) {

       path =path_principal+'/proyecto/listEmpresasDelProyecto/?format=json';
       parameter = { proyecto_id: proyecto }
         RequestGet(function (datos, estado, mensage) {

            if (datos!=null && datos.length > 0) {
                $("#mensaje_funcionario").html('');
                self.listado_empresa(datos);

            } else {
                    self.listado_empresa([]);
                   $("#mensaje_funcionario").html('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning fa-2x"></i>No se encontro correspondencia asociada al proyecto.</div>');
            }     

         }, path, parameter);
     }


    self.consultar_funcionario_empresa = function (proyecto,empresa) {

        path =path_principal+'/proyecto/list_proyecto_funcionario/?format=json';
        parameter = { proyecto_id: proyecto , empresa_id:empresa}
        RequestGet(function (datos, estado, mensage) {

            //console.log(datos);        
            if(datos==''){

                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>No se encontraron funcionarios activos relacionados al proyecto.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });

            }else{  

                self.listado_funcionario_empresa(datos);
                $('#ver_funcionarios').modal('show');

            }

         }, path, parameter);
     } 

/* ARCHIVOS -- ARCHIVOS -- ARCHIVOS -- ARCHIVOS -- ARCHIVOS -- ARCHIVOS -- ARCHIVOS */
    var administraccion_de_recurso = 12;
    self.listado_archivos=ko.observableArray([]);  
    //VARIABLES
    self.mcontrato_id=ko.observable('');
    self.departamento_id=ko.observable('');
    self.municipio_id=ko.observable('');
    self.proyecto_id=ko.observable('');
    self.checkall=ko.observable(false);

    //VARIABLES DE BUSQUEDA
    self.proyecto_id=ko.observable(0);
    self.m_contrato_id=ko.observable(0);

    //DOBLE CLICK IZQUIERDO
    self.dobleclick  = function(d,e){
        /*SI TIPO DE ARCHIVO ES 58 PORQUE ES UNA CARPETA*/
        if(d.tipoArchivo_id==58){
            $('#jstree').jstree("close_all");   
            $('#jstree').jstree("open_node",d.id);
            $("#jstree").jstree("deselect_all");
            $("#jstree").jstree("select_node",'#'+d.id);
            self.consultar();
        }else{
            //window.open(d.destino,"_blank");
            window.open(path_principal+"/miNube/descargar-un-archivo/?archivo="+ d.id, "_blank");
        }
    }
    //descargar archivos 
    self.descarga_archivo = function () { 
        var lista_id=[];
        var count=0;
         ko.utils.arrayForEach(self.listado_archivos(), function(d) {
                if(d.eliminado()==true){
                    count=1;
                    lista_id.push(d.id)                 
                }
         });             

        if(lista_id.length>0){
            location.href=path_principal+"/miNube/download_file?archivo="+ lista_id;
        }else{
            mensajeInformativo('Debe seleccionar un archivo ó carpeta.','Mi Nube');
        } 
    } 

    self.abrir_modal_filtro = function () { $('#modal_acciones_filtro').modal('show'); }  

    self.consultarContratoProyecto_btn = function (d,e) {
        self.consultarContratoProyecto();
    }
    self.consultarContratoProyecto_enter = function (d,e) {
        if (e.which == 13) {
            self.consultarContratoProyecto();
        }
        return true;
    } 
    //funcion consultar archivos que puede ver la persona
    self.consultarContratoProyecto = function () {  
        padre_id = parseInt($("#jstree").jstree("get_selected")) ; 
        if(!isNaN(padre_id)){
            self.filtro($('#txtBuscarContratoProyecto').val());
            path = path_principal+'/miNube/list_archivo_ContratoProyecto/';
            parameter = { dato: self.filtro() , padre : padre_id , mcontrato : self.m_contrato_id() , proyecto : self.proyecto_id() };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    self.listado_archivos(agregarOpcionesObservable(datos))
                } else {
                    self.listado_archivos([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
            }, path, parameter); 
        }        
    }

    self.checkall.subscribe(function(value ){
         ko.utils.arrayForEach(self.listado_archivos(), function(d) { d.eliminado(value); }); 
    });
    //consulta para crear el arbol solo consulta carpetas
    self.consultar_arbol = function (){
            path = path_principal+'/miNube/list_carpeta_ContratoProyecto/';
            parameter = { proyecto : self.proyecto_id() };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {                       

                    $('#jstree').jstree({  
                          'core': {
                           'data':  datos,
                           "check_callback" : true
                          },           
                          "state" : { "key" : "state_demo" },           
                          "plugins" : [ "sort","state"]
                    });  
      
                }       

            }, path, parameter);
    }    

    

 //funcion que se ejecuta cuando se cambia en el select de cronograma
    self.cronograma_select.subscribe(function (value) {

        if(value >0){

            self.grafica_avance(1,value);

        }else{

            self.lista_porcentaje(0);
            self.por_base(0);
            self.por_programada(0);
            self.por_avance(0);
        }
    });



     //funcion consultar de tipo get recibe un parametro
    self.grafica_avance = function (pagina,id_cronograma) {
                    
        self.filtro(0);
        path = path_principal+'/avance_de_obra/listar_linea_base/'+id_cronograma+'/'+pagina+'/'+3+'/'+self.filtro();
        parameter=''
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok') {
                    self.mensaje('');
                    //self.listado(results);     
                    self.mostrar_grafica_barra(datos.result);                        
                    self.mostrar_grafica_linea(datos.porcentaje_grafica,id_cronograma);
            } else {
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
        }, path, parameter);

    }

    //grafica de barra
    self.mostrar_grafica_barra=function(data){
        var lista_capitulos=[];
        self.lista_porcentaje([]);
        var fecha=[];
        
        ko.utils.arrayForEach(data, function(d) { 

            if(d['nivel']==1){
                lista_capitulos.push(d['nombre'].substring(0, 15));
                var valor=(d['total']*100)/d['meta']
                if(valor>100){
                    valor=100;
                }
                self.lista_porcentaje.push(Math.round(valor,2));

            }
        });

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
                            
                            categories: lista_capitulos,
                            labels: {
                                rotation: -90,
                                style: {
                                    fontSize: '9px',
                                    fontFamily: 'Verdana, sans-serif'
                                }
                            }
                        },
                tooltip: {
                            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                            pointFormat: '<tr><td style="color:{series.color};padding:0">Avance: </td>' +
                                '<td style="padding:0"><b>{point.y:.1f} %</b></td></tr>',
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
                        },
                series: [{
                            name: lista_capitulos,
                            data: self.lista_porcentaje()
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
    }

    self.array_porcentaje=function(data,numeros_dias,fecha){

        var lista=[];
        
        ko.utils.arrayForEach(data, function(d) { 
                var valor=(numeros_dias*d.intervalo)-numeros_dias;
                var res=fecha.split('-');
                fecha_intervalo= new Date(res[0],res[1]-1,res[2]);
                fecha_intervalo.setDate(fecha_intervalo.getDate()+parseInt(valor));
                var anno=fecha_intervalo.getFullYear();
                var mes= fecha_intervalo.getMonth()+1;
                var dia= fecha_intervalo.getDate();
                mes = (mes < 10) ? ("0" + mes) : mes;
                dia = (dia < 10) ? ("0" + dia) : dia;
                var lista2=[]
                lista2.push(Date.UTC(anno, mes, dia),d['porcentaje']);
                lista.push(lista2);
        });
        return lista;          
             
    }

    self.mostrar_grafica_linea=function(data,cronograma_id){

        path = path_principal+'/api/Cronograma/'+cronograma_id;
        parameter = '';
        RequestGet(function (datos, estado, mensaje) {
                 
            var fecha=[];
            self.por_base(self.array_porcentaje(data.base,datos.periodicidad.numero_dias,datos.fecha_inicio_cronograma));
            self.por_programada(self.array_porcentaje(data.programada,datos.periodicidad.numero_dias,datos.fecha_inicio_cronograma))
            self.por_avance(self.array_porcentaje(data.avance,datos.periodicidad.numero_dias,datos.fecha_inicio_cronograma))
                    
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
                                colors: [bgPrimary, bgPrimary,
                                    bgInfo, bgInfo
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
                            name: 'Linea Base',
                            data: self.por_base()
                        }, {
                            name: 'Linea Programada',
                            data: self.por_programada()
                        }, {
                            name: 'Linea de Avance',
                            data: self.por_avance()
                        }]
                    });
        }, path, parameter);
       
    }


            //consulta la correspondencia
    self.consultar_correspondencia=function(proyecto){

        path =path_principal+'/correspondencia/list_correspondenciaEnviadaProyecto/?format=json';
        parameter = {proyecto_id: proyecto};
        RequestGet(function (datos, estado, mensaje) {

            if (datos!=null && datos.length > 0) {
                $("#mensaje_correspondencia").html('');
                self.listado_correspondencia(datos);

                console.log(datos) 

            } else {
                    self.listado_correspondencia([]);
                   $("#mensaje_correspondencia").html('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning fa-2x"></i>No se encontro correspondencia asociada al proyecto.</div>');
            }
           
           
         }, path, parameter);

         
    }


    //consultar los procesos segun el proyecto
    self.consultar_contrato_proyecto = function (proyecto) {

        path =path_principal+'/proyecto/listado_proceso/';
        parameter={ proyecto_id:proyecto};

        RequestGet(function (datos, estado, mensage) {

            if (datos!=null && datos.length > 0) {
                self.mensaje_proyecto_contrato('');
                self.listado_contrato_proyecto(datos); 

            } else {
                self.listado_contrato_proyecto([]);
                //self.mensaje_proyecto_contrato(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                self.mensaje_proyecto_contrato(mensageNoFound(mensage));
            }


        }, path, parameter);
    }



        //consultar los giros asociados a los contratos del proyecto
    self.consultar_giros_contrato = function (proyecto) {

        path =path_principal+'/proyecto/listado_giros/';
        parameter={ proyecto_id:proyecto};

        RequestGet(function (datos, estado, mensage) {

            if (datos!=null && datos.length > 0) {
                self.mensaje_giros_contrato('');
                self.listado_giros_contrato(datos); 

            } else {
                self.listado_giros_contrato([]);
                //self.mensaje_giros_contrato(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                self.mensaje_giros_contrato(mensageNoFound('No se encontraron giros relacionados a los contratos'));
            }


        }, path, parameter);
    }


            //consultar los giros asociados a los contratos del proyecto
    self.consultar_poliza_contrato = function (proyecto) {

        path =path_principal+'/proyecto/listado_poliza/';
        parameter={ proyecto_id:proyecto};

        RequestGet(function (datos, estado, mensage) {

            if (datos!=null && datos.length > 0) {
                self.mensaje_poliza_contrato('');
                self.listado_poliza_contrato(datos); 

            } else {
                self.listado_poliza_contrato([]);
                //self.mensaje_poliza_contrato(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                self.mensaje_poliza_contrato(mensageNoFound(mensage));
            }


        }, path, parameter);
    }


    //consultar las vigencias asociados a los contratos del proyecto
    self.consultar_vigencia_contrato = function (proyecto,validacion) {

        path =path_principal+'/proyecto/listado_vigencia/';
        parameter={ proyecto_id:proyecto,validacion:validacion};

        RequestGet(function (datos, estado, mensage) {

            if (datos!=null && datos.length > 0) {

                if (validacion==1){

                    self.mensaje_vigencia_contrato('');
                    self.listado_vigencia_contrato(datos);

                }else if (validacion==2){

                    self.mensaje_actas_replanteo('');
                    self.listado_actas_replanteo(datos);
                }
                 

            } else {

                    if (validacion==1){

                        self.listado_vigencia_contrato([]);
                        //self.mensaje_vigencia_contrato(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                        self.mensaje_vigencia_contrato(mensageNoFound(mensage));

                    }else if (validacion==2){

                        self.listado_actas_replanteo([]);
                        //self.mensaje_actas_replanteo(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js

                        self.mensaje_actas_replanteo(mensageNoFound(mensage));
                    }
               
            }


        }, path, parameter);
    }


    //funcion consultar las categorias
    self.consultar_categoria = function (id_proyecto) {        

        path = path_principal+'/api/categoria?format=json';
        parameter = {proyecto:id_proyecto};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje_categoria('');
                self.listado_categoria(agregarOpcionesObservable(datos.data));   

            } else {
                self.listado_categoria([]);
                self.mensaje_categoria(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }

        }, path, parameter);
    }


    //consultar las subcategorias
    self.consultar_subcategoria = function () {

         var lista_id='';
         var count=0;
         ko.utils.arrayForEach(self.listado_categoria(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id+=d.id+',';
                   
                }
         });

        if(lista_id !=''){

            lista_id=lista_id.slice(0,-1);

            path = path_principal+'/api/subcategoria?format=json';
            parameter = {lista:lista_id,id_proyecto:self.proyecto()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    //self.mensaje('');
                    self.listado_subcategoria(agregarOpcionesObservable(datos.data));   

                } else {
                    self.listado_subcategoria([]);
                    //self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

            }, path, parameter);

        }else{

           self.listado_subcategoria([]); 
        }
      
         return true;
        
    }


    //consultar las fotos de las subcategoria
    self.consultar_fotos_subcategoria = function () {

        var lista_sub_id='';
        var count=0;

        ko.utils.arrayForEach(self.listado_subcategoria(), function(d) {

            if(d.eliminado()==true){
                count=1;
                lista_sub_id+=d.id+',';
                   
            }
        });

        if(lista_sub_id!=''){

            lista_sub_id=lista_sub_id.slice(0,-1);

            path = path_principal+'/api/fotos_subcategoria?format=json';
            parameter = {lista:lista_sub_id,desde:self.desde(),hasta:self.hasta()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    //self.mensaje('');
                    self.listado_fotos_subcategoria(agregarOpcionesObservable(datos.data));   

                } else {
                    self.listado_fotos_subcategoria([]);
                    //self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

            }, path, parameter);

        }else{
            self.listado_fotos_subcategoria([]);

        } 
        
        return true;
        
    }
    self.getIdCronograma =function(id_proyecto){           
        $('#loading2').show();
        path = path_principal+'/api/avanceGrafico2Cronograma/?format=json';
        parameter = {proyecto_id:id_proyecto};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {                
                self.cargarGrafica(datos.data[0].id);
            } else {                
                //self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
            $('#loading2').hide();
            cerrarLoading();
        }, path, parameter,undefined, false);

    }    

    self.cargarGrafica = function(id) {
        path = path_principal+'/avanceObraGrafico2/graficacronograma/'+id+'/';
        parameter = {}
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null) {
                self.mensaje('');
                //self.listado(results); 
                self.porcentajes (agregarOpcionesObservable(datos.porHito));
                self.listadoCurvaAvanceObra (agregarOpcionesObservable(datos.curvaAvanceObra));
                self.listadoCurvaAvanceFinanciero(agregarOpcionesObservable(datos.curvaAvanceFinanciero));
                self.programacion (agregarOpcionesObservable(datos.curvaProgramada));

            } else {
                self.porcentajes([]);
                self.listadoCurvaAvanceObra([]);
                self.listadoCurvaAvanceFinanciero([]);
            }
            demoCircleGraphs();
            demoHighLines();
            // cerrarLoading();
        }, path, parameter,undefined, false);

    }    

}

var resumen = new HojaResumenViewModel();
ko.applyBindings(resumen);
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
                        return '<h2 class="circle-text-value">' + value + '</h2><p>' + title + '</p>' 
                    } 
                    else {
                        return '<h2 class="circle-text-value mb5">' + value + '</h2>'
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
    if (line3.length) {
        //organizar array de categorias
        //var curvaAvanceObra = tablero.listadoCurvaAvanceObra;
        ko.utils.arrayForEach(resumen.listadoCurvaAvanceObra(), function(obj) {
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
        ko.utils.arrayForEach(resumen.listadoCurvaAvanceFinanciero(), function(obj) {
            montos.push(obj.monto);
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
                pointFormat: '<tr><td style="color:{series.color};padding:0">vlr. ganado: </td>' +
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
            series: [{
                name: 'Valor ganado',
                data: montos,
                  tooltip: {
                    valuePrefix: '$'
                  }
            }]
        });


    }
}