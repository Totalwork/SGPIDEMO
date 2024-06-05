# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
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
# Create your views here.
from .models import AArea, BSolicitud, CSoportesSolicitud
from empresa.models import Empresa
from usuario.models import Usuario, Persona
from estado.models import Estado
from tipo.models import Tipo
from contrato.models import Contrato
from empresa.models import Empresa
from django.conf import settings
from datetime import datetime
from sinin4.functions import functions
from proceso.models import AProceso, FProcesoRelacion, GProcesoRelacionDato, BItem
from contrato.models import EmpresaContrato
from .enumeration import TipoT, EstadoT
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from parametrizacion.models import Funcionario
from proceso.models import INotificacionVencimiento
from adminMail.models import Mensaje
from proceso.tasks import sendMail

proceso_id=2
proyecto_id=6

class PersonaSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model=Persona
		fields=('nombres','apellidos')

class UsuarioSerializerLite(serializers.HyperlinkedModelSerializer):
	persona = PersonaSerializer(read_only=True)
	class Meta:
		model=Usuario
		fields=('id','persona')

class AreaUSerializer(serializers.HyperlinkedModelSerializer):
	responsableArea = UsuarioSerializerLite(read_only=True) 
	responsableArea_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=Usuario.objects.all())


	class Meta:
		model=AArea
		fields=('id','nombre','responsableArea','responsableArea_id')


class AreaUSerializerLite(serializers.HyperlinkedModelSerializer):
	class Meta:
		model=AArea
		fields=('id','nombre',)

class AreaViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista con las areas registradas en la empresa que gestiona sus solicitudes de contratacion.<br/>
		Utilice el parametro <b>dato</b> para buscar las areas por nombre
	"""
	model=AArea
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = AreaUSerializer
	paginate_by = 10
	nombre_modulo='solicitudServicio.area'

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
			queryset = super(AreaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			mensaje=''	
			
			if (dato):
				qset=Q(nombre__icontains=dato)
				queryset = self.model.objects.filter(qset)

			if queryset.count()==0:
				mensaje='No se encontraron areas con los criterios de busqueda ingresados'

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
		#import pdb; pdb.set_trace()
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializerA = AreaUSerializer(data=request.DATA,context={'request': request})
				if serializerA.is_valid():
					serializerA.save(responsableArea_id=request.DATA['responsableArea_id'])
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializerA.data['id']
					)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializerA.data},status=status.HTTP_201_CREATED)
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
				serializer = AreaUSerializer(instance,data=request.DATA,
					context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(responsableArea_id=request.DATA['responsableArea_id'])	
					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_actualizar,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=instance.id
					)
					#import pdb; pdb.set_trace()
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

# Modelo: BSolicitud
# Codigo Backend para comunicacion con la base de datos

class EstadoSerializerLite(serializers.HyperlinkedModelSerializer):
	class Meta:
		model=Estado
		fields=('id','nombre',)

class TipoSerializerLite(serializers.HyperlinkedModelSerializer):
	class Meta:
		model=Tipo
		fields=('id','nombre',)

class ContratoSerializerLite(serializers.HyperlinkedModelSerializer):
	nombreContratante = serializers.SerializerMethodField('_contratante',read_only=True)

	def _contratante(self,obj):
		contratante = Empresa.objects.get(pk=obj.contratante.id)
		return contratante.nombre

	class Meta:
		model=Contrato
		fields=('id','nombre','numero','nombreContratante')


class EmpresaSerializer(serializers.HyperlinkedModelSerializer):
	#logo = serializers.ImageField(required=False)

	class Meta:
		model = Empresa
		fields=('id','nombre')


class SolicitudSerializer(serializers.HyperlinkedModelSerializer):
	area = AreaUSerializerLite(read_only=True) 
	area_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=AArea.objects.all())
	solicitante = UsuarioSerializerLite(read_only=True) 
	solicitante_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=Usuario.objects.all(), allow_null=True)		
	tipo = TipoSerializerLite(read_only=True) 
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=Tipo.objects.filter(app='SolicitudServicio'))
	contrato = ContratoSerializerLite(read_only=True) 
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=Contrato.objects.all(),allow_null=True)
	# tramitador = UsuarioSerializerLite(read_only=True) 
	# tramitador_id = serializers.PrimaryKeyRelatedField(write_only=True,
	# 	queryset=Usuario.objects.all(), allow_null=True)	
	# autoriza = UsuarioSerializerLite(read_only=True) 
	# autoriza_id = serializers.PrimaryKeyRelatedField(write_only=True,
	# 	queryset=Usuario.objects.all())	
	estado = EstadoSerializerLite(read_only=True) 
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=Estado.objects.filter(app='SolicitudServicio'), allow_null=True)
	porcentajeCumplido = serializers.SerializerMethodField('_porcentaje',read_only=True)
	procesoRelacion = serializers.SerializerMethodField('_procesoRelacion',read_only=True)


	class Meta:
		model=BSolicitud
		fields=('id','fechaCreacion','area','area_id','estado_id','estado','solicitante_id','solicitante',
			'contrato_id','contrato','descripcion','tipo','tipo_id','porcentajeCumplido','procesoRelacion')

	def _porcentaje(self,obj):

		pr = FProcesoRelacion.objects.filter(proceso_id=proceso_id,
			idApuntador=proyecto_id,idTablaReferencia=obj.id).values('id')
		if pr:
			totalItems = GProcesoRelacionDato.objects.filter(procesoRelacion_id=pr[0]['id']).count()
			itemsCumplidos = GProcesoRelacionDato.objects.filter(procesoRelacion_id=pr[0]['id'],
				estado='1').count()

			return round((float(itemsCumplidos) / float(totalItems))*100,2)
		else:
			return 0

	def _procesoRelacion(self,obj):
		pr = FProcesoRelacion.objects.filter(proceso_id=proceso_id,
			idApuntador=proyecto_id,idTablaReferencia=obj.id).values('id')
		if pr:
			return pr[0]['id']
		else:
			return 0		





class SolicitudSerializerLite(serializers.HyperlinkedModelSerializer):
	area = AreaUSerializerLite(read_only=True)
	solicitante = UsuarioSerializerLite(read_only=True)  
	estado = EstadoSerializerLite(read_only=True) 
	class Meta:
		model=BSolicitud
		fields=('id','fechaCreacion','area','solicitante','estado')

class SolicitudSerializerLite2(serializers.HyperlinkedModelSerializer): 
	class Meta:
		model=BSolicitud
		fields=('id','descripcion',)


class SolicitudServicioViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de solicitudes de servicio.<br/>
		Utilice el parameto <b>dato</b> para buscar las solicitudes a traves de la descripcion, numero de contrato, 
		nombre de contrato.<br/>
		Utilice el parameto <b>lite=1</b> para retornar la informacion con los datos estrictamente necesarios.

	"""
	model=BSolicitud
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = SolicitudSerializer
	paginate_by = 10
	nombre_modulo='solicitudServicio.solicitudServicio'
	#########################################################################################################
	#datos para configuracion de enlace al modulo de procesos												#
	#########################################################################################################	
	proyecto=6 # id del proyecto usado para enlace al modulo de proceso
	proceso=2 # id del proceso a implementar
	itemInicial=6 #id del item que inicia el proceso, registrando la expresion de necesidad

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
			queryset = super(SolicitudServicioViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			lite = self.request.query_params.get('lite', None)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			mensaje=''	
			qset = ~Q(id=0)
			if dato:
				qset= qset & ( Q(descripcion__icontains=dato) | Q(contrato__nombre__icontains=dato) | Q(contrato__numero__icontains=dato))
			
			usuarioActual = Usuario.objects.get(user=request.user)	
			qset=qset & Q(empresas=usuarioActual.empresa)

			queryset = self.model.objects.filter(qset)

			if queryset.count()==0:
				mensaje='No se encontraron Items con los criterios de busqueda ingresados'

			if ignorePagination:
				if lite:
					serializer = SolicitudSerializerLite(queryset,many=True)
				else:
					serializer = self.get_serializer(queryset,many=True)
				return Response({'message':mensaje,'success':'ok',
				'data':serializer.data})				
			else:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = SolicitudSerializerLite(queryset,many=True)	
					else:
						serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':mensaje,'success':'ok',
					'data':serializer.data})
				if lite:
					serializer = SolicitudSerializerLite(queryset,many=True)
				else:
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
				
				serializer = SolicitudSerializer(data=request.DATA,context={'request': request})
				#print (request.DATA)
				if serializer.is_valid():
					
					estadoT=EstadoT()
					serializer.save(area_id=request.DATA['area_id'],
						solicitante_id=request.user.usuario.id,
						estado_id=estadoT.Solicitado,
						tipo_id=request.DATA['tipo_id'],
						contrato_id=request.DATA['contrato_id'] if request.DATA['contrato_id'] != '' else None)

					#sol = BSolicitud.objects.get(pk=serializer.data['id']) 

					#sol.empresas.add(Usuario.objects.get(user=request.user).empresa)


					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)
					logs_model.save()
					#############################################################################################
					# Codigo para implementacion del proceso 													#
					#############################################################################################
					pr=FProcesoRelacion.objects.create(proceso_id=self.proceso,idApuntador=self.proyecto,
						idTablaReferencia=serializer.data['id'])
					items=BItem.objects.filter(proceso_id=self.proceso)
					for it in items:
						if it.id == self.itemInicial:
							prd=GProcesoRelacionDato.objects.create(procesoRelacion=pr,	
								item=it, valor=datetime.now(), estado='1')
							funcionario=Funcionario.objects.filter(persona=request.user.usuario.persona).values('id')
							notificacion = 	INotificacionVencimiento.objects.create(
								procesoRelacionDato=prd,
								funcionario=Funcionario.objects.get(pk=funcionario[0]['id']),
								responsableTitular=True)						

						else:
							prd=GProcesoRelacionDato.objects.create(procesoRelacion=pr,	item=it)
						#############################################################################################
						# Codigo para agregar las notificaciones a los responsables del item   						#
						#############################################################################################
						if it.responsable and it.contratistaResponsable==False and it.id != self.itemInicial:
							funcionario=Funcionario.objects.filter(persona=it.responsable.persona).values('id')
							notificacion = 	INotificacionVencimiento.objects.create(
								procesoRelacionDato=prd,
								funcionario=Funcionario.objects.get(pk=funcionario[0]['id']),
								responsableTitular=True)
					#import pdb; pdb.set_trace()			
					#################################################################################################
					#Codigo para el envio del correo de inicio del proceso 											#	
					#################################################################################################
					it = BItem.objects.get(pk=self.itemInicial)
					correo = INotificacionVencimiento.objects.filter(procesoRelacionDato__procesoRelacion=pr,
						procesoRelacionDato__item__orden=it.orden+1).values('funcionario__persona__correo','procesoRelacionDato__item__descripcion')
					if correo:
						contenido='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
						contenido=contenido + 'Nos permitimos comunicarle que el funcionario ' + request.user.usuario.persona.nombres + ' '
						contenido = contenido + request.user.usuario.persona.apellidos + ', del area ' + serializer.data['area']['nombre'] + ', ha registrado ' 
						contenido = contenido + 'la solicitud de servicio <b>' + serializer.data['descripcion'] +'</b> de tipo <b>' 
						contenido = contenido + serializer.data['tipo']['nombre'] +'</b> '
						contenido = contenido + 'asociado al contrato <b>' + serializer.data['contrato']['nombre'] 
						contenido = contenido + ' - ' + serializer.data['contrato']['numero'] + '</b><br/><br/>'
						contenido = contenido + 'se requiere su valiosa colaboración para atender el siguiente paso del proceso '
						contenido = contenido + 'asociado al presente mensaje: <br/><br/>'
						direccion = settings.SERVER_URL
						if settings.PORT_SERVER != '':
							direccion = direccion + ':'+ settings.PORT_SERVER
						direccion = direccion + '/proceso/solicitudServicioSeguimiento/' + str(pr.id) + '/'
						contenido = contenido + '<a href="'+direccion+'">'
						contenido = contenido + correo[0]['procesoRelacionDato__item__descripcion']
						contenido = contenido + '</a><br/><br/>'
						contenido = contenido + 'Favor no responder este correo, es de uso informativo exclusivamente,'
						contenido = contenido + '<br/></br><br/>Equipo SININ'
						mail = Mensaje(
							remitente=settings.REMITENTE,
							destinatario=correo[0]['funcionario__persona__correo'],
							asunto='Actualización en seguimiento de proceso de gestión precontractual',
							contenido=contenido,
							appLabel='SolicitudServicio',
						)
						mail.save()						
						res=sendMail.delay(mail)

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
				serializer = SolicitudSerializer(instance,data=request.DATA,
					context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(area_id=request.DATA['area_id'],
									solicitante_id=request.DATA['solicitante_id'],
									estado_id=request.DATA['estado_id'],
									tipo_id=request.DATA['tipo_id'],
									contrato_id=request.DATA['contrato_id'] if request.DATA['contrato_id'] != '' else None)

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

# Modelo: CSoportesSolicitud
# Codigo Backend para comunicacion con la base de datos

class SoportesSolicitudSerializer(serializers.HyperlinkedModelSerializer):

	solicitud = SolicitudSerializerLite2(read_only=True) 
	solicitud_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=BSolicitud.objects.all())		


	class Meta:
		model=CSoportesSolicitud
		fields=('id','fechaCreacion','nombre','documento','solicitud','solicitud_id')

class SoporteSolicitudServicioViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de soportes de la solicitud de servicio.<br/>
		Utilice el parameto <b>dato</b> para buscar las solicitudes a traves del nombre del archivo.<br/>
		Utilice el parameto <b>solicitud</b> para retornar los soportes de una solicitud.

	"""
	model=CSoportesSolicitud
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = SoportesSolicitudSerializer
	paginate_by = 10
	nombre_modulo='solicitudServicio.solicitudServicioSoporte'

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
			queryset = super(SoporteSolicitudServicioViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			solicitud = self.request.query_params.get('solicitud', None)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			mensaje=''	
			qset=(~Q(id=0))
			if dato or solicitud:
				if dato:
					qset = qset & (Q(nombre__icontains=dato))
				if solicitud:
					qset = qset & (Q(solicitud__id=solicitud))	

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
				serializer = SoportesSolicitudSerializer(data=request.DATA,
					context={'request': request})
				if serializer.is_valid():
					serializer.save(
						solicitud_id=request.DATA['solicitud_id'],
						documento=self.request.FILES.get('documento')
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
				serializer = SoportesSolicitudSerializer(instance,data=request.DATA,
					context={'request': request},partial=partial)
				if serializer.is_valid():
					valores=CSoportesSolicitud.objects.get(id=instance.id)
					if self.request.FILES.get('documento') is not None:
						serializer.save(
							solicitud_id=request.DATA['solicitud_id'],
							documento=self.request.FILES.get('documento')
						)
					else:
						serializer.save(
							solicitud_id=request.DATA['solicitud_id'],
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

@api_view(['DELETE'])
def eliminar_solicitudes(request):
	if request.method == 'DELETE':	
		sid = transaction.savepoint()
		try:
			
			resultado=json.loads(request.POST['_content'])
			lista=resultado['lista']
			for id in lista:
				solicitud=BSolicitud.objects.get(pk=id)
				solicitud.delete()
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitudservicio.solicitud',id_manipulado=id)
				logs_model.save()

			transaction.savepoint_commit(sid)	
			return Response({'message':'Los registros se han eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)


@login_required
def servicio_solicitud(request):
	contratos = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id).values('contrato__id', 'contrato__nombre').distinct()
	usuarios = Usuario.objects.filter(empresa__id=request.user.usuario.empresa.id)	
	tipos = Tipo.objects.filter(app='SolicitudServicio')	
	areas = AArea.objects.all()
	# Inicio Codigo para enviar los items pendientes por atenter con su id de procesoRelacion
	pendientes=[]
	# qset = ~Q(estado='1')
	# qset = qset & Q(item__responsable=request.user.usuario)
	#import pdb; pdb.set_trace()
	qset = ~Q(procesoRelacionDato__estado='1')
	qset = qset & Q(funcionario=Funcionario.objects.filter(persona=request.user.usuario.persona,
		empresa=request.user.usuario.empresa)[:1])
	qset = qset & Q(procesoRelacionDato__procesoRelacion__proceso__id=proceso_id)
	qset = qset & Q(responsableTitular=True)	
	# procesoRelacionDatos = GProcesoRelacionDato.objects.filter(qset).order_by('procesoRelacion__id',
	# 	'item__orden').values('item__orden','procesoRelacion__id','item__descripcion',
	# 	'procesoRelacion__proceso__tablaForanea__id','procesoRelacion__idApuntador',
	# 	'procesoRelacion__idTablaReferencia','procesoRelacion__proceso__etiqueta')
	notificaciones = INotificacionVencimiento.objects.filter(qset).order_by('procesoRelacionDato__procesoRelacion__id',
		'procesoRelacionDato__item__orden').values('procesoRelacionDato__item__orden',
		'procesoRelacionDato__procesoRelacion__id','procesoRelacionDato__item__descripcion',
		'procesoRelacionDato__procesoRelacion__proceso__tablaForanea__id','procesoRelacionDato__procesoRelacion__idApuntador',
		'procesoRelacionDato__procesoRelacion__idTablaReferencia','procesoRelacionDato__procesoRelacion__proceso__etiqueta').distinct()
	
	for prd in notificaciones:
		prdAnterior = GProcesoRelacionDato.objects.filter(procesoRelacion__id=prd['procesoRelacionDato__procesoRelacion__id'],
			item__orden=(prd['procesoRelacionDato__item__orden']-1),estado='1')
		if prdAnterior.count()>0:
			modeloReferencia = ContentType.objects.get(
				pk=prd['procesoRelacionDato__procesoRelacion__proceso__tablaForanea__id']).model_class()
			elemento = modeloReferencia.objects.filter(
				id=prd['procesoRelacionDato__procesoRelacion__idTablaReferencia']).values(prd['procesoRelacionDato__procesoRelacion__proceso__etiqueta'])

			if len(prd['procesoRelacionDato__item__descripcion'])>48:
				descripcion=prd['procesoRelacionDato__item__descripcion'][0:48] + '...'
			else:
				descripcion=prd['procesoRelacionDato__item__descripcion']
			textoElementoAnalizado=elemento[0][prd['procesoRelacionDato__procesoRelacion__proceso__etiqueta']]
			if len(textoElementoAnalizado)>48:
				textoElementoAnalizado=textoElementoAnalizado[0:45] + '...'
			pendientes.append(
				{
					'procesoRelacionDato__item__descripcion':descripcion,
					'procesoRelacionDato__procesoRelacion__id':prd['procesoRelacionDato__procesoRelacion__id'],
					'procesoRelacionDato__elementoAnalizado': textoElementoAnalizado
				}
			)
	# Fin Codigo para enviar los items pendientes por atenter con su id de procesoRelacion
	return render(request, 'servicio_solicitud.html',
		{'model':'bsolicitud','app':'solicitudservicio', 'usuarios':usuarios, 
		'contratos': contratos, 'areas':areas, 'tipos':tipos, 'pendientes':pendientes})	

@login_required
def mis_pendientes(request):
	# Inicio Codigo para enviar los items pendientes por atenter con su id de procesoRelacion
	pendientes=[]
	# qset = ~Q(estado='1')
	# qset = qset & Q(item__responsable=request.user.usuario)
	qset = ~Q(procesoRelacionDato__estado='1')
	qset = qset & Q(funcionario=Funcionario.objects.filter(persona=request.user.usuario.persona,
		empresa=request.user.usuario.empresa)[:1])
	qset = qset & Q(procesoRelacionDato__procesoRelacion__proceso__id=proceso_id)
	qset = qset & Q(responsableTitular=True)	
	notificaciones = INotificacionVencimiento.objects.filter(qset).order_by('procesoRelacionDato__procesoRelacion__id',
		'procesoRelacionDato__item__orden').values('procesoRelacionDato__item__orden',
		'procesoRelacionDato__procesoRelacion__id','procesoRelacionDato__item__descripcion',
		'procesoRelacionDato__procesoRelacion__proceso__tablaForanea__id','procesoRelacionDato__procesoRelacion__idApuntador',
		'procesoRelacionDato__procesoRelacion__idTablaReferencia','procesoRelacionDato__procesoRelacion__proceso__etiqueta').distinct()
	for prd in notificaciones:
		prdAnterior = GProcesoRelacionDato.objects.filter(procesoRelacion__id=prd['procesoRelacionDato__procesoRelacion__id'],
			item__orden=(prd['procesoRelacionDato__item__orden']-1),estado='1')
		if prdAnterior.count()>0:
			modeloReferencia = ContentType.objects.get(
				pk=prd['procesoRelacionDato__procesoRelacion__proceso__tablaForanea__id']).model_class()
			elemento = modeloReferencia.objects.filter(
				id=prd['procesoRelacionDato__procesoRelacion__idTablaReferencia']).values(prd['procesoRelacionDato__procesoRelacion__proceso__etiqueta'])

			descripcion=prd['procesoRelacionDato__item__descripcion']
			textoElementoAnalizado=elemento[0][prd['procesoRelacionDato__procesoRelacion__proceso__etiqueta']]
			pendientes.append(
				{
					'item__descripcion':descripcion,
					'procesoRelacion__id':prd['procesoRelacionDato__procesoRelacion__id'],
					'elementoAnalizado': textoElementoAnalizado
				}
			)
	# Fin Codigo para enviar los items pendientes por atenter con su id de procesoRelacion	
	return render(request, 'misPendientes.html',
		{'model':'servicio_solicitud','app':'solicitudservicio', 'pendientes':pendientes},
		)			

