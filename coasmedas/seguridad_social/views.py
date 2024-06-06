# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import transaction, connection
from datetime import *
from django.shortcuts import render,redirect,render_to_response
from django.urls import reverse
from .models import Empleado, AEscolaridad, AMatricula, Novedad, Planilla, EmpresaPermiso,ZRequerimientosEmpleados,Cargo,PlanillaEmpleado, CorreoContratista
from rest_framework import viewsets, serializers
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
from empresa.views import EmpresaSerializer
from usuario.views import PersonaSerializer, PersonaLiteSerializer
from tipo.views import TipoSerializer
from estado.views import EstadoSerializer
from estado.models import Estado

from empresa.models import Empresa
from usuario.models import Persona
from tipo.models import Tipo
from .enum import EnumEstadoPlanilla, EnumEstadoEmpleado
from logs.models import Logs,Acciones
from django.contrib.auth.decorators import login_required
from contrato.models import EmpresaContrato
from coasmedas.functions import functions
import uuid
from adminMail.models import Mensaje
from adminMail.tasks import sendAsyncMail, sendAsyncFullMail
from django.conf import settings
from rest_framework.decorators import api_view
from .enum import EnumEstadoPlanilla

# Escolaridad
class EscolaridadSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = AEscolaridad
		fields=('id','nombre',)
								  
								  
class EscolaridadViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=AEscolaridad
	queryset = model.objects.all()
	serializer_class = EscolaridadSerializer
	parser_classes=(FormParser, MultiPartParser,)
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
			queryset = super(EscolaridadViewSet, self).get_queryset()
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
				serializer = EscolaridadSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.escolaridad',id_manipulado=serializer.data['id'])
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
				serializer = EscolaridadSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='seguridad_social.escolaridad',id_manipulado=instance.id)
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
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.escolaridad',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 

# Fin Escolaridad

# Matricula

class MatriculaSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = AMatricula
		fields=('id','nombre',)
								  
								  
class MatriculaViewSet(viewsets.ModelViewSet):
	model=AMatricula
	queryset = model.objects.all()
	serializer_class = MatriculaSerializer
	parser_classes=(FormParser, MultiPartParser,)
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
			queryset = super(MatriculaViewSet, self).get_queryset()
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
				serializer = MatriculaSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save()
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.matricula',id_manipulado=serializer.data['id'])
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
				serializer = MatriculaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='seguridad_social.matricula',id_manipulado=serializer.data['id'])
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

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.matricula',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 


# Fin matricula

# Cargo
class CargoSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Cargo
		fields=('id', 'nombre', 'soporte_tsa', 'soporte_matricula', 'hoja_de_vida',)
								  
								  
class CargoSeguridadSocialViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=Cargo
	queryset = model.objects.all().order_by('nombre')
	serializer_class = CargoSerializer
	parser_classes=(FormParser, MultiPartParser,)
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
			queryset = super(CargoSeguridadSocialViewSet, self).get_queryset()
			paginacion = self.request.query_params.get('sin_paginacion', None)
			dato = self.request.query_params.get('dato', None)
			if dato:
				qset=(Q(nombre__icontains=dato))			
				queryset = self.model.objects.filter(qset).order_by('nombre')
						
			if paginacion is None:				
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})
			else:				
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})	
		except Exception as e:
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = CargoSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.cargo',id_manipulado=serializer.data['id'])
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
				serializer = CargoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='seguridad_social.cargo',id_manipulado=instance.id)
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
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.cargo',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 

# Fin Cargo


# Empleado
	

class EmpleadoSerializer(serializers.HyperlinkedModelSerializer):
	
	empresa = EmpresaSerializer(read_only=True)
	persona_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Persona.objects.all())
	persona = PersonaSerializer(read_only=True)
	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Estado.objects.filter(app='seguridad_social'))
	escolaridad = EscolaridadSerializer(read_only=True)
	escolaridad_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = AEscolaridad.objects.all())
	matricula = MatriculaSerializer(read_only=True)
	matricula_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = AMatricula.objects.all())
	tipo_matricula = TipoSerializer(read_only=True)
	tipo_matricula_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Tipo.objects.filter(app='seguridad_social'), allow_null = True, default=None)
	cargo = CargoSerializer(read_only=True)
	cargo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Cargo.objects.all())
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Empresa.objects.filter(esContratista=True))
	contratista = EmpresaSerializer(read_only=True)
	apto = serializers.BooleanField(default=False)

	class Meta:	
		order_by = True	
		model = Empleado		
		fields=('id','persona','persona_id','fecha_nacimiento','escolaridad','escolaridad_id','contratista','contratista_id',
			'empresa','fecha_tsa','soporte_tsa','matricula','matricula_id','tipo_matricula','tipo_matricula_id',
			'soporte_matricula','estado','estado_id','cargo','cargo_id','hoja_de_vida','apto','observacion','foto','fecha_ingreso', 'tiene_licencia',
			'vencimiento_licencia', 'soporte_licencia', 'foto_publica')

class EmpleadoLiteSerializer(serializers.HyperlinkedModelSerializer):
	persona = PersonaSerializer(read_only=True)
	class Meta:	
		order_by = True	
		model = Empleado		
		fields=('id','persona',)

class EmpleadoLite2Serializer(serializers.HyperlinkedModelSerializer):
    	
	# empresa = EmpresaSerializer(read_only=True)
	# persona_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Persona.objects.all())
	persona = PersonaSerializer(read_only=True)
	estado = EstadoSerializer(read_only=True)
	# estado_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Estado.objects.filter(app='seguridad_social'))
	# escolaridad = EscolaridadSerializer(read_only=True)
	# escolaridad_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = AEscolaridad.objects.all())
	# matricula = MatriculaSerializer(read_only=True)
	# matricula_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = AMatricula.objects.all())
	# tipo_matricula = TipoSerializer(read_only=True)
	# tipo_matricula_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Tipo.objects.filter(app='seguridad_social'), allow_null = True, default=None)
	# cargo = CargoSerializer(read_only=True)
	# cargo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Cargo.objects.all())
	# contratista_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Empresa.objects.filter(esContratista=True))
	contratista = EmpresaSerializer(read_only=True)
	# apto = serializers.BooleanField(default=False)

	class Meta:	
		order_by = True	
		model = Empleado		
		fields=('id','persona', 'estado', 'contratista', 'apto')		

