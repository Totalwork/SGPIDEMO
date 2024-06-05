from django.conf.urls import url

from . import views


urlpatterns = [
  	url(r'^ubicacion/(?P<num>[0-9]+)/$', views.Ubicacion, name='ubicacion.ubicacion'),

]