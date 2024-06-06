from django.db import models
from django.contrib.contenttypes.models import ContentType

from coasmedas.functions import functions, RandomFileName

from contrato.models import Contrato
from estado.models import Estado
from tipo.models import Tipo
from empresa.models import Empresa
from parametrizacion.models import Banco
from proyecto.models import Proyecto
from proceso.models import HSoporteProcesoRelacionDato

# from giros.models import DEncabezadoGiro
from seguimiento_factura.models import GestionOp

#Defino los modelos para factura.
class BaseModel(models.Model):
	referencia = models.CharField(max_length=500, blank = True)

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.referencia

class Factura(BaseModel):
	contrato 		= models.ForeignKey(Contrato, related_name='fk_factura_contrato', on_delete=models.PROTECT)
	estado			= models.ForeignKey(Estado, related_name='fk_factura_estado', on_delete=models.PROTECT)
	numero			= models.CharField(max_length=100)
	radicado		= models.CharField(max_length=500, blank = True)
	fecha			= models.DateField(blank=True, null=True)
	concepto		= models.CharField(max_length=4000)
	valor_factura	= models.FloatField()
	valor_contable	= models.FloatField(blank=True, null=True)
	valor_subtotal	= models.FloatField(blank=True, null=True)
	soporte			= models.FileField(upload_to = RandomFileName('factura/factura','fac'), blank=True, null=True)
	# soporte		= models.FileField(upload_to = 'factura/factura', blank=True, null=True)
	codigo_op 		= models.ForeignKey(GestionOp, related_name='fk_seguimiento_factura',blank=True, null=True, on_delete=models.PROTECT)
	pagada 			= models.BooleanField(default=False)
	bloqueo_factura	= models.BooleanField(default=False)
	recursos_propios= models.BooleanField(default=False)
	orden_pago		= models.BooleanField(default=False)
	fecha_reporte	= models.DateField(blank=True, null=True)
	proceso_soporte	= models.ForeignKey(HSoporteProcesoRelacionDato, blank=True, null=True, related_name='fk_factura_soporte_proceso', on_delete=models.PROTECT)
	fecha_pago		= models.DateField(blank=True, null=True)
	motivo_anulacion= models.TextField(null=True,blank=True)
	mcontrato 		= models.ForeignKey(Contrato, related_name='fk_factura_mcontrato', blank=True, null=True, on_delete=models.PROTECT)
	fecha_contabilizacion	= models.DateField(blank=True, null=True)
	fecha_vencimiento	= models.DateField(blank=True, null=True)

	# Lista los meses causados de la factura
	def mes_causado(self):
		mes_causado = MesCausado.objects.filter(factura__id=self.id)
		return mes_causado

	def proyecto(self):
		factura_proy = FacturaProyecto.objects.filter(factura__id=self.id).values('proyecto__nombre')
		return factura_proy

	# Nombre de la tabla
	class Meta:
		db_table = 'factura'
		permissions = (
			("can_see_factura","can see factura"),("can_see_deshabilitarFactura","can_see_deshabilitarFactura"),
			("can_see_habilitarFactura","can_see_habilitarFactura"),("can_see_cargaMasivaFactura","can_see_cargaMasivaFactura"),
			("can_see_facturas_por_contabilizar","can see facturas por contabilizar"),

		)

class MesCausado(models.Model):
	factura 				= models.ForeignKey(Factura, related_name='fk_mesCausado_factura', on_delete=models.PROTECT)
	mes 						= models.CharField(max_length=20)
	ano 						= models.CharField(max_length=10)

	class Meta:
		db_table = 'factura_mes_causado'

class Cesion(BaseModel):
	contrato 				= models.ForeignKey(Contrato, related_name='fk_cesion_contrato2', on_delete=models.PROTECT)
	beneficiario		= models.ForeignKey(Empresa, related_name='fk_cesion_beneficiario', on_delete=models.PROTECT)
	banco						= models.ForeignKey(Banco, blank=True, null=True, related_name='fk_cesion_banco', on_delete=models.PROTECT)
	proceso_soporte	= models.ForeignKey(HSoporteProcesoRelacionDato, blank=True, null=True, related_name='fk_cesion_soporte_proceso', on_delete=models.PROTECT)
	numero_cuenta		= models.CharField(max_length=500, blank=True, null=True)
	descripcion			= models.CharField(max_length=4000, blank=True, null=True)
	fecha						= models.DateField(blank=True, null=True)
	valor						= models.FloatField()
	tipo_cuenta			= models.ForeignKey(Tipo, blank=True, null=True, related_name="cesion_tipoCuenta", on_delete=models.PROTECT)
	soporte					= models.FileField(upload_to = RandomFileName('factura/cesion','fac_ces'), blank=True, null=True)
	# soporte					= models.FileField(upload_to = 'factura/cesion', blank=True, null=True)

	class Meta:
		db_table = 'factura_cesion'

class Descuento(BaseModel):
	contrato 				= models.ForeignKey(Contrato, related_name='fk_descuento_contrato', on_delete=models.PROTECT)
	banco						= models.ForeignKey(Banco, blank=True, null=True, related_name='fk_descuento_banco', on_delete=models.PROTECT)
	numero_cuenta		= models.CharField(max_length=500, blank=True, null=True)
	concepto				= models.CharField(max_length=4000)
	valor						= models.FloatField()
	soporte					= models.FileField(upload_to = RandomFileName('factura/descuento','fac_desc'), blank=True, null=True)
	# soporte					= models.FileField(upload_to = 'factura/descuento', blank=True, null=True)

	class Meta:
		db_table = 'factura_descuento'

class Compensacion(BaseModel):
	contrato 				= models.ForeignKey(Contrato, related_name='fk_compensacion_contrato', on_delete=models.PROTECT)
	fecha						= models.DateField()
	descripcion			= models.CharField(max_length=4000, blank=True, null=True)
	valor						= models.FloatField()

	def detalle_cruce(self):
		detalle=DetalleCompensacion.objects.filter(compensacion__id=self.id)
		return detalle

	class Meta:
		db_table = 'factura_compensacion'

class DetalleCompensacion(models.Model):
	compensacion		= models.ForeignKey(Compensacion, related_name='fk_detalleCompensacion_compensacion', on_delete=models.PROTECT)
	tablaForanea		= models.ForeignKey(ContentType, on_delete=models.PROTECT, verbose_name='Tabla foranea del DetalleCompensacion', related_name='fk_tablaForanea_detalleCompensacion')
	id_registro			= models.IntegerField()

	# def registro(self):
	# 	registro_referencia=self.tablaForanea.model.objects.get(pk=self.id_registro)
	# 	return registro_referencia

	class Meta:
		db_table = 'factura_detalle_compensacion'

class FacturaProyecto(models.Model):
	factura 				= models.ForeignKey(Factura, related_name='fk_factura_facturaProyecto', on_delete=models.PROTECT)
	proyecto 				= models.ForeignKey(Proyecto, related_name='fk_proyecto_facturaProyecto', on_delete=models.PROTECT)
	valor						= models.FloatField(blank=True, null=True)

	class Meta:
		db_table = 'factura_proyecto'

		unique_together=('factura','proyecto')

