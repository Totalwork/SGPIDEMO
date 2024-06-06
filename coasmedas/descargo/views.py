from django.shortcuts import render,redirect,render_to_response
from django.urls import reverse

from rest_framework import viewsets, serializers
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
from django.contrib.auth.decorators import login_required
from empresa.views import EmpresaSerializer
from contrato.views import ContratoSerializer
from proyecto.views import ProyectoSerializer
from parametrizacion.views import DepartamentoSerializer,MunicipioSerializer
from estado.views import EstadoSerializer
from seguridad_social.views import EmpleadoSerializer
from tipo.views import TipoSerializer
from usuario.views import PersonaSerializer

from .models import Correo_descargo,AIdInternoDescargo,ATrabajo,AManiobra,ABMotivoSgi,AMotivoInterventor,Descargo,FotoDescargo

from empresa.models import Empresa
from contrato.models import Contrato,EmpresaContrato
from proyecto.models import Proyecto,Proyecto_empresas
from parametrizacion.models import Departamento,Municipio
from estado.models import Estado
from seguridad_social.models import Empleado
from tipo.models import Tipo

from django.db import transaction
from logs.models import Logs,Acciones
from coasmedas.functions import functions

from .enumeration import estadoD, tipoD

from .forms import DescargoForm,DescargoCorreoForm

from contrato.enumeration import tipoC

from datetime import datetime, timedelta

import xlsxwriter

# Create your views here.

#Serializadores versiones Lite
class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):
	esContratista = serializers.BooleanField(default=False)
	#logo = serializers.ImageField(required=False)

	class Meta:
		model = Empresa
		fields=('url','id','nombre','esContratista')

class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):


	contratista = EmpresaLiteSerializer(read_only=True)

	class Meta:
		model = Contrato
		fields=( 'id','nombre',
				 'numero' , 
				 'contratista')			

class EmpleadoLiteSerializer(serializers.HyperlinkedModelSerializer):

	empresa = EmpresaLiteSerializer(read_only=True)
	persona = PersonaSerializer(read_only=True)
	estado = EstadoSerializer(read_only=True)
	contratista = EmpresaLiteSerializer(read_only=True)

	class Meta:	
		order_by = True	
		model = Empleado		
		fields=('id','persona','contratista',
			'empresa','estado')

class ProyectoEmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):

	empresa = EmpresaLiteSerializer(read_only = True  )

	class Meta:
		model = Proyecto_empresas
		fields=('id','empresa')

class ProyectoLiteSerializer(serializers.HyperlinkedModelSerializer):


	mcontrato = ContratoLiteSerializer(read_only = True)

	municipio = MunicipioSerializer(read_only = True)

	contrato = ContratoLiteSerializer(read_only = True, many = True)

	class Meta:
		model = Proyecto
		fields=( 'id','nombre',
				 'mcontrato' , 
				 'municipio'  ,'contrato')
#Fin Serializadores Lite


#Api rest para correo de descargo
class CorreoDescargoSerializer(serializers.HyperlinkedModelSerializer):


	contratista = EmpresaLiteSerializer(read_only=True)
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.filter(esContratista=True))

	tipo = TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='descargo'))

	class Meta:
		model = Correo_descargo
		fields=('id' , 'nombre' , 'apellido','correo','contratista','contratista_id','tipo','tipo_id')

class CorreoDescargoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model=Correo_descargo
	queryset = model.objects.all()
	serializer_class = CorreoDescargoSerializer
	nombre_modulo = 'Descargo - CorreoDescargoViewSet'

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
			queryset = super(CorreoDescargoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			
			if (dato):
				if dato:
					qset = (
						Q(nombre__icontains=dato)|
						Q(apellido__icontains=dato)|
						Q(correo__icontains=dato)
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
				serializer = CorreoDescargoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(tipo_id=request.DATA['tipo_id'],contratista_id=request.DATA['contratista_id'])
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
				serializer = CorreoDescargoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(tipo_id=request.DATA['tipo_id'],contratista_id=request.DATA['contratista_id'])
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
#Fin api rest para correo de descargo


#Api rest para  id interno
class AIdInternoDescargoSerializer(serializers.HyperlinkedModelSerializer):


	convenio = ContratoSerializer(read_only=True)
	convenio_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all()) 

	departamento = DepartamentoSerializer(read_only=True)
	departamento_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Departamento.objects.all()) 

	class Meta:
		model = AIdInternoDescargo
		fields=('id' , 'convenio','convenio_id','departamento','departamento_id','numero')

class AIdInternoDescargoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model=AIdInternoDescargo
	queryset = model.objects.all()
	serializer_class = AIdInternoDescargoSerializer
	nombre_modulo = 'Descargo - AIdInternoDescargoViewSet'

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
			queryset = super(AIdInternoDescargoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			contrato_id = self.request.query_params.get('contrato',None)
			departamento_id = self.request.query_params.get('departamento',None)

			if (dato or departamento_id or contrato_id ):

				if (dato):
					if dato:
						qset = (
							Q(numero=dato)
							)
	
				if contrato_id:
					if dato:
						qset = qset &(
							Q(convenio__id=contrato_id)
							)
					else:
						qset=(Q(convenio__id=contrato_id))
	
				if departamento_id:
	
					if contrato_id or dato:
						# print departamento_id
						qset = qset &(
							Q(departamento__id=departamento_id)
							)
					else:
						qset = (
							Q(departamento__id=departamento_id)
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
				serializer = AIdInternoDescargoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():

					serializer.save(convenio_id=request.DATA['convenio_id'],departamento_id=request.DATA['departamento_id'])
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
				serializer = AIdInternoDescargoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.save(serializer)
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
#Fin api rest para id interno


#Api rest para  maniobra
class ManiobraSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = AManiobra
		fields=('id' , 'nombre')

class ManiobraViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model=AManiobra
	queryset = model.objects.all()
	serializer_class = ManiobraSerializer
	nombre_modulo = 'Descargo - ManiobraViewSet'

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
			queryset = super(ManiobraViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			
			if (dato):
				if dato:
					qset = (
						Q(nombre__icontains=dato)
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
				serializer = ManiobraSerializer(data=request.DATA,context={'request': request})

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
				serializer = ManiobraSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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
#Fin api rest para maniobra


#Api rest para  motivo sgi
class MotivoSgiSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = ABMotivoSgi
		fields=('id' , 'nombre','estado_descargo')

class MotivoSgiViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model=ABMotivoSgi
	queryset = model.objects.all()
	serializer_class = MotivoSgiSerializer
	nombre_modulo = 'Descargo - MotivoSgiViewSet'

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
			queryset = super(MotivoSgiViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			
			if (dato):
				if dato:
					qset = (
						Q(nombre__icontains=dato)
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
				serializer = MotivoSgiSerializer(data=request.DATA,context={'request': request})

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
				serializer = MotivoSgiSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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
#Fin api rest para motivo sgi


#Api rest para  MotivoInterventor
class MotivoInterventorSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = AMotivoInterventor
		fields=('id' , 'nombre','motivo_sgi')

class MotivoInterventorViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model=AMotivoInterventor
	queryset = model.objects.all()
	serializer_class = MotivoInterventorSerializer
	nombre_modulo = 'Descargo - MotivoInterventorViewSet'

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
			queryset = super(MotivoInterventorViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			
			if (dato):
				if dato:
					qset = (
						Q(nombre__icontains=dato)
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
				serializer = MotivoInterventorSerializer(data=request.DATA,context={'request': request})

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
				serializer = MotivoInterventorSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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
#Fin api rest para Motivo Interventor


#Api rest para  trabajo descargo
class DescargoTrabajoSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = ATrabajo
		fields=('id' , 'nombre')

class DescargoTrabajoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model=ATrabajo
	queryset = model.objects.all()
	serializer_class = DescargoTrabajoSerializer
	nombre_modulo = 'Descargo - DescargoTrabajoViewSet'

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
			queryset = super(DescargoTrabajoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			
			if (dato):
				if dato:
					qset = (
						Q(nombre__icontains=dato)
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
				serializer = DescargoTrabajoSerializer(data=request.DATA,context={'request': request})

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
				serializer = DescargoTrabajoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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
#Fin api rest para trabajo descargo	


#Api rest para  descargo
class DescargoSerializer(serializers.HyperlinkedModelSerializer):


	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.all()) 

	proyecto = ProyectoLiteSerializer(read_only=True)
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Proyecto.objects.all())

	maniobra = ManiobraSerializer(read_only=True)
	maniobra_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = AManiobra.objects.all())

	jefe_trabajo = EmpleadoLiteSerializer(read_only=True)
	jefe_trabajo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empleado.objects.all())

	agente_descargo = EmpleadoLiteSerializer(read_only=True)
	agente_descargo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empleado.objects.all())

	contratista = EmpresaLiteSerializer(read_only=True)
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.filter(esContratista=True)) 

	trabajo = DescargoTrabajoSerializer(read_only=True,many=True)


	class Meta:
		model = Descargo
		fields=('id' ,'id_interno','numero','trabajo','estado','estado_id','proyecto','proyecto_id','barrio','direccion','bdi','perdida_mercado','area_afectada','elemento_intervenir','maniobra','maniobra_id','fecha','hora_inicio','hora_fin','jefe_trabajo','jefe_trabajo_id','agente_descargo','agente_descargo_id','observacion','correo_bdi','soporte_ops','soporte_protocolo','lista_chequeo','numero_requerimiento','contratista','contratista_id','motivo_sgi','motivo_interventor','observacion_interventor')

class DescargoLiteSerializer(serializers.HyperlinkedModelSerializer):

	estado = EstadoSerializer(read_only=True)
	proyecto = ProyectoLiteSerializer(read_only=True)

	class Meta:
		model = Descargo
		fields=('id' , 'id_interno','numero','estado','proyecto')

class DescargoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model=Descargo
	queryset = model.objects.all()
	serializer_class = DescargoSerializer
	nombre_modulo = 'Descargo - DescargoViewSet'

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
			queryset = super(DescargoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			agente = self.request.query_params.get('agente', None)
			mcontrato= self.request.query_params.get('mcontrato', None)
			contratista = self.request.query_params.get('contratista', None)
			municipio = self.request.query_params.get('municipio', None)
			departamento = self.request.query_params.get('departamento', None)
			estado = self.request.query_params.get('estado', None)
			fechadesde = self.request.query_params.get('fechadesde', None)
			fechahasta = self.request.query_params.get('fechahasta', None)
			bdi = self.request.query_params.get('bdi',None)
			perdida = self.request.query_params.get('perdida',None)
			hora_inicio = self.request.query_params.get('hora_inicio',None)
			hora_fin = self.request.query_params.get('hora_fin',None)
			jefetrabajo = self.request.query_params.get('jefe_trabajo',None)
			proyecto = self.request.query_params.get('proyecto',None)
			liteversion = self.request.query_params.get('lite',None)

			qset=(Q(proyecto__in=(Proyecto_empresas.objects.filter(empresa_id=request.user.usuario.empresa.id).values('proyecto'))))
			# request.user.usuario.empresa.id

			# if (dato  or agente and int(agente)>0 or mcontrato and int(mcontrato)>0 or 
			# 	contratista and int(contratista)>0 or municipio and int(municipio)>0 or 
			# 	departamento and int(departamento)>0 or estado and int(estado)>0 or 
			# 	fechadesde or fechahasta or bdi or perdida or hora_inicio or hora_fin or jefetrabajo):
			if dato:
				qset = qset &(Q(numero__icontains=dato)|Q(id_interno__icontains=dato))
			if agente:
				qset = qset &(Q(agente_descargo_id=agente))
			if jefetrabajo:
				qset = qset &(Q(jefe_trabajo_id=jefetrabajo))						
			if mcontrato and int(mcontrato)>0:
				qset = qset &(Q(proyecto__mcontrato_id=mcontrato))
			if contratista and int(contratista)>0:
				qset = qset &(Q(contratista_id=contratista))
			if departamento and int(departamento)>0:
				qset = qset &(Q(proyecto__municipio__departamento_id=departamento))
			if municipio and int(municipio)>0:
				qset = qset &(Q(proyecto__municipio_id=municipio))
			if proyecto and int(proyecto)>0:
				qset = qset &(Q(proyecto__id=proyecto))
			if estado and int(estado)>0:
				qset = qset &(Q(estado_id=estado))
			if fechadesde:
				qset = qset &(Q(fecha__gte=fechadesde))
			if fechahasta:
				qset = qset &(Q(fecha__lte=fechahasta))
			if bdi:
				qset = qset &(Q(bdi=bdi))
			if perdida:
				qset = qset &(Q(perdida_mercado=perdida))
			if hora_inicio and hora_fin:
				qset = qset &((Q(hora_inicio__range=(hora_inicio,hora_fin)))|(Q(hora_fin__range=(hora_inicio,hora_fin))))
			queryset = self.model.objects.filter(qset).order_by('-id')
			#print queryset.query

			serializer_context = {
				'request': request,
			}
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if liteversion is not None:

						serializer = DescargoLiteSerializer(page,many=True,context=serializer_context)

						return self.get_paginated_response({'message':'','success':'ok',
							'data':serializer.data})

					serializer = self.get_serializer(page,many=True,context=serializer_context)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})


			if liteversion is not None:

				serializer = DescargoLiteSerializer(queryset,many=True,context=serializer_context)

				return Response({'message':'','success':'ok',
					'data':serializer.data})

			serializer = self.get_serializer(queryset,many=True,context=serializer_context)

			if hora_inicio is not None and hora_fin is not None:
				if queryset:
					return Response({'message':'La persona se encuentra ocupado en esa hora, seleccione otra hora ','success':'warnning','data':serializer.data})
				else:
					return Response({'message':'Esta persona se encuentra disponible','success':'ok',
						'data':serializer.data})					
			else:
				return Response({'message':'','success':'ok',
					'data':serializer.data})				
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:		

				serializer = DescargoSerializer(data=request.DATA,context={'request': request})						
				if serializer.is_valid():
					serializer.save(estado_id=request.DATA['estado_id'],proyecto_id=request.DATA['proyecto_id'],
						maniobra_id=request.DATA['maniobra_id'],agente_descargo_id=request.DATA['agente_descargo_id'],jefe_trabajo_id=request.DATA['jefe_trabajo_id'],
						contratista_id=request.DATA['contratista_id'],soporte_ops='',soporte_protocolo='')
					createTrabajoDescargo(str(request.DATA['trabajo_id']),serializer.data['id'])
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					# print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				if e.code=='busyboss':
					return JsonResponse({'message':'El jefe de trabajo se encuentra ocupado en esa hora','success':'warning','status':'warning','data':''})
				elif e.code=='busyagent':
					return JsonResponse({'message':'El agente se encuentra ocupado en esa hora','success':'warning','status':'warning','data':''})
				else:
					functions.toLog(e,self.nombre_modulo)
					return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  			'data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:

				partial = kwargs.pop('partial', False)
				instance = self.get_object()

				if request.DATA['numero']=='null':
					request.DATA['numero']=None
						
				serializer = DescargoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
					
				# print 'asdadas'
				if serializer.is_valid():
	
					if request.DATA['observacion_interventor']=='null':
						request.DATA['observacion_interventor']=None
	
					if request.DATA['numero_requerimiento']=='null':
						request.DATA['numero_requerimiento']=None

					serializer.save(soporte_ops=request.FILES.get('soporte_ops'),lista_chequeo=request.FILES.get('lista_chequeo'),estado_id=request.DATA['estado_id'],proyecto_id=request.DATA['proyecto_id'],
							maniobra_id=request.DATA['maniobra_id'],agente_descargo_id=request.DATA['agente_descargo_id'],jefe_trabajo_id=request.DATA['jefe_trabajo_id'],
							contratista_id=request.DATA['contratista_id'],soporte_protocolo=request.FILES.get('soporte_protocolo'),correo_bdi=request.FILES.get('correo_bdi'))
					if request.DATA['trabajo_id']!='':
						createTrabajoDescargo(str(request.DATA['trabajo_id']),serializer.data['id'])
	
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:

					# print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)


			except Exception as e:

				if e.code=='unico':
					return JsonResponse({'message':'El numero de descargo ya se encuentra en el sistema','success':'warning','status':'warning','data':''})
					# return JsonResponse({'message':str(e.__str__,'status':'warning','data':''})
				elif e.code=='busyboss':
					return JsonResponse({'message':'El jefe de trabajo se encuentra ocupado en esa hora','success':'warning','status':'warning','data':''})
				elif e.code=='busyagent':
					return JsonResponse({'message':'El agente se encuentra ocupado en esa hora','success':'warning','status':'warning','data':''})					
				else:
					functions.toLog(e,self.nombre_modulo)
					transaction.savepoint_rollback(sid)
					return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			

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
#Fin api rest para descargo


#Api rest para fotos de descargo
class FotoDescargoSerializer(serializers.HyperlinkedModelSerializer):

	descargo = DescargoSerializer(read_only=True)
	descargo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Descargo.objects.all()) 

	class Meta:
		model = FotoDescargo
		fields=('id' , 'ruta' , 'regla','descargo','descargo_id')

class FotoDescargoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model=FotoDescargo
	queryset = model.objects.all()
	serializer_class = FotoDescargoSerializer
	nombre_modulo = 'Descargo - FotoDescargoViewSet'

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
			queryset = super(FotoDescargoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			descargo = self.request.query_params.get('descargo', None)
			
			if (dato or descargo):
				if dato:
					qset = (
						Q(regla__icontains=dato)
						)

				if descargo:
					if dato:
						qset = qset &(
							Q(descargo__id=descargo)
							)
					else:
						qset=(Q(descargo__id=descargo))

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
				serializer = FotoDescargoSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(descargo_id=request.DATA['descargo_id'],ruta=request.FILES.get('ruta'))
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
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
				serializer = FotoDescargoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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
#fin api rest para fotos de descargo


#guardado descargo especifico
def createTrabajoDescargo(trabajolist, descargo_id):
	# if request.method == 'POST':
	nombre_modulo = 'Descargo - createTrabajoDescargo'
	try:
		myList = trabajolist.split(',')
		descargo = Descargo.objects.get(pk=descargo_id)
		descargo.trabajo.remove(*myList)
		descargo.trabajo.add(*myList)
		return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Actualiza el numero del radicado y la fecha en la pestana no.radicado
@transaction.atomic
def actualizar_nodescargo(request):

	nombre_modulo = 'Descargo - actualizar_nodescargo'
	sid = transaction.savepoint()
	try:
		
		lista=request.POST['_content']
		respuesta= json.loads(lista)		
		id = respuesta['id']
		numero = respuesta['numero']

		descargo=Descargo.objects.get(pk=id)
		descargo.numero=numero

		descargo.save()

		# print descargo.save()

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='descargo.descargo',id_manipulado=id)
		logs_model.save()

		transaction.savepoint_commit(sid)

		return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data':''})

	except Exception as e:
		if e.code=='unico':
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'El numero de descargo ya se encuentra en el sistema','success':'warning','status':'warning','data':''})
			# return JsonResponse({'message':str(e.__str__,'status':'warning','data':''})	
		else:
			functions.toLog(e, nombre_modulo)
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			

