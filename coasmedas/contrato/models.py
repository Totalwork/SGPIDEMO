from django.db import models
from empresa.models import Empresa
from tipo.models import Tipo
from estado.models import Estado

from coasmedas.functions import functions, RandomFileName

from .enumeration import tipoV

from datetime import *
import calendar
from django.db.models import Q,Sum

from parametrizacion.models import Funcionario

# Create your models here.
class BaseModel(models.Model):
	nombre = models.CharField(max_length=4000)

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.nombre

class ActaAsignacionRecursos(BaseModel):
	fechafirma = models.DateField()
	soporte = models.FileField(upload_to = RandomFileName('contrato','cto'))
	# soporte = models.FileField(upload_to = 'contrato')

	class Meta:
		db_table = 'contrato_actaasignacionrecursos'

	def archivo(self):
		return """<a href="%s" >Documento</a>"""%self.soporte.url

	archivo.allow_tags = True

class Contrato(BaseModel):
	numero 				= models.CharField(max_length=100)
	tipo_contrato = models.ForeignKey(Tipo, on_delete=models.PROTECT)
	descripcion 	= models.CharField(max_length=4000)
	estado 			= models.ForeignKey(Estado, on_delete=models.PROTECT)
	contratista 	= models.ForeignKey(Empresa, related_name='fk_contratista', on_delete=models.PROTECT)
	contratante 	= models.ForeignKey(Empresa, related_name='fk_contratante', on_delete=models.PROTECT)
	mcontrato 		= models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)
	activo 			= models.BooleanField(default= True)
	fecha_acta_inicio		=models.DateField(blank=True, null=True)
	fecha_firma		=models.DateField(blank=True, null=True)
	fondo = models.ForeignKey(Tipo, on_delete=models.PROTECT, 
		related_name='fk_contrato_fondo', null=True, blank=True)
	fechaAdjudicacion = models.DateField(blank=True, null=True)
	# sub_contratista = models.ManyToManyField(Empresa, related_name='fk_sub_contratista' , null = True, blank=True)

	def empresa_contrato(self):
		empresa_con=EmpresaContrato.objects.filter(contrato__id=self.id)
		return empresa_con

	def vigencia_contrato(self):
		vigencia_con=VigenciaContrato.objects.filter(contrato__id=self.id)
		return vigencia_con


	def suma_vigencia_contrato(self):
		tipo_v=tipoV()
		suma_vigencia=VigenciaContrato.objects.filter(contrato__id=self.id,tipo_id=tipo_v.otrosi).aggregate(Sum('valor'))
		return suma_vigencia

	def fecha_inicio(self):
		tipo_v=tipoV()
		fecha_inicio = ''
		# fecha_i= ''
		# formato_fecha = "%Y-%m-%d"

		result = VigenciaContrato.objects.filter(contrato_id=self.id)

		if result:
			for vigencia in result:
				if vigencia.tipo.id == tipo_v.contrato:
					fecha_inicio = vigencia.fecha_inicio

			for vigencia in result:
				if vigencia.tipo.id == tipo_v.replanteo and vigencia.fecha_inicio:
					fecha_inicio = vigencia.fecha_inicio

			# print fecha_inicio
			# fecha_i = datetime.strptime(str(fecha_inicio), formato_fecha)

			return str(fecha_inicio)
		else:
			return None

	def fecha_fin(self):

		tipo_v=tipoV()
		fecha_fin = '' # Fecha fin vigencia de contrato, replante y otroSi
		fecha_f = ''
		fecha_f1 = ''
		fecha_f_rei = ''
		a_inicio = None
		a_reinicio = None
		formato_fecha = "%Y-%m-%d"
		cont = 0
		cont2 = 0

		result = VigenciaContrato.objects.filter(contrato_id=self.id)

		if result:
			for vigencia in result:
				if vigencia.tipo.id == tipo_v.contrato:
					fecha_fin = vigencia.fecha_fin

			for vigencia in result:
				if vigencia.tipo.id == tipo_v.replanteo and vigencia.fecha_fin:
					fecha_fin = vigencia.fecha_fin

			for vigencia in result:
				if vigencia.tipo.id == tipo_v.otrosi or vigencia.tipo.id == tipo_v.actaAmpliacion:
					if vigencia.fecha_fin:

						if fecha_fin < vigencia.fecha_fin:
							fecha_fin = vigencia.fecha_fin

			# print("FechaFinVig::",fecha_fin)
			# fecha_f1 = datetime.strptime(str(fecha_fin), formato_fecha)
			fecha_f1 = fecha_fin

			# Para sacar los dias que duro suspendidos
			for vigencia in result:

				if vigencia.tipo.id == tipo_v.actaSuspension:
					a_inicio = vigencia.fecha_inicio

				if vigencia.tipo.id == tipo_v.actaReinicio:
					a_reinicio = vigencia.fecha_inicio
					cont += 1

				if a_reinicio != None and a_inicio != None:
					# print("a_inicio",a_inicio)
					# print("a_reinicio",a_reinicio)

					a_inicio = datetime.strptime(str(a_inicio), formato_fecha)
					a_reinicio = datetime.strptime(str(a_reinicio), formato_fecha)
					
					dias = a_reinicio - a_inicio
					# print "dias:"+str(dias.days)

					if dias.days > 0:
						fecha_fin = fecha_fin + timedelta(days=dias.days)
						# print("FechaFinActas::",fecha_fin)

					a_inicio = None
					a_reinicio = None

				# fecha_f = datetime.strptime(str(fecha_fin), formato_fecha)
				fecha_f = fecha_fin

			# Para sacar la fecha fin del acta de reinicio
			if cont > 0:
				for vigencia in result:

					if vigencia.tipo.id == tipo_v.actaReinicio:
						cont2 = cont2+1
						if ((vigencia.fecha_fin) and (cont2 == cont)):
							# fecha_f_rei = datetime.strptime(str(vigencia.fecha_fin), formato_fecha)
							fecha_f_rei = vigencia.fecha_fin

			# Sacar la fecha fin mayor
			if fecha_f_rei != '':
				if fecha_f1 > fecha_f_rei:
					return fecha_f1
				else:
					return fecha_f_rei
			else:
				return fecha_f
		else:
			return None

	# ES CUANDO HAY REPLANTEO , OTRO SI 
	def valor_actual(self):
		nombre_modulo = 'Contrato.model - contrato.valor_actual'
		tipo_v=tipoV()
		valor_actual = 0

		try:
			result = VigenciaContrato.objects.filter(contrato_id=self.id)

			# suma_vigencia=VigenciaContrato.objects.filter(contrato__id=self.id,tipo_id=tipo_v.otrosi).values('contrato_id').annotate(valor_otrosi=Sum('valor')).values('valor_otrosi')
			suma_vigencia=VigenciaContrato.objects.filter(contrato__id=self.id,tipo_id=tipo_v.otrosi).aggregate(valor_otrosi=Sum('valor'))
			# print suma_vigencia['valor_otrosi']
			# print suma_vigencia

			# for val in suma_vigencia:
			# 	print val['valor_otrosi']

			if suma_vigencia:
				# print "print 1:"+str(suma_vigencia.valor_otrosi)
				if suma_vigencia['valor_otrosi'] > 0:
					valor_actual = suma_vigencia['valor_otrosi']
					# print suma_vigencia[0].valor_otrosi

			# print "vacio result_otrosi"
			result_replanteo = result.filter(tipo_id = tipo_v.replanteo)

			if result_replanteo:
				# print "lleno result_replanteo"					
				if result_replanteo[0].valor>0:
					valor_actual = int(valor_actual) + int(result_replanteo[0].valor)
				else:
					result_contrato = result.filter(tipo_id = tipo_v.contrato)

					if result_contrato:
						valor_actual = int(valor_actual) + int(result_contrato[0].valor)
			else:
				# print "vacio result_replanteo"
				result_contrato = result.filter(tipo_id = tipo_v.contrato)

				if result_contrato:
					valor_actual = int(valor_actual) + int(result_contrato[0].valor)
			return str(valor_actual)
			# return 1
			# ------------------------------------------------------------- #
			# result = VigenciaContrato.objects.filter(contrato_id=self.id)

			# result_otrosi = result.filter(tipo_id = tipo_v.otrosi)

			# if result_otrosi:
			# 	# print "lleno result_otrosi"
			# 	result_otrosi = result_otrosi.latest('id')

			# 	if result_otrosi.valor:
			# 		valor_actual = result_otrosi.valor
			# else:
			# 	# print "vacio result_otrosi"
			# 	result_replanteo = result.filter(tipo_id = tipo_v.replanteo)

			# 	if result_replanteo:
			# 		# print "lleno result_replanteo"					
			# 		if result_replanteo[0].valor>0:
			# 			valor_actual = result_replanteo[0].valor
			# 		else:
			# 			result_contrato = result.filter(tipo_id = tipo_v.contrato)

			# 			if result_contrato:
			# 				valor_actual = result_contrato[0].valor

			# 	else:
			# 		# print "vacio result_replanteo"
			# 		result_contrato = result.filter(tipo_id = tipo_v.contrato)
			# 		if result_contrato:
			# 			valor_actual = result_contrato[0].valor
			# return valor_actual

		except VigenciaContrato.DoesNotExist as e:
			functions.toLog(e,nombre_modulo)
			return valor_actual

	class Meta:
		db_table = 'contrato'
		ordering=['nombre']
		permissions = (
			("can_see_contrato","can see contrato"),
			("can_see_informe_ejcutivo", "can see informe ejcutivo"),
			("can_see_informe_interventoria_dispac","can see informe interventoria dispac")
		)

