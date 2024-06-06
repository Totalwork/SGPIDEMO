from django.db import models
from empresa.models import Empresa
from django.contrib.contenttypes.models import ContentType
from smart_selects.db_fields import ChainedForeignKey
from parametrizacion.models import Funcionario
from coasmedas.functions import functions, RandomFileName
from usuario.models import Usuario
from proyecto.models import Proyecto
from contrato.models import Contrato
# Create your models here.
class AProceso(models.Model):
	apuntadorChoices=(
		(u'0',u'[Seleccione...]'),
		(u'1',u'Proyecto'),
		(u'2',u'Contrato'),
	)
	nombre = models.CharField(max_length=150)
	activo = models.BooleanField(default=True)
	apuntador = models.CharField(max_length=1,choices=apuntadorChoices,default=0)
	tablaReferencia = models.ForeignKey(ContentType, on_delete=models.PROTECT, 
		verbose_name='Tabla referenciada', related_name='fk_tablaReferenciaProceso')
	campoEnlace = models.CharField(max_length=50, null=False, verbose_name='Campo enlace')
	tablaForanea = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True, 
		verbose_name='Tabla foranea de la referencia', related_name='fk_tablaForaneaRefenciaProceso')
	campoEnlaceTablaForanea=models.CharField(max_length=50,null=True, blank=True,
		verbose_name='Campo Tabla foranea de la referencia' )
	etiqueta = models.CharField(max_length=50,null=True,blank=True,
		verbose_name='Origen Etiqueta en implementacion')
	empresas  = models.ManyToManyField(Empresa, related_name='fk_empresasQueAccedenAlProceso', verbose_name='Empresas que acceden al proceso')
	pasoAPaso = models.BooleanField(default=False, 
		verbose_name='Indica si el seguimiento se hace paso a paso (defina responsables de items)')

	class Meta:		
		db_table = 'Proceso_proceso'	
		permissions = (
			("can_see_proceso","can see proceso"),
		)
		verbose_name='Proceso' 

	def __unicode__(self):
		return self.nombre

	def nombreApuntador(self):
		retorno='No asignado'
		if self.apuntador=='1':
			retorno='Proyecto'
		if self.apuntador=='2':
			retorno='Contrato'

		return retorno

	def get_empresas(self):
		return Empresa.objects.all()
	

class BItem(models.Model):
	tipoDatoChoices=(
		(u'0',u'[Seleccione...]'),
		(u'1',u'Numerico'),
		(u'2',u'Texto'),
		(u'3',u'Si/No'),
		(u'4',u'Fecha'),
	)
	notificacionCumplimientoChoices=(
		(u'1',u'A nadie'),
		(u'2',u'A todos los responsables del proyecto/contrato'),
		(u'3',u'Seleccionar a quien notificar'),
	)
	proceso = models.ForeignKey(AProceso, related_name='procesoDelItem',on_delete=models.PROTECT)
	orden = models.IntegerField(default=1)
	descripcion = models.TextField(max_length=150)
	tipoDato = models.CharField(max_length=1,choices=tipoDatoChoices,default=0, verbose_name='Tipo de dato')
	notificacionCumplimiento = models.CharField(max_length=1,
		choices=notificacionCumplimientoChoices,default=1, 
		verbose_name='Accion acerca de notificacion de cumplimiento')
	tieneVencimiento = models.BooleanField(default=False)
	tieneObservacion = models.BooleanField(default=False)
	tieneSoporte = models.BooleanField(default=False)
	soporteObligatorio = models.BooleanField(default=False)
	activo = models.BooleanField(default=True)
	responsable = models.ForeignKey(Usuario, related_name='responsableTitularItem',null=True, 
		blank=True, on_delete=models.PROTECT)
	afectarImplementacionesAnteriores = models.BooleanField(default=False,
		verbose_name='Defina como Si, en caso que desee afectar implementaciones realizadas')
	contratistaResponsable = models.BooleanField(default=False,
		verbose_name='indica si el eventual contratista es el responsable de este item')

	class Meta:		
		db_table = 'Proceso_item'
		verbose_name='Item' 

	def save(self, *args, **kwargs):
		super(BItem, self).save(*args, **kwargs)
		if self.afectarImplementacionesAnteriores:
			procesoRelaciones=FProcesoRelacion.objects.filter(proceso=self.proceso).values('id')
			for pr in procesoRelaciones:
				prd = GProcesoRelacionDato.objects.filter(procesoRelacion=FProcesoRelacion.objects.get(id=pr['id']),
					item=self)
				#import pdb; pdb.set_trace()
				if prd.count()==0:
					prd = GProcesoRelacionDato(
						procesoRelacion=FProcesoRelacion.objects.get(id=pr['id']),
						item=self)
					prd.save()

	def __unicode__(self):
		return self.proceso.nombre +' >> '+self.descripcion

