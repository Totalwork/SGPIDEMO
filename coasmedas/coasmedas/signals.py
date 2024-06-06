# from usuario.models import UserSession
# from django.contrib.sessions.models import Session

# def user_logged_in_handler(sender, request, user, **kwargs):
# 	sessiones = Session.objects.filter(session_key=request.session.session_key)
# 	if request.session.session_key and sessiones.count() > 0:		
# 		UserSession.objects.get_or_create(
# 			user = user,
# 			session_id = request.session.session_key
# 		)
		
# 	keys = [v.session.session_key for v in UserSession.objects.filter(user__id=request.user.id).exclude(session__session_key=request.session.session_key)]
# 	if request.user.usuario.cantidad_sesiones > 0 and len(keys) > request.user.usuario.cantidad_sesiones - 1:		
# 		sesion = Session.objects.filter(session_key__in=keys).first()
# 		sesion.delete()

from usuario.models import UserSession
from django.contrib.sessions.models import Session

def user_logged_in_handler(sender, request, user, **kwargs):
	sessiones = Session.objects.filter(session_key=request.session.session_key)
	if request.session.session_key and sessiones.count() > 0:		
		UserSession.objects.get_or_create(
			user = user,
			session_id = request.session.session_key
		)
		
	keys = [v.session.session_key for v in UserSession.objects.filter(user=request.user).exclude(session_id=request.session.session_key).order_by('-id')]
	if request.user.usuario.cantidad_sesiones > 0 and len(keys) > request.user.usuario.cantidad_sesiones - 1:		
		sesion = Session.objects.filter(session_key__in=keys).first()
		sesion.delete()


