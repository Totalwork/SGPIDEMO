from django.db import models
from empresa.models import Empresa
from contrato.models import Contrato
from parametrizacion.models import Banco
from financiero.models import FinancieroCuenta
from correspondencia.models import CorrespondenciaEnviada
from factura.models import Cesion, Compensacion
from tipo.models import Tipo
from estado.models import Estado
from django.db.models import F, FloatField, Sum
from sinin4.functions import functions, RandomFileName

class BaseModel(models.Model):
	nombre = models.CharField(max_length=50)

	class Meta:
		abstract = True


	def __unicode__(self):
		return self.nombre


class CNombreGiro(BaseModel):
	contrato=models.ForeignKey(Contrato,related_name="nombre_giro_contrato",on_delete=models.PROTECT)
	tipo=models.ForeignKey(Tipo,related_name="nombre_giro_tipo",on_delete=models.PROTECT)
	class Meta:
		db_table = "giros_nombre_giro"
		permissions = (("can_see_cnombregiro","can_see_cnombregiro"),)
		verbose_name='Nombre giros' 		


class DEncabezadoGiro(models.Model):
	nombre=models.ForeignKey(CNombreGiro,related_name="encabezado_nombre_giro",on_delete=models.PROTECT)
	contrato=models.ForeignKey(Contrato,related_name="encabezado_contrato",on_delete=models.PROTECT)
	soporte=models.FileField(upload_to=RandomFileName('giros/encabezado_giro','plz'),blank=True, null=True)
	# soporte=models.FileField(upload_to=functions.path_and_rename('giros/encabezado_giro','plz'),blank=True, null=True)
 	#soporte=models.FileField(upload_to='giros/encabezado_giro',blank=True, null=True)
	#estado = models.ForeignKey(Estado)
	referencia = models.CharField(max_length=50, blank=True)
	num_causacion = models.CharField(max_length=100, blank=True)
	fecha_conta = models.DateField(null=True,blank=True)
	disparar_flujo = models.BooleanField(default = False )
	numero_radicado = models.CharField(max_length=100, blank=True)
	pago_recurso = models.ForeignKey(Tipo,related_name="encabezado_tipo_pago",on_delete=models.PROTECT)
	comentario = models.CharField(max_length=500, blank=True)
	flujo_test = models.BooleanField(default=0)
	texto_documento_sap = models.CharField(max_length=500, blank=True)

	def suma_detalle(self):		
		sumatoria=DetalleGiro.objects.filter(encabezado_id=self.id).exclude(estado_id__in=[4,106]).aggregate(suma_detalle=Sum('valor_girar'))		
		return sumatoria['suma_detalle']

	class Meta:
		db_table = "giros_encabezado_giro"
		permissions = (("can_see_dencabezadogiro","can_see_dencabezadogiro"),("can_see_detalle","can_see_detalle"),("can_see_reporte","can_see_reporte"),("can_see_seguimiento","can_see_seguimiento"),("can_see_actualizar_tipo_pago","can_see_actualizar_tipo_pago"),("can_see_disparar_flujo","can_see_disparar_flujo"),
						# permisos sol de giros
						("can_see_sol_giros","can_see_sol_giros")
						,("can_see_registro_consulta_referencia","can_see_registro_consulta_referencia")
						,("can_see_sol_giros_sin_revisar","can_see_sol_giros_sin_revisar")
						,("can_see_sol_giros_test_op","can_see_sol_giros_test_op")
						,("can_see_sol_giros_por_pagar","can_see_sol_giros_por_pagar")
						,("can_see_sol_giros_pagos_rechazados","can_see_sol_giros_pagos_rechazados")

						)
		verbose_name='Encabezado giros'

	def __unicode__(self):
		return self.contrato.nombre + ' - ' + self.nombre.nombre 			

class DetalleGiro(models.Model):

	encabezado=models.ForeignKey(DEncabezadoGiro,related_name="detalle_encabezado_giro",on_delete=models.PROTECT)
	contratista=models.ForeignKey(Empresa,related_name="detalle_empresa",on_delete=models.PROTECT)
	banco=models.ForeignKey(Banco,related_name="detalle_banco",on_delete=models.PROTECT)
	no_cuenta = models.CharField(max_length=30)
	tipo_cuenta=models.ForeignKey(Tipo,related_name="detalle_tipo",on_delete=models.PROTECT)
	valor_girar = models.FloatField()
	#carta_autorizacion = models.IntegerField(null=True,blank=True)
	carta_autorizacion = models.ForeignKey(CorrespondenciaEnviada,related_name="FK_giros_detalle_giro_correspondencia_correspondenciaenviada",on_delete=models.PROTECT, null=True)
	estado = models.ForeignKey(Estado,related_name="detalle_estado",on_delete=models.PROTECT)
	fecha_pago = models.DateField(null=True,blank=True)
	cuenta = models.ForeignKey(FinancieroCuenta,related_name="detalle_cuenta", null=True,blank=True,on_delete=models.PROTECT)
	test_op = models.CharField(max_length=150, blank=True)
	fecha_pago_esperada = models.DateField(null=True,blank=True)
	codigo_pago = models.CharField(max_length=50,null=True,blank=True)
	#soporte_autorizacion=models.FileField(upload_to=functions.path_and_rename('giros/detalle_giro','plz'),blank=True, null=True)
	soporte_consecutivo_desabilitado = models.FileField(upload_to=RandomFileName('giros/consecutivo_desahabilitado','plz'),blank=True, null=True)
	#soporte_consecutivo_desabilitado = models.FileField(upload_to='giros/detalle_giro',blank=True, null=True)
	# soporte_autorizacion=models.FileField(upload_to='giros/consecutivo_desahabilitado',blank=True, null=True)
	cesion = models.ForeignKey(Cesion,related_name="detalle_giro_cesion", null=True, blank=True, on_delete=models.PROTECT)
	cruce = models.ForeignKey(Compensacion,related_name="detalle_giro_compensacion", null=True, blank=True, on_delete=models.PROTECT)
	fecha_transaccion_test = models.DateField(null=True,blank=True)

	class Meta:
		db_table = "giros_detalle_giro"
		permissions = (("can_see_detallegiro","can_see_detallegiro"),("can_see_autorizar","can_see_autorizar"),("can_see_desautorizar","can_see_desautorizar"),("can_see_pagar","can_see_pagar"),("can_see_reversar","can_see_reversar"),)	

class RechazoGiro(models.Model):

	detalle=models.OneToOneField(DetalleGiro,related_name="detalle_rechazo_giro",on_delete=models.PROTECT)
	fecha=models.DateField(null=True,blank=True)
	motivo=models.CharField(max_length=150,null=True,blank=True)
	atendido = models.BooleanField(default=0,blank=True)


	class Meta:
		db_table = "giros_rechazo"
		permissions = (("can_see_girosrechazo","can_see_girosrechazo"),)				
 