from django.conf.urls import url

from . import views,tasks
from .schedules import schedules

urlpatterns = [
	url(r'^inicio/$', views.facturacion, name='factura.inicio'),
	url(r'^factura/$', views.factura, name='factura.factura'),
	url(r'^cesion/$', views.cesion, name='factura.cesion'),
	url(r'^descuento/$', views.descuento, name='factura.descuento'),
	url(r'^cruce/$', views.compensacion, name='factura.cruce'),
	
	# url(r'^cesion_economica/(?P<id_contrato>[0-9]+)/$', views.cesionEconomica, name='cesion_economica'),

	url(r'^list_anticipo/$', views.listAnticipo, name='list_anticipo'),

	url(r'^cambiar_estado_factura/$', views.cambiarEstadoFactura, name='cambiar_estado_factura'),
	url(r'^eliminar_cesion/$', views.destroyCesion, name='eliminar_cesion'),
	url(r'^eliminar_descuento/$', views.destroyDescuento, name='eliminar_descuento'),
	url(r'^guardar_planilla/$', views.guardarFacturaProyecto, name='guardar_planilla'),
	url(r'^eliminar_cruce/$', views.destroyCompensacion, name='eliminar_compensacion'),

	url(r'^excel_factura/$', views.exportReporteFactura, name='excel_factura'),
	url(r'^excel_cesion/$', views.exportReporteCesion, name='excel_cesion'),
	url(r'^excel_descuento/$', views.exportReporteDescuento, name='excel_descuento'),
	url(r'^excel_cruce/$', views.exportReporteCompensacion, name='excel_cruce'),
	url(r'^excel_cruce2/$', views.exportReporteCruce, name='excel_cruce2'),
	url(r'^excel_planilla/$', views.exportPlantilla, name='excel_planilla'),
	url(r'^pago_factura/$', views.guardar_pago_factura, name='factura.pago_factura'),
	url(r'^recursos_propios/$', views.pagoRecursosPropios, name='factura.recursos_propios'),
	url(r'^ver-soporte/$', views.VerSoporte, name='factura.VerSoporte'),# descarga de archivos
	url(r'^ver-soporte-cesion/$', views.VerSoporteCesion, name='factura.VerSoporteCesion'),
	url(r'^ver-soporte-descuento/$', views.VerSoporteDescuento, name='factura.VerSoporteDescuento'),

	#schedules
	url(r'^task/factura-sin-contabilizar/$', schedules.facturasSinContabilizar, name='factura.facturasSinContabilizar'),
]