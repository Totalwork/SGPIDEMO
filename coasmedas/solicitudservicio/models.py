from django.db import models
from usuario.models import Usuario
from tipo.models import Tipo
from contrato.models import Contrato
from estado.models import Estado
from coasmedas.functions import functions, RandomFileName
from parametrizacion.models import Empresa

# Create your models here.

class AArea(models.Model):
	nombre = models.CharField(max_length=100)
	responsableArea = models.ForeignKey(Usuario, on_delete=models.PROTECT,
	 related_name='fk_solicitud_responsableArea')

	def __unicode__(self):
		return self.nombre

	def responsable(self):
		return self.responsableArea.persona.nombres + ' ' + self.responsableArea.persona.apellidos

	class Meta:
		unique_together = (("nombre",),)
		db_table = 'solicitudservicio_area'
		permissions = (
			("can_see_area","can see area"),
		)

class BSolicitud(models.Model):
	fechaCreacion = models.DateField(auto_now_add=True)
	area = models.ForeignKey(AArea, on_delete=models.PROTECT, related_name='fk_solicitud_usuarioSolicitante')
	solicitante = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='fk_solicitud_usuarioSolicitante')
	tipo =  models.ForeignKey(Tipo, on_delete=models.PROTECT, related_name='fk_solicitud_tipo')
	contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT, 
		related_name='fk_solicitud_tipo',null=True, blank=True)
	descripcion = models.CharField(max_length = 250)
	#tramitador =  models.ForeignKey(Usuario, on_delete=models.PROTECT,
	#	related_name='fk_solicitud_usuarioTramitador', null=True, blank=True)
	#autoriza =  models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='fk_solicitud_usuarioAutorizador')
	#fechaAutorizacionArea = models.DateField(blank=True,null=True)
	estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='fk_solicitud_estado')
	empresas  = models.ManyToManyField(Empresa, related_name='fk_solicitud_empresa', verbose_name='Empresas que acceden a la solicitud')


	def __unicode__(self):
		return self.area.nombre + '.' + self.solicitante.persona.nombres + ' ' + self.solicitante.persona.apellidos

	def nombreSolicitante(self):
		return self.solicitante.persona.nombres + ' ' + self.solicitante.persona.apellidos

	def nombreAutoriza(self):
		return self.autoriza.persona.nombres + ' ' + self.autoriza.persona.apellidos

	def numeroContrato(self):
		if self.contrato:
			return self.contrato.numero
		else:
			return ''

	class Meta:
		db_table = 'solicitudservicio_solicitud'
		permissions = (
			("can_see_solicitudservicio","can see solicitudservicio"),
		)

	def save(self, *args, **kwargs):
		super(BSolicitud, self).save(*args, **kwargs)
		self.empresas.add(self.solicitante.empresa)



class CSoportesSolicitud(models.Model):
	fechaCreacion = models.DateField(auto_now_add=True)
	solicitud = models.ForeignKey(BSolicitud,on_delete=models.PROTECT, related_name='fk_solicitud_soportes')
	nombre = models.CharField(max_length=150,default='soporte de la solicitud')
	#documento = models.FileField(upload_to='solicitudservicio/soportes',null=True)
	documento = models.FileField(null=True,upload_to=RandomFileName('solicitudservicio/soportes','solSer'))

	def __unicode__(self):
		return self.nombre

	def archivo(self):
		return """<a href="%s">archivo</a> """ % self.documento.url

	archivo.allow_tags = True

	class Meta:
		db_table='solicitudservicio_soporte'
		permissions=(
			("can_see_solicitudserviciosoporte","can see solicitudserviciosoporte"),
		)

