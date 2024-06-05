
function InformeViewModel() {
	
	var self = this;
	self.listado=ko.observableArray([]);
	self.mensaje=ko.observable('');
	self.titulo=ko.observable('');
	self.filtro=ko.observable('');
    self.checkall=ko.observable(false); 

    var fecha=new Date();

    self.informeVO={
        id_contrato:ko.observable('').extend({ required: { message: '(*)Seleccione un contrato' } }),
        desde:ko.observable('').extend({ required: { message: '(*)Seleccione un mes' } }),
        hasta:ko.observable('').extend({ required: { message: '(*)Seleccione un mes' } }),
        ano:ko.observable(fecha.getFullYear()).extend({ required: { message: '(*)Seleccione un ano' } }),
        firma:ko.observable(0)
    }


   

    self.excel_verificar_datos=function(){

        if (InformeViewModel.errores_informe().length == 0) {//se activa las validaciones

            location.href=path_principal+"/informe_ministerio/excel_verificar_datos?contrato_id="
            +self.informeVO.id_contrato()+"&desde="+self.informeVO.desde()+"&hasta="+self.informeVO.hasta()+"&ano="+self.informeVO.ano();

        }else{

            InformeViewModel.errores_informe.showAllMessages();//mostramos las validacion
        }
    }


    self.generar_informe=function(){

        if (InformeViewModel.errores_informe().length == 0) {//se activa las validaciones

            if(self.informeVO.firma()==''){

                 $.confirm({
                    title:'Informativo',
                    content: '<h4><i class="text-info fa fa-info-circle fa-2x"></i>Seleccione una firma para generar el informe.<h4>',
                    cancelButton: 'Cerrar',
                    confirmButton: false
                    });
            }else{

                 location.href=path_principal+"/informe_ministerio/generar_informe?contrato_id="
                +self.informeVO.id_contrato()+"&desde="+self.informeVO.desde()+"&hasta="+self.informeVO.hasta()
                +"&ano="+self.informeVO.ano()+"&firma="+self.informeVO.firma()+"&empresa_id="+$("#id_empresa").val();

                 self.limpiar();
            }

        }else{

            InformeViewModel.errores_informe.showAllMessages();//mostramos las validacion
        }
    }
   
    // //limpiar el modelo 
     self.limpiar=function(){  

        var fecha=new Date();
        self.informeVO.id_contrato('');
        self.informeVO.id_contrato.isModified(false);
        self.informeVO.desde('');
        self.informeVO.desde.isModified(false);
        self.informeVO.hasta('');
        self.informeVO.hasta.isModified(false);
        self.informeVO.ano(fecha.getFullYear());
        self.informeVO.ano.isModified(false);
        self.informeVO.firma(0);

     }

   


    // //funcion guardar




 }

var informe = new InformeViewModel();
InformeViewModel.errores_informe = ko.validation.group(informe.informeVO);
var content= document.getElementById('content_wrapper');
var header= document.getElementById('header');
ko.applyBindings(informe,content);
ko.applyBindings(informe,header);