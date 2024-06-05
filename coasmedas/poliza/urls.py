from django.conf.urls import url
from . import views
from .schedules import schedules

urlpatterns = [

    url(r'^poliza/(?P<contrato_id>[0-9]+)?/?$', views.poliza, name='poliza.poliza'), 
    url(r'^vigencias-poliza/(?P<poliza_id>[0-9]+)/$', views.vigencia_poliza, name='poliza.vigencia_poliza'), 
    url(r'^asociar-soporte/(?P<vigencia_id>[0-9]+)/$', views.asociar_soporte, name='poliza.asociar_soporte'), 
    url(r'^poliza-contrato/$', views.poliza_contrato, name='poliza.poliza_contrato'), 

    url(r'^guardar_asociacion_soporte/$', views.guardar_asociacion_soporte, name='poliza.guardar_asociacion_soporte'), 
    url(r'^eliminar_vigencias/$', views.eliminar_vigencias, name='poliza.eliminar_vigencias'), 
    url(r'^eliminar_polizas/$', views.eliminar_polizas, name='poliza.eliminar_polizas'), 
    url(r'^exportar-polizas/$', views.exportar_polizas, name='poliza.exportar_polizas'), 
    url(r'^exportar-vigencias/$', views.exportar_vigencias, name='poliza.exportar_vigencias'),     
    url(r'^ver-soporte/$', views.VerSoporte, name='VerSoporte'),# descarga de archivos

    # schedules
    url(r'^task/actualizar-estado-poliza/$', schedules.ActualizarEstadoPoliza, name='poliza.ActualizarEstadoPoliza'),   
    url(r'^task/poliza-por-vencer/$', schedules.PolizaPorVencer, name='poliza.PolizaPorVencer'),   
    url(r'^task/poliza-vencida/$', schedules.PolizaVencida, name='poliza.PolizaVencida'),
]    