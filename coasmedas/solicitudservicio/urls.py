from django.conf.urls import url
from . import views


urlpatterns = [
	url(r'^solicitud/$', views.servicio_solicitud, name='serviciosolicitud.servicio_solicitud'),
	url(r'^eliminar_solicitudes/$', views.eliminar_solicitudes, name='serviciosolicitud.eliminar_solicitudes'),	
	url(r'^solicitud/mispendientes/$', views.mis_pendientes, name='serviciosolicitud.mis_pendientes'),	
]