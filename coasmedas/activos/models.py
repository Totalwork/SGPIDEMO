from django.db import models
from usuario.models import Persona
from contrato.models import Contrato
from parametrizacion.models import Funcionario
from sinin4.functions import functions, RandomFileName

# Create your models here.

class Categoria (models.Model):
	nombre = models.CharField(max_length=30,null=False, blank= False)

	def __str__(self):		
		return str(self.nombre)
	class Meta:
		db_table = 'activos_categoria'
		
class Tipo_Activo (models.Model):
	categoria = models.ForeignKey(Categoria,related_name="tipoactivo_categoria", on_delete=models.PROTECT, null=False, blank=False)
	nombre = models.CharField(max_length=30, null=False, blank=False)
	prefijo = models.CharField(max_length=10, null=True, blank=True)

	def __str__(self):		
		return str(self.nombre)
	class Meta:
		db_table = 'activos_tipo'

class Activo (models.Model):
	tipo = models.ForeignKey(Tipo_Activo, related_name="activo_tipoactivo", on_delete=models.PROTECT, null=True, blank=True)
	identificacion = models.CharField(max_length=50, null=True, blank=True)
	serial_placa = models.CharField(max_length=50, null=True, blank=True)
	descripcion = models.CharField(max_length=150, null=False, blank=False)
	contrato = models.ForeignKey(Contrato, related_name="activo_contrato", on_delete=models.PROTECT, null=False, blank=False)
	valor_compra = models.BigIntegerField(null=True, blank=True)
	responsable = models.ForeignKey(Funcionario,related_name="activo_funcionario", on_delete=models.PROTECT, null=False, blank=False)
	vida_util_dias = models.IntegerField(null=False, blank=False)
	periodicidad_mantenimiento = models.IntegerField(null=True, blank= True)
	debaja = models.BooleanField(default= False, null=False, blank= False)
	motivo_debaja = models.CharField(max_length=150, null=True, blank=True)
	#soportedebaja = models.FileField(upload_to='activos', null=True, blank= True)
	soportedebaja = models.FileField(upload_to=RandomFileName('activos','act'), null=True, blank= True)
	fecha_baja = models.DateField(null=True, blank= True)
	fecha_alta = models.DateField(null=False, blank= False)

	def __str__(self):		
		return str(self.identificacion)
	class Meta:
		db_table = 'activos_activo'
		permissions = (
			("can_see_activos","can see activos"),
		)

	

class Activo_gps(models.Model):
	activo = models.ForeignKey(Activo, related_name="activogps_activo",on_delete=models.PROTECT, null=False, blank=False)
	nombre =  models.CharField(max_length=30, null=True, blank=True)
	longitud =  models.CharField(max_length=50)
	latitud =  models.CharField(max_length=50)

	def __str__(self):
		return str (self.nombre)+' | '+ str(self.longitud) +', '+str(self.latitud)
	class Meta:
		db_table = 'activos_gps'
		unique_together=('activo','nombre')

		
class Atributo (models.Model):
	tipo = models.ForeignKey(Tipo_Activo,related_name="atributo_tipo", on_delete=models.PROTECT, null=False, blank=False)
	nombre = models.CharField(max_length=30, null=False, blank=False)
	requiere_soporte = models.BooleanField(default= False, null=False, blank= False)

	def __str__(self):		
		return str(self.nombre)
	class Meta:
		db_table = 'activos_atributo'


class Activo_atributo (models.Model):
	activo = models.ForeignKey(Activo, related_name="activoatributo_activo",on_delete=models.PROTECT, null=False, blank=False)
	atributo = models.ForeignKey(Atributo,related_name="activoatributo_atributo", on_delete=models.PROTECT, null=False, blank=False)
	valor = models.CharField(max_length=30, null=False, blank=False)

	def __str__(self):		
		return str(self.activo.identificacion) + ', ' + str(self.atributo.nombre)
	class Meta:
		db_table = 'activos_activo_atributo'
		


class Activo_atributo_soporte (models.Model):
	activo_atributo = models.ForeignKey(Activo_atributo, related_name="activoatributosoporte_activoatributo", on_delete=models.PROTECT, null=False, blank=False)
	#documento = models.FileField(upload_to='activos/atributo_soporte', null=False, blank= False)
	documento = models.FileField(upload_to=RandomFileName('activos/atributo_soporte','atri_sop'), null=False, blank= False)
	
	def __str__(self):		
		return str(self.documento)
	class Meta:
		db_table = 'activos_activo_atributo_soporte'


class Activo_persona (models.Model):
	persona = models.ForeignKey(Persona,related_name="activopersona_persona",  on_delete=models.PROTECT, null=False, blank= False)
	activo = models.ForeignKey(Activo, related_name="activopersona_activo", on_delete=models.PROTECT, null=False, blank= False)
	
	def __str__(self):		
		return str(self.activo+' de '+self.persona)
	class Meta:
		db_table = 'activos_activo_persona'

class Motivo (models.Model):
	tipo_activo = models.ForeignKey(Tipo_Activo,related_name="motivo_tipoactivo", on_delete=models.PROTECT,null=False, blank=False)
	nombre = models.CharField(max_length=30,null=False, blank= False)

	def __str__(self):		
		return str(self.nombre)
	class Meta:
		db_table = 'activos_motivo'



class Mantenimiento (models.Model):
	activo = models.ForeignKey(Activo, related_name="mantenimiento_activo",on_delete=models.PROTECT, null=False, blank=False)
	motivo = models.ForeignKey(Motivo, related_name="mantenimiento_motivo",on_delete=models.PROTECT, null=False, blank=False)
	fecha =  models.DateField(null=False, blank= False)
	hora = models.TimeField(null=True, blank= True)
	observaciones = models.CharField(max_length=50, null=True, blank=True)
	contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT, null=False, blank=False)
	
	def __str__(self):		
		return str(self.activo) + ' | ' + str(self.motivo)

	class Meta:
		db_table = 'activos_mantenimiento'
		





class Soporte_mantenimiento (models.Model):
	mantenimiento = models.ForeignKey(Mantenimiento, related_name="soportemantenimiento_mantenimiento", on_delete=models.PROTECT, null=False, blank=False)
	nombre = models.CharField(max_length=30,null=True, blank= True)
	#archivo = models.FileField(upload_to='activos/soporte_mantenimiento', null=False, blank= False)
	archivo = models.FileField(upload_to=RandomFileName('activos/soporte_mantenimiento','sop_man'), null=False, blank= False)
	
	def __str__(self):		
		return str(self.nombre)
	class Meta:
		db_table = 'activos_soporte_mantenimiento'
