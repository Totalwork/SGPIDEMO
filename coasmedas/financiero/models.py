from django.db import models
from contrato.models import Contrato
from tipo.models import Tipo
from empresa.models import Empresa
from estado.models import Estado
from django.db.models import Count
from django.db.models import F, FloatField, Sum

from coasmedas.functions import functions, RandomFileName

class BaseModel(models.Model):
	nombre = models.CharField(max_length=100)

	class Meta:
		abstract = True


	def __unicode__(self):
		return self.nombre


class FinancieroCuenta(BaseModel):

	numero = models.CharField(max_length=50,null=True,blank=True)
	valor = models.FloatField()
	contrato=models.ForeignKey(Contrato,related_name="financiero_cuenta_contrato",on_delete=models.PROTECT)
	fiduciaria = models.CharField(max_length=100,null=True,blank=True)
	tipo=models.ForeignKey(Tipo,related_name="financiero_cuenta_tipo",null=True,blank=True,on_delete=models.PROTECT)
	codigo_fidecomiso = models.CharField(max_length=10,null=True,blank=True)
	codigo_fidecomiso_a = models.CharField(max_length=10,null=True,blank=True)
	nombre_fidecomiso = models.CharField(max_length=250,null=True,blank=True)
	empresa = models.ForeignKey(Empresa , related_name = 'fk_Empresa_empresa',null=True,blank=True, on_delete=models.PROTECT)
	estado 	= models.ForeignKey(Estado, on_delete=models.PROTECT)

	def cantidad_movimiento(self):
		cantidad=FinancieroCuentaMovimiento.objects.filter(cuenta_id=self.id).count()
		return cantidad

	@property
	def suma_ingreso(self):		
		valor_ingreso=FinancieroCuentaMovimiento.objects.filter(cuenta_id=self.id, tipo_id=31).aggregate(suma_ingreso=Sum('valor'))		
		return int(valor_ingreso['suma_ingreso']) if not valor_ingreso['suma_ingreso'] is None else 0

	@property	
	def suma_egreso(self):		
		valor_egreso=FinancieroCuentaMovimiento.objects.filter(cuenta_id=self.id, tipo_id=29).aggregate(suma_egreso=Sum('valor'))		
		return int(valor_egreso['suma_egreso']) if not valor_egreso['suma_egreso'] is None else 0

	@property	
	def suma_rendimiento(self):		
		# import pdb; pdb.set_trace()
		valor_rendimiento=FinancieroCuentaMovimiento.objects.filter(cuenta_id=self.id, tipo_id=32).aggregate(suma_rendimiento=Sum('valor'))		
		return int(valor_rendimiento['suma_rendimiento']) if not valor_rendimiento['suma_rendimiento'] is None else 0

	@property
	def fechaCorteMovimientos(self):
		max_date = FinancieroCuentaMovimiento.objects.filter(
			cuenta_id=self.id)

		if max_date:
			max_date = max_date.latest('fecha').fecha

			meses= ['','Enero','Febrero','Marzo','Abril','Mayo','Junio',\
			'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

			return meses[max_date.month] + ' de ' + str(max_date.year)
		else:
			return 'Sin corte'	
		
	class Meta:
		db_table = "financiero_cuenta"
		permissions = (("can_see_financierocuenta","can_see_financierocuenta"),("can_see_financieroEstado","can_see_financieroEstado"),("can_see_financieroMovimiento","can_see_financieroMovimiento"),)		


class FinancieroCuentaMovimiento(models.Model):

	cuenta=models.ForeignKey(FinancieroCuenta,related_name="financiero_cuenta_movimiento",on_delete=models.PROTECT)
	tipo=models.ForeignKey(Tipo,related_name="financiero_cuenta_movimiento",on_delete=models.PROTECT)
	valor = models.FloatField()
	descripcion = models.CharField(max_length=100,null=True,blank=True)
	fecha = models.DateField(null=True,blank=True)
	periodo_inicio = models.CharField(max_length=50,null=True,blank=True)
	periodo_final = models.CharField(max_length=50,null=True,blank=True)
	ano = models.IntegerField(null=True,blank=True)
	bloquear = models.BooleanField(default=False)

	class Meta:
		db_table = "financiero_cuenta_movimiento"
		permissions = (("can_see_financierocuentamovimiento","can_see_financierocuentamovimiento"),)	



class NExtracto(models.Model):

	cuenta=models.ForeignKey(FinancieroCuenta,related_name="financiero_cuenta_extracto",on_delete=models.PROTECT)
	mes = models.IntegerField(null=True,blank=True)
	ano = models.IntegerField(null=True,blank=True)
	soporte	= models.FileField(upload_to = RandomFileName('financiero/extracto','extracto'), blank=True, null=True)
	#soporte= models.FileField(upload_to = 'financiero/extracto', blank=True, null=True)


	class Meta:
		db_table = "financiero_cuenta_extracto"
		permissions = (("can_see_financieroextracto","can_see_financieroextracto"),)	


	def nombre_mes(self):
		meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
		
		return meses[int(self.mes)-1]




	



