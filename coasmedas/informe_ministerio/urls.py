from django.conf.urls import url

from . import views


urlpatterns = [
	

	url(r'^informe_ministerio/$', views.informe_ministerio, name='informe.informe_ministerio'),
	url(r'^excel_verificar_datos/$', views.excel_verificar_datos, name='informe.excel_verificar_datos'),
	url(r'^generar_informe/$', views.generar_informe, name='informe.generar_informe'),
]