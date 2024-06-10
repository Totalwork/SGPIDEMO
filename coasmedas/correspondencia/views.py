# -*- coding: utf-8 -*- 
from coasmedas.functions import functions
from datetime import date
import datetime
import shutil
import time
import os
from io import StringIO
from django.db.models import Max

from django.contrib.auth.models import User, Permission, Group

from django.shortcuts import render
#, render_to_response
from django.urls import reverse
from django.db import transaction
from .models import CorrespondenciaEnviada,  CorrespondenciaConsecutivo, CorresPfijo , CorrespondenciaSoporte , CorrespondenciaRadicado , CorrespondenciaPlantilla
from rest_framework import viewsets, serializers, response
from django.db.models import Q
from django.template import RequestContext
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
import xlsxwriter
import json
from django.http import HttpResponse,JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import connection
from django.contrib.auth.decorators import login_required
# Create your views here.
from empresa.models import Empresa , EmpresaAcceso
from empresa.views import EmpresaSerializer
from usuario.models import Usuario ,Persona
from usuario.views import UsuarioSerializer ,PersonaSerializer
from estado.models import Estado
from estado.views import EstadoSerializer
from tipo.models import Tipo
from tipo.views import TipoSerializer

from parametrizacion.models import Municipio ,Funcionario ,Departamento 
from parametrizacion.views import MunicipioSerializer , FuncionarioSerializer , DepartamentoSerializer

from contrato.models import Contrato,EmpresaContrato
from contrato.views import ContratoSerializer

from proyecto.models import Proyecto , Proyecto_empresas
from proyecto.views import ProyectoSerializer

from correspondencia_recibida.models import CorrespondenciaRecibida , CorrespondenciaRecibidaAsignada

import uuid

from rest_framework.decorators import api_view
from .enumeration import EnumTipoCorrespondecia

from babel.dates import format_date, format_datetime, format_time
from babel.numbers import format_number, format_decimal, format_percent
from numbertoletters import number_to_letters


from django.conf import settings
from docx import Document
from docx.shared import Inches , Pt
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.style import WD_STYLE
from docx.enum.text import WD_ALIGN_PARAGRAPH

import os
import mimetypes
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper

from logs.models import Logs,Acciones
# from datetime import *
from django.db import transaction,connection
from django.db.models.deletion import ProtectedError
import re



#----------------------------------------------------------------------
class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('id','username',)		
class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	class Meta:
		model = Empresa
		fields=('id' , 'nombre'	)
class PersonaLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	class Meta:
		model = Persona
		fields = ('id', 'nombres','apellidos')
class UsuarioLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""
	user=UserSerializer(read_only=True)	
	persona = PersonaLiteSerializer(read_only=True)
	class Meta:
		model = Usuario
		fields=('id', 'persona' , 'user')
class FuncionarioLiteSerializer(serializers.HyperlinkedModelSerializer):	
	persona = PersonaLiteSerializer(read_only=True)	
	class Meta:
		model = Funcionario
		fields=('id','persona')

class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	tipo_contrato = TipoSerializer(read_only=True)
	contratista = EmpresaLiteSerializer(read_only=True)
	contratante = EmpresaLiteSerializer(read_only=True)
	class Meta:
		model = Contrato
		fields=('id' , 'nombre'	, 'contratista' , 'contratante' , 'tipo_contrato' , 'numero')

class CorresPfijoLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	class Meta:
		model = CorresPfijo
		fields=('id', 'nombre')
		
#Api rest para prefijos de correspondencia
class CorresPfijoSerializer(serializers.HyperlinkedModelSerializer):
	empresa = EmpresaLiteSerializer(read_only = True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Empresa.objects.all())
	
	class Meta:
		model = CorresPfijo
		fields=('id' , 'nombre' , 'empresa' ,'empresa_id' , 'estado')
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'empresa_id' , 'nombre' ),
				message=('El nombre del prefijo  no puede  estar repetido en la empresa.')
				)
				]
class CorresPfijoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de prefijos de correspondencia , 
	<br>puede utilizar el parametro (dato) a traves del cual puede consultar todos los prefijo.
	<br>puede utilizar el parametro (empresa) a traves del cual puede consultar todos los prefijo de una empresa en especifico.
	"""
	model = CorresPfijo
	queryset = model.objects.all()
	serializer_class = CorresPfijoSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CorresPfijoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			empresa = self.request.query_params.get('empresa', None)
			estado = self.request.query_params.get('estado', None)

			# qset=(~Q(id=0))
			if estado:
				qset=(Q(estado=estado))
			else:
				qset=(Q(estado=True))
			
			if (dato or empresa):
				if dato:
					qset = qset & ( Q(nombre__icontains=dato) )

				if empresa:
					qset = qset &( Q(empresa = empresa) )

				queryset = self.model.objects.filter(qset)
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})				
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:

				serializer = CorresPfijoSerializer( data=request.DATA,context={'request': request})		
				if serializer.is_valid():
					serializer.save(empresa_id = request.DATA['empresa_id'])
					
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia.CorresPfijo',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "nombre" in serializer.errors:
						mensaje = serializer.errors["nombre"][0]
					else:
						mensaje = 'datos requeridos no fueron recibidos'

					return Response({'message': mensaje ,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = CorresPfijoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(empresa_id = request.DATA['empresa_id'])
					# self.perform_update(serializer)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	
#Fin api rest para prefijos correspondencia	

#Api rest para radicados de las correspondencias recibidas
class CorrespondenciaRadicadoSerializer(serializers.HyperlinkedModelSerializer):
	empresa = EmpresaLiteSerializer(read_only = True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Empresa.objects.all())
	
	class Meta:
		model = CorrespondenciaRadicado
		fields=('id' , 'empresa' ,'empresa_id' , 'ano' , 'numero')
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'empresa_id' , 'ano' ),
				message=('El año del radicado no puede  estar repetido en la empresa.')
				)
				]
class CorrespondenciaRadicadoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de radicados de las  correspondencias recibidas , 
	<br>puede utilizar el parametro (dato) a traves del cual puede consultar todos los radicados.
	<br>puede utilizar el parametro (empresa) a traves del cual puede consultar todos los radicados de una empresa en especifico.
	"""
	model = CorrespondenciaRadicado
	queryset = model.objects.all()
	serializer_class = CorrespondenciaRadicadoSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CorrespondenciaRadicadoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			empresa = self.request.query_params.get('empresa', None)
		
			qset=(~Q(id=0))		
			if (dato or empresa):
				if dato:
					qset = qset & ( Q(ano__icontains=dato) | Q(numero__icontains=dato) )

				if empresa:
					qset = qset &( Q(empresa = empresa) )

				queryset = self.model.objects.filter(qset)
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})				
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:

				serializer = CorrespondenciaRadicadoSerializer( data=request.DATA,context={'request': request})		
				if serializer.is_valid():
					serializer.save(empresa_id = request.DATA['empresa_id'])
					
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia.CorresPfijo',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:

					# print(serializer.errors)
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "nombre" in serializer.errors:
						mensaje = serializer.errors["nombre"][0]
					else:
						mensaje = 'datos requeridos no fueron recibidos'

					return Response({'message': mensaje ,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = CorrespondenciaRadicadoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(empresa_id = request.DATA['empresa_id'])
					# self.perform_update(serializer)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	
#Fin api rest para radicados de las  correspondencias recibidas	

#Api rest para consecutivos de correspondencia
class CorrespondenciaConsecutivoSerializer(serializers.HyperlinkedModelSerializer):	
	prefijo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=CorresPfijo.objects.all())
	prefijo = CorresPfijoSerializer(read_only = True)
	class Meta:
		model = CorrespondenciaConsecutivo
		fields=('id' , 'ano' , 'numero' , 'prefijo' , 'prefijo_id')
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( "prefijo_id", "ano" ),
				message=('El numero del consecutivo  no se puede repetir (anualidad , prefijo).')
				)
				]

class CorrespondenciaConsecutivoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de consecutivos de las correspondencias , 
	<br>puede utilizar el parametro (dato) a traves del cual puede consultar todos los consecutivos.
	<br>puede utilizar el parametro (empresa) a traves del cual puede consultar todos los consecutivos de una empresa en especifico.
	"""
	model = CorrespondenciaConsecutivo
	queryset = model.objects.all()
	serializer_class = CorrespondenciaConsecutivoSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CorrespondenciaConsecutivoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			empresa = self.request.query_params.get('empresa', request.user.usuario.empresa.id)
			numero = self.request.query_params.get('numero', None)
			tipo = self.request.query_params.get('tipo', None)
			
			qset=(~Q(id=0))
			if (dato or empresa or tipo):
				if dato:
					qset = qset & (Q(numero__icontains= numero))
				if empresa:
					qset = qset & ( Q(prefijo__empresa = empresa) )
				if numero:
					qset = qset & ( Q(numero = numero) )	
									
				queryset = self.model.objects.filter(qset)
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})				
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = CorrespondenciaConsecutivoSerializer( data=request.DATA,context={'request': request})		
				if serializer.is_valid():
					serializer.save(prefijo_id = request.DATA["prefijo_id"])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia.CorrespondenciaConsecutivo',id_manipulado=serializer.data['id'])
					logs_model.save()
										
					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					# print(serializer.errors)
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "ano" in serializer.errors:
						mensaje = serializer.errors["ano"][0]
					elif "numero" in serializer.errors:
						mensaje = serializer.errors["numero"][0]
					else:
						mensaje = 'datos requeridos no fueron recibidos'

					return Response({'message':mensaje ,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = CorrespondenciaConsecutivoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					# self.perform_update(serializer)
					serializer.save(prefijo_id = request.DATA["prefijo_id"] )

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					# print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	
#Fin api rest para consecutivos correspondencia	

#Api rest para CorrespondenciaEnviada

# ANULAR CARTA
@transaction.atomic
def destroyCorrespondenciaEnviada(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']
			# print myList
			CorrespondenciaEnviada.objects.filter(id__in = myList).update(anulado = 1)
			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok','data': ''})
		except Exception as e:
			# print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ESTABLECER CARTA 
@transaction.atomic
def establishCorrespondenciaEnviada(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']
			CorrespondenciaEnviada.objects.filter(id__in = myList).update(anulado = 0)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok','data': ''})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# // -- CorrespondenciaEnviada Contratos -- //# // -- CorrespondenciaEnviada Contratos -- //# // -- CorrespondenciaEnviada Contratos -- //
@transaction.atomic
def createCorrespondenciaEnviadaContrato(request):
	if request.method == 'POST': 
		sid = transaction.savepoint()
		try:
			correspondenciaenviada_id = request.POST['correspondenciaenviada_id']
			myList = request.POST['contrato_id'].split(',')
			model = CorrespondenciaEnviada.objects.get(pk=correspondenciaenviada_id)
			model.contrato.add(*myList)

			cc= model.contrato.through.objects.filter(contrato_id__in = myList)

			insert_list = []
			for i in cc:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_crear
										,nombre_modelo='correspondencia.CorrespondenciaEnviada.contrato'
										,id_manipulado=i.id)
										)
		
			Logs.objects.bulk_create(insert_list)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
		except Exception as e:
			transaction.savepoint_rollback(sid)
			# print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def destroyCorrespondenciaEnviadaContrato(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['contrato_id']
			model = CorrespondenciaEnviada.objects.get(pk=respuesta['correspondenciaenviada_id'])			
			cc= model.contrato.through.objects.filter(contrato_id__in = myList)

			insert_list = []
			for i in cc:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_borrar
										,nombre_modelo='correspondencia.CorrespondenciaEnviada.contrato'
										,id_manipulado=i.id)
										)
		
			Logs.objects.bulk_create(insert_list)

			model.contrato.remove(*myList)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			transaction.savepoint_rollback(sid)
			# print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def listCorrespondenciaEnviadaContrato(request):
	if request.method == 'GET':
		try:
			correspondenciaId = request.GET['correspondencia_id'] if 'correspondencia_id' in request.GET else None
			contrato = request.GET['contrato_id'] if 'contrato_id' in request.GET else None
			dato = request.GET['dato'] if 'dato' in request.GET else None
			tipoContrato = request.GET['tipoContrato'] if 'tipoContrato' in request.GET else None

			if dato or correspondenciaId or contrato or tipoContrato:
				if correspondenciaId:
					model = CorrespondenciaEnviada.objects.get(pk=correspondenciaId)

					if contrato is not None and int(contrato)>0 :
						queryset = model.contrato.filter(id = contrato).values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero')
					else:
						queryset = model.contrato.all().values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero')
				
					if dato:
						queryset  = queryset.filter( Q(nombre__icontains = dato) | Q(numero__icontains = dato))

				elif contrato:
					queryset = CorrespondenciaEnviada.objects.filter(contrato__id = contrato).values('id', 'contrato__nombre' , 'contrato__tipo_contrato__nombre' , 'contrato__numero')
					# print queryset.query
			return JsonResponse({'message':'','success':'ok','data':list(queryset)})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin de funciones de correspondencias asocidas a contratos

def listContratosSinCorrespondenciaEnviada(request):
	if request.method == 'GET':
		try:
			# filtro por id de correspondencia
			dato = request.GET['dato'] if 'dato' in request.GET else None;
			correspondenciaId = request.GET['correspondencia'] if 'correspondencia' in request.GET else None;
			estado = request.GET['estado'] if 'estado' in request.GET else None;
			macroContrato = request.GET['mcontrato'] if 'mcontrato' in request.GET else None;

			c = CorrespondenciaEnviada.objects.get(pk=correspondenciaId)
			qContrato = c.contrato.all()
			qset =  (Q(numero__icontains = dato) | Q(nombre__icontains = dato))

			empresaId = request.user.usuario.empresa.id

			contratos = EmpresaContrato.objects.filter(empresa_id = empresaId).values('contrato__id')		

			if estado:
				qset = qset & (Q(estado_id = estado))
			if macroContrato:
				qset = qset & (Q(mcontrato_id = macroContrato))

			queryset = Contrato.objects.filter(qset , id__in = contratos).values('id', 'nombre', 'numero' , 'tipo_contrato__nombre').exclude(pk__in = qContrato)

			return JsonResponse({'message':'','success':'ok','data':list(queryset)})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin de funciones de proyecto asocido a contratos


# // -- CorrespondenciaEnviada Proyectos -- //# // -- CorrespondenciaEnviada Proyectos -- //# // -- CorrespondenciaEnviada Proyectos -- //
@transaction.atomic
def createCorrespondenciaEnviadaProyecto(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			myList = request.POST['proyecto_id'].split(',')
			model = CorrespondenciaEnviada.objects.get(pk=request.POST['correspondenciaenviada_id'])
			model.proyecto.add(*myList)
			cc= model.proyecto.through.objects.filter(proyecto_id__in = myList)
			insert_list = []
			for i in cc:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_crear
										,nombre_modelo='correspondencia.CorrespondenciaEnviada.proyecto'
										,id_manipulado=i.id)
										)
			Logs.objects.bulk_create(insert_list)

			transaction.savepoint_commit(sid)

			return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def destroyCorrespondenciaEnviadaProyecto(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['proyecto_id']
			model = CorrespondenciaEnviada.objects.get(pk=respuesta['correspondenciaenviada_id'])

			cc= model.proyecto.through.objects.filter(proyecto_id__in = myList)

			insert_list = []
			for i in cc:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_borrar
										,nombre_modelo='correspondencia.CorrespondenciaEnviada.proyecto'
										,id_manipulado=i.id)
										)
		
			Logs.objects.bulk_create(insert_list)

			model.proyecto.remove(*myList)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def listCorrespondenciaEnviadaProyecto(request):
	if request.method == 'GET':
		try:
			correspondenciaId = request.GET['correspondencia_id'] if 'correspondencia_id' in request.GET else None;
			proyecto = request.GET['proyecto_id'] if 'proyecto_id' in request.GET else None;
			dato = request.GET['dato'] if 'dato' in request.GET else None;

			if dato or correspondenciaId or proyecto:
				if correspondenciaId:
					model = CorrespondenciaEnviada.objects.get(pk=correspondenciaId)
					queryset = model.proyecto.all().values('id' , 'nombre' , 'mcontrato__nombre' , 'tipo_proyecto__nombre')
					if dato:
						queryset = queryset.filter( Q(nombre__icontains = dato) ).values('id', 'nombre' , 'mcontrato__nombre' , 'tipo_proyecto__nombre')

				elif proyecto:
					queryset = CorrespondenciaEnviada.objects.filter(proyecto__id = proyecto).values('id', 'consecutivo' , 'asunto' , 'fechaEnvio' , 'empresa__nombre' , 'firma__persona__nombres' , 'firma__persona__apellidos' , 'prefijo__nombre')
					# print queryset.query
			return JsonResponse({'message':'','success':'ok','data':list(queryset)})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def listProyectosSinCorrespondenciaEnviada(request):
	if request.method == 'GET':
		try:
			# filtro por id de correspondencia
			dato = request.GET['dato'] if 'dato' in request.GET else None;
			correspondenciaId = request.GET['correspondencia'] if 'correspondencia' in request.GET else None;
			macroContrato = request.GET['mcontrato'] if 'mcontrato' in request.GET else None;

			c = CorrespondenciaEnviada.objects.get(pk=correspondenciaId)
			qProyecto = c.proyecto.all()
			qset =  ( Q(nombre__icontains = dato))

			empresaId = request.user.usuario.empresa.id

			proyectos = Proyecto_empresas.objects.filter(empresa_id = empresaId).values('proyecto_id')

			if macroContrato:
				qset = qset & ( Q(mcontrato_id = macroContrato) )

			queryset = Proyecto.objects.filter(qset , id__in = proyectos).values('id', 'nombre' , 'mcontrato__nombre' , 'tipo_proyecto__nombre').exclude(pk__in = qProyecto)

			return JsonResponse({'message':'','success':'ok','data':list(queryset)})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)	

class CorrespondenciaEnviadaSerializer(serializers.HyperlinkedModelSerializer):

	ciudad = MunicipioSerializer(read_only =True)
	ciudad_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Municipio.objects.all())

	empresa = EmpresaLiteSerializer(read_only =True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Empresa.objects.all())

	usuarioSolicitante = UsuarioLiteSerializer(read_only =True)
	usuarioSolicitante_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	municipioEmpresa = MunicipioSerializer(read_only =True)
	municipioEmpresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Municipio.objects.all())

	prefijo = CorresPfijoLiteSerializer(read_only =True)
	prefijo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=CorresPfijo.objects.all())

	firma = FuncionarioSerializer(read_only =True)
	firma_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Funcionario.objects.all())

	totalSoportes = serializers.SerializerMethodField()

	class Meta:
		model = CorrespondenciaEnviada
		fields=('id' 
				, 'empresa'
				, 'empresa_id' 
				, 'usuarioSolicitante' 
				, 'usuarioSolicitante_id' 
				, 'consecutivo' 
				, 'fechaEnvio'
				, 'anoEnvio'
				, 'asunto'
				, 'referencia'
				, 'fechaRegistro'
				, 'grupoSinin'
				, 'persona_destino'
				, 'cargo_persona'
				, 'direccion'
				, 'municipioEmpresa'
				, 'municipioEmpresa_id'
				, 'telefono'
				, 'contenido'
				, 'contenidoHtml'
				, 'firma' , 'firma_id'
				, 'ciudad' , 'ciudad_id'
				, 'privado'
				, 'empresa_destino'
				, 'anulado'
				, 'prefijo' , 'prefijo_id'
				, 'totalSoportes'
				)

		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'empresa_id' , 'consecutivo' , 'anoEnvio'),
				message=('El consecutivo no puede  estar repetido en la misma anualidad de envio.')
				)
				]
	def get_totalSoportes(self, obj):
		# code here to calculate the result
		# or return obj.calc_result() if you have that calculation in the models
		return CorrespondenciaSoporte.objects.filter(correspondencia_id = obj.id , anulado = 0).count()


class CorrespondenciaEnviadaLiteSerializer(serializers.HyperlinkedModelSerializer):
	empresa = EmpresaLiteSerializer(read_only =True)
	usuarioSolicitante = UsuarioLiteSerializer(read_only =True)
	prefijo = CorresPfijoLiteSerializer(read_only =True)
	totalSoportes = serializers.SerializerMethodField()
	class Meta:
		model = CorrespondenciaEnviada
		fields=('id' 
				, 'empresa'
				, 'usuarioSolicitante' 
				, 'consecutivo' 
				, 'fechaEnvio'
				, 'asunto'
				, 'referencia'
				, 'persona_destino'
				, 'privado'
				, 'anulado'
				, 'prefijo' 
				, 'totalSoportes'
				)
	def get_totalSoportes(self, obj):
		return CorrespondenciaSoporte.objects.filter(correspondencia_id = obj.id , anulado = 0).count()

class CorrespondenciaEnviadaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model = CorrespondenciaEnviada
	queryset = model.objects.all()
	serializer_class = CorrespondenciaEnviadaSerializer
	nombre_modulo = 'correspondencia.CorrespondenciaEnviadaViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CorrespondenciaEnviadaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)

			correspondenciaId = self.request.query_params.get('correspondencia', 0)

			usuarioId = self.request.query_params.get('usuario', None)
			copia = self.request.query_params.get('copia', None)
						
			firma = self.request.query_params.get('firma', None)
			usuarioElaboro = self.request.query_params.get('usuarioElaboro', None)
			soporte_si = self.request.query_params.get('soporte_si', 0)
			soporte_no = self.request.query_params.get('soporte_no', 0)

			asunto = self.request.query_params.get('asunto', 0)
			referencia = self.request.query_params.get('referencia', 0)
			consecutivo = self.request.query_params.get('consecutivo', 0)
			destinatario = self.request.query_params.get('destinatario', 0)

			fechaDesde = self.request.query_params.get('fechaDesde', None)
			fechaHasta = self.request.query_params.get('fechaHasta', None)

			empresaActual = request.user.usuario.empresa.id
			usuarioActual = request.user.usuario.id

			if (int(correspondenciaId)>0):
				qset = ( Q(id = correspondenciaId ) )
			else:	

				if usuarioElaboro:		
					qset = ( ( Q(empresa_id = empresaActual ) & Q(privado = False ) ) )

				else:
					qset = ( ( Q(empresa_id = empresaActual ) & Q(privado = False ) ) | ( Q(empresa_id = empresaActual ) & Q(privado = True ) & Q(usuarioSolicitante_id = usuarioActual ) ) )


			if firma:
				qset = qset & ( Q(firma_id = firma ) )

			if usuarioElaboro:
				qset = qset & ( Q(usuarioSolicitante_id = usuarioElaboro ) )

			if dato:
	
				if int(asunto)==1 and int(referencia)==0 and int(consecutivo)==0 and int(destinatario)==0:
					qset = qset & ( Q(asunto__icontains = dato ) )

				if int(referencia)==1 and int(asunto)==0 and int(consecutivo)==0 and int(destinatario)==0:
					qset = qset & ( Q(referencia__icontains = dato ) )

				if int(consecutivo)==1 and int(asunto)==0 and int(referencia)==0 and int(destinatario)==0:
					qset = qset & ( Q(consecutivo__icontains = dato ) )
				
				if int(destinatario)==1 and int(asunto)==0 and int(referencia)==0 and int(consecutivo)==0:
					qset = qset & ( Q(persona_destino__icontains = dato ) )

				#  CONBINACIONES DE DOS BUSQUEDA
				if int(asunto)==1 and int(referencia)==1 and int(consecutivo)==0 and int(destinatario)==0:
					qset = qset & ( Q(asunto__icontains = dato ) | Q(referencia__icontains = dato ) )
				if int(asunto)==1 and int(referencia)==0 and int(consecutivo)==1 and int(destinatario)==0:
					qset = qset & ( Q(asunto__icontains = dato ) | Q(consecutivo__icontains = dato ) )
				if int(asunto)==1 and int(referencia)==0 and int(consecutivo)==0 and int(destinatario)==1:
					qset = qset & ( Q(asunto__icontains = dato ) | Q(persona_destino__icontains = dato ) )
				
				if int(asunto)==0 and int(referencia)==1 and int(consecutivo)==1 and int(destinatario)==0:
					qset = qset & ( Q(referencia__icontains = dato ) | Q(consecutivo__icontains = dato ) )
				if int(asunto)==0 and int(referencia)==1 and int(consecutivo)==0 and int(destinatario)==1:
					qset = qset & ( Q(referencia__icontains = dato ) | Q(persona_destino__icontains = dato ) )

				if int(asunto)==0 and int(referencia)==0 and int(consecutivo)==1 and int(destinatario)==1:
					qset = qset & ( Q(consecutivo__icontains = dato ) | Q(persona_destino__icontains = dato ) )
			
				#  CONBINACIONES DE TRES BUSQUEDA	
				if int(asunto)==1 and int(referencia)==1 and int(consecutivo)==1 and int(destinatario)==0:
					qset = qset & ( Q(asunto__icontains = dato ) | Q(referencia__icontains = dato ) | Q(consecutivo__icontains = dato ) )
				if int(asunto)==1 and int(referencia)==1 and int(consecutivo)==0 and int(destinatario)==1:
					qset = qset & ( Q(asunto__icontains = dato ) | Q(referencia__icontains = dato ) | Q(persona_destino__icontains = dato ) )
				if int(asunto)==1 and int(referencia)==0 and int(consecutivo)==1 and int(destinatario)==1:
					qset = qset & ( Q(asunto__icontains = dato ) | Q(consecutivo__icontains = dato ) | Q(persona_destino__icontains = dato ) )
				if int(asunto)==0 and int(referencia)==1 and int(consecutivo)==1 and int(destinatario)==1:
					qset = qset & ( Q(referencia__icontains = dato ) | Q(consecutivo__icontains = dato ) | Q(persona_destino__icontains = dato ) )
				
				#  CONBINACIONES DE CUATRO BUSQUEDA
				if int(asunto)==1 and int(referencia)==1 and int(consecutivo)==1 and int(destinatario)==1:
					qset = qset & ( Q(asunto__icontains = dato ) | Q(referencia__icontains = dato ) | Q(consecutivo__icontains = dato ) | Q(persona_destino__icontains = dato ) )


			if (fechaDesde and (fechaHasta is not None) ):
				qset = qset & ( Q(fechaEnvio__gte= fechaDesde ) )
			
			if ( (fechaDesde is not None) and fechaHasta ):
				qset = qset & ( Q(fechaEnvio__lte=fechaHasta)  )

			if (fechaDesde and fechaHasta):	
				qset = qset & ( Q(fechaEnvio__range = (fechaDesde , fechaHasta) ) )

			if (int(soporte_si)>0 and int(soporte_no)==0):
				queryset = self.model.objects.filter(qset).order_by('-fechaEnvio')
				querySoporte = CorrespondenciaSoporte.objects.filter(anulado = 0).values('correspondencia')# tipo cero correspondencia enviada
				queryset = queryset.filter(id__in = querySoporte)
			elif (int(soporte_si)==0 and int(soporte_no)>0):
				queryset = self.model.objects.filter(qset).order_by('-fechaEnvio')	
				querySoporte = CorrespondenciaSoporte.objects.filter(anulado = 0).values('correspondencia')# tipo cero correspondencia enviada
				queryset = queryset.exclude(id__in = querySoporte)	
			else:
				# print qset 
				queryset = self.model.objects.filter(qset).order_by('-fechaEnvio' , '-consecutivo')

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			serializer_context = {
				'request': request,
			}
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					# serializer = self.get_serializer(page,many=True)
					serializer = CorrespondenciaEnviadaLiteSerializer(page,many=True,context=serializer_context)

					# TRAER DATOS CON PARAMETROS DE REGISTRO
					parametro_select=self.request.query_params.get('parametro_select', None)
					if parametro_select:
						
						qsetFuncionariosFirman = Funcionario.objects.filter(empresa_id = empresaActual ,activo=True).order_by('persona__nombres')
						funcionariosFirmanData = FuncionarioLiteSerializer(qsetFuncionariosFirman,many=True).data

						qsetUsuariosElaboran = Usuario.objects.filter(empresa_id = empresaActual ,user__is_active=True).order_by('persona__nombres')
						usuariosElaboranData = UsuarioLiteSerializer(qsetUsuariosElaboran,many=True).data

						contratos = EmpresaContrato.objects.filter(empresa_id = empresaActual , contrato__tipo_contrato__id = 12).values('contrato_id')

						qsetMcontratos = Contrato.objects.filter(pk__in = contratos)
						mcontratosData = ContratoLiteSerializer(qsetMcontratos,many=True).data

						qsetEstadoContratos = Estado.objects.filter(app = "contrato")
						estadosContratosData = EstadoSerializer(qsetEstadoContratos,many=True).data
					
						return self.get_paginated_response({'message':'','success':'ok'
							,'data':{ 'correspondencias':serializer.data 
									, 'funcionarios':funcionariosFirmanData
									, 'usuarios' : usuariosElaboranData
									, 'mcontratos' : mcontratosData									
									, 'estadoContratos' : estadosContratosData
									 }})

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

			serializer = self.get_serializer(queryset,many=True)

			return Response({'message':'','success':'ok','data':serializer.data})				
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':			
			try:			
				fecha = request.DATA['fechaEnvio'] if 'fechaEnvio' in request.DATA else None;
				anoEnvio = int(fecha[:4])
				grupoSinin = request.DATA['grupoSinin'] if 'grupoSinin' in request.DATA else 0;
				proyecto_id = request.DATA['proyecto_id'] if 'proyecto_id' in request.DATA else 0;
				usuarioActual = request.DATA['usuarioSolicitante_id']

				u = Usuario.objects.get(pk = usuarioActual)
				p = Persona.objects.get(pk = u.persona_id)
				empresaIdActual = u.empresa.id
				empresaConsecutivoDigitado = u.empresa.consecutivoDigitado

				if empresaConsecutivoDigitado:
					consecutivo = request.DATA['consecutivo'] if 'consecutivo' in request.DATA else None;

					# se valida que el consecutivo que esta digitado no exista
					validacion = CorrespondenciaEnviada.objects.filter(consecutivo = consecutivo ,prefijo_id = request.DATA['prefijo_id'] ,anoEnvio = anoEnvio)
					
					if validacion:
						mensaje='El consecutivo ya se encuentra registrado.'
						return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)	

				else:
					
					#  SE CONSULTA EL CONSECUTIVO					
					qsetConsecutivo = (Q(prefijo_id = int(request.DATA['prefijo_id'])))
					qsetConsecutivo = qsetConsecutivo & (Q(ano = int(anoEnvio)))
					
					Cc2 = CorrespondenciaConsecutivo.objects.filter(qsetConsecutivo)					
					if any(Cc2) == True:						
						cC = CorrespondenciaConsecutivo.objects.get(prefijo_id = int(request.DATA['prefijo_id']) ,ano = anoEnvio)	
						consecutivo = cC.numero	
						request.DATA['consecutivo'] = int(consecutivo)													

				correspondencia_respuesta_id = request.DATA['correspondencia_respuesta_id'] if 'correspondencia_respuesta_id' in request.DATA else 0;
				# print "empresaConsecutivoDigitado"
				serializer = CorrespondenciaEnviadaSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					d = datetime.datetime.now()		

					myListDestinatarioCopiar = request.DATA['destinatarioCopia'] if 'destinatarioCopia' in request.DATA else None;
					sid = transaction.savepoint()
					try:
						insert_list = []

						if  int(grupoSinin)>0:
							
							if request.DATA['destinatario'] == "":
								mensaje='Seleccione el destinatario.'
								return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
							
							destinatario = int(request.DATA['destinatario'])
							usuarioDestinatario = Usuario.objects.get(pk = destinatario)
							
							try:
								usuarioDestinatarioFuncionario = Funcionario.objects.get(persona_id = usuarioDestinatario.persona.id
																				 ,empresa_id = usuarioDestinatario.empresa.id)
								cargo = usuarioDestinatarioFuncionario.cargo.nombre
							except Funcionario.DoesNotExist:
								cargo = None
								mensaje='El destinatario no tiene un cargo asignado o verifigue la empresa.'
								return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)	

							# print "serializer.save"
							serializer.save( empresa_id = empresaIdActual
											,anoEnvio = anoEnvio
											,ciudad_id = request.DATA['ciudad_id']
											,prefijo_id = request.DATA['prefijo_id']
											,firma_id = request.DATA['firma_id']
											,anulado = 0
											,consecutivo = consecutivo
											,grupoSinin = 1
											,persona_destino = usuarioDestinatario.persona.nombres+' '+usuarioDestinatario.persona.apellidos
											,cargo_persona = cargo
											,empresa_destino = usuarioDestinatario.empresa.nombre
											,direccion = usuarioDestinatario.empresa.direccion	
											,municipioEmpresa_id = request.DATA['municipioEmpresa_id']
											,usuarioSolicitante_id = usuarioActual
											 )

							if not usuarioDestinatario.empresa.consecutivoDigitado:
								radicado = CorrespondenciaRadicado.objects.get(empresa_id = usuarioDestinatario.empresa.id, ano = d.year)

								cR = CorrespondenciaRecibida(
													radicado = radicado.numero, fechaRecibida = fecha, anoRecibida = anoEnvio 
													,remitente = p.nombres+' '+p.apellidos
													,asunto = request.DATA['asunto']
													,privado = 1 # carta privada
													,correspondenciaEnviada_id = serializer.data["id"]
													,empresa_id = usuarioDestinatario.empresa.id
													,usuarioSolicitante_id = destinatario
													)
								cR.save()
								# SE REGISTRA EL LOG DE LA CORRESPONDENCIA RECIBIDA 
								insert_list.append(Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibida',id_manipulado= cR.id ))
								
								radicado.numero = radicado.numero+1
								radicado.save()

								cRa=CorrespondenciaRecibidaAsignada(
										correspondenciaRecibida_id = cR.id ,usuario_id = destinatario
										,fechaAsignacion = d ,estado_id = 33# estado de la correspondencia por revisar
										,respuesta_id = None ,copia = 0 # boleano false porque no es copia
									)
								cRa.save()
								# SE REGISTRA EL LOG DE LA CORRESPONDENCIA A QUIEN SE LE ASIGNA 
								insert_list.append(Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibidaAsignada',id_manipulado= cRa.id ))
						else:

							serializer.save( empresa_id = empresaIdActual
											,anoEnvio = anoEnvio
											,ciudad_id = request.DATA['ciudad_id']									
											,prefijo_id = request.DATA['prefijo_id']
											,firma_id = request.DATA['firma_id']
											,anulado = 0
											,consecutivo = consecutivo
											,municipioEmpresa_id = request.DATA['municipioEmpresa_id']
											,usuarioSolicitante_id = usuarioActual
										)

						# SE REGISTRA EL LOG DE LA CORRESPONDENCIA ENNVIADA
						insert_list.append(Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia.CorrespondenciaEnviada',id_manipulado=serializer.data['id']))
							
						if not empresaConsecutivoDigitado:
							cC.numero = cC.numero+1
							cC.save()

						correspondenciEnviada = self.model.objects.get(pk=serializer.data["id"])
						if myListDestinatarioCopiar:
							correspondenciEnviada.usuario.add(*myListDestinatarioCopiar)

							# SE REGISTRA EL LOG DE LAS COPIAS QUE SE HACEN A LOS USUARIOS
							insert_list.append(Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia.CorrespondenciaEnviada.usuario',id_manipulado=serializer.data['id']))

						if int(correspondencia_respuesta_id)>0:
							obj = CorrespondenciaRecibidaAsignada(
								correspondenciaRecibida_id = correspondencia_respuesta_id
								, usuario_id = usuarioActual
								, estado_id = 35 # ESTADO RESPONDIDA
								, respuesta_id = serializer.data["id"]
							)
							obj.save()

							# SE REGISTRA EL LOG DE RESPUESTA DE LA CARTA
							insert_list.append(Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibida',id_manipulado=obj.id))

						# INSERTAR PROYECTO
						if proyecto_id and int(proyecto_id)>0:
							correspondenciEnviada.proyecto.add(proyecto_id)	

						if insert_list:
							Logs.objects.bulk_create(insert_list)	
						transaction.savepoint_commit(sid)
						anoEnvio = str(anoEnvio)

						mensaje= str(correspondenciEnviada.prefijo.nombre)+'-'+str(consecutivo)
						if correspondenciEnviada.prefijo.mostrar_ano:
							mensaje = mensaje +'-'+str(anoEnvio[2:4])

						return Response({'message':'Se ha generado el consecutivo No :'+mensaje,'success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)	
					except CorrespondenciaConsecutivo.DoesNotExist as e:
						transaction.savepoint_rollback(sid)
						functions.toLog(e,self.nombre_modulo)						
						mensaje='No existe el (consecutivo ó radicado) para la fecha de envio solicitada.'
						return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

					except CorrespondenciaRadicado.DoesNotExist as e:
						transaction.savepoint_rollback(sid)
						functions.toLog(e,self.nombre_modulo)						
						mensaje='No existe el radicado para la fecha (año) de envio solicitada.'
						return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

					except Exception as e:
						transaction.savepoint_rollback(sid)
						functions.toLog(e,self.nombre_modulo)
						mensaje='El consecutivo no puede  estar repetido en la misma anualidad de envio.'
						return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)					
				else:
					# print(serializer.errors)
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "consecutivo" in serializer.errors:
						mensaje = serializer.errors["consecutivo"][0]+" En el campo consecutivo"
					elif "anoEnvio" in serializer.errors:
						mensaje = serializer.errors["anoEnvio"][0]+" En el campo anoEnvio"
					else:
						mensaje = 'datos requeridos no fueron recibidos'

					return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
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
				serializer = CorrespondenciaEnviadaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					fecha = request.DATA['fechaEnvio']
					d = datetime.datetime.now()

					serializer.save(empresa_id =  request.DATA['empresa_id']
									,ciudad_id = request.DATA['ciudad_id']
									,prefijo_id = request.DATA['prefijo_id']
									,firma_id = request.DATA['firma_id']
									,municipioEmpresa_id = request.DATA['municipioEmpresa_id']
									,usuarioSolicitante_id = request.DATA['usuarioSolicitante_id']
									 )

					# SE REGISTRA LA EDICCION
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='correspondencia.CorrespondenciaEnviada',id_manipulado=serializer.data['id'])
					logs_model.save()
					
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				
				print(e)
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
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	
#Fin api rest para CorrespondenciaEnviada	

#Api rest para CorrespondenciaSoporte
class CorrespondenciaSoporteSerializer(serializers.HyperlinkedModelSerializer):

	correspondencia = CorrespondenciaEnviadaLiteSerializer(read_only = True)
	correspondencia_id = serializers.PrimaryKeyRelatedField(write_only=True , queryset=CorrespondenciaEnviada.objects.all())

	class Meta:
		model = CorrespondenciaSoporte
		fields=(
				'id'
				,'nombre'
				, 'correspondencia' , 'correspondencia_id' 
				,'soporte' 
				,'anulado'
				)

class CorrespondenciaSoporteViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model = CorrespondenciaSoporte
	queryset = model.objects.all()
	serializer_class = CorrespondenciaSoporteSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CorrespondenciaSoporteViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			correspondenciaId = self.request.query_params.get('correspondencia', None)
			# anulado = self.request.query_params.get('anulado', None)

			qset = ( Q(anulado = 0) )

			if dato:
				qset = qset & ( Q(nombre__icontains=dato) )

			if correspondenciaId:
				qset = qset &( Q(correspondencia_id = correspondenciaId) )
			
			queryset = self.model.objects.filter(qset)

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':' No se encontraron registros','success':'ok',
				'data':serializer.data})				
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = CorrespondenciaSoporteSerializer(data=request.DATA,context={'request': request})
				# d = date.today()
				archivo = request.FILES['soporte']
				filename, file_extension = os.path.splitext(archivo.name)
				t = datetime.datetime.now()
				
				# valida si seleccionan para cambiar el nombre del archivo
				if request.POST['nombre'] == '':
					nombre = filename
				else:	
					nombre = request.POST['nombre']

				archivo.name = str(request.user.usuario.empresa.id)+'-'+str(request.user.usuario.id)+'-'+str(t.year)+str(t.month)+str(t.day)+str(t.hour)+str(t.minute)+str(t.second)+str(file_extension)
				destino = archivo

				if serializer.is_valid():
					serializer.save(soporte = destino , nombre = nombre , anulado = 0 ,  correspondencia_id = request.POST['correspondencia_id'])	

					# SE REGISTRA LA CARGA DEL SOPORTE
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia.CorrespondenciaSoporte',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:

					# print(serializer.errors)
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "nombre" in serializer.errors:
						mensaje = serializer.errors["nombre"][0]+" En el campo nombre"
					elif "anulado" in serializer.errors:
						mensaje = serializer.errors["anulado"][0]+" En el campo anulado"
					else:
						mensaje = 'datos requeridos no fueron recibidos'


					return Response({'message': mensaje ,'success':'fail',
			 			'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

@transaction.atomic
def destroyCorrespondenciaSoporte(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['soporte_id']
			CorrespondenciaSoporte.objects.filter(id__in = myList).update(anulado = 1)


			insert_list = []
			for i in myList:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_borrar
										,nombre_modelo='correspondencia.CorrespondenciaSoporte'
										,id_manipulado=i)
										)
			if insert_list:
				Logs.objects.bulk_create(insert_list)

			transaction.savepoint_commit(sid)
			
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Fin api rest para CorrespondenciaSoporte


#Api rest para CorrespondenciaPlantilla
class CorrespondenciaPlantillaSerializer(serializers.HyperlinkedModelSerializer):

	empresa = EmpresaSerializer(read_only = True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True , queryset=Empresa.objects.all())

	class Meta:
		model = CorrespondenciaPlantilla
		fields=('id', 'empresa' , 'empresa_id' ,'soporte' )

class CorrespondenciaPlantillaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de plantillas de las empresas , 
	<br>puede utilizar el parametro (dato) a traves del cual puede consultar todas las plantillas.
	<br>puede utilizar el parametro (empresa) a traves del cual puede consultar las plantillas por empresa.
	"""
	model = CorrespondenciaPlantilla
	queryset = model.objects.all()
	serializer_class = CorrespondenciaPlantillaSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CorrespondenciaPlantillaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			empresa_id = self.request.query_params.get('empresa', None)


			qset=(~Q(id=0))

			if dato:
				qset = qset & ( Q(soporte__icontains=dato) )

			if empresa_id:
				qset = qset &( Q(empresa_id = empresa_id) )
			
			queryset = self.model.objects.filter(qset)

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':' No se encontraron registros','success':'ok',
				'data':serializer.data})				
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = CorrespondenciaPlantillaSerializer(data=request.DATA,context={'request': request})

				archivo = request.FILES['soporte']
				filename, file_extension = os.path.splitext(archivo.name)				
				# valida si seleccionan para cambiar el nombre del archivo
				nombre = filename

				archivo.name = str(request.user.usuario.empresa.id)+'-plantilla-correspondencia-enviada'+str(file_extension)
				destino = archivo

				if serializer.is_valid():
					serializer.save(soporte = destino , empresa_id = request.POST['empresa_id'])	

					# SE REGISTRA LA CARGA DEL SOPORTE
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia.CorrespondenciaPlantilla',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:

					print(serializer.errors)
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje = 'datos requeridos no fueron recibidos'


					return Response({'message': mensaje ,'success':'fail',
			 			'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
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
				serializer = CorrespondenciaPlantillaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				
				archivo = request.FILES['soporte']
				filename, file_extension = os.path.splitext(archivo.name)				
				# valida si seleccionan para cambiar el nombre del archivo
				nombre = filename

				archivo.name = str(request.user.usuario.empresa.id)+'-plantilla-correspondencia-enviada'+str(file_extension)
				destino = archivo

				if serializer.is_valid():
					
					serializer.save(soporte = destino , empresa_id = request.POST['empresa_id'])	

					# SE REGISTRA LA CARGA DEL SOPORTE
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='correspondencia.CorrespondenciaPlantilla',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:

					print(serializer.errors)
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje = 'datos requeridos no fueron recibidos'

					return Response({'message': mensaje ,'success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

#Fin api rest para CorrespondenciaPlantilla

@transaction.atomic
def correspondenciaGenerarConsecutivos(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		nombre_modulo = 'correspondencia.correspondenciaGenerarConsecutivos'
		try:
			# print "mendoza"

			numeroConsecutivo = request.POST['numeroConsecutivo'] if 'numeroConsecutivo' in request.POST else 0;

			municipioEmpresa_id = request.POST['municipioEmpresa_id'] if 'municipioEmpresa_id' in request.POST else None;
			usuarioActual = request.POST['usuarioSolicitante_id']
			fecha = request.POST['fechaEnvio']


			# VALIDACION SI EXISTE EL CONSECUTIVO EN LA EMPRESA
			u = Usuario.objects.get(pk = usuarioActual)
			p = Persona.objects.get(pk = u.persona_id)
			empresaIdActual = u.empresa.id
			empresaConsecutivoDigitado = u.empresa.consecutivoDigitado
				
			if empresaConsecutivoDigitado:
				mensaje='Su empresa no tiene habilitado para generar consecutivos.'
				return JsonResponse({'message': mensaje ,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)		

			else:
				# SE  INCREMENTA EL CONSECUTIVO EN 1
				cC = CorrespondenciaConsecutivo.objects.filter(prefijo_id = request.POST['prefijo_id'] , ano = int(fecha[:4]))	

				if not cC:
					mensaje='No existe el (consecutivo ó radicado) para la fecha de envio solicitada.'
					return JsonResponse({'message': mensaje ,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)		


			# FINALIZA LA VALIDACION DEL CONSECUTIVO

			if municipioEmpresa_id=='undefined':
				municipioEmpresa_id = None

			if int(numeroConsecutivo)>0:
				
				i = 1
				insert_list = []
				
				
				u = Usuario.objects.get(pk = usuarioActual)
				p = Persona.objects.get(pk = u.persona_id)
				empresaIdActual = u.empresa.id

				while i <= int(numeroConsecutivo):
					# print(i)
					# print municipioEmpresa_id
					# SE  INCREMENTA EL CONSECUTIVO EN 1
					cC = CorrespondenciaConsecutivo.objects.get(prefijo_id = request.POST['prefijo_id'] , ano = int(fecha[:4]) )		

					correspondencia=CorrespondenciaEnviada(empresa_id = empresaIdActual
														,fechaEnvio = fecha
														,anoEnvio = int(fecha[:4])
														,ciudad_id = request.POST['ciudad_id']									
														,prefijo_id = request.POST['prefijo_id']
														,firma_id = request.POST['firma_id']
														,anulado = 0
														,consecutivo = cC.numero
														,municipioEmpresa_id = municipioEmpresa_id
														,usuarioSolicitante_id = usuarioActual
														,contenido = ''
														,contenidoHtml = '<p></p>'
													)

					correspondencia.save()
					# SE REGISTRA LA TRANSACCION DE LAS CORRESPONDENCIAS
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia.CorrespondenciaEnviada',id_manipulado=correspondencia.id)
					logs_model.save()	

					insert_list.append(cC.numero)
					cC.numero = cC.numero+1
					cC.save()
					# SE REGISTRA LA TRANSACCION DE LOS CONSECUTIVOS
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='correspondencia.CorrespondenciaConsecutivo',id_manipulado=cC.id)
					logs_model.save()										
					i += 1
				# print("Programa terminado")

				#   # INICIO - Crear el Excel
				unique_filename = uuid.uuid4()
				ruta = settings.STATICFILES_DIRS[0]

				t = datetime.datetime.now()
				nombre_hora = str(usuarioActual)+'-'+str(t.year)+str(t.month)+str(t.day)+str(t.hour)+str(t.minute)+str(t.second)

				nombre_archivo = ruta+'\papelera\Cons'+nombre_hora+'.xlsx'.format(unique_filename)    
				workbook = xlsxwriter.Workbook(nombre_archivo)
				worksheet = workbook.add_worksheet('Correspondencias')

				worksheet.set_column('A:A', 25)
				worksheet.set_column('B:B', 15)
				worksheet.set_column('C:D', 50)
				worksheet.set_column('E:E', 35)
				worksheet.set_column('F:F', 45)

				format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
				format1.set_align('center')
				format1.set_align('vcenter')
				format2=workbook.add_format({'border':0})
				format5=workbook.add_format()
				format5.set_num_format('yyyy-mm-dd')
				format_money=workbook.add_format({'border':False,
					'font_size':11,
					'bold':False,
					'valign':'vright',
					'num_format': '$#,##0'})

				row=1
				col=0

				worksheet.write('A1', unicode('Fecha de envio', 'utf-8'), format1)
				worksheet.write('B1', 'Consecutivo', format1)



				for objecto in insert_list:

					worksheet.write(row, col  ,fecha,format5)
					worksheet.write(row, col+1,objecto,format2)
					row +=1

				workbook.close()# FIN - Crear el Excel

		
					
			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': 'Cons'+nombre_hora})
		except Exception as e:
			functions.toLog(e ,nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)		

def donwloadFileConsecutivos(request):
	if request.method == 'GET':
		try:
			nombre_archivo = request.GET['nombre']
			plantilla = settings.STATICFILES_DIRS[0] + '\papelera/'+str(nombre_archivo)+'.xlsx'
			# print plantilla

			excel = open(plantilla, "rb")
			output = StringIO.StringIO(excel.read())
			out_content = output.getvalue()
			# print out_content
			output.close()
			response = HttpResponse(out_content,content_type='application/vnd.ms-excel;charset=utf-8')
			response['Content-Disposition'] = 'attachment; filename='+str(nombre_archivo)+'.xlsx'
			return response
		except Exception as e:
			print(e)
		


@login_required
def correspondenciaConsecutivos(request):

	departamentos = Departamento.objects.filter().values()
	empresaActual = request.user.usuario.empresa.id
	prefijos = CorresPfijo.objects.filter(empresa_id = empresaActual)
	funcionarios_firman = Funcionario.objects.filter(empresa_id = empresaActual)
	empresas = EmpresaAcceso.objects.filter(empresa_id = empresaActual)

	return render(request, 'correspondencia/correspondenciaEnviadaConsecutivo.html',
			{'empresas':empresas ,'funcionarios_firman':funcionarios_firman, 'departamentos': departamentos, 'prefijos': prefijos 
			, 'model':'correspondenciaenviada','app':'correspondencia'} ,context_instance=RequestContext(request))

@login_required
def correspondenciaEnviada(request):
	return render(request, 'correspondencia/correspondenciaEnviada.html', { 'model':'correspondenciaenviada','app':'correspondencia'} ,context_instance=RequestContext(request))

@login_required
def correspondenciaEnviadaCreate(request , proyecto_id  = None ):

	departamentos = Departamento.objects.filter().values()
	empresaActual = request.user.usuario.empresa.id
	prefijos = CorresPfijo.objects.filter(empresa_id = empresaActual)
	funcionarios_firman = Funcionario.objects.filter(empresa_id = empresaActual ,activo=True).order_by('persona__nombres')
	empresas = EmpresaAcceso.objects.filter(empresa_id = empresaActual)
	
	try:
		if proyecto_id:
			valida = Proyecto_empresas.objects.filter(empresa_id = empresaActual , proyecto_id = proyecto_id)
		else:
			valida = 1
	except Proyecto_empresas.DoesNotExist:
		valida = None

	return render(request, 'correspondencia/correspondenciaEnviadaCreate.html', { 'valida':valida,'empresas':empresas ,'funcionarios_firman':funcionarios_firman,'proyecto_id': proyecto_id , 'departamentos': departamentos, 'prefijos': prefijos ,'model':'correspondenciaenviada','app':'correspondencia'} ,context_instance=RequestContext(request))

@login_required
def correspondenciaEnviadaUpdate(request , id = None):

	correspondencia = CorrespondenciaEnviada.objects.get( pk = id)
	departamentos = Departamento.objects.filter().values()
	empresaActual = request.user.usuario.empresa.id
	prefijos = CorresPfijo.objects.filter(empresa_id = empresaActual)
	funcionarios_firman = Funcionario.objects.filter(empresa_id = empresaActual ,activo=True).order_by('persona__nombres')
	empresas = EmpresaAcceso.objects.filter(empresa_id = empresaActual)

	return render(request, 'correspondencia/correspondenciaEnviadaUpdate.html', {'correspondencia':correspondencia.id, 'empresas':empresas ,'funcionarios_firman':funcionarios_firman , 'id':id , 'departamentos': departamentos, 'prefijos': prefijos ,'model':'correspondenciaenviada','app':'correspondencia'} ,context_instance=RequestContext(request))

@login_required
def correspondenciaEnviadaCopy(request , id = None):

	correspondencia = CorrespondenciaEnviada.objects.get( pk = id)
	departamentos = Departamento.objects.filter().values()
	empresaActual = request.user.usuario.empresa.id
	prefijos = CorresPfijo.objects.filter(empresa_id = empresaActual)
	funcionarios_firman = Funcionario.objects.filter(empresa_id = empresaActual ,activo=True).order_by('persona__nombres')
	empresas = EmpresaAcceso.objects.filter(empresa_id = empresaActual)

	return render(request, 'correspondencia/correspondenciaEnviadaCopy.html', {'correspondencia':correspondencia.id, 'empresas':empresas ,'funcionarios_firman':funcionarios_firman , 'id':id , 'departamentos': departamentos, 'prefijos': prefijos ,'model':'correspondenciaenviada','app':'correspondencia'} ,context_instance=RequestContext(request))

@login_required
def datosRegistrarCorrespondencia(request):
	if request.method == 'GET':
		try:

			empresaActual = request.user.usuario.empresa.id

			qsetDepartamentos = Departamento.objects.filter().values("id" , "nombre")

			qsetPrefijos = CorresPfijo.objects.filter(empresa_id = empresaActual).values("id" , "nombre")

			qsetFuncionariosFirman = Funcionario.objects.filter(empresa_id = empresaActual).values("id" ,"persona__nombres" , "persona__apellidos")

			qsetEmpresas = Empresa.objects.filter(fk_EmpresaAcceso_empresa = empresaActual).values("id" , "nombre")

			return JsonResponse({'message':'','success':'ok'
								,'data': { 'departamentos':list(qsetDepartamentos)
											, 'prefijos':list(qsetPrefijos)
											, 'funcionarios_firman' : list(qsetFuncionariosFirman)
											, 'empresas' : list(qsetEmpresas)									
											 }})
		except Exception as e:
			print(e)
	

# exporta a excel correspondencia enviada
def exportReporteCorrespondenciaEnviada(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="Reporte_correspondenciaEnviada.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Proyectos')
	
	# FORMATO PARA ENCABEZADOS	
	format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
	# FORMATO PARA CAMPOS DE TIPOS TEXTO
	format2=workbook.add_format({'border':1})
	# FORMATO DE FECHA
	format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
	# FORMATO MONEDA
	format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})

	row=1
	col=0

	dato = request.GET['dato'] if 'dato' in request.GET else None;

	firma = request.GET['firma'] if 'firma' in request.GET else None;
	usuarioElaboro = request.GET['usuarioElaboro'] if 'usuarioElaboro' in request.GET else None;
	soporte_si = request.GET['soporte_si'] if 'soporte_si' in request.GET else 0;
	soporte_no = request.GET['soporte_no'] if 'soporte_no' in request.GET else 0;

	asunto = request.GET['asunto'] if 'asunto' in request.GET else 0;
	referencia = request.GET['referencia'] if 'referencia' in request.GET else 0;
	consecutivo = request.GET['consecutivo'] if 'consecutivo' in request.GET else 0;
	destinatario = request.GET['destinatario'] if 'destinatario' in request.GET else 0;

	fechaDesde = request.GET['fechaDesde'] if 'fechaDesde' in request.GET else None;
	fechaHasta = request.GET['fechaHasta'] if 'fechaHasta' in request.GET else None;

	empresaId = request.user.usuario.empresa.id

	model=CorrespondenciaEnviada

	if empresaId:
		qset = ( Q(empresa_id = empresaId) )
	else:
		qset = ( Q(empresa_id = empresaId) )


	if dato:
		qset = qset & ( Q(consecutivo__icontains = dato) )

	if firma:
		qset = qset & ( Q(firma_id = firma ) )

	if usuarioElaboro:
		qset = qset & ( Q(usuarioSolicitante_id = usuarioElaboro ) )

	if int(asunto)==1 and int(referencia)==0 and int(consecutivo)==0 and int(destinatario)==0:
		qset = qset & ( Q(asunto__icontains = dato ) )

	if int(referencia)==1 and int(asunto)==0 and int(consecutivo)==0 and int(destinatario)==0:
		qset = qset & ( Q(referencia__icontains = dato ) )

	if int(consecutivo)==1 and int(asunto)==0 and int(referencia)==0 and int(destinatario)==0:
		qset = qset & ( Q(consecutivo__icontains = dato ) )
	
	if int(destinatario)==1 and int(asunto)==0 and int(referencia)==0 and int(consecutivo)==0:
		qset = qset & ( Q(persona_destino__icontains = dato ) )

	#  CONBINACIONES DE DOS BUSQUEDA
	if int(asunto)==1 and int(referencia)==1 and int(consecutivo)==0 and int(destinatario)==0:
		qset = qset & ( Q(asunto__icontains = dato ) | Q(referencia__icontains = dato ) )
	if int(asunto)==1 and int(referencia)==0 and int(consecutivo)==1 and int(destinatario)==0:
		qset = qset & ( Q(asunto__icontains = dato ) | Q(consecutivo__icontains = dato ) )
	if int(asunto)==1 and int(referencia)==0 and int(consecutivo)==0 and int(destinatario)==1:
		qset = qset & ( Q(asunto__icontains = dato ) | Q(persona_destino__icontains = dato ) )
	
	if int(asunto)==0 and int(referencia)==1 and int(consecutivo)==1 and int(destinatario)==0:
		qset = qset & ( Q(referencia__icontains = dato ) | Q(consecutivo__icontains = dato ) )
	if int(asunto)==0 and int(referencia)==1 and int(consecutivo)==0 and int(destinatario)==1:
		qset = qset & ( Q(referencia__icontains = dato ) | Q(persona_destino__icontains = dato ) )

	if int(asunto)==0 and int(referencia)==0 and int(consecutivo)==1 and int(destinatario)==1:
		qset = qset & ( Q(consecutivo__icontains = dato ) | Q(persona_destino__icontains = dato ) )
	
	#  CONBINACIONES DE TRES BUSQUEDA	
	if int(asunto)==1 and int(referencia)==1 and int(consecutivo)==1 and int(destinatario)==0:
		qset = qset & ( Q(asunto__icontains = dato ) | Q(referencia__icontains = dato ) | Q(consecutivo__icontains = dato ) )
	if int(asunto)==1 and int(referencia)==1 and int(consecutivo)==0 and int(destinatario)==1:
		qset = qset & ( Q(asunto__icontains = dato ) | Q(referencia__icontains = dato ) | Q(persona_destino__icontains = dato ) )
	if int(asunto)==1 and int(referencia)==0 and int(consecutivo)==1 and int(destinatario)==1:
		qset = qset & ( Q(asunto__icontains = dato ) | Q(consecutivo__icontains = dato ) | Q(persona_destino__icontains = dato ) )
	if int(asunto)==0 and int(referencia)==1 and int(consecutivo)==1 and int(destinatario)==1:
		qset = qset & ( Q(referencia__icontains = dato ) | Q(consecutivo__icontains = dato ) | Q(persona_destino__icontains = dato ) )
	
	#  CONBINACIONES DE CUATRO BUSQUEDA
	if int(asunto)==1 and int(referencia)==1 and int(consecutivo)==1 and int(destinatario)==1:
		qset = qset & ( Q(asunto__icontains = dato ) | Q(referencia__icontains = dato ) | Q(consecutivo__icontains = dato ) | Q(persona_destino__icontains = dato ) )


	if (fechaDesde and (fechaHasta is not None) ):
		qset = qset & ( Q(fechaEnvio__gte= fechaDesde ) )
	
	if ( (fechaDesde is not None) and fechaHasta ):
		qset = qset & ( Q(fechaEnvio__lte=fechaHasta)  )

	if (fechaDesde and fechaHasta):	
		qset = qset & ( Q(fechaEnvio__range = (fechaDesde , fechaHasta) ) )

	if (int(soporte_si)>0 and int(soporte_no)==0):
		queryset = model.objects.filter(qset)
		querySoporte = CorrespondenciaSoporte.objects.filter(anulado = 0).values('correspondencia')# tipo uno correspondencia recibida
		queryset = queryset.filter(id__in = querySoporte)
	elif (int(soporte_si)==0 and int(soporte_no)>0):
		queryset = model.objects.filter(qset)	
		querySoporte = CorrespondenciaSoporte.objects.filter(anulado = 0).values('correspondencia')# tipo uno correspondencia recibida
		queryset = queryset.exclude(id__in = querySoporte)
	else:
		queryset = model.objects.filter(qset)

	
	formato_fecha = "%Y-%m-%d"
	
	# queryset = model.objects.all().order_by('-id')

	worksheet.set_column('A:K', 20)

	worksheet.write('A1', 'Consecutivo', format1)
	worksheet.write('B1', 'Fecha de Envio', format1)
	worksheet.write('C1', 'Asunto', format1)
	worksheet.write('D1', 'Referencia', format1)
	worksheet.write('E1', 'Destinatario', format1)
	worksheet.write('F1', 'Cargo', format1)
	worksheet.write('G1', 'Direccion', format1)
	worksheet.write('H1', 'Empresa Destino', format1)
	worksheet.write('I1', 'Ciudad', format1)
	worksheet.write('J1', 'Firma', format1)
	worksheet.write('K1', 'Estado', format1)

	worksheet.set_column('A:A', 10)
	worksheet.set_column('B:B', 10)
	worksheet.set_column('C:C', 50)
	worksheet.set_column('D:D', 50)
	worksheet.set_column('E:E', 40)
	worksheet.set_column('F:F', 18)
	worksheet.set_column('G:G', 18)
	worksheet.set_column('H:H', 30)
	worksheet.set_column('I:I', 18)
	worksheet.set_column('J:J', 40)
	worksheet.set_column('K:K', 18)

	for destinatarioCorrespondenciaEnviada in queryset:

		if destinatarioCorrespondenciaEnviada.anulado == 0:  
			estado = 'Establecida' 
		else: 
			estado = 'Anulada'

		firma = destinatarioCorrespondenciaEnviada.firma.persona.nombres+' '+destinatarioCorrespondenciaEnviada.firma.persona.apellidos
		cargo = destinatarioCorrespondenciaEnviada.cargo_persona
		direccion = destinatarioCorrespondenciaEnviada.direccion
		empresaDestino = destinatarioCorrespondenciaEnviada.empresa_destino
		ciudad = destinatarioCorrespondenciaEnviada.municipioEmpresa.nombre if destinatarioCorrespondenciaEnviada.municipioEmpresa else '';

		worksheet.write(row, col,destinatarioCorrespondenciaEnviada.consecutivo ,format2)
		worksheet.write(row, col+1,destinatarioCorrespondenciaEnviada.fechaEnvio ,format_date)
		worksheet.write(row, col+2,destinatarioCorrespondenciaEnviada.asunto ,format2)
		worksheet.write(row, col+3,destinatarioCorrespondenciaEnviada.referencia ,format2)
		worksheet.write(row, col+4,destinatarioCorrespondenciaEnviada.persona_destino ,format_money)
		worksheet.write(row, col+5, cargo ,format2)
		worksheet.write(row, col+6, direccion ,format2)
		worksheet.write(row, col+7, empresaDestino ,format2)
		worksheet.write(row, col+8, ciudad ,format2)
		worksheet.write(row, col+9, firma ,format2)
		worksheet.write(row, col+10, estado ,format2)
		
		row +=1
	workbook.close()
	return response


@login_required
def correspondencia_prefijo(request):
	return render(request, 'correspondencia/prefijos.html', {'model':'correspfijo','app':'correspondencia'} ,context_instance=RequestContext(request))

@login_required
def correspondencia_plantilla(request):
	return render(request, 'correspondencia/plantilla.html', {'model':'correspondenciaplantilla','app':'correspondencia'} ,context_instance=RequestContext(request))

@api_view(['DELETE'])
def eliminar_o_deshabilitar_prefijo(request, id):
	if request.method== "DELETE":		
		try:
			
			correspondencias=CorrespondenciaEnviada.objects.filter(prefijo__id=id).count()
			if correspondencias > 0:
				prefijo=CorresPfijo.objects.get(pk=id)
				prefijo.estado=False
				prefijo.save()
				return Response({'message':'El registro se ha deshabilitado correctamente','success':'ok',
				'data':''},status=status.HTTP_201_CREATED)
			else:
				prefijo=CorresPfijo.objects.get(pk=id)
				prefijo.delete()
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_201_CREATED)			
		
		except Exception as e:
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)

@login_required
def correspondencia_consecutivo(request):
	tipos=Tipo.objects.filter(app='correspondencia')	
	prefijos=CorresPfijo.objects.filter(empresa__id=request.user.usuario.empresa.id)
	return render(request, 'correspondencia/consecutivo.html', {'model':'correspondenciaconsecutivo','app':'correspondencia', 'tipos':tipos, 'prefijos':prefijos} ,context_instance=RequestContext(request))


@api_view(['GET'])
def usuariosCorrespondencia(request):
	if request.method == 'GET':
		try:

			dato = request.GET['dato'] if 'dato' in request.GET else None;
			empresaActual = request.GET['empresa'] if 'empresa' in request.GET else None; 

			# boolean para consultar tambien el usuario actual
			usuario_actual = request.GET['usuario_actual'] if 'usuario_actual' in request.GET else False; 

			qset = Q(user__is_active = True)

			if empresaActual is None or empresaActual=="":
				empresaActual = request.user.usuario.empresa.id
				empresas = EmpresaAcceso.objects.filter(empresa_id = empresaActual).values_list("empresa_ver_id")
				qset = qset & ( Q(empresa_id__in = empresas) | Q(empresa_id = empresaActual) )	

			else:
				qset = qset & (Q(empresa_id = empresaActual))
	

			if dato:
				qset = qset & (Q(persona__nombres__icontains=dato) | Q(persona__apellidos__icontains=dato))
				

			if usuario_actual:
				qsetUsuariosElaboran = Usuario.objects.filter(qset).order_by('persona__nombres')
			else:	
				usuarioActual = request.user.usuario.id
				qsetUsuariosElaboran = Usuario.objects.filter(qset).exclude(pk = usuarioActual).order_by('persona__nombres')
			
			usuariosElaboranData = UsuarioLiteSerializer(qsetUsuariosElaboran,many=True).data

			return JsonResponse({'message':'','success':'ok','data': usuariosElaboranData })
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			archivo = CorrespondenciaSoporte.objects.get(pk=request.GET['id'])
			
			filename = ""+str(archivo.soporte)+""
			extension = filename[filename.rfind('.'):]
			nombre = re.sub('[^A-Za-z0-9 ]+', '', archivo.nombre)
			return functions.exportarArchivoS3(str(archivo.soporte),  nombre + extension)

		except Exception as e:
			functions.toLog(e,'correspondencia.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def VerSoporteSolicitudSoporte(request):
	if request.method == 'GET':
		try:

			archivo = CorrespondenciaPlantilla.objects.get(pk=request.GET['id'])
			return functions.exportarArchivoS3(str(archivo.soporte))

		except Exception as e:
			functions.toLog(e,'correspondencia.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)