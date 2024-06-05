function PolizaViewModel(argument) {

    var self=this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.url=path_principal+'/api/Poliza/'; 
    self.nombre_beneficiario=ko.observable('');
    self.seleccionar_polizas=ko.observable(false);
    //self.tipo_contrato_id=ko.observable('');    
    self.lista_contratos=ko.observableArray([]); 
    self.listado_poliza_contratos=ko.observableArray([]);   
    self.contrato_id=ko.observable('');
    self.origen=ko.observable('');
    self.soporte = ko.observable('');
    self.tipo_acta_id = ko.observable();
    /*parametros de busqueda*/
    self.filtros={
      tipo_contrato_id:ko.observable(''),
      contrato_id:ko.observable(''),      
      tipo_id:ko.observable(''),   
      lista_contratos:ko.observableArray([])
    }

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
        },
        totalRegistrosBuscados:ko.observable(0)
    }

    self.polizaVO={
        id:ko.observable(0),     
        contrato_id:ko.observable('').extend({ required: { message: '(*)Seleccione el contrato de la poliza' } }),
        tipo_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de poliza' } }),
        /*Vigencia*/
        fecha_inicio:ko.observable('').extend({ required: { message: '(*)Seleccione la fecha inicio de la poliza' } }).extend({ validation: { validator: validar_fecha_final, message: '(*) La fecha inicio no puede ser mayor que la fecha final.' } }),
        fecha_final:ko.observable('').extend({ required: { message: '(*)Seleccione la fecha final de la poliza' } }).extend({ validation: { validator: validar_fecha_final, message: '(*) La fecha final no puede ser menor que la fecha de inicio.' } }),
        valor:ko.observable(0).money().extend({ required: { message: '(*)Ingrese el valode la poliza' } }),
        observacion:ko.observable(''),
        soporte:ko.observable(''),
        amparo:ko.observable(''),
        tomador:ko.observable(''),
        numero:ko.observable(''),//.extend({ required: { message: '(*)Digite' } }),
        reemplaza:ko.observable(),
        aseguradora_id:ko.observable('').extend({ required: { message: '(*)Seleccione la aseguradora de la poliza' } }),
        beneficiarios:ko.observableArray([]),
        tipo_contrato_id:ko.observable(''),//.extend({ required: { message: '(*)Seleccione' } })
        tipo_acta_id:ko.observable(''),// .extend({ required: { message: '(*)Seleccione el tipo de acta' } }),
        tipo_documento_id:ko.observable('').extend({ required: { message: '(*)Seleccione el tipo de documento asociado' } }),
        documento_id:ko.observable(''), //.extend({ validation: { validator: validar_ducumento, message: '(*)Seleccione el documento.' } }),
        numero_certificado:ko.observable('')
    }
    
   
    function validar_fecha_final(){

      var fecha_final=self.polizaVO.fecha_final(); 
      var fecha_inicio=self.polizaVO.fecha_inicio();
      if (fecha_inicio!=null && fecha_inicio!='' && fecha_final!=null && fecha_final!='') { 
        return  new Date(fecha_final) >= new Date(fecha_inicio);
      }else{
        return true;
      }      
    }

    function validar_ducumento(val){
      var tipo_acta_id=self.tipo_acta_id();
      if($('#hd_TipoActaNinguno').val()==tipo_acta_id && $('#hd_TipoActaNinguno').val()==tipo_acta_id && (val=='' || val==null)){
          return false;
      }
      return true;
    }

    self.polizaVO.tipo_acta_id.subscribe(function(val) {
      self.tipo_acta_id(val);
      self.polizaVO.documento_id('');
    });

    self.llenar_paginacion = function (data,pagina) {
        self.paginacion.pagina_actual(pagina);
        self.paginacion.total(data.count);       
        self.paginacion.cantidad_por_paginas(resultadosPorPagina);
        var buscados = (resultadosPorPagina * pagina) > data.count ? data.count : (resultadosPorPagina * pagina);
        self.paginacion.totalRegistrosBuscados(buscados);
    }

    self.exportar_excel=function(){      
      location.href=path_principal+"/poliza/exportar-polizas/?dato="+self.filtro()+"&contrato_id="+self.filtros.contrato_id()+"&tipo_id="+self.filtros.tipo_id();     
    }

    self.abrir_modal = function () {
        self.limpiar();
        self.titulo('Registrar Poliza');
        $('#modal_acciones').modal('show');
    }

    self.abrir_filtros=function(){
        self.consultar_select_filter_proyecto();
        $('#modal_filtros').modal('show');
    }
    self.consultar_select_filter_proyecto = function () {                         
        self.filtros.tipo_id(sessionStorage.getItem("app_tipo_contrato_poliza"||""));        
        self.filtros.contrato_id(sessionStorage.getItem("app_contrato_poliza"||""));        
    }             
    
    self.limpiar=function(){

      self.polizaVO.id(0);
      self.polizaVO.contrato_id($('#hd_contrato_id').val());
      self.polizaVO.tipo_id('');

      self.polizaVO.fecha_inicio('');
      self.polizaVO.fecha_final('');
      self.polizaVO.valor(0);
      self.polizaVO.observacion('');
      self.polizaVO.soporte('');
      self.polizaVO.amparo('');
      self.polizaVO.tomador('');
      self.polizaVO.numero('');
      self.polizaVO.reemplaza('');
      self.polizaVO.aseguradora_id('');
      self.polizaVO.beneficiarios([]);
      self.polizaVO.tipo_contrato_id('');
      self.polizaVO.documento_id('');
      self.polizaVO.tipo_acta_id('');
      self.polizaVO.tipo_documento_id('');
      self.polizaVO.numero_certificado('');

      self.polizaVO.contrato_id.isModified(false);
      self.polizaVO.tipo_id.isModified(false);
      self.polizaVO.fecha_inicio.isModified(false);
      self.polizaVO.fecha_final.isModified(false);
      self.polizaVO.valor.isModified(false);
      self.polizaVO.aseguradora_id.isModified(false);

      self.polizaVO.documento_id.isModified(false);
      self.polizaVO.tipo_acta_id.isModified(false);
      self.polizaVO.tipo_documento_id.isModified(false);
      
      $('#soporte').fileinput('reset');
      $('#soporte').val('');
    }

    self.limpiar_filtros=function(){
      self.filtros.contrato_id('0');
      self.filtros.tipo_id('0');
      self.filtros.tipo_contrato_id('');
      self.filtros.lista_contratos([]);
    }

    self.consultar = function (pagina) {
        if (pagina > 0) {           
            //self.buscado_rapido(true);
            self.filtro($('#txtBuscar').val());
            path =self.url + '?sin_paginacion=&lite=1&format=json&page='+pagina;
            parameter = { dato: self.filtro(), 
                contrato_id:self.filtros.contrato_id(),
                tipo_id:self.filtros.tipo_id()};
            RequestGet(function (datos, estado, mensage) {

                if (estado == 'ok' && datos!=null && datos.length > 0) {
                    
                    self.mensaje('');
                    //self.listado(results);  
                    self.listado(agregarOpcionesObservable(datos));                      
                    if (datos.length>0) {
                        $('#modal_filtros').modal('hide');
                    }

                } else {
                    self.listado([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                //self.llenar_paginacion(datos,pagina);
                
            }, path, parameter, function(){
                    cerrarLoading();                    
                   });
        }
    }
    
    self.consulta_enter = function (d,e) {
        if (e.which == 13) {
            self.consultar(1);
        }
        return true;
    }

    self.paginacion.pagina_actual.subscribe(function (pagina) {
        if (self.origen()=='poliza') {
            self.consultar(pagina);
          }else{
            self.consultar_poliza_contratos(pagina);
          }    
          
    });

    self.guardar=function(){

        if (self.polizaVO.tipo_documento_id() == '91') {
          self.polizaVO.documento_id('');
        }
    	   
        PolizaViewModel.errores.showAllMessages(); 
        if (self.polizaVO.beneficiarios()==null || self.polizaVO.beneficiarios().length==0) {
            $('#validacion_beneficiario').show();
            return;
        }else{
            $('#validacion_beneficiario').hide();
        }

        if (PolizaViewModel.errores().length==0) {

            var formData = new FormData();
            formData.append('contrato_id', self.polizaVO.contrato_id());
            formData.append('tipo_id', self.polizaVO.tipo_id());
            formData.append('fecha_inicio', self.polizaVO.fecha_inicio());
            formData.append('fecha_final', self.polizaVO.fecha_final());
            formData.append('valor', self.polizaVO.valor());
            formData.append('observacion', self.polizaVO.observacion());
            formData.append('soporte', self.polizaVO.soporte());
            formData.append('amparo', self.polizaVO.amparo());
            formData.append('tomador', self.polizaVO.tomador());
            formData.append('numero', self.polizaVO.numero());
            formData.append('reemplaza', self.polizaVO.reemplaza());
            formData.append('aseguradora_id', self.polizaVO.aseguradora_id());
            formData.append('beneficiarios', ko.toJSON(self.polizaVO.beneficiarios()));
            formData.append('tipo_contrato_id', self.polizaVO.tipo_contrato_id());
            formData.append('documento_id', self.polizaVO.documento_id());
            formData.append('tipo_acta_id', self.polizaVO.tipo_acta_id());
            formData.append('tipo_documento_id', self.polizaVO.tipo_documento_id());
            formData.append('numero_certificado', self.polizaVO.numero_certificado());
            
            if (self.polizaVO.id()==0) {
            	var parametros={           
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {  
                            $('#modal_acciones').modal('hide');              
                            self.consultar(1);                         
                         }
                      },//funcion para recibir la respuesta 
                      url:self.url,
                      parametros: formData,
                      completado:function(){
                        cerrarLoading();
                      }
                };
                       
                RequestFormData2(parametros);
            }else{
                var parametros={   
                      metodo:'PUT',                
                      callback:function(datos, estado, mensaje){
                         if (estado=='ok') {     
                            $('#modal_acciones').modal('hide');            
                            self.consultar(1);
                         }
                      },//funcion para recibir la respuesta 
                      url:self.url+ self.polizaVO.id() + '/',
                      parametros:self.polizaVO,
                      completado:function(){
                        cerrarLoading();
                      }
                };
                       
                Request(parametros);
            }
        } else {
            PolizaViewModel.errores.showAllMessages();//mostramos las validacion
        }

    }

    self.eliminar=function(){
         var lista=[];
        ko.utils.arrayForEach(self.listado(), function(p){          
          if (p.procesar()) {
            lista.push(p.id);
          }
        });
        
        RequestAnularOEliminar('¿Desea eliminar el(los) registro(s) seleccionado(s)?', 
          path_principal+'/poliza/eliminar_polizas/', {lista:lista}, 
          function(datos, estado, mensage){
             if (estado=='ok') {                     
                  self.consultar(self.paginacion.pagina_actual());                  
             }
        }, function(){

            cerrarLoading();
        
        }, false); 	
    }

    self.agregar_beneficiario=function(){

        if (self.nombre_beneficiario()!='') {
            self.polizaVO.beneficiarios.push({nombre:self.nombre_beneficiario()});
            self.nombre_beneficiario(''); 
        }   

        if (self.polizaVO.beneficiarios()==null || self.polizaVO.beneficiarios().length==0) {
            $('#validacion_beneficiario').show();
            return;
        }else{
            $('#validacion_beneficiario').hide();
        }
    }

    self.remover_beneficiario=function(obj){
        self.polizaVO.beneficiarios.remove(obj);
    }

    self.consultar_por_id = function (id) {
       
      // alert(obj.id)
       path =self.url+id+'/?format=json';
         RequestGet(function (datos, estado, mensage) {
           
            self.limpiar();
            self.titulo('Actualizar Poliza');
            
            self.polizaVO.tipo_contrato_id(datos.contrato.tipo_contrato.id);
            self.polizaVO.id(datos.id);                     
            self.polizaVO.tipo_id(datos.tipo.id);
                        
            self.contrato_id(datos.contrato.id);
            self.polizaVO.fecha_inicio(datos.fecha_inicio);
            self.polizaVO.fecha_final(datos.fecha_final);
            self.polizaVO.valor(datos.valor);
            self.polizaVO.observacion(datos.observacion);
            self.polizaVO.soporte(datos.soporte);
            self.polizaVO.amparo(datos.amparo);
            self.polizaVO.tomador(datos.tomador);
            self.polizaVO.numero(datos.vigencias[0].numero);
            self.polizaVO.reemplaza(datos.reemplaza);
            self.polizaVO.aseguradora_id(datos.vigencias[0].aseguradora.id);
            self.polizaVO.beneficiarios(agregarOpcionesObservable(convertToObservableArray(datos.vigencias[0].beneficiarios)));
                        
            $('#modal_acciones').modal('show');
         }, path, {}, function(){
                    cerrarLoading();
                   });

    }

    self.seleccionar_polizas.subscribe(function(val){
       ko.utils.arrayForEach(self.listado(),function(p){
          p.procesar(val);
       });
    });

    self.val2=0;
    self.consultar_contrato=function(val){

        if (val>0){
             path =path_principal +'/api/Contrato/?format=json&sin_paginacion';             
             parametros={id_tipo:val};
             RequestGet(function (datos, estado, mensage) {                
                if (estado=='ok') {                    
                    self.lista_contratos(datos);
                }               
             }, path, parametros,function(){                
                self.polizaVO.contrato_id(self.contrato_id());
                cerrarLoading();
               
             });
        }else{
            self.lista_contratos([]);
        }

    }

    self.filtros.tipo_contrato_id.subscribe(function(val){

        if (val>0){
             path =path_principal + '/api/Contrato/?format=json&sin_paginacion';
             parametros={id_tipo:val};
             RequestGet(function (datos, estado, mensage) {
               self.filtros.lista_contratos(datos);
             }, path, parametros, function(){
                    cerrarLoading();
                    self.filtros.contrato_id(val);
                   });
        }else{            
            self.filtros.contrato_id('');
        } 

    });

    self.setColorIconoFiltro = function (){
        app_tipo_contrato = sessionStorage.getItem("app_tipo_contrato_poliza"||self.filtros.tipo_id());
        app_contrato = sessionStorage.getItem("app_contrato_poliza"||self.filtros.contrato_id());          	       
      
        //alert(" color, tipo_contrato : " + tipo_contrato);
    	//alert(" color, estado_id : " + estado_id);
    	//alert(" color, contratista_id : " + contratista_id);
    	//alert(" color, mcontrato: "+mcontrato);

    	

        if ((app_tipo_contrato!='' && app_tipo_contrato != 0 && app_tipo_contrato != null) || 
        	(app_contrato != '' && app_contrato !=0 && app_contrato != null) 
        	){

            $('#iconoFiltro').addClass("filtrado");
        }else{
            $('#iconoFiltro').removeClass("filtrado");
        }
    }    

    self.consultar_contrato_por_tipo=function(val){

        if (val>0){
             path = path_principal + '/api/Contrato/?format=json';
             parametros={id_tipo:val, lite:4, sin_paginacion:0};             
             RequestGet(function (datos, estado, mensage) {                                
                if (estado=='ok') {                                    
                    self.filtros.lista_contratos(datos.data);
                }               
             }, path, parametros,function(){                
                self.filtros.tipo_id(val);
                cerrarLoading();
               
             });
        }else{
            self.filtros.lista_contratos([]);
            self.filtros.tipo_id('');
            self.filtros.contrato_id('');
        }

    }

    self.filtros.tipo_id.subscribe(function(val){        
        if (val>0){
            self.consultar_contrato_por_tipo(val);
            //sessionStorage.setItem("app_tipo_contrato_poliza", val || '');                        
            //  path =path_principal +'/api/Contrato/?format=json&sin_paginacion';
            //  parametros={id_tipo:val};
            //  RequestGet(function (datos, estado, mensage) {
            //    self.filtros.lista_contratos(datos);
            //  }, path, parametros, function(){
            //         cerrarLoading();
            //        });
        }else{
            self.filtros.lista_contratos([]);
            self.consultar_contrato_por_tipo(0);
        } 

    });
    self.filtros.contrato_id.subscribe(function(val){        
        if (val>0){
            self.filtros.contrato_id(val);
            //sessionStorage.setItem("app_contrato_poliza", val);            
        }else{
            self.filtros.contrato_id('');
        }

    });    
     self.cargar = function (pagina) {
        sessionStorage.setItem("app_tipo_contrato_poliza", self.filtros.tipo_id());
        sessionStorage.setItem("app_contrato_poliza", self.filtros.contrato_id());
        sessionStorage.setItem("dato_poliza", self.filtro());
        self.consultar_poliza_contratos(pagina);
     }   

     self.consultar_poliza_contratos = function (pagina) {                
        if (pagina > 0) {                      
            app_tipo_contrato = sessionStorage.getItem("app_tipo_contrato_poliza"||'');
            app_contrato = sessionStorage.getItem("app_contrato_poliza"||''); 
            self.filtros.tipo_id(app_tipo_contrato);
            self.filtros.contrato_id(app_contrato);        
            //self.buscado_rapido(true);            
            path =path_principal + '/api/Contrato/?lite=2&format=json&page='+pagina;
            parameter = { dato: self.filtro(), 
                id:app_contrato,
                id_tipo:app_tipo_contrato};
            RequestGet(function (datos, estado, mensage) {
                
                if (estado == 'ok' && datos.data!=null && datos.data.length > 0) {                    
                    self.mensaje('');
                    // var lista=[];                   
                    // var lista_id={};
                    // for (var i = 0; i < datos.data.length; i++) {
                    //     var obj=datos.data[i];                       
                    //     var r=ko.toJSON({'id':obj.contrato.id});                       
                    //     if(!(r in lista_id)){
                    //         lista_id[r]=obj.contrato.id;
                    //         lista.push(obj.contrato);
                    //     }
                    // }
                                                  
                    self.listado_poliza_contratos(datos.data);                     
                    self.setColorIconoFiltro();
                    if (datos.data.length>0) {
                        $('#modal_filtros').modal('hide');
                    }

                } else {

                    self.listado_poliza_contratos([]);
                    console.log(self.listado_poliza_contratos());
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                }

                self.llenar_paginacion(datos,pagina);
                
            }, path, parameter, function(){                    
                    cerrarLoading();
                   });
        }
    }

      self.consulta_poliza_contratos_enter = function (d,e) {
        if (e.which == 13) {
            self.filtro($('#txtBuscar').val());
            self.cargar(1);
        }
        return true;
    }

}

var poliza = new PolizaViewModel();
PolizaViewModel.errores=ko.validation.group(poliza.polizaVO);
$('#txtBuscar').val(sessionStorage.getItem("dato_poliza"))
ko.applyBindings(poliza);