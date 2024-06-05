from django.conf.urls import url

from . import views


urlpatterns = [
  	url(r'^contratista/$', views.contratistas, name='empresa.contratista'),
  	url(r'^empresa/$', views.empresa, name='empresa.empresa'),
  	url(r'^empresa/cargo$', views.cargo, name='empresa.cargo'),
  	url(r'^proveedor/$', views.proveedor, name='empresa.proveedor'),
  	url(r'^export/$', views.export_excel, name='export_excel'),
  	url(r'^eliminar_id/$', views.eliminar_varios_id, name='eliminar_id'),
  	url(r'^actualizar_estado/$', views.actualizar_estados_varios_id, name='actualizar_estado'),  	   
    url(r'^consultar_datos_nit/$', views.consultar_datos_nit, name='consultar_datos_nit'),
    url(r'^actualizar-empresa-cuenta/$', views.actualizar_estado_empresa_cuenta, name='empresa.actualizar-empresa-cuenta'),
    url(r'^exportar-empresa-cuenta/$', views.export_excel_cuenta, name='empresa.exportar-empresa-cuenta'),
]