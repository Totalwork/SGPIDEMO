from django.shortcuts import render,redirect,render_to_response
from django.urls import reverse
from django.core.serializers import serialize
from rest_framework import viewsets, serializers
from .models import AEquipo,Colaborador,DTarea,DTareaAsignacion,SoporteAsignacionTarea
from .models import TareaActividad,TareaActividadSoporte,DTareaComentario,TareaActividadSoporte

from usuario.views import UsuarioSerializer
from usuario.models import Usuario

from descargo.views import ProyectoLiteSerializer

from empresa.models import Empresa

import re

from estado.views import EstadoSerializer
from tipo.views import TipoSerializer
from estado.models import Estado,Estados_posibles
from tipo.models import Tipo

from django.db.models import Q,Sum,Prefetch,F

from logs.models import Logs,Acciones
from django.template import RequestContext
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

import json
from django.http import HttpResponse,JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models.deletion import ProtectedError

from django.core.paginator import Paginator
from administrador_tarea.tasks import envioNotificacionPunto,envioActividad
from django.contrib.auth.decorators import login_required


from django.db import transaction
from .enumeration import TipoT, EstadoT

from django.db import connection

from datetime import *
import pytz
import zipfile
import os
from io import StringIO
from coasmedas.functions import functions
# Create your views here.

#Api rest para equipo
class EquipoSerializer(serializers.HyperlinkedModelSerializer):

	usuario_responsable=UsuarioSerializer(read_only=True)
	usuario_responsable_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	usuario_administrador=UsuarioSerializer(read_only=True)
	usuario_administrador_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	class Meta:
		model = AEquipo
		fields=('id','nombre','descripcion','usuario_responsable','usuario_responsable_id',
			'usuario_administrador_id','usuario_administrador',)


class EquipoViewSet(viewsets.ModelViewSet):
	
	model=AEquipo
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='administrador_tarea.equipo'
	queryset = model.objects.all()
	serializer_class = EquipoSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(EquipoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			if dato:
				qset = (
					Q(nombre__icontains=dato)
					)
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
	
			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
					'data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = EquipoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(usuario_responsable_id=request.DATA['usuario_responsable_id'],usuario_administrador_id=request.DATA['usuario_administrador_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = EquipoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(usuario_responsable_id=request.DATA['usuario_responsable_id'],usuario_administrador_id=request.DATA['usuario_administrador_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	

#Fin Api rest para equipo



#Api rest para colaborador
class ColaboradorSerializer(serializers.HyperlinkedModelSerializer):

	equipo=EquipoSerializer(read_only=True)
	equipo_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=AEquipo.objects.all())

	usuario=UsuarioSerializer(read_only=True)
	usuario_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	totalTarea=serializers.SerializerMethodField()

	porcentajeRendimiento=serializers.SerializerMethodField()

	class Meta:
		model = Colaborador
		fields=('id','usuario','usuario_id','equipo','equipo_id','totalTarea','porcentajeRendimiento')

	def get_totalTarea(self, obj):
		tareas=DTarea.objects.filter(colaborador_actual_id=obj.id)
		numero=0
		tipoT=TipoT()
		estadoT=EstadoT()
		for item in tareas:
			asignacion=DTareaAsignacion.objects.filter(tarea_id=item.id).last()

			if asignacion is not None:
				if int(asignacion.estado_id)!=int(estadoT.atendida_fueraTiempo) and int(asignacion.estado_id)!=int(estadoT.atendida):
					numero=numero+1
		
		return numero


	def get_porcentajeRendimiento(self, obj):
		
		tareas=DTarea.objects.filter(colaborador_actual_id=obj.id)
		numero=0
		tipoT=TipoT()
		estadoT=EstadoT()

		if tareas is not None:
			for item in tareas:
				if item.estado is not None:
					if int(item.estado['estado__id'])==int(estadoT.atendida_fueraTiempo) or int(item.estado['estado__id'])==int(estadoT.atendida):
						numero=numero+1

		porcentaje=0
		if tareas is not None and len(tareas)>0:
			porcentaje=(numero*100)/len(tareas)	
		
		valor=str(round(porcentaje,2))+'%'	
		return valor


class ColaboradorViewSet(viewsets.ModelViewSet):
	
	model=Colaborador
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='administrador_tarea.colaborador'
	queryset = model.objects.all()
	serializer_class = ColaboradorSerializer	
	paginate_by = 10

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:			
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ColaboradorViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			equipo_id= self.request.query_params.get('equipo_id',None)

			if dato or equipo_id:
				if dato:
					qset = (
						Q(usuario__persona__nombres__icontains=dato) |
						Q(usuario__persona__apellidos__icontains=dato)
						)

				if equipo_id and equipo_id>0:
					if dato: 
						qset=qset &(Q(equipo_id=equipo_id))
					else:
						qset=(Q(equipo_id=equipo_id))

				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
	
			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
					'data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ColaboradorSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(equipo_id=request.DATA['equipo_id'],usuario_id=request.DATA['usuario_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ColaboradorSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(equipo_id=request.DATA['equipo_id'],usuario_id=request.DATA['usuario_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	

#Fin Api rest para colaborador
class AsignacionTareaLiteSerializer(serializers.HyperlinkedModelSerializer):

	# colaborador=ColaboradorSerializer(read_only=True)
	# colaborador_id=serializers.PrimaryKeyRelatedField(queryset=Colaborador.objects.all(), allow_null = True)

	# tarea=TareaSerializer(read_only=True)
	# tarea_id=serializers.PrimaryKeyRelatedField(queryset=DTarea.objects.all(), allow_null = True)

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='Tarea'))

	# solicitante=UsuarioSerializer(read_only=True)
	# solicitante_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	# totalSoporte=serializers.SerializerMethodField()

	class Meta:
		model = DTareaAsignacion
		fields=('id','fecha','estado','estado_id','comentario',)

	# def get_totalSoporte(self, obj):
	# 	tareas=SoporteAsignacionTarea.objects.filter(asignacion_tarea_id=obj.id)	
	# 	return len(tareas)
#Serializador para tarea
class SoporteAsignacionTareaLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = SoporteAsignacionTarea
		fields=('id','nombre','ruta', 'ruta_publica')

class SoporteAsignacionTareaLite2Serializer(serializers.HyperlinkedModelSerializer):

	asignacion_tarea=AsignacionTareaLiteSerializer(read_only=True)
	asignacion_tarea_id=serializers.PrimaryKeyRelatedField(queryset=DTareaAsignacion.objects.all(), allow_null = True)

	class Meta:
		model = SoporteAsignacionTarea
		fields=('id','asignacion_tarea','asignacion_tarea_id','nombre','ruta', 'ruta_publica')	

#Fin de serializador de soporte de tarea

#Serializador para comentarios
class TareaComentarioLiteSerializer(serializers.HyperlinkedModelSerializer):

	usuario=UsuarioSerializer(read_only=True)

	class Meta:
		model = DTareaComentario
		fields=('id','comentario','usuario','fecha','fecha_format')

#Fin de serializador de comentarios de tarea

#Api rest para tarea
class TareaSerializer(serializers.HyperlinkedModelSerializer):

	colaborador_actual=ColaboradorSerializer(read_only=True)
	colaborador_actual_id=serializers.PrimaryKeyRelatedField(queryset=Colaborador.objects.all(), allow_null = True)

	tipo_tarea = TipoSerializer(read_only=True)
	tipo_tarea_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='Tarea'))

	usuario_responsable=UsuarioSerializer(read_only=True)
	usuario_responsable_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	proyecto=ProyectoLiteSerializer(read_only=True,many=True)

	soporte=SoporteAsignacionTareaLiteSerializer(read_only=True,many=True)

	comentarios=TareaComentarioLiteSerializer(read_only=True,many=True)

	class Meta:
		model = DTarea
		fields=('id','asunto','descripcion','fecha_fin','colaborador_actual_id',
			'colaborador_actual','numero','tipo_tarea','tipo_tarea_id','usuario_responsable_id','usuario_responsable',
			'estado','proyecto','soporte','comentarios')	
		