class EmpleadoViewSet(viewsets.ModelViewSet):
	"""
		{sin_paginacion=''}Con este parametro obtenemos todos los registros de la busqueda sin paginar<br>
		{dato=Buscar por todos los campos de texto}<br>
		{contratista_id}<br>
		{estado_id=(Ingreso, Retirado, ReIngreso)}		<br>
		{apto=Tipo Bool} obtiene los empleados aptos o no aptos<br>
		{estudio_personas=Tipo Bool} Obtiene las personas que estan es estudio y a un no han sido asiganadas aun contratista
	"""
	model=Empleado
	queryset = model.objects.all()
	serializer_class = EmpleadoSerializer
	#parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 30
	nombre_modulo='seguridad_social.empleado'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(EmpleadoViewSet, self).get_queryset()
			paginacion = self.request.query_params.get('sin_paginacion', None)
			dato = self.request.query_params.get('dato', None)
			contratista_id = self.request.query_params.get('contratista_id', None)
			estado_id = self.request.query_params.get('estado_id', None)			
			apto = self.request.query_params.get('apto', None)
			estudio_personas = self.request.query_params.get('estudio_personas', None)
			lite = self.request.query_params.get('lite', None)			
			lite2 = self.request.query_params.get('lite2', None)			
			qset=None
			 
			if estudio_personas:
				qset = Q(empresa__id=request.user.usuario.empresa.id)
				if dato:
					qset = qset & (
						Q(persona__nombres__icontains=dato)|
						Q(persona__apellidos__icontains=dato)|
						Q(persona__cedula__icontains=dato)
						)
				if apto is not None:
					apto = True if str(apto) == '1' else False
					if qset:
						qset = qset & (Q(apto=apto))
					else:
						qset = (Q(apto=apto))	
				if qset:	
					qset=qset & (Q(contratista__isnull=True))
				else:
					qset= (Q(contratista__isnull=True))					
				
			else:
				contratistas = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id).values('contrato__contratista__id').distinct()
				empresas_acceso = EmpresaPermiso.objects.filter(empresa__id=request.user.usuario.empresa.id).values('empresa_acceso__id').distinct()
				qset= (Q(contratista__id__in=contratistas) & Q(empresa__id__in=empresas_acceso))
				if dato:
					qset = qset & (
						Q(persona__nombres__icontains=dato)|
						Q(persona__apellidos__icontains=dato)|
						Q(persona__cedula__icontains=dato)
						)									
				if contratista_id:
					if qset:
						qset = qset & (Q(contratista__id=contratista_id))
					else:
						qset = (Q(contratista__id=contratista_id))
				if estado_id:
					if str(estado_id) == '1000':
						qset = qset & (Q(estado__id__in=[5,7,]))					
					else:
						qset = qset & (Q(estado__id=estado_id))								
				if qset:					
					qset=qset & (Q(contratista__isnull=False))
				else:
					qset= (Q(contratista__isnull=False))	
					
			queryset = self.model.objects.filter(qset).order_by('-id')

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite is not None:
						serializer = EmpleadoLiteSerializer(page, many=True, context={'request': request})	
					elif lite2 is not None:
						serializer = EmpleadoLite2Serializer(page, many=True, context={'request': request})		
					else:	
						serializer = self.get_serializer(page, many=True)						
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})
			else:
				if lite is not None:
					serializer = EmpleadoLite2Serializer(queryset, many=True, context={'request': request}) #context=serializer_context
				elif lite2 is not None:
					serializer = EmpleadoLiteSerializer(queryset, many=True, context={'request': request}) #context=serializer_context
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
				empleado = Empleado.objects.filter(persona__id=request.DATA['persona_id'], contratista__id=request.DATA['contratista_id'], empresa__id=request.user.usuario.empresa.id)
				
				if empleado:					
					return Response({'message':'Ya existe esta persona asignada al contratista seleccionado.','success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)						
				else:
					est_empleado = Empleado.objects.filter(persona__id=request.DATA['persona_id'], contratista__isnull=True, empresa__id=request.user.usuario.empresa.id)
					if est_empleado:
						return Response({'message':'La persona que intenta ingresar se encuentra en estudio.','success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)	
				request.DATA['apto'] = True if str(request.DATA['apto']) == '1' else False						
				serializer = EmpleadoSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					
					serializer.save(soporte_tsa=self.request.FILES['soporte_tsa'] if self.request.FILES.get('soporte_tsa') is not None else '', 
						soporte_matricula = self.request.FILES['soporte_matricula'] if self.request.FILES.get('soporte_matricula') is not None else '',
						hoja_de_vida=self.request.FILES['hoja_de_vida'] if self.request.FILES.get('hoja_de_vida') is not None else '',
						foto=self.request.FILES['foto'] if self.request.FILES.get('foto') is not None else '',
						empresa_id=request.user.usuario.empresa.id,persona_id=request.DATA['persona_id'],
						escolaridad_id=request.DATA['escolaridad_id'],contratista_id=request.DATA['contratista_id'],
						matricula_id=request.DATA['matricula_id'],tipo_matricula_id=request.DATA['tipo_matricula_id'] if request.DATA['tipo_matricula_id']!='' else None ,
						estado_id=request.DATA['estado_id'],cargo_id=request.DATA['cargo_id'],
						soporte_licencia=self.request.FILES['soporte_licencia'] if self.request.FILES.get('soporte_licencia') is not None else '')
					
					# Registro de Novedad
					enumEstado=EnumEstadoEmpleado()
					novedad=Novedad(fecha=request.DATA['fecha_ingreso'],empleado_id=serializer.data['id'],estado_id=enumEstado.Ingreso,descripcion='')
					novedad.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.novedad',id_manipulado=novedad.id)
					logs_model.save()	
					
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.empleado',id_manipulado=serializer.data['id'])
					logs_model.save()	
					
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:					
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:				
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				request.DATA['apto'] = True if str(request.DATA['apto']) == '1' else False
				serializer = EmpleadoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					
					# instance.soporte_tsa=self.request.FILES['soporte_tsa'] if self.request.FILES.get('soporte_tsa') is not None else instance.soporte_tsa
					# instance.soporte_matricula = self.request.FILES['soporte_matricula'] if self.request.FILES.get('soporte_matricula') is not None else instance.soporte_matricula
					# instance.hoja_de_vida=self.request.FILES['hoja_de_vida'] if self.request.FILES.get('hoja_de_vida') is not None else instance.hoja_de_vida
					# instance.foto=self.request.FILES['foto'] if self.request.FILES.get('foto') is not None else instance.foto
					# #instance.empresa_id=request.user.usuario.empresa.id,persona_id=request.DATA['persona_id']
					# instance.escolaridad_id=request.DATA['escolaridad_id']
					# contratista_id=request.DATA['contratista_id']
					# instance.matricula_id=request.DATA['matricula_id']
					# instance.tipo_matricula_id=request.DATA['tipo_matricula_id'] if request.DATA['tipo_matricula_id']!='' else None
					# #instance.estado_id=request.DATA['estado_id']
					# instance.cargo_id=request.DATA['cargo_id']
					# instance.tiene_licencia = request.DATA['tiene_licencia']=='1'
					# instance.vencimiento_licencia=request.DATA['vencimiento_licencia'] if request.DATA['vencimiento_licencia']!='' else None
					# instance.soporte_licencia=self.request.FILES['soporte_licencia'] if self.request.FILES.get('soporte_licencia') is not None else instance.soporte_licencia
					# instance.save()

					serializer.save(soporte_tsa=self.request.FILES['soporte_tsa'] if self.request.FILES.get('soporte_tsa') is not None else instance.soporte_tsa, 
						soporte_matricula = self.request.FILES['soporte_matricula'] if self.request.FILES.get('soporte_matricula') is not None else instance.soporte_matricula,
						hoja_de_vida=self.request.FILES['hoja_de_vida'] if self.request.FILES.get('hoja_de_vida') is not None else instance.hoja_de_vida,
						foto=self.request.FILES['foto'] if self.request.FILES.get('foto') is not None else instance.foto,
						empresa_id=instance.empresa.id,
						persona_id=request.DATA['persona_id'],
						escolaridad_id=request.DATA['escolaridad_id'],
						contratista_id=request.DATA['contratista_id'],
						matricula_id=request.DATA['matricula_id'],
						tipo_matricula_id=request.DATA['tipo_matricula_id'] if request.DATA['tipo_matricula_id']!='' else None ,
						estado_id=instance.estado.id if instance.estado else request.DATA['estado_id'],
						cargo_id=request.DATA['cargo_id'],
						soporte_licencia=self.request.FILES['soporte_licencia'] if self.request.FILES.get('soporte_licencia') is not None else instance.soporte_licencia)
					

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.empleado',id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:				
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def destroy(self,request,*args,**kwargs):		
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			self.perform_destroy(instance)

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.empleado',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 


# Fin Empleado

# Novedad

class NovedadSerializer(serializers.HyperlinkedModelSerializer):
	empleado = EmpleadoSerializer(read_only=True)
	empleado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empleado.objects.all())
	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='seguridad_social').filter(estado=True))
	class Meta:
		model = Novedad
		fields=('id','fecha','empleado','empleado_id','estado','estado_id','descripcion','fecha_registro')

								  
								  
class NovedadViewSet(viewsets.ModelViewSet):
	"""
	{dato=}Busca en todos los campos de tipo texto
	{sin_paginacion=}Con este parametro obtenemos todos los registros de la busqueda sin paginar<br>
	{contratista_id=,fecha_inicio=,fecha_final=}Estos tres campos trabajan juntos y obtienen los proveedores	
	"""
	model=Novedad
	queryset = model.objects.all()
	serializer_class = NovedadSerializer
	paginate_by = 10
	nombre_modulo='seguridad_social.novedad'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(NovedadViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)
			contratista_id = self.request.query_params.get('contratista_id', None)
			fecha_inicio = self.request.query_params.get('fecha_inicio', None)
			fecha_final = self.request.query_params.get('fecha_final', None)
			contratistas = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id).values('contrato__contratista__id').distinct()
			qset = (Q(empleado__contratista__id__in=contratistas) & Q(empleado__empresa__id=request.user.usuario.empresa.id))
			if dato:
				qset = qset & (
					Q(empleado__persona__nombres__icontains=dato)|
					Q(empleado__persona__apellidos__icontains=dato)|
					Q(empleado__persona__cedula__icontains=dato)
					)
			if contratista_id or fecha_inicio or fecha_final:
				if contratista_id:
					qset= qset & (Q(empleado__contratista__id=contratista_id))	
				if fecha_inicio and fecha_final:	
					qset=qset & (Q(fecha__range=(fecha_inicio,fecha_final)))

			queryset = self.model.objects.filter(qset)
			
			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True) 
					return self.get_paginated_response({'message':'','success':'ok',
															'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})
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
				serializer = NovedadSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():

					serializer.save(empleado_id=self.request.DATA['empleado_id'],estado_id=self.request.DATA['estado_id'])					
					
					empleado=Empleado.objects.get(id=self.request.DATA['empleado_id'])
					empleado.estado=Estado.objects.get(id=self.request.DATA['estado_id'])
					empleado.save();	

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.empleado',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:				
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = NovedadSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='seguridad_social.empleado',id_manipulado=instance.id)
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
			transaction.savepoint_commit(sid)
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.novedad',id_manipulado=instance.id)
			logs_model.save()
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 


# Fin Novedad

# Planilla

class PlanillaSerializer(serializers.HyperlinkedModelSerializer):
	contratista = EmpresaSerializer(read_only=True)
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.filter(esContratista=True))
	empresa = EmpresaSerializer(read_only=True)	
	class Meta:
		model = Planilla
		fields=('id', 'contratista_id','contratista', 'ano', 'mes', 'fecha_pago', 'soporte', 'fecha_limite', 'empresa', 'estado','estado_planilla_empleado')
								  
								  