#Actualiza el numero del radicado y la fecha en la pestana no.radicado
@transaction.atomic
def actualizar_estado(request):

	nombre_modulo = 'Descargo - actualizar_estado'
	sid = transaction.savepoint()
	try:
				
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		for item in respuesta['lista']:		

			motivo_sgi = respuesta['motivo_sgi']
			motivo_interventor = respuesta['motivo_interventor']
			estado = respuesta['estado']

			descargo=Descargo.objects.get(pk=item)
			descargo.estado_id=estado
			descargo.motivo_interventor_id=motivo_interventor
			descargo.motivo_sgi_id=motivo_sgi
			descargo.save()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='descargo.descargo',id_manipulado=item)
			logs_model.save()

		transaction.savepoint_commit(sid)

		return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data':''})

	except Exception as e:
		functions.toLog(e, nombre_modulo)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Actualiza el numero del radicado y la fecha en la pestana no.radicado
@transaction.atomic
def estado_completar(request):

	nombre_modulo = 'Descargo - estado_completar'
	sid = transaction.savepoint()
	try:
				
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		descargo=Descargo.objects.get(pk=respuesta['id'])

		if respuesta['caso']==1:
			observacion_interventoria = respuesta['observacion']
			estado = respuesta['estado']
			descargo.estado_id=estado
			descargo.observacion_interventor=observacion_interventoria


		elif respuesta['caso']==2:
			descargo.numero_requerimiento = respuesta['numero_requerimiento']


		elif respuesta['caso']==3:
			descargo.lista_chequeo = respuesta['lista_chequeo']
			descargo.soporte_protocolo = respuesta['soporte_protocolo']
			

		descargo.save()
		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='descargo.descargo',id_manipulado=respuesta['id'])
		logs_model.save()

		transaction.savepoint_commit(sid)

		return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data':''})

	except Exception as e:
		functions.toLog(e, nombre_modulo)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#vistas