class TareaViewSet(viewsets.ModelViewSet):
	
	model=DTarea
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='administrador_tarea.tarea'
	queryset = model.objects.all()
	serializer_class = TareaSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(TareaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			estado_id= self.request.query_params.get('estado_id',None)
			muro= self.request.query_params.get('muro',None)
			fecha_inicio=self.request.query_params.get('fecha_inicio',None)
			fecha_final=self.request.query_params.get('fecha_final',None)
			proyecto_id=self.request.query_params.get('proyecto_id',None)
			tipoT=TipoT()
			estadoT=EstadoT()

			qset=''
			if muro is not None:
				fecha_hoy=str(datetime.now().strftime('%Y-%m-%d'))
				fecha=date.today() - timedelta(days=7)
				fecha_atras=str(fecha.strftime('%Y-%m-%d'))

				qset=(Q(usuario_responsable__empresa_id=request.user.usuario.empresa.id))

				if dato == '' and (proyecto_id and int(proyecto_id)==0):
					if (fecha_inicio is None or fecha_inicio=='') and (fecha_final is None or fecha_final==''):
						qset=qset&(Q(fecha_fin__range=(fecha_atras,fecha_hoy)))
			else:
				qset=((Q(usuario_responsable_id=request.user.usuario.id)& Q(colaborador_actual_id=None))
				|Q(colaborador_actual__usuario_id=request.user.usuario.id))

			if dato:
				qset = qset & (
					Q(asunto__icontains=dato)
					)
			
			if estado_id and estado_id!='':
				lista_id=[]
				for item in queryset:
					valor=str(estado_id).find(str(item.estado['estado__id']))
					if valor>=0:
						lista_id.append(item.id)
				qset = qset & (
					Q(id__in=(lista_id))
					)

			
			if (fecha_inicio and fecha_inicio!='') or (fecha_final and fecha_final!=''):
				if fecha_final=='' and fecha_inicio!='':
					qset = qset & (
						Q(fecha_fin=fecha_inicio)
						)
				elif fecha_inicio=='' and fecha_final!='':
					qset = qset & (
						Q(fecha_fin=fecha_final)
						)
				elif fecha_inicio!='' and fecha_final!='':
					qset = qset & (
						Q(fecha_fin__range=(fecha_inicio,fecha_final))
						)

			if proyecto_id and int(proyecto_id)>0:
					qset=qset&(Q(proyecto=proyecto_id))
			
			# print qset
			queryset = self.model.objects.filter(qset).order_by('-fecha_fin')

			cant=0
			for item in queryset:
				if item.estado['estado__id']==estadoT.atendida_fueraTiempo or item.estado['estado__id']==estadoT.atendida:
					cant=cant+1
			
			porcentaje=0
			if cant>0:
				# print len(queryset)
				porcentaje=(cant*100)/len(queryset)

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':{'datos':serializer.data,'porcentaje':round(porcentaje,2)}})
	
			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
					'data':{'datos':serializer.data,'porcentaje':round(porcentaje,2)}})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				tipoT=TipoT()
				estadoT=EstadoT()
				if int(request.DATA['colaborador_actual_id'])==0:
					request.DATA['colaborador_actual_id']=None

				if int(request.DATA['tipo_tarea_id'])==0:
					request.DATA['tipo_tarea_id']=tipoT.propia
				else:
					request.DATA['tipo_tarea_id']=tipoT.grupo

				colaboradores = []	
				if request.DATA.get('listado_colaboradores', None):					
					colaboradores = json.loads(request.DATA['listado_colaboradores'])

				if len(colaboradores) == 0:
					colaboradores.append(request.DATA['colaborador_actual_id'])

				for colaborador_id in colaboradores:
					request.DATA['colaborador_actual_id']=colaborador_id
					serializer = TareaSerializer(data=request.DATA,context={'request': request})							
					if serializer.is_valid():

						serializer.save(colaborador_actual_id=colaborador_id,tipo_tarea_id=request.DATA['tipo_tarea_id'],usuario_responsable_id=request.DATA['usuario_responsable_id'])
						logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
						logs_model.save()

						objecto_numero=DTarea.objects.get(pk=serializer.data['id'])
						if request.DATA['lista_proyecto']!='':
							listado=str(request.DATA['lista_proyecto']).split(',')
							if listado and len(listado)>0:
								objecto_numero.proyecto.add(*listado)
						
						objecto_numero.numero=str(datetime.now().strftime('%Y%m%d'))+str(serializer.data['id'])
						
						objecto_numero.save()
						logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
						logs_model.save()	

						fecha=datetime.now().strftime('%Y-%m-%d')
						asignacion=DTareaAsignacion(colaborador_id=colaborador_id,tarea_id=serializer.data['id'],fecha=fecha,estado_id=estadoT.solicitada,comentario=request.DATA['comentario'],solicitante_id=request.DATA['usuario_responsable_id'])		
						asignacion.save()
						logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo='administrador_tarea.asignacion_tarea',id_manipulado=asignacion.pk)
						logs_model.save()

						soportes=request.FILES.getlist('soporte[]')
						
						if soportes:
							i = 0
							for sp in soportes:							
								s= SoporteAsignacionTarea(ruta=sp, nombre=sp.name, asignacion_tarea_id=asignacion.pk)
								s.save()				

					
					else:
						transaction.savepoint_rollback(sid)
						print(serializer.errors)
						return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
				 		'data':''},status=status.HTTP_400_BAD_REQUEST)

				transaction.savepoint_commit(sid)
				if len(colaboradores) == 1:
					return Response({'message':'El registro ha sido guardado exitosamente.','success':'ok', 'data':serializer.data},status=status.HTTP_201_CREATED)	
				else:	
					return Response({'message':'Los registros han sido guardado exitosamente.','success':'ok', 'data':serializer.data},status=status.HTTP_201_CREATED)	
			except Exception as e:				
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				if request.DATA['colaborador_actual_id']=='null':
					request.DATA['colaborador_actual_id']=None
				serializer = TareaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(colaborador_actual_id=request.DATA['colaborador_actual_id'],tipo_tarea_id=request.DATA['tipo_tarea_id'],usuario_responsable_id=request.DATA['usuario_responsable_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()

					if request.DATA['lista_proyecto']!='':
						listado=str(request.DATA['lista_proyecto']).split(',')
						objecto_numero=DTarea.objects.get(pk=instance.id)
						if listado and len(listado)>0:
							objecto_numero.proyecto.clear()
							objecto_numero.proyecto.add(*listado)
							objecto_numero.save()
					else:
						objecto_numero=DTarea.objects.get(pk=instance.id)
						objecto_numero.proyecto.clear()


					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:				
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	

#Fin Api rest para tarea


#Api rest para asignacion de tarea
class AsignacionTareaSerializer(serializers.HyperlinkedModelSerializer):

	colaborador=ColaboradorSerializer(read_only=True)
	colaborador_id=serializers.PrimaryKeyRelatedField(queryset=Colaborador.objects.all(), allow_null = True)

	tarea=TareaSerializer(read_only=True)
	tarea_id=serializers.PrimaryKeyRelatedField(queryset=DTarea.objects.all(), allow_null = True)

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='Tarea'))

	solicitante=UsuarioSerializer(read_only=True)
	solicitante_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	totalSoporte=serializers.SerializerMethodField()

	class Meta:
		model = DTareaAsignacion
		fields=('id','tarea','tarea_id','colaborador_id','colaborador','fecha',
			'estado','estado_id','comentario','solicitante','solicitante_id','totalSoporte',)

	def get_totalSoporte(self, obj):
		tareas=SoporteAsignacionTarea.objects.filter(asignacion_tarea_id=obj.id)	
		return len(tareas)


