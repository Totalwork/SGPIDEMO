from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^no_conformidad/$', views.no_conformidad, name='no_conformidad.no_conformidad'),

	url(r'^eliminar_no_conformidad/$', views.destroyNoConformidad, name='eliminar_no_conformidad'),
	url(r'^excel_no_conformidad/$', views.exportReporteNoConformidad, name='excel_no_conformidad'),
	url(r'^word_no_conformidad/$', views.exportReporteWordNoConformidad, name='word_no_conformidad'),
	# url(r'^factura/$', views.factura, name='factura.factura'),
	# url(r'^cesion/$', views.cesion, name='factura.cesion'),
	# url(r'^descuento/$', views.descuento, name='factura.descuento'),
	# url(r'^cruce/$', views.compensacion, name='factura.cruce'),
	
	# # url(r'^cesion_economica/(?P<id_contrato>[0-9]+)/$', views.cesionEconomica, name='cesion_economica'),

	# url(r'^list_anticipo/$', views.listAnticipo, name='list_anticipo'),

	# url(r'^cambiar_estado_factura/$', views.cambiarEstadoFactura, name='cambiar_estado_factura'),
	# url(r'^eliminar_descuento/$', views.destroyDescuento, name='eliminar_descuento'),
	# url(r'^guardar_planilla/$', views.guardarFacturaProyecto, name='guardar_planilla'),
	# url(r'^eliminar_cruce/$', views.destroyCompensacion, name='eliminar_compensacion'),

	# url(r'^excel_factura/$', views.exportReporteFactura, name='excel_factura'),
	# url(r'^excel_descuento/$', views.exportReporteDescuento, name='excel_descuento'),
	# url(r'^excel_cruce/$', views.exportReporteCompensacion, name='excel_cruce'),
	# url(r'^excel_cruce2/$', views.exportReporteCruce, name='excel_cruce2'),
	# url(r'^excel_planilla/$', views.exportPlantilla, name='excel_planilla'),
	# url(r'^pago_factura/$', views.guardar_pago_factura, name='factura.pago_factura')
	url(r'^ver-soporte/$', views.VerSoporte, name='NoConformidad.VerSoporte'),# descarga de archivos
	url(r'^graficas/$', views.graficas, name='NoConformidad.graficas'),
	url(r'^obtenerdatosgraficas/$', views.get_dataGraph, name='NoConformidad.obtener_datosGraficas'),
]