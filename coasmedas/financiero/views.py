from django.shortcuts import render,redirect,render_to_response
from django.urls import reverse
from rest_framework import viewsets, serializers
from django.db.models import Q,Sum
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
from tipo.models import Tipo
from tipo.views import TipoSerializer
from .models import FinancieroCuenta,FinancieroCuentaMovimiento,NExtracto
from contrato.models import Contrato, EmpresaContrato
from contrato.views import ContratoSerializer
from logs.models import Logs,Acciones
from django.db import connection
from datetime import *
from django.db import transaction
from django.db.models.deletion import ProtectedError
from empresa.models import Empresa
from empresa.views import EmpresaSerializer
from .enum import enumEstados
from estado.views import EstadoSerializer
from estado.models import Estado
from django.contrib.auth.decorators import login_required
from sinin4.functions import functions

from factura.models import Factura,DetalleCompensacion,Compensacion
from giros.models import DetalleGiro,DEncabezadoGiro
from multa.models import Solicitud,SolicitudHistorial
from contrato.enumeration import tipoC
from django.conf import settings

from proyecto.models import Proyecto

# Serializador de contrato
class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Contrato
		fields=('id','nombre', 'mcontrato')

	def get_fields(self):
		fields = super(ContratoLiteSerializer, self).get_fields()
		fields['mcontrato'] = ContratoLiteSerializer(read_only=True)
		return fields
		
