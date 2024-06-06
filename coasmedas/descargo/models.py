from django.db import models
from django.db.models import Q
from parametrizacion.models import BaseModel,Departamento
from contrato.models import Contrato
from tipo.models import Tipo
from estado.models import Estado
from empresa.models import Empresa
from seguridad_social.models import Empleado
from proyecto.models import Proyecto
from smart_selects.db_fields import ChainedForeignKey
from coasmedas.functions import functions, RandomFileName
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _



# Create your models here.

class Correo_descargo(BaseModel):
	apellido = models.CharField(max_length=50)
	correo = models.CharField(max_length=300)
	tipo = models.ForeignKey(Tipo,on_delete=models.PROTECT,related_name='tipo_correoDescargo')
	contratista = models.ForeignKey(Empresa,null=True,on_delete=models.PROTECT,related_name='correoDescargo_contratista')
	
	class Meta:
		permissions = (("can_see_Correo_descargo","can_see_Correo_descargo"),) 


class AIdInternoDescargo(models.Model):
	convenio = models.ForeignKey(Contrato,on_delete=models.PROTECT,related_name='contrato_idinternodescargo')
	departamento = models.ForeignKey(Departamento,on_delete=models.PROTECT,related_name='idinternodescargo_departamento')
	numero = models.IntegerField()

	class Meta:
		db_table = "descargo_id_interno_descargo"
		permissions = (("can_see_IdInternoDescargo","can_see_IdInternoDescargo"),) 

	#def __unicode__(self):
	#	return self.id


class ATrabajo(BaseModel):

	class Meta:
		db_table = "descargo_trabajo"
		permissions = (("can_see_Trabajo","can_see_Trabajo"),)

class AManiobra(BaseModel):

	class Meta:
		db_table = "descargo_maniobra"
		permissions = (("can_see_Maniobra","can_see_Maniobra"),)

class ABMotivoSgi(BaseModel):
	estado_descargo = models.ForeignKey(Estado,on_delete=models.PROTECT,related_name='estadoDescargo_motivosgi')

	class Meta:
		db_table = "descargo_motivo_sgi"
		permissions = (("can_see_MotivoSGI","can_see_MotivoSGI"),)

class AMotivoInterventor(BaseModel):
	motivo_sgi=models.ForeignKey(ABMotivoSgi,on_delete=models.PROTECT,related_name='motivosgi_motivointerventor')

	class Meta:
		db_table = "descargo_motivo_interventor"
		permissions = (("can_see_Motivointerventor","can_see_Motivointerventor"),)

