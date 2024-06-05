
function ActividadViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);  
    self.numero_tree=ko.observable(1);
    self.peso_total=ko.observable(0);
   // self.url=path_principal+'api/Banco'; 

    self.actividadVO={
        id:ko.observable(0),
        nombre:ko.observable('').extend({ required: { message: '(*)Digite el nombre del capitulo' } }),
        nivel:ko.observable(0),
        padre:ko.observable(0),
        peso:ko.observable(0).extend({ max: {params:100,message:"(*)Digite un numero minimo de 100"}}).
        extend({ min: {params:0,message:"(*)Digite un numero maximo de 0"}}),
        esquema_id:ko.observable(0)
     };

    self.switch_expandir=ko.observable(0);
    self.titulo_expandir=ko.observable('Expandir todos los capitulos')

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

     self.abrir_modal = function (titulo,nivel,padre) {
        self.limpiar();
        self.titulo('Registrar '+titulo);
        self.actividadVO.nivel(nivel);
        self.actividadVO.padre(padre);
        self.habilitar_campos(true);
        $('#modal_acciones').modal('show');
        
    }

    /*self.getTreegridClass = function(item) {
        alert(self.numero_tree())
        console.log(item)
        var className = '';
        className += 'treegrid-' + self.numero_tree();
        if (item.padre>0){
            className += ' treegrid-parent-' + self.numero_tree();
        }          
        self.numero_tree(self.numero_tree()+1);
        return className;
    }*/

     self.checkall.subscribe(function(value ){

             ko.utils.arrayForEach(self.listado(), function(d) {

                    d.eliminado(value);
             }); 
    });

   

    self.guardar=function(){

        if (ActividadViewModel.errores_actividad().length == 0) {//se activa las validaciones

           // self.contratistaVO.logo($('#archivo')[0].files[0]);
            self.actividadVO.esquema_id($("#id_esquema").val());
            if(self.actividadVO.id()==0){

                var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.filtro("");
                            self.consultar(self.paginacion.pagina_actual());
                            $('#modal_acciones').modal('hide');
                            self.limpiar();
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/api/Esquema_Capitulos_Actividades_avance_obra/',//url api
                     parametros:self.actividadVO                        
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
                        }  

                       },//funcion para recibir la respuesta 
                       url:path_principal+'/api/Esquema_Capitulos_Actividades_avance_obra/'+self.actividadVO.id()+'/',
                       parametros:self.actividadVO                        
                  };

                  Request(parametros);

            }

        } else {
             ActividadViewModel.errores_actividad.showAllMessages();//mostramos las validacion
        }
     }

    //Funcion para crear la paginacion
    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);

    }

   
    // //limpiar el modelo 
     self.limpiar=function(){   
           
           self.actividadVO.id(0);
           self.actividadVO.nombre('');
           self.actividadVO.nivel(0);
           self.actividadVO.padre(0);
           self.actividadVO.peso(0);
           self.filtro(0);
     }


     self.expandir=function(){

        if(self.switch_expandir()==0){
            self.titulo_expandir('Colapsar todos los capitulos');
            $('.tree').treegrid({
              initialState:'expanded' 
            });
            self.switch_expandir(1);
        }else{
            self.titulo_expandir('Expandir todos los capitulos');
            $('.tree').treegrid({
              initialState:'collapsed' 
            });
            self.switch_expandir(0);
        }
        
     }

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/avance_de_obra/listar_esquema_actividades/'+$("#id_esquema").val();
            parameter = {};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.listado(self.ordenar(datos));                    
                    self.titulo_expandir('Expandir todos los capitulos');
                    self.switch_expandir(0);
                     $('.tree').treegrid({
                        initialState:'collapsed' 
                     });

                     $('#modal_acciones').modal('hide');

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                //if ((Math.ceil(parseFloat(results.count) / resultadosPorPagina)) > 1){
                //    $('#paginacion').show();
                //    self.llenar_paginacion(results,pagina);
                //}
            }, path, parameter);
        }


    }

    self.ordenar=function(data){

            var lista=[];
            self.numero_tree(1);
            data=agregarOpcionesObservable(data);
            self.peso_total(0);
            ko.utils.arrayForEach(data, function(d) {
                    var className = '';
                    className = 'treegrid-' + self.numero_tree();
                    if (d.padre==0){                                         
                        self.numero_tree(self.numero_tree()+1);
                        d.valor_generico(className); 
                        lista.push(d);
                        self.peso_total(self.peso_total()+d['peso']);
                        var num=0;
                        d.procesar(num);
                        ko.utils.arrayForEach(data, function(x) {
                            if(d.id==x.padre){
                                  d.procesar(num+1);
                                  num++;
                                  var res = d.valor_generico().split("-");  
                                  className = 'treegrid-'+ self.numero_tree() + ' treegrid-parent-'+res[1];  
                                  self.numero_tree(self.numero_tree()+1);
                                  x.valor_generico(className); 
                                  lista.push(x);
                                  var num2=0;
                                  x.procesar(num2);
                                  ko.utils.arrayForEach(data, function(a) { 
                                        if(x.id==a.padre){
                                            x.procesar(num2+1);
                                            num2++;
                                            var res = x.valor_generico().split("-");  
                                            className = 'treegrid-'+ self.numero_tree() + ' treegrid-parent-'+res[1]; 
                                            self.numero_tree(self.numero_tree()+1);
                                            a.valor_generico(className);
                                            lista.push(a);  
                                        }
                                  });
                            }
                        });
                    }                           
            });
       self.peso_total(parseFloat(self.peso_total()).toFixed(2))
        if(self.peso_total()>100){
            self.peso_total(100);
        }
        return lista;
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

    self.actividad=function(obj){
        
        location.href=path_principal+"/avance_de_obra/actividades/"+obj.id;
    }


    self.consultar_por_id = function (obj) {
       
      // alert(obj.id)
        self.filtro(obj.procesar());
       path =path_principal+'/api/Esquema_Capitulos_Actividades_avance_obra/'+obj.id+'/?format=json';
         RequestGet(function (results,count) {
           
             self.titulo('Actualizar');

             self.actividadVO.id(results.id);
             self.actividadVO.nombre(results.nombre);
             self.actividadVO.peso(results.peso);
             self.actividadVO.padre(results.padre);
             self.actividadVO.nivel(results.nivel);
             self.habilitar_campos(true);
             $('#modal_acciones').modal('show');
         }, path, parameter);

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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un capitulo o actividad para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avance_de_obra/eliminar_id_capitulos_esquema/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los capitulos o las actvidades seleccionados (se borraran las actividades o las subactividades de este capitulo o actvidad)?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    
        
    }





 }

var actividad = new ActividadViewModel();
actividad.consultar(1);//iniciamos la primera funcion
ActividadViewModel.errores_actividad = ko.validation.group(actividad.actividadVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(actividad,content);
ko.applyBindings(actividad,header);