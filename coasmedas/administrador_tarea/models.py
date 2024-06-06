from django.db import models
from tipo.models import Tipo
from estado.models import Estado
from usuario.models import Usuario
from proyecto.models import Proyecto
from .enumeration import TipoT, EstadoT
from django.db.models import Q
from coasmedas.functions import functions, RandomFileName

# Create your models here.


class AEquipo(models.Model):
	nombre=models.TextField()
	descripcion=models.TextField()
	usuario_responsable=models.ForeignKey(Usuario, on_delete=models.PROTECT,related_name="equipo_usuario_responsable",blank=True, null=True)
	usuario_administrador=models.ForeignKey(Usuario, on_delete=models.PROTECT,related_name="equipo_usuario_administrador",blank=True, null=True)

	
	@property
	def cantidadTareas(self):
		tareas=DTarea.objects.filter(colaborador_actual__equipo_id=self.id)
		numero=0
		tipoT=TipoT()
		estadoT=EstadoT()

		for item in tareas:
			asignacion=DTareaAsignacion.objects.filter(tarea_id=item.id).last()

			if int(asignacion.estado_id)!=int(estadoT.atendida_fueraTiempo) and int(asignacion.estado_id)!=int(estadoT.atendida):
				numero=numero+1
			
		return numero

	@property
	def porcentajeTareas(self):
		tareas=DTarea.objects.filter(colaborador_actual__equipo_id=self.id)
		numero=0
		tipoT=TipoT()
		estadoT=EstadoT()

		for item in tareas:
			asignacion=DTareaAsignacion.objects.filter(tarea_id=item.id).last()

			if int(asignacion.estado_id)==int(estadoT.atendida_fueraTiempo) or int(asignacion.estado_id)==int(estadoT.atendida):
				numero=numero+1

		porcentaje=0
		if len(tareas)>0:
			porcentaje=(numero*100)/len(tareas)	
		
		valor=str(round(porcentaje,2))+'%'	
		return valor


	class Meta:
		db_table = 'administrador_tarea_equipo'

	def __unicode__(self):
		return self.nombre


class Colaborador(models.Model):
	equipo=models.ForeignKey(AEquipo, on_delete=models.PROTECT,related_name="colaborador_equipo")
	usuario=models.ForeignKey(Usuario, on_delete=models.PROTECT,related_name="colaborador_usuario")

	class Meta:
		db_table = 'administrador_tarea_colaborador'

	def __unicode__(self):
		return self.usuario.user.username

class DTarea(models.Model):
	asunto=models.TextField()
	descripcion=models.TextField(null=True, blank=True)
	fecha_fin=models.DateField(null=True)
	colaborador_actual=models.ForeignKey(Colaborador, on_delete=models.PROTECT,related_name="tarea_colaborador",null=True, blank=True)
	numero=models.TextField(null=True, blank=True)
	tipo_tarea=models.ForeignKey(Tipo, on_delete=models.PROTECT,related_name="tarea_tipo")
	usuario_responsable=models.ForeignKey(Usuario, on_delete=models.PROTECT,related_name="tarea_usuario")
	proyecto=models.ManyToManyField(Proyecto,related_name="tarea_proyecto", blank=True)

	@property
	def estado(self):
		return DTareaAsignacion.objects.filter(tarea__id=self.id).values('estado__color','estado__icono','estado__nombre','estado__id').last()

	@property
	def soporte(self):
		return SoporteAsignacionTarea.objects.filter(asignacion_tarea__tarea_id=self.id)

	@property
	def comentarios(self):
		return DTareaComentario.objects.filter(tarea_id=self.id)

	class Meta:
		db_table = 'administrador_tarea_tarea'

	def __unicode__(self):
		return self.descripcion


class DTareaAsignacion(models.Model):
	colaborador=models.ForeignKey(Colaborador, on_delete=models.PROTECT,related_name="asignacion_colaborador",null=True, blank=True)
	tarea=models.ForeignKey(DTarea, on_delete=models.PROTECT,related_name="asignacion_tarea")
	fecha=models.DateField()
	estado=models.ForeignKey(Estado, on_delete=models.PROTECT,related_name="asignacion_estado")
	comentario=models.TextField(null=True, blank=True)
	solicitante=models.ForeignKey(Usuario, on_delete=models.PROTECT,related_name="asignacion_usuario")

	class Meta:
		db_table = 'administrador_tarea_asignacion_tarea'

	def __unicode__(self):
		return self.tarea.asunto

class DTareaComentario(models.Model):
	tarea=models.ForeignKey(DTarea,related_name="comentario_tarea",on_delete=models.PROTECT)
	comentario = models.TextField()
	usuario=models.ForeignKey(Usuario,related_name="comentario_tarea_usuario",on_delete=models.PROTECT)
	fecha=models.DateTimeField(null=True,blank=True)

	class Meta:
		db_table = 'administrador_tarea_comentario'

	def __unicode__(self):
		return self.comentario

	def fecha_format(self):
		return self.fecha.strftime("%Y-%m-%d %H:%M:%S") 



class SoporteAsignacionTarea(models.Model):
	asignacion_tarea=models.ForeignKey(DTareaAsignacion, on_delete=models.PROTECT,related_name="soporte_asignacion")
	nombre=models.TextField()
	ruta = models.FileField(upload_to=RandomFileName('tarea/soporte_tarea','tt'),blank=True, null=True)
	#ruta = models.ImageField(upload_to='tarea',blank=True, null=True)

	class Meta:
		db_table = 'administrador_tarea_soporte_asignacion_tarea'

	def __unicode__(self):
		return self.nombre

	@property	
	def ruta_publica(self):
		if self.ruta:			
			return functions.crearRutaTemporalArchivoS3(str(self.ruta))
		else:
			return None		


class TareaActividad(models.Model):	
	tipo=models.ForeignKey(Tipo, on_delete=models.PROTECT,related_name="actividad_tipo")
	asunto=models.TextField()
	solicitante=models.ForeignKey(Usuario, on_delete=models.PROTECT,related_name="actividad_usuario")
	fecha=models.DateTimeField()
	fecha_transaccion=models.DateField()
	lugar=models.TextField()
	usuario_inivitado=models.ManyToManyField(Usuario,related_name="actividad_usuario_invitado", blank=True)

	class Meta:
		db_table = 'administrador_tarea_actividad'

	def __unicode__(self):
		return self.asunto

	def fecha_format(self):
		return self.fecha.strftime("%Y-%m-%d %H:%M:%S") 

	@property
	def soporte(self):
		return TareaActividadSoporte.objects.filter(tarea_actividad_id=self.id)


class TareaActividadSoporte(models.Model):	
	tarea_actividad=models.ForeignKey(TareaActividad, on_delete=models.PROTECT,related_name="actividad_soporte")
	nombre=models.TextField()
	ruta = models.FileField(upload_to=RandomFileName('tarea/soporte_actividad','ta'),blank=True, null=True)
	#ruta = models.ImageField(upload_to='tarea',blank=True, null=True)

	class Meta:
		db_table = 'administrador_tarea_actividad_soporte'

	def __unicode__(self):
		return self.nombre

	@property	
	def ruta_publica(self):
		if self.ruta:			
			return functions.crearRutaTemporalArchivoS3(str(self.ruta))
		else:
			return None		





