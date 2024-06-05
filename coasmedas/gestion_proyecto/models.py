from django.db import models
from empresa.models import Empresa
from estado.models import Estado
from parametrizacion.models import BaseModel,Municipio
from sinin4.functions import functions
from usuario.models import Usuario

# Create your models here.

class AFondo(BaseModel):
	empresa=models.ForeignKey(Empresa, on_delete=models.PROTECT,related_name="fondo_empresa")
	estado=models.ForeignKey(Estado, on_delete=models.PROTECT,related_name="fondo_estado")

	class Meta:
		db_table = 'gestion_proyecto_fondo'		
		permissions = (
			("can_see_afondo","can see afondo"),
		)

class ACampana(BaseModel):
	class Meta:
		db_table = 'gestion_proyecto_campana'		
		permissions = (
			("can_see_acampana","can see acampana"),
		)

class ASolicitante(BaseModel):
	class Meta:
		db_table = 'gestion_proyecto_solicitante'		
		permissions = (
			("can_see_asolicitante","can see asolicitante"),
		)

class AUnidadMedida(BaseModel):
	class Meta:
		db_table = 'gestion_proyecto_documento_unidad_medida'

class CampanaEmpresa(models.Model):
	campana=models.ForeignKey(ACampana, on_delete=models.PROTECT,related_name="campana_estado_campana")
	empresa=models.ForeignKey(Empresa, on_delete=models.PROTECT,related_name="campana_estado_empresa")
	propietario=models.BooleanField(default=False)

	class Meta:
		db_table = 'gestion_proyecto_campana_empresa'
		permissions = (
			("can_see_campana_empresa","can see campana_empresa"),
		) 

	def __unicode__(self):
		return self.empresa.nombre


class CSolicitud(BaseModel):
	fecha=models.DateField()
	entidad=models.CharField(max_length=250,blank=True,null=True)
	visita= models.BooleanField(default=False)
	fecha_visita=models.DateField(blank=True,null=True)
	fecha_respuesta=models.DateField(blank=True,null=True)
	descripcion_visita=models.TextField(blank=True,null=True)

	@property
	def soportes(self):
		try:
			return SoporteSolicitud.objects.filter(solicitud_id=self.id)
		except Exception as e:
			print(e)

	class Meta:
		db_table = 'gestion_proyecto_solicitud'
		permissions = (
			("can_see_solicitud","can see solicitud"),
		) 


class DatoDiseno(BaseModel):
	unidad_medida=models.ForeignKey(AUnidadMedida, on_delete=models.PROTECT,related_name="dato_diseno_unidad_medida")
	orden=models.IntegerField()

	class Meta:
		db_table = 'gestion_proyecto_dato_diseno'
		permissions = (
			("can_see_datodiseno","can see datodiseno"),
		) 

class Diseno(BaseModel):
	municipio=models.ForeignKey(Municipio, on_delete=models.PROTECT,related_name="diseno_municipio")
	fondo=models.ForeignKey(AFondo, on_delete=models.PROTECT,related_name="diseno_fondo")
	solicitante=models.ForeignKey(ASolicitante, on_delete=models.PROTECT,related_name="diseno_solicitante")
	campana=models.ForeignKey(ACampana, on_delete=models.PROTECT,related_name="diseno_campana")
	propietaria=models.ForeignKey(Empresa, on_delete=models.PROTECT,related_name="diseno_empresa")
	activado= models.BooleanField(default=True)
	costo_proyecto=models.BigIntegerField()
	costo_diseno=models.BigIntegerField()
	disenadores=models.ManyToManyField(Empresa,related_name="diseno_disenadores", blank=True)
	solicitudes=models.ManyToManyField(CSolicitud,related_name="diseno_solicitudes", blank=True)

	class Meta:
		db_table = 'gestion_proyecto_diseno'		
		permissions = (
			("can_see_diseno","can see diseno"),
			("can_see_reportar_diseno","can see reportar_diseno"),
			("can_see_revision_diseno","can see revision_diseno"),
		)


	@property
	def estado(self):
		Estado=[]
		Version=DVersionesDiseno.objects.filter(diseno_id=self.id).values('id').last()
		
		if Version is not None:
			Estado=EstadoDiseno.objects.filter(diseno_id=self.id,version_diseno_id=Version['id']).values('estado__nombre','estado__id').last()
			
		return Estado


class DocumentoEstado(BaseModel):
	estado=models.ForeignKey(Estado, on_delete=models.PROTECT,related_name="documento_estado")
	campana=models.ForeignKey(ACampana, on_delete=models.PROTECT,related_name="documento_campana")

	class Meta:
		db_table = 'gestion_proyecto_documento_estado'		
		permissions = (
			("can_see_documentoestado","can see documentoestado"),
		)


class DVersionesDiseno(BaseModel):
	diseno=models.ForeignKey(Diseno, on_delete=models.PROTECT,related_name="versiones_diseno")
	fecha=models.DateField(auto_now_add=True,blank=True,null=True)
	reportar_diseno= models.BooleanField(default=False)
	estado_reporte=models.ForeignKey(Estado, on_delete=models.PROTECT,related_name="diseno_reporte",null=True, blank=True)
	reportar_satisfaccion= models.BooleanField(default=False)


	class Meta:
		db_table = 'gestion_proyecto_version_diseno'
		permissions = (
			("can_see_dversionesdiseno","can see dversionesdiseno"),
		) 

	def __unicode__(self):
		return '{0}|{1}'.format(self.diseno.nombre,self.fecha.strftime("%Y-%m-%d"))

	def fecha_format(self):
		return self.fecha.strftime("%Y-%m-%d") 


