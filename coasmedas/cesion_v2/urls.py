from django.conf.urls import url
from . import views

urlpatterns = [

	url(r'^cesion_v2/$', views.cesion_v2, name='cesion_v2.cesion_v2'),
	url(r'^detalle_cesion/(?P<id_cesion>[0-9]+)$', views.detalle_cesion, name='cesion_v2.detalle_cesion'),
	url(r'^detalle_proceso/(?P<id_cesion>[0-9]+)$', views.detalle_proceso, name='cesion_v2.detalle_proceso'),
	url(r'^verificacion_correo/$', views.verificacion_correo, name='cesion_v2.verificacion_correo'),
	url(r'^aprobacion_rechazo/$', views.aprobacion_rechazo, name='cesion_v2.aprobacion_rechazo'),
	url(r'^guardar_cesion/$', views.guardar_cesion, name='cesion_v2.guardar_cesion'),
	url(r'^validacion_cesion/$', views.validacion_cesion, name='cesion_v2.validacion_cesion'),
	url(r'^export_excel_cesiones/$', views.export_excel_cesiones, name='cesion_v2.export_excel_cesiones'),
	url(r'^listado_nombre_giro/$', views.listado_nombre_giro, name='cesion_v2.listado_nombre_giro'),
	url(r'^ver-soporte/$', views.VerSoporte, name='.cesion_v2.VerSoporte'),# descarga de archivos
	url(r'^ver-soporte-detalle/$', views.VerSoporteDetalle, name='.cesion_v2.VerSoporteDetalle'),# descarga de archivos
]