function ViewModel(argument) {

    var self=this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.url=path_principal+'/api/bitacora/'; 
    self.listado_usuarios = ko.observableArray([]);    
    var resultadosPorPagina = 20;

    /*parametros de busqueda*/
    self.filtros={      
      usuario_id: ko.observable(''),//.extend({ required: { message: '(*)Seleccione el usuario' } }),
      proyecto_id:ko.observable($('#hdProyecto').val()),
      fecha_inicio:ko.observable(''),
      fecha_final:ko.observable(''),
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

    self.modelVO={
         id:ko.observable(0),     
         comentario:ko.observable('').extend({ required: { message: '(*)Ingrese el comentario' } }),
         proyecto_id:ko.observable($('#hdProyecto').val()),
         usuario_id:ko.observable($('#hdUsuario').val())
    }
  
  
    self.llenar_paginacion = function (data,pagina) {        
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);
    }

    self.exportar_excel=function(){      
      
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Poliza');
        $('#modal_acciones').modal('show');
    }

    self.abrir_filtros=function(){
      if($('#hdBuscarUsuario').val()=='true'){
          self.obtener_usuarios();
      }
      $('#modal_filtros').modal('show');
    }

    self.limpiar=function(){

         self.modelVO.id(0);
         self.modelVO.comentario('');
         self.modelVO.proyecto_id($('#hdProyecto').val());
         self.modelVO.usuario_id($('#hdUsuario').val());

         self.modelVO.comentario.isModified(false);
         
    }

    self.limpiar_filtros=function(){
        
    }

    self.consultar = function (pagina) {
        if (pagina > 0) {
            //self.buscado_rapido(true);
            self.filtro($('#txtBuscar').val());
            path =self.url + '?format=json&page='+pagina;
            parameter = { dato: self.filtro(), proyecto_id: self.filtros.proyecto_id(),
                        usuario_id:self.filtros.usuario_id(), fecha_inicio: self.filtros.fecha_inicio(),
                        fecha_final: self.filtros.fecha_final()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    
                    self.mensaje('');
                    
                    ko.utils.arrayForEach(datos.data, function(d) {
                       self.listado.push(d); 
                    });                     
                    
                    $('#modal_filtros').modal('hide');
                    
                    self.llenar_paginacion(datos,pagina);

                    var cantidad_de_paginas = (Math.ceil(parseFloat(self.paginacion.total()) / resultadosPorPagina));
                    if(cantidad_de_paginas == self.paginacion.pagina_actual()){
                      $('#vermas').text('No hay mas anotaciones para mostrar');          
                    }

                } else {
                    self.listado([]);
                    self.mensaje(mensageNoFound('¡No se encontraron anotaciones en la bitácora!'));//mensaje not found se encuentra el el archivo call-back.js
                }

                //self.llenar_paginacion(datos,pagina);
                
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
    	   
        ViewModel.errores.showAllMessages(); 
        
        if (ViewModel.errores().length==0) {
            
        	var parametros={           
              callback:function(datos, estado, mensaje){
                 if (estado=='ok') {  
                    $('#modal_acciones').modal('hide'); 
                    self.listado([]);             
                    self.consultar(1);                         
                 }
              },//funcion para recibir la respuesta 
              url:self.url,
              parametros:self.modelVO,
              completado:function(){
                cerrarLoading();
              },
              alerta:false
          };
                 
          Request(parametros);
          
        } else {
            ViewModel.errores.showAllMessages();//mostramos las validacion
        }

    }

    self.eliminar=function(item){
        
      if (item.minutos<=10) {

        RequestAnularOEliminar('¿Desea eliminar el registro?', 
          self.url+item.id+'/', {}, 
          function(datos, estado, mensage){
             if (estado=='ok') {                                       
                self.listado.remove(item);
                if (self.listado()==null || self.listado().length==0) {
                  self.listado([]);
                }
             }
        }, function(){

            cerrarLoading();
        
        }, false); 

      }

    }

    self.verMas = function () {
      
      var cantidad_de_paginas = (Math.ceil(parseFloat(self.paginacion.total()) / resultadosPorPagina));
      if (cantidad_de_paginas > self.paginacion.pagina_actual()) {
         var pagina = self.paginacion.pagina_actual()+1;
         self.paginacion.pagina_actual(pagina);
      }

      if(cantidad_de_paginas == self.paginacion.pagina_actual()){
        $('#vermas').text('No hay mas anotaciones para mostrar');          
      }

    }

    self.obtener_usuarios = function () {
        
        path =path_principal+'/bitacora/obtener_usuario/'+self.filtros.proyecto_id()+'/';
        parameter = { };
        RequestGet(function (datos, estado, mensage) {
          if (estado == 'ok' && datos!=null && datos.length > 0) {                  
              self.listado_usuarios(datos);                 
          }
        }, path, parameter, function(){
          cerrarLoading();
        });
       
    }

    self.consultar_por_filtros=function(){

      if (ViewModel.errores_filtros.length==0) {
        self.listado([]);
        self.consultar(1);
      }else {
        ViewModel.errores_filtros.showAllMessages();//mostramos las validacion
      }

    }
   

}

var viewModel = new ViewModel();
viewModel.consultar(1);
ViewModel.errores=ko.validation.group(viewModel.modelVO);
ViewModel.errores_filtros=ko.validation.group(viewModel.filtros);
ko.applyBindings(viewModel);