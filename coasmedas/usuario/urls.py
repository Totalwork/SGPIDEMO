from django.conf.urls import url
from . import views
from .api_usuario import crear_usuario


urlpatterns = [
  
    url(r'^$', views.index_view, name='usuario.index'),
    url(r'^login/$', views.login_view, name='usuario.login'),
    # url(r'^perfil/$', views.perfil_view, name='usuario.perfil'),
    # url(r'^editar-foto/$', views.editar_foto_view, name='usuario.editar-foto'),
    url(r'^logout/$', views.logout_view, name='usuario.logout'),
    # url(r'^perfil/$', views.profile_view, name='usuario.perfil'),
    # url(r'^editar_email/$', views.editar_email_view, name='usuario.editar_email'),
    # url(r'^editar_foto/$', views.editar_foto_view, name='usuario.editar_foto'),
    # url(r'^editar_clave/$', views.editar_clave_view, name='usuario.editar_clave'),
    url(r'^resetPassword/$', views.resetPassword, name='usuario.resetPassword'),
    url(r'^cambiar_clave/$', views.passwordChange, name='usuario.cambioclave'),    
    url(r'^cambiousuario/$', views.cambiar_usuario, name='usuario.changePass'),
    url(r'^sendMail/$', views.sendMail, name='usuario.sendMail'),
    url(r'^finishResetPass/(?P<id>[\w\-]+)/$', views.finishResetPass, name='usuario.finishResetPassword'),
    url(r'^perfil/$', views.perfil, name='usuario.perfil'),
    url(r'^accesos-directos/$', views.accesos_directos, name='usuario.accesos_directos'),
    url(r'^obtener_opciones/$', views.obtener_opciones, name='usuario.obtener_opciones'),
    url(r'^obtener_opciones_usuario/$', views.obtener_opciones_usuario, name='usuario.obtener_opciones_usuario'),
    url(r'^eliminar_opciones_usuario/$', views.eliminar_opciones_usuario, name='usuario.eliminar_opciones_usuario'),
    url(r'^guardar_opciones_usuario/$', views.guardar_opciones_usuario, name='usuario.guardar_opciones_usuario'),
    url(r'^obtener_notificaciones_autogestionables/$', views.obtener_notificaciones_autogestionables, name='usuario.guardar_opciones_usuario'),
    url(r'^autenticar/$', views.autenticar, name='usuario.autenticar'),
    url(r'^index_usuario/$', views.index_usuario, name='usuario.index_usuario'),

    url(r'^eliminar_varios_usuarios/$', views.eliminar_varios_usuarios, name='eliminar_varios_usuarios'),
    url(r'^cambiar_clave_usuario/$', views.passwordChangeUsuario, name='usuario.cambioclaveusuario'), 
    url(r'^crear-usuario/$', crear_usuario, name='usuario.api_usuario'), 

    # autenticacion enelar
    url(r'^z427FcQtOqRYwMSPZuDG7cItOqRYOBSuI3pjrYScCBtuCPETwjVeYMzyTQi7S0NM0csFbIjNWGDqUpw1MEo1DG7cIOBu3606pHzjCOBSuI3psDG7cIOBSuI3pBu3606pHzjCOs/$', views.autenticar_externos, name='usuario.autenticar-externos'),
    url(r'^descargar-aplicaion/$', views.descargarAplicaion, name='usuario.descargarAplicaion'),
    url(r'^esta-autenticado/$', views.estaAutenticado, name='usuario.estaAutenticado'),

    #graficas del index
    url(r'^obtenerdatosgraficas/$', views.get_dataGraph, name='usuario.obtener_datosGraficas'),
 
]