from django.conf.urls import url

from . import views
from . import copiarArchivos

urlpatterns = [
	

	url(r'^informe/$', views.index, name='informe.index'),
	url(r'^informeMME/$', views.interventoria, name='informe.informe-mme'),
	url(r'^informeInterventoria/$', views.interventoria, name='informe.interventoria'),
	url(r'^informeRegistroSistema/$', views.registroSistema, name='informe.registroSistema'),
	url(r'^informeFotosProyecto/$', views.fotosProyecto, name='informe.fotosProyecto'),
	url(r'^informeinformeMME/$', views.informeMME, name='informe.informeMME'),

	url(r'^GenerarinformeMME/$', views.GenerarinformeMME, name='informe.GenerarinformeMME'),
	url(r'^GenerarinformeMME_validar/$', views.GenerarinformeMME_validar, name='informe.GenerarinformeMME'),

	# DISPAC
	url(r'^informeInterventoriaDispac/$', views.informeInterventoriaDispac, name='informeInterventoriaDispac'),
	
	# ELECTRICARIBE

	# DISPAC Y ELECTRICARIBE
	url(r'^generate-informeFotosProyecto/$', views.informeFotosProyecto, name='informeFotosProyecto'),
	url(r'^obtener-columnas/$', views.obtenerColumnas, name='informe.obtenerColumnas'),
	url(r'^generar-informe-dinamico/$', views.generarInformeDinamico, name='informe.generarInformeDinamico'),
	url(r'^informe-dinamico/$', views.informeDinamico, name='informe.informeDinamico'),
	url(r'^crear-estrutura-contrato/$', views.crearEstruturaContrato, name='informe.crearEstruturaContrato'),
	url(r'^generar-informe-trimestral/$', views.generarInformeTrimestral, name='informe.generarInformeTrimestral'),
	url(r'^crear-estrutura-encabezado-giros/$', views.crearEstruturaEncabezadoGiros, name='informe.crearEstruturaEncabezadoGiros'),
	# url(r'^generar-mapa-archivos/$', views.generarMapaArchivos, name='informe.generarMapaArchivos'),
	url(r'^copiar-archivos/$', copiarArchivos.copiarArchivos, name='informe.copiarArchivos'),
	url(r'^crear-linea-infotecnica-eq/$', copiarArchivos.crearLineasInfoTecnicaEQ, name='informe.crearLineasInfoTecnicaEQ'),
	url(r'^crear-linea-infotecnica-at/$', copiarArchivos.crearLineasInfoTecnicaAT, name='informe.crearLineasInfoTecnicaAT'),

	url(r'^descargar-plantilla-actividades-contrato/(?P<proyecto_id>[0-9]+)$', views.descargar_plantilla_actividades_contrato, name='informe.descargar_plantilla_actividades_contrato'),
	url(r'^guardar-actividades-archivo/$', views.guardar_actividades_contrato, name='informe.guardar_actividades_contrato'),
]