class PlanillaViewSet(viewsets.ModelViewSet):
	"""
		{dato=} Busca en todos los campos de tipo texto <br>
		{contratista_id=, ano=} Obtiene la planilla por el campo ano
	"""
	model=Planilla
	queryset = model.objects.all()
	serializer_class = PlanillaSerializer
	paginate_by = 20
	nombre_modulo = 'seguridad_social.planilla'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(PlanillaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			contratista_id = self.request.query_params.get('contratista_id', None)
			ano = self.request.query_params.get('ano', None)
			contratistas = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id).values('contrato__contratista__id').distinct()
			empresas_acceso = EmpresaPermiso.objects.filter(empresa__id=request.user.usuario.empresa.id).values('empresa_acceso__id').distinct()
			qset=(Q(contratista__id__in=contratistas) & Q(empresa__id__in=empresas_acceso))
			if dato:
				qset = qset & Q(contratista__nombre__icontains=dato)
			if contratista_id:
				if qset:
					qset = qset & (Q(contratista__id=contratista_id))
				else:
					qset = Q(contratista__id=contratista_id)
			if ano:
				if qset:					
					qset = qset & (Q(ano=ano))
				else:
					qset = Q(ano=ano)
						
			if qset:				
				queryset = self.model.objects.filter(qset)
			
			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page,many=True)	
				return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})
				
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
				serializer = PlanillaSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():

					serializer.save(contratista_id=request.DATA['contratista_id'],
						empresa_id=request.user.usuario.empresa.id,
						soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else '')					
					
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.planilla',id_manipulado=serializer.data['id'])
					logs_model.save()
					
					transaction.savepoint_commit(sid)					
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:				
				transaction.savepoint_rollback(sid)	
				functions.toLog(e,self.nombre_modulo)	
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:				
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				request.DATA['fecha_pago']= request.DATA.get('fecha_pago') if request.DATA['fecha_pago']!='null' else None;
				serializer = PlanillaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(contratista_id=request.DATA['contratista_id'],
						empresa_id=instance.empresa.id,
						soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte)					
					
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='seguridad_social.planilla',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			self.perform_destroy(instance)

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.planill',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)

			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:			
			transaction.savepoint_rollback(sid)			
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 
class PlanillaEmpleadoSerializer(serializers.HyperlinkedModelSerializer):

	planilla = PlanillaSerializer(read_only=True)
	empleado = EmpleadoSerializer(read_only=True)	

	class Meta:
		model = PlanillaEmpleado
		fields=('id', 'tiene_pago','planilla', 'empleado')

class PlanillaEmpleadoViewSet(viewsets.ModelViewSet):
	"""
		{dato=} Busca en todos los campos de tipo texto <br>
		{contratista_id=, ano=} Obtiene la planilla por el campo ano
	"""
	model=PlanillaEmpleado
	queryset = model.objects.all()
	serializer_class = PlanillaEmpleadoSerializer
	paginate_by = 10
	nombre_modulo = 'seguridad_social.planilla_empleado'		

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
	

	@transaction.atomic			
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			self.perform_destroy(instance)

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.planilla_empleado',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)

			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:			
			transaction.savepoint_rollback(sid)			
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 
# Fin planilla

# Correo Contratista

class CorreoContratistaSerializer(serializers.HyperlinkedModelSerializer):
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Empresa.objects.filter(esContratista=True))
	contratista = EmpresaSerializer(read_only=True)
	class Meta:
		model = CorreoContratista
		fields=('id', 'correo','contratista_id', 'contratista',)
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'contratista_id' , 'correo',),
				message=('El correo ya existe para este contratista.')
				)]
								  
								  
