from django.db import models
from proyecto.models import Proyecto
from usuario.models import Usuario
from estado.models import Estado
from tipo.models import Tipo
from sinin4.functions import functions, RandomFileName
from django.utils.html import format_html
from datetime import *


class Servidumbre_expediente(models.Model):
	proyecto = models.OneToOneField(Proyecto , related_name = 'f_proyecto_proyecto' , on_delete=models.PROTECT, unique= True)
	fecha_creacion = models.DateField(auto_now_add = True)
	usuario_creador = models.ForeignKey(Usuario, related_name='f_Usuario_usuario', on_delete=models.PROTECT)
	estado = models.ForeignKey(Estado , related_name = 'f_Servidumbre_documento_Estado' , 
		on_delete=models.PROTECT, default = 159)


	class Meta:
		db_table = 'servidumbre_expediente'	
		unique_together = [
			["proyecto",],
		]
		permissions = (("can_see_Expediente","can_see_Expediente"),)	

	def __unicode__(self):
		return  self.proyecto.municipio.departamento.nombre + ' | ' + self.proyecto.municipio.nombre + ' | '  +  self.proyecto.nombre
	

class Servidumbre_grupo_documento(models.Model):	
	nombre =  models.CharField(max_length = 60, null = False)

	class Meta:
		db_table = 'servidumbre_grupo_documento'
		unique_together = (("nombre",))
		permissions = (("can_see_ExpedienteGrupoDocumento","can_see_ExpedienteGrupoDocumento"),)

	def __unicode__(self):
		return self.nombre

class Servidumbre_documento(models.Model):
	grupo_documento = models.ForeignKey(Servidumbre_grupo_documento , related_name = 'f_Servidumbre_grupo_documento' , on_delete=models.PROTECT)
	nombre =  models.CharField(max_length = 60, null = False)

	class Meta:	
		db_table =	'servidumbre_documento'
		unique_together = [
			["grupo_documento","nombre"],
		]
		
	def __unicode__(self):
		return self.nombre


class Servidumbre_persona(models.Model):
	cedula = models.IntegerField(blank = False, unique = True)
	nombres =  models.CharField(max_length = 60, blank = False)
	apellidos = models.CharField(max_length = 60, blank = False)
	celular = models.CharField(max_length = 60, blank = True)
	telefono = models.CharField(max_length = 60, blank = True)

	class Meta:
		db_table = 'servidumbre_persona'		
	def __unicode__(self):
		return self.nombres + ' ' +self.apellidos

class Servidumbre_predio(models.Model):
	expediente = models.ForeignKey(Servidumbre_expediente , related_name = 'fk_Servidumbre_expediente' , on_delete=models.PROTECT)
	persona = models.ForeignKey(Servidumbre_persona , related_name = 'fk_Servidumbre_persona' , on_delete=models.PROTECT)
	nombre_direccion = models.CharField(max_length = 150, blank = False, unique=True)
	tipo = models.ForeignKey(Tipo , related_name = 'fk_Servidumbre_predio_Tipo' , on_delete=models.PROTECT , null = True , blank = True)#related_name="f_MODEL_APP"
	grupo_documento = models.ForeignKey(Servidumbre_grupo_documento , related_name = 'fk_Servidumbre_grupo_documento' , on_delete=models.PROTECT)

	class Meta:
		db_table = 'servidumbre_predio'
		unique_together = [
			["persona","nombre_direccion"],
		]
	def __unicode__(self):
		return  self.nombre_direccion	

class Servidumbre_predio_documento(models.Model):
	predio =  models.ForeignKey(Servidumbre_predio , related_name = 'f_Servidumbre_predio' , on_delete=models.PROTECT)
	documento = models.ForeignKey(Servidumbre_documento , related_name = 'f_Servidumbre_documento' , on_delete=models.PROTECT)
	nombre = models.CharField(max_length = 60, blank = False)	
	#archivo = models.FileField(upload_to='servidumbre', null = True)
	archivo = models.FileField(upload_to=RandomFileName('servidumbre','ser'), null=True)

	class Meta:
		db_table = 'servidumbre_predio_documento'
		# unique_together = [
		# 	["predio.id","documento"],
		# ]
	def __unicode__(self):
		return self.documento.nombre


class Servidumbre_predio_georeferencia(models.Model):
	predio = models.ForeignKey(Servidumbre_predio , related_name = 'f_Servidumbre_georeferencia_predio' , on_delete=models.PROTECT)
	orden = models.IntegerField(blank = True, null=True)
	longitud = models.CharField(max_length=50)
	latitud = models.CharField(max_length=50)
	class Meta:
		db_table = 'servidumbre_predio_georefencia'
		permissions = (("can_see_predio_georefencia","can_see_predio_georefencia"),)
		unique_together = [
			["predio","orden"],
		]
	def __unicode__(self):
		return self.predio.nombre_direccion + ' ['+self.longitud+','+self.latitud+']'
	# def save(self, *args, **kwargs):		
	# 	if not self.orden:
	# 		qset = (Q(predio__id=int(self.predio.id))&(~Q(orden=None)))
	# 		geocoordenadas = Servidumbre_predio_geocoordenada.objects.filter(qset).order_by('orden')
	# 		orden_actual = int(geocoordenadas.last().orden())+1
	# 		self.orden = orden_actual			
	# 	super(Servidumbre_predio_geocoordenada, self).save(*args, **kwargs)

# Create your models here.
