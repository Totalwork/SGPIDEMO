from django.db import models
from proyecto.models import Proyecto
from contrato.models import Contrato
from usuario.models import Usuario
from tipo.models import Tipo
from empresa.models import Empresa
from datetime import *
from django.utils import * 
# from coasmedas.functions import functions, RandomFileName
from colorfield.fields import ColorField
from estado.models import Estado
from django.db.models import Sum
# Create your models here.


class BaseModel(models.Model):
	nombre = models.CharField(max_length=255)

	class Meta:
	 	abstract = True
	 	#permission = ('puede_ver','puede_ver')


	def __str__(self):
		return self.nombre


class APeriodicidadG(BaseModel):
	numero_dias=models.IntegerField()

	class Meta:
		db_table = 'avanceObraLite_periodicidad'
		permissions = (
			("can_see_periodicidadlite","can see periodicidadlite"),
		)
		unique_together = [
			["nombre",],
		]
		verbose_name='Periodicidad' 

# -----------------------------------------------------------------------------------
### Esquemas de histos / actividades
# --------------------------------------------
class BEsquemaCapitulosG(BaseModel):
	macrocontrato=models.ForeignKey(Contrato,related_name="esquema_macrocontrato",on_delete=models.PROTECT)

	class Meta:
		db_table = 'avanceObraLite_esquemaCapitulos'
		permissions = (
			("can_see_esquemacapituloslite","can see esquemacapituloslite"),
		)
		verbose_name='Esquemas'


class CEsquemaCapitulosActividadesG(BaseModel):
	esquema=models.ForeignKey(BEsquemaCapitulosG,related_name="actividades_esquemalite",on_delete=models.PROTECT)
	nivel=models.IntegerField()
	padre = models.IntegerField()
	peso = models.FloatField()

	class Meta:
		db_table = 'avanceObraLite_esquemaCapitulosActividades'
		permissions = (
			("can_see_esquemacapitulosactividadeslite","can see esquemacapitulosactividadeslite"),
		)
		verbose_name='Capitulos y actividades'

# -----------------------------------------------------------------------------------
### Administrador de catalogos
# --------------------------------------------
class CatalogoUnidadConstructiva (models.Model):
	nombre = models.CharField(max_length=200)
	ano = models.IntegerField()
	activo = models.BooleanField(default=True)	
	mcontrato = models.ForeignKey(Contrato,related_name="catalogo_mcontrato",null=True, blank=True, on_delete=models.PROTECT)

	def __str__(self):
		return self.nombre

	class Meta:
		permissions=(
			("can_see_catalogo","can see catalogo"),
		)		
		db_table = 'avanceObraLite_catalogo'
		verbose_name = 'Catalogo de Unidades Constructivas'

class TipoUnidadConstructiva (models.Model):
	nombre = models.CharField(max_length=200)
	activa = models.BooleanField(default=True)

	def __str__(self):
		return self.nombre

	class Meta:
		db_table = 'avanceObraLite_tipounidadconstructiva'
		verbose_name = 'Tipo de unidad constructiva'



class UnidadConstructiva (models.Model):
	catalogo = models.ForeignKey(CatalogoUnidadConstructiva,
		related_name='unidadConstructiva_catalogo',on_delete=models.PROTECT)
	tipoUnidadConstructiva = models.ForeignKey(TipoUnidadConstructiva,
		related_name='unidadConstructiva_tipo',on_delete=models.PROTECT)
	codigo = models.CharField(max_length=20)
	descripcion = models.CharField(max_length=200)

	def __str__(self):
		return self.descripcion

	class Meta:
		db_table = 'avanceObraLite_unidadconstructiva'
		verbose_name = 'Unidad constructiva'

class Material (models.Model):
	catalogo = models.ForeignKey(CatalogoUnidadConstructiva,related_name='Material_catalogo',on_delete=models.PROTECT)
	codigo = models.CharField(max_length=20)
	descripcion = models.CharField(max_length=200)
	valorUnitario = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	unidadMedida = models.CharField(max_length=10, default='Und')

	def __str__(self):
		return self.descripcion

	class Meta:
		db_table = 'avanceObraLite_material'
		verbose_name = 'Material'

class DesgloceMaterial (models.Model):
	unidadConstructiva = models.ForeignKey(UnidadConstructiva,
		related_name='desgloceMaterial_unidadConstructiva',on_delete=models.PROTECT)
	material = models.ForeignKey(Material,
		related_name='desgloceMaterial_material',on_delete=models.PROTECT)
	cantidad = models.DecimalField(max_digits=30,decimal_places=4)

	def __str__(self):
		return self.unidadConstructiva.nombre + '->' + \
		self.material.descripcion

	class Meta:
		db_table = 'avanceObraLite_desglocematerial'
		verbose_name = 'Desgloce de material'

