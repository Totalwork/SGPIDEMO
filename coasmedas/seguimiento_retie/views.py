# -*- coding: utf-8 -*-
from django.db import transaction, connection
from datetime import *
from django.shortcuts import render,redirect
#,render_to_response
from django.urls import reverse
from .models import ConfiguracionPorcentajes, ProyectosNotificados, Aretie, AsistenteVisita, Historial, NoConformidad, Soporte, NotificarCorreo
from rest_framework import viewsets, serializers
from django.db.models import Q
from django.template import RequestContext
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
import xlsxwriter
import json
import re

from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from rest_framework.parsers import MultiPartParser, FormParser
from usuario.views import PersonaSerializer
from tipo.views import TipoSerializer
from tipo.models import Tipo
from estado.models import Estado
from estado.views import EstadoSerializer
from contrato.models import Contrato, EmpresaContrato
from logs.models import Logs,Acciones
from django.conf import settings
import os
from django.contrib.auth.decorators import login_required
from proyecto.models import Proyecto, Proyecto_empresas
from usuario.models import Persona, Usuario
from usuario.views import PersonaSerializer, UsuarioSerializer
from coasmedas.functions import functions
from adminMail.models import Mensaje
from adminMail.tasks import sendAsyncMail
from parametrizacion.views import MunicipioSerializer
from .enum import EnumEstadoRetie
import uuid

class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = Contrato
		fields=('id','nombre','numero')

class ProyectoLiteSerializer(serializers.HyperlinkedModelSerializer):
	mcontrato = ContratoLiteSerializer(read_only=True)
	municipio = MunicipioSerializer(read_only=True)
	class Meta: 
		model = Proyecto
		fields=( 'id','nombre', 'municipio', 'mcontrato')

#Configuracion Porcentajes
class ConfiguracionPorcentajesSerializer(serializers.HyperlinkedModelSerializer):
	contrato = ContratoLiteSerializer(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Contrato.objects.all())
	class Meta:
		model = ConfiguracionPorcentajes
		fields=('id', 'porcentaje', 'comentario', 'contrato_id', 'contrato')

class ConfiguracionPorcentajesViewSet(viewsets.ModelViewSet):
	model=ConfiguracionPorcentajes
	queryset = model.objects.all()
	serializer_class = ConfiguracionPorcentajesSerializer	
	paginate_by = 10

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ConfiguracionPorcentajesViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)
			contrato_id = self.request.query_params.get('contrato_id', None)
			qset=None
			if dato:
				qset=(Q(contrato__nombre__icontains=dato))			
				queryset = self.model.objects.filter(qset)

			if contrato_id:
				if qset:					
					qset=qset & (Q(contrato__id=contrato_id))
				else:
					qset=Q(contrato__id=contrato_id)
			
			if qset:
				queryset = self.model.objects.filter(qset)	
			
			mensaje=''
			if queryset.count()==0:
				mensaje='No se encontraron configuraciones con los criterios de busqueda ingresados'

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})
			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})	
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ConfiguracionPorcentajesSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='retie.configuracion_porcentajes',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ConfiguracionPorcentajesSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					#self.perform_update(serializer)
					serializer.save(contrato_id=request.DATA['contrato_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='retie.configuracion_porcentajes',id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic				
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':
			sid = transaction.savepoint()
			try:
				instance = self.get_object()
				self.perform_destroy(instance)
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='retie.configuracion_porcentajes',id_manipulado=instance.id)
				logs_model.save()
				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

#fin Configuracion Porcentajes

#ProyectosNotificados
class ProyectosNotificadosSerializer(serializers.HyperlinkedModelSerializer):
	proyecto = ProyectoLiteSerializer(read_only=True)
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Proyecto.objects.all())
	class Meta:
		model = ProyectosNotificados
		fields=('id', 'enviado', 'fecha', 'proyecto_id', 'proyecto')

class ProyectosNotificadosViewSet(viewsets.ModelViewSet):
	model=ProyectosNotificados
	queryset = model.objects.all()
	serializer_class = ProyectosNotificadosSerializer	
	paginate_by = 10

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ProyectosNotificadosViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)
			proyecto_id = self.request.query_params.get('proyecto_id', None)
			qset=None
			if dato:
				qset=(Q(proyecto__nombre__icontains=dato))			
				
			if proyecto_id:
				if qset:					
					qset=qset & (Q(proyecto__id=proyecto_id))
				else:
					qset=Q(contrato__id=proyecto_id)
			
			if qset:
				queryset = self.model.objects.filter(qset)	
			
			mensaje=''
			if queryset.count()==0:
				mensaje='No se encontraron proyectos con los criterios de busqueda ingresados'

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})
			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})	
		except Exception as e:
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ProyectosNotificadosSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(proyecto_id=request.DATA['proyecto_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='retie.proyectos_nitificados',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ProyectosNotificadosSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='retie.proyectos_nitificados',id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic				
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='retie.proyectos_nitificados',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

#fin ProyectosNotificados


#Retie

class SoporteRetieSerializer(serializers.HyperlinkedModelSerializer):		
	class Meta:
		model = Soporte
		fields=('id', 'soporte', 'nombre')


class NoConformidadRetieSerializer(serializers.HyperlinkedModelSerializer):		
	class Meta:
		model = NoConformidad
		fields=('id', 'descripcion', 'corregida')

class HistorialRetieSerializer(serializers.HyperlinkedModelSerializer):			
	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Estado.objects.filter(app='retie'))
	usuario = UsuarioSerializer(read_only=True)
	usuario_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Usuario.objects.all(), allow_null = True, default=None)
	class Meta:
		model = Historial
		fields=('id', 'fecha_programada', 'fecha_ejecutada', 'hora', 'comentario', 'fecha_ingreso', 'estado_id', 'estado', 'usuario_id', 'usuario')

class AsistenteVisitaRetieSerializer(serializers.HyperlinkedModelSerializer):
	persona = PersonaSerializer(read_only=True)
	persona_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Persona.objects.all())	
	rol = TipoSerializer(read_only=True)
	rol_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Tipo.objects.filter(app='retie'))
	class Meta:
		model = AsistenteVisita
		fields=('id', 'no_asistio', 'persona_id', 'persona', 'rol_id', 'rol', 'notificacion_enviada')

