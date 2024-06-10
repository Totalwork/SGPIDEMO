from django.shortcuts import render,redirect
#,render_to_response
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
from .models import CesionEconomica
from giros.models import DEncabezadoGiro,DetalleGiro
from contrato.models import Contrato,VigenciaContrato
from contrato.views import ContratoSerializer
from empresa.models import Empresa
from empresa.views import EmpresaSerializer
from giros.models import CNombreGiro,DEncabezadoGiro,DetalleGiro
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
from coasmedas.functions import functions
import time
from adminMail.models import Mensaje
from adminMail.tasks import sendAsyncMail
from django.conf import settings
from django.db.models import F, FloatField, Sum


#Serialezer de empresa
class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Contrato
		fields=('id','nombre')

#Serialezer de empresa
class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Empresa
		fields=('id','nombre')

# Serializador de contrato
class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):

	contratista = EmpresaLiteSerializer(read_only=True)
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	mcontrato = ContratoLiteSerializer(read_only=True)
	mcontrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	class Meta:
		model = Contrato
		fields=('id','nombre','numero','contratista','contratista_id','mcontrato_id','mcontrato',)


#Api rest para la cesion economica
class CesionEconomicaSerializer(serializers.HyperlinkedModelSerializer):

	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Contrato.objects.all())
	contrato=ContratoLiteSerializer(read_only=True)

	proveedor = EmpresaLiteSerializer(read_only=True)
	proveedor_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	tipo_cuenta = TipoSerializer(read_only=True)
	tipo_cuenta_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='cuenta'),allow_null=True,default=None)

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='CesionEconomica'),allow_null=True)
	
	nombre_giro_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=CNombreGiro.objects.all())
	nombre_giro=NombreGiroSerializer(read_only=True)

	banco_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Banco.objects.all())
	banco=BancoSerializer(read_only=True)


	class Meta:
		model = CesionEconomica
		fields=('id','contrato','contrato_id','proveedor','proveedor_id','tipo_cuenta','tipo_cuenta_id','estado','estado_id',
			'nombre_giro_id','nombre_giro','banco_id','banco','numero_cuenta','motivo_rechazo','valor','soporte_tramite','fecha_tramite',
			'soporte_enaprobacion','fecha_enaprobacion','soporte_aprobado','fecha_aprobada')


class CesionEconomicaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de cesion economica.
	"""
	model=CesionEconomica
	queryset = model.objects.all()
	serializer_class = CesionEconomicaSerializer
	nombre_modulo='cesion_economica'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:

			queryset = super(CesionEconomicaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			mcontrato= self.request.query_params.get('mcontrato',None)
			contrato= self.request.query_params.get('contrato',None)
			contratista= self.request.query_params.get('contratista',None)
			estado= self.request.query_params.get('estado',None)
			sin_paginacion=self.request.query_params.get('sin_paginacion',None)
			id_empresa = request.user.usuario.empresa.id
			idcesion= self.request.query_params.get('idcesion',None)
			qset=''


			if idcesion and int(idcesion)>0:
				qset =(
					Q(id=idcesion)
					)

			else:

				qset=(~Q(id=0))


			if id_empresa and int(id_empresa)>0:
				qset =qset &(
					Q(contrato__empresacontrato__empresa=id_empresa)
					)


			if mcontrato and int(mcontrato)>0:
				qset =qset &(
					Q(contrato__mcontrato__id=mcontrato)
					)

			
			if contrato and int(contrato)>0:
				qset =qset &(
					Q(contrato__id=contrato)
					)


			if contratista and int(contratista)>0:
				qset =qset &(
					Q(contrato__contratista__id=contratista)
					)


			if estado and int(estado)>0:
				qset =qset &(
					Q(estado__id=estado)
					)

			if dato:

				qset = qset & (Q(proveedor__nombre__icontains=dato) | Q(contrato__nombre__icontains=dato) | Q(contrato__numero__icontains=dato) )


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

				request.DATA['estado_id'] = enumEstados.tramite

				serializer = CesionEconomicaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					
					serializer.save(contrato_id=request.DATA['contrato_id'],proveedor_id=request.DATA['proveedor_id'],
						tipo_cuenta_id=request.DATA['tipo_cuenta_id'],estado_id=request.DATA['estado_id'],
						banco_id=request.DATA['banco_id'],nombre_giro_id=request.DATA['nombre_giro_id'],
						soporte_tramite=request.FILES.get('archivo') if request.FILES.get('archivo') is not None else '',
						soporte_enaprobacion='',soporte_aprobado='')


					notificacion_tramite(serializer.data['id'])


					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cesion',id_manipulado=serializer.data['id'])
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

				request.DATA['estado_id'] = enumEstados.tramite

				serializer = CesionEconomicaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					if self.request.FILES.get('archivo') is not None:
					
						serializer.save(contrato_id=request.DATA['contrato_id'],proveedor_id=request.DATA['proveedor_id'],
							tipo_cuenta_id=request.DATA['tipo_cuenta_id'],estado_id=request.DATA['estado_id'],
							banco_id=request.DATA['banco_id'],nombre_giro_id=request.DATA['nombre_giro_id'],
							soporte_tramite=request.FILES.get('archivo') if request.FILES.get('archivo') is not None else '',
							soporte_enaprobacion=request.FILES['soporte_enaprobacion'] if request.FILES.get('soporte_enaprobacion') is not None else '',
							soporte_aprobado=request.FILES['soporte_aprobado'] if request.FILES.get('soporte_aprobado') is not None else '')

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cesion.economica',id_manipulado=serializer.data['id'])
						logs_model.save()

					else:

						cesion=self.model.objects.get(pk=instance.id)
						
						serializer.save(contrato_id=request.DATA['contrato_id'],proveedor_id=request.DATA['proveedor_id'],
							tipo_cuenta_id=request.DATA['tipo_cuenta_id'],estado_id=request.DATA['estado_id'],
							banco_id=request.DATA['banco_id'],nombre_giro_id=request.DATA['nombre_giro_id'],
							soporte_tramite=cesion.soporte_tramite,
							soporte_enaprobacion=request.FILES['soporte_enaprobacion'] if request.FILES.get('soporte_enaprobacion') is not None else '',
							soporte_aprobado=request.FILES['soporte_aprobado'] if request.FILES.get('soporte_aprobado') is not None else '')


						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cesion.economica',id_manipulado=serializer.data['id'])
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

#Fin api rest para cesion economica

#Actualiza en aprobacion
@transaction.atomic
def actualizar_enaprobacion(request):

	sid = transaction.savepoint()
	try:

		fecha = time.strftime("%Y-%m-%d")

		cesion=CesionEconomica.objects.get(pk=request.POST['id'])
		cesion.soporte_enaprobacion=request.FILES['archivo']
		cesion.estado_id=enumEstados.aprobacion
		cesion.fecha_enaprobacion=fecha
		cesion.save()

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cesion_economica.cesion_economica',id_manipulado=request.POST['id'])
		logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':''})
		
	except Exception as e:
		#print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Actualiza a anulada
@transaction.atomic
def actualizar_anulada(request):

	sid = transaction.savepoint()
	try:

		lista=request.POST['_content']
		respuesta= json.loads(lista)		
		id = respuesta['id']
		banco = respuesta['banco']
		proveedor = respuesta['proveedor']
		tipo_cuenta = respuesta['tipo_cuenta']
		numero_cuenta = respuesta['numero_cuenta']
		contratoid = respuesta['contratoid']
		nombregiro = respuesta['nombregiro']

		cesion=CesionEconomica.objects.get(pk=id)
		cesion.estado_id=enumEstados.anulada
		cesion.save()

		encabezado = DEncabezadoGiro.objects.filter(contrato__id=contratoid,nombre__id=nombregiro)

		if encabezado:

			detalle=DetalleGiro.objects.get(encabezado_id=encabezado[0].id,banco_id=banco,
				contratista_id=proveedor,tipo_cuenta_id=tipo_cuenta,no_cuenta=numero_cuenta)
			detalle.estado_id=140
			detalle.save()

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cesion_economica.cesion_economica',id_manipulado=id)
		logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro ha sido anulado exitosamente','success':'ok','data':''})
		
	except Exception as e:
		print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#Actualiza a rechazado
@transaction.atomic
def actualizar_rechazado(request):

	sid = transaction.savepoint()
	try:

		lista=request.POST['_content']
		respuesta= json.loads(lista)		
		id = respuesta['id']

		cesion=CesionEconomica.objects.get(pk=id)
		cesion.estado_id=enumEstados.rechazado
		cesion.motivo_rechazo=respuesta['motivo']
		cesion.save()

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cesion_economica.cesion_economica',id_manipulado=id)
		logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro ha sido rechazado exitosamente','success':'ok','data':''})
		
	except Exception as e:
		#print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)





#Actualiza en aprobada
@transaction.atomic
def actualizar_aprobada(request):

	sid = transaction.savepoint()
	try:

		fecha = time.strftime("%Y-%m-%d")

		cesion=CesionEconomica.objects.get(pk=request.POST['id'])
		cesion.soporte_aprobado=request.FILES['archivo']
		cesion.estado_id=enumEstados.aprobada
		cesion.fecha_aprobada=fecha

		if request.POST['observacion']:

			cesion.observacion = request.POST['observacion']

		cesion.save()

		encabezado = DEncabezadoGiro.objects.filter(contrato__id=request.POST['contratoid'],nombre__id=request.POST['nombregiro'])

		if encabezado:
			#print(e)ncabezado[0].id

			detalle=DetalleGiro(encabezado_id=encabezado[0].id,contratista_id=request.POST['proveedor'],banco_id=request.POST['banco'],
				tipo_cuenta_id=request.POST['tipo_cuenta'],valor_girar=request.POST['valor'],no_cuenta=request.POST['numero_cuenta'],
				estado_id=2,carta_autorizacion_id=None,cuenta_id=None,cruce_id=None,cesion_id=None,codigo_pago='')
			detalle.save()

		else:
			giros=DEncabezadoGiro(nombre_id=request.POST['nombregiro'],contrato_id=request.POST['contratoid'],pago_recurso_id=83)
			giros.save()

			detalle=DetalleGiro(encabezado_id=giros.id,contratista_id=request.POST['proveedor'],banco_id=request.POST['banco'],
				tipo_cuenta_id=request.POST['tipo_cuenta'],valor_girar=request.POST['valor'],no_cuenta=request.POST['numero_cuenta'],
				estado_id=2,carta_autorizacion_id=None,cuenta_id=None,cruce_id=None,cesion_id=None,codigo_pago='')
			detalle.save()

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cesion_economica.cesion_economica',id_manipulado=request.POST['id'])
		logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro ha sido aprobado exitosamente','success':'ok','data':''})
		
	except Exception as e:
		print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#funcion para validar
def validacion_aprobada(request):

	try:
		contrato = request.GET['contrato']
		suma = 0
		total=0

		vigencia = VigenciaContrato.objects.get(contrato__id = contrato, tipo__id=20)
		encabezado = DEncabezadoGiro.objects.filter(contrato__id = contrato)
		cesiones=CesionEconomica.objects.filter(contrato__id = contrato).aggregate(suma_cesiones=Sum('valor'))

		for item in encabezado:

			valor_detalle=DetalleGiro.objects.filter(encabezado__id=item.id).aggregate(suma_ingreso=Sum('valor_girar'))

			suma = suma + valor_detalle['suma_ingreso']

		total = vigencia.valor - suma - cesiones['suma_cesiones']

		return JsonResponse({'message':'','success':'ok','data':total})	

	except Exception as e:
		#print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)	



def notificacion_tramite(idcesion):
	mensaje=''
	status=''
	res=''
	
	try:

		cesion = CesionEconomica.objects.get(id=idcesion)

		#inicio del codigo del envio de correo
		contenido='<h3>SININ - Sistema Integral de informacion</h3>'
		contenido = contenido + 'Buen dia,'
		contenido = contenido + 'Se ha creado un registro de cesion economica en SININ, por valor de $'+str(cesion.valor)+' en favor del proveedor '+str(cesion.proveedor.nombre)+', asociado al contrato No.'+str(cesion.contrato.numero)+' del macrocontrato '+str(cesion.contrato.mcontrato.nombre)+'.'
		contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
		contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
		mail = Mensaje(
			remitente=settings.REMITENTE,
			destinatario='danny-daniel1991@hotmail.com',
			asunto='informativo de SININ',
			contenido=contenido,
			appLabel='Usuario',
			)			
		mail.save()
		res=sendAsyncMail(mail)
		mensaje='Notificacion de cesion economica.'
		status='ok'			
			
	except Exception as e:
		#print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)	


@login_required
def cesion_economica(request):
	return render(request, 'cesion/cesion_economica.html',{'app':'cesion_economica','model':'cesioneconomica'})

