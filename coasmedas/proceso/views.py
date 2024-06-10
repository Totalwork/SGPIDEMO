# -*- coding: utf-8 -*-
from django.shortcuts import render
#, render_to_response
from django.db import transaction
from logs.models import Logs,Acciones
from rest_framework import viewsets, serializers, response
from django.db.models import Q
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
from django.contrib.contenttypes.models import ContentType
from .models import AProceso
from .models import BItem
from .models import CPermisoEmpresaItem
from .models import DVinculo
from .models import FProcesoRelacion, GProcesoRelacionDato, HSoporteProcesoRelacionDato, ECampoInforme
from .models import INotificacionVencimiento, JSeguidorProcesoRelacion

from empresa.models import Empresa
from proyecto.models import Proyecto_empresas, Proyecto
from usuario.models import Usuario
from contrato.models import EmpresaContrato, Contrato
from parametrizacion.models import Departamento, Municipio, Cargo
from factura.models import Factura

from django.db import IntegrityError
import operator
from decimal import *
from datetime import datetime, date, time, timedelta
import xlsxwriter
from django.contrib.auth.decorators import login_required
from parametrizacion.models import Funcionario
from usuario.models import Persona
from adminMail.models import Mensaje
from .tasks import sendMail
from django.conf import settings
from coasmedas.functions import functions
from solicitudservicio.models import BSolicitud
from giros.models import DEncabezadoGiro
import re
# Create your views here.

class ContentTypeSerializer(serializers.HyperlinkedModelSerializer):
	#url = serializers.HyperlinkedIdentityField(view_name="myapp:contenttype-detail")
	class Meta:
		model=ContentType
		fields=('id','app_label','name','model')

class EmpresaSerializer(serializers.HyperlinkedModelSerializer):
	esDisenador = serializers.BooleanField(default=False)
	esProveedor = serializers.BooleanField(default=False)
	esContratista = serializers.BooleanField(default=False)
	esContratante = serializers.BooleanField(default=False)
	#logo = serializers.ImageField(required=False)

	class Meta:
		model = Empresa
		fields=('id','nombre','nit','direccion','logo','esDisenador','esProveedor','esContratista','esContratante')

#Modelo AProceso
#Codigo Backend para comunicacion con la base de datos

class ProcesoSerializer(serializers.HyperlinkedModelSerializer):
	tablaReferencia = ContentTypeSerializer(read_only=True)
	tablaReferencia_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=ContentType.objects.all())	
	tablaForanea = ContentTypeSerializer(read_only=True)
	tablaForanea_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=ContentType.objects.all())	
	empresas = EmpresaSerializer(read_only=True,many=True)
	empresas_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=Empresa.objects.all(),many=True)
	pasoAPaso = serializers.BooleanField(default=True)	
	
	class Meta:
		model=AProceso
		fields=('url','id','nombre','activo','apuntador','tablaReferencia','tablaReferencia_id',
			'campoEnlace','tablaForanea','tablaForanea_id','campoEnlaceTablaForanea','empresas',
			'empresas_id','pasoAPaso')
	

	def create(self, validated_data):		
		tablaReferencia=validated_data.pop('tablaReferencia_id')		
		tablaForanea=validated_data.pop('tablaForanea_id')
		empresasObjects =[]		
		#recorrer las empresas
		proceso=AProceso.objects.create(
			nombre=validated_data.pop('nombre'),
			activo=validated_data.pop('activo'),
			campoEnlace=validated_data.pop('campoEnlace'),
			campoEnlaceTablaForanea=validated_data.pop('campoEnlaceTablaForanea'),
			tablaReferencia=tablaReferencia,
			tablaForanea=tablaForanea,
			)
		empresas_list = validated_data.pop('empresas_id')
		for empresa in empresas_list:
			empresasObjects.append(empresa)
		proceso.empresas.add(*empresasObjects)		
		return proceso

	def update(self,instance, validated_data):
		# print validated_data
		# print 'tabla referencia'
		# print validated_data.get('tablaReferencia_id').id
		# print 'tabla referencia instancia: '
		# print instance.tablaReferencia.id
		empresasObjects =[]		
		#recorrer las empresas
		

		instance.nombre=validated_data.get('nombre'),
		instance.activo=validated_data.get('activo'),
		instance.campoEnlace=validated_data.get('campoEnlace'),
		instance.campoEnlaceTablaForanea=validated_data.get('campoEnlaceTablaForanea'),
		#instance.tablaReferencia=ContentType.objects.get(id=validated_data.get('tablaReferencia_id').id),
		#instance.tablaForanea=ContentType.objects.get(id=validated_data.get('tablaForanea_id').id),
			
		empresas_list = validated_data.get('empresas_id')
		for empresa in empresas_list:
			empresasObjects.append(empresa)
		instance.empresas.clear()
		instance.empresas.add(*empresasObjects)		
		return instance



class ProcesoViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de procesos, puede utilizar el parametro <b>{dato=[texto a buscar]}</b>, a traves del cual, se podra buscar por todo o parte del nombre del proceso.<br/>
		Puede utilizar el parametro <b>{empresa=[id de la empresa]}</b> para ubicar los procesos que la empresa puede acceder.
	"""
	model=AProceso
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = ProcesoSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo='Procesos.procesos'
	

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ProcesoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			empresa = self.request.query_params.get('empresa', None)
			mensaje=''	
			
			if (dato or empresa):
				if (dato and empresa):
					qset=Q(nombre__icontains=dato) & Q(empresas=empresa)
				if dato:
					qset=Q(nombre__icontains=dato)
				if empresa:
					qset = Q(empresas=empresa)

				queryset = self.model.objects.filter(qset)

			if queryset.count()==0:
				mensaje='No se encontraron Items con los criterios de busqueda ingresados'

			if ignorePagination:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
				'data':serializer.data})				
			else:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':mensaje,'success':'ok',
					'data':serializer.data})
				
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
					'data':serializer.data})					
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ProcesoSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save()
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)
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
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			logs_model=self.model_log(
				usuario_id=request.user.usuario.id,
				accion=self.model_acciones.accion_borrar,
				nombre_modelo=self.nombre_modulo,
				id_manipulado=instance.id
			)
			logs_model.save()	
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update (self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ProcesoSerializer(instance,data=request.DATA,
					context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save()	
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_actualizar,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=instance.id
					)
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



# Modelo: BItem
# Codigo Backend para comunicacion con la base de datos

#serializador para Usuario
class UsuarioSimpleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.IntegerField(read_only=True)
	nombre = serializers.SerializerMethodField('_nombre',read_only=True)
	empresa = EmpresaSerializer(read_only=True)
	class Meta:
		model = Usuario
		fields = ('id','nombre','empresa')

	def _nombre(self,obj):
		usuario=Usuario.objects.get(pk=obj.id)
		return usuario.persona.nombres + ' ' + usuario.persona.apellidos

#Defino otro ProcesoSerializer como ProcesoSerializerItem para que el json 
#no tenga ruidos en la consulta de items
class ProcesoSerializerItem(serializers.HyperlinkedModelSerializer):
	class Meta:
		model= AProceso
		fields=('url','id','nombre')


class ItemSerializer(serializers.HyperlinkedModelSerializer):
	proceso = ProcesoSerializerItem(read_only=True)
	proceso_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=AProceso.objects.all())
	orden = serializers.IntegerField(default=1)
	activo = serializers.BooleanField(default=True)
	afectarImplementacionesAnteriores = serializers.BooleanField(default=True)

	responsable = UsuarioSimpleSerializer(read_only=True)
	responsable_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=Usuario.objects.all(),allow_null=True)
	
	class Meta:
		model = BItem
		fields=('url','id','proceso','proceso_id','orden','descripcion','tipoDato','notificacionCumplimiento',
			'tieneVencimiento','tieneObservacion','tieneSoporte','soporteObligatorio','activo',
			'responsable','responsable_id','afectarImplementacionesAnteriores')	

class ItemViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de Items, puede utilizar el parametro <b>{dato=[texto a buscar]}</b>, a traves del cual, se podra buscar por todo o parte del nombre del item.<br/>
		Puede utilizar el parametro <b>{proceso=[id del proceso]}</b> para ubicar los items de determinado proceso.<br/>
		Utilice el parametro <b>{ignorePagination=1}</b> para obtener los resultados sin paginacion.<br/>
	"""
	model=BItem
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = ItemSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo='Procesos.item'
	

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		#import pdb; pdb.set_trace()
		try:
			queryset = super(ItemViewSet, self).get_queryset().order_by('orden')
			dato = self.request.query_params.get('dato', None)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			proceso = self.request.query_params.get('proceso', None)
			mensaje=''
			
			if (dato or proceso):
				if dato:
					qset=(Q(descripcion__icontains=dato))
				if proceso:
					if dato:
						qset = qset & (Q(proceso=proceso))
					else:
						qset = (Q(proceso=proceso))

				queryset = self.model.objects.filter(qset).order_by('orden')
			
			if queryset.count()==0:
				mensaje='No se encontraron Items con los criterios de busqueda ingresados'	

			if ignorePagination:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'count':queryset.count(),'results':{'message':mensaje,'success':'ok',
				'data':serializer.data}})				
			else:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':mensaje,'success':'ok',
					'data':serializer.data})
				
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
					'data':serializer.data})					
		except Exception as e:
			print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ItemSerializer(data=request.DATA,context={'request': request})
				#print serializer.is_valid()
				#print serializer.data
				if serializer.is_valid():
					serializer.save(proceso_id=request.DATA['proceso_id'],
						responsable_id = request.DATA['responsable_id'])
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)
					logs_model.save()
					#transaction.savepoint_commit(sid)
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
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			logs_model=self.model_log(
				usuario_id=request.user.usuario.id,
				accion=self.model_acciones.accion_borrar,
				nombre_modelo=self.nombre_modulo,
				id_manipulado=instance.id
			)
			logs_model.save()	
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update (self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ItemSerializer(instance,data=request.DATA,
					context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(proceso_id=request.DATA['proceso_id'],
						responsable_id = request.DATA['responsable_id'])	
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_actualizar,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=instance.id
					)
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

# Modelo: CPermisoEmpresaItem
# Codigo Backend para comunicacion con la base de datos

#Se elabora un serializador personalizado para la empresa, con el animo de reducir la cantidad de
#datos en el json.
class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Empresa
		fields=('id','nombre')

class PermisoEmpresaItemSerializer(serializers.HyperlinkedModelSerializer):
	empresa = EmpresaLiteSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Empresa.objects.all())
	item = ItemSerializer(read_only=True)
	item_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=BItem.objects.all())
	lectura = serializers.BooleanField(default=True)
	escritura = serializers.BooleanField(default=False)
	
	class Meta:
		model = CPermisoEmpresaItem
		fields=('url','id','empresa','empresa_id','item','item_id','lectura','escritura')	
		validators=[
			serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=('empresa_id','item_id'),
				message=('La empresa ya tiene asignado el permiso que intenta registrar')
			)
		]



class PermisoEmpresaItemViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de Items y permisos por empresa, puede utilizar el parametro <b>{dato=[texto a buscar]}</b>, a traves del cual, se podra buscar por todo o parte del nombre del item.<br/>
		Puede utilizar el parametro <b>{proceso=[id del proceso]}</b> para ubicar los items de determinado proceso y ver los permisos asignados.<br/>
		Puede utilizar el parametro <b>{empresa=[id de la empresa]}</b> para acceder a los items de cierta empresa.<br/>
		Utilice el parametro <b>{ignorePagination=1}</b> para obtener los resultados sin paginacion.<br/>
	"""
	model=CPermisoEmpresaItem
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = PermisoEmpresaItemSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo='Procesos.PermisoEmpresaItem'
	

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(PermisoEmpresaItemViewSet, self).get_queryset().order_by('item__orden')
			dato = self.request.query_params.get('dato', None)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			proceso = self.request.query_params.get('proceso', None)
			empresa = self.request.query_params.get('empresa', None)
			mensaje=''
			
			if (dato or proceso or empresa):
				if dato:
					qset=(Q(item__descripcion__icontains=dato))
				if proceso:
					if dato:
						qset = qset & (Q(item__proceso=proceso))
					else:
						qset = (Q(item__proceso=proceso))
				if empresa:
					if dato or proceso:
						qset = qset & (Q(empresa=empresa))
					else:
						qset = (Q(empresa=empresa))

				queryset = self.model.objects.filter(qset).order_by('item__orden')
			
			if queryset.count()==0:
				mensaje='No se encontraron Items con los criterios de busqueda ingresados'	

			if ignorePagination:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
				'data':serializer.data})				
			else:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':mensaje,'success':'ok',
					'data':serializer.data})
				
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
					'data':serializer.data})					
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = PermisoEmpresaItemSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(
						empresa_id=request.DATA['empresa_id'],
						item_id=request.DATA['item_id']
					)
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail',
						 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
				'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic			
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			logs_model=self.model_log(
				usuario_id=request.user.usuario.id,
				accion=self.model_acciones.accion_borrar,
				nombre_modelo=self.nombre_modulo,
				id_manipulado=instance.id
			)
			logs_model.save()	
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update (self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = PermisoEmpresaItemSerializer(instance,data=request.DATA,
					context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(
						empresa_id=request.DATA['empresa_id'],
						item_id=request.DATA['item_id']
					)	
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_actualizar,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=instance.id
					)
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

# Modelo: DVinculo
# Codigo Backend para comunicacion con la base de datos
class VinculoSerializer(serializers.HyperlinkedModelSerializer):
	procesoOrigen = ProcesoSerializerItem(read_only=True)
	procesoOrigen_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=AProceso.objects.all())
	procesoDestino = ProcesoSerializerItem(read_only=True)
	procesoDestino_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=AProceso.objects.all())	
	itemVinculado = ItemSerializer(read_only=True)
	itemVinculado_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=BItem.objects.all())

	class Meta:
		model = DVinculo
		fields=('url','id','procesoOrigen','procesoOrigen_id','procesoDestino',
			'procesoDestino_id','itemVinculado','itemVinculado_id')

		validators=[
			serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=('procesoOrigen_id','procesoDestino_id','itemVinculado_id'),
				message=('Los procesos origen y destino seleccionados ya estan vinculados por el item indicado')
			)
		]

class VinculoViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de vinculos establecidos entre procesos.<br/>
		Puede utilizar el parametro <b>{procesoOrigen=[id del proceso]}</b> para identificar los items vinculados a traves de este procesoOrigen.<br/>
		Puede utilizar el parametro <b>{procesoDestino=[id del proceso]}</b> para identificar los items vinculados a traves de este procesoDestino.<br/>
		Puede utilizar el parametro <b>{item=[id del item]}</b> para identificar en que procesos se encuentra vinculado el item.<br/>
		Utilice el parametro <b>{ignorePagination=1}</b> para obtener los resultados sin paginacion.<br/>
	"""
	model=DVinculo
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = VinculoSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo='Procesos.Vinculo'	

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},
				status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(VinculoViewSet, self).get_queryset().order_by('itemVinculado__orden')
			procesoOrigen = self.request.query_params.get('procesoOrigen', None)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			procesoDestino = self.request.query_params.get('procesoDestino', None)
			itemVinculado = self.request.query_params.get('itemVinculado', None)
			mensaje=''
			
			if (procesoOrigen or procesoDestino or itemVinculado):
				if procesoOrigen:
					qset=(Q(procesoOrigen=procesoOrigen))
				if procesoDestino:
					if procesoOrigen:
						qset = qset & (Q(procesoDestino=procesoDestino))
					else:
						qset = (Q(procesoDestino=procesoDestino))
				if itemVinculado:
					if procesoOrigen or procesoDestino:
						qset = qset & (Q(itemVinculado=itemVinculado))
					else:
						qset = (Q(itemVinculado=itemVinculado))

				queryset = self.model.objects.filter(qset).order_by('itemVinculado__orden')
			
			if queryset.count()==0:
				mensaje='No se encontraron Items con los criterios de busqueda ingresados'	

			if ignorePagination:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
				'data':serializer.data})				
			else:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':mensaje,'success':'ok',
					'data':serializer.data})
				
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
					'data':serializer.data})					
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = VinculoSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(
						procesoOrigen_id=request.DATA['procesoOrigen_id'],
						procesoDestino_id=request.DATA['procesoDestino_id'],
						itemVinculado_id=request.DATA['itemVinculado_id']
					)
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail',
						 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
				'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic			
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			logs_model=self.model_log(
				usuario_id=request.user.usuario.id,
				accion=self.model_acciones.accion_borrar,
				nombre_modelo=self.nombre_modulo,
				id_manipulado=instance.id
			)
			logs_model.save()	
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update (self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = VinculoSerializer(instance,data=request.DATA,
					context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(
						procesoOrigen_id=request.DATA['procesoOrigen_id'],
						procesoDestino_id=request.DATA['procesoDestino_id'],
						itemVinculado_id=request.DATA['itemVinculado_id']
					)	
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_actualizar,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=instance.id
					)
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

# Modelo: FProcesoRelacion
# Codigo Backend para comunicacion con la base de datos
class ProcesoRelacionSerializer(serializers.HyperlinkedModelSerializer):
	proceso = ProcesoSerializer(read_only=True)
	proceso_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=AProceso.objects.all())
	idApuntador = serializers.IntegerField(required=True)
	idTablaReferencia = serializers.IntegerField(required=True)

	class Meta:
		model = FProcesoRelacion
		fields=('url','id','proceso','proceso_id','idApuntador','idTablaReferencia')

		validators=[
			serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=('proceso_id','idApuntador','idTablaReferencia'),
				message=('El proceso seleccionado ya se encuentra implementado sobre el proyecto/contrato indicado')
			)
		]
# Modelo: Departamento
class DepartamentoSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model=Departamento
		fields=('url','id','nombre')

# Modelo: Municipio
class MunicipioSerializer(serializers.HyperlinkedModelSerializer):
	departamento = DepartamentoSerializer(read_only=True)
	class Meta:
		model=Municipio
		fields=('url','id','departamento','nombre')

# Modelo: Proyecto
class ProyectoSerializer(serializers.HyperlinkedModelSerializer):
	municipio=MunicipioSerializer(read_only=True)
	class Meta:
		model = Proyecto
		fields=('url','id','municipio','nombre')

# Modelo: Contrato
class ContratoSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model=Contrato
		fields=('url','id','numero','nombre')


class ProcesoRelacionViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de implementaciones del proceso, donde:<br/>
		idApuntador: corresponde al id del proyecto o contrato, segun el apuntador del proceso.<br/>
		idTablaReferencia: corresponde al id de la tablaReferencia del proceso.<br/>
		puede utilizar el parametro <b>{usuario=[id del usuario]}</b> para filtrar contratos o proyectos segun los permisos de acceso del usuario.<br/>
		Puede utilizar el parametro <b>{proceso=[id del proceso]}</b> para identificar los id de los proyectos o contratos implementados sobre el proceso.<br/>
		Puede utilizar el parametro <b>{idApuntador=[id del proyecto o contrato]}</b> para identificar las implementaciones sobre el proyecto o contrato.<br/>
		Puede utilizar el parametro <b>{idTablaReferencia=[id del registro de la tabla referencia del proceso]}.</b><br/>
		Utilice el parametro <b>{ignorePagination=1}</b> para obtener los resultados sin paginacion.<br/>
		<b>Importante:</b> el parametro <b>{usuario=[id del usuario]}</b> es obligatorio en todas las consultas a esta API, debido a que es necesario validar acceso a los datos<br/>
		si este parametro no es recibido, la API intentará tomar el usuario actual, si no se encuentra el registro se enviará un error 500.<br/>
		Puede utilizar el parametro <b>{apuntador=[1/2]}</b> donde con 1 retorna los proyectos implementados al proceso y con 2 retorna
		los contratos implementados al proceso.<br/>
		Puede utilizar el parametro <b>{noImplementado=[1]}</b> para saber los proyectos/contratos con los cuales no
		esta implementado el proceso.</br>
		Puede usar el parametro <b>{dato=[texto]}</b> con el que se puede buscar los proyectos/contratos, implementados o no,
		a traves de su nombre.<b>Importante:</b> Este parametro solo funcionara si se usa en combinacion con el parametro apuntador.<br/>
		Puede utilizar el parametro <b>{verDetalle=1}</b> que retorna una lista con el detalle de la implementacion.
		<b>Importante:</b> Este parametro solo funcionara si se recibe el parametro proceso y el parameto apuntador.<br/>
		Puede utilizar el parametro <b>{responsables=[1]}</b> para traer los funcionarios responsables del proyecto
		involucrado en el seguimiento actual. <b>Importante: </b> Este parametro solo funciona si se recibe el
		parametro procesoRelacionId=[id del proceso].

	"""
	model=FProcesoRelacion
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = ProcesoRelacionSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo='Procesos.procesoRelacion'	

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},
				status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ProcesoRelacionViewSet, self).get_queryset()
			usuario = self.request.query_params.get('usuario', request.user.id)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			proceso = self.request.query_params.get('proceso', None)
			idApuntador = self.request.query_params.get('idApuntador', None)
			idTablaReferencia = self.request.query_params.get('idTablaReferencia', None)
			apuntador = self.request.query_params.get('apuntador',None)
			noImplementado = self.request.query_params.get('noImplementado',None)
			dato = self.request.query_params.get('dato',None)
			mcontrato = self.request.query_params.get('mcontrato',None)
			verDetalle = self.request.query_params.get('verDetalle',None)
			procesoRelacionId = self.request.query_params.get('procesoRelacionId',None)
			responsables = self.request.query_params.get('responsables',None)
			pagina = self.request.query_params.get('pagina',1)
			mensaje=''

			#import pdb; pdb.set_trace()
			if procesoRelacionId and responsables:
				pr = FProcesoRelacion.objects.filter(id=procesoRelacionId).values(
					'proceso__apuntador','idApuntador')
				if pr[0]['proceso__apuntador']=='1':
					#proyecto
					funcionarios = Proyecto.objects.filter(id=pr[0]['idApuntador'],
						funcionario__activo=True).order_by('funcionario__empresa__nombre').values(
						'funcionario__persona__nombres','funcionario__persona__apellidos',
						'funcionario__persona__correo','funcionario__empresa__nombre',
						'funcionario__cargo__nombre')
				else:	
					#contrato
					funcionarios = Proyecto.objects.filter(contrato__id=pr[0]['idApuntador'],
						funcionario__activo=True).order_by('funcionario__empresa__nombre').values(
						'funcionario__persona__nombres','funcionario__persona__apellidos',
						'funcionario__persona__correo','funcionario__empresa__nombre',
						'funcionario__cargo__nombre')
				if funcionarios.count()>0:
					mensaje=''
				else:
					mensaje='No se encontraron responsables asociados al proyecto/contrato'
				return Response ({'results':{'message':mensaje,'data':funcionarios,'success':'ok'}})				

			
			retorno =[]
			if proceso and apuntador and verDetalle:
				#import pdb; pdb.set_trace()
				usuarioApp = Usuario.objects.get(user=usuario)
				objProceso = AProceso.objects.get(id=proceso)
				qset = Q(proceso=objProceso)
				
				if apuntador == '1':
					proyectoEmpresasPrevio = Proyecto_empresas.objects.filter(empresa=usuarioApp.empresa).values('proyecto__id')
					qset = qset & (Q(idApuntador__in=proyectoEmpresasPrevio))
				if apuntador == '2':
					contratoEmpresaPrecio = EmpresaContrato.objects.filter(empresa=usuarioApp.empresa).values('contrato__id')
					qset = qset & (Q(idApuntador__in=contratoEmpresaPrecio))
				if idTablaReferencia:
					qset = qset & (Q(idTablaReferencia=idTablaReferencia))
				desde=(int(pagina)-1)*10
				hasta=int(pagina)*10
				queryProcesoRelacion = FProcesoRelacion.objects.filter(qset)
				listaProcesoRelacion = queryProcesoRelacion.order_by('id').values()[desde:hasta]
				cantidadRegistros = queryProcesoRelacion.count()

				
				contadorRegistros = 0
				if apuntador == '1':
					qset = Q(empresa=usuarioApp.empresa)
					if dato or idApuntador:
						if dato:
							qset = qset & (Q(proyecto__nombre__icontains=dato))
							listaDeBusqueda = queryProcesoRelacion.values()
						else:
							listaDeBusqueda=listaProcesoRelacion
						if idApuntador:
							qset = qset & (Q(proyecto__id=idApuntador))
					else:
						listaDeBusqueda=listaProcesoRelacion	

					proyectoEmpresas = Proyecto_empresas.objects.filter(qset).values('proyecto__id')

					for pr in listaDeBusqueda:
						
						qset=Q(proyecto__id_in=proyectoEmpresas) & Q(empresa=usuarioApp.empresa)
						qset = qset & (Q(proyecto__id=pr['idApuntador']))
						
						proy = Proyecto_empresas.objects.filter(qset).values('proyecto__id',
							'proyecto__mcontrato__nombre',
							'proyecto__municipio__departamento__nombre',
							'proyecto__municipio__nombre','proyecto__nombre')
						if proy:

							contadorRegistros = contadorRegistros + 1	
							if objProceso.tablaForanea:
								modeloReferencia = ContentType.objects.get(pk=objProceso.tablaForanea.id)
								modeloReferencia = ContentType.objects.get(app_label=modeloReferencia.app_label,
									model = modeloReferencia.model).model_class()
								#import pdb; pdb.set_trace()
								elemento = modeloReferencia.objects.filter(
									id=pr['idTablaReferencia']).values(objProceso.etiqueta)
								etiquetaElemento= elemento[0][objProceso.etiqueta]
							else:
								etiquetaElemento = proy[0]['proyecto__nombre']
							qsprd = GProcesoRelacionDato.objects.filter(procesoRelacion=
									FProcesoRelacion.objects.get(id=pr['id']))
							tareas= float(qsprd.count())
							tareasCumplidas = float(qsprd.filter(estado=1).count())
							porcentaje = round((tareasCumplidas / tareas)*100,2)
							retorno.append({'id':pr['id'],'proyecto':proy,'elemento':etiquetaElemento,
								'elemento_id':pr['idTablaReferencia'],'porcentaje':porcentaje})
				elif apuntador == '2':

					qset = Q(empresa=usuarioApp.empresa)
					if dato or idApuntador:
						if dato:
							qset = qset & (Q(contrato__nombre__icontains=dato) | 
								Q(contrato__numero__icontains=dato))
							listaDeBusqueda = queryProcesoRelacion.values()
						else:
							listaDeBusqueda=listaProcesoRelacion
						if idApuntador:
							qset = qset & (
								Q(contrato__id=idApuntador)	
								)
					else:
						listaDeBusqueda=listaProcesoRelacion
					empresasContrato = EmpresaContrato.objects.filter(qset).values('contrato__id')
					for pr in listaDeBusqueda:
						qset=Q(contrato__id_in=empresasContrato) & Q(empresa=usuarioApp.empresa)
						qset = qset & (Q(contrato__id=pr['idApuntador']))
						ct = EmpresaContrato.objects.filter(qset).values(
							'contrato__id','contrato__numero','contrato__nombre')

						if ct:
							contadorRegistros = contadorRegistros + 1
							if objProceso.tablaForanea:
								#import pdb; pdb.set_trace()
								modeloReferencia = ContentType.objects.get(pk=objProceso.tablaForanea.id)
								modeloReferencia = ContentType.objects.get(app_label=modeloReferencia.app_label,
									model = modeloReferencia.model).model_class()
								elemento = modeloReferencia.objects.filter(
									id=pr['idTablaReferencia']).values(objProceso.etiqueta)
								etiquetaElemento= elemento[0][objProceso.etiqueta]
							else:
								elemento = ct
								etiquetaElemento = elemento[0]['contrato__nombre']
							qsprd = GProcesoRelacionDato.objects.filter(procesoRelacion=
									FProcesoRelacion.objects.get(id=pr['id']))
							tareas= float(qsprd.count())
							tareasCumplidas = float(qsprd.filter(estado=1).count())
							porcentaje = int((tareasCumplidas / tareas)*100)

							retorno.append({'id':pr['id'],'contrato':ct,'elemento':etiquetaElemento,
								'elemento_id':pr['idTablaReferencia'],'porcentaje':porcentaje})
						
				if dato or idApuntador:
					#import pdb; pdb.set_trace()
					cantidadRegistros = contadorRegistros
					if desde==0:
						desde=1
					retorno=retorno[desde-1:hasta-1]
				
				if str(pagina) == '1':
					previo=None
				else:
					paginaPrevia=int(pagina)-1
					previo=settings.SERVER_URL+request.get_full_path().replace('pagina='+str(pagina),'pagina='+str(paginaPrevia))

				if str(pagina)==str(hasta):
					siguiente=None
				else:
					paginaSiguiente=int(pagina)+1
					siguiente=settings.SERVER_URL+request.get_full_path().replace('pagina='+str(pagina),'pagina='+str(paginaSiguiente))

				return Response ({'count':cantidadRegistros,
					'next':siguiente,
					'previous':previo,
					'results':{'message':mensaje,'data':retorno,'success':'ok'}})
				
			
			if (proceso or idApuntador or idTablaReferencia):
				if proceso:
					qset =(Q(proceso=proceso))
				if idApuntador:
					if proceso:
						qset = qset & (Q(idApuntador=idApuntador))
					else:
						mensaje='el parametro proceso es obligatorio al utilizar el parametro idApuntador'
				if idTablaReferencia:
					if proceso and idApuntador:
						qset = qset & (Q(idTablaReferencia=idTablaReferencia))		
					else:
						mensaje='los parametros proceso y idApuntador son obligatorios al utilizar el parametro idTablaReferencia'
				if mensaje=='':		
					#print qset
					queryset = self.model.objects.filter(qset)
				else:
					return Response({'message':mensaje,'status':'error','data':''})
			if queryset.count()>=0:
				#filtrar los resultados del queryset de acuerdo a los proyectos/contratos
				#que puede ver la empresa asociada al usuario que accede al recurso
				array=[]
				proyectos=[]
				contratos=[]
				usuarioApp = Usuario.objects.get(user=usuario)	

				for row in queryset.values():
					procesoAnalizado = AProceso.objects.get(id=row['proceso_id'])
					if int(procesoAnalizado.apuntador) == 1:
						#la implementacion esta sobre un proyecto, ahora es necesario validar
						#que el usuario actual tenga acceso al proyecto
						permisosAlProyecto=Proyecto_empresas.objects.filter(
							proyecto=row['idApuntador'],
							empresa=usuarioApp.empresa
						)
						if permisosAlProyecto:
							array.append(row['id'])
							proyectos.append(row['idApuntador'])
					else:
						if int(procesoAnalizado.apuntador) == 2:
							#la implementacion esta sobre un contrato, ahora es necesario validar
							#que el usuario actual tenga acceso al contrato
							permisosAlContrato = EmpresaContrato.objects.filter(
								contrato=row['idApuntador'],
								empresa = usuarioApp.empresa
							)
							if permisosAlContrato:
								array.append(row['id'])
								contratos.append(row['idApuntador'])
				if apuntador:				
					if apuntador == '1':
						
						#devolver proyectos implementados
						# queryset= Proyecto.objects.filter(
						# 	id=FProcesoRelacion.objects.filter(id__in=array).values('idApuntador')
						# )
						qset = (Q(id__in=FProcesoRelacion.objects.filter(id__in=array).values('idApuntador')))
						if noImplementado=='1':
							qs=Proyecto.objects.exclude(
								id__in=FProcesoRelacion.objects.filter(id__in=array).values_list('idApuntador',flat=True)
							).values_list('id',flat=True)
							
							qs1=Proyecto_empresas.objects.filter(proyecto__in=qs,
								empresa=usuarioApp.empresa).values_list('proyecto',flat=True)
							
							qset=Q(id__in=qs1)
						if dato:
							qset = qset & (Q(nombre__icontains=dato))	
						if mcontrato:
							qset = qset & (Q(mcontrato=mcontrato))

						queryset=Proyecto.objects.filter(qset)
						

					else:
						#devolver contratos implementados
						# queryset= Contrato.objects.filter(
						# 	id=FProcesoRelacion.objects.filter(id__in=array).values('idApuntador')
						# )
						qset = (Q(id__in=FProcesoRelacion.objects.filter(id__in=array).values('idApuntador')))
						
						if noImplementado == '1':
							#print FProcesoRelacion.objects.filter(id__in=array).values_list('idApuntador',flat=True)
							qs=Contrato.objects.exclude(
								id__in=FProcesoRelacion.objects.filter(id__in=array).values_list('idApuntador',flat=True)
							).values_list('id',flat=True)
							
							qs1=EmpresaContrato.objects.filter(contrato__in=qs,
								empresa=usuarioApp.empresa).values_list('contrato',flat=True)
							
							qset=(Q(id__in=qs1))
						if dato:
							
							qset = qset & (Q(nombre__icontains=dato) | Q(numero__icontains=dato))	
						if mcontrato:
							qset = qset & (Q(mcontrato=mcontrato))
								
						queryset=Contrato.objects.filter(qset)
				else:
					queryset = FProcesoRelacion.objects.filter(id__in=array)


			if queryset.count()==0:
				mensaje='No se encontraron registros con los criterios de busqueda ingresados'

			if apuntador:
				if apuntador == '1':
					serializer = ProyectoSerializer(queryset,many=True, context={'request': request})
				else:
					serializer = ContratoSerializer(queryset,many=True, context={'request': request})	
			else:	
				serializer = self.get_serializer(queryset,many=True, context={'request': request})
			
			if ignorePagination:					
				return Response({'message':mensaje,'success':'ok',
				'data':serializer.data})				
			else:

				page = self.paginate_queryset(queryset)
				if page is not None:
					if apuntador:
						if apuntador == '1':
							serializer = ProyectoSerializer(page,many=True, context={'request': request})
						else:
							serializer = ContratoSerializer(page,many=True, context={'request': request})	
					else:	
						serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':mensaje,'success':'ok',
					'data':serializer.data})
				
				#serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
					'data':serializer.data})					
		except Exception as e:
			#print ('error!!!!!!!!!!!!')
			#print(pr['id'])
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ProcesoRelacionSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(proceso_id=request.DATA['proceso_id'])
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail',
						 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)				
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
				'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic			
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			logs_model=self.model_log(
				usuario_id=request.user.usuario.id,
				accion=self.model_acciones.accion_borrar,
				nombre_modelo=self.nombre_modulo,
				id_manipulado=instance.id
			)
			logs_model.save()	
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update (self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ProcesoRelacionSerializer(instance,data=request.DATA,
					context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(proceso_id=request.DATA['proceso_id'])	
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_actualizar,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=instance.id
					)
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


# Modelo: GProcesoRelacionDato



#serializador simplificado para procecesoRelacionDato
class ProcesoRelacionSimpleSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = FProcesoRelacion
		fields=('url','id')

# Codigo Backend para comunicacion con la base de datos
class ProcesoRelacionDatoSerializer(serializers.HyperlinkedModelSerializer):
	procesoRelacion = ProcesoRelacionSimpleSerializer(read_only=True)
	procesoRelacion_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=FProcesoRelacion.objects.all())
	item = ItemSerializer(read_only=True)
	item_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=BItem.objects.all())
	escritura = serializers.SerializerMethodField('_permiso',read_only=True)
	cantidadSoportes = serializers.SerializerMethodField('_cantidadSoportes',read_only=True)
	itemDesHabilitado = serializers.SerializerMethodField('_desHabilitado',read_only=True)


	def _permiso(self,obj):
		usuarioApp = Usuario.objects.get(user=self.context['request'].user)
		permisos = CPermisoEmpresaItem.objects.filter(empresa=usuarioApp.empresa,
			item=obj.item).values('escritura')
		return permisos[0]['escritura']


	def _cantidadSoportes(self,obj):
		return HSoporteProcesoRelacionDato.objects.filter(procesoRelacionDato=obj).count()

	def _desHabilitado(self,obj):
		proceso = AProceso.objects.get(pk=obj.procesoRelacion.proceso.id)
		if proceso.pasoAPaso:
			if obj.item.orden < 2:
				return False
			else:
				it = GProcesoRelacionDato.objects.filter(procesoRelacion=obj.procesoRelacion,
					item__orden=(obj.item.orden - 1)).values('estado')
				if it:
					if it[0]['estado']=='1':
						return False
					else:
						return True
				else:
					return False

		else:
			return False



	class Meta:
		model = GProcesoRelacionDato
		fields=('url','id','procesoRelacion','procesoRelacion_id','item','item_id',
			'fechaVencimiento','observacion','valor','estado','escritura','cantidadSoportes','itemDesHabilitado')

		validators=[
			serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=('procesoRelacion_id','item_id'),
				message=('La implementacion del proceso ya tiene un conjunto de datos asociados')
			)
		]

class ProcesoRelacionDatoViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista con los datos asociados a la implementacion del proceso:<br/>
		debe utilizar el parametro <b>{usuario=[id del usuario]}</b> para validar acceso a la información.<br/>
		puede utilizar el parametro <b>{procesoRelacion=[id del procesoRelacion]}</b> para identificar los datos de la implementacion solicitada.<br/>
		Utilice el parametro <b>{ignorePagination=1}</b> para obtener los resultados sin paginacion.<br/>
		<b>Importante:</b> el parametro <b>{usuario=[id del usuario]}</b> es obligatorio en todas las consultas a esta API, debido a que es necesario validar acceso a los datos<br/>
		si este parametro no es recibido, la API intentará tomar el usuario actual.<br/>
		Utilice el parametro <b>{vinculados=[1]} para que retornar un json adicional llamado vinculados 
		que tiene los ProcesoRelacionDato de los items vinculados al proceso actual.</b><br/>
		utilice el parametro <b>{item=[id del item]}</b> para retornar el detalle en funcion de un item particular.

	"""
	model=GProcesoRelacionDato
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = ProcesoRelacionDatoSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo='Procesos.procesoRelacionDatos'	

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},
				status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			# import pdb; pdb.set_trace()
			queryset = super(ProcesoRelacionDatoViewSet, self).get_queryset().order_by('item__orden')
			usuario = self.request.query_params.get('usuario', request.user.id)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			procesoRelacion = self.request.query_params.get('procesoRelacion', None)
			vinculados = self.request.query_params.get('vinculados',None)
			item = self.request.query_params.get('item',None)
			mensaje=''
			tareas=0
			tareasCumplidas=0			
			porcentaje=0
			etiquetaPorcentaje=0
			procesosRelacionDatos=[]
			usuarioApp = Usuario.objects.get(user=usuario)

			#import pdb; pdb.set_trace()
			if (procesoRelacion):
				itemsPermitidos=CPermisoEmpresaItem.objects.filter(empresa=usuarioApp.empresa).values('item__id')
				condicion= (Q(procesoRelacion=procesoRelacion)) & (Q(item__id__in=itemsPermitidos))
				if item:
					condicion = condicion & (Q(item__id=item))
				queryset=self.model.objects.filter(condicion).order_by('item__orden')			
				procesoRelacionObj =  FProcesoRelacion.objects.get(id=procesoRelacion)

				tareas = (GProcesoRelacionDato.objects.filter(procesoRelacion=procesoRelacion).count())
				tareasCumplidas = (GProcesoRelacionDato.objects.filter(procesoRelacion=procesoRelacion,estado=1).count())
				if tareas>0:
					porcentaje = (float(tareasCumplidas) / float(tareas))*100
					etiquetaPorcentaje =int((float(tareasCumplidas) / float(tareas))*100)
				if vinculados:
					qsetVinculados = DVinculo.objects.filter(procesoDestino=procesoRelacionObj.proceso,
						itemVinculado__id__in=itemsPermitidos).order_by('itemVinculado__orden').values(
						'procesoOrigen__id','procesoOrigen__nombre','procesoDestino__id',
						'itemVinculado__id') 
					for vinculo in qsetVinculados:	
						prdv = GProcesoRelacionDato.objects.filter(
							procesoRelacion__proceso__id=vinculo['procesoOrigen__id'],
							procesoRelacion__idApuntador=procesoRelacionObj.idApuntador,
							procesoRelacion__idTablaReferencia=procesoRelacionObj.idTablaReferencia,
							item__id__in=itemsPermitidos).order_by('item__orden').values(
							'id','estado','procesoRelacion__id','item__descripcion',
							'item__tieneSoporte','fechaVencimiento','observacion','valor')
						procesosRelacionDatos.append({'proceso':vinculo['procesoOrigen__nombre'],
							'procesosRelacionDatos':prdv})


			if queryset.count()==0:
				mensaje='No se encontraron registros con los criterios de busqueda ingresados'	
			#import pdb; pdb.set_trace()
			proveedores=Empresa.objects.filter(esContratista=True).order_by('nombre').values('id','nombre')		
			if ignorePagination:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
				'data':{'listado':serializer.data,'porcentaje':porcentaje,
					'etiquetaPorcentaje':etiquetaPorcentaje,'vinculados':procesosRelacionDatos}})				
			else:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':mensaje,'success':'ok',
					'data':{'listado':serializer.data,'porcentaje':porcentaje,
					'etiquetaPorcentaje':etiquetaPorcentaje,'vinculados':procesosRelacionDatos}})
				
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
					'data':{'listado':serializer.data,'porcentaje':porcentaje,
					'etiquetaPorcentaje':etiquetaPorcentaje,'vinculados':procesosRelacionDatos}})					
		except Exception as e:
			#print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ProcesoRelacionDatoSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(
						procesoRelacion_id=request.DATA['procesoRelacion_id'],
						item_id=request.DATA['item_id']
					)
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail',
						 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
				'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic			
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			logs_model=self.model_log(
				usuario_id=request.user.usuario.id,
				accion=self.model_acciones.accion_borrar,
				nombre_modelo=self.nombre_modulo,
				id_manipulado=instance.id
			)
			logs_model.save()	
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update (self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ProcesoRelacionDatoSerializer(instance,data=request.DATA,
					context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(
						procesoRelacion_id=request.DATA['procesoRelacion_id'],
						item_id=request.DATA['item_id'])	

					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_actualizar,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=instance.id
					)
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



# Modelo: HSoporteProcesoRelacionDato

#serializador ProcesoRelacionDatoSimpleSerializer
class ProcesoRelacionDatoSimpleSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = GProcesoRelacionDato
		fields=('url','id')


# Codigo Backend para comunicacion con la base de datos
class SoporteProcesoRelacionDatoSerializer(serializers.HyperlinkedModelSerializer):
	procesoRelacionDato = ProcesoRelacionDatoSimpleSerializer(read_only=True)
	procesoRelacionDato_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=GProcesoRelacionDato.objects.all())
	#soporte = serializers.FileField(required=True)
	

	class Meta:
		model = HSoporteProcesoRelacionDato
		fields=('url','id','procesoRelacionDato','procesoRelacionDato_id','nombre','documento')

class SoporteProcesoRelacionDatoViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista con los soportes asociados a al dato registrado en la implementacion del proceso:<br/>
		debe utilizar el parametro <b>{usuario=[id del usuario]}</b> para validar acceso a la información.<br/>
		puede utilizar el parametro <b>{procesoRelacionDato=[id del procesoRelacionDato]}</b> para identificar los datos de la implementacion solicitada.<br/>
		Utilice el parametro <b>{ignorePagination=1}</b> para obtener los resultados sin paginacion.<br/>
		<b>Importante:</b> el parametro <b>{usuario=[id del usuario]}</b> es obligatorio en todas las consultas a esta API, debido a que es necesario validar acceso a los datos<br/>
		si este parametro no es recibido, la API intentará tomar el usuario actual.<br/>
	"""
	model=HSoporteProcesoRelacionDato
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = SoporteProcesoRelacionDatoSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo='Procesos.soporteProcesoRelacionDatos'	

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},
				status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(SoporteProcesoRelacionDatoViewSet, self).get_queryset()
			usuario = self.request.query_params.get('usuario', request.user.id)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			procesoRelacionDato = self.request.query_params.get('procesoRelacionDato', None)
			giro = self.request.query_params.get('giro',None)
			mensaje=''
			#import pdb; pdb.set_trace()
			if (procesoRelacionDato):
				queryset=self.model.objects.filter(procesoRelacionDato=procesoRelacionDato)
			elif giro:
				#busco el procesoRelacion de ese giro
				contrato_id=DEncabezadoGiro.objects.filter(id=giro).values('contrato__id')

				if contrato_id:
					procesoRelacion_id = FProcesoRelacion.objects.filter(
						proceso__id=2,idTablaReferencia=giro,idApuntador=contrato_id[0]['contrato__id']
						).values('id')
					#busco el procesoRelacionDato de este procesoRelacion
					if procesoRelacion_id:
						procesoRelacionDato_id = GProcesoRelacionDato.objects.filter(
							procesoRelacion__id=procesoRelacion_id[0]['id'],
							item__id=39
							).values('id')	
						queryset=self.model.objects.filter(procesoRelacionDato=procesoRelacionDato_id[0]['id'])		

			if queryset.count()==0:
				mensaje='No se encontraron registros con los criterios de busqueda ingresados'	

			if ignorePagination:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
				'data':serializer.data})				
			else:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':mensaje,'success':'ok',
					'data':serializer.data})
				
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
					'data':serializer.data})					
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = SoporteProcesoRelacionDatoSerializer(data=request.DATA,
					context={'request': request})
				if serializer.is_valid():
					serializer.save(
						procesoRelacionDato_id=request.DATA['procesoRelacionDato_id'],
						documento=self.request.FILES.get('documento')
					)
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)
					# prd=GProcesoRelacionDato.objects.get(id=request.DATA['procesoRelacionDato_id'])
					# if prd.item.soporteObligatorio and prd.estado != '1':
					# 	prd.estado='1'
					# 	prd.save()
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					#print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
						 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
				'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic			
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			logs_model=self.model_log(
				usuario_id=request.user.usuario.id,
				accion=self.model_acciones.accion_borrar,
				nombre_modelo=self.nombre_modulo,
				id_manipulado=instance.id
			)
			logs_model.save()
			prd=GProcesoRelacionDato.objects.get(id=instance.procesoRelacionDato.id)
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			qsetSoportes = HSoporteProcesoRelacionDato.objects.filter(procesoRelacionDato=prd)
			if qsetSoportes.count()==0 and prd.item.soporteObligatorio:
				if prd.item.tieneVencimiento and prd.fechaVencimiento:
					hoy = date.today()
					hoyMasUnaSemana = date.today() + timedelta(days=8)
					# fechaVencimiento = datetime.strptime(prd.fechaVencimiento,
					# 		"%Y-%m-%d").date()
					fechaVencimiento = prd.fechaVencimiento
					if str(fechaVencimiento) < str(hoy):
						prd.estado=3
					else:
						if str(fechaVencimiento) <= str(hoyMasUnaSemana):
							prd.estado=2
						else:
							prd.estado=0

				else:
					prd.estado=0
				prd.save()

			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_200_OK)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update (self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = SoporteProcesoRelacionDatoSerializer(instance,data=request.DATA,
					context={'request': request},partial=partial)
				if serializer.is_valid():
					valores=HSoporteProcesoRelacionDato.objects.get(id=instance.id)
					if self.request.FILES.get('documento') is not None:
						serializer.save(
							procesoRelacionDato_id=request.DATA['procesoRelacionDato_id'],
							documento=self.request.FILES.get('documento')
						)
					else:
						serializer.save(
							procesoRelacionDato_id=request.DATA['procesoRelacionDato_id'],
							documento=valores.documento
						)
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_actualizar,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=instance.id
					)
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

# Create your views here. comentario
class PersonaLiteSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model= Persona
		fields = ('id','nombres','apellidos','correo','telefono')


class CargoLiteSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Cargo
		fields=('id','nombre')

class FuncionarioLiteSerializer(serializers.HyperlinkedModelSerializer):	
	persona = PersonaLiteSerializer(read_only=True)
	cargo = CargoLiteSerializer(read_only=True)
	empresa = EmpresaLiteSerializer(read_only=True)
	persona_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Persona.objects.all())
	cargo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Cargo.objects.all())
	
	
	class Meta:
		model = Funcionario
		fields=('id','persona','persona_id','cargo','cargo_id', 'empresa')

# Modelo: INotificacionVencimiento
class NotificacionVencimientoSerializer(serializers.HyperlinkedModelSerializer):
	procesoRelacionDato = ProcesoRelacionDatoSimpleSerializer(read_only=True)
	procesoRelacionDato_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=GProcesoRelacionDato.objects.all())

	funcionario = FuncionarioLiteSerializer(read_only=True)
	funcionario_id= serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=Funcionario.objects.all())	

	class Meta:
		model = INotificacionVencimiento
		fields=('url','id','procesoRelacionDato','procesoRelacionDato_id','funcionario','funcionario_id','responsableTitular')

class NotificacionVencimientoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de funcrionarios a los cuales se les notifica por cumplimiento o vencimiento de un item implementado
	sobre algun elemento.<br/>
	Use el parametro <b>procesoRelacionDatoId</b> para obtener los funcionarios a los cuales se les notifica en caso de cumplimiento o vencimiento.<br/>
	Use el parametro <b>empresas=1</b> para obtener un json adicional con las empresas en donde se puede consultar funcionarios.<br/>
	Use los parametros esContratista, esDiseñador, esProveedor, esContratante para filtar las empresas por tipo<br/>
	Use el parametro <b>funcionariosNoAsignados=1</b> obtiene una lista con los funcionarios no asignados, es requerido el parametro procesoRelacionDatoId.<br/>
	Use el parametro <b>empresaId=[id de la empresa de consulta]</b> obtiene una lista con los funcionarios de una empresa que no tienen la notificacion asignada.<br/>
	Use el parametro <b>nombreFuncionario=[texto] para combinar la busqueda con el nombre o apellido del funcionario</b>
	"""	
	model= INotificacionVencimiento
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='proceso.notificacionSobreItem'
	queryset = model.objects.all()
	serializer_class = NotificacionVencimientoSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		#import pdb; pdb.set_trace()
		procesoRelacionDatoId = self.request.query_params.get('procesoRelacionDatoId', None)
		empresas = self.request.query_params.get('empresas', None)
		esContratista= self.request.query_params.get('esContratista',None)
		esContratante= self.request.query_params.get('esContratante',None)
		esProveedor= self.request.query_params.get('esProveedor',None)
		esDisenador= self.request.query_params.get('esDisenador',None)
		funcionariosNoAsignados= self.request.query_params.get('funcionariosNoAsignados',None)
		empresaId= self.request.query_params.get('empresaId',None)
		nombreFuncionario= self.request.query_params.get('nombreFuncionario',None)
		queryset = super(NotificacionVencimientoViewSet, self).get_queryset()

		empresasData=[]
		mensaje=''
		registros=0
		try:
			if empresas:
				qset=(~Q(id=0))
				if (esContratista or esContratante or esProveedor or esDisenador):
					if esContratista:
						qset = qset & (Q(esContratista=1))
					if esContratante:
						qset = qset & (Q(esContratante=1))
					if esProveedor:
						qset = qset & (Q(esProveedor=1))
					if esDisenador:
						qset = qset & (Q(esDisenador=1))

				qsetEmpresas = Empresa.objects.filter(qset)
				#serializerEmpresa=EmpresaLiteSerializer(qsetEmpresas,many=True)
				empresasData=EmpresaLiteSerializer(qsetEmpresas,many=True).data
			if procesoRelacionDatoId:
				queryset = self.model.objects.filter(procesoRelacionDato__id=procesoRelacionDatoId)
				if funcionariosNoAsignados:
					qsetFuncionarioNoAsignado = (~Q(id=0))
					if empresaId:
						qsetFuncionarioNoAsignado = qsetFuncionarioNoAsignado & (Q(empresa__id=empresaId))
					if nombreFuncionario:
						qsetFuncionarioNoAsignado = qsetFuncionarioNoAsignado & (
							Q(persona__nombres__icontains=nombreFuncionario) |
							Q(persona__apellidos__icontains=nombreFuncionario))
					querysetFuncionarios = Funcionario.objects.exclude(
						id__in=queryset.values('funcionario__id')).filter(
							qsetFuncionarioNoAsignado)
					serializer = FuncionarioLiteSerializer(querysetFuncionarios,many=True)
					if querysetFuncionarios.count() == 0:
						mensaje='No se encontraron resultados'	
					
					return Response({'count':querysetFuncionarios.count(),'results':{
						'message':mensaje,'success':'ok','data':serializer.data}})

				qsetFuncionarioAsignado = (~Q(id=0))
				if empresaId:
					qsetFuncionarioAsignado = qsetFuncionarioAsignado & (Q(funcionario__empresa__id=empresaId))
				if nombreFuncionario:
					qsetFuncionarioAsignado = qsetFuncionarioAsignado & (
						Q(funcionario__persona__nombres__icontains=nombreFuncionario) |
						Q(funcionario__persona__apellidos__icontains=nombreFuncionario))
			
				qsetNotificaciones = queryset.filter(qsetFuncionarioAsignado)		
				serializer = self.get_serializer(qsetNotificaciones,many=True)
				registros = qsetNotificaciones.count()
			else:
				serializer = self.get_serializer(queryset,many=True)
				registros = queryset.count()
			if registros==0:
				mensaje='No se encontraron resultados'
			return Response({'count':registros,'results':{'message':mensaje,'success':'ok','data': {
				'notificaciones':serializer.data,'empresas':empresasData}}})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 			