class NotificarCorreoRetieSerializer(serializers.HyperlinkedModelSerializer):		
	class Meta:
		model = NotificarCorreo
		fields=('id', 'correo', 'nombre', 'notificacion_enviada')

class RetieSerializer(serializers.HyperlinkedModelSerializer):
	proyecto = ProyectoLiteSerializer(read_only=True)
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Proyecto.objects.all())
	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Estado.objects.filter(app='retie'))
	historial = HistorialRetieSerializer(read_only=True, many=True)
	asistentes = AsistenteVisitaRetieSerializer(read_only=True, many=True)
	no_conformidades = NoConformidadRetieSerializer(read_only=True, many=True)
	soportes = SoporteRetieSerializer(read_only=True, many=True)
	notificar_correos = NotificarCorreoRetieSerializer(read_only=True, many=True)
	class Meta:
		model = Aretie
		fields=('id', 'fecha_programada', 'fecha_ejecutada', 'hora', 'observacion', 'comentario_cancelado', 'estado_id', 'estado', 'proyecto_id', 'proyecto', 'historial', 'asistentes', 'no_conformidades', 'soportes', 'notificar_correos')

class RetieViewSet(viewsets.ModelViewSet):
	model=Aretie
	queryset = model.objects.all()
	serializer_class = RetieSerializer	
	paginate_by = 10

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(RetieViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)
			mcontrato_id = self.request.query_params.get('contrato_id', None)
			proyecto_id = self.request.query_params.get('proyecto_id', None)
			departamento_id = self.request.query_params.get('departamento_id', None)
			municipio_id = self.request.query_params.get('municipio_id', None)
			estado_id = self.request.query_params.get('estado_id', None)
			fecha_inicio_programada = self.request.query_params.get('fecha_inicio_programada', None)
			fecha_final_programada = self.request.query_params.get('fecha_final_programada', None)
			fecha_inicio_ejecutada = self.request.query_params.get('fecha_inicio_ejecutada', None)
			fecha_final_ejecutada = self.request.query_params.get('fecha_final_ejecutada', None)
			proyectos = Proyecto_empresas.objects.filter(empresa__id=request.user.usuario.empresa.id).values('proyecto__id').distinct()
			qset=Q(proyecto__id__in=proyectos)
			if dato:
				qset=qset & (Q(proyecto__nombre__icontains=dato) |
					  Q(proyecto__mcontrato__nombre__icontains=dato) |
					  Q(proyecto__mcontrato__numero__icontains=dato) |
					  Q(proyecto__municipio__nombre__icontains=dato) |
					  Q(proyecto__municipio__departamento__nombre__icontains=dato))			
				
			if proyecto_id:									
				qset=qset & (Q(proyecto_id=proyecto_id))

			if mcontrato_id:								
				qset=qset & (Q(proyecto__mcontrato__id=mcontrato_id))	

			if municipio_id:
				qset=qset & (Q(proyecto__municipio__id=municipio_id))	

			if departamento_id:
				if qset:					
					qset=qset & (Q(proyecto__municipio__depatamento__id=departamento_id))
				else:
					qset=Q(proyecto__municipio__depatamento__id=departamento_id)			

			if estado_id:
				qset=qset & (Q(estado__id=estado_id))						
			
			if fecha_inicio_programada and fecha_final_programada:
				qset=qset & (Q(fecha_programada__range=(fecha_inicio_programada, fecha_final_programada)))
			elif fecha_inicio_programada and fecha_final_programada is None:
				qset=qset & (Q(fecha_programada=fecha_inicio_programada))

			if fecha_inicio_ejecutada and fecha_final_ejecutada:
				qset=qset & (Q(fecha_ejecutada__range=(fecha_inicio_ejecutada, fecha_final_ejecutada)))
			elif fecha_inicio_ejecutada and fecha_final_ejecutada is None:
				qset=qset & (Q(fecha_ejecutada=fecha_inicio_ejecutada))			

			if qset:
				queryset = self.model.objects.filter(qset)	
			
			mensaje=''
			if queryset.count()==0:
				mensaje='No se encontraron visitas retie con los criterios de busqueda ingresados'

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})
			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})	
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = RetieSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(proyecto_id=request.DATA['proyecto_id'], estado_id=request.DATA['estado_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='retie.retie',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()			
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = RetieSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					retie = Aretie.objects.get(pk=instance.id)	
					serializer.save(estado_id=request.DATA['estado_id'], proyecto_id=request.DATA['proyecto_id'])
					
					estado_id=None
					if retie.fecha_programada is not None and instance.fecha_ejecutada is None and \
						(instance.fecha_programada != retie.fecha_programada or instance.hora != retie.hora):
						estado_id=EnumEstadoRetie.Reprogramada	
						instance.estado_id=estado_id
						instance.save()					
					elif retie.fecha_programada is None:
						estado_id=EnumEstadoRetie.Programada
						instance.estado_id=estado_id
						instance.save()
					elif retie.fecha_ejecutada is None and instance.fecha_ejecutada is not None and \
						 instance.fecha_programada == instance.fecha_ejecutada:
						estado_id=EnumEstadoRetie.Ejecutada
						instance.estado_id=estado_id
						instance.save()
					elif retie.fecha_ejecutada is None and instance.fecha_ejecutada is not None and \
						 instance.fecha_ejecutada > instance.fecha_programada:
						estado_id=EnumEstadoRetie.EjecutadaAtrazada	
						instance.estado_id=estado_id
						instance.save()					

					asistentes=AsistenteVisita.objects.filter(retie__id=instance.id)
					if asistentes:
						asistentes.delete()
					
					for x in request.DATA['asistentes']:
						asis=AsistenteVisita(no_asistio=x['no_asistio'],
							persona_id=x['persona']['id'],
							retie_id=instance.id,
							rol_id=x['rol']['id'],
							notificacion_enviada=x['notificacion_enviada'])
						asis.save()	

					notificar_correo=NotificarCorreo.objects.filter(retie__id=instance.id)
					if notificar_correo:
						notificar_correo.delete()	

					for x in request.DATA['notificar_correos']:
						notCorr=NotificarCorreo(retie_id=instance.id,
											nombre=x['nombre'],
											correo=x['correo'],
											notificacion_enviada=x['notificacion_enviada'])
						notCorr.save()			

					h=Historial(fecha_programada=request.DATA['fecha_programada'],
								fecha_ejecutada=request.DATA['fecha_ejecutada'],
								hora=request.DATA['hora'],
								comentario=request.DATA['comentario_cancelado'],								
								estado_id=request.DATA['estado_id'],
								retie_id=instance.id,
								usuario_id=request.user.usuario.id)
					h.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='retie.historial',id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)

					#envia las notificaciones a los correos que agregue la persona encargada
					notificar_correo=NotificarCorreo.objects.filter(retie__id=instance.id)
					if notificar_correo:
						for item in notificar_correo:
							if item.correo:
								
								if item.retie.fecha_programada != retie.fecha_programada or item.retie.hora != retie.hora or \
									item.notificacion_enviada is None or item.notificacion_enviada == False:
									
									try:								
																				
										contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
										contenido = contenido + 'Se&ntilde;or Usuario(a) {}<br/><br/>'.format(item.nombre)																
										if item.notificacion_enviada:										
											contenido = contenido + 'Nos permitimos comunicarle que la visita RETIE que tenia programada para la fecha {}, fue reprogramada para la fecha {} a las {} para el siguiente proyecto:'.format(retie.fecha_programada,request.DATA['fecha_programada'], request.DATA['hora'])
										else:
											contenido = contenido + 'Nos permitimos comunicarle que usted tiene una visita RETIE programada para la fecha {} a las {} para el siguiente proyecto:'.format(request.DATA['fecha_programada'], request.DATA['hora'])

										contenido = contenido + '<br><br><br>';
										contenido = contenido + '<table border="1" cellpadding="2" cellspacing="2">'
										contenido = contenido + '<tr> \
													 			   	<th valign="top">Macro-contrato</th> \
													 			   	<th valign="top">Departamento</th> \
													 			   	<th valign="top">Municipio</th> \
													 			   	<th valign="top">Proyecto</th>\
													 			 </tr>'
										
										contenido = contenido + '<tr>\
													 			   	<td>{}</td>\
													 			   	<td>{}</td>\
													 			   	<td>{}</td>\
													 			   	<td>{}</td>\
													 			  </tr>'.format(instance.proyecto.mcontrato.numero,
																 			  	instance.proyecto.municipio.departamento.nombre,
																 			  	instance.proyecto.municipio.nombre,
																 			  	instance.proyecto.nombre)	
										contenido = contenido + '</table>';	
										contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
										contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
										mail = Mensaje(
										remitente=settings.REMITENTE,
										destinatario=item.correo,
										asunto='Visita RETIE Reprogramada' if item.notificacion_enviada == True else 'Visita RETIE Programada',
										contenido=contenido,
										appLabel='seguimiento_retie',
										)
										mail.save()									
										sendAsyncMail(mail)	
										item.notificacion_enviada=True
										item.save()
									except Exception as e:
										functions.toLog(e,self.nombre_modulo)
										pass

					asistentes=AsistenteVisita.objects.filter(retie__id=instance.id)
					if asistentes:
						for item in asistentes:
							if item.persona.correo:
								
								if item.retie.fecha_programada != retie.fecha_programada or item.retie.hora != retie.hora or \
									item.notificacion_enviada is None or item.notificacion_enviada == False:
									
									try:								
										
										nombre = "{} {}".format(item.persona.nombres, item.persona.apellidos)
										contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
										contenido = contenido + 'Se&ntilde;or Usuario(a) {}<br/><br/>'.format(nombre)																
										if item.notificacion_enviada:										
											contenido = contenido + 'Nos permitimos comunicarle que la visita RETIE que tenia programada para la fecha {}, fue reprogramada para la fecha {} a las {} para el siguiente proyecto:'.format(retie.fecha_programada,request.DATA['fecha_programada'], request.DATA['hora'])
										else:
											contenido = contenido + 'Nos permitimos comunicarle que usted tiene una visita RETIE programada para la fecha {} a las {} para el siguiente proyecto:'.format(request.DATA['fecha_programada'], request.DATA['hora'])

										contenido = contenido + '<br><br><br>';
										contenido = contenido + '<table border="1" cellpadding="2" cellspacing="2">'
										contenido = contenido + '<tr> \
													 			   	<th valign="top">Macro-contrato</th> \
													 			   	<th valign="top">Departamento</th> \
													 			   	<th valign="top">Municipio</th> \
													 			   	<th valign="top">Proyecto</th>\
													 			 </tr>'
										
										contenido = contenido + '<tr>\
													 			   	<td>{}</td>\
													 			   	<td>{}</td>\
													 			   	<td>{}</td>\
													 			   	<td>{}</td>\
													 			  </tr>'.format(instance.proyecto.mcontrato.numero,
																 			  	instance.proyecto.municipio.departamento.nombre,
																 			  	instance.proyecto.municipio.nombre,
																 			  	instance.proyecto.nombre)	
										contenido = contenido + '</table>';	
										contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
										contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'					
										mail = Mensaje(
										remitente=settings.REMITENTE,
										destinatario=item.persona.correo,
										asunto='Visita RETIE Reprogramada' if item.notificacion_enviada == True else 'Visita RETIE Programada',
										contenido=contenido,
										appLabel='seguimiento_retie',
										)
										mail.save()									
										sendAsyncMail(mail)	
										item.notificacion_enviada=True
										item.save()
									except Exception as e:
										functions.toLog(e,self.nombre_modulo)
										pass

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:					
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
	
	@transaction.atomic				
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='retie.retie',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

#fin retie


#AsistenteVisita
class AsistenteVisitaSerializer(serializers.HyperlinkedModelSerializer):
	persona = PersonaSerializer(read_only=True)
	persona_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Persona.objects.all())
	retie = RetieSerializer(read_only=True)
	retie_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Aretie.objects.all())
	rol = TipoSerializer(read_only=True)
	rol_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Tipo.objects.filter(app='retie'))
	class Meta:
		model = AsistenteVisita
		fields=('id', 'no_asistio', 'persona_id', 'persona','retie_id', 'retie', 'rol_id', 'rol', 'notificacion_enviada')

