from django.conf.urls import url

from . import views


urlpatterns = [
  	url(r'^obtener_archivos/$', views.obtener_archivos, name='deploy.obtener_archivos'),

]
