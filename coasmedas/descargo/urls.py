from django.conf.urls import url, include

from . import views#, tasks

urlpatterns = [
  	url(r'^descargo/$', views.descargo, name='descargo.descargo'),
  	url(r'^registroconsulta/$', views.registroconsulta, name='descargo.registro'),
  	url(r'^registrar/$', views.registro, name='descargo.registro_registrar'),
  	url(r'^registrarcopia/(?P<id>[0-9]+)/$', views.registrocc, name='descargo.registro_registrarcc'),
  	url(r'^editar/(?P<id>[0-9]+)/$', views.registro_editar, name='descargo.registro_registrar_editar'),
  	url(r'^completarregistro/(?P<id>[0-9]+)/$', views.completarregistro, name='descargo.completar_registro'),
  	url(r'^actualizarnodescargo/$', views.actualizar_nodescargo, name='descargo.actualizar_no_descargo'),
  	url(r'^actualizarestado/$', views.actualizar_estado, name='descargo.actualizarestado'),
  	url(r'^completarestado/$', views.estado_completar, name='descargo.completarestado'),
    url(r'^mapaDescargo/$', views.mapadescargo, name='descargo.mapa'),
    url(r'^correoDescargo/$', views.correodedescargo, name='descargo.correo'),
    url(r'^excel_descargo/$', views.exportReporteDescargo, name='excel_descargo'),
  	url(r'^chaining/', include('smart_selects.urls')),
    url(r'^eliminar_id/$', views.eliminar_varios_id, name='descargo.eliminar_id'),
    url(r'^ver-soporte/$', views.VerSoporte, name='descargo.VerSoporte'),# descarga de archivos
		# url(r'^notificar_descargo/$', tasks.NotificacionDescargoFuncionario, name='notificar_descargo'),
]