class CPermisoEmpresaItem(models.Model):
	empresa = models.ForeignKey(Empresa,related_name='fk_empresaConPermisoAlItem',on_delete=models.PROTECT)
	item = models.ForeignKey(BItem, related_name='fk_itemConPermisoAlaEmpresa',on_delete=models.PROTECT)
	lectura = models.BooleanField(default=True)
	escritura = models.BooleanField(default=False)

	class Meta:		
		db_table = 'Proceso_permisoEmpresaItem' 
		verbose_name='Permisos de empresas sobre items'
		unique_together = [
			["empresa", "item"],
		]

	def __unicode__(self):
		return self.item.descripcion

	def nombreProceso(self):
		return self.item.proceso.nombre

	def nombreEmpresa(self):
		return self.empresa.nombre

	def descripcionItem(self):
		return self.item.descripcion	

class DVinculo(models.Model):
	procesoOrigen=models.ForeignKey(AProceso,related_name='fk_vinculoProcesoOrigen',
		on_delete=models.PROTECT, verbose_name='Proceso origen del vinculo')
	procesoDestino = models.ForeignKey(AProceso,related_name='fk_vinculoProcesoDestino',
		on_delete=models.PROTECT,verbose_name='Proceso destino del vinculo')
	# itemVinculado = models.ForeignKey(BItem,related_name='fk_itemVinculadoEntreProcesos',
	# 	verbose_name='item vinculado',on_delete=models.PROTECT)
	itemVinculado = ChainedForeignKey(
		BItem,
		chained_field='procesoOrigen',
		chained_model_field='proceso',
		related_name='fk_itemVinculadoEntreProcesos',
		verbose_name='item vinculado',on_delete=models.PROTECT, null=False
	)

	class Meta:
		db_table= 'Proceso_vinculo'
		verbose_name='items vinculados entre procesos'
		unique_together = [
			["procesoOrigen", "procesoDestino","itemVinculado"],
		]

	def __unicode__(self):
		return self.itemVinculado.descripcion

	def nombreProcesoOrigen(self):
		return self.procesoOrigen

	def nombreProcesoDestino(self):
		return self.procesoDestino

	def descripcionItemVinculado(self):
		return self.itemVinculado.descripcion


class ECampoInforme(models.Model):
	proceso = models.ForeignKey(AProceso,related_name='fk_procesoConfInforme',
		on_delete=models.PROTECT)
	nombreCampoApuntador = models.CharField(max_length=50, null=False)
	tablaForanea = models.ForeignKey(ContentType,related_name='fk_tablaForaneaRefencia',
		on_delete=models.PROTECT,null=True,blank=True)
	campoTablaForanea = models.CharField(max_length=50,null=True,blank=True)

	class Meta:
		db_table='Proceso_CampoInforme'
		verbose_name='CampoInforme'

	def __unicode__(self):
		return self.proceso.nombre + ' >> ' + self.nombreCampoApuntador	

	def nombreProceso(self):
		return self.proceso.nombre

	def nombreTablaForanea(self):
		if self.tablaForanea:
			return self.tablaForanea.name
		else:
			return ''

class FProcesoRelacion(models.Model):
	proceso = models.ForeignKey(AProceso,related_name='fk_procesoRelacion',
		on_delete=models.PROTECT, null=False)
	idApuntador = models.IntegerField(null=False,verbose_name='id del proyecto/contrato sobre el proceso')
	idTablaReferencia = models.IntegerField(null=False)

	class Meta:
		db_table = 'Proceso_procesoRelacion'
		verbose_name='ProcesoRelacion'
		unique_together = [
			["proceso", "idApuntador","idTablaReferencia"],
		]

	def __unicode__(self):
		return self.proceso.nombre + '['+ str(self.idApuntador)+']['+str(self.idTablaReferencia)+']'

	def nombreProceso(self):
		return self.proceso.nombre

	def apuntador(self):
		return self.proceso.apuntador

