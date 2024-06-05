from django.conf.urls import url

from . import views


urlpatterns = [

	url(r'^indicador_calidad/$', views.indicador, name='indicador.indicador_calidad'),
	url(r'^seguimiento_indicador/(?P<id_indicador>[0-9]+)/$', views.seguimientoIndicador, name='indicador.seguimiento_indicador'),
	url(r'^eliminar_indicador/$', views.eliminar_varios_id, name='indicador.eliminar_indicador'),
	url(r'^exportar_indicador/$', views.export_excel_indicadores, name='indicador.exportar_indicador'),
	url(r'^eliminar_seguimiento/$', views.eliminar_varios_seguimiento, name='indicador.eliminar_seguimiento'),
	url(r'^exportar_seguimiento/$', views.export_excel_seguimiento, name='indicador.exportar_seguimiento'),
	
]