class ActaAsignacionRecursosContrato(models.Model):
	actaAsignacion = models.ForeignKey(ActaAsignacionRecursos,on_delete=models.PROTECT)
	contrato = models.ForeignKey(Contrato,on_delete=models.PROTECT)

	class Meta:
		db_table = 'contrato_actaasignacionrecursoscontrato'


class VigenciaContrato(BaseModel):
	contrato 		= models.ForeignKey(Contrato, on_delete=models.PROTECT)
	tipo 			= models.ForeignKey(Tipo, on_delete=models.PROTECT)
	fecha_inicio 	= models.DateField(blank=True, null=True)
	fecha_fin 		= models.DateField(blank=True, null=True)
	valor 			= models.FloatField()
	soporte 		= models.FileField(upload_to = RandomFileName('contrato','cto'), blank=True, null=True)
	# soporte		= models.FileField(upload_to = 'contrato', blank=True, null=True)
	acta_id			= models.IntegerField(blank=True, null=True)
	acta_compra 	= models.FileField(upload_to = RandomFileName('contrato','act_com'), blank=True, null=True)
	# acta_compra		= models.FileField(upload_to = 'contrato', blank=True, null=True)

	class Meta:
		db_table = 'contrato_vigencia'

	def archivo(self):
		return """<a href="%s" >Documento</a>"""%self.soporte.url
	archivo.allow_tags = True

