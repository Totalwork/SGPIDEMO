from django.db import models
from proyecto.models import Proyecto
from django.contrib.auth.models import Permission

# Create your models here.
class BaseModel(models.Model):
	nombre = models.CharField(max_length=1255)
	longitud = models.CharField(max_length=70)
	latitud = models.CharField(max_length=70)

	def __unicode__(self):
		return self.nombre

	class Meta:
		abstract = True
		permissions = (
			("puede_ver","puede ver"),
		)

class Ubicacion(BaseModel):
	proyecto = models.ForeignKey(Proyecto, on_delete=models.PROTECT)