## Codigo Externo a la API
###############################################################################################
###############################################################################################
@login_required
def procesos(request):
	return render(request, 'proceso/procesos-list.html',
		{'model':'AProceso','app':'proceso'})

@login_required
def procesoSeguimiento(request):
	return render(request, 'proceso/proceso-seguimiento.html',
		{'model':'GProcesoRelacionDato','app':'proceso'})

@login_required
def itemsProcesos(request,id):
	items = BItem.objects.filter(proceso=id)
	return render(request, 'proceso/proceso-items.html',
		{'id':id,'items':items,'model':'BItem','app':'proceso'})

@login_required
def detalleSeguimientoProcesos(request,id):
	proceso = AProceso.objects.get(id=id)
	return render(request, 'proceso/detalle-proceso-seguimiento.html',
		{'id':id,'proceso':proceso,'model':'FProcesoRelacion','app':'proceso'},
		)

@login_required
def responsables(request,id):
	items = BItem.objects.filter(proceso=id)
	empresas = Empresa.objects.filter(id__in=(AProceso.objects.filter(id=id).values('empresas'))) 
	usuarios = Usuario.objects.filter(empresa__id__in=empresas.values('id')).values('id','persona__nombres',
		'persona__apellidos','empresa__nombre').order_by('empresa__nombre','persona__nombres')

	return render(request, 'proceso/responsable-items.html',
		{'usuarios':usuarios,'id':id,'items':items,
		'model':'BItem','app':'proceso'})

@login_required
def detalleSeguimientoProcesosDatos(request,id):
	#import pdb; pdb.set_trace()
	procesoRelacion =  FProcesoRelacion.objects.get(id=id)
	elementoAnalizado=''
	soloLectura = None
	if procesoRelacion.proceso.apuntador == '1':
		puntero = Proyecto.objects.filter(id=procesoRelacion.idApuntador).values('nombre',
			'municipio__nombre','municipio__departamento__nombre', 'mcontrato__nombre', 'mcontrato__id')

		empresaContrato = EmpresaContrato.objects.filter(contrato__id=puntero[0]['mcontrato__id'], empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		#serializer = ProyectoSerializer(puntero,many=True, context={'request': request})
	else:
		puntero = Contrato.objects.filter(id=procesoRelacion.idApuntador).values('nombre','numero','mcontrato__nombre', 'mcontrato__id')	
		contrato = None
		if puntero[0]['mcontrato__id']:
			contrato = puntero[0]['mcontrato__id']
		else:
			contrato = procesoRelacion.idApuntador	
		empresaContrato = EmpresaContrato.objects.filter(contrato__id=contrato, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		#serializer = ContratoSerializer(puntero,many=True, context={'request': request})
	tareas = (GProcesoRelacionDato.objects.filter(procesoRelacion=procesoRelacion).count())
	tareasCumplidas = (GProcesoRelacionDato.objects.filter(procesoRelacion=procesoRelacion,estado=1).count())
	porcentaje = (float(tareasCumplidas) / float(tareas))*100
	etiquetaPorcentaje =int((float(tareasCumplidas) / float(tareas))*100)
	if procesoRelacion.proceso.tablaForanea:
		#inciar rutina para identificar el elemento analizado
		modeloReferencia = ContentType.objects.get(
			pk=procesoRelacion.proceso.tablaForanea.id).model_class()
		elemento = modeloReferencia.objects.filter(
		id=procesoRelacion.idTablaReferencia).values(
			procesoRelacion.proceso.etiqueta)
		elementoAnalizado = elemento[0][procesoRelacion.proceso.etiqueta]		
	return render(request, 'proceso/detalle-proceso-seguimiento-datos.html',
		{'id':id,'procesoRelacion':procesoRelacion,'model':'GProcesoRelacionDato','app':'proceso',
		'puntero':puntero[0],'avance':porcentaje, 'etiquetaAvance':etiquetaPorcentaje,
		'elementoAnalizado':elementoAnalizado, 'soloLectura': soloLectura},
		)

@login_required
def detalleSeguimientoProcesosDatosSolicitud(request,id):
	procesoRelacion =  FProcesoRelacion.objects.get(id=id)
	elementoAnalizado=''
	if procesoRelacion.proceso.apuntador == '1':
		puntero = Proyecto.objects.filter(id=procesoRelacion.idApuntador).values('nombre',
			'municipio__nombre','municipio__departamento__nombre', 'mcontrato__nombre')
		#serializer = ProyectoSerializer(puntero,many=True, context={'request': request})
	else:
		puntero = Contrato.objects.filter(id=procesoRelacion.idApuntador).values('nombre','numero','mcontrato__nombre')	
		#serializer = ContratoSerializer(puntero,many=True, context={'request': request})
	tareas = (GProcesoRelacionDato.objects.filter(procesoRelacion=procesoRelacion).count())
	tareasCumplidas = (GProcesoRelacionDato.objects.filter(procesoRelacion=procesoRelacion,estado=1).count())
	porcentaje = (float(tareasCumplidas) / float(tareas))*100
	etiquetaPorcentaje =int((float(tareasCumplidas) / float(tareas))*100)
	if procesoRelacion.proceso.tablaForanea:
		#inciar rutina para identificar el elemento analizado
		modeloReferencia = ContentType.objects.get(
			pk=procesoRelacion.proceso.tablaForanea.id).model_class()
		elemento = modeloReferencia.objects.filter(
		id=procesoRelacion.idTablaReferencia).values(
			procesoRelacion.proceso.etiqueta)
		elementoAnalizado = elemento[0][procesoRelacion.proceso.etiqueta]

		seguidor = JSeguidorProcesoRelacion.objects.filter(procesoRelacion=procesoRelacion,
			usuario=request.user.usuario)
		if seguidor.count()>0:
			seguido = True
		else:
			seguido = False

	proveedores = Empresa.objects.filter(esContratista=True).order_by('nombre').values('id','nombre')
	proveedorActual = GProcesoRelacionDato.objects.filter(item__id=19,procesoRelacion=procesoRelacion).values('valor')
	funcionarios = Funcionario.objects.filter(empresa__id=request.user.usuario.empresa.id).values('id',
		'persona__nombres','persona__apellidos')	
	funcionarioActual = GProcesoRelacionDato.objects.filter(item__id=26,procesoRelacion=procesoRelacion).values('valor')

	return render(request, 'proceso/detalle-proceso-seguimiento-datos-solicitud.html',
		{'id':id,'procesoRelacion':procesoRelacion,'model':'GProcesoRelacionDato','app':'proceso',
		'puntero':puntero[0],'avance':porcentaje, 'etiquetaAvance':etiquetaPorcentaje,
		'elementoAnalizado':elementoAnalizado, 'seguido':seguido,'proveedores':proveedores, 
		'proveedorActual':proveedorActual[0]['valor'],'funcionarios':funcionarios,
		'funcionarioActual':funcionarioActual[0]['valor']},
		)

@login_required
def ConfigurarSeguimiento(request,id):
	#import pdb; pdb.set_trace()
	seguidor = JSeguidorProcesoRelacion.objects.filter(procesoRelacion__id=id,
		usuario=request.user.usuario)
	if seguidor.count()>0:
		se = seguidor.values('id')
		JSeguidorProcesoRelacion.objects.get(pk=se[0]['id']).delete()
	else:
		se = JSeguidorProcesoRelacion(usuario=request.user.usuario,
			procesoRelacion=FProcesoRelacion.objects.get(pk=id))
		se.save()

	procesoRelacion =  FProcesoRelacion.objects.get(id=id)
	elementoAnalizado=''
	if procesoRelacion.proceso.apuntador == '1':
		puntero = Proyecto.objects.filter(id=procesoRelacion.idApuntador).values('nombre',
			'municipio__nombre','municipio__departamento__nombre', 'mcontrato__nombre')
		#serializer = ProyectoSerializer(puntero,many=True, context={'request': request})
	else:
		puntero = Contrato.objects.filter(id=procesoRelacion.idApuntador).values('nombre','numero','mcontrato__nombre')	
		#serializer = ContratoSerializer(puntero,many=True, context={'request': request})
	tareas = (GProcesoRelacionDato.objects.filter(procesoRelacion=procesoRelacion).count())
	tareasCumplidas = (GProcesoRelacionDato.objects.filter(procesoRelacion=procesoRelacion,estado=1).count())
	porcentaje = (float(tareasCumplidas) / float(tareas))*100
	etiquetaPorcentaje =int((float(tareasCumplidas) / float(tareas))*100)
	if procesoRelacion.proceso.tablaForanea:
		#inciar rutina para identificar el elemento analizado
		modeloReferencia = ContentType.objects.get(
			pk=procesoRelacion.proceso.tablaForanea.id).model_class()
		elemento = modeloReferencia.objects.filter(
		id=procesoRelacion.idTablaReferencia).values(
			procesoRelacion.proceso.etiqueta)
		elementoAnalizado = elemento[0][procesoRelacion.proceso.etiqueta]

		seguidor = JSeguidorProcesoRelacion.objects.filter(procesoRelacion=procesoRelacion,
			usuario=request.user.usuario)
		if seguidor.count()>0:
			seguido = True
		else:
			seguido = False

	return render(request, 'proceso/detalle-proceso-seguimiento-datos-solicitud.html',
		{'id':id,'procesoRelacion':procesoRelacion,'model':'GProcesoRelacionDato','app':'proceso',
		'puntero':puntero[0],'avance':porcentaje, 'etiquetaAvance':etiquetaPorcentaje,
		'elementoAnalizado':elementoAnalizado, 'seguido':seguido},
		)


			

@login_required
def implementacion(request,id):
	proceso = AProceso.objects.get(id=id)
	return render(request, 'proceso/implementacion.html',
		{'proceso':proceso,'model':'AProceso','app':'proceso'})

@login_required
@transaction.atomic
def implementar(request):
	#import pdb; pdb.set_trace()	
	sid = transaction.savepoint()
	mensaje="Elementos implementados correctamente"
	encontrado=False
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)		
		proceso = AProceso.objects.get(id=respuesta['proceso'])
		items = BItem.objects.filter(proceso=proceso).values('id')	
		#inicio codigo de la implementacion
		if proceso.tablaForanea:
			#el proceso se vincula con una tabla externa a proyecto/contrato
			#debo buscar los id de la tabla externa con la que se vincula el proceso haciendo UNION
			#por el campoEnlace del proceso
			modeloReferencia = ContentType.objects.get(pk=proceso.tablaForanea.id).model_class()

			# print 'lista:'
			# print respuesta['lista']
			# print modeloReferencia
			argument_list=[]
			

			for item in respuesta['lista']:
				#ids=modeloReferencia.objects.filter(proceso.campoEnlace=item).values('id')
				argument_list.append(Q(**{proceso.campoEnlace:int(item.replace('chkDis',''))}))
				ids= modeloReferencia.objects.filter(reduce(operator.or_,argument_list)).values('id')
				#print ids

				for i in ids:
					#print proceso
					## print item
					#print i['id']
					encontrado=True
					pr = FProcesoRelacion(proceso=proceso,idApuntador=int(item.replace('chkDis','')),
						idTablaReferencia=i['id'])
					pr.save()
					#print 'items: '
					## print items
					for it in items:
						prd = GProcesoRelacionDato(
							procesoRelacion=pr,
							item=BItem.objects.get(id=it['id'])
						)
						prd.save()
					logs_model=Logs(
						usuario_id=request.user.usuario.id,
						accion=Acciones.accion_crear,
						nombre_modelo='proceso.FProcesoRelacion',
						id_manipulado=pr.id
					)
					logs_model.save()
				if encontrado == False:
					mensaje='Proceso terminado correctamente. Sin embargo, no se encontraron elementos de segundo nivel asociado al elemento seleccionado'
		else:
			#el proceso se vincula con proyecto/contrato
			for item in respuesta['lista']:
				pr = FProcesoRelacion(proceso=proceso,idApuntador=int(item.replace('chkDis','')),
					idTablaReferencia=int(item.replace('chkDis','')))
				pr.save()
				for it in items:
					prd = GProcesoRelacionDato(
						procesoRelacion=pr,
						item=BItem.objects.get(id=it['id'])
					)
					prd.save()

				logs_model=Logs(
					usuario_id=request.user.usuario.id,
					accion=Acciones.accion_crear,
					nombre_modelo='proceso.FProcesoRelacion',
					id_manipulado=pr.id
				)
				logs_model.save()
		transaction.savepoint_commit(sid)
		#fin codigo de la implementacion
		return JsonResponse({'message':mensaje,'success':'ok',
				'data':''})
	except Exception as e:
		functions.toLog(e,'Procesos.implementarProceso')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	

@login_required
@transaction.atomic
def ImplementarRetieSimple(request,id):
	idProyecto= id
	idProceso = 10
	mensaje=''
	sid = transaction.savepoint()
	try:
		if idProyecto:
			procesoRelacion=FProcesoRelacion.objects.filter(proceso__id=idProceso,
				idApuntador=idProyecto,idTablaReferencia=idProyecto)
			if procesoRelacion:
				#transaction.savepoint_rollback(sid)
				return detalleSeguimientoProcesosDatos(request,procesoRelacion.id)
			else:
				#import pdb; pdb.set_trace()
				procesoRelacion = FProcesoRelacion(proceso=AProceso.objects.get(pk=idProceso),
					idApuntador=idProyecto,idTablaReferencia=idProyecto)
				procesoRelacion.save()
				items = BItem.objects.filter(proceso__id=idProceso).values('id')
				for item in items:
					prd = GProcesoRelacionDato(
						procesoRelacion=procesoRelacion,
						item=BItem.objects.get(pk=item['id']))
					prd.save()
				
				logs_model=Logs(
					usuario_id=request.user.usuario.id,
					accion=Acciones.accion_crear,
					nombre_modelo='proceso.FProcesoRelacion',
					id_manipulado=procesoRelacion.id
				)
				logs_model.save()
				transaction.savepoint_commit(sid)
				return detalleSeguimientoProcesosDatos(request,procesoRelacion.id)	
		else:
			mensaje='No fue posible implementar el proceso, no se encontro el proyecto'
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':mensaje,'success':'error','data':''})

	except Exception as e:
		functions.toLog(e,'Procesos.implementarRetieSimple')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	




@login_required
@transaction.atomic
def quitarImplementacion(request):
	#print 'Ingreso a quitarImplementacion'
	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		#print lista
		respuesta= json.loads(lista)
		proceso = AProceso.objects.get(id=respuesta['proceso'])	
		ids=[]
		#print 'elementos: '	
		for item in respuesta['lista']:
			ids=FProcesoRelacion.objects.filter(proceso__id=proceso.id,idApuntador=item.replace('chkImp','')).values('id')
			#print 'ids'
			#print ids
			for i in ids:
				GProcesoRelacionDato.objects.filter(procesoRelacion=i['id']).delete()
				FProcesoRelacion.objects.get(id=i['id']).delete()
				logs_model=Logs(
					usuario_id=request.user.usuario.id,
					accion=Acciones.accion_borrar,
					nombre_modelo='proceso.FProcesoRelacion',
					id_manipulado=i['id']
				)
				logs_model.save()
		transaction.savepoint_commit(sid)		
		return JsonResponse({'message':'Los elementos seleccionados han dejado de estar implementados',
			'success':'ok','data':''})
	except Exception as e:
		transaction.savepoint_rollback(sid)
		mensaje ='Se presentaron errores al procesar la solicitud'
		mensajeExeption=e[0]
		if mensajeExeption.find("referenced through a protected foreign key") >=0:
			mensaje='Se encontraron datos sobre uno o varios elementos sobre los cuales desea retirar la implementacion'
		return JsonResponse({'message':mensaje,'success':'error',
			'data':''})	

@login_required
@transaction.atomic
def asignarNotificacion(request):
	sid = transaction.savepoint()
	mensaje="Se asigno correctamente la notificacion a los funcionarios seleccionados"
	encontrado=False
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		procesoRelacionDatoId=respuesta['procesoRelacionDatoId']
		for item in respuesta['lista']:
			notificacion = INotificacionVencimiento(
				procesoRelacionDato=GProcesoRelacionDato.objects.get(id=procesoRelacionDatoId),
				funcionario=Funcionario.objects.get(id=item.replace('chkDis','')))
			notificacion.save()
			logs_model=Logs(
				usuario_id=request.user.usuario.id,
				accion=Acciones.accion_crear,
				nombre_modelo='proceso.INotificacionVencimiento',
				id_manipulado=notificacion.id
			)
			logs_model.save()
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'La notificacion fue configurada correctamente',
			'success':'ok','data':''})
	except Exception as e:
		functions.toLog(e,'proceso.INotificacionVencimiento')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud',
			'success':'error','data':''})


