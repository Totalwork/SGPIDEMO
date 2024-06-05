function IndexViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');    
    self.checkall=ko.observable(false);
    self.habilitar_campos=ko.observable(true);
    self.archivo_carga = ko.observable('');

    self.catalogo2 = {
        descripcion:ko.observable(''),
        id:ko.observable(''),        
    }

    self.catalogo = {
        id: ko.observable(0),
        nombre: ko.observable('').extend({ required: { message: '(*)Ingrese el nombre.' } }),
        mcontrato_id: ko.observable('').extend({ required: { message: '(*)Seleccione el contrato.' } }),
        ano: ko.observable('').extend({ required: { message: '(*)Ingrese el año.' } }),
        activo: ko.observable(true)
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
        self.catalogo.id(0);
        self.catalogo.nombre('');
        self.catalogo.mcontrato_id('');
        self.catalogo.ano('');
    }    

    self.consultar=function(pagina){
        sessionStorage.setItem("filtro_catalogo", self.filtro());
        self.cargar(pagina);
    }

    self.cargar =function(pagina){           
        let filtro_avance=sessionStorage.getItem("filtro_catalogo");
        path = path_principal+'/api/avanceObraLiteCatalogoUUCC/?format=json&page='+pagina;
        parameter = {dato: filtro_avance};
        RequestGet(function (datos, estado, mensage) {

            if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {
                self.mensaje('');                
                self.listado(agregarOpcionesObservable(datos.data));
                 $('#modal_acciones').modal('hide');

            } else {
                self.listado([]);
                self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
            }

            self.llenar_paginacion(datos,pagina);
            cerrarLoading();
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
        self.titulo('Registrar Catalogo');
        $('#modal_acciones').modal('show');
    }

    self.abrir_carga_masiva = function (obj) { 
        self.archivo_carga('');               
        self.catalogo2.id(obj.id);
        self.catalogo2.descripcion(obj.nombre);
        self.titulo('Carga Masiva');
        $('#modal_carga_masiva').modal('show');
    }    
        
    self.carga_excel=function(){

        if(self.archivo_carga()==''){
    
          $.confirm({
            title:'Informativo',
            content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Cargue el archivo.<h4>',
            cancelButton: 'Cerrar',
            confirmButton: false
          });
    
    
        }else{
    
          var data = new FormData();
    
          data.append('catalogo_id',self.catalogo2.id());
          data.append('archivo',self.archivo_carga());
          var parametros={                     
            callback:function(datos, estado, mensaje){
              self.consultar(1);
              $('#modal_carga_masiva').modal('hide');                    
                              
            },//funcion para recibir la respuesta 
            url:path_principal+'/avanceObraLite/carga_masiva_catalogo/',
            parametros:data                        
          };
          RequestFormData2(parametros);
    
        }
    
      }  

    self.guardar=function(){

         if (IndexViewModel.errores_catalogos().length == 0) {//se activa las validaciones           
            if(self.catalogo.id()==0){
                var parametros={                     
                    callback:function(datos, estado, mensaje){

                       if (estado=='ok') {
                           self.limpiar();
                           self.filtro("");
                           self.consultar(self.paginacion.pagina_actual());
                           $('#modal_acciones').modal('hide');
                       }                        
                       
                    },
                    url:path_principal+'/api/avanceObraLiteCatalogoUUCC/',//url api
                    parametros:self.catalogo                        
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
					url:path_principal+'/api/avanceObraLiteCatalogoUUCC/'+self.catalogo.id()+'/',
					parametros:self.catalogo                        
				};
				RequestFormData(parametros);			
            }

        } else {
             IndexViewModel.errores_catalogos.showAllMessages();//mostramos las validacion
        }
    }

    self.exportar_excel=function(){
		location.href=path_principal+"/avanceObraLite/excel_catalogo/?dato="+self.filtro()
    } 
    
    self.consultar_por_id=function(obj){
        self.titulo('Actualizar Catalogo');
        path = path_principal+'/api/avanceObraLiteCatalogoUUCC/'+obj.id+'/?format=json';
        parameter = {};
        RequestGet(function (datos, estado, mensage) {
            self.catalogo.id(datos.id);
            self.catalogo.nombre(datos.nombre);
            self.catalogo.ano(datos.ano);                            
            self.catalogo.mcontrato_id(datos.mcontrato_id);
            $('#modal_acciones').modal('show');            
            cerrarLoading();
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
    
    self.consultar_uucc = function(obj){        
        location.href=path_principal+"/avanceObraLite/uucc/"+obj.id+"/";
    }

    self.consultar_materiales = function(obj){        
        location.href=path_principal+"/avanceObraLite/materiales/"+obj.id+"/";
    }

    self.consultar_manoObra = function(obj){        
        location.href=path_principal+"/avanceObraLite/mano_obra/"+obj.id+"/";
    }    

    self.paginacion.pagina_actual.subscribe(function (pagina) {    
        self.consultar(pagina);
     });    

}


var index = new IndexViewModel();
$('#txtBuscar').val(sessionStorage.getItem("filtro_catalogo"));
index.cargar(1);//iniciamos la primera funcion
IndexViewModel.errores_catalogos = ko.validation.group(index.catalogo);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(index,content);
ko.applyBindings(index,header);

