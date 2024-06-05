from django.db import models
from django.core.mail import EmailMessage
from datetime import datetime
from django.template.defaultfilters import truncatechars
from django.conf import settings
# from utilidades.mailGun import Mail
from utilidades.mail import Mail

# Create your models here.
class Mensaje(models.Model):
	remitente =  models.EmailField()
	destinatario = models.TextField()
	copia = models.TextField(blank=True, null=True)
	asunto = models.CharField(max_length=255)
	contenido = models.TextField()
	tieneAdjunto = models.BooleanField(default=False)
	adjunto = models.TextField(blank=True, null=True)
	appLabel = models.CharField(max_length=100)
	enviado = models.BooleanField(default=False)
	horaPreparacion = models.DateTimeField(auto_now_add=True, blank=True)
	horaEnvio = models.DateTimeField(blank=True,null=True)

	def __unicode__(self):
		return self.asunto
	@property
	def resumeDestinatario(self):
		return truncatechars(self.destinatario, 30)

	#envio de correos simple sin copias, 1 remitente, 1 destinatario	
	def simpleSend(self):
		self.asunto = '{0}-{1}'.format(settings.SOURCE, self.asunto)
		res=''
		email = EmailMessage(
			self.asunto,
			self.contenido,
			self.remitente,
			[self.destinatario]
			)
		email.content_subtype = "html"
		# res =email.send(fail_silently=False)
		# #res = send_mail(self.asunto,self.contenido,self.remitente,[self.destinatario],fail_silently=False)
		# if res ==1:
		# 	self.enviado=True
		# 	self.horaEnvio = datetime.now()
		# 	self.save()

		# return res
		
		res = Mail.send(self.asunto, self.contenido, self.destinatario, self.adjunto)
		print(res)
		# if res ==1:
		self.enviado=True
		self.contenido = res
		self.hora_envio = datetime.now()
		self.save()
		
		return self

	#envio de correos con varios destinatarios, varias copias y adjuntos. 
	#(varias direcciones separadas por ";")  		
	def Send(self):
		res=''
		#construir el array de los destinatarios
		self.asunto = '{0}-{1}'.format(settings.SOURCE, self.asunto)
		ArrayDestinatarios=[x.strip() for x in self.destinatario.split(";")]
		#construir el array de las copias
		if self.copia:
			ArrayCopia=[x.strip() for x in self.copia.split(";")]
		else:
			ArrayCopia=[]
		# email = EmailMessage(
		# 	self.asunto,
		# 	self.contenido,
		# 	self.remitente,
		# 	ArrayDestinatarios,
		# 	ArrayCopia
		# 	)
		# if self.adjunto:
		# 	email.attach_file(self.adjunto)

		# email.content_subtype = "html"
		# print(email)
		# res =email.send(fail_silently=False)
		res = Mail.sendMultiples(self.asunto, self.contenido, ArrayDestinatarios, ArrayCopia, self.adjunto)
		print(res)
		if res:
			self.enviado=True
			self.horaEnvio = datetime.now()
			self.save()

		return res		


			
