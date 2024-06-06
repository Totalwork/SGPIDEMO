from django.db import models
from contrato.models import Contrato
from proyecto.models import Proyecto
from tipo.models import Tipo
from estado.models import Estado
from usuario.models import Usuario
from django.db.models import Max
from coasmedas.functions import functions, RandomFileName



class ASolicita(models.Model):
	nombre = models.CharField(max_length=100)

	class Meta:
		db_table = "control_cambios_solicita"
		permissions = (("can_see_solicita","can_see_solicita"),)
		verbose_name='solicita'

	def __unicode__(self):
		return self.nombre	 


class BUnidadConstructiva(models.Model):
	contrato=models.ForeignKey(Contrato,related_name="UnidadConstructiva_contrato",on_delete=models.PROTECT)
	proyecto=models.ForeignKey(Proyecto,related_name="UnidadConstructiva_proyecto",null=True,blank=True,on_delete=models.PROTECT)
	codigo = models.CharField(max_length=50,null=True,blank=True)
	descripcion = models.TextField(null=True,blank=True)
	valor_mano_obra = models.FloatField()
	valor_materiales = models.FloatField()
	#tipo_registro = models.BooleanField(default=False)
	
	class Meta:
		db_table = "control_cambios_unidad_constructiva"
		permissions = (("can_see_UnidadConstructiva","can_see_UnidadConstructiva"),)
		verbose_name='Unidades Constructivas'

	def __unicode__(self):
		return self.codigo	 


class CCambio(models.Model):
	proyecto=models.ForeignKey(Proyecto,related_name="cambio_proyecto",on_delete=models.PROTECT)
	tipo=models.ForeignKey(Tipo,related_name="cambio_tipo",null=True,blank=True,on_delete=models.PROTECT)
	usuario=models.ForeignKey(Usuario,related_name="cambio_usuario",on_delete=models.PROTECT)
	usuario_revisa=models.ForeignKey(Usuario,related_name="cambio_usuarioRevisa",null=True,blank=True,on_delete=models.PROTECT)
	solicita=models.ForeignKey(ASolicita,related_name="cambio_solicita",on_delete=models.PROTECT)
	fecha = models.DateField(null=True,blank=True)
	numero_cambio = models.IntegerField(null=True,blank=True)
	motivo = models.TextField(null=True,blank=True)
	solicitud_enviada = models.BooleanField(default=False)

	def cantidad_cambio(self):
		cantidad=CCambio.objects.filter(proyecto_id=self.proyecto_id)
		return cantidad.count() if cantidad is not None else 0
		# return cantidad

	def maximo_id_cambio(self):
		maximo_id=CCambio.objects.filter(proyecto_id=self.proyecto_id).aggregate(Max('id'))
		return maximo_id

	def estado_cambio_proyecto(self):
		estado=FCambioProyecto.objects.filter(cambio_id=self.id,estado_id=97).count()

		if estado and int(estado)>0:

			nombre_estado='Pendiente'

		else:

			nombre_estado='Completado'

		return nombre_estado
			

	class Meta:
		db_table = "control_cambios_cambio"
		permissions = (("can_see_cambio","can_see_cambio"),)
		verbose_name='Cambio'

	def __unicode__(self):
		return str(self.numero_cambio)	 



class DMaterial(models.Model):
	codigo = models.CharField(max_length=50,null=True,blank=True)
	descripcion = models.TextField(null=True,blank=True)
	unidad = models.CharField(max_length=50,null=True,blank=True)
	
	class Meta:
		db_table = "control_cambios_material"
		permissions = (("can_see_material","can_see_material"),)
		verbose_name='Material'

	def __unicode__(self):
		return str(self.codigo)	   


class EUUCCMaterial(models.Model):
	uucc=models.ForeignKey(BUnidadConstructiva,related_name="UnidadConstructiva_UnidadConstructiva",on_delete=models.PROTECT)
	material = models.ForeignKey(DMaterial,related_name="UnidadConstructiva_material",on_delete=models.PROTECT)
	cantidad = models.FloatField()
	
	class Meta:
		db_table = "control_cambios_uucc_material"
		permissions = (("can_see_UUCCMateriales","can_see_UUCCMateriales"),)
		verbose_name='UUCC Materiales'



class FCambioProyecto(models.Model):
	uucc=models.ForeignKey(BUnidadConstructiva,related_name="CambioProyecto_uucc",on_delete=models.PROTECT)
	cambio = models.ForeignKey(CCambio,related_name="CambioProyecto_cambio",on_delete=models.PROTECT)
	cantidad = models.FloatField()
	estado 	= models.ForeignKey(Estado, on_delete=models.PROTECT,null=True,blank=True)
	comentario = models.TextField(null=True,blank=True)
	
	class Meta:
		db_table = "control_cambios_cambio_proyecto"
		permissions = (("can_see_CambioProyecto","can_see_CambioProyecto"),)
		verbose_name='Cambio proyecto'



class GSoporte(models.Model):
	nombre = models.CharField(max_length=200)
	#ruta=models.FileField(upload_to='control_cambios/ruta',blank=True, null=True)
	ruta=models.FileField(upload_to=RandomFileName('control_cambios/Soporte_ruta','plz'),blank=True, null=True)
	cambio = models.ForeignKey(CCambio,related_name="Soporte_cambio",on_delete=models.PROTECT)
	
	class Meta:
		db_table = "control_cambios_soporte"
		permissions = (("can_see_Soporte","can_see_Soporte"),)
		verbose_name='Soporte'