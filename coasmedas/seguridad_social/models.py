from django.db import models
from empresa.models import Empresa
from usuario.models import Persona
from estado.models import Estado
from tipo.models import Tipo
from .enum import EnumEstadoPlanilla
from datetime import *
from django.db.models import Count
from coasmedas.functions import functions, RandomFileName
# Create your models here.

class BaseModel(models.Model):
	nombre = models.CharField(max_length=50)

	class Meta:
		abstract = True
	 	#permission = ('puede_ver','puede_ver')

	def __unicode__(self):
		return self.nombre


class AEscolaridad(BaseModel):

	class Meta:		
		db_table = 'seguridad_social_escolaridad'	
		permissions = (
			("can_see_escolaridad","can see escolaridad"),
		) 	


class AMatricula(BaseModel):

	class Meta:		
		db_table = 'seguridad_social_matricula'
		permissions = (
			("can_see_matricula","can see matricula"),
		) 

class Cargo(BaseModel):
	soporte_tsa=models.BooleanField(default=False)
	soporte_matricula=models.BooleanField(default=False)
	hoja_de_vida=models.BooleanField(default=False)
	class Meta:		
		db_table = 'seguridad_social_cargo'
		permissions = (
			("can_see_cargo_ss","can see cargo ss"),
		) 

class Empleado(models.Model):
	persona = models.ForeignKey(Persona, on_delete=models.PROTECT)
	fecha_nacimiento = models.DateField(null=True)
	escolaridad = models.ForeignKey(AEscolaridad, blank=True, null=True,related_name="escolaridad_empleado",on_delete=models.PROTECT)
	contratista = models.ForeignKey(Empresa, blank=True, null=True, related_name='empleado_empresa_contratista', on_delete=models.PROTECT)
	empresa = models.ForeignKey(Empresa, related_name='empleado_empresa_creadora', null=True, on_delete=models.PROTECT)	
	fecha_tsa = models.DateField(blank=True, null=True)
	soporte_tsa = models.FileField(upload_to=RandomFileName('seguridad_social/soporte_tsa','ss'),blank=True, null=True)
	# soporte_tsa = models.FileField(upload_to='seguridad_social/soporte_tsa',blank=True, null=True)
	matricula = models.ForeignKey(AMatricula, blank=True, null=True,related_name="matricula_empleado",on_delete=models.PROTECT)
	tipo_matricula = models.ForeignKey(Tipo,blank=True, null=True, default=None,related_name="tipo_matricula_empleado",on_delete=models.PROTECT)
	soporte_matricula = models.FileField(upload_to=RandomFileName('seguridad_social/soporte_matricula','ss'),blank=True, null=True)
	# soporte_matricula = models.FileField(upload_to='seguridad_social/soporte_matricula',blank=True, null=True)
	estado = models.ForeignKey(Estado, blank=True, null=True,related_name="estado_empleado",on_delete=models.PROTECT)
	cargo = models.ForeignKey(Cargo, blank=True, null=True,related_name="cargo_empleado",on_delete=models.PROTECT)
	hoja_de_vida = models.FileField(upload_to=RandomFileName('seguridad_social/hoja_de_vida','ss'),blank=True, null=True)
	# hoja_de_vida = models.FileField(upload_to='seguridad_social/hoja_de_vida',blank=True, null=True)
	apto = models.BooleanField(default=False)
	observacion = models.TextField(blank=True, null=True)
	foto = models.ImageField(upload_to=RandomFileName('seguridad_social/empleado','ss'),blank=True, null=True)
	# foto = models.ImageField(upload_to='seguridad_social/empleado',blank=True, null=True)
	fecha_ingreso = models.DateField(blank=True, null=True)
	tiene_licencia = models.BooleanField(default=False)
	vencimiento_licencia = models.DateField(null=True, blank=True)
	soporte_licencia = models.FileField(upload_to=RandomFileName('seguridad_social/licencia','ss'),blank=True, null=True)
	# soporte_licencia = models.FileField(upload_to='seguridad_social/licencia',blank=True, null=True)


	class Meta:		
		db_table = 'seguridad_social_empleado'
		#unique_together = (("persona", "contratista"),)
		ordering=['id']
		permissions = (
			("can_see_empleado","can see empleado"),
		) 

	def __unicode__(self):
		return self.persona.nombres	+ ' ' + self.persona.apellidos

	@property	
	def foto_publica(self):
		if self.foto:			
			return functions.crearRutaTemporalArchivoS3(str(self.foto))
		else:
			return None		

class Novedad(models.Model):
	fecha = models.DateField(null=True)
	empleado = models.ForeignKey(Empleado,null=True,related_name="empleado_novedad",on_delete=models.PROTECT)
	estado = models.ForeignKey(Estado,null=True,related_name="estado_novedad",on_delete=models.PROTECT)
	descripcion = models.CharField(max_length=300, blank=True, null=True)
	fecha_registro = models.DateTimeField(auto_now_add=True, blank=True)

	class Meta:		
		db_table = 'seguridad_social_novedad'
		permissions = (
			("can_see_novedad","can see novedad"),
		) 


