from django.db import models
from tipo.models import Tipo
from estado.models import Estado
from coasmedas.functions import functions, RandomFileName

# Create your models here.
class Empresa(models.Model):
	nit = models.CharField(max_length=255, unique=True)
	nombre = models.CharField(max_length=255)
	direccion = models.CharField(max_length=255)
	logo = models.ImageField(upload_to=RandomFileName('empresa/soporte','logo'),blank=True, null=True, default='empresa/default.jpg')
	# logo = models.ImageField(upload_to=functions.path_and_rename('empresa/soporte','logo'),blank=True, null=True, default='empresa/default.jpg')
	# logo = models.ImageField(upload_to='empresa',blank=True, null=True, default='empresa/default.jpg')
	esDisenador = models.BooleanField(default=False)
	esProveedor = models.BooleanField(default=False)
	esContratista = models.BooleanField(default=False)
	esContratante = models.BooleanField(default=False)

	# AGREGADO POR LUIS ALBERTO MENDOZA
	encabezado = models.ImageField(upload_to=RandomFileName('empresa/soporte','enca'),blank=True, null=True, default='empresa/default.jpg')
	piePagina = models.ImageField(upload_to=RandomFileName('empresa/soporte','pie'),blank=True, null=True, default='empresa/default.jpg')
	marcaAgua = models.ImageField(upload_to=RandomFileName('empresa/soporte','agua'),blank=True, null=True, default='empresa/default.jpg')
	# encabezado = models.ImageField(upload_to=functions.path_and_rename('empresa/soporte','enca'),blank=True, null=True, default='empresa/default.jpg')
	# piePagina = models.ImageField(upload_to=functions.path_and_rename('empresa/soporte','pie'),blank=True, null=True, default='empresa/default.jpg')
	# marcaAgua = models.ImageField(upload_to=functions.path_and_rename('empresa/soporte','agua'),blank=True, null=True, default='empresa/default.jpg')
	# encabezado = models.ImageField(upload_to='empresa',blank=True, null=True, default='empresa/default.jpg')
	# piePagina = models.ImageField(upload_to='empresa',blank=True, null=True, default='empresa/default.jpg')
	# marcaAgua = models.ImageField(upload_to='empresa',blank=True, null=True, default='empresa/default.jpg')
	peso = models.FloatField(blank=True , null=True)
	consecutivoDigitado =  models.BooleanField(default=False)

	abreviatura = models.CharField(blank=True, null=True,max_length=255)
	control_pago_factura 					= models.BooleanField(default=False)
	codigo_acreedor = models.IntegerField(null=True,blank=True)

	# correspondencia
	tipo_letra = models.CharField(max_length=255 ,blank=True)

	tam_letra_consecutivo = models.IntegerField(null=True)
	tam_letra_iniciales = models.IntegerField(null=True)
	tam_letra_elaboro = models.IntegerField(null=True)
	tam_letra_referencia = models.IntegerField(null=True)
	tam_letra_contenido = models.IntegerField(null=True)
  
	class Meta:
		ordering=['nombre']
		permissions = (

			("can_see","can see"),

		) 
	
	def logo_empresa(self):
		return """<img width="150px" height="60px" src="%s" alt="logo de la empresa">""" % self.logo.url

	logo_empresa.allow_tags=True

	def __unicode__(self):
		return self.nombre


class EmpresaAcceso(models.Model):
	empresa = models.ForeignKey(Empresa, related_name="fk_EmpresaAcceso_empresa",on_delete=models.PROTECT)
	# id de la empresa que se puede ver
	empresa_ver = models.ForeignKey(Empresa, related_name="fk_EmpresaAcceso_empresa_ver",on_delete=models.PROTECT)

	class Meta:	
		unique_together = (("empresa","empresa_ver"),)

class EmpresaContratante(models.Model):
	empresa = models.ForeignKey(Empresa, related_name="fk_EmpresaContratante_empresa",on_delete=models.PROTECT)
	# id de la empresa que se puede ver
	empresa_ver = models.ForeignKey(Empresa, related_name="fk_EmpresaContratante_empresa_ver",on_delete=models.PROTECT)

	class Meta:
		db_table = 'empresa_contratante'
		unique_together = (("empresa","empresa_ver"),)


class EmpresaCuenta(models.Model):
	empresa = models.ForeignKey(Empresa, related_name="fk_EmpresaCuenta_empresa",on_delete=models.PROTECT)
	tipo_cuenta=models.ForeignKey(Tipo,related_name="tipo_cuenta_empresa",null=True,blank=True,on_delete=models.PROTECT)
	entidad_bancaria = models.CharField(max_length=255,blank=True)
	numero_cuenta = models.CharField(max_length=255,blank=True)
	estado 	= models.ForeignKey(Estado,related_name="fk_EmpresaCuenta_estado", on_delete=models.PROTECT)


	class Meta:
		db_table = "empresa_cuenta"
		permissions = (("can_see_empresa_cuenta","can_see_empresa_cuenta"),("can_see_empresa_cuentaEstado","can_see_empresa_cuentaEstado"),)		