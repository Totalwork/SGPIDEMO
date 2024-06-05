from django.db import models

from tipo.models import Tipo
from estado.models import Estado
# from .enumeration import tipoCesion

from contrato.models import Contrato

from sinin4.functions import functions, RandomFileName

# Create your models here.
class BaseModel(models.Model):
	nombre = models.CharField(max_length=1000)

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.nombre

class ASolicitud(models.Model):
	tipo = models.ForeignKey(Tipo, on_delete=models.PROTECT)
	estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
	contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT)
	fecha = models.DateField(blank=True, null=True)
	observacion = models.CharField(max_length=4000, blank=True, null=True)
	carta_aceptacion = models.FileField(upload_to = RandomFileName('solicitud/solicitud','slt_crt'), blank=True, null=True)
	# carta_aceptacion = models.FileField(upload_to = 'solicitud/solicitud', blank=True, null=True)
	soporte = models.FileField(upload_to = RandomFileName('solicitud/solicitud','slt_spt'), blank=True, null=True)
	# soporte = models.FileField(upload_to = 'solicitud/solicitud', blank=True, null=True)

	class Meta:
		db_table = 'solicitud'
		permissions = (
			("can_see_solicitud","can see solicitud"),
		)

	def archivo(self):
		return """<a href="%s" >Documento</a>"""%self.soporte.url
	archivo.allow_tags = True

	def __unicode__(self):
		return self.tipo.nombre+ ' - '+ self.contrato.nombre

# Juridico
class BRequisitoJuridico(BaseModel):

	class Meta:
		db_table = 'solicitud_requisito_juridico'

class CFavorabilidadJuridica(models.Model):
	solicitud = models.ForeignKey(ASolicitud, on_delete=models.PROTECT)
	observacion = models.CharField(max_length=4000, blank=True, null=True)
	soporte = models.FileField(upload_to = RandomFileName('solicitud/favorabilidad_juridica','fvd_jrc'), blank=True, null=True)
	# soporte = models.FileField(upload_to = 'solicitud/favorabilidad_juridica', blank=True, null=True)

	class Meta:
		db_table = 'solicitud_favorabilidad_juridica'

	def archivo(self):
		return """<a href="%s" >Documento</a>"""%self.soporte.url
	archivo.allow_tags = True

	def __unicode__(self):
		return self.solicitud.tipo.nombre+ ' - '+ self.solicitud.contrato.nombre

class DFavorabilidadJuridicaRequisito(models.Model):
	requisito = models.ForeignKey(BRequisitoJuridico, related_name='fk_favorabilidad_juridica_requisito', on_delete=models.PROTECT)
	favorabilidad = models.ForeignKey(CFavorabilidadJuridica, on_delete=models.PROTECT)
	estado = models.BooleanField(default= False)

	class Meta:
		db_table = 'solicitud_favorabilidad_juridica_requisito'
# Fin de Juridico

# Compras
class BRequisitoCompras(BaseModel):

	class Meta:
		db_table = 'solicitud_requisito_compras'

class CFavorabilidadCompras(models.Model):
	solicitud = models.ForeignKey(ASolicitud, on_delete=models.PROTECT)
	observacion = models.CharField(max_length=4000, blank=True, null=True)
	soporte = models.FileField(upload_to = RandomFileName('solicitud/favorabilidad_compras','fvd_cmp'), blank=True, null=True)
	# soporte = models.FileField(upload_to = 'solicitud/favorabilidad_compras', blank=True, null=True)

	class Meta:
		db_table = 'solicitud_favorabilidad_compras'

	def archivo(self):
		return """<a href="%s" >Documento</a>"""%self.soporte.url
	archivo.allow_tags = True

	def __unicode__(self):
		return self.solicitud.tipo.nombre+ ' - '+ self.solicitud.contrato.nombre

class DFavorabilidadComprasRequisito(models.Model):
	requisito = models.ForeignKey(BRequisitoCompras, on_delete=models.PROTECT)
	favorabilidad = models.ForeignKey(CFavorabilidadCompras, on_delete=models.PROTECT)
	estado = models.BooleanField(default= False)

	class Meta:
		db_table = 'solicitud_favorabilidad_compras_requisito'
# Fin de Compras

# Tecnica
class BRequisitoTecnico(BaseModel):

	class Meta:
		db_table = 'solicitud_requisito_tecnico'

class CFavorabilidadTecnica(models.Model):
	solicitud = models.ForeignKey(ASolicitud, on_delete=models.PROTECT)
	observacion = models.CharField(max_length=4000, blank=True, null=True)
	soporte = models.FileField(upload_to = RandomFileName('solicitud/favorabilidad_tecnica','fvd_tcn'), blank=True, null=True)
	# soporte = models.FileField(upload_to = 'solicitud/favorabilidad_tecnica', blank=True, null=True)

	class Meta:
		db_table = 'solicitud_favorabilidad_tecnica'

	def archivo(self):
		return """<a href="%s" >Documento</a>"""%self.soporte.url
	archivo.allow_tags = True

	def __unicode__(self):
		return self.solicitud.tipo.nombre+ ' - '+ self.solicitud.contrato.nombre

class DFavorabilidadTecnicaRequisito(models.Model):
	requisito = models.ForeignKey(BRequisitoTecnico, on_delete=models.PROTECT)
	favorabilidad = models.ForeignKey(CFavorabilidadTecnica, on_delete=models.PROTECT)
	estado = models.BooleanField(default= False)

	class Meta:
		db_table = 'solicitud_favorabilidad_tecnica_requisito'
# Fin de Tecnica

# Poliza
class BRequisitoPoliza(BaseModel):

	class Meta:
		db_table = 'solicitud_requisito_poliza'

class CValidarPoliza(models.Model):
	solicitud = models.ForeignKey(ASolicitud, related_name='fk_validar_poliza_solicitud', on_delete=models.PROTECT)
	soporte = models.FileField(upload_to = RandomFileName('solicitud/validar_poliza','vld_plz'), blank=True, null=True)
	# soporte = models.FileField(upload_to = 'solicitud/validar_poliza', blank=True, null=True)

	class Meta:
		db_table = 'solicitud_validar_poliza'

	def archivo(self):
		return """<a href="%s" >Documento</a>"""%self.soporte.url
	archivo.allow_tags = True

	def __unicode__(self):
		return self.solicitud.tipo.nombre

class DPolizaTipo(models.Model):
	validar_poliza = models.ForeignKey(CValidarPoliza, related_name='fk_poliza_tipo_validar_poliza', on_delete=models.PROTECT)
	tipo = models.ForeignKey(Tipo, on_delete=models.PROTECT)

	class Meta:
		db_table = 'solicitud_poliza_tipo'

	def __unicode__(self):
		return self.tipo.nombre

class EPolizaTipoRequisito(models.Model):
	requisito = models.ForeignKey(BRequisitoPoliza, related_name='fk_poliza_tipo_requisito_requisito', on_delete=models.PROTECT)
	poliza_tipo = models.ForeignKey(DPolizaTipo, related_name='fk_poliza_tipo_requisito_tipo', on_delete=models.PROTECT)
	estado = models.BooleanField(default = False)

	class Meta:
		db_table = 'solicitud_poliza_tipo_requisito'
# Fin de Poliza


