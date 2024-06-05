function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');    
    self.checkall=ko.observable(false);
    self.habilitar_campos=ko.observable(true);
    self.listadoTipos = ko.observableArray([]);


    self.manoObra = {
        id: ko.observable(0),
        descripcion: ko.observable('').extend({ required: { message: '(*)Ingrese la descripcion.' } }),        
        valorHora: ko.observable(0).money().extend({ required: { message: '(*)Ingrese el valor.' } }),
        codigo: ko.observable('').extend({ required: { message: '(*)Ingrese el codigo.' } }),
        catalogo_id: ko.observable(0)
    }

    self.paginacion = {
        pagina_actual: ko.observable(1),
        total: ko.observable(0),
        maxPaginas: ko.observable(10),
        directiones: ko.observable(true),
        limite: ko.observable(true),
        cantidad_por_paginas: ko.observable(0),
        totalRegistrosBuscados:ko.observable(0),
        text: {
            first: ko.observable('Inicio'),
            last: ko.observable('Fin'),
            back: ko.observable('<'),
            forward: ko.observable('>')
        }
    }

    self.limpiar=function(){   
        self.manoObra.id(0);
        self.manoObra.descripcion('');        
        self.manoObra.valorHora(0);
        self.manoObra.codigo('');
    }    

    self.checkall.subscribe(function(value ){
        ko.utils.arrayForEach(self.listado(), function(d) {
            d.eliminado(value);
        }); 
    });


    self.consultar=function(pagina){
        sessionStorage.setItem("filtro_manoObra", self.filtro());
        self.cargar(pagina);
    }

    self.cargar =function(pagina){        
        self.manoObra.catalogo_id( $('#catalogo_id').val());   
        let filtro_avance=sessionStorage.getItem("filtro_manoObra");
        path = path_principal+'/api/avanceObraLiteMano-obra/?format=json&page='+pagina;
        parameter = {dato: filtro_avance, catalogo: self.manoObra.catalogo_id()};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje('');                
                self.listado(agregarOpcionesObservable(datos.data));
                 $('#modal_acciones').modal('hide');
                 cerrarLoading();

            } else {
                self.listado([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                cerrarLoading();
            }

            self.llenar_paginacion(datos,pagina);            
        }, path, parameter,undefined, false);
    }

    self.llenar_paginacion = function (data,pagina) {

        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);

    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.consultar(1);
        }
        return true;
    }


    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Mano de Obra');                
        $('#modal_acciones').modal('show');
    }
    
    self.eliminar=function(){
        var lista_id=[];
         var count=0;
         ko.utils.arrayForEach(self.listado(), function(d) {
            if(d.eliminado()==true){
                count=1;
                lista_id.push({id:d.id})
            }
         });

         if(count==0){

              $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una mano de obra para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraLite/eliminar_id_mano_obra/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar las manos de obra seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    }
    

    self.guardar=function(){

         if (IndexViewModel.errores_manoObra().length == 0) {//se activa las validaciones           
            if(self.manoObra.id()==0){
                var parametros={                     
                    callback:function(datos, estado, mensaje){

                       if (estado=='ok') {
                           self.limpiar();
                           self.filtro("");
                           self.consultar(self.paginacion.pagina_actual());
                           $('#modal_acciones').modal('hide');
                       }                        
                       
                    },
                    url:path_principal+'/api/avanceObraLiteMano-obra/',//url api
                    parametros:self.manoObra                        
               };               
               RequestFormData(parametros);                                
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
					url:path_principal+'/api/avanceObraLiteMano-obra/'+self.manoObra.id()+'/',
					parametros:self.manoObra                        
				};
				RequestFormData(parametros);			
            }

        } else {
             IndexViewModel.errores_manoObra.showAllMessages();//mostramos las validacion
        }
    }

    self.exportar_excel=function(){
        location.href=path_principal+"/avanceObraLite/excel_mo/?dato="+self.filtro()+"&catalogo_id="+self.manoObra.catalogo_id();
    } 
        
    self.modificar_manoObra = function(obj){                
        self.limpiar()
        self.consultar_por_id(obj);
        // setTimeout(function(){ self.consultar_por_id(obj);}, 1000);                                      
    }

    self.consultar_por_id=function(obj){         
        self.titulo('Actualizar Mano de Obra');
        path = path_principal+'/api/avanceObraLiteMano-obra/'+obj.id+'/?format=json';
        parameter = {};
        RequestGet(function (datos, estado, mensage) {                        
            
            self.manoObra.id(datos.id);
            self.manoObra.descripcion(datos.descripcion);
            self.manoObra.codigo(datos.codigo);                            
            self.manoObra.valorHora(datos.valorHora);   

            cerrarLoading();
            $('#modal_acciones').modal('show'); 
        }, path, parameter,undefined, false);
    }

    self.inactivar1 = function(obj){ 
        self.titulo('Confirmar');       
        $('#modal_estado1').modal('show');
        self.catalogo.id(obj.id);
    }

    self.activar1 = function(obj){ 
        self.titulo('Confirmar');       
        $('#modal_estado2').modal('show');
        self.catalogo.id(obj.id);
    }    

    self.inactivar2 = function(){               
        path = path_principal+'/avanceObraLite/inactivar-catalogo/';
        parameter = {id:self.catalogo.id()};
        RequestGet(function (datos, estado, mensage) {                        
            self.consultar(self.paginacion.pagina_actual());
            $('#modal_estado1').modal('hide');            
            cerrarLoading();
        }, path, parameter,undefined, false);        
    }

    self.activar2 = function(){               
        path = path_principal+'/avanceObraLite/activar-catalogo/';
        parameter = {id:self.catalogo.id()};
        RequestGet(function (datos, estado, mensage) {                        
            self.consultar(self.paginacion.pagina_actual());
            $('#modal_estado2').modal('hide');            
            cerrarLoading();
        }, path, parameter,undefined, false);        
    } 
   
    self.paginacion.pagina_actual.subscribe(function (pagina) {    
        self.consultar(pagina);
     });        

}


var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_manoObra"));
index.cargar(1);//iniciamos la primera funcion
IndexViewModel.errores_manoObra = ko.validation.group(index.manoObra);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);
var formatCurrency = function (amount) {
    if (amount.toString() == "0"){
        return "$0.00"
    }else{
        if (!amount) {
            return "";
        }
        amount += '';
        x = amount.split('.');
        x1 = x[0];
        x2 = x.length > 1 ? '.' + x[1] : '';
        var rgx = /(\d+)(\d{3})/;
        while (rgx.test(x1)) {
            x1 = x1.replace(rgx, '$1' + ',' + '$2');
        }
        return "$" + x1 + x2;
    }    
}

