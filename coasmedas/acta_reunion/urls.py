from django.conf.urls import url

from . import views


urlpatterns = [
	url(r'^acta/$', views.acta, name='actareunion.acta'),
	url(r'^consecutivo/$', views.consecutivo, name='actareunion.consecutivo'),
	url(r'^mis-compromisos/$', views.mis_compromisos, name='actareunion.mis_compromisos'),
	url(r'^acta-examinar/(?P<acta_id>[0-9]+)$', views.acta_examinar, name='servidumbre.acta_examinar'),
	url(r'^filtrar-proyectoscontratos/$', views.filtrar_proyectoscontratos, name='actareunion.filtrar_proyectoscontratos'),
	url(r'^obtener-participantes/$', views.obtener_participantes, name='actareunion.obtener_participantes'),
	url(r'^eliminar-participantes/$', views.eliminar_varios_participantes_id, name='actareunion.eliminar_varios_participantes_id'),
	url(r'^cerrar-acta/$', views.cerrar_acta, name='actareunion.cerrar_acta'),
	url(r'^ver-soporte-acta/$', views.ver_soporte_acta, name='actareunion.ver_soporte_acta'),
	url(r'^obtener-noparticipantes/$', views.obtener_noparticipantes, name='actareunion.obtener_noparticipantes'),
	url(r'^exportar-actas/$', views.exportar_actas, name='actareunion.exportar_actas'),
	url(r'^anularActa/$', views.anularActa, name='actareunion.anularActa'),
	url(r'^transferir-acta/$', views.transferir_acta, name='actareunion.transferir_acta'),
	url(r'^subirsoporte-acta/$', views.subirsoporte_acta, name='actareunion.subirsoporte_acta'),
	url(r'^asignar-contrato-acta/$', views.asignarContrato, name='actareunion.asignar-contrato-acta'),
	url(r'^desasignar-contrato-acta/$', views.desasignarContrato, name='actareunion.desasignar-contrato-acta'),
	url(r'^asignar-proyecto-acta/$', views.asignarProyecto, name='actareunion.asignar-proyecto-acta'),
	url(r'^desasignar-proyecto-acta/$', views.desasignarProyecto, name='actareunion.desasignar-proyecto-acta'),	
	url(r'^subirconclusiones-acta/$', views.subirconclusiones_acta, name='actareunion.subirconclusiones_acta'),	
	url(r'^asistencia-acta/$', views.asistencia_acta, name='actareunion.asistencia_acta'),
	url(r'^actualizar-tienes-acta/$', views.actualizar_tienes_acta, name='actareunion.actualizar_tienes_acta'),
	url(r'^obtener-porcentaje-acta/$', views.obtener_porcentaje_acta, name='actareunion.obtener_porcentaje_acta'),
	url(r'^guardar-cumplimiento/$', views.guardar_cumplimiento, name='actareunion.guardar_cumplimiento'),	
	url(r'^ver-soporte-compromiso/$', views.ver_soporte_compromiso, name='actareunion.ver_soporte_compromiso'),
	url(r'^cancelar-compromiso/$', views.cancelar_compromiso, name='actareunion.cancelar_compromiso'),
	url(r'^restablecer-compromiso/$', views.restablecer_compromiso, name='actareunion.restablecer_compromiso'),
	url(r'^prorrogar-compromiso/$', views.prorrogar_compromiso, name='actareunion.prorrogar_compromiso'),
	url(r'^reasignar-compromiso/$', views.reasignar_compromiso, name='actareunion.reasignar_compromiso'),
	url(r'^llenar-graficasactas/$', views.llenar_graficas_actas, name='actareunion.llenar_graficas_actas'),	
	url(r'^generar-codigo-qr/$', views.generar_codigo_qr, name='activos.generar_codigo_qr'),
]
