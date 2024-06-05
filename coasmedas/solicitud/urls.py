from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^solicitud/$', views.solicitud, name='solicitud.solicitud'),

	url(r'^update_requisitos_poliza/$', views.updateRequisitosPoliza, name='actualizar_requisitos_poliza'),
	url(r'^eliminar_solicitud/$', views.destroySolicitud, name='eliminar_solicitud')
]