class CorreoContratistaViewSet(viewsets.ModelViewSet):
	"""
	"""
	model=CorreoContratista
	queryset = model.objects.all()
	serializer_class = CorreoContratistaSerializer
	# parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo = 'seguridad_social.correo_contratista'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CorreoContratistaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			contratista_id = self.request.query_params.get('contratista_id', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)
			contratistas = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id).values('contrato__contratista__id').distinct()
			qset=(Q(contratista__id__in=(contratistas)))

			if dato:
				qset=qset & (Q(contratista__nombre__icontains=dato) |
						Q(correo__icontains=dato))	
			if contratista_id:
				qset= qset & (Q(contratista__id=contratista_id))
										
			queryset = self.model.objects.filter(qset)	
						
			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})
			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})	
		
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = CorreoContratistaSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(contratista_id=request.DATA['contratista_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.correo_contratista',id_manipulado=serializer.data['id'])
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
					return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:				
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = CorreoContratistaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(contratista_id=request.DATA['contratista_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='seguridad_social.correo_contratista',id_manipulado=instance.id)
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
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.correo_contratista',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 

# Fin Correo Contratista


#Vistas y servicios

def empleados(request):	

		qsContratistas = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id).order_by('contrato__contratista__nombre').values('contrato__contratista__id', 'contrato__contratista__nombre').distinct()
		qsEstadosNovedad = Estado.objects.filter(app='seguridad_social')				
		return render(request, 'empleado/empleado.html',
			{'contratistas':qsContratistas,'estado_novedad':qsEstadosNovedad, 'model':'empleado','app':'seguridad_social'},
			)

def crear_empleado(request):
		qsContratistas = Empresa.objects.filter(esContratista=True)
		qsEscolaridad = AEscolaridad.objects.all()
		qsMatriculas = AMatricula.objects.all()
		#qsCargos = Cargo.objects.all()	
		qsTipos = Tipo.objects.filter(app='seguridad_social')	
		qsEstadosNovedad = Estado.objects.filter(app='seguridad_social')		
		return render(request, 'empleado/crear_empleado.html',
			{'contratistas':qsContratistas, 'escolaridades':qsEscolaridad, 'matriculas':qsMatriculas,
			 'tipos':qsTipos,'estado_novedad':qsEstadosNovedad,'model':'empleado','app':'seguridad_social'},
			)		

def editar_empleado(request, id):
		qsContratistas = Empresa.objects.filter(esContratista=True)
		qsEscolaridad = AEscolaridad.objects.all()
		qsMatriculas = AMatricula.objects.all()
		#qsCargos = Cargo.objects.all()
		qsTipos = Tipo.objects.filter(app='seguridad_social')	
		qsEstadosNovedad = Estado.objects.filter(app='seguridad_social')		
		return render(request, 'empleado/editar_empleado.html',
			{'id':id,'contratistas':qsContratistas, 'escolaridades':qsEscolaridad, 'matriculas':qsMatriculas,
			 'tipos':qsTipos,'estado_novedad':qsEstadosNovedad,'model':'empleado','app':'seguridad_social'},
			)				

def completar_informacion_empleados(request,empleado_id):
		qsContratistas = Empresa.objects.filter(esContratista=True)
		qsEscolaridad = AEscolaridad.objects.all()
		qsMatriculas = AMatricula.objects.all()
		#qsCargos = Cargo.objects.filter(empresa_id=request.user.usuario.empresa.id)		
		qsTipos = Tipo.objects.filter(app='seguridad_social')	
		qsEstadosNovedad = Estado.objects.filter(app='seguridad_social')	
		
		return render(request, 'empleado/completar_informacion_empleados.html',
			{'contratistas':qsContratistas, 'escolaridades':qsEscolaridad, 
			'matriculas':qsMatriculas, 'tipos':qsTipos,'empleado_id':empleado_id,
			'model':'empleado','app':'seguridad_social'},
			)

@transaction.atomic
def actualizar_empleado_acto(request):
	sid = transaction.savepoint()
	try:		
		respuesta=json.loads(request.POST['_content'])
		objeto=Empleado.objects.get(id=respuesta['id'])		
		objeto.apto=respuesta['apto']
		objeto.observacion=respuesta['observacion']		
		objeto.save()
		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='seguridad_social.empleado',id_manipulado=request.GET['id'])
		logs_model.save()
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok',
				'data':''})
	except Exception as e:		
		transaction.savepoint_rollback(sid)		
		functions.toLog(e,'seguridad_social.actualizar_empleado_acto')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	

def planilla(request):
		# querysetCont = Empresa.objects.filter(esContratista=True)						
		qsContratistas = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id).order_by('contrato__contratista__nombre').values('contrato__contratista__id', 'contrato__contratista__nombre', 'contrato__contratista__nit').distinct()
		return render(request, 'empleado/planilla.html',
			{'contratistas':qsContratistas,'model':'planilla','app':'seguridad_social'},)


def obtener_meses_planilla(request):
	try:
		
		contratista_id=request.GET['contratista_id']
		ano=request.GET['ano']
		qset = (Q(contratista__id=contratista_id) & Q(ano=ano) & Q(empresa__id=request.user.usuario.empresa.id))
		planillas=Planilla.objects.filter(qset).filter()
		
		listaMeses=[]

		if planillas:
			for x in range(1,13):
				valido=buscar_mes(planillas,x)				
				if valido==False:	
					item={						
						'mes':x 
					}
					listaMeses.append(item)	
		else:
			listaMeses=[{'mes':1},{'mes':2},{'mes':3},{'mes':4},{'mes':5},{'mes':6},
				{'mes':7},{'mes':8},{'mes':9},{'mes':10},{'mes':11},{'mes':12}]

		return JsonResponse({'message':'','success':'ok','data':listaMeses})
	except Exception as e:
		functions.toLog(e,'seguridad_social.obtener_meses_planilla')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	

def buscar_mes(lista, valor):	
	for x in list(lista):		
		if x.mes==valor:
			return True

	return False		

