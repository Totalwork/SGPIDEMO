function PlanillaViewModel(argument) {
  var self=this;

  self.listado=ko.observableArray([]);
  self.mensaje=ko.observable('');
  self.titulo=ko.observable('');
  self.filtro=ko.observable('');
  self.checkall=ko.observable(false);
  self.listado_persona=ko.observableArray([]);
  self.listado_contratista=ko.observableArray([]);
  self.listado_meses=ko.observableArray([]);
  self.listado_planilla_empleado=ko.observableArray([]);
  self.filtro_persona=ko.observable('');
  self.nit=ko.observable('');
  self.nombre_contratista=ko.observable('');
  self.id_planilla=ko.observable(0);
  self.url=path_principal+'/api/Planilla/'; 
  self.mes=ko.observable('');
  self.planilla=ko.observable('');
  self.cargar_pago=ko.observable(false);
  self.listado_empleado=ko.observableArray([]);
  self.empleado_id=ko.observable(0);
  self.mensaje_empleado=ko.observable('');
  self.seleccionar=ko.observable(false);
  self.seleccionarEmpleados=ko.observable(false);

  self.planillaVO={
    id:ko.observable(0),
    contratista_id:ko.observable('').extend({ validation: {validator:validar, message: '(*)Seleccione el contratista' } }),
    ano:ko.observable('').extend({ required: { message: '(*)Digite el año de la planilla' } }),
    mes:ko.observable('').extend({ validation: {validator:validar, message: '(*)Seleccione el mes de la planilla' } }),
    fecha_pago:ko.observable('').extend({ validation: {validator:validar2, message: '(*)Seleccione la fecha del pago' } }),
    soporte:ko.observable('').extend({ validation: { validator: validar_soporte, message: '(*) Seleccione el soporte de la planilla.' } }),
    fecha_limite:ko.observable('').extend({ required: { message: '(*)Seleccione' } }),
    selectedContratista:ko.observable()//.extend({ validation: {validator:validar, message: '(*)Seleccione' } }),
  };
  
   function validar_soporte(val) {
       if (self.id_planilla()==0 || self.cargar_pago()==false) {
            return true;
       }else if(self.id_planilla()>0 && self.cargar_pago()==true && (self.planilla()=='' || self.planilla()==null) && (val=='' || val==null)){
            return false;
       }else if(self.id_planilla()>0 && self.cargar_pago()==true && ((self.planilla()!='' && self.planilla()!=null) || (val!='' && val!=null))) {
            return true;
       }
    }

    function validar(val) {
       if (self.id_planilla()>0 || self.cargar_pago()==true) {
            return true;
       }else if(self.id_planilla()==0 && self.cargar_pago()==false && (val=='' || val==null)){
            return false;
       }else if(self.id_planilla()==0 && self.cargar_pago()==false && val!='' && val!=null){
            return true;
       }
    }

    function validar2(val) {
       if (self.id_planilla()==0 || self.cargar_pago()==false) {
            return true;
       }else if(self.id_planilla()>0 && self.cargar_pago()==true && (val=='' || val==null)){
            return false;
       }else if(self.id_planilla()>0 && self.cargar_pago()==true && val!='' && val!=null){
            return true;
       }
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

    self.filtros={
      contratista_id:ko.observable(''),//.extend({ required: { message: '(*) Seleccione el contratista' } }),
      ano:ko.observable(new Date().getFullYear())//.extend({ required: { message: '(*) Ingrese el año' } })      
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.cargar_pago(false);
        self.titulo('Registrar Planilla');
        $('#modal_acciones').modal('show');
    }

    self.abrir_filtros=function(){
      $('#modal_filtros').modal('show');
    }
   
    self.abrir_image_planilla=function(){
      $('#img_planilla').show();
    }

    self.abrir_buscar_empleado=function(){

      self.consultar_empleados('');
      $('#modal_buscar_empleado').modal('show');

    }

    self.cerrar_image_planilla=function(){
      $('#img_planilla').hide();
    }

     //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(20);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    //exportar excel    
    self.exportar_excel=function(){
        location.href=path_principal+"/seguridad-social/exportar-planilla?contratista_id="+self.filtros.contratista_id()+"&ano="+self.filtros.ano();    
      }

    // //limpiar el modelo 
     self.limpiar=function(){      
        
      self.planillaVO.id(0);
      self.planillaVO.contratista_id('');
      self.planillaVO.ano('');
      self.planillaVO.mes('');
      self.planillaVO.fecha_pago('');
      self.planillaVO.soporte('');
      self.planillaVO.fecha_limite('');
      self.id_planilla(0);

      $('#soporte').fileinput('reset');
      $('#soporte').val('');

      self.planillaVO.contratista_id.isModified(false);
      self.planillaVO.ano.isModified(false);
      self.planillaVO.mes.isModified(false);
      self.planillaVO.fecha_pago.isModified(false);
      self.planillaVO.soporte.isModified(false);
      self.planillaVO.fecha_limite.isModified(false);
          
     }

      self.guardar=function(opcion){
        
             if (self.planillaVO.id()>0) {
                self.planillaVO.mes(self.mes());

                 //console.log(PlanillaViewModel.errores_planilla());
                if (PlanillaViewModel.errores_planilla().length == 0) {
                    var parametros={  
                        metodo:'PUT',                  
                         callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                               self.filtro("");
                               if(opcion=='pago'){
                                  window.location.href = '../planilla-empleado/'+ self.planillaVO.id() + '/' + self.planillaVO.contratista_id()
                               }
                               self.consultar(self.paginacion.pagina_actual());
                               $('#modal_acciones').modal('hide');
                               $('#modal_acciones_actualizar').modal('hide');
                               self.limpiar();
                            }                        
                            
                         },//funcion para recibir la respuesta 
                         url:self.url+self.planillaVO.id()+'/',
                         parametros:self.planillaVO ,
                         completado:function(){
                            cerrarLoading();
                          }                     
                   };
                          
                   RequestFormData(parametros);
               }
               else{
                  PlanillaViewModel.errores_planilla.showAllMessages();
               }

           }else{
              
              if (PlanillaViewModel.errores_planilla().length == 0) {

                  var parametros={                                        
                   callback:function(datos, estado, mensaje){
                      if (estado=='ok') {
                         self.filtro("");
                         self.consultar(self.paginacion.pagina_actual());
                         $('#modal_acciones').modal('hide');                         
                         self.limpiar();
                      }                        
                      
                   },//funcion para recibir la respuesta 
                   url:self.url,
                   parametros:self.planillaVO,
                   completado:function(){
                    cerrarLoading();
                   }                       
             };
                        
             RequestFormData(parametros);

             }
               else{
                  PlanillaViewModel.errores_planilla.showAllMessages();
               }

           }
         
      }

       self.guardar_planilla_empleado=function(notificar){

             var lista=[]; 
             ko.utils.arrayForEach(self.listado_planilla_empleado(), function (p) {
                //if (p.tiene_pago()) {
                  lista.push({id:p.id(),tiene_pago:p.tiene_pago()});
                //}
             });
             var parametros={                     
                   callback:function(datos, estado, mensaje){
                      if (estado=='ok') {
                        self.consultar_planilla_empleado();
                      }                        
                      
                   },//funcion para recibir la respuesta 
                   url:path_principal+'/seguridad-social/guardar_panilla_empleado/',
                   parametros:{lista:lista,planilla_id:$('#hd_planilla').val(), notificar: notificar},
                    completado:function(){
                    cerrarLoading();
                   }
             };
                        
             Request(parametros);
       }
       
      
      self.consultar = function (pagina) {
        if (pagina > 0) {            
            
            path =self.url + '?format=json&page='+pagina;
            parameter = { contratista_id: self.filtros.contratista_id(),ano:self.filtros.ano()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                  
                    self.mensaje('');
                    //self.listado(results);  
                    self.listado(agregarOpcionesObservable(datos.data)); 
                    
                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                cerrarLoading();
            }, path, parameter, undefined, false);
        }
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
       self.consultar(pagina);    
    });


     self.consultar_contratista = function () {                            
      path =path_principal + '/seguridad-social/consultar_contratistas/';
      parameter = { };
      RequestGet(function (datos, estado, mensage) {

          if (estado == 'ok' && datos!=null && datos.length > 0) {
             
              self.listado_contratista(datos);  

          } else {
              self.listado_contratista([]);                    
          }                
      }, path, parameter, function(){
                    cerrarLoading();
                   });       
    }

     self.consultar_por_filtros=function(pagina){
      if (PlanillaViewModel.errores_filtros().length==0) {                         
            self.consultar(1);   
            $('#modal_filtros').modal('hide');      
      }else{
        PlanillaViewModel.errores_filtros.showAllMessages();
      }
      
    }

    self.consulta_enter = function (d,e) {
      if (PlanillaViewModel.errores_filtros().length==0) {  
        if (e.which == 13) {
            self.filtros.ano($('#ano').val());
            self.consultar(1);
            $('#modal_filtros').modal('hide'); 
            return false;
        }
        }else{
          PlanillaViewModel.errores_filtros.showAllMessages();
        }
        return true;
    }

    self.consultar_por_id = function (obj) {
     
       path =self.url+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
         self.limpiar();  
         self.titulo('Actualizar Planilla');
         
         self.id_planilla(datos.id);   
         self.planillaVO.id(datos.id);
         self.planillaVO.contratista_id(datos.contratista.id);         
         self.planillaVO.ano(datos.ano);
         self.planillaVO.mes(datos.mes);
         self.mes(datos.mes);
         self.nit(datos.contratista.nit);
         self.planillaVO.fecha_pago(datos.fecha_pago);
         //self.planillaVO.soporte('');
         self.planillaVO.fecha_limite(datos.fecha_limite);
         //self.planillaVO.selectedContratista(datos.contratista);
         self.planilla(datos.soporte);
         self.nombre_contratista(datos.contratista.nombre);
         $('#modal_acciones').modal('show');
         self.cargar_pago(false);

         }, path, parameter, function(){
                    cerrarLoading();
                   });

     }

      self.abrir_cargar_pago = function (obj) {
        
         path =self.url+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
         
         self.limpiar();   
         self.titulo('Cargar Pago');
         
         self.id_planilla(datos.id);   
         self.planillaVO.id(datos.id);
         self.planillaVO.contratista_id(datos.contratista.id);
         self.planillaVO.ano(datos.ano);
         self.planillaVO.mes(datos.mes);
         self.mes(datos.mes);
         self.planillaVO.fecha_pago(datos.fecha_pago);
         //self.planillaVO.soporte('');
         self.planillaVO.fecha_limite(datos.fecha_limite);
         self.planillaVO.selectedContratista(datos.contratista);
         self.planilla(datos.soporte);
         self.nombre_contratista(datos.contratista.nombre);
         $('#modal_acciones_actualizar').modal('show');
         self.cargar_pago(true);

         }, path, parameter, function(){
                    cerrarLoading();
                   });

    }

     self.consultar_meses=function(contratista_id,ano){
        path =path_principal + '/seguridad-social/obtener_meses_planilla/';
        parameter={contratista_id:contratista_id,ano:ano};
        RequestGet(function (datos, estado, mensage) {
          self.listado_meses(datos);
         }, path, parameter, function(){
                    cerrarLoading();
                   });
     }

     self.consultar_planilla_empleado = function () {                            
      path =path_principal + '/seguridad-social/consultar_planilla_empleado/';
      parameter = { planilla_id: $('#hd_planilla').val()};
      RequestGet(function (datos, estado, mensage) {

          if (estado == 'ok' && datos!=null && datos.length > 0) {
            
              //self.mensaje('');
              //self.listado(results);  
              self.listado_planilla_empleado(convertToObservableArray(datos));  

          } else {
              self.listado_planilla_empleado([]);                    
          }                
      }, path, parameter, function(){
                    cerrarLoading();
                   });       
    }

     self.planillaVO.ano.subscribe(function(val){
        if (val.length==4 && self.planillaVO.contratista_id()>0) {
          self.consultar_meses(self.planillaVO.contratista_id(),val);
        }
     });

      self.planillaVO.contratista_id.subscribe(function(val){
        if (val>0 && self.planillaVO.ano()>0) {
          self.consultar_meses(val,self.planillaVO.ano());
        }
     });
    
    self.planillaVO.selectedContratista.subscribe(function(data){
      if (self.planillaVO.id()==0) {
        self.nit(data ? data.nit : '');        
        self.planillaVO.contratista_id(data ? data.id : '');
      }        
    });


    self.consultar_empleados = function (criterio) {                            
      path =path_principal + '/seguridad-social/consultar_empleados_por_contratista/';
      parameter = {criterio:criterio, planilla_id:$('#hd_planilla').val(),contratista_id: $('#hd_contratista').val()};
      RequestGet(function (datos, estado, mensage) {

          if (estado == 'ok' && datos!=null && datos.length > 0) {
             
              self.listado_empleado(agregarOpcionesObservable(datos));  

          } else {
              self.mensaje_empleado(mensajeNoFound);
              self.listado_empleado([]);                    
          }                
      }, path, parameter, function(){
                    cerrarLoading();
                   });       
    }

    self.agregar_empleado_a_planilla = function () {                            
      if (self.listado_empleado()!=null && self.listado_empleado().length>0) {

        var lista=[]; 
        ko.utils.arrayForEach(self.listado_empleado(), function (p) {
          if (p.procesar()) {
            lista.push(p.id);
          }
        });
        var parametros={                     
           callback:function(datos, estado, mensaje){
              if (estado=='ok') {
                //$('#modal_buscar_empleado').modal('close');
                self.consultar_empleados();
                self.consultar_planilla_empleado();                                
              } 
           },//funcion para recibir la respuesta 
           url:path_principal + '/seguridad-social/agregar_empleado_a_planilla/',
           parametros:{lista_empleado:lista,planilla_id:$('#hd_planilla').val()},
            completado:function(){
                cerrarLoading();
            }
        };
                   
        Request(parametros);
      }
    }

     self.eliminar=function(){
         var lista=[];
        ko.utils.arrayForEach(self.listado(), function(p){          
          if (p.procesar()) {
            lista.push(p.id);
          }
        });
        
        RequestAnularOEliminar('¿Desea eliminar el(los) registro(s) seleccionado(s)?', 
          path_principal+'/seguridad-social/eliminar_planilla/', {lista:lista}, 
          function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultar(self.paginacion.pagina_actual());                  
             }
        }, function(){
            cerrarLoading();              
        }, false);  
    }

    self.seleccionar.subscribe(function(val){
      ko.utils.arrayForEach(self.listado(),function(p){
          p.procesar(val);
      });
    });

    self.consultar_contratista_id=function(val){

      ko.utils.arrayForEach(self.listado_contratista(), function(p){

        if (p.id == val) {
          self.nit(p.nit);
        }

      });     

    }

     self.eliminar_planilla_empleado=function(item){
                 
        RequestAnularOEliminar('¿Desea quitar de la planilla al el empleado "'+ item.nombres() + ' ' + item.apellidos() +'"?', 
          path_principal+'/api/PlanillaEmpleado/'+item.planilla_empleado_id()+'/', {}, 
          function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultar_planilla_empleado(self.paginacion.pagina_actual());                  
             }
        }, function(){
            cerrarLoading();              
        }, true);  
    }

     self.exportar_planilla_empleado_excel=function(){
        location.href=path_principal+"/seguridad-social/exportar-planilla_empleados/?planilla_id="+$('#hd_planilla').val();    
      }

    self.seleccionarEmpleados.subscribe(function(val){
      ko.utils.arrayForEach(self.listado_empleado(),function(p){
          p.procesar(val);
      });
    }); 

} 

var planilla = new PlanillaViewModel();
PlanillaViewModel.errores_planilla = ko.validation.group(planilla.planillaVO);
PlanillaViewModel.errores_filtros = ko.validation.group(planilla.filtros);
planilla.consultar(1);//iniciamos la primera funcion
planilla.consultar_contratista();
ko.applyBindings(planilla);