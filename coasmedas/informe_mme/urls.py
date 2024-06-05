from django.conf.urls import url
from . import views

urlpatterns = [

	url(r'^informe_mme/$', views.informe_ministerio, name='informe_mme.informe_mme'),
	
]