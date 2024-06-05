function ConsecutivoViewModel() {

	var self = this;
	self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');

    self.url=path_principal+'/api/';
    self.url_funcion=path_principal+'/actareunion/'; 

    self.consecutivoVO ={
        id:ko.observable(0),
        ano:ko.observable('').extend({ required: { message: '(*)Digite el año' } }),
        consecutivo:ko.observable('').extend({ required: { message: '(*)Digite el consecutivo' } }),
        empresa_id:ko.observable($('#empresa_id').val()).extend({ required: { message: '(*)No se selecciono la empresa' } }),
    };

    self.limpiar = function(){
        self.consecutivoVO.id(0)
        self.consecutivoVO.ano('');
        self.consecutivoVO.consecutivo('');
        self.consecutivoVO.empresa_id($('#empresa_id').val());

        self.consecutivoVO.id.isModified(false);
        self.consecutivoVO.ano.isModified(false);
         self.consecutivoVO.consecutivo.isModified(false);
    }

    self.abrir_modal = function(){
        self.titulo('Registrar consecutivo');
        self.limpiar();
        $('#modal_acciones').modal('show');
    }

    self.consultar = function(){
        path = path_principal + '/api/actareunion-consecutivo/?format=json';
        parameter = {
            empresa_id:self.consecutivoVO.empresa_id(),
            ignorePagination:true,           
            lite:1,
        };
        RequestGet(function(datos,estado,mensaje) {      
            if(estado=='ok' && datos!=null && datos.length>0){                
                self.listado(datos);
                self.mensaje('');
            }else{
                self.mensaje(mensajeNoFound);
                self.listado([]);
            }            
            cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.consultar_por_id = function(obj){
        path = path_principal + '/api/actareunion-consecutivo/'+obj.id+'/?format=json';
        parameter = {            
            ignorePagination:true,           
            lite:1,
        };
        RequestGet(function(datos,mensaje,estado) {
            //alert(estado);
            if(datos!=null){                              
                self.consecutivoVO.id(datos.id);
                self.consecutivoVO.ano(datos.ano);
                self.consecutivoVO.consecutivo(datos.consecutivo);
                self.consecutivoVO.empresa_id(datos.empresa.id);
                 self.titulo('Editar consecutivo');
                $('#modal_acciones').modal('show');

            }else{                
                mensajeError(mensaje);
            }            
            cerrarLoading();
        }, path, parameter,undefined,false);
    }

    self.eliminar_por_id = function(obj){
        var path =path_principal+'/api/actareunion-consecutivo/'+obj.id+'/';
        var parameter = {metodo:'DELETE'};
        RequestAnularOEliminar("Esta seguro que desea eliminar el consecutivo?", path, parameter, 
            function(datos, estado, mensaje){
                if (estado=='ok') { 
                    self.consultar();
                    //mensajeExitoso(mensaje);
                }
        
            });
    }

    self.guardar = function(){
        if (ConsecutivoViewModel.errores_consecutivo().length == 0 ) {
            if(self.consecutivoVO.id()==0){
                //alert('ALGO');
                var parametros={
                    metodo:'POST',
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            mensajeExitoso(mensaje);
                            self.consultar();
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }else{
                             mensajeError(mensaje);
                        }
                        cerrarLoading();
                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/actareunion-consecutivo/',//url api
                    parametros:self.consecutivoVO,
                    alerta:false                       
                };
                RequestFormData(parametros);

            }else{
                var parametros={
                    metodo:'PUT',
                    callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.consultar();
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }else{
                             mensajeError(mensaje);
                        }
                        cerrarLoading();
                    }, //funcion para recibir la respuesta 
                    url:path_principal+'/api/actareunion-consecutivo/'+self.consecutivoVO.id()+'/',//url api
                    parametros:self.consecutivoVO                  
                };
                RequestFormData(parametros);
            }

        } else {            
            ConsecutivoViewModel.errores_consecutivo.showAllMessages();            
        }
    }
}

var consecutivo = new ConsecutivoViewModel();
consecutivo.consultar();

ConsecutivoViewModel.errores_consecutivo = ko.validation.group(consecutivo.consecutivoVO);
ko.applyBindings(consecutivo);