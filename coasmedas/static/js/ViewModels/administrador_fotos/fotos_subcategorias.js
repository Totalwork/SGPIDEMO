

function FotosSubcategoriaViewModel() {
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);

    self.archivo1=ko.observable('');
    self.archivo2=ko.observable('');
    self.valida_foto=ko.observable(0);
    self.vali_fot=ko.observable(0);
    self.focus_validar_foto=ko.observable('');

    //var num=0;
    //self.url=path_principal+'api/empresa'; 

     //Representa un modelo de las fotos subcategorias
    self.fotosSubcategoriaVO={
        id:ko.observable(0),
        ruta:ko.observable('').extend({ required: { message: '(*)Seleccione el archivo' } }),
        subcategoria_id:ko.observable(0),
        mes:ko.observable(0).extend({ required: { message: '(*)Seleccione el mes' } }),
        ano:ko.observable(new Date().getFullYear()).extend({ required: { message: '(*)Digite el año' } }),

     };

     //paginacion de la fotos subcategoria
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

    //paginacion
    self.paginacion.pagina_actual.subscribe(function (pagina) {
        self.consultar(pagina);
    });


    //Funcion para crear la paginacion 
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

  
    //funcion para seleccionar los datos a eliminar
    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.listado(), function(d) {

            d.eliminado(value);
        }); 
    });

    //funcion para abrir modal de registrar fotos subcategorias
    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Subcategoria');
        $('#modal_acciones').modal('show');
    }


     //limpiar el modelo de la fotos subcategoria
     self.limpiar=function(){     
         
        self.fotosSubcategoriaVO.id(0);
        //self.fotosSubcategoriaVO.subcategoria_id(0);
        self.fotosSubcategoriaVO.ruta('');
        self.archivo1('');
        self.archivo2('');
        self.fotosSubcategoriaVO.mes(0);
        self.fotosSubcategoriaVO.ano(new Date().getFullYear());
        self.vali_fot(0);

        //self.fotosSubcategoriaVO.fecha.isModified(false);
        $('#archivo, #archivo2').fileinput('reset');
        $('#archivo, #archivo2').val('');
      
     }


    //funcion para exportar a excel las fotos subcategorias
    self.exportar_excel = function (obj) {
        //self.titulo('Generar informe');
        //$('#generar_informe').modal('show');
    }


    //funcion guardar las fotos subcategoria
     self.guardar=function(){

        //if (FotosSubcategoriaViewModel.errores().length == 0) {//se activa las validaciones

            var data = new FormData();

            var subcategoria=self.fotosSubcategoriaVO.subcategoria_id();
            //var mes=self.vali_fot();
            mes=self.fotosSubcategoriaVO.mes();


            if (mes=='' && self.fotosSubcategoriaVO.ano()=='') {

                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe digitar el mes y el año.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
                return false
            }

            if($("#archivo").val()!=undefined && $("#archivo2").val()!=undefined){

                if ($("#archivo").val()=='' && $("#archivo2").val()=='') {

                    $.confirm({
                        title:'Informativo',
                        content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Debe cargar las fotos.<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });
                    return false
                }
             }

            data.append('subcategoria_id',subcategoria);
            data.append('mes',mes);
            data.append('ano',self.fotosSubcategoriaVO.ano());

            if($("#archivo").val()!=undefined){
                data.append('archivo[]', $('#archivo')[0].files[0]);
            }

            data.append('archivo[]', $('#archivo2')[0].files[0]);


            var parametros={                     
                callback:function(datos, estado, mensaje){

                    if (estado=='ok') {
                        self.filtro("");
                        self.limpiar();
                        self.consultar(self.paginacion.pagina_actual());
                        $('#modal_acciones').modal('hide');
                    }                        
                            
                },//funcion para recibir la respuesta 
                    url:path_principal+'/api/fotos_subcategoria/',//url api
                    parametros:data,
                    completado:function(){
                        //self.encabezado();
                    }                          
            };
            RequestFormData2(parametros);

        // } else {
        //      FotosSubcategoriaViewModel.errores.showAllMessages();//mostramos las validacion
        // } 
    }


    //funcion consultar las fotos subcategorias
    self.consultar = function (pagina) {
        
        if (pagina > 0) {            

            self.filtro($('#txtBuscar').val());
            var subcategoria=self.fotosSubcategoriaVO.subcategoria_id();
            var tipo_contrato='8';

           path = path_principal+'/api/fotos_subcategoria/?format=json';
            parameter = { dato: self.filtro(), page: pagina, subcategoria_id:subcategoria};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(agregarOpcionesObservable(datos.data));  
                    //console.log(datos.data)
                    self.validaFoto();
                    cerrarLoading();

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    cerrarLoading();
                }

                self.llenar_paginacion(datos,pagina);

            }, path, parameter,undefined, false);
        }
    }


   
    //eliminar las fotos subcategorias
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione las fotos de las subcategorias para la eliminación.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/administrador_fotos/eliminar_fotos_subcategoria/';
             var parameter = { lista: lista_id };
             RequestAnularOEliminar("Esta seguro que desea eliminar las fotos de las subcategorias seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
                 self.validaFoto();
             })

         }     
    
        
    }


    //funcion que se ejecuta cuando se cambia en el select de mes
    self.fotosSubcategoriaVO.mes.subscribe(function (value) {

        //alert(value)
        if(value >0){
            self.validaFoto(value);

        }else{
           self.valida_foto(0); 
        }

    });


    self.focus_validar_foto.subscribe(function(newValue) {

            if(newValue==false){
                self.validaFoto();
            }
    });


    //consultar la cantidad de fotos
    self.validaFoto=function(mes){
        
        //var subcategoria=self.fotosSubcategoriaVO.subcategoria_id();
        var subcategoria=$("#id_subcategoria").val();
        var ano=self.fotosSubcategoriaVO.ano();

        path =path_principal+'/api/fotos_subcategoria/?sin_paginacion&format=json';
        parameter = {subcategoria_id:subcategoria,mes:mes,ano:ano};
        RequestGet(function (datos, estado, mensaje) {

            if (datos !='') {

                self.valida_foto(datos[0].cantidad_fotosSubcategoria);

            }else{

                self.valida_foto(0);
            } 

        }, path, parameter);

    }


}

var fotosSubcategoria = new FotosSubcategoriaViewModel();
FotosSubcategoriaViewModel.errores = ko.validation.group(fotosSubcategoria.fotosSubcategoriaVO);
ko.applyBindings(fotosSubcategoria);

