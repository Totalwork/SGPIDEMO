from django.conf.urls import url

from . import views
from .schedules import schedules


urlpatterns = [

    url(r'^empleados/$', views.empleados, name='seguridad_social.empleados'), 
    url(r'^crear-empleado/$', views.crear_empleado, name='seguridad_social.crear_empleado'), 
    url(r'^editar-empleado/(?P<id>[0-9]+)/$', views.editar_empleado, name='seguridad_social.editar_empleado'), 
    url(r'^planilla/$', views.planilla, name='seguridad_social.planilla'), 
    url(r'^planilla-empleado/(?P<planilla_id>[0-9]+)/(?P<contratista_id>[0-9]+)/$', views.planilla_empleado, name='seguridad_social.planilla_empleado'), 
    url(r'^novedades/$', views.novedades, name='seguridad_social.novedades'), 
    url(r'^empresa-permisos/$', views.empresa_permisos, name='seguridad_social.empresa_permisos'), 
    url(r'^estudio-personas/$', views.estudio_personas, name='seguridad_social.estudio_personas'), 
    url(r'^informe/$', views.informe, name='seguridad_social.informe'), 
    url(r'^completar-informacion-empleados/(?P<empleado_id>[0-9]+)/$', views.completar_informacion_empleados, name='seguridad_social.completar_informacion_empleados'),
    
    url(r'^actualizar_empleado_acto/$', views.actualizar_empleado_acto, name='seguridad_social.actualizar_empleado_acto'), 	
    url(r'^obtener_meses_planilla/$', views.obtener_meses_planilla, name='seguridad_social.obtener_meses_planilla'), 	
    url(r'^guardar_panilla_empleado/$', views.guardar_panilla_empleado, name='seguridad_social.guardar_panilla_empleado'), 	
    url(r'^consultar_planilla_empleado/$', views.consultar_planilla_empleado, name='seguridad_social.consultar_planilla_empleado'), 	
    url(r'^consultar_empresa/$', views.consultar_empresa, name='seguridad_social.consultar_empresa'),   
    url(r'^consultar_empresa_permisos/$', views.consultar_empresa_permisos, name='seguridad_social.consultar_empresa_permisos'),   
  	url(r'^guardar_empresa_permisos/$', views.guardar_empresa_permisos, name='seguridad_social.guardar_empresa_permisos'),   
    url(r'^eliminar_empresa_permisos/$', views.eliminar_empresa_permisos, name='seguridad_social.eliminar_empresa_permisos'),   
    url(r'^consultar_requerimientos_empleado/$', views.consultar_requerimientos_empleado, name='seguridad_social.consultar_requerimientos_empleado'),   
    url(r'^guardar_estudio_personas/$', views.guardar_estudio_personas, name='seguridad_social.guardar_estudio_personas'),   
    url(r'^actualizar_estudio_personas/$', views.actualizar_estudio_personas, name='seguridad_social.actualizar_estudio_personas'),   
    url(r'^exportar-empleados/$', views.exportar_empleados, name='seguridad_social.exportar_empleados'),   
    url(r'^exportar-planilla/$', views.exportar_planilla, name='seguridad_social.exportar_planilla'),   
    url(r'^exportar-novedades/$', views.exportar_novedades, name='seguridad_social.exportar_novedades'),   
    url(r'^exportar-informe/$', views.exportar_informe, name='seguridad_social.exportar_informe'),   
    url(r'^agregar_empleado_a_planilla/$', views.agregar_empleado_a_planilla, name='seguridad_social.agregar_empleado_a_planilla'),   
    url(r'^consultar_empleados_por_contratista/$', views.consultar_empleados_por_contratista, name='seguridad_social.consultar_empleados_por_contratista'),   
    url(r'^eliminar_planilla/$', views.eliminar_planilla, name='seguridad_social.eliminar_planilla'),   
    url(r'^correos-contratista/$', views.correos_contratista, name='seguridad_social.correos_contratista'),

    url(r'^list_empleados_con_seguridad_social/$', views.listEmpleadosSeguridadSocialPaga, name='list_empleados_con_seguridad_social'),
    url(r'^exportar-planilla_empleados/$', views.exportar_planilla_empleados, name='seguridad_social.exportar_planilla_empleados'),   
    url(r'^consultar_contratistas/$', views.consultar_contratistas, name='seguridad_social.consultar_contratistas'),   
    url(r'^ver-soporte/$', views.VerSoporte, name='seguridad_social.VerSoporte'),# descarga de archivos
    url(r'^ver-soporte-planilla/$', views.VerSoportePlanilla, name='seguridad_social.VerSoportePlanilla'),# descarga de archivos

    # schedules
    url(r'^task/trabajo-altura-por-vencer/$', schedules.TrabajoEnAlturaPorVencer, name='seguridad_social.TrabajoEnAlturaPorVencer'),   
    url(r'^task/trabajo-altura-vencido/$', schedules.TrabajoEnAlturaVencido, name='seguridad_social.TrabajoEnAlturaVencido'),   
    url(r'^task/seguridad-social-vencida/$', schedules.SeguridadSocialVencida, name='seguridad_social.SeguridadSocialVencida'),
    url(r'^task/licencia-por-vencer/$', schedules.LicenciaPorVencer, name='seguridad_social.LicenciaPorVencer'),
    url(r'^task/licencia-vencida/$', schedules.LicenciaVencida, name='seguridad_social.LicenciaVencida')

]