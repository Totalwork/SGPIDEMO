function GestionServidumbreViewModel() {

	var self = this;
	self.listado_expedientes=ko.observableArray([]);
    self.listado_proyectos=ko.observableArray([]);
    self.listadoproyectos=ko.observableArray([]);
	self.mensaje=ko.observable('');
    self.mensajeProyecto=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    self.habilitar_campos=ko.observable(true);

    self.filtroProyecto = ko.observable('');

    self.url=path_principal+'/api/';
    self.urlHOME=path_principal+'/servidumbre/home';
    self.url_funcion=path_principal+'/servidumbre/'; 

    self.filtro_expediente={
        dato:ko.observable(''),
        id:ko.observable(''),
    };

    self.filtro_expedienteVO={
        dato:ko.observable(''),
        proyecto_id:ko.observable(''),
        estado_id:ko.observable(''),
        usuario_creador_id:ko.observable('')
        
    };

    self.expedienteVO={        
        id:ko.observable(0),
        proyecto_id:ko.observable(0).extend({ required: { message: '(*)Seleccione el proyecto' } }),
        fecha_creacion:ko.observable(''),
        usuario_creador_id:ko.observable(0),
        usuario_creador:ko.observable(''),
        estado_id:ko.observable(''),     
        //nopredios:ko.observable(''),   
     };

     //Representa un modelo ded la tabla proyecto
     self.proyectoVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend(),
        mcontrato_id:ko.observable('').extend(),
        municipio_id:ko.observable('').extend(),
        departamento_id:ko.observable('').extend()
     };

     self.guardarExpediente = function(){
        if (self.expedienteVO.proyecto_id() != 0) {//se activa las validaciones
            $("#validacionProyecto").hide();
            if(self.expedienteVO.id()==0){
                var parametros={
                     callback:function(datos, estado, mensaje){
                        if (estado=='ok') {
                            self.cargar(self.paginacion.pagina_actual());
                            self.limpiar();
                        }                     
                     },//funcion para recibir la respuesta 
                     url: path_principal + '/api/servidumbreexpediente/',//url api
                     parametros:self.expedienteVO                        
                };
                RequestFormData(parametros);

            }else{
                //se utiliza cuando se desea mdificar un registro
                 var parametros={     
                        metodo:'PUT',                
                       callback:function(datos, estado, mensaje){
                            if (estado=='ok') {
                            self.cargar(self.paginacion.pagina_actual());
                            self.limpiar();
                            } 
                       },//funcion para recibir la respuesta 
                     url: path_principal + '/api/servidumbreexpediente/'+ self.expedienteVO.id()+'/',//url api
                     parametros:self.expedienteVO                        
                  };
                  RequestFormData(parametros);
            }

            location.href=self.urlHOME;

        }else{
            $("#validacionProyecto").show();
        }
     }
    
    self.consultar_proyecto = function(obj){
        path =self.url+'Proyecto/'+obj.id+'/?format=json';
        RequestGet(function (results,count) {
            self.proyectoVO.id(results.id);
            self.proyectoVO.nombre(results.nombre);
            self.proyectoVO.municipio_id(results.municipio);
            self.proyectoVO.departamento_id(results.municipio.departamento);
            self.proyectoVO.mcontrato_id(results.mcontrato);            
            cerrarLoading();
        }, path, parameter,undefined,false);

     }         
     
  
    //cerrar los expedientes
    self.cerrar_expedientes = function () {
        var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_expedientes(), function(d) {

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione expedientes.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/servidumbre/cerrar_expedientes/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea cerrar los expedientes seleccionados?", path, parameter, function () {
                 self.cargar(1);
                 self.checkall(false);
             })

         }  
}

    self.Reabrir = function(obj){
       var path =path_principal+'/servidumbre/reabrir/'+obj.id;
             var parameter = {};
             RequestAnularOEliminar("Esta seguro que desea reabrir el expediente seleccionado?", path, parameter, function () {
                 self.cargar(1);
                 self.checkall(false);
             })

         

    }
    self.Cerrar = function(obj){
           var path =path_principal+'/servidumbre/cerrar/'+obj.id;
             var parameter = {};
             RequestAnularOEliminar("Esta seguro que desea cerrar el expediente seleccionado?", path, parameter, function () {
                 self.cargar(1);
                 self.checkall(false);
             })

         

    }

   //funcion para seleccionar los datos a eliminar del detalle del giro
    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_expedientes(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.utilizarProyecto = function (obj) {        
        $("#txtNombreProyecto").val(obj.nombre);
        $("#txtMcontratoProyecto").val(obj.mcontrato);
        $("#txtDepartamentoProyecto").val(obj.departamento);
        $("#txtMunicipioProyecto").val(obj.municipio);
        $('#modal_busqueda_proyecto').modal('hide');
        
        self.expedienteVO.proyecto_id(obj.id);
        self.expedienteVO.usuario_creador_id($('#idUsuario').val());
       
    }
    
    self.consultar_proyectos = function(pagina){
    if (pagina > 0){
      
            path = self.url+'Proyecto/?format=json';
            parameter = {};
            RequestGet(function (datos, estado, mensage) {
                if (datos!=null && datos.length > 0) {
                    self.listado_proyectos(datos); 
                } else {
                    self.listado_proyectos([]);
                }
                cerrarLoading();
            }, path, parameter,undefined,false);
    }    
    }
    
 
    self.paginacionProyecto = {
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

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.cargar(pagina);
    });

    self.limpiar=function(){
        self.expedienteVO.id(0);       
        self.expedienteVO.proyecto_id('');

        //self.expedienteVO.proyecto_id.isModified(false);
    
    }

    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
       // var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
       // self.paginacion.totalRegistrosBuscados(buscados);

    }

     //Funcion para crear la paginacion
    self.llenar_paginacionProyectos = function (data,pagina) {
        self.paginacionProyecto.pagina_actual(pagina);
        self.paginacionProyecto.total(data.count);
        self.paginacionProyecto.cantidad_por_paginas(resultadosPorPagina);

    }
     self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.cargar(1);
        }
        return true;
    }

    self.buscarProyecto = function (d,e) {
        if (e.which == 13) {
            //self.consultar(1);
            self.filtroProyecto($('#txtBuscarProyecto').val());
            self.get_proyecto(1)
        }
        return true;
    }

    self.cargar = function(pagina){

        self.filtro_expedienteVO.dato($('#txtBuscar').val())
        sessionStorage.getItem("app_servidumbre_dato", self.filtro_expedienteVO.dato() || '');
        sessionStorage.getItem("app_servidumbre_proyecto", self.filtro_expedienteVO.proyecto_id() || '');

            path = path_principal+'/api/servidumbreexpediente/?format=json';
            parameter = { dato: self.filtro_expedienteVO.dato(), 
                          page: pagina, 
                          proyecto : self.filtro_expedienteVO.proyecto_id()
            };
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listado_expedientes(agregarOpcionesObservable(datos.data));
                    cerrarLoading();
                } else {
                    self.listado_expedientes([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
                }
                self.llenar_paginacion(datos,pagina);
                

            }, path, parameter,undefined, false);

    }

    self.get_proyecto = function(pagina){        
        //Codigo para consultar los propietarios
        path = path_principal+'/api/Proyecto/?lite=1&format=json&page=' + pagina;;
        if (pagina > 0) {
            //alert('entre aqui' + self.filtroProyecto()); 
            //self.buscado_rapido(true);            
            parameter = {
                dato: self.filtroProyecto(),
                proyectos_post_eca: true,
                servidumbre: true,          
            };
            RequestGet(function(datos, estado, mensage) {
                //alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensajeProyecto('');
                    self.listadoproyectos(datos.data);
                } else {
                    self.listadoproyectos([]);
                    self.mensajeProyecto(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
                }
                
                self.llenar_paginacionProyectos(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        } 
    }

    self.paginacionProyecto.pagina_actual.subscribe(function (pagina) {
        self.get_proyecto(pagina);     
    });

    self.get_proyecto2 = function(){
        self.get_proyecto(1);
    }

    

   

    self.abrir_modal = function () {
        self.titulo('Buscar proyecto'); 
        $('#modal_busqueda_proyecto').modal('show');
        self.get_proyecto(1);
        return true;
    }

     self.eliminar = function () {
        return true;
     }

    self.consultar_por_id = function(obj){
        location.href=sefl.url_funcion+"editarexpediente/"+(obj.id);    
    }
    

    self.exportar_excel=function(){
        location.href=self.url_funcion+"reporte_expedientes/";
    
    
        return true;
        }
    


}


var expedientes= new GestionServidumbreViewModel();

$('#txtBuscar').val(sessionStorage.getItem("app_servidumbre_dato"))   
expedientes.filtro_expedienteVO.proyecto_id(sessionStorage.getItem("app_proyecto_proyecto"));

GestionServidumbreViewModel.errores_expedientes=ko.validation.group(expedientes.expedienteVO);
GestionServidumbreViewModel.errores_proyecto=ko.validation.group(expedientes.proyectoVO);

ko.applyBindings(expedientes);