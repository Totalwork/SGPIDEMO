
function ConfigurarUnidadConstructivaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

    self.macrocontrato_select=ko.observable(0);
    self.lista_contrato=ko.observableArray([]);
    self.lista_proyecto=ko.observableArray([]);
    self.proyecto_select=ko.observable(0);

    self.nombre_contrato=ko.observable('');
    self.nombre_proyecto=ko.observable('');
    self.contrato_id=ko.observable('');
    self.archivo=ko.observable('');
  

     //Representa un modelo de configurar unidad constructiva
    self.ConfigurarUnidadConstructivaVO={
        id:ko.observable(0),
        contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contrato' } }),
        proyecto_id:ko.observable(''),
        codigo:ko.observable('').extend({ required: { message: '(*)Digite el codigo' } }),
        descripcion:ko.observable(''),
        valor_mano_obra:ko.observable(0),
        valor_materiales:ko.observable(0),
        //tipo_registro:ko.observable(0),

     };

     //paginacion de configurar unidad constructiva
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

    //paginacion
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

  
    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });

    //funcion para abrir modal de registrar la unidad constructiva
    self.abrir_modal = function () {
        self.limpiar();
        self.consultar_macrocontrato();
        self.titulo('Nueva Unidad Constructiva');
        $('#modal_acciones').modal('show');
    }


    //funcion para filtrar las unidades constructivas
    self.filtrar_unidades_constructivas = function () {
        self.titulo('Filtrar Unidades Constructiva');
        //self.limpiar();
        self.consultar_macrocontrato();
        $('#modal_filtro_unidades').modal('show');
    }


    //funcion para abrir modal de carga masiva
    self.carga_masiva = function () {
        self.consultar_macrocontrato();
        self.titulo('Carga masiva');
        $('#modal_carga_masiva').modal('show');
    }


     //limpiar el modelo de configurar unidad constructiva
     self.limpiar=function(){     
         
        self.ConfigurarUnidadConstructivaVO.id(0);
        self.ConfigurarUnidadConstructivaVO.contrato_id('');
        self.ConfigurarUnidadConstructivaVO.proyecto_id('');
        self.ConfigurarUnidadConstructivaVO.codigo('');
        self.ConfigurarUnidadConstructivaVO.descripcion('');
        self.ConfigurarUnidadConstructivaVO.valor_mano_obra('');
        self.ConfigurarUnidadConstructivaVO.valor_materiales('');
        //self.ConfigurarUnidadConstructivaVO.tipo_registro('');

        self.ConfigurarUnidadConstructivaVO.contrato_id.isModified(false);
        self.ConfigurarUnidadConstructivaVO.codigo.isModified(false);
     }


    //consultar los macrocontrato
    self.consultar_macrocontrato=function(){

         path =path_principal+'/proyecto/filtrar_proyectos/';
         parameter={ tipo: '12' };
         RequestGet(function (datos, estado, mensaje) {
           
            self.lista_contrato(datos.macrocontrato);

         }, path, parameter,function(){
                 self.macrocontrato_select(sessionStorage.getItem("mcontrato_filtro_unidades"));       
             },false,false);

    }


    //funcion que se ejecuta cuando se cambia en el select de contrato 
    self.ConfigurarUnidadConstructivaVO.contrato_id.subscribe(function (value) {
        if(value!=''){
            self.consultar_proyecto(value);

        }else{

            self.lista_proyecto([]);

        }
    });

        //funcion que se ejecuta cuando se cambia en el select de contrato 
    self.macrocontrato_select.subscribe(function (value) {
        if(value!=''){
            self.consultar_proyecto(value);

        }else{

            self.lista_proyecto([]);

        }
    });


    //consultar los proyectos
    self.consultar_proyecto=function(mcontrato){

        if (mcontrato>0) {
           path =path_principal+'/api/Proyecto_empresas_lite/?sin_paginacion';
           parameter={mcontrato:mcontrato,empresa: $("#id_empresa").val()};
           RequestGet(function (datos, estado, mensaje) {

              self.lista_proyecto(datos);

           }, path, parameter,function(){
                   self.proyecto_select(sessionStorage.getItem("proyecto_filtro_unidades"));       
               },false,false);
        }

    }


    //funcion guardar y actualizar las nuevas unidades constructivas
     self.guardar=function(){


        if (ConfigurarUnidadConstructivaViewModel.errores_configuracion().length == 0) {//se activa las validaciones

            if(self.ConfigurarUnidadConstructivaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.limpiar();
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Unidad_contructiva/',//url api
                     parametros:self.ConfigurarUnidadConstructivaVO                        
                };
                Request(parametros);
            }else{              

                  var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                          self.filtro("");
                          self.limpiar();
                          self.consultar(self.paginacion.pagina_actual());
                          $('#modal_acciones').modal('hide');
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Unidad_contructiva/'+self.ConfigurarUnidadConstructivaVO.id()+'/',
                       parametros:self.ConfigurarUnidadConstructivaVO                        
                  };

                  Request(parametros);

            }

        } else {
             ConfigurarUnidadConstructivaViewModel.errores_configuracion.showAllMessages();//mostramos las validacion
        } 
     }



    //funcion consultar
    self.consultar = function (pagina) {
        
        //alert($('#mcontrato_filtro').val())
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            sessionStorage.setItem("dato_puntos_unidades", $('#txtBuscar').val() || '');
            sessionStorage.setItem("proyecto_filtro_unidades", $('#proyecto_filtro').val() || '');           
            sessionStorage.setItem("mcontrato_filtro_unidades", $('#mcontrato_filtro').val() || '');

            self.cargar(pagina);
            
        }
    }

    self.cargar = function(pagina){

        let filtro = sessionStorage.getItem("dato_puntos_unidades");
        let proyecto = sessionStorage.getItem("proyecto_filtro_unidades");
        let mcontrato_filtro = sessionStorage.getItem("mcontrato_filtro_unidades");

        var empresa=$("#empresa").val();

        path = path_principal+'/api/Unidad_contructiva/?format=json';
            parameter = { dato: filtro, page: pagina,mcontrato:mcontrato_filtro,
                            proyecto:proyecto};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)
                    cerrarLoading();

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter,undefined, false);

    }


    //consultar precionando enter
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    //consultar por id de la nuevas unidades constructivas
    self.consultar_por_id = function (obj) {

        // self.consultar_macrocontrato();
        // self.consultar_proyecto();            
       
        path =path_principal+'/api/Unidad_contructiva/'+obj.id+'/?format=json';
         RequestGet(function (datos, estado, mensaje) {
           
            self.titulo('Actualizar Unidad Constructiva');

            self.ConfigurarUnidadConstructivaVO.id(datos.id);
            self.ConfigurarUnidadConstructivaVO.contrato_id(datos.contrato.id);
            self.ConfigurarUnidadConstructivaVO.codigo(datos.codigo);
            self.ConfigurarUnidadConstructivaVO.descripcion(datos.descripcion);
            self.ConfigurarUnidadConstructivaVO.valor_mano_obra(datos.valor_mano_obra);
            self.ConfigurarUnidadConstructivaVO.valor_materiales(datos.valor_materiales);

            if (datos.proyecto!=null) {

              self.ConfigurarUnidadConstructivaVO.proyecto_id(datos.proyecto.id);
              self.nombre_proyecto(datos.proyecto.nombre)

            }else{
              self.ConfigurarUnidadConstructivaVO.proyecto_id('');
              self.nombre_proyecto('')

            }

            self.nombre_contrato(datos.contrato.nombre)

            $('#modal_acciones').modal('show');

         }, path, parameter);

     }

   
    //eliminar las nuevas unidades constructivas
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las unidades constructivas para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/control_cambios/eliminar_unidad_constructiva/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las unidades cons seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }



    //exportar excel la tabla del listado de las nuevas unidades constructivas
   self.exportar_excel=function(){

        // var contrato=self.ConfigurarUnidadConstructivaVO.contrato_id();
        // var proyecto=self.ConfigurarUnidadConstructivaVO.proyecto_id();

         location.href=path_principal+"/control_cambios/exportar_unidad_constructiva/";
     }


  //funcion para carga masiva
  self.carga_excel=function(){

    if(self.contrato_id()=='' || self.archivo()==''){

      $.confirm({
        title:'Informativo',
        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione el contrato y cargue el archivo.<h4>',
        cancelButton: 'Cerrar',
        confirmButton: false
      });


    }else{

      var data = new FormData();

      data.append('contrato',self.contrato_id());
      data.append('archivo',self.archivo());
      var parametros={                     
        callback:function(datos, estado, mensaje){
          self.consultar(1);
          $('#modal_carga_masiva').modal('hide');                    
                          
        },//funcion para recibir la respuesta 
        url:path_principal+'/control_cambios/carga_masiva_excel/',//url api
        parametros:data                        
      };
      RequestFormData2(parametros);

    }

  }   

}

var unidad_constructiva = new ConfigurarUnidadConstructivaViewModel();
ConfigurarUnidadConstructivaViewModel.errores_configuracion= ko.validation.group(unidad_constructiva.ConfigurarUnidadConstructivaVO);
ko.applyBindings(unidad_constructiva);
