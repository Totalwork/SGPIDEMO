from django.conf.urls import url

from . import views


urlpatterns = [

 	
 	url(r'^configuracion/$', views.configuracion, name='servidumbre.configuracion'),	


 	url(r'^home/$', views.expediente, name='servidumbre.expediente'),
 	url(r'^expediente/(?P<id>[0-9]+)$', views.expedientes, name='servidumbre.expedientes'),
 	url(r'^nuevoexpediente/$', views.nuevo_expediente, name='servidumbre.nuevo_expediente'),
 	url(r'^editarexpediente/(?P<id>[0-9]+)$', views.editar_expediente, name='servidumbre.editar_expediente'),
 	url(r'^reporte_expedientes/$', views.exportReporteExpedientes, name='reporte_expedientes'),

 	
 	
 	url(r'^predios/(?P<id>[0-9]+)/$', views.predios, name='servidumbre.predios'),
 	url(r'^predio/(?P<id>[0-9]+)/(?P<pk>[0-9]+)/$', views.predio, name='servidumbre.predio'),
 	url(r'^nuevopredio/(?P<id>[0-9]+)/$', views.nuevo_predio, name='servidumbre.nuevo_predio'),
 	url(r'^editarpredio/(?P<id>[0-9]+)/(?P<pk>[0-9]+)/$', views.editar_predio, name='servidumbre.editar_predio'),
 	url(r'^reporte_predios/$', views.exportReportePredios, name='reporte_predios'),
 	
 	url(r'^documentos/(?P<id>[0-9]+)/(?P<pk>[0-9]+)/$', views.documentos, name='servidumbre.predio_documentos'),
 	
 	url(r'^cerrar_expedientes/$', views.cerrar_expedientes, name='servidumbre.cerrar_expedientes'),
 	url(r'^reabrir/(?P<pk>[0-9]+)$', views.reabrir, name='servidumbre.rearbrir'),
 	url(r'^cerrar/(?P<pk>[0-9]+)$', views.cerrar, name='servidumbre.cerrar'),

 	url(r'^eliminar_grupos/$', views.eliminar_grupos, name='servidumbre.eliminar_grupos'),
 	url(r'^eliminar_documentos/$', views.eliminar_documentos, name='servidumbre.eliminar_documentos'),
 	url(r'^eliminar_predios/$', views.eliminar_predios, name='servidumbre.eliminar_predios'),

 	url(r'^ver-soporte/$', views.VerSoporte, name='servidumbre.VerSoporte'),
 	
 	url(r'^select-create-update-predio/$', views.select_create_update_predio, 
 		name='servidumbre.select_create_update_predio'),

 	url(r'^documentospredio/$', views.documentos_predio, name='servidumbre.documentos_predio'),
 	url(r'^guardar_archivo/$', views.guardar_archivo, name='servidumbre.guardar_archivo'),

 	url(r'^expediente-georeferencias/(?P<id>[0-9]+)$', views.expediente_georeferencias, name='servidumbre.expediente_georeferencias'),
	url(r'^predio-georeferencias/(?P<id>[0-9]+)/(?P<pk>[0-9]+)/$', views.predio_georeferencias, name='servidumbre.predio_georeferencias'),
	
	url(r'^descargar-plantilla-georeferencias/$', views.descargar_plantilla_georeferencias, name='servidumbre.descargar_plantilla_georeferencias'),

	url(r'^guardar-coordenadas-archivo/$', views.guardar_coordenadas_archivo, name='servidumbre.guardar_coordenadas_archivo'),

	url(r'^guardar-cambio-cantidades/$', views.guardar_cambio_cantidades, name='servidumbre.guardar_cambio_cantidades'),
	url(r'^consultar_predios_coordenadas/$', views.consultar_predios_coordenadas, name='servidumbre.consultar_predios_coordenadas'),

	url(r'^graficas/$', views.graficas, name='servidumbre.graficas'),
	url(r'^obtenerdatosgraficas/$', views.get_dataGraph, name='servidumbre.obtener_datosGraficas'),
]


