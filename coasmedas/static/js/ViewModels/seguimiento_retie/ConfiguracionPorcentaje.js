function ConfiguracionPorcentajeViewModel() {
	var self=this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');    
    self.url=path_principal+'/api/ConfiguracionPorcentajes/'; 
    self.filtro=ko.observable('');
    self.seleccionar=ko.observable(false);
    
    self.filtros={
    	contrato_id:ko.observable('')
    }

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
        },
        totalRegistrosBuscados:ko.observable(0)
    }

    self.configuracionVO={
		    id:ko.observable(0),
		    porcentaje:ko.observable('').extend({min:{params:1, message:'El porcentaje debe ser mayor a 0'}, max:{params:100, message:'El porcentaje debe ser menor a 100'} ,required: { message: '(*)Ingrese el porcentaje' } }),
		    contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contrato a configurar' } }),
		    comentario:ko.observable('')		
 	};
    
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);
    }

    self.exportar_excel=function(){      
      location.href=path_principal+"/retie/exportar-configuracion-porcentajes/?dato="+self.filtro()+"&contrato_id="+self.filtros.contrato_id();     
    }

     self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Configuración');
        $('#modal_acciones').modal('show');
    }

    self.abrir_filtros = function () {      
        $('#modal_filtros').modal('show');
    }

     self.limpiar=function(){
      self.configuracionVO.id(0);
      self.configuracionVO.porcentaje('');
      self.configuracionVO.contrato_id('');
      self.configuracionVO.comentario('');

      self.configuracionVO.porcentaje.isModified(false);
      self.configuracionVO.contrato_id.isModified(false);
      
    }

    self.consultar = function (pagina) {
        if (pagina > 0) {
            //self.buscado_rapido(true);
            self.filtro($('#txtBuscar').val());
            path =self.url + '?format=json&page='+pagina;
            parameter = { dato: self.filtro(), contrato_id:self.filtros.contrato_id()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    
                    self.mensaje('');
                    //self.listado(results);  
                    self.listado(agregarOpcionesObservable(datos.data));  
                                       
                   
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                $('#modal_filtros').modal('hide');
                self.llenar_paginacion(datos,pagina);
                
            }, path, parameter, function(){
                    cerrarLoading();
                   });
        }
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }


    self.paginacion.pagina_actual.subscribe(function (pagina) {       
       self.consultar(pagina);
    });


     self.guardar=function(){    	  
       
        if (ConfiguracionPorcentajeViewModel.errores().length==0) {
           
            if (self.configuracionVO.id()==0) {
            	var parametros={           
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {  
                            $('#modal_acciones').modal('hide');              
                            self.consultar(1);                         
                         }
                      },//funcion para recibir la respuesta 
                      url:self.url,
                      parametros:self.configuracionVO,
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
                      url:self.url+ self.configuracionVO.id() + '/',
                      parametros:self.configuracionVO,
                      completado:function(){
                        cerrarLoading();
                      }
                };
                       
                Request(parametros);
            }
          
        } else {
            ConfiguracionPorcentajeViewModel.errores.showAllMessages();//mostramos las validacion
        }
    }


    self.eliminar_un_registro=function(id){
               
        RequestAnularOEliminar('¿Desea eliminar el registro seleccionado?', 
          self.url + id+'/', 
          function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultar(self.paginacion.pagina_actual());                  
             }
        }, function(){           
            cerrarLoading();                   
        }, false); 	
    }

    self.eliminar=function(){
         var lista=[];
        ko.utils.arrayForEach(self.listado(), function(p){          
          if (p.procesar()) {
            lista.push(p.id);
          }
        });
        
        RequestAnularOEliminar('¿Desea eliminar el(los) registro(s) seleccionado(s)?', 
          path_principal+'/retie/eliminar_configuracion_porcentajes/', {lista:lista}, 
          function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultar(self.paginacion.pagina_actual());                  
             }
        }, function(){ 
            cerrarLoading();            
        }, false); 	
    }


    self.consultar_por_id = function (id) {
       
      // alert(obj.id)
       path =self.url+id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
            self.limpiar();
            self.titulo('Actualizar Configuración');
            
            self.configuracionVO.id(datos.id);
      			self.configuracionVO.porcentaje(datos.porcentaje);
      			self.configuracionVO.contrato_id(datos.contrato.id);
      			self.configuracionVO.comentario(datos.comentario);
            
            $('#modal_acciones').modal('show');

         }, path, {}, function(){
          cerrarLoading();
         });

    }

    self.seleccionar.subscribe(function(val){
    	ko.utils.arrayForEach(self.listado(),function(p){
    		p.procesar(val);
    	});
    });

}

var configuracion = new ConfiguracionPorcentajeViewModel();
ConfiguracionPorcentajeViewModel.errores=ko.validation.group(configuracion.configuracionVO);
configuracion.consultar(1);
ko.applyBindings(configuracion);