from django.db import models
from empresa.models import Empresa
from usuario.models import Usuario,Persona
from django.contrib.contenttypes.models import ContentType
from sinin4.functions import functions, RandomFileName
# Create your models here.

class BaseModel(models.Model):
	nombre = models.CharField(max_length=200)

	class Meta:
		abstract = True
		permissions = (

			("puede_ver","puede ver"),

		) 

	def __unicode__(self):
		return self.nombre


class Departamento(BaseModel):
	iniciales = models.CharField(max_length=50)

class Municipio(BaseModel):
	departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)

class Banco(BaseModel):
	codigo_bancario = models.IntegerField()

class Cargo(BaseModel):
	empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
	firma_cartas = models.BooleanField(default=False)

	class Meta:
		permissions = (

			("can_see_cargo","can see cargo"),

		) 

class Notificacion(models.Model):
	nombre = models.CharField(max_length=150,blank=True,null=True, unique=True)	
	descripcion = models.TextField(blank=True,null=True)
	usuario_cc=models.ManyToManyField(Persona, related_name='fk_notificacion_usuario', blank=True)	
	# app = models.CharField(max_length=50,blank=True,null=True)	
	tabla_referencia = models.ForeignKey(ContentType, on_delete=models.PROTECT, 
										verbose_name='Tabla Referenciada', 
										related_name='fk_tablaReferenciaNotificacion',null=True)

	def __unicode__(self):
		return self.nombre

	class Meta:
		db_table = 'parametrizacion_notificacion'
		permissions = (
			("can_see_notificacion","can see notificacion"),
		) 
		# unique_together=['nombre',]

class EResponsabilidades(BaseModel):
	empresa = models.ForeignKey(Empresa,related_name="responsabilidades_empresa",on_delete=models.PROTECT)
	descripcion = models.TextField(blank=True,null=True)

	class Meta:
		db_table = 'parametrizacion_responsabilidad'

class Funcionario(models.Model):
	empresa = models.ForeignKey(Empresa,related_name="empresa_funcionario",on_delete=models.PROTECT)
	persona = models.ForeignKey(Persona,related_name="persona_funcionario",on_delete=models.PROTECT)
	cargo = models.ForeignKey(Cargo,related_name="cargo_funcionario",on_delete=models.PROTECT)
	iniciales = models.CharField(max_length=20,blank=True,null=True)
	notificaciones=models.ManyToManyField(Notificacion, related_name='fk_funcionario_notificacion', blank=True)
	activo=models.BooleanField(default=True)

	def __unicode__(self):
		return self.persona.nombres + ' ' + self.persona.apellidos
	responsabilidades=models.ManyToManyField(EResponsabilidades, related_name='fk_funcionario_responsabilidades')

	class Meta:
		permissions = (

			("can_see_funcionario","can see funcionario"),

		) 

class GrupoVideosTutoriales(models.Model):
	nombre 		= 	models.CharField(max_length=255)
	orden		=	models.IntegerField(default=0)	
	class Meta:
		permissions = (
			("can_see_grupo_videos_tutoriales","can see grupo videos tutoriales"),
		)

	def __unicode__(self):
			return self.nombre

class VideosTutoriales(models.Model):
	grupo 		= 	models.ForeignKey(GrupoVideosTutoriales, on_delete=models.PROTECT)
	titulo 		= 	models.CharField(max_length=255)		
	poster 		= 	models.ImageField(upload_to=RandomFileName('video_tutorial', ''), verbose_name='Poster del video', null=True, blank=True)
	video 		= 	models.FileField(upload_to=RandomFileName('video_tutorial', ''), verbose_name='Video')
	orden		=	models.IntegerField(default=0)
	class Meta:
		permissions = (
			("can_see_videos_tutoriales","can see videos tutoriales"),
		)

	@property	
	def video_publico(self):
		if self.video:			
			return functions.crearRutaTemporalArchivoS3(str(self.video), 7200)
		else:
			return None		

	@property	
	def poster_publico(self):
		if self.poster:			
			return functions.crearRutaTemporalArchivoS3(str(self.poster), 7200)
		else:
			return None		

	@property	
	def video_publico_base64(self):
		return self.video_publico.encode('base64')

	@property	
	def poster_publico_base4(self):
		return self.poster_publico.encode('base64')
