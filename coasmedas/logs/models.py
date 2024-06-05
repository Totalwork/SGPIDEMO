from django.db import models
from usuario.models import Usuario
from datetime import *
from django.utils import timezone


# Create your models here.

class Logs(models.Model):
	fecha_hora=models.DateTimeField(auto_now_add=True)
	usuario=models.ForeignKey(Usuario,related_name="logs_usuario",on_delete=models.PROTECT)
	accion=models.CharField(max_length=250)
	nombre_modelo=models.CharField(max_length=250)
	id_manipulado=models.IntegerField()

	def __unicode__(self):
		return self.nombre_modelo

#	class Meta:  
#  		 db_table = 'logs.logs'

class Acciones():
	accion_crear='Crear'
	accion_actualizar='Actualizar'
	accion_borrar='Borrar'
	

class LogsIngresoUsuario(models.Model):
	fecha_hora=models.DateTimeField(auto_now_add=True)
	usuario=models.ForeignKey(Usuario,related_name="logs_usuario_ingreso",on_delete=models.PROTECT)
	ingreso=models.IntegerField();	