class AsignacionTareaViewSet(viewsets.ModelViewSet):
	
	model=DTareaAsignacion
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='administrador_tarea.asignacion_tarea'
	queryset = model.objects.all()
	serializer_class = AsignacionTareaSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(AsignacionTareaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			tarea_id= self.request.query_params.get('tarea_id',None)
			qset=None

			if dato:
				qset = (
					Q(comentario__icontains=dato)
					)

			if tarea_id and tarea_id>0:
				if dato:
					qset=qset & (
					Q(tarea_id=tarea_id)
					)
				else:
					qset = (
					Q(tarea_id=tarea_id)
					)

				if qset != None:
					queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
	
			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
					'data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				request.DATA['fecha']=datetime.now().strftime('%Y-%m-%d')
				if request.DATA['colaborador_id']=='None':
					request.DATA['colaborador_id']=None
				serializer = AsignacionTareaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(colaborador_id=request.DATA['colaborador_id'],tarea_id=request.DATA['tarea_id'],estado_id=request.DATA['estado_id'],solicitante_id=request.DATA['solicitante_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()

					if request.DATA['lista_id'] and request.DATA['lista_id']!='':
						listado=str(request.DATA['lista_id']).split(',')
						envioNotificacionPunto.delay(listado,serializer.data['id'])


					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = AsignacionTareaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(colaborador_id=request.DATA['colaborador_id'],tarea_id=request.DATA['tarea_id'],estado_id=request.DATA['estado_id'],solicitante_id=request.DATA['solicitante_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	

#Fin Api rest para asignacion de tarea

#Api rest para soporte de asignacion de tarea
class SoporteAsignacionTareaSerializer(serializers.HyperlinkedModelSerializer):

	asignacion_tarea=AsignacionTareaSerializer(read_only=True)
	asignacion_tarea_id=serializers.PrimaryKeyRelatedField(queryset=DTareaAsignacion.objects.all(), allow_null = True)

	class Meta:
		model = SoporteAsignacionTarea
		fields=('id','asignacion_tarea','asignacion_tarea_id','nombre','ruta', 'ruta_publica')

class SoporteAsignacionTareaViewSet(viewsets.ModelViewSet):
	
	model=SoporteAsignacionTarea
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='administrador_tarea.soporte_asignacion_tarea'
	queryset = model.objects.all()
	serializer_class = SoporteAsignacionTareaLite2Serializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(SoporteAsignacionTareaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			tarea_id= self.request.query_params.get('tarea_id',None)
			asignacion_tarea_id= self.request.query_params.get('asignacion_tarea_id',None)
			qset=None

			if dato:
				qset = (
					Q(nombre__icontains=dato)
					)

			if tarea_id and tarea_id>0:
				if dato:
					qset=qset & (
					Q(asignacion_tarea__tarea_id=tarea_id)
					)
				else:
					qset = (
					Q(asignacion_tarea__tarea_id=tarea_id)
					)

			if asignacion_tarea_id and asignacion_tarea_id>0:
				if dato or tarea_id and tarea_id>0:
					qset=qset & (
					Q(asignacion_tarea_id=asignacion_tarea_id)
					)
				else:
					qset = (
					Q(asignacion_tarea_id=asignacion_tarea_id)
					)

			if qset !=None:
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
	
			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
					'data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = SoporteAsignacionTareaSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(asignacion_tarea_id=request.DATA['asignacion_tarea_id'],ruta=self.request.FILES.get('ruta'))
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = SoporteAsignacionTareaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(asignacion_tare_id=request.Data['asignacion_tare_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		try:
			sid = transaction.savepoint()
			instance = self.get_object()
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	

#Fin Api rest para soporte de asignacion de tarea



#Api rest para soporte de asignacion de tarea
class TareaComentarioSerializer(serializers.HyperlinkedModelSerializer):

	tarea=TareaSerializer(read_only=True)
	tarea_id=serializers.PrimaryKeyRelatedField(queryset=DTarea.objects.all(), allow_null = True)

	usuario=UsuarioSerializer(read_only=True)
	usuario_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	class Meta:
		model = DTareaComentario
		fields=('id','tarea','tarea_id','comentario','usuario','usuario_id','fecha','fecha_format')

class TareaComentarioViewSet(viewsets.ModelViewSet):
	
	model=DTareaComentario
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='administrador_tarea.comentraio_tarea'
	queryset = model.objects.all()
	serializer_class = TareaComentarioSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(TareaComentarioViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			tarea_id= self.request.query_params.get('tarea_id',None)
			qset=None

			if dato:
				qset = (
					Q(comentario__icontains=dato)
					)

			if tarea_id and tarea_id>0:
				if dato:
					qset=qset & (
					Q(tarea_id=tarea_id)
					)
				else:
					qset = (
					Q(tarea_id=tarea_id)
					)


			if qset !=None:
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
	
			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
					'data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				request.DATA['fecha']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				serializer = TareaComentarioSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(tarea_id=request.DATA['tarea_id'],usuario_id=request.DATA['usuario_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = SoporteAsignacionTareaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(tarea_id=request.DATA['tarea_id'],usuario_id=request.DATA['usuario_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		try:
			sid = transaction.savepoint()
			instance = self.get_object()
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	

#Fin Api rest para soporte de asignacion de tarea

#Api rest para soporte de asignacion de tarea
class TareaActividadSoporteLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = TareaActividadSoporte
		fields=('id','nombre','ruta',)

#Api rest para tarea actividad
class TareaActividadSerializer(serializers.HyperlinkedModelSerializer):

	tipo=TipoSerializer(read_only=True)
	tipo_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Tipo.objects.filter(app='Tarea_actividad'))

	solicitante=UsuarioSerializer(read_only=True)
	solicitante_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	usuario_inivitado=UsuarioSerializer(read_only=True,many=True)

	soporte=TareaActividadSoporteLiteSerializer(read_only=True,many=True)

	class Meta:
		model = TareaActividad
		fields=('id','tipo','tipo_id','asunto','solicitante','solicitante_id','fecha','fecha_format','fecha_transaccion',
			'lugar','usuario_inivitado','soporte')


class TareaActividadViewSet(viewsets.ModelViewSet):
	
	model=TareaActividad
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='administrador_tarea.tarea_actividad'
	queryset = model.objects.all()
	serializer_class = TareaActividadSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(TareaActividadViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			if dato:
				if dato:
					qset = (
						Q(asunto__icontains=dato) 
						)
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
	
			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
					'data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				request.DATA['fecha_transaccion']=datetime.now().strftime('%Y-%m-%d')
				serializer = TareaActividadSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(tipo_id=request.DATA['tipo_id'],solicitante_id=request.DATA['solicitante_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()

					if request.DATA['listado_usuarios']!='':
						modelactividad=TareaActividad.objects.get(pk=serializer.data['id'])
						listado=str(request.DATA['listado_usuarios']).split(',')
						modelactividad.usuario_inivitado.add(*listado)
						modelactividad.save()
						#envio de correo de la actividad						
						envioActividad.delay(listado,serializer.data['id'])

					soportes=request.FILES.getlist('soporte[]')
					
					if soportes:
						for sp in soportes:							
							s= TareaActividadSoporte(ruta=sp, nombre=sp.name, tarea_actividad_id=serializer.data['id'])
							s.save()
							logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo='administrador_tarea.actividad_tarea',id_manipulado=s.pk)
							logs_model.save()
							

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = TareaActividadSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(tipo_id=request.DATA['tipo_id'],solicitante_id=request.DATA['solicitante_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()

					if request.DATA['invitados_id']!='':
						listado=str(request.DATA['invitados_id']).split(',')
						objecto_numero=TareaActividad.objects.get(pk=instance.id)
						if listado and len(listado)>0:
							objecto_numero.usuario_inivitado.clear()
							objecto_numero.usuario_inivitado.add(*listado)
							objecto_numero.save()
					else:
						objecto_numero=TareaActividad.objects.get(pk=instance.id)
						objecto_numero.usuario_inivitado.clear()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	

#Fin Api rest para tarea actividad



#Api rest para tarea actividad
class TareaActividadSoporteSerializer(serializers.HyperlinkedModelSerializer):

	tarea_actividad=TareaActividadSerializer(read_only=True)
	tarea_actividad_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=TareaActividad.objects.all())

	class Meta:
		model = TareaActividadSoporte
		fields=('id','tarea_actividad','tarea_actividad_id','nombre','ruta')


class TareaActividadSoporteViewSet(viewsets.ModelViewSet):
	
	model=TareaActividadSoporte
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='administrador_tarea.tarea_actividad_soporte'
	queryset = model.objects.all()
	serializer_class = TareaActividadSoporteSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(TareaActividadSoporteViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			if dato:
				if dato:
					qset = (
						Q(ruta__icontains=dato) 
						)
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
	
			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
					'data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = TareaActividadSoporteSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(tarea_actividad_id=request.DATA['tarea_actividad_id'],ruta=self.request.FILES.get('ruta'))
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()							

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = TareaActividadSoporteSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(tarea_actividad_id=request.DATA['tarea_actividad_id'],ruta=self.request.FILES.get('ruta'))
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	

#Fin Api rest para tarea actividad


@transaction.atomic
def cambiar_estado(request):
	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		tipoT=TipoT()
		estadoT=EstadoT()

		fecha=datetime.now().strftime('%Y-%m-%d')

		for item in respuesta['lista']:
			tarea=DTarea.objects.get(pk=item['id'])
			asignacion=None

			if tarea.estado['estado__id']!=estadoT.no_leida:
				if int(tarea.tipo_tarea_id)==tipoT.propia:
					asignacion=DTareaAsignacion(colaborador_id=None,tarea_id=item['id'],fecha=fecha,estado_id=estadoT.no_leida,comentario=None,solicitante_id=respuesta['usuario_responsable_id'])		
					asignacion.save()
				else:
					asignacion=DTareaAsignacion(colaborador_id=respuesta['usuario_responsable_id'],tarea_id=item['id'],fecha=fecha,estado_id=estadoT.no_leida,comentario='',solicitante_id=tarea.solicitante_id)		
					asignacion.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='administrador_tarea.asignacion_tarea',id_manipulado=asignacion.pk)
				logs_model.save()				

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha registrado correctamente','success':'ok',
				'data':''})
	except ProtectedError:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error',
			'data':''})		
	except Exception as e:
		functions.toLog(e,'administrador_tarea.asignacion_tarea')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	


def listado_grupo(request):

	try:
		filtro_equipo=request.GET['filtro_equipo']
		filtro_tarea=request.GET['filtro_tarea']
		equipo_id=request.GET['equipo_id']
		lista_id=request.GET['lista_id']
		fecha_inicio=request.GET['fecha_inicio']
		fecha_final=request.GET['fecha_final']
		colaborador_id=request.GET['colaborador_id']
		pagina=int(request.GET['pagina'])-1
		ListPrincipal=[]
		ListEquipos=[]
		listado2=[]
		registro=10
		paginacion=int(pagina)*registro
		valor_total=0
		
		if filtro_equipo!='':
			listado2=AEquipo.objects.filter((Q(usuario_responsable_id=request.user.usuario.id)|Q(usuario_administrador_id=request.user.usuario.id))&(Q(nombre__icontains=filtro_equipo)))
		else:
			listado2=AEquipo.objects.filter(Q(usuario_responsable_id=request.user.usuario.id)|Q(usuario_administrador_id=request.user.usuario.id))
		
		for x in listado2:
			valor_total=valor_total+x.cantidadTareas
			lista={
				'id':x.id,
				'nombre':x.nombre,
				'descripcion':x.descripcion,
				'cantidad':x.cantidadTareas,
				'porcentaje':x.porcentajeTareas,
			}
			ListEquipos.append(lista)

		ListTareas=[]
		listado=None
		if int(equipo_id)>0:
			listado=AEquipo.objects.filter((Q(usuario_responsable_id=request.user.usuario.id)|Q(usuario_administrador_id=request.user.usuario.id))&(Q(pk=equipo_id)))
		else:
			listado=AEquipo.objects.filter(Q(usuario_responsable_id=request.user.usuario.id)|Q(usuario_administrador_id=request.user.usuario.id))

		for item in listado:
			if int(colaborador_id)>0:
				colaboradores=Colaborador.objects.filter(equipo_id=item.id,pk=colaborador_id)
			else:
				colaboradores=Colaborador.objects.filter(equipo_id=item.id)
			for item2 in colaboradores:
				qset=(Q(colaborador_actual_id=item2.id))
				tarea=[]
				if filtro_tarea!='':
					qset=qset & (Q(asunto__icontains=filtro_tarea))
					
				if (fecha_inicio and fecha_inicio!='') or (fecha_final and fecha_final!=''):
					if fecha_final=='' and fecha_inicio!='':
						qset = qset & (
							Q(fecha_fin=fecha_inicio)
							)
					elif fecha_inicio=='' and fecha_final!='':
						qset = qset & (
							Q(fecha_fin=fecha_final)
							)
					elif fecha_inicio!='' and fecha_final!='':
						qset = qset & (
							Q(fecha_fin__range=(fecha_inicio,fecha_final))
							)

				tarea=DTarea.objects.filter(qset)

				if len(tarea)>0:
					for x in tarea:
						if lista_id!='':
							valor1=str(lista_id).find(str(x.estado['estado__id']))
							# print valor1
							if valor1>=0:
								lista={
									'id':x.id,
									'estado':x.estado,
									'asunto':x.asunto,
									'descripcion':x.descripcion,
									'fecha_fin':x.fecha_fin,
									'nombre_completo':str(x.usuario_responsable.persona.nombres)+' '+str(x.usuario_responsable.persona.apellidos),
								}
								ListTareas.append(lista)
						else:
							lista={
								'id':x.id,
								'estado':x.estado,
								'asunto':x.asunto,
								'descripcion':x.descripcion,
								'fecha_fin':x.fecha_fin,
								'nombre_completo':str(x.usuario_responsable.persona.nombres)+' '+str(x.usuario_responsable.persona.apellidos),
							}
							ListTareas.append(lista)

		#ListTareas=DTarea.objects.filter()		
		ListPrincipal.append({'valor_total':valor_total,'Equipos':list(ListEquipos),'Tareas':ListTareas[int(paginacion):int(paginacion)+int(registro)]})
			
		return JsonResponse({'count':len(ListTareas),'results':{'message':'','success':'ok','data':ListPrincipal[0]}})

	except Exception as e:
		functions.toLog(e,'administrador_tarea')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	


def guardar_colaboradores(request):

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		for item in respuesta['lista']:
			consulta=Colaborador.objects.filter(equipo_id=respuesta['equipo_id'],usuario_id=item['id'])
			if len(consulta)==0:
				colaborador=Colaborador(equipo_id=respuesta['equipo_id'],usuario_id=item['id'])
				colaborador.save()
			
		return JsonResponse({'message':'El registro se ha guardando correctamente','success':'ok',
					'data':''})

	except Exception as e:
		functions.toLog(e,'administrador_tarea')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	

def porcentaje_equipo(request):
	cursor = connection.cursor()
	
	try:
		lista=request.GET['equipo_id']

		cursor.callproc('[administrador_tarea].[porcentaje_grafica]',[int(request.user.usuario.id),int(lista),])

		result_set = cursor.fetchall()
		lista=[]
		listado_total=[]
		for x in list(result_set):			
			lista.append([x[1],round(x[3],2)])
				
		return JsonResponse({'message':'','success':'ok','data':lista})	

	except Exception as e:
		functions.toLog(e,'administrador_tarea')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()


def porcentaje_barra(request):
	try:
		ListTareas=DTarea.objects.filter(colaborador_actual__usuario_id=request.user.usuario.id)
		Lista=[]
		listado_total=[]
		tipoT=TipoT()
		estadoT=EstadoT()

		for item in ListTareas:
			porcentaje=0
			if item.estado['estado__id']==estadoT.atendida or item.estado['estado__id']==estadoT.atendida_fueraTiempo:
				porcentaje=100

			lista={
				'name':item.fecha_fin,
				'y':porcentaje,
				'drilldown':item.fecha_fin
			}

			listado_total.append(lista)

				
		return JsonResponse({'message':'','success':'ok','data':listado_total})	

	except Exception as e:
		functions.toLog(e,'administrador_tarea')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	


def download_zip(request):
	try:
		t = datetime.now()
		myListArchivos = request.GET['archivo']

		myListArchivos = str(myListArchivos).split(',')

		nombreArchivo = str(t.year)+str(t.month)+str(t.day)+str(t.hour)+str(t.minute)+str(t.second)		
		newpath = r'media/administrador_tarea/descargas/'+str(nombreArchivo)+"/"
			
		if not os.path.exists(newpath):
			os.makedirs(newpath)

		carpetaNoExiste = ''
		reemplazar_por = ''

		for i in myListArchivos:
			soporte=SoporteAsignacionTarea.objects.get(pk=i)
			functions.descargarArchivoS3(str(soporte.ruta), str(newpath) ,soporte.nombre)				
				
			
		zip_subdir = nombreArchivo
		zip_filename = "%s.zip" % zip_subdir

		s = StringIO.StringIO()

		zf = zipfile.ZipFile(s, "w")			
		buscar = 'media/administrador_tarea/descargas/'
			
		for dirname, subdirs, files in os.walk(newpath):
			zf.write(dirname)
			for filename in files:
				zf.write(os.path.join(dirname, filename))

			# Must close zip for all contents to be written
		zf.close()
			# Grab ZIP file from in-memory, make response with correct MIME-type
		resp = HttpResponse(s.getvalue(), content_type="application/zip")
			# # ..and correct content-disposition
		resp['Content-Disposition'] = 'attachment; filename='+str(nombreArchivo)+'.zip'

		return resp

	except Exception as e:
		functions.toLog(e,'administrador_tarea')
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@login_required
def administrador_tarea(request):
		Listado_equipos=AEquipo.objects.filter(Q(usuario_responsable_id=request.user.usuario.id)|Q(usuario_administrador_id=request.user.usuario.id))
		ListEquipos=Colaborador.objects.filter(usuario_id=request.user.usuario.id)
		ListPendientes=[]
		ListRechazados=[]
		tipoT=TipoT()
		estadoT=EstadoT()
		cont_pen=0
		cont_recha=0
		for item in ListEquipos:
			Tareas=DTarea.objects.filter(colaborador_actual_id=item.id)
			cont=0
			cont2=0
			for item2 in Tareas:
				if int(item2.estado['estado__id'])!=int(estadoT.atendida_fueraTiempo) and int(item2.estado['estado__id'])!=int(estadoT.atendida) and int(item2.estado['estado__id'])!=int(estadoT.rechazada):
					cont=cont+1
					cont_pen=cont_pen+1
				elif int(item2.estado['estado__id'])==int(estadoT.rechazada):
					cont2=cont2+1
					cont_recha=cont_recha+1

			if cont>0:
				lista={
					'id':item.id,
					'nombre_equipo':item.equipo.nombre,
					'contador':cont
				}
				ListPendientes.append(lista)

			if cont2>0:
				lista={
					'id':item.id,
					'nombre_equipo':item.equipo.nombre,
					'contador':cont2
				}
				ListRechazados.append(lista)	

		fecha_hoy=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		cantidad=TareaActividad.objects.filter(fecha__gte=fecha_hoy)
		
		return render(request, 'administrador_tarea/index.html',{'model':'administrador_tarea','app':'administrador_tarea','Pendientes':ListPendientes,'Rechazados':ListRechazados,'Cont_pendiente':cont_pen,'Cont_rechazado':cont_recha,'Total':cont_recha+cont_pen,'Equipos':Listado_equipos,'cant_agenda':len(cantidad)})



@login_required
def grupo(request):
		ListUsuario=Usuario.objects.filter(empresa_id=request.user.usuario.empresa_id)
		ListEmpresa=Empresa.objects.all()
		ListEquipo=AEquipo.objects.filter(Q(usuario_responsable_id=request.user.usuario.id)|Q(usuario_administrador_id=request.user.usuario.id))

		return render(request, 'administrador_tarea/grupo.html',{'model':'grupo','app':'administrador_tarea','Usuarios':ListUsuario,'Empresas':ListEmpresa,'Equipos':ListEquipo})

@login_required
def detalle_tarea(request,id_tarea):
		tarea=DTarea.objects.get(pk=id_tarea)
		colaborador_id=None
		fecha_hoy=datetime.now().strftime('%Y-%m-%d')
		tipoT=TipoT()
		estadoT=EstadoT()
		
		if tarea.tipo_tarea_id==tipoT.grupo:
			colaborador_id=tarea.colaborador_actual_id

		estado_posibles=Estados_posibles.objects.filter(actual=tarea.estado['estado__id'])

		sw=0
		for item in estado_posibles:
			if item.siguiente_id==estadoT.leida:
				sw=1
		if sw==1:
			asignacion=DTareaAsignacion(colaborador_id=colaborador_id,tarea_id=id_tarea,fecha=fecha_hoy,estado_id=estadoT.leida,comentario=' Actualizacion de tarea a estado Leida',solicitante_id=request.user.usuario.id)
			asignacion.save()
		return render(request, 'administrador_tarea/detalle_tarea.html',{'model':'administrador_tarea','app':'administrador_tarea','id_tarea':id_tarea,'tarea':tarea})

@login_required
def nuevo_punto(request,id_tarea):
		tarea=DTarea.objects.get(pk=id_tarea)
		ListEmpresa=Empresa.objects.all()
		estado_posibles=None
		tipoT=TipoT()
		estadoT=EstadoT()

		if tarea.tipo_tarea_id==tipoT.grupo:
			estado_posibles=Estados_posibles.objects.filter(actual_id=tarea.estado['estado__id'])
		else:
			estado_posibles=Estados_posibles.objects.filter((Q(actual_id=tarea.estado['estado__id']))&(~(Q(siguiente_id=estadoT.rechazada))))

		return render(request, 'administrador_tarea/nuevo_punto.html',{'model':'administrador_tarea','app':'administrador_tarea','id_tarea':id_tarea,'tarea':tarea,'estado_posible':estado_posibles,'Empresas':ListEmpresa,'tipo_resignada':estadoT.reasignada})


@login_required
def agenda(request):
		ListTipo=Tipo.objects.filter(app='Tarea_actividad')
		ListEmpresa=Empresa.objects.all()
		return render(request, 'administrador_tarea/agenda.html',{'model':'administrador_tarea','app':'administrador_tarea','Tipos':ListTipo,'Empresas':ListEmpresa})


@login_required
def muro(request):
		return render(request, 'administrador_tarea/muro.html',{'model':'administrador_tarea','app':'administrador_tarea'})



@login_required
def tarea(request,id_tarea):
	tarea=DTarea.objects.get(pk=id_tarea)
	colaborador_id=None
	fecha_hoy=datetime.now().strftime('%Y-%m-%d')
	tipoT=TipoT()
	if tarea.colaborador_actual and tarea.tipo_tarea_id==tipoT.grupo:
		colaborador_id=tarea.colaborador_actual.id

	return render(request, 'administrador_tarea/tarea.html',{'model':'administrador_tarea','app':'administrador_tarea','id_tarea':id_tarea,'tarea':tarea})


@login_required
def edicion_actividad(request,id_actividad):
		Tipos=Tipo.objects.filter(app='Tarea_actividad')
		ListEmpresa=Empresa.objects.all()
		return render(request, 'administrador_tarea/edicion_actividad.html',{'model':'administrador_tarea','app':'administrador_tarea','id_actividad':id_actividad,'tipo':Tipos,'Empresas':ListEmpresa})


@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			archivo = SoporteAsignacionTarea.objects.get(pk=request.GET['id'])
			
			filename = str(archivo.ruta)
			extension = filename[filename.rfind('.'):]
			nombre = re.sub('[^A-Za-z0-9 ]+', '', archivo.nombre)
			return functions.exportarArchivoS3(str(archivo.ruta), nombre + extension)

		except Exception as e:
			functions.toLog(e,'factura.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def VerSoporteActividad(request):
	if request.method == 'GET':
		try:

			archivo = TareaActividadSoporte.objects.get(pk=request.GET['id'])			
			return functions.exportarArchivoS3(str(archivo.ruta))

		except Exception as e:
			functions.toLog(e,'contrato.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)