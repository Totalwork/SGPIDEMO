from django.conf.urls import url

from . import views


urlpatterns = [
  	url(r'^index/$', views.avance_de_obra, name='avance_de_obra.avance_de_obra'),
    url(r'^regla_estado/(?P<id_esquema>[0-9]+)/$', views.regla_estado, name='avance_de_obra.regla_estado'),
    url(r'^administrar_capitulos/$', views.administrar_capitulos, name='avance_de_obra.administrar_capitulos'),    
    url(r'^administrar_actividades/(?P<id_esquema>[0-9]+)/$', views.administrar_actividades, name='avance_de_obra.administrar_actividades'),
  	url(r'^cronograma/(?P<id_proyecto>[0-9]+)/$', views.cronograma, name='avance_de_obra.cronograma'),
  	url(r'^actividades/(?P<id_cronograma>[0-9]+)/(?P<id_proyecto>[0-9]+)/$', views.actividades, name='avance_de_obra.actividades'),
  	url(r'^metas/(?P<id_cronograma>[0-9]+)/(?P<id_proyecto>[0-9]+)/$', views.metas, name='avance_de_obra.metas'),
  	url(r'^eliminar_id_cronograma/$', views.eliminar_id_cronograma, name='avance_de_obra.eliminar_id_cronograma'),
    url(r'^listar_actividades/(?P<id_cronograma>[0-9]+)/$', views.listar_actividades, name='avance_de_obra.listar_actividades'),
  	url(r'^guardar_metas_actividades/$', views.crear_metas_array, name='avance_de_obra.crear_meta_array'),
  	url(r'^listar_metas_actividades/(?P<id_cronograma>[0-9]+)/$', views.lista_metas_actividad, name='avance_de_obra.listar_metas_actividades'),
  	url(r'^linea_base/(?P<id_cronograma>[0-9]+)/(?P<id_proyecto>[0-9]+)/$', views.linea_base, name='avance_de_obra.linea_base'),
  	url(r'^listar_linea_base/(?P<id_cronograma>[0-9]+)/(?P<pagina>[0-9]+)/(?P<tipo_linea>[0-9]+)/(?P<filtro>[0-9]+)/$', views.listar_linea_base, name='avance_de_obra.listar_linea_base'),
    url(r'^actualizar_intervalos_linea/$', views.actualizar_intervalo_linea, name='avance_de_obra.actualizar_intervalo_linea'),
    url(r'^agregar_cantidades/$', views.registro_cantidades, name='avance_de_obra.registro_cantidades'),
    url(r'^guardar_linea_base/$', views.guardar_linea_base, name='avance_de_obra.guardar_linea_base'),
    url(r'^linea_programada/(?P<id_cronograma>[0-9]+)/(?P<id_proyecto>[0-9]+)/$', views.linea_programada, name='avance_de_obra.linea_programada'),
    url(r'^linea_avance/(?P<id_cronograma>[0-9]+)/(?P<id_proyecto>[0-9]+)/$', views.linea_avance, name='avance_de_obra.linea_avance'),
    url(r'^agregar_intervalos/$', views.agregar_intervalos, name='avance_de_obra.agregar_intervalos'),
    url(r'^quitar_intervalos/$', views.quitar_intervalos, name='avance_de_obra.quitar_intervalos'),
    url(r'^listar_esquema_actividades/(?P<id_esquema>[0-9]+)/$', views.listar_esquema_actividades, name='avance_de_obra.listar_esquema_actividades'),
    url(r'^eliminar_id_capitulos_esquema/$', views.eliminar_id_capitulo_actividad_esquema, name='avance_de_obra.eliminar_id_capitulo_actividad_esquema'),
    url(r'^clonacion_esquema/$', views.clonacion_esquema, name='avance_de_obra.clonacion_esquema'),
    url(r'^export_excel_cantidades/$', views.export_excel_cantidades, name='avance_de_obra.export_excel_cantidades'),
    url(r'^export_excel_resumen/$', views.export_excel_resumen, name='avance_de_obra.export_excel_resumen'),
    url(r'^eliminar_esquema/$', views.eliminar_esquema, name='avance_de_obra.eliminar_esquema'),
    url(r'^eliminar_id_regla_estado/$', views.eliminar_id_regla_estado, name='avance_de_obra.eliminar_id_regla_estado'),
    url(r'^actualizar_sin_avance/$', views.actualizar_sin_avance, name='avance_de_obra.actualizar_sin_avance'),
    
]