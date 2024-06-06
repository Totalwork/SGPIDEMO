from django.db import models
from proyecto.models import Proyecto
from contrato.models import Contrato
from usuario.models import Usuario
from empresa.models import Empresa
from tipo.models import Tipo
from datetime import *
from django.utils import * 
from coasmedas.functions import functions
from colorfield.fields import ColorField

from django.db.models import Sum
# Create your models here.


class BaseModel(models.Model):
	nombre = models.CharField(max_length=255)

	class Meta:
		abstract = True
		#permission = ('puede_ver','puede_ver')


	def __unicode__(self):
		return self.nombre


class APeriodicidadG(BaseModel):
	numero_dias=models.IntegerField()

	class Meta:
		db_table = 'avanceObraGrafico_periodicidad'
		permissions = (
			("can_see_periodicidadg","can see periodicidadg"),
		)
		unique_together = [
			["nombre",],
		]
		verbose_name='Periodicidad' 

class BEsquemaCapitulosG(BaseModel):
	macrocontrato=models.ForeignKey(Contrato,related_name="esquema_contratog",on_delete=models.PROTECT)

	class Meta:
		db_table = 'avanceObraGrafico_esquemaCapitulos'
		permissions = (
			("can_see_esquemacapitulosg","can see esquemacapitulosg"),
		)
		verbose_name='Esquemas'


class CEsquemaCapitulosActividadesG(BaseModel):
	#condiciones = ((u'0',u'[Ninguna...]'),(u'1',u'Finaliza con'),
		#(u'2',u'Comienza con'),(u'3',u'Finaliza al comenzar'), (u'4',u'Comienza al finalizar'),)
	esquema=models.ForeignKey(BEsquemaCapitulosG,related_name="actividades_esquemag",on_delete=models.PROTECT)
	nivel=models.IntegerField()
	padre = models.IntegerField()
	peso = models.FloatField()
	#condicion = models.CharField(max_length=1,choices=condiciones, default=0, 
		#verbose_name='condicion de inicio o finalizacion de actividad')
	#cantidadDias = models.IntegerField(verbose_name='numero de dias para complementar la condicion de inicio o finalizacion')
	#referencia = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, 
		#verbose_name='actividad referencia para complementar la condicion de inicio o finalizacion')

	class Meta:
		db_table = 'avanceObraGrafico_esquemaCapitulosActividades'
		permissions = (
			("can_see_esquemacapitulosactividadesg","can see esquemacapitulosactividadesg"),
		)
		verbose_name='Capitulos y actividades'



class DReglasEstadoG(BaseModel):
	esquema=models.ForeignKey(BEsquemaCapitulosG,related_name="regla_esquemag",on_delete=models.PROTECT)
	orden=models.IntegerField()
	operador=models.IntegerField()
	limite=models.FloatField()
	#estado=models.TextField(blank=True, null=True)

	class Meta:
		db_table = 'avanceObraGrafico_reglaEstado'
		permissions = (
			("can_see_reglaEstadog","can see reglaestadog"),
		)
		verbose_name='estructura de estado del cronograma'

	def __unicode__(self):
		return self.estado

class EPresupuesto(BaseModel):
	proyecto = models.ForeignKey(Proyecto, related_name='presupuesto_proyecto_avanceobragrafico',on_delete=models.PROTECT)
	esquema = models.ForeignKey(BEsquemaCapitulosG, related_name='presupuesto_esquemaCapitulos',on_delete=models.PROTECT)
	cerrar_presupuesto=models.BooleanField(default=False)

	class Meta:
		db_table='avanceObraGrafico_presupuesto'
		permissions=(
			("can_see_presupuesto","can see presupuesto"),
		)
		verbose_name='Encabezado de presupuesto'
	def __unicode__(self):
		return self.nombre

	def cantidad_cronograma(self):
		cronograma=KCronograma.objects.filter(presupuesto_id=self.id)
		return len(cronograma)

class FDetallePresupuesto(models.Model):
	presupuesto = models.ForeignKey(EPresupuesto,related_name='detallePresupuesto_presupuesto',on_delete=models.PROTECT)
	actividad = models.ForeignKey(CEsquemaCapitulosActividadesG,
		related_name='detallePresupuesto_esquemacpitulosactividades',on_delete=models.PROTECT)
	codigoUC = models.CharField(max_length=20,blank=True,null=True)
	descripcionUC = models.CharField(max_length=255,blank=True,null=True)
	valorManoObra = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	valorMaterial = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	valorGlobal = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	cantidad = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	porcentaje = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)

	class Meta:
		db_table='avanceObraGrafico_detallePresupuesto'
		permissions=(
			('can_see_detallepresupuesto','can see detallepresupuesto'),
		)
		verbose_name = 'detalle de presupuesto'


	def nombre_padre(self):
		padre=CEsquemaCapitulosActividadesG.objects.get(pk=self.actividad.padre)
		return padre.nombre

	def cantidad_apoyo(self):
		porcentaje=JCantidadesNodo.objects.filter(detallepresupuesto_id=self.id).aggregate(Sum('cantidad'))
		porcentaje['cantidad__sum']=0 if porcentaje['cantidad__sum']==None else porcentaje['cantidad__sum']
		return porcentaje['cantidad__sum']

	def disponibilidad_cantidad_apoyo(self):
		porcentaje=JCantidadesNodo.objects.filter(detallepresupuesto_id=self.id).aggregate(Sum('id'))
		porcentaje['id__sum']=0 if porcentaje['id__sum']==None else porcentaje['id__sum']
		return porcentaje['id__sum']

	def __unicode__(self):
		return self.presupuesto.nombre + ' >> ' + self.actividad.nombre

