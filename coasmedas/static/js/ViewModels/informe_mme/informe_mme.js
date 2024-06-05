
function InformeMMeViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.desde_filtro=ko.observable('');
    self.hasta_filtro=ko.observable('');
    self.lista_contrato=ko.observableArray([]);
    self.fecha_informe=ko.observable('');
    self.mcontrato_informe=ko.observable('');
    self.soporte=ko.observable('');

     //Representa el modelo de informe_mme
    self.informe_mmeVO={
        id:ko.observable(0),
        contrato_id:ko.observable(''),
        empresa_id:ko.observable(''),
        fecha:ko.observable(''),
        consecutivo:ko.observable(''),
        soporte:ko.observable(''),

     };

     //paginacion de informe_mme
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
        self.paginacion.cantidad_por_paginas(resultadosPorPagina)
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

  
    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });

    //funcion para filtrar los informe
    self.filtrar_informe = function () {
        self.titulo('Filtrar informe');
        $('#modal_filtro_informe').modal('show');
    }


    //funcion para exportar a excel los informe
    self.exportar_excel_modal = function () {

        self.limpiar(); 
        self.titulo('Generar informe');
        $('#modal_informe').modal('show');
    }


    //consultar los macrocontrato
    self.consultar_macrocontrato=function(){
        
         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_contrato(datos.macrocontrato);

         }, path, parameter,undefined,false,false);
    }



     //limpiar el modelo del informe
     self.limpiar=function(){     
         
        self.mcontrato_informe(0); 
        self.fecha_informe('');
      
     }


    //funcion consultar los informe
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            
            self.filtro($('#txtBuscar').val());
            var desde=$("#desde_filtro").val();
            var hasta=$("#hasta_filtro").val();
            var contrato_id=$("#mcontrato_filtro").val();

            path = path_principal+'/api/Informemme?format=json';
            parameter = { dato: self.filtro(), page: pagina,contrato_id:contrato_id, desde:desde, hasta:hasta};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    $('#modal_filtro_informe').modal('hide'); 
                    self.listado(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)
                    cerrarLoading();

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter,undefined, false);
        }
    }


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    //exportar excel
   self.exportar_excel_informe=function(){

        var fecha=$("#fecha_informe").val();
        var contrato_id=$("#mcontrato_exportar").val();

        if(contrato_id==0){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione el macrocontrato.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false;
        }

        if(fecha==0){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione la fecha.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false;
        }


       $.confirm({
            title: 'Confirmar!',
            content: "<h4>Desea genera este informe con consecutivo?</h4>",
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {

                //path = path_principal+'http://localhost:51149/exportar/informe-ministerio-MME/?mcontrato_id="+contrato_id';


                path = 'http://caribemar.sinin.co:8080/exportar/informe-ministerio-MME/?mcontrato_id='+contrato_id+"&validacion=2";
                //path = "http://localhost:51149/exportar/informe-ministerio-MME/?mcontrato_id="+contrato_id+"&validacion=2";
                parameter = {};
                RequestGet(function (datos, estado, mensage) {

                    console.log(datos.file);

                    var data = new FormData();

                    data.append('fecha',fecha);
                    data.append('contrato_id',contrato_id);
                    data.append('nombre_soporte',datos.file);

                    var parametros={                     
                         callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                            console.log(datos.file);
                                self.consultar(1);
                                $('#modal_informe').modal('hide'); 
                               
                            }                     
                         },//funcion para recibir la respuesta 
                         url:path_principal+'/api/Informemme/',//url api
                         parametros: data                         
                    };
                    RequestFormData2(parametros); 


                }, path, parameter);
      
            },
            cancel:function(){
                location.href="http://caribemar.sinin.co:8080/exportar/informe-ministerio-MME/?mcontrato_id="+contrato_id+"&validacion=1";
                //location.href="http://localhost:51149/exportar/informe-ministerio-MME/?mcontrato_id="+contrato_id+"&validacion=1";
            }
        });    
     } 





   
}

var informe_MMe = new InformeMMeViewModel();
InformeMMeViewModel.errores_informe = ko.validation.group(informe_MMe.informe_mmeVO);
ko.applyBindings(informe_MMe);
