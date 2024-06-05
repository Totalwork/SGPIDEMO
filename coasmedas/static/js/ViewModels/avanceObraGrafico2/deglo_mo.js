function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
    self.mensajeMat=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');    
    self.checkall=ko.observable(false);
    self.habilitar_campos=ko.observable(true);
    self.listadoMo = ko.observableArray([]);
    self.manoDeObra_id = ko.observable('');
    self.filtro_mo = ko.observable('');

    self.mo = {
        descripcion : ko.observable('')
    }

    self.desgl_mo = {
        id: ko.observable(0),
        catalogo_id : ko.observable(''),
        uucc_id: ko.observable(''),
        rendimiento: ko.observable('').extend({ required: { message: '(*)Ingrese el rendimiento.' } }),
        manoDeObra_id: ko.observable('').extend({ required: { message: '(*)Seleccione la Mano de Obra.' } })
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
        self.desgl_mo.id(0);        
        self.desgl_mo.manoDeObra_id('');
        self.manoDeObra_id('');
        $('#descripcionMo').val('') 
        self.desgl_mo.rendimiento('');
    }    

    self.checkall.subscribe(function(value ){
        ko.utils.arrayForEach(self.listado(), function(d) {
            d.eliminado(value);
        }); 
    });


    self.consultar=function(pagina){
        sessionStorage.setItem("filtro_desgl_mo", self.filtro());
        self.cargar(pagina);
    }

    self.cargar =function(pagina){             
        
        self.desgl_mo.uucc_id( $('#uucc_id').val());   
        self.desgl_mo.catalogo_id( $('#catalogo_id').val());   
        
        let filtro_avance=sessionStorage.getItem("filtro_desgl_mo");
        path = path_principal+'/api/desgl-mo/?format=json&page='+pagina;
        parameter = {dato: filtro_avance, uucc_id:  self.desgl_mo.uucc_id()};
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

    self.consulta_enter_mo = function (d,e) {
        if (e.which == 13) {                        
            self.consultar_mo();
        }
        return true;
    }               

    self.consultar_mo = function(){                
        path = path_principal+'/api/mano-obra/?format=json';
        if ($('#txt_buscar_mo').val() == ''){
            parameter = {
                catalogo: self.desgl_mo.catalogo_id(),                 
                ignorePagination: 1, 
                lite:1};            
        }else{
            parameter = {
                catalogo: self.desgl_mo.catalogo_id(), 
                dato: $('#txt_buscar_mo').val(),
                ignorePagination: 1, 
                lite:1};
        }        
        RequestGet(function (datos, estado, mensage) {
            if (estado == 'ok' && datos != null && datos.length > 0) {
                self.listadoMo(datos)                                            
            }else{
                self.listadoMo([]);
                self.mensajeMat(mensajeNoFound); //mensaje not found se encuentra el el archivo call-back.js
            }

            cerrarLoading();
        }, path, parameter,undefined, false);        
    }

    self.seleccionar_mo = function() {

        self.desgl_mo.manoDeObra_id(self.manoDeObra_id());
        path = path_principal+'/api/mano-obra/?format=json';        
        parameter = {
            catalogo: self.desgl_mo.catalogo_id(),                 
            ignorePagination: 1, 
            lite:1,
            pk: self.desgl_mo.manoDeObra_id()
        };        
        RequestGet(function (datos, estado, mensage) {
            $('#descripcionMo').val(datos[0]["descripcion"])            
            $('#modal_buscar_mo').modal('hide');
            $('#txt_buscar_mo').val('')
            cerrarLoading();
        }, path, parameter,undefined, false);                                    

    }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Desglose Mano de Obra'); 
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
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un desglose mano de obra para la eliminacion.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });

         }else{
             var path =path_principal+'/avanceObraGrafico2/eliminar_id_desgl_mo/';
             var parameter = { lista: lista_id};
             RequestAnularOEliminar("Esta seguro que desea eliminar los desgloses de mano de obra seleccionadas?", path, parameter, function () {
                 self.consultar(1);
                 self.checkall(false);
             })

         }     
    }
    

    self.guardar=function(){
        self.desgl_mo.manoDeObra_id(self.manoDeObra_id())        
        if($('#descripcionMo').val() == ''){
            mensajeInformativo("Seleccione una Mano de Obra","Informativo");
        }else{
            if (IndexViewModel.errores_mo().length == 0) {//se activa las validaciones                       
                if(self.desgl_mo.id()==0){
                    var parametros={                     
                        callback:function(datos, estado, mensaje){
    
                           if (estado=='ok') {
                               self.limpiar();
                               self.filtro("");
                               self.consultar(self.paginacion.pagina_actual());
                               $('#modal_acciones').modal('hide');
                           }                        
                           
                        },
                        url:path_principal+'/api/desgl-mo/',//url api
                        parametros:self.desgl_mo                        
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
                        url:path_principal+'/api/desgl-mo/'+self.desgl_mo.id()+'/',
                        parametros:self.desgl_mo                        
                    };
                    RequestFormData(parametros);			
                }
    
            } else {
                 IndexViewModel.errores_mo.showAllMessages();//mostramos las validacion
            }           
        }

    }

    self.exportar_excel=function(){
        location.href=path_principal+"/avanceObraGrafico2/excel_desgl_mo/?dato="+self.filtro()+"&uucc_id="+self.desgl_mo.uucc_id();  
    } 
    

    self.modificar_desgl_mo = function(obj){                
        self.limpiar()        
        // window.setTimeout(() => {console.log('');}, 2000);
        self.consultar_por_id(obj);        
    }

    self.consultar_por_id=function(obj){         
        self.titulo('Actualizar Desglose Mano de Obra');
        path = path_principal+'/api/desgl-mo/'+obj.id+'/?format=json';
        parameter = {};
        RequestGet(function (datos, estado, mensage) {                        
            self.desgl_mo.id(datos.id);
            self.desgl_mo.rendimiento(datos.rendimiento);
            self.manoDeObra_id(datos.manoDeObra.id);
            self.desgl_mo.manoDeObra_id(datos.manoDeObra.id);
            $('#descripcionMo').val(datos.manoDeObra.descripcion);                       
            // self.desgl_mo.descripcion(datos.descripcion);
            // self.desgl_mo.tipoUnidadConstructiva_id(datos.tipoUnidadConstructiva_id);                            
            // self.desgl_mo.codigo(datos.codigo);   
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
        path = path_principal+'/avanceObraGrafico2/inactivar-catalogo/';
        parameter = {id:self.catalogo.id()};
        RequestGet(function (datos, estado, mensage) {                        
            self.consultar(self.paginacion.pagina_actual());
            $('#modal_estado1').modal('hide');            
            cerrarLoading();
        }, path, parameter,undefined, false);        
    }

    self.activar2 = function(){               
        path = path_principal+'/avanceObraGrafico2/activar-catalogo/';
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
     
     self.desglose_mat = function(obj){        
        location.href=path_principal+"/avanceObraGrafico2/mo/"+obj.id+"/";
    }      

    self.abrir_buscar_mo = function(){
        self.consultar_mo();
        $('#modal_buscar_mo').modal('show');
    }


}


var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_uucc"));
index.cargar(1);//iniciamos la primera funcion
IndexViewModel.errores_mo = ko.validation.group(index.desgl_mo);
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