class GProcesoRelacionDato(models.Model):
	estadoChoice=(
		(u'0',u'Por cumplir'),
		(u'1',u'Cumplido'),
		(u'2',u'Por vencer'),
		(u'3',u'Vencido'),
	)
	procesoRelacion = models.ForeignKey(FProcesoRelacion,related_name='fk_DatosDelProcesoImplementado',
		on_delete=models.PROTECT)
	item = models.ForeignKey(BItem,related_name='fk_itemProcesoRelacionDatos',
		on_delete=models.PROTECT)
	fechaVencimiento = models.DateField(null=True,blank=True, verbose_name='Fecha de vencimiento de cumplimiento del item')
	observacion = models.TextField(max_length=150,null=True, blank=True)
	valor = models.CharField(max_length=50,default='Vacio')
	estado= models.CharField(max_length=1,choices=estadoChoice,default=0)


	class Meta:
		db_table = 'Proceso_procesoRelacionDato'
		verbose_name='ProcesoRelacionDatos'
		unique_together = [
			["procesoRelacion", "item"],
		]


	def __unicode__(self):
		return str(self.procesoRelacion.id) + ' - ' + self.item.descripcion

	def nombreItem(self):
		return self.item.descripcion

	def nombreProceso(self):
		return self.procesoRelacion.proceso.nombre

	def nombreEstado(self):
		retorno='No asignado'
		if self.estado=='0':
			retorno='Por cumplir'
		if self.estado=='1':
			retorno='Cumplido'
		if self.estado=='2':
			retorno='Por vencer'
		if self.estado=='3':
			retorno='Vencido'
		return retorno


class HSoporteProcesoRelacionDato(models.Model):
	procesoRelacionDato = models.ForeignKey(GProcesoRelacionDato,related_name='fk_soporteProcesoRelacionDato',
		on_delete=models.PROTECT, null=False)
	nombre = models.CharField(max_length=100, null=False)
	#documento = models.FileField(upload_to='procesos/soportes',null=True)
	documento = models.FileField(null=True,upload_to=RandomFileName('procesos/soportes','pso'))


	class Meta:
		db_table = 'Proceso_soporteProcesoRelacionDato'
		verbose_name='Soportes del procesoRelacionDato'

	def __unicode__(self):
		return self.nombre

	@property	
	def nombreProceso(self):
		return self.procesoRelacionDato.nombreProceso

	@property	
	def nombreItem(self):
		return self.procesoRelacionDato.nombreItem

	def archivo(self):
		return """<a href="%s">archivo</a> """ % self.documento.url

	archivo.allow_tags = True


class INotificacionVencimiento(models.Model):
	procesoRelacionDato = models.ForeignKey(GProcesoRelacionDato,
		related_name='fk_notificacionVencimientoProcesoRelacionDato',
		on_delete=models.PROTECT, null=False)
	funcionario = models.ForeignKey(Funcionario,related_name='fk_funcionarioANotificar',
		on_delete=models.PROTECT, null=False)
	responsableTitular = models.BooleanField(default=False)

	class Meta:
		db_table='Proceso_notificacionVencimiento'
		verbose_name='Notificacion de vencimiento'

	def nombreFuncionario(self):
		return self.funcionario.persona.nombres + ' ' + self.funcionario.persona.apellidos

	def empresaFuncionario(self):
		return self.funcionario.empresa.nombre

	def procesoANotificar(self):
		return self.procesoRelacionDato.procesoRelacion.proceso.nombre

	def itemANotificar(self):
		return self.procesoRelacionDato.item.descripcion

	def elementoAnalizado(self):
		elemento='No detectado'
		if self.procesoRelacionDato.procesoRelacion.proceso.tablaForanea:
			modeloReferencia = ContentType.objects.get(pk=self.procesoRelacionDato.procesoRelacion.proceso.tablaForanea.id).model_class()
			objElemento = modeloReferencia.objects.filter(
				id=self.procesoRelacionDato.procesoRelacion.idTablaReferencia).values(self.procesoRelacionDato.procesoRelacion.proceso.etiqueta)
			elemento= objElemento[0][self.procesoRelacionDato.procesoRelacion.proceso.etiqueta]			
		else:
			if self.procesoRelacionDato.procesoRelacion.proceso.apuntador=='1':
				proyecto = Proyecto.objects.get(pk=int(self.procesoRelacionDato.procesoRelacion.idApuntador))
				if proyecto:
					elemento = proyecto.nombre
			else:
				contrato = Contrato.objects.get(pk=int(self.procesoRelacionDato.procesoRelacion.idApuntador))	
				if contrato:
					elemento = contrato.nombre	
		return elemento

	def __unicode__(self):
		return self.procesoRelacionDato.item.descripcion + ' >> ' + self.funcionario.persona.nombres + ' ' + self.funcionario.persona.apellidos


class JSeguidorProcesoRelacion(models.Model):
	procesoRelacion = models.ForeignKey(FProcesoRelacion, related_name='fk_seguidor_procesoRelacion', on_delete=models.PROTECT)
	usuario = models.ForeignKey(Usuario,related_name='fk_seguidor_usuario', on_delete=models.PROTECT)

	class Meta:
		db_table='Proceso_SeguidorProcesoRelacion'
		verbose_name='Seguidor de procesoRelacion'
		unique_together = [
			["procesoRelacion", "usuario"],
		]

	def __unicode__(self):
		return self.usuario.user.username + ' - ' + str(self.procesoRelacion.id)		
