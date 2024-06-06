from django.db import models
from contrato.models import Contrato
from tipo.models import Tipo
from estado.models import Estado
from empresa.models import Empresa
from giros.models import CNombreGiro
from parametrizacion.models import Banco
from django.db.models import Count
from coasmedas.functions import functions,RandomFileName



class CesionV(models.Model):

	contratista=models.ForeignKey(Empresa,related_name="cesion_V2_proveedor",on_delete=models.PROTECT)
	estado=models.ForeignKey(Estado,related_name="cesion_v2_estado",on_delete=models.PROTECT)
	fecha_carta = models.DateField(blank=True, null=True)
	#soporte_solicitud= models.FileField(upload_to = 'cesion_v2/solocitud', blank=True, null=True)
	soporte_solicitud= models.FileField(upload_to = functions.path_and_rename('cesion_v2/solicitud','solicitud'), blank=True, null=True)

	def cantidad_detalle(self):
		cantidad=DetalleCesionV.objects.filter(cesion_id=self.id).count()
		return cantidad

	def detalle_contrato(self):
		deta=DetalleCesionV.objects.filter(cesion_id=self.id).values('contrato__id','contrato__nombre','contrato__mcontrato__id','contrato__mcontrato__nombre','contrato__contratista__id','contrato__empresacontrato__empresa__id','banco__nombre','beneficiario__nombre','cesion__contratista__nombre','estado__nombre','tipo_cuenta__nombre','nombre_giro__nombre')
		return deta

	class Meta:
		db_table = "cesion_v2"
		permissions = (("can_see_CesionV2","can_see_CesionV2"),)
		verbose_name='cesion_v2' 


class DetalleCesionV(models.Model):

	contrato=models.ForeignKey(Contrato,related_name="cesion_V2_contrato",on_delete=models.PROTECT)
	cesion=models.ForeignKey(CesionV,related_name="cesion_id",on_delete=models.PROTECT)
	nombre_giro=models.ForeignKey(CNombreGiro,related_name="cesion_v2_nombre_giro",on_delete=models.PROTECT)
	beneficiario=models.ForeignKey(Empresa,related_name="cesion_V2_beneficiario",on_delete=models.PROTECT)
	banco=models.ForeignKey(Banco,related_name="cesion_v2_banco",on_delete=models.PROTECT)
	tipo_cuenta=models.ForeignKey(Tipo,related_name="cesion_v2_tipo_cuenta",on_delete=models.PROTECT)
	estado=models.ForeignKey(Estado,related_name="detallecesionv_estado",on_delete=models.PROTECT)
	numero_cuenta = models.CharField(max_length=50,null=True,blank=True)
	valor = models.FloatField()
	#correo_verificacion= models.FileField(upload_to = 'detalle_cesion/correo_verificacion', blank=True, null=True)
	correo_verificacion= models.FileField(upload_to = functions.path_and_rename('detalle_cesion/correo_verificacion','correo_verificacion'), blank=True, null=True)
	#carta_rechazo_aprobacion= models.FileField(upload_to = 'detalle_cesion/carta_rechazo_aprobacion', blank=True, null=True)
	carta_rechazo_aprobacion= models.FileField(upload_to = functions.path_and_rename('detalle_cesion/carta_rechazo_aprobacion','carta_rechazo_aprobacion'), blank=True, null=True)

	