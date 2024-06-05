function EventoViewModel() {

	var self = this;
	self.titulo=ko.observable('');
    self.titulo_btn=ko.observable('Guardar');
    self.filtro=ko.observable('');
    self.mensaje=ko.observable('');
    self.conjunto_id =ko.observable('');
    
	self.url=path_principal+'/api/'; 
	self.listado = ko.observableArray([]);
	self.listado_conjunto_eventos = ko.observableArray([]);	

	self.checkall=ko.observable(false);
	// -- -- -- EVENTOS -- -- -- EVENTOS -- -- --- EVENTOS -- -- -- EVENTOS //
	self.eventoVO={
	 	id:ko.observable(0),
	 	conjunto_id:ko.observable('').extend({ required: { message: ' Seleccione el conjunto.' } }),
	 	nombre:ko.observable('').extend({ required: { message: ' Digite el nombre del evento.' } }),
	 	valor:ko.observable('').extend({ required: { message: ' Digite el valor del evento.' } }),    
	};
	// //limpiar el modelo 
     self.limpiar=function(){      
        self.eventoVO.id(0);
        self.eventoVO.conjunto_id('');
        self.eventoVO.nombre('');
        self.eventoVO.valor('');  
        self.eventoVO.conjunto_id.isModified(false);
        self.eventoVO.nombre.isModified(false);
        self.eventoVO.valor.isModified(false);       
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
    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }
    self.paginacion.pagina_actual.subscribe(function (pagina) {       
       self.consultar(pagina);
    });
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Evento');
        $('#modal_acciones').modal('show');
    }
    //exportar excel    
    self.exportar_excel=function(){
        location.href=self.url_funcion+"reporte_proyecto?dato="+self.filtro()+"&mcontrato="+self.mcontrato_id_filtro()+"&contratista="+self.contratista_id_filtro();
    } 
    self.abrir_modal_busqueda = function () {
        self.titulo('Consulta de eventos');
        $("#modal_busqueda").modal("show");
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }
	//funcion consultar proyectos que ppuede  ver la empresa
    self.consultar = function (pagina) {
        if (pagina > 0) {        
            self.filtro($('#txtBuscar').val());
            path = self.url+'MultaEvento/';
            parameter = { dato: self.filtro(), pagina: pagina , conjunto : self.conjunto_id() };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado(agregarOpcionesObservable(datos.data));  

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
                self.llenar_paginacion(datos,pagina);
            }, path, parameter);
        }
    }
	//funcion consultar conjunto de eventos
    self.consultar_conjunto_eventos = function () {                
            path = self.url+'MultaConjuntoEvento/';
            parameter = { ignorePagination : 1 };
            RequestGet(function (datos, estado, mensage) {
                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.listado_conjunto_eventos(datos);
                } else {
                    self.listado_conjunto_eventos([]);
                }          
            }, path, parameter);        
    }
    // //funcion guardar
     self.guardar=function(){
    	if (EventoViewModel.errores_evento().length == 0) {//se activa las validaciones
            if(self.eventoVO.id()==0){
                peticion = 'POST';
                url_peticion = self.url+'MultaEvento/';
            }else{       
                peticion = 'PUT'; 
                url_peticion = self.url+'MultaEvento/'+ self.eventoVO.id()+'/';         
            }

            var parametros={     
                    metodo: peticion,                
                   callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                          self.filtro("");
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                          self.limpiar();
                        } 
                   },//funcion para recibir la respuesta 
                   url: url_peticion,
                   parametros:self.eventoVO                        
            };
            RequestFormData(parametros);
        } else {
             EventoViewModel.errores_evento.showAllMessages();//mostramos las validacion
        }
     }

    self.eliminar = function () {

        var lista_id=[];

        $(".checkboxList:checkbox:checked").each(function() {
            lista_id.push($(this).val())
        });

        if(lista_id.length==0){
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un evento para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{
             var path =self.url_funcion+'destroy_proyecto/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar los eventos seleccionados?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })
        }    
    } 

    self.consultar_por_id = function (obj) { 
        self.titulo_btn('Actualizar');       
        path =path_principal+'/api/MultaEvento/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
            self.titulo('Actualizar Evento');
            $('#modal_acciones').modal('show');
            self.eventoVO.id(results.id);
            self.eventoVO.conjunto_id(results.conjunto.id);
            self.eventoVO.nombre(results.nombre);
            self.eventoVO.valor(results.valor);       
        }, path, parameter);
    } 

    self.checkall.subscribe(function(value ){
        value==true?$(".checkboxList").prop('checked',true):$(".checkboxList").prop('checked', false);
    });

}

var evento = new EventoViewModel();
EventoViewModel.errores_evento = ko.validation.group(evento.eventoVO);
ko.applyBindings(evento);