from django.db import models

# Create your models here.
class BaseModel(models.Model):
	nombre = models.CharField(max_length=50)

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.nombre
#estados de la aplicaciones 
class Estado(BaseModel):
	app = models.CharField(max_length = 250)
	color = models.CharField(max_length = 250 , blank= True)
	icono = models.CharField(max_length = 250 , blank= True)
	estado = models.BooleanField( default = 1 )
	codigo = models.IntegerField(blank= True,null=True)
	orden=models.IntegerField()

	def __unicode__(self):
		return self.app + '.' + self.nombre
	class Meta:
		unique_together = (("app" , "codigo" ),)

	def ObtenerID(self,app,codigo):
		return Estado.objects.get(app=app,codigo=codigo).id



# esta clase sirve para los posibles estado que puede pasar un unico estado
class Estados_posibles(models.Model):
										#related_name="f_MODEL_APP"
	actual = models.ForeignKey(Estado , related_name="f_Estado_estado" , on_delete=models.PROTECT)## id actual del estado
	siguiente = models.ForeignKey(Estado , related_name="f_Estado_estado_2" , on_delete=models.PROTECT)## id posible


		