@transaction.atomic
def guardar_panilla_empleado(request):
	sid = transaction.savepoint()
	try:
		cursor = connection.cursor()
		resultado=json.loads(request.POST['_content'])			
		lista=resultado['lista']
		# planillaEmpleado=PlanillaEmpleado.objects.filter(planilla__id=resultado['planilla_id'])				
		# planillaEmpleado.delete()

		for item in lista:
			planillaEmpleado=PlanillaEmpleado.objects.filter(planilla__id=resultado['planilla_id'], empleado__id=item['id']).first()
			if planillaEmpleado:
				planillaEmpleado.tiene_pago = item['tiene_pago']
				planillaEmpleado.save()			
				# logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='seguridad_social.planilla_empleado',id_manipulado=planillaEmpleado.id)
				# logs_model.save()
			else:
				planillaEmpleado=PlanillaEmpleado(planilla_id=resultado['planilla_id'], empleado_id=item['id'], tiene_pago=item['tiene_pago'])
				planillaEmpleado.save()	
				# logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.planilla_empleado',id_manipulado=planillaEmpleado.id)
				# logs_model.save()
		
		if resultado['notificar']=='true':
			
			ruta = settings.STATICFILES_DIRS[0]
			rutaPapelera = ruta + '\papelera'

			planilla = Planilla.objects.get(pk=resultado['planilla_id'])
			correo_contratista = CorreoContratista.objects.filter(contratista__id=planilla.contratista.id)
			if correo_contratista:
				correo_envio=''	
				for cr in correo_contratista:
					correo_envio= correo_envio + cr.correo + ';'

				
				cursor.callproc('[dbo].[seguridad_social_responsable_proyecto_contratista]',[planilla.contratista.id,7,planilla.empresa.id])		
				columns = cursor.description 
				responsables_proyectos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]					
				con_copias = ''
				for r in responsables_proyectos:
					con_copias=con_copias + r['correo']+';'

				correo_envio=correo_envio[:-1]	
				con_copias=con_copias[:-1]	

				qset = (Q(planilla__id=resultado['planilla_id']) & (Q(tiene_pago__isnull=True) | Q(tiene_pago=False)))
				planillaEmpleadoNoReportados=PlanillaEmpleado.objects.filter(qset)

				qset2 = (Q(planilla__id=resultado['planilla_id']) & Q(tiene_pago=True))
				planillaEmpleadoReportados=PlanillaEmpleado.objects.filter(qset2)
				
				if planillaEmpleadoNoReportados.count()>0:
					unique_filename = uuid.uuid4()
					nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
					workbook = xlsxwriter.Workbook(nombre_archivo)
					worksheet = workbook.add_worksheet()

					format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
					format2=workbook.add_format({'border':1})
					format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
					
					worksheet.write('A1','Cedula', format1)	
					worksheet.write('B1','Nombres', format1)
					worksheet.write('C1','Apellidos', format1)
					worksheet.write('D1','Escolaridad', format1)
					worksheet.write('E1','Cargo', format1)	

					worksheet.set_column('A:A',30)
					worksheet.set_column('B:B',30)
					worksheet.set_column('C:C',30)
					worksheet.set_column('D:D',30)
					worksheet.set_column('E:E',30)
					row=1
					col=0
					for e in planillaEmpleadoNoReportados:					
						worksheet.write(row,col,e.empleado.persona.cedula ,format2)
						worksheet.write(row,col+1,e.empleado.persona.nombres ,format2)
						worksheet.write(row,col+2,e.empleado.persona.apellidos ,format2)
						worksheet.write(row,col+3,e.empleado.escolaridad.nombre ,format2)						
						worksheet.write(row,col+4,e.empleado.cargo.nombre ,format2)
						row +=1

					workbook.close()
					contenido = crear_contenido_planilla_empleado(request, planilla, 1)
					mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=correo_envio,
						asunto='Petición: Pago y reporte de seguridad social - Personal no reportado en la planilla.',
						contenido=contenido,
						tieneAdjunto=True,
						adjunto=nombre_archivo,
						appLabel='seguridad_social',
						copia=con_copias
						)
					mail.save()									
					sendAsyncFullMail(mail)

				if planillaEmpleadoReportados.count()>0:
					unique_filename = uuid.uuid4()
					nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
					workbook = xlsxwriter.Workbook(nombre_archivo)
					worksheet = workbook.add_worksheet()

					format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
					format2=workbook.add_format({'border':1})
					format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
					
					worksheet.write('A1','Cedula', format1)	
					worksheet.write('B1','Nombres', format1)
					worksheet.write('C1','Apellidos', format1)
					worksheet.write('D1','Escolaridad', format1)
					worksheet.write('E1','Cargo', format1)	

					worksheet.set_column('A:A',30)
					worksheet.set_column('B:B',30)
					worksheet.set_column('C:C',30)
					worksheet.set_column('D:D',30)
					worksheet.set_column('E:E',30)
					row=1
					col=0
					for e in planillaEmpleadoReportados:					
						worksheet.write(row,col,e.empleado.persona.cedula ,format2)
						worksheet.write(row,col+1,e.empleado.persona.nombres ,format2)
						worksheet.write(row,col+2,e.empleado.persona.apellidos ,format2)
						worksheet.write(row,col+3,e.empleado.escolaridad.nombre ,format2)						
						worksheet.write(row,col+4,e.empleado.cargo.nombre ,format2)
						row +=1

					workbook.close()
					contenido = crear_contenido_planilla_empleado(request, planilla, 2)
					mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=correo_envio,
						asunto='Peticion: Pago y reporte de seguridad social - Personal reportado en la planilla.',
						contenido=contenido,
						tieneAdjunto=True,
						adjunto=nombre_archivo,
						appLabel='seguridad_social',
						copia=con_copias
						)
					mail.save()									
					sendAsyncFullMail(mail)

		transaction.savepoint_commit(sid)			
		if resultado['notificar']=='true':
			return JsonResponse({'message':'Los empleados seleccionados fueron relacionados y notificados satisfactoriamente.','success':'ok','data':''})
		return JsonResponse({'message':'Los empleados seleccionados fueron relacionados satisfactoriamente.','success':'ok','data':''})
	
	except Exception as e:		
		transaction.savepoint_rollback(sid)
		functions.toLog(e, 'seguridad_social.guardar_panilla_empleado')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

def crear_contenido_planilla_empleado(request, planilla, opcion):
	meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
	if opcion == 1:	# persona no autorizado		
		contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
		contenido = """Se&ntilde;or Usuario(a) {0}<br/><br/>	
						Nos permitimos comunicarle, que el personal relacionado en el adjunto no se encuentra reportado en 
						la planilla recibida correspondiente al periodo {1} - {2}, motivo por el cual, 
						dicho personal no est&aacute; autorizado para continuar con las actividades en campo.
						<br><br><br>
						No siendo m&aacute;s la presente quedamos atentos.
						<br><br><br>
						No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>
						<br><br>
						Si presenta alguna inquietud favor comunicarse con la firma interventora {3}
						<br/><br/><br/>
						Gracias,<br/><br/><br/>
						Soporte SININ<br/>soporte@sinin.co
						""".format(planilla.contratista.nombre, meses[planilla.mes-1], planilla.ano, planilla.empresa.nombre)
	if opcion == 2:	# persona autorizado	
		contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
		contenido = """Se&ntilde;or Usuario(a) {0}<br/><br/>	
						Nos permitimos comunicarle, que el personal relacionado en el adjunto se encuentra reportado en 
						la planilla recibida correspondiente al periodo {1} - {2}, motivo por el cual, 
						dicho personal est&aacute; autorizado para continuar con las actividades en campo.
						<br><br><br>
						No siendo m&aacute;s la presente quedamos atentos.
						<br><br><br>
						No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>
						<br><br>
						Si presenta alguna inquietud favor comunicarse con la firma interventora {3}
						<br/><br/><br/>
						Gracias,<br/><br/><br/>
						Soporte SININ<br/>soporte@sinin.co
					""".format(planilla.contratista.nombre, meses[planilla.mes-1], planilla.ano, planilla.empresa.nombre)

	return contenido;

@login_required	
@transaction.atomic
def agregar_empleado_a_planilla(request):
	sid = transaction.savepoint()
	try:
		resultado=json.loads(request.POST['_content'])
		listaEmpleados = resultado['lista_empleado']

		for empleado_id in listaEmpleados:			
			planillaEmpleado=PlanillaEmpleado.objects.filter(planilla__id=resultado['planilla_id'],empleado__id=empleado_id)		
			if not planillaEmpleado.exists():			
				p=PlanillaEmpleado(planilla_id=resultado['planilla_id'], empleado_id=empleado_id, tiene_pago=False)
				p.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.planilla_empleado',id_manipulado=p.id)
				logs_model.save()

			
		# querySet.empleado.clear()
		# querySet.empleado.add(*lista)		
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'Los empleado fueron agregados a la planilla satisfactoriamente.','success':'ok','data':''})
	except Exception as e:		
		transaction.savepoint_rollback(sid)
		functions.toLog(e, 'seguridad_social.agregar_empleado_a_planilla')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

@login_required
@transaction.atomic
def eliminar_planilla(request):
	sid = transaction.savepoint()
	try:
		resultado=json.loads(request.POST['_content'])

		for id in resultado['lista']:
			planilla=Planilla.objects.get(pk=id)
			planilla.delete()	

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.planilla',id_manipulado=planilla.id)
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El(Los) registro(s) fueron eliminado satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:		
		transaction.savepoint_rollback(sid)		
		functions.toLog(e, 'seguridad_social.eliminar_planilla')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

def consultar_planilla_empleado(request):
	cursor = connection.cursor()
	try:
		planilla_id=request.GET['planilla_id']
		cursor.callproc('[dbo].[seguridad_social_consultar_planilla_empleado]', [planilla_id,])
		columns = cursor.description 
		empleados = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]					
		# result_set = cursor.fetchall()
		lista=[]
		for x in list(empleados):
			item={
			'id':x['id'],
			'cedula':x['cedula'],
			'nombres':x['nombres'],
			'apellidos':x['apellidos'],
			'tiene_pago':x['tiene_pago']>0,
			'planilla_empleado_id':x['planilla_empleado_id']
			}
			lista.append(item)
		return JsonResponse({'message':'','success':'ok','data':lista})
	except Exception as e:
		functions.toLog(e, 'seguridad_social.consultar_planilla_empleado')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

