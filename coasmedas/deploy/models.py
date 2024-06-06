from django.db import models
from coasmedas.functions import functions, RandomFileName

class NombreArchivo(models.Model):
	nombre = models.CharField(max_length=150)		
	class Meta:
		db_table = 'deploy_nombre_archivo'

	def __unicode__(self):
		return self.nombre	

class SistemaVersion(models.Model):
	version = models.CharField(max_length=100, unique=True )	
	fecha = models.DateTimeField(auto_now_add=True, blank=True)
	activo = models.BooleanField(default=False)
	class Meta:
		db_table = 'deploy_sistema_version'

	def __unicode__(self):
		return self.version	

class ZInformacionArchivos(models.Model):
	archivo = models.FileField(upload_to=RandomFileName('deploy'), blank=True, null=True)
	# archivo = models.FileField(upload_to='deploy', blank=True, null=True)
	nombre_archivo = models.ForeignKey(NombreArchivo, related_name='fk_sistema_version_nombre_archivo',blank=True, null=True, on_delete=models.PROTECT)
	descripcion = models.TextField(null=True, blank=True)
	sistema_version = models.ForeignKey(SistemaVersion, related_name='fk_sistema_version_informacion_archivo',blank=True, null=True, on_delete=models.PROTECT)	

	class Meta:
		db_table = 'deploy_informacion_archivos'		