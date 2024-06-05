from django.contrib import admin
from .models import Mensaje
# Register your models here.
class AdminMensaje(admin.ModelAdmin):
	list_display=('asunto','remitente','resumeDestinatario','tieneAdjunto',
		'appLabel','enviado', 'horaPreparacion','horaEnvio')
	search_fields=('asunto','destinatario','contenido','adjunto')
	list_filter=('remitente','tieneAdjunto','appLabel','enviado','horaPreparacion','horaEnvio')

admin.site.register(Mensaje,AdminMensaje)