def consultar_empleados_por_contratista(request):
	cursor = connection.cursor()
	try:
		planilla_id=request.GET['planilla_id']
		contratista_id=request.GET['contratista_id']
		criterio=request.GET.get('criterio', '')
		cursor.callproc('[dbo].[seguridad_social_consulta_empleados]', [contratista_id,planilla_id,criterio,])
		#if cursor.return_value == 1:
		result_set = cursor.fetchall()
		lista=[]
		for x in list(result_set):
			item={
			'id':x[0],
			'cedula':x[1],
			'nombres':x[2],
			'apellidos':x[3]			
			}
			lista.append(item)
		return JsonResponse({'message':'','success':'ok','data':lista})
	except Exception as e:
		functions.toLog(e, 'seguridad_social.consultar_empleados_por_contratista')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

def planilla_empleado(request,planilla_id,contratista_id):
	planilla =Planilla.objects.get(pk=planilla_id)	
	return render(request, 'empleado/planilla_empleado.html',
		{'planilla':planilla,'planilla_id':planilla_id,'contratista_id':contratista_id},
		)

def novedades(request):
	querysetCont = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id).order_by('contrato__contratista__nombre').values('contrato__contratista__id', 'contrato__contratista__nombre', 'contrato__contratista__nit').distinct()
	return render(request, 'empleado/novedades.html',
		{'contratistas':querysetCont,'model':'novedad','app':'seguridad_social'},)	

def consultar_empresa(request):
	cursor = connection.cursor()
	try:
		empresa_id=request.user.usuario.empresa.id
		dato=request.GET['dato']
		cursor.callproc('[dbo].[seguridad_social_consultar_empresa]', [empresa_id,dato,])
		#if cursor.return_value == 1:
		result_set = cursor.fetchall()
		lista=[]
		for x in list(result_set):
			item={
			'id':x[0],
			'nombre':x[1]			
			}
			lista.append(item)
		return JsonResponse({'message':'','success':'ok','data':lista})
	except Exception as e:
		functions.toLog(e,'seguridad_social.consultar_empresa')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

def consultar_empresa_permisos(request):
	cursor = connection.cursor()
	try:
		empresa_id=request.user.usuario.empresa.id
		dato=request.GET['dato']
		cursor.callproc('[dbo].[seguridad_social_consultar_empresa_permisos]', [empresa_id,dato,])
		#if cursor.return_value == 1:
		result_set = cursor.fetchall()
		lista=[]
		for x in list(result_set):
			item={
			'id':x[0],
			'id_empresa':x[1],	
			'empresa':x[2],			
			}
			lista.append(item)
		return JsonResponse({'message':'','success':'ok','data':lista})
	except Exception as e:
		functions.toLog(e,'seguridad_social.consultar_empresa_permisos')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

@transaction.atomic
def guardar_empresa_permisos(request):
	sid = transaction.savepoint()
	try:
		
		resultado=json.loads(request.POST['_content'])		
		lista=resultado['lista_empresas']

		for x in lista:
			ee=EmpresaPermiso(empresa_id=request.user.usuario.empresa.id, empresa_acceso_id=x)	
			ee.save()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.empresa_permiso',id_manipulado=x)
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'La(s) empresa(s) fueron agragadas satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:		
		transaction.savepoint_rollback(sid)
		functions.toLog(e, 'seguridad_social.guardar_empresa_permisos')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

@transaction.atomic
def eliminar_empresa_permisos(request):
	sid = transaction.savepoint()
	try:
		
		resultado=json.loads(request.POST['_content'])		
		lista=resultado['lista']

		for x in lista:
			ee=EmpresaPermiso.objects.get(pk=x)	
			ee.delete()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.empresa_permiso',id_manipulado=x)
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'La(s) empresa(s) fueron eliminadas satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:		
		transaction.savepoint_rollback(sid)
		functions.toLog(e,'seguridad_social.eliminar_empresa_permisos')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

def empresa_permisos(request):
	return render(request, 'empleado/empresa_permisos.html',
		{'model':'empresa_permiso','app':'seguridad_social'},
		)

def estudio_personas(request):	
	return render(request, 'empleado/estudio_personas.html',
		{'model':'empleado','app':'seguridad_social'},
		)

	#return render(request, 'empleado/estudio_personas.html',)

def consultar_requerimientos_empleado(request):
	cursor = connection.cursor()
	try:
		
		empleado_id=request.GET['empleado_id']
		cursor.callproc('[dbo].[seguridad_social_consultar_requerimientos_empleado]', [empleado_id,])
		#if cursor.return_value == 1:
		result_set = cursor.fetchall()
		lista=[]
		for x in list(result_set):
			valor=x[2] if x[2]>0 else x[3] if x[3]>0 else x[4]
			item={
			'requerimiento_id':x[0],
			'requerimiento':x[1],	
			'cumple':x[2],				
			'no_cumple':x[3],
			'no_aplica':x[4],
			'requerimiento_valor_id': str(valor),		
			
			}
			lista.append(item)
		return JsonResponse({'message':'','success':'ok','data':lista})
	except Exception as e:
		functions.toLog(e, 'seguridad_social.consultar_requerimientos_empleado')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

@transaction.atomic
def guardar_estudio_personas(request):
	sid = transaction.savepoint()
	try:	
		
		persona_id=request.POST['persona_id']
		fecha_nacimiento=request.POST['fecha_nacimiento']
		observacion=request.POST['observacion']
		apto=True if int(request.POST['apto'])==1 else False
		foto=request.FILES['foto'] if request.FILES.get('foto') is not None else ''
		lista=json.loads(request.POST['lista'])
		
		ee=Empleado(persona_id=persona_id,fecha_nacimiento=fecha_nacimiento,
					observacion=observacion,foto=foto,apto=apto, empresa_id=request.user.usuario.empresa.id)
		ee.save()

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='seguridad_social.empleado',id_manipulado=ee.id)
		logs_model.save()

		#guardamos requerimientos
		for x in lista:
			r=ZRequerimientosEmpleados(empleado_id=ee.id,requerimiento_id=x['requerimiento_id'],requerimiento_valor_id=x['requerimiento_valor_id'])
			r.save()
			
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro fue guardado satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:		
		transaction.savepoint_rollback(sid)		
		functions.toLog(e,'seguridad_social.guardar_estudio_personas')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

@transaction.atomic
def actualizar_estudio_personas(request):
	sid = transaction.savepoint()
	try:

		id=request.POST['id']			
		persona_id=request.POST['persona_id']
		fecha_nacimiento=request.POST['fecha_nacimiento']
		observacion=request.POST['observacion']
		apto=request.POST['apto']
		lista=json.loads(request.POST['lista'])

		ee=Empleado.objects.get(pk=id)
		ee.persona_id=persona_id
		ee.fecha_nacimiento=fecha_nacimiento
		ee.observacion=observacion
		ee.foto=request.FILES['foto'] if request.FILES.get('foto') is not None else ee.foto
		ee.apto=apto
		
		ee.save()

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='seguridad_social.empleado',id_manipulado=ee.id)
		logs_model.save()

		ZRequerimientosEmpleados.objects.filter(empleado__id=id).delete()
		#guardamos requerimientos
		for x in lista:
			r=ZRequerimientosEmpleados(empleado_id=ee.id,requerimiento_id=x['requerimiento_id'],requerimiento_valor_id=x['requerimiento_valor_id'])
			r.save()
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro fue actualizado satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:		
		transaction.savepoint_rollback(sid)	
		functions.toLog(e, 'seguridad_social.actualizar_estudio_personas')	
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

