function ViewModel() {

  var self=this;
  self.listado=ko.observableArray([]);
  self.mensaje=ko.observable('');
  self.titulo=ko.observable('');
  self.filtro=ko.observable('');
  self.url=path_principal+'/api/solicitudServicioSolicitud/'; 
  self.seleccionar_todos=ko.observable(false);  

  
  self.modelVO={
      id : ko.observable(0),      
      descripcion : ko.observable('').extend({ required: { message: '(*)Ingrese la descricpión' } }),
      //fechaAutorizacionArea: ko.observable(''),
      area_id : ko.observable('').extend({ required: { message: '(*)Seleccione el área' } }),
      //autoriza_id: ko.observable('').extend({ required: { message: '(*)Seleccione quién autoriza' } }),
      contrato_id: ko.observable('').extend({ required: { message: '(*)Selecione el contrato' } }),      
      tipo_id: ko.observable('').extend({ required: { message: '(*)Seleccione el tipo' } }),
      //tramitador_id: ko.observable('').extend({ required: { message: '(*)Seleccione el tramitador' } }),
      estado_id: ko.observable(''),
      solicitante_id : ko.observable('')
  };

  self.detalleVO={ 
    contrato: ko.observable(''),
    tipo: ko.observable(''),
    area: ko.observable(''),
    //fecha_autorizacion: ko.observable(''),
    descripcion: ko.observable(''),
    solicitante: ko.observable(''),
    //autoriza: ko.observable(''),
    //tramitador: ko.observable(''),
    estado: ko.observable(''),
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
        },
        totalRegistrosBuscados:ko.observable(0)
    } 

    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    self.consultar=function(pagina) {
    
        self.filtro($('#txtBuscar').val());
        path =self.url + '?format=json&page='+pagina;
        parameter = { dato: self.filtro()};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                
              self.mensaje('');              
              self.listado(agregarOpcionesObservable(datos.data));

            } else {
                self.listado([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js

            }

            self.llenar_paginacion(datos, pagina);
                
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

      if (ViewModel.errores().length==0) {
          if (self.modelVO.id()==0) {
            var parametros={           
                    callback:function(datos, estado, mensaje){
                       if (estado=='ok') {  
                          $('#modal_acciones').modal('hide');              
                          self.consultar(1);                         
                       }
                    },//funcion para recibir la respuesta 
                    url:self.url,
                    parametros:self.modelVO,
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
                    url:self.url+ self.modelVO.id() + '/',
                    parametros:self.modelVO,
                    completado:function(){
                      cerrarLoading();
                    }
              };
                     
              Request(parametros);
          }
      } else {
          ViewModel.errores.showAllMessages();//mostramos las validacion          
      }     
    }  


     self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =self.url+obj.id+'/?format=json';
       RequestGet(function (datos, estado, mensage) {
         
          self.limpiar();
          self.titulo('Actualizar Solicitud');
          
          self.modelVO.id(datos.id);
          self.modelVO.descripcion(datos.descripcion);
          //self.modelVO.fechaAutorizacionArea(datos.fechaAutorizacionArea);
          self.modelVO.area_id (datos.area.id.toString());
          //self.modelVO.autoriza_id(datos.autoriza.id.toString());
          self.modelVO.contrato_id(datos.contrato.id.toString());
          self.modelVO.tipo_id(datos.tipo.id.toString());
          //self.modelVO.tramitador_id(datos.tramitador.id.toString());
          self.modelVO.solicitante_id(datos.solicitante.id);
          self.modelVO.estado_id(datos.estado.id);
          
          $('#modal_acciones').modal('show');
        }, path, {}, function(){
          cerrarLoading();
        });

    }

     self.ver_detalle = function (obj) {
       
      // alert(obj.id)
       path =self.url+obj.id+'/?format=json';
       RequestGet(function (datos, estado, mensage) {
                   
          self.detalleVO.contrato(datos.contrato.nombre);
          self.detalleVO.tipo(datos.tipo.nombre);
          self.detalleVO.area(datos.area.nombre);
          //self.detalleVO.fecha_autorizacion(datos.fecha_autorizacion);
          self.detalleVO.descripcion(datos.descripcion);
          self.detalleVO.solicitante(datos.solicitante.persona.nombres + ' ' + datos.solicitante.persona.apellidos);
          //self.detalleVO.autoriza(datos.autoriza.persona.nombres + ' ' + datos.autoriza.persona.apellidos);
          //self.detalleVO.tramitador(datos.tramitador.persona.nombres + ' ' + datos.tramitador.persona.apellidos);
          self.detalleVO.estado(datos.estado.nombre);
                   
          $('#modal_detalle').modal('show');
        }, path, {}, function(){
          cerrarLoading();
        });

    }
   

    self.limpiar=function () {

      self.modelVO.id(0);      
      self.modelVO.descripcion('');
      //self.modelVO.fechaAutorizacionArea('');
      self.modelVO.area_id ('');
      //self.modelVO.autoriza_id('');
      self.modelVO.contrato_id('');
      self.modelVO.tipo_id('');
      //self.modelVO.tramitador_id('');
      self.modelVO.solicitante_id('');
      self.modelVO.estado_id('');

      self.modelVO.descripcion.isModified(false);      
      self.modelVO.area_id .isModified(false);
      //self.modelVO.autoriza_id.isModified(false);
      self.modelVO.contrato_id.isModified(false);
      self.modelVO.tipo_id.isModified(false);
      //self.modelVO.tramitador_id.isModified(false);
                
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Crear solicitud de servicio');
        $('#modal_acciones').modal('show');
    }

    self.eliminar=function(id){

        var lista=[];
        ko.utils.arrayForEach(self.listado(), function(p){          
          if (p.procesar()) {
            lista.push(p.id);
          }
        });
        
        RequestAnularOEliminar('¿Desea eliminar el(los) registro(s) seleccionado(s)?', 
          path_principal+'/solicitud-servicio/eliminar_solicitudes/', {lista:lista}, 
          function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultar(self.paginacion.pagina_actual());                  
             }
        }, function(){
            cerrarLoading();              
        }, true); 

    }
   
    self.exportar_excel=function(){}

    self.seleccionar_todos.subscribe(function(val){
      ko.utils.arrayForEach(self.listado(), function(p){          
         p.procesar(val);
      });
    });
    
    
}

var _viewModel = new ViewModel();
ViewModel.errores=ko.validation.group(_viewModel.modelVO);
_viewModel.consultar(1);
ko.applyBindings(_viewModel);