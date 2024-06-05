from django.db import models
from contrato.models import Contrato
from proyecto.models import Proyecto
from tipo.models import Tipo
from django.db.models import Count
from sinin4.functions import functions, RandomFileName


class BaseModel(models.Model):
	nombre = models.CharField(max_length=50)

	class Meta:
		abstract = True


	def __unicode__(self):
		return self.nombre


class ACategoria(models.Model):
	proyecto=models.ForeignKey(Proyecto,related_name="administradorFotosProyecto",on_delete=models.PROTECT)
	categoria = models.CharField(max_length=500,null=True,blank=True)
	contrato=models.ForeignKey(Contrato,related_name="administrador_fotos_contrato",on_delete=models.PROTECT)

	class Meta:
		db_table = "administrador_categoria"
		permissions = (("can_see_AdministradorCategoria","can_see_AdministradorCategoria"),("can_see_ActividadesContratista","can_see_ActividadesContratista"),("can_see_Subcategoria","can_see_Subcategoria"),)
		verbose_name='Categoria' 

	def __unicode__(self):
		return self.categoria				


class BSubcategoria(models.Model):
	categoria=models.ForeignKey(ACategoria,related_name="administrador_fotos_categoria",on_delete=models.PROTECT)
	titulo = models.CharField(max_length=300,null=True,blank=True)
	contenido = models.TextField(null=True,blank=True)
	proyecto=models.ForeignKey(Proyecto,related_name="administrador_fotos_proyecto",on_delete=models.PROTECT)

	def cantidad_fotos_subcategoria(self):
		cantidad=DFotosSubcategoria.objects.filter(subcategoria_id=self.id).count()
		return cantidad
	
	class Meta:
		db_table = "administrador_subcategoria"
		permissions = (("can_see_AdministradorSubcategoria","can_see_AdministradorSubcategoria"),("can_see_FotoSubcategoria","can_see_FotoSubcategoria"),)
		verbose_name='Subcategoria'


	def __unicode__(self):
		return self.titulo				
	


class CFotosProyecto(models.Model):

	proyecto=models.ForeignKey(Proyecto,related_name="administradorFotos_proyecto",on_delete=models.PROTECT)
	fecha = models.DateField(null=True,blank=True)
	#ruta=models.FileField(upload_to=functions.path_and_rename('administrador_fotos/fotos_proyecto','plz'),blank=True, null=True)
	ruta  = models.FileField(upload_to=RandomFileName('administrador_fotos/fotos_proyecto'), blank=True, null=True, verbose_name='Ruta') 
	comentarios = models.TextField(null=True,blank=True)
	asociado_reporte = models.BooleanField(default=False)
	tipo=models.ForeignKey(Tipo,related_name="administrador_fotos_tipo",null=True,blank=True,on_delete=models.PROTECT)
	
	class Meta:
		db_table = "administrador_fotos_proyecto"
		permissions = (("can_see_AdministradorFotosProyecto","can_see_AdministradorFotosProyecto"),("can_see_fotosProyecto","can_see_fotosProyecto"),)
		verbose_name='Fotos proyectos'

	@property	
	def ruta_publica(self):
		if self.ruta:			
			return functions.crearRutaTemporalArchivoS3(str(self.ruta))
		else:
			return None	



class DFotosSubcategoria(models.Model):
	subcategoria=models.ForeignKey(BSubcategoria,related_name="administrador_fotos_subcategoria",on_delete=models.PROTECT)
	ruta=models.FileField(upload_to=RandomFileName('administrador_fotos/subcategoria_fotos','plz'),blank=True, null=True)
	#fecha = models.DateField(null=True,blank=True)
	mes = models.IntegerField(null=True,blank=True,default=0)
	ano = models.IntegerField(null=True,blank=True,default=0)

	def cantidad_fotosSubcategoria(self):
		cantidad=DFotosSubcategoria.objects.filter(subcategoria_id=self.subcategoria.id,mes=self.mes).count()
		return cantidad
		
	class Meta:
		db_table = "administrador_fotos_subcategoria"
		permissions = (("can_see_AdministradorFotosSubcategoria","can_see_AdministradorFotosSubcategoria"),)
		verbose_name='Fotos subcategoria' 							




	



