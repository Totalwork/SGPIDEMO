from django.db import models
from empresa.models import Empresa
from tipo.models import Tipo
from parametrizacion.models import BaseModel
from sinin4.functions import functions

# Create your models here.

class Planilla(models.Model):
	empresa=models.ForeignKey(Empresa, on_delete=models.PROTECT,related_name="planilla_empresa")
	tipo=models.ForeignKey(Tipo, on_delete=models.PROTECT,related_name="planilla_tipo",null=True, blank=True)
	#archivo = models.FileField(upload_to=functions.path_and_rename('informe/informe_ministerio','im'),blank=True, null=True)
	archivo = models.FileField(upload_to='informe_ministerio',blank=True, null=True)

	class Meta:
		db_table = 'informe_planilla'		
		permissions = (
			("can_see_planilla","can see planilla"),
		)


class Tag(BaseModel):
	modelo=models.CharField(max_length=250,blank=True,null=True)
	campo=models.CharField(max_length=250,blank=True,null=True)
	planilla=models.ManyToManyField(Planilla,related_name="tag_planilla", blank=True)
	tag_especial=models.BooleanField(default=False)
	mayuscula=models.BooleanField(default=False)
	nombre_variable=models.CharField(max_length=250,blank=True,null=True)
	inner=models.TextField(blank=True,null=True)

	class Meta:
		db_table = 'informe_tag'		
		permissions = (
			("can_see_tag","can see tag"),
		)