@login_required
@transaction.atomic
def quitarNotificacion(request):
	sid = transaction.savepoint()
	mensaje="Se quito correctamente la notificacion a los funcionarios seleccionados"
	encontrado=False
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		#procesoRelacionDatoId=respuesta['procesoRelacionDatoId']
		for item in respuesta['lista']:
			notificacion = INotificacionVencimiento.objects.get(id=item.replace('chk',''))			
			logs_model=Logs(
				usuario_id=request.user.usuario.id,
				accion=Acciones.accion_borrar,
				nombre_modelo='proceso.INotificacionVencimiento',
				id_manipulado=notificacion.id
			)
			notificacion.delete()
			logs_model.save()
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'La notificacion fue eliminada correctamente',
			'success':'ok','data':''})
	except Exception as e:
		functions.toLog(e,'proceso.INotificacionVencimiento')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud',
			'success':'error','data':''})

@login_required
@transaction.atomic
def responsablesGuardarCambios(request):
	lista=request.POST['_content']
	sid = transaction.savepoint()
	
	try:
		respuesta = json.loads(lista)
		for datos in respuesta['lista']:
			#import pdb; pdb.set_trace()
			jsonDatos = json.loads(datos.replace("'",'"'))
			if jsonDatos['responsable'] != 0:
				item = BItem.objects.get(pk=jsonDatos['id'])
				responsableAnterior=0
				if item.responsable:
					responsableAnterior = item.responsable.id
				if jsonDatos['responsable'] != -1:	
					item.responsable=Usuario.objects.get(pk=jsonDatos['responsable'])
				else:
					item.responsable=None
				item.save()	
				#guadar notificacion para el responsable configurado y quitar el responsable anterior
				if responsableAnterior != 0:
					#quitar notificaciones a responsables anteriores
					usr = Usuario.objects.get(pk=responsableAnterior)
					funcionario=Funcionario.objects.filter(persona__id=usr.persona.id).order_by('id')[:1]					
					INotificacionVencimiento.objects.filter(procesoRelacionDato__item=item, 
						funcionario=funcionario).delete()
				#agregar notificacion a responsables nuevos
				#import pdb; pdb.set_trace()
				if item.responsable:
					funcionario=Funcionario.objects.filter(persona__id=item.responsable.persona.id).order_by('id')[:1].values('id')
					procesoRelacionDato = GProcesoRelacionDato.objects.filter(item=item).values('id')
					for prd in procesoRelacionDato:
						notificacion = INotificacionVencimiento(
							procesoRelacionDato=GProcesoRelacionDato.objects.get(pk=int(prd['id'])),
							funcionario=Funcionario.objects.get(pk=int(funcionario[0]['id'])),
							responsableTitular=True
							)
						notificacion.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,
					accion=Acciones.accion_actualizar,
					nombre_modelo='Proceso.item(responsable)',
					id_manipulado=item.id)
				logs_model.save()
		return JsonResponse({'message':'Los cambios se han guardado correctamente','success':'ok','data':''})

	except Exception as e:
		functions.toLog(e,'Proceso.item(responsable)')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud',
			'success':'error','data':''})