class Descargo(models.Model):
	id_interno = models.CharField(max_length=100,null=True,blank=True)
	numero = models.CharField(max_length=30,null=True)
	estado = models.ForeignKey(Estado,on_delete=models.PROTECT,related_name='Descargo_estado')
	proyecto = models.ForeignKey(Proyecto,on_delete=models.PROTECT,related_name='Descargo_proyecto')
	barrio = models.CharField(max_length=1000)
	direccion = models.CharField(max_length=1000)
	bdi = models.BooleanField(default=0)
	perdida_mercado = models.BooleanField(default=0)
	area_afectada = models.CharField(max_length=1000)
	elemento_intervenir = models.CharField(max_length=1000)
	maniobra = models.ForeignKey(AManiobra,on_delete=models.PROTECT,related_name='maniobra_descargo')
	trabajo = models.ManyToManyField(ATrabajo)
	fecha = models.DateField()
	hora_inicio = models.TimeField()
	hora_fin = models.TimeField()
	jefe_trabajo = models.ForeignKey(Empleado,related_name='empleado_jefe',on_delete=models.PROTECT)
	agente_descargo = models.ForeignKey(Empleado,related_name='empleado_agente',on_delete=models.PROTECT)
	observacion=models.CharField(max_length=4000,null=True)
	observacion_interventor=models.CharField(max_length=4000,null=True)
	correo_bdi=models.FileField(upload_to=RandomFileName('descargo/correo_bdi','cbdi'),null=True,blank=True)
	soporte_ops=models.FileField(upload_to=RandomFileName('descargo/soportes_ops','sops'),null=True,blank=True)
	soporte_protocolo=models.FileField(upload_to=RandomFileName('descargo/soporte_protocolo','spt'),null=True,blank=True)
	lista_chequeo=models.FileField(upload_to=RandomFileName('descargo/lista_chequeo','lchk'),null=True,blank=True)
	numero_requerimiento = models.CharField(max_length=50,null=True)
	contratista = models.ForeignKey(Empresa,on_delete=models.PROTECT,related_name='Empresa_Descargo')
	motivo_sgi = ChainedForeignKey(ABMotivoSgi,chained_field="estado", chained_model_field="estado_descargo", null=True,on_delete=models.PROTECT,related_name='motivosgi_Descargo')
	motivo_interventor = ChainedForeignKey(AMotivoInterventor,chained_field="motivo_sgi", chained_model_field="motivo_sgi",null=True,on_delete=models.PROTECT,related_name='motivointerventor_Descargo')

	class Meta:
		permissions = (("can_see_Descargo","can_see_Descargo"),)

	def validate_unique(self, exclude=None):
		 # qs = Descargo.objects.filter(numero=self.numero).exists()
		if self.id is not None:
			if Descargo.objects.filter(numero=self.numero).exclude(pk=self.id).exists() and Descargo.objects.filter(numero=self.numero).exclude(numero=None).exists():
				raise ValidationError(_('numero no debe ser igual'),code='unico')

	def consecutive_id(self):
		
		if AIdInternoDescargo.objects.filter(convenio=self.proyecto.mcontrato.id,departamento=self.proyecto.municipio.departamento.id).exists():
			interno=AIdInternoDescargo.objects.get(convenio=self.proyecto.mcontrato.id,departamento=self.proyecto.municipio.departamento.id)
			idinterno2=AIdInternoDescargo.objects.get(pk=interno.id)
			idinterno2.numero=interno.numero+1			
			idinterno2.save()
			nombre=str(idinterno2.convenio.id)+str(idinterno2.departamento.iniciales)+'-'+str(idinterno2.numero)
		else:
			idinterno2=AIdInternoDescargo()
			idinterno2.convenio=self.proyecto.mcontrato
			idinterno2.departamento=self.proyecto.municipio.departamento
			idinterno2.numero=1
			idinterno2.save()
			nombre=str(idinterno2.convenio.id)+str(idinterno2.departamento.iniciales)+'-'+str(idinterno2.numero)
		return nombre

	def unavaliable_boss(self):
		qs=Descargo.objects.filter(
			(Q(jefe_trabajo_id=self.jefe_trabajo,fecha=self.fecha,hora_inicio__range=(self.hora_inicio,self.hora_fin)))|
			(Q(jefe_trabajo_id=self.jefe_trabajo,fecha=self.fecha,hora_fin__range=(self.hora_inicio,self.hora_fin)))|

			# (Q(jefe_trabajo_id=self.jefe_trabajo,fecha=self.fecha,self.hora_inicio__range=(hora_inicio,hora_fin)))|
			# (Q(jefe_trabajo_id=self.jefe_trabajo,fecha=self.fecha,self.hora_fin__range=(hora_inicio,hora_fin)))|

			(Q(jefe_trabajo_id=self.jefe_trabajo,fecha=self.fecha,hora_inicio__lte=self.hora_inicio,hora_inicio__gte=self.hora_fin,
																hora_fin__gte=self.hora_inicio,hora_fin__lte=self.hora_fin))
			# (Q(jefe_trabajo_id=self.jefe_trabajo,fecha=self.fecha,hora_inicio__lte=self.hora_inicio,hora_inicio__gte=self.hora_fin,hora_fin__lte=self.hora_inicio,hora_fin__gte=self.hora_fin))
			).exclude(pk=self.id)
		if qs.exists():
			raise ValidationError(_('Jefe ocupado'),code='busyboss')

	def unavaliable_agent(self):
		qs=Descargo.objects.filter((Q(agente_descargo_id=self.agente_descargo,fecha=self.fecha,hora_inicio__range=(self.hora_inicio,self.hora_fin)))|
					(Q(agente_descargo_id=self.agente_descargo,fecha=self.fecha,hora_fin__range=(self.hora_inicio,self.hora_fin)))|
					(Q(agente_descargo_id=self.agente_descargo,fecha=self.fecha,hora_inicio__lte=self.hora_inicio,hora_inicio__gte=self.hora_fin,hora_fin__lte=self.hora_inicio,hora_fin__gte=self.hora_fin))).exclude(pk=self.id)
		if qs.exists():
			raise ValidationError(_('agente ocupado'),code='busyagent')


	def save(self, *args, **kwargs):

		self.validate_unique()

		self.unavaliable_boss()

		self.unavaliable_agent()

		if self.id is None:

			self.id_interno=self.consecutive_id()

		super(Descargo, self).save(*args, **kwargs)		



class FotoDescargo(models.Model):
	ruta = models.ImageField(upload_to=RandomFileName('descargo/fotos_descargo','dft'),null=True,blank=True)
	regla = models.IntegerField()
	descargo = models.ForeignKey(Descargo,on_delete=models.PROTECT,related_name='fotodescargo_descargo')

	class Meta:
		permissions = (("can_see_FotoDescargo","can_see_FotoDescargo"),)

