from django.db import models
from usuario.models import Usuario, Persona
from contrato.models import Contrato
from proyecto.models import Proyecto
from estado.models import Estado
from empresa.models import Empresa
from tipo.models import Tipo

from sinin4.functions import functions, RandomFileName
# Create your models here.
class Consecutivo(models.Model):
	ano = models.IntegerField(blank = False, null=False)
	empresa = models.ForeignKey(Empresa,related_name="fk_empresa_consecutivo",on_delete=models.PROTECT, blank = False, null = False)
	consecutivo = models.IntegerField(blank = False, null=False)

	class Meta:
		db_table = 'acta_consecutivo'	
		unique_together = [
			["empresa","ano"],
		]
		permissions = (("can_see_consecutivo","can_see_consecutivo"),)	

	def __unicode__(self):
		return  str(self.empresa.id)+str(self.consecutivo)

class Acta(models.Model):
	consecutivo = models.IntegerField(blank = False, null = False)
	tema_principal = models.CharField(max_length = 2000, blank = False, null = False)
	controlador_actual = models.ForeignKey(Usuario,related_name="fk_controlador_acta",on_delete=models.PROTECT, blank = False, null = False)
	usuario_organizador = models.ForeignKey(Usuario,related_name="fk_organizador_acta",on_delete=models.PROTECT, blank = False, null = False)
	#soporte = models.FileField(upload_to='acta_reunion/acta', null = True, blank=True)
	soporte = models.FileField(upload_to=RandomFileName('acta_reunion/acta','act'), blank=True, null=True)
	acta_previa = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)
	conclusiones = models.CharField(max_length = 2000, blank = True, null = True)
	contrato = models.ManyToManyField(Contrato, related_name='fk_contrato_acta' ,  blank=True)
	proyecto = models.ManyToManyField(Proyecto, related_name='fk_proyecto_acta' , blank=True)
	#estado = models.ForeignKey(Estado , related_name = 'fk_estado_acta' , on_delete=models.PROTECT)
	estado = models.ForeignKey(Estado , related_name = 'fk_estado_acta' , on_delete=models.PROTECT, default = 155, blank = True, null = True)
	fecha = models.DateField(blank = False, null = False)	
	tiene_contrato = models.BooleanField(default= True, blank = False, null = False)
	tiene_proyecto = models.BooleanField(default= True, blank = False, null = False)
	tiene_conclusiones = models.BooleanField(default= True, blank = False, null = False)
	tiene_compromisos = models.BooleanField(default= True, blank = False, null = False)

	class Meta:
		db_table = 'acta_acta'		
		permissions = (("can_see_acta","can_see_acta"),)	

	def __unicode__(self):
		return  str(self.consecutivo)

class Tema(models.Model):	
	acta = models.ForeignKey(Acta,related_name="fk_acta_tema",on_delete=models.PROTECT, blank = False, null = False)
	tema = models.CharField(max_length = 2000, blank = False, null = False)

	class Meta:
		db_table = 'acta_tema'
		permissions = (("can_see_tema","can_see_tema"),)	

	def __unicode__(self):
		return  self.tema

class Acta_historial(models.Model):
	acta = models.ForeignKey(Acta,related_name="fk_acta_acta_historial",on_delete=models.PROTECT, blank = False, null = False)
	fecha = models.DateField(blank = False, null = False)
	tipo_operacion = models.ForeignKey(Tipo,related_name="fk_tipo_acta_historial",on_delete=models.PROTECT, blank = True, null=True)
	motivo = models.CharField(max_length = 2000, blank = True, null=True)
	controlador = models.ForeignKey(Usuario,related_name="fk_controlador_acta_historial",on_delete=models.PROTECT, blank = False, null = False)

	class Meta:
		db_table = 'acta_acta_historial'
		permissions = (("can_see_acta_historial","can_see_acta_historial"),)	

	def __unicode__(self):
		return  str(self.acta.consecutivo) +' | '+self.tipo_operacion.nombre


