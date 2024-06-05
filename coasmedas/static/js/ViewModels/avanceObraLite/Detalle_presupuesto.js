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
   self.cerrado_presupuesto=ko.observable($('#cerrado').val());


   self.listado_actividades=ko.observableArray([]);

    self.sin_poste=ko.observable(false);


    self.busquedaVO={
        hito_id:ko.observable(''),
        actividad_id:ko.observable('')
     };


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


    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Carga Masiva de Presupuesto');
        $('#modal_acciones').modal('show');
    }


    self.abrir_modal_filter = function () {
        self.limpiar();
        self.titulo('Filtro');
        $('#modal_filtro').modal('show');
    }


     self.limpiar=function(){   
           
         
     }



     self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });



     self.busquedaVO.hito_id.subscribe(function(value ){

             if(value!=0){
                path = path_principal+'/api/avanceObraLiteEsquemaCapitulosActividades/?sin_paginacion';
                parameter = {padre_id:value};
                RequestGet(function (datos, estado, mensage) {

                    self.listado_actividades(datos);
                }, path, parameter,function(){
                    // self.disenoVO.municipio_id(0);
                    // self.disenoVO.municipio_id(self.municipio());
                }
                );
            }else{
                self.listado_actividades([]);
                self.busquedaVO.actividad_id('')
            }
    });


    self.filtrar=function(){

       self.consultar(1);
        $('#modal_filtro').modal('hide');
    }



    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;

            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("filtro_avance_detalle",self.filtro() || '');


            self.cargar(pagina);

        }


    }


    self.cargar =function(pagina){           


            let filtro_avance_detalle=sessionStorage.getItem("filtro_avance_detalle");

            path = path_principal+'/api/avanceObraLiteDetallePresupuesto/?format=json&page='+pagina;
            parameter = {pagina:pagina,dato: filtro_avance_detalle,presupuesto_id:$('#id_presupuesto').val(),
            hito_id:self.busquedaVO.hito_id(),actividad_id:self.busquedaVO.actividad_id(),lite2:1};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(self.llenar_datos(datos.data)));
                    //self.cargar_total_presupuesto(datos);
                     $('#modal_acciones').modal('hide');

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                if($('#sin_poste').val()=='False'){
                    self.sin_poste(false);
                }else{
                    self.sin_poste(true);
                }
                self.llenar_paginacion(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
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




    self.guardar=function(){

         if ((self.archivo_carga()=='') || ($('#cmbCatalogo').val()==0)){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un archivo y el catalogo de UUCC para cargar el presupuesto.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

        }else{
            var data= new FormData();
            data.append('presupuesto_id',$('#id_presupuesto').val());
            data.append('archivo',self.archivo_carga());
            data.append('catalogoUnidadConstructiva_id', $('#cmbCatalogo').val())
            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar(1);
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraLite/guardar_presupuesto_archivo/',//url api
                     parametros:data                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
            RequestFormData2(parametros);
        }
   
    }

    self.guardar_cantidad=function(){
        

         var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraLite/actualizar_cantidad/',//url api
                     parametros:{ lista: self.listado_cantidad() }                         
                  };
                RequestFormData(parametros);

    }

    self.listado_cantidad=function(){
        var lista=[];
        ko.utils.arrayForEach(self.listado(), function(obj) {
            if(obj.cantidad()==''){
                obj.cantidad(0);
            }
            lista.push({
                id:obj.id(),
                cantidad:obj.cantidad()
            });
        });

        return lista;
    }


    self.guardar_presupuesto=function(){
        var lista=[];
        var sw=0;
        var mensaje="";

        ko.utils.arrayForEach(self.listado(), function(obj) {
                
                if(obj.codigoUC()=='' || obj.codigoUC() == null){
                    sw=1
                }
        });

        if(sw==1){
            mensaje="¿Esta seguro que desea guardar el presupuesto con codigo UUCC vacio?, no podra ser modificado";
        }else{
            mensaje="¿Esta seguro que desea guardar el presupuesto?, no podra ser modificado";
        }




        $.confirm({
        title: 'Confirmar!',
        content: "<h4>"+mensaje+"</h4>",
        confirmButton: 'Si',
        confirmButtonClass: 'btn-info',
        cancelButtonClass: 'btn-danger',
        cancelButton: 'No',
        confirm: function() {

            
        var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.cerrado_presupuesto(true);
                            self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraLite/cierre_presupuesto/',//url api
                     parametros:{ lista: self.listado_cantidad(),id_presupuesto:$('#id_presupuesto').val() }                         
                  };
                Request(parametros);
        }
    });

}

    self.llenar_datos=function(data){
        self.valor_total(0);
         var lista=[];
         sw=true;
         //alert(self.cerrado_presupuesto())
         if(self.cerrado_presupuesto()==true || self.cerrado_presupuesto()=='True'){
            sw=false;
         }
         
          ko.utils.arrayForEach(data, function(obj) {
                    color='';
                    if(obj.codigoUC=='' || obj.codigoUC == null){
                        color='#E18989'
                    }
                    // valor2=parseInt(obj.valorMaterial)+parseInt(obj.valorManoObra);
                    // if (isNaN(valor2)){
                    //     valor2=0;
                    // }
                    valor=parseFloat(obj.cantidad)*parseFloat(obj.valorGlobal);

                    // if (isNaN(valor)){
                    //     valor=0;
                    // }

                    lista.push({
                        id:ko.observable(obj.id),
                        nombre_padre:ko.observable(obj.nombre_padre),
                        actividad_nombre:ko.observable(obj.actividad.nombre),
                        codigoUC:ko.observable(obj.codigoUC),
                        descripcionUC:ko.observable(obj.descripcionUC),
                        valorUC:ko.observable(obj.valorGlobal),
                        cantidad:ko.observable(obj.cantidad),
                        subtotal:ko.observable(valor),
                        color:ko.observable(color),
                        habilitar:ko.observable(sw)
                    });
                    self.valor_total(parseFloat(obj.sumaPresupuesto));
             });
        return lista;
    }


    self.descargar_plantilla=function(){

             location.href=path_principal+"/avanceObraLite/descargar_plantilla_presupuesto?id_esquema="+$('#id_esquema').val();

    }


    self.exportar_excel=function(){

         location.href=path_principal+"/avanceObraLite/informe_detallepresupuesto?presupuesto_id="+$('#id_presupuesto').val();   

    }

   

    self.habilitar_sin_poste=function(){

        $.confirm({
            title: 'Confirmar!',
            content: "<h4>Esta seguro que desea marcar el presupuesto sin Poste a Poste?</h4>",
            confirmButton: 'Si',
            confirmButtonClass: 'btn-info',
            cancelButtonClass: 'btn-danger',
            cancelButton: 'No',
            confirm: function() {

                var parametros={     
                metodo:'POST',                
                callback:function(datos, estado, mensaje){

                        self.sin_poste(true);
                        self.consultar(1);
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avanceObraLite/reportar_sin_poste/',//url api
                     parametros:{presupuesto_id:$('#id_presupuesto').val() }                         
                  };
                RequestFormData(parametros);
            }
        });
    }

 }



var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_avance_detalle"));
index.cargar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

