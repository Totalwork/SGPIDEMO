from django.db import models
from django.conf import settings
from empresa.models import Empresa 
from sinin4.functions import functions
from django.contrib.sessions.models import Session
# Create your models here.


class Persona(models.Model):
	cedula = models.BigIntegerField(unique=True)
	nombres = models.CharField(max_length=255)
	apellidos = models.CharField(max_length=255)
	correo = models.EmailField(max_length=70,blank=True, null=True)
	telefono = models.CharField(max_length=200,blank=True, null=True)	
	def __unicode__(self):
		return self.nombres + ' ' + self.apellidos

	class Meta:
		ordering=['nombres', 'apellidos']	

class Usuario(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	persona = models.ForeignKey(Persona,related_name="persona_usuario",on_delete=models.PROTECT)
	# foto = models.ImageField(upload_to=functions.path_and_rename('usuario','user'),blank=True, null=True, default='usuario/default.jpg')
	foto = models.ImageField(upload_to='usuario',blank=True, null=True, default='usuario/default.jpg')
	empresa = models.ForeignKey(Empresa,related_name="Empresa_usuario",on_delete=models.PROTECT)
	iniciales = models.CharField(max_length=5)
	cantidad_sesiones = models.IntegerField(null=True, blank=True, default=1)
	def __unicode__(self):
		return unicode(self.user.username) or u''
	
	@property	
	def foto_publica(self):
		if self.foto:			
			return functions.crearRutaTemporalArchivoS3(str(self.foto))
		else:
			return None	

	def foto_usuario(self):
		return """<img width="100px" height="120px" src="%s" alt="foto del usuario">""" % self.foto_publica


	def nombres(self):
		return self.persona.nombres

	def apellidos(self):
		return self.persona.apellidos

	def correo(self):
		return self.persona.correo

	foto_usuario.allow_tags=True	  

class UserSession(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='logged_in_user', on_delete=models.PROTECT)
	# Session keys are 32 characters long
	# session_key = models.CharField(max_length=32, null=True, blank=True)
	session = models.ForeignKey(Session, related_name="Sesion", on_delete=models.CASCADE)
	def __str__(self):
		return self.user.username