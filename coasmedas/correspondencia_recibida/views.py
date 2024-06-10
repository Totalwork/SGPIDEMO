# -*- coding: utf-8 -*- 
from coasmedas.functions import functions
from datetime import date
import datetime
import shutil
import time
import os
from io import StringIO
import json
from django.db.models import Max

from django.shortcuts import render
#, render_to_response
from django.urls import reverse
from django.db import transaction
from .models import  CorrespondenciaRecibida,  CorrespondenciaRecibidaAsignada  , CorrespondenciaRecibidaSoporte
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

from correspondencia.models import CorrespondenciaEnviada , CorrespondenciaSoporte , CorrespondenciaConsecutivo  , CorrespondenciaRadicado
from correspondencia.views import CorrespondenciaEnviadaLiteSerializer 

from empresa.models import Empresa
from usuario.models import Usuario ,Persona

from django.contrib.auth.models import User, Permission

from estado.models import Estado
from estado.views import EstadoSerializer
from tipo.models import Tipo
from tipo.views import TipoSerializer
# --------------------------------------------------------------
# BARCODE BARCODE BARCODE
from reportlab.graphics.barcode import code39, code128, code93
from reportlab.graphics.barcode import eanbc, qr, usps
from reportlab.graphics.shapes import Drawing 
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm 
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF

# from django.http import HttpResponse
from reportlab.lib.units import cm 
from reportlab.graphics.barcode.qr import QrCodeWidget 
from reportlab.graphics.barcode.eanbc import Ean13BarcodeWidget , Ean8BarcodeWidget
# from reportlab.graphics.barcode.usps import Ean13BarcodeWidget
# from reportlab.pdfgen.canvas import Canvas
# from reportlab.platypus import Frame
# from reportlab.lib.units import mm
# Create your views here.
from django.db.models import Max

global  estado_por_revisar , estado_revisada , estado_respondida , estado_reasignada , estado_anulada

estado_por_revisar = 33
estado_revisada = 34
estado_respondida = 35
estado_reasignada = 36
estado_anulada = 66

from logs.models import Logs,Acciones
# from datetime import *
from django.db import transaction,connection
from django.db.models.deletion import ProtectedError
import re

# extensiones validas para los soportes de la correspondencias
extensiones_permitidas = ['.jpg' , '.zip' , '.pdf' ]

#Api rest para CorrespondenciaRecibida
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
	persona = PersonaLiteSerializer(read_only=True)
	user=UserSerializer(read_only=True)

	class Meta:
		model = Usuario
		fields=('id', 'persona' , 'user')
# ANULAR CARTA
@transaction.atomic
def destroyCorrespondenciaRecibida(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']
			
			insert_list = []
			for i in myList:
				usuario_id=request.user.usuario.id

				raAsig=CorrespondenciaRecibidaAsignada( respuesta_id = None
															,copia = 0 #  cero porque no es copia ; uno es una copia ;
															,correspondenciaRecibida_id = i
															,estado_id = estado_anulada # se anula el radicado 
															,usuario_id = usuario_id
															)

				raAsig.save()

				insert_list.append(Logs(usuario_id = usuario_id
										,accion = Acciones.accion_borrar
										,nombre_modelo = 'correspondencia.CorrespondenciaRecibidaAsignada'
										,id_manipulado = raAsig.id)
										)

			Logs.objects.bulk_create(insert_list)
			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok','data': ''})
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ESTABLECER CARTA 
@transaction.atomic
def establishCorrespondenciaRecibida(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']

			insert_list = []
			for i in myList:

				raAsig=CorrespondenciaRecibidaAsignada( respuesta_id = None
															,copia = 0 #  cero porque no es copia ; uno es una copia ;
															,correspondenciaRecibida_id = i
															,estado_id = estado_por_revisar # se anula el radicado 
															,usuario_id = request.user.usuario.id
															)

				raAsig.save()

				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_crear
										,nombre_modelo='correspondencia.CorrespondenciaRecibidaAsignada'
										,id_manipulado=raAsig.id)
										)

			Logs.objects.bulk_create(insert_list)
			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok','data': ''})
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CorrespondenciaRecibidaSerializer(serializers.HyperlinkedModelSerializer):

	correspondenciaEnviada = CorrespondenciaEnviadaLiteSerializer(read_only = True)

	empresa = EmpresaLiteSerializer(read_only = True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Empresa.objects.all())

	usuarioSolicitante = UsuarioLiteSerializer(read_only = True)
	usuarioSolicitante_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	asignacion = serializers.SerializerMethodField()
	totalSoportes = serializers.SerializerMethodField()

	class Meta:
		model = CorrespondenciaRecibida
		fields=(	 'id' 
					, 'empresa' , 'empresa_id'
					, 'usuarioSolicitante' , 'usuarioSolicitante_id'
					, 'radicado' 
					, 'fechaRecibida'
					, 'anoRecibida'
					, 'remitente' 
					, 'asunto' 	
					, 'fechaRegistro' 
					, 'privado' 
					, 'correspondenciaEnviada'
					, 'radicadoPrevio'
					, 'asignacion'
					, 'totalSoportes'
					, 'fechaRespuesta' 
					)
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'empresa_id' , 'radicado' , 'anoRecibida'),
				message=('El radicado no puede  estar repetido en la misma anualidad de recibido.')
				)
				]

	def get_asignacion(self, obj):
	
		try:
			qsetCorrespondencia = CorrespondenciaRecibidaAsignada.objects.filter(correspondenciaRecibida_id = obj.id, copia = False ).latest('id')
			# correspondenciaData = CorrespondenciaRecibidaAsignadaLiteSerializer(qsetCorrespondencia,many=True).data
			return {
						'usuario_id' : qsetCorrespondencia.usuario_id
						,'estado_id': qsetCorrespondencia.estado_id
					}
		except CorrespondenciaRecibidaAsignada.DoesNotExist as e:
			return 0

	def get_totalSoportes(self, obj):
		id_corre = obj.correspondenciaEnviada_id
		if id_corre:
			soporte = CorrespondenciaRecibidaSoporte.objects.filter(correspondencia__in = [obj.id , id_corre] , anulado = 0).count()
			
		else:
			soporte = CorrespondenciaRecibidaSoporte.objects.filter(correspondencia = obj.id , anulado = 0).count()
		
		return soporte 


class CorrespondenciaRecibidaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model = CorrespondenciaRecibida
	queryset = model.objects.all()
	serializer_class = CorrespondenciaRecibidaSerializer
	nombre_modulo = 'correspondencia_recibida.CorrespondenciaRecibidaViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CorrespondenciaRecibidaViewSet, self).get_queryset()
			misCorrespondencias = self.request.query_params.get('mis_correspondencias', 0)

			dato = self.request.query_params.get('dato', None)


			copia = self.request.query_params.get('copia', None)
			estadoId = self.request.query_params.get('estado', 0)

			usuarioElaboro = self.request.query_params.get('usuarioElaboro', None)
			soporte_si = self.request.query_params.get('soporte_si', 0)
			soporte_no = self.request.query_params.get('soporte_no', 0)
			remitente = self.request.query_params.get('remitente', 0)
			radicado = self.request.query_params.get('radicado', 0)
			asunto = self.request.query_params.get('asunto', 0)
			fechaDesde = self.request.query_params.get('fechaDesde', None)
			fechaHasta = self.request.query_params.get('fechaHasta', None)
			radicado_previo = self.request.query_params.get('radicado_previo', None)

			# empresa que hace la peticion
			empresaActual = self.request.query_params.get('empresa_actual', request.user.usuario.empresa.id )
			
			usuarioActual = request.user.usuario.id
			empresaId = request.user.usuario.empresa.id

			# # SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y ESTEN PRIVADA
			queryHistorial = CorrespondenciaRecibidaAsignada.objects.filter(correspondenciaRecibida__empresa=empresaId, correspondenciaRecibida__privado=True).values('correspondenciaRecibida_id').annotate(id=Max('id'))
			lista = [value['id'] for value in queryHistorial]			
			# #SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y  ESTEN PRIVADA Y SEAN DEL USUARIO
			query_cartas_usuario_asigno = CorrespondenciaRecibidaAsignada.objects.filter(id__in = lista , usuario = usuarioActual , copia = False).values('correspondenciaRecibida_id')
			idConsulta = [value['correspondenciaRecibida_id'] for value in query_cartas_usuario_asigno]
			qset2 = Q(id__in=idConsulta) 

			qset = Q(empresa = empresaId, privado=False) 
			

			if usuarioElaboro:
				qset = qset & ( Q(usuarioSolicitante_id = usuarioElaboro ) )
						
			if (int(remitente)==1) and (len(dato)>0) and (int(radicado)==0) and (int(asunto)==0):
				qset = qset & ( Q(remitente__icontains = dato ) )

			if (int(radicado)==1) and (len(dato)>0) and (int(remitente)==0) and (int(asunto)==0):
				qset = qset & ( Q(radicado__icontains = dato ) )
			
			if (int(asunto)==1) and (len(dato)>0) and (int(remitente)==0) and (int(radicado)==0):
				qset = qset & ( Q(asunto__icontains = dato ) )

			if (int(asunto)==1) and (int(remitente)==1) and (int(radicado)==0):
				qset = qset & ( Q(remitente__icontains = dato ) |  Q(asunto__icontains = dato ) )

			if (int(asunto)==1) and (int(remitente)==0) and (int(radicado)==1):
				qset = qset & ( Q(radicado__icontains = dato ) | Q(asunto__icontains = dato ) )

			if (int(asunto)==0) and (int(remitente)==1) and (int(radicado)==1):
				qset = qset & ( Q(radicado__icontains = dato ) | Q(remitente__icontains = dato ) )

			if (int(asunto)==1) and (int(remitente)==1) and (int(radicado)==1):
				qset = qset & ( Q(remitente__icontains = dato ) | Q(radicado__icontains = dato ) | Q(asunto__icontains = dato ) )

				
			if (fechaDesde and (fechaHasta is not None) ):
				qset = qset & ( Q(fechaRecibida__gte= fechaDesde ) )
			
			if ( (fechaDesde is not None) and fechaHasta ):
				qset = qset & ( Q(fechaRecibida__lte=fechaHasta)  )

			if (fechaDesde and fechaHasta):	
				qset = qset & ( Q(fechaRecibida__range = (fechaDesde , fechaHasta) ) )

			if radicado_previo:
				qset = qset & ( Q(radicadoPrevio__icontains = radicado_previo ) )

			if (int(soporte_si)>0 and int(soporte_no)==0):
				queryset = self.model.objects.filter(qset | qset2)
				querySoporte = CorrespondenciaRecibidaSoporte.objects.filter(anulado = 0).values('correspondencia')# tipo uno correspondencia recibida
				queryset = queryset.filter(id__in = querySoporte)
			elif (int(soporte_si)==0 and int(soporte_no)>0):
				queryset = self.model.objects.filter(qset | qset2)
				querySoporte = CorrespondenciaRecibidaSoporte.objects.filter(anulado = 0).values('correspondencia')# tipo uno correspondencia recibida
				queryset = queryset.exclude(id__in = querySoporte)
			else:
				queryset = self.model.objects.filter(qset | qset2)
				# print queryset.query	

			# print queryset.query
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:

					serializer_context = {
						'request': request,
					}			

					# TRAER DATOS CON PARAMETROS DE REGISTRO
					parametro_select = self.request.query_params.get('parametro_select', None)

					if parametro_select:
						serializer = CorrespondenciaRecibidaSerializer(page,many=True,context=serializer_context)

						qsetEstadoCorrespondenciaAsignada = Estado.objects.filter(app = "correspondencia_recibida")
						estadosCorrespondenciaAsignadaData = EstadoSerializer(qsetEstadoCorrespondenciaAsignada,many=True).data

							
						qsetUsuariosElaboran = Usuario.objects.filter(empresa_id = empresaActual)
						usuariosElaboranData = UsuarioLiteSerializer(qsetUsuariosElaboran,many=True).data

						return self.get_paginated_response({'message':'','success':'ok'
							,'data':{'correspondencias_recibidas':serializer.data 
									, 'estados' : estadosCorrespondenciaAsignadaData
									, 'usuarios' : usuariosElaboranData#usuarios de la empresa que hace la peticion actual
									 }})

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
			
			try:

				fecha = request.DATA['fechaRecibida']
				request.DATA['anoRecibida'] = int(fecha[:4]) 
				radicado = request.DATA['radicado'] if 'radicado' in request.DATA else None;

				if radicado is None:
					request.DATA['radicado'] = 0
				request.DATA['fechaRespuesta'] = None

				# se cargan los soportes de la correspondencia
				# listado de soportes de la corresppondencia
				archivos = request.FILES.getlist('soporte[]') if 'soporte[]' in request.FILES else None;


				serializer = CorrespondenciaRecibidaSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					sid = transaction.savepoint()
					insert_list = []
					
					usuarioActual = request.DATA['usuarioSolicitante_id']
					u = Usuario.objects.get(pk = usuarioActual)
					empresaIdActual = u.empresa.id

					# listado de usuarios a copiar
					myListDestinatarioCopiar = request.DATA.getlist('destinatarioCopia[]') if 'destinatarioCopia[]' in request.DATA else None;
					
					destinatario = request.DATA['destinatario'] if 'destinatario' in request.DATA else None;
					try:
						# SE  INCREMENTA EL RADICADO EN 1
						cC = CorrespondenciaRadicado.objects.get(empresa_id = empresaIdActual , ano = int(fecha[:4]) )

						serializer.save( empresa_id = empresaIdActual
										, radicado = cC.numero
										, anoRecibida = int(fecha[:4]) 
										, usuarioSolicitante_id = usuarioActual 
										, correspondenciaEnviada_id = None
										)
						# SE REGISTRA EL  RADICADO
						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibida',id_manipulado=serializer.data['id'])
						logs_model.save()
						# insertar soortes de la correspondencia registrada
						insert_list = []

						if archivos:
							for archivo in archivos:
								filename, file_extension = os.path.splitext(archivo.name)	
								if file_extension.lower() in extensiones_permitidas:					

									t = datetime.datetime.now()
									nombre = filename
									archivo.name = str(request.user.usuario.empresa.id)+'-'+str(request.user.usuario.id)+'-'+str(t.year)+str(t.month)+str(t.day)+str(t.hour)+str(t.minute)+str(t.second)+str(t.microsecond)+str(file_extension)
									destino = archivo
								
									insert_list.append(
										CorrespondenciaRecibidaSoporte(
										nombre = nombre, correspondencia_id = serializer.data['id'], soporte = destino, anulado = False)
										)

							if insert_list:
								CorrespondenciaRecibidaSoporte.objects.bulk_create(insert_list)

						cC.numero = cC.numero+1
						cC.save()

						if destinatario:
							raAsig=CorrespondenciaRecibidaAsignada( respuesta_id = None
															,copia = 0 #  cero porque no es copia ; uno es una copia ;
															,correspondenciaRecibida_id = serializer.data["id"]
															,estado_id = 33 # por revisar 
															,usuario_id = destinatario
															)

							raAsig.save()
							# SE REGISTRA EL DESTINATARIO DEL RADICADO
							logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibidaAsignada',id_manipulado=raAsig.id)
							logs_model.save()


						if myListDestinatarioCopiar:
						
							for i in myListDestinatarioCopiar:

								if i != destinatario:
									raAsig2=CorrespondenciaRecibidaAsignada( 
																	respuesta_id = None
																	,copia = 1 #  cero porque no es copia ; uno es una copia ;
																	,correspondenciaRecibida_id = serializer.data["id"]
																	,estado_id = 33 # por revisar
																	,usuario_id = i
																	)
									raAsig2.save()
									# SE REGISTRA LOS USUARIOS A COPIAR DEL RADICADO
									logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibidaAsignada',id_manipulado=raAsig2.id)
									logs_model.save()

						transaction.savepoint_commit(sid)
						return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)
					except CorrespondenciaRadicado.DoesNotExist as e:
						functions.toLog(e,self.nombre_modulo)
						transaction.savepoint_rollback(sid)
						mensaje='No existe el radicado para la fecha (año) solicitada.'
						return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
					
				else:
					
					print(serializer.errors)
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "radicado" in serializer.errors:
						mensaje = serializer.errors["radicado"][0]+" En el campo radicado"
					elif "empresa" in serializer.errors:
						mensaje = serializer.errors["empresa"][0]+" En el campo empresa"
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
				serializer = CorrespondenciaRecibidaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				fechaRespuesta = request.DATA['fechaRespuesta'] if 'fechaRespuesta' in request.DATA else None;

				if serializer.is_valid():
					usuarioActual = request.DATA['usuarioSolicitante_id']
					u = Usuario.objects.get(pk = usuarioActual)
					empresaIdActual = u.empresa.id
					serializer.save( empresa_id = empresaIdActual , usuarioSolicitante_id = usuarioActual )

					# SE ACTUALIZA EL RADICADO RADICADO
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibida',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
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
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	
#Fin api rest para CorrespondenciaEnviada

