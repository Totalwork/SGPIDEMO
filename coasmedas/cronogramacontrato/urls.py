from django.conf.urls import url
from cronogramacontrato.views import index_cronogramacontrato,\
index_esquemacronograma, index_capitulosesquema, index_listadoactividades, \
index_seguimientodelcontrato, getAnosyFondos, fillGraph, fillGraphById, \
getActividadesContratosTablaById, VerSoporte, CambiarEstadoCronograma, \
actualizar_capitulo, listUrlsById, getActivities, editarProgramacion, \
registarInicioActividad, registarFinActividad, actualizar_actividad, \
getListaContratos, asociarCronogramaContrato

urlpatterns = [
    url(r'^home/$', index_cronogramacontrato, name='cronogramacontrato.home'),
    url(r'^esquemacronograma/$', index_esquemacronograma, name='cronogramacontrato.esquemacronograma'),
    url(r'^capitulosesquema/(?P<id_cronograma>[0-9]+)/$', index_capitulosesquema, name='cronogramacontrato.capitulosesquema'),
    url(r'^listadoactividades/(?P<capituloid>[0-9]+)/$', index_listadoactividades, name='cronogramacontrato.listadoactividades'),
    url(r'^seguimientodelcontrato/(?P<id_contrato>[0-9]+)/$', index_seguimientodelcontrato, name='cronogramacontrato.seguimientodelcontrato'),
    url(r'^getanosyfondos/$', getAnosyFondos, name='cronogramacontrato.getAnosyFondos'),
    url(r'^getdatagraph/$', fillGraph, name='cronogramacontrato.getdatagraph'),
    url(r'^getdatagraphbyid/$', fillGraphById, name='cronogramacontrato.getdatagraphbyid'),
    url(r'^getactividadescontratostablabyid/$', getActividadesContratosTablaById, name='cronogramacontrato.getActividadesContratosTablaById'),
    url(r'^getsoportesbyid/$', VerSoporte, name='cronogramacontrato.VerSoporte'),
    url(r'^cambiarestadocronograma/$', CambiarEstadoCronograma, name='cronogramacontrato.CambiarEstadoCronograma'),
    url(r'^actualizarcapitulo/$', actualizar_capitulo, name='cronogramacontrato.actualizar_capitulo'),
    url(r'^actualizaractividad/$', actualizar_actividad, name='cronogramacontrato.actualizar_actividad'),
    url(r'^getslistbyid/$', listUrlsById, name='cronogramacontrato.VerSoporte'),
    url(r'^getslistacontratos/$', getListaContratos, name='cronogramacontrato.getListaContratos'),
    url(r'^asociarcronogramacontrato/$', asociarCronogramaContrato, name='cronogramacontrato.asociarCronogramaContrato'),
    url(r'^getactivities/$', getActivities, name='cronogramacontrato.getActivities'),
    url(r'^programar/$', editarProgramacion, name='cronogramacontrato.programar'),
    url(r'^registroinicio/$', registarInicioActividad, name='cronogramacontrato.registroInicioActividad'),
    url(r'^registrofin/$', registarFinActividad, name='cronogramacontrato.registroFinActividad'),
]