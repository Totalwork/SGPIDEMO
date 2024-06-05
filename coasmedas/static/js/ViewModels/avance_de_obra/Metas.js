
function MetasViewModel() {
	
	var self = this;
	
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.habilitar_campos=ko.observable(true);
    self.checkall=ko.observable(false);  
    self.numero_tree=ko.observable(1);
    self.peso_total=ko.observable(0);
   // self.url=path_principal+'api/Banco'; 
    self.metaVO=ko.observableArray([]);

    self.id_actividades=ko.observable('');
    self.cantidad_actividades=ko.observable('');   

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

     
   

    self.guardar=function(){            

                self.llenar();
                var parametros={                     
                     callback:function(datos, estado, mensaje){
                        
                        if (estado=='ok') {

                            self.consultar(1);
                        }                        
                        
                     },//funcion para recibir la respuesta 
                     url:path_principal+'/avance_de_obra/guardar_metas_actividades/',//url api
                     parametros:{actividad_id:self.id_actividades(),cantidades:self.cantidad_actividades(),id_cronograma:$("#id_cronograma").val()}                     
                };
                //parameter =ko.toJSON(self.contratistaVO);
                Request(parametros);

     }
    

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/avance_de_obra/listar_metas_actividades/'+$("#id_cronograma").val();
            //parameter = { dato: self.filtro(), pagina: pagina,id_cronograma:$("#id_cronograma").val()};
            parameter=''
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    self.metaVO(self.ordenar(datos)); 

                     $('#modal_acciones').modal('hide');

                } else {
                    self.metaVO([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
            }, path, parameter);
        }


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
                        lista.push(self.llenar_meta(d));
                        ko.utils.arrayForEach(data, function(x) {
                            if(d.id==x.padre){
                                  x.procesar(0);
                                  lista.push(self.llenar_meta(x));
                                  num++;
                                  var valor=num;
                                  ko.utils.arrayForEach(data, function(a) { 
                                        if(x.id==a.padre){
                                            lista[valor].procesar(1);
                                            a.procesar(0);
                                            lista.push(self.llenar_meta(a));
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


    self.llenar_meta=function(obj){

        var lista=[];
         lista.push({
            id:ko.observable(obj.actividad_id==null ? 0 : obj.actividad_id),
            actividad_id:ko.observable(obj.id_act),
            nombre:ko.observable(obj.nombre),
            peso:ko.observable(obj.peso),
            padre:ko.observable(obj.padre),
            nivel:ko.observable(obj.nivel),
            cantidad:ko.observable(obj.cantidad==null ? 0 : obj.cantidad),
            procesar:ko.observable(obj.procesar())
        });
        return lista[0];
    }

    self.llenar=function(){

        self.id_actividades('');
        self.cantidad_actividades('');

        ko.utils.arrayForEach(self.metaVO(), function(d) { 
            
            if(d.procesar()==0){ 
                if(self.id_actividades()==''){
                    self.id_actividades(d['actividad_id']());
                    self.cantidad_actividades(d['cantidad']());
                }else{                    
                    valor1=d['actividad_id']()+','+self.id_actividades();
                    self.id_actividades(valor1);
                    valor2=d['cantidad']()+','+self.cantidad_actividades();
                    self.cantidad_actividades(valor2);
                }  
            }
           
        });
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.limpiar();
            self.consultar(1);
        }
        return true;
    }

 }

var metas = new MetasViewModel();
metas.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(metas,content);
ko.applyBindings(metas,header);