class VigenciaContrato_motivo(models.Model):
	vigencia_contrato 	= models.ForeignKey(VigenciaContrato, on_delete=models.PROTECT)
	motivo 				= models.CharField(max_length=4000,null=False)

	class Meta:
		db_table = 'contrato_vigencia_motivo'
		unique_together = [
			["vigencia_contrato",],
		]

class EmpresaContrato(models.Model):
	contrato 	= models.ForeignKey(Contrato , on_delete=models.PROTECT)
	empresa 	= models.ForeignKey(Empresa, on_delete=models.PROTECT)
	participa = models.BooleanField(default= False)
	edita 		= models.BooleanField(default= False)

	class Meta:
		db_table = 'contrato_empresa'

		unique_together=('contrato','empresa')
	# siempre pide requerido 'field 1', 'field 2', 'field n', a pesar que en el serializer colocamos field 1_id (write_only=True)

class Rubro(BaseModel):
	contrato = models.ManyToManyField(Contrato, related_name='fk_contrato_rubro', blank=True)

	class Meta:
		db_table = 'contrato_rubro'

class Sub_contratista(models.Model):
	contrato = models.ForeignKey(Contrato, related_name='fk_contrato_sub_contratista', on_delete=models.PROTECT)
	empresa = models.ForeignKey(Empresa, related_name='fk_sub_contratista_empresa', on_delete=models.PROTECT)
	soporte	= models.FileField(upload_to = RandomFileName('contrato','sub_cto'), blank=True, null=True)
	# soporte	= models.FileField(upload_to = 'contrato', blank=True, null=True)

	class Meta:
		db_table = 'contrato_sub_contratista'

	def archivo(self):
		return """<a href="%s" >Documento</a>"""%self.soporte.url
	archivo.allow_tags = True

	unique_together=('contrato','empresa')

class Contrato_cesion(models.Model):
	contrato = models.ForeignKey(Contrato, related_name='fk_cesion_contrato', on_delete=models.PROTECT)
	contratista_nuevo = models.ForeignKey(Empresa, related_name='fk_cesion_contrato_empresa_nuevo', on_delete=models.PROTECT)
	contratista_antiguo = models.ForeignKey(Empresa, related_name='fk_cesion_contrato_empresa_antiguo', on_delete=models.PROTECT)
	fecha = models.DateField(blank=True, null=True)
	soporte	= models.FileField(upload_to = RandomFileName('contrato','cto_cs'), blank=True, null=True)
	# soporte	= models.FileField(upload_to = 'contrato', blank=True, null=True)

	class Meta:
		db_table = 'contrato_cesion'

	def archivo(self):
		return """<a href="%s" >Documento</a>"""%self.soporte.url
	archivo.allow_tags = True

