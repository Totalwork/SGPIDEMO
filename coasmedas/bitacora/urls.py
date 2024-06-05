from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^bitacora/(?P<proyecto_id>[0-9]+)/$', views.bitacora, name='bitacora.bitacora'),
	url(r'^obtener_usuario/(?P<proyecto_id>[0-9]+)/$', views.obtener_usuario, name='obtener_usuario'),
	
]
