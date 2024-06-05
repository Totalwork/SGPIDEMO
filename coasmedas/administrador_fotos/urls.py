from django.conf.urls import url

from . import views


urlpatterns = [

	url(r'^administrador_fotos/$', views.AdministradorFotos, name='administrador_fotos.administrador_fotos'),
	url(r'^categoria/(?P<id_proyecto>[0-9]+)/(?P<id_contrato>[0-9]+)/$', views.CategoriaAdministrador, name='administrador_fotos.categoria'),
	url(r'^subcategoria/(?P<id_categoria>[0-9]+)/(?P<id_proyecto>[0-9]+)/(?P<id_contrato>[0-9]+)/$', views.SubcategoriaAdministrador, name='administrador_fotos.subcategoria'),

	url(r'^fotosProyecto/(?P<id_proyecto>[0-9]+)/$', views.FotosProyectoAdministrador, name='administrador_fotos.fotosProyecto'),
	url(r'^fotosSubcategoria/(?P<id_subcategoria>[0-9]+)/(?P<id_proyecto>[0-9]+)/(?P<id_categoria>[0-9]+)/(?P<id_contrato>[0-9]+)/$', views.FotosSubcategoriaAdministrador, name='administrador_fotos.fotosSubcategoria'),

	url(r'^eliminar_categoria/$', views.eliminar_varios_id, name='administrador_fotos.eliminar_categoria'),
	url(r'^eliminar_subcategoria/$', views.eliminar_varias_subcategorias, name='administrador_fotos.eliminar_subcategoria'),
	url(r'^eliminar_fotos_subcategoria/$', views.eliminar_varias_fotos_subcategorias, name='administrador_fotos.eliminar_fotos_subcategoria'),
	url(r'^eliminar_fotos_proyecto/$', views.eliminar_varias_fotos_proyecto, name='administrador_fotos.eliminar_fotos_proyecto'),

	url(r'^exportar_categoria/$', views.export_excel_categoria, name='exportar_categoria'),
	url(r'^exportar_subcategoria/$', views.export_excel_subcategoria, name='exportar_subcategoria'),
	url(r'^carpetas/$', views.carpeta_foto, name='administrador_fotos.carpetas'),
	url(r'^actualizar_fecha/$', views.actualizar_fecha, name='administrador_fotos.actualizar_fecha'),
	url(r'^asociar_reporte/$', views.asociar_reporte, name='administrador_fotos.asociar_reporte'),
	
]