def descargo(request):
	return render(request, 'descargo/descargo_opciones.html')

def registroconsulta(request):
	tipo_c=tipoC()

	form = DescargoForm(
		request.POST or None
	)
	if request.POST:
		if form.is_valid():
			form.save()		
	context = {
		'form': form['estado'],
		'form2':form['motivo_sgi'],
		'form3':form['motivo_interventor'],
		'mcontrato':Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato,empresacontrato__empresa=request.user.usuario.empresa.id,empresacontrato__participa=1,activo=1),
		'motivo_sgi': ABMotivoSgi.objects.all(),
		'trabajo': ATrabajo.objects.all(),
		'contratista': EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id,contrato__tipo_contrato_id=tipo_c.contratoProyecto,participa=1,contrato__activo=1).values('contrato__contratista__id','contrato__contratista__nombre'),
		'departamento': Departamento.objects.all(),
		'municipio': Municipio.objects.all(),
		'proyecto': Proyecto.objects.all(),
		'estado':Estado.objects.filter(app='descargo'),
		'model':'descargo',
		'app':'descargo'

	}	

	return render(request, 'descargo/registrar_consulta.html',context)

def registro(request):

	tipo_c=tipoC()

	querysetTrabajo=ATrabajo.objects.all()

	querysetManiobra=AManiobra.objects.all()

	querysetEstadosdescargo=Estado.objects.filter(app='descargo')

	querysetmcontrato=Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato,empresacontrato__empresa=request.user.usuario.empresa.id,empresacontrato__participa=1,activo=1)

	querysetcontratista=Empresa.objects.filter(esContratista=True)

	guardar='Guardar'

	return render(request, 'descargo/descargo_registrar.html',{'guardar':guardar,'maniobra':querysetManiobra,'mcontrato':querysetmcontrato,'contratista_sec':querysetcontratista,'id_descargo_editar':0,'trabajo':querysetTrabajo,'estado':querysetEstadosdescargo,'model':'descargo','app':'descargo'})

def mapadescargo(request):
	tipo_c=tipoC()

	querysetmcontrato=Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato,empresacontrato__empresa=request.user.usuario.empresa.id,empresacontrato__participa=1,activo=1)
	return render(request, 'descargo/mapa_descargo.html',{'model':'descargo','mcontrato':querysetmcontrato,'app':'descargo'})	

def registrocc(request,id):

	tipo_c=tipoC()

	querysetTrabajo=ATrabajo.objects.all()

	querysetmcontrato=Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato,empresacontrato__empresa=request.user.usuario.empresa.id,empresacontrato__participa=1,activo=1)

	querysetEstadosdescargo=Estado.objects.filter(app='descargo')

	querysetcontratista=Empresa.objects.filter(esContratista=True)

	querysetManiobra=AManiobra.objects.all()

	contratistaagente=Descargo.objects.get(pk=id)

	contratoobra=Proyecto.contrato.through.objects.filter(proyecto_id=contratistaagente.proyecto.id,contrato__tipo_contrato=tipo_c.contratoProyecto).values('contrato_id')

	if contratoobra.exists():
		obra=contratoobra[0]
	else:
		obra=0

	guardar='Guardar'

	copia=1

	return render(request, 'descargo/descargo_registrar.html',{'copia':copia,'guardar':guardar,'contratista_jefe':contratistaagente.jefe_trabajo.contratista.id,'contratoobra':obra,'contratista_agente':contratistaagente.agente_descargo.contratista.id,'mcontrato':querysetmcontrato,'maniobra':querysetManiobra,'contratista_sec':querysetcontratista,'id_descargo_editar':id,'trabajo':querysetTrabajo,'estado':querysetEstadosdescargo,'model':'descargo','app':'descargo'})
	
