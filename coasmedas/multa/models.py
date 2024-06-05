from django.db import models

from parametrizacion.models import Funcionario
from empresa.models import Empresa
from contrato.models import Contrato
from estado.models import Estado
from correspondencia.models import CorrespondenciaEnviada
from tipo.models import Tipo 
from usuario.models import Usuario
from multa.enumeration import EstadoMulta


# Create your models here.
class BaseModel(models.Model):
 nombre = models.CharField(max_length=250)

 class Meta:
   abstract = True

 def __unicode__(self):
  return self.nombre


class SolicitudConsecutivo(models.Model):
	consecutivo = models.BigIntegerField()
	empresa = models.OneToOneField(Empresa , related_name = 'fk_Empresa_Consecutivo' , on_delete=models.PROTECT, primary_key=True)
	class Meta:	
		unique_together = (("empresa"),)

class ConjuntoEvento(BaseModel):
	pass
	class Meta:	
		unique_together = (("nombre"),)

class Evento(BaseModel):
	valor = models.FloatField()
	conjunto = models.ForeignKey(ConjuntoEvento , related_name = 'fk_ConjuntoEvento_conjunto' , on_delete=models.PROTECT)
	class Meta:	
		unique_together = (("nombre","conjunto"),)
		permissions = (("can_see_eventos","can see eventos"),)

class Solicitud(models.Model):
	contrato = models.ForeignKey(Contrato , related_name = 'fk_Contrato_contrato' , on_delete=models.PROTECT)
	correspondenciasolicita = models.ForeignKey(CorrespondenciaEnviada , related_name = 'fk_CorrespondenciaEnviada_correspondenciaEnviadaSolicitud' , on_delete=models.PROTECT )
	consecutivo = models.BigIntegerField(null = True)
	diasApelar = models.BigIntegerField()
	firmaImposicion = models.ForeignKey(Funcionario , related_name="fk_Funcionario_firmaImposicion" , on_delete=models.PROTECT , null=True)
	fechaDiligencia  = models.DateField(null=True)
	soporte  = models.FileField(upload_to='multa',blank=True, null=True)
	valorSolicitado  = models.FloatField()
	valorImpuesto  = models.FloatField()
	correspondenciadescargo  = models.ForeignKey(CorrespondenciaEnviada, related_name='fk_CorrespondenciaEnviada_correspondenciaEnviadaDescargo' , null = True , on_delete=models.PROTECT)
	# order de facturacion
	codigoOF = models.CharField(max_length=250 , blank=True)
	# codigo de referencia sap
	codigoReferencia = models.CharField(max_length=250 , blank=True)

	# estado actual
	def estado(self):
		historial = SolicitudHistorial.objects.filter(solicitud_id = self.id).latest('id')
		return historial

	class Meta:	
		permissions = (("can_see_solicitud","can_see_solicitud")
						# ELABORAR 
						,("can_see_elaborar","can see elaborar")
						,("can_download_elaborar","can download elaborar")
						,("can_upload_elaborar","can download elaborar")
						,("can_delete_elaborar","can delete elaborar")
						# GENERAR
						,("can_see_generar","can see generar")
						,("can_add_generar","can add generar")
						# DESCARGOS
						,("can_see_descargos_sin_pronunciar","can see descargos sin pronunciar")
						#  REGISTRAR OF
						,("can_see_registrar_codigo_of","can see registrar codigo of")
						 )

	def __unicode__(self):
		return	'Contrato '+str(self.contrato.nombre)+' -- Correspondencia '+str(self.correspondenciasolicita.consecutivo)+' -- consecutivo '+str(self.consecutivo)

class SolicitudSoporte(models.Model):
	nombre = models.CharField(max_length=250 , blank=True)
	solicitud = models.ForeignKey(Solicitud , related_name="fk_SolicitudSoporte_solicitud" , on_delete=models.PROTECT)
	soporte = models.FileField(upload_to='multa-solicitud' , null=True )
	anulado =  models.BooleanField(default=False)

	class Meta:
		permissions = (("can_see_SolicitudSoporte","can_see_SolicitudSoporte"),)


class SolicitudEmpresa(models.Model):
	empresa = models.ForeignKey(Empresa , related_name = 'fk_Empresa_SolicitudEmpresa' , on_delete=models.PROTECT)
	solicitud = models.ForeignKey(Solicitud , related_name = 'fk_Solicitud_SolicitudEmpresa' , on_delete=models.PROTECT)
	propietario = models.BooleanField(default=False)

	class Meta:	
		unique_together = (("empresa" , "solicitud"),("empresa" , "solicitud" , "propietario"))
		permissions = (("can_see_solicitudempresa","can_see_solicitudempresa"),)

class SolicitudEvento(models.Model):
	evento = models.ForeignKey(Evento , related_name = 'fk_Evento_evento' , on_delete=models.PROTECT)
	solicitud = models.ForeignKey(Solicitud , related_name = 'fk_Solicitud_SolicitudEvento' , on_delete=models.PROTECT)
	numeroimcumplimiento = models.IntegerField()

	class Meta:	
		unique_together = (("evento" , "solicitud"),)

class SolicitudHistorial(models.Model):
	fecha = models.DateTimeField(auto_now_add=True) 
	solicitud = models.ForeignKey(Solicitud , related_name = 'fk_Solicitud_SolicitudHistorial' , on_delete=models.PROTECT)
	estado = models.ForeignKey(Estado , related_name = 'fk_Estado_SolicitudHistorial' , on_delete=models.PROTECT)
	usuario = models.ForeignKey(Usuario , related_name = 'fk_Usuario_SolicitudHistorial' , on_delete=models.PROTECT)
	soporte = models.FileField(upload_to='multa-historial',blank=True, null=True)
	comentarios = models.TextField(blank=True)


class SolicitudApelacion(models.Model):
	fecha = models.DateField()
	solicitud = models.ForeignKey(Solicitud , related_name = 'fk_Solicitud_SolicitudApelacion' , on_delete=models.PROTECT )
	comentarios = models.TextField(blank=True)
	fecha_transacion = models.DateTimeField(auto_now_add=True) 
	soporte = models.FileField(upload_to='multa-apelacion',blank=True, null=True)

	class Meta:	
		permissions = (("can_see_solicitudapelacion","can_see_solicitudapelacion"),)

class SolicitudPronunciamiento(models.Model):

	apelacion = models.OneToOneField(SolicitudApelacion, related_name = 'fk_Apelacion_SolicitudPronunciamiento' , on_delete=models.PROTECT)
	comentarios = models.TextField(blank=True)
	fecha_transacion = models.DateTimeField(auto_now_add=True) 

	class Meta:	
		permissions = (("can_see_solicitudpronunciamiento","can_see_solicitudpronunciamiento"),)


	

