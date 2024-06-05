from django.db import models
from proyecto.models import Proyecto
from contrato.models import Contrato
from usuario.models import Usuario
from datetime import *
from django.utils import * 
from sinin4.functions import functions
# Create your models here.


class BaseModel(models.Model):
	nombre = models.CharField(max_length=255)

	class Meta:
	 	abstract = True
	 	#permission = ('puede_ver','puede_ver')


	def __unicode__(self):
		return self.nombre


class APeriodicidad(BaseModel):
	numero_dias=models.IntegerField()

	class Meta:
		db_table = 'avance_de_obra_periodicidad'
		permissions = (
			("can_see_periodicidad","can see periodicidad"),
		) 

class AEsquemaCapitulos(BaseModel):
	macrocontrato=models.ForeignKey(Contrato,related_name="esquema_contrato",on_delete=models.PROTECT)

	class Meta:
		db_table = 'avance_de_obra_esquema_capitulos'
		permissions = (
			("can_see_esquemacapitulos","can see esquemacapitulos"),
		)


class AEsquemaCapitulosActividades(BaseModel):
	esquema=models.ForeignKey(AEsquemaCapitulos,related_name="actividades_esquema",on_delete=models.PROTECT)
	nivel=models.IntegerField()
	padre = models.IntegerField()
	peso = models.FloatField()

	class Meta:
		db_table = 'avance_de_obra_esquema_capitulos_actividades'
		permissions = (
			("can_see_esquemacapitulosactividades","can see esquemacapitulosactividades"),
		)

class AReglasEstado(models.Model):
	esquema=models.ForeignKey(AEsquemaCapitulos,related_name="regla_esquema",on_delete=models.PROTECT)
	orden=models.IntegerField()
	operador=models.IntegerField()
	limite=models.FloatField()
	estado=models.TextField(blank=True, null=True)

	class Meta:
		db_table = 'avance_de_obra_regla_estado'
		permissions = (
			("can_see_reglaEstado","can see reglaEstado"),
		)

	def __unicode__(self):
		return self.estado

class BCronograma(BaseModel):
	proyecto = models.ForeignKey(Proyecto,related_name="cronograma_proyecto",on_delete=models.PROTECT)
	intervalos=models.IntegerField()
	linea_base_terminada=models.BooleanField(default=False)
	fecha_inicio_cronograma=models.DateField(null=True)
	periodicidad=models.ForeignKey(APeriodicidad,related_name="cronograma_periodicidad",on_delete=models.PROTECT)
	esquema=models.ForeignKey(AEsquemaCapitulos,related_name="cronograma_esquema",on_delete=models.PROTECT)
	estado = models.ForeignKey(AReglasEstado,related_name="cronograma_regla",on_delete=models.PROTECT,null=True, blank=True)

	class Meta:
		db_table = 'avance_de_obra_cronograma'
		permissions = (
			("can_see_bcronograma","can see bcronograma"),
		) 

	def porcentaje_avance(self):
		porcentaje=0
		intervalo=CIntervaloCronograma.objects.filter(cronograma_id=self.id,tipo_linea=3).values('id').order_by('intervalo').last()
	
		if intervalo is not None:
			queryporcentaje=Porcentaje.objects.filter(intervalo_id=intervalo['id'],tipo_linea=3).values('porcentaje').first()

			if queryporcentaje is None:
				porcentaje=0
			else:
				porcentaje=queryporcentaje['porcentaje']

		return porcentaje

class CIntervaloCronograma(models.Model):
	cronograma=models.ForeignKey(BCronograma,related_name="intervalo_cronograma",on_delete=models.PROTECT)
	intervalo=models.IntegerField()
	tipo_linea=models.IntegerField()
	sinAvance=models.BooleanField(default=False)
	comentario_sinAvance=models.TextField(null=True,blank=True)
	fecha_corte=models.DateField(null=True)

	class Meta:
		db_table = 'avance_de_obra_intervalo_cronograma'

	def __unicode__(self):
		return self.intervalo

class Comentario(models.Model):
	intervalo=models.ForeignKey(CIntervaloCronograma,related_name="comentario_intervalo",on_delete=models.PROTECT)
	tipo_linea=models.IntegerField()
	comentario = models.TextField()
	usuario=models.ForeignKey(Usuario,related_name="comentario_usuario",on_delete=models.PROTECT)
	fecha=models.DateField(auto_now_add=True, blank=True)

	class Meta:
		db_table = 'avance_de_obra_comentario'

	def __unicode__(self):
		return self.comentario

class DActividad(models.Model):
	cronograma=models.ForeignKey(BCronograma,related_name="actividad_cronograma",on_delete=models.PROTECT)
	esquema_actividades=models.ForeignKey(AEsquemaCapitulosActividades,related_name="actividad_esquemactividades",on_delete=models.PROTECT)

	class Meta:
		db_table = 'avance_de_obra_actividad'
		permissions = (
			("can_see_dactividad","can see dactividad"),
		)




class Linea(models.Model):
	intervalo=models.ForeignKey(CIntervaloCronograma,related_name="linea_intervalo",on_delete=models.PROTECT)
	tipo_linea=models.IntegerField()
	cantidad = models.FloatField()
	actividad=models.ForeignKey(DActividad,related_name="linea_actividad",on_delete=models.PROTECT)

	class Meta:
		db_table = 'avance_de_obra_linea'
		permissions = (
			("can_see_linea","can see linea"),
		)

	def __unicode__(self):
		return self.actividad

class Meta(models.Model):
	actividad=models.ForeignKey(DActividad,related_name="meta_actividad",on_delete=models.PROTECT)
	cantidad=models.FloatField()

	class Meta:
		db_table = 'avance_de_obra_meta'
		permissions = (
			("can_see_meta","can see meta"),
		)

	def __unicode__(self):
		return self.actividad

class Porcentaje(models.Model):
	intervalo=models.ForeignKey(CIntervaloCronograma,related_name="porcentaje_intervalo",on_delete=models.PROTECT)
	tipo_linea=models.IntegerField()
	porcentaje=models.FloatField()

	class Meta:
		db_table = 'avance_de_obra_porcentaje'

	def __unicode__(self):
		return self.porcentaje




class Soporte(BaseModel):
	intervalo=models.ForeignKey(CIntervaloCronograma,related_name="soporte_intervalo",on_delete=models.PROTECT)
	#ruta=models.FileField(upload_to=functions.path_and_rename('avanceObra/soporte','ado'),blank=True, null=True)
	ruta=models.FileField(upload_to='avanceObra/soporte',blank=True, null=True)

	class Meta:
		db_table = 'avance_de_obra_soporte'





			
