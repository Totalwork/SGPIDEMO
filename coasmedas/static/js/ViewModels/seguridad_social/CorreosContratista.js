function CorreoContratistaViewModel() {

	var self=this;
	self.listado=ko.observableArray([]);
  self.mensaje=ko.observable('');
  self.titulo=ko.observable('');
  self.filtro=ko.observable('');
  self.url=path_principal+'/api/CorreoContratista/'; 
  self.contratista_id = ko.observable('');

    self.correo_contratistaVO={
    	id: ko.observable(0),
      correo: ko.observable('').extend({ required: { message: '(*)Ingrese el correo' } }).extend({ email: { message: '(*)Ingrese un correo valido' } }), 
      contratista_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contratista' } })
    };

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
        }
    } 

 self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

	self.consultar=function(pagina, contratista) {
		
		    self.filtro($('#txtBuscar').val());
        path =self.url + '?format=json&page='+pagina;
        parameter = { empresa:$('#empresa_id').val(), dato: self.filtro(), contratista_id: contratista > 0 ? contratista : ''};
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    
                    self.mensaje('');
                    //self.listado(results);  
                    self.listado(datos.data);  

                    if (datos.data.length>0) {
                        $('#modal_filtros').modal('hide');
                    }

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                
            	}, path, parameter, function(){
                    cerrarLoading();
        });		

	}

  self.consulta_enter = function(d, e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }

	self.guardar=function(){
    	
        if (CorreoContratistaViewModel.errores().length==0) {
            if (self.correo_contratistaVO.id()==0) {
            	var parametros={           
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {  
                            $('#modal_acciones').modal('hide');              
                            self.consultar(self.paginacion.pagina_actual(), self.contratista_id());                         
                         }
                      },//funcion para recibir la respuesta 
                      url:self.url,
                      parametros:self.correo_contratistaVO,
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
                            self.consultar(1);
                         }
                      },//funcion para recibir la respuesta 
                      url:self.url+ self.correo_contratistaVO.id() + '/',
                      parametros:self.correo_contratistaVO,
                      completado:function(){
                        cerrarLoading();
                      }
                };
                       
                Request(parametros);
            }
        } else {
            CorreoContratistaViewModel.errores.showAllMessages();//mostramos las validacion
        }

    }

     self.consultar_por_id = function (id) {
       
      // alert(obj.id)
       path =self.url+id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
            self.limpiar();
            self.titulo('Actualizar Correo');
            
            self.correo_contratistaVO.id(datos.id);
            self.correo_contratistaVO.correo(datos.correo);  
            self.correo_contratistaVO.contratista_id(datos.contratista.id);           
            
            $('#modal_acciones').modal('show');
         }, path, {}, function(){
            cerrarLoading();
       	});

    }

    self.limpiar=function () {

    	self.correo_contratistaVO.id(0);
    	self.correo_contratistaVO.correo('');
      self.correo_contratistaVO.contratista_id('');

    	self.correo_contratistaVO.correo.isModified(false);  
      self.correo_contratistaVO.contratista_id.isModified(false);  
      	  
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Correo');
        $('#modal_acciones').modal('show');
    }

    self.eliminar=function(id){

        RequestAnularOEliminar('¿Desea eliminar el registro seleccionado?', self.url+id + '/', {},
        function(datos, estado, mensage){
            if (estado=='ok') {                     
                self.consultar(1);                   
            }
        }, function(){
           cerrarLoading();           
        }, false); 
    }

    self.consultar_por_contratista=function() {
       self.consultar(1, self.contratista_id());
    }

    self.abrir_filtros=function () {
        $('#modal_filtros').modal('show');
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {       
      self.consultar(pagina);           
    });

}

var correo_contratista = new CorreoContratistaViewModel();
CorreoContratistaViewModel.errores=ko.validation.group(correo_contratista.correo_contratistaVO);
correo_contratista.consultar(1);
ko.applyBindings(correo_contratista);