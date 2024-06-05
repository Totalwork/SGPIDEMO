
function PropietarioViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]); 
    self.listado_asociado=ko.observableArray([]);    
    self.mensaje=ko.observable('');
    self.mensaje_asociado=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.filtro2=ko.observable('');
    self.checkall=ko.observable(false);
    self.checkall2=ko.observable(false);



     //Representa el modelo de propietario
    self.propietarioVO={
        id:ko.observable(0),
        cedula:ko.observable('').extend({ required: { message: '(*)Digite la cedula del propietario' } }),
        nombres:ko.observable('').extend({ required: { message: '(*)Digite el nombre del propietario' } }),
        apellidos:ko.observable('').extend({ required: { message: '(*)Digite el apellido del propietario' } }),
        correo:ko.observable(''),
        telefono:ko.observable(''),

     };


    //Representa el modelo de propietario lote
    self.propietario_loteVO={
        id:ko.observable(0),
        propietario_id:ko.observable(0),
        lote_id:ko.observable(0),

     };


    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });


    //funcion para seleccionar los datos a eliminar propietarios
    self.checkall2.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado_asociado(), function(d) {

            d.eliminado(value);
        }); 
    });


    //funcion para abrir modal de propietario
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Propietario');
        $('#modal_acciones').modal('show');
    }

     //limpiar el modelo del propietario 
     self.limpiar=function(){     
         
        self.propietarioVO.id(0);
        self.propietarioVO.cedula('');
        self.propietarioVO.nombres('');
        self.propietarioVO.apellidos('');
        self.propietarioVO.correo('');
        self.propietarioVO.telefono('');
   
     }


    //limpiar el modelo del propietario lote
     self.limpiar_propietario_lote=function(){     
         
        self.propietario_loteVO.id(0);
        self.propietario_loteVO.propietario_id(0);
   
     }


    //funcion guardar y actualizar los propietarios
     self.guardar=function(){

        if (PropietarioViewModel.errores_propietario().length == 0) {//se activa las validaciones

            if(self.propietarioVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.limpiar();
                            self.consultar();
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Propietario/',//url api
                     parametros:self.propietarioVO                        
                };
                Request(parametros);
            }else{              

                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.limpiar();
                          self.consultar();
                          $('#modal_acciones').modal('hide');
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Propietario/'+self.propietarioVO.id()+'/',
                       parametros:self.propietarioVO                        
                  };

                  Request(parametros);

            }

        } else {
             PropietarioViewModel.errores_propietario.showAllMessages();//mostramos las validacion
        }
     }


    //funcion consultar los propietario
    self.consultar = function () {
        
        self.filtro($('#txtBuscarE').val());

        path = path_principal+'/p_p_construccion/listado_propietario?format=json';
        parameter = { dato: self.filtro()};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos!=null && datos.length > 0) {
                self.mensaje('');
                self.listado(agregarOpcionesObservable(datos));
                cerrarLoading();  

            } else {
                self.listado([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
            }

        }, path, parameter,undefined, false);
    }


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    //consultar por id de los propietarios
    self.consultar_por_id = function (obj) {
       
       path =path_principal+'/api/Propietario/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar Propietario');

            self.propietarioVO.id(datos.id);
            self.propietarioVO.cedula(datos.cedula);
            self.propietarioVO.nombres(datos.nombres);
            self.propietarioVO.apellidos(datos.apellidos);
            self.propietarioVO.coreo(datos.coreo);
            self.propietarioVO.telefono(datos.telefono);
             
             $('#modal_acciones').modal('show');

         }, path, parameter);

     }

    self.eliminar = function () { }


    //asociar propietarios
    self.asociar_propietarios = function () {
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los propietarios a asociar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/p_p_construccion/asociar_propietario_lote/';
             var parameter = { lista: lista_id, lote_id:self.propietario_loteVO.lote_id() };

              $.confirm({
                    title: 'Confirmar!',
                    content: "<h4>Esta seguro que desea asociar el lote a los propietarios seleccionados?</h4>",
                    confirmButton: 'Si',
                    confirmButtonClass: 'btn-info',
                    cancelButtonClass: 'btn-danger',
                    cancelButton: 'No',
                    confirm: function() {

                        var parametros = {
                            callback: function () {
                                         self.consultar(1);
                                         self.consultar_propietarios_asociados();
                                         self.checkall(false);
                                     },
                            url: path,
                            parametros: parameter,
                            completado: function(){},
                            metodo:'POST',
                            alerta:true

                        };
                        Request(parametros);
                    }
                });
            
         }     
         
    }


        //exportar excel la tabla lote
    self.exportar_excel=function(){}


        //funcion consultar los propietario asociados al lote
    self.consultar_propietarios_asociados = function () {
        
        self.filtro2($('#txtBuscarA').val());

        path = path_principal+'/api/PropietarioLote?format=json';
        parameter = { dato: self.filtro2(),lote_id:self.propietario_loteVO.lote_id()};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje_asociado('');
                self.listado_asociado(agregarOpcionesObservable(datos.data));
                cerrarLoading();  

            } else {
                self.listado_asociado([]);
                self.mensaje_asociado(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
            }

        }, path, parameter,undefined, false);
    }



    //desasociar propietarios
    self.desasociar_propietarios = function () {

         var lista_desasociar=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_asociado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_desasociar.push({
                        id:d.id
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los propietarios a desasociar.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/p_p_construccion/desasociar_propietario/';
             var parameter = { lista: lista_desasociar };
             RequestAnularOEliminar("Esta seguro que desea desasociar los propietarios seleccionados?", path, parameter, function () {
                 self.consultar_propietarios_asociados();
                 self.consultar(1);
                 self.checkall2(false);
             })

         }     
    
        
    }

}

var propietario = new PropietarioViewModel();
PropietarioViewModel.errores_propietario = ko.validation.group(propietario.propietarioVO);
ko.applyBindings(propietario);
