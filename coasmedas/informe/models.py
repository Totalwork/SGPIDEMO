from django.db import models
from proyecto.models import Proyecto
from contrato.models import Actividad

# Create your models here.

class Informe(models.Model):
	nombre = models.CharField(max_length=50)

	class Meta:
		permissions = (("can_see_informe_dinamico","can_see_informe_dinamico"),)

	def __unicode__(self):
		return self.nombre

class Proyecto_Actividad_contrato(models.Model):
	proyecto 		= models.ForeignKey(Proyecto, on_delete=models.PROTECT, blank=True)
	actividad 		= models.ForeignKey(Actividad, on_delete=models.PROTECT, blank=True)
	valor 			= models.CharField(max_length=4000,null=True,blank=True)

	class Meta:
		db_table = 'proyecto_actividad_contrato'
		unique_together=('proyecto','actividad')