from django.db import models
from proyecto.models import Proyecto
from tipo.models import Tipo
from proceso.models import FProcesoRelacion
from django.db.models import Count
from sinin4.functions import functions, RandomFileName


class ALote(models.Model):
	proyecto=models.ForeignKey(Proyecto,related_name="p_p_construccion_lote_proyecto",on_delete=models.PROTECT)
	nombre = models.CharField(max_length=300,null=True,blank=True)
	direccion = models.CharField(max_length=300,null=True,blank=True)
	cantidad_estructura = models.IntegerField(null=True,blank=True,default=0)

	def cantidad_propietarios_asociados(self):
		cantidad=EPropietarioLote.objects.filter(lote__id=self.id).count()
		return cantidad


	def proceso_relacion_id(self):
		procesoRelacionid = FProcesoRelacion.objects.filter(proceso__id=7,idApuntador=self.proyecto.id,idTablaReferencia=self.id).values('id')
		return procesoRelacionid

	class Meta:
		db_table = "p_p_construccion_lote"
		permissions = (("can_see_ALote","can_see_ALote"),)
		verbose_name='Lote'

	def __unicode__(self):
		return self.nombre				


class BSoporte(models.Model):
	proyecto=models.ForeignKey(Proyecto,related_name="p_p_construccion_soporte_proyecto",on_delete=models.PROTECT)
	soporte=models.FileField(upload_to=RandomFileName('lote/soporte'),blank=True, null=True)
	#soporte=models.FileField(upload_to=RandomFileName('lote/soporte','plz'),blank=True, null=True) 
	tipo=models.ForeignKey(Tipo,related_name="p_p_construccion_soporte_tipo",null=True,blank=True,on_delete=models.PROTECT)
	nombre = models.CharField(max_length=300,null=True,blank=True)

	
	class Meta:
		db_table = "p_p_construccion_soporte"
		permissions = (("can_see_BSoporte","can_see_BSoporte"),)
		verbose_name='Soporte'


	def __unicode__(self):
		return self.nombre



class CEstructura(models.Model):
	codigo = models.CharField(max_length=100,null=True,blank=True)
	lote=models.ForeignKey(ALote,related_name="p_p_construccion_estructura_lote",on_delete=models.PROTECT)
	
	class Meta:
		db_table = "p_p_construccion_estructura"
		permissions = (("can_see_CEstructura","can_see_CEstructura"),)
		verbose_name='Estructura'

	def __unicode__(self):
		return self.codigo						
	


class DPropietario(models.Model):
	cedula = models.CharField(max_length=300,null=True,blank=True,unique=True)
	nombres = models.CharField(max_length=300,null=True,blank=True)
	apellidos = models.CharField(max_length=300,null=True,blank=True)
	telefono = models.CharField(max_length=200,null=True,blank=True)
	correo = models.CharField(max_length=300,null=True,blank=True)

	class Meta:
		db_table = "p_p_construccion_propietario"
		permissions = (("can_see_DPropietario","can_see_DPropietario"),)
		verbose_name='Propietario'

	def __unicode__(self):
		return self.nombres +' '+ self.apellidos



class EPropietarioLote(models.Model):
	lote=models.ForeignKey(ALote,related_name="p_p_construccion_propietario_lote_lote",on_delete=models.PROTECT)
	propietario=models.ForeignKey(DPropietario,related_name="p_p_construccion_propietario_lote_propietario",on_delete=models.PROTECT)
	
	class Meta:
		db_table = "p_p_construccion_propietario_lote"
		permissions = (("can_see_EPropietarioLote","can_see_EPropietarioLote"),)
		verbose_name='Propietario lote'
			