def registro_editar(request,id):

	tipo_c=tipoC()

	querysetTrabajo=ATrabajo.objects.all()

	querysetmcontrato=Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato,empresacontrato__empresa=request.user.usuario.empresa.id,empresacontrato__participa=1,activo=1)

	querysetEstadosdescargo=Estado.objects.filter(app='descargo')

	querysetcontratista=Empresa.objects.filter(esContratista=True)

	querysetManiobra=AManiobra.objects.all()

	contratistaagente=Descargo.objects.get(pk=id)
	# func_resp = model_funcionario.responsabilidades.through.objects.filter(eresponsabilidades_id__in = myList)

	contratoobra=Proyecto.contrato.through.objects.filter(proyecto_id=contratistaagente.proyecto.id,contrato__tipo_contrato=tipo_c.contratoProyecto).values('contrato_id')

	if contratoobra.exists():
		obra=contratoobra[0]
	else:
		obra=0

	editar='Editar'

	return render(request, 'descargo/descargo_registrar.html',{'guardar':editar,'contratista_jefe':contratistaagente.jefe_trabajo.contratista.id,'contratoobra':obra,'contratista_agente':contratistaagente.agente_descargo.contratista.id,'mcontrato':querysetmcontrato,'maniobra':querysetManiobra,'contratista_sec':querysetcontratista,'id_descargo_editar':id,'trabajo':querysetTrabajo,'estado':querysetEstadosdescargo,'model':'descargo','app':'descargo'})

def completarregistro(request,id):

	querysetEstadosdescargo=Estado.objects.filter(app='descargo')

	return render(request, 'descargo/completar_registro.html',{'estados':querysetEstadosdescargo,'id_descargo':id,'model':'descargo','app':'descargo'})

def correodedescargo(request):

	form = DescargoCorreoForm(
		request.POST or None
	)
	if request.POST:
		if form.is_valid():
			form.save()
	context = {
		'form': form,
		'model':'descargo',
		'app':'descargo'
	}

	return render(request, 'descargo/correo_descargo.html',context)

@transaction.atomic
def eliminar_varios_id(request):

	nombre_modulo = 'Descargo - eliminar_varios_id'
	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		#print respuesta['lista'].split()

		#lista=respuesta['lista'].split(',')
		
		for item in respuesta['lista']:
			Correo_descargo.objects.filter(id=item['id']).delete()

		#return HttpResponse(str('0'), content_type="text/plain")

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='descargo.Correodescargo',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})

		
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})			 


