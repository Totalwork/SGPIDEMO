function PrefijoViewModel() {

	var self=this;
	self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.url=path_principal+'/api/CorrespondenciaPrefijo/'; 

    self.prefijoVO={
    	id: ko.observable(0),
        nombre: ko.observable('').extend({ required: { message: '(*)Ingrese el prefijo' } }),
        empresa_id: $('#empresa_id').val()
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

    self.paginacion.pagina_actual.subscribe(function (pagina) {    
       self.consultar(pagina);
    });

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

	self.consultar=function(pagina) {
		
		self.filtro($('#txtBuscar').val());
        path =self.url + '?format=json';
        parameter = { empresa:$('#empresa_id').val(), dato: self.filtro() , page: pagina };
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    
                    self.mensaje('');
                    //self.listado(results);  
                    self.listado(agregarOpcionesObservable(datos.data));  

                    if (datos.length>0) {
                        $('#modal_filtros').modal('hide');
                    }

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

          self.llenar_paginacion(datos,pagina);
          cerrarLoading();
      }, path, parameter,undefined,false);		

	}

  self.consulta_enter = function(d, e) {
        if (e.which == 13) {
            self.consultar();
        }
        return true;
    }

	self.guardar=function(){
    	
        if (PrefijoViewModel.errores().length==0) {
            if (self.prefijoVO.id()==0) {
            	var parametros={           
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {  
                            $('#modal_acciones').modal('hide');              
                            self.consultar();                         
                         }
                      },//funcion para recibir la respuesta 
                      url:self.url,
                      parametros:self.prefijoVO,
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
                            self.consultar();
                         }
                      },//funcion para recibir la respuesta 
                      url:self.url+ self.prefijoVO.id() + '/',
                      parametros:self.prefijoVO,
                      completado:function(){
                        cerrarLoading();
                      }
                };
                       
                Request(parametros);
            }
        } else {
            PrefijoViewModel.errores.showAllMessages();//mostramos las validacion
        }

    }

     self.consultar_por_id = function (id) {
       
      // alert(obj.id)
       path =self.url+id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
            self.limpiar();
            self.titulo('Actualizar Prefijo');
            
            self.prefijoVO.id(datos.id);
            self.prefijoVO.nombre(datos.nombre);           
            
            $('#modal_acciones').modal('show');
         }, path, {}, function(){
            cerrarLoading();
       	});

    }

    self.limpiar=function () {
    	self.prefijoVO.id(0);
    	self.prefijoVO.nombre('');
    	self.prefijoVO.nombre.isModified(false);       	  
    }

	self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Prefijo');
        $('#modal_acciones').modal('show');
    }

    self.eliminar=function(id){

        RequestAnularOEliminar('¿Desea eliminar el registro seleccionado?', 
          path_principal+'/correspondencia/eliminar_o_deshabilitar_prefijo/'+id+'/', {},
          function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultar();                   
             }
        }, function(){

           cerrarLoading();
           
        }, false); 
    }

}

var prefijo = new PrefijoViewModel();
PrefijoViewModel.errores=ko.validation.group(prefijo.prefijoVO);
prefijo.consultar(1);
ko.applyBindings(prefijo);