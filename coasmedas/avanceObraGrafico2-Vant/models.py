from django.db import models
from proyecto.models import Proyecto
from contrato.models import Contrato
from usuario.models import Usuario
from tipo.models import Tipo
from empresa.models import Empresa
from datetime import *
from django.utils import * 
from sinin4.functions import functions
from colorfield.fields import ColorField
from estado.models import Estado

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
		db_table = 'avanceObraGrafico2_periodicidad'
		permissions = (
			("can_see_periodicidadgrafico","can see periodicidadgrafico"),
		)
		unique_together = [
			["nombre",],
		]
		verbose_name='Periodicidad' 


class BEsquemaCapitulosG(BaseModel):
	macrocontrato=models.ForeignKey(Contrato,related_name="esquema_contrato_grafico",on_delete=models.PROTECT)

	class Meta:
		db_table = 'avanceObraGrafico2_esquemaCapitulos'
		permissions = (
			("can_see_esquemacapitulosgrafico","can see esquemacapitulosgrafico"),
		)
		verbose_name='Esquemas'


class CEsquemaCapitulosActividadesG(BaseModel):
	esquema=models.ForeignKey(BEsquemaCapitulosG,related_name="actividades_esquemagrafico",on_delete=models.PROTECT)
	nivel=models.IntegerField()
	padre = models.IntegerField()
	peso = models.FloatField()

	class Meta:
		db_table = 'avanceObraGrafico2_esquemaCapitulosActividades'
		permissions = (
			("can_see_esquemacapitulosactividadesgrafico","can see esquemacapitulosactividadesgrafico"),
		)
		verbose_name='Capitulos y actividades'


class CReglasEstadoG(BaseModel):
	esquema=models.ForeignKey(BEsquemaCapitulosG,related_name="regla_esquema_grafico",on_delete=models.PROTECT)
	orden=models.IntegerField()
	operador=models.IntegerField()
	limite=models.FloatField()

	class Meta:
		db_table = 'avanceObraGrafico2_reglaEstado'
		permissions = (
			("can_see_reglaEstadografico","can see reglaestadografico"),
		)
		verbose_name='estructura de estado del cronograma'

	def __unicode__(self):
		return self.estado


class Cronograma(BaseModel):
	proyecto = models.ForeignKey(Proyecto,related_name='cronograma_proyecto_grafico',on_delete=models.PROTECT)	
	estado = models.ForeignKey(CReglasEstadoG,related_name="cronograma_reglaEstado_grafico",on_delete=models.PROTECT,
		null=True, blank=True)
	programacionCerrada=models.BooleanField(default=False)
	periodicidad = models.ForeignKey(APeriodicidadG,related_name='cronograma_perioridicidad_grafico',on_delete=models.PROTECT)	
	esquema=models.ForeignKey(BEsquemaCapitulosG,related_name="cronograma_esquema_grafico",on_delete=models.PROTECT)
	

	class Meta:
		permissions=(
			('can_see_cronograma','can see cronograma'),
		)		
		db_table='avanceObraGrafico2_cronograma'
		verbose_name='Cronograma'


class DiagramaGrahm(models.Model):
	cronograma=models.ForeignKey(Cronograma,related_name='diagramagrahm_cronograma_grafico',
		on_delete=models.PROTECT)
	actividad=models.ForeignKey(CEsquemaCapitulosActividadesG,related_name='diagramagrahm_actividad_grafico',
		on_delete=models.PROTECT)
	fechaInicio = models.DateField(null=True,blank=True)
	fechaFinal = models.DateField(null=True,blank=True)
	actividad_inicial=models.BooleanField(default=False)
	

	class Meta:
		db_table='avanceObraGrafico2_diagrama'
		verbose_name='Diagrama Grahm'
		permissions=(
			('can_see_diagramaGrahm','can see diagramaGrahm'),
		)	
		
	def nombre_padre(self):
		padre=CEsquemaCapitulosActividadesG.objects.get(pk=self.actividad.padre)
		return padre.nombre


class EPresupuesto(BaseModel):
	cronograma = models.ForeignKey(Cronograma, related_name='presupuesto_cronograma_grafico',on_delete=models.PROTECT)
	cerrar_presupuesto=models.BooleanField(default=False)
	sin_poste=models.BooleanField(default=False)

	class Meta:
		db_table='avanceObraGrafico2_presupuesto'
		permissions=(
			("can_see_presupuesto","can see presupuesto"),
		)
		verbose_name='Encabezado de presupuesto'

	def __unicode__(self):
		return self.nombre


class FDetallePresupuesto(models.Model):
	presupuesto = models.ForeignKey(EPresupuesto,related_name='detallePresupuesto_presupuesto_grafico',on_delete=models.PROTECT)
	actividad = models.ForeignKey(CEsquemaCapitulosActividadesG,
		related_name='detallePresupuesto_esquemacpitulosactividades_grafico',on_delete=models.PROTECT)
	codigoUC = models.CharField(max_length=20,blank=True,null=True)
	descripcionUC = models.CharField(max_length=255,blank=True,null=True)
	valorManoObra = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	valorMaterial = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	valorGlobal = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	cantidad = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	porcentaje = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)

	class Meta:
		db_table='avanceObraGrafico2_detallePresupuesto'
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
		db_table = 'avanceObraGrafico2_capa'
		verbose_name = 'Capa'