#Api rest para financiero cuenta
class FinancieroCuentaSerializer(serializers.HyperlinkedModelSerializer):

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='EstadoCuenta'),allow_null=True)

	tipo = TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='cuenta'),allow_null=True,default=None)

	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Contrato.objects.all())
	contrato=ContratoLiteSerializer(read_only=True)

	empresa = EmpresaSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())
	soloLectura = serializers.SerializerMethodField()
	class Meta:
		model = FinancieroCuenta
		fields=('id','numero','nombre','valor','contrato','contrato_id','fiduciaria',
			'tipo','tipo_id','codigo_fidecomiso','codigo_fidecomiso_a','nombre_fidecomiso',
			'empresa','empresa_id','cantidad_movimiento','suma_ingreso','suma_egreso',
			'suma_rendimiento','estado','estado_id', 'soloLectura','fechaCorteMovimientos')

	def get_soloLectura(self, obj):
		request = self.context.get("request")
		if request is None:
			return False
		contrato = None
		if obj.contrato.mcontrato:
			contrato = obj.contrato.mcontrato.id
		else:
			contrato = obj.contrato.id

		empresaContrato = EmpresaContrato.objects.filter(contrato__id=contrato, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		return soloLectura		
			
class FinancieroCuentaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista las cuentas del finaciero.
	"""
	model=FinancieroCuenta
	queryset = model.objects.all()
	serializer_class = FinancieroCuentaSerializer
	nombre_modulo='financiero.cuenta'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(FinancieroCuentaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			mcontrato= self.request.query_params.get('mcontrato',None)
			sin_paginacion = self.request.query_params.get('sin_paginacion', None)
			cuenta_id= self.request.query_params.get('cuenta_id',None)
			id_empresa = request.user.usuario.empresa.id
			estado= self.request.query_params.get('estado',None)
			qset=''

			qset = (Q(empresa__id=id_empresa))

			#qset = qset & (Q(estado__id=enumEstados.Activo))

			if dato:
				qset = qset & (
					Q(numero__icontains=dato) | Q(nombre__icontains=dato) | Q(contrato__nombre__icontains=dato)
					)

			if mcontrato and int(mcontrato)>0:
				qset = qset & (Q(contrato__id=mcontrato))

			if cuenta_id:
				qset = qset & (Q(id=cuenta_id))


			if estado and int(estado)>0:
				qset = qset & (Q(estado__id=estado))


			if qset != '':
				queryset = self.model.objects.filter(qset).order_by('-id')


			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
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
			#print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = FinancieroCuentaSerializer(data=request.DATA,context={'request': request})

				id_empresa = request.user.usuario.empresa.id
				request.DATA['estado_id']=enumEstados.Activo

				if serializer.is_valid():

					finan=FinancieroCuenta.objects.filter(contrato__id=request.DATA['contrato_id'], estado__id=request.DATA['estado_id']).values('id')

					if len(finan)<=0:

						serializer.save(estado_id=request.DATA['estado_id'],tipo_id=request.DATA['tipo_id'] if request.DATA['tipo_id'] is not None else None ,contrato_id=request.DATA['contrato_id'],empresa_id=request.DATA['empresa_id'])

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='finaciero.cuenta',id_manipulado=serializer.data['id'])
						logs_model.save()

						transaction.savepoint_commit(sid)

						return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)

					else:

						return JsonResponse({'message':'Se encontro una cuenta activa del contrato','success':'error','data':''})	

				else:
					#print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				#print(e)
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
				serializer = FinancieroCuentaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(tipo_id=self.request.query_params.get('tipo_id',None),contrato_id=request.DATA['contrato_id'],empresa_id=request.DATA['empresa_id'],estado_id=request.DATA['estado_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='financiero.cuenta',id_manipulado=serializer.data['id'])
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


#Fin api rest para financiero cuenta

#Serialezer de empresa
class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Empresa
		fields=('id','nombre')

#Serialezer FinancieroCuentaSerializer
class FinancieroLiteCuentaSerializer(serializers.HyperlinkedModelSerializer):

	empresa = EmpresaLiteSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	class Meta:
		model = FinancieroCuenta
		fields=('id','nombre','empresa','empresa_id')

#Api rest para financiero cuenta movimiento
class FinancieroCuentaMovimientoSerializer(serializers.HyperlinkedModelSerializer):

	tipo = TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='TipoFinacieroCuentaMovimiento'))

	cuenta_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=FinancieroCuenta.objects.all())
	cuenta=FinancieroLiteCuentaSerializer(read_only=True)

	bloquear = serializers.BooleanField(default=False)
	
	class Meta:
		model = FinancieroCuentaMovimiento
		fields=('id','cuenta','cuenta_id','tipo_id','tipo','valor',
			'descripcion','fecha','periodo_inicio','periodo_final','ano','bloquear')


class FinancieroCuentaMovimientoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de movientos de las cuentas del financiero.
	"""
	model=FinancieroCuentaMovimiento
	queryset = model.objects.all()
	serializer_class = FinancieroCuentaMovimientoSerializer
	nombre_modulo='financiero.cuentaMovimiento'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:

			queryset = super(FinancieroCuentaMovimientoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			desde= self.request.query_params.get('desde',None)
			hasta= self.request.query_params.get('hasta',None)
			tipo_filtro= self.request.query_params.get('tipo_filtro',None)
			cuenta_id= self.request.query_params.get('cuenta_id',None)
			sin_paginacion=self.request.query_params.get('sin_paginacion',None)
			id_empresa = request.user.usuario.empresa.id
			qset=''

			if (dato or desde or hasta or tipo_filtro or cuenta_id or id_empresa):

				qset = (Q(cuenta__empresa__id=id_empresa))
				
				if int(cuenta_id)>0:
					qset =qset &(
						Q(cuenta__id=cuenta_id)
						)

				if dato:
					qset = qset &(
						Q(descripcion__icontains=dato)
						)

				if int(tipo_filtro)>0:
					qset =qset &(
						Q(tipo__id=tipo_filtro)
						)		


				if (desde and (hasta is not None)):

						qset = qset & (
							Q(fecha__gte=desde)
							)

				if (hasta and (desde is not None)):

						qset = qset & (
							Q(fecha__lte=hasta)
							)

				if(desde and hasta):
						qset = qset &(
							Q(fecha__gte=desde) and Q(fecha__lte=hasta) 
						)


			#print qset
			if qset != '':
				queryset = self.model.objects.filter(qset).order_by('-fecha')

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
			#print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()

			try:
				serializer = FinancieroCuentaMovimientoSerializer(data=request.DATA,context={'request': request})

				# if request.DATA['desde'] =='' and request.DATA['hasta'] =='':
				# 	request.DATA['desde']=None
				# 	request.DATA['hasta']=None

				if serializer.is_valid():
					serializer.save(tipo_id=request.DATA['tipo_id'],cuenta_id=request.DATA['cuenta_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='finaciero.cuenta_movimiento',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					#print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				#print(e)
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
				serializer = FinancieroCuentaMovimientoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				# if request.DATA['desde'] =='' and request.DATA['hasta'] =='':
				# 	request.DATA['desde']=None
				# 	request.DATA['hasta']=None

				if serializer.is_valid():
					serializer.save(tipo_id=request.DATA['tipo_id'],cuenta_id=request.DATA['cuenta_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='financiero.cuenta_movimiento',id_manipulado=serializer.data['id'])
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



#Api rest para financiero cuenta movimiento
class ExtractoSerializer(serializers.HyperlinkedModelSerializer):

	cuenta_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=FinancieroCuenta.objects.all())
	cuenta=FinancieroLiteCuentaSerializer(read_only=True)
	
	class Meta:
		model = NExtracto
		fields=('id','cuenta','cuenta_id','mes','ano','soporte','nombre_mes')


class ExtractoCuentaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de movientos de las cuentas del financiero.
	"""
	model=NExtracto
	queryset = model.objects.all()
	serializer_class = ExtractoSerializer
	nombre_modulo='financiero.extracto'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:

			queryset = super(ExtractoCuentaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			cuenta_id= self.request.query_params.get('cuenta_id',None)
			mes= self.request.query_params.get('mes',None)
			ano= self.request.query_params.get('ano',None)
			sin_paginacion=self.request.query_params.get('sin_paginacion',None)
			qset=''

			
			qset=(~Q(id=0))
			if dato:
				qset = qset &(
					Q(cuenta__nombre__icontains=dato)
					)

			if cuenta_id is not None and int(cuenta_id)>0:
				qset=qset &(Q(cuenta_id=cuenta_id))

			if mes is not None and int(mes)>0:
				qset=qset &(Q(mes=mes))

			if ano is not None and int(ano)>0:
				qset=qset &(Q(ano=ano))


			#print qset
			if qset != '':
				queryset = self.model.objects.filter(qset).order_by('-ano','-mes')

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
			#print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()

			try:
				serializer = ExtractoSerializer(data=request.DATA,context={'request': request})

				validar_extracto=NExtracto.objects.filter(cuenta_id=request.DATA['cuenta_id'],mes=request.DATA['mes'],ano=request.DATA['ano'])
				if len(validar_extracto) == 0:
					if serializer.is_valid():
						serializer.save(cuenta_id=request.DATA['cuenta_id'],soporte=self.request.FILES.get('soporte'))

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='finaciero.extracto',id_manipulado=serializer.data['id'])
						logs_model.save()

						transaction.savepoint_commit(sid)

						return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)
					else:
						#print(serializer.errors)
						return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)
				else:
					return Response({'message':'El extracto ya esta registrado','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)


			except Exception as e:
				#print(e)
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
				serializer = ExtractoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				validar_extracto=NExtracto.objects.filter(cuenta_id=request.DATA['cuenta_id'],mes=request.DATA['mes'],ano=request.DATA['ano']).exclude(id=instance.id)

				if len(validar_extracto) == 0:

					if serializer.is_valid():
						valores=NExtracto.objects.get(id=instance.id)
						if self.request.FILES.get('soporte') is not None:
							serializer.save(cuenta_id=request.DATA['cuenta_id'],soporte=self.request.FILES.get('soporte'))
						else:
							serializer.save(cuenta_id=request.DATA['cuenta_id'],soporte=valores.soporte)

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='financiero.extracto',id_manipulado=serializer.data['id'])
						logs_model.save()

						transaction.savepoint_commit(sid)

						return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)
					else:
						#print(serializer.errors)
						return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
				 		'data':''},status=status.HTTP_400_BAD_REQUEST)
				else:
					return Response({'message':'El extracto ya esta registrado','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		try:
			instance = self.get_object()
			self.perform_destroy(instance)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)	


#Fin api rest para encabezado del giro
@login_required
def financiero_cuenta(request):
		return render(request, 'financiero_cuenta/cuenta.html',{'app':'financiero','model':'financierocuenta'})


@login_required
def financiero_movimiento(request,id_cuenta=None):

		return render(request, 'financiero_cuenta/movimiento_cuenta.html',{'app':'financiero','model':'financierocuentamovimiento','id_cuenta':id_cuenta})		


#eliminar cuentas del financiero
@transaction.atomic
def eliminar_varios_id(request):
	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			FinancieroCuenta.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='financiero.cuenta',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})

	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})
		
	except Exception as e:
		#print(e)
		functions.toLog(e,self.nombre_modulo)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})			 
		


#eliminar movientos de la cuenta del financiero
@transaction.atomic
def eliminar_varios_id_movimiento(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			FinancieroCuentaMovimiento.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='financiero.cuenta_movimiento',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})	
		
	except Exception as e:
		functions.toLog(e,self.nombre_modulo)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})


#exportar los datos de las cuenta del financiero ya sea por parametro mcontrato o por id_empresa
def export_excel_cuenta(request):
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="cuenta.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Cuenta')
	format1=workbook.add_format({'border':1,'font_size':15,'bold':True})
	format2=workbook.add_format({'border':1})
	format3=workbook.add_format({'num_format': '$#,##0', 'border':1})

	worksheet.set_column('A:C',20)
	worksheet.set_column('D:D',18)
	worksheet.set_column('E:H',30)
	worksheet.set_column('I:I',20)
	worksheet.set_column('J:J',15)

	row=1
	col=0

	

	mcontrato= request.GET['mcontrato']
	id_empresa = request.user.usuario.empresa.id

	if (int(mcontrato)>0 or int(id_empresa)>0):
		
		if (int(id_empresa)>0):
			qset=	(Q(empresa__id=id_empresa))
		

		if (int(mcontrato)>0):

			qset = qset &(Q(contrato_id=mcontrato))
				
		cuenta = FinancieroCuenta.objects.filter(qset)
		worksheet.write('A1', 'Fiduciaria', format1)
		worksheet.write('B1', 'Banco', format1)
		worksheet.write('C1', 'Tipo de cuenta', format1)
		worksheet.write('D1', 'No. de cuenta', format1)
		worksheet.write('E1', 'Contrato Air-e --> MME', format1)
		worksheet.write('F1', 'Departamento', format1)
		worksheet.write('G1', 'Municipio', format1)
		worksheet.write('H1', 'Nombre del proyecto', format1)
		worksheet.write('I1', 'Saldo', format1)
		worksheet.write('J1', 'Corte', format1)

		# worksheet.write('A1', 'Contrato', format1)
		# worksheet.write('B1', 'Nombre cuenta', format1)
		# worksheet.write('C1', 'Numero cuenta', format1)
		# worksheet.write('D1', 'Banco', format1)
		# worksheet.write('E1', 'Saldo', format1)
		# worksheet.write('F1', 'Corte', format1)

		dpto = ''
		mun = ''
		proy = ''
		for cuentas in cuenta:
			#import pdb; pdb.set_trace()
			worksheet.write(row, col,'Corficolombiana',format2)
			worksheet.write(row, col+1,cuentas.fiduciaria,format2)
			worksheet.write(row, col+2,cuentas.tipo.nombre,format2)
			worksheet.write(row, col+3,cuentas.numero,format2)
			worksheet.write(row, col+4,cuentas.contrato.nombre,format2)

			proyectos = Proyecto.objects.filter(
				mcontrato__id=cuentas.contrato.id
				).values(
				'municipio__departamento__nombre',
				'municipio__nombre',
				'nombre')
			if proyectos:
				sep = ''
				dpto = ''
				mun = ''
				proy = ''
				for proyecto in proyectos:
					dpto = dpto + sep + proyecto['municipio__departamento__nombre']
					mun = mun + sep + proyecto['municipio__nombre']
					proy = proy + sep + proyecto['nombre']
					sep = ' | '
			
			
			worksheet.write(row, col+5, dpto, format2)
			worksheet.write(row, col+6, mun, format2)
			worksheet.write(row, col+7, proy, format2)

			ingresos = cuentas.suma_ingreso if cuentas.suma_ingreso else 0
			rendimientos = cuentas.suma_rendimiento if cuentas.suma_rendimiento else 0
			egresos = cuentas.suma_egreso if cuentas.suma_egreso else 0

			saldo = ingresos + rendimientos - egresos
			worksheet.write(row, col+8,saldo,format3)

			worksheet.write(row,col+9,cuentas.fechaCorteMovimientos,format2)

			row +=1


	workbook.close()

	return response
    #return response



#exportar los datos de los movimientos de la cuenta del financiero por fechas
def export_excel_movimiento(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="movimientos.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Movimientos')

	format1=workbook.add_format({'border':0,'font_size':12,'bold':True})

	format2=workbook.add_format({'border':0})
	format2.set_text_wrap()

	format3=workbook.add_format({'border':0,'font_size':12})

	format5=workbook.add_format()
	format5.set_num_format('yyyy-mm-dd')

	format6 = workbook.add_format({'num_format': '$#,##0.00'})

	worksheet.set_column('A:A', 15)
	worksheet.set_column('B:C', 25)
	worksheet.set_column('D:D', 40)

	row=1
	col=0

	# cursor = connection.cursor()
	# import pdb; pdb.set_trace()

	desde= request.GET['desde'] if 'desde' in request.GET else None
	hasta= request.GET['hasta'] if 'hasta' in request.GET else None
	tipo_filtro = request.GET['tipo_filtro'] if 'tipo_filtro' in request.GET else None
	cuenta_id=request.GET['cuenta_id'] if 'cuenta_id' in request.GET else None
	id_empresa = request.user.usuario.empresa.id

	qset = (Q(cuenta__empresa__id=id_empresa))
	if int(cuenta_id)>0:
		qset =qset &(
			Q(cuenta__id=cuenta_id)
			)

	if int(tipo_filtro)>0:
		qset =qset &(
			Q(tipo__id=tipo_filtro)
			)

	if (desde and (hasta is not None)):
		qset = qset & (
			Q(fecha__gte=desde)
			)

	if (hasta and (desde is not None)):
		qset = qset & (
			Q(fecha__lte=hasta)
			)

	if(desde and hasta):
		qset = qset &(
			Q(fecha__gte=desde) and Q(fecha__lte=hasta) 
		)

				
	movimiento_cuenta = FinancieroCuentaMovimiento.objects.filter(qset).order_by('-fecha')

	worksheet.write('A1', 'Fecha', format1)
	worksheet.write('B1', 'Valor', format1)
	worksheet.write('C1', 'Tipo', format1)
	worksheet.write('D1', 'Descripcion', format1)

	for movimiento_cuenta in movimiento_cuenta:
		valor = movimiento_cuenta.valor if movimiento_cuenta.valor else ''
		worksheet.write(row, col,movimiento_cuenta.fecha if movimiento_cuenta.fecha else '',format5)
		worksheet.write(row, col+1,-valor if valor != '' and movimiento_cuenta.tipo.id ==  29 else valor,format6)
		worksheet.write(row, col+2,movimiento_cuenta.tipo.nombre if movimiento_cuenta.tipo else '',format2)
		worksheet.write(row, col+3,movimiento_cuenta.descripcion if movimiento_cuenta.descripcion else '',format2)
	
		row +=1


	workbook.close()

	return response
    #return response


#actualiza el campo estado de la tabla cuenta
@transaction.atomic
def actualizar_estado_cuenta(request):

	sid = transaction.savepoint()

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		estado= respuesta['estado']

		for item in respuesta['lista']:
			object_cuenta=FinancieroCuenta.objects.get(pk=item['id'])

			object_cuenta.estado_id=estado
			object_cuenta.save()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='financiero.cuenta',id_manipulado=item['id'])
			logs_model.save()

			transaction.savepoint_commit(sid)

		return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok',
				'data':''})
		
	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})


def Financiero_encabezado (request):
	try:
		# import pdb; pdb.set_trace()
		cuenta_id= request.GET['cuenta_id'] if 'cuenta_id' in request.GET else None
		desde= request.GET['desde'] if 'desde' in request.GET else None
		hasta= request.GET['hasta'] if 'hasta' in request.GET else None
		tipo_filtro= request.GET['tipo_filtro'] if 'tipo_filtro' in request.GET else None
		id_empresa = request.user.usuario.empresa.id

		if cuenta_id:
			objCuenta = FinancieroCuenta.objects.get(pk=cuenta_id)

			qset = (Q(cuenta__empresa__id=id_empresa))
			if int(cuenta_id)>0:
				qset =qset &(
					Q(cuenta__id=cuenta_id)
					)

			if int(tipo_filtro)>0:
				qset =qset &(
					Q(tipo__id=tipo_filtro)
					)

			if (desde and (hasta is not None)):
				qset = qset & (
					Q(fecha__gte=desde)
					)

			if (hasta and (desde is not None)):
				qset = qset & (
					Q(fecha__lte=hasta)
					)

			if(desde and hasta):
				qset = qset &(
					Q(fecha__gte=desde) and Q(fecha__lte=hasta) 
				)

			movimientos = FinancieroCuentaMovimiento.objects.filter(qset)

			valor_ingreso = movimientos.filter(tipo_id=31).aggregate(suma_ingreso=Sum('valor'))	
			valor_egreso = movimientos.filter(tipo_id=29).aggregate(suma_egreso=Sum('valor'))	
			valor_rendimiento = movimientos.filter(tipo_id=32).aggregate(suma_rendimiento=Sum('valor'))	


			dato = [{
				'numero': objCuenta.numero,
				'nombre': objCuenta.nombre,
				'fiduciaria': objCuenta.fiduciaria,
				'tipo_nombre': objCuenta.tipo.nombre,
				'cantidad_movimiento': objCuenta.cantidad_movimiento(),
				'suma_egreso': valor_egreso['suma_egreso'],
				'suma_ingreso': valor_ingreso['suma_ingreso'],
				'suma_rendimiento': valor_rendimiento['suma_rendimiento'],
			}]

			return JsonResponse({'message':'','success':'ok',
				'data':dato})

	except Exception as e:
		funciones.toLog(e, 'financierocuenta.encabezado')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})


def descargar_informe_financiero(request):

	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="informe_financiero.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})

	format1=workbook.add_format({'border':1,'font_size':12,'bold':True})
	format2=workbook.add_format({'border':1})

	format5=workbook.add_format({'border':1})
	format5.set_num_format('yyyy-mm-dd')


	macrocontrato_id= request.GET['macrocontrato_id']
	fecha= request.GET['fecha']
	activar= request.GET['activar']
	contrato_id= request.GET['contrato_id']


	if int(activar) == 0:
		worksheet1 = workbook.add_worksheet('Fiduciaria')

	worksheet2 = workbook.add_worksheet('Facturas')
	worksheet3 = workbook.add_worksheet('Anticipos')
	worksheet4 = workbook.add_worksheet('Multas')
	worksheet5 = workbook.add_worksheet('Cruces')
	worksheet6 = workbook.add_worksheet('Analisis')

	if int(activar) == 0:
		worksheet1.set_column('A:F', 30)
		
	worksheet2.set_column('A:O', 30)
	worksheet3.set_column('A:O', 30)
	worksheet4.set_column('A:O', 30)	
	worksheet5.set_column('A:O', 30)
	worksheet6.set_column('A:O', 30)	

	total_anticipos=0
	total_facturas=0
	total_aportes=0
	total_multas=0

	if int(activar) == 0:
		tipo=Tipo.objects.filter(app='TipoFinacieroCuentaMovimiento',codigo=2)
		movimientos=None
		
		if fecha != '':
			movimientos=FinancieroCuentaMovimiento.objects.filter((Q(tipo_id=tipo[0].id))&(Q(cuenta__contrato_id=macrocontrato_id))&(Q(descripcion__icontains="Aportes"))&(Q(descripcion__icontains="MME"))&(Q(fecha__lte=fecha)))
		else:
			movimientos=FinancieroCuentaMovimiento.objects.filter((Q(tipo_id=tipo[0].id))&(Q(cuenta__contrato_id=macrocontrato_id))&(Q(descripcion__icontains="Aportes"))&(Q(descripcion__icontains="MME")))

		row=1
		col=0

		worksheet1.write('A1', 'Macrocontrato', format1)
		worksheet1.write('B1', 'Numero cuenta', format1)
		worksheet1.write('C1', 'Fecha movimiento', format1)
		worksheet1.write('D1', 'Valor Ingreso', format1)
		worksheet1.write('E1', 'Descripcion Movimiento', format1)
		worksheet1.write('F1', 'Tipo Movimiento', format1)

		
		for item in movimientos:
			worksheet1.write(row, col,item.cuenta.contrato.nombre,format2)
			worksheet1.write(row, col+1,item.cuenta.numero,format2)
			worksheet1.write(row, col+2,item.fecha,format5)
			worksheet1.write(row, col+3,item.valor,format2)
			worksheet1.write(row, col+4,item.descripcion,format2)
			worksheet1.write(row, col+5,item.tipo.nombre,format2)
			if item.valor is not None:
				total_aportes=total_aportes+item.valor

			row +=1

	contrato=None
	if int(activar) == 0:
		contrato=Contrato.objects.get(pk=macrocontrato_id)
	else:
		contrato=Contrato.objects.get(pk=contrato_id)

	facturas=None

	if int(activar)== 0:

		if 'prone' in str(contrato.nombre).lower():

			if fecha != '':
				facturas=Factura.objects.filter(mcontrato_id=macrocontrato_id,contrato__tipo_contrato_id__in=[8,10,11,13,14,103],fecha__lte=fecha)			
			else:
				facturas=Factura.objects.filter(mcontrato_id=macrocontrato_id,contrato__tipo_contrato_id__in=[8,10,11,13,14,103])			

		if 'faer' in str(contrato.nombre).lower():

			if fecha != '':
				facturas=Factura.objects.filter(mcontrato_id=macrocontrato_id,contrato__tipo_contrato_id__in=[8,9,11,13,14,103],fecha__lte=fecha)
			else:
				facturas=Factura.objects.filter(mcontrato_id=macrocontrato_id,contrato__tipo_contrato_id__in=[8,9,11,13,14,103])

	else:
		if fecha != '':
			facturas=Factura.objects.filter(contrato_id=contrato_id,fecha__lte=fecha)
		else:
			facturas=Factura.objects.filter(contrato_id=contrato_id)


	row=1
	col=0

	worksheet2.write('A1', 'Macrocontrato', format1)
	worksheet2.write('B1', 'Numero de contrato', format1)
	worksheet2.write('C1', 'Nombre Contrato', format1)
	worksheet2.write('D1', 'Numero Factura', format1)
	worksheet2.write('E1', 'Fecha Factura', format1)
	worksheet2.write('F1', 'Referencia SAP', format1)
	worksheet2.write('G1', 'Codigo acreedor', format1)
	worksheet2.write('H1', 'Nombre acreedor', format1)
	worksheet2.write('I1', 'Valor factura antes de Impuesto y retencion', format1)
	worksheet2.write('J1', 'Valor Contable', format1)
	worksheet2.write('K1', 'Referencia SAP Anticipos Cruzados', format1)
	worksheet2.write('L1', 'Anticipos Cruzados', format1)

	
	for item in facturas:

		worksheet2.write(row, col,item.mcontrato.nombre,format2)
		worksheet2.write(row, col+1,item.contrato.numero,format2)
		worksheet2.write(row, col+2,item.contrato.nombre,format5)
		worksheet2.write(row, col+3,item.numero,format2)
		worksheet2.write(row, col+4,item.fecha,format5)
		worksheet2.write(row, col+5,item.referencia,format2)
		worksheet2.write(row, col+6,item.contrato.contratista.codigo_acreedor,format2)
		worksheet2.write(row, col+7,item.contrato.contratista.nombre,format2)
		worksheet2.write(row, col+8,item.valor_factura,format2)
		worksheet2.write(row, col+9,item.valor_contable,format2)


		compensacion=DetalleCompensacion.objects.filter(id_registro=item.id,tablaForanea_id=140)
		valor_sap=''
		valor_anticipos=''

		for item2 in compensacion:
			list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2.compensacion_id).order_by('tablaForanea_id')
			num_conse=1

			for item3 in list_compensacion:

				if int(item3.tablaForanea_id)==38:
					encabezado=DEncabezadoGiro.objects.get(pk=item3.id_registro)
					if valor_sap=='':
						valor_sap=encabezado.referencia
					else:
						valor_sap=valor_sap+','+encabezado.referencia

					if valor_anticipos=='':
						valor_anticipos=encabezado.nombre.nombre+'('+encabezado.contrato.numero+')'
					else:
						valor_anticipos=valor_anticipos+','+encabezado.nombre.nombre+'('+encabezado.contrato.numero+')'


				if int(item3.tablaForanea_id)==161:
					multa=Solicitud.objects.get(pk=item3.id_registro)
					if valor_sap=='':
						valor_sap=multa.codigoOF
					else:
						valor_sap=valor_sap+','+multa.codigoOF

					if valor_anticipos=='':
						valor_anticipos='Multa '+str(num_conse)
						num_conse=num_conse+1
					else:
						valor_anticipos=valor_anticipos+', Multa '+str(num_conse)
						num_conse=num_conse+1


		worksheet2.write(row, col+10,valor_sap,format2)
		worksheet2.write(row, col+11,valor_anticipos,format2)

		if item.valor_factura is not None:
			total_facturas=total_facturas+item.valor_factura

		row +=1


	tipo_bancaria=Tipo.objects.filter(app='encabezadoGiro_pago_recurso',codigo=1)
	autorizado=Estado.objects.filter(app='EstadoGiro',codigo=2)
	pagado=Estado.objects.filter(app='EstadoGiro',codigo=3)

	if int(activar) == 0:
		detalle=DetalleGiro.objects.filter(encabezado__contrato__mcontrato_id=macrocontrato_id,encabezado__pago_recurso_id=tipo_bancaria[0].id,estado_id__in=[int(autorizado[0].id),int(pagado[0].id)])
	else:
		detalle=DetalleGiro.objects.filter(encabezado__contrato_id=contrato_id,encabezado__pago_recurso_id=tipo_bancaria[0].id,estado_id__in=[int(autorizado[0].id),int(pagado[0].id)])

	row=1
	col=0

	worksheet3.write('A1', 'Macrocontrato', format1)
	worksheet3.write('B1', 'Contrato y Origen de fondos', format1)
	worksheet3.write('C1', 'Numero Contrato', format1)
	worksheet3.write('D1', 'Nombre Contrato', format1)
	worksheet3.write('E1', 'Referencia SAP', format1)
	worksheet3.write('F1', 'Nombre del giro', format1)
	worksheet3.write('G1', 'Linea', format1)
	worksheet3.write('H1', 'Proveedor', format1)
	worksheet3.write('I1', 'Valor Giro', format1)
	worksheet3.write('J1', 'Estado Giro', format1)
	worksheet3.write('K1', 'Pago Recurso', format1)
	worksheet3.write('L1', 'Numero Acreedor', format1)
	worksheet3.write('M1', 'Nombre Acreedor', format1)
	worksheet3.write('N1', 'Referencia SAP Facturas Cruzadas', format1)
	worksheet3.write('O1', 'Numero de Facturas Cruzadas', format1)


	
	for item in detalle:
		
		if fecha != '':
			if int(item.estado.id)==int(pagado[0].id):
				if str(fecha) >= str(item.fecha_pago):
					worksheet3.write(row, col,item.encabezado.contrato.mcontrato.nombre,format2)
					worksheet3.write(row, col+1,item.encabezado.contrato.mcontrato.nombre+" - "+item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+2,item.encabezado.contrato.numero,format5)
					worksheet3.write(row, col+3,item.encabezado.contrato.nombre,format2)
					worksheet3.write(row, col+4,item.encabezado.referencia,format2)
					worksheet3.write(row, col+5,item.encabezado.nombre.nombre,format2)
					worksheet3.write(row, col+6,item.id,format2)
					worksheet3.write(row, col+7,item.contratista.nombre,format2)
					worksheet3.write(row, col+8,item.valor_girar,format2)
					worksheet3.write(row, col+9,item.estado.nombre,format2)
					worksheet3.write(row, col+10,item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+11,item.encabezado.contrato.contratista.codigo_acreedor,format2)
					worksheet3.write(row, col+12,item.encabezado.contrato.contratista.nombre,format2)

					compensacion=DetalleCompensacion.objects.filter(id_registro=item.encabezado.id,tablaForanea_id=38)
					valor_sap=''
					valor_factura=''

					for item2 in compensacion:
						list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2.compensacion_id).order_by('tablaForanea_id')
						num_conse=1

						for item3 in list_compensacion:

							if int(item3.tablaForanea_id)==140:
								factura=Factura.objects.get(pk=item3.id_registro)
								if valor_sap=='':
									valor_sap=factura.referencia
								else:
									valor_sap=valor_sap+','+factura.referencia

								if valor_factura=='':
									valor_factura=factura.numero
								else:
									valor_factura=valor_factura+','+factura.numero


							if int(item3.tablaForanea_id)==161:
								multa=Solicitud.objects.get(pk=item3.id_registro)
								if valor_sap=='':
									valor_sap=multa.codigoOF
								else:
									valor_sap=valor_sap+','+multa.codigoOF

								if valor_factura=='':
									valor_factura='Multa '+str(num_conse)
									num_conse=num_conse+1
								else:
									valor_factura=valor_factura+', Multa '+str(num_conse)
									num_conse=num_conse+1


					worksheet3.write(row, col+13,valor_sap,format2)
					worksheet3.write(row, col+14,valor_factura,format2)

					if item.valor_girar is not None:
						total_anticipos=total_anticipos+item.valor_girar
					row +=1

			if int(item.estado.id)==int(autorizado[0].id):
				if str(fecha) >= str(item.carta_autorizacion.fechaEnvio):
					worksheet3.write(row, col,item.encabezado.contrato.mcontrato.nombre,format2)
					worksheet3.write(row, col+1,item.encabezado.contrato.mcontrato.nombre+" - "+item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+2,item.encabezado.contrato.numero,format5)
					worksheet3.write(row, col+3,item.encabezado.contrato.nombre,format2)
					worksheet3.write(row, col+4,item.encabezado.referencia,format2)
					worksheet3.write(row, col+5,item.encabezado.nombre.nombre,format2)
					worksheet3.write(row, col+6,item.id,format2)
					worksheet3.write(row, col+7,item.contratista.nombre,format2)
					worksheet3.write(row, col+8,item.valor_girar,format2)
					worksheet3.write(row, col+9,item.estado.nombre,format2)
					worksheet3.write(row, col+10,item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+11,item.encabezado.contrato.contratista.codigo_acreedor,format2)
					worksheet3.write(row, col+12,item.encabezado.contrato.contratista.nombre,format2)

					compensacion=DetalleCompensacion.objects.filter(id_registro=item.encabezado.id,tablaForanea_id=38)
					valor_sap=''
					valor_factura=''

					for item2 in compensacion:
						list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2.compensacion_id).order_by('tablaForanea_id')
						num_conse=1

						for item3 in list_compensacion:

							if int(item3.tablaForanea_id)==140:
								factura=Factura.objects.get(pk=item3.id_registro)
								if valor_sap=='':
									valor_sap=factura.referencia
								else:
									valor_sap=valor_sap+','+factura.referencia

								if valor_factura=='':
									valor_factura=factura.numero
								else:
									valor_factura=valor_factura+','+factura.numero


							if int(item3.tablaForanea_id)==161:
								multa=Solicitud.objects.get(pk=item3.id_registro)
								if valor_sap=='':
									valor_sap=multa.codigoOF
								else:
									valor_sap=valor_sap+','+multa.codigoOF

								if valor_factura=='':
									valor_factura='Multa '+str(num_conse)
									num_conse=num_conse+1
								else:
									valor_factura=valor_factura+', Multa '+str(num_conse)
									num_conse=num_conse+1

					worksheet3.write(row, col+13,valor_sap,format2)
					worksheet3.write(row, col+14,valor_factura,format2)

					if item.valor_girar is not None:
						total_anticipos=total_anticipos+item.valor_girar
					row +=1

		else:
			worksheet3.write(row, col,item.encabezado.contrato.mcontrato.nombre,format2)
			worksheet3.write(row, col+1,item.encabezado.contrato.mcontrato.nombre+" - "+item.encabezado.pago_recurso.nombre,format2)
			worksheet3.write(row, col+2,item.encabezado.contrato.numero,format5)
			worksheet3.write(row, col+3,item.encabezado.contrato.nombre,format2)
			worksheet3.write(row, col+4,item.encabezado.referencia,format2)
			worksheet3.write(row, col+5,item.encabezado.nombre.nombre,format2)
			worksheet3.write(row, col+6,item.id,format2)
			worksheet3.write(row, col+7,item.contratista.nombre,format2)
			worksheet3.write(row, col+8,item.valor_girar,format2)
			worksheet3.write(row, col+9,item.estado.nombre,format2)
			worksheet3.write(row, col+10,item.encabezado.pago_recurso.nombre,format2)
			worksheet3.write(row, col+11,item.encabezado.contrato.contratista.codigo_acreedor,format2)
			worksheet3.write(row, col+12,item.encabezado.contrato.contratista.nombre,format2)

			compensacion=DetalleCompensacion.objects.filter(id_registro=item.encabezado.id,tablaForanea_id=38)
			valor_sap=''
			valor_factura=''

			for item2 in compensacion:
				list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2.compensacion_id).order_by('tablaForanea_id')
				num_conse=1

				for item3 in list_compensacion:

					if int(item3.tablaForanea_id)==140:
						factura=Factura.objects.get(pk=item3.id_registro)
						if valor_sap=='':
							valor_sap=factura.referencia
						else:
							valor_sap=valor_sap+','+factura.referencia

						if valor_factura=='':
							valor_factura=factura.numero
						else:
							valor_factura=valor_factura+','+factura.numero


					if int(item3.tablaForanea_id)==161:
						multa=Solicitud.objects.get(pk=item3.id_registro)
						if valor_sap=='':
							valor_sap=multa.codigoOF
						else:
							valor_sap=valor_sap+','+multa.codigoOF

						if valor_factura=='':
							valor_factura='Multa '+str(num_conse)
							num_conse=num_conse+1
						else:
							valor_factura=valor_factura+', Multa '+str(num_conse)
							num_conse=num_conse+1


			worksheet3.write(row, col+13,valor_sap,format2)
			worksheet3.write(row, col+14,valor_factura,format2)

			if item.valor_girar is not None:
				total_anticipos=total_anticipos+item.valor_girar
			row +=1
		


	row=1
	col=0


	estado_confirmada=Estado.objects.filter(app='multa',codigo=5)
	estado_contabiizada=Estado.objects.filter(app='multa',codigo=10)

	if int(activar) == 0:
		multas=Solicitud.objects.filter(contrato__mcontrato_id=macrocontrato_id)
	else:
		multas=Solicitud.objects.filter(contrato_id=contrato_id)

	worksheet4.write('A1', 'Macrocontrato', format1)
	worksheet4.write('B1', 'Numero Contrato', format1)
	worksheet4.write('C1', 'Nombre Contrato', format1)
	worksheet4.write('D1', 'Codigo Acreedor', format1)
	worksheet4.write('E1', 'Nombre Acreedor', format1)
	worksheet4.write('F1', 'Codigo OF', format1)
	worksheet4.write('G1', 'Valor Impuesto', format1)
	
	for item in multas:

		estado_multa=None
		if fecha != '': 
			estado_multa=SolicitudHistorial.objects.filter(solicitud_id=item.id,fecha__lte=fecha).order_by('-id').first()
		else:
			estado_multa=SolicitudHistorial.objects.filter(solicitud_id=item.id).order_by('-id').first()

		if estado_multa:	
			if int(estado_multa.estado_id)==int(estado_confirmada[0].id) or int(estado_multa.estado_id)==int(estado_contabiizada[0].id):

				worksheet4.write(row, col,item.contrato.mcontrato.nombre,format2)
				worksheet4.write(row, col+1,item.contrato.numero,format5)
				worksheet4.write(row, col+2,item.contrato.nombre,format2)
				worksheet4.write(row, col+3,item.contrato.contratista.codigo_acreedor,format2)
				worksheet4.write(row, col+4,item.contrato.contratista.nombre,format2)
				worksheet4.write(row, col+5,item.codigoOF,format2)
				worksheet4.write(row, col+6,item.valorImpuesto,format2)
				if item.valorImpuesto is not None:
					total_multas=total_multas+item.valorImpuesto
				row +=1


	row=1
	col=0

	worksheet5.write('A1', 'Macrocontrato', format1)
	worksheet5.write('B1', 'Numero Contrato', format1)
	worksheet5.write('C1', 'Nombre Contrato', format1)
	worksheet5.write('D1', 'Tipo', format1)
	worksheet5.write('E1', 'No. Factura / Nombre anticipo', format1)
	worksheet5.write('F1', 'Documento SAP / Codigo OF', format1)
	worksheet5.write('G1', 'Valor', format1)

	sql_compensada=None

	if int(activar) == 0:
		sql_compensada=Compensacion.objects.filter(contrato__mcontrato_id=macrocontrato_id)
	else:
		sql_compensada=Compensacion.objects.filter(contrato_id=contrato_id)


	for item in sql_compensada:
		sql_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item.id)

		for item2 in sql_compensacion:
			if int(item2.tablaForanea_id)==38:
				sql_resultado=DEncabezadoGiro.objects.get(pk=item2.id_registro)
				sumatoria=DetalleGiro.objects.filter(encabezado_id=sql_resultado.id).aggregate(suma_detalle=Sum('valor_girar'))

				worksheet5.write(row, col,sql_resultado.contrato.mcontrato.nombre,format2)
				worksheet5.write(row, col+1,sql_resultado.contrato.numero,format5)
				worksheet5.write(row, col+2,sql_resultado.contrato.nombre,format2)
				worksheet5.write(row, col+3,"Anticipos",format2)
				worksheet5.write(row, col+4,sql_resultado.nombre.nombre,format2)
				worksheet5.write(row, col+5,sql_resultado.referencia,format2)
				worksheet5.write(row, col+6,sumatoria['suma_detalle'],format2)
				row +=1

			if int(item2.tablaForanea_id)==140:
				sql_resultado=Factura.objects.get(pk=item2.id_registro)

				worksheet5.write(row, col,sql_resultado.contrato.mcontrato.nombre,format2)
				worksheet5.write(row, col+1,sql_resultado.contrato.numero,format5)
				worksheet5.write(row, col+2,sql_resultado.contrato.nombre,format2)
				worksheet5.write(row, col+3,"Factura",format2)
				worksheet5.write(row, col+4,sql_resultado.numero,format2)
				worksheet5.write(row, col+5,sql_resultado.referencia,format2)
				worksheet5.write(row, col+6,"-"+str(sql_resultado.valor_contable),format2)
				row +=1

			if int(item2.tablaForanea_id)==161:
				sql_resultado=Solicitud.objects.get(pk=item2.id_registro)

				worksheet5.write(row, col,sql_resultado.contrato.mcontrato.nombre,format2)
				worksheet5.write(row, col+1,sql_resultado.contrato.numero,format5)
				worksheet5.write(row, col+2,sql_resultado.contrato.nombre,format2)
				worksheet5.write(row, col+3,"Multa",format2)
				worksheet5.write(row, col+4,"No Aplica",format2)
				worksheet5.write(row, col+5,sql_resultado.codigoOF,format2)
				worksheet5.write(row, col+6,sql_resultado.valorImpuesto,format2)
				row +=1


	worksheet6.write('B1', contrato.nombre+" - Cuenta Bancaria", format1)
	worksheet6.write('A2', 'Contrato', format1)
	worksheet6.write('B2', contrato.nombre, format1)

	if int(activar) == 0:
		worksheet6.write('A3', 'Aportes del MME', format1)

	worksheet6.write('A4', 'Anticipos', format1)
	worksheet6.write('A5', 'Ejecucion', format1)
	worksheet6.write('A6', 'Multas', format1)
	worksheet6.write('A7', 'Anticipos v.s. Ejecucion', format1)

	if int(activar) == 0:
		worksheet6.write('A8', 'Aportes V.s. Ejecucion', format1)
		worksheet6.write('B3',total_aportes,format2)
		worksheet6.write('B8',total_aportes-total_facturas,format2)
	
	worksheet6.write('B4',total_anticipos,format2)
	worksheet6.write('B5',total_facturas,format2)
	worksheet6.write('B6',total_multas,format2)
	worksheet6.write('B7',total_anticipos-total_facturas,format2)

	workbook.close()

	return response
    #return response




#Api lite de empresa proyecto
class ContratistaContratoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de los contratista
	"""
	model=Contrato
	queryset = model.objects.all()
	nombre_modulo='financiero.contratista_contrato'

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ContratistaContratoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			contratante_id = self.request.query_params.get('contratante_id', None)
			sin_paginacion = self.request.query_params.get('sin_paginacion', None)

			qset=(~Q(id=0))
				
			if dato:
				qset = qset & ( Q(contratista__nombre__icontains = dato) |
							Q(contratista__codigo_acreedor__icontains = dato))					
			

			if contratante_id and int(contratante_id)>0:
				qset = qset & (Q(contratante_id = contratante_id))	

			
			if qset != '':
				contratistas = self.model.objects.filter(qset).values_list('contratista_id').distinct()
				queryset = Empresa.objects.filter(id__in = contratistas , esContratista = True).values('id','nombre','codigo_acreedor')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					#serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':list(page)})
		
				#serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok',
						'data':list(page)})
			else:
				#serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok',
						'data':list(page)})

		except Exception as e:
			print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)