class Cesion_economica(models.Model):
	contrato = models.ForeignKey(Contrato, related_name='fk_cesion_economica_contrato', on_delete=models.PROTECT)
	empresa = models.ForeignKey(Empresa, related_name='fk_cesion_economica_empresa', on_delete=models.PROTECT)
	fecha = models.DateField(blank=True, null=True)
	soporte	= models.FileField(upload_to = RandomFileName('contrato','cs_ecm'), blank=True, null=True)
	# soporte	= models.FileField(upload_to = 'contrato', blank=True, null=True)

	class Meta:
		db_table = 'contrato_cesion_economica'
		unique_together=('contrato','empresa')

	def archivo(self):
		return """<a href="%s" >Documento</a>"""%self.soporte.url
	archivo.allow_tags = True


class Contrato_CDP(models.Model):
	contrato 		= models.ForeignKey(Contrato, on_delete=models.PROTECT)
	fecha 			= models.DateField(blank=True, null=True)
	numero			= models.CharField(max_length=50)

	class Meta:
		db_table = 'contrato_cdp'

class Contrato_Financiacion(models.Model):
	contrato 		= models.ForeignKey(Contrato, on_delete=models.PROTECT,null=False)
	empresa			= models.ForeignKey(Empresa, on_delete=models.PROTECT,null=False)
	valor			= models.IntegerField(null=False)
	fecha_suscripcion = models.DateField(null=False)
	es_cofinanciacion = models.BooleanField(default=False)
	tipo 			= models.ForeignKey(Tipo, on_delete=models.PROTECT,null=True,blank=True)
	class Meta:
		db_table = 'contrato_financiacion'
		

class Contrato_financiacion_condicion(models.Model):
	financiacion 		= models.ForeignKey(Contrato_Financiacion, on_delete=models.PROTECT,null=False)
	condicion			= models.CharField(max_length=4000,null=False)
	fecha_suscripcion	= models.DateField(null=False)

	class Meta:
		db_table = 'contrato_financiacion_condicion'		

class Contrato_Vigencia_anual(models.Model):
	contrato 		= models.ForeignKey(Contrato, on_delete=models.PROTECT)
	ano 			= models.IntegerField()
	porcentaje		= models.FloatField()

	class Meta:
		db_table = 'contrato_vigencia_anual'
	
class Contrato_Desembolso(models.Model):
	vigencia_anual		= models.ForeignKey(Contrato_Vigencia_anual, on_delete=models.PROTECT)
	requisito			= models.CharField(max_length=250,null=False)
	porcentaje			= models.FloatField()
	valor_requerido		= models.FloatField()

	class Meta:
		db_table = 'contrato_desembolso'

class Contrato_Desembolso_desembolsados(models.Model):
	desembolso			= models.ForeignKey(Contrato_Desembolso, on_delete=models.PROTECT)
	valor_desembolsado	= models.FloatField()
	fecha_suscripcion	= models.DateField(null=False)

	class Meta:
		db_table = 'contrato_desembolso_desembolsado'


class Contrato_Remuneracion(models.Model):
	contrato 			= models.ForeignKey(Contrato, on_delete=models.PROTECT)
	requisito			= models.CharField(max_length=250,null=False)
	porcentaje			= models.FloatField()
	valor_requerido		= models.FloatField()

	class Meta:
		db_table = 'contrato_remuneracion'

class Contrato_Remuneracion_pagos(models.Model):
	remuneracion		= models.ForeignKey(Contrato_Remuneracion, on_delete=models.PROTECT)
	valor_pagado		= models.FloatField()
	fecha_suscripcion	= models.DateField(null=False)

	class Meta:
		db_table = 'contrato_remuneracion_pagos'


class Actividad(models.Model):
	nombre 				= models.CharField(max_length=250,null=False)

	class Meta:
		db_table = 'contrato_actividad'


class Contrato_Actividad(models.Model):
	contrato 		= models.ForeignKey(Contrato, on_delete=models.PROTECT)
	actividad 		= models.ForeignKey(Actividad, on_delete=models.PROTECT)
	valor 			= models.CharField(max_length=4000,null=False)

	class Meta:
		db_table = 'contrato_actividad_contrato'
		unique_together=('contrato','actividad')

class Contrato_Administracion(models.Model):
	contrato 		= models.ForeignKey(Contrato, on_delete=models.PROTECT)

	class Meta:
		db_table = 'contrato_administracion'
		unique_together = [
			["contrato",],
		]

ListaCargo = (
	(1, 'Principal'),
	(2, 'Apoyo')
)

class Contrato_supervisor(models.Model):
	contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT)
	funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT)
	empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
	cargo = models.IntegerField(choices=ListaCargo, default = 1)

	class Meta:
		db_table = 'contrato_supervisor'
		unique_together = [
			["contrato","empresa","cargo"],
		]

