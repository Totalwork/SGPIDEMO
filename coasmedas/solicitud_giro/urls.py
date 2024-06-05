from django.conf.urls import url

from . import views


urlpatterns = [

	url(r'^solicitudes/$', views.solicitud_inicio, name='solicitud.inicio'),
	url(r'^countsolicitudes/$', views.conteoSolPendientes, name='solicitud.count'),
	url(r'^referencia/$', views.solicitud_referencia, name='solicitud.referencia'),
	url(r'^actualizar_referencia/$', views.actualizar_referencia, name='solicitud.actualizar.referencia'),
	url(r'^detallegiro/(?P<id_encabezado>[0-9]+)/(?P<mcontrato>[0-9]+)/(?P<contrato>[0-9]+)/$', views.detalle_giros, name='giros.detallegiro'),
	url(r'^reporte_test_realizados/$', views.test_realizados, name='generar_test_realizados'),
	url(r'^testop_reporte/$', views.report_testOP, name='report_testOP'),
	url(r'^rechazo_giro/$', views.rechazados, name='rechazo.solicitud'),	

	url(r'^actualizar_testop/$', views.actualizar_testop, name='solicitud.actualizar.testop'),
	url(r'^actualizar_flujotest/$', views.actualizar_flujotest, name='solicitud.flujo_test'),

	url(r'^solTestOP/$', views.solTestOP, name='solicitud.solTestOP'),

	url(r'^solSinPagar/$', views.solSinTestPagar, name='solicitud.solSinTestPagar'),

	url(r'^detalletestop/$', views.actualizar_detalle_testop, name='solicitud.detalleop'),

	url(r'^registrarcodpago/$', views.registrarCodPago, name='solicitud.registrarcodigopago'),

	# genera el reporte de las plantillas fiduciarias
	url(r'^reporte_anticipo/$', views.generar_reporte_fiduciario, name='solicitud.reporte_fiduciario'),

	url(r'^fechapago/$', views.establecer_fechapago, name='solicitud.fechadepago'),
	url(r'^rechazopago/$', views.establecer_rechazo, name='solicitud.rechazopago'),

	url(r'^registrar_codigo/$', views.codigo_pago, name='solicitud.registrocodigo'),


]
