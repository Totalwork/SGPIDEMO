from django.db import models
from empresa.models import Empresa
from tipo.models import Tipo
from contrato.models import Contrato
# Create your models here.
class BaseModel(models.Model):
 nombre = models.CharField(max_length=250)

 class Meta:
   abstract = True

 def __unicode__(self):
  return self.nombre

class Cuenta(BaseModel):
	numero = models.IntegerField()
	valor = models.FloatField()
	contrato = models.ForeignKey(Contrato , related_name = 'fk_Contrato_contrato' , on_delete=models.PROTECT)
	fiduciaria = models.CharField(max_length=250)
	tipo = models.ForeignKey(Tipo , related_name="f_Tipo_cuenta_tipo" , on_delete=models.PROTECT)#tipo de cuenta
	codigo_fidecomiso = models.CharField(max_length=250,  blank = True)
	codigo_fidecomiso_a = models.CharField(max_length=250 , blank = True)
	empresa = models.ForeignKey(Empresa , related_name = 'fk_Empresa_empresa' , on_delete=models.PROTECT)
	class Meta:
		unique_together = (("numero"),)

class Cuenta_movimiento(models.Model):	
	cuenta = models.ForeignKey(Cuenta , related_name="fk_Cuenta_cuenta" , on_delete=models.PROTECT)
	tipo = models.ForeignKey(Tipo , related_name="fk_Tipo_cuentamovimiento_tipo" , on_delete=models.PROTECT)#tipos de movimientos en la cuenta
	valor = models.FloatField()
	descripcion = models.CharField(max_length=250 , null = True)
	fecha = models.DateField()
	periodo_inicial = models.CharField(max_length=50 , null = True)
	periodo_final = models.CharField(max_length=50 , null = True)
	ano = models.IntegerField( null = True)