class AsistenteVisitaViewSet(viewsets.ModelViewSet):
	model=AsistenteVisita
	queryset = model.objects.all()
	serializer_class = AsistenteVisitaSerializer	
	paginate_by = 10

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(AsistenteVisitaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)
			persona_id = self.request.query_params.get('persona_id', None)
			retie_id = self.request.query_params.get('retie_id', None)
			qset=None
			if dato:
				qset=(Q(persona__nombres__icontains=dato) | 
					Q(persona__apellidos__icontains=dato) | 
					Q(persona__cedula__icontains=dato) |
					Q(rol__nombre__icontains=dato))			
				
			if persona_id:
				if qset:					
					qset=qset & (Q(persona__id=persona_id))
				else:
					qset=Q(persona__id=persona_id)

			if retie_id:
				if qset:					
					qset=qset & (Q(retie__id=retie_id))
				else:
					qset=Q(retie__id=retie_id)		
			
			if qset:
				queryset = self.model.objects.filter(qset)	
			
			mensaje=''
			if queryset.count()==0:
				mensaje='No se encontraron visitas retie con los criterios de busqueda ingresados'

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})
			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})	
		except Exception as e:
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = AsistenteVisitaSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(persona_id=request.DATA['persona_id'],retie_id=request.DATA['retie_id'], rol_id=request.DATA['rol_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='retie.asistente_visita',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = AsistenteVisitaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='retie.asistente_visita',id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic				
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='retie.asistente_visita',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

#fin AsistenteVisita

#notificar correo
class NotificarCorreoSerializer(serializers.HyperlinkedModelSerializer):	
	retie = RetieSerializer(read_only=True)
	retie_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Aretie.objects.all())	
	class Meta:
		model = NotificarCorreo
		fields=('id', 'retie_id', 'retie', 'correo', 'nombre', 'notificacion_enviada')

class NotificarCorreoViewSet(viewsets.ModelViewSet):
	model=NotificarCorreo
	queryset = model.objects.all()
	serializer_class = NotificarCorreoSerializer	
	paginate_by = 10

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(NotificarCorreoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)
			nombre = self.request.query_params.get('nombre', None)
			correo = self.request.query_params.get('correo', None)
			retie_id = self.request.query_params.get('retie_id', None)
			qset=None
			if dato:
				qset=(Q(nombre__icontains=dato) | Q(correo__icontains=dato))			
			
			if retie_id:
				if qset:					
					qset=qset & (Q(retie__id=retie_id))
				else:
					qset=Q(retie__id=retie_id)		
			
			if qset:
				queryset = self.model.objects.filter(qset)	
			
			mensaje=''
			if queryset.count()==0:
				mensaje='No se encontraron correos con los criterios de busqueda ingresados'

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})
			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})	
		except Exception as e:
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = NotificarCorreoSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(retie_id=request.DATA['retie_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='retie.notificar_correo',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = NotificarCorreoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='retie.notificar_correo',id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic				
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='retie.notificar_correo',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

#fin notificar correo

#historial
class HistorialSerializer(serializers.HyperlinkedModelSerializer):	
	retie = RetieSerializer(read_only=True)
	retie_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Aretie.objects.all())
	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Estado.objects.filter(app='retie'))
	usuario = UsuarioSerializer(read_only=True)
	usuario_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Usuario.objects.all(), allow_null = True, default=None)
	class Meta:
		model = Historial
		fields=('id', 'fecha_programada', 'fecha_ejecutada', 'hora', 'comentario', 'fecha_ingreso', 'estado_id', 'estado', 'retie_id', 'retie', 'usuario_id', 'usuario')

