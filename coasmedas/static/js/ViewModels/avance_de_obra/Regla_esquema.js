function ReglaViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
    self.listado_regla=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.habilitar_campos=ko.observable(true);


    self.reglaVO={
        id:ko.observable(0),
        esquema_id:ko.observable(0),
        orden:ko.observable(0),
        operador:ko.observable(0).extend({ min: {params:1,message:"(*)Seleccione un operador"}}),
        limite:ko.observable('').extend({ required: { message: '(*)Digite el limite' } }),
        estado:ko.observable('').extend({ required: { message: '(*)Digite el nombre del estado' } }),
        regla_anterior:ko.observable(0)
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

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Agregar Regla');
        self.habilitar_campos(true);
        $('#modal_acciones').modal('show');
    }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }



    // //limpiar el modelo 
     self.limpiar=function(){   
        self.reglaVO.id(0);
        self.reglaVO.orden(0);
        self.reglaVO.limite(0);
        self.reglaVO.estado('');
        self.reglaVO.operador(0);
        self.reglaVO.esquema_id(0);
        self.reglaVO.regla_anterior(0);
     }


    self.checkall.subscribe(function(value){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });


    self.regla_anterior=function(){

        path =path_principal+'/api/Regla_Estado_avance_obra/?format=json&sin_paginacion';
        parameter = {esquema_id:$('#id_esquema').val()};
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos!=null && datos.length > 0) {

                self.listado_regla(datos);            
            }else{
                self.listado_regla([]);
            }   
        }, path, parameter);  
    }


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("dato_regla_esquema",self.filtro() || '');
            path = path_principal+'/api/Regla_Estado_avance_obra/?format=json&sin_paginacion';
            parameter = { dato: self.filtro(),esquema_id:$('#id_esquema').val()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(convertToObservableArray(datos)));
                     $('#modal_acciones').modal('hide');

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
            }, path, parameter);
    }

    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)

         path =path_principal+'/api/Regla_Estado_avance_obra/'+obj.id()+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Regla');

             self.reglaVO.id(results.id);
             self.reglaVO.estado(results.estado);
             self.reglaVO.orden(results.orden);
             self.reglaVO.limite(results.limite);
             self.reglaVO.operador(results.operador);
             if(results.reglaAnterior==null){
                self.reglaVO.regla_anterior(0);
             }else{
                self.reglaVO.regla_anterior(results.reglaAnterior.id);
             }             
             self.habilitar_campos(true);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }

      self.consultar_por_id_detalle = function (obj) {
             // alert(obj.id)

        
       path =path_principal+'/api/Regla_Estado_avance_obra/'+obj.id()+'/?format=json';
         RequestGet(function (results,count) {
           
              self.titulo('Regla');

             self.reglaVO.id(results.id);
             self.reglaVO.estado(results.estado);
             self.reglaVO.orden(results.orden);
             self.reglaVO.limite(results.limite);
             self.reglaVO.operador(results.operador);
             if(results.reglaAnterior==null){
                self.reglaVO.regla_anterior(0);
             }else{
                self.reglaVO.regla_anterior(results.reglaAnterior.id);
             }
             self.habilitar_campos(false);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }

    self.guardar=function(){

        if (ReglaViewModel.errores_regla().length == 0) {//se activa las validaciones

           self.reglaVO.esquema_id($('#id_esquema').val());

            if(self.reglaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                            self.regla_anterior();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Regla_Estado_avance_obra/',//url api
                     parametros:self.reglaVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
           }else{

                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                          self.limpiar();
                          self.regla_anterior();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Regla_Estado_avance_obra/'+self.reglaVO.id()+'/',
                       parametros:self.reglaVO                        
                  };

                  Request(parametros);

            }

        } else {
             ReglaViewModel.errores_regla.showAllMessages();//mostramos las validacion
        }
     }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.limpiar();
            self.consultar(1);
        }
        return true;
    }

    self.eliminar = function () {

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id.push({
                        id:d.id()
                   })
                }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una regla para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avance_de_obra/eliminar_id_regla_estado/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar las reglas seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }

   

 }


var regla = new ReglaViewModel();

$('#txtBuscar').val(sessionStorage.getItem("dato_regla_esquema"));
ReglaViewModel.errores_regla = ko.validation.group(regla.reglaVO);
regla.consultar(1);//iniciamos la primera funcion
regla.regla_anterior();
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(regla,content);
ko.applyBindings(regla,header);
