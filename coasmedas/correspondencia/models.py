from django.db import models
from empresa.models import Empresa
from tipo.models import Tipo
from usuario.models import Usuario
from estado.models import Estado
from parametrizacion.models import Funcionario , Municipio

from contrato.models import Contrato,EmpresaContrato
from proyecto.models import Proyecto
import datetime
# Create your models here.
class BaseModel(models.Model):
 nombre = models.CharField(max_length=250)

 class Meta:
   abstract = True

 def __unicode__(self):
  return self.nombre

class CorresPfijo(BaseModel):
	empresa = models.ForeignKey(Empresa , related_name="fk_CorrespondenciaConsecutivo_empresa_Empresa" , on_delete=models.PROTECT )
	estado = models.BooleanField(default=True)
	# campo para mostrar el ano en el consecutivo de la correspondencias
	mostrar_ano =  models.BooleanField(default=False)
	class Meta:
		unique_together = (("nombre", "empresa"),)
		permissions = (("can_see_CorresPfijo","can_see_CorresPfijo"),)
		
# se usa para las correspondencias enviadas
class CorrespondenciaConsecutivo(models.Model):
	ano =  models.IntegerField()
	numero =  models.IntegerField()
	prefijo = models.ForeignKey(CorresPfijo , related_name="fk_CorrespondenciaConsecutivo_CorresPfijo" , on_delete=models.PROTECT )

	class Meta:
		unique_together = (("prefijo", "ano"),)
		permissions = (("can_see_CorrespondenciaConsecutivo","can_see_CorrespondenciaConsecutivo"),)

class CorrespondenciaEnviada(models.Model):
	empresa = models.ForeignKey(Empresa , related_name="fk_CorrespondenciaEnviada_empresa_Empresa" , on_delete=models.PROTECT )
	consecutivo = models.BigIntegerField(blank=True)
	fechaEnvio = models.DateField()
	anoEnvio = models.BigIntegerField()
	asunto = models.CharField(max_length=4000,  blank = True)
	referencia = models.CharField(max_length=4000 , blank = True)
	fechaRegistro = models.DateTimeField(auto_now_add=True)
	grupoSinin = models.BooleanField(default=False)
	persona_destino = models.CharField( max_length=250, blank=True)
	cargo_persona = models.CharField(max_length=250 , blank=True)
	direccion = models.CharField(max_length=250, blank=True)
	municipioEmpresa = models.ForeignKey(Municipio , related_name="fk_CorrespondenciaEnviada_municipioEmpresa" , on_delete=models.PROTECT , null=True , blank=True)
	telefono = models.CharField(max_length=250, blank=True)
	contenido = models.TextField(blank=True)
	contenidoHtml = models.TextField(blank=True)
	# ESTE CAMPO HACE REFERENCIA SOLAMENTE A MULTA y solo puede ser blanco 
	clausula_afectada = models.TextField(blank=True)
	clausula_afectadaHtml = models.TextField(blank=True)
	firma = models.ForeignKey(Funcionario , related_name="fk_CorrespondenciaEnviada_firma" , on_delete=models.PROTECT)
	ciudad = models.ForeignKey(Municipio , related_name="fk_CorrespondenciaEnviada_ciudad" , on_delete=models.PROTECT)
	privado = models.BooleanField(default=False)
	empresa_destino = models.CharField(max_length=250, blank=True)
	anulado = models.BooleanField(default=False)
	prefijo = models.ForeignKey(CorresPfijo , related_name="fk_CorrespondenciaEnviada_perfijo" , on_delete=models.PROTECT)
	usuarioSolicitante = models.ForeignKey(Usuario , related_name = 'fk_CorrespondenciaEnviada_usuarioSolicitante_Usuario' , on_delete=models.PROTECT)
	contrato  = models.ManyToManyField(Contrato, related_name='fk_CorrespondenciaEnviada_contrato',  blank = True)
	proyecto  = models.ManyToManyField(Proyecto, related_name='fk_CorrespondenciaEnviada_proyecto', blank = True)
	usuario  = models.ManyToManyField(Usuario, related_name='fk_CorrespondenciaEnviada_usuario')
	class Meta:
		permissions = (("can_see_CorrespondenciaEnviada","can_see_CorrespondenciaEnviada"),)
		unique_together = [ ["empresa", "consecutivo" , "anoEnvio" , "prefijo" ],]
	def __unicode__(self):
		return	'Consecutivo '+str(self.consecutivo)+' -- Empresa '+str(self.empresa)+' -- Fecha '+str(self.fechaEnvio)

class CorrespondenciaSoporte(models.Model):
	nombre = models.CharField(max_length=600 , null=True )
	correspondencia = models.ForeignKey(CorrespondenciaEnviada , related_name="fk_CorrespondenciaSoporte_correspondencia" , on_delete=models.PROTECT)
	soporte = models.FileField(upload_to='correspondencia' , null=True )
	anulado =  models.BooleanField(default=False)

	class Meta:
		permissions = (("can_see_CorrespondenciaSoporte","can_see_CorrespondenciaSoporte"),)


# se usa para las correspondencias recibidas
class CorrespondenciaRadicado(models.Model):
	"""docstring for CorrespondenciaRecibidaRadicado"""
	empresa = models.ForeignKey(Empresa , related_name="fk_CorrespondenciaRadicado_empresa" , on_delete=models.PROTECT)
	ano =  models.IntegerField()
	numero =  models.IntegerField()

	class Meta:
		unique_together = (("empresa", "ano"),)


# plantilla para la correspondencia de la empresa
class CorrespondenciaPlantilla(models.Model):
	"""docstring for CorrespondenciaRecibidaRadicado"""
	empresa = models.OneToOneField(Empresa , related_name="fk_CorrespondenciaPlantilla_empresa" , on_delete=models.PROTECT , unique = True)
	soporte = models.FileField(upload_to='plantillas/correspondenciaEnviada' , null=True )