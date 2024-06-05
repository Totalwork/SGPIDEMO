from django.conf.urls import url

from . import views


urlpatterns = [
  	url(r'^index/$', views.administrador_tarea, name='administrador_tarea.administrador_tarea'),
    url(r'^muro/$', views.muro, name='administrador_tarea.muro'),
    url(r'^cambiar_estado/$', views.cambiar_estado, name='administrador_tarea.cambiar_estado'),
    url(r'^grupo/$', views.grupo, name='administrador_tarea.grupo'),
    url(r'^listado_grupo/$', views.listado_grupo, name='administrador_tarea.listado_grupo'),
    url(r'^guardar_colaboradores/$', views.guardar_colaboradores, name='administrador_tarea.guardar_colaboradores'),
    url(r'^detalle_tarea/(?P<id_tarea>[0-9]+)/$', views.detalle_tarea, name='administrador_tarea.detalle_tarea'),
    url(r'^nuevo_punto/(?P<id_tarea>[0-9]+)/$', views.nuevo_punto, name='administrador_tarea.nuevo_punto'),
    url(r'^agenda/$', views.agenda, name='administrador_tarea.agenda'),
    url(r'^grafica1/$', views.porcentaje_equipo, name='administrador_tarea.porcentaje_equipo'),
    url(r'^grafica2/$', views.porcentaje_barra, name='administrador_tarea.porcentaje_barra'),    
    url(r'^download_zip/$', views.download_zip, name='administrador_tarea.download_zip'),
    url(r'^tarea/(?P<id_tarea>[0-9]+)/$', views.tarea, name='administrador_tarea.tarea'),
    url(r'^edicion_actividad/(?P<id_actividad>[0-9]+)/$', views.edicion_actividad, name='administrador_tarea.edicion_actividad'),
    url(r'^ver-soporte/$', views.VerSoporte, name='administrador_tarea.VerSoporte'),# descarga de archivos
    url(r'^ver-soporte-actividad/$', views.VerSoporteActividad, name='administrador_tarea.VerSoporteActividad'),# descarga de archivos
]