class Participante_externo(models.Model):
	acta = models.ForeignKey(Acta,related_name="fk_acta_participante_externo",on_delete=models.PROTECT, blank = False, null = False)
	persona = models.ForeignKey(Persona, related_name='fk_persona_participante_externo', on_delete=models.PROTECT, blank = False, null = False)
	asistio = models.BooleanField(default= False, blank = False, null=False)
	class Meta:
		db_table = 'acta_participante_externo'
		permissions = (("can_see_participante_externo","can_see_participante_externo"),)	

	def __unicode__(self):
		return  self.persona.nombres + ' ' + self.persona.apellidos


class Participante_interno(models.Model):
	acta = models.ForeignKey(Acta,related_name="fk_acta_participante_interno",on_delete=models.PROTECT, blank = False, null = False)
	usuario = models.ForeignKey(Usuario,related_name="fk_usuario_participante_interno",on_delete=models.PROTECT, blank = False, null = False)
	asistio = models.BooleanField(default= False, blank = False, null=False)
	class Meta:
		db_table = 'acta_participante_interno'
		permissions = (("can_see_participante_interno","can_see_participante_interno"),)	

	def __unicode__(self):
		return  self.usuario.persona.nombres + ' ' + self.usuario.persona.apellidos

class Compromiso(models.Model):
	acta = models.ForeignKey(Acta,related_name="fk_acta_acta_compromiso",on_delete=models.PROTECT, blank = False, null=False)
	supervisor = models.ForeignKey(Usuario,related_name="fk_supervisor_compromiso",on_delete=models.PROTECT, blank = False, null=False)
	responsable_interno = models.BooleanField(default= False, blank = False, null=False)
	participante_responsable = models.ForeignKey(Participante_externo,related_name="fk_participante_responsable_compromiso",on_delete=models.PROTECT, blank = True, null=True)
	usuario_responsable = models.ForeignKey(Usuario,related_name="fk_usuario_responsable_compromiso",on_delete=models.PROTECT,blank = True, null=True)
	fecha_compromiso = models.DateField(blank = False, null = False)
	fecha_proximidad = models.DateField(blank = False, null = False)
	descripcion = models.CharField(max_length = 2000, blank = False, null = False)
	#estado = models.ForeignKey(Estado , related_name = 'fk_estado_compromiso' , on_delete=models.PROTECT)
	estado = models.ForeignKey(Estado , related_name = 'fk_estado_compromiso' , on_delete=models.PROTECT, default=159, blank = False, null = False)
	requiere_soporte = models.BooleanField(default= False, blank = False, null=False)
	#soporte = models.FileField(upload_to='acta_reunion/compromiso', null = True, blank=True)
	soporte = models.FileField(upload_to=RandomFileName('acta_reunion/compromiso','com'), null=True, blank=True) 
	notificar_organizador = models.BooleanField(default= True, blank = False, null = False)
	notificar_controlador = models.BooleanField(default= True, blank = False, null = False)

	class Meta:
		db_table = 'acta_compromiso'
		permissions = (("can_see_acta_compromiso","can_see_acta_compromiso"),)	

	def __unicode__(self):
		return  str(self.acta.consecutivo) +' | '+self.descripcion

class Compromiso_historial(models.Model):
	compromiso = models.ForeignKey(Compromiso,related_name="fk_compromiso_compromiso_historial",on_delete=models.PROTECT, blank = False, null = False)
	fecha = models.DateField(blank = False, null = False)
	tipo_operacion = models.ForeignKey(Tipo,related_name="fk_tipo_compromiso_historial",on_delete=models.PROTECT, blank = True, null=True)
	motivo = models.CharField(max_length = 2000, blank = True, null=True)
	participante_externo = models.ForeignKey(Participante_externo,related_name="fk_participante_externo_compromiso_historial",on_delete=models.PROTECT,  blank = True, null=True)
	participante_interno = models.ForeignKey(Participante_interno,related_name="fk_participante_interno_compromiso_historial",on_delete=models.PROTECT,  blank = True, null=True)

	class Meta:
			db_table = 'acta_compromiso_historial'
			permissions = (("can_see_compromiso_historial","can_see_compromiso_historial"),)	

	def __unicode__(self):
		return  self.compromiso.descripcion +' | '+self.tipo_operacion.nombre