class Planilla(models.Model):
	contratista = models.ForeignKey(Empresa, related_name='planilla_empresa_contratista', on_delete=models.PROTECT)
	ano = models.IntegerField()
	mes =  models.IntegerField()
	fecha_pago =  models.DateField(null=True, blank=True)
	soporte =  models.FileField(upload_to=RandomFileName('seguridad_social/planillas','ss'),blank=True, null=True)
	# soporte =  models.FileField(upload_to='seguridad_social/planillas',blank=True, null=True)
	fecha_limite =  models.DateField(null=True, blank=True)
	empresa =  models.ForeignKey(Empresa, null=True ,related_name="empresa_planilla",on_delete=models.PROTECT)
	
	def estado(self):
		nombre_estado=''
		if self.fecha_pago is None:

			date1 = date.today()					
			date2 = self.fecha_limite				
			datediff= date2	- date1
			dias=datediff.days
			
			# nombre_estado= EnumEstadoPlanilla.AlDia if dias>0 else EnumEstadoPlanilla.Vencida
			if dias >= 6:
				nombre_estado= EnumEstadoPlanilla.AlDia
			elif dias <= 0:
				nombre_estado= EnumEstadoPlanilla.Vencida
			elif dias < 6 and dias > 0:
				nombre_estado= EnumEstadoPlanilla.PorVencer	
		elif self.fecha_pago is not None:
			date1 =self.fecha_limite
			date2 =self.fecha_pago
			datediff = date1 - date2
			dias=datediff.days
			nombre_estado= EnumEstadoPlanilla.AlDia if dias > 0 else EnumEstadoPlanilla.PagadoFueraFecha
		return nombre_estado

	def estado_planilla_empleado(self):
		cantidad1=PlanillaEmpleado.objects.filter(planilla__id=self.id, tiene_pago=True).count()
		cantidad2=PlanillaEmpleado.objects.filter(planilla__id=self.id).count()
				
		#completa
		if cantidad2>0 and cantidad1==cantidad2:
			return 1

		#no ha reportado el pago de los empleados	
		if cantidad1==0 and cantidad2 > 0 or cantidad2==0:
			return 2	

		#El pago de los empleados es incompleto		
		if cantidad1!=cantidad2:
			return 3	

		#return 2		
	def dias_vencidos(self):
		if self.fecha_pago is None:

			date1 = date.today()					
			date2 = self.fecha_limite				
			datediff= date1 - date2				
			dias=datediff.days
			return dias
		elif self.fecha_pago is not None:
			date1 =self.fecha_limite
			date2 =self.fecha_pago
			datediff = date1 - date2
			dias=datediff.days
			return dias
		
	class Meta:		
		db_table = 'seguridad_social_planilla'
		#unique_together = (("contratista", "ano", "mes"),)
		ordering=['-ano', '-mes']
		permissions = (
			("can_see_planilla","can see planilla"),
		) 


class PlanillaEmpleado(models.Model):
	planilla=models.ForeignKey(Planilla, related_name='planilla_empleado_planilla', on_delete=models.PROTECT)
	empleado=models.ForeignKey(Empleado, related_name='planilla_empleado_empleado', on_delete=models.PROTECT)
	tiene_pago=models.BooleanField(default=False)

	class Meta:
		db_table = 'seguridad_social_planilla_empleado'
		#unique_together = (("contratista", "ano", "mes"),)
		permissions = (
			("can_see_planilla_empleado","can see planilla empleado"),
		) 
			
class EmpresaPermiso(models.Model):
	empresa_acceso = models.ForeignKey(Empresa, related_name="empresa_permiso_empresa_acceso",on_delete=models.PROTECT)
	empresa = models.ForeignKey(Empresa, related_name="empresa_permiso_empresa",on_delete=models.PROTECT)

	class Meta:		
		db_table = 'seguridad_social_empresa_permiso'
		#unique_together = (("empresa_acceso", "empresa"),)
		permissions = (
			("can_see_empresa_permiso","can see empresa permiso"),
		) 

	def __unicode__(self):
		return self.nombre	

class Requerimientos(BaseModel):
	"""docstring for RequerimientosEmpleados"""	
	class Meta:		
		db_table = 'seguridad_social_requerimiento'
		permissions = (
			("can_see_requermientos","can see requerimientos"),
		) 
	def __unicode__(self):
		return self.nombre

class RequerimientosValor(BaseModel):
	"""docstring for RequerimientosEmpleados"""
	class Meta:		
		db_table = 'seguridad_social_requerimiento_valor'
		permissions = (
			("can_see_requermientos_valor","can see requermientos valor"),
		) 

	def __unicode__(self):
		return self.nombre															

class ZRequerimientosEmpleados(models.Model):
	"""docstring for RequerimientosEmpleados"""
	requerimiento=models.ForeignKey(Requerimientos, null=True,related_name="requeriemientos_requerimientos_empleado",on_delete=models.PROTECT)
	empleado=models.ForeignKey(Empleado, null=True,related_name="requerimientos_empleados_empleado",on_delete=models.PROTECT)
	requerimiento_valor=models.ForeignKey(RequerimientosValor, null=True, on_delete=models.PROTECT)
	class Meta:		
		db_table = 'seguridad_social_requerimientos_empleados'	
		permissions = (
			("can_see_requermientos_empleados","can see requermientos empleados"),
		) 													

class CorreoContratista(models.Model):
	"""docstring for ClassName"""
	contratista = models.ForeignKey(Empresa, null=True, related_name='empleado_correo_contratista', on_delete=models.PROTECT)
	correo = models.CharField(max_length=100)	
	class Meta:		
		db_table = 'seguridad_social_correo_contratista'	
		unique_together = (("contratista", "correo"),)
		permissions = (
			("can_see_correo_contratista","can see correo contratista"),
		) 						