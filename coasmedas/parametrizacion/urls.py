from django.conf.urls import url

from . import views


urlpatterns = [
  	url(r'^parametrizacion/$', views.parametrizacion, name='parametrizacion.parametrizacion'),
    url(r'^manual_usuario/$', views.manual_usuario, name='parametrizacion.manual_usuario'),
  	url(r'^banco/$', views.banco, name='parametrizacion.banco'),
  	url(r'^funcionario/$', views.funcionario, name='parametrizacion.funcionario'),
    url(r'^inicioResponsabilidades/$', views.inicioResponsabilidades, name='parametrizacion.inicioResponsabilidades'),
    url(r'^responsabilidades/$', views.responsabilidades, name='parametrizacion.responsabilidades'),
    url(r'^asignar_responsabilidades/$', views.asignarResponsabilidades, name='parametrizacion.asignar_responsabilidades'),
    url(r'^misResponsabilidades/$', views.misResponsabilidades, name='parametrizacion.misResponsabilidades'),
  	url(r'^export_banco/$', views.export_excel_banco, name='export_excel.banco'),
  	url(r'^eliminar_id_banco/$', views.eliminar_varios_id_banco, name='eliminar_id.banco'),
  	url(r'^export_cargo/$', views.export_excel_cargo, name='export_excel.cargo'),
  	url(r'^eliminar_id_cargo/$', views.eliminar_varios_id_cargo, name='eliminar_id.cargo'),  
  	url(r'^export_funcionario/$', views.export_excel_funcionario, name='export_excel.funcionario'),	
  	url(r'^eliminar_id_funcionario/$', views.eliminar_varios_id_funcionario, name='eliminar_id.funcionario'),
  	url(r'^select_departamento/$', views.select_departamento, name='select.departamento'),
    url(r'^eliminar_responsabilidades_lista/$', views.eliminar_responsabilidades, name='eliminar_responsabilidades'),
    url(r'^create_responsabilidades_funcionario/$', views.createResponsabilidadesFuncionarioConLista, name='create_responsabilidades_funcionarioConLista'),
    url(r'^destroy_responsabilidades_funcionario/$', views.destroyResponsabilidadesFuncionarioConLista, name='destroy_responsabilidades_funcionarioConLista'),
    url(r'^lista_mis_responsabilidades/$', views.listMisResponsabilidades, name='list_mis_responsabilidades'),

    # usuarios que tienen funcionario se excluye el usuario actual
    url(r'^usuariosConFuncionarios/$', views.usuariosConFuncionarios, name='usuariosConFuncionarios.usuariosConFuncionarios'),
     # usuarios que tienen funcionario sin excluir usuario actual
    url(r'^usuarios_conFuncionariosEmpresa/$', views.usuariosConFuncionariosEmpresa, name='usuariosConFuncionariosEmpresa'),
    url(r'^obtener_notificaciones_por_persona/$', views.obtener_notificaciones_por_persona, name='obtener_notificaciones_por_persona'),
    url(r'^grupo-videos-tutoriales/$', views.grupo_videos_tutoriales, name='grupo_videos_tutoriales'),
    url(r'^videos-tutoriales/(?P<grupo_id>[0-9]+)/$', views.videos_tutoriales, name='videos_tutoriales'),
    url(r'^videos/$', views.video, name='parametrizacion.video'),
    url(r'^transacciones/$', views.transacciones, name='parametrizacion.transacciones'),
    url(r'^exportTransacciones/$', 
        views.exportTransacciones, 
        name='avance_de_obra_grafico2.exportTransacciones'),
]