class GCapa(BaseModel):
	color = ColorField(default='#000000')

	def __unicode__(self):
		return self.nombre

	class Meta:		
		unique_together = [
			["nombre"],
		]
		db_table = 'avanceObraGrafico_capa'
		verbose_name = 'Capa'

class HNodo(models.Model):
	presupuesto = models.ForeignKey(EPresupuesto,related_name='nodo_presupuesto',on_delete=models.PROTECT)
	nombre	= models.CharField(max_length=50)
	capa = models.ForeignKey(GCapa, related_name='capaDelNodo',on_delete=models.PROTECT)
	longitud	= models.CharField(max_length=50,null=True)
	latitud	= models.CharField(max_length=50,null=True)
	noProgramado = models.BooleanField(default=False)
	eliminado = models.BooleanField(default=False)

	def __unicode__(self):
		return self.nombre

	class Meta:
		permissions=(
			('can_see_nodo','can see nodo'),
		)
		db_table = 'avanceObraGrafico_nodo'
		verbose_name = 'Nodo'
	

class IEnlace(models.Model):
	nodoOrigen = models.ForeignKey(HNodo, related_name='nodoOrigenRefenciado',on_delete=models.PROTECT)	
	nodoDestino = models.ForeignKey(HNodo, related_name='nodoDestinoRefenciado',on_delete=models.PROTECT)
	capa = models.ForeignKey(GCapa, related_name='capaDelEnlace',on_delete=models.PROTECT)	
	detallepresupuesto = models.ForeignKey(FDetallePresupuesto,
		related_name='enlance_detallepresupuesto',on_delete=models.PROTECT)
	class Meta:
		permissions=(
			('can_see_enlace','can see enlace'),
		)
		db_table = 'avanceObraGrafico_enlace'
		verbose_name = 'enlace entre nodos'

	def __unicode__(self):
		return self.nodoOrigen.nombre + '->' + self.nodoDestino.nombre

class JCantidadesNodo(models.Model):
	detallepresupuesto = models.ForeignKey(FDetallePresupuesto,
		related_name='cantidadesnodo_detallepresupuesto',on_delete=models.PROTECT)
	nodo = models.ForeignKey(HNodo,related_name='cantidadesnodo_nodo',on_delete=models.PROTECT)
	cantidad = models.DecimalField(max_digits=30, decimal_places=2)

	class Meta:
		unique_together = [
			["detallepresupuesto","nodo"],
		]
		permissions=(
			('can_see_cantidadesnodo','can see cantidadesnodo'),
		)
		db_table='avanceObraGrafico_cantidadesnodo'
		verbose_name = 'cantidades por nodo'


