from django.conf.urls import url

from . import views


urlpatterns = [
   

  url(r'^miNube/$', views.miNube, name='miNube.miNube'),
  url(r'^valida_espacio/$', views.validarEspacio, name='validarEspacio'),# lista archivo   de un contenido
  #crear carpeta 
  url(r'^destroyArchivo/$', views.destroyArchivo, name='destroyArchivo'),# eliminar archivo
  url(r'^list_archivo_carpeta/$', views.listArchivoUsuarioCarpeta, name='listArchivoUsuarioCarpeta'),# lista carpetas para crear el arbol
  url(r'^list_archivo/$', views.listArchivoUsuario, name='listArchivoUsuario'),# lista archivo   de un contenido

  #DOWNLOAD FILE 
  url(r'^download_file/$', views.downloadFile, name='downloadFile'),# descarga de archivos

  #PROYECTO  archivos 
  url(r'^list_proyectosSin_archivo/$', views.listProyectosSinArchivo, name='listProyectosSinArchivo'),# listar proyectos que no estan en la lista de archivos
  url(r'^list_proyectosCon_archivo/$', views.listProyectosConArchivo, name='listProyectosConArchivo'),# listar proyecto que estan relacionado con la lista de archivo
  url(r'^create_proyectoCon_archivo/$', views.createProyectoConArchivo, name='createProyectoConArchivo'),# crear proyecto con archivo
  url(r'^destroy_proyectoCon_archivo/$', views.destroyProyectoConArchivo, name='destroyProyectoConArchivo'),# eliminar proyecto con archivo

  #CONTRATOS archivos 
  url(r'^list_contratosSin_archivo/$', views.listContratosSinArchivo, name='listContratosSinArchivo'),# listar contrato que no estan en la lista de archivo
  url(r'^list_contratosCon_archivo/$', views.listContratosConArchivo, name='listContratosConArchivo'),# listar contrato que estan relacionado con la lista de archivo
  url(r'^create_contratoCon_archivo/$', views.createContratoConArchivo, name='createContratoConArchivo'),# crear contrato con archivo
  url(r'^destroy_contratoCon_archivo/$', views.destroyContratoConArchivo, name='destroyContratoConArchivo'),# eliminar contrato con archivo
  

  #compartir archivos con usuarios
  url(r'^list_usuarioSin_archivo/$', views.listUsuarioSinArchivo, name='listUsuarioSinArchivo'),# actualizar nombre archivo
  url(r'^list_usuarioCon_archivo/$', views.listUsuarioConArchivo, name='listUsuarioConArchivo'),# actualizar nombre archivo
  url(r'^create_usuarioCon_archivo/$', views.createUsuarioConArchivo, name='createUsuarioConArchivo'),# actualizar nombre archivo
  url(r'^destroy_usuarioCon_archivo/$', views.destroyUsuarioConArchivo, name='destroyUsuarioConArchivo'),# actualizar nombre archivo

  # MOVER ARCHIVO A OTRA CARPETA
  url(r'^move_file/$', views.moveFile, name='moveFile'),# mover archivo

  url(r'^subir_archivoAsync/$', views.subirAsyncArchivos, name='subirAsyncArchivos'),# lista archivo   de un contenido
  url(r'^verifica_cargandoArchivo/$', views.verificaTareaArchivo, name='verificaTareaArchivo'),# lista archivo   de un contenido


  # MOSTRAR ARCHIVOS EN RESUMEN DE PROYECTO POR CONTRATOS O POR PROYECTOS
  url(r'^list_carpeta_ContratoProyecto/$', views.listFolderContratoProyecto, name='listFolderContratoProyecto'),# 
  url(r'^list_archivo_ContratoProyecto/$', views.listFileContratoProyecto, name='listFileContratoProyecto'),# 
  url(r'^obtener_carpetas_arbol/$', views.obtenerCarpetasArbol, name='obtenerCarpetasArbol'),
  url(r'^obtener_archivo_por_id/(?P<id>[0-9]+)/$', views.obtener_archivo_por_id, name='obtener_archivo_por_id'),
  url(r'^guardar-archivo/$', views.guardarArchivo, name='mu_nube.guardarArchivo'),

  url(r'^descargar-un-archivo/$', views.descargarUnArchivo, name='descargarUnArchivo'),# descarga de archivos
]