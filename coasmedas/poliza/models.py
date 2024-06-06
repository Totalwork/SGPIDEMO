from django.db import models
from empresa.models import Empresa
from usuario.models import Persona
from estado.models import Estado
from tipo.models import Tipo
from contrato.models import Contrato
from parametrizacion.models import Cargo
from datetime import *
from tipo.models import Tipo
import json
from coasmedas.functions import functions, RandomFileName
from django.db.models import Q, Max, Min

# Create your models here.
	

class Aseguradora(models.Model):
	nombre=models.CharField(max_length=50)

	def __unicode__(self):
			return self.nombre
			
	class Meta:		
		db_table = 'poliza_aseguradora'
		permissions = (
			("can_see_aseguradora","can see aseguradora"),
		) 
		

class Poliza(models.Model):	
	tipo=models.ForeignKey(Tipo,blank=True, null=True, default=None,related_name="poliza_tipo_poliza",on_delete=models.PROTECT)
	contrato=models.ForeignKey(Contrato,blank=True, null=True,related_name="poliza_contrato",on_delete=models.PROTECT)		
	estado=models.ForeignKey(Estado, blank=True, null=True,related_name="poliza_estado", on_delete=models.PROTECT)		
	
	def vigencias(self):		
		return VigenciaPoliza.objects.filter(poliza__id=self.id)
	
	def fecha_inicio(self):
		# fechas=VigenciaPoliza.objects.values('fecha_inicio') \
		# 		.filter(poliza__id=self.id) \
		# 		.order_by('id')[:1]	
		# return fechas.first()['fecha_inicio'] if fechas.first() else ""
		resultado = VigenciaPoliza.objects.filter(poliza__id=self.id).aggregate(Min('fecha_inicio'))	
		fecha_inicio = resultado['fecha_inicio__min'];
		return fecha_inicio

	def fecha_final(self):

		qset = (Q(poliza__id=self.id) & Q(fecha_final__isnull=False))
		item = VigenciaPoliza.objects.filter(qset).last()
		return item.fecha_final	if item is not None else ""
		# resultado = VigenciaPoliza.objects.filter(poliza__id=self.id).aggregate(Max('fecha_final'))	
		# fecha_final = resultado['fecha_final__max']
		# return fecha_final

	def valor(self):
		query=VigenciaPoliza.objects.filter(poliza__id=self.id)	
		valor= 0
		if query.count() == 1:
			item = query.first()
			valor=item.valor
		elif query.count() > 1:	
			query2=VigenciaPoliza.objects.filter(poliza__id=self.id, reemplaza=True)				
			if query2.count() == 0:
				item = query.first()
				valor=item.valor
			elif query2.count() > 0:	
				item = query2.last()
				valor=item.valor
						
		return valor
	
	def vigencias(self):
		vigencias=VigenciaPoliza.objects.filter(poliza__id=self.id)
		
		return vigencias
	
	class Meta:		
		db_table = 'poliza'
		permissions = (
			("can_see_poliza","can see poliza"),
		)


class VigenciaPoliza(models.Model):
	poliza 				=	models.ForeignKey(Poliza,blank=True, null=True, default=None,related_name="vigencia_poliza_tipo_poliza",on_delete=models.PROTECT)
	fecha_inicio		=	models.DateField(null=True)
	fecha_final			=	models.DateField(null=True)
	valor 				=	models.DecimalField(null=True, max_digits=18, decimal_places=2)
	observacion 		=	models.TextField(null=True)
	#soporte 			=	models.FileField(upload_to='poliza/soporte',blank=True, null=True)		
	soporte 			=	models.FileField(upload_to=RandomFileName('poliza/soporte','plz'),blank=True, null=True)	
	aseguradora 		= 	models.ForeignKey(Aseguradora,blank=True, null=True, default=None,related_name="vigencia_poliza_aseguradora",on_delete=models.PROTECT)
	amparo 				= 	models.CharField(max_length=500, null=True)
	tomador 			= 	models.CharField(max_length=100, null=True)
	numero 				= 	models.CharField(max_length=200, null=True)
	reemplaza 			= 	models.BooleanField(default=False)
	documento_id 		=	models.IntegerField(null=True, blank=True)#se puede guardar una poliza o una vigencia
	tipo_acta 			=	models.ForeignKey(Tipo, blank=True, null=True, default=None,related_name="poliza_tipo_acta",on_delete=models.PROTECT)
	tipo_documento 		=	models.ForeignKey(Tipo, blank=True, null=True, default=None,related_name="poliza_tipo_documento",on_delete=models.PROTECT)	
	numero_certificado  = 	models.CharField(max_length=300, null=True, blank=True)

	def beneficiarios(self):
		return ZBeneficiorio.objects.filter(vigencia_poliza__id=self.id)

	class Meta:		
		db_table = 'poliza_vigencia_poliza'
		ordering=['id']
		permissions = (
			("can_see_vigencia_poliza","can see vigencia poliza"),
		)

class VigenciaPoliza_AprobacionMME(models.Model):
	vigencia_poliza =models.ForeignKey(VigenciaPoliza,blank=True, null=True, default=None,on_delete=models.PROTECT)
	fecha 			= models.DateField(blank=True, null=True)

	class Meta:
		db_table = 'poliza_vigencia_poliza_aprobacion_mme'
		unique_together = [
			["vigencia_poliza",],
		]

class ZBeneficiorio(models.Model):
	nombre=models.CharField(max_length=120)
	vigencia_poliza=models.ForeignKey(VigenciaPoliza,blank=True, null=True, default=None,related_name="vigencia_poliza_beneficiario",on_delete=models.PROTECT)	
	class Meta:		
		db_table = 'poliza_beneficiario_vigencia_poliza'
		permissions = (
			("can_see_vigencia_poliza_beneficiario_vigencia_poliza","can see beneficiario vigencia poliza"),
		)	