function AsignacionProyectoViewModel(){
    
    var self = this;
    self.listado=ko.observableArray([]);
    self.mensaje=ko.observable('');
    self.mensaje2=ko.observable('');
    self.titulo=ko.observable('');
    self.filtro=ko.observable('');
    self.checkall=ko.observable(false);
    //self.titulo_tab=ko.observable('');
    self.checkall2=ko.observable(false);

    self.funcionario_id=ko.observable('');
    self.empresa=ko.observable('');
    self.cargo=ko.observable('');
    self.proyectoasociados=ko.observable();

    self.macrocontrato_select=ko.observable(0);
    self.contratista=ko.observable(0);
    self.departamento=ko.observable(0);
    self.municipio=ko.observable(0);

    self.macrocontrato_select2=ko.observable(0);
    self.contratista2=ko.observable(0);
    self.departamento2=ko.observable(0);
    self.municipio2=ko.observable(0);
    
    //self.tipos=ko.observableArray([]);
    //self.lista_otrosi_contrato=ko.observableArray([]);

    self.lista_cargo=ko.observableArray([]);
    self.lista_funcionario=ko.observableArray([]);

    self.lista_contrato=ko.observableArray([]);
    self.listado_contratista=ko.observableArray([]);
    self.departamento_select=ko.observableArray([]);
    self.listado_municipio=ko.observableArray([]);
    self.lista_proyecto=ko.observableArray([]);

    self.listado_contratista2=ko.observableArray([]);
    self.departamento_select2=ko.observableArray([]);
    self.listado_municipio2=ko.observableArray([]);
    self.lista_proyecto2=ko.observableArray([]);

    self.numero_c=ko.observable('');
    self.nombre_c=ko.observable('');
    self.tituloPanel=ko.observable('');
    self.contrato_id=ko.observable(0);

    self.mostrarasignados=ko.observable(false);

    self.tipo={
        contratoProyecto:ko.observable(8),
        interventoria:ko.observable(9),
        medida:ko.observable(10),
        retie:ko.observable(11),
        m_contrato:ko.observable(12),
        suministros:ko.observable(13),
        obra:ko.observable(14),
        otros:ko.observable(15)
    };

    self.guardar_proyecto = function () {
        var lista_id='';
        var count=0;
        ko.utils.arrayForEach(self.lista_proyecto(), function(d) {

            if(d.eliminado()==true){
                count=1;
                lista_id=lista_id+d.id+',';
            }
        });
        if (self.funcionario_id()!=0) {
            if(count==0){
                $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un proyecto para asociar.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                });
            }else{
                // parameter={ proyecto_id: lista_id, funcionario_id:self.funcionario_id()};
                parameter={ proyecto_id: lista_id, funcionario_id:self.funcionario_id()};
                path =path_principal+'/proyecto/crearfuncionarioproyecto/';
    
                RequestGet(function (data,success,message) {
                    if (success=='ok') {
                        mensajeExitoso(message);
                        self.list_proyecto2(1);
                        self.checkall(false);
                    }else{
                        mensajeError(message);
                    }
                    //console.log("nom:"+results);
                }, path, parameter);
            }            

        } else {
            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un funcionario para asignar un proyecto.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }
    }

    self.eliminar_proyecto = function () {
        var lista_id=[];
        var count=0;
        ko.utils.arrayForEach(self.lista_proyecto2(), function(d) {

            if(d.eliminado()==true){
                count=1;
                // lista_id=lista_id+d.id+',';
                lista_id.push({id:d.id})
            }
        });
        if(count==0){

            $.confirm({
                title:'Informativo',
                content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione un proyecto para eliminarlo.<h4>',
                cancelButton: 'Cerrar',
                confirmButton: false
            });
        }else{
            var path =path_principal+'/proyecto/eliminarfuncionarioproyecto/';
            var parameter = { lista: lista_id, funcionario_id:self.funcionario_id()};
            RequestAnularOEliminar("Esta seguro que desea eliminar los proyectos seleccionados?", path, parameter, function () {
                
                if (self.macrocontrato_select()!=0) {
                    self.list_proyecto2(1);
                }else{
                    self.list_proyecto2(0);
                }
                self.checkall2(false);
            })
        }
    }


    // OnChange de empresa
    self.empresa.subscribe(function (value) {
        if(value >0){

            self.list_cargo();
            self.list_funcionario();
        }else{
            self.lista_cargo([]);
            self.lista_funcionario([]);
            //self.departamento_select([]);
            //self.listado_municipio([]);
        }
    });

         // OnChange de cargo
    self.cargo.subscribe(function (value) {
        if(value >0){
            self.list_funcionario();
        }else{
            self.lista_funcionario([]);
            //self.departamento_select([]);
            //self.listado_municipio([]);
        }
    })

    // OnChange de funcionario_id
    self.funcionario_id.subscribe(function (value) {
        if(value >0){
            self.mostrarasignados(true);
            self.list_proyecto2(0);

        }else{
            self.mostrarasignados(false);
            //self.departamento_select([]);
            //self.listado_municipio([]);
        }
    })    

    // INICIO - GESTION DE PROYECTO
    // OnChange de m-contrato1
    self.macrocontrato_select.subscribe(function (value) {
        if(value >0){

            self.filtros3(value,0,self.departamento(),1);
        }else{
            //self.listado_contratista([]);
            self.departamento_select([]);
            self.listado_municipio([]);
        }
    });

    // OnChange de m-contrato2
    self.macrocontrato_select2.subscribe(function (value) {
        if(value >0){

            self.filtros3(value,self.contratista2(),self.departamento2(),2);
        }else{
            self.listado_contratista2([]);
            self.departamento_select2([]);
            self.listado_municipio2([]);
        }
    });

    // OnChange de contratista2
    self.contratista.subscribe(function (value) {
        if(value >0){

            self.filtros(self.macrocontrato_select(),value,1);
        }else{

            self.departamento_select([]);
            self.listado_municipio([]);
        }
    });    

    // OnChange de contratista2
    self.contratista2.subscribe(function (value) {
        if(value >0){

            self.filtros(self.macrocontrato_select2(),value,2);
        }else{

            self.departamento_select2([]);
            self.listado_municipio2([]);
        }
    });

    // OnChange de departamento1
    self.departamento.subscribe(function (value) {
        if(value >0){

            self.filtros2(self.macrocontrato_select(),value,1);
        }else{
            self.listado_municipio([]);
        }
    });

    // OnChange de departamento2
    self.departamento2.subscribe(function (value) {
        if(value >0){

            self.filtros2(self.macrocontrato_select2(),self.contratista2(),value,2);
        }else{
            self.listado_municipio2([]);
        }
    });

    self.filtros=function(contrato,contratista,num){
        tipos=self.tipo.contratoProyecto();
        path =path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+contrato+'&contratista='+contratista+'&tipo='+tipos;
        parameter='';
        RequestGet(function (results,count) {
            // num = 1 igual al buscador de proyectos de la izquierda y 2 = de la derecha
            if(num == 1){
                self.departamento_select(results.departamento);
                self.listado_municipio(results.municipio);
                //self.descargoVO.proyecto(results.proyecto);
            }else if(num == 2){
                self.departamento_select2(results.departamento);
                self.listado_municipio2(results.municipio);
            }
        }, path, parameter);
    }

    self.filtros2=function(contrato,contratista,departamento,num){
        tipos=self.tipo.contratoProyecto();
        path =path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+contrato+'&contratista='+contratista+'&departamento='+departamento+'&tipo='+tipos;
        parameter='';
        RequestGet(function (results,count) {

            if(num == 1){
                self.listado_contratista(results.contratista);
                self.listado_municipio(results.municipio);
                //self.descargoVO.proyecto(results.proyecto);
            }else if(num == 2){

                self.listado_municipio2(results.municipio);
            }
        }, path, parameter);
    }

    self.filtros3=function(contrato,contratista,departamento,num){
        tipos=self.tipo.contratoProyecto();

        path =path_principal+'/proyecto/filtrar_proyectos/?mcontrato='+contrato+'&departamento='+departamento+'&tipo='+tipos;
        if(contratista != 0){
            path += '&contratista='+contratista;
        }
        parameter={};

        RequestGet(function (results,count) {
            // num = 1 igual al buscador de proyectos de la izquierda y 2 = de la derecha
            if(num == 1){
                self.listado_contratista(results.contratista);
                self.departamento_select(results.departamento);
                self.listado_municipio(results.municipio);
            }else if(num == 2){
                self.listado_contratista2(results.contratista);
                self.departamento_select2(results.departamento);
                self.listado_municipio2(results.municipio);
            }
            //self.descargoVO.proyecto(results.proyecto);
        }, path, parameter);
    }

    self.list_proyecto=function(){

        path =path_principal+'/api/Proyecto/?lite=2';

        var contrato = self.macrocontrato_select();
        //var contratista = self.contratista();
        var departamento = self.departamento();
        var municipio = self.municipio();
        var lista = '';
        ko.utils.arrayForEach(self.lista_proyecto2(),function (p) {
            if (p.id){
                if(lista == ''){
                    lista = p.id;
                }else{
                    lista = lista+','+p.id;
                }
            }
        });
        self.proyectoasociados(lista);

        if(contrato == 0 ){
            mensajeInformativo('Seleccione una convocatoria');
        }else{
            path += '&contrato='+contrato;

            if(departamento != 0){
                path += '&departamento_id='+departamento;
            }
            if(municipio != 0){
                path += '&municipio_id='+municipio;
            }
            if(self.proyectoasociados() != null){
                path += '&listado='+self.proyectoasociados();
            }
            parameter = '';

            RequestGet(function (results,success,message) {

                if (success == 'ok' && results.data!=null && results.data.length > 0) {
                    self.mensaje('');
                    self.lista_proyecto(agregarOpcionesObservable(results.data));
                    
                } else {
                    self.lista_proyecto([]);
                    self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    //mensajeInformativo('No se encontraron registros');
                }
                //self.llenar_paginacion(datos,pagina);
            }, path, parameter);
        }
    }

    self.list_cargo=function(){
        path =path_principal+'/api/Cargo?lite=1&empresa_filtro='+self.empresa();
        parameter='';
            RequestGet(function (results,success,message) {

                if (success == 'ok' && results.data!=null && results.data.length > 0) {
                    self.mensaje('');
                    self.lista_cargo(agregarOpcionesObservable(results.data));
                } else {
                    self.lista_cargo([]);
                    //self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    //mensajeInformativo('No se encontraron registros');
                }
                //self.llenar_paginacion(datos,pagina);
            }, path, parameter);
    }

    self.list_funcionario=function(){
        path =path_principal+'/api/Funcionario?lite=1&empresa_filtro='+self.empresa();
        parameter={};
        if(self.cargo() > 0){
            parameter = {cargo: self.cargo()}
        }
        
            RequestGet(function (results,success,message) {

                if (success == 'ok' && results.data!=null && results.data.length > 0) {
                    self.mensaje('');
                    self.lista_funcionario(agregarOpcionesObservable(results.data));
                } else {
                    self.lista_funcionario([]);
                    //self.mensaje(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    //mensajeInformativo('No se encontraron registros');
                }
                //self.llenar_paginacion(datos,pagina);
            }, path, parameter);
    }        
        

    self.list_proyecto2=function(llamar_list_proy){

        path =path_principal+'/api/Proyecto/?lite=2';

        var contrato = self.macrocontrato_select2();
        var contratista = self.contratista2();
        var departamento = self.departamento2();
        var municipio = self.municipio2();
        var contrato_obra = self.contrato_id();

        //if(contrato == 0 || contratista == 0){
            //mensajeError('Seleccione un M-Contrato y un contratista');
        //}else{
            //path += 'contrato='+contrato+'&id_contratista='+contratista;
            if(contrato != 0){
                path += '&contrato='+contrato;
            }
            if(contratista != 0){
                path += '&id_contratista='+contratista;
            }
            if(departamento != 0){
                path += '&departamento_id='+departamento;
            }
            if(municipio != 0){
                path += '&municipio_id='+municipio;
            }
            if(contrato_obra != 0){
                path += '&contrato_obra='+contrato_obra;
            }

            if(self.funcionario_id() > 0){
                path += '&funcionario='+self.funcionario_id();
            }

            parameter = {};
            RequestGet(function (results,success,message) {
                
                if (success == 'ok' && results.data!=null && results.data.length > 0) {
                    self.mensaje2('');
                    self.lista_proyecto2(agregarOpcionesObservable(results.data));
                } else {
                    self.lista_proyecto2([]);
                    self.proyectoasociados([])
                    self.mensaje2(mensajeNoFound);//mensaje not found se encuentra el el archivo call-back.js
                    //mensajeInformativo('No se encontraron registros');
                }
                //self.llenar_paginacion(datos,pagina);
            }, path, parameter,function(){

                if(llamar_list_proy == 1){

                    if (self.macrocontrato_select()!=0) {
                        setTimeout(function(){
                            self.list_proyecto();
                            cerrarLoading()
                        },500)
                    }
                }
            });
        //}
    }

    self.checkall.subscribe(function(value ){

        ko.utils.arrayForEach(self.lista_proyecto(), function(d) {

            d.eliminado(value);
        });
    });

    self.checkall2.subscribe(function(value ){

        ko.utils.arrayForEach(self.lista_proyecto2(), function(d) {

            d.eliminado(value);
        });
    });
    // FIN - GESTION DE PROYECTO
}

var asignacionProyecto = new AsignacionProyectoViewModel();
//ContratoVigenciaViewModel.errores_vigencia = ko.validation.group(contratoVigencia.vigenciaVO);
//contratoVigencia.consultar_macrocontrato();//iniciamos la primera funcion

ko.applyBindings(asignacionProyecto);
