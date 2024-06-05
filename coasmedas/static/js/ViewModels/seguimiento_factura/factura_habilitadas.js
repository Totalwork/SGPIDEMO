
function FacturaHabilitadasViewModel() {
    
    var self = this;
    self.listado_factura_vencidas=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

    self.macontrato_filtro_select2=ko.observable(0);
    self.contratista_filtro_selects=ko.observable(0);
    self.lista_contrato=ko.observableArray([]);

    self.filtro_factura = {
        mcontrato:ko.observable(''),
        tipo:ko.observable(''),
        contratista_lista:ko.observableArray([]),
        contratista_nom:ko.observable(''),
        contratista:ko.observable(),
        numero_c:ko.observable(''),
        numero_f:ko.observable('')
    }


     //paginacion del movimiento de la cuenta
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
  
    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado_factura_vencidas(), function(d) {

            d.eliminado(value);
        }); 
    });

    //funcion para filtrar las facturas vencidas
    self.filtrar_facturas_vencidas_modal = function () {
        self.titulo('Filtrar facturas');
        //self.limpiar();
        self.consultar_macrocontrato();
        self.consultar_contratista_filtro();
        $('#modal_factura_vencida').modal('show');
    }

    //funcion para exportar a excel las facturas habilitadas para tes op
    self.exportar_excel = function (obj) {
        self.titulo('Generar informe');
        self.consultar_macrocontrato();
        $('#generar_informe').modal('show');
    }
    //consultar los macrocontrato para facturas vencidas
    self.consultar_macrocontrato=function(){

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_contrato(datos.macrocontrato);

         }, path, parameter,function(){
                 self.macontrato_filtro_select2(sessionStorage.getItem("mcontrato_filtro_seguimiento_habilitar"));       
             });

    }
    //funcion que se ejecuta cuando se cambia en el select de contrato para filtrar en la tabla factura vencida
    self.macontrato_filtro_select2.subscribe(function (value) {

        if(value >0){
            self.consultar_contratista_filtro(value);

        }else{
            self.filtro_factura.contratista_lista([]);
        }
    });
    //consultar los nombre de los contratista segun el tipo
    self.consultar_contratista_filtro=function(value){

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={mcontrato:value,tipo_contratista:'1'};
         RequestGet(function (datos, estado, mensaje) {
          
            self.filtro_factura.contratista_lista(datos.contratista);
           
         }, path, parameter,function(){
                self.contratista_filtro_selects(sessionStorage.getItem("contratista_filtro_seguimiento_habilitar"));      
            });
         
    }
    //funcion consultar 
    self.consultar = function (pagina) {
        //alert($('#mcontrato_filtro').val())
        if (pagina > 0) {            
            self.cargar(pagina);
        }
    }

    self.cargar = function(pagina){

        var empresa=$("#empresa").val();
        self.filtro($('#txtBuscar').val());
             path = path_principal+'/api/Factura?format=json';
            // = { dato: self.filtro(), page: pagina,orden_pago:1, bloqueo_factura:0, pagada:0, id_contrato:contrato_consultar, id_contratista:contratista_consultar,recursos_propios:0};
            parameter = { 
                page: pagina
                ,dato: self.filtro()
                ,id_mcontrato:self.filtro_factura.mcontrato()
                ,tipo_contrato:self.filtro_factura.tipo()
                ,id_contratista: self.filtro_factura.contratista()
                ,numero_contrato: self.filtro_factura.numero_c()
                ,numero: self.filtro_factura.numero_f()
                ,habilitadas_para_contabilizacion: true};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    $('#modal_factura_vencida').modal('hide'); 
                    self.listado_factura_vencidas(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)

                } else {
                    self.listado_factura_vencidas([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter);

    }

    //funcion consultar las facturas vencidas donde el campo orden_pago sea igual a 1
   /* self.consultar = function (pagina) {
        
        if (pagina > 0) { 

            self.filtro($('#txtBuscar').val());
            var contrato_consultar=$('#mcontrato_filtro').val()
            var contratista_consultar=$('#contratista_filtro').val()
            
            
            path = path_principal+'/api/Factura?format=json';
            // = { dato: self.filtro(), page: pagina,orden_pago:1, bloqueo_factura:0, pagada:0, id_contrato:contrato_consultar, id_contratista:contratista_consultar,recursos_propios:0};
            parameter = { dato: self.filtro(), page: pagina,orden_pago:1, bloqueo_factura:0, pagada:0, id_contrato:contrato_consultar, id_contratista:contratista_consultar};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    $('#modal_factura_vencida').modal('hide'); 
                    self.listado_factura_vencidas(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)

                } else {
                    self.listado_factura_vencidas([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter);
        }
    } */


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }

    //Actualiza el campo orden pago de las facturas
    self.desabilitar_factura_vencida = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_factura_vencidas(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione la factura a deshabilitar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/seguimiento_factura/deshabilitar-factura/';
             var parameter = { lista: lista_id, orden_pago:0 };
             RequestAnularOEliminar("Esta seguro que desea deshabilitar las facturas seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
        
    }

     //Actualiza el campo orden pago de las facturas
    self.habilitar_factura_vencida = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_factura_vencidas(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione la(s) factura(s) a habilitar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/seguimiento_factura/deshabilitar-factura/';
             var parameter = { lista: lista_id, orden_pago:1 };
             RequestAnularOEliminar("Esta seguro que desea habilitar las factura(s) seleccionada(s)?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
        
    }
    //exportar excel de las facturas habilitadas tes op
   self.exportar_excel_factura_habilitada=function(){

        var contrato= self.filtro_factura.mcontrato();
        var contratista= self.filtro_factura.contratista();

        location.href=path_principal+"/seguimiento_factura/exportar_factura_vencida/?id_contrato="+contrato+'&id_contratista='+contratista+'&bloqueo_factura=0'+'&pagada=0';
    } 
    // Buscar el contratista
    self.empresa=function(){
        // parameter={dato:$("#contratista_nom").val() };
        if(self.filtro_factura.contratista_nom() != ''){

            parameter={dato: self.filtro_factura.contratista_nom() };
            path =path_principal+'/api/empresa/?sin_paginacion&esContratista=1&format=json';

            RequestGet(function (results,count) {

                self.filtro_factura.contratista_lista(results);
            }, path, parameter, undefined, true);
        }
    }    


}

var seguimiento_factura = new FacturaHabilitadasViewModel();
//FacturaHabilitadasViewModel.errores_movimiento = ko.validation.group(seguimiento_factura.gestionOpVO);
ko.applyBindings(seguimiento_factura);