@login_required
@transaction.atomic
def guardarCambios(request):
	#import pdb; pdb.set_trace()
	lista=request.POST['_content']
	sid = transaction.savepoint()
	#print lista
	try:
		respuesta= json.loads(lista)
		for datos in respuesta['lista']:
			notificar =False
			cambiarEstado=False
			jsonDatos = json.loads(datos.replace("'",'"'))
			prd=GProcesoRelacionDato.objects.get(id=jsonDatos['id'])
			if jsonDatos['fechaVencimiento'] != 'null':
				prd.fechaVencimiento=jsonDatos['fechaVencimiento']
			else:
				prd.fechaVencimiento=None
			if jsonDatos['valor']!=prd.valor:
				notificar=True
			if jsonDatos['valor']!= 'Vacio':
				prd.valor=jsonDatos['valor']
				
				if jsonDatos['soporteObligatorio']==False:
					cambiarEstado=True
				else:
					#codigo para verificar si se tiene cargado el soporte	
					qset = HSoporteProcesoRelacionDato.objects.filter(procesoRelacionDato=prd)
					if qset.count()>0:
						cambiarEstado=True
			else:
				prd.valor = 'Vacio'
				cambiarEstado=True
			if jsonDatos['observacion'] != 'null':
				prd.observacion=jsonDatos['observacion']
			else:
				prd.observacion=None

			if cambiarEstado:
				if jsonDatos['fechaVencimiento'] =='null':
					if prd.valor=='Vacio':
						prd.estado=0
					else:
						prd.estado=1
				else:
					if prd.valor!='Vacio':
						prd.estado=1
					else:
						hoy = date.today()
						hoyMasUnaSemana = date.today() + timedelta(days=8)
						fechaVencimiento = datetime.strptime(jsonDatos['fechaVencimiento'],
							"%Y-%m-%d").date()
						if str(fechaVencimiento) < str(hoy):
							prd.estado=3
						else:
							if str(fechaVencimiento) <= str(hoyMasUnaSemana):
								prd.estado=2
							else:
								prd.estado=0

			prd.usuarioEditor = request.user.usuario.id					
			prd.save()
			logs_model=Logs(usuario_id=request.user.usuario.id,
				accion=Acciones.accion_actualizar,
				nombre_modelo='Proceso.ProcesoRelacionDato(Detalle)',
				id_manipulado=prd.id)
			logs_model.save()
			# preguntar si se trata del item que preconfigura el responsable de los items de 
			# id: 23, descripcion: pólizas del contrato expedidas por el contratista (incluyendo recibo de pago)
			# id: 27, descripcion: Requisitos para inicio del contrato
			# if prd.item.id==21:
			# 	import pdb; pdb.set_trace()
			direccion = settings.SERVER_URL
			if settings.PORT_SERVER != '':
				direccion = direccion + ':'+ settings.PORT_SERVER
			db = settings.DATABASES['default']['NAME']			
			itemsResponsableEmpresa = [23,27]
			if prd.item.id==19 and prd.valor != 'Vacio' and notificar and cambiarEstado and db=='coasmedas1_Enelar':
				funcionarioResponsable = Funcionario.objects.filter(empresa__id=int(prd.valor)).order_by('id')[:1].values(
					'id')

				if funcionarioResponsable:
					for it in itemsResponsableEmpresa:
						prdArray = GProcesoRelacionDato.objects.filter(item__id=it,
							procesoRelacion__id=prd.procesoRelacion.id).values('id')

						if prdArray:
							fun=Funcionario.objects.get(pk=funcionarioResponsable[0]['id'])
							notificacion=INotificacionVencimiento.objects.create(
								procesoRelacionDato=GProcesoRelacionDato.objects.get(pk=prdArray[0]['id']),
								funcionario=fun,
								responsableTitular=True)
							notificacion.save()
					#agregar la empresa del funcionario a proceso.empresas
					proveedorSeleccionado = Empresa.objects.get(pk=fun.empresa.id)
					encontrado=False
					empresasActuales = prd.procesoRelacion.proceso.empresas.all().values('id')
					for emp in empresasActuales:
						if emp['id']==proveedorSeleccionado.id:
							encontrado=True
					#import pdb; pdb.set_trace()
					if (encontrado == False):
						prd.procesoRelacion.proceso.empresas.add(proveedorSeleccionado)	
					#asignar permiso de lectura a la empresa de todos los items del procesoRelacion
						#y en el caso de los items 23 y 27 asignar permisos de escritura
					itemsArray=GProcesoRelacionDato.objects.filter(
						procesoRelacion__id=prd.procesoRelacion.id).values('item__id')
					for itm in itemsArray:
						escritura=False
						if itm['item__id']==23 or itm['item__id']==27: 
							escritura=True
						#verificar la existencia del permiso
						p = CPermisoEmpresaItem.objects.filter(empresa=proveedorSeleccionado,
							item__id=itm['item__id']).values('id')
						
						if p:
							permiso=CPermisoEmpresaItem.objects.get(pk=p[0]['id'])
							permiso.escritura=escritura
						else:	
							permiso = CPermisoEmpresaItem.objects.create(
								empresa=proveedorSeleccionado,
								item=BItem.objects.get(pk=itm['item__id']),
								lectura=True,
								escritura=escritura
							)
						permiso.save()
					#asignar el permiso para ver la solicitud de servicio
					solicitud = BSolicitud.objects.get(pk=prd.procesoRelacion.idTablaReferencia)
					solicitud.empresas.add(proveedorSeleccionado)	

			#asignacion de supervisor del contrato		
			if prd.item.id==26 and prd.valor != 'Vacio' and notificar and cambiarEstado and db=='coasmedas1_Enelar':
				itemsResponsableSupervisor=[28,29,30,31,38,41]
				funcionarioResponsable = Funcionario.objects.get(pk=int(prd.valor))
				if funcionarioResponsable:
					for it in itemsResponsableSupervisor:
						prdArray = GProcesoRelacionDato.objects.filter(item__id=it,
							procesoRelacion__id=prd.procesoRelacion.id).values('id')
						if prdArray:
							
							notificacion=INotificacionVencimiento.objects.create(
								procesoRelacionDato=GProcesoRelacionDato.objects.get(pk=prdArray[0]['id']),
								funcionario=funcionarioResponsable,
								responsableTitular=True)
							notificacion.save()
					contenidoAsignacion='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
					contenidoAsignacion = contenidoAsignacion+ 'Señor(a) ' + funcionarioResponsable.persona.nombres + ' ' + funcionarioResponsable.persona.apellidos
					contenidoAsignacion=contenidoAsignacion + ' Nos permitimos comunicarle que ha sido asignado como <b>Supervisor</b>'
					contenidoAsignacion=contenidoAsignacion + ' del contrato derivado de la solicitud de servicio <b>'
					solicitud = BSolicitud.objects.get(pk=prd.procesoRelacion.idTablaReferencia)
					contenidoAsignacion=contenidoAsignacion + solicitud.descripcion + '</b>, registrada por el(la) usuario(a) '
					contenidoAsignacion=contenidoAsignacion + solicitud.solicitante.persona.nombres + ' '
					contenidoAsignacion=contenidoAsignacion + solicitud.solicitante.persona.apellidos +', el día '
					contenidoAsignacion=contenidoAsignacion + solicitud.fechaCreacion.strftime('%Y-%m-%d') + '.<br/><br/>'
					contenidoAsignacion=contenidoAsignacion + 'Como supervisor del contrato, tendra acceso su seguimiento '
					contenidoAsignacion=contenidoAsignacion + 'a traves del siguiente link (debe tener la sesión abierta en '
					contenidoAsignacion=contenidoAsignacion + '<a href="http://enelar.sinin.co">SININ</a>):<br/><br/>'
					direccionA=direccion + '/proceso/solicitudServicioSeguimiento/' + str(prd.procesoRelacion.id) + '/'
					contenidoAsignacion=contenidoAsignacion + '<a href="'+direccionA+'"> Seguimiento </a><br/><br/>'
					contenidoAsignacion = contenidoAsignacion + 'Favor no responder este correo, es de uso informativo exclusivamente,'
					contenidoAsignacion = contenidoAsignacion + '<br/></br><br/>Equipo SININ'
					correosDestinoA=funcionarioResponsable.persona.correo+';'+request.user.usuario.persona.correo
					mailA = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=correosDestinoA,
						asunto='Notificacion: Asignación de contrato a supervisar',
						contenido=contenidoAsignacion,
						appLabel='Proceso(solicitudservicio)',
					)
					mailA.save()						
					res=sendMail.delay(mailA)					




			#notificacion de cambio del item:
			# print prd.item.notificacionCumplimiento
			# print notificar
			referencias=[{'proceso_id': 2, 'item_id':19},]
			if (prd.item.notificacionCumplimiento=='2' or prd.item.notificacionCumplimiento=='3') and notificar and cambiarEstado:
				estados=['Por cumplir','Cumplido','Por vencer','Vencido']
				destinatarios=[]
				tipo=''
				if prd.item.notificacionCumplimiento=='2':
					#notificar a todos los responsables del proyecto
					if prd.procesoRelacion.proceso.apuntador=='1':
						destinatarios = Proyecto.objects.filter(id=prd.procesoRelacion.idApuntador, funcionario__activo=1).values(
							'funcionario__persona__correo')
					elif prd.procesoRelacion.proceso.apuntador=='2':
						destinatarios = Proyecto.objects.filter(
							contrato__id=prd.procesoRelacion.idApuntador, funcionario__activo=1).values(
								'funcionario__persona__correo')
				else:
					#notificar a los funcionarios que tengan la notificaion configurada
					destinatarios = INotificacionVencimiento.objects.filter(
						procesoRelacionDato=prd,funcionario__activo=1).values('funcionario__persona__correo')
										
					#busco el responsable del siguiente item en el procesoRelacion si el proceso es paso a paso
					ResponsableSiguiente=''
					sepS=''
					if prd.procesoRelacion.proceso.pasoAPaso:
						objSiguiente = GProcesoRelacionDato.objects.filter(item__orden=prd.item.orden+1,
							procesoRelacion=prd.procesoRelacion).values('item__responsable__persona__correo',
							'item__descripcion','item__responsable__persona__nombres',
							'item__responsable__persona__apellidos','item__contratistaResponsable',
							'procesoRelacion__proceso__id','procesoRelacion__id')
						if objSiguiente:
							if objSiguiente[0]['item__contratistaResponsable']==False:	
								ResponsableSiguiente=objSiguiente[0]['item__responsable__persona__correo']
								sepS=';'
						#busco las direcciones de correo de los seguidores
						
						seguidores = JSeguidorProcesoRelacion.objects.filter(
							procesoRelacion=prd.procesoRelacion).values('usuario__persona__correo')
						
						for seguidor in seguidores:
							if ResponsableSiguiente:
								if ResponsableSiguiente.find(seguidor['usuario__persona__correo']) < 0:
									ResponsableSiguiente = ResponsableSiguiente + sepS + seguidor['usuario__persona__correo']
							else:
								ResponsableSiguiente=seguidor['usuario__persona__correo']
						

						

				if prd.procesoRelacion.proceso.apuntador=='1':
					proy=Proyecto.objects.filter(
						id=prd.procesoRelacion.idApuntador).values('nombre',
							'municipio__departamento__nombre','municipio__nombre')
					tipo='proyecto ' + proy[0]['nombre'] + ' en ' + proy[0]['municipio__nombre'] + ' - ' + proy[0]['municipio__departamento__nombre']
				elif prd.procesoRelacion.proceso.apuntador=='2':		
					cont = Contrato.objects.filter(id=prd.procesoRelacion.idApuntador).values(
						'numero','nombre','contratista__nombre')
					tipo='contrato No. ' + cont[0]['numero'] + ' - ' + cont[0]['nombre'] + ' del contratista ' + cont[0]['contratista__nombre']

				if destinatarios.count()>0 or ResponsableSiguiente != '':
					#enviar correos
					correosDestino=ResponsableSiguiente
					
					for destinatario in destinatarios:
						if correosDestino:
							if correosDestino.find(destinatario['funcionario__persona__correo']) < 0:
								correosDestino = correosDestino + sepS + destinatario['funcionario__persona__correo']
						else:
							correosDestino=	destinatario['funcionario__persona__correo']	
					contenido='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
					contenido = contenido + 'Nos permitimos comunicarle que el item <b>'+prd.item.descripcion+'</b>'
					contenido = contenido + ' del proceso <b>' + prd.procesoRelacion.proceso.nombre + '</b>'
					contenido = contenido + ' ha sido actualizado al estado <b>'+ estados[int(prd.estado)]+'</b>'
					contenido = contenido + ' aplicado sobre '
					if prd.procesoRelacion.proceso.tablaForanea:
						#buscar el elemento
						modeloReferencia = ContentType.objects.get(
							pk=prd.procesoRelacion.proceso.tablaForanea.id).model_class()
						elemento = modeloReferencia.objects.filter(
							id=prd.procesoRelacion.idTablaReferencia).values(
								prd.procesoRelacion.proceso.etiqueta)
						contenido = contenido + '<b>'+ elemento[0][prd.procesoRelacion.proceso.etiqueta] + '</b>'
						contenido = contenido + ' del ' + tipo
					else:
						contenido = contenido + 'el ' + tipo
					contenido = contenido + '.<br/><br/>'
					
					if prd.procesoRelacion.proceso.pasoAPaso and prd.estado==1 and db=='coasmedas1_Enelar':
						#consultar el porcentaje de avance y concatenarlo al cuerpo del correo
						totalItems = GProcesoRelacionDato.objects.filter(procesoRelacion=prd.procesoRelacion).count()
						itemsCumplidos = GProcesoRelacionDato.objects.filter(procesoRelacion=prd.procesoRelacion,
							estado='1').count()

						contenido = contenido + 'El porcentaje de avance de este proceso es: <b>'
						contenido = contenido + str(round((float(itemsCumplidos) / float(totalItems))*100,2)) + '%</b>.<br/><br/>'
						#import pdb; pdb.set_trace()
						#agregar al cuerpo del correo la solicitud de revisar el siguiente item
						if objSiguiente:
							if objSiguiente[0]['item__contratistaResponsable']==False:
								if objSiguiente[0]['item__responsable__persona__nombres'] and objSiguiente[0]['item__responsable__persona__apellidos']:
									contenido = contenido + 'Señor(a) ' + objSiguiente[0]['item__responsable__persona__nombres']
									contenido = contenido + ' ' + objSiguiente[0]['item__responsable__persona__apellidos'] + ', '
							else:
								#consulto el id del contrato para traer a la persona asociada al funcionario
								for ref in referencias:
									if ref['proceso_id'] == objSiguiente[0]['procesoRelacion__proceso__id']:
										prdContratista = GProcesoRelacionDato.objects.filter(
											procesoRelacion__id=objSiguiente[0]['procesoRelacion__id'],
											item__id=ref['item_id']).values('valor')
										#contratista = Contrato.objects.get(pk=prdContrato[0]['valor']).values('contratista__id')
										if prdContratista:
											#busco el correo del contratista si esta definido como responsable del siguiente item
											correoContratista = Usuario.objects.filter(
												empresa__id=prdContratista[0]['valor']).order_by('id')[:1].values('persona__correo',
												'empresa__nombre')
											if correoContratista:
												correosDestino = correosDestino + ';' + correoContratista[0]['persona__correo']
												#agregar al cuerpo del correo el nombre del contratista
												contenido = contenido + 'Señores <b>' + correoContratista[0]['empresa__nombre'] + '</b> '
										else:
											#notifico que el contrato no esta asociado
											contenido = contenido + 'Señores <font color="red"><b>Contratista no definido</b></font> '
								




						contenido = contenido + 'nos permitimos informarle que se requiere su valiosa colaboración '
						contenido = contenido + 'para atender el siguiente paso del proceso asociado al '
						contenido = contenido + 'presente mensaje: <br/><br/>'

						direccion = direccion + '/proceso/solicitudServicioSeguimiento/' + str(prd.procesoRelacion.id) + '/'
						contenido = contenido + '<a href="'+direccion+'">'
						contenido = contenido + objSiguiente[0]['item__descripcion']
						contenido = contenido + '</a><br/><br/>'

					contenido = contenido + 'Favor no responder este correo, es de uso informativo exclusivamente,'
					contenido = contenido + '<br/></br><br/>Equipo SININ'
					mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=correosDestino,
						asunto='Actualizacion en seguimiento de proceso',
						contenido=contenido,
						appLabel='Proceso',
					)
					mail.save()						
					res=sendMail.delay(mail)

			# Si el Item es el Num. 50 cambiar el estado de la factura a Pagada
			if prd.item.id == 50 and prd.estado == 1 and db=='coasmedas1_Enelar':
				# print "Cabiar estado factura"
				pagarFactura(request, prd.procesoRelacion.idTablaReferencia, prd.valor)

		transaction.savepoint_commit(sid)

		return JsonResponse({'message':'Los cambios se han guardado correctamente',
			'success':'ok','data':''})
	except Exception as e:
		functions.toLog(e,'proceso.procesoRelacionDato(Detalle)')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al guardar los cambios','success':'error',
			'data':''})	