def descargar_informe_financiero_contratista(request):
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="informe_financiero.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})

	worksheet2 = workbook.add_worksheet('Facturas')
	worksheet3 = workbook.add_worksheet('Anticipos')
	worksheet4 = workbook.add_worksheet('Multas')
	worksheet5 = workbook.add_worksheet('Cruces')
	worksheet6 = workbook.add_worksheet('Analisis')

	format1=workbook.add_format({'border':1,'font_size':12,'bold':True})
	format2=workbook.add_format({'border':1})

	format5=workbook.add_format({'border':1})
	format5.set_num_format('yyyy-mm-dd')

	worksheet2.set_column('A:O', 30)
	worksheet3.set_column('A:O', 30)	
	worksheet4.set_column('A:O', 30)
	worksheet5.set_column('A:O', 30)
	worksheet6.set_column('A:O', 30)

	contratista_id= request.GET['contratista_id']
	fecha= request.GET['fecha']
	total_anticipos=0
	total_facturas=0
	total_multas=0

	#import pdb; pdb.set_trace()

	facturas=None
	if fecha == '':		
		facturas = obtenerConsulta('[dbo].[obtener_factura_informe]', [contratista_id, None])
	elif fecha:
		facturas = obtenerConsulta('[dbo].[obtener_factura_informe]', [contratista_id, fecha])
	
	row=1
	col=0

	worksheet2.write('A1', 'Macrocontrato', format1)
	worksheet2.write('B1', 'Numero de contrato', format1)
	worksheet2.write('C1', 'Nombre Contrato', format1)
	worksheet2.write('D1', 'Numero Factura', format1)
	worksheet2.write('E1', 'Fecha Factura', format1)
	worksheet2.write('F1', 'Referencia SAP', format1)
	worksheet2.write('G1', 'Codigo acreedor', format1)
	worksheet2.write('H1', 'Nombre acreedor', format1)
	worksheet2.write('I1', 'Valor factura con Impuesto y retencion', format1)
	worksheet2.write('J1', 'Valor Contable', format1)
	worksheet2.write('K1', 'Referencia SAP Anticipos Cruzados', format1)
	worksheet2.write('L1', 'Anticipos Cruzados', format1)

	
	for item in facturas:
		worksheet2.write(row, col,item['mcontrato'],format2)
		worksheet2.write(row, col+1,item['numero_contrato'],format2)
		worksheet2.write(row, col+2,item['nombre_contrato'],format5)
		worksheet2.write(row, col+3,item['numero'],format2)
		worksheet2.write(row, col+4,item['fecha'],format5)
		worksheet2.write(row, col+5,item['referencia'],format2)
		worksheet2.write(row, col+6,item['codigo_acreedor'],format2)
		worksheet2.write(row, col+7,item['nombre_contratista'],format2)
		worksheet2.write(row, col+8,item['valor_factura'],format2)
		worksheet2.write(row, col+9,item['valor_contable'],format2)

		# compensacion=DetalleCompensacion.objects.filter(id_registro=item['id'],tablaForanea_id=140)
		compensacion = obtenerConsulta('[dbo].[obtener_detalle_compensacion_informe]', [item['id'], 140, None])

		valor_sap=''
		valor_anticipos=''

		for item2 in compensacion:
			# list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2['compensacion_id']).order_by('tablaForanea_id')
			list_compensacion = obtenerConsulta('[dbo].[obtener_detalle_compensacion_informe]', [None, None, item2['compensacion_id']])
			num_conse=1

			for item3 in list_compensacion:

				if int(item3['tablaForanea_id'])==38:
					# encabezado=DEncabezadoGiro.objects.get(pk=item3['id_registro'])
					encabezado = obtenerConsulta('[dbo].[obtener_detalle_encabezado_giro_informe]', [item3['id_registro']])
					encabezado = encabezado[0]
					if valor_sap=='':
						valor_sap=encabezado['referencia']
					else:
						valor_sap=valor_sap+','+encabezado['referencia']

					if valor_anticipos=='':
						valor_anticipos=encabezado['nombre_giro']+'('+encabezado['numero_contrato']+')'
					else:
						valor_anticipos=valor_anticipos+','+encabezado['nombre_giro']+'('+encabezado['numero_contrato']+')'


				if int(item3['tablaForanea_id'])==161:
					# multa=Solicitud.objects.get(pk=item3.id_registro)
					multa = obtenerConsulta('[dbo].[obtener_solicitud_informe]', [item3['id_registro']])
					multa = multa[0]
					if valor_sap=='':
						valor_sap=multa['codigoOF']
					else:
						valor_sap=valor_sap+','+multa['codigoOF']

					if valor_anticipos=='':
						valor_anticipos='Multa '+str(num_conse)
						num_conse=num_conse+1
					else:
						valor_anticipos=valor_anticipos+', Multa '+str(num_conse)
						num_conse=num_conse+1


		worksheet2.write(row, col+10,valor_sap,format2)
		worksheet2.write(row, col+11,valor_anticipos,format2)

		if item['valor_factura'] is not None:
			total_facturas=total_facturas+item['valor_factura']

		row +=1


	autorizado=Estado.objects.filter(app='EstadoGiro',codigo=2)
	pagado=Estado.objects.filter(app='EstadoGiro',codigo=3)

	# detalle=DetalleGiro.objects.filter(encabezado__contrato__contratista_id=contratista_id,estado_id__in=[int(autorizado[0].id),int(pagado[0].id)])
	detalle = obtenerConsulta('[dbo].[obtener_detalle_giro_informe]', [contratista_id, '{0},{1}'.format(autorizado[0].id, pagado[0].id)])
	row=1
	col=0

	worksheet3.write('A1', 'Macrocontrato', format1)
	worksheet3.write('B1', 'Contrato y Origen de fondos', format1)
	worksheet3.write('C1', 'Numero Contrato', format1)
	worksheet3.write('D1', 'Nombre Contrato', format1)
	worksheet3.write('E1', 'Referencia SAP', format1)
	worksheet3.write('F1', 'Nombre del giro', format1)
	worksheet3.write('G1', 'Linea', format1)
	worksheet3.write('H1', 'Proveedor', format1)
	worksheet3.write('I1', 'Valor Giro', format1)
	worksheet3.write('J1', 'Estado Giro', format1)
	worksheet3.write('K1', 'Pago Recurso', format1)
	worksheet3.write('L1', 'Numero Acreedor', format1)
	worksheet3.write('M1', 'Nombre Acreedor', format1)
	worksheet3.write('N1', 'Referencia SAP Facturas Cruzadas', format1)
	worksheet3.write('O1', 'Numero de Facturas Cruzadas', format1)

	#import pdb; pdb.set_trace()
	for item in detalle:
		
		if fecha != '':
			if int(item.estado.id)==int(pagado[0].id):
				if str(fecha) >= str(item.fecha_pago):
					worksheet3.write(row, col,item['mcontrato'],format2)
					worksheet3.write(row, col+1,item['mcontrato']+" - "+item['pago_recurso'],format2)
					worksheet3.write(row, col+2,item['numero_contrato'],format5)
					worksheet3.write(row, col+3,item['nombre_contrato'],format2)
					worksheet3.write(row, col+4,item['referencia'],format2)
					worksheet3.write(row, col+5,item['nombre_giro'],format2)
					worksheet3.write(row, col+6,item['id'],format2)
					worksheet3.write(row, col+7,item['nombre_contratista'],format2)
					worksheet3.write(row, col+8,item['valor_girar'],format2)
					worksheet3.write(row, col+9,item['estado'],format2)
					worksheet3.write(row, col+10,item['pago_recurso'],format2)
					worksheet3.write(row, col+11,item['codigo_acreedor'],format2)
					worksheet3.write(row, col+12,item['nombre_contratista_contrato'],format2)

					# compensacion=DetalleCompensacion.objects.filter(id_registro=item.encabezado.id,tablaForanea_id=38)
					compensacion = obtenerConsulta('obtener_detalle_compensacion_informe', [item['encabezado_id'], 38, None])
					valor_sap=''
					valor_factura=''

					for item2 in compensacion:
						# list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2['compensacion_id']).order_by('tablaForanea_id')
						list_compensacion = obtenerConsulta('obtener_detalle_compensacion_informe', [None, None, item2['compensacion_id']])
						num_conse=1

						for item3 in list_compensacion:

							if int(item3['tablaForanea_id'])==140:
								# factura=Factura.objects.get(pk=item3.id_registro)
								factura = obtenerConsulta('obetener_factura_porid_informe', item3['id_registro'])
								factura = factura[0]
								if valor_sap=='':
									valor_sap=factura['referencia']
								else:
									valor_sap=valor_sap+','+factura['referencia']

								if valor_factura=='':
									valor_factura=factura['numero']
								else:
									valor_factura=valor_factura+','+factura['numero']


							if int(item3['tablaForanea_id'])==161:
								# multa=Solicitud.objects.get(pk=item3.id_registro)
								multa = obtenerConsulta('obtener_solicitud_informe', item3['id_registro'])
								multa = multa[0]
								if valor_sap=='':
									valor_sap=multa['codigoOF']
								else:
									valor_sap=valor_sap+','+multa['codigoOF']

								if valor_factura=='':
									valor_factura='Multa '+str(num_conse)
									num_conse=num_conse+1
								else:
									valor_factura=valor_factura+', Multa '+str(num_conse)
									num_conse=num_conse+1


					worksheet3.write(row, col+13,valor_sap,format2)
					worksheet3.write(row, col+14,valor_factura,format2)

					if item['valor_girar'] is not None:
						total_anticipos=total_anticipos+item['valor_girar']
					row +=1

			if int(item['estado_id'])==int(autorizado[0].id):
				if str(fecha) >= str(item['fechaEnvio']):
					worksheet3.write(row, col,item['mcontrato'],format2)
					worksheet3.write(row, col+1,item['mcontrato']+" - "+item['pago_recurso'],format2)
					worksheet3.write(row, col+2,item['numero_contrato'],format5)
					worksheet3.write(row, col+3,item['nombre_contrato'],format2)
					worksheet3.write(row, col+4,item['referencia'],format2)
					worksheet3.write(row, col+5,item['nombre_giro'],format2)
					worksheet3.write(row, col+6,item['id'],format2)
					worksheet3.write(row, col+7,item['nombre_contratista'],format2)
					worksheet3.write(row, col+8,item['valor_girar'],format2)
					worksheet3.write(row, col+9,item['estado'],format2)
					worksheet3.write(row, col+10,item['pago_recurso'],format2)
					worksheet3.write(row, col+11,item['codigo_acreedor'],format2)
					worksheet3.write(row, col+12,item['nombre_contratista_contrato'],format2)

					# compensacion=DetalleCompensacion.objects.filter(id_registro=item.encabezado.id,tablaForanea_id=38)
					compensacion = obtenerConsulta('obtener_detalle_compensacion_informe', [item['encabezado_id'], 38, None])
					valor_sap=''
					valor_factura=''

					for item2 in compensacion:
						# list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2.compensacion_id).order_by('tablaForanea_id')
						list_compensacion = obtenerConsulta('obtener_detalle_compensacion_informe', [None, None, item2['compensacion_id']])
						num_conse=1

						for item3 in list_compensacion:

							if int(item3['tablaForanea_id'])==140:
								# factura=Factura.objects.get(pk=item3.id_registro)
								factura = obtenerConsulta('obetener_factura_porid_informe', item3['id_registro'])
								factura = factura[0]
								if valor_sap=='':
									valor_sap=factura['referencia']
								else:
									valor_sap=valor_sap+','+factura['referencia']

								if valor_factura=='':
									valor_factura=factura['numero']
								else:
									valor_factura=valor_factura+','+factura['numero']


							if int(item3['tablaForanea_id'])==161:
								# multa=Solicitud.objects.get(pk=item3['id_registro'])
								multa = obtenerConsulta('obtener_solicitud_informe', item3['id_registro'])
								multa = multa[0]
								if valor_sap=='':
									valor_sap=multa['codigoOF']
								else:
									valor_sap=valor_sap+','+multa['codigoOF']

								if valor_factura=='':
									valor_factura='Multa '+str(num_conse)
									num_conse=num_conse+1
								else:
									valor_factura=valor_factura+', Multa '+str(num_conse)
									num_conse=num_conse+1

					worksheet3.write(row, col+13,valor_sap,format2)
					worksheet3.write(row, col+14,valor_factura,format2)

					if item['valor_girar'] is not None:
						total_anticipos=total_anticipos+item['valor_girar']
					row +=1

		else:
			worksheet3.write(row, col,item['mcontrato'],format2)
			worksheet3.write(row, col+1,item['mcontrato']+" - "+item['pago_recurso'],format2)
			worksheet3.write(row, col+2,item['numero_contrato'],format5)
			worksheet3.write(row, col+3,item['nombre_contrato'],format2)
			worksheet3.write(row, col+4,item['referencia'],format2)
			worksheet3.write(row, col+5,item['nombre_giro'],format2)
			worksheet3.write(row, col+6,item['id'],format2)
			worksheet3.write(row, col+7,item['nombre_contratista'],format2)
			worksheet3.write(row, col+8,item['valor_girar'],format2)
			worksheet3.write(row, col+9,item['estado'],format2)
			worksheet3.write(row, col+10,item['pago_recurso'],format2)
			worksheet3.write(row, col+11,item['codigo_acreedor'],format2)
			worksheet3.write(row, col+12,item['nombre_contratista_contrato'],format2)

			# compensacion=DetalleCompensacion.objects.filter(id_registro=item.encabezado.id,tablaForanea_id=38)
			compensacion = obtenerConsulta('obtener_detalle_compensacion_informe', [item['encabezado_id'], 38, None])
			valor_sap=''
			valor_factura=''

			for item2 in compensacion:
				# list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2.compensacion_id).order_by('tablaForanea_id')
				list_compensacion = obtenerConsulta('obtener_detalle_compensacion_informe', [None, None, item2['compensacion_id']])
				num_conse=1

				for item3 in list_compensacion:

					if int(item3['tablaForanea_id'])==140:
						# factura=Factura.objects.get(pk=item3.id_registro)
						factura = obtenerConsulta('obetener_factura_porid_informe', item3['id_registro'])
						factura = factura[0]
						if valor_sap=='':
							valor_sap=factura['referencia']
						else:
							valor_sap=valor_sap+','+factura['referencia']

						if valor_factura=='':
							valor_factura=factura['numero']
						else:
							valor_factura=valor_factura+','+factura['numero']


					if int(item3['tablaForanea_id'])==161:
						# multa=Solicitud.objects.get(pk=item3.id_registro)
						multa = obtenerConsulta('obtener_solicitud_informe', item3['id_registro'])
						multa = multa[0]
						if valor_sap=='':
							valor_sap=multa['codigoOF']
						else:
							valor_sap=valor_sap+','+multa['codigoOF']

						if valor_factura=='':
							valor_factura='Multa '+str(num_conse)
							num_conse=num_conse+1
						else:
							valor_factura=valor_factura+', Multa '+str(num_conse)
							num_conse=num_conse+1


			worksheet3.write(row, col+13,valor_sap,format2)
			worksheet3.write(row, col+14,valor_factura,format2)

			if item['valor_girar'] is not None:
				total_anticipos=total_anticipos+item['valor_girar']
			row +=1
		


	row=1
	col=0

	estado_confirmada=Estado.objects.filter(app='multa',codigo=5)
	estado_contabiizada=Estado.objects.filter(app='multa',codigo=10)

	# multas=Solicitud.objects.filter(contrato__contratista_id=contratista_id)
	multas = obtenerConsulta('obtener_multas_informe', [contratista_id])

	worksheet4.write('A1', 'Macrocontrato', format1)
	worksheet4.write('B1', 'Numero Contrato', format1)
	worksheet4.write('C1', 'Nombre Contrato', format1)
	worksheet4.write('D1', 'Codigo Acreedor', format1)
	worksheet4.write('E1', 'Nombre Acreedor', format1)
	worksheet4.write('F1', 'Codigo OF', format1)
	worksheet4.write('G1', 'Valor Impuesto', format1)
	
	for item in multas:

		estado_multa=None
		if fecha != '': 
			estado_multa=SolicitudHistorial.objects.filter(solicitud_id=item['id'],fecha__lte=fecha).order_by('-id').first()
		else:
			estado_multa=SolicitudHistorial.objects.filter(solicitud_id=item['id']).order_by('-id').first()

		if int(estado_multa.estado_id)==int(estado_confirmada[0].id) or int(estado_multa.estado_id)==int(estado_contabiizada[0].id):

			worksheet4.write(row, col,item['mcontrato'],format2)
			worksheet4.write(row, col+1,item['numero_contrato'],format5)
			worksheet4.write(row, col+2,item['nombre_contrato'],format2)
			worksheet4.write(row, col+3,item['codigo_acreedor'],format2)
			worksheet4.write(row, col+4,item['nombre_contratista'],format2)
			worksheet4.write(row, col+5,item['codigoOF'],format2)
			worksheet4.write(row, col+6,item['valorImpuesto'],format2)
			if item['valorImpuesto'] is not None:
				total_multas=total_multas+int(item['valorImpuesto'])
			row +=1


	row=1
	col=0

	worksheet5.write('A1', 'Macrocontrato', format1)
	worksheet5.write('B1', 'Numero Contrato', format1)
	worksheet5.write('C1', 'Nombre Contrato', format1)
	worksheet5.write('D1', 'Tipo', format1)
	worksheet5.write('E1', 'No. Factura / Nombre anticipo', format1)
	worksheet5.write('F1', 'Documento SAP / Codigo OF', format1)
	worksheet5.write('G1', 'Valor', format1)

	sql_compensada=None

	ListMacro = EmpresaContrato.objects.filter(contrato__tipo_contrato=tipoC.m_contrato,empresa=4,participa=1,edita=1).values('contrato_id').order_by("contrato_id")

	qset = (Q(contrato__contratista_id=contratista_id))
	qset = qset &(Q(contrato__mcontrato_id__in=ListMacro))
	sql_compensada=Compensacion.objects.filter(qset)


	for item in sql_compensada:
		sql_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item.id)

		for item2 in sql_compensacion:
			if int(item2.tablaForanea_id)==38:
				sql_resultado=DEncabezadoGiro.objects.get(pk=item2.id_registro)
				sumatoria=DetalleGiro.objects.filter(encabezado_id=sql_resultado.id).aggregate(suma_detalle=Sum('valor_girar'))

				worksheet5.write(row, col,sql_resultado.contrato.mcontrato.nombre,format2)
				worksheet5.write(row, col+1,sql_resultado.contrato.numero,format5)
				worksheet5.write(row, col+2,sql_resultado.contrato.nombre,format2)
				worksheet5.write(row, col+3,"Anticipos",format2)
				worksheet5.write(row, col+4,sql_resultado.nombre.nombre,format2)
				worksheet5.write(row, col+5,sql_resultado.referencia,format2)
				worksheet5.write(row, col+6,sumatoria['suma_detalle'],format2)
				row +=1

			if int(item2.tablaForanea_id)==140:
				sql_resultado=Factura.objects.get(pk=item2.id_registro)

				worksheet5.write(row, col,sql_resultado.contrato.mcontrato.nombre,format2)
				worksheet5.write(row, col+1,sql_resultado.contrato.numero,format5)
				worksheet5.write(row, col+2,sql_resultado.contrato.nombre,format2)
				worksheet5.write(row, col+3,"Factura",format2)
				worksheet5.write(row, col+4,sql_resultado.numero,format2)
				worksheet5.write(row, col+5,sql_resultado.referencia,format2)
				worksheet5.write(row, col+6,"-"+str(sql_resultado.valor_contable),format2)
				row +=1

			if int(item2.tablaForanea_id)==161:
				sql_resultado=Solicitud.objects.get(pk=item2.id_registro)

				worksheet5.write(row, col,sql_resultado.contrato.mcontrato.nombre,format2)
				worksheet5.write(row, col+1,sql_resultado.contrato.numero,format5)
				worksheet5.write(row, col+2,sql_resultado.contrato.nombre,format2)
				worksheet5.write(row, col+3,"Multa",format2)
				worksheet5.write(row, col+4,"No Aplica",format2)
				worksheet5.write(row, col+5,sql_resultado.codigoOF,format2)
				worksheet5.write(row, col+6,sql_resultado.valorImpuesto,format2)
				row +=1


	
	worksheet6.write('A2', 'Analisis', format1)
	worksheet6.write('A4', 'Anticipos', format1)
	worksheet6.write('A5', 'Ejecucion', format1)
	worksheet6.write('A6', 'Multas', format1)
	worksheet6.write('A7', 'Anticipos v.s. Ejecucion', format1)

	worksheet6.write('B4',total_anticipos,format2)
	worksheet6.write('B5',total_facturas,format2)
	worksheet6.write('B6',total_multas,format2)
	worksheet6.write('B7',total_anticipos-total_facturas,format2)

	workbook.close()

	return response
    #return response

