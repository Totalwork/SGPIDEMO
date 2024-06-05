from django.db import models

# Create your models here.
class BaseModel(models.Model):
	nombre = models.CharField(max_length=200)

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.nombre

#estados de la aplicaciones 
class Tipo(BaseModel):
	app = models.CharField(max_length = 250)
	color = models.CharField(max_length = 250 , blank=True)
	codigo = models.IntegerField(blank= True,null=True)
	icono = models.CharField(max_length = 200 , blank=True)
	
	def __unicode__(self):
		return self.app + '.' + self.nombre
	class Meta:
		unique_together = (("app" , "codigo" ),)

	def ObtenerID(self,app,codigo):
		return Tipo.objects.get(app=app,codigo=codigo).id

		
# esta clase sirve para los posibles tipo que puede pasar un unico Tipo
class Tipos_posibles(models.Model):
									#related_name="f_MODEL_APP"
	actual = models.ForeignKey(Tipo , related_name="f_Tipo_tipo" , on_delete=models.PROTECT)## id actual del tipo
	siguiente = models.ForeignKey(Tipo , related_name="f_Tipo_tipo_2" , on_delete=models.PROTECT)## id posible

