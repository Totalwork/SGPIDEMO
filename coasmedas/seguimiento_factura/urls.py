from django.conf.urls import url
from . import views, tasks


urlpatterns = [
	url(r'^index/$', views.index_seguimiento, name='seguimiento_factura.index'),
	url(r'^habilitar-testOp/$', views.habilitar_testOp, name='seguimiento_factura.habilitar-testOp'),
	url(r'^deshabilitar-factura/$', views.actualizar_orden_factura, name='seguimiento_factura.deshabilitar-factura'),
	url(r'^pago_factura/$', views.pago_factura, name='seguimiento_factura.pago_factura'),

	url(r'^deshabilitar-testOp/$', views.deshabilitar_testOp, name='seguimiento_factura.deshabilitar-testOp'),
	url(r'^exportar_factura_vencida/$', views.export_factura_vencidas, name='seguimiento_factura.exportar_factura_vencida'),
	url(r'^test_op/$', views.test_op, name='seguimiento_factura.test_op'),
	url(r'^lista_contrato/$', views.listado_contrato, name='seguimiento_factura.lista_contrato'),
	url(r'^gestion-op/$', views.gestion_op, name='seguimiento_factura.gestion-op'),
	url(r'^gestion-op-recursos-propios/$', views.gestion_op_recursos_propios, name='seguimiento_factura.gestion-op-recursos-propios'),
	url(r'^consulta-factura-pagada/$', views.consulta_factura_pagada, name='seguimiento_factura.consulta-factura-pagada'),
	url(r'^listado-pagos/(?P<id_pago>[0-9]+)/$', views.listado_factura_pagada, name='seguimiento_factura.listado-pagos'),
	url(r'^lista_pagos_gestion/$', views.listado_de_pagos, name='seguimiento_factura.lista_pagos_gestion'),
	url(r'^consulta-pago-factura/$', views.consulta_pago_factura, name='seguimiento_factura.consulta-pago-factura'),
	url(r'^exportar_gestion_op/$', views.export_gestion_op, name='seguimiento_factura.exportar_gestion_op'),
	url(r'^consulta-pago-factura-recursos-propios/$', views.consulta_pago_factura_recursos_propios, name='seguimiento_factura.consulta-pago-factura-recursos-propios'),
	url(r'^carga-masiva/$', views.carga_masiva, name='seguimiento_factura.carga-masiva'),
	url(r'^leer_excel/$', views.consulta_excel, name='seguimiento_factura.leer_excel'),
	url(r'^actualizar_excel/$', views.actualizar_excel, name='seguimiento_factura.actualizar_excel'),
	url(r'^actualizar_conflicto/$', views.actualizar_conflicto, name='seguimiento_factura.actualizar_conflicto'),
	url(r'^descargar_plantilla/$', views.descargar_plantilla, name='seguimiento_factura.descargar_plantilla'),

	url(r'^filtro_contrato_pago/$', views.filtro_consultar_contrato_pago, name='seguimiento_factura.filtro_contrato_pago'),
	url(r'^filtro_contratista_pago/$', views.filtro_consultar_contratista_pago, name='seguimiento_factura.filtro_contratista_pago'),

	url(r'^administrador-cuenta/$', views.administrador_cuenta, name='seguimiento_factura.administrador-cuenta'),
	url(r'^export-factura-pagadas/$', views.export_factura_pagadas, name='seguimiento_factura.export-factura-pagadas'),
	url(r'^generar-reporte/$', views.generar_reporte, name='seguimiento_factura.generar-reporte'),


	# LUIS MENDOZA
	url(r'^facturas-por-contabilizar/$', views.facturas_por_contabilizar, name='seguimiento_factura.facturas_por_contabilizar'),
	url(r'^facturas-por-pagar/$', views.facturas_por_pagar, name='seguimiento_factura.facturas_por_pagar'),
	url(r'^exportar-facturas_por-contabilizar/$', views.exportar_facturas_por_contabilizar, name='seguimiento_factura.exportar_facturas_por_contabilizar'),
	url(r'^actualizar-codigo-compensacion/$', views.actualizar_codigo_compensacion, name='seguimiento_factura.actualizar_codigo_compensacion'),
	url(r'^actualizar-pago-factura/$', views.actualizar_pago_factura, name='seguimiento_factura.actualizar_pago_factura'),
	url(r'^export-factura/$', views.export_factura, name='seguimiento_factura.export-factura'),
	url(r'^exportar_gestion_op_recursos_propios/$', views.exportar_gestion_op_recursos_propios, name='seguimiento_factura.exportar_gestion_op_recursos_propios'),
	# facturas a pagar con recursos propios
	url(r'^exportar-facturas-recursos-propios/$', views.exportar_facturas_recursos_propios, name='seguimiento_factura.exportar-facturas-recursos-propios'),
	# anular pagos
	url(r'^anular-pago-compensacion/$', views.anular_pago_compensacion, name='seguimiento_factura.anular-pago-compensacion'),

	# url(r'^test-task/$', tasks.seguimientoTestTask, name='factura.facturaTestTask'),
]