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
from .models import CesionV, DetalleCesionV
from contrato.models import Contrato
from contrato.views import ContratoSerializer
from empresa.models import Empresa
from empresa.views import EmpresaSerializer
from giros.models import CNombreGiro,DEncabezadoGiro,DetalleGiro
from contrato.models import Contrato,VigenciaContrato
from giros.views import NombreGiroSerializer
from parametrizacion.models import Banco
from parametrizacion.views import BancoSerializer
from tipo.models import Tipo
from tipo.views import TipoSerializer
from estado.views import EstadoSerializer
from estado.models import Estado
from .enum import enumEstados
from logs.models import Logs,Acciones
from django.db import connection
from datetime import *
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required
from sinin4.functions import functions
import time
import xlsxwriter
from adminMail.models import Mensaje
from adminMail.tasks import sendAsyncMail
from django.conf import settings
from django.db.models import F, FloatField, Sum
from rest_framework.decorators import api_view, throttle_classes

#Serialezer de empresa
class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Empresa
		fields=('id','nombre')


#Serialezer de empresa
class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):

	contratista = EmpresaLiteSerializer(read_only=True)
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	class Meta:
		model = Contrato
		fields=('id','nombre','contratista','contratista_id')

# Serializador de contrato
class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):

	contratista = EmpresaLiteSerializer(read_only=True)
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	mcontrato = ContratoLiteSerializer(read_only=True)
	mcontrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	class Meta:
		model = Contrato
		fields=('id','nombre','numero','contratista','contratista_id','mcontrato_id','mcontrato')




#Api rest para la cesion economica
class CesionVSerializer(serializers.HyperlinkedModelSerializer):

	contratista = EmpresaLiteSerializer(read_only=True)
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='CesionV2'),allow_null=True)
	
	class Meta:
		model = CesionV
		fields=('id','contratista','contratista_id','estado','estado_id','fecha_carta','soporte_solicitud','cantidad_detalle','detalle_contrato')