class HNodo(BaseModel):
	presupuesto = models.ForeignKey(EPresupuesto,related_name='nodo_presupuesto_grafico',on_delete=models.PROTECT)
	capa = models.ForeignKey(GCapa, related_name='nodo_capa_grafico',on_delete=models.PROTECT)
	longitud	= models.CharField(max_length=50,null=True)
	latitud	= models.CharField(max_length=50,null=True)
	noProgramado = models.BooleanField(default=False)
	eliminado = models.BooleanField(default=False)
	porcentajeAcumulado = models.FloatField(blank=True,null=True)

	def __unicode__(self):
		return self.nombre

	class Meta:
		permissions=(
			('can_see_nodo','can see nodo'),
		)
		db_table = 'avanceObraGrafico2_nodo'
		verbose_name = 'Nodo'


class IEnlace(models.Model):
	nodoOrigen = models.ForeignKey(HNodo, related_name='nodoorigen_nodo_grafico',on_delete=models.PROTECT)	
	nodoDestino = models.ForeignKey(HNodo, related_name='nododestino_nodo_grafico',on_delete=models.PROTECT)
	capa = models.ForeignKey(GCapa, related_name='enlace_capa_grafico',on_delete=models.PROTECT)	
	detallepresupuesto = models.ForeignKey(FDetallePresupuesto,
		related_name='enlance_detallepresupuesto_grafico',on_delete=models.PROTECT)
	
	class Meta:
		permissions=(
			('can_see_enlace','can see enlace'),
		)
		db_table = 'avanceObraGrafico2_enlace'
		verbose_name = 'enlace entre nodos'

	def __unicode__(self):
		return self.nodoOrigen.nombre + '->' + self.nodoDestino.nombre


class JCantidadesNodo(models.Model):
	detallepresupuesto = models.ForeignKey(FDetallePresupuesto,
		related_name='cantidadesnodo_detallepresupuesto_grafico',on_delete=models.PROTECT)
	nodo = models.ForeignKey(HNodo,related_name='cantidadesnodo_nodo_grafico',on_delete=models.PROTECT)
	cantidad = models.DecimalField(max_digits=30, decimal_places=2)

	class Meta:
		permissions=(
			('can_see_cantidadesnodo','can see cantidadesnodo'),
		)
		db_table='avanceObraGrafico2_cantidadesnodo'
		verbose_name = 'cantidades por nodo'



class JReporteTrabajo(models.Model):
	presupuesto = models.ForeignKey(EPresupuesto,
		related_name='reportetrabajo_presupuesto_grafico',on_delete=models.PROTECT)
	fechaTrabajo = models.DateField(null=True,blank=True)
	usuario_registro = models.ForeignKey(Usuario,related_name='reportetrabajo_usuario_grafico',on_delete=models.PROTECT)
	valor_ganando_acumulado = models.FloatField(null=True)
	avance_obra_acumulado = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	sinAvance = models.BooleanField(default=False)
	motivoSinAvance = models.CharField(max_length=255,blank=True,null=True)
	fecharevision = models.DateField(null=True,blank=True)
	#soporteAprobacion = models.FileField(upload_to=functions.path_and_rename('avanceObraGrafico/soporte_aprobacion','aog'),blank=True, null=True)
	soporteAprobacion = models.FileField(upload_to='avanceObraGrafico_archivo',blank=True, null=True)
	usuario_aprueba= models.ForeignKey(Usuario,related_name='reportetrabajo_usuarioaprueba_grafico',on_delete=models.PROTECT,blank=True,null=True)
	estado=models.ForeignKey(Estado, on_delete=models.PROTECT,related_name="reportetrabajo_estado")
	reporteCerrado=models.BooleanField(default=False)
	empresa = models.ForeignKey(Empresa,related_name='reporte_empresa',on_delete=models.PROTECT)

	class Meta:
		permissions=(
			('can_see_jreportetrabajo','can see jreportetrabajo'),
		)
		db_table='avanceObraGrafico2_reportetrabajo'
		verbose_name = 'Reporte de Trabajo'

	def fecha_format(self):
		return self.fechaTrabajo.strftime("%Y-%m-%d") 


class KDetalleReporteTrabajo(models.Model):
	reporte_trabajo = models.ForeignKey(JReporteTrabajo,
		related_name='detallereportetrabajo_reportetrabajo_grafico',on_delete=models.PROTECT)
	nodo = models.ForeignKey(HNodo,related_name='detallereportetrabajo_nodo_grafico',on_delete=models.PROTECT)
	detallepresupuesto = models.ForeignKey(FDetallePresupuesto,related_name='detallereportetrabajo_detallepresupuesto_grafico',on_delete=models.PROTECT)
	cantidadEjecutada = models.DecimalField(max_digits=30, decimal_places=2)

	class Meta:
		permissions=(
			('can_see_kdetallereportetrabajo','can see kdetallereportetrabajo'),
		)
		db_table='avanceObraGrafico2_detallereportetrabajo'
		verbose_name = 'Detalle de Reporte de Trabajo'


