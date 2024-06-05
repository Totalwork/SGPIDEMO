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
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);


    self.checkall2=ko.observable(false);

    self.listado_estado=ko.observableArray([]);
    self.checkall3=ko.observable(false);
    self.listado_filter_colaboradores=ko.observableArray([]);
    var lista_id_estado='';

    self.mensaje_grafico=ko.observable('');

    self.filterVO={
        desde:ko.observable(''),
        hasta:ko.observable('')
    }

    self.lista_macrocontrato=ko.observableArray([]);
    self.id_macrocontrato=ko.observable(0);
    self.listado_contratista=ko.observableArray([]);
    self.id_contratista=ko.observable(0);
    self.listado_departamento=ko.observableArray([]);
    self.id_departamento=ko.observable(0);
    self.listado_municipio=ko.observableArray([]);
    self.id_municipio=ko.observable(0);
    self.listado_proyectos=ko.observableArray([])
    self.id_proyecto=ko.observableArray([]);

    self.tareaVO={
        id:ko.observable(0),
        asunto:ko.observable('').extend({ required: { message: '(*)Digite el asunto de la tarea' } }),
        descripcion:ko.observable(''),
        fecha_fin:ko.observable('').extend({ required: { message: '(*)Digite una fecha fin de la tarea' } }),
        colaborador_actual_id:ko.observable(0),
        numero:ko.observable(0),
        tipo_tarea_id:ko.observable(0),
        usuario_responsable_id:ko.observable(0),
        comentario:ko.observable(''),
        proyecto_id:ko.observable(0),
        listado_archivo:ko.observableArray([{
            'soporte':ko.observable('')
        }]),
        listado_proyectos:ko.observableArray([])       
    }

    self.porcentaje_total=ko.observable(0);

    self.nombre_tarea=ko.observable('');
    self.listado_soporte=ko.observableArray([]);
    self.mensaje_soporte=ko.observable('');

    self.id_equipo=ko.observable(0);
	
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

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Tarea');
        $('#modal_acciones').modal('show');
    }

    self.abrir_modal_grafica1 = function () {
        self.limpiar();
        self.titulo('Mi rendimiento general por grupo');
        self.graficar_circular();
        $('#modal_circular').modal('show');
    }

    self.abrir_modal_grafica2 = function () {
        self.limpiar();
        self.titulo('Productividad por actividad de grupo');
        self.grafica_barra();
        $('#modal_barra').modal('show');
    }

    self.abrir_modal_edicion = function (obj) {
        self.titulo('Edicion de la Tarea');
        self.consultar_id_tarea(obj.id)
    }

     self.abrir_detalle_tarea = function (obj) {
        location.href=path_principal+"/administrador_tarea/detalle_tarea/"+obj.id;
    }

     self.abrir_agenda = function (obj) {
        location.href=path_principal+"/administrador_tarea/agenda/";
    }

    self.abrir_modal_filtro = function (obj) {
        self.titulo('Filtro');
        $('#modal_filter').modal('show');
    }


    self.limpiar_filtro=function(){
        self.checkall3(false);
        lista_id_estado='';
        self.filterVO.desde('');
        self.filterVO.hasta('');
        self.consultar(1);
    }

    self.abrir_modal_soporte = function (obj) {
        self.limpiar();
        self.checkall2(false);
        self.mensaje_soporte('');
        self.titulo('Folder de Archivo');
        self.nombre_tarea(obj.asunto);

        path = path_principal+'/api/SoporteAsignacionTarea/?format=json&sin_paginacion';
        parameter = {tarea_id:obj.id};
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado_soporte(agregarOpcionesObservable(datos));
                     $('#modal_acciones').modal('hide');

                } else {
                    self.listado_soporte([]);
                     self.mensaje_soporte('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron registros</div>');
                    
                    //self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
                

                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
        }, path, parameter);
        $('#modal_soportes').modal('show');
    }


    self.abrir_modal_estado = function () {

        var count=0;
        ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                }
        });

        if(count==0){
            $.confirm({
                title:'Error',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una tarea para cambiar el estado.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{

            self.titulo('Cambiar a no leído');
            $('#modal_estado').modal('show');  
        }
    }


    self.consultar_id_tarea=function(id){

            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/Tarea/'+id+'/';
            parameter ='';
            RequestGet(function (datos, estado, mensage) {
                self.tareaVO.id(datos.id);
                self.tareaVO.fecha_fin(datos.fecha_fin);  
                self.tareaVO.asunto(datos.asunto);
                self.tareaVO.descripcion(datos.descripcion);
                self.tareaVO.colaborador_actual_id(datos.colaborador_actual_id);
                self.tareaVO.usuario_responsable_id(datos.usuario_responsable_id);
                self.tareaVO.numero(datos.numero);
                self.tareaVO.tipo_tarea_id(datos.tipo_tarea.id);
                self.tareaVO.listado_proyectos(datos.proyecto);
                $('#modal_edicion').modal('show');

                cerrarLoading();
            }, path, parameter,undefined, false);
    }

    self.consultar_estado=function(){
        path = path_principal+'/api/Estados?format=json&ignorePagination';
        parameter = {aplicacion:'Tarea'};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {                    
                    self.listado_estado(agregarOpcionesObservable(datos));
                } else {
                    self.listado_estado([]);
                }
                
            }, path, parameter,undefined, false,false);
    }

     self.archivo_zip=function(){
        var cont=0;
        listado_id="";
        ko.utils.arrayForEach(self.listado_soporte(), function(d) {

                if(d.eliminado()==true){
                    if(listado_id==""){
                        listado_id=d.id;
                    }else{
                        listado_id=listado_id+","+d.id;
                    }
                    cont++;
                }
        }); 

        if(cont==0){
            self.mensaje_soporte('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>Seleccione un archivo para descargar.</div>');
            return true;
        }

        window.open(path_principal+"/administrador_tarea/download_zip?archivo="+ listado_id,'_blank');
    }

    self.archivo_download=function(obj){
        window.open(path_principal+"/administrador_tarea/ver-soporte?id="+ obj.id,'_blank');
    }

    self.checkall3.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_estado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.checkall2.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_soporte(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.id_equipo.subscribe(function(value ){

            if(value>0){
                self.graficar_circular();  
            }else{
                self.mensaje_grafico('');
            }
            
    });
    

    self.grafica_barra=function(){

        path = path_principal+'/administrador_tarea/grafica2';
        parameter = '';

        RequestGet(function (datos, estado, mensage) {

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
                            pointFormat: '<tr><td style="padding:0"><b>Rendimiento:{point.y:.1f} %</b></td></tr>',
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
                        series:[{
                                name: 'Tarea',
                                colorByPoint: true,
                                data:datos
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
            }, path, parameter,undefined, false,false);

        
    }

    


    self.graficar_circular=function(){
                var pie1 = $('#high-pie');                 
                self.mensaje_grafico('');         
                path = path_principal+'/administrador_tarea/grafica1';
                parameter = {equipo_id:self.id_equipo()};
                RequestGet(function (datos, estado, mensage) {

                        if(datos.length==0){ 
                            self.mensaje_grafico(mensajeNoFound);
                        }

                         if (pie1.length) {

                                    // Pie Chart1
                                    $('#high-pie').highcharts({
                                        credits: false,
                                        title: {
                                            text: null
                                        },
                                        tooltip: {
                                            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                                        },
                                        plotOptions: {
                                            pie: {
                                                center: ['30%', '50%'],
                                                allowPointSelect: true,
                                                cursor: 'pointer',
                                                dataLabels: {
                                                    enabled: false
                                                },
                                                showInLegend: true
                                            }
                                        },
                                        colors: highColors,
                                        legend: {
                                            x: 90,
                                            floating: true,
                                            verticalAlign: "middle",
                                            layout: "vertical",
                                            itemMarginTop: 10
                                        },
                                        series: [{
                                            type: 'pie',
                                            name: 'Tareas',
                                            data: datos
                                        }]
                                    });
                            }
                        
        }, path, parameter,undefined, false,false);                
    }

    self.consultar_filtro=function(){

        lista_id_estado='';        
        var count=0;
        ko.utils.arrayForEach(self.listado_estado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                    if(lista_id_estado!=''){                        
                        lista_id_estado=lista_id_estado+','+d.id;
                    }else{
                        lista_id_estado=d.id;
                    }
                }
         });
        self.consultar(1);

    }


    self.cambiar_estado=function(){

        var lista_id=[];
        ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                    lista_id.push({
                        id:d.id
                   })
                }
        });

        var parametros={                     
            callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        self.filtro("");
                        self.checkall(false);
                        self.consultar(self.paginacion.pagina_actual());
                        $('#modal_estado').modal('hide');
                        self.limpiar();
                        
                    }                        
                    
                 },//funcion para recibir la respuesta 
                 url:path_principal+'/administrador_tarea/cambiar_estado/',//url api
                 parametros:{lista: lista_id,usuario_responsable_id:$('#id_usuario').val()}                    
            };
                //parameter =ko.toJSON(self.contratistaVO);
        Request(parametros);

    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

    self.agregar_soporte=function(){
        self.tareaVO.listado_archivo.push({'soporte':ko.observable('')});
    }

    self.eliminar_soporte=function(val){
        self.tareaVO.listado_archivo.remove(val);
    }

     self.limpiar=function(){ 

        self.nombre_tarea('');
        self.tareaVO.id(0);
        self.tareaVO.asunto('');
        self.tareaVO.descripcion('');
        self.tareaVO.fecha_fin('');
        self.tareaVO.colaborador_actual_id(0);
        self.tareaVO.numero(0);
        self.tareaVO.usuario_responsable_id(0);
        self.tareaVO.listado_archivo([]);
        self.tareaVO.listado_archivo([{
            'soporte':ko.observable('')
        }]);
        self.tareaVO.listado_proyectos([]);
        self.id_macrocontrato(0);
        self.id_contratista(0);
        self.id_departamento(0);
        self.id_municipio(0);
        self.tareaVO.comentario('');
     }


    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.consultar_macrocontrato=function(){
        
         // path =path_principal+'/proyecto/filtrar_proyectos/?tipo=2';
         path =path_principal+'/proyecto/filtrar_proyectos/?tipo=12';
         parameter='';
         RequestGet(function (results,count) {
           
            self.lista_macrocontrato(results.macrocontrato);

         }, path, parameter,undefined, false,false);
         // $('#loading').hide();
    }

    self.id_macrocontrato.subscribe(function(value){

        var tipo='12';
        if(value!=0){

            path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+value+'&tipo='+tipo;
            parameter = '';
            RequestGet(function (datos, estado, mensage) {
                
                if (estado=='ok') {
                    self.listado_contratista(datos.contratista);
                    self.listado_departamento(datos.departamento);
                    self.listado_municipio(datos.municipio);
                    self.consultar_proyecto();

                }
            }, path, parameter);
        }else{
            self.listado_contratista([]);
            self.consultar_departamento();
            self.listado_municipio([]);
            self.listado_proyectos([]);
        }

    });

 

    self.id_departamento.subscribe(function(value){


        if(value!=0){

            if(self.id_macrocontrato()>0 || self.id_contratista()>0){                

                path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+self.id_macrocontrato()+'&contratista='+self.id_contratista()+'&departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                        self.listado_municipio(datos.municipio);
                        self.consultar_proyecto();
                }, path, parameter);
            }else{
                path = path_principal+'/api/Municipio/?ignorePagination&id_departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                    self.listado_municipio(datos);
                    self.consultar_proyecto();
                }, path, parameter);
            }
        }

    });


    self.id_contratista.subscribe(function(value){


        if(value!=0){
                path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+self.id_macrocontrato()+'&contratista='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                        self.listado_departamento(datos.departamento);
                        self.listado_municipio(datos.municipio);
                        self.consultar_proyecto();

                }, path, parameter);
           
        }

    });


    self.id_municipio.subscribe(function(value){


        if(value!=0){
            
           self.consultar_proyecto();
        }

    });


    self.consultar_proyecto=function(){

        path = path_principal+'/api/Proyecto/?format=json&ignorePagination';
        parameter = {departamento_id:self.id_departamento(),municipio_id:self.id_municipio(),
            contrato:self.id_macrocontrato(), id_contratista:self.id_contratista()};
        RequestGet(function (datos, estado, mensage) {
            self.listado_proyectos(datos);
        }, path, parameter);
    }


     self.consultar_departamento=function(){

            path = path_principal+'/api/departamento/?ignorePagination';
            parameter = '';
            RequestGet(function (datos, estado, mensage) {

                if (datos.length > 0) {
                    self.listado_departamento(datos);
                }
            }, path, parameter,undefined, false,false);
    }

    //guardar la lista de proyectos

    self.addProyectos=function(){

        if(self.id_proyecto()>0){
            var sel = document.forms['frmactividad'].elements['proyecto'];
            var nombre = sel.options[sel.selectedIndex].text;
            sw=0;
            ko.utils.arrayForEach(self.tareaVO.listado_proyectos(), function(d) {

                if(d.id==self.id_proyecto()){
                   sw=1;
                }
            });            

            if(sw==0){
                 self.tareaVO.listado_proyectos.push({
                        id:self.id_proyecto(),
                        nombre:nombre
                     });
            }   
        }
                 
      };


    self.deleteProyectos=function(value){
        self.tareaVO.listado_proyectos.remove(value);
    }



    self.guardar=function(){

         if (IndexViewModel.errores_tarea().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            self.tareaVO.usuario_responsable_id($("#id_usuario").val());
            lista_id='';

            ko.utils.arrayForEach(self.tareaVO.listado_proyectos(), function(d) {

                if(lista_id==''){
                   lista_id=d.id;
                }else{
                    lista_id=lista_id+','+d.id;
                }
            });  

            var data = new FormData();
            data.append('usuario_responsable_id',self.tareaVO.usuario_responsable_id());
            data.append('asunto',self.tareaVO.asunto());
            data.append('descripcion',self.tareaVO.descripcion());
            data.append('fecha_fin',self.tareaVO.fecha_fin());
            data.append('colaborador_actual_id',self.tareaVO.colaborador_actual_id());
            data.append('numero',self.tareaVO.numero());
            data.append('tipo_tarea_id',self.tareaVO.tipo_tarea_id());
            data.append('comentario',self.tareaVO.comentario());
            data.append('lista_proyecto',lista_id);

            ko.utils.arrayForEach(self.tareaVO.listado_archivo(), function(d) {

                    if(d.soporte()!=''){
                         data.append('soporte[]',d.soporte());
                    }
             }); 

            if(self.tareaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            //self.consultar(self.paginacion.pagina_actual());
                            location.reload();
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        } 
                                               
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Tarea/',//url api
                     parametros:data                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData2(parametros);
           }else{

                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          $('#modal_edicion').modal('hide');
                          self.limpiar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Tarea/'+self.tareaVO.id()+'/',
                       parametros:data                            
                  };

                  RequestFormData2(parametros);

            }

        } else {
             IndexViewModel.errores_tarea.showAllMessages();//mostramos las validacion
        }

    }


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_administrador_tarea",self.filtro() || '');
            
            path = path_principal+'/api/Tarea/?format=json&page='+pagina;
            parameter = { dato: self.filtro(), pagina: pagina,estado_id:lista_id_estado,fecha_inicio:self.filterVO.desde(),
                fecha_final:self.filterVO.hasta()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data.datos!=null && datos.data.datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data.datos));
                    self.porcentaje_total(datos.data.porcentaje);
                     $('#modal_acciones').modal('hide');
                     $('#modal_filter').modal('hide');

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


    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.limpiar();
            self.consultar(1);
        }
        return true;
    }
   

 }

var index = new IndexViewModel();

$('#txtBuscar').val(sessionStorage.getItem("filtro_administrador_tarea"));

index.consultar(1);//iniciamos la primera funcion
index.consultar_estado();
index.consultar_macrocontrato();
IndexViewModel.errores_tarea = ko.validation.group(index.tareaVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);