def obtenerConsulta(procedimiento, parametros):
	cursor = connection.cursor()
	cursor.callproc(procedimiento, parametros)
	columns = cursor.description 
	resultado = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
	return resultado



def descargar_reporte_pago(request):

	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="reporte_pago.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})

	worksheet = workbook.add_worksheet('Facturas')

	format1=workbook.add_format({'font_size':9,'bold':True,'font_color': 'white'})
	format2=workbook.add_format({'font_size':9})
	format3=workbook.add_format({'font_size':25,'font_color': '#1F497D'})
	format4=workbook.add_format({'font_size':20,'font_color': '#1F497D'})

	format1.set_bg_color('#1F497D')

	format5=workbook.add_format({'border':1})
	format5.set_num_format('yyyy-mm-dd')

	worksheet.set_column('A:U', 20)	

	fecha_desde= request.GET['fecha_desde']
	fecha_hasta= request.GET['fecha_hasta']

	worksheet.write(1,0, 'ELECTRIFICADORA DEL CARIBE S.A. E.S.P.', format3)
	worksheet.write(3,0, 'REPORTE POR FUERA DE PROPUESTA', format4)
	worksheet.insert_image('O1',settings.BASE_DIR+'/static/images/imagenElictricaribe.jpg',{'x_scale':1, 'y_scale': 0.5})
	#worksheet.insert_image('O1','C:\AppServ\www\sinin4\Scripts\SININWEB\static\images\imagenElictricaribe.jpg',{'x_scale':1, 'y_scale': 0.5})

	worksheet.write('A6', 'FEC_REPORTE', format1)
	worksheet.write('B6', 'SOC', format1)
	worksheet.write('C6', 'ACREEDOR / DEUDOR', format1)
	worksheet.write('D6', 'NOMBRE ACREEDOR', format1)
	worksheet.write('E6', 'REFERENCIA', format1)
	worksheet.write('F6', 'FECHA DE VENCIMIENTO', format1)
	worksheet.write('G6', 'FECHA DOCUMENTO', format1)
	worksheet.write('H6', 'FECHA CONTABLE', format1)
	worksheet.write('I6', 'No. RADICADO', format1)
	worksheet.write('J6', 'No. DOC SAP', format1)
	worksheet.write('K6', 'CLASE_DOC.', format1)
	worksheet.write('L6', 'IMPORTE EN ML', format1)
	worksheet.write('M6', 'MON. PAGO', format1)
	worksheet.write('N6', 'TEXTO DOCUMENTO', format1)
	worksheet.write('O6', 'ASIGNACION', format1)
	worksheet.write('P6', 'VIA DE PAGO', format1)
	worksheet.write('Q6', 'CUENTA BENEFICIARIO', format1)
	worksheet.write('R6', 'GIRAR DE:', format1)
	worksheet.write('S6', 'AUTORIZADO POR:', format1)
	worksheet.write('T6', 'USUARIO', format1)
	worksheet.write('U6', 'NOMBRE USUARIO', format1)

	row=6
	col=0

	detalle=DetalleGiro.objects.filter(encabezado__fecha_conta__range=(fecha_desde,fecha_hasta))

	for item in detalle:

		worksheet.write(row, col,"",format2)
		worksheet.write(row, col+1,"0795",format2)
		worksheet.write(row, col+2,item.contratista.codigo_acreedor,format2)
		worksheet.write(row, col+3,item.contratista.nombre,format2)
		
		if item.encabezado.contrato.mcontrato is None:
			worksheet.write(row, col+4,"",format2)
		else:
			worksheet.write(row, col+4,item.encabezado.contrato.mcontrato.nombre,format2)

		worksheet.write(row, col+5,"",format2)
		worksheet.write(row, col+6,"",format2)
		worksheet.write(row, col+7,"",format2)
		worksheet.write(row, col+8,item.encabezado.numero_radicado,format2)
		worksheet.write(row, col+9,item.encabezado.referencia,format2)

		if 'final' in str(item.encabezado.nombre.nombre).lower():
			worksheet.write(row, col+10,"U3",format2)
		else:
			worksheet.write(row, col+10,"F3",format2)

		worksheet.write(row, col+11,item.valor_girar,format2)
		worksheet.write(row, col+12,"COP",format2)
		worksheet.write(row, col+13,item.encabezado.texto_documento_sap,format2)
		worksheet.write(row, col+14,"POST-TOMA",format2)
		worksheet.write(row, col+15,"TRANSFERENCIA",format2)
		tipo_cuenta=""

		if 'ahorro' in str(item.tipo_cuenta.nombre).lower():
			tipo_cuenta='AHO'

		if 'corriente' in str(item.tipo_cuenta.nombre).lower():
			tipo_cuenta='CTE'

		worksheet.write(row, col+16,item.banco.nombre+" "+tipo_cuenta+" "+item.no_cuenta,format2)

		nombre_girar=""
		if 'cuenta bancaria' in str(item.encabezado.pago_recurso.nombre).lower():
			financiero=FinancieroCuenta.objects.filter(contrato_id=item.encabezado.contrato.mcontrato.id)

			tipo_cuenta2=""

			if 'ahorro' in str(financiero[0].tipo.nombre).lower():
				tipo_cuenta2='AHO'

			if 'corriente' in str(financiero[0].tipo.nombre).lower():
				tipo_cuenta2='CTE'

			nombre_girar=financiero[0].fiduciaria+" "+tipo_cuenta2+" "+financiero[0].numero

		else:
			nombre_girar="RECURSOS PROPIOS ELECTRICARIBE"


		worksheet.write(row, col+17,nombre_girar,format2)
		worksheet.write(row, col+18,"RAFAEL ONORO ACOSTA",format2)
		worksheet.write(row, col+19,"",format2)
		worksheet.write(row, col+20,"",format2)

			
		row +=1


	workbook.close()

	return response
    #return response