class MComentarioRechazo(models.Model):
	reporte_trabajo = models.ForeignKey(JReporteTrabajo,related_name='comentariorechazo_reportetrabajo_grafico',on_delete=models.PROTECT)
	motivoRechazo = models.CharField(max_length=255,blank=True,null=True)
	fecha_hora=models.DateTimeField(auto_now_add=True)
			

	class Meta:
		permissions=(
			('can_see_comentariorechazo','can see comentariorechazo'),
		)
		db_table='avanceObraGrafico2_comentariorechazo'
		verbose_name = 'Comentario de Rechazo'


	def fecha_format(self):
		return self.fecha_hora.strftime("%Y-%m-%d") 

class LCambio(models.Model):
	presupuesto = models.ForeignKey(EPresupuesto,
		related_name='cambio_presupuesto_grafico',on_delete=models.PROTECT)
	empresaSolicitante= models.ForeignKey(Empresa,related_name='cambio_empresaSolicitante_grafico',on_delete=models.PROTECT)
	empresaTecnica= models.ForeignKey(Empresa,related_name='cambio_empresaoTecnica_grafico',on_delete=models.PROTECT,blank=True,null=True)
	empresaFinanciera= models.ForeignKey(Empresa,related_name='cambio_empresaFinanciera_grafico',on_delete=models.PROTECT,blank=True,null=True)
	estado=models.ForeignKey(Estado, on_delete=models.PROTECT,related_name="cambio_estado_grafico")
	descripcion = models.CharField(max_length=255,blank=True,null=True)
	motivo = models.CharField(max_length=255,blank=True,null=True)
	fecha_creacion=models.DateField(auto_now_add=True)

	class Meta:
		permissions=(
			('can_see_cambio','can see cambio'),
			('can_see_aprobacioncambio','can see aprobacioncambio'),
			('can_see_autorizacioncambio','can see autorizacioncambio'),
		)
		db_table='avanceObraGrafico2_cambio'
		verbose_name = 'Cambio'


class LDetalleCambio(models.Model):
	detallepresupuesto = models.ForeignKey(FDetallePresupuesto,related_name='detallecambio_detallepresupuesto_grafico',on_delete=models.PROTECT,blank=True,null=True)
	codigoUC = models.CharField(max_length=20,blank=True,null=True)
	descripcionUC = models.CharField(max_length=255,blank=True,null=True)
	valorManoObra = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	valorMaterial = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	valorGlobal = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	cambio = models.ForeignKey(LCambio,related_name='detallecambio_cambio_grafico',on_delete=models.PROTECT)
	nodo = models.ForeignKey(HNodo,related_name='detallecambio_nodo_grafico',on_delete=models.PROTECT)
	#1-agregar,2-quitar
	operacion=models.IntegerField()
	cantidadPropuesta = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	#estado=models.ForeignKey(Estado, on_delete=models.PROTECT,related_name="detallecambio_estado_grafico")
	

	class Meta:
		permissions=(
			('can_see_detallecambio','can see detallecambio'),
		)
		db_table='avanceObraGrafico2_detallecambio'
		verbose_name = 'Detalle de Cambio'


class LHistorialCambio(models.Model):
	fecha=models.DateField(auto_now_add=True)
	cambio = models.ForeignKey(LCambio,related_name='historialcambio_cambio_grafico',on_delete=models.PROTECT)
	usuario_registro = models.ForeignKey(Usuario,related_name='historialcambio_usuario_grafico',on_delete=models.PROTECT)
	estado=models.ForeignKey(Estado, on_delete=models.PROTECT,related_name="historialcambio_estado_grafico")
	motivoEstado = models.CharField(max_length=255,blank=True,null=True)		

	class Meta:
		permissions=(
			('can_see_historialcambio','can see historialcambio'),
		)
		db_table='avanceObraGrafico2_historialcambio'
		verbose_name = 'Historial del Cambio'


class LSoporteCambio(models.Model):
	cambio = models.ForeignKey(LCambio,related_name='soportecambio_cambio_grafico',on_delete=models.PROTECT)
	nombre_soporte = models.CharField(max_length=255)
	#soporte = models.FileField(upload_to=functions.path_and_rename('avanceObraGrafico/soporte_cambio','aog'),blank=True, null=True)
	soporte = models.FileField(upload_to='avanceObraGrafico_cambio_archivo',blank=True, null=True)
			

	class Meta:
		permissions=(
			('can_see_soportecambio','can see soportecambio'),
		)
		db_table='avanceObraGrafico2_soportecambio'
		verbose_name = 'Soporte del Cambio'
