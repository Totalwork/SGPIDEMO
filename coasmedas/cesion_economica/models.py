from django.db import models
from contrato.models import Contrato
from tipo.models import Tipo
from estado.models import Estado
from empresa.models import Empresa
from giros.models import CNombreGiro
from parametrizacion.models import Banco
from django.db.models import Count
from sinin4.functions import functions, RandomFileName


class CesionEconomica(models.Model):

	contrato=models.ForeignKey(Contrato,related_name="cesion_economica_contrato",on_delete=models.PROTECT)
	proveedor=models.ForeignKey(Empresa,related_name="cesion_economica_proveedor",on_delete=models.PROTECT)
	tipo_cuenta=models.ForeignKey(Tipo,related_name="cesion_economica_tipo_cuenta",on_delete=models.PROTECT)
	estado=models.ForeignKey(Estado,related_name="cesion_economica_estado",on_delete=models.PROTECT)
	banco=models.ForeignKey(Banco,related_name="cesion_economica_banco",on_delete=models.PROTECT)
	nombre_giro=models.ForeignKey(CNombreGiro,related_name="cesion_economica_banco",on_delete=models.PROTECT)
	numero_cuenta = models.CharField(max_length=50,null=True,blank=True)
	motivo_rechazo = models.CharField(max_length=100,null=True,blank=True)
	observacion = models.CharField(max_length=100,null=True,blank=True)
	valor = models.FloatField()
	soporte_tramite	= models.FileField(upload_to = RandomFileName('cesion_economica/soporte_tramite','soporte_tramite'), blank=True, null=True)
	#soporte_tramite= models.FileField(upload_to = 'cesion_economica/soportes', blank=True, null=True)
	fecha_tramite = models.DateField(auto_now_add=True)
	soporte_enaprobacion	= models.FileField(upload_to = RandomFileName('cesion_economica/soporte_enaprobacion','soporte_enaprobacion'), blank=True, null=True)
	#soporte_enaprobacion= models.FileField(upload_to = 'cesion_economica/soportes', blank=True, null=True)
	fecha_enaprobacion = models.DateField(blank=True, null=True)
	soporte_aprobado	= models.FileField(upload_to = RandomFileName('cesion_economica/soporte_aprobado','soporte_aprobado'), blank=True, null=True)
	#soporte_aprobado= models.FileField(upload_to = 'cesion_economica/soportes', blank=True, null=True)
	fecha_aprobada = models.DateField(blank=True, null=True)
	

	class Meta:
		db_table = "cesion_economica"
		permissions = (("can_see_CesionEconomica","can_see_CesionEconomica"),)
		verbose_name='cesion_economica' 