class ManoDeObra (models.Model):
	catalogo = models.ForeignKey(CatalogoUnidadConstructiva,related_name='ManoDeObra_catalogo',on_delete=models.PROTECT)
	codigo = models.CharField(max_length=20)
	descripcion = models.CharField(max_length=200)
	valorHora = models.DecimalField(max_digits=30, decimal_places=2)

	def __str__(self):
		return self.descripcion

	class Meta:
		db_table = 'avanceObraLite_manodeobra'
		verbose_name = 'Mano de obra'

class DesgloceManoDeObra (models.Model):
	unidadConstructiva = models.ForeignKey(UnidadConstructiva,
		related_name='desgloceManoDeObra_unidadConstructiva',on_delete=models.PROTECT)
	manoDeObra =  models.ForeignKey(ManoDeObra,
		related_name='desgloceManoDeObra_manoDeObra',on_delete=models.PROTECT)
	rendimiento = models.DecimalField(max_digits=30,decimal_places=4)

	def __str__(self):
		return self.unidadConstructiva.nombre + '->' + \
		self.manoDeObra.descripcion

	class Meta:
		db_table = 'avanceObraLite_desglocemanodeobra'
		verbose_name = 'Desgloce de mano de obra'


# -----------------------------------------------------------------------------------
class Cronograma(BaseModel):
	proyecto = models.ForeignKey(Proyecto,related_name='cronograma_proyecto_lite',on_delete=models.PROTECT)
	programacionCerrada=models.BooleanField(default=False)
	periodicidad = models.ForeignKey(APeriodicidadG,related_name='cronograma_perioridicidad_lite',on_delete=models.PROTECT)	
	esquema=models.ForeignKey(BEsquemaCapitulosG,related_name="cronograma_esquema_lite",on_delete=models.PROTECT)
	fechaInicio = models.DateField(null=True,blank=True)
	fechaFinal = models.DateField(null=True,blank=True)	
	confirmarFechas = models.BooleanField(default=False)

	class Meta:
		permissions=(
			('can_see_cronograma','can see cronograma'),
		)		
		db_table='avanceObraLite_cronograma'
		verbose_name='Cronograma'





# -----------------------------------------------------------------------------------
### Presupuesto
# --------------------------------------------

class EPresupuesto(BaseModel):
	cronograma = models.ForeignKey(Cronograma, related_name='presupuesto_cronograma_lite',on_delete=models.PROTECT)
	cerrar_presupuesto=models.BooleanField(default=False)
	aiu=models.FloatField()

	class Meta:
		db_table='avanceObraLite_presupuesto'
		permissions=(
			("can_see_presupuesto","can see presupuesto"),
		)
		verbose_name='Encabezado de presupuesto'

	def __str__(self):
		return self.nombre

	
	def suma_presupuesto(self):
		sumatoria=0
		suma=FDetallePresupuesto.objects.filter(presupuesto_id=self.id)	
		
		for item in suma:			
			total=float(item.valorGlobal)*float(item.cantidad)

			sumatoria=sumatoria+total

		return round(sumatoria,3)

class FDetallePresupuesto(models.Model):
	presupuesto = models.ForeignKey(EPresupuesto,related_name='detallePresupuesto_presupuesto_lite',on_delete=models.PROTECT)
	actividad = models.ForeignKey(CEsquemaCapitulosActividadesG,
		related_name='detallePresupuesto_esquemacpitulosactividades_lite',on_delete=models.PROTECT)
	codigoUC = models.CharField(max_length=20,blank=True,null=True)
	descripcionUC = models.CharField(max_length=255,blank=True,null=True)
	valorManoObra = models.DecimalField(max_digits=30, decimal_places=4,blank=True,null=True)
	valorMaterial = models.DecimalField(max_digits=30, decimal_places=4,blank=True,null=True)
	valorGlobal = models.DecimalField(max_digits=30, decimal_places=4,blank=True,null=True)
	cantidad = models.DecimalField(max_digits=30, decimal_places=4,blank=True,null=True)
	porcentaje = models.DecimalField(max_digits=30, decimal_places=2,blank=True,null=True)
	catalogoUnidadConstructiva = models.ForeignKey(CatalogoUnidadConstructiva,
		related_name='detallePresupuesto_catalogoUnidadConstructiva',
		on_delete=models.PROTECT)

	class Meta:
		db_table='avanceObraLite_detallePresupuesto'
		permissions=(
			('can_see_detallepresupuesto','can see detallepresupuesto'),
		)
		verbose_name = 'detalle de presupuesto'


	def nombre_padre(self):
		padre=CEsquemaCapitulosActividadesG.objects.get(pk=self.actividad.padre)
		return padre.nombre	

	
	def suma_presupuesto(self):
		sumatoria=0
		suma=FDetallePresupuesto.objects.filter(presupuesto_id=self.presupuesto.id)	
		
		for item in suma:			
			total=float(item.valorGlobal)*float(item.cantidad)

			sumatoria=sumatoria+total

		return round(sumatoria,3)

	
	def peso(self):
		# import pdb; pdb.set_trace()
		aiu = self.presupuesto.aiu	
		cant_ejecutada = DetalleReporteTrabajo.objects.filter(detallePresupuesto_id=self.id).aggregate(Sum('cantidad'))
		if cant_ejecutada['cantidad__sum']:
			subtotal= float(cant_ejecutada['cantidad__sum'])*float(self.valorGlobal)
			valor_aiu =float(subtotal)*float(aiu)	

			return float(float(valor_aiu)/float(self.suma_presupuesto()*aiu))
		else:
			return 0

	def __str__(self):
		return self.presupuesto.nombre + ' >> ' + self.actividad.nombre


