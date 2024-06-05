from django.conf.urls import url
from . import views

urlpatterns = [

	url(r'^proyectos_construccion/$', views.ListadoProyectos, name='p_p_construccion.proyectos_construccion'),
	url(r'^lote/(?P<id_proyecto>[0-9]+)/$', views.Lote, name='p_p_construccion.lote'),
	url(r'^propietario/(?P<lote_id>[0-9]+)/(?P<proyecto_id>[0-9]+)/$', views.PropietarioVista, name='p_p_construccion.propietario'),
	url(r'^eliminar_estrucura/$', views.eliminar_varios_estruturas, name='p_p_construccion.eliminar_estrucura'),
	url(r'^asociar_propietario_lote/$', views.AsociarPropietariosLote, name='p_p_construccion.asociar_propietario_lote'),
	url(r'^listado_propietario/$', views.consulta_listado_propietarios, name='p_p_construccion.listado_propietario'),
	url(r'^desasociar_propietario/$', views.desasociar_propietario, name='p_p_construccion.desasociar_propietario'),
	url(r'^eliminar_lote/$', views.eliminar_lotes, name='p_p_construccion.eliminar_lote'),
	url(r'^eliminar_documento/$', views.eliminar_documentos, name='p_p_construccion.eliminar_documento'),
		
]