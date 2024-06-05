from django.conf.urls import url

from . import views


urlpatterns = [
  	url(r'^cuenta/$', views.cuenta, name='cuenta.cuenta'),

]