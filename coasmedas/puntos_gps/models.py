from django.db import models
from proyecto.models import Proyecto

class BaseModel(models.Model):
	nombre = models.CharField(max_length=1000)

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.nombre

class PuntosGps(BaseModel):

	proyecto = models.ForeignKey(Proyecto , related_name = 'fk_Proyecto_proyecto',on_delete=models.PROTECT)
	longitud = models.CharField(max_length=50)
	latitud = models.CharField(max_length=50)
						
	class Meta:
		db_table = "puntos_gps"
		permissions = (("can_see_puntosgps","can_see_puntosgps"),("can_see_cargaMasiva","can_see_cargaMasiva"),)		
