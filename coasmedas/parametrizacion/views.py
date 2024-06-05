from django.shortcuts import render,redirect,render_to_response
from django.urls import reverse
from .models import Departamento, Municipio, Banco, Cargo, Funcionario, Notificacion, EResponsabilidades, VideosTutoriales, GrupoVideosTutoriales
from rest_framework import viewsets, serializers
from django.db.models import Q
from empresa.views import EmpresaSerializer
from usuario.views import PersonaSerializer, UsuarioSerializer, PersonaLiteSerializer
from usuario.models import Persona , Usuario
from empresa.models import Empresa
from logs.models import Logs,Acciones
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
from django.db.models.deletion import ProtectedError
import parametrizacion
from django.contrib.auth.decorators import login_required
from django.db import transaction, connection
from rest_framework.decorators import api_view

from sinin4.functions import functions
from informe_ministerio.models import Planilla
from usuario.views import UsuarioSerializer
from logs.models import Logs
from datetime import date, datetime, timedelta
import datetime
from datetime import *
# Create your views here.

#Api rest para departamento
class DepartamentoSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Departamento
		fields=('id','nombre','iniciales')

class DepartamentoLiteSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Departamento
		fields=('id','nombre')

class DepartamentoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de departamentos, puede utilizar el parametro (dato) a traver del cual, se podra buscar por todo o parte del nombre, tambien puede ser buscado por sus iniciales.
	"""
	model=Departamento
	queryset = model.objects.all()
	nombre_modulo='parametrizacion.departamento'
	serializer_class = DepartamentoSerializer

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
			queryset = super(DepartamentoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			if dato:
				qset = (
					Q(nombre__icontains=dato)|
					Q(iniciales__icontains=dato)
					)
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
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				serializer = DepartamentoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save()
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = DepartamentoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
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
#Fin api rest para departamento


#Api rest para municipio
class MunicipioSerializer(serializers.HyperlinkedModelSerializer):

	departamento_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Departamento.objects.all())
	departamento=DepartamentoSerializer(read_only=True)
	class Meta:
		model = Municipio
		fields=('id','nombre','departamento','departamento_id')

class MunicipioLiteSerializer(serializers.HyperlinkedModelSerializer):

	departamento=DepartamentoLiteSerializer(read_only=True)
	class Meta:
		model = Municipio
		fields=('id','nombre','departamento')

class MunicipioViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de Municipios, puede utilizar el parametro (dato) a traver del cual, se podra buscar por todo o parte del nombre, tambien puede buscar los municipios que hacen parte de determinado departamento.
	"""
	model=Municipio
	queryset = model.objects.all()
	serializer_class = MunicipioSerializer
	nombre_modulo='parametrizacion.municipio'

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
			queryset = super(MunicipioViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			id_departamento= self.request.query_params.get('id_departamento', None)
			
			if dato or id_departamento:
				if dato:
					qset = (
						Q(nombre__icontains=dato)|
						Q(nit__icontains=dato)
						)
				if id_departamento:
					if dato:
						qset=qset&(Q(departamento_id=id_departamento))
					else:
						qset=(Q(departamento_id=id_departamento))
						

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
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				serializer = MunicipioSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(departamento_id=request.DATA['departamento_id'])
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = MunicipioSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
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
#Fin api rest para municipio


#Api rest para Banco
class BancoSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Banco
		fields=('id','nombre','codigo_bancario')

class BancoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de Bancos, puede utilizar el parametro (dato) a traver del cual, se podra buscar por todo o parte del nombre, tambien puede buscar por medio del codigo bancario.
	"""
	model=Banco
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='parametrizacion.banco'
	queryset = model.objects.all()
	serializer_class = BancoSerializer

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
			queryset = super(BancoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			if dato:
				qset = (
					Q(nombre__icontains=dato)|
					Q(codigo_bancario__icontains=dato)
					)
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
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				request.DATA['codigo_bancario']=request.DATA['codigo_bancario'] if request.DATA['codigo_bancario'] !='' and request.DATA['codigo_bancario'] !=None else 0 
				serializer = BancoSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save()
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				request.DATA['codigo_bancario']=request.DATA['codigo_bancario'] if request.DATA['codigo_bancario'] !='' and request.DATA['codigo_bancario'] !=None else 0 
				serializer = BancoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
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
#Fin Api rest para banco


#Api rest para Cargo
class CargoSerializer(serializers.HyperlinkedModelSerializer):
	empresa = EmpresaSerializer(read_only=True)

	class Meta:
		model = parametrizacion.models.Cargo
		fields=('id','nombre','empresa','firma_cartas')

class CargoLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = parametrizacion.models.Cargo
		fields=('id','nombre')

class CargoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de Cargos, puede utilizar el parametro (dato) a traver del cual, se podra buscar por todo o parte del nombre, tambien puede buscar por medio de la empresa de cual pertenece dicho cargo.
	"""
	model=parametrizacion.models.Cargo
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='parametrizacion.cargo'
	queryset = model.objects.all()
	serializer_class = CargoSerializer

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
			paginacion = self.request.query_params.get('sin_paginacion', None)

			
			queryset = super(CargoViewSet, self).get_queryset()
			#con busqueda en un solo campo: recuperado
			# valorEsContratista = self.request.query_params.get('nombre', None)
			# if valorEsContratista:
			# 	queryset = queryset.filter(nombre__icontains=valorEsContratista)
			dato = self.request.query_params.get('dato', None)
			empresa_filtro=self.request.query_params.get('empresa_filtro', None)
			lite = self.request.query_params.get('lite', None)

			if empresa_filtro:
				empresa_id = empresa_filtro
				qset=(Q(empresa_id=empresa_id))
			else:
				empresa_id = self.request.query_params.get('empresa_id', request.user.usuario.empresa.id)
				qset=(Q(empresa=empresa_id))

			if dato:
				qset = qset & (Q(nombre__icontains=dato))
				
			queryset = self.model.objects.filter(qset)
			
			if paginacion==None:

				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = CargoLiteSerializer(page,many=True)
					else:
						serializer = self.get_serializer(page,many=True)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
		
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok',
					'data':serializer.data})

			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok',
					'data':serializer.data})

		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				serializer = CargoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(empresa_id=request.user.usuario.empresa.id)
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = CargoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(empresa_id=request.user.usuario.empresa.id)
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
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
#Fin Api rest para Cargo


