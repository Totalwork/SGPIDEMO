from django.db import models
from empresa.models import Empresa
from estado.models import Estado
from tipo.models import Tipo
from contrato.models import Contrato
from proyecto.models import Proyecto
from usuario.models import Persona, Usuario
from datetime import *
from tipo.models import Tipo
import json
from sinin4.functions import functions, RandomFileName


class ConfiguracionPorcentajes(models.Model):
	porcentaje 				=	models.DecimalField(null=True, max_digits=5, decimal_places=2)
	contrato 				=	models.OneToOneField(Contrato, unique=True, related_name="configuracion_porcentaje_contrato",on_delete=models.PROTECT)
	comentario 				=	models.TextField(blank=True, null=True)

	class Meta:		
		db_table 	= 'retie_configuracion_porcentajes'
		permissions = (
			("can_see_configuracion_porcentajes","can see configuracion porcentajes"),
		) 

class ProyectosNotificados(models.Model):	
	proyecto 				=	models.ForeignKey(Proyecto,blank=True, null=True, default=None,related_name="proyectos_notificados_proyecto",on_delete=models.PROTECT)
	enviado 				=	models.BooleanField(default=False)
	fecha 					=	models.DateTimeField(auto_now_add=True,blank=True,null=True)
			
	class Meta:		
		db_table = 'retie_proyectos_notificados'
		permissions = (
			("can_see_proyectos_notificados","can see proyectos notificados"),
		) 

class Aretie(models.Model):		
	proyecto 				=	models.ForeignKey(Proyecto,blank=True, null=True, default=None,related_name="visita_retie_proyecto",on_delete=models.PROTECT)
	fecha_programada		=	models.DateField(blank=True,null=True)
	fecha_ejecutada 		=	models.DateField(blank=True,null=True)
	hora 					= 	models.TimeField(blank=True, null=True)
	estado 					=	models.ForeignKey(Estado,blank=True, null=True, default=None,related_name="visita_retie_estado",on_delete=models.PROTECT)
	observacion 			=	models.TextField(blank=True, null=True)
	comentario_cancelado 	=	models.TextField(blank=True, null=True)
	
	def __unicode__(self):
		return self.proyecto.nombre

	def historial(self):
		return Historial.objects.filter(retie__id=self.id)

	def asistentes(self):
		return AsistenteVisita.objects.filter(retie__id=self.id)	

	def no_conformidades(self):
		return NoConformidad.objects.filter(retie__id=self.id)	

	def soportes(self):
		return Soporte.objects.filter(retie__id=self.id)		

	def notificar_correos(self):
		return NotificarCorreo.objects.filter(retie__id=self.id)				

	class Meta:
		db_table = 'retie'
		permissions = (
			("can_see_retie","can see retie"),
		) 

class AsistenteVisita(models.Model):		
	retie 					=	models.ForeignKey(Aretie,blank=True, null=True, default=None,related_name="asistente_retie",on_delete=models.PROTECT)
	persona 				=	models.ForeignKey(Persona,blank=True, null=True, default=None,related_name="asistente_visita_persona",on_delete=models.PROTECT)
	rol 					=	models.ForeignKey(Tipo,blank=True, null=True, default=None,related_name="asistente_visita_tipo",on_delete=models.PROTECT)
	no_asistio				=	models.BooleanField(default=False)	
	notificacion_enviada	=	models.BooleanField(default=False)	
	class Meta:
		db_table = 'retie_asistente_visita'
		permissions = (
			("can_see_retie_asistente_visita","can see retie asistente visita"),
		) 

class NotificarCorreo(models.Model):		
	retie 					=	models.ForeignKey(Aretie,blank=True, null=True, default=None,related_name="notificar_correo_retie",on_delete=models.PROTECT)		
	correo					=	models.CharField(max_length=255)
	nombre					=	models.CharField(max_length=255)
	notificacion_enviada	=	models.BooleanField(default=False)	
	class Meta:
		db_table = 'retie_notificar_correo'
		permissions = (
			("can_see_retie_retie_notificar_correo","can see retie retie notificar correo"),
		) 		

class Historial(models.Model):	
	retie 					=	models.ForeignKey(Aretie,blank=True, null=True, default=None,related_name="historial_visita_retie",on_delete=models.PROTECT)
	estado 					=	models.ForeignKey(Estado,blank=True, null=True, default=None,related_name="historial_retie_estado",on_delete=models.PROTECT)
	fecha_programada		=	models.DateField(blank=True,null=True)
	fecha_ejecutada 		=	models.DateField(blank=True,null=True)
	hora 					=	models.TimeField(blank=True, null=True)
	comentario 				=	models.TextField(blank=True, null=True)
	usuario 				=	models.ForeignKey(Usuario,blank=True, null=True, default=None,related_name="historial_retie_usuario",on_delete=models.PROTECT)
	fecha_ingreso 			=	models.DateTimeField(auto_now_add=True,blank=True,null=True)
	class Meta:
		db_table = 'retie_historial'
		permissions = (
			("can_see_retie_historial","can see retie historial"),
		) 	

class NoConformidad(models.Model):	
	retie 					=	models.ForeignKey(Aretie,blank=True, null=True, default=None,related_name="no_conformidad_retie",on_delete=models.PROTECT)	
	descripcion 			=	models.TextField(blank=True, null=True)
	corregida 				= 	models.BooleanField(default=False)	

	class Meta:
		db_table 	= 'retie_no_conformidad'
		permissions = (
			("can_see_retie_no_conformidad","can see retie no conformidad"),
		) 	

class Soporte(models.Model):	
	retie 					=	models.ForeignKey(Aretie,blank=True, null=True, default=None,related_name="soporte_retie",on_delete=models.PROTECT)	
	soporte 				=	models.FileField(upload_to=RandomFileName('retie/soporte','vrt'),blank=True, null=True)	
	# soporte 				=	models.FileField(upload_to='retie/soporte',blank=True, null=True)	#este se descomenta para crear la migracion
	nombre 					=	models.CharField(max_length=100)

	class Meta:
		db_table 	= 'retie_soporte'
		permissions = (
			("can_see_retie_soporte","can see retie soporte"),
		) 	