class KCronograma(BaseModel):
	presupuesto = models.ForeignKey(EPresupuesto,related_name='cronograma_presupuesto',on_delete=models.PROTECT)	
	fechaInicio = models.DateField(null=True)
	estado = models.ForeignKey(DReglasEstadoG,related_name="cronograma_reglaEstado",on_delete=models.PROTECT,
		null=True, blank=True)
	programacionCerrada=models.BooleanField(default=False)

	class Meta:
		permissions=(
			('can_see_cronograma','can see cronograma'),
		)		
		db_table='avanceObraGrafico_cronograma'
		verbose_name='Cronograma'

	def save(self, *args, **kwargs):
		#valido si el presupuesto tiene cantidades cargadas		
		queryset_linea = LProgramacion.objects.filter(cronograma__id=self.id,tipo_linea=1)
		if queryset_linea.count()==0:
			queryset = JCantidadesNodo.objects.filter(detallepresupuesto__presupuesto__id=self.presupuesto.id)
			if queryset.count()>0:
				super(KCronograma, self).save(*args, **kwargs)
				cantidadesNodo = queryset.values('id')
				for cn in cantidadesNodo:
					programacion = LProgramacion(
						cronograma=self,
						tipo_linea=1,
						cantidadesNodo=JCantidadesNodo.objects.get(id=cn['id'])
					)
					programacion.save()
		else:			
			super(KCronograma, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		#si borro el cronograma, debo borrar todas las programaciones que tenga asociadas el cronograma
		LProgramacion.objects.filter(cronograma=self).delete()
		super(KCronograma, self).delete(*args, **kwargs)



class LPorcentaje(models.Model):
	cronograma = models.ForeignKey(KCronograma,related_name='porcentaje_cronograma',on_delete=models.PROTECT)
	fecha = models.DateField(null=True)
	porcentaje = models.FloatField()
	detallepresupuesto = models.ForeignKey(FDetallePresupuesto,
		related_name='porcentaje_detallepresupuesto',on_delete=models.PROTECT)
	tipo_linea=models.IntegerField()
	# tipo linea 1 es linea base y tipo linea 2 es programada

	class Meta:
		permissions=(
			('can_see_porcentaje','can see porcentaje'),
		)
		db_table='avanceObraGrafico_porcentaje'
		verbose_name='Porcentaje de trabajos'


class LProgramacion(models.Model):
	cronograma = models.ForeignKey(KCronograma,related_name='programacion_cronograma',on_delete=models.PROTECT)
	cantidadesNodo = models.ForeignKey(JCantidadesNodo,related_name='programacion_cantidadesnodo',on_delete=models.PROTECT)
	fecha = models.DateField(null=True,blank=True)
	tipo_linea=models.IntegerField()
	# tipo linea 1 es linea base y tipo linea 2 es programada

	class Meta:
		permissions=(
			('can_see_programacion','can see programacion'),
		)
		db_table='avanceObraGrafico_programacion'
		verbose_name='Programacion de trabajos'

	def cantidad_ejecutadas(self):
		cantidad=QEjecucionProgramada.objects.filter(programacion_id=self.id).aggregate(Sum('cantidadEjecutada'))
		cantidad['cantidadEjecutada__sum']=0 if cantidad['cantidadEjecutada__sum']==None else cantidad['cantidadEjecutada__sum']
		return cantidad['cantidadEjecutada__sum']

class MEstadoCambio(BaseModel):
	class Meta:
		db_table='avanceObraGrafico_estado'
		verbose_name='Estados de un cambio'
		unique_together = [
			["nombre",],
		]
		permissions=(
			('can_see_estadoCambio','can see estadoCambio'),
		)


class NCambio(BaseModel):
	cronograma = models.ForeignKey(KCronograma,related_name='cambio_cronograma',on_delete=models.PROTECT)
	estado = models.ForeignKey(MEstadoCambio,related_name='cambio_estadocambio',on_delete=models.PROTECT)
	motivo = models.CharField(max_length=500)
	fecha = models.DateTimeField(auto_now_add=True)	
	solicitante = models.ForeignKey(Usuario,related_name='cambio_usuario_solicitante',on_delete=models.PROTECT)
	nodos=models.ManyToManyField(HNodo,related_name="cambio_nodo", blank=True)
	empresa_tecnica = models.ForeignKey(Empresa,related_name='cambio_empresa_tecnica',on_delete=models.PROTECT)
	empresa_financiera = models.ForeignKey(Empresa,related_name='cambio_empresa_financiera',on_delete=models.PROTECT)
	tipo_accion=models.ForeignKey(Tipo, on_delete=models.PROTECT,related_name="cambio_tipo_accion")
	motivoRechazoTecnico = models.CharField(max_length=255,null=True,blank=True)
	motivoRechazoFinanciero = models.CharField(max_length=255,null=True,blank=True)
	motivoCancelacion = models.CharField(max_length=255,null=True,blank=True)

	class Meta:
		db_table='avanceObraGrafico_cambio'
		verbose_name='Encabezado del control de cambios'
		permissions=(
			('can_see_cambios','can see cambios'),
		)

	def fecha_format(self):
		return self.fecha.strftime("%Y-%m-%d %H:%M:%S") 




# class PDetalleNodoNuevo(models.Model):
# 	detallePresupuesto=models.ForeignKey(FDetallePresupuesto,related_name='detalleNodoNuevo_detallePresupuesto',
# 		on_delete=models.PROTECT)
# 	nodo = models.ForeignKey(HNodo,related_name='detalleNodoNuevo_nodo',on_delete=models.PROTECT)
# 	cantidad = models.DecimalField(max_digits=30, decimal_places=3)
# 	fecha = models.DateField()

# 	class Meta:
# 		db_table='avanceObraGrafico_detalleNodoNuevo'
# 		verbose_name='Detalle de los nodos nuevos'
# 		permissions=(
# 			('can_see_detalleNodoNuevo','can see detalleNodoNuevo'),
# 		)


class PDetalleCambio(models.Model):
	detallePresupuesto=models.ForeignKey(FDetallePresupuesto,related_name='detalleCambio_detallePresupuesto',
		on_delete=models.PROTECT)
	cambio = models.ForeignKey(NCambio,related_name='detalleCambio_cambio',on_delete=models.PROTECT)
	nodo = models.ForeignKey(HNodo,related_name='detalleCambio_nodo',on_delete=models.PROTECT)
	cantidad = models.DecimalField(max_digits=30, decimal_places=3)
	fechaProgramada = models.DateField(null=True,blank=True)

	class Meta:
		db_table='avanceObraGrafico_detalleCambio'
		verbose_name='Detalle del cambio'
		permissions=(
			('can_see_detalleCambio','can see detalleCambio'),
		)

class QEjecucionProgramada(models.Model):
	programacion = models.ForeignKey(LProgramacion,related_name='ejecucionProgramada_programacion',
		on_delete=models.PROTECT)
	cantidadEjecutada = models.DecimalField(max_digits=30, decimal_places=3)
	fecha = models.DateField(null=True,blank=True)
	observacion = models.CharField(max_length=255,null=True,blank=True)

	class Meta:
		db_table='avanceObraGrafico_ejecucionProgramada'
		verbose_name='Ejecucion programada'
		unique_together=[
			['programacion','cantidadEjecutada','fecha'],
		]
		permissions=(
			('can_see_ejecucionProgramada','can see ejecucionProgramada'),
		)


class RDiagramaGrahm(models.Model):
	# condiciones = ((u'0',u'[Ninguna...]'),(u'1',u'Finaliza con'),
	# 	(u'2',u'Comienza con'),(u'3',u'Finaliza al comenzar'), (u'4',u'Comienza al finalizar'),)
	presupuesto=models.ForeignKey(EPresupuesto,related_name='diagramagrahm_presupuesto',
		on_delete=models.PROTECT)
	actividad=models.ForeignKey(CEsquemaCapitulosActividadesG,related_name='diagramagrahm_actividad',
		on_delete=models.PROTECT)
	fechaInicio = models.DateField(null=True,blank=True)
	fechaFinal = models.DateField(null=True,blank=True)
	# dias = models.IntegerField(null=True,blank=True)
	# condicion = models.CharField(max_length=1,choices=condiciones, default=0, 
	# 	verbose_name='condicion de inicio o finalizacion de actividad')
	# referencia = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, 
	# 	verbose_name='actividad referencia para complementar la condicion de inicio o finalizacion')

	class Meta:
		db_table='avanceObraGrafico_diagrama'
		verbose_name='Diagrama Grahm'
		permissions=(
			('can_see_diagramaGrahm','can see diagramaGrahm'),
		)	
		
	def nombre_padre(self):
		padre=CEsquemaCapitulosActividadesG.objects.get(pk=self.actividad.padre)
		return padre.nombre


class RPorcentajeApoyo(models.Model):
	apoyo = models.ForeignKey(HNodo,related_name='porcentaje_apoyo',on_delete=models.PROTECT)
	porcentaje = models.FloatField()
	cronograma = models.ForeignKey(KCronograma,related_name='porcentaje_apoyo_cronograma',on_delete=models.PROTECT)

	class Meta:
		db_table='avanceObraGrafico_porcentaje_apoyo'
		verbose_name='Porcentaje de Apoyo'
		permissions=(
			('can_see_porcentaje_apoyo','can see porcentaje_apoyo'),
		)

class LPorcentajePresupuesto(models.Model):
	cronograma = models.ForeignKey(KCronograma,related_name='porcentaje_presupuesto_cronograma',on_delete=models.PROTECT)
	fecha = models.DateField(null=True)
	valor_ganando = models.FloatField()
	detallepresupuesto = models.ForeignKey(FDetallePresupuesto,
		related_name='porcentaje_presupuesto_detallepresupuesto',on_delete=models.PROTECT)

	class Meta:
		permissions=(
			('can_see_porcentaje_ganando','can see porcentaje_ganando'),
		)
		db_table='avanceObraGrafico_porcentaje_presupuesto'
		verbose_name='Porcentaje de saldo de trabajos'	
		

# class REjecucionCambio(models.Model):
# 	detalleCambio = models.ForeignKey(PDetalleCambio,related_name='ejecicionCambio_detalleCambio',
# 		on_delete=models.PROTECT)
# 	cantidadEjecutada = models.DecimalField(max_digits=30, decimal_places=3)
# 	fecha = models.DateField()
# 	observacion = models.CharField(max_length=255,null=True,blank=True)

# 	class Meta:
# 		db_table='avanceObraGrafico_ejecucionCambio'
# 		verbose_name='Ejecucion cambio'
# 		unique_together=[
# 			['detalleCambio','cantidadEjecutada','fecha'],
# 		]
# 		permissions=(
# 			('can_see_ejecucionCambio','can see ejecucionCambio'),
# 		)