#Api rest para Responsabilidades
class ResponsabilidadesSerializer(serializers.HyperlinkedModelSerializer):

	empresa = EmpresaSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.filter(esContratante=1))

	class Meta:
		model = EResponsabilidades
		fields=('id','nombre','empresa','empresa_id','descripcion')

class ResponsabilidadesViewSet(viewsets.ModelViewSet):
	"""
	
	"""
	model=EResponsabilidades
	queryset = model.objects.all()
	serializer_class = ResponsabilidadesSerializer
	nombre_modulo='parametrizacion.responsabilidades'

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
			queryset = super(ResponsabilidadesViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			nombre = self.request.query_params.get('nombre', None)
			id_empresa = self.request.query_params.get('id_empresa', None)
			empresa_id = self.request.query_params.get('empresa_usu', None)
			descripcion = self.request.query_params.get('descripcion', None)
			con_funcionario = self.request.query_params.get('con_funcionario',None)
			listadoasociado = self.request.query_params.get('listado').split(',') if self.request.query_params.get('listado') else None
			sin_paginacion = self.request.query_params.get('sin_paginacion',None)

			if con_funcionario is not None:
				funcionario_model = Funcionario.objects.get(persona_id = request.user.usuario.persona.id)

			if empresa_id:
				id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))
			if dato:
				qset = qset &(Q(nombre__icontains=dato)|Q(descripcion__icontains=dato)|Q(empresa__nombre__icontains=dato))

			if nombre:
				qset = qset &(Q(nombre__icontains=nombre))

			if id_empresa:
				qset = qset &(Q(empresa=id_empresa))

			if descripcion:
				qset = qset &(Q(descripcion__icontains=descripcion))

			if listadoasociado:
				queryset = self.model.objects.filter(qset).exclude(pk__in = listadoasociado)
			elif qset is not None:
				queryset = self.model.objects.filter(qset)

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})
		
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ResponsabilidadesSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(empresa_id=request.DATA['empresa_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='parametrizacion.responsabilidades',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ResponsabilidadesSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(empresa_id=request.DATA['empresa_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='parametrizacion.responsabilidades',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# print instance.id
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='parametrizacion.responsabilidades',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			# print(e)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para Responsabilidades

#Api rest para Funcionario
#class FuncionarioSerializer(serializers.HyperlinkedModelSerializer):
#	empresa = EmpresaSerializer()
#	#persona = serializers.SlugRelatedField(queryset=Persona.objects.all(),slug_field='nombres')
#	#persona=PersonaSerializer(lookup_field='nombres')
#	persona = PersonaSerializer(read_only=True)
#	#persona = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Persona.objects.all(), source='nombres')
#	id_cargo = CargoSerializer()
#	class Meta:
#		model = Funcionario
#		fields=('id','empresa','persona','id_cargo','iniciales')

class FuncionarioSerializer(serializers.HyperlinkedModelSerializer):
	
	persona = PersonaSerializer(read_only=True)
	cargo = CargoSerializer(read_only=True)
	persona_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Persona.objects.all())
	cargo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Cargo.objects.all())
	notificaciones = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Notificacion.objects.all())
	responsabilidades = ResponsabilidadesSerializer(read_only = True, many = True)
	
	class Meta:
		model = Funcionario
		fields=('id','persona','persona_id','cargo','cargo_id','iniciales','notificaciones','responsabilidades', 'activo')

