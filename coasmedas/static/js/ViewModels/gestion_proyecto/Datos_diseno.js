
function DatosViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false); 

    self.datosVO={
	 	id:ko.observable(0),
	 	nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del datos.' } }),
        unidad_medida_id:ko.observable('').extend({ required: { message: '(*)Seleccione una unidad de medida.' } }),
        orden:ko.observable(0)
	 };



    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Dato del diseño');
        $('#modal_acciones').modal('show');
    }

     self.subir_nivel=function(obj){
          var index=0;
          var valor=obj.orden();
          
          ko.utils.arrayForEach(self.listado(), function(d) {
              
              if(obj.orden()!=1){
                 if(d.orden()==obj.orden()){
                    var valor2=self.listado()[index-1].orden();
                    self.listado()[index-1].orden(valor);
                    d.orden(valor2);
                    return true;
                    //alert(d.orden())
                 }
              }
               index++;
               // obj.orden(1);
          });
         
     };

 self.bajar_nivel=function(obj){
      
      var index=0;
      var valor=obj.orden();
      ko.utils.arrayForEach(self.listado(), function(d) {
           
          if(obj.orden()!=self.listado().length){
             if(d.orden()==obj.orden()){
                var valor2=self.listado()[index+1].orden();                
                self.listado()[index+1].orden(valor);
                d.orden(valor2); 
                return true;
                //alert(d.orden())
             }
          }
           index++;
           // obj.orden(1);
      });
 };

   
   
    // //limpiar el modelo 
     self.limpiar=function(){    	 
         
             self.datosVO.id(0);
             self.datosVO.nombre('');
             self.datosVO.unidad_medida_id('');
             self.datosVO.orden(0);
     }
    // //funcion guardar
     self.guardar=function(){

    	if (DatosViewModel.errores_datos().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);

            if(self.datosVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar();
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/GestionProyectoDatoDiseno/',//url api
                     parametros:self.datosVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
            }else{

                 
                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.consultar();
                          $('#modal_acciones').modal('hide');
                          self.limpiar();
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/GestionProyectoDatoDiseno/'+self.datosVO.id()+'/',
                       parametros:self.datosVO                        
                  };

                  Request(parametros);

            }

        } else {
             DatosViewModel.errores_datos.showAllMessages();//mostramos las validacion
        }
     }
    //funcion consultar de tipo get recibe un parametro
    self.consultar = function () {
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/GestionProyectoDatoDiseno?sin_paginacion';
            parameter = { dato: self.filtro()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(convertToObservableArray(datos)));  

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
    }

    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar();
        }
        return true;
    }

    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
       path =path_principal+'/api/GestionProyectoDatoDiseno/'+obj.id()+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar Tipo de Fondo');

             self.datosVO.id(results.id);
             self.datosVO.nombre(results.nombre);
             self.datosVO.unidad_medida_id(results.unidad_medida.id);
             self.datosVO.orden(results.orden);
             $('#modal_acciones').modal('show');
         }, path, parameter);

     }


    self.actualizar_orden=function(valor){

         var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {

               lista_id.push({
                        id:d.id,
                        orden:d.orden()
                })
         });

         var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar();
                            self.checkall(false);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/gestion_proyecto/actualizar_orden/',//url api
                     parametros:{ lista: lista_id }                     
                };
                //parameter =ko.toJSON(self.contratistaVO);
        Request(parametros);

    }


    
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un dato para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/gestion_proyecto/eliminar_datos_disenos/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los datos seleccionados?", path, parameter, function () {
                 self.consultar();
                 self.checkall(false);
             })

         }     
    
        
    }

 }

var datos = new DatosViewModel();
DatosViewModel.errores_datos = ko.validation.group(datos.datosVO);
datos.consultar();//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(datos,content);
ko.applyBindings(datos,header);