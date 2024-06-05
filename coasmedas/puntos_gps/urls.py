from django.conf.urls import url

from . import views


urlpatterns = [

	url(r'^gps/$', views.puntos_gps, name='puntos.gps'),
	url(r'^listado_gps/(?P<id_proyecto>[0-9]+)/$', views.listado_gps, name='puntos.listado_gps'),
	url(r'^eliminar_gps/$', views.eliminar_varios_id, name='puntos.eliminar_gps'),
	url(r'^exportar/$', views.export_excel_gps, name='exportar'),
	url(r'^mapa/(?P<id_proyecto>[0-9]+)/$', views.mapa_proyecto, name='puntos.mapa'),
	url(r'^carga_masiva/$', views.cargar_excel, name='puntos.carga_masiva'),
	url(r'^descargar_plantilla/$', views.descargar_plantilla, name='puntos.descargar_plantilla'),
	url(r'^ubicacion/$', views.ubicacion, name='ubicacion.proyecto'),
	
]