def descargar_informe_anticipos(request):

	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="informe_financiero.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})

	format1=workbook.add_format({'border':1,'font_size':12,'bold':True})
	format2=workbook.add_format({'border':1})

	format5=workbook.add_format({'border':1})
	format5.set_num_format('yyyy-mm-dd')


	macrocontrato_id= request.GET['macrocontrato_id']
	fecha= request.GET['fecha']
	activar= request.GET['activar']
	contrato_id= request.GET['contrato_id']



	worksheet3 = workbook.add_worksheet('Anticipos')
		
	worksheet3.set_column('A:L', 30)

	total_anticipos=0

	tipo_bancaria=Tipo.objects.filter(app='encabezadoGiro_pago_recurso',codigo=1)

	if int(activar) == 0:
		detalle=DetalleGiro.objects.filter(encabezado__contrato__mcontrato_id=macrocontrato_id)
	else:
		detalle=DetalleGiro.objects.filter(encabezado__contrato_id=contrato_id)

	row=1
	col=0


	pagado=Estado.objects.filter(app='EstadoGiro',codigo=3)
	autorizado=Estado.objects.filter(app='EstadoGiro',codigo=2)

	worksheet3.write('A1', 'Macrocontrato', format1)
	worksheet3.write('B1', 'Contrato y Origen de fondos', format1)
	worksheet3.write('C1', 'Numero Contrato', format1)
	worksheet3.write('D1', 'Nombre Contrato', format1)
	worksheet3.write('E1', 'Referencia SAP', format1)
	worksheet3.write('F1', 'Nombre del giro', format1)
	worksheet3.write('G1', 'Linea', format1)
	worksheet3.write('H1', 'Proveedor', format1)
	worksheet3.write('I1', 'Valor Giro', format1)
	worksheet3.write('J1', 'Estado Giro', format1)
	worksheet3.write('K1', 'Pago Recurso', format1)
	worksheet3.write('L1', 'Numero Acreedor', format1)
	worksheet3.write('M1', 'Nombre Acreedor', format1)


	
	for item in detalle:
		
		if fecha != '':
			if int(item.estado.id)==int(pagado[0].id):
				if str(fecha) >= str(item.fecha_pago):
					worksheet3.write(row, col,item.encabezado.contrato.mcontrato.nombre,format2)
					worksheet3.write(row, col+1,item.encabezado.contrato.mcontrato.nombre+" - "+item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+2,item.encabezado.contrato.numero,format5)
					worksheet3.write(row, col+3,item.encabezado.contrato.nombre,format2)
					worksheet3.write(row, col+4,item.encabezado.referencia,format2)
					worksheet3.write(row, col+5,item.encabezado.nombre.nombre,format2)
					worksheet3.write(row, col+6,item.id,format2)
					worksheet3.write(row, col+7,item.contratista.nombre,format2)
					worksheet3.write(row, col+8,item.valor_girar,format2)
					worksheet3.write(row, col+9,item.estado.nombre,format2)
					worksheet3.write(row, col+10,item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+11,item.encabezado.contrato.contratista.codigo_acreedor,format2)
					worksheet3.write(row, col+12,item.encabezado.contrato.contratista.nombre,format2)
					if item.valor_girar is not None:
						total_anticipos=total_anticipos+item.valor_girar
					row +=1

			if int(item.estado.id)==int(autorizado[0].id):
				if str(fecha) >= str(item.carta_autorizacion.fechaEnvio):
					worksheet3.write(row, col,item.encabezado.contrato.mcontrato.nombre,format2)
					worksheet3.write(row, col+1,item.encabezado.contrato.mcontrato.nombre+" - "+item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+2,item.encabezado.contrato.numero,format5)
					worksheet3.write(row, col+3,item.encabezado.contrato.nombre,format2)
					worksheet3.write(row, col+4,item.encabezado.referencia,format2)
					worksheet3.write(row, col+5,item.encabezado.nombre.nombre,format2)
					worksheet3.write(row, col+6,item.id,format2)
					worksheet3.write(row, col+7,item.contratista.nombre,format2)
					worksheet3.write(row, col+8,item.valor_girar,format2)
					worksheet3.write(row, col+9,item.estado.nombre,format2)
					worksheet3.write(row, col+10,item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+11,item.encabezado.contrato.contratista.codigo_acreedor,format2)
					worksheet3.write(row, col+12,item.encabezado.contrato.contratista.nombre,format2)
					if item.valor_girar is not None:
						total_anticipos=total_anticipos+item.valor_girar
					row +=1

		else:
			worksheet3.write(row, col,item.encabezado.contrato.mcontrato.nombre,format2)


			nombre_pagp=""
			if 'cuenta bancaria' in str(item.encabezado.pago_recurso.nombre).lower():
				nombre_pagp="CUENTA BANCARIA"

			else:
				nombre_pagp="RECURSOS PROPIOS ELECTRICARIBE"

			worksheet3.write(row, col+1,item.encabezado.contrato.mcontrato.nombre+" - "+nombre_pagp,format2)
			worksheet3.write(row, col+2,item.encabezado.contrato.numero,format5)
			worksheet3.write(row, col+3,item.encabezado.contrato.nombre,format2)
			worksheet3.write(row, col+4,item.encabezado.referencia,format2)
			worksheet3.write(row, col+5,item.encabezado.nombre.nombre,format2)
			worksheet3.write(row, col+6,item.id,format2)
			worksheet3.write(row, col+7,item.contratista.nombre,format2)
			worksheet3.write(row, col+8,item.valor_girar,format2)
			worksheet3.write(row, col+9,item.estado.nombre,format2)

			nombre_girar=""
			if 'cuenta bancaria' in str(item.encabezado.pago_recurso.nombre).lower():
				financiero=FinancieroCuenta.objects.filter(contrato_id=item.encabezado.contrato.mcontrato.id)

				tipo_cuenta2=""

				if 'ahorro' in str(financiero[0].tipo.nombre).lower():
					tipo_cuenta2='AHO'

				if 'corriente' in str(financiero[0].tipo.nombre).lower():
					tipo_cuenta2='CTE'

				nombre_girar=financiero[0].fiduciaria+" "+tipo_cuenta2+" "+financiero[0].numero

			else:
				nombre_girar="RECURSOS PROPIOS ELECTRICARIBE"

			worksheet3.write(row, col+10,nombre_girar,format2)
			worksheet3.write(row, col+11,item.encabezado.contrato.contratista.codigo_acreedor,format2)
			worksheet3.write(row, col+12,item.encabezado.contrato.contratista.nombre,format2)
			if item.valor_girar is not None:
				total_anticipos=total_anticipos+item.valor_girar
			row +=1



	workbook.close()

	return response
    #return response



