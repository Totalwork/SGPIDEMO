from django.conf.urls import url

from . import views


urlpatterns = [
	url(r'^cuenta/$', views.financiero_cuenta, name='financiero_cuenta.cuenta'),
	url(r'^cuenta_moviento/(?P<id_cuenta>[0-9]+)/$', views.financiero_movimiento, name='financiero_movimiento.cuenta_moviento'),
	url(r'^eliminar_cuenta/$', views.eliminar_varios_id, name='financiero_cuenta.eliminar_cuenta'),
	url(r'^eliminar_movimiento/$', views.eliminar_varios_id_movimiento, name='financiero_movimiento.eliminar_movimiento'),
	url(r'^exportar/$', views.export_excel_cuenta, name='exportar'),
	url(r'^exportar_movimiento/$', views.export_excel_movimiento, name='exportar_movimiento'),
	url(r'^deshabilitar-cuenta/$', views.actualizar_estado_cuenta, name='seguimiento_factura.deshabilitar-cuenta'),
	url(r'^informe_financiero/$', views.informe_financiero, name='financiero_movimiento.informe_financiero'),
	url(r'^descargar_informe_financiero/$', views.descargar_informe_financiero, name='financiero_movimiento.descargar_informe_financiero'),
	url(r'^index_informe/$', views.index_informe, name='financiero_movimiento.index_informe'),
	url(r'^informe_financiero_contratista/$', views.informe_financiero_contratista, name='financiero_movimiento.informe_financiero_contratista'),
	url(r'^descargar_informe_financiero_contratista/$', views.descargar_informe_financiero_contratista, name='financiero_movimiento.descargar_informe_financiero_contratista'),
	url(r'^reporte_pago/$', views.reporte_pago, name='financiero_movimiento.reporte_pago'),
	url(r'^descargar_reporte_pago/$', views.descargar_reporte_pago, name='financiero_movimiento.descargar_reporte_pago'),
	url(r'^informe_anticipos/$', views.informe_anticipos, name='financiero_movimiento.informe_anticipos'),
	url(r'^descargar_informe_anticipos/$', views.descargar_informe_anticipos, name='financiero_movimiento.descargar_informe_anticipos'),
	url(r'^informe_financiero_origen/$', views.informe_financiero_origen, name='financiero_movimiento.informe_financiero_origen'),
	url(r'^descargar_informe_financiero_origen/$', views.descargar_informe_financiero_origen, name='financiero_movimiento.descargar_informe_financiero_origen'),
	url(r'^ver-soporte/$', views.VerSoporte, name='VerSoporte'),
	url(r'^encabezado/$', views.Financiero_encabezado, name='VerSoporte'),
	
	
]