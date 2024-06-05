function CorreoDescargoViewModel() {

    var self = this;
    self.url=path_principal+'/api/';


    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.checkall=ko.observable(false);

    //LISTADOS   
    self.listado=ko.observableArray([]);
    //FILTROS
    self.filtro=ko.observable('');


     //Representa un modelo de la tabla cuenta
    self.CorreoDescargoVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*) Digite el nombre.' } }),
        apellido:ko.observable('').extend({ required: { message: '(*) Digite el apellido.' } }),
        correo:ko.observable('').extend({ required: { message: '(*) Digite un correo electronico.' } }),
        tipo_id:ko.observable(0),        
        contratista_id:ko.observable(0).extend({ required: { message: '(*) Seleccione un contratista.' } }),
     };

     self.paginacion = {
        pagina_actual: ko.observable(0),
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
    // //limpiar el modelo 
     self.limpiar=function(){       
        self.CorreoDescargoVO.id(0);
        self.CorreoDescargoVO.nombre('');
        self.CorreoDescargoVO.apellido('');
        self.CorreoDescargoVO.tipo_id(0);
        self.CorreoDescargoVO.contratista_id(0);
    

        $('#id_nombre').val('')
        $('#id_apellido').val('')
        $('#id_correo').val('')
        $('#id_tipo').removeAttr('selected')
        $('#id_contratista').val('')
     }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar correo');
        $('#modal_acciones').modal('show');
    }
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }
    //FUNCION PARA INABIHILITAR LA CUENTA
    self.eliminar = function () {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un Correo para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/descargo/eliminar_id/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los Correos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }    
    }  

     //funcion guardar
     self.guardar=function(){

        self.CorreoDescargoVO.nombre($('#id_nombre').val());
        self.CorreoDescargoVO.apellido($('#id_apellido').val());
        self.CorreoDescargoVO.correo($('#id_correo').val());
        self.CorreoDescargoVO.tipo_id($('#id_tipo').val());
        self.CorreoDescargoVO.contratista_id($('#id_contratista').val());


        if (CorreoDescargoViewModel.errores_cuenta().length == 0) {//se activa las validaciones
            if(self.CorreoDescargoVO.id()==0){
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: self.url+'Correo_descargo/',//url api
                     parametros : self.CorreoDescargoVO                        
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
                       url: self.url+'Correo_descargo/'+ self.CorreoDescargoVO.id()+'/',
                       parametros : self.CorreoDescargoVO                        
                  };
                  RequestFormData(parametros);
            }
        } else {
             CorreoDescargoViewModel.errores_cuenta.showAllMessages();//mostramos las validacion
        }
     }
    //funcion consultar proyectos que ppuede  ver la empresa
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/Correo_descargo/?format=json&page='+pagina;
            parameter = { dato: self.filtro(), pagina: pagina };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data));  
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
            }, path, parameter);
            $('#loading').hide();
        }
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);

        }
        return true;
    }    
    //exportar excel    

    self.consultar_por_id = function (obj) {

       path =path_principal+'/api/Correo_descargo/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
            self.titulo('Actualizar Cuenta');
            self.CorreoDescargoVO.id(results.id);
            $('#id_nombre').val(results.nombre)
            $('#id_apellido').val(results.apellido)
            $('#id_correo').val(results.correo)
            $('#id_tipo').val(results.tipo.id)
            $('#id_contratista').val(results.contratista.id)
            self.CorreoDescargoVO.nombre(results.nombre);
            self.CorreoDescargoVO.apellido(results.apellido);
            self.CorreoDescargoVO.correo(results.correo);             
            self.CorreoDescargoVO.tipo_id(results.tipo.id);
            self.CorreoDescargoVO.contratista_id(results.contratista.id);
             $('#modal_acciones').modal('show');
         }, path, parameter);
     }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });        


}

var correoDescargo = new CorreoDescargoViewModel();
CorreoDescargoViewModel.errores_cuenta = ko.validation.group(correoDescargo.CorreoDescargoVO);
// cuenta.consultar_contratos();
// cuenta.consultar_tipos_cuenta();
// cuenta.consultar_tipos_movimientos();
correoDescargo.consultar(1);//iniciamos la primera funcion

ko.applyBindings(correoDescargo);