@api_view(['GET',])
def consultar_contratistas(request):
	try:
		qsContratistas = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id).order_by('contrato__contratista__nombre').values('contrato__contratista__id', 'contrato__contratista__nombre', 'contrato__contratista__nit').distinct()
		lista = []
		for row in qsContratistas:
			lista.append({
		 			'id': row['contrato__contratista__id'],
		 			'nombre': row['contrato__contratista__nombre'],
					'nit': row['contrato__contratista__nit']
				}) 
		return Response({'message':'','success':'ok','data': lista})
	except Exception as e:
		return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)	

#exportar a excel
def exportar_empleados(request):
	# try:
		
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="Listado-de-personal.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Contratista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
						
		dato = request.GET.get('dato', None)
		contratista_id = request.GET.get('contratista_id', None)
		estado_id = request.GET.get('estado_id', None)		
		apto = request.GET.get('apto', None)
		estudio_personas = request.GET.get('estudio_personas', None)
		
		qset=None
		if estudio_personas:
			if dato:
				qset = (
					Q(persona__nombres__icontains=dato)|
					Q(persona__apellidos__icontains=dato)|
					Q(persona__cedula__icontains=dato)
					)
			if apto:
				if qset:
					qset = qset & (Q(apto=apto))
				else:
					qset = (Q(apto=apto))	
			if qset:	
				qset=qset & (Q(contratista__isnull=True))
			else:
				qset= (Q(contratista__isnull=True))	
			
		else:				
			if dato or contratista_id or estado_id:
				qset = (~Q(id=0))
				if contratista_id:
					qset = qset & (
						Q(contratista__id=contratista_id)					
					)
				if estado_id:
					if str(estado_id) == '1000':
						qset = qset & (Q(estado__id__in=[5,7,]))	
					else:
						qset = qset & (
							Q(estado__id=estado_id)					
						)
				if dato:
					qset = qset & (
						Q(persona__nombres__icontains=dato)|
						Q(persona__apellidos__icontains=dato)|
						Q(persona__cedula__icontains=dato)
					)			
			
			if qset:					
				qset=qset & (Q(contratista__isnull=False))
			else:
				qset= (Q(contratista__isnull=False))	
			
		
		empleados = Empleado.objects.filter(qset).order_by('-id')	

		worksheet.write('A1', 'Cedula', format1)
		worksheet.write('B1', 'Apellidos', format1)
		worksheet.write('C1', 'Nombres', format1)
		worksheet.write('D1', 'Telefono', format1)
		worksheet.write('E1', 'Correo', format1)
		
		if estudio_personas is None or estudio_personas==False:		
			worksheet.write('F1', 'Cargo', format1)
			worksheet.write('G1', 'STA', format1)	
			worksheet.write('H1', 'Matricula', format1)

		worksheet.set_column('A:A', 18)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 18)
		worksheet.set_column('E:E', 24)
		worksheet.set_column('F:F', 18)
		worksheet.set_column('G:G', 18)
		worksheet.set_column('H:H', 18)

		row=1
		col=0
		
		for emp in empleados:
			worksheet.write(row,col  ,emp.persona.cedula ,format2)
			worksheet.write(row,col+1,emp.persona.apellidos ,format2)
			worksheet.write(row,col+2,emp.persona.nombres ,format2)
			worksheet.write(row,col+3,emp.persona.telefono ,format2)
			worksheet.write(row,col+4,emp.persona.correo ,format2)
			
			if estudio_personas is None or estudio_personas==False:	
				worksheet.write(row,col+5,emp.cargo.nombre if emp.cargo is not None else '',format2)
				worksheet.write(row,col+6,emp.fecha_tsa ,format2)	
				worksheet.write(row,col+7,emp.matricula.nombre if emp.matricula is not None else '' ,format2)
			row +=1
		
		workbook.close()
		return response
	# except Exception as e:
	# 	print(e)

def exportar_planilla(request):
	# try:
		
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="planilla-empleados.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Lista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})

		meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
		
		dato = request.GET.get('dato', None)
		contratista_id = request.GET.get('contratista_id', None)
		ano = request.GET.get('ano', None)
		qset=None
		if contratista_id and ano:
			qset = (
				Q(contratista__id=contratista_id)
				)
			qset = qset & (
				Q(ano=ano)
				)

		if qset:				
			planillas = Planilla.objects.filter(qset)
		else:		
			planillas = Planilla.objects.all()		
		
		worksheet.write('A1', 'Mes', format1)
		worksheet.write('B1', 'Fecha Limite', format1)
		worksheet.write('C1', 'Fecha de Pago', format1)
		worksheet.write('D1', 'Estado', format1)
		

		worksheet.set_column('A:A', 18)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 22)
		
		row=1
		col=0
		
		for plan in planillas:			
			worksheet.write(row,col  ,meses[plan.mes-1] ,format2)
			worksheet.write(row,col+1,plan.fecha_limite ,format_date)
			worksheet.write(row,col+2,plan.fecha_pago ,format_date)
			worksheet.write(row,col+3,plan.estado(),format2)
					
			row +=1
		
		workbook.close()
		return response
	# except Exception as e:
	# 	print(e)		

def exportar_novedades(request):
	# try:
		
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="Listado-de-novedades.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Lista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
				
		dato = request.GET.get('dato', None)		
		contratista_id = request.GET.get('contratista_id', None)
		fecha_inicio = request.GET.get('fecha_inicio', None)
		fecha_final = request.GET.get('fecha_final', None)
		qset=None
		if dato:
			qset = (
				Q(empleado__persona__nombres__icontains=dato)|
				Q(empleado__persona__apellidos__icontains=dato)|
				Q(empleado__persona__cedula__icontains=dato)
				)
		elif contratista_id or fecha_inicio or fecha_final:
			if contratista_id:
				qset=(Q(empleado__contratista__id=contratista_id))	
			if fecha_inicio and fecha_final:
				qset=qset & (Q(fecha__range=(fecha_inicio,fecha_final)))
		
		novedades=None			
		if qset:			
			novedades = Novedad.objects.filter(qset)
		else:
			novedades = Novedad.objects.all()

		worksheet.write('A1', 'Apellidos', format1)
		worksheet.write('B1', 'Nombres', format1)
		worksheet.write('C1', 'Fecha', format1)
		worksheet.write('D1', 'Tipo', format1)
		worksheet.write('E1', 'Descripcion', format1)		

		worksheet.set_column('A:A', 18)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 22)
		worksheet.set_column('E:E', 22)
		
		row=1
		col=0
		
		for nov in novedades:
			
			worksheet.write(row,col  ,nov.empleado.persona.apellidos ,format2)
			worksheet.write(row,col+1,nov.empleado.persona.nombres ,format_date)
			worksheet.write(row,col+2,nov.fecha ,format_date)
			worksheet.write(row,col+3,nov.estado.nombre,format2)
			worksheet.write(row,col+4,nov.descripcion,format2)					
			row +=1
		
		workbook.close()
		return response
	# except Exception as e:
	# 	print(e)		

