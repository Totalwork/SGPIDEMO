from django.conf.urls import url

from . import views
from .schedules import schedules

urlpatterns = [

	url(r'^procesos/$', views.procesos, name='proceso.procesos'),
	url(r'^seguimiento/$', views.procesoSeguimiento, name='proceso.procesoSeguimiento'),
	url(r'^itemsProceso/(?P<id>[0-9]+)/$', views.itemsProcesos, name='proceso.itemsProcesos'),

	url(r'^detalleSeguimientoProceso/(?P<id>[0-9]+)/$', views.detalleSeguimientoProcesos, 
		
		name='proceso.procesoDetalleSeguimiento'),
	url(r'^detalleSeguimientoProcesoDatos/(?P<id>[0-9]+)/$', views.detalleSeguimientoProcesosDatos, 
		name='proceso.procesoDetalleSeguimientoDatos'),
	url(r'^implementacion/(?P<id>[0-9]+)/$', views.implementacion, name='proceso.implementacion'),
	url(r'^implementacion/(?P<id>[0-9]+)/(?P<lista>[\w\-]+)$', views.implementar, name='proceso.implementar'),
	url(r'^implementacion/implementar/$', views.implementar, name='proceso.implementar'),
	url(r'^detalleSeguimientoProcesoDatos/asignarNotificacion/$', views.asignarNotificacion, 
		name='proceso.asignarNotificacion'),
	url(r'^detalleSeguimientoProcesoDatos/quitarNotificacion/$', views.quitarNotificacion, 
		name='proceso.quitarNotificacion'),
	url(r'^implementacion/quitarImplementacion/$', views.quitarImplementacion, name='proceso.quitarImplementacion'),
	url(r'^detalleSeguimientoProcesoDatos/guardarCambios/$', views.guardarCambios, name='procesoRelacionDatos.guardarCambios'),
	url(r'^exportarxls/$', views.exportarExcel, name='proceso.exportarExcel'),
	url(r'^responsables/(?P<id>[0-9]+)/$', views.responsables, name='proceso.responsables'),
	url(r'^responsables/guardarCambios/$', views.responsablesGuardarCambios, name='item.responsablesGuardarCambios'),
	url(r'^solicitudServicioSeguimiento/(?P<id>[0-9]+)/$', views.detalleSeguimientoProcesosDatosSolicitud, 
		name='proceso.procesoDetalleSeguimientoDatos'),
	url(r'^solicitudServicioSeguimientoC/(?P<id>[0-9]+)/$', views.ConfigurarSeguimiento, 
		name='proceso.ConfigurarSeguimiento'),
	url(r'^implementacion/retiesimple/(?P<id>[0-9]+)/$',
	 views.ImplementarRetieSimple, name='proceso.implementarRetieSimple'),
	#url(r'^vigencia/$', views.vencimientoItems, name='proceso.vigencia'),
	url(r'^ver-soporte/$', views.VerSoporte, name='VerSoporte'),# descarga de archivos

	#schedules
	url(r'^task/vencimiento-items/$', schedules.vencimientoItems, name='proceso.vencimientoItems'),
]