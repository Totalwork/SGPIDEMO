
function TestOpViewModel() {
    
    var self = this;
    self.listado_contrato_factura=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);


    //Representa un modelo de la gestion_op
    self.test_opVO={
        id:ko.observable(0),
        valor:ko.observable(0),
        codigo:ko.observable('').extend({ required: { message: '(*)Digite el codigo de la test/op' } }),      
        fecha_registro:ko.observable(''),
        fecha_pago:ko.observable(''),   
        soporte:ko.observable(''),
        contrato_id:ko.observable(0),
        beneficiario_id:ko.observable(0),
        pagado_recursos_propios:ko.observable(0),
        lista_factura:ko.observableArray([]),

        
     };

    //funcion para filtrar las facturas vencidas
    self.filtrar_facturas_vencidas_modal = function () {
        self.titulo('Filtrar facturas');
        //self.limpiar();
        $('#modal_factura_vencida').modal('show');
    }

    //funcion para exportar a excel las facturas habilitadas para tes op
    self.exportar_excel = function (obj) {
        self.titulo('Generar informe');
        $('#generar_informe').modal('show');
    }

    //funcion consultar los contrato y contratista de las facturas segun la empresa
    self.consultar = function (validacion) {

        if(validacion==1){

            var orden_pago=1;
            var bloqueo_factura=0;
            var pagada=0;
            var recursos_propios=0

        }else{

            var orden_pago=1;
            var bloqueo_factura=0;
            var pagada=0;
            var recursos_propios=1
        }

        self.filtro($('#txtBuscar').val());
           
        path = path_principal+'/seguimiento_factura/lista_contrato?format=json';
        parameter = { dato: self.filtro(),orden_pago:orden_pago , bloqueo_factura:bloqueo_factura , pagada:pagada, recursos_propios:recursos_propios};
        RequestGet(function (datos, estado, mensage) {
            console.log(datos)

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensaje('');
                $('#modal_factura_vencida').modal('hide'); 
                self.listado_contrato_factura(agregarOpcionesObservable(datos));  
                //console.log(datos.data)

            } else {
                self.listado_contrato_factura([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }

        }, path, parameter);
    }
    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }
    //funcion guardar las test op
    self.guardar_gestion=function(item,validacion){

        if(validacion==1){

            self.test_opVO.codigo($("#codigo-"+item.id_contratista+'-'+item.contrato_id).val());
            self.test_opVO.valor(item.valor_total.suma_ingreso);
            self.test_opVO.beneficiario_id(item.id_contratista);
            self.test_opVO.lista_factura(ko.toJSON(item["listado_factura"]));
            self.test_opVO.contrato_id(item.contrato_id);
            self.test_opVO.pagado_recursos_propios(0);

            if(self.test_opVO.codigo()==''){

                  $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Digite el codigo de TEST/OP.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
                  return false
            }

        }else{

            self.test_opVO.codigo($("#codigo-"+item.id_contratista+'-'+item.contrato_id).val());
            self.test_opVO.valor(item.valor_total.suma_ingreso);
            self.test_opVO.beneficiario_id(item.id_contratista);
            self.test_opVO.lista_factura(ko.toJSON(item["listado_factura"]));
            self.test_opVO.soporte($('#archivo')[0].files[0]);
            self.test_opVO.contrato_id(item.contrato_id);
            self.test_opVO.pagado_recursos_propios(1);

            if(self.test_opVO.codigo()==''){

                  $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Digite el codigo de TEST/OP y seleccione el documente a cargar.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
                  return false
            }

        }


        var parametros={                     
            callback:function(datos, estado, mensaje){

                if (estado=='ok') {
                    //self.limpiar();
                    self.consultar(validacion);
                }                        
                        
            },//funcion para recibir la respuesta 
            url:path_principal+'/api/gestion_op/',//url api
            parametros:self.test_opVO                        
        };
        //parameter =ko.toJSON(self.contratistaVO);
        RequestFormData(parametros);
    }

    //Actualiza el campo orden pago de las facturas
    self.desabilitar_factura_vencida = function (obj) {
         var lista_id=[];
         // var count=0;
         // ko.utils.arrayForEach(self.listado_factura_vencidas(), function(d) {

         //        if(d.eliminado()==true){
         //            count=1;
         //           lista_id.push({
         //                id:d.id
         //           })
         //        }
         // });

         lista_id.push({id:obj.id_factura})

         // if(count==0){

         //      $.confirm({
         //        title:'Informativo',
         //        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione la factura a deshabilitar.<h4>',
         //        cancelButton: 'Cerrar',
         //        confirmButton: false
         //    });

         // }else{
             var path =path_principal+'/seguimiento_factura/deshabilitar-factura/';
             var parameter = { lista: lista_id, orden_pago:0 };
             RequestAnularOEliminar("Esta seguro que desea deshabilitar la factura numero :"+obj.numero+"?", path, parameter, function () {
                 self.consultar(1);
             })

         // }     
        
    }


}

var test_op = new TestOpViewModel();
TestOpViewModel.errores_test = ko.validation.group(test_op.test_opVO);
ko.applyBindings(test_op);
