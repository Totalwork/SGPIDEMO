from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^miscorrespondencia/$', views.miscorrespondencia, name='correspondenciaRecibida.miscorrespondencias'),
  	url(r'^correspondenciaRecibida/$', views.correspondenciaRecibida, name='correspondenciaRecibida.correspondenciaRecibida'),
    url(r'^destroy_correspondenciaRecibida/$', views.destroyCorrespondenciaRecibida, name='destroy_correspondenciaRecibida'),
    url(r'^establish_correspondenciaRecibida/$', views.establishCorrespondenciaRecibida, name='establish_correspondenciaRecibida'),
    url(r'^reporte_correspondenciaRecibida/$', views.exportReporteCorrespondenciaRecibida, name='reporte_correspondenciaRecibida'),
    url(r'^create_asignar_correspondencia/$', views.createAsignarCorrespondencia, name='create_AsignarCorrespondencia'),

    url(r'^createBarCodes/$', views.createBarCodes, name='createBarCodes'),# GENERA CODIGO DE BARRA PARA EL RADICADO 

    url(r'^destroy-correspondenciaRecibidaSoporte/$', views.destroyCorrespondenciaSoporte, name='destroy_correspondenciaSoporte'),
    url(r'^ver-soporte/$', views.VerSoporte, name='VerSoporte'),# descarga de archivos
   
]