class HistorialViewSet(viewsets.ModelViewSet):
	model=Historial
	queryset = model.objects.all()
	serializer_class = HistorialSerializer	
	paginate_by = 10

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(HistorialViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)
			proyecto_id = self.request.query_params.get('proyecto_id', None)
			retie_id = self.request.query_params.get('retie_id', None)
			qset=None
			if dato:
				qset=(Q(retie__proyecto__nombre__icontains=dato))			
				queryset = self.model.objects.filter(qset)

			if proyecto_id:
				if qset:					
					qset=qset & (Q(retie__proyecto__id=proyecto_id))
				else:
					qset=Q(retie__proyecto__id=proyecto_id)

			if retie_id:
				if qset:					
					qset=qset & (Q(retie__id=retie_id))
				else:
					qset=Q(retie__id=retie_id)		
			
			if qset:
				queryset = self.model.objects.filter(qset)	
			
			mensaje=''
			if queryset.count()==0:
				mensaje='No se encontraron visitas retie con los criterios de busqueda ingresados'

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})
			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})	
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = HistorialSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					usuario_id=request.DATA['usuario_id'] if request.FILES.get('usuario_id') is not None else request.user.usuario.id
					serializer.save(retie_id=request.DATA['retie_id'], estado_id=request.DATA['estado_id'], usuario_id=usuario_id)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='retie.historial',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = HistorialSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='retie.retie',id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic				
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='retie.retie',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

#fin historial

#no conformidades
class NoConformidadSerializer(serializers.HyperlinkedModelSerializer):	
	retie = RetieSerializer(read_only=True)
	retie_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Aretie.objects.all())	
	class Meta:
		model = NoConformidad
		fields=('id', 'descripcion', 'corregida', 'retie_id', 'retie')

