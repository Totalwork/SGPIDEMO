from django.conf.urls import url

from . import views
from .schedules import schedules


urlpatterns = [

    # url(r'^empleados/$', views.empleados, name='seguridad_social.empleados'), 
    url(r'^configuracion-porcentajes/$', views.configuracion_porcentajes, name='seguimiento_retie.configuracion_porcentajes'), 
    url(r'^exportar-configuracion-porcentajes/$', views.exportar_configuracion_porcentajes, name='seguimiento_retie.exportar_configuracion_porcentajes'), 
    url(r'^exportar-visitas/$', views.exportar_visitas, name='seguimiento_retie.exportar_configuracion_porcentajes'), 
    url(r'^consultar-visitas/$', views.consultar_visitas_retie, name='seguimiento_retie.consultar_visitas_retie'), 
    url(r'^programar-visita/(?P<id>[0-9]+)/$', views.programar_visitas_retie, name='seguimiento_retie.programar_visitas_retie'), 
    url(r'^seguimiento-visita/(?P<id>[0-9]+)/$', views.seguimiento_visitas_retie, name='seguimiento_retie.seguimiento_visitas_retie'), 
    url(r'^reporte/$', views.reporte, name='seguimiento_retie.reporte'), 
    url(r'^exportar_informe/$', views.exportar_informe, name='seguimiento_retie.exportar_informe'), 
    url(r'^eliminar_configuracion_porcentajes/$', views.eliminar_configuracion_porcentajes, name='seguimiento_retie.eliminar_configuracion_porcentajes'), 
	url(r'^actualizar_seguimiento/(?P<pk>[0-9]+)$', views.actualizar_seguimiento),
	url(r'^cancelar_visita/(?P<pk>[0-9]+)$', views.cancelar_visita),
    url(r'^ver-soporte/$', views.VerSoporte, name='seguimiento_retie.VerSoporte'),# descarga de archivos

    # schedules
    url(r'^task/enviar-correo-visitas-no-programadas/$', schedules.EnviarCorreoVisitasNoProgramadas, name='seguimiento_retie.EnviarCorreoVisitasNoProgramadas'),
    url(r'^task/guardar-visitas-retie/$', schedules.GuardarVisitasRetie, name='seguimiento_retie.GuardarVisitasRetie'),
]