#Api rest para CorrespondenciaRecibidaAsignada
class CorrespondenciaRecibidaAsignadaSerializer(serializers.HyperlinkedModelSerializer):

	correspondenciaRecibida = CorrespondenciaRecibidaSerializer(read_only = True)
	correspondenciaRecibida_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=CorrespondenciaRecibida.objects.all())

	usuario = UsuarioLiteSerializer(read_only = True)
	usuario_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	estado = EstadoSerializer(read_only = True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Estado.objects.filter(app="correspondencia_recibida"))

	respuesta = CorrespondenciaEnviadaLiteSerializer(read_only = True)
	respuesta_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=CorrespondenciaEnviada.objects.all())

	totalSoportes = serializers.SerializerMethodField()

	destinatario = serializers.SerializerMethodField()

	class Meta:
		model = CorrespondenciaRecibidaAsignada
		fields=('id'
				,'correspondenciaRecibida' ,'correspondenciaRecibida_id' 
				,'usuario' ,'usuario_id'
				,'fechaAsignacion' 
				,'estado' , 'estado_id' 
				,'respuesta' , 'respuesta_id' 
				,'copia' 
				,'totalSoportes'
				,'destinatario'
				)

	def get_totalSoportes(self, obj):
		id_corre = obj.correspondenciaRecibida.correspondenciaEnviada_id
		if id_corre:
			soporte = CorrespondenciaRecibidaSoporte.objects.filter(correspondencia__in = [obj.correspondenciaRecibida_id , id_corre] , anulado = 0).count()
			
		else:
			soporte = CorrespondenciaRecibidaSoporte.objects.filter(correspondencia = obj.correspondenciaRecibida_id , anulado = 0).count()
		
		return soporte 


	def get_destinatario(self, obj):
		# code here to calculate the result
		# or return obj.calc_result() if you have that calculation in the models		
		try:
			correspondencia = CorrespondenciaRecibidaAsignada.objects.filter(correspondenciaRecibida_id = obj.correspondenciaRecibida_id , copia = 0 ).values('correspondenciaRecibida_id' ).annotate(id=Max('id'))

			c = CorrespondenciaRecibidaAsignada.objects.get(pk = correspondencia[0]["id"] )
			return c.usuario_id
		except CorrespondenciaRecibidaAsignada.DoesNotExist as e:
			return 0

class CorrespondenciaRecibidaAsignadaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista del historial del radicado , 
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los registro.
	"""
	model = CorrespondenciaRecibidaAsignada
	queryset = model.objects.all()
	serializer_class = CorrespondenciaRecibidaAsignadaSerializer
	nombre_modulo = 'correspondencia_recibida.CorrespondenciaRecibidaAsignadaViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CorrespondenciaRecibidaAsignadaViewSet, self).get_queryset()

			misCorrespondencias = self.request.query_params.get('mis_correspondencias', 0)

			dato = self.request.query_params.get('dato', None)
			correspondenciaId = self.request.query_params.get('correspondencia', 0)

			copia = self.request.query_params.get('copia', None)
			estadoId = self.request.query_params.get('estado', 0)

			usuarioElaboro = self.request.query_params.get('usuarioElaboro', None)
			soporte_si = self.request.query_params.get('soporte_si', 0)
			soporte_no = self.request.query_params.get('soporte_no', 0)
			remitente = self.request.query_params.get('remitente', 0)
			radicado = self.request.query_params.get('radicado', 0)
			asunto = self.request.query_params.get('asunto', 0)
			fechaDesde = self.request.query_params.get('fechaDesde', None)
			fechaHasta = self.request.query_params.get('fechaHasta', None)
			radicado_previo = self.request.query_params.get('radicado_previo', None)

			# empresa que hace la peticion
			empresaActual = self.request.query_params.get('empresa_actual', request.user.usuario.empresa.id )


			if (int(correspondenciaId)>0):
				qset = ( Q(correspondenciaRecibida_id = correspondenciaId ) )
			else:
				usuarioActual = request.user.usuario.id
				empresaId = request.user.usuario.empresa.id


				# # SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y NO SEAN COPIA
				queryHistorial = CorrespondenciaRecibidaAsignada.objects.filter(correspondenciaRecibida__empresa=empresaId, copia=False).values('correspondenciaRecibida_id').annotate(id=Max('id')).values('id')
				# #SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y SEAN DEL USUARIO
				query_cartas_usuario_asigno = CorrespondenciaRecibidaAsignada.objects.filter(id__in = queryHistorial, usuario = usuarioActual).values('id')
			

				if int(misCorrespondencias)==0:
					# # SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y ESTEN PUBLICA
					queryHistorial = CorrespondenciaRecibidaAsignada.objects.filter(correspondenciaRecibida__empresa=empresaId, correspondenciaRecibida__privado=False).values('correspondenciaRecibida_id').annotate(id=Max('id')).values('id')
					# #SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y  ESTEN PUBLICA
					query_cartas_empresa = CorrespondenciaRecibidaAsignada.objects.filter(id__in = queryHistorial).values('id')
					qset = (Q(id__in=query_cartas_empresa) | Q(id__in=query_cartas_usuario_asigno) )

				else:
					qset = Q(id__in=query_cartas_usuario_asigno) 


			if copia:
				qset = qset & ( Q(copia = copia ) )

			if estadoId:
				qset = qset & ( Q(estado_id = estadoId) )

			if usuarioElaboro:
				qset = qset & ( Q(correspondenciaRecibida__usuarioSolicitante_id = usuarioElaboro ) )
						
			if (int(remitente)==1) and (len(dato)>0) and (int(radicado)==0) and (int(asunto)==0):
				qset = qset & ( Q(correspondenciaRecibida__remitente__icontains = dato ) )

			if (int(radicado)==1) and (len(dato)>0) and (int(remitente)==0) and (int(asunto)==0):
				qset = qset & ( Q(correspondenciaRecibida__radicado__icontains = dato ) )
			
			if (int(asunto)==1) and (len(dato)>0) and (int(remitente)==0) and (int(radicado)==0):
				qset = qset & ( Q(correspondenciaRecibida__asunto__icontains = dato ) )

			if (int(asunto)==1) and (int(remitente)==1) and (int(radicado)==0):
				qset = qset & ( Q(correspondenciaRecibida__remitente__icontains = dato ) |  Q(correspondenciaRecibida__asunto__icontains = dato ) )

			if (int(asunto)==1) and (int(remitente)==0) and (int(radicado)==1):
				qset = qset & ( Q(correspondenciaRecibida__radicado__icontains = dato ) | Q(correspondenciaRecibida__asunto__icontains = dato ) )

			if (int(asunto)==0) and (int(remitente)==1) and (int(radicado)==1):
				qset = qset & ( Q(correspondenciaRecibida__radicado__icontains = dato ) | Q(correspondenciaRecibida__remitente__icontains = dato ) )

			if (int(asunto)==1) and (int(remitente)==1) and (int(radicado)==1):
				qset = qset & ( Q(correspondenciaRecibida__remitente__icontains = dato ) | Q(correspondenciaRecibida__radicado__icontains = dato ) | Q(correspondenciaRecibida__asunto__icontains = dato ) )

				
			if (fechaDesde and (fechaHasta is not None) ):
				qset = qset & ( Q(correspondenciaRecibida__fechaRecibida__gte= fechaDesde ) )
			
			if ( (fechaDesde is not None) and fechaHasta ):
				qset = qset & ( Q(correspondenciaRecibida__fechaRecibida__lte=fechaHasta)  )

			if (fechaDesde and fechaHasta):	
				qset = qset & ( Q(correspondenciaRecibida__fechaRecibida__range = (fechaDesde , fechaHasta) ) )

			if radicado_previo:
				qset = qset & ( Q(correspondenciaRecibida__radicadoPrevio__icontains = radicado_previo ) )


			if (int(correspondenciaId)>0):
				queryset = self.model.objects.filter(qset)
			else:
				if (int(soporte_si)>0 and int(soporte_no)==0):
					queryset = self.model.objects.filter(qset)
					querySoporte = CorrespondenciaRecibidaSoporte.objects.filter(anulado = 0).values('correspondencia')# tipo uno correspondencia recibida
					queryset = queryset.filter(correspondenciaRecibida_id__in = querySoporte).order_by('-correspondenciaRecibida__fechaRecibida','-correspondenciaRecibida__radicado')
				elif (int(soporte_si)==0 and int(soporte_no)>0):
					queryset = self.model.objects.filter(qset)
					querySoporte = CorrespondenciaRecibidaSoporte.objects.filter(anulado = 0).values('correspondencia')# tipo uno correspondencia recibida
					queryset = queryset.exclude(correspondenciaRecibida_id__in = querySoporte).order_by('-correspondenciaRecibida__fechaRecibida','-correspondenciaRecibida__radicado')
				else:
					queryset = self.model.objects.filter(qset).order_by('-correspondenciaRecibida__fechaRecibida','-correspondenciaRecibida__radicado')

					# print queryset.query	

			# print queryset.query
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:

					serializer_context = {
						'request': request,
					}			

					# TRAER DATOS CON PARAMETROS DE REGISTRO
					parametro_select = self.request.query_params.get('parametro_select', None)

					if parametro_select:
						serializer = CorrespondenciaRecibidaAsignadaSerializer(page,many=True,context=serializer_context)

						qsetEstadoCorrespondenciaAsignada = Estado.objects.filter(app = "correspondencia_recibida")
						estadosCorrespondenciaAsignadaData = EstadoSerializer(qsetEstadoCorrespondenciaAsignada,many=True).data

						qsetUsuariosElaboran = Usuario.objects.filter(empresa_id = empresaActual ,user__is_active=True).order_by('persona__nombres')
						usuariosElaboranData = UsuarioLiteSerializer(qsetUsuariosElaboran,many=True).data

						return self.get_paginated_response({'message':'','success':'ok'
							,'data':{'correspondencias_asignadas':serializer.data 
									, 'estados' : estadosCorrespondenciaAsignadaData
									, 'usuarios' : usuariosElaboranData#usuarios de la empresa que hace la peticion actual
									 }})

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
				serializer = CorrespondenciaRecibidaAsignadaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(correspondenciaRecibida_id = request.DATA['correspondenciaRecibida_id']
									, usuario_id = request.DATA['usuario_id']
									, estado_id = request.DATA['estado_id']
									, respuesta_id = request.DATA['respuesta_id']
									 )	

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibidaAsignada',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "usuario" in serializer.errors:
						mensaje = serializer.errors["usuario"][0]+" En el campo usuario"
					elif "estado" in serializer.errors:
						mensaje = serializer.errors["estado"][0]+" En el campo estado"
					else:
						mensaje = 'datos requeridos no fueron recibidos'
					return Response({'message': mensaje ,'success':'fail',
			 			'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = CorrespondenciaRecibidaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
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
#Fin api rest para CorrespondenciaRecibidaAsignada	

@transaction.atomic
def createAsignarCorrespondencia(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:			

			myList = request.POST['correspondenciaRecibida_id'].split(',')

			for item in myList:
				c = CorrespondenciaRecibidaAsignada(
					correspondenciaRecibida_id = item
					, usuario_id = request.POST['usuario_id']
					, estado_id = request.POST['estado_id']
					, respuesta_id = None
				)
				c.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibidaAsignada',id_manipulado= c.id )
				logs_model.save()

			transaction.savepoint_commit(sid)
			return JsonResponse({'message': 'El registro ha sido guardado exitosamente','success':'ok','data': ''})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)	
	
def createBarCodes(request):
	if request.method == 'GET':
		try:
			correspondenciaObject = CorrespondenciaRecibida.objects.get(pk = request.GET['correspondencia'])
			"""
			Create barcode examples and embed in a PDF
			"""
			# Create the HttpResponse object with the appropriate PDF headers.
			response = HttpResponse(content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="doc'+str(correspondenciaObject.radicado)+'.pdf"'

			# p = canvas.Canvas(response)

			# qrw = QrCodeWidget('Helo World!') 
			# b = qrw.getBounds()

			# w=b[2]-b[0] 
			# h=b[3]-b[1] 

			# d = Drawing(45,45,transform=[45./w,0,0,45./h,0,0]) 
			# d.add(qrw)

			# renderPDF.draw(d, p, 1, 1)

			# p.showPage()
			# p.save()
			# return response

			# draw the eanbc8 code
			c = canvas.Canvas(response)

			barcode_value = str(correspondenciaObject.radicado)

			tam = 20-len(barcode_value)
			i = 1
			codigo_mostra = barcode_value
			while i<=tam:
				codigo_mostra = '0'+codigo_mostra 
				i+=1

			barcode128 = code128.Code128(barcode_value,barWidth=1.0*mm,barHeight=18*mm)
			# # the multiwidth barcode appears to be broken
			# #barcode128Multi = code128.MultiWidthBarcode(barcode_value)

			barcode128.drawOn(c, 1*cm , 1*cm)
				

			# barcode_eanbc8 = Ean8BarcodeWidget(barcode_value)
			# b = barcode_eanbc8.getBounds()
			# w = b[2] - b[0]
			# h = b[3] - b[1]
			t = datetime.datetime.now()
			c.setFont('Helvetica', 5) 
			c.drawString(6*mm, 2*mm, "RECIBIDO NO IMPLICA ACEPTACION" )
			c.setFont('Helvetica', 9) 
			c.drawString(30*mm, 7*mm, codigo_mostra )
			c.setFont('Helvetica', 8) 
			c.drawString(6*mm, 36*mm, "Barranquilla "+ t.strftime("%Y-%m-%d %H:%M:%S") ) 
			c.drawString(6*mm, 33*mm, str(correspondenciaObject.empresa.abreviatura) ) 
			c.drawString(6*mm, 30*mm, "RADICADO No." ) 

			# d = Drawing(220,80,transform=[210./40,0,0,60./40,0,0]) 
			# d.add(barcode128)
			# renderPDF.draw(d, c, 15, 20)

			# draw the eanbc13 code
			# c = canvas.Canvas(response)
			# barcode_eanbc13 = Ean13BarcodeWidget(str(correspondenciaObject.radicado))
			# b = barcode_eanbc13.getBounds()
			# w=b[2]-b[0] 
			# h=b[3]-b[1] 
			# t = datetime.datetime.now()
			# c.setFont('Helvetica', 5) 
			# c.drawString(6*mm, 2*mm, "RECIBIDO NO IMPLICA ACEPTACION" )
			# c.setFont('Helvetica', 8) 
			# c.drawString(6*mm, 36*mm, "Barranquilla "+ t.strftime("%Y-%m-%d %H:%M:%S") ) 
			# c.drawString(6*mm, 33*mm, str(correspondenciaObject.empresa.nombre) ) 
			# c.drawString(6*mm, 30*mm, "RADICADO No." ) 

			# d = Drawing(220,80,transform=[210./w,0,0,60./h,0,0]) 
			# d.add(barcode_eanbc13)
			# renderPDF.draw(d, c, 15, 20)

			c.setPageSize((227, 113))
			# c.setPageSize((227, 113))
			c.showPage()
			c.save()
			return response
		except Exception as e:
			raise e

# exporta a excel correspondencia recibida
def exportReporteCorrespondenciaRecibida(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="Reporte_correspondenciaRecibida.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Cartas recibidas')	
	
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
	copia = request.GET['copia'] if 'copia' in request.GET else None;
	estadoId = request.GET['estado'] if 'estado' in request.GET else None;
	usuarioElaboro = request.GET['usuarioElaboro'] if 'usuarioElaboro' in request.GET else None;
	soporte_si = request.GET['soporte_si'] if 'soporte_si' in request.GET else 0;
	soporte_no = request.GET['soporte_no'] if 'soporte_no' in request.GET else 0;

	remitente = request.GET['remitente'] if 'remitente' in request.GET else 0;
	radicado = request.GET['radicado'] if 'radicado' in request.GET else 0;
	asunto = request.GET['asunto'] if 'asunto' in request.GET else 0;
	fechaDesde = request.GET['fechaDesde'] if 'fechaDesde' in request.GET else None;
	fechaHasta = request.GET['fechaHasta'] if 'fechaHasta' in request.GET else None;


	misCorrespondencias = request.GET['mis_correspondencias'] if 'mis_correspondencias' in request.GET else 0; 

	empresaId = request.user.usuario.empresa.id
	usuarioActual = request.user.usuario.id
	model=CorrespondenciaRecibidaAsignada


	# INICIA CONSULTA PARA CORRESPONDENCIAS RECIBIDAS

	lista = [] 
	# SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA
	queryHistorial = model.objects.filter(correspondenciaRecibida__empresa=empresaId).values('correspondenciaRecibida_id').annotate(id=Max('id'))

	for i in queryHistorial:
		lista.append(i['id'])
		# print i['id']			
	#SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y AL USUARIO QUE SE LE ASIGNO 
	queryHistorial = model.objects.filter(id__in = lista , usuario = usuarioActual , copia = False).values('id')
	idConsulta = []
	for i in queryHistorial:
		idConsulta.append(i['id'])
		# print "usuario asignado="+str(i['id']) 

	if int(misCorrespondencias)==0:
		#SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y AL USUARIO QUE SE LE copio
		queryHistorial = model.objects.filter(id__in = lista , usuario = usuarioActual , copia = True).values('id')
		for i in queryHistorial:
			idConsulta.append(i['id'])

		#SE CONSULTA TODAS LAS CARTAS DE LA EMPRESA QUE NO SEAN PRIVADAS
		queryHistorial = model.objects.filter(correspondenciaRecibida__empresa=empresaId,correspondenciaRecibida__privado=False).values('correspondenciaRecibida_id').annotate(id=Max('id')).exclude(id__in=idConsulta)
		
		for i in queryHistorial:
			idConsulta.append(i['id'])
			# print i['id']

	# FINALIZA LA CONSULTA PARA CORRESPONDENCIAS RECIBIDAS

	qset = ( Q(id__in = idConsulta) )

	if copia:
		qset = qset & ( Q(copia = copia ) )

	if estadoId:
		qset = qset & ( Q(estado_id = estadoId) )

	if usuarioElaboro:
		qset = qset & ( Q(correspondenciaRecibida__usuarioSolicitante_id = usuarioElaboro ) )
				
	
	# FILTRO POR RADICADO , ASUNTO , REMITENTE
	if (int(remitente)==1) and (len(dato)>0) and (int(radicado)==0) and (int(asunto)==0):
		qset = qset & ( Q(correspondenciaRecibida__remitente__icontains = dato ) )

	if (int(radicado)==1) and (len(dato)>0) and (int(remitente)==0) and (int(asunto)==0):
		qset = qset & ( Q(correspondenciaRecibida__radicado__icontains = dato ) )
	
	if (int(asunto)==1) and (len(dato)>0) and (int(remitente)==0) and (int(radicado)==0):
		qset = qset & ( Q(correspondenciaRecibida__asunto__icontains = dato ) )

	if (int(asunto)==1) and (int(remitente)==1) and (int(radicado)==0):
		qset = qset & ( Q(correspondenciaRecibida__remitente__icontains = dato ) |  Q(correspondenciaRecibida__asunto__icontains = dato ) )

	if (int(asunto)==1) and (int(remitente)==0) and (int(radicado)==1):
		qset = qset & ( Q(correspondenciaRecibida__radicado__icontains = dato ) | Q(correspondenciaRecibida__asunto__icontains = dato ) )

	if (int(asunto)==0) and (int(remitente)==1) and (int(radicado)==1):
		qset = qset & ( Q(correspondenciaRecibida__radicado__icontains = dato ) | Q(correspondenciaRecibida__remitente__icontains = dato ) )

	if (int(asunto)==1) and (int(remitente)==1) and (int(radicado)==1):
		qset = qset & ( Q(correspondenciaRecibida__remitente__icontains = dato ) | Q(correspondenciaRecibida__radicado__icontains = dato ) | Q(correspondenciaRecibida__asunto__icontains = dato ) )

		
		
	if (fechaDesde and (fechaHasta is not None) ):
		qset = qset & ( Q(correspondenciaRecibida__fechaRecibida__gte= fechaDesde ) )
	
	if ( (fechaDesde is not None) and fechaHasta ):
		qset = qset & ( Q(correspondenciaRecibida__fechaRecibida__lte=fechaHasta)  )

	if (fechaDesde and fechaHasta):	
		qset = qset & ( Q(correspondenciaRecibida__fechaRecibida__range = (fechaDesde , fechaHasta) ) )

	if (int(soporte_si)>0 and int(soporte_no)==0):
		queryset = model.objects.filter(qset)
		querySoporte = CorrespondenciaSoporte.objects.filter(tipo = 1 , anulado = 0).values('correspondencia')# tipo uno correspondencia recibida
		queryset = queryset.filter(correspondenciaRecibida_id__in = querySoporte)
	elif (int(soporte_si)==0 and int(soporte_no)>0):
		queryset = model.objects.filter(qset)
		querySoporte = CorrespondenciaSoporte.objects.filter(tipo = 1, anulado = 0).values('correspondencia')# tipo uno correspondencia recibida
		queryset = queryset.exclude(correspondenciaRecibida_id__in = querySoporte)
	else:
		queryset = model.objects.filter(qset)


	
	formato_fecha = "%Y-%m-%d"	
	queryset = queryset.order_by('-id')
	worksheet.set_column('A:K', 20)

	worksheet.write('A1', 'Radicado', format1)
	worksheet.write('B1', 'Fecha Recibida', format1)
	worksheet.write('C1', 'Asunto', format1)
	worksheet.write('D1', 'Remitente', format1)
	worksheet.write('E1', 'Elaborado Por', format1)
	worksheet.write('F1', 'Radicado Previo', format1)
	worksheet.write('G1', 'Estado', format1)

	worksheet.set_column('A:A', 10)
	worksheet.set_column('B:B', 17)
	worksheet.set_column('C:C', 50)
	worksheet.set_column('D:D', 50)
	worksheet.set_column('E:E', 40)
	worksheet.set_column('F:F', 18)
	worksheet.set_column('G:G', 18)

	for destinatarioCorrespondenciaRecibida in queryset:

		estado = destinatarioCorrespondenciaRecibida.estado.nombre 

		correspondencia = destinatarioCorrespondenciaRecibida.correspondenciaRecibida

		radicado = correspondencia.radicado
		fechaRecibida = correspondencia.fechaRecibida
		asunto = correspondencia.asunto
		remitente = correspondencia.remitente
		elaboro = correspondencia.usuarioSolicitante.persona.nombres+' '+correspondencia.usuarioSolicitante.persona.apellidos
		radicadoPrevio = correspondencia.radicadoPrevio

		worksheet.write(row, col, radicado ,format2)
		worksheet.write(row, col+1,fechaRecibida ,format_date)
		worksheet.write(row, col+2,asunto ,format2)
		worksheet.write(row, col+3,remitente ,format2)
		worksheet.write(row, col+4, elaboro ,format2)
		worksheet.write(row, col+5, radicadoPrevio ,format2)
		worksheet.write(row, col+6, estado ,format2)
		
		row +=1
	workbook.close()
	return response

#Api rest para CorrespondenciaSoporte
class CorrespondenciaRecibidaSoporteSerializer(serializers.HyperlinkedModelSerializer):

	correspondencia = CorrespondenciaRecibidaSerializer(read_only = True)
	correspondencia_id = serializers.PrimaryKeyRelatedField(write_only=True , queryset=CorrespondenciaRecibida.objects.all())

	class Meta:
		model = CorrespondenciaRecibidaSoporte
		fields=(
				'id'
				,'nombre'
				, 'correspondencia' , 'correspondencia_id' 
				,'soporte' 
				,'anulado'
				)

class CorrespondenciaRecibidaSoporteViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de soportes de las correspondencia recibida , 
	<br>puede utilizar el parametro (dato) a traves del cual puede consultar todos los soportes.
	<br>puede utilizar el parametro (correspondencia) a traves del cual puede consultar todos los de la correspondencia indicada.
	"""
	model = CorrespondenciaRecibidaSoporte
	queryset = model.objects.all()
	serializer_class = CorrespondenciaRecibidaSoporteSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CorrespondenciaRecibidaSoporteViewSet, self).get_queryset()
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
				serializer = CorrespondenciaRecibidaSoporteSerializer(data=request.DATA,context={'request': request})
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
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibidaSoporte',id_manipulado=serializer.data['id'])
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
			CorrespondenciaRecibidaSoporte.objects.filter(id__in = myList).update(anulado = 1)


			insert_list = []
			for i in myList:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_borrar
										,nombre_modelo='correspondencia_recibida.CorrespondenciaRecibidaSoporte'
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


@login_required
def correspondenciaRecibida(request):
	return render(request, 'correspondencia_recibida/correspondenciaRecibida.html', {'model':'correspondenciarecibida','app':'correspondencia_recibida'} )

@login_required
def miscorrespondencia(request):
	return render(request, 'correspondencia_recibida/correspondencia.html', {'model':'correspondenciarecibida','app':'correspondencia_recibida'} )

@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			archivo = CorrespondenciaRecibidaSoporte.objects.get(pk=request.GET['id'])
			
			filename = ""+str(archivo.soporte)+""
			extension = filename[filename.rfind('.'):]
			nombre = re.sub('[^A-Za-z0-9 ]+', '', archivo.nombre)
			return functions.exportarArchivoS3(str(archivo.soporte),  nombre + extension)

		except Exception as e:
			functions.toLog(e,'correspondencia_recibida.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

			