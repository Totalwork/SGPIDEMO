from django.conf.urls import url

from . import views


urlpatterns = [
  # api que trae todos los select necesarios para un registro o modificacion del proyecto
  url(r'^select-create-update-proyecto/$', views.select_create_update_proyecto, name='proyecto.select_create_update_proyecto'),
  url(r'^select-filter-proyecto/$', views.select_filter_proyecto, name='proyecto.select_filter_proyecto'),

	url(r'^proyecto/$', views.proyecto, name='proyecto.proyecto'),
	url(r'^destroy_proyecto/$', views.destroyProyecto, name='destroy_proyecto'),
	url(r'^reporte_proyecto/$', views.exportReporteProyecto, name='reporte_proyecto'),

	##PROYECTO EMPRESA
	url(r'^create_proyecto_empresa/$', views.createProyectoEmpresa, name='create_proyecto_empresa'),#asociar empresas al proyecto
	url(r'^destroy_proyecto_empresa/$', views.destroyProyectoEmpresa, name='destroy_proyecto_empresa'),#denegar empresas del proyecto
	url(r'^listEmpresasSinProyecto/$', views.listEmpresasSinProyecto, name='listEmpresasSinProyecto'),#funcion lista empresas que no estan asociadas al proyecto filtrado
	url(r'^listEmpresasDelProyecto/$', views.listEmpresasDelProyecto, name='listEmpresasDelProyecto'),#funcion lista empresas que pueden ver el  proyecto filtrado
	## PROYECTO FUNCIONARIO
	url(r'^list_proyecto_funcionario/$', views.listProyectoFuncionario, name='list_proyecto_funcionario'),#listado de proyectos asociados a funcionarios
	url(r'^create_proyecto_funcionario/$', views.createProyectoFuncionario, name='create_proyecto_funcionario'),#asociar proyectos a funcionarios
	url(r'^destroy_proyecto_funcionario/$', views.destroyProyectoFuncionario, name='destroy_proyecto_funcionario'),#denegar proyectos a funcionarios
	url(r'^listFuncionariosSinProyecto/$', views.listFuncionariosSinProyecto, name='listFuncionariosSinProyecto'),#funcion lista funcionarios  que no estas asignados al proyecto  filtrado
	## PROYECTO CONTRATO
	url(r'^list_proyecto_contrato/$', views.listProyectoContrato, name='list_proyecto_contrato'),#listado de proyectos asociados a contratos
	url(r'^create_proyecto_contrato/$', views.createProyectoContrato, name='create_proyecto_contrato'),#asociar proyectos a contratos
	url(r'^destroy_proyecto_contrato/$', views.destroyProyectoContrato, name='destroy_proyecto_contrato'),#denegar proyectos a contratos
	url(r'^listContratosSinProyecto/$', views.listContratosSinProyecto, name='listContratosSinProyecto'),#listado de proyectos asociados a contratos
	##PROYECTO INFORMACION TECNICA
	url(r'^destroy_proyecto_info_tecnica/$', views.destroyProyectoInfoTecnica, name='destroy_proyecto_info_tecnica'),#denegar informacion del proyecto

  url(r'^filtrar_proyectos/$', views.filtrarProyecto, name='proyecto.filtrarProyecto'),

  url(r'^listar_macroContrato_Proyectos/$', views.listMacroContratosParaAsignarProyecto, name='proyecto.listMacroContratosParaAsignarProyecto'),

  #url(r'^resumen_proyecto/$', views.resumen, name='proyecto.resumen_proyecto'),

  #url(r'^hoja_proyecto/(?P<id_proyecto>[0-9]+)/$', views.hoja_resumen, name='proyecto.hoja_proyecto'),

  url(r'^asignacionproyecto/$', views.AsignacionProyecto, name='asignacion_proyecto'),
  url(r'^crearfuncionarioproyecto/$', views.crearProyectoFuncionario, name='asignacionproyectofuncionario'),#funcion para asociar una lista de proyectos a un funcionario
  url(r'^eliminarfuncionarioproyecto/$', views.destroylistaProyectoFuncionario, name='asignacionproyectofuncionarioeliminar'),#funcion para asociar una lista de proyectos a un funcionario

  #url(r'^listado_proceso/$', views.listProyectoProceso, name='proyecto.listado_proceso'),
  #url(r'^listado_giros/$', views.listadoGiroContrato, name='proyecto.listado_giros'),
  #url(r'^listado_poliza/$', views.listadoPolizaContrato, name='proyecto.listado_poliza'),
  #url(r'^listado_vigencia/$', views.listadoVigenciaContrato, name='proyecto.listado_vigencia'),

  url(r'^resumen_proyecto/$', views.resumen, name='proyecto.resumen_proyecto'),
  url(r'^hoja_proyecto/(?P<id_proyecto>[0-9]+)/$', views.hoja_resumen, name='proyecto.hoja_proyecto'),
  url(r'^listado_proceso/$', views.listProyectoProceso, name='proyecto.listado_proceso'),
  url(r'^listado_giros/$', views.listadoGiroContrato, name='proyecto.listado_giros'),
  url(r'^listado_poliza/$', views.listadoPolizaContrato, name='proyecto.listado_poliza'),
  url(r'^listado_vigencia/$', views.listadoVigenciaContrato, name='proyecto.listado_vigencia'),
  
  #INFORMES EJECUTIVOS
  url(r'^resumen-por-fondo/$', views.resumen_por_fondo, name='proyecto.resumen_por_fondo'),
  url(r'^resumen-por-contrato/(?P<fondo_id>[0-9]+)/$', views.resumen_por_contrato, name='proyecto.resumen_por_contrato'),
  url(r'^resumen-por-contrato-tipo-proyecto/(?P<fondo_id>[0-9]+)/$', views.resumen_por_contrato_tipo_proyecto, name='proyecto.resumen_por_contrato_tipo_proyecto'),
  url(r'^resumen-por-proyecto/(?P<fondo_id>[0-9]+)/$', views.resumen_por_proyecto, name='proyecto.resumen_por_proyecto'),
  url(r'^resumen-por-giros/(?P<fondo_id>[0-9]+)/$', views.resumen_por_giros, name='proyecto.resumen_por_giros'),  	
  url(r'^resumen-por-fondo-contrato-giro/(?P<fondo_id>[0-9]+)/$', views.resumen_por_fondo_contrato_giro, name='proyecto.resumen_por_fondo_contrato_giro'),  	
  url(r'^balance-financiero/(?P<contrato_id>[0-9]+)/(?P<fondo_id>[0-9]+)/$', views.balance_financiero, name='proyecto.balance_financiero'),  	
  url(r'^resumen-por-fondo-giro-contratista/(?P<fondo_id>[0-9]+)/$', views.resumen_por_fondo_giro_contratista, name='proyecto.resumen_por_fondo_giro_contratista'),  	
  url(r'^consulta_fondo_proyecto/$', views.consulta_fondo_proyecto, name='proyecto.consulta_fondo_proyecto'),
  url(r'^exportar_resumen_por_fondo/$', views.exportar_resumen_por_fondo, name='proyecto.exportar_resumen_por_fondo'),
  url(r'^exportar_resumen_por_contrato/(?P<fondo_id>[0-9]+)/$', views.exportar_resumen_por_contrato, name='proyecto.exportar_resumen_por_contrato'),
  url(r'^exportar_resumen_por_fondo_proyecto/$', views.exportar_resumen_por_fondo_proyecto, name='proyecto.exportar_resumen_por_fondo_proyecto'),
	url(r'^exportar_resumen_por_contrato_tipo_proyecto/(?P<fondo_id>[0-9]+)/$', views.exportar_resumen_por_contrato_tipo_proyecto, name='proyecto.exportar_resumen_por_contrato_tipo_proyecto'),
  url(r'^exportar_resumen_por_giros/(?P<fondo_id>[0-9]+)/$', views.exportar_resumen_por_giros, name='proyecto.exportar_resumen_por_giros'),
	url(r'^exportar_balance_financiero/$', views.exportar_balance_financiero, name='proyecto.exportar_balance_financiero'),
  url(r'^exportar_fondo_giro_contratista/$', views.exportar_fondo_giro_contratista, name='proyecto.exportar_fondo_giro_contratista'),
  url(r'^consulta_balance_financiero/$', views.consulta_balance_financiero, name='proyecto.consulta_balance_financiero'),
  url(r'^consultar_fondo_giro_contratista/$', views.consultar_fondo_giro_contratista, name='proyecto.consultar_fondo_giro_contratista'),
  #INFORMES EJECUTIVOS

  #url de vistas sin logueo

  url(r'^resumen_dispac/$', views.resumen_dispac, name='proyecto.resumen_dispac'),
  url(r'^hoja_proyecto_dispac/(?P<id_proyecto>[0-9]+)/$', views.hoja_resumen_dispac, name='proyecto.hoja_proyecto_dispac'),
  
  # PROYECTO ACTIVIDADES
  url(r'^proyecto_actividades/(?P<id_proyecto>[0-9]+)/$', views.proyectoActividades, name='proyecto_actividades'),
  url(r'^destroy_proyecto_actividades/$', views.destroyProyectoActividadesConLista, name='eliminar_proyecto_actividades'),
]