class EstadoDiseno(models.Model):
	estado=models.ForeignKey(Estado, on_delete=models.PROTECT,related_name="estado_diseno_estado")
	diseno=models.ForeignKey(Diseno, on_delete=models.PROTECT,related_name="estado_diseno")
	version_diseno=models.ForeignKey(DVersionesDiseno, on_delete=models.PROTECT,related_name="estado_version_diseno")
	fecha=models.DateField()


	class Meta:
		db_table = 'gestion_proyecto_estado_diseno'
		permissions = (
			("can_see_estado_diseno","can see estado_diseno"),
		) 

	def __unicode__(self):
		return '{0}|{1}'.format(self.estado.nombre,self.fecha.strftime("%Y-%m-%d"))


class InfoDiseno(models.Model):
	diseno=models.ForeignKey(Diseno, on_delete=models.PROTECT,related_name="informacion_diseno")
	version_diseno=models.ForeignKey(DVersionesDiseno, on_delete=models.PROTECT,related_name="informacion_version_diseno")
	dato_diseno=models.ForeignKey(DatoDiseno, on_delete=models.PROTECT,related_name="informacion_dato_diseno")
	valor=models.FloatField()

	class Meta:
		db_table = 'gestion_proyecto_info_diseno'
		permissions = (
			("can_see_info_diseno","can see info_diseno"),
		) 

	def __unicode__(self):
		return self.valor

class MapaDiseno(BaseModel):
	longitud=models.TextField()
	latitud=models.TextField()
	diseno=models.ForeignKey(Diseno, on_delete=models.PROTECT,related_name="mapa_diseno")
	version_diseno=models.ForeignKey(DVersionesDiseno, on_delete=models.PROTECT,related_name="mapa_version_diseno")

	class Meta:
		db_table = 'gestion_proyecto_mapa_diseno'
		permissions = (
			("can_see_mapa_diseno","can see mapa_diseno"),
		) 


class PermisoDiseno(models.Model):
	diseno=models.ForeignKey(Diseno, on_delete=models.PROTECT,related_name="permiso_diseno_diseno")
	empresa=models.ForeignKey(Empresa, on_delete=models.PROTECT,related_name="permiso_diseno_empresa")
	consultar=models.BooleanField(default=False)
	editar=models.BooleanField(default=False)

	class Meta:
		db_table = 'gestion_proyecto_permiso_diseno'
		permissions = (
			("can_see_permiso_diseno","can see permiso_diseno"),
		) 

	def __unicode__(self):
		return self.empresa.nombre


class SoporteEstado(BaseModel):
	estado_diseno=models.ForeignKey(EstadoDiseno, on_delete=models.PROTECT,related_name="soporte_estado_estado_diseno")
	documento_estado=models.ForeignKey(DocumentoEstado, on_delete=models.PROTECT,related_name="soporte_estado_documento_estado")
	usuario=models.ForeignKey(Usuario, on_delete=models.PROTECT,related_name="soporte_estado_usuario")
	fecha=models.DateField(auto_now_add=True,blank=True,null=True)
	#ruta = models.FileField(upload_to=functions.path_and_rename('gestion_proyecto/soporte_estado','se'),blank=True, null=True)
	ruta = models.FileField(upload_to='gestion_diseno_estado',blank=True, null=True)


	@property
	def cantidad_comentarios(self):
		try:
			return SoporteEstadoComentario.objects.filter(soporte_estado_id=self.id).count()
		except Exception as e:
			print(e)

	class Meta:
		db_table = 'gestion_proyecto_soporte_estado'


class SoporteEstadoComentario(models.Model):
	soporte_estado=models.ForeignKey(SoporteEstado, on_delete=models.PROTECT,related_name="soporte_comentario_soporte_estado")
	usuario=models.ForeignKey(Usuario, on_delete=models.PROTECT,related_name="soporte_comentario_usuario")
	comentario=models.TextField()
	fecha=models.DateTimeField(auto_now_add=True,blank=True,null=True)

	class Meta:
		db_table = 'gestion_proyecto_soporte_comentario'
		permissions = (
			("can_see_comentario_soporte","can see comentario_soporte"),
		) 

	def __unicode__(self):
		return self.comentario

	def fecha_format(self):
		return self.fecha.strftime("%Y-%m-%d %H:%M:%S") 


class SoporteSolicitud(BaseModel):
	solicitud=models.ForeignKey(CSolicitud, on_delete=models.PROTECT,related_name="soporte_solicitud_solicitud")
	usuario=models.ForeignKey(Usuario, on_delete=models.PROTECT,related_name="soporte_solicitud_usuario")
	fecha=models.DateField()
	#ruta = models.FileField(upload_to=functions.path_and_rename('gestion_proyecto/soporte_solicitud','ss'),blank=True, null=True)
	ruta = models.FileField(upload_to='gestion_diseno_solicitud',blank=True, null=True)


	class Meta:
		db_table = 'gestion_proyecto_soporte_solicitud'


class TComentarioDiseno(models.Model):
	diseno=models.ForeignKey(Diseno,related_name="comentario_diseno",on_delete=models.PROTECT)
	version_diseno=models.ForeignKey(DVersionesDiseno, on_delete=models.PROTECT,related_name="comentarios_version_diseno")
	comentario = models.TextField()
	usuario=models.ForeignKey(Usuario,related_name="comentario_diseno_usuario",on_delete=models.PROTECT)
	fecha=models.DateTimeField(auto_now_add=True,null=True,blank=True)

	class Meta:
		db_table = 'gestion_proyecto_comentario'

	def __unicode__(self):
		return self.comentario

	def fecha_format(self):
		return self.fecha.strftime("%Y-%m-%d %H:%M:%S") 







