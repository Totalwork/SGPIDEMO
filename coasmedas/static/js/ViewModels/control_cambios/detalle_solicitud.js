
function DetalleViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.listado_encabezado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.cambio_id=ko.observable('');
    self.proyecto_id=ko.observable('');
    self.filtro=ko.observable('');
    self.lista_soporte=ko.observableArray([]);
    self.listado_soporte=ko.observableArray([]);
    self.mensaje_listado_soportes=ko.observable('');
    self.motivo=ko.observable('');
    self.titulo=ko.observable('');
    self.checkall=ko.observable(false);
    self.comentario=ko.observable('');
    self.motivo=ko.observable('');
    self.listado_estado=ko.observableArray([]);
    self.estado_cambio=ko.observable('');

    //funcion para abri el mnodal de actualizar estado
    self.actualizar_estado = function () {
        self.titulo('Actualizar estado');
        self.consultar_estados();
        $('#modal_actualizar_estado').modal('show');
    }


    //funcion para abrir modal de ver soportes
    self.soporte_cambio = function (cambio_id,motivo) {

        self.motivo(motivo);
        self.consultar_soporte(cambio_id)
        self.titulo('Archivos del cambio');
        $('#soporte_cambio').modal('show');
    }

    
    //consultar los nombre de los estados
    self.consultar_estados=function(){

         path =path_principal+'/api/Estados/';
         parameter={ aplicacion:'EstadoControlCambio'};
         RequestGet(function (datos, estado, mensaje) {
          
            self.listado_estado(datos.data);
           
         }, path, parameter);
         
    }


    //funcion para seleccionar los datos a eliminar del detalle de solicitud
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.procesar(value);
        }); 
    });


     self.limpiar=function(){

        self.estado_cambio('');
        self.motivo('');
        self.comentario('');
     } 


    //funcion consultar el listado de detalle de solicitud
    self.consultar = function () {

        self.filtro($('#txtBuscar').val());

        path = path_principal+'/control_cambios/lista_detalle/?format=json';
        parameter = { dato:self.filtro(),proyecto_id:self.proyecto_id(),cambio_id:self.cambio_id()};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' ) {
                self.mensaje('');
                self.listado_encabezado(datos['encabezados']);
                self.listado(agregarOpcionesObservable(datos['lista']));
                self.lista_soporte(datos['soportes']);     
                cerrarLoading();

            } else {
                self.listado_encabezado([]);
                self.listado([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                cerrarLoading();
            }

        }, path, parameter,undefined, false);
    }


    //funcion consultar el listado de control de cambio
    self.consultar_soporte=function(cambio_id){

        path = path_principal+'/api/Soporte_cambio/?format=json';
        parameter={ cambio_id: cambio_id};
        RequestGet(function (datos, estado, mensaje) {

            if (datos.data!=null && datos.data.length > 0) {

                self.listado_soporte(datos.data);

            } else {
                self.listado_soporte([]);
                self.mensaje_listado_soportes(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }
            
        }, path, parameter);

    } 


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar();
        }
        return true;
    }


    //exportar excel la tabla del listado de las nuevas unidades constructivas
    self.exportar_excel=function(){
        self.filtro($('#txtBuscar').val());

        location.href=path_principal+"/control_cambios/exportar_reporte_detalle_solocitud/?dato="+self.filtro()+"&proyecto_id="+self.proyecto_id()+"&cambio_id="+self.cambio_id();
    }



    //actualizar estado
    self.actualizar_estado_cambio_proyecto = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.procesar()==true){
                    count=1;
                   lista_id.push({
                        id:d.id_uucc
                   })
                  
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione los cambios.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/control_cambios/actualizar_estado_cambio_proyecto/';
             var parameter = { lista: lista_id, cambio_id:self.cambio_id(), motivo:self.motivo(), comentario:self.comentario(), estado:self.estado_cambio()};
             RequestAnularOEliminar("Esta seguro que desea actualizar el estados de los cambios seleccionados?", path, parameter, function () {
                 self.consultar();
                 self.checkall(false);
                $('#modal_actualizar_estado').modal('hide');
                self.limpiar();

             })

         } 
    
        
    }
 


}

var detalle = new DetalleViewModel();
//AdministrarUUCCViewModel.errores_administrar= ko.validation.group(administrar_uucc.AdministrarUUCCVO);
ko.applyBindings(detalle);