class NoConformidadRetieViewSet(viewsets.ModelViewSet):
	model=NoConformidad
	queryset = model.objects.all()
	serializer_class = NoConformidadSerializer	
	paginate_by = 10

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(NoConformidadRetieViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)			
			retie_id = self.request.query_params.get('retie_id', None)
			qset=None
			if dato:
				qset=Q(descripcion__icontains=dato)			
			
			if retie_id:
				if qset:					
					qset=qset & (Q(retie__id=retie_id))
				else:
					qset=Q(retie__id=retie_id)		
			
			if qset:
				queryset = self.model.objects.filter(qset)	
			
			mensaje=''
			if queryset.count()==0:
				mensaje='No se encontraron No Nonformidades con los criterios de busqueda ingresados'

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})
			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})	
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = NoConformidadSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(retie_id=request.DATA['retie_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='retie.no_conformidad',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = NoConformidadSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(retie_id=request.DATA['retie_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='retie.no_conformidad',id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic				
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='retie.no_conformidad',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

#no conformidades

#soportes

class SoporteSerializer(serializers.HyperlinkedModelSerializer):	
	retie = RetieSerializer(read_only=True)
	retie_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Aretie.objects.all())	
	class Meta:
		model = Soporte
		fields=('id', 'soporte', 'nombre', 'retie_id', 'retie')

class SoporteViewSet(viewsets.ModelViewSet):
	model=Soporte
	queryset = model.objects.all()
	serializer_class = SoporteSerializer	
	paginate_by = 10

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(SoporteViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)			
			retie_id = self.request.query_params.get('retie_id', None)
			qset=None
			if dato:
				qset=Q(nombre__icontains=dato)
			
			if retie_id:
				if qset:					
					qset=qset & (Q(retie__id=retie_id))
				else:
					qset=Q(retie__id=retie_id)		
			
			if qset:
				queryset = self.model.objects.filter(qset)	
			
			mensaje=''
			if queryset.count()==0:
				mensaje='No se encontraron No Nonformidades con los criterios de busqueda ingresados'

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})
			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok','data':serializer.data})	
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = SoporteSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(retie_id=request.DATA['retie_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='retie.no_conformidad',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = SoporteSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(retie_id=request.DATA['retie_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='retie.no_conformidad',id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic				
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='retie.no_conformidad',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

#fin soportes


@transaction.atomic	
@login_required		
@api_view(['PUT',])
def actualizar_seguimiento(request,pk):
	if request.method == 'PUT':
		sid = transaction.savepoint()			
		try:
			#print request.FILES
			instance = Aretie.objects.get(pk=pk)
			serializer = RetieSerializer(instance,data=request.DATA,context={'request': request})
			if serializer.is_valid():
				retie = Aretie.objects.get(pk=instance.id)	
				serializer.save(estado_id=request.DATA['estado_id'], proyecto_id=request.DATA['proyecto_id'])
				
				estado_id=None
				if retie.fecha_ejecutada is None and instance.fecha_ejecutada is not None and \
					instance.fecha_programada == instance.fecha_ejecutada:
					estado_id=EnumEstadoRetie.Ejecutada
					instance.estado_id=estado_id
					instance.save()
				elif retie.fecha_ejecutada is None and instance.fecha_ejecutada is not None and \
					instance.fecha_ejecutada > instance.fecha_programada:
					estado_id=EnumEstadoRetie.EjecutadaAtrazada	
					instance.estado_id=estado_id
					instance.save()

				asistentes=AsistenteVisita.objects.filter(retie__id=instance.id)
				if asistentes:
					asistentes.delete()
								
				listaAsistentes=json.loads(request.DATA['asistentes'])
				for x in listaAsistentes:
					asis=AsistenteVisita(no_asistio=x['no_asistio'],
						persona_id=x['persona']['id'],
						retie_id=instance.id,
						rol_id=x['rol']['id'],
						notificacion_enviada=x['notificacion_enviada'])
					asis.save()		

				notificar_correo=NotificarCorreo.objects.filter(retie__id=instance.id)
				if notificar_correo:
					notificar_correo.delete()	

				listaNotificarCorreos=json.loads(request.DATA['notificar_correos'])
				for x in listaNotificarCorreos:
					notCorr=NotificarCorreo(retie_id=instance.id,
										nombre=x['nombre'],
										correo=x['correo'],
										notificacion_enviada=x['notificacion_enviada'])
					notCorr.save()				

				no_conformidades=NoConformidad.objects.filter(retie__id=instance.id)
				if no_conformidades:
					no_conformidades.delete()	

				listaNoConformidades=json.loads(request.DATA['no_conformidades'])
				for x in listaNoConformidades:
					noConf=NoConformidad(descripcion=x['descripcion'],
										corregida=x['corregida'],
										retie_id=instance.id)	
					noConf.save()						
				
				listaSoportes=json.loads(request.DATA['soportes'])
				for x in listaSoportes:
					if x['id'] > 0 and x['eliminado']==True:
						s=Soporte.objects.get(pk=x['id'])
						s.delete()

				soportes=request.FILES.getlist('soporte[]')
					
				if soportes:
					i = 0
					for sp in soportes:						
						nombre = request.DATA.getlist('nombre[]')						
						s= Soporte(soporte=sp, nombre=nombre[i], retie_id=instance.id)
						s.save()
					i = i + 1

				h=Historial(fecha_programada=request.DATA['fecha_programada'],
							fecha_ejecutada=request.DATA['fecha_ejecutada'],
							hora=request.DATA['hora'],
							comentario=request.DATA['comentario_cancelado'],								
							estado_id=request.DATA['estado_id'],
							retie_id=instance.id,
							usuario_id=request.user.usuario.id)
				h.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='retie.historial',id_manipulado=instance.id)
				logs_model.save()
				transaction.savepoint_commit(sid)
				
				if instance.fecha_ejecutada != retie.fecha_ejecutada:	

					notificar_correo=NotificarCorreo.objects.filter(retie__id=instance.id)
					if notificar_correo:
						for item in notificar_correo:
							if item.correo:																									
								try:								
																		
									contenido=crear_contenido_actualizar(request, instance, item.nombre, item.notificacion_enviada)
														
									mail = Mensaje(
									remitente=settings.REMITENTE,
									destinatario=item.correo,
									asunto='Visita RETIE Ejecutada',
									contenido=contenido,
									appLabel='seguimiento_retie',
									)
									mail.save()									
									sendAsyncMail(mail)	
									item.notificacion_enviada=True
									item.save()
								except Exception as e:
									functions.toLog(e,self.nombre_modulo)
									pass

					asistentes=AsistenteVisita.objects.filter(retie__id=instance.id)				
					if asistentes:
						for item in asistentes:
							if item.persona.correo:																									
								try:								
									
									nombre = "{} {}".format(item.persona.nombres, item.persona.apellidos)
									contenido=crear_contenido_actualizar(request, instance, nombre, item.notificacion_enviada)
														
									mail = Mensaje(
									remitente=settings.REMITENTE,
									destinatario=item.persona.correo,
									asunto='Visita RETIE Ejecutada',
									contenido=contenido,
									appLabel='seguimiento_retie',
									)
									mail.save()									
									sendAsyncMail(mail)	
									item.notificacion_enviada=True
									item.save()
								except Exception as e:
									functions.toLog(e,self.nombre_modulo)
									pass

				return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
			else:
				# print(serializer.errors)
				return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
	
def crear_contenido_actualizar(request, instance, nombre, notificacion_enviada):

	contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
	contenido = contenido + 'Se&ntilde;or Usuario(a) {}<br/><br/>'.format(nombre)																
											
	contenido = contenido + 'Nos permitimos comunicarle que la visita RETIE que tenia programada para la fecha {}, fue ejecutada el {} para el siguiente proyecto:'.format(instance.fecha_programada,request.DATA['fecha_ejecutada'])
	
	contenido = contenido + '<br><br><br>';
	contenido = contenido + '<table border="1" cellpadding="2" cellspacing="2">'
	contenido = contenido + '<tr> \
				 			   	<th valign="top">Macro-contrato</th> \
				 			   	<th valign="top">Departamento</th> \
				 			   	<th valign="top">Municipio</th> \
				 			   	<th valign="top">Proyecto</th>\
				 			 </tr>'
	
	contenido = contenido + '<tr>\
				 			   	<td>{}</td>\
				 			   	<td>{}</td>\
				 			   	<td>{}</td>\
				 			   	<td>{}</td>\
				 			  </tr>'.format(instance.proyecto.mcontrato.numero,
							 			  	instance.proyecto.municipio.departamento.nombre,
							 			  	instance.proyecto.municipio.nombre,
							 			  	instance.proyecto.nombre)	
	contenido = contenido + '</table>';
	contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
	contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'

	return contenido;

@transaction.atomic	
@login_required		
@api_view(['PUT',])
def cancelar_visita(request,pk):
	if request.method == 'PUT':
		sid = transaction.savepoint()	
		try:
			instance = Aretie.objects.get(pk=pk)
			instance.comentario_cancelado=request.DATA['comentario']
			instance.estado_id=EnumEstadoRetie.Cancelada
			instance.save()

			h=Historial(fecha_programada=instance.fecha_programada,
						fecha_ejecutada=instance.fecha_ejecutada,
						hora=instance.hora,
						comentario=request.DATA['comentario'],								
						estado_id=EnumEstadoRetie.Cancelada,
						retie_id=instance.id,
						usuario_id=request.user.usuario.id)
			h.save()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='retie',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)

			notificar_correo=NotificarCorreo.objects.filter(retie__id=instance.id)				
			if notificar_correo:
				for item in notificar_correo:
					if item.correo:																									
						try:								
														
							contenido=crear_contenido_cancelar(request, instance, item.nombre, item.notificacion_enviada)
												
							mail = Mensaje(
							remitente=settings.REMITENTE,
							destinatario=item.correo,
							asunto='Visita RETIE Cancelada',
							contenido=contenido,
							appLabel='seguimiento_retie',
							)
							mail.save()									
							sendAsyncMail(mail)	
							item.notificacion_enviada=True
							item.save()
						except Exception as e:
							functions.toLog(e,self.nombre_modulo)
							pass

			asistentes=AsistenteVisita.objects.filter(retie__id=instance.id)				
			if asistentes:
				for item in asistentes:
					if item.persona.correo:																									
						try:								
							
							nombre = "{} {}".format(item.nombres, item.apellidos)
							contenido=crear_contenido_cancelar(request, instance, nombre, item.notificacion_enviada)
												
							mail = Mensaje(
							remitente=settings.REMITENTE,
							destinatario=item.persona.correo,
							asunto='Visita RETIE Cancelada',
							contenido=contenido,
							appLabel='seguimiento_retie',
							)
							mail.save()									
							sendAsyncMail(mail)	
							item.notificacion_enviada=True
							item.save()
						except Exception as e:
							functions.toLog(e,self.nombre_modulo)
							pass

			return Response({'message':'Las visita ha sido cancelada exitosamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)	


def crear_contenido_cancelar(request, instance, nombre, notificacion_enviada):

	contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
	contenido = contenido + 'Se&ntilde;or Usuario(a) {}<br/><br/>'.format(nombre)																
											
	contenido = contenido + 'Nos permitimos comunicarle que la visita RETIE que tenia programada para la fecha {} a las {}, ha sido cancelada para el siguiente proyecto:'.format(instance.fecha_programada,instance.hora)
	
	contenido = contenido + '<br><br><br>';
	contenido = contenido + '<table border="1" cellpadding="2" cellspacing="2">'
	contenido = contenido + '<tr> \
				 			   	<th valign="top">Macro-contrato</th> \
				 			   	<th valign="top">Departamento</th> \
				 			   	<th valign="top">Municipio</th> \
				 			   	<th valign="top">Proyecto</th>\
				 			 </tr>'
	
	contenido = contenido + '<tr>\
				 			   	<td>{}</td>\
				 			   	<td>{}</td>\
				 			   	<td>{}</td>\
				 			   	<td>{}</td>\
				 			  </tr>'.format(instance.proyecto.mcontrato.numero,
							 			  	instance.proyecto.municipio.departamento.nombre,
							 			  	instance.proyecto.municipio.nombre,
							 			  	instance.proyecto.nombre)	
	contenido = contenido + '</table>';
	contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
	contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
	return contenido;

#configuracion pocentajes
@login_required
@transaction.atomic
def configuracion_porcentajes(request):
	#configuraciones_contratos=[(x.contrato.id) for x in ConfiguracionPorcentajes.objects.all()]	
	contratos=EmpresaContrato.objects.filter(contrato__tipo_contrato__id=12, participa=1, empresa__id=request.user.usuario.empresa.id)#.exclude(contrato__id__in=configuraciones_contratos)#macro contratos
	return render(request, 'configuracion_porcentajes.html',
		{'contratos':contratos,'model':'configuracion_porcentaje','app':'seguimiento_retie'},
		)

@login_required
def eliminar_configuracion_porcentajes(request):
	sid = transaction.savepoint()
	try:
		resultado=json.loads(request.POST['_content'])

		for id in resultado['lista']:
			conf=ConfiguracionPorcentajes.objects.get(pk=id)			
			conf.delete()		
		
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El(Los) registro(s) fueron eliminado satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:
		transaction.savepoint_rollback(sid)
		functions.toLog(e,self.nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

@login_required
def exportar_configuracion_porcentajes(request):
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="Configuraciones-Contrato.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Vigencias')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})

		dato = request.GET.get('dato', None)		
		contrato_id = request.GET.get('contrato_id', None)
		qset=None
		if dato:
			qset=(Q(contrato__nombre__icontains=dato))
		if contrato_id:
			if qset:					
				qset=qset & (Q(contrato__id=contrato_id))
			else:
				qset=Q(contrato__id=contrato_id)
		
		queryset=None
		if qset:
			queryset = ConfiguracionPorcentajes.objects.filter(qset)	
		else:
			queryset = ConfiguracionPorcentajes.objects.all()			
			

		worksheet.write('A1', 'Numero', format1)		
		worksheet.write('B1', 'Macro-Contrato', format1)
		worksheet.write('C1', 'Porcentaje', format1)
		worksheet.write('D1', 'Comentario', format1)
		
		worksheet.set_column('A:A', 24)		
		worksheet.set_column('B:B', 24)
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 20)				

		row=1
		col=0

		for item in queryset:
			worksheet.write(row,col  ,item.contrato.numero ,format2)			
			worksheet.write(row,col+1,item.contrato.nombre ,format2)
			worksheet.write(row,col+2,item.porcentaje,format2)
			worksheet.write(row,col+3,item.comentario,format2)								
			row +=1		

		workbook.close()
		return response	

	except Exception as e:
		functions.toLog(e,self.nombre_modulo)


@login_required
def exportar_visitas(request):
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="Reporte Visitas Retie.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Vigencias')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})
		format_hour=workbook.add_format({'border':1,'num_format': 'h:mm:ss'})
		
		#import pdb; pdb.set_trace()
		dato = request.GET['dato'] if 'dato' in request.GET else None
		mcontrato_id = request.GET['contrato_id'] if 'contrato_id' in request.GET else None
		# proyecto_id = request.GET['proyecto_id'] if 'proyecto_id' in request.GET else None
		# departamento_id = request.GET['departamento_id'] if 'departamento_id' in request.GET else None
		# municipio_id = request.GET['municipio_id'] if 'municipio_id' in request.GET else None
		# estado_id = request.GET['estado_id'] if 'estado_id' in request.GET else None
		# fecha_inicio_programada = request.GET['fecha_inicio_programada'] if 'fecha_inicio_programada' in request.GET else None
		# fecha_final_programada = request.GET['fecha_final_programada'] if 'fecha_final_programada' in request.GET else None
		# fecha_inicio_ejecutada = request.GET['fecha_inicio_ejecutada'] if 'fecha_inicio_ejecutada' in request.GET else None
		# fecha_final_ejecutada = request.GET['fecha_final_ejecutada'] if 'fecha_final_ejecutada' in request.GET else None
		
		proyectos = Proyecto_empresas.objects.filter(empresa__id=request.user.usuario.empresa.id).values('proyecto__id').distinct()
		
		qset=Q(proyecto__id__in=proyectos)
		
		if dato:
			qset=(Q(proyecto__nombre__icontains=dato) | 
					Q(proyecto__mcontrato__nombre__icontains=dato) |
					Q(proyecto__mcontrato__numero__icontains=dato) |
					Q(proyecto__municipio__nombre__icontains=dato) |
					Q(proyecto__municipio__departamento__nombre__icontains=dato))			
			
		# if proyecto_id:
		# 	if qset:					
		# 		qset=qset & (Q(proyecto__id=proyecto_id))
		# 	else:
		# 		qset=Q(proyecto__id=proyecto_id)

		if mcontrato_id:
			if qset:					
				qset=qset & (Q(proyecto__mcontrato__id=mcontrato_id))
			else:
				qset=Q(proyecto__mcontrato__id=mcontrato_id)	

		# if municipio_id:
		# 	if qset:					
		# 		qset=qset & (Q(proyecto__municipio__id=municipio_id))
		# 	else:
		# 		qset=Q(proyecto__municipio__id=municipio_id)	

		# if departamento_id:
		# 	if qset:					
		# 		qset=qset & (Q(proyecto__municipio__depatamento__id=departamento_id))
		# 	else:
		# 		qset=Q(proyecto__municipio__depatamento__id=departamento_id)			

		# if estado_id:
		# 	if qset:					
		# 		qset=qset & (Q(estado__id=estado_id))
		# 	else:
		# 		qset=Q(estado__id=estado_id)						
		
		# if fecha_inicio_programada and fecha_final_programada:
		# 	if qset:					
		# 		qset=qset & (Q(fecha_programada__range=(fecha_inicio_programada, fecha_final_programada)))
		# 	else:
		# 		qset=(Q(fecha_programada__range=(fecha_inicio_programada, fecha_final_programada)))
		# elif fecha_inicio_programada and fecha_final_programada is None:
		# 	if qset:					
		# 		qset=qset & (Q(fecha_programada=fecha_inicio_programada))
		# 	else:
		# 		qset=(Q(fecha_programada=fecha_inicio_programada))

		# if fecha_inicio_ejecutada and fecha_final_ejecutada:
		# 	if qset:					
		# 		qset=qset & (Q(fecha_ejecutada__range=(fecha_inicio_ejecutada, fecha_final_ejecutada)))
		# 	else:
		# 		qset=(Q(fecha_ejecutada__range=(fecha_inicio_ejecutada, fecha_final_ejecutada)))
		# elif fecha_inicio_ejecutada and fecha_final_ejecutada is None:
		# 	if qset:					
		# 		qset=qset & (Q(fecha_ejecutada=fecha_inicio_ejecutada))
		# 	else:
		# 		qset=(Q(fecha_ejecutada=fecha_inicio_ejecutada))		

		if qset:
			queryset = Aretie.objects.filter(qset)				
			

		worksheet.write('A1', 'Macro-Contrato', format1)		
		worksheet.write('B1', 'Proyecto', format1)
		worksheet.write('C1', 'Departamento', format1)
		worksheet.write('D1', 'Municipio', format1)
		worksheet.write('E1', 'Hora', format1)
		worksheet.write('F1', 'Fecha Programada', format1)
		worksheet.write('G1', 'Fecha de Ejecucion', format1)
		worksheet.write('H1', 'Estado', format1)
		
		worksheet.set_column('A:A', 24)		
		worksheet.set_column('B:B', 24)
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 25)	
		worksheet.set_column('E:E', 20)
		worksheet.set_column('F:F', 20)
		worksheet.set_column('G:G', 20)			
		worksheet.set_column('H:H', 24)			

		row=1
		col=0

		for item in queryset:
			worksheet.write(row,col  ,item.proyecto.mcontrato.nombre ,format2)			
			worksheet.write(row,col+1,item.proyecto.nombre ,format2)
			worksheet.write(row,col+2,item.proyecto.municipio.departamento.nombre,format2)
			worksheet.write(row,col+3,item.proyecto.municipio.nombre,format2)								
			worksheet.write(row,col+4,item.hora,format_hour)								
			worksheet.write(row,col+5,item.fecha_programada,format_date)								
			worksheet.write(row,col+6,item.fecha_ejecutada,format_date)								
			worksheet.write(row,col+7,item.estado.nombre,format2)								
			row +=1		

		workbook.close()
		return response	

	except Exception as e:
		functions.toLog(e,self.nombre_modulo)

#fin configuracion porcentaje


#visitas retie

@login_required
def consultar_visitas_retie(request):	
	contratos=EmpresaContrato.objects.filter(contrato__tipo_contrato__id=12, empresa__id=request.user.usuario.empresa.id)#.exclude(contrato__id__in=configuraciones_contratos)#macro contratos
	estados=Estado.objects.filter(app='retie')
	return render(request, 'consultar_visitas_retie.html',
		{'estados':estados,'contratos':contratos,'model':'retie','app':'seguimiento_retie'},
		)

@login_required
def programar_visitas_retie(request, id):	
	retie=Aretie.objects.get(pk=id)	
	roles = Tipo.objects.filter(app='retie')
	correos=NotificarCorreo.objects.filter(retie__id=id).values('correo')
	nombres=NotificarCorreo.objects.filter(retie__id=id).values('nombre')
	return render(request, 'programar_visita.html',
		{'nombres':nombres,'correos':correos,'retie':retie, 'roles':roles, 'model':'retie','app':'seguimiento_retie'},
		)	

@login_required
def seguimiento_visitas_retie(request, id):	
	retie=Aretie.objects.get(pk=id)	
	roles = Tipo.objects.filter(app='retie')
	correos=NotificarCorreo.objects.filter(retie__id=id).values('correo')
	nombres=NotificarCorreo.objects.filter(retie__id=id).values('nombre')
	return render(request, 'seguimiento_visita.html',
		{'nombres':nombres,'correos':correos, 'retie':retie, 'roles':roles, 'model':'retie','app':'seguimiento_retie'},
		)	

@login_required
def reporte(request):	
	contratos=EmpresaContrato.objects.filter(contrato__tipo_contrato__id=12, participa=1,empresa__id=request.user.usuario.empresa.id)
	estados=Estado.objects.filter(app='retie')
	return render(request, 'reporte.html',
		{'estados':estados,'contratos':contratos,'model':'retie','app':'seguimiento_retie'},
		)	

def exportar_informe(request):
	cursor = connection.cursor()
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="Reporte Visitas Retie.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Visitas retie')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_time=workbook.add_format({'border':1,'num_format': 'hh:mm AM/PM'})

		worksheet.write('A1','No. Macro-Contrato', format1)
		worksheet.write('B1','Macro Contrato', format1)
		worksheet.write('C1','Contrato de Obra', format1)
		worksheet.write('D1','Proyecto', format1)
		worksheet.write('E1','Departamento', format1)
		worksheet.write('F1','Municipio', format1)
		worksheet.write('G1','Contratista', format1)
		worksheet.write('H1','Interventor', format1)
		worksheet.write('I1','Fecha Programada', format1)
		worksheet.write('J1','Hora Programada', format1)
		worksheet.write('K1','Fecha de Ejecucion', format1)
		worksheet.write('L1','Estado', format1)
		
		worksheet.set_column('A:A', 24)
		worksheet.set_column('B:B', 24)
		worksheet.set_column('C:C', 22)
		worksheet.set_column('D:D', 40)
		worksheet.set_column('E:E', 30)
		worksheet.set_column('F:F', 30)
		worksheet.set_column('G:G', 25)
		worksheet.set_column('H:H', 25)
		worksheet.set_column('I:I', 19)
		worksheet.set_column('J:J', 19)
		worksheet.set_column('K:K', 19)
		worksheet.set_column('L:L', 24)
				
		row=1
		col=0
		
		mcontrato = request.GET.get('mcontrato', None)
		contratista = request.GET.get('contratista', None)
		proyecto = request.GET.get('proyecto', None)
		estado = request.GET.get('estado', None)

		cursor.callproc('[dbo].[retie_reporte]', [mcontrato,contratista,proyecto,estado])
		columns = cursor.description 
		result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
				
		for r in result:			
			worksheet.write(row,col,r['numero'] ,format2)
			worksheet.write(row,col+1,r['mcontrato'] ,format2)
			worksheet.write(row,col+2,r['no_contrato_obra'] ,format2)
			worksheet.write(row,col+3,r['proyecto'] ,format2)
			worksheet.write(row,col+4,r['departamento'] ,format2)
			worksheet.write(row,col+5,r['municipio'] ,format2)
			worksheet.write(row,col+6,r['contratista'] ,format2)
			worksheet.write(row,col+7,r['interventoria'] ,format2)
			worksheet.write(row,col+8,r['fecha_programada'] ,format_date)
			worksheet.write(row,col+9,r['hora'] ,format_time)
			worksheet.write(row,col+10,r['fecha_ejecutada'] ,format_date)
			worksheet.write(row,col+11,r['estado'] ,format2)						
			row +=1
		
		workbook.close()
		return response
		
	except Exception as e:
		functions.toLog(e,self.nombre_modulo)
#fin visitas retie	

@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			archivo = Soporte.objects.get(pk=request.GET['id'])
			
			filename = ""+str(archivo.soporte)+""
			extension = filename[filename.rfind('.'):]
			f = re.sub('[^A-Za-z0-9 ]+', '', archivo.nombre)
			return functions.exportarArchivoS3(str(archivo.soporte),  f + extension)

		except Exception as e:
			functions.toLog(e,'retie.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

