from django.db import models

# Create your models here.
class Periodicidad(models.Model):
	dias = models.IntegerField(null=False,blank=False)
	descripcion = models.CharField(max_length=150,null=False,blank=False)

	class Meta:
		db_table = 'Calidad_periodicidad'	

class AIndicador(models.Model):
	nombre = models.CharField(max_length=150,null=False,blank=False)
	unidadMedida = models.CharField(max_length=10,null=False,blank=False)
	objetivoAnual = models.CharField(max_length=10,null=False,blank=False)	
	periodicidad = models.ForeignKey(Periodicidad,null=True,blank=True,related_name="IndicadorPeriodicidad",on_delete=models.PROTECT)

	def cantidad_seguimiento(self):
		cantidad=BSeguimientoIndicador.objects.filter(indicador_id=self.id).count()
		return cantidad

	def inicio_periodo(self):
		formato_fecha = "%Y-%m-%d"
		inicio=BSeguimientoIndicador.objects.filter(indicador_id=self.id).values('inicioPeriodo').exists()
		if inicio:
			inicio=BSeguimientoIndicador.objects.filter(indicador_id=self.id).values('inicioPeriodo').first()
			return inicio['inicioPeriodo']
		else:
			aux = ''
			return aux		

	def fin_periodo(self):
		fin=BSeguimientoIndicador.objects.filter(indicador_id=self.id).values('finPeriodo').exists()
		if fin:
			fin=BSeguimientoIndicador.objects.filter(indicador_id=self.id).values('finPeriodo').first()
			return fin['finPeriodo']
		else:
			return None

	class Meta:		
			db_table = 'Calidad_indicador'	
			permissions = (
				("can_see_aindicador","can see aindicador"),
			)
			verbose_name='Indicador' 

	def __unicode__(self):
		return self.nombre

class BSeguimientoIndicador(models.Model):
	indicador = models.ForeignKey(AIndicador, related_name='seguimientoIndicadorCalidad',on_delete=models.PROTECT)
	inicioPeriodo = models.DateField()
	finPeriodo = models.DateField()
	valor = models.FloatField()

	class Meta:		
			db_table = 'Calidad_seguimientoIndicador'	
			permissions = (
				("can_see_bseguimientoindicador","can see bseguimientoindicador"),
			)
			verbose_name='SeguimientoIndicador' 

	def __unicode__(self):
		return self.indicador.nombre

