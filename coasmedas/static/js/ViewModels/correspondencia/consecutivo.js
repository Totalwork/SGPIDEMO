function ConsecutivoViewModel() {

	var self=this;
	self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.url=path_principal+'/api/CorrespondenciaConsecutivo/'; 
    self.consecutivos = ko.observableArray([]);
    self.radicados = ko.observableArray([]);
    self.mensaje_radicado=ko.observable('');
    self.mensaje_consecutivo=ko.observable('');
    self.tipo = ko.observable('1');

    self.consecutivoVO={
    	  id: ko.observable(0),
        ano: ko.observable('').extend({ required: { message: '(*)Ingrese la cedula' } }),
        numero: ko.observable('').extend({ required: { message: '(*)Ingrese el numero' } }),
        // tipo_id: ko.observable('').extend({ required: { message: '(*)Seleccione el tipo' } }),
        prefijo_id: ko.observable('').extend({ required: { message: '(*)Seleccione el prefijo' } }),
        // empresa_id: $('#empresa_id').val()
    };

    self.radicadoVO={
        id: ko.observable(0),
        ano: ko.observable('').extend({ required: { message: '(*)Ingrese la cedula' } }),
        numero: ko.observable('').extend({ required: { message: '(*)Ingrese el numero' } }),        
        empresa_id: $('#empresa_id').val()
    };

	self.consultar_radicados=function() {
		
		self.filtro($('#txtBuscar').val());
        path = path_principal + '/api/CorrespondenciaRadicado/?ignorePagination=&format=json';
        parameter = { empresa:$('#empresa_id').val(), tipo:0};
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    
                    self.radicados(datos); 
                    self.mensaje_radicado('');    

                } else {
                    self.radicados([]);
                    self.mensaje_radicado(mensajeNoFound);                        
                }

                //self.llenar_paginacion(datos,pagina);
                
            	}, path, parameter, function(){
                    cerrarLoading();
        });		
	}

  self.consultar_consecutivos=function() {
    
    self.filtro($('#txtBuscar').val());
        path =self.url + '?ignorePagination=&format=json';
        parameter = { empresa:$('#empresa_id').val(), tipo:1};
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    
                    self.consecutivos(datos);                   
                    self.mensaje_consecutivo('');

                } else {
                    self.consecutivos([]);
                    self.mensaje_consecutivo(mensajeNoFound);
                }

                //self.llenar_paginacion(datos,pagina);
                
              }, path, parameter, function(){
                    cerrarLoading();
        });   

  }

	self.guardar_radicado=function(){
    	
        if (ConsecutivoViewModel.errores_radicado().length==0) {
            if (self.consecutivoVO.id()==0) {
            	var parametros={           
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {  
                            $('#modal_acciones').modal('hide');
                            self.consultar_radicados();
                         }
                      },//funcion para recibir la respuesta 
                      url:path_principal+'/api/CorrespondenciaRadicado/',
                      parametros:self.radicadoVO,
                      completado:function(){
                        cerrarLoading();
                      }
                };
                       
                Request(parametros);
            }else{
                var parametros={   
                      metodo:'PUT',                
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {     
                            $('#modal_acciones').modal('hide');                                                           
                            self.consultar_radicados();
                         }
                      },//funcion para recibir la respuesta 
                      url:path_principal+'/api/CorrespondenciaRadicado/'+ self.radicadoVO.id() + '/',
                      parametros:self.radicadoVO,
                      completado:function(){
                        cerrarLoading();
                      }
                };
                       
                Request(parametros);
            }
        } else {
            ConsecutivoViewModel.errores_radicado.showAllMessages();//mostramos las validacion
        }

    }

    self.guardar=function(){
      
        if (ConsecutivoViewModel.errores().length==0) {
            if (self.consecutivoVO.id()==0) {
              var parametros={           
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {  
                            $('#modal_acciones').modal('hide');              
                            self.consultar_consecutivos();
                         }
                      },//funcion para recibir la respuesta 
                      url:self.url,
                      parametros:self.consecutivoVO,
                      completado:function(){
                        cerrarLoading();
                      }
                };
                       
                Request(parametros);
            }else{
                var parametros={   
                      metodo:'PUT',                
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {     
                            $('#modal_acciones').modal('hide');            
                            self.consultar_consecutivos();  
                         }
                      },//funcion para recibir la respuesta 
                      url:self.url+ self.consecutivoVO.id() + '/',
                      parametros:self.consecutivoVO,
                      completado:function(){
                        cerrarLoading();
                      }
                };
                       
                Request(parametros);
            }
        } else {
            ConsecutivoViewModel.errores.showAllMessages();//mostramos las validacion
        }

    }

    self.consultar_radicado_por_id = function (item) {
       
      // alert(obj.id)
       path = path_principal+'/api/CorrespondenciaRadicado/'+item.id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
            self.limpiar();
            self.titulo('Actualizar radicado');
            self.tipo(1);
            self.radicadoVO.id(datos.id);
            self.radicadoVO.ano(datos.ano);
            self.radicadoVO.numero(datos.numero);
            
            $('#modal_acciones').modal('show');
         }, path, {}, function(){
            cerrarLoading();
        });

    }

     self.consultar_por_id = function (item) {
       
      // alert(obj.id)
       path =self.url+item.id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
            self.limpiar();
            self.titulo('Actualizar consecutivo');
            self.tipo(2);
            self.consecutivoVO.id(datos.id);
            self.consecutivoVO.ano(datos.ano);
            self.consecutivoVO.numero(datos.numero);
            self.consecutivoVO.prefijo_id(datos.prefijo.id);         
            
            $('#modal_acciones').modal('show');
         }, path, {}, function(){
            cerrarLoading();
       	});

    }

    self.limpiar=function () {


      self.consecutivoVO.id(0);
      self.consecutivoVO.ano('');
      self.consecutivoVO.numero('');
      self.consecutivoVO.prefijo_id('');

      self.consecutivoVO.id.isModified(false);
      self.consecutivoVO.ano.isModified(false);
      self.consecutivoVO.numero.isModified(false);
      self.consecutivoVO.prefijo_id.isModified(false);

      self.radicadoVO.id(0);
      self.radicadoVO.ano('');
      self.radicadoVO.numero('');
      
      self.radicadoVO.id.isModified(false);
      self.radicadoVO.ano.isModified(false);
      self.radicadoVO.numero.isModified(false);      

    }

	self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar ' + (self.tipo==1 ? 'Radicado' : 'Consecutivo'));
        $('#modal_acciones').modal('show');
  }

    self.eliminar=function(id){

        // RequestAnularOEliminar('¿Desea eliminar el registro seleccionado?', 
        //   path_principal+'/correspondencia/eliminar_o_deshabilitar_prefijo/'+id+'/', {},
        //   function(datos, estado, mensage){
        //      if (estado=='ok') {                     
        //           self.consultar();                   
        //      }
        // }, function(){

        //    cerrarLoading();
           
        // }, false); 
    }

}

var consecutivo = new ConsecutivoViewModel();
ConsecutivoViewModel.errores=ko.validation.group(consecutivo.consecutivoVO);
ConsecutivoViewModel.errores_radicado=ko.validation.group(consecutivo.radicadoVO);
consecutivo.consultar_radicados();
consecutivo.consultar_consecutivos();
ko.applyBindings(consecutivo);