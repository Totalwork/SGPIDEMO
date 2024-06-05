from django.db import models
from proyecto.models import Proyecto
from usuario.models import Usuario
from datetime import *
from django.utils import timezone
# Create your models here.

class Bitacora(models.Model):
	comentario = models.TextField()
	usuario = models.ForeignKey(Usuario, related_name = 'bitacora_usuario' , on_delete=models.PROTECT) 
	proyecto = models.ForeignKey(Proyecto, related_name = 'bitacora_proyecto' , on_delete=models.PROTECT)
	fecha = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	class Meta:
		permissions = (
			("can_see_bitacora", "can see bitacora"),
			("see_all_bitacora", "see all bitacora"),
		) 

	def __unicode__(self):
		return self.comentario

	#los minutos que han pasado despues de guardado mensaje	
	def minutos(self):
		minutos = 0
		if self.fecha:
			date1 = timezone.now()					
			date2 = self.fecha				
			datediff = date1 - date2				
			minutos = datediff.total_seconds() / 60
		return minutos #* 24 * 60