# Descargo - listado de Empleados con seguridad Social Paga
def listEmpleadosSeguridadSocialPaga(request):
	try:
		id_contratista=request.GET['id_contratista']

		serializer_context = {
			'request': request,
		}

		fecha = date.today()

		qset=(~Q(id=0))

		if id_contratista:
			# qset = qset &(Q(empleado__contratista_id=id_contratista) 
			# 							& Q(tiene_pago=1)
			# 							& Q(planilla__mes=str(fecha.month))
			# 							& Q(planilla__ano=str(fecha.year)) )
			qset = qset &(Q(contratista__id=id_contratista)											
							& Q(mes=str(fecha.month))
							& Q(ano=str(fecha.year)))	

		planilla = Planilla.objects.filter(qset)
		if planilla:
			planilla = planilla.first()
			if planilla.estado() != EnumEstadoPlanilla.Vencida:	
				qset = (Q(contratista__id=id_contratista)
						& Q(estado__id__in=[5,7,]))
				queryset = Empleado.objects.filter(qset).values('id', 'persona__nombres', 'persona__apellidos')
		else:
			queryset = []		
		# queryset = model_contrato.sub_contratista.filter(qset).values('id', 'nit', 'nombre')
		# else:
		# 	# print "jj"
		# 	model_contrato = Contrato.objects.get(pk=id_contrato)
		# 	queryset = model_contrato.sub_contratista.all().values('id', 'nit', 'nombre')
		# 	#queryset = model_contrato.sub_contratista.felter(empresa__nombre__icontains=dato, empresa__nit__icontains=dato).values('id', 'nit', 'nombre')

		# listContratante = EmpleadoSerializer(queryset, many=True, context=serializer_context).data
		# listContratante = PlanillaEmpleadoSerializer(queryset, many=True, context=serializer_context).data

		return JsonResponse({'message':'','success':'ok','data':list(queryset)})
	except Exception as e:
		functions.toLog(e,'seguridad_social.listEmpleadosSeguridadSocialPaga')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})

def informe(request):
	return render(request, 'empleado/informe.html',)
	
def exportar_informe(request):
	cursor = connection.cursor()
	# try:
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="Informe-empleados.xls"'

	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Lista')
	format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
	format2=workbook.add_format({'border':1})
	format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
	
	worksheet.write('A1','Contratista', format1)
	worksheet.write('B1','Cedula', format1)
	worksheet.write('C1','Nombres', format1)
	worksheet.write('D1','Apellidos', format1)
	worksheet.write('E1','Escolaridad', format1)
	worksheet.write('F1','Cargo', format1)
	worksheet.write('G1','Apto', format1)
	worksheet.write('H1','Estado', format1)
	worksheet.write('I1','Fecha de Ingreso', format1)
	worksheet.write('J1','Fecha de Retiro', format1)
	worksheet.write('K1','vigencia Planilla', format1)
	worksheet.write('L1','Tiene Cert. Trabajo en altura', format1)
	worksheet.write('M1','Fecha de Cert. Trabajo en altura', format1)
	worksheet.write('N1','Tiene Cert. Conte / M.P.', format1)
	worksheet.write('O1','Tiene Hoja de Vida', format1)	
	worksheet.write('P1','Tiene Licencia de Conduccion', format1)		
	worksheet.write('Q1','Fecha Vencimiento de Licencia de Conduccion', format1)		

	worksheet.set_column('A:A', 18)
	worksheet.set_column('B:B', 18)
	worksheet.set_column('C:C', 18)
	worksheet.set_column('D:D', 18)
	worksheet.set_column('E:E', 18)
	worksheet.set_column('F:F', 18)
	worksheet.set_column('G:G', 18)
	worksheet.set_column('H:H', 18)
	worksheet.set_column('I:I', 18)
	worksheet.set_column('J:J', 18)
	worksheet.set_column('K:K', 18)
	worksheet.set_column('L:L', 18)
	worksheet.set_column('M:M', 18)
	worksheet.set_column('N:N', 18)
	worksheet.set_column('O:O', 18)
	worksheet.set_column('P:P', 45)
	worksheet.set_column('Q:Q', 50)
	
	row=1
	col=0
	
	mes=request.GET['mes']
	ano=request.GET['ano']	
	empresa_id=request.user.usuario.empresa.id	
	cursor.callproc('[dbo].[seguridad_social_informe]', [mes,ano,empresa_id,])
	result_set = cursor.fetchall()
	
	for r in list(result_set):			
		worksheet.write(row,col,r[0] ,format2)
		worksheet.write(row,col+1,r[1] ,format2)
		worksheet.write(row,col+2,r[2] ,format2)
		worksheet.write(row,col+3,r[3] ,format2)
		worksheet.write(row,col+4,r[4] ,format2)
		worksheet.write(row,col+5,r[5] ,format2)
		worksheet.write(row,col+6,r[6] ,format2)
		worksheet.write(row,col+7,r[7] ,format2)
		worksheet.write(row,col+8,r[8] ,format_date)
		worksheet.write(row,col+9,r[9] ,format_date)
		worksheet.write(row,col+10,r[10] ,format_date)
		worksheet.write(row,col+11,r[11] ,format2)
		worksheet.write(row,col+12,r[12] ,format_date)
		worksheet.write(row,col+13,r[13] ,format2)
		worksheet.write(row,col+14,r[14] ,format2)	
		worksheet.write(row,col+15,r[15] ,format2)	
		worksheet.write(row,col+16,r[16] ,format_date)					
		row +=1
	
	workbook.close()
	return response
	# except Exception as e:
	# 	print(e)

@login_required
def correos_contratista(request):	
	qsContratistas = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id).values('contrato__contratista__id', 'contrato__contratista__nombre').distinct()					
	return render(request, 'empleado/correos_contratista.html',
			{'contratistas':qsContratistas, 'model':'empleado','app':'seguridad_social'},
			)

def exportar_planilla_empleados(request):
	# try:
		
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="planilla-empleados.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Lista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
									
		planillaEmpleados = PlanillaEmpleado.objects.filter(planilla__id=request.GET['planilla_id'])
		meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
		worksheet.write('A1', 'Contratista:', format2)
		worksheet.write('B1', planillaEmpleados.first().empleado.contratista.nombre, format2)
		worksheet.write('A2', 'Mes:', format2)
		worksheet.write('B2', meses[planillaEmpleados.first().planilla.mes - 1], format2)
		worksheet.write('A3', 'Año:', format2)
		worksheet.write('B3', planillaEmpleados.first().planilla.ano, format2)

		worksheet.write('A4', 'Cedula', format1)
		worksheet.write('B4', 'Nombres', format1)
		worksheet.write('C4', 'Apellidos', format1)
		worksheet.write('D4', 'Cargo', format1)
		worksheet.write('E4', 'Pago Reportado', format1)

		worksheet.set_column('A:A', 18)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 22)
		worksheet.set_column('E:E', 18)
		
		row=4
		col=0
		
		for plan in planillaEmpleados:			
			worksheet.write(row,col  , plan.empleado.persona.cedula, format2)
			worksheet.write(row,col+1, plan.empleado.persona.nombres, format_date)
			worksheet.write(row,col+2, plan.empleado.persona.apellidos, format_date)
			worksheet.write(row,col+3, plan.empleado.cargo.nombre, format2)
			worksheet.write(row,col+4, ('Si' if plan.tiene_pago else 'No'), format2)
					
			row +=1
		
		workbook.close()
		return response
	# except Exception as e:
	# 	print(e)			

@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:

			tipo = request.GET['tipo']
			archivo = Empleado.objects.get(pk=request.GET['id'])			
			if tipo == 'soporte_tsa':
				return functions.exportarArchivoS3(str(archivo.soporte_tsa))
			elif tipo == 'soporte_matricula':
				return functions.exportarArchivoS3(str(archivo.soporte_matricula))
			elif tipo == 'hoja_de_vida':
				return functions.exportarArchivoS3(str(archivo.hoja_de_vida))
			elif tipo == 'soporte_licencia':
				return functions.exportarArchivoS3(str(archivo.soporte_licencia))			

		except Exception as e:
			functions.toLog(e,'seguridad_social.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def VerSoportePlanilla(request):
	if request.method == 'GET':
		try:

			archivo = Planilla.objects.get(pk=request.GET['id'])			
			
			return functions.exportarArchivoS3(str(archivo.soporte))					

		except Exception as e:
			functions.toLog(e,'seguridad_social.VerSoportePlanilla')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
