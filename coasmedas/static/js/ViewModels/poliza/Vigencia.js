function VigenciaPolizaViewModel(argument) {

var self=this;
self.listado=ko.observableArray([]);
self.mensaje=ko.observable('');
self.titulo=ko.observable('');
self.filtro=ko.observable('');
self.url=path_principal+'/api/VigenciaPoliza/'; 
self.nombre_beneficiario=ko.observable('');
self.soporte=ko.observable('');
self.listado_polizas=ko.observableArray([]);
self.seleccionar_todos=ko.observable(false);
self.seleccionar_vigencias=ko.observable(false);
self.obj_poliza=ko.observable({});
self.tipo_acta_id = ko.observable();
 
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

self.vigencia_polizaVO={
     id:ko.observable(0),    
     fecha_inicio:ko.observable('').extend({ required: { message: '(*)Seleccione la fecha inicio de la poliza' } }).extend({ validation: { validator: validar_fecha_final, message: '(*) La fecha inicio no puede ser mayor que la fecha final.' } }),
     fecha_final:ko.observable('').extend({ required: { message: '(*)Seleccione la fecha final de la poliza' } }).extend({ validation: { validator: validar_fecha_final, message: '(*) La fecha final no puede ser menor que la fecha de inicio.' } }),
     valor:ko.observable(0).money().extend({ validation: { validator: validar_valor, message: '(*) Ingrese el valor de la poliza.' } }),
     observacion:ko.observable(''),
     soporte:ko.observable(''),
     amparo:ko.observable(''),
     tomador:ko.observable(''),
     numero:ko.observable('').extend({ required: { message: '(*)Ingrese el numero de la poliza' } }),
     reemplaza:ko.observable(''),
     aseguradora_id:ko.observable('').extend({ required: { message: '(*)Seleccione la aseguradora de la poliza' } }),
     poliza_id:ko.observable($('#hd_poliza_id').val()),
     beneficiarios:ko.observableArray([]),     
     tipo_acta_id:ko.observable(''), //.extend({ required: { message: '(*)Seleccione el tipo de acta' } }),
     tipo_documento_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de documento asociado' } }),
     documento_id:ko.observable(''), //.extend({ validation: { validator: validar_ducumento, message: '(*)Seleccione el documento.' } }),
     numero_certificado:ko.observable('')
}

function validar_fecha_final(){      
    var fecha_final=self.vigencia_polizaVO.fecha_final(); 
    var fecha_inicio=self.vigencia_polizaVO.fecha_inicio();
    if (fecha_inicio!=null && fecha_inicio!='' && fecha_final!=null && fecha_final!='') { 
      return  new Date(fecha_final) >= new Date(fecha_inicio);
    }else{
      return true;
    }      
}

function validar_ducumento(val){
  var tipo_acta_id=self.tipo_acta_id();
  if($('#hd_TipoActaNinguno').val()==tipo_acta_id && (val=='' || val==null)){
      return false;
  }
  return true;
}

self.vigencia_polizaVO.tipo_acta_id.subscribe(function(val) {
  self.tipo_acta_id(val);
  self.vigencia_polizaVO.documento_id('');
});

self.datos_de_rererencia={     
    
     no_contrato:ko.observable(0),  
     nombre_contrato:ko.observable(0),  
     contratante:ko.observable(0),  
     contratista:ko.observable(0),  
     tipo_poliza:ko.observable(0),  
     fecha_inicio:ko.observable(''),
     fecha_final:ko.observable(''),
     valor_total:ko.observable(0),     
     aseguradora:ko.observable(0),     
}

    function validar_valor(val) {  
      return val > 0;
    }

    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
    }

    self.exportar_excel=function(){
      location.href=path_principal+"/poliza/exportar-vigencias/?poliza_id=" + $('#hd_poliza_id').val();     
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Nueva vigencia poliza');
        $('#modal_acciones').modal('show');
    }

    self.limpiar=function(){

        self.vigencia_polizaVO.id(0);     
        self.vigencia_polizaVO.fecha_inicio($('#hd_poliza_fecha_inicio').val());
        self.vigencia_polizaVO.fecha_final($('#hd_poliza_fecha_final').val());
        self.vigencia_polizaVO.valor($('#hd_poliza_valor').val() || 0);
        self.vigencia_polizaVO.observacion('');
        self.vigencia_polizaVO.soporte('');
        self.vigencia_polizaVO.amparo($('#hd_poliza_amparo').val());
        self.vigencia_polizaVO.tomador($('#hd_poliza_tomador').val());
        self.vigencia_polizaVO.numero($('#hd_poliza_numero').val());
        self.vigencia_polizaVO.reemplaza(false);
        self.vigencia_polizaVO.aseguradora_id($('#hd_poliza_aseguradora_id').val());
        self.vigencia_polizaVO.beneficiarios([]);
        self.vigencia_polizaVO.documento_id('');
        self.vigencia_polizaVO.tipo_acta_id('');
        self.vigencia_polizaVO.tipo_documento_id('');
        self.vigencia_polizaVO.numero_certificado('');
        $('#soporte').fileinput('reset');
        $('#soporte').val('');

        self.vigencia_polizaVO.fecha_inicio.isModified(false);
        self.vigencia_polizaVO.fecha_final.isModified(false);
        self.vigencia_polizaVO.aseguradora_id.isModified(false);
        self.vigencia_polizaVO.numero.isModified(false);
        self.vigencia_polizaVO.valor.isModified(false);
        self.vigencia_polizaVO.documento_id.isModified(false);
        self.vigencia_polizaVO.tipo_acta_id.isModified(false);
        self.vigencia_polizaVO.tipo_documento_id.isModified(false);
    }

    self.consultar = function (pagina) {
   
       //self.buscado_rapido(true);
       self.filtro($('#txtBuscar').val());
       path =self.url + '?format=json&sin_paginacion=&lite=1';
       parameter = { poliza_id: $('#hd_poliza_id').val()};
       RequestGet(function (datos, estado, mensage) {
           if (estado == 'ok' && datos!=null && datos.length > 0) {
               
               self.mensaje('');
               //self.listado(results);  
               self.listado(agregarOpcionesObservable(datos));  
           } else {
               self.listado([]);
               self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
           }
           //self.llenar_paginacion(datos,pagina);
           
       }, path, parameter, function(){
                    cerrarLoading();
                   });
    
    }

    self.consultar_poliza_por_id = function () {
   
       //self.buscado_rapido(true);       
       path =path_principal + '/api/Poliza/' + $('#hd_poliza_id').val()+'/?format=json';
       parameter = {  };
       RequestGet(function (datos, estado, mensage) {
           if (estado == 'ok') {
                
             self.datos_de_rererencia.no_contrato(datos.contrato.numero);
             self.datos_de_rererencia.nombre_contrato(datos.contrato.nombre);
             self.datos_de_rererencia.contratante(datos.contrato.contratante.nombre);
             self.datos_de_rererencia.contratista(datos.contrato.contratista.nombre);
             self.datos_de_rererencia.tipo_poliza(datos.tipo.nombre);
             self.datos_de_rererencia.fecha_inicio(datos.fecha_inicio);
             self.datos_de_rererencia.fecha_final(datos.fecha_final);
             self.datos_de_rererencia.valor_total(datos.valor);
             self.datos_de_rererencia.aseguradora(datos.vigencias[0].aseguradora.nombre);

           }            
           
       }, path, parameter, function(){
                    cerrarLoading();
                   });
    
    }

    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }

    self.seleccionar_vigencias.subscribe(function(val){
       ko.utils.arrayForEach(self.listado(),function(p){
          p.procesar(val);
       });
    });

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        /*if (self.buscado_rapido()) {
            self.consultar(pagina);
          }else{
            self.consultar_por_filtros(pagina);
          }  */    
          self.consultar(pagina); 
    });

    self.guardar=function(){

      if (self.vigencia_polizaVO.tipo_documento_id() == '91') {
        self.vigencia_polizaVO.documento_id('');
      }
    	
      if (VigenciaPolizaViewModel.errores_vigencia().length == 0) {

          var formData= new FormData();
          formData.append("id", self.vigencia_polizaVO.id());
          formData.append("fecha_inicio", self.vigencia_polizaVO.fecha_inicio());
          formData.append("fecha_final", self.vigencia_polizaVO.fecha_final());
          formData.append("valor", self.vigencia_polizaVO.valor());
          formData.append("observacion", self.vigencia_polizaVO.observacion() || '');
          formData.append("soporte", self.vigencia_polizaVO.soporte());
          formData.append("amparo", self.vigencia_polizaVO.amparo() || '');
          formData.append("tomador", self.vigencia_polizaVO.tomador());
          formData.append("numero", self.vigencia_polizaVO.numero());
          formData.append("reemplaza", self.vigencia_polizaVO.reemplaza());
          formData.append("aseguradora_id", self.vigencia_polizaVO.aseguradora_id());
          formData.append("poliza_id", self.vigencia_polizaVO.poliza_id());
          formData.append('documento_id', self.vigencia_polizaVO.documento_id() || '');
          formData.append('tipo_acta_id', self.vigencia_polizaVO.tipo_acta_id() || '');
          formData.append('tipo_documento_id', self.vigencia_polizaVO.tipo_documento_id() || '');
          formData.append('numero_certificado', self.vigencia_polizaVO.numero_certificado());
          // beneficiarios='';
          // ko.utils.arrayForEach(self.vigencia_polizaVO.beneficiarios(),function(p){
          //   beneficiarios+=ko.toJSON(p)+',';        
          // });
          // formData.append("beneficiarios", '['+beneficiarios.substring(0, beneficiarios.length - 1)+']');
          formData.append("beneficiarios", ko.toJSON(self.vigencia_polizaVO.beneficiarios()));

        if (self.vigencia_polizaVO.id()==0) {

      	 var parametros={           
                callback:function(datos, estado, mensaje){
                   if (estado=='ok') {  
                      $('#modal_acciones').modal('hide');              
                      self.consultar(1);
                   }
                },//funcion para recibir la respuesta 
                completado:function(){
                  self.consultar_poliza_por_id();
                  // cerrarLoading();
                },
                url:self.url,
                parametros:formData
          };
                 
          RequestFormData2(parametros);
        }else{
          
          var parametros={   
                metodo:'PUT',                
                callback:function(datos, estado, mensaje){
                   if (estado=='ok') {     
                      $('#modal_acciones').modal('hide');            
                      self.consultar(self.paginacion.pagina_actual());
                   }
                },//funcion para recibir la respuesta 
                completado:function(){
                  self.consultar_poliza_por_id();
                },
                url:self.url + self.vigencia_polizaVO.id() + '/',
                parametros:formData
          };
                 
          RequestFormData2(parametros);

        }  
      }else{
        VigenciaPolizaViewModel.errores_vigencia.showAllMessages();//mostramos las validacion
      }    
    }
   
    self.agregar_beneficiario=function(){
        if (self.nombre_beneficiario()!='') {
            self.vigencia_polizaVO.beneficiarios.push({nombre:self.nombre_beneficiario()});
            self.nombre_beneficiario(''); 
        }   
    }

    self.remover_beneficiario=function(obj){
        self.vigencia_polizaVO.beneficiarios.remove(obj);
    }

    self.consultar_por_id = function (id,copiar) {
       
      // alert(obj.id)
       path =self.url+id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
            self.limpiar();
            
            if(!copiar)
              self.vigencia_polizaVO.id(datos.id); 

             if(self.vigencia_polizaVO.id()==0)
                self.titulo('Nueva vigencia poliza');
             else
                self.titulo('Actualizar Poliza');

            self.vigencia_polizaVO.fecha_inicio(datos.fecha_inicio);
            self.vigencia_polizaVO.fecha_final(datos.fecha_final);
            self.vigencia_polizaVO.valor(datos.valor);
            self.vigencia_polizaVO.observacion(datos.observacion);
            self.vigencia_polizaVO.soporte('');
            self.soporte(datos.soporte);
            self.vigencia_polizaVO.amparo(datos.amparo);
            self.vigencia_polizaVO.tomador(datos.tomador);
            self.vigencia_polizaVO.numero(datos.numero);
            self.vigencia_polizaVO.reemplaza(datos.reemplaza);
            self.vigencia_polizaVO.aseguradora_id(datos.aseguradora.id.toString());
            self.vigencia_polizaVO.beneficiarios(agregarOpcionesObservable(convertToObservableArray(datos.beneficiarios)));
            self.vigencia_polizaVO.tipo_documento_id(datos.tipo_documento_id ? datos.tipo_documento_id.toString() : '');
            self.vigencia_polizaVO.tipo_acta_id(datos.tipo_acta_id ? datos.tipo_acta_id : '');            
            self.vigencia_polizaVO.documento_id(datos.documento_id);
            self.vigencia_polizaVO.numero_certificado(datos.numero_certificado)

            $('#modal_acciones').modal('show');
         }, path, {}, function(){
                    cerrarLoading();
                   });

     }

     //obtiene las polizas por contrato
     self.consultar_por_contrato = function () {
   
       //self.buscado_rapido(true);       
       path =path_principal+'/api/Poliza/?format=json&sin_paginacion=';
       parameter = { contrato_id: $('#hd_contrato_id').val()};
       RequestGet(function (datos, estado, mensage) {
           if (estado == 'ok' && datos!=null && datos.length > 0) {
               
               self.mensaje('');
               
               ko.utils.arrayForEach(datos, function (p,i) {
                  datos[i].vigencias=agregarOpcionesObservable(p.vigencias);
               });

               self.listado_polizas(convertToObservableArray(datos));
               

           } else {
               self.listado_polizas([]);
               self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
           }
           //self.llenar_paginacion(datos,pagina);
           
       }, path, parameter, function(){
                    cerrarLoading();
                   });
    
    }

    self.seleccionar_todos.subscribe(function(val){
      ko.utils.arrayForEach(self.listado_polizas(),function(p){
        ko.utils.arrayForEach(p.vigencias(),function(vig){
          vig.procesar(val);
        });
      });
    });

    self.guardar_asociacion=function(){

      var lista=[]

      ko.utils.arrayForEach(self.listado_polizas(),function(p){
        ko.utils.arrayForEach(p.vigencias(),function(vig){
          if(vig.procesar())
            lista.push(vig.id());
        });
      });

      if (lista.length==0) {
        mensajeInformativo('Seleccione el(los) registros a asociar', 'Información');
        return false;
      }

      var parametros={                       
            callback:function(datos, estado, mensaje){
               if (estado=='ok') {    
                  self.consultar_por_contrato();
               }
            },//funcion para recibir la respuesta 
            url:path_principal + '/poliza/guardar_asociacion_soporte/',
            parametros:{vigencia_id:$('#hd_vigencia_asoaiar').val(),lista:lista},
             completado:function(){
                    cerrarLoading();
                   }
      };
             
      Request(parametros);

    }

    self.eliminar=function(){
        
        var lista=[];
        ko.utils.arrayForEach(self.listado(), function(p){          
          if (p.procesar()) {
            lista.push(p.id);
          }
        });
        
        RequestAnularOEliminar('¿Desea eliminar el(los) registro(s) seleccionado(s)?', 
          path_principal+'/poliza/eliminar_vigencias/', {lista:lista}, 
          function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultar(self.paginacion.pagina_actual()); 
                  self.consultar_poliza_por_id();
             }
        }, function(){

           cerrarLoading();
           
        }, false); 

    }

    self.ver_soporte = function(obj) {
        window.open(path_principal+"/poliza/ver-soporte/?id="+ obj.id, "_blank");
    }

}

var vigencia = new VigenciaPolizaViewModel();
VigenciaPolizaViewModel.errores_vigencia=ko.validation.group(vigencia.vigencia_polizaVO);
ko.applyBindings(vigencia);