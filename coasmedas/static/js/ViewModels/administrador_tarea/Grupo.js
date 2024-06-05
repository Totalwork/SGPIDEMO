function GrupoViewModel() {
	
	var self = this;
    var lista_id_estado='';
        
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

    self.listado_tarea=ko.observableArray([]);
    self.valor_total=ko.observable(0);

    self.listado_usuarios=ko.observableArray([]);
    self.filtro_usuario=ko.observable('');
    self.id_empresa=ko.observable(0);
    self.checkall2=ko.observable(false);
    self.mensaje_guardando=ko.observable('');

    self.mensaje_usuario=ko.observable('');
    self.mensaje_guardando_usuario=ko.observable('');
    self.equipo_id=ko.observable(0);


    self.filtro_equipo=ko.observable('');
    self.filtro_tarea=ko.observable('');

    self.nombre_tarea=ko.observable('');
    self.listado_soporte=ko.observableArray([]);
    self.mensaje_soporte=ko.observable('');

    self.listado_colaboradores=ko.observableArray([]);
    self.mensaje_colaborador=ko.observable('');
    self.filtro_colaborador=ko.observable('');

    self.listado_estado=ko.observableArray([]);
    self.checkall3=ko.observable(false);
    self.listado_filter_colaboradores=ko.observableArray([]);
    self.checkall_coalboradores=ko.observable(false);

    self.filterVO={
        desde:ko.observable(''),
        hasta:ko.observable(''),
        equipo_id:ko.observable(0),
        colaborador_id:ko.observable(0)
    }

    self.grupoVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del grupo' } }),
        descripcion:ko.observable('').extend({ required: { message: '(*)Digite la descripcion del grupo' } }),
        usuario_administrador_id:ko.observable('').extend({ required: { message: '(*)Digite una fecha fin de la tarea' } }),
        usuario_responsable_id:ko.observable(0)
    }

    self.lista_macrocontrato=ko.observableArray([]);
    self.id_macrocontrato=ko.observable(0);
    self.listado_contratista=ko.observableArray([]);
    self.id_contratista=ko.observable(0);
    self.listado_departamento=ko.observableArray([]);
    self.id_departamento=ko.observable(0);
    self.listado_municipio=ko.observableArray([]);
    self.id_municipio=ko.observable(0);
    self.listado_proyectos=ko.observableArray([])
    self.id_proyecto=ko.observableArray([]);

    self.tareaVO={
        id:ko.observable(0),
        asunto:ko.observable('').extend({ required: { message: '(*)Digite el asunto de la tarea' } }),
        descripcion:ko.observable(''),
        fecha_fin:ko.observable('').extend({ required: { message: '(*)Digite una fecha fin de la tarea' } }),
        colaborador_actual_id:ko.observable(0),
        numero:ko.observable(0),
        tipo_tarea_id:ko.observable(1),
        usuario_responsable_id:ko.observable(0),
        comentario:ko.observable(''),
        listado_archivo:ko.observableArray([{
            'soporte':ko.observable('')
        }]),        
        listado_proyectos:ko.observableArray([]),
        listado_colaboradores:ko.observableArray([])     
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

    self.paginacion_colaboradores = {
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

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Equipo');
        $('#modal_acciones').modal('show');
    }

    self.abrir_modal_colaborador = function (obj) {
        self.limpiar_colaborador();
        self.equipo_id(obj.id);
        self.consultar_colaboradores(1);
        self.titulo('Registrar/Consultar Colaboradores');
        $('#modal_colaborador').modal('show');
    }

    self.abrir_modal_soporte = function (obj) {
        self.mensaje_soporte('');
        self.checkall(false);
        self.titulo('Folder de Archivo');
        self.nombre_tarea(obj.asunto);

        path = path_principal+'/api/SoporteAsignacionTarea/?format=json&sin_paginacion';
        parameter = {tarea_id:obj.id};
        RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado_soporte(agregarOpcionesObservable(datos));

                } else {
                    self.listado_soporte([]);
                    self.mensaje_soporte('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron registros</div>');
                    
                    //self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                

                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
        }, path, parameter);
        $('#modal_soportes').modal('show');
    }

    self.abrir_modal_usuario = function () {
        self.limpiar();
        $('#modal_usuario').modal('show');
    }

    self.abrir_modal_tarea = function (obj) {
        self.tareaVO.colaborador_actual_id(obj.id);
        $('#modal_tarea').modal('show');
    }

    self.abrir_detalle_tarea = function (obj) {
        location.href=path_principal+"/administrador_tarea/detalle_tarea/"+obj.id;
    }

    self.limpiar_filtro=function(){
        self.filterVO.desde('');
        self.filterVO.hasta('');
        self.filterVO.equipo_id(0);
        self.filterVO.colaborador_id(0);
        lista_id_estado='';
        self.checkall3(false);
        self.filtro_tarea('');
        $('#txtBuscar4').val('');
        self.consultar(1);
    }

    self.abrir_modal_filtro = function (obj) {
        self.titulo('Filtro');
        $('#modal_filter').modal('show');
    }

    self.agregar_soporte=function(){
        self.tareaVO.listado_archivo.push({'soporte':ko.observable('')});
    }

    self.eliminar_soporte=function(val){
        self.tareaVO.listado_archivo.remove(val);
    }


    self.archivo_zip=function(){
        var cont=0;
        listado_id="";
        ko.utils.arrayForEach(self.listado_soporte(), function(d) {

                if(d.eliminado()==true){
                    if(listado_id==""){
                        listado_id=d.id;
                    }else{
                        listado_id=listado_id+","+d.id;
                    }
                    cont++;
                }
        }); 

        if(cont==0){
            self.mensaje_soporte('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>Seleccione un archivo para descargar.</div>');
            return true;
        }

        window.open(path_principal+"/administrador_tarea/download_zip?archivo="+ listado_id,'_blank');
    }

    self.guardar_tarea=function(){

         if (GrupoViewModel.errores_tarea().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            self.tareaVO.usuario_responsable_id($("#id_usuario").val());
            lista_id='';

            ko.utils.arrayForEach(self.tareaVO.listado_proyectos(), function(d) {

                if(lista_id==''){
                   lista_id=d.id;
                }else{
                    lista_id=lista_id+','+d.id;
                }
            });  
            var data = new FormData();
            data.append('usuario_responsable_id',self.tareaVO.usuario_responsable_id());
            data.append('asunto',self.tareaVO.asunto());
            data.append('descripcion',self.tareaVO.descripcion());
            data.append('fecha_fin',self.tareaVO.fecha_fin());
            data.append('colaborador_actual_id',self.tareaVO.colaborador_actual_id());
            data.append('numero',self.tareaVO.numero());
            data.append('tipo_tarea_id',self.tareaVO.tipo_tarea_id());
            data.append('usuario_responsable_id',self.tareaVO.usuario_responsable_id());
            data.append('comentario',self.tareaVO.comentario());
            data.append('lista_proyecto',lista_id);
            data.append('listado_colaboradores', ko.toJSON(self.tareaVO.listado_colaboradores()));

            ko.utils.arrayForEach(self.tareaVO.listado_archivo(), function(d) {

                    if(d.soporte()!=''){
                         data.append('soporte[]',d.soporte());
                    }
             }); 

            if(self.tareaVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            //self.filtro("");
                            //self.consultar(self.paginacion.pagina_actual());
                            $('#modal_tarea').modal('hide');
                            self.consultar_colaboradores(1);
                            self.consultar(1);
                            self.limpiar_tarea();
                            //self.limpiar();
                        }  
                                              
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Tarea/',//url api
                     parametros:data                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                RequestFormData2(parametros);
            }

        } else {
             GrupoViewModel.errores_tarea.showAllMessages();//mostramos las validacion
        }

    }


    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }


    self.llenar_paginacion_colaborador = function (data,pagina) {

        self.paginacion_colaboradores.pagina_actual(pagina);
        self.paginacion_colaboradores.total(data.count);       
        self.paginacion_colaboradores.cantidad_por_paginas(resultadosPorPagina);

    }


    self.llenar_paginacion_usuario = function (data,pagina) {

        self.paginacion_usuario.pagina_actual(pagina);
        self.paginacion_usuario.total(data.count);       
        self.paginacion_usuario.cantidad_por_paginas(resultadosPorPagina);

    }



     self.limpiar=function(){ 

        self.grupoVO.id(0);
        self.grupoVO.nombre('');
        self.grupoVO.descripcion('');
        self.grupoVO.usuario_administrador_id(0);
        self.grupoVO.usuario_responsable_id(0);
        self.checkall2(false);
        $('#txtBuscar2').val('');
        self.filtro_usuario('');

     }

     self.limpiar_tarea=function(){ 

        self.tareaVO.id(0);
        self.tareaVO.asunto('');
        self.tareaVO.descripcion('');
        self.tareaVO.fecha_fin('');
        self.tareaVO.colaborador_actual_id(0);
        self.tareaVO.numero(0);
        self.tareaVO.tipo_tarea_id(1);
        self.tareaVO.usuario_responsable_id(0);
        self.tareaVO.listado_archivo([]);
        self.tareaVO.listado_archivo([{
            'soporte':ko.observable('')
        }]);
        self.tareaVO.listado_proyectos([]);
        self.id_macrocontrato(0);
        self.id_contratista(0);
        self.id_departamento(0);
        self.id_municipio(0);
        self.tareaVO.comentario('');

     }

     self.limpiar_colaborador=function(){ 

        self.filtro_colaborador('');
        $('#txtBuscar3').val('');
        self.listado_colaboradores([]);
        self.equipo_id(0);

     }


    self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_soporte(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.checkall2.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_usuarios(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.checkall3.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado_estado(), function(d) {

                    d.eliminado(value);
             }); 
    });

    self.filterVO.equipo_id.subscribe(function(value ){

            if(value>0){
                path = path_principal+'/api/ColaboradorTarea?format=json&sin_paginacion';
                parameter = {equipo_id:value};
                    RequestGet(function (datos, estado, mensage) {

                        if (estado == 'ok' && datos!=null && datos.length > 0) {                    
                            self.listado_filter_colaboradores(datos);
                        } else {
                            self.listado_filter_colaboradores([]);
                        }

                        
                    }, path, parameter,undefined, false,false);
            }else{
                self.listado_filter_colaboradores([]);
            }
    });


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
            }, path, parameter,undefined, false,false);
        }

    }


    self.consultar_colaboradores=function(pagina){

        if (pagina > 0) {                         
            self.filtro_colaborador($('#txtBuscar3').val());
            path = path_principal+'/api/ColaboradorTarea/?format=json&page='+pagina;
            parameter = {'equipo_id':self.equipo_id(),pagina:pagina,dato:self.filtro_colaborador()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje_colaborador('');
                    //self.listado(results); 
                    self.listado_colaboradores(agregarOpcionesObservable(datos.data));

                } else {
                    self.mensaje_colaborador('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron registros</div>');
                    self.listado_colaboradores([]);
                }

                self.llenar_paginacion_colaborador(datos,pagina);
                
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
                cerrarLoading();
            }, path, parameter,undefined, false);
        }

    }

     self.consultar_macrocontrato=function(){
        
         // path =path_principal+'/proyecto/filtrar_proyectos/?tipo=2';
         path =path_principal+'/proyecto/filtrar_proyectos/?tipo=12';
         parameter='';
         RequestGet(function (results,count) {
           
            self.lista_macrocontrato(results.macrocontrato);

         }, path, parameter,undefined, false,false);
         // $('#loading').hide();
    }

    self.id_macrocontrato.subscribe(function(value){

        var tipo='12';
        if(value!=0){

            path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+value+'&tipo='+tipo;
            parameter = '';
            RequestGet(function (datos, estado, mensage) {
                
                if (estado=='ok') {
                    self.listado_contratista(datos.contratista);
                    self.listado_departamento(datos.departamento);
                    self.listado_municipio(datos.municipio);
                    self.consultar_proyecto();

                }
            }, path, parameter,undefined, false,false);
        }else{
            self.listado_contratista([]);
            self.consultar_departamento();
            self.listado_municipio([]);
            self.listado_proyectos([]);
        }

    });

 

    self.id_departamento.subscribe(function(value){


        if(value!=0){

            if(self.id_macrocontrato()>0 || self.id_contratista()>0){                

                path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+self.id_macrocontrato()+'&contratista='+self.id_contratista()+'&departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                        self.listado_municipio(datos.municipio);
                        self.consultar_proyecto();
                }, path, parameter);
            }else{
                path = path_principal+'/api/Municipio/?ignorePagination&id_departamento='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                    self.listado_municipio(datos);
                    self.consultar_proyecto();
                }, path, parameter,undefined, false,false);
            }
        }

    });


    self.id_contratista.subscribe(function(value){


        if(value!=0){
                path = path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+self.id_macrocontrato()+'&contratista='+value;
                parameter = '';
                RequestGet(function (datos, estado, mensage) {

                        self.listado_departamento(datos.departamento);
                        self.listado_municipio(datos.municipio);
                        self.consultar_proyecto();

                }, path, parameter,undefined, false,false);
           
        }

    });


    self.id_municipio.subscribe(function(value){


        if(value!=0){
            
           self.consultar_proyecto();
        }

    });


    self.consultar_proyecto=function(){

        path = path_principal+'/api/Proyecto/?format=json&ignorePagination';
        parameter = {departamento_id:self.id_departamento(),municipio_id:self.id_municipio(),
            contrato:self.id_macrocontrato(), id_contratista:self.id_contratista()};
        RequestGet(function (datos, estado, mensage) {
            self.listado_proyectos(datos);
        }, path, parameter,undefined, false,false);
    }


     self.consultar_departamento=function(){

            path = path_principal+'/api/departamento/?ignorePagination';
            parameter = '';
            RequestGet(function (datos, estado, mensage) {

                if (datos.length > 0) {
                    self.listado_departamento(datos);
                }
            }, path, parameter,undefined, false,false);
    }

    //guardar la lista de proyectos

    self.addProyectos=function(){

        if(self.id_proyecto()>0){
            var sel = document.forms['frmactividad'].elements['proyecto'];
            var nombre = sel.options[sel.selectedIndex].text;
            sw=0;
            ko.utils.arrayForEach(self.tareaVO.listado_proyectos(), function(d) {

                if(d.id==self.id_proyecto()){
                   sw=1;
                }
            });            

            if(sw==0){
                 self.tareaVO.listado_proyectos.push({
                        id:self.id_proyecto(),
                        nombre:nombre
                     });
            }   
        }
                 
      };


    self.deleteProyectos=function(value){
        self.tareaVO.listado_proyectos.remove(value);
    }


    self.guardar=function(){

         if (GrupoViewModel.errores_grupos().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            self.grupoVO.usuario_responsable_id($("#id_usuario").val());

          
            if(self.grupoVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                        
                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/EquipoTarea/',//url api
                     parametros:self.grupoVO                        
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);
            }
            // }else{

                 
            //       var parametros={     
            //             metodo:'PUT',                
            //            callback:function(datos, estado, mensaje){

            //             if (estado=='ok') {
            //               self.filtro("");
            //               self.consultar(self.paginacion.pagina_actual());
            //               $('#modal_acciones').modal('hide');
            //               self.limpiar();
            //             }  

            //            },//funcion para recibir la respuesta 
            //            url:path_principal+'/api/Actividad_avance_obra/'+self.actividadVO.id()+'/',
            //            parametros:self.actividadVO                        
            //       };

            //       Request(parametros);

            // }

        } else {
             GrupoViewModel.errores_grupos.showAllMessages();//mostramos las validacion
        }

    }


    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro_tarea($('#txtBuscar4').val());
            self.filtro_equipo($('#txtBuscar5').val());

            sessionStorage.setItem("filtro_equipo",self.filtro_equipo() || '');
            sessionStorage.setItem("filtro_tarea",self.filtro_tarea() || '');

            path = path_principal+'/administrador_tarea/listado_grupo';
            parameter = {filtro_equipo:self.filtro_equipo(),filtro_tarea:self.filtro_tarea(),
                pagina:pagina,lista_id:lista_id_estado,equipo_id:self.filterVO.equipo_id(),
                colaborador_id:self.filterVO.colaborador_id(),fecha_inicio:self.filterVO.desde(),
                fecha_final:self.filterVO.hasta()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.Equipos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data.Equipos));
                    self.listado_tarea(agregarOpcionesObservable(datos.data.Tareas));
                    self.valor_total(datos.data.valor_total);
                    $('#modal_acciones').modal('hide');
                    $('#modal_filter').modal('hide');
                    if(datos.data.Tareas.length==0){
                        self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    }

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}

                cerrarLoading();
            }, path, parameter,undefined, false);
        }


    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    self.paginacion_colaboradores.pagina_actual.subscribe(function (pagina) {
        self.consultar_colaboradores(pagina);
    });

    self.paginacion_usuario.pagina_actual.subscribe(function (pagina) {
        self.consultar_usuario(pagina);
    });


    self.id_empresa.subscribe(function (valor) {
            if(valor>0){
                self.filtro_usuario($('#txtBuscar2').val());
                self.consultar_usuario(1);
            }else{
               self.filtro_usuario($('#txtBuscar2').val());
               self.consultar_usuario(1); 
            }
    });


    self.guardar_usuario=function(){
        self.mensaje_guardando_usuario('');
        var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado_usuarios(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                   lista_id.push({
                        id:d.id
                   })
                }
         });

          if(count==0){
            self.mensaje_guardando_usuario('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>Seleccione un usuario.</div>');

         }else{
             var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultar_colaboradores(1);
                            self.mensaje_guardando_usuario('<div class="alert alert-success alert-dismissable"><i class="fa fa-check"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>'+mensaje+'</div>');
                        }else{
                            self.mensaje_guardando_usuario('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>'+mensaje+'</div>');
                        }  
                                              
                        
                     },//funcion para recibir la respuesta 
                     alerta:false,
                     url:path_principal+'/administrador_tarea/guardar_colaboradores/',//url api
                     parametros:{lista:lista_id,equipo_id:self.equipo_id()}                       
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

         }  
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.limpiar();
            self.consultar(1);
        }
        return true;
    }


     self.consulta_enter_usuario = function (d,e) {
        if (e.which == 13) {
            self.consultar_usuario(1);
        }
        return true;
    }
   
   self.consulta_enter_colaborador = function (d,e) {
        if (e.which == 13) {
            self.consultar_colaboradores(1);
        }
        return true;
    }

    self.consulta_enter_equipo = function (d,e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }

    self.consultar_estado=function(){
        path = path_principal+'/api/Estados?format=json&ignorePagination';
        parameter = {aplicacion:'Tarea'};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {                    
                    self.listado_estado(agregarOpcionesObservable(datos));
                } else {
                    self.listado_estado([]);
                }
                
            }, path, parameter,undefined, false,false);
    }


    self.consultar_filtro=function(){

        lista_id_estado='';        
        var count=0;
        ko.utils.arrayForEach(self.listado_estado(), function(d) {

                if(d.eliminado()==true){
                    count=1;
                    if(lista_id_estado!=''){                        
                        lista_id_estado=lista_id_estado+','+d.id;
                    }else{
                        lista_id_estado=d.id;
                    }
                }
         });
        self.consultar(1);

    }

    self.checkall_coalboradores.subscribe(function(val){
        ko.utils.arrayForEach(self.listado_colaboradores(), function(item){
            item.procesar(val);
        });
    });

    self.abrir_modal_tarea_grupal = function () {
        // self.tareaVO.colaborador_actual_id(obj.id);
        ko.utils.arrayForEach(self.listado_colaboradores(), function(item){
            if (item.procesar()) {
                self.tareaVO.listado_colaboradores.push(item.id);
            }
        });
        self.mensaje_colaborador('');
        if (self.tareaVO.listado_colaboradores().length > 0){
            $('#modal_tarea').modal('show');    
        } else {
            self.mensaje_colaborador('<div class="alert alert-warning alert-dismissable"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button><i class="fa fa-warning"></i>Porfavor seleccione los colabores.</div>');
        }
        
    }

 }

var grupo = new GrupoViewModel();

$('#txtBuscar4').val(sessionStorage.getItem("filtro_tarea"));
$('#txtBuscar5').val(sessionStorage.getItem("filtro_equipo"));

grupo.consultar(1);//iniciamos la primera funcion
grupo.consultar_usuario(1);
grupo.consultar_estado();
grupo.consultar_macrocontrato();
GrupoViewModel.errores_tarea = ko.validation.group(grupo.tareaVO);
GrupoViewModel.errores_grupos = ko.validation.group(grupo.grupoVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(grupo,content);
ko.applyBindings(grupo,header);