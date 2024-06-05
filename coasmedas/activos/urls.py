from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^activo/$', views.activo_view,name='activos.activo'),
	url(r'^ver-soporte/$', views.VerSoporte, name='VerSoporte'),
	url(r'^ver-soporte-activos/$', views.VerSoporteActivos, name='VerSoporteActivos'),
	url(r'^ver-soporte-mantenimiento/$', views.VerSoporteManteniento, name='VerSoporteManteniento'),
	url(r'^ver-soporte-atributo/$', views.VerSoporteAtributo, name='VerSoporteAtributo'),
	url(r'^reporte_activos/$', views.exportReporteActivos, name='reporte_activos'),
	url(r'^reporte_mantenimientos/$', views.exportReporteMantenimientos, name='reporte_mantenimientos'),
	url(r'^mantenimientos/(?P<id>[0-9]+)/$', views.mantenimientos, name='activo.mantenimiento'),
	url(r'^ubicacion/$', views.ubicacion_view,name='activos.ubicacion'),

]