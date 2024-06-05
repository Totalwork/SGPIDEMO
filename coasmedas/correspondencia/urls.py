from django.conf.urls import url

from . import views, functions

urlpatterns = [
    
    # usuarios para correspondencia :  son usuarios de la empresa que puede ver una empresa
    url(r'^usuariosCorrespondencia/$', views.usuariosCorrespondencia, name='usuariosCorrespondencia'),

  	url(r'^correspondenciaEnviada/$', views.correspondenciaEnviada, name='correspondenciaEnviada.correspondenciaEnviada'),
    url(r'^correspondenciaEnviadaCreate/?(?P<proyecto_id>[0-9]+)?/?$', views.correspondenciaEnviadaCreate, name='correspondenciaEnviada.correspondenciaEnviadaCreate'),
    url(r'^correspondenciaEnviadaUpdate/?(?P<id>[0-9]+)?/?$', views.correspondenciaEnviadaUpdate, name='correspondenciaEnviada.correspondenciaEnviadaUpdate'),
    url(r'^correspondenciaEnviadaCopy/?(?P<id>[0-9]+)?/?$', views.correspondenciaEnviadaCopy, name='correspondenciaEnviada.correspondenciaEnviadaCopy'),

    url(r'^correspondenciaEnviadaConsecutivo/$', views.correspondenciaConsecutivos, name='correspondenciaEnviadaConsecutivo'),

  	url(r'^destroy_correspondenciaEnviada/$', views.destroyCorrespondenciaEnviada, name='destroy_correspondenciaEnviada'),
  	url(r'^establish_correspondenciaEnviada/$', views.establishCorrespondenciaEnviada, name='establish_correspondenciaEnviada'),
  	url(r'^reporte_correspondenciaEnviada/$', views.exportReporteCorrespondenciaEnviada, name='reporte_correspondenciaEnviada'),
  	url(r'^destroy_correspondenciaSoporte/$', views.destroyCorrespondenciaSoporte, name='destroy_correspondenciaSoporte'),

  	url(r'^list_contratosSinCorrespondenciaEnviada/$', views.listContratosSinCorrespondenciaEnviada, name='list_contratosSinCorrespondenciaEnviada'),
  	url(r'^list_correspondenciaEnviadaContrato/$', views.listCorrespondenciaEnviadaContrato, name='list_correspondenciaEnviadaContrato'),
  	url(r'^list_correspondenciaEnviadaProyecto/$', views.listCorrespondenciaEnviadaProyecto, name='list_correspondenciaEnviadaProyecto'),
  	url(r'^list_proyectosSinCorrespondenciaEnviada/$', views.listProyectosSinCorrespondenciaEnviada, name='list_proyectosSinCorrespondenciaEnviada'),
  	
  	url(r'^create_correspondenciaEnviada_contrato/$', views.createCorrespondenciaEnviadaContrato, name='create_correspondenciaEnviada_contrato'),#asociar correspondencias a contratos
  	url(r'^create_correspondenciaEnviada_proyecto/$', views.createCorrespondenciaEnviadaProyecto, name='create_correspondenciaEnviada_proyecto'),#asociar correspondencias a contratos

  	url(r'^destroy_correspondenciaEnviadaContrato/$', views.destroyCorrespondenciaEnviadaContrato, name='destroy_correspondenciaEnviadaContrato'),#asociar correspondencias a contratos
  	url(r'^destroy_correspondenciaEnviadaProyecto/$', views.destroyCorrespondenciaEnviadaProyecto, name='destroy_correspondenciaEnviadaProyecto'),#asociar correspondencias a contratos

    url(r'^generar_consecutivos/$', views.correspondenciaGenerarConsecutivos, name='correspondenciaGenerarConsecutivos'),# GENERA WORD PARA LAS CARTAS ENVIADAS
    url(r'^export_consecutivos_excel/$', views.donwloadFileConsecutivos, name='donwloadFileConsecutivos'),# GENERA WORD PARA LAS CARTAS ENVIADAS


    url(r'^createWord/$', functions.converToDocx, name='correspondencia.createWord'),# GENERA WORD PARA LAS CARTAS ENVIADAS
    url(r'^createPdf/$', functions.converToDocx, name='correspondencia.pdf'),# GENERA WORD PARA LAS CARTAS ENVIADAS
    url(r'^converToDocx/$', functions.converToDocx, name='correspondencia.docx'),# GENERA WORD PARA LAS CARTAS ENVIADAS


    # SELECT NECESARIO PARA EL REGISTRO DE CORRESPONDENCIA
    url(r'^parameter_select/$', views.datosRegistrarCorrespondencia, name='parameter_select'),# GENERA WORD PARA LAS CARTAS ENVIADAS
    url(r'^prefijo/$', views.correspondencia_prefijo, name='correspondencia.prefijo'),
    url(r'^eliminar_o_deshabilitar_prefijo/?(?P<id>[0-9]+)?/?$', views.eliminar_o_deshabilitar_prefijo, name='correspondencia.eliminar_o_deshabilitar_prefijo'),
    url(r'^consecutivo/$', views.correspondencia_consecutivo, name='correspondencia.correspondencia_consecutivo'),
    
    url(r'^plantilla/$', views.correspondencia_plantilla, name='correspondencia.plantilla'),
    url(r'^ver-soporte/$', views.VerSoporte, name='VerSoporte'),# descarga de archivos
    url(r'^soporte-descarga/$', views.VerSoporteSolicitudSoporte, name='SoporteDescarga'),# descarga de archivos para plantilla,    
]