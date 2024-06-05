
function CargaMasivaViewModel() {
    
    var self = this;
    self.listado_conflictos=ko.observableArray([]);
    self.listado_contratista=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.fecha=ko.observable('');
    self.checkSistema=ko.observable(false);
    self.checkrecibido=ko.observable(false);
    self.valida_tabla=ko.observable('');
    self.obj=ko.observable(null);

    self.referencia=ko.observable('');
    self.referencia2=ko.observable('');
    self.valor=ko.observable('');
    self.valor2=ko.observable('');
    self.validacion=ko.observable('');
    self.id_factura=ko.observable('');
    self.descripcion_conflicto=ko.observable('');
    self.facturas_no_encontradas=ko.observable('');
    self.contratista_id=ko.observable('');
    self.fecha_reporte_sist=ko.observable('');
    self.fecha_reporte_archi=ko.observable('');


    //funcion para seleccionar los datos del registro del sistema
    self.checkSistema.subscribe(function(value){

        ko.utils.arrayForEach(self.listado_conflictos(), function(d) {

            d.eliminado(value);
        });

        if(value)
            self.checkrecibido(!value); 
    });


    //funcion para seleccionar los datos del archivo
    self.checkrecibido.subscribe(function(value){

        ko.utils.arrayForEach(self.listado_conflictos(), function(d) {

            d.procesar(value);
        });

        if(value)
            self.checkSistema(!value); 

    });


    self.chequear_checkbox=function (obj) {
        obj.procesar(false);      
        return true;
    }

    self.chequear_checkbox2=function (obj) {        
        obj.eliminado(false);   
        return true;      
    }

        //limpiar el modelo de la categoria
     self.limpiar=function(){    

        self.fecha('');
        self.contratista_id(0); 

        //$('#archivo').fileinput('reset');
        $('#archivo').val('');
      
     }

    //funcion para leer el archivo en excel
    // self.leer_excel=function(){

    //      var data = new FormData();
    //      data.append('contratista',$('#contratista_filtro').val());
    //      data.append('fecha_reporte',self.fecha());
    //      data.append('archivo', $('#archivo')[0].files[0]);

    //     var parametros={                     
    //         callback:function(datos, estado, mensaje){

    //             if (datos.numero_fa!='' && datos.numero_fa!=null) {

    //                 $("#mensajeFactura_no").html('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning fa-2x"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button> No se encontraron las siguientes facturas con los numeros '+datos.numero_fa +'  revise el codigo acreedor en el archivo excel o el contratista seleccionado.</div>');
       
    //             }else{
    //                 $("#mensajeFactura_no").html('');
    //             }

    //             console.log(datos)
    //             self.facturas_no_encontradas(datos.numero_fa); 
    //             self.listado_conflictos(agregarOpcionesObservable(datos.lista_errores));
    //             self.valida_tabla(datos.valida_tabla); 
    //             //self.limpiar();                       
                        
    //         },//funcion para recibir la respuesta 
    //         url:path_principal+'/seguimiento_factura/leer_excel/',//url api
    //         parametros:data                        
    //     };
    //     //parameter =ko.toJSON(self.contratistaVO);
    //     RequestFormData2(parametros);
    // }

    self.leer_excel=function(){

         var data = new FormData();
         data.append('contratista',$('#contratista_filtro').val());
         data.append('fecha_reporte',self.fecha());
         data.append('archivo', $('#archivo')[0].files[0]);

        var parametros={                     
            callback:function(datos, estado, mensaje){

                // if (datos.numero_fa!='' && datos.numero_fa!=null) {

                //     $("#mensajeFactura_no").html('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning fa-2x"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button> No se encontraron las siguientes facturas con los numeros '+datos.numero_fa +'  revise el codigo acreedor en el archivo excel o el contratista seleccionado.</div>');
       
                // }else{
                //     $("#mensajeFactura_no").html('');
                // }

                // console.log(datos)
                // self.facturas_no_encontradas(datos.numero_fa); 
                // self.listado_conflictos(agregarOpcionesObservable(datos.lista_errores));
                // self.valida_tabla(datos.valida_tabla); 
                self.limpiar();

                                       
                        
            },//funcion para recibir la respuesta 
            url:path_principal+'/seguimiento_factura/leer_excel/',//url api
            parametros:data                        
        };
        //parameter =ko.toJSON(self.contratistaVO);
        RequestFormData2(parametros);
    }

     //eliminar los movimientos
    self.actualizar_excel = function () {

         var data=[];
         var conteo=0;
      
        ko.utils.arrayForEach(self.listado_conflictos(),function(p) {

            if(self.valida_tabla()==true && p.mostrar==true){
                
                if (p.eliminado() || p.procesar()) {
                    //alert(p.id_factura)
                    data.push(p);

                }
                
            }else if(p.mostrar==false){

                data.push(p);
                conteo++;
            }

            //console.log(data);
            
        });

        // if(self.fecha()==''){

        //     $.confirm({
        //         title:'Informativo',
        //         content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione la fecha de reporte.<h4>',
        //         cancelButton: 'Cerrar',
        //         confirmButton: false
        //     });
        //     return false
        // }

        if(conteo>0 && self.valida_tabla()==true && data.length==0){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione la funcion a realizar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
            return false
        }

        var path =path_principal+'/seguimiento_factura/actualizar_excel/';
        var parameter = { lista: data, fecha_reporte:self.fecha() };
        RequestAnularOEliminar("Esta seguro que desea guardar los cambios seleccionados?", path, parameter, function () {
            //self.leer_excel();

            self.facturas_no_encontradas(''); 
            self.listado_conflictos([]);
            self.valida_tabla('');
            self.limpiar(); 

            self.checkSistema(false);
            self.checkrecibido(false);
        })

  
    }


    //abrir modal para ver el detalle
    self.modalDetalle=function(obj) {

        self.referencia(obj.referencia);
        self.referencia2(obj.referencia2);
        self.valor(obj.valor_pagado);
        self.valor2(obj.valor_pagado2);
        self.validacion(obj.validacion);
        self.id_factura(obj.id_factura);
        self.descripcion_conflicto(obj.descripcion);

        self.fecha_reporte_sist(obj.fecha_reporte_sist);
        self.fecha_reporte_archi(obj.fecha_reporte_archi);

        $('#modalDetalle').modal('show');
    }


    //Actualizar conflicto
    self.actualizar_conflicto = function (validacion) {

        $.confirm({
        title: 'Confirmar!',
        content: "<h4>Esta seguro que desea guardar la opcion seleccionada?</h4>",
        confirmButton: 'Si',
        confirmButtonClass: 'btn-info',
        cancelButtonClass: 'btn-danger',
        cancelButton: 'No',
        confirm: function() {

            var parametros = {
                callback: function(datos, estado, mensaje){
                    self.leer_excel();
                },
                url: path_principal+'/seguimiento_factura/actualizar_conflicto/',
                parametros: { id_factura:self.id_factura(), validacion:validacion, referencia:self.referencia(), referencia2:self.referencia2(), valor:self.valor(), valor2:self.valor2(), fecha_reporte:self.fecha(), orden_pago:1 }             
            };

            Request(parametros);
        }
    });
  
    }

            //consultar los nombre de los contratista segun el macrocontrato 
    self.consultar_contratista=function(){

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={};
         RequestGet(function (datos, estado, mensaje) {
          
            self.listado_contratista(datos.contratista);
           
         }, path, parameter);
         
    }

}

var carga_masiva = new CargaMasivaViewModel();
ko.applyBindings(carga_masiva);