def exportarExcel(request):
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		ahora=datetime.now()
		archivo=str(ahora.year)+str(ahora.month)+str(ahora.day)+str(ahora.hour)+str(ahora.minute)+str(ahora.second)
		response['Content-Disposition'] = 'attachment; filename="informe'+archivo+'.xls"'
		
		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('datos')
		format1=workbook.add_format({'border':1,'font_size':10,'bold':True})
		format2=workbook.add_format({'border':1})


		# worksheet.write('A1', 'Nit', format1)
		# worksheet.write('B1', 'Nombre', format1)
		# worksheet.write('C1', 'Direccion', format1)		

		row=0	
		proceso = AProceso.objects.get(id=request.GET['id'])
		# Codigo para traer los nombres de las columnas fijas
		if proceso.apuntador == '1':
			#El informe toma como base el proyecto
			worksheet.write('A1','Macrocontrato',format1)
			worksheet.write('B1','Departamento',format1)
			worksheet.write('C1','Municipio',format1)
			worksheet.write('D1','Nombre del proyecto',format1)
			worksheet.write('E1','Numero de contrato',format1)
			worksheet.set_column('A:E',25)
			col=5
		else:
			#El informe toma como base el contrato
			worksheet.write('A1','Nombre contrato',format1)		
			worksheet.write('B1','Numero contrato',format1)
			worksheet.write('C1','Contratante',format1)		
			worksheet.write('D1','Contratista',format1)		
			worksheet.set_column('A:D',25)

			col=4
		# Fin codigo para traer los nombres de las columnas fijas
		# Codigo para traer una columna si hay un elemento de segundo nivel asociado al proceso
		if proceso.etiqueta:
			worksheet.write(row,col,'Elemento analizado',format1)		
			col=col+1

		# Codigo para traer las columnas dinamicas del informe
		nombre=''
		camposInforme = ECampoInforme.objects.filter(proceso=proceso).values(
			'nombreCampoApuntador','tablaForanea__name','campoTablaForanea')
		for campo in camposInforme:
			nombre=''
			if campo['tablaForanea__name']:
				nombre = campo['nombreCampoApuntador'] + '.' + campo['campoTablaForanea']
			else:
				nombre = campo['nombreCampoApuntador']
			worksheet.write(row,col,nombre,format1)
			col=col+1
		# Fin Codigo para traer las columnas dinamicas del informe
		worksheet.write(row,col,'Avance (%)',format1)
		col=col+1	
		# Codigo para traer las columnas del proceso
		items = BItem.objects.filter(proceso=proceso).order_by('orden').values('descripcion')
		# Fin codigo para traer las columnas del proceso
		for item in items:
			worksheet.write(row,col,item['descripcion'],format1)
			col=col+1
		# Inicio Codigo para traer los datos fijos		
		usuarioApp = Usuario.objects.get(user=request.user)
		if proceso.apuntador == '1':
			datos = Proyecto_empresas.objects.filter(empresa=usuarioApp.empresa,
				proyecto__id__in=FProcesoRelacion.objects.filter(
					proceso=proceso).values('idApuntador')).order_by(
						'proyecto__municipio__departamento__nombre','proyecto__municipio__nombre').values(
							'proyecto__id','proyecto__municipio__departamento__nombre',
							'proyecto__municipio__nombre','proyecto__nombre','proyecto__mcontrato__nombre')

		else:
			datos = Contrato.objects.filter(id__in=FProcesoRelacion.objects.filter(
				proceso=proceso).values('idApuntador')).order_by(
				'numero').values('id','nombre','numero','contratante__nombre','contratista__nombre')
		
		rowData=1
		colData=0
		for data in datos:
			#import pdb; pdb.set_trace()
			if proceso.apuntador == '1':
				if proceso.etiqueta != '' and proceso.tablaForanea:
					
					listaProcesoRelacion = FProcesoRelacion.objects.filter(
						idApuntador=data['proyecto__id'],proceso=proceso).values('id','idTablaReferencia')
					for pr in listaProcesoRelacion:
						worksheet.write(rowData,colData,data['proyecto__mcontrato__nombre'])
						worksheet.write(rowData,colData+1,data['proyecto__municipio__departamento__nombre'])
						worksheet.write(rowData,colData+2,data['proyecto__municipio__nombre'])
						worksheet.write(rowData,colData+3,data['proyecto__nombre'])
						numeroContrato = Proyecto.objects.filter(contrato__tipo_contrato__id=8,
							id=data['proyecto__id']).values('contrato__numero')
						if numeroContrato.count()>0:
							worksheet.write(rowData,colData+4,numeroContrato[0]['contrato__numero'])

						f=colData+5
						#Codigo para consultar el avance del proceso para este elemento
						prdCumplidos = GProcesoRelacionDato.objects.filter(
							procesoRelacion__id=pr['id'],estado=1)
						procesoRelacionDatos = GProcesoRelacionDato.objects.filter(
							procesoRelacion__id=pr['id']).values('valor','id').order_by('item__orden')
						if proceso.etiqueta:
							modeloReferencia = ContentType.objects.get(pk=proceso.tablaForanea.id).model_class()
							elemento = modeloReferencia.objects.filter(
												id=pr['idTablaReferencia']).values(proceso.etiqueta)
							worksheet.write(rowData,f,elemento[0][proceso.etiqueta])

						f=f+1

						#fin codigo para consultar el avance del proceso para este elemento					
						if nombre !='':
							#agrego valores de campos dinamicos		
							for campo in camposInforme:

								if campo['tablaForanea__name']:
									nombreCampo = campo['nombreCampoApuntador'] + '__' + campo['campoTablaForanea']
								else:
									nombreCampo = campo['nombreCampoApuntador']
								proy=Proyecto.objects.get(id=data['proyecto__id']).values(nombreCampo)
								
								worksheet.write(rowdata,f,proy[0][nombreCampo])
								f=f+1
							#colData=colData+f		
						#worksheet.write(rowData,f,elemento[0][proceso.etiqueta])
						#f=f+1
						worksheet.write(rowData,f,(float(prdCumplidos.count())/float(procesoRelacionDatos.count()))*100)
						f=f+1
						for prd in procesoRelacionDatos:
							if prd['valor']!='Vacio':
								cantidadArchivos=0
								cantidadArchivos = HSoporteProcesoRelacionDato.objects.filter(
													procesoRelacionDato__id=prd['id']).count()
								if cantidadArchivos>0:
									disponible=' - Disponible en el sistema'
								else:
									disponible = ' - Sin soporte'

								worksheet.write(rowData,f,str(prd['valor'])+disponible)
							f=f+1
						rowData=rowData+1
				else:
					listaProcesoRelacion = FProcesoRelacion.objects.filter(
						idApuntador=data['proyecto__id'],proceso=proceso).values('id')
					for pr in listaProcesoRelacion:
						worksheet.write(rowData,colData,data['proyecto__mcontrato__nombre'])
						worksheet.write(rowData,colData+1,data['proyecto__municipio__departamento__nombre'])
						worksheet.write(rowData,colData+2,data['proyecto__municipio__nombre'])
						worksheet.write(rowData,colData+3,data['proyecto__nombre'])
						#import pdb; pdb.set_trace()
						numeroContrato = Proyecto.objects.filter(contrato__tipo_contrato__id=8,
							id=data['proyecto__id']).values('contrato__numero')
						if numeroContrato:
							worksheet.write(rowData,colData+4,numeroContrato[0]['contrato__numero'])
						f=colData+5	
						#Codigo para consultar el avance del proceso para este elemento
						prdCumplidos = GProcesoRelacionDato.objects.filter(
							procesoRelacion__id=pr['id'],estado='1')
						

						procesoRelacionDatos = GProcesoRelacionDato.objects.filter(
							procesoRelacion__id=pr['id']).values('valor','id').order_by('item__orden')


						#fin codigo para consultar el avance del proceso para este elemento					
						if nombre !='':
							#agrego valores de campos dinamicos							
							for campo in camposInforme:
								if campo['tablaForanea__name']:
									nombreCampo = campo['nombreCampoApuntador'] + '__' + campo['campoTablaForanea']
								else:
									nombreCampo = campo['nombreCampoApuntador']
								proy=Proyecto.objects.filter(id=data['proyecto__id']).values(nombreCampo)
								
								worksheet.write(rowData,f,proy[0][nombreCampo])
								f=f+1
							#colData=colData+f		
						worksheet.write(rowData,f,(float(prdCumplidos.count())/float(procesoRelacionDatos.count()))*100)
						f=f+1
						#f=colData+4
						for prd in procesoRelacionDatos:
							if prd['valor']!='Vacio':
								cantidadArchivos=0
								cantidadArchivos = HSoporteProcesoRelacionDato.objects.filter(
													procesoRelacionDato__id=prd['id']).count()
								if cantidadArchivos>0:
									disponible=' - Disponible en el sistema'
								else:
									disponible = ' - Sin soporte'

								worksheet.write(rowData,f,str(prd['valor']) + disponible)
							f=f+1	
						rowData=rowData+1
			else:
				# Inicio codigo para traer los datos de la columna de segundo nivel
				if proceso.etiqueta != '' and proceso.tablaForanea:
					listaProcesoRelacion = FProcesoRelacion.objects.filter(
						idApuntador=data['id'],proceso=proceso).values('id','idTablaReferencia')
					for pr in listaProcesoRelacion:
						modeloReferencia = ContentType.objects.get(pk=proceso.tablaForanea.id).model_class()
						elemento = modeloReferencia.objects.filter(
											id=pr['idTablaReferencia']).values(proceso.etiqueta)

						worksheet.write(rowData,colData,data['nombre'])	
						worksheet.write(rowData,colData+1,data['numero'])
						worksheet.write(rowData,colData+2,data['contratante__nombre'])		
						worksheet.write(rowData,colData+3,data['contratista__nombre'])
						
						f=colData+4
						#Codigo para consultar el avance del proceso para este elemento
						prdCumplidos = GProcesoRelacionDato.objects.filter(
							procesoRelacion__id=pr['id'],estado=1)				

						procesoRelacionDatos = GProcesoRelacionDato.objects.filter(
							procesoRelacion__id=pr['id']).values('valor','id').order_by('item__orden')


						#fin codigo para consultar el avance del proceso para este elemento						
						if nombre !='':
							#agrego valores de campos dinamicos
							for campo in camposInforme:

								if campo['tablaForanea__name']:
									nombreCampo = campo['nombreCampoApuntador'] + '__' + campo['campoTablaForanea']
								else:
									nombreCampo = campo['nombreCampoApuntador']
								proy=Proyecto.objects.get(id=data['id']).values(nombreCampo)
								
								worksheet.write(rowdata,f,proy[0][nombreCampo])
								f=f+1

						if elemento:
							worksheet.write(rowData,f,elemento[0][proceso.etiqueta])
						f=f+1
						worksheet.write(rowData,f,(float(prdCumplidos.count())/float(procesoRelacionDatos.count()))*100)
						f=f+1
						# Fin codigo para traer los datos de la columna de segundo nivel
					
						for prd in procesoRelacionDatos:
							if prd['valor']!='Vacio':
								cantidadArchivos=0
								cantidadArchivos = HSoporteProcesoRelacionDato.objects.filter(
													procesoRelacionDato__id=prd['id']).count()
								if cantidadArchivos>0:
									disponible=' - Disponible en el sistema'
								else:
									disponible = ' - Sin soporte'
								worksheet.write(rowData,f,str(prd['valor']) + disponible )
							f=f+1
						rowData=rowData+1		
				else:
					listaProcesoRelacion = FProcesoRelacion.objects.filter(
						idApuntador=data['id'],proceso=proceso).values('id')
					for pr in listaProcesoRelacion:
						worksheet.write(rowData,colData,data['nombre'])	
						worksheet.write(rowData,colData+1,data['numero'])
						worksheet.write(rowData,colData+2,data['contratante__nombre'])		
						worksheet.write(rowData,colData+3,data['contratista__nombre'])

						f=colData+4
						#Codigo para consultar el avance del proceso para este elemento
						prdCumplidos = GProcesoRelacionDato.objects.filter(
							procesoRelacion__id=pr['id'],estado=1)					

						procesoRelacionDatos = GProcesoRelacionDato.objects.filter(
							procesoRelacion__id=pr['id']).values('valor','id').order_by('item__orden')

						worksheet.write(rowData,f,(float(prdCumplidos.count())/float(procesoRelacionDatos.count()))*100)
						f=f+1
						#fin codigo para consultar el avance del proceso para este elemento

						if nombre !='':
							#agrego valores de campos dinamicos
							for campo in camposInforme:

								if campo['tablaForanea__name']:
									nombreCampo = campo['nombreCampoApuntador'] + '__' + campo['campoTablaForanea']
								else:
									nombreCampo = campo['nombreCampoApuntador']
								proy=Proyecto.objects.get(id=data['id']).values(nombreCampo)
								
								worksheet.write(rowdata,f,proy[0][nombreCampo])
								f=f+1

						#f=colData+4
						for prd in procesoRelacionDatos:
							if prd['valor']!='Vacio':
								cantidadArchivos=0
								cantidadArchivos = HSoporteProcesoRelacionDato.objects.filter(
													procesoRelacionDato__id=prd['id']).count()
								if cantidadArchivos>0:
									disponible=' - Disponible en el sistema'
								else:
									disponible = ' - Sin soporte'

								worksheet.write(rowData,f,str(prd['valor'])+disponible)
							f=f+1								
						rowData=rowData+1
		# Fin Codigo para traer los datos fijos
	
		workbook.close()

		return response	
	except Exception as e:
		print(e)
		functions.toLog(e,'proceso.GeneracionInforme')

def pagarFactura(request, id_factura, fecha):
	try:
		model_factura = Factura.objects.get(pk=id_factura)

		model_factura.fecha_pago=fecha
		model_factura.pagada=1
		model_factura.save()

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='factura.facturas',id_manipulado=id_factura)
		logs_model.save()
	except Exception as e:
		functions.toLog(e, 'Proceso.pagarFactura')

@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			archivo = HSoporteProcesoRelacionDato.objects.get(pk=request.GET['id'])
			
			filename = ""+str(archivo.documento)+""
			extension = filename[filename.rfind('.'):]
			nombre = re.sub('[^A-Za-z0-9 ]+', '', archivo.nombre)
			return functions.exportarArchivoS3(str(archivo.documento),  nombre + extension)

		except Exception as e:
			functions.toLog(e,'proceso.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			