class CesionV2ViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de cesion economica.
	"""
	model=CesionV
	queryset = model.objects.all()
	serializer_class = CesionVSerializer
	nombre_modulo='cesion_V2'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:

			queryset = super(CesionV2ViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			mcontrato= self.request.query_params.get('mcontrato',None)
			contrato= self.request.query_params.get('contrato',None)
			contratista= self.request.query_params.get('contratista',None)
			estado= self.request.query_params.get('estado',None)
			desde= self.request.query_params.get('desde',None)
			hasta= self.request.query_params.get('hasta',None)
			sin_paginacion=self.request.query_params.get('sin_paginacion',None)
			id_empresa = request.user.usuario.empresa.id
			qset=''

			qset=(~Q(id=0))

			if contrato:
				con = DetalleCesionV.objects.filter(contrato__id=contrato).values('cesion__id')

				if con:
					qset = qset &(Q(id__in=con))


			if mcontrato:
				mcon = DetalleCesionV.objects.filter(contrato__mcontrato__id=mcontrato).values('cesion__id')

				if mcon:
					qset = qset &(Q(id__in=mcon))


			if id_empresa:
				emp = DetalleCesionV.objects.filter(contrato__empresacontrato__empresa__id=id_empresa).values('cesion__id')

				if emp:
					qset = qset &(Q(id__in=emp))


			if contratista and int(contratista)>0:
				qset =qset &(
					Q(contratista__id=contratista)
					)


			if estado and int(estado)>0:
				qset =qset &(
					Q(estado__id=estado)
					)


			if (desde and (hasta is not None)):

				qset = qset & (Q(fecha_carta__gte=desde))

			if(desde and hasta):
				qset = qset &(Q(fecha_carta__gte=desde) and Q(fecha_carta__lte=hasta))


			if dato:

				qset = qset & (Q(contratista__nombre__icontains=dato))


			if qset != '':
				queryset = self.model.objects.filter(qset).order_by('-fecha_carta')

			if sin_paginacion is None:	
	
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					#print serializer
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
			print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()

			try:

				request.DATA['estado_id'] = enumEstados.en_verificacon

				serializer = CesionVSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					
					serializer.save(contratista_id=request.DATA['contratista_id'],
						estado_id=request.DATA['estado_id'],
						soporte_solicitud=request.FILES.get('archivo') if request.FILES.get('archivo') is not None else '')


					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cesionV',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)

				else:
					#print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				print(e)
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

				request.DATA['estado_id'] = enumEstados.en_verificacon


				serializer = CesionVSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(contratista_id=request.DATA['contratista_id'],
						estado_id=request.DATA['estado_id'])


					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cesion_v',id_manipulado=serializer.data['id'])
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

#Fin api rest para cesion economica




#Api rest para detalle de la cesion
class DetalleCesionSerializer(serializers.HyperlinkedModelSerializer):

	cesion_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=CesionV.objects.all())
	cesion=CesionVSerializer(read_only=True)

	contrato = ContratoLiteSerializer(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	nombre_giro_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=CNombreGiro.objects.all())
	nombre_giro=NombreGiroSerializer(read_only=True)

	beneficiario = EmpresaLiteSerializer(read_only=True)
	beneficiario_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	banco_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Banco.objects.all())
	banco=BancoSerializer(read_only=True)

	tipo_cuenta = TipoSerializer(read_only=True)
	tipo_cuenta_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='cuenta'),allow_null=True,default=None)

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='CesionV2'),allow_null=True)
	

	class Meta:
		model = DetalleCesionV
		fields=('id','cesion','cesion_id','contrato','contrato_id','beneficiario','beneficiario_id','tipo_cuenta','tipo_cuenta_id','estado','estado_id',
			'nombre_giro_id','nombre_giro','banco_id','banco','numero_cuenta','valor','correo_verificacion','carta_rechazo_aprobacion')


class DetalleCesionViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de detalle de cesion.
	"""
	model=DetalleCesionV
	queryset = model.objects.all()
	serializer_class = DetalleCesionSerializer
	nombre_modulo='detalle_cesion'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:

			queryset = super(DetalleCesionViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion=self.request.query_params.get('sin_paginacion',None)
			id_empresa = request.user.usuario.empresa.id
			idcesion= self.request.query_params.get('idcesion',None)
			qset=''


			if idcesion and int(idcesion)>0:
				qset =(
					Q(cesion__id=idcesion)
					)

			else:

				qset=(~Q(id=0))


			# if id_empresa and int(id_empresa)>0:
			# 	qset =qset &(
			# 		Q(contrato__empresacontrato__empresa=id_empresa)
			# 		)

			if qset != '':
				queryset = self.model.objects.filter(qset)

			if sin_paginacion is None:	
	
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					#print serializer
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
			print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()

			try:

				request.DATA['estado_id'] = enumEstados.en_verificacon

				serializer = DetalleCesionSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					
					serializer.save(contrato_id=request.DATA['contrato_id'],cesion_id=request.DATA['cesion_id'],beneficiario_id=request.DATA['beneficiario_id'],
						tipo_cuenta_id=request.DATA['tipo_cuenta_id'],estado_id=request.DATA['estado_id'],
						banco_id=request.DATA['banco_id'],nombre_giro_id=request.DATA['nombre_giro_id'],
						correo_verificacion='',carta_rechazo_aprobacion='')


					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='detalle_cesion',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)

				else:
					#print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				print(e)
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

				request.DATA['estado_id'] = enumEstados.en_verificacon


				serializer = DetalleCesionSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(contrato_id=request.DATA['contrato_id'],cesion_id=request.DATA['cesion_id'],beneficiario_id=request.DATA['beneficiario_id'],
						tipo_cuenta_id=request.DATA['tipo_cuenta_id'],estado_id=request.DATA['estado_id'],
						banco_id=request.DATA['banco_id'],nombre_giro_id=request.DATA['nombre_giro_id'],
						correo_verificacion=request.FILES['correo_verificacion'] if request.FILES.get('correo_verificacion') is not None else '',
						carta_rechazo_aprobacion=request.FILES['carta_rechazo_aprobacion'] if request.FILES.get('carta_rechazo_aprobacion') is not None else '')

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='detalle_cesion',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
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

#Fin api rest para detalle de la cesion

