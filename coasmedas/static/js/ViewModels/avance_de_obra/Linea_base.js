
function BaseViewModel() {
	
	var self = this;
	
    
	self.mensaje=ko.observable('');
    self.mensaje_guardando=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);  
    self.numero_tree=ko.observable(1);
    self.peso_total=ko.observable(0);
   // self.url=path_principal+'api/Banco'; 
    self.metaVO=ko.observableArray([]);
    self.header=ko.observableArray([]);
    self.porcentaje=ko.observableArray([]);

    self.activacion=ko.observable(0);

    self.id_actividades=ko.observable('');
    self.cantidad_actividades=ko.observable('');

    self.limite=ko.observable(true);
    self.inicio=ko.observable(true);

    self.lineaVO=ko.observable([]);

    self.tipo_linea=ko.observable(1);

    self.actividadesVO=ko.observable([]);  
    

    self.cantidadVO={
        id_actividad:ko.observable(0).extend({ required: { message: '(*)Seleccione una actividad' }}),
        desde:ko.observable(1).extend({ min: {params:1,message:"(*)Digite un numero maximo de 1"}}),
        hasta:ko.observable(1).extend({ min: {params:1,message:"(*)Digite un numero maximo de 1"}}),
        cantidad:ko.observable(1).extend({ required: { message: '(*)Digite una cantidad' }})
     };

	self.paginacion = {
        pagina_actual: ko.observable(0),
        total: ko.observable(0),
        maxPaginas: ko.observable(4),
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

     
   

    self.guardar=function(){            
       
        if (BaseViewModel.errores_cantidades().length == 0) {//se activa las validaciones
            self.llenar(0);
            var parametros={                     
                     callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                           self.consultar(self.paginacion.pagina_actual()); 
                           $('#modal_acciones').modal('hide');
                           self.limpiar();
                        }                    
                        

                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avance_de_obra/agregar_cantidades/',//url api
                     parametros:{id_actividades:self.id_actividades(),id_actividad:self.cantidadVO.id_actividad(),cantidad:self.cantidadVO.cantidad(),desde:self.cantidadVO.desde(),hasta:self.cantidadVO.hasta(),tipo_linea:self.tipo_linea(),id_cronograma:$("#id_cronograma").val()}                    
                };
                //parameter =ko.toJSON(self.contratistaVO);
            Request(parametros);    
           
        } else {
             BaseViewModel.errores_cantidades.showAllMessages();//mostramos las validacion
        }      

    }


    self.guardar_linea=function(){            

            $.confirm({
                title: 'Confirmacion',
                content: "<h4>¿Esta seguro que desea guardar la linea base, no podra editar la linea base una vez guardada?</h4>",
                confirmButton: 'Si',
                confirmButtonClass: 'btn-info',
                cancelButtonClass: 'btn-danger',
                cancelButton: 'No',
                confirm: function() {

                    var parametros={                     
                         callback:function(datos, estado, mensaje){

                            if (estado=='ok') {
                               location.href=path_principal+"/avance_de_obra/linea_base/"+$("#id_cronograma").val()+"/"+$("#id_proyecto").val();

                            }                        
                            
                         },//funcion para recibir la respuesta 
                         url:path_principal+'/avance_de_obra/guardar_linea_base/',//url api
                         parametros:{id_cronograma:$("#id_cronograma").val()}                    
                    };
                    //parameter =ko.toJSON(self.contratistaVO);
                    Request(parametros);   
                }
            });       

     }


     self.limpiar=function(){

        self.cantidadVO.cantidad(0);
        self.cantidadVO.id_actividad(0);
        self.cantidadVO.desde(0);
        self.cantidadVO.hasta(0);
     }
    

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro(0);
            path = path_principal+'/avance_de_obra/listar_linea_base/'+$("#id_cronograma").val()+'/'+pagina+'/'+self.tipo_linea()+'/'+self.filtro();
            //parameter = { dato: self.filtro(), pagina: pagina,id_cronograma:$("#id_cronograma").val()};
            parameter=''
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok') {
                        self.mensaje('');
                        //self.listado(results);
                        self.header([]);
                        self.metaVO([]);
                        self.header(datos.header);
                        self.porcentaje(datos.porcentajes);
                        self.metaVO(self.ordenar(datos.result));
                        self.actividadesVO(self.llenar_actividades());
                        self.paginacion.pagina_actual(pagina);
                        self.paginacion.cantidad_por_paginas(datos.result[0]['cant']);
                        var valor=Math.ceil(self.paginacion.cantidad_por_paginas()/self.paginacion.maxPaginas());
                       
                        if(self.paginacion.pagina_actual()==(valor-1)){
                            self.limite(false);
                        }else{
                            self.limite(true);
                        }
                        if(self.paginacion.pagina_actual()==0){
                            self.inicio(false);
                        }else{
                            self.inicio(true);
                        }
                } else {
                    self.metaVO([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
            }, path, parameter);


    }

    self.abrir_modal = function () {
        self.titulo('Registrar Cantidad');
        self.limpiar();
        $('#modal_acciones').modal('show');
        
    }



    self.activacion_intervalo=function(obj){
        if($('#linea_base').val()=='False'){
            if (self.activacion()>0){
                self.llenar(self.activacion());

                 var parametros={                     
                         callback:function(datos, estado, mensaje){
                            self.mensaje_guardando('');
                            if (estado=='ok') {
                               self.consultar(self.paginacion.pagina_actual()); 
                               if(self.activacion()==obj){
                                self.activacion(0);
                               }else{
                                self.activacion(obj);
                               }
                               self.mensaje_guardando('<div class="alert alert-success alert-dismissable"><i class="fa fa-check"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>'+mensaje+'</div>');
                               
                            }else{
                                console.log(0);
                               self.mensaje_guardando('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>'+mensaje+'</div>');
                            }                        
                            
                         },//funcion para recibir la respuesta 
                         alerta:false,
                         url:path_principal+'/avance_de_obra/actualizar_intervalos_linea/',//url api
                         parametros:{id_actividades:self.id_actividades(),cantidad_actividades:self.cantidad_actividades(),intervalo_id:self.buscar_id_intervalo(self.activacion()),tipo_linea:self.tipo_linea(),id_cronograma:$("#id_cronograma").val()}                    
                    };
                    //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);          

            }else{
                self.activacion(obj);
            }
        }
    }


    self.guardar_intervalo=function(){

        if($('#linea_base').val()=='False'){
            if (self.activacion()>0){

                self.llenar(self.activacion());
                self.mensaje_guardando('');
                 var parametros={                     
                         callback:function(datos, estado, mensaje){
                            self.mensaje_guardando('');
                            if (estado=='ok') {
                               self.mensaje_guardando('<div class="alert alert-success alert-dismissable"><i class="fa fa-check"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>'+mensaje+'</div>');
                               
                            }else{
                               self.mensaje_guardando('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i><button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>'+mensaje+'</div>');
                            }                        
                            
                         },//funcion para recibir la respuesta 
                         alerta:false,
                         url:path_principal+'/avance_de_obra/actualizar_intervalos_linea/',//url api
                         parametros:{id_actividades:self.id_actividades(),cantidad_actividades:self.cantidad_actividades(),intervalo_id:self.buscar_id_intervalo(self.activacion()),tipo_linea:self.tipo_linea(),id_cronograma:$("#id_cronograma").val()}                    
                    };
                    //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros); 

            }

        }
    }


    self.llenar_actividades=function(){

        var lista=[];
        ko.utils.arrayForEach(self.metaVO(), function(d) { 
            
            if(d.procesar()==0){ 
                lista.push({
                    'id':d['actividad_id'](),
                    'nombre':d['nombre']()
                })
            }
           
        });

        return lista;
    }

    self.llenar=function(valor){

        var lista=[];
        self.id_actividades('');
        self.cantidad_actividades('');
        if(valor>0){
            var id=self.buscar_id_intervalo(valor);
        }
        ko.utils.arrayForEach(self.metaVO(), function(d) { 
            
            if(d.procesar()==0){ 
                if(self.id_actividades()==''){
                    self.id_actividades(d['actividad_id']());
                    if(valor>0){
                        self.cantidad_actividades(d[valor]());
                    }
                }else{                    
                    valor1=d['actividad_id']()+','+self.id_actividades();
                    self.id_actividades(valor1);
                    if(valor>0){
                         valor2=d[valor]()+','+self.cantidad_actividades();
                         self.cantidad_actividades(valor2);
                    }
                   
                }
            }
           
        });
    }

    self.buscar_id_intervalo=function(valor){

        var id=0;
        ko.utils.arrayForEach(self.porcentaje(), function(d) {
            
            if(d['intervalo']==valor){
                id=d['id_intervalo'];
            }         
        });

        return id;
    }


    self.paginacion_anterior=function(){
        
        if(self.paginacion.pagina_actual()>0){
            self.guardar_intervalo();
            self.activacion(0);
            self.paginacion.pagina_actual(self.paginacion.pagina_actual()-1);
            self.consultar(self.paginacion.pagina_actual())
        }
    }


    self.paginacion_siguiente=function(){
        var cant=Math.ceil(self.paginacion.cantidad_por_paginas()/self.paginacion.maxPaginas());
        
        if(self.paginacion.pagina_actual()<cant-1){
            self.guardar_intervalo();
            self.activacion(0);
            self.paginacion.pagina_actual(self.paginacion.pagina_actual()+1);
            self.consultar(self.paginacion.pagina_actual())
        }
    }

    self.paginacion_final=function(){
        var cant=Math.ceil(self.paginacion.cantidad_por_paginas()/self.paginacion.maxPaginas());
        self.guardar_intervalo();
        self.activacion(0);
        self.consultar(cant-1)
    }

    self.paginacion_inicio=function(){
        self.guardar_intervalo();
        self.activacion(0);
        self.consultar(0);
    }

    self.ordenar=function(data){

            var lista=[];
            data=agregarOpcionesObservable(data);
            self.peso_total(0);
            num=0;
            ko.utils.arrayForEach(data, function(d) {

                    if (d.padre==0){ 
                        self.peso_total(self.peso_total()+d['peso']);
                        d.procesar(1);
                        lista.push(convertToObservable(d));
                        ko.utils.arrayForEach(data, function(x) {
                            if(d.id==x.padre){
                                  x.procesar(0);
                                  lista.push(convertToObservable(x));
                                  num++;
                                  var valor=num;
                                  ko.utils.arrayForEach(data, function(a) { 
                                        if(x.id==a.padre){
                                            lista[valor].procesar(1);
                                            a.procesar(0);
                                            lista.push(convertToObservable(a));
                                            num++;
                                        }
                                  });
                            }
                        });                        
                        num++;
                    }                         
            });
        return lista;
    }


    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            if(self.filtro()!=''){
                var x=0
                var cont=1
                var sw=0;
                var cant=Math.ceil(self.paginacion.cantidad_por_paginas()/self.paginacion.maxPaginas());
                while(x<cant){
                    if(self.filtro()>=cont && self.filtro()<cont+4 && self.filtro()<=self.paginacion.cantidad_por_paginas()){
                        self.consultar(x);
                        sw=1;
                        return true;
                    }
                    cont=cont+4;
                    x++;
                }

                if(sw==0){
                    $.confirm({
                        title: 'Advertencia',
                        content: '<h4><i class="text-warning fa fa-exclamation-triangle fa-2x"></i>No se encontraron registros con ese intervalo<h4>',
                        cancelButton: 'Cerrar',
                        confirmButton: false
                    });
                }
            }else{
                self.consultar(0);
            }
        }
        return true;
    }

 }

var base = new BaseViewModel();
BaseViewModel.errores_cantidades = ko.validation.group(base.cantidadVO);
base.consultar(0);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(base,content);
ko.applyBindings(base,header);