# -----------------------------------------------------------------------------------
### Programacion
# --------------------------------------------
class PeriodoProgramacion(models.Model):
	cronograma = models.ForeignKey(Cronograma,related_name='periodoProgramacion_cronograma',on_delete=models.PROTECT)
	fechaDesde = models.DateField(null=True,blank=True)
	fechaHasta = models.DateField(null=True,blank=True)	

	class Meta:
		db_table='avanceObraLite_periodoProgramacion'
		verbose_name='ProgramacionPeriodo'
		permissions=(
			('can_see_periodoProgramacionPeriodo','can see periodoProgramacion'),
		)	

	def __str__(self):
		return self.cronograma.nombre + ' (' + str(self.fechaDesde) + '-' + str(self.fechaHasta) +' )'

class DetallePeriodoProgramacion(models.Model):
	periodoProgramacion = models.ForeignKey(PeriodoProgramacion,related_name='detallePeriodoProgramacion_periodoProgramacion',on_delete=models.PROTECT)
	detallePresupuesto = models.ForeignKey(FDetallePresupuesto,related_name='detallePeriodoProgramacion_detallePresupuesto',on_delete=models.PROTECT)
	cantidad = models.DecimalField(max_digits=30, decimal_places=4,blank=True,null=True)	

	class Meta:
		db_table='avanceObraLite_detallePeriodoProgramacion'
		verbose_name='DetallePeriodoProgramacion'
		permissions=(
			('can_see_detallePeriodoProgramacion','can see detallePeriodoProgramacion'),
		)	



# -----------------------------------------------------------------------------------
### Reporte de trabajo
# --------------------------------------------

class ReporteTrabajo(models.Model):
	periodoProgramacion = models.ForeignKey(PeriodoProgramacion,related_name='reporteTrabajo_periodoProgramacion',on_delete=models.PROTECT)
	fechaReporte = models.DateField(null=False,blank=False)	
	sinAvance = models.BooleanField(default=False)
	motivoSinAvance = models.CharField(max_length=255,blank=True,null=True)
	usuario_registro = models.ForeignKey(Usuario,related_name='reportetrabajo_usuario_lite',on_delete=models.PROTECT)
	# usuario_aprueba= models.ForeignKey(Usuario,related_name='reportetrabajo_usuarioaprueba_lite',on_delete=models.PROTECT,blank=True,null=True)
	reporteCerrado=models.BooleanField(default=False)

	class Meta:
		db_table='avanceObraLite_reporteTrabajo'
		verbose_name='ReporteTrabajo'
		permissions=(
			('can_see_reporteTrabajo','can see reporteTrabajo'),
		)	

class DetalleReporteTrabajo(models.Model):
	reporteTrabajo = models.ForeignKey(ReporteTrabajo,related_name='detalleReporteTrabajo_reporteTrabajo',on_delete=models.PROTECT)
	detallePresupuesto = models.ForeignKey(FDetallePresupuesto,related_name='detalleReporteTrabajo_detallePresupuesto',on_delete=models.PROTECT)
	cantidad = models.DecimalField(max_digits=30, decimal_places=4,blank=True,null=True)

	class Meta:
		db_table='avanceObraLite_detalleReporteTrabajo'
		verbose_name='DetalleReporteTrabajo'
		permissions=(
			('can_see_detalleReporteTrabajo','can see detalleReporteTrabajo'),
		)	

	def peso(self):
		aiu = self.detallePresupuesto.presupuesto.aiu
		if self.cantidad:
			subtotal= float(self.cantidad)*float(self.detallePresupuesto.valorGlobal)
			valor_aiu =float(subtotal)*float(aiu)	

			return float(float(valor_aiu)/float(self.detallePresupuesto.suma_presupuesto()*aiu))
		else:
			return 0

	def subtotal(self):
		if self.cantidad:
			return float(self.cantidad)*float(self.detallePresupuesto.valorGlobal)
		else:
			0