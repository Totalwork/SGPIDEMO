from django.conf.urls import url

from . import views


urlpatterns = [
	
	url(r'^index/$', views.index_control_cambio, name='control_cambios.index'),
	url(r'^configurar_unidades_constructivas/$', views.ConfigurarUnidadesConstructivas, name='control_cambios.configurar_unidades_constructivas'),
	url(r'^cambio_obra/$', views.CambiosObra, name='control_cambios.cambio_obra'),
	url(r'^mis_solicitudes/$', views.MisSolicitudes, name='control_cambios.mis_solicitudes'),
	url(r'^eliminar_unidad_constructiva/$', views.eliminar_unidad_constructiva, name='control_cambios.eliminar_unidad_constructiva'),
	url(r'^exportar_unidad_constructiva/$', views.export_excel_unidades_constructivas, name='exportar_unidad_constructiva'),
	url(r'^administrar_uucc/(?P<id_proyecto>[0-9]+)/$', views.AdministrarUUCC, name='control_cambios.administrar_uucc'),
	url(r'^eliminar_cambio_uucc/$', views.eliminar_cambio_uucc, name='control_cambios.eliminar_cambio_uucc'),
	url(r'^agregar_uucc/(?P<id_proyecto>[0-9]+)/(?P<id_cambio>[0-9]+)/(?P<id_contrato>[0-9]+)/$', views.AgregarUUCC, name='control_cambios.agregar_uucc'),
	url(r'^actualizar_cantidad/$', views.actualizar_cantidad_cambio_proyecto, name='control_cambios.actualizar_cantidad'),
	url(r'^eliminar_cambio_proyecto/$', views.eliminar_cambio_proyecto, name='control_cambios.eliminar_cambio_proyecto'),
	url(r'^actualizar_todo_agregar_uucc/$', views.actualizar_todo_agregar_uucc, name='control_cambios.actualizar_todo_agregar_uucc'),
	url(r'^cargar_soporte_uucc/$', views.cargar_soporte_uucc_cambio, name='control_cambios.cargar_soporte_uucc'),
	url(r'^eliminar_soporte_uucc/$', views.eliminar_soporte_uucc_cambio, name='control_cambios.eliminar_soporte_uucc'),
	url(r'^carga_masiva_cambio/$', views.cargar_excel_masivo_cambio, name='control_cambios.carga_masiva_cambio'),
	url(r'^comparar/(?P<id_proyecto>[0-9]+)/$', views.Comparar, name='control_cambios.comparar'),
	url(r'^lista_comparar/$', views.lista_comparar, name='control_cambios.lista_comparar'),
	url(r'^exportar_reporte_comparar/$', views.export_reporte_comparar, name='exportar_reporte_comparar'),
	url(r'^carga_masiva_excel/$', views.cargar_excel_unidades_constructivas, name='control_cambios.carga_masiva_excel'),
	url(r'^descargar_plantilla_uucc/$', views.descargar_plantilla_agregaruucc, name='control_cambios.descargar_plantilla_uucc'),
	url(r'^detalle_solicitud/(?P<id_proyecto>[0-9]+)/(?P<id_cambio>[0-9]+)/$', views.DetalleSolicitud, name='control_cambios.detalle_solicitud'),
	url(r'^lista_detalle/$', views.lista_detalle_solicitud, name='control_cambios.lista_detalle'),
	url(r'^exportar_reporte_detalle_solocitud/$', views.export_reporte_detalle_solicitud, name='exportar_reporte_detalle_solocitud'),
	url(r'^actualizar_estado_cambio_proyecto/$', views.actualizar_estado_mis_solicitudes, name='control_cambios.actualizar_estado_cambio_proyecto'),
	url(r'^descargar_plantilla_configuracion/$', views.descargar_plantilla_unidadesConstructiva, name='control_cambios.descargar_plantilla_configuracion'),

]