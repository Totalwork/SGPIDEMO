from django.db import models
from empresa.models import Empresa
from tipo.models import Tipo
from usuario.models import Usuario
from estado.models import Estado
from parametrizacion.models import Funcionario , Municipio

from contrato.models import Contrato,EmpresaContrato
from proyecto.models import Proyecto
from correspondencia.models import CorrespondenciaEnviada
import datetime
# Create your models here.


class CorrespondenciaRecibida(models.Model):	
	empresa = models.ForeignKey(Empresa , related_name="fk_CorrespondenciaRecibida_empresa_Empresa" , on_delete=models.PROTECT)
	radicado = models.BigIntegerField()
	fechaRecibida = models.DateField()
	anoRecibida = models.BigIntegerField()
	remitente = models.CharField(max_length=250 , null = True)
	asunto = models.TextField(blank=True)
	usuarioSolicitante = models.ForeignKey(Usuario , related_name = 'fk_CorrespondenciaRecibida_usuarioSolicitante_Usuario' , on_delete=models.PROTECT)
	fechaRegistro = models.DateTimeField(auto_now_add=True)
	privado = models.BooleanField(default=False)
	correspondenciaEnviada = models.ForeignKey(CorrespondenciaEnviada , related_name = 'fk_CorrespondenciaRecibida_correspondenciaEnviada' ,on_delete=models.PROTECT , null = True )
	radicadoPrevio = models.CharField(max_length=250 , blank=True)
	fechaRespuesta = models.DateField(null = True, blank=True)
	class Meta:
		permissions = (("can_see_CorrespondenciaRecibida","can_see_CorrespondenciaRecibida"),)
		unique_together = [ ["empresa", "radicado" , "anoRecibida"],]

	def __unicode__(self):
		return 'Radicado '+str(self.radicado)+' -- Empresa '+str(self.empresa)+' -- Fecha '+str(self.fechaRecibida)

class CorrespondenciaRecibidaAsignada(models.Model):
	correspondenciaRecibida = models.ForeignKey(CorrespondenciaRecibida , related_name="fk_CorrespondenciaRecibidaAsignada_correspondencia" , on_delete=models.PROTECT)
	usuario = models.ForeignKey(Usuario , related_name="fk_CorrespondenciaRecibidaAsignada_usuario" , on_delete=models.PROTECT)
	fechaAsignacion =  models.DateTimeField(auto_now_add=True)
	estado =  models.ForeignKey(Estado , related_name="fk_CorrespondenciaRecibidaAsignada_estado" , on_delete=models.PROTECT)
	respuesta =   models.ForeignKey(CorrespondenciaEnviada , related_name = 'fk_CorrespondenciaRecibidaAsignada_correspondenciaEnviada' ,on_delete=models.PROTECT , null = True , blank = True)
	copia =  models.BooleanField(default=False)
	class Meta:
		permissions = (("can_see_CorrespondenciaRecibidaAsignada","can_see_CorrespondenciaRecibidaAsignada"),)


class CorrespondenciaRecibidaSoporte(models.Model):
	nombre = models.CharField(max_length=250 , null=True )
	correspondencia = models.ForeignKey(CorrespondenciaRecibida , related_name="fk_CorrespondenciaRecibidaSoporte_correspondencia" , on_delete=models.PROTECT)
	soporte = models.FileField(upload_to='correspondencia_recibida' , null=True )
	anulado =  models.BooleanField(default=False)

	class Meta:
		permissions = (("can_see_CorrespondenciaRecibidaSoporte","can_see_CorrespondenciaRecibidaSoporte"),)