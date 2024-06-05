function AgendaViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
  self.checkall=ko.observable(false);

  self.listado_usuarios=ko.observableArray([]);
  self.filtro_usuario=ko.observable('');
  self.id_empresa=ko.observable(0);
  self.checkall2=ko.observable(false);
  self.mensaje_usuario=ko.observable('');
  self.mensaje_guardando_usuario=ko.observable('');

  self.actividadVO={
        tipo_id:ko.observable(0).extend({ required: { message: '(*)Seleccione el tipo de la actividad' } }),
        asunto:ko.observable('').extend({ required: { message: '(*)Digite el asunto de la actividad' } }),
        solicitante_id:ko.observable(0),
        fecha:ko.observable(new Date()).extend({ required: { message: '(*)Digite una fecha de la actividad' } }),
        fecha_transaccion:ko.observable(''),
        lugar:ko.observable('').extend({ required: { message: '(*)Digite un lugar de la actividad' } }),
        listado_archivo:ko.observableArray([{
            'soporte':ko.observable('')
        }]),
        listado_usuarios:ko.observableArray([])       
    }

  self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
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


  self.paginacion_usuario = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
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


  self.abrir_modal_usuario = function () {
        //self.limpiar();
        $('#modal_usuario').modal('show');
  }

  self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Actividad');
        $('#modal_acciones').modal('show');
  }

  self.agregar_soporte=function(){
        self.actividadVO.listado_archivo.push({'soporte':ko.observable('')});
  }

  self.eliminar_soporte=function(val){
        self.actividadVO.listado_archivo.remove(val);
  }

  self.limpiar=function(){

        self.actividadVO.tipo_id(0);
        self.actividadVO.asunto('');
        self.actividadVO.solicitante_id(0);
        self.actividadVO.fecha('');
        self.actividadVO.fecha_transaccion('');
        self.actividadVO.lugar('');
        self.actividadVO.listado_archivo([{
            'soporte':ko.observable('')
        }]);
        self.actividadVO.listado_usuarios([]);
  }


  self.guardar=function(){

       if (AgendaViewModel.errores_actividad().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            var lista_id='';
            self.actividadVO.solicitante_id($("#id_usuario").val());
            var data = new FormData();
            data.append('solicitante_id',self.actividadVO.solicitante_id());
            data.append('asunto',self.actividadVO.asunto());
            data.append('fecha_transaccion',self.actividadVO.fecha_transaccion());
            data.append('fecha',self.actividadVO.fecha());
            data.append('lugar',self.actividadVO.lugar());
            data.append('tipo_id',self.actividadVO.tipo_id());

            ko.utils.arrayForEach(self.actividadVO.listado_archivo(), function(d) {

                    if(d.soporte()!=''){
                         data.append('soporte[]',d.soporte());
                    }
             }); 

            lista_id=$("#id_usuario").val();
            ko.utils.arrayForEach(self.actividadVO.listado_usuarios(), function(d) {
                    lista_id=lista_id+","+d.id;
             }); 

            data.append('listado_usuarios',lista_id);

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            $('#modal_acciones').modal('hide');
                            self.consultar(1);
                        }                        
                        
                        $('#loading').hide();
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/TareaActividad/',//url api
                     parametros:data                      
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData2(parametros);

        } else {
             AgendaViewModel.errores_actividad.showAllMessages();//mostramos las validacion
        }

  }

  self.eliminar_usuario=function(val){
      self.actividadVO.listado_usuarios.remove(val);

      if(self.actividadVO.listado_usuarios().length==0){
          self.mensaje('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se han agregado invitados para esta actividad.</div>');
      }else{
        self.mensaje('');
      }
  }


  self.consultar_usuario=function(pagina){

        if (pagina > 0) { 
            var empresa=0;             
            self.filtro_usuario($('#txtBuscar2').val());
            if(self.id_empresa()==0){
                empresa=$("#id_empresa").val();
            }else{
                empresa=self.id_empresa();
            }
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            path = path_principal+'/api/usuario/?format=json&page='+pagina;
            parameter = {'empresa_id':empresa,pagina:pagina,dato:self.filtro_usuario()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje_usuario('');
                    //self.listado(results); 
                    self.listado_usuarios(agregarOpcionesObservable(datos.data));

                } else {
                    self.mensaje_usuario('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron registros</div>');
                    self.listado_usuarios([]);
                }

                self.llenar_paginacion_usuario(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
        }

    }

    self.consulta_enter_usuario = function (d,e) {
        if (e.which == 13) {
            self.consultar_usuario(1);
        }
        return true;
    }


    self.guardar_usuario=function(){
      ko.utils.arrayForEach(self.listado_usuarios(), function(d) {

                if(d.eliminado()==true){
                    cant=0;
                    ko.utils.arrayForEach(self.actividadVO.listado_usuarios(), function(x) {
                        if(x.id==d.id){
                          cant=1;
                        }
                    });
                    if(cant==0){
                      self.actividadVO.listado_usuarios.push(d);
                    }
                    
                }
      }); 
      self.mensaje_guardando_usuario();
      self.mensaje_guardando_usuario('<div class="alert alert-success alert-dismissable"><i class="fa fa-check"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>El registro ha sido guardado exitosamente.</div>');
      self.mensaje('');
      self.checkall2(false);

    }

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {  

            self.mensaje('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se han agregado invitados para esta actividad.</div>');
            
            path = path_principal+'/api/TareaActividad/?format=json&sin_paginacion';
            parameter = '';
            RequestGet(function (datos, estado, mensage) {

                $('#calendar').fullCalendar( 'destroy' );
                var Calendar = $('#calendar');
                var Picker = $('.inline-mp');

                // Init FullCalendar Plugin
                Calendar.fullCalendar({
                  header: {
                    left: 'prevYear,nextYear prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay'
                  },
                  lang:'es',
                  events:self.llenar_lista(datos),
                  eventClick: function(calEvent, jsEvent, view) {
                      location.href=path_principal+"/administrador_tarea/edicion_actividad/"+calEvent.id;
                  },
                  viewRender: function(view) {
                    // If monthpicker has been init update its date on change
                    if (Picker.hasClass('hasMonthpicker')) {
                      var selectedDate = Calendar.fullCalendar('getDate');
                      var formatted = moment(selectedDate, 'MM-DD-YYYY').format('MM/YY');
                      Picker.monthpicker("setDate", formatted);
                    }
                    // Update mini calendar title
                    var titleContainer = $('.fc-title-clone');
                    if (!titleContainer.length) {
                      return;
                    }
                    titleContainer.html(view.title);
                  }
                });

                // Init MonthPicker Plugin and Link to Calendar
                Picker.monthpicker({
                  prevText: '<i class="fa fa-chevron-left"></i>',
                  nextText: '<i class="fa fa-chevron-right"></i>',
                  showButtonPanel: false,
                  onSelect: function(selectedDate) {
                    var formatted = moment(selectedDate, 'MM/YYYY').format('MM/DD/YYYY');
                    Calendar.fullCalendar('gotoDate', formatted)
                  }
                });
                cerrarLoading();
            }, path, parameter,undefined, false);      
            
            

        }
    }

  self.llenar_lista=function(data){

     var lista=[];

    
      ko.utils.arrayForEach(data, function(d) {

          fecha_completo=d['fecha'].split(' ');
        
          lista_id={
            title:d['asunto'],
            id:d['id'],
            start:d['fecha'],
            end:d['fecha']
          };
          lista.push(lista_id);
      });
     return lista;
  }



  self.checkall2.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_usuarios(), function(d) {

                    d.eliminado(value);
             }); 
    });


  self.llenar_paginacion_usuario = function (data,pagina) {

        self.paginacion_usuario.pagina_actual(pagina);
        self.paginacion_usuario.total(data.count);       
        self.paginacion_usuario.cantidad_por_paginas(resultadosPorPagina);

    }

  self.paginacion_usuario.pagina_actual.subscribe(function (pagina) {
        self.consultar_usuario(pagina);
    });


  self.id_empresa.subscribe(function (valor) {
           
          self.filtro_usuario($('#txtBuscar2').val());
          self.consultar_usuario(1); 
          
    });


   

 }

var agenda = new AgendaViewModel();
agenda.consultar(1);//iniciamos la primera funcion
agenda.consultar_usuario(1);
AgendaViewModel.errores_actividad = ko.validation.group(agenda.actividadVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(agenda,content);
ko.applyBindings(agenda,header);