class FuncionarioLiteSerializer(serializers.HyperlinkedModelSerializer):
    	
	persona = PersonaLiteSerializer(read_only=True)
	
	class Meta:
		model = Funcionario
		fields=('id','persona')

class FuncionarioViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de Funcionarios, puede utilizar el parametro (dato) a traver del cual, se podra buscar por todo o parte del nombre, tambien puede buscar por los siguientes parametros:
	<br><b>(Empresa)</b>: a cual pertenece el funcionario.
	<br><b>(Por persona)</b>
	<br><b>(Cargo)</b>: que tiene el funcionario.
	<br><b>(Iniciales)</b>: del funcionario.
	"""
	model=Funcionario
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='parametrizacion.funcionario'
	queryset = model.objects.all()
	serializer_class = FuncionarioSerializer

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
			queryset = super(FuncionarioViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			funcionario = self.request.query_params.get('funcionario', None)
			cargo = self.request.query_params.get('cargo', None)

			empresa_filtro=self.request.query_params.get('empresa_filtro', None)
			lite = self.request.query_params.get('lite', None)

			# qset=(Q(activo=True))
			qset=(~Q(id=0))
			qset=qset & (Q(activo=True))
			
			if empresa_filtro:
				empresa_id = empresa_filtro
				qset=qset &(Q(empresa_id=empresa_id))
			else:
				empresa_id = self.request.query_params.get('empresa_id', request.user.usuario.empresa.id)
				qset=qset &(Q(empresa=empresa_id))

			if dato:
				qset = qset &(
					Q(persona__nombres__icontains=dato)|
					Q(persona__apellidos__icontains=dato)|
					Q(cargo__nombre__icontains=dato)|
					Q(iniciales__icontains=dato)
					)

			if cargo:
				qset = qset &(Q(cargo__id = cargo))

			queryset = self.model.objects.filter(qset)

			
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = FuncionarioLiteSerializer(page,many=True)
					else:
						serializer = self.get_serializer(page,many=True)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
			if lite:
				serializer = FuncionarioLiteSerializer(queryset,many=True)
			else:
				serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
					'data':serializer.data})

		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	def create(self, request, *args, **kwargs):

		if request.method == 'POST':
			try:
				if request.DATA['persona_id'] == 0:
					serializer_persona = PersonaSerializer(data=request.DATA['persona'],context={'request': request})
					
					if serializer_persona.is_valid():
						valor=serializer_persona.save()
						logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo='usuario.persona',id_manipulado=valor.id)
						logs_model.save()
						request.DATA['persona_id']=valor.id

					else:
						return Response({'message':'datos requeridos no fueron recibidos de persona','success':'fail',
							'data':''},status=status.HTTP_400_BAD_REQUEST)


				serializer = FuncionarioSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					
					serializer.save(empresa_id=request.user.usuario.empresa.id,persona_id=request.DATA['persona_id'],
						cargo_id=request.DATA['cargo_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()
							
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
								'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
						 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				# #print request.DATA

				if request.DATA['persona_id'] == 0:

					serializer_persona = PersonaSerializer(data=request.DATA['persona'],context={'request': request})
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo='usuario.persona',id_manipulado=valor.id)
					logs_model.save()
					
					if serializer_persona.is_valid():
						valor=serializer_persona.save()
						request.DATA['persona_id']=valor.id

					else:
						# print(serializer.errors)
						return Response({'message':'datos requeridos no fueron recibidos de persona','success':'fail',
							'data':''},status=status.HTTP_400_BAD_REQUEST)

				serializer = FuncionarioSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(empresa_id=request.user.usuario.empresa.id,
								persona_id=request.DATA['persona_id'],cargo_id=request.DATA['cargo_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()
					
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
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


# consulta funcionarios por empresa o dato pero excluye el usuario actual
def usuariosConFuncionarios(request):
	if request.method == 'GET':
		try:
			empresa = request.GET['empresa'] if 'empresa' in request.GET else None;
			dato = request.GET['dato'] if 'dato' in request.GET else None;
			usuarioActual = request.user.usuario.id

			if empresa:
				qset = Q(empresa_id = empresa)
				if dato :
					qset = qset & (Q(persona__nombres__icontains=dato) | Q(persona__apellidos__icontains=dato))
				queryset = Usuario.objects.filter(qset).values( 'id' , 'user__username' , 'persona__nombres' , 'persona__apellidos' ).exclude(pk = usuarioActual)
			else:
				if dato:
					qset = (Q(persona__nombres__icontains=dato) | Q(persona__apellidos__icontains=dato))
					queryset = Usuario.objects.filter(qset).values( 'id' , 'user__username' , 'persona__nombres' , 'persona__apellidos' ).exclude(pk = usuarioActual)
				else:
					queryset = Usuario.objects.all().values( 'id' , 'user__username' , 'persona__nombres' , 'persona__apellidos' ).exclude(pk = usuarioActual)
	
			return JsonResponse({'message':'','success':'ok','data':list(queryset)})
		except Exception as e:
			functions.toLog(e,'parametrizacion.funcionario')
		else:
			pass
		finally:
			pass

# consulta funcionarios de la empresa actual 
def usuariosConFuncionariosEmpresa(request):
	if request.method == 'GET':
		try:

			dato = request.GET['dato'] if 'dato' in request.GET else None;
			empresaActual = request.user.usuario.empresa.id
			qset = Q(empresa_id = empresaActual)
				
			if dato:
				qset = qset & (Q(persona__nombres__icontains=dato) | Q(persona__apellidos__icontains=dato))
				queryset = Usuario.objects.filter(qset).values( 'id' , 'user__username' , 'persona__nombres' , 'persona__apellidos' )	
			else:
				queryset = Usuario.objects.filter(qset).values( 'id' , 'user__username' , 'persona__nombres' , 'persona__apellidos' )

			return JsonResponse({'message':'','success':'ok','data':list(queryset)})
		except Exception as e:
			functions.toLog(e,'parametrizacion.funcionario')
		else:
			pass
		finally:
			pass
#Fin Api rest para Funcionario


#api notificacion
class NotificacionSerializer(serializers.HyperlinkedModelSerializer):	
	class Meta:
		model = Notificacion
		fields=('id', 'nombre', 'descripcion')
		validators=[serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=('nombre','app'),
				message=('La notificacion ya existe para la aplicacion ingresada'))]

class NotificacionViewSet(viewsets.ModelViewSet):
	model=Notificacion
	queryset = model.objects.all()
	serializer_class = NotificacionSerializer
	nombre_modulo='parametrizacion.notificacion'
	paginate_by = 10

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
			queryset = super(NotificacionViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)			
			qset=None
			if dato:
				qset=(Q(nombre__icontains=dato) | 
					Q(descripcion__icontains=dato))							
						
			if qset:
				queryset = self.model.objects.filter(qset)	
			
			mensaje=''
			if queryset.count()==0:
				mensaje='No se encontraron notificacion con los criterios de busqueda ingresados'
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
				serializer = NotificacionSerializer(data=request.DATA,context={'request': request})
				mensaje=''
				if serializer.is_valid():
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='parametrizacion.notificacion',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
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
				serializer = NotificacionSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='parametrizacion.notificacion',id_manipulado=instance.id)
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
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='parametrizacion.notificacion',id_manipulado=instance.id)
				logs_model.save()
				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#fin api notificacion


def export_excel_cargo(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="cargos.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Cargos')
	format1=workbook.add_format({'border':1,'font_size':15,'bold':True})
	format2=workbook.add_format({'border':1})

	row=1
	col=0

	dato= request.GET['dato']

	qset=(Q(empresa=request.user.usuario.empresa.id))				

	if (len(dato)>0):

		qset = qset = qset &(Q(nombre__icontains=dato))

	cargos = 	Cargo.objects.filter(qset)

	worksheet.write('A1', 'Nombre', format1)
	worksheet.write('B1', 'Firma', format1)

	for cargo in cargos:
		worksheet.write(row, col,cargo.nombre,format2)
		if cargo.firma_cartas==True:
			worksheet.write(row, col+1,'Tiene Firma',format2)

		if cargo.firma_cartas==False:
			worksheet.write(row, col+1,'No Tiene Firma',format2) 

		row +=1


	workbook.close()

	return response

def export_excel_banco(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="bancos.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Bancos')
	format1=workbook.add_format({'border':1,'font_size':15,'bold':True})
	format2=workbook.add_format({'border':1})

	row=1
	col=0

	dato= request.GET['dato']

	if (len(dato)>0):

		qset = (
				Q(nombre__icontains=dato)|
				Q(codigo_bancario__icontains=dato)
				)
				
		bancos = 	Banco.objects.filter(qset)
	else:
		bancos = 	Banco.objects.all()

	worksheet.write('A1', 'Nombre', format1)
	worksheet.write('B1', 'Codigo Bancario', format1)

	for banco in bancos:
		worksheet.write(row, col,banco.nombre,format2)
		worksheet.write(row, col+1,banco.codigo_bancario,format2)

		row +=1


	workbook.close()

	return response

def export_excel_funcionario(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="funcionario.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Funcionario')
	format1=workbook.add_format({'border':1,'font_size':15,'bold':True})
	format2=workbook.add_format({'border':1})

	row=1
	col=0

	dato= request.GET['dato']

	qset=(Q(empresa_id=request.user.usuario.empresa.id))

	if (len(dato)>0):

		qset = qset &(
			Q(persona__nombres__icontains=dato)|
			Q(persona__apellidos__icontains=dato)|
			Q(cargo__nombre__icontains=dato)|
			Q(iniciales__icontains=dato)
			)
				
	funcionarios = 	Funcionario.objects.filter(qset)

	worksheet.write('A1', 'Nombre Persona', format1)
	worksheet.write('B1', 'Cargo', format1)
	worksheet.write('C1', 'Iniciales', format1)

	for funcionario in funcionarios:
		worksheet.write(row, col,funcionario.persona.nombres+" "+funcionario.persona.apellidos,format2)
		worksheet.write(row, col+1,funcionario.cargo.nombre,format2)
		worksheet.write(row, col+2,funcionario.iniciales,format2)

		row +=1


	workbook.close()

	return response

def eliminar_varios_id_banco(request):

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		#print respuesta['lista'].split()

		#lista=respuesta['lista'].split(',')
		
		for item in respuesta['lista']:
			Banco.objects.filter(id=item['id']).delete()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='parametrizacion.banco',id_manipulado=item['id'])
			logs_model.save()
		
		

		#return HttpResponse(str('0'), content_type="text/plain")
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except Exception as e:
		functions.toLog(e,'parametrizacion.banco')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})

def eliminar_varios_id_funcionario(request):

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		#print respuesta['lista'].split()

		#lista=respuesta['lista'].split(',')
		
		for item in respuesta['lista']:
			funcionario=Funcionario.objects.get(id=item['id'])
			funcionario.activo=False
			funcionario.save()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='parametrizacion.funcionario',id_manipulado=item['id'])
			logs_model.save()

		#return HttpResponse(str('0'), content_type="text/plain")
		return JsonResponse({'message':'El registro se ha desactivado correctamente','success':'ok',
				'data':''})
		
	except Exception as e:
		functions.toLog(e,'parametrizacion.funcionario')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})

def eliminar_varios_id_cargo(request):

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		#print respuesta['lista'].split()

		#lista=respuesta['lista'].split(',')
		
		for item in respuesta['lista']:
			Cargo.objects.filter(id=item['id'],empresa_id=request.user.usuario.empresa.id).delete()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='parametrizacion.cargo',id_manipulado=item['id'])
			logs_model.save()

		#return HttpResponse(str('0'), content_type="text/plain")
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error',
			'data':''})	
	except Exception as e:
		functions.toLog(e,'parametrizacion.cargo')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})			 

def eliminar_responsabilidades(request):
	if request.method == 'POST':
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']

			for item in myList:
				# # print item
				model = EResponsabilidades.objects.get(pk=item['id'])
				model.delete()
			# Proyecto.objects.filter(id = item ).delete()

			# transaction.commit()
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			functions.toLog(e,'parametrizacion.responsabilidades')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Guardar responsabilidades del funcionario
@transaction.atomic
def createResponsabilidadesFuncionarioConLista(request):
	# if request.method == 'POST':
	sid = transaction.savepoint()
	try:
		funcionario_id = request.GET['funcionario_id']
		responsabilidades_id = request.GET['responsabilidades_id']

		myList = str(responsabilidades_id).split(',')

		model_funcionario = Funcionario.objects.get(pk=funcionario_id)
		model_funcionario.responsabilidades.add(*myList)

		func_resp = model_funcionario.responsabilidades.through.objects.filter(eresponsabilidades_id__in = myList)

		insert_list = []
		for i in func_resp:
			insert_list.append(Logs(usuario_id=request.user.usuario.id
															,accion=Acciones.accion_crear
															,nombre_modelo='parametrizacion.asignarResponsabilidades'
															,id_manipulado=i.id))
		Logs.objects.bulk_create(insert_list)
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
	except Exception as e:
		functions.toLog(e,'parametrizacion.responsabilidades')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Eliminar responsabilidades del funcionario
@transaction.atomic
def destroyResponsabilidadesFuncionarioConLista(request):
	if request.method == 'POST':
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']

			model_funcionario = Funcionario.objects.get(pk=respuesta['id_funcionario'])

			func_resp = model_funcionario.responsabilidades.through.objects.filter(eresponsabilidades_id__in = myList)
			insert_list = []
			for i in func_resp:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
																,accion=Acciones.accion_borrar
																,nombre_modelo='parametrizacion.asignarResponsabilidades'
																,id_manipulado=i.id))
			Logs.objects.bulk_create(insert_list)

			model_funcionario.responsabilidades.remove(*myList)

			# transaction.commit()
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			functions.toLog(e,'parametrizacion.responsabilidades')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# lista las REsponsabilidades por funcionario y la empressa de la sesion activa
def listMisResponsabilidades(request):
	try:
		dato = request.GET['dato']

		# funcionario_model = Funcionario.objects.get(persona = request.user.usuario.persona.id, empresa=request.user.usuario.empresa.id)

		# listaresp=[]
		# for responsabilidad in funcionario_model.responsabilidades.all():
		# 	listaresp.append({'nombre':responsabilidad.nombre,'descripcion':responsabilidad.descripcion})
		
		# return JsonResponse({'message':'','success':'ok','data':listaresp})
		qset = (
			(Q(nombre__icontains=dato)|
			Q(descripcion__icontains=dato))#&
			# Q(id=id_contrato)
			)
		funcionario_model = Funcionario.objects.get(persona = request.user.usuario.persona.id, empresa=request.user.usuario.empresa.id)

		queryset = funcionario_model.responsabilidades.filter(qset).values('id', 'nombre', 'descripcion')

		return JsonResponse({'message':'','success':'ok','data':list(queryset)})
	except Exception as e:
		functions.toLog(e,'parametrizacion.responsabilidades')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})


@login_required
def parametrizacion(request):
	return render(request, 'parametrizacion/parametrizacion.html')

@login_required
def manual_usuario(request):	
	try:
		planilla =  Planilla.objects.get(id=3)			
		return functions.exportarArchivoS3(str(planilla.archivo))

	except Exception as e:
		functions.toLog(e,'parametrizacion.manual_usuario')
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			


@login_required
def banco(request):
	return render(request, 'parametrizacion/banco.html',{'model':'banco','app':'parametrizacion'})

@login_required
def funcionario(request):
	queryset_cargo=Cargo.objects.filter(empresa_id=request.user.usuario.empresa.id)
	return render(request, 'parametrizacion/funcionario.html',{'cargos':queryset_cargo, 'model':'funcionario','app':'parametrizacion'})

@login_required
def inicioResponsabilidades(request):
	return render(request, 'responsabilidades/inicioResponsabilidades.html',{'model':'eresponsabilidades','app':'parametrizacion'})

@login_required
def transacciones(request):
	empresas = Empresa.objects.all()
	return render(request, 'parametrizacion/transacciones.html',{'empresas':empresas, 'model':'parametrizacion','app':'parametrizacion'})
	
@login_required
def responsabilidades(request):
	id_empresa = request.user.usuario.empresa.id
	empresas = Empresa.objects.filter(id=id_empresa)
	return render(request, 'responsabilidades/responsabilidades.html',{'empresas':empresas, 'model':'eresponsabilidades','app':'parametrizacion'})

@login_required
def asignarResponsabilidades(request):
	id_empresa = request.user.usuario.empresa.id
	# empresas = Empresa.objects.filter(esContratante=1)
	return render(request, 'responsabilidades/asignarResponsabilidades.html',{'id_empresa':id_empresa, 'model':'eresponsabilidades','app':'parametrizacion'})

@login_required
def misResponsabilidades(request):
	return render(request, 'responsabilidades/misResponsabilidades.html',{'model':'eresponsabilidades','app':'parametrizacion'})


#funcion para traer los departamentos segun mcontrato y contratista
def select_departamento(request):

	cursor = connection.cursor()
	try:
		id_macontrato = request.GET['id_macontrato']
		id_contratista = request.GET['id_contratista']
		cursor.callproc('[dbo].[select_departamento]', [id_macontrato,id_contratista])
		#if cursor.return_value == 1:   
		result_set = cursor.fetchall()
		# print result_set
		lista=[]
		for x in list(result_set):
			item={
				'id_departamento':x[0],
				'nombre_departamento':x[1],
			}
			lista.append(item)
		return JsonResponse({'message':'','success':'ok','data':lista}) 
	except Exception as e:
		functions.toLog(e,'parametrizacion.departamentos')
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
	finally:
		cursor.close()


@api_view(['GET'])
def obtener_notificaciones_por_persona(request):
	cursor = connection.cursor()
	if request.method == 'GET':
		try:

			persona_id = request.GET['persona_id']			
			usuario = Usuario.objects.filter(persona__id=persona_id, empresa__id=request.user.usuario.empresa.id).first()
			# print usuario
			if usuario:				
				cursor.callproc('[dbo].[parametrizacion_obtener_notificaciones_autogestionables]', [usuario.id, usuario.empresa.id,])
				columns = cursor.description 
				notificaciones = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
				
				if notificaciones:
					return Response({'message':'','success':'ok','data':notificaciones})	
				else:
					return Response({'message':'No se encuentran notificaciones asociadas.','success':'fail','data':None})	
			else:
				return Response({'message':'El funcionario no tiene un usuario asignado','success':'fail','data':[]})	
					
		except Exception as e:
			functions.toLog(e,'parametrizacion.notificaciones')
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

@login_required
def grupo_videos_tutoriales(request):
	grupovideostutoriales = GrupoVideosTutoriales.objects.order_by('orden')
	return render(request, 'parametrizacion/grupo_videos_tutoriales.html',{'model':'grupo_videos_tutoriales','app':'parametrizacion', 'grupovideostutoriales':grupovideostutoriales})

@login_required
def videos_tutoriales(request, grupo_id):
	videostutoriales = VideosTutoriales.objects.filter(grupo__id=grupo_id).order_by('orden')
	return render(request, 'parametrizacion/videos_tutoriales.html',{'model':'videos_tutoriales','app':'parametrizacion', 'videostutoriales':videostutoriales})

@login_required
def video(request):
	url = str(request.GET['url']).decode('base64')
	poster = str(request.GET['poster']).decode('base64')
	return render(request, 'parametrizacion/video.html',{'model':'videos_tutoriales','app':'parametrizacion', 'url_video':url, 'poster':poster})


class LogsSerializer(serializers.HyperlinkedModelSerializer):
	usuario_persona = serializers.SerializerMethodField()
	usuario_empresa = serializers.SerializerMethodField()
	fecha =  serializers.SerializerMethodField()
	hora =  serializers.SerializerMethodField()
	class Meta:
		model = Logs
		fields=('id','usuario_persona','usuario_empresa','fecha','hora','accion','nombre_modelo','id_manipulado')

	def get_usuario_persona(self, obj):
		return obj.usuario.persona.nombres+' '+obj.usuario.persona.apellidos
	def get_usuario_empresa(self, obj):
		return obj.usuario.empresa.nombre

	def get_fecha(self, obj):
		var_fecha = str(obj.fecha_hora)
		#fecha = datetime.strptime(str(obj_fecha),'%Y-%m-%d').date()
		fecha = datetime.strptime(str(var_fecha[:10]),'%Y-%m-%d').date()
		return fecha.strftime('%Y-%m-%d')

	def get_hora(self, obj):
		var_hora = str(obj.fecha_hora)
		#hora = datetime.strptime(str(var_hora[11:19]),'%I:%M:%S').date()
		return str(var_hora[11:19])

class TransaccionesViewSet(viewsets.ModelViewSet):	
	model=Logs
	queryset = model.objects.all()
	serializer_class = LogsSerializer
	nombre_modulo = 'Logs - Logs'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance, context={'request': request})
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(TransaccionesViewSet, self).get_queryset()
			empresa_id = self.request.query_params.get('empresa_id', None)
			usuario_id = self.request.query_params.get('usuario_id', None)
			fecha_inicio = self.request.query_params.get('fecha_inicio', None)
			fecha_fin = self.request.query_params.get('fecha_fin', None)
			sin_paginacion  = self.request.query_params.get('sin_paginacion', None)
			page = self.request.query_params.get('page', None)
			#import pdb; pdb.set_trace()

			qset = (~Q(id=0))
			if empresa_id or usuario_id or fecha_inicio or fecha_fin:
				if empresa_id:
					qset = qset &(
						Q(usuario__empresa__id=empresa_id)
						)
				if usuario_id:
					qset = qset &(
						Q(usuario__id=usuario_id)
						)
				if fecha_inicio:
					qset = qset &(
						Q(fecha_hora__gte=fecha_inicio)
						)
				if fecha_fin:
					qset = qset &(
						Q(fecha_hora__lte=fecha_fin)
						)
			queryset = self.model.objects.filter(qset).order_by('-id')
			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def exportTransacciones(request):
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="Reporte_transacciones.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Transacciones')
		format1=workbook.add_format({'border':0,'font_size':12,'bold':True})		
		format2=workbook.add_format({'border':0})
		format1.set_align('center')
		format2.set_align('center')
		format2.set_align('vcenter')
		format3=workbook.add_format({'border':0,'font_size':12})
		format4=workbook.add_format({'border':0,'font_size':12})
		format4.set_align('center')
		# format3.set_align('vcenter')

		format5=workbook.add_format()
		format5.set_num_format('yyyy-mm-dd')
		format5.set_align('center')
		worksheet.set_column('A:A', 35)
		worksheet.set_column('B:B', 35)
		worksheet.set_column('C:E', 15)
		worksheet.set_column('F:F', 50)
		worksheet.set_column('G:G', 15)
		row=1
		col=0

		empresa_id = request.GET['empresa_id'] if request.GET['empresa_id'] else None
		usuario_id = request.GET['usuario_id'] if request.GET['usuario_id'] else None
		fecha_inicio = request.GET['fecha_inicio'] if request.GET['fecha_inicio'] else None
		fecha_fin = request.GET['fecha_fin'] if request.GET['fecha_fin'] else None




		qset = (~Q(id=0))
		if empresa_id or usuario_id or fecha_inicio or fecha_fin:
			if empresa_id:
				qset = qset &(
					Q(usuario__empresa__id=empresa_id)
					)
			if usuario_id:
				qset = qset &(
					Q(usuario__id=usuario_id)
					)
			if fecha_inicio:
				qset = qset &(
					Q(fecha_hora__gte=fecha_inicio)
					)
			if fecha_fin:
				qset = qset &(
					Q(fecha_hora__lte=fecha_fin)
					)
		queryset = Logs.objects.filter(qset).order_by('-id')

		serializer_context = {
			'request': request
		}

		serializer = LogsSerializer(queryset,many=True,context=serializer_context)

		if serializer:
			worksheet.write('A1', 'Usuario', format1)
			worksheet.write('B1', 'Empresa', format1)
			worksheet.write('C1', 'Fecha', format1)
			worksheet.write('D1', 'Hora', format1)
			worksheet.write('E1', 'Accion', format1)
			worksheet.write('F1', 'Modulo', format1)
			worksheet.write('G1', 'ID manipulado', format1)

			for item in serializer.data:
				#import pdb; pdb.set_trace()
				worksheet.write(row, col,item['usuario_persona'],format3)
				worksheet.write(row, col+1,item['usuario_empresa'],format3)
				worksheet.write(row, col+2,item['fecha'],format5)
				worksheet.write(row, col+3,item['hora'],format4)				
				worksheet.write(row, col+4,item['accion'],format2)
				worksheet.write(row, col+5,item['nombre_modelo'],format3)
				worksheet.write(row, col+6,item['id_manipulado'],format4)

				row +=1

		workbook.close()
		return response
	except Exception as e:
		#print(e)
		functions.toLog(e,'avanceObraGrafico2')
		return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)  