from django.db import models
from usuario.models import Usuario
from django.contrib.auth.models import Permission

# Create your models here.
class BaseModel(models.Model):
	destino = models.CharField(max_length=100)
	icono = models.CharField(max_length=50)

	def __unicode__(self):
		return self.texto

	class Meta:
 		abstract = True
		# permissions = (
		# 	("puede_ver","puede ver"),
		# )

class Opcion(BaseModel):
	orden = models.IntegerField()
	padre = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.PROTECT)
	texto = models.CharField(max_length=50)
	permiso = models.ForeignKey(Permission, blank=True, null=True, related_name='permiso', on_delete=models.PROTECT)
	#tieneHijos = models.BooleanField(default=False)
	urlActiva = models.CharField(max_length=60, blank=True, null=True)

class Opcion_Usuario(models.Model):
	opcion = models.ForeignKey(Opcion, on_delete=models.PROTECT)
	usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
	#esAccesoDirecto = models.BooleanField(default=False)
