function DocumentoViewModel(){
	var self=this;
	self.url=path_principal;
    self.titulo = ko.observable('');
	self.listado=ko.observableArray([]);
    self.listadoArchivos=ko.observableArray([]);
    self.mensaje=ko.observable('');
	self.porcentajeKo = ko.observable(0);

 

    self.PredioDocumentoVO = {
        id:ko.observable(0),
        predio_id:ko.observable(0),
        documento_id:ko.observable(0),
        archivo:ko.observable('').extend({ required: { message: '(*)Seleccione un archivo por favor' } }),
        nombre:ko.observable('')

    }

    self.consultar = function (predio) {
        if (predio > 0) {           
            path = self.url + '/servidumbre/documentospredio?format=json&id=' + predio;
            
            parameter = {              
                id:predio               
            };
            RequestGet(function(data,count) {      
                self.listado(data.documentos);
                self.PredioDocumentoVO.predio_id(predio);
                self.porcentajeKo(data.porcentaje);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }       
    }
    self.abrir_modal = function(obj) {
        self.titulo('Archivos de este documento');
        self.PredioDocumentoVO.documento_id(obj.id)
        $('#modal_archivos').modal('show');
       
        
        self.consultarArchivos(obj.id,$('#txtPredio').val());


    }

    self.consultarArchivos = function(documento_id,predio_id){
        if (documento_id > 0) {
            //alert('entre aqui' + pagina); 
            //self.buscado_rapido(true);
            path = path_principal+'/api/servidumbreprediodocumento/' + '?format=json';
            parameter = {
                documento_id: documento_id,
                predio_id: predio_id,
            };
            RequestGet(function(datos, estado, mensage) {
                //alert(datos.data);
                if (estado == 'ok' && datos.data != null && datos.data.length > 0) {
                    self.mensaje('');
                    self.listadoArchivos(datos.data);
                } else {
                    self.listadoArchivos([]);
                    self.mensaje('<div class="alert alert-warning alert-dismissable"><i class="fa fa-warning"></i>No se encontraron archivos cargados a este tipo de documento.</div>'); //mensaje not found se encuentra el el archivo call-back.js
                }
                //self.llenar_paginacion(datos, pagina);
                cerrarLoading();
            }, path, parameter,undefined,false);
        }
    }

    self.limpiar = function(){
        self.PredioDocumentoVO.id(0);
        self.PredioDocumentoVO.predio_id(0);
        self.PredioDocumentoVO.documento_id(0);
        self.PredioDocumentoVO.archivo('');
        self.PredioDocumentoVO.nombre('');
        $('#soporte').fileinput('reset');
        $('#soporte').val('');  
        
        self.PredioDocumentoVO.nombre.isModified(false);
        self.PredioDocumentoVO.archivo.isModified(false);

    }
   
    self.guardarArchivo = function(){
        if (DocumentoViewModel.errores_archivo().length == 0) {
            // self.soporteVO.documento($('#archivo')[0].files[0]);
            if(self.PredioDocumentoVO.id()==0){
                var parametros={                     
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultarArchivos($('#txtDocumento').val(),$('#txtPredio').val());                            
                            self.consultar($('#txtPredio').val());
                            self.limpiar();
                        }else{
                            self.mensaje('<div class="alert alert-danger alert-dismissable"><i class="fa fa-warning"></i>Se presentaron errores al guardar el archivo.</div>'); //mensaje not found se encuentra el el archivo call-back.js                           
                        }                        
                                
                    },//funcion para recibir la respuesta 
                             // url:path_principal+'/servidumbre/guardar_archivo/',//url api
                             url:path_principal+'/api/servidumbreprediodocumento/',//url api
                             parametros:self.PredioDocumentoVO                        
                };
                RequestFormData(parametros);

            }else{
                var parametros={     
                    metodo:'PUT',                
                    callback:function(datos, estado, mensaje){

                        if (estado=='ok') {
                            self.consultarArchivos($('#txtDocumento').val(),$('#txtPredio').val());
                            self.consultar($('#txtPredio').val());
                            self.limpiar();
                           
                        }  
                    },
                    // url:path_principal+'/servidumbre/guardar_archivo/'+self.PredioDocumentoVO.id()+'/',
                    url:path_principal+'/api/servidumbreprediodocumento/'+self.PredioDocumentoVO.id()+'/',
                    parametros:self.PredioDocumentoVO                        
                };

                RequestFormData(parametros);
                
            }

            //location.href=self.url+'/servidumbre/documentos/'+$('#idExpediente').val()+'/'+$('#txtPredio').val()+'/'
        }else{
            DocumentoViewModel.errores_archivo.showAllMessages();//mostramos las validacion
        }
    }
  
    self.eliminar = function(id) {
        var path =path_principal+'/api/servidumbreprediodocumento/'+id+'/';
        var parameter = {metodo:'DELETE'};
        RequestAnularOEliminar("Esta seguro que desea eliminar el soporte?", path, parameter, 
            function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultarArchivos($('#txtDocumento').val(),$('#txtPredio').val());
                  self.consultar($('#txtPredio').val());
                }
        
        });

    }

}
var documentoPredio = new DocumentoViewModel();
DocumentoViewModel.errores_archivo=ko.validation.group(documentoPredio.PredioDocumentoVO);
ko.applyBindings(documentoPredio);