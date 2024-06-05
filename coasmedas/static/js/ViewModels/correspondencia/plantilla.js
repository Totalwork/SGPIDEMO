function PlantillaViewModel() {

    var self=this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.url=path_principal+'/api/CorrespondenciaPantillas/'; 

    self.plantillaVO={
    	id: ko.observable(0),
      empresa_id: ko.observable($('#empresa_id').val()),
      soporte: ko.observable('').extend({ required: { message: '(*) Seleccione un documento word (.docx).' } }),
    };

     // //limpiar el modelo 
     self.limpiar = function(){      
        self.plantillaVO.id(0);
        self.plantillaVO.soporte('');
        self.plantillaVO.soporte.isModified(false);  

        $('#archivo').fileinput('reset');
        $('#archivo').val('');
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
        parameter = { empresa : $('#empresa_id').val(), dato: self.filtro() , page: pagina };
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
      }, path, parameter,undefined,false);		

	}

  self.consulta_enter = function(d, e) {
        if (e.which == 13) {
            self.consultar();
        }
        return true;
    }

	self.guardar_archivo=function(){
    	
        if (PlantillaViewModel.errores().length==0) {


            if(self.plantillaVO.id()==0){
                peticion = 'POST';
                url_peticion = self.url;
            }else{       
                peticion = 'PUT'; 
                url_peticion = self.url+ self.plantillaVO.id()+'/';         
            }


            var parametros={     
                metodo: peticion,                 
                callback:function(datos, estado, mensaje){
                    if (estado=='ok') {
                        if (peticion=="POST") {
                            self.limpiar();  
                            $('#modal_acciones_soporte').modal('hide');  
                        };
                        
                        self.consultar(self.paginacion.pagina_actual());   
                        $('#soportes').fileinput('reset');
                        $('#soportes').val('');                            
                    }                     
                 },//funcion para recibir la respuesta 
                 url:  url_peticion,//url api
                 parametros: self.plantillaVO                        
            };
            RequestFormData(parametros); 



        } else {
            PlantillaViewModel.errores.showAllMessages();//mostramos las validacion
        }

    }

	self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Subir plantilla');
        $('#modal_acciones_soporte').modal('show');
    }

     self.consultar_por_id = function (obj) {
        self.limpiar();
       path = self.url+obj.id+'/?format=json';
         RequestGet(function (results,count) {

            self.plantillaVO.id(results.id);
             
            self.titulo('Modificar plantilla'); 
            $('#modal_acciones_soporte').modal('show');

             
         }, path, parameter);
     }   



}

var plantilla = new PlantillaViewModel();
PlantillaViewModel.errores=ko.validation.group(plantilla.plantillaVO);
ko.applyBindings(plantilla);