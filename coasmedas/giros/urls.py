from django.conf.urls import url

from . import views
from .schedules import schedules

urlpatterns = [
	url(r'^encabezado_giro/$', views.giros, name='giros.encabezado_giro'),
	url(r'^detalle_giro/(?P<id_encabezado>[0-9]+)/(?P<mcontrato>[0-9]+)/(?P<contrato>[0-9]+)/$', views.detalle_giros, name='giros.detalle_giro'),
	url(r'^eliminar_id/$', views.eliminar_varios_id, name='giros.eliminar_id'),
	url(r'^actualizar_no_radicado/$', views.actualizar_radicado, name='giros.actualizar_no_radicado'),
	url(r'^eliminar_id_detalle/$', views.eliminar_varios_id_detalle, name='giros.eliminar_id_detalle'),
	url(r'^encabezado_detalle/$', views.encabezado_detalle_giro, name='giros.encabezado_detalle'),
	url(r'^pago_detalle/$', views.guardar_pago_detalle, name='giros.pago_detalle'),
	url(r'^exportar_detalle_giro/$', views.export_excel_detalle_giro, name='giros.exportar_detalle_giro'),
	url(r'^reversar_giros/$', views.reversar_giros, name='giros.reversar_giros'),
	url(r'^autorizar_giros/$', views.autorizar_giros, name='giros.autorizar_giros'),
	url(r'^exportar_encabezado_giro/$', views.export_excel_encabezado_giro, name='giros.exportar_encabezado_giro'),
	url(r'^reporte_giro_exportar/$', views.export_reporte_giro, name='giros.reporte_giro_exportar'),
	url(r'^consultar_excel/$', views.consulta_excel, name='giros.consultar_excel'),
	url(r'^consultar_procesos/$', views.consultar_procesos, name='giros.consultar_procesos'),
	url(r'^guardar_procesos/$', views.guardar_proceso, name='giros.guardar_procesos'),
	url(r'^actualizar_estado_detalle/$', views.Actualizar_detalle_giro_segun_consecutivo, name='giros.actualizar_estado_detalle'),
	url(r'^reporte_anticipo/$', views.generar_reporte_solicitud_anticipo, name='giros.reporte_anticipo'),
	url(r'^detalle_giro_lectura/(?P<id_encabezado>[0-9]+)/(?P<mcontrato>[0-9]+)/(?P<contrato>[0-9]+)/$', views.detalle_giros_solo_lectura, name='giros.detalle_giro_lectura'),
	url(r'^cargar_soporte/$', views.cargar_soporte_proceso, name='giros.cargar_soporte'),
	url(r'^desautorizar_giros/$', views.desautorizar_giros, name='giros.desautorizar_giros'),
	url(r'^update_tipo_pago_del_giro/$', views.updateTipoPagoGiro, name='giros.update_tipo_pago_del_giro'),
	url(r'^update_disparar_flujo/$', views.updateDispararFlujo, name='giros.update_disparar_flujo'),
	url(r'^descargar_plantilla/$', views.descargar_plantilla, name='giros.descargar_plantilla'),
	url(r'^reporte_anticipo2/$', views.generar_reporte_solicitud_anticipo2, name='giros.reporte_anticipo2'),

	url(r'^validar_estado_cuenta/$', views.validar_estado_cuenta, name='giros.validar_estado_cuenta'),#indica si la cuenta tiene dinero
	url(r'^ver-soporte/$', views.VerSoporte, name='giros.VerSoporte'),# descarga de archivos
	url(r'^ver-soporteconsecutivodeshabilitado/$', views.VerSoporteConsecutivoDeshabilitado, name='detalleGiros.VerSoporteDeshabilitado'),
	url(r'^validacion_giro/$', views.validacion_giro, name='giros.validacion_giro'),

	# schecules
	url(r'^task/envio-giro-por-contabilizar/$', schedules.envioCorreoGiroPorContabilizar, name='giros.envioCorreoGiroPorContabilizar'),
	url(r'^task/envio-giro-por-contabilizar-procesar/$', schedules.envioCorreoGiroPorContabilizarProcesar, name='giros.envioCorreoGiroPorContabilizarProcesar'),
	url(r'^task/envio-correo-ordenpago-procesar$', schedules.envioCorreoOrdenPagoProcesar, name='giros.envioCorreoOrdenPagoProcesar'),

]