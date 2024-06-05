
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



    

    //funcion consultar de tipo get recibe un parametro
    self.consultar = function (pagina) {
        if (pagina > 0) {            
            //path = 'http://52.25.142.170:100/api/consultar_persona?page='+pagina;
            self.filtro($('#txtBuscar').val());
            path = path_principal+'/api/avanceObraGraficoDetallePresupuesto/?format=json&sin_paginacion';
            parameter = { presupuesto_id:$("#id_presupuesto").val()};
            //parameter=''
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    self.mensaje('');
                    //self.listado(results); 
                    var lista=self.buscar_padres(datos);

                    self.peso_total(0);

                    ko.utils.arrayForEach(lista, function(d) {

                                path =path_principal+'/api/avanceObraGraficoEsquemaCapitulosActividades/'+d.id+'/?format=json';
                                RequestGet(function (results,count) {

                                    self.metaVO.push({
                                        nombre:ko.observable(results.nombre),
                                        peso:ko.observable(results.peso),
                                        nivel:ko.observable(1)
                                    });
                                    self.peso_total(self.peso_total()+results.peso);
                                    
                                    ko.utils.arrayForEach(datos, function(x) {

                                           if(x.actividad.padre==results.id){
                                                self.metaVO.push({
                                                    nombre:ko.observable(x.actividad.nombre),
                                                    peso:ko.observable(x.actividad.peso),
                                                    nivel:ko.observable(2),
                                                    cantidad:ko.observable(x.cantidad)
                                                });
                                           } 
                                    });
                                }, path, parameter);
                         });
                    cerrarLoading();

                } else {
                    self.metaVO([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }
            }, path, parameter,undefined,false);
        }


    }


    self.buscar_padres=function(data){

            var lista=[];

             ko.utils.arrayForEach(data, function(d) {
                     sw=0;
                    ko.utils.arrayForEach(lista, function(x) {
                          if(x.id==d.actividad.padre){
                                sw=1
                           }
                    });
                     if(sw==0){
                       // data2=self.informacion_padre(d.actividad.padre);
                        lista.push({
                            id:d.actividad.padre
                        });
                     }

            });

        return lista;
    }


 }

var metas = new MetasViewModel();
metas.consultar(1);//iniciamos la primera funcion
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(metas,content);
ko.applyBindings(metas,header);