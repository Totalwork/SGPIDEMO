from django.conf.urls import url
from . import views

urlpatterns = [

	url(r'^cesion_economica/$', views.cesion_economica, name='cesion_economica.cesioneconomica'),
	url(r'^actualizar_enaprobacion/$', views.actualizar_enaprobacion, name='cesion_economica.actualizar_enaprobacion'),
	url(r'^actualizar_anulada/$', views.actualizar_anulada, name='cesion_economica.actualizar_anulada'),
	url(r'^actualizar_rechazado/$', views.actualizar_rechazado, name='cesion_economica.actualizar_rechazado'),
	url(r'^actualizar_aprobada/$', views.actualizar_aprobada, name='cesion_economica.actualizar_aprobada'),
	url(r'^validacion_aprobada/$', views.validacion_aprobada, name='cesion_economica.validacion_aprobada'),
	
]