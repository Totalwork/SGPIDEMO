from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^inicio/$', views.balance_scorecard, name='balance_scorecard.inicio'),
	url(r'^aspectos_finacieros/$', views.aspectos_financieros, name='balance_scorecard.aspectos_finacieros'),
	url(r'^procesos_internos/$', views.procesos_internos, name='balance_scorecard.procesos_internos'),
	url(r'^cultura_organizacional/$', views.cultura_organizacional, name='balance_scorecard.cultura_organizacional'),	
	url(r'^consultar_por_departamento/$', views.consultarpordepartamento, name='balance_scorecard.consultarpordepartamento'),
	url(r'^contrato_por_departamento/$', views.contratopordepartamento, name='balance_scorecard.contratopordepartamento'),

]