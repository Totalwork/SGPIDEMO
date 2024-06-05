from django.conf.urls import url

from . import views#, tasks
from .schedules import schedules

urlpatterns = [
	url(r'^contrato/$', views.contrato, name='contrato.contrato'),
	url(r'^detalle_contrato/(?P<id_contrato>[0-9]+)/$', views.detalleContrato, name='detalle_contrato'),
	url(r'^vigencia_contrato/(?P<id_contrato>[0-9]+)/$', views.vigenciaContrato, name='vigencia_contrato'),
	url(r'^historial-contrato/(?P<id_contrato>[0-9]+)/$', views.historialContrato, name='historial-contrato'),
	url(r'^gestionar_proyectos/(?P<id_contrato>[0-9]+)/$', views.gestionarProyectos, name='gestionar_proyectos'),
	url(r'^permiso_contrato/(?P<id_contrato>[0-9]+)/$', views.permisoContrato, name='permiso_contrato'),
	url(r'^actas_contrato/(?P<id_contrato>[0-9]+)/$', views.actasContrato, name='actas_contrato'),
	url(r'^sub_contratista/(?P<id_contrato>[0-9]+)/$', views.subContratista, name='sub_contratista'),
	url(r'^contrato_cesion/(?P<id_contrato>[0-9]+)/$', views.contratoCesion, name='contrato_cesion'),
	url(r'^cesion_economica/(?P<id_contrato>[0-9]+)/$', views.cesionEconomica, name='cesion_economica'),
	# url(r'^list_contrato/$', views.listContrato, name='list_contrato_tipo'),
	url(r'^list_contrato_rubro/$', views.listRubroContrato, name='list_contrato_rubro'),
	url(r'^list_proy_contrato/$', views.listProyContrato, name='list_proy_contrato'),
	url(r'^create_proyecto_contrato/$', views.createProyectoContratoConLista, name='create_proyecto_contrato'),
	url(r'^eliminar_proyecto/$', views.destroyProyectoContrato, name='eliminar_proyecto'),
	url(r'^create_sub_contratista/$', views.createSubContratistaConLista, name='create_sub_contratista'),
	url(r'^list_sub_contratista/$', views.listSubContratista, name='list_sub_contratista'),
	url(r'^eliminar_sub_contratista/$', views.destroySubContratista, name='eliminar_sub_contratista'),
	url(r'^eliminar_contrato_cesion/$', views.destroyContratoCesion, name='eliminar_contrato_cesion'),
	url(r'^eliminar_cesion_economica/$', views.destroyCesionEconomica, name='eliminar_cesion_economica'),

	url(r'^excel_contrato/$', views.exportReporteContrato2, name='excel_contrato'),
	url(r'^excel_vigenciacontrato/$', views.exportReporteVigenciaContrato, name='excel_vigenciacontrato'),
	# url(r'^contrato_estado/$', tasks.cambioEstadoContrato, name='contrato_estado')
	url(r'^ver-soporte/$', views.VerSoporte, name='VerSoporte'),
	url(r'^ver-soporte-acta-compra/$', views.VerSoporteCompra, name='VerSoporteCompra'), # descarga de archivos
	url(r'^validar-permiso/$', views.validarPermiso, name='validarPermiso'),
	url(r'^ver-soporte-acta-adjudicacion/$', views.VerSoporteActaAdjudicacion, name='VerSoporteActaAdjudicacion'),

	#schedules
	url(r'^task/cambio-estado-contrato/$', schedules.cambioEstadoContrato, name='contrato.cambioEstadoContrato'),
	url(r'^task/contrato-de-obra-por-vencidos/$', schedules.contratoDeObraPorVencidos, name='contrato.contratoDeObraPorVencidos'),
	url(r'^task/contrato-de-obra-vencido/$', schedules.contratoDeObraVencidos, name='contrato.contratoDeObraVencidos'),
	url(r'^task/contrato-auxiliar-por-vencer/$', schedules.contratoAuxiliarPorVencer, name='contrato.contratoAuxiliarPorVencer'),
	url(r'^task/contrato-auxiliares-vencidos/$', schedules.contratoAuxiliaresVencidos, name='contrato.contratoAuxiliaresVencidos'),
	
]