# exporta a excel contrato
def exportReporteDescargo(request):

	tipo_c=tipoC()
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="Reporte descargo.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Todos')
	format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
	format1.set_align('center')
	format1.set_align('vcenter')
	format2=workbook.add_format({'border':0})
	format3=workbook.add_format({'border':0,'font_size':12})
	format5=workbook.add_format()
	format6=workbook.add_format()
	format5.set_num_format('yyyy-mm-dd')
	format6.set_num_format('hh:mm')

	worksheet.set_column('A:AF', 30)
	m=[]
	worksheetarray=[]
	rowarray=[]

	row=1
	col=0
	trabajos=''
	trs=''

	# cursor = connection.cursor()

	# encabezado_id= request.GET['encabezado_id']

	dato = None
	mcontrato = None
	departamento = None
	municipio = None
	estado = None
	fechadesde = None
	fechahasta = None
	bdi = None
	perdida = None
	contratista = None

	id_empresa = request.user.usuario.empresa.id

	if request.GET['dato']:
		dato = request.GET['dato']
	if request.GET['mcontrato']:
		mcontrato = request.GET['mcontrato']
	if request.GET['departamento']:
		departamento = request.GET['departamento']				
	if request.GET['municipio']:
		municipio = request.GET['municipio']		
	if request.GET['fechadesde']:
		fechadesde = request.GET['fechadesde']	
	if request.GET['fechahasta']:
		fechahasta = request.GET['fechahasta']			
	if request.GET['bdi']:
		bdi = request.GET['bdi']
	if request.GET['perdida']:
		perdida = request.GET['perdida']			
	if request.GET['id_estado']:
		estado = request.GET['id_estado']
	if request.GET['contratista']:
		contratista = request.GET['contratista']

	qset = None

	if dato!=None or int(mcontrato)>0 or int(departamento)>0 or int(municipio)>0 or int(estado)>0 or fechadesde != None or fechahasta!=None or bdi !=None or perdida != None or int(contratista)>0:
		
		if dato:
			qset = (
				Q(fecha__icontains=dato)|
				Q(id_interno__icontains=dato)
				)
		
		if mcontrato and int(mcontrato)>0:
			if dato  :
				qset = qset &(
					Q(proyecto__mcontrato_id=mcontrato)
					)
			else:
				qset=(Q(proyecto__mcontrato_id=mcontrato))
	
		if contratista and int(contratista)>0:
			if dato  or mcontrato :
				qset = qset &(
					Q(proyecto__contrato__contratista_id=contratista)
					)
			else:
				qset=(Q(proyecto__contrato__contratista_id=contratista))			
	
	
		if departamento and int(departamento)>0:
			if dato  or mcontrato or contratista :
				qset = qset &(
					Q(proyecto__municipio__departamento_id=departamento)
					)
			else:
				qset=(Q(proyecto__municipio__departamento_id=departamento))
	
		if municipio and int(municipio)>0:
			if dato  or mcontrato or contratista or departamento :
				qset = qset &(
					Q(proyecto__municipio_id=municipio)
					)
			else:
				qset=(Q(proyecto__municipio_id=municipio))
	
		if estado and int(estado)>0:
			if dato  or mcontrato and int(mcontrato)>0  or contratista and int(contratista)>0 or departamento and int(departamento)>0 or municipio and int(municipio)>0 :
				qset = qset &(
					Q(estado_id=estado)
					)
			else:
				qset=(Q(estado_id=estado))
	
		if fechadesde:
			if dato  or mcontrato and int(mcontrato)>0  or departamento and int(departamento)>0 or municipio and int(municipio)>0 or estado and int(estado)>0 :
				qset = qset &(
					Q(fecha__gte=fechadesde)
					)
			else:
				qset=(Q(fecha__gte=fechadesde))	
	
	
		if fechahasta:
			if dato  or mcontrato and int(mcontrato)>0  or contratista and int(contratista)>0 or departamento and int(departamento)>0 or municipio and int(municipio)>0 or estado and int(estado)>0 :
				qset = qset &(
					Q(fecha__lte=fechahasta)
					)
			else:
				qset=(Q(fecha__lte=fechahasta))
	
		if bdi:
			if dato  or mcontrato and int(mcontrato)>0  or contratista and int(contratista)>0 or departamento and int(departamento)>0 or municipio and int(municipio)>0 or estado and int(estado)>0 :
				qset = qset &(
					Q(bdi=bdi)
					)
			else:
				qset=(Q(bdi=bdi))
	
		if perdida:
			if dato  or mcontrato and int(mcontrato)>0  or contratista and int(contratista)>0 or departamento and int(departamento)>0 or municipio and int(municipio)>0 or estado and int(estado)>0 :
				qset = qset &(
					Q(perdida_mercado=perdida)
					)
			else:
				qset=(Q(perdida_mercado=perdida))
	else:


		last_month = datetime.today() - timedelta(days=180)

		qset=(Q(fecha__gte=last_month))

	

	model=Descargo
	formato_fecha = "%Y-%m-%d"
	if qset is not None:
		queryset = model.objects.filter(qset).order_by('-id')

		# serializer = self.get_serializer(queryset,many=True)
		# return Response({'message':'','success':'ok','data':serializer.data})

		# detalle = DetalleGiro.objects.filter(qset)

		worksheet.write('A1', 'Consultor', format1)
		worksheet.write('B1', 'ID interno', format1)
		worksheet.write('C1', 'Convenio/Contrato', format1)
		worksheet.write('D1', 'No. Descargo', format1)
		worksheet.write('E1', 'Estado Descargo', format1)
		worksheet.write('F1', 'Municipio', format1)
		worksheet.write('G1', 'Contratista', format1)
		worksheet.write('H1', 'Nombre Proyecto', format1)
		worksheet.write('I1', 'Numero Contrato', format1)
		worksheet.write('J1', 'Barrio', format1)
		worksheet.write('K1', 'Direccion', format1)
		worksheet.write('L1', 'BDI', format1)
		worksheet.write('M1', 'Orden de Servicio', format1)
		worksheet.write('N1', 'Area Afectada', format1)
		worksheet.write('O1', 'Elemento a intervenir', format1)
		worksheet.write('P1', 'Maniobra', format1)
		worksheet.write('Q1', 'Trabajo', format1)
		worksheet.write('R1', 'Fecha', format1)
		worksheet.write('S1', 'Hora inicio', format1)
		worksheet.write('T1', 'Hora fin', format1)
		worksheet.write('U1', 'Jefe trabajo', format1)
		worksheet.write('V1', 'Agente zona de trabajo', format1)
		worksheet.write('W1', 'Observacion', format1)
		worksheet.write('X1', 'Motivo SGI', format1)
		worksheet.write('Y1', 'Observacion interventoria', format1)
		worksheet.write('Z1', 'Motivo interventor', format1)
		worksheet.write('AA1', 'No. Requerimiento', format1)
		worksheet.write('AB1', 'Correo BDI', format1)
		worksheet.write('AC1', 'Formato IPDC', format1)
		worksheet.write('AD1', 'Soporte Protocolo', format1)
		worksheet.write('AE1', 'Lista de chequeo', format1)
		worksheet.write('AF1', 'Estado Registro', format1)

	# parsed = json.loads(queryset)
	# print json.dumps(parsed, indent=4, sort_keys=True)
	# for pestanas in queryset:

	# 	if pestanas.proyecto.municipio.departamento.id not in m:
	# 		m.append(pestanas.proyecto.municipio.departamento.id)
	# 		worksheetarray.append(workbook.add_worksheet(str(pestanas.proyecto.municipio.departamento.nombre)))

	for descargo in queryset:

		if descargo.proyecto.municipio.departamento.id not in m:
			m.append(descargo.proyecto.municipio.departamento.id)
			worksheetarray.append(workbook.add_worksheet(str(descargo.proyecto.municipio.departamento.nombre)))

			posicion= m.index(descargo.proyecto.municipio.departamento.id)

			rowarray.append(1)

			worksheetarray[posicion].set_column('A:AF', 30)

			worksheetarray[posicion].write('A1', 'Consultor', format1)
			worksheetarray[posicion].write('B1', 'ID interno', format1)
			worksheetarray[posicion].write('C1', 'Convenio/Contrato', format1)
			worksheetarray[posicion].write('D1', 'No. Descargo', format1)
			worksheetarray[posicion].write('E1', 'Estado Descargo', format1)
			worksheetarray[posicion].write('F1', 'Municipio', format1)
			worksheetarray[posicion].write('G1', 'Contratista', format1)
			worksheetarray[posicion].write('H1', 'Nombre Proyecto', format1)
			worksheetarray[posicion].write('I1', 'Numero Contrato', format1)
			worksheetarray[posicion].write('J1', 'Barrio', format1)
			worksheetarray[posicion].write('K1', 'Direccion', format1)
			worksheetarray[posicion].write('L1', 'BDI', format1)
			worksheetarray[posicion].write('M1', 'Orden de Servicio', format1)
			worksheetarray[posicion].write('N1', 'Area Afectada', format1)
			worksheetarray[posicion].write('O1', 'Elemento a intervenir', format1)
			worksheetarray[posicion].write('P1', 'Maniobra', format1)
			worksheetarray[posicion].write('Q1', 'Trabajo', format1)
			worksheetarray[posicion].write('R1', 'Fecha', format1)
			worksheetarray[posicion].write('S1', 'Hora inicio', format1)
			worksheetarray[posicion].write('T1', 'Hora fin', format1)
			worksheetarray[posicion].write('U1', 'Jefe trabajo', format1)
			worksheetarray[posicion].write('V1', 'Agente zona de trabajo', format1)
			worksheetarray[posicion].write('W1', 'Observacion', format1)
			worksheetarray[posicion].write('X1', 'Motivo SGI', format1)
			worksheetarray[posicion].write('Y1', 'Observacion interventoria', format1)
			worksheetarray[posicion].write('Z1', 'Motivo interventor', format1)
			worksheetarray[posicion].write('AA1', 'No. Requerimiento', format1)
			worksheetarray[posicion].write('AB1', 'Correo BDI', format1)
			worksheetarray[posicion].write('AC1', 'Formato IPDC', format1)
			worksheetarray[posicion].write('AD1', 'Soporte Protocolo', format1)
			worksheetarray[posicion].write('AE1', 'Lista de chequeo', format1)
			worksheetarray[posicion].write('AF1', 'Estado Registro', format1)

		if descargo.proyecto.municipio.departamento.id in m:


			posicion= m.index(descargo.proyecto.municipio.departamento.id)

			# if detalle.cuenta is not None:
			# 	cuenta_nombre= "Girar de la cuenta de %s No. %s ' - ' %s" % (detalle.cuenta.nombre , detalle.cuenta.numero, detalle.cuenta.fiduciaria) if detalle.cuenta.nombre is not None else ''
	
			# if detalle.cuenta is not None:
			# 	cuenta_referencia= detalle.encabezado.referencia  if detalle.encabezado.referencia is not None else ''	
			#worksheet.write(row, col,descargo.nombre,format2)
			worksheetarray[posicion].write(rowarray[posicion], col+1,descargo.id_interno,format2)#id interno
			worksheetarray[posicion].write(rowarray[posicion], col+2,descargo.proyecto.mcontrato.nombre,format2)#convenio/contrato
			worksheetarray[posicion].write(rowarray[posicion], col+3,descargo.numero,format2)#No.Descargo
			worksheetarray[posicion].write(rowarray[posicion], col+4,descargo.estado.nombre,format2)#estado descargo
			worksheetarray[posicion].write(rowarray[posicion], col+5,descargo.proyecto.municipio.nombre,format2)#municipio
			worksheetarray[posicion].write(rowarray[posicion], col+6,descargo.contratista.nombre,format2)#contratista
			worksheetarray[posicion].write(rowarray[posicion], col+7,descargo.proyecto.nombre,format2)#nombre proyecto
			worksheetarray[posicion].write(rowarray[posicion], col+9,descargo.barrio,format2)#Barrio
			worksheetarray[posicion].write(rowarray[posicion], col+10,descargo.direccion,format2)#direccion
			if descargo.bdi==False:
				worksheetarray[posicion].write(rowarray[posicion], col+11,'No',format2)#BDI
			else:
				worksheetarray[posicion].write(rowarray[posicion], col+11,'Si',format2)#BDI
			if descargo.perdida_mercado==False:
				worksheetarray[posicion].write(rowarray[posicion], col+12,'No',format2)#Orden de servicio
			else:
				worksheetarray[posicion].write(rowarray[posicion], col+12,'Si',format2)#Orden de servicio
			worksheetarray[posicion].write(rowarray[posicion], col+13,descargo.area_afectada,format2)#Area Afectada
			worksheetarray[posicion].write(rowarray[posicion], col+14,descargo.elemento_intervenir,format2)#Elemento a intervenir
			worksheetarray[posicion].write(rowarray[posicion], col+15,descargo.maniobra.nombre,format2)#Maniobra
			for trabajo in descargo.trabajo.all():
				trabajos = trabajo.nombre+','+trabajos
			trabajos=trabajos[:-1]
			worksheetarray[posicion].write(rowarray[posicion], col+16,trabajos,format2)#Trabajo
			trabajos=''
			worksheetarray[posicion].write(rowarray[posicion], col+17,descargo.fecha,format5)#Fecha
			worksheetarray[posicion].write(rowarray[posicion], col+18,descargo.hora_inicio,format6)#Hora inicio
			worksheetarray[posicion].write(rowarray[posicion], col+19,descargo.hora_fin,format6)#hora fin
			worksheetarray[posicion].write(rowarray[posicion], col+20,descargo.jefe_trabajo.persona.nombres+' '+descargo.jefe_trabajo.persona.apellidos,format2)#Jefe trabajo
			worksheetarray[posicion].write(rowarray[posicion], col+21,descargo.agente_descargo.persona.nombres+' '+descargo.agente_descargo.persona.apellidos,format2)#Agente zona de trabajo
			worksheetarray[posicion].write(rowarray[posicion], col+22,descargo.observacion,format2)#Observacion
			if descargo.motivo_sgi==None:
				worksheetarray[posicion].write(rowarray[posicion], col+23,'',format2)#Motivo SGI
			else:
				worksheetarray[posicion].write(rowarray[posicion], col+23,descargo.motivo_sgi.nombre,format2)#Motivo SGI
			worksheetarray[posicion].write(rowarray[posicion], col+24,descargo.observacion_interventor,format2)#Observacion interventoria
			if descargo.motivo_interventor==None:
				worksheetarray[posicion].write(rowarray[posicion], col+25,'',format2)#Motivo interventor
			else:
				worksheetarray[posicion].write(rowarray[posicion], col+25,descargo.motivo_interventor.nombre,format2)#Motivo interventor
			worksheetarray[posicion].write(rowarray[posicion], col+26,descargo.numero_requerimiento,format2)#No requerimiento
			if descargo.correo_bdi==None:
				worksheetarray[posicion].write(rowarray[posicion], col+27,'Por Subir',format2)#Correo BDI
			else:
				worksheetarray[posicion].write(rowarray[posicion], col+27,str(descargo.correo_bdi),format2)#Correo BDI
			if descargo.soporte_ops==None:
				worksheetarray[posicion].write(rowarray[posicion], col+28,'Por subir',format2)#Formato IPDC
			else:
				worksheetarray[posicion].write(rowarray[posicion], col+28,str(descargo.soporte_ops),format2)#Formato IPDC
			if descargo.soporte_protocolo==None:
				worksheetarray[posicion].write(rowarray[posicion], col+29,descargo.soporte_protocolo,format2)#Soporte protocolo
			else:
				worksheetarray[posicion].write(rowarray[posicion], col+29,str(descargo.soporte_protocolo),format2)#Soporte protocolo
			if descargo.lista_chequeo==None:
				worksheetarray[posicion].write(rowarray[posicion], col+30,'Por subir',format2)#Lista de chequeo
			else:
				worksheetarray[posicion].write(rowarray[posicion], col+30,str(descargo.lista_chequeo),format2)#Lista de chequeo
			#worksheetarray[posicion].write(rowarray[posicion], col+12,descargo.estado.nombre,format2)#Estado Registro
	
	
			for contrato in descargo.proyecto.contrato.all():
				if contrato.tipo_contrato.id == tipo_c.contratoProyecto:
					worksheetarray[posicion].write(rowarray[posicion], col+8,contrato.numero,format5)
				if contrato.tipo_contrato.id == tipo_c.interventoria:
					worksheetarray[posicion].write(rowarray[posicion], col,contrato.contratista.nombre,format5)
		
			rowarray[posicion]=rowarray[posicion]+1
			#worksheet.write(row, col+7,detalle.cuenta.nombre if detalle.cuenta is not None else '',format2)
		worksheet.write(row, col+1,descargo.id_interno,format2)#id interno
		worksheet.write(row, col+2,descargo.proyecto.mcontrato.nombre,format2)#convenio/contrato
		worksheet.write(row, col+3,descargo.numero,format2)#No.Descargo
		worksheet.write(row, col+4,descargo.estado.nombre,format2)#estado descargo
		worksheet.write(row, col+5,descargo.proyecto.municipio.nombre,format2)#municipio
		worksheet.write(row, col+6,descargo.contratista.nombre,format2)#contratista
		worksheet.write(row, col+7,descargo.proyecto.nombre,format2)#nombre proyecto
		worksheet.write(row, col+9,descargo.barrio,format2)#Barrio
		worksheet.write(row, col+10,descargo.direccion,format2)#direccion
		if descargo.bdi==False:
			worksheet.write(row, col+11,'No',format2)#BDI
		else:
			worksheet.write(row, col+11,'Si',format2)#BDI
		if descargo.perdida_mercado==False:
			worksheet.write(row, col+12,'No',format2)#Orden de servicio
		else:
			worksheet.write(row, col+12,'Si',format2)#Orden de servicio
		worksheet.write(row, col+13,descargo.area_afectada,format2)#Area Afectada
		worksheet.write(row, col+14,descargo.elemento_intervenir,format2)#Elemento a intervenir
		worksheet.write(row, col+15,descargo.maniobra.nombre,format2)#Maniobra
		for tr in descargo.trabajo.all():
				trs = tr.nombre+','+trs
		trs=trs[:-1]
		worksheet.write(row, col+16,trs,format2)#Trabajo
		trs=''
		#worksheet.write(row, col+12,descargo.estado.nombre,format2)#Trabajo
		worksheet.write(row, col+17,descargo.fecha,format5)#Fecha
		worksheet.write(row, col+18,descargo.hora_inicio,format6)#Hora inicio
		worksheet.write(row, col+19,descargo.hora_fin,format6)#hora fin
		worksheet.write(row, col+20,descargo.jefe_trabajo.persona.nombres+' '+descargo.jefe_trabajo.persona.apellidos,format2)#Jefe trabajo
		worksheet.write(row, col+21,descargo.agente_descargo.persona.nombres+' '+descargo.agente_descargo.persona.apellidos,format2)#Agente zona de trabajo
		worksheet.write(row, col+22,descargo.observacion,format2)#Observacion
		if descargo.motivo_sgi==None:
			worksheet.write(row, col+23,'',format2)#Motivo SGI
		else:
			worksheet.write(row, col+23,descargo.motivo_sgi.nombre,format2)#Motivo SGI
		worksheet.write(row, col+24,descargo.observacion_interventor,format2)#Observacion interventoria
		if descargo.motivo_interventor==None:
			worksheet.write(row, col+25,'',format2)#Motivo interventor
		else:
			worksheet.write(row, col+25,descargo.motivo_interventor.nombre,format2)#Motivo interventor
		worksheet.write(row, col+26,descargo.numero_requerimiento,format2)#No requerimiento
		if descargo.correo_bdi==None:
			worksheet.write(row, col+27,'Por Subir',format2)#Correo BDI
		else:
			worksheet.write(row, col+27,str(descargo.correo_bdi),format2)#Correo BDI
		if descargo.soporte_ops==None:
			worksheet.write(row, col+28,'Por subir',format2)#Formato IPDC
		else:
			worksheet.write(row, col+28,str(descargo.soporte_ops),format2)#Formato IPDC
		if descargo.soporte_protocolo==None:
			worksheet.write(row, col+29,descargo.soporte_protocolo,format2)#Soporte protocolo
		else:
			worksheet.write(row, col+29,str(descargo.soporte_protocolo),format2)#Soporte protocolo
		if descargo.lista_chequeo==None:
			worksheet.write(row, col+30,'Por subir',format2)#Lista de chequeo
		else:
			worksheet.write(row, col+30,str(descargo.lista_chequeo),format2)#Lista de chequeo
		#worksheet.write(row, col+12,descargo.estado.nombre,format2)#Estado Registro


		for contrato in descargo.proyecto.contrato.all():
			if contrato.tipo_contrato.id == tipo_c.contratoProyecto:
				worksheet.write(row, col+8,contrato.numero,format5)
			if contrato.tipo_contrato.id == tipo_c.interventoria:
				worksheet.write(row, col,contrato.contratista.nombre,format5)
		
		row +=1

	for x in xrange(1,10):
		pass

	workbook.close()
	return response


@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			tipo = request.data['tipo']
			archivo = Descargo.objects.get(pk=request.GET['id'])
			
			if tipo == 'correo_bdi':
				return functions.exportarArchivoS3(str(archivo.correo_bdi))
			elif tipo == 'soporte_ops':
				return functions.exportarArchivoS3(str(archivo.soporte_ops))
			elif tipo == 'soporte_protocolo':
				return functions.exportarArchivoS3(str(archivo.soporte_protocolo))
			elif tipo == 'lista_chequeo':
				return functions.exportarArchivoS3(str(archivo.lista_chequeo))
			

		except Exception as e:
			functions.toLog(e,'descargo.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

