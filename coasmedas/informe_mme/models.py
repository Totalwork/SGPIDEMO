from django.db import models
from contrato.models import Contrato
from empresa.models import Empresa 


class InformeMME(models.Model):

	contrato = models.ForeignKey(Contrato , related_name = 'fk_informe_contrato',on_delete=models.PROTECT)
	empresa = models.ForeignKey(Empresa,related_name="fk_informe_empresa",on_delete=models.PROTECT)
	fecha = models.DateField(null=True,blank=True)
	consecutivo = models.BigIntegerField()	
	soporte= models.FileField(upload_to = 'informe_mme/soporte', blank=True, null=True)
	ano =  models.IntegerField()
	#soporte=models.FileField(upload_to=functions.path_and_rename('informe_mme/soporte','plz'),blank=True, null=True)

	class Meta:
		unique_together = [ ["empresa", "consecutivo" , "ano"],]
		db_table = "informe_mme"
		permissions = (("can_see_informemme","can_see_informemme"),)		



class InformeConsecutivo(models.Model):
	ano =  models.IntegerField()
	numero =  models.IntegerField()
	empresa = models.ForeignKey(Empresa,related_name="informeconsecutivo_empresa",on_delete=models.PROTECT)

	class Meta:
		unique_together = [ ["empresa" , "ano"],]
		permissions = (("can_see_InformeConsecutivo","can_see_InformeConsecutivo"),)