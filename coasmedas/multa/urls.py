from django.conf.urls import url

from . import views


urlpatterns = [

	url(r'^select-filter-multa/$', views.select_filter_multa, name='proyecto.select_filter_multa'),

	url(r'^index/$', views.index, name='multa.index'),
	url(r'^multaElaboradas/$', views.multaElaboradas, name='multa.multaElaboradas'),
	url(r'^multaElaborar/$', views.multaElaborar, name='multa.multaElaborar'),
	url(r'^multaSolicitadas/$', views.multaSolicitadas, name='multa.multaSolicitadas'),
	url(r'^multas/$', views.multas, name='multa.multas'),
	url(r'^descargos/$', views.descargos, name='multa.descargos'),
	url(r'^eventos/$', views.eventos, name='multa.eventos'),
	url(r'^reporte_multa/$', views.exportReporteMulta, name='reporte.multa'),
	url(r'^multa-confirmadas/$', views.multaConfirmadas, name='multa.multaConfirmadas'),

	url(r'^multa-historial/?(?P<id>[0-9]+)?/?$', views.multaHistorial, name='multa-historial'),
	

	# PRESENTAR DESCARGO DE LA MULTA
	url(r'^multa-presentar-descargo/?(?P<id>[0-9]+)?/?$', views.multaPresentarDescargo, name='multa_presentar_descargo'),

	# RESPUESTA DESCARGO DE LA MULTA
	url(r'^multa-respuesta-descargo/?(?P<id>[0-9]+)?/?$', views.multaRespuestaDescargo, name='multa_respuesta_descargo'),
	# CREATE RESPUESTA DESCARGO DE LA MULTA
	url(r'^create-respuesta-descargo/$', views.create_respuesta_descargo, name='create-respuesta-descargo'),



	# GENERAR MULTA
	url(r'^generate_solicitud/$', views.generateSolicitud, name='generate_solicitud'),

	# DESCARGAR FORMATO DE LA CARTA DE SOLICITAR LA MULTA
	url(r'^createWordSolicitud/$', views.createWordSolicitud, name='createWordSolicitud'),# GENERA WORD PARA LA CARTA DE SOLICITUD
	# DESCARGAR FORMATO DE SOLICITUD GENERADA
	# url(r'^generate-format-solicitud/$', views.generateFormatSolicitud, name='generate-format-solicitud'),
	# DESCARGAR FORMATO DE RESPUESTA A DESCARGOS
	url(r'^generate-format-respuestaDescargo/$', views.generate_format_respuesta_descargo, name='generate-format-respuestaDescargo'),
	# DESCARGAR FORMATO DE OF
	url(r'^generate-format-OF/$', views.generate_format_OF, name='generate-format-OF'),

	# ACTUALIZA EL VALOR DE LA IMPOSICION O MULTA
	url(r'^update-valorimpuesto/$', views.updateValorImpuesto),
	# REGISTRAR CODIGO OF
	url(r'^register_codigo_of/$', views.registerCodigoOF, name='register_codigo_of'),
	# REGISTRAR CODIGO DE REFERENCIA
	url(r'^register_codigo_referencia/$', views.registerCodigoReferencia, name='register_codigo_referencia'),

	# SUBIR SOPORTE DE LA CARTA DE SOLICITUD
	url(r'^upload-CartaSolicitudSoporte/$', views.uploapCartaSolicitudSoporte, name='upload-CartaSolicitudSoporte'),
	# ELIMINAR PRUEBAS DE LA SOLICITUD
	url(r'^destroy-SolicitudSoporte/$', views.destroySolicitudSoporte, name='destroy-SolicitudSoporte'),
	url(r'^ver-soporte/$', views.VerSoporte, name='solicitudMulta.VerSoporte'),# descarga de archivos
	url(r'^ver-soporte-solicitud/$', views.VerSoporteSolicitud, name='solicitud.VerSoporteSolicitud'),# descarga de archivos
	url(r'^ver-soporte-solicitud-soporte/$', views.VerSoporteSolicitudSoporte, name='solicitud.VerSoporteSolicitudSoporte'),# descarga de archivos
]
