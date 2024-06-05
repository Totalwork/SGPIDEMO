from django.shortcuts import render
from .models import	SistemaVersion, ZInformacionArchivos

from rest_framework import viewsets, serializers, response
from django.db.models import Q
from django.template import RequestContext
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse,JsonResponse

from logs.models import Logs,Acciones
# from datetime import *
from django.db import transaction,connection
from rest_framework.decorators import api_view

# Create your views here.

class SistemaVersionSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = SistemaVersion
		fields=( 'id','version', 'carpeta', 'fecha', 'activo')

class SistemaVersionViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=SistemaVersion
	queryset = model.objects.all()
	serializer_class = SistemaVersionSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 30

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(SistemaVersionViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			if dato:
				qset=(Q(version__icontains=dato) | Q(carpeta__icontains=dato))			
				queryset = self.model.objects.filter(qset)
						
			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page,many=True)	
				return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})
				
			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = SistemaVersionSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(sistema_version_id=request.DATA['sistema_version_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='deploy.sistema_version',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = SistemaVersionSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='deploy.sistema_version',id_manipulado=instance.id)
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
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='deploy.sistema_version',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 



class InformacionArchivosSerializer(serializers.HyperlinkedModelSerializer):
	
	sistema_version = SistemaVersionSerializer(read_only=True)
	sistema_version_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = SistemaVersion.objects.all())
	class Meta:
		model = ZInformacionArchivos
		fields=( 'id','nombre', 'descripcion', 'sistema_version', 'sistema_version_id', 'archivo')		


class InformacionArchivosViewSet(viewsets.ModelViewSet):
	"""

	"""
	model = ZInformacionArchivos
	queryset = model.objects.all()
	serializer_class = InformacionArchivosSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 50

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(InformacionArchivosViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			if dato:
				qset=(Q(nombre__icontains=dato))			
				queryset = self.model.objects.filter(qset)
						
			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page,many=True)	
				return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})
				
			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = InformacionArchivosSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='deploy.informacion_archivos',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = InformacionArchivosSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='deploy.informacion_archivos',id_manipulado=instance.id)
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
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='deploy.informacion_archivos',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 

def obtener_archivos(request):	
	if request.method == 'GET':		
		try:			
			cursor = connection.cursor()			
			cursor.execute(
				"with query as (select max(ia.id) as id,max(ia.sistema_version_id) as sistema_version_id\
					from [dbo].[deploy_informacion_archivos] as ia\
					where ia.sistema_version_id >= (select id from deploy_sistema_version as vs where vs.version='{}')\
					group by ia.nombre_archivo_id)\
					select sv.id, ia.id as nombre_archivo_id, na.nombre, ia.archivo, ia.descripcion, sv.fecha, sv.activo,\
					(select v2.version \
					from [dbo].[deploy_sistema_version] as v2 \
					where v2.id=(select max(sistema_version_id) from query)) as 'version'\
					from [dbo].[deploy_informacion_archivos] as ia\
					inner join query as q on ia.id=q.id\
					inner join [dbo].[deploy_sistema_version] as sv on ia.sistema_version_id=sv.id\
					inner join [dbo].[deploy_nombre_archivo] as na on ia.nombre_archivo_id=na.id\
					where sv.activo=1".format(request.GET['version']))
									
			columns = cursor.description 
			result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
			
			if len(result)>0:								
				archivos=[]
				for x in list(result):
					archivos.append({
						'id':x['nombre_archivo_id'],
				        'nombre':x['nombre'],
				        'archivo':x['archivo'],
				        'descripcion':x['descripcion'],
				        'sistema_version_id':x['id']			        
					})
						
				lista = {'id':result[0]['id'] , 
							'version': result[0]['version'] , 
							'activo' : result[0]['activo'], 
							'informacion_archivos': archivos}
					
				return JsonResponse({'message':'', 'success':'ok', 'data':lista})

			return JsonResponse({'message':'No se encontraron versiones disponibles', 'success':'ok', 'data':None})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