#Verifica la solicitud
@transaction.atomic
@api_view(['POST'])
def verificacion_correo(request):

	sid = transaction.savepoint()

	try:

		respuesta= json.loads(request.POST['lista'])
		for item in respuesta:

			detal = DetalleCesionV.objects.filter(id=item['id'])

			if detal[0].estado.id ==147:

				verifi=DetalleCesionV.objects.get(pk=item['id'])
				verifi.correo_verificacion=request.FILES['archivo']
				verifi.estado_id=request.POST['estado']
				verifi.save()

		can_deta=DetalleCesionV.objects.filter(cesion_id=request.POST['cesion_id']).count()
		can_deta_est=DetalleCesionV.objects.filter(cesion_id=request.POST['cesion_id'], estado_id=request.POST['estado']).count()

		if can_deta == can_deta_est:

			ce=CesionV.objects.get(pk=request.POST['cesion_id'])
			ce.estado_id=request.POST['estado']
			ce.save()

		transaction.savepoint_commit(sid)
		return Response({'message':'los registros han sido actualizados exitosamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		
	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)


#Aprueba o rechaza las solicitudes
@transaction.atomic
@api_view(['POST'])
def aprobacion_rechazo(request):

	sid = transaction.savepoint()

	try:

		respuesta= json.loads(request.POST['lista'])
		for item in respuesta:

			detal = DetalleCesionV.objects.filter(id=item['id'])

			if detal[0].estado.id ==148:

				aproba=DetalleCesionV.objects.get(pk=item['id'])
				aproba.carta_rechazo_aprobacion=request.FILES['archivo']
				aproba.estado_id=request.POST['estado']
				aproba.save()

				encabezado = DEncabezadoGiro.objects.filter(contrato__id=detal[0].contrato.id,nombre__id=detal[0].nombre_giro.id)

				if encabezado:
					#print(e)ncabezado[0].id

					detalle=DetalleGiro(encabezado_id=encabezado[0].id,contratista_id=detal[0].beneficiario.id,
						banco_id=detal[0].banco.id,tipo_cuenta_id=detal[0].tipo_cuenta.id,
						valor_girar=detal[0].valor,no_cuenta=detal[0].numero_cuenta,
						estado_id=2,carta_autorizacion_id=None,cuenta_id=None,cruce_id=None,cesion_id=None,codigo_pago='')
					detalle.save()

				else:

					giros=DEncabezadoGiro(nombre_id=detal[0].nombre_giro.id,contrato_id=detal[0].contrato.id,pago_recurso_id=83)
					giros.save()

					detalle=DetalleGiro(encabezado_id=giros.id,contratista_id=detal[0].beneficiario.id,
						banco_id=detal[0].banco.id,tipo_cuenta_id=detal[0].tipo_cuenta.id,valor_girar=detal[0].valor,
						no_cuenta=detal[0].numero_cuenta,estado_id=2,carta_autorizacion_id=None,
						cuenta_id=None,cruce_id=None,cesion_id=None,codigo_pago='')
					detalle.save()


		if int(request.POST['estado']) == 149:
			can_deta=DetalleCesionV.objects.filter(cesion_id=request.POST['idcesion']).count()
			can_deta_apro=DetalleCesionV.objects.filter(cesion_id=request.POST['idcesion'], estado_id=149).count()

			if can_deta == can_deta_apro:

				ce=CesionV.objects.get(pk=request.POST['idcesion'])
				ce.estado_id=149
				ce.save()

			else:

				ce=CesionV.objects.get(pk=request.POST['idcesion'])
				ce.estado_id=151
				ce.save()

		else:

			can_detal=DetalleCesionV.objects.filter(cesion_id=request.POST['idcesion']).count()
			can_deta_rech=DetalleCesionV.objects.filter(cesion_id=request.POST['idcesion'], estado_id=150).count()

			if can_detal == can_deta_rech:

				ce=CesionV.objects.get(pk=request.POST['idcesion'])
				ce.estado_id=150
				ce.save()




		transaction.savepoint_commit(sid)
		return Response({'message':'los registros han sido actualizados exitosamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		
	except Exception as e:
		print(e)
		transaction.savepoint_rollback(sid)
		return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)



#Guardar cesion
@transaction.atomic
@api_view(['POST'])
def guardar_cesion(request):

	sid = transaction.savepoint()

	try:
		contratista = request.POST['contratista']
		fecha_carta = request.POST['fecha_carta']
		archivo = request.FILES['archivo']
		estado = request.POST['estado']

		cesio=CesionV(contratista_id=contratista,fecha_carta=fecha_carta,soporte_solicitud=archivo,estado_id=estado)
		cesio.save()

		respuesta= json.loads(request.POST['lista'])
		for item in respuesta:

			deta=DetalleCesionV(cesion_id=cesio.id, contrato_id=item['contrato']['id'],nombre_giro_id=item['nombre_giro']['id'],
				beneficiario_id=item['beneficiario']['id'],banco_id=item['banco']['id'],tipo_cuenta_id=item['tipo_cuenta']['id'],
				estado_id=item['estado']['id'],numero_cuenta=item['numero_cuenta']['numero'],
				valor=item['valor_cesion']['valor'])
			deta.save()

		notificacion_cesion(cesio.id)

		transaction.savepoint_commit(sid)
		return Response({'message':'los registros han sido actualizados exitosamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		
	except Exception as e:
		print(e)
		transaction.savepoint_rollback(sid)
		return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)




def notificacion_cesion(idcesion):
	mensaje=''
	status=''
	res=''
	
	try:
		cursor = connection.cursor()
		cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[48,])
		columns = cursor.description 
		LisCorreos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

		correo_envio=''
		for p in LisCorreos:
			if correo_envio=='':
				correo_envio=p['correo']+';'
			else:
				correo_envio=correo_envio+p['correo']+';'


		deta = DetalleCesionV.objects.filter(cesion_id=idcesion)
		cesion = CesionV.objects.get(id=idcesion)

		#inicio del codigo del envio de correo
		contenido='<h3>SININ - Sistema Integral de informacion</h3>'
		contenido = contenido + 'Buen dia,<br>'
		contenido = contenido + 'Se ha creado un registro de cesion economica en SININ, al contratista '+cesion.contratista.nombre+'.<br><br>'
		
		contenido = contenido + '<table border=2>'
		contenido = contenido + '<tr>'
		contenido = contenido + '<td>Contrato </td>'
		contenido = contenido + '<td>No. contrato </td>'
		contenido = contenido + '<td>Beneficiario</td>'
		contenido = contenido + '<td>Valor</td>'
		contenido = contenido + '</tr>'
		contenido = contenido + '<tbody>'

		for c in deta:
			contenido = contenido + '<tr>'

			contenido = contenido + '<td>'+c.contrato.nombre+'</td>'
			contenido = contenido + '<td>'+c.contrato.numero+'</td>'
			contenido = contenido + '<td>'+c.beneficiario.nombre+'</td>'
			contenido = contenido + '<td>'+str(c.valor)+'</td>'

			contenido = contenido + '</tr>'

		contenido = contenido + '</tbody>'
		contenido = contenido + '</table>'

		#print contenido

		contenido = contenido + '<br>No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
		contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
		mail = Mensaje(
			remitente=settings.REMITENTE,
			destinatario=correo_envio,
			asunto='informativo de SININ',
			contenido=contenido,
			appLabel='Usuario',
			)			
		mail.save()
		res=sendAsyncMail(mail)
		mensaje='Notificacion de cesion economica.'
		status='ok'			
			
	except Exception as e:
		# print 'entro'
		# print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)	


#funcion para validar
def validacion_cesion(request):

	try:
		contrato = request.GET['contrato']
		valor_ces = request.GET['valor']
		suma = 0
		total=0
		valor_detalle=0

		vigencia = VigenciaContrato.objects.get(contrato__id = contrato, tipo__id=20)
		encabezado = DEncabezadoGiro.objects.filter(contrato__id = contrato)
		detalle=DetalleCesionV.objects.filter(contrato__id = contrato).aggregate(suma_cesiones=Sum('valor'))

		if detalle['suma_cesiones']:
			valor_detalle=detalle['suma_cesiones']

		for item in encabezado:

			valor_detalle=DetalleGiro.objects.filter(encabezado__id=item.id).aggregate(suma_ingreso=Sum('valor_girar'))

			suma = suma + valor_detalle['suma_ingreso']

		if valor_detalle == 0:

			total = vigencia.valor - float(valor_ces)
		else:

			total = vigencia.valor - suma - float(valor_ces)

		return JsonResponse({'message':'','success':'ok','data':total})	

	except Exception as e:
		#print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)	



#exportar las cesiones
def export_excel_cesiones(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="listado_cesiones.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Cesiones')
	format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
	format2=workbook.add_format({'border':0})
	format3=workbook.add_format({'border':0,'font_size':12})
	format5=workbook.add_format()
	format5.set_num_format('yyyy-mm-dd')

	row=1
	col=0

	cursor = connection.cursor()

	id_empresa = request.user.usuario.empresa.id
	qset=None

	qset = (Q(contrato__empresacontrato__empresa__id=id_empresa))

	detalle = DetalleCesionV.objects.filter(qset)

	worksheet.write('A1', 'Mcontrato', format1)
	worksheet.write('B1', 'Contrato', format1)
	worksheet.write('C1', 'Contratista', format1)
	worksheet.write('D1', 'Beneficiario', format1)
	worksheet.write('E1', 'Nombre giro', format1)
	worksheet.write('F1', 'Banco', format1)
	worksheet.write('G1', 'Numero cuenta', format1)
	worksheet.write('H1', 'Tipo cuenta', format1)
	worksheet.write('I1', 'Valor', format1)
	worksheet.write('J1', 'Estado', format1)

	for d in detalle:

		worksheet.write(row, col,d.contrato.mcontrato.nombre,format2)
		worksheet.write(row, col+1,d.contrato.nombre,format2)
		worksheet.write(row, col+2,d.cesion.contratista.nombre,format2)
		worksheet.write(row, col+3,d.beneficiario.nombre,format2)
		worksheet.write(row, col+4,d.nombre_giro.nombre,format2)
		worksheet.write(row, col+5,d.banco.nombre,format2)
		worksheet.write(row, col+6,d.numero_cuenta,format2)
		worksheet.write(row, col+7,d.tipo_cuenta.nombre,format2)
		worksheet.write(row, col+8,d.valor,format2)
		worksheet.write(row, col+9,d.estado.nombre,format2)
	
		row +=1


	workbook.close()

	return response
    #return response


@login_required
def listado_nombre_giro(request):

	try:

		contrato= request.GET['contrato']
		qset = None

		giro = DEncabezadoGiro.objects.filter(contrato=contrato)

		lista_datos=[]

		for item in giro:

			lista_datos.append(
				{	
					'id':item.nombre.id,
					'nombre':item.nombre.nombre					
				}
			)

		return JsonResponse({'message':'','success':'ok','data':lista_datos})
		
	except Exception as e:
		#print(e)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})


@login_required
def cesion_v2(request):

	con_verif=CesionV.objects.filter(estado_id=147).count()
	con_tramit=CesionV.objects.filter(estado_id=148).count()
	con_aprob=CesionV.objects.filter(estado_id=149).count()
	con_recha=CesionV.objects.filter(estado_id=150).count()
	con_parcia=CesionV.objects.filter(estado_id=151).count()

	return render(request, 'cesionv/cesionv.html',{'con_verif':con_verif,'con_tramit':con_tramit,'con_aprob':con_aprob,'con_recha':con_recha,'con_parcia':con_parcia,'app':'cesion_v2','model':'cesionv'})


@login_required
def detalle_cesion(request,id_cesion=None):
	return render(request, 'cesionv/detalle_cesion.html',{'app':'cesion_v2','model':'cesionv','id_cesion':id_cesion})		


@login_required
def detalle_proceso(request,id_cesion=None):

	con_tramit=DetalleCesionV.objects.filter(cesion_id=id_cesion,estado_id=148).count()
	
	return render(request, 'cesionv/detalle_proceso.html',{'con_tramit':con_tramit,'app':'cesion_v2','model':'cesionv','id_cesion':id_cesion})		


@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			archivo = CesionV.objects.get(pk=request.GET['id'])
			return functions.exportarArchivoS3(str(archivo.soporte_solicitud))

		except Exception as e:
			functions.toLog(e,'cesionv.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
def VerSoporteDetalle(request):
	if request.method == 'GET':
		try:
			
			tipo = request.GET['tipo']
			archivo = DetalleCesionV.objects.get(pk=request.GET['id'])
			if tipo == 'correo_verificacion':
				return functions.exportarArchivoS3(str(archivo.correo_verificacion))
			elif tipo == 'carta_rechazo_aprobacion':
				return functions.exportarArchivoS3(str(archivo.carta_rechazo_aprobacion))

		except Exception as e:
			functions.toLog(e,'cesionv.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