def descargar_informe_financiero_origen(request):

	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="informe_financiero.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})

	format1=workbook.add_format({'border':1,'font_size':12,'bold':True})
	format2=workbook.add_format({'border':1})

	format5=workbook.add_format({'border':1})
	format5.set_num_format('yyyy-mm-dd')


	macrocontrato_id= request.GET['macrocontrato_id']
	fecha= request.GET['fecha']
	activar= request.GET['activar']
	contrato_id= request.GET['contrato_id']


	worksheet2 = workbook.add_worksheet('Facturas')
	worksheet3 = workbook.add_worksheet('Anticipos')
	worksheet4 = workbook.add_worksheet('Multas')
	worksheet5 = workbook.add_worksheet('Cruces')

	worksheet2.set_column('A:O', 30)
	worksheet3.set_column('A:O', 30)
	worksheet4.set_column('A:O', 30)	
	worksheet5.set_column('A:O', 30)	


	total_facturas=0
	total_anticipos=0
	total_multas=0


	contrato=None
	if int(activar) == 0:
		contrato=Contrato.objects.get(pk=macrocontrato_id)
	else:
		contrato=Contrato.objects.get(pk=contrato_id)

	facturas=None

	if int(activar)== 0:

		if 'prone' in str(contrato.nombre).lower():

			if fecha != '':
				facturas=Factura.objects.filter(mcontrato_id=macrocontrato_id,contrato__tipo_contrato_id__in=[8,10,11,13,14,103],fecha__lte=fecha)			
			else:
				facturas=Factura.objects.filter(mcontrato_id=macrocontrato_id,contrato__tipo_contrato_id__in=[8,10,11,13,14,103])			

		if 'faer' in str(contrato.nombre).lower():

			if fecha != '':
				facturas=Factura.objects.filter(mcontrato_id=macrocontrato_id,contrato__tipo_contrato_id__in=[8,9,11,13,14,103],fecha__lte=fecha)
			else:
				facturas=Factura.objects.filter(mcontrato_id=macrocontrato_id,contrato__tipo_contrato_id__in=[8,9,11,13,14,103])

	else:
		if fecha != '':
			facturas=Factura.objects.filter(contrato_id=contrato_id,fecha__lte=fecha)
		else:
			facturas=Factura.objects.filter(contrato_id=contrato_id)

	row=1
	col=0

	worksheet2.write('A1', 'Macrocontrato', format1)
	worksheet2.write('B1', 'Numero de contrato', format1)
	worksheet2.write('C1', 'Nombre Contrato', format1)
	worksheet2.write('D1', 'Numero Factura', format1)
	worksheet2.write('E1', 'Fecha Factura', format1)
	worksheet2.write('F1', 'Origen de Recursos', format1)
	worksheet2.write('G1', 'Referencia SAP', format1)
	worksheet2.write('H1', 'Codigo acreedor', format1)
	worksheet2.write('I1', 'Nombre acreedor', format1)
	worksheet2.write('J1', 'Valor factura antes de Impuesto y retencion', format1)
	worksheet2.write('K1', 'Valor Contable', format1)
	worksheet2.write('L1', 'Referencia SAP Anticipos Cruzados', format1)
	worksheet2.write('M1', 'Anticipos Cruzados', format1)

	
	for item in facturas:

		worksheet2.write(row, col,item.contrato.mcontrato.nombre,format2)
		worksheet2.write(row, col+1,item.contrato.numero,format2)
		worksheet2.write(row, col+2,item.contrato.nombre,format5)
		worksheet2.write(row, col+3,item.numero,format2)
		worksheet2.write(row, col+4,item.fecha,format5)

		recursos=''
		if item.recursos_propios==True:
			recursos='RECURSOS PROPIOS DE ELECTRICARIBE'
		else:
			financiero=FinancieroCuenta.objects.filter(contrato_id=item.contrato.mcontrato.id)
			tipo_cuenta2=""

			if 'ahorro' in str(financiero[0].tipo.nombre).lower():
				tipo_cuenta2='AHO'

			if 'corriente' in str(financiero[0].tipo.nombre).lower():
				tipo_cuenta2='CTE'

			recursos=financiero[0].fiduciaria+" "+tipo_cuenta2+" "+financiero[0].numero


		worksheet2.write(row, col+5,recursos,format5)

		worksheet2.write(row, col+6,item.referencia,format2)
		worksheet2.write(row, col+7,item.contrato.contratista.codigo_acreedor,format2)
		worksheet2.write(row, col+8,item.contrato.contratista.nombre,format2)
		worksheet2.write(row, col+9,item.valor_factura,format2)
		worksheet2.write(row, col+10,item.valor_contable,format2)


		compensacion=DetalleCompensacion.objects.filter(id_registro=item.id,tablaForanea_id=140)
		valor_sap=''
		valor_anticipos=''

		for item2 in compensacion:
			list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2.compensacion_id).order_by('tablaForanea_id')
			num_conse=1

			for item3 in list_compensacion:

				if int(item3.tablaForanea_id)==38:
					encabezado=DEncabezadoGiro.objects.get(pk=item3.id_registro)
					if valor_sap=='':
						valor_sap=encabezado.referencia
					else:
						valor_sap=valor_sap+','+encabezado.referencia

					if valor_anticipos=='':
						valor_anticipos=encabezado.nombre.nombre+'('+encabezado.contrato.numero+')'
					else:
						valor_anticipos=valor_anticipos+','+encabezado.nombre.nombre+'('+encabezado.contrato.numero+')'


				if int(item3.tablaForanea_id)==161:
					multa=Solicitud.objects.get(pk=item3.id_registro)
					if valor_sap=='':
						valor_sap=multa.codigoOF
					else:
						valor_sap=valor_sap+','+multa.codigoOF

					if valor_anticipos=='':
						valor_anticipos='Multa '+str(num_conse)
						num_conse=num_conse+1
					else:
						valor_anticipos=valor_anticipos+', Multa '+str(num_conse)
						num_conse=num_conse+1


		worksheet2.write(row, col+11,valor_sap,format2)
		worksheet2.write(row, col+12,valor_anticipos,format2)

		if item.valor_factura is not None:
			total_facturas=total_facturas+item.valor_factura

		row +=1


	tipo_bancaria=Tipo.objects.filter(app='encabezadoGiro_pago_recurso',codigo=1)
	autorizado=Estado.objects.filter(app='EstadoGiro',codigo=2)
	pagado=Estado.objects.filter(app='EstadoGiro',codigo=3)

	if int(activar) == 0:
		detalle=DetalleGiro.objects.filter(encabezado__contrato__mcontrato_id=macrocontrato_id)
	else:
		detalle=DetalleGiro.objects.filter(encabezado__contrato_id=contrato_id)

	row=1
	col=0

	worksheet3.write('A1', 'Macrocontrato', format1)
	worksheet3.write('B1', 'Contrato y Origen de fondos', format1)
	worksheet3.write('C1', 'Numero Contrato', format1)
	worksheet3.write('D1', 'Nombre Contrato', format1)
	worksheet3.write('E1', 'Referencia SAP', format1)
	worksheet3.write('F1', 'Nombre del giro', format1)
	worksheet3.write('G1', 'Linea', format1)
	worksheet3.write('H1', 'Proveedor', format1)
	worksheet3.write('I1', 'Valor Giro', format1)
	worksheet3.write('J1', 'Estado Giro', format1)
	worksheet3.write('K1', 'Pago Recurso', format1)
	worksheet3.write('L1', 'Numero Acreedor', format1)
	worksheet3.write('M1', 'Nombre Acreedor', format1)
	worksheet3.write('N1', 'Referencia SAP Facturas Cruzadas', format1)
	worksheet3.write('O1', 'Numero de Facturas Cruzadas', format1)


	
	for item in detalle:
		
		if fecha != '':
			if int(item.estado.id)==int(pagado[0].id):
				if str(fecha) >= str(item.fecha_pago):
					worksheet3.write(row, col,item.encabezado.contrato.mcontrato.nombre,format2)
					worksheet3.write(row, col+1,item.encabezado.contrato.mcontrato.nombre+" - "+item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+2,item.encabezado.contrato.numero,format5)
					worksheet3.write(row, col+3,item.encabezado.contrato.nombre,format2)
					worksheet3.write(row, col+4,item.encabezado.referencia,format2)
					worksheet3.write(row, col+5,item.encabezado.nombre.nombre,format2)
					worksheet3.write(row, col+6,item.id,format2)
					worksheet3.write(row, col+7,item.contratista.nombre,format2)
					worksheet3.write(row, col+8,item.valor_girar,format2)
					worksheet3.write(row, col+9,item.estado.nombre,format2)
					worksheet3.write(row, col+10,item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+11,item.encabezado.contrato.contratista.codigo_acreedor,format2)
					worksheet3.write(row, col+12,item.encabezado.contrato.contratista.nombre,format2)

					compensacion=DetalleCompensacion.objects.filter(id_registro=item.encabezado.id,tablaForanea_id=38)
					valor_sap=''
					valor_factura=''

					for item2 in compensacion:
						list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2.compensacion_id).order_by('tablaForanea_id')
						num_conse=1

						for item3 in list_compensacion:

							if int(item3.tablaForanea_id)==140:
								factura=Factura.objects.get(pk=item3.id_registro)
								if valor_sap=='':
									valor_sap=factura.referencia
								else:
									valor_sap=valor_sap+','+factura.referencia

								if valor_factura=='':
									valor_factura=factura.numero
								else:
									valor_factura=valor_factura+','+factura.numero


							if int(item3.tablaForanea_id)==161:
								multa=Solicitud.objects.get(pk=item3.id_registro)
								if valor_sap=='':
									valor_sap=multa.codigoOF
								else:
									valor_sap=valor_sap+','+multa.codigoOF

								if valor_factura=='':
									valor_factura='Multa '+str(num_conse)
									num_conse=num_conse+1
								else:
									valor_factura=valor_factura+', Multa '+str(num_conse)
									num_conse=num_conse+1


					worksheet3.write(row, col+13,valor_sap,format2)
					worksheet3.write(row, col+14,valor_factura,format2)

					if item.valor_girar is not None:
						total_anticipos=total_anticipos+item.valor_girar
					row +=1

			if int(item.estado.id)==int(autorizado[0].id):
				if str(fecha) >= str(item.carta_autorizacion.fechaEnvio):
					worksheet3.write(row, col,item.encabezado.contrato.mcontrato.nombre,format2)
					worksheet3.write(row, col+1,item.encabezado.contrato.mcontrato.nombre+" - "+item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+2,item.encabezado.contrato.numero,format5)
					worksheet3.write(row, col+3,item.encabezado.contrato.nombre,format2)
					worksheet3.write(row, col+4,item.encabezado.referencia,format2)
					worksheet3.write(row, col+5,item.encabezado.nombre.nombre,format2)
					worksheet3.write(row, col+6,item.id,format2)
					worksheet3.write(row, col+7,item.contratista.nombre,format2)
					worksheet3.write(row, col+8,item.valor_girar,format2)
					worksheet3.write(row, col+9,item.estado.nombre,format2)
					worksheet3.write(row, col+10,item.encabezado.pago_recurso.nombre,format2)
					worksheet3.write(row, col+11,item.encabezado.contrato.contratista.codigo_acreedor,format2)
					worksheet3.write(row, col+12,item.encabezado.contrato.contratista.nombre,format2)

					compensacion=DetalleCompensacion.objects.filter(id_registro=item.encabezado.id,tablaForanea_id=38)
					valor_sap=''
					valor_factura=''

					for item2 in compensacion:
						list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2.compensacion_id).order_by('tablaForanea_id')
						num_conse=1

						for item3 in list_compensacion:

							if int(item3.tablaForanea_id)==140:
								factura=Factura.objects.get(pk=item3.id_registro)
								if valor_sap=='':
									valor_sap=factura.referencia
								else:
									valor_sap=valor_sap+','+factura.referencia

								if valor_factura=='':
									valor_factura=factura.numero
								else:
									valor_factura=valor_factura+','+factura.numero


							if int(item3.tablaForanea_id)==161:
								multa=Solicitud.objects.get(pk=item3.id_registro)
								if valor_sap=='':
									valor_sap=multa.codigoOF
								else:
									valor_sap=valor_sap+','+multa.codigoOF

								if valor_factura=='':
									valor_factura='Multa '+str(num_conse)
									num_conse=num_conse+1
								else:
									valor_factura=valor_factura+', Multa '+str(num_conse)
									num_conse=num_conse+1

					worksheet3.write(row, col+13,valor_sap,format2)
					worksheet3.write(row, col+14,valor_factura,format2)

					if item.valor_girar is not None:
						total_anticipos=total_anticipos+item.valor_girar
					row +=1

		else:
			worksheet3.write(row, col,item.encabezado.contrato.mcontrato.nombre,format2)
			worksheet3.write(row, col+1,item.encabezado.contrato.mcontrato.nombre+" - "+item.encabezado.pago_recurso.nombre,format2)
			worksheet3.write(row, col+2,item.encabezado.contrato.numero,format5)
			worksheet3.write(row, col+3,item.encabezado.contrato.nombre,format2)
			worksheet3.write(row, col+4,item.encabezado.referencia,format2)
			worksheet3.write(row, col+5,item.encabezado.nombre.nombre,format2)
			worksheet3.write(row, col+6,item.id,format2)
			worksheet3.write(row, col+7,item.contratista.nombre,format2)
			worksheet3.write(row, col+8,item.valor_girar,format2)
			worksheet3.write(row, col+9,item.estado.nombre,format2)
			worksheet3.write(row, col+10,item.encabezado.pago_recurso.nombre,format2)
			worksheet3.write(row, col+11,item.encabezado.contrato.contratista.codigo_acreedor,format2)
			worksheet3.write(row, col+12,item.encabezado.contrato.contratista.nombre,format2)

			compensacion=DetalleCompensacion.objects.filter(id_registro=item.encabezado.id,tablaForanea_id=38)
			valor_sap=''
			valor_factura=''

			for item2 in compensacion:
				list_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item2.compensacion_id).order_by('tablaForanea_id')
				num_conse=1

				for item3 in list_compensacion:

					if int(item3.tablaForanea_id)==140:
						factura=Factura.objects.get(pk=item3.id_registro)
						if valor_sap=='':
							valor_sap=factura.referencia
						else:
							valor_sap=valor_sap+','+factura.referencia

						if valor_factura=='':
							valor_factura=factura.numero
						else:
							valor_factura=valor_factura+','+factura.numero


					if int(item3.tablaForanea_id)==161:
						multa=Solicitud.objects.get(pk=item3.id_registro)
						if valor_sap=='':
							valor_sap=multa.codigoOF
						else:
							valor_sap=valor_sap+','+multa.codigoOF

						if valor_factura=='':
							valor_factura='Multa '+str(num_conse)
							num_conse=num_conse+1
						else:
							valor_factura=valor_factura+', Multa '+str(num_conse)
							num_conse=num_conse+1


			worksheet3.write(row, col+13,valor_sap,format2)
			worksheet3.write(row, col+14,valor_factura,format2)

			if item.valor_girar is not None:
				total_anticipos=total_anticipos+item.valor_girar
			row +=1
		


	row=1
	col=0


	estado_confirmada=Estado.objects.filter(app='multa',codigo=5)
	estado_contabiizada=Estado.objects.filter(app='multa',codigo=10)

	if int(activar) == 0:
		multas=Solicitud.objects.filter(contrato__mcontrato_id=macrocontrato_id)
	else:
		multas=Solicitud.objects.filter(contrato_id=contrato_id)

	worksheet4.write('A1', 'Macrocontrato', format1)
	worksheet4.write('B1', 'Numero Contrato', format1)
	worksheet4.write('C1', 'Nombre Contrato', format1)
	worksheet4.write('D1', 'Codigo Acreedor', format1)
	worksheet4.write('E1', 'Nombre Acreedor', format1)
	worksheet4.write('F1', 'Codigo OF', format1)
	worksheet4.write('G1', 'Valor Impuesto', format1)
	
	for item in multas:

		estado_multa=None
		if fecha != '': 
			estado_multa=SolicitudHistorial.objects.filter(solicitud_id=item.id,fecha__lte=fecha).order_by('-id').first()
		else:
			estado_multa=SolicitudHistorial.objects.filter(solicitud_id=item.id).order_by('-id').first()

		if int(estado_multa.estado_id)==int(estado_confirmada[0].id) or int(estado_multa.estado_id)==int(estado_contabiizada[0].id):

			worksheet4.write(row, col,item.contrato.mcontrato.nombre,format2)
			worksheet4.write(row, col+1,item.contrato.numero,format5)
			worksheet4.write(row, col+2,item.contrato.nombre,format2)
			worksheet4.write(row, col+3,item.contrato.contratista.codigo_acreedor,format2)
			worksheet4.write(row, col+4,item.contrato.contratista.nombre,format2)
			worksheet4.write(row, col+5,item.codigoOF,format2)
			worksheet4.write(row, col+6,item.valorImpuesto,format2)
			if item.valorImpuesto is not None:
				total_multas=total_multas+item.valorImpuesto
			row +=1


	row=1
	col=0

	worksheet5.write('A1', 'Macrocontrato', format1)
	worksheet5.write('B1', 'Numero Contrato', format1)
	worksheet5.write('C1', 'Nombre Contrato', format1)
	worksheet5.write('D1', 'Tipo', format1)
	worksheet5.write('E1', 'No. Factura / Nombre anticipo', format1)
	worksheet5.write('F1', 'Documento SAP / Codigo OF', format1)
	worksheet5.write('G1', 'Valor', format1)

	sql_compensada=None

	if int(activar) == 0:
		sql_compensada=Compensacion.objects.filter(contrato__mcontrato_id=macrocontrato_id)
	else:
		sql_compensada=Compensacion.objects.filter(contrato_id=contrato_id)


	for item in sql_compensada:
		sql_compensacion=DetalleCompensacion.objects.filter(compensacion_id=item.id)

		for item2 in sql_compensacion:
			if int(item2.tablaForanea_id)==38:
				sql_resultado=DEncabezadoGiro.objects.get(pk=item2.id_registro)
				sumatoria=DetalleGiro.objects.filter(encabezado_id=sql_resultado.id).aggregate(suma_detalle=Sum('valor_girar'))

				worksheet5.write(row, col,sql_resultado.contrato.mcontrato.nombre,format2)
				worksheet5.write(row, col+1,sql_resultado.contrato.numero,format5)
				worksheet5.write(row, col+2,sql_resultado.contrato.nombre,format2)
				worksheet5.write(row, col+3,"Anticipos",format2)
				worksheet5.write(row, col+4,sql_resultado.nombre.nombre,format2)
				worksheet5.write(row, col+5,sql_resultado.referencia,format2)
				worksheet5.write(row, col+6,sumatoria['suma_detalle'],format2)
				row +=1

			if int(item2.tablaForanea_id)==140:
				sql_resultado=Factura.objects.get(pk=item2.id_registro)

				worksheet5.write(row, col,sql_resultado.contrato.mcontrato.nombre,format2)
				worksheet5.write(row, col+1,sql_resultado.contrato.numero,format5)
				worksheet5.write(row, col+2,sql_resultado.contrato.nombre,format2)
				worksheet5.write(row, col+3,"Factura",format2)
				worksheet5.write(row, col+4,sql_resultado.numero,format2)
				worksheet5.write(row, col+5,sql_resultado.referencia,format2)
				worksheet5.write(row, col+6,"-"+str(sql_resultado.valor_contable),format2)
				row +=1

			if int(item2.tablaForanea_id)==161:
				sql_resultado=Solicitud.objects.get(pk=item2.id_registro)

				worksheet5.write(row, col,sql_resultado.contrato.mcontrato.nombre,format2)
				worksheet5.write(row, col+1,sql_resultado.contrato.numero,format5)
				worksheet5.write(row, col+2,sql_resultado.contrato.nombre,format2)
				worksheet5.write(row, col+3,"Multa",format2)
				worksheet5.write(row, col+4,"No Aplica",format2)
				worksheet5.write(row, col+5,sql_resultado.codigoOF,format2)
				worksheet5.write(row, col+6,sql_resultado.valorImpuesto,format2)
				row +=1



	workbook.close()

	return response
    #return response



#Fin api rest para encabezado del giro
@login_required
def informe_financiero(request):
		return render(request, 'financiero_cuenta/informe_financiero.html',{'app':'financiero','model':'financierocuenta'})


@login_required
def index_informe(request):
		return render(request, 'financiero_cuenta/index_informe.html',{'app':'financiero','model':'financierocuenta'})


@login_required
def informe_financiero_contratista(request):
		return render(request, 'financiero_cuenta/informe_financiero_contratista.html',{'app':'financiero','model':'financierocuenta'})


@login_required
def reporte_pago(request):
		return render(request, 'financiero_cuenta/reporte_pago.html',{'app':'financiero','model':'financierocuenta'})


@login_required
def informe_anticipos(request):
		return render(request, 'financiero_cuenta/informe_anticipos.html',{'app':'financiero','model':'financierocuenta'})


@login_required
def informe_financiero_origen(request):
		return render(request, 'financiero_cuenta/informe_financiero_origen.html',{'app':'financiero','model':'financierocuenta'})

@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			archivo = NExtracto.objects.get(pk=request.GET['id'])			
			return functions.exportarArchivoS3(str(archivo.soporte))

		except Exception as e:
			functions.toLog(e,'constrato.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			

