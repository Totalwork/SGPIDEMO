from django.shortcuts import render,redirect
#,render_to_response
#from django.urls import reverse
from django.urls import reverse
from .models import APeriodicidad,BCronograma,CIntervaloCronograma,DActividad,Linea,Meta,Porcentaje,Soporte,Comentario
from .models import Porcentaje,Soporte,Comentario,AEsquemaCapitulos,AEsquemaCapitulosActividades,AReglasEstado
from rest_framework import viewsets, serializers
from django.db.models import Q,Sum,Prefetch
from logs.models import Logs,Acciones
from usuario.models import Usuario
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

from proyecto.views import ProyectoSerializer
from proyecto.models import Proyecto

from contrato.models import EmpresaContrato,Contrato
from contrato.views import ContratoSerializer
from contrato.enumeration import tipoC

from parametrizacion.models import Departamento

from django.db import connection

from datetime import timedelta

from usuario.views import UsuarioSerializer

from django.core.paginator import Paginator
from avance_de_obra.tasks import createAsyncLine,createAsyncIntervalo,createAsyncEsquema,createAsyncEstado,updateAsyncEstado,updateActividad
from django.contrib.auth.decorators import login_required

from parametrizacion.views import  MunicipioSerializer

from django.conf import settings
from django.db import transaction
from coasmedas.functions import functions

# Create your views here.

#Api rest para periodicidad
class PeriodicidadSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = APeriodicidad
		fields=('id','nombre','numero_dias')


class PeriodicidadViewSet(viewsets.ModelViewSet):
	
	model=APeriodicidad
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='avance_de_obra.periodicidad'
	queryset = model.objects.all()
	serializer_class = PeriodicidadSerializer

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
			queryset = super(PeriodicidadViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			if dato:
				qset = (
					Q(nombre__icontains=dato)
					)
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
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


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = PeriodicidadSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save()
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
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
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = PeriodicidadSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
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

#Fin Api rest para periodicidad


# Serializador de contrato
class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):
	soloLectura = serializers.SerializerMethodField()
	class Meta:
		model = Contrato
		fields=('id','nombre', 'contratista', 'soloLectura')

	def get_soloLectura(self, obj):
		request = self.context.get("request")
		if request is None:
			return False
		contrato = None
		if obj.mcontrato:
			contrato = obj.mcontrato.id
		else:
			contrato = obj.id

		empresaContrato = EmpresaContrato.objects.filter(contrato__id=contrato, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		return soloLectura	


#Api rest para Esquema de Capitulos
class EsquemaCapitulosSerializer(serializers.HyperlinkedModelSerializer):

	tipo=tipoC()
	macrocontrato=ContratoLiteSerializer(read_only=True)
	macrocontrato_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Contrato.objects.filter(tipo_contrato=tipo.m_contrato))	

	class Meta:
		model = AEsquemaCapitulos
		fields=('id','macrocontrato','macrocontrato_id','nombre')


class EsquemaCapitulosViewSet(viewsets.ModelViewSet):
	
	model=AEsquemaCapitulos
	queryset = model.objects.all()
	serializer_class = EsquemaCapitulosSerializer	
	model_log=Logs
	model_acciones=Acciones	
	nombre_modulo='avance_de_obra.esquema_capitulos'

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
			queryset = super(EsquemaCapitulosViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			macrocontrato_id= self.request.query_params.get('macrocontrato_id',None)
			lista_contrato=[]
			tipo=tipoC()
			mcontrato=EmpresaContrato.objects.filter(contrato__tipo_contrato=tipo.m_contrato,empresa=request.user.usuario.empresa.id,participa=1)

			if mcontrato is None:
				lista_contrato.append(0)
			else:
				for item in mcontrato:
					lista_contrato.append(item.contrato.id)

			qset=(Q(macrocontrato_id__in=lista_contrato))
			if dato:
				qset = qset &(
					Q(nombre__icontains=dato)
					)

			if macrocontrato_id is not None and int(macrocontrato_id)>0:
				qset=qset&(Q(macrocontrato_id=macrocontrato_id))

			
			
			if qset is not None:
				queryset = self.model.objects.filter(qset)	

			if sin_paginacion is None:
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

	@transaction.atomic		
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = EsquemaCapitulosSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(macrocontrato_id=request.DATA['macrocontrato_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
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
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = EsquemaCapitulosSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				
				if serializer.is_valid():
					valor2=AEsquemaCapitulos.objects.get(pk=instance.id)
					if valor2.macrocontrato_id!=request.DATA['macrocontrato_id']:
						valor=BCronograma.objects.filter(esquema_id=instance.id)
						if len(valor)>0:
							return Response({'message':'No se puede cambiar el macrocontrato, se esta usado en un cronograma','success':'fail',
			 					'data':''},status=status.HTTP_400_BAD_REQUEST)
					
					serializer.save(macrocontrato_id=request.DATA['macrocontrato_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
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

#Fin Api rest para Esquema de Capitulos


#Api rest para Esquema de Capitulos de las actividades
class EsquemaCapitulosActividadesSerializer(serializers.HyperlinkedModelSerializer):

	esquema=EsquemaCapitulosSerializer(read_only=True)
	esquema_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=AEsquemaCapitulos.objects.all())	

	class Meta:
		model = AEsquemaCapitulosActividades
		fields=('id','esquema','esquema_id','nombre','nivel','padre','peso')


class EsquemaCapitulosActividadesViewSet(viewsets.ModelViewSet):
	
	model=AEsquemaCapitulosActividades
	queryset = model.objects.all()
	serializer_class = EsquemaCapitulosActividadesSerializer	
	model_log=Logs
	model_acciones=Acciones	
	nombre_modulo='avance_de_obra.esquema_capitulos_actividades'

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
			queryset = super(EsquemaCapitulosActividadesViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			if dato:
				qset = (
					Q(nombre__icontains=dato)
					)
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
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


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = EsquemaCapitulosActividadesSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					model_actividad=AEsquemaCapitulosActividades.objects.filter(esquema_id=request.DATA['esquema_id'],nivel=1).aggregate(Sum('peso'))
					model_actividad['peso__sum']=0 if model_actividad['peso__sum']==None else model_actividad['peso__sum']
					valor=round(float(model_actividad['peso__sum']),3)+round(float(request.DATA['peso']),3)
					
					if float(valor) <= 100: 
						serializer.save(esquema_id=request.DATA['esquema_id'])
						logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
						logs_model.save()

						updateActividad.delay(request.DATA['esquema_id'],serializer.data['id'])
						padre=request.DATA['padre']

						if padre>0:
							if int(request.DATA['nivel'])==3:
								valores=AEsquemaCapitulosActividades.objects.get(pk=padre)
								valor=float(valores.peso)+float(request.DATA['peso'])
								valores.peso=valor
								valores.save()
								logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=padre)
								logs_model.save()								
								padre=valores.padre

							valores=AEsquemaCapitulosActividades.objects.get(pk=padre)
							valor=float(valores.peso)+float(request.DATA['peso'])
							valores.peso=valor
							valores.save()
							logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=padre)
							logs_model.save()

						transaction.savepoint_commit(sid)

					else:
						return Response({'message':'El registro no se guardo, por que supera el porcentaje de 100%','success':'fail',
						'data':serializer.data},status=status.HTTP_201_CREATED)
					
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
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = EsquemaCapitulosActividadesSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					model_actividad=AEsquemaCapitulosActividades.objects.filter(esquema_id=request.DATA['esquema_id'],nivel=1).aggregate(Sum('peso'))
					model_actividad['peso__sum']=0 if model_actividad['peso__sum']==None else model_actividad['peso__sum']

					model_actividad2=AEsquemaCapitulosActividades.objects.get(pk=instance.id)
					valor_restante=float(request.DATA['peso']) - float(model_actividad2.peso)
					valor=float(model_actividad['peso__sum'])+valor_restante

					if float(valor) <= 100: 
						serializer.save(esquema_id=request.DATA['esquema_id'])					
						logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
						logs_model.save()
						padre=request.DATA['padre']

						if padre>0:
							if int(request.DATA['nivel'])==3:
								valores=AEsquemaCapitulosActividades.objects.get(pk=padre)
								valor=float(valores.peso)+float(valor_restante)
								valores.peso=valor
								valores.save()
								logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=padre)
								logs_model.save()
								padre=valores.padre

							valores=AEsquemaCapitulosActividades.objects.get(pk=padre)
							valor=float(valores.peso)+float(valor_restante)
							valores.peso=valor
							valores.save()
							logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=padre)
							logs_model.save()

						transaction.savepoint_commit(sid)

					else:
						return Response({'message':'El registro no se guardo, por que supera el porcentaje de 100%','success':'fail',
						'data':serializer.data},status=status.HTTP_201_CREATED)

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

#Fin Api rest para Esquema de Capitulos de las actividades



#Api rest para regla de estado
class ReglaEstadoSerializer(serializers.HyperlinkedModelSerializer):

	esquema=EsquemaCapitulosSerializer(read_only=True)
	esquema_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=AEsquemaCapitulos.objects.all())

	reglaAnterior=serializers.SerializerMethodField()	

	class Meta:
		model = AReglasEstado
		fields=('id','esquema','esquema_id','orden','operador','limite','estado','reglaAnterior',)

	def get_reglaAnterior(self, obj):
		return AReglasEstado.objects.filter(orden__lt=obj.orden,esquema_id=obj.esquema_id).values('id','estado').order_by('orden').last()


class ReglaEstadoViewSet(viewsets.ModelViewSet):
	
	model=AReglasEstado
	queryset = model.objects.all()
	serializer_class = ReglaEstadoSerializer	
	model_log=Logs
	model_acciones=Acciones	
	nombre_modulo='avance_de_obra.regla'

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
			queryset = super(ReglaEstadoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			esquema_id= self.request.query_params.get('esquema_id',None)
			qset=None


			if dato:
				qset = (
					Q(estado__icontains=dato)
					)

			if esquema_id and esquema_id>0:
				if dato:
					qset = qset &(
					Q(esquema_id=esquema_id)
					)
				else:
					qset =(
					Q(esquema_id=esquema_id)
					)

			if qset !=None:
				queryset = self.model.objects.filter(qset).order_by('orden')


			if sin_paginacion is None:
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

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				reglas=AReglasEstado.objects.filter(esquema_id=request.DATA['esquema_id'])
				if len(reglas) > 0:
					for item in list(reglas):
						if int(item.operador)==int(request.DATA['operador']) and float(item.limite)==float(request.DATA['limite']):
							return Response({'message':'Debe registrar otro operador o limite, el limite y el operador ya existe','success':'fail',
				 					'data':''},status=status.HTTP_400_BAD_REQUEST)

				orden=None
				orden=AReglasEstado.objects.filter(esquema_id=request.DATA['esquema_id']).order_by('orden').last()
				
				if orden is None:
					request.DATA['orden']=1
				else:
					request.DATA['orden']=orden.orden+1

				if int(request.DATA['regla_anterior'])>0:
					reglas2=AReglasEstado.objects.get(pk=request.DATA['regla_anterior'])
					valor=int(reglas2.orden)+1
					request.DATA['orden']=valor

					if float(reglas2.limite)>=float(request.DATA['limite']) and int(reglas2.operador)==int(request.DATA['operador']):
						return Response({'message':'Debe registrar otro limite, el limite es menor que el limite anterior','success':'fail',
			 					'data':''},status=status.HTTP_400_BAD_REQUEST)

					reglas3=AReglasEstado.objects.filter(orden__gt=reglas2.orden,esquema_id=request.DATA['esquema_id'])
					if len(reglas3)>0:
						for item in reglas3:
							if float(item.limite)<=float(request.DATA['limite']) and int(item.operador)==int(request.DATA['operador']):
								return Response({'message':'Debe registrar otro limite, el limite es mayor que el limite siguiente','success':'fail',
				 					'data':''},status=status.HTTP_400_BAD_REQUEST)

						reglas_actualizar=AReglasEstado.objects.filter(orden__gt=reglas2.orden,esquema_id=request.DATA['esquema_id'])
						for item2 in reglas_actualizar:
							estado=AReglasEstado.objects.get(pk=item2.id)
							estado.orden=estado.orden+1
							estado.save()
				
				serializer = ReglaEstadoSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(esquema_id=request.DATA['esquema_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()
					updateAsyncEstado.delay(request.DATA['esquema_id'])
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
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()

				reglas=AReglasEstado.objects.filter(esquema_id=request.DATA['esquema_id'])
				for item in list(reglas):
					if item.id!=instance.id:
						if int(item.operador)==int(request.DATA['operador']) and float(item.limite)==float(request.DATA['limite']):
							return Response({'message':'Debe registrar otro operador o limite, el limite y el operador ya existe','success':'fail',
				 					'data':''},status=status.HTTP_400_BAD_REQUEST)

				if int(request.DATA['regla_anterior'])>0:					
					valor=AReglasEstado.objects.filter(orden__lt=request.DATA['orden'],esquema_id=request.DATA['esquema_id']).values('id','estado','orden').order_by('orden').last()
					if valor is None:
						valor=0

					reglas2=AReglasEstado.objects.get(pk=request.DATA['regla_anterior'])
					if float(reglas2.limite)>=float(request.DATA['limite']) and int(reglas2.operador)==int(request.DATA['operador']):
							return Response({'message':'Debe registrar otro limite, el limite es menor que el limite anterior','success':'fail',
				 					'data':''},status=status.HTTP_400_BAD_REQUEST)

					reglas3=AReglasEstado.objects.filter(orden__gt=request.DATA['orden'],esquema_id=request.DATA['esquema_id']).values('id','estado','orden','limite','operador').order_by('orden').first()
					if reglas3 is not None:
							if float(reglas3['limite'])<=float(request.DATA['limite']) and int(reglas3['operador'])==int(request.DATA['operador']):
								return Response({'message':'Debe registrar otro limite, el limite es mayor que el limite siguiente','success':'fail',
						 					'data':''},status=status.HTTP_400_BAD_REQUEST)

					if int(request.DATA['regla_anterior'])!=int(valor['id']):
						valor=int(reglas2.orden)+1
						request.DATA['orden']=valor	
						if reglas3 is not None:
							reglas_actualizar=AReglasEstado.objects.filter(orden__gt=reglas2.orden,esquema_id=request.DATA['esquema_id'])
							for item2 in reglas_actualizar:
								estado=AReglasEstado.objects.get(pk=item2.id)
								estado.orden=estado.orden+1
								estado.save()


				serializer = ReglaEstadoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(esquema_id=request.DATA['esquema_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()
					updateAsyncEstado.delay(request.DATA['esquema_id'])
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

#Fin Api rest para regla de estado


# Serializer de proyecto
class ProyectoLiteSerializer(serializers.HyperlinkedModelSerializer):

	municipio = MunicipioSerializer(read_only = True)
	totalCronograma=serializers.SerializerMethodField()
	soloLectura = serializers.SerializerMethodField()
	class Meta: 
		model = Proyecto
		fields=( 'id','nombre','municipio','totalCronograma', 'soloLectura')

	def get_totalCronograma(self, obj):
		return BCronograma.objects.filter(proyecto_id=obj.id).count()

	def get_soloLectura(self, obj):
		request = self.context.get("request")
		if request is None:
			return False
		empresaContrato = EmpresaContrato.objects.filter(contrato__id=obj.mcontrato.id, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		return soloLectura	
	

#Api rest para cronograma
class CronogramaSerializer(serializers.HyperlinkedModelSerializer):

	proyecto=ProyectoLiteSerializer(read_only=True)
	proyecto_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto.objects.all())

	periodicidad=PeriodicidadSerializer(read_only=True)
	periodicidad_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=APeriodicidad.objects.all())

	esquema=EsquemaCapitulosSerializer(read_only=True)
	esquema_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=AEsquemaCapitulos.objects.all())

	estado=ReglaEstadoSerializer(read_only=True)
	class Meta:
		model = BCronograma
		fields=('id','nombre','proyecto','proyecto_id','intervalos',
			'linea_base_terminada','fecha_inicio_cronograma','periodicidad','periodicidad_id','esquema','esquema_id',
			'estado','porcentaje_avance',)


class CronogramaViewSet(viewsets.ModelViewSet):
	
	model=BCronograma
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='avance_de_obra.cronograma'
	queryset = model.objects.all()
	serializer_class = CronogramaSerializer

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
			queryset = super(CronogramaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			id_proyecto= self.request.query_params.get('id_proyecto',None)

			if dato or id_proyecto:
				if dato:
					qset = (
						Q(nombre__icontains=dato)
						)

				if id_proyecto:
					if dato:
						qset=qset&(Q(proyecto_id=id_proyecto))
					else:
						qset=(Q(proyecto_id=id_proyecto))

				queryset = self.model.objects.filter(qset)



			if sin_paginacion is None:
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

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try: 
				serializer = CronogramaSerializer(data=request.DATA,context={'request': request})

				porcentaje=AEsquemaCapitulosActividades.objects.filter(esquema_id=request.DATA['esquema_id'],nivel=1).aggregate(Sum('peso'))
				porcentaje['peso__sum']=0 if porcentaje['peso__sum']==None else porcentaje['peso__sum']
				
				if round(porcentaje['peso__sum'])==100:

					if serializer.is_valid():
						serializer.save(proyecto_id=request.DATA['proyecto_id'],periodicidad_id=request.DATA['periodicidad_id'],esquema_id=request.DATA['esquema_id'])
						logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
						logs_model.save()

						transaction.savepoint_commit(sid)
						createAsyncIntervalo.delay(serializer.data['id'],request.DATA['intervalos'])
						createAsyncEsquema.delay(1,request.DATA['esquema_id'],serializer.data['id'],0)		

						return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
								'data':serializer.data},status=status.HTTP_201_CREATED)
					else:
						return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
				 				'data':''},status=status.HTTP_400_BAD_REQUEST)	
				
				else:
					transaction.savepoint_rollback(sid)
					return JsonResponse({'message':'El esquema seleccionado no esta al 100%','success':'error',
								'data':''})	
				
			except Exception as e:
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
				serializer = CronogramaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				porcentaje=AEsquemaCapitulosActividades.objects.filter(esquema_id=request.DATA['esquema_id'],nivel=1).aggregate(Sum('peso'))
				porcentaje['peso__sum']=0 if porcentaje['peso__sum']==None else porcentaje['peso__sum']

				if porcentaje['peso__sum']==100:					

					cursor = connection.cursor()
					cursor.callproc('[avance_de_obra].[consultar_metas]', [instance.id,])
					columns = cursor.description 
					result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]	

					sw=0
					for item in result:
						if item['cantidad'] is not None and item['cantidad']>0:
							sw=1
							break

					if sw==0:
						if serializer.is_valid():
							valor_anterior=BCronograma.objects.get(pk=instance.id)
							serializer.save(proyecto_id=request.DATA['proyecto_id'],periodicidad_id=request.DATA['periodicidad_id'],esquema_id=request.DATA['esquema_id'])
							logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
							logs_model.save()

							transaction.savepoint_commit(sid)
							createAsyncEsquema.delay(2,request.DATA['esquema_id'],instance.id,valor_anterior.esquema_id)

							return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
								'data':serializer.data},status=status.HTTP_201_CREATED)
						else:
							return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
				 				'data':''},status=status.HTTP_400_BAD_REQUEST)
					else:
						transaction.savepoint_rollback(sid)
						return Response({'message':'No se puede actualizar, los datos del esquema se esta usado en otra parte del sistema','success':'fail',
				 			'data':''},status=status.HTTP_400_BAD_REQUEST)	
				else:
					transaction.savepoint_rollback(sid)
					return JsonResponse({'message':'El esquema seleccionado no esta al 100%','success':'error',
								'data':''})	
				
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

#Fin Api rest para cronograma


#Api rest para Intervalo_Cronograma
class IntervaloCronogramaSerializer(serializers.HyperlinkedModelSerializer):

	cronograma=CronogramaSerializer(read_only=True)
	cronograma_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=BCronograma.objects.all())

	class Meta:
		model = CIntervaloCronograma
		fields=('id','cronograma','cronograma_id','intervalo','fecha_corte')


class IntervaloCronogramaViewSet(viewsets.ModelViewSet):
	
	model=CIntervaloCronograma
	queryset = model.objects.all()
	serializer_class = IntervaloCronogramaSerializer
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='avance_de_obra.intervalo_cronograma'

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
			queryset = super(IntervaloCronogramaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			if dato:
				qset = (
					Q(nombre__icontains=dato)|
					Q(iniciales__icontains=dato)
					)
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
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

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = IntervaloCronogramaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():					
					serializer.save(cronograma_id=request.DATA['cronograma_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_commit(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = IntervaloCronogramaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():					
					serializer.save(cronograma_id=request.DATA['cronograma_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_commit(sid)
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

#Fin Api rest para intervalo_cronograma


#Api rest para Comentario
class ComentarioSerializer(serializers.HyperlinkedModelSerializer):

	intervalo=IntervaloCronogramaSerializer(read_only=True)
	intervalo_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=CIntervaloCronograma.objects.all())
	usuario=UsuarioSerializer(read_only=True)
	usuario_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	class Meta:
		model = Comentario
		fields=('id','intervalo','intervalo_id','tipo_linea','comentario','usuario_id','usuario','fecha',)


class ComentarioViewSet(viewsets.ModelViewSet):
	
	model=Comentario
	queryset = model.objects.all()
	serializer_class = ComentarioSerializer
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='avance_de_obra.comentarios'

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
			queryset = super(ComentarioViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			intervalo_id = self.request.query_params.get('intervalo_id', None)
			tipo_linea = self.request.query_params.get('tipo_linea', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			qset=None

			if dato:
				qset = (
					Q(comentario__icontains=dato)
					)

			if tipo_linea:
				if dato:
					qset=qset&(
					Q(tipo_linea=tipo_linea)
					)
				else:
					qset=(
					Q(tipo_linea=tipo_linea)
					)

			if intervalo_id:
				if dato or tipo_linea:
					qset=qset&(
					Q(intervalo_id=intervalo_id)
					)
				else:
					qset=(
					Q(intervalo_id=intervalo_id)
					)

			if qset!=None:
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
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

	@transaction.atomic		
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				request.DATA['usuario_id']=request.user.usuario.id
				serializer = ComentarioSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(intervalo_id=request.DATA['intervalo_id'],usuario_id=request.DATA['usuario_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
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
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ComentarioSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(intervalo_id=request.DATA['intervalo_id'],usuario_id=request.DATA['usuario_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
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

#Fin Api rest para comentario


#Api rest para Actividad
class ActividadSerializer(serializers.HyperlinkedModelSerializer):

	cronograma=CronogramaSerializer(read_only=True)
	cronograma_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=BCronograma.objects.all())

	class Meta:
		model = DActividad
		fields=('id','cronograma','cronograma_id','nivel','padre','peso','nombre')


class ActividadViewSet(viewsets.ModelViewSet):
	
	model=DActividad
	queryset = model.objects.all()
	serializer_class = ActividadSerializer
	model_log=Logs
	model_acciones=Acciones	
	nombre_modulo='avance_de_obra.actividad'

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
			queryset = super(ActividadViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			id_cronograma= self.request.query_params.get('id_cronograma',None)
			qset=''

			if dato or id_cronograma:

				if dato:
					qset = (
						Q(nombre__icontains=dato)
						)

				if id_cronograma and int(id_cronograma)>0:
					if dato:
						qset=qset&(
								Q(cronograma_id=id_cronograma)
								)
					else:
						qset=(Q(cronograma_id=id_cronograma))

				if qset!='':
					queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
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

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ActividadSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():

					model_actividad=DActividad.objects.filter(cronograma=request.DATA['cronograma_id'],nivel=1).aggregate(Sum('peso'))
					model_actividad['peso__sum']=0 if model_actividad['peso__sum']==None else model_actividad['peso__sum']
					valor=float(model_actividad['peso__sum'])+float(request.DATA['peso'])

					if float(valor) <= 100: 
						serializer.save(cronograma_id=request.DATA['cronograma_id'])
						logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
						logs_model.save()
						padre=request.DATA['padre']

						if padre>0:
							if int(request.DATA['nivel'])==3:
								valores=DActividad.objects.get(pk=padre)
								valor=float(valores.peso)+float(request.DATA['peso'])
								valores.peso=valor
								valores.save()
								logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=padre)
								logs_model.save()								
								padre=valores.padre

							valores=DActividad.objects.get(pk=padre)
							valor=float(valores.peso)+float(request.DATA['peso'])
							valores.peso=valor
							valores.save()
							logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=padre)
							logs_model.save()

						transaction.savepoint_commit(sid)

						return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)
					else:
						transaction.savepoint_rollback(sid)
						return Response({'message':'El peso supera el 100%','success':'fail',
			 					'data':''},status=status.HTTP_400_BAD_REQUEST)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
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
				serializer = ActividadSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					model_actividad=DActividad.objects.filter(cronograma=request.DATA['cronograma_id'],nivel=1).aggregate(Sum('peso'))
					model_actividad['peso__sum']=0 if model_actividad['peso__sum']==None else model_actividad['peso__sum']

					model_actividad2=DActividad.objects.get(pk=instance.id)
					valor_restante=float(request.DATA['peso']) - float(model_actividad2.peso)
					valor=float(model_actividad['peso__sum'])+valor_restante

					if float(valor) <= 100: 
						serializer.save(cronograma_id=request.DATA['cronograma_id'])
						logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
						logs_model.save()
						padre=request.DATA['padre']

						if padre>0:
							if int(request.DATA['nivel'])==3:
								valores=DActividad.objects.get(pk=padre)
								valor=float(valores.peso)+float(valor_restante)
								valores.peso=valor
								valores.save()
								logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=padre)
								logs_model.save()
								padre=valores.padre

							valores=DActividad.objects.get(pk=padre)
							valor=float(valores.peso)+float(valor_restante)
							valores.peso=valor
							valores.save()
							logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=padre)
							logs_model.save()
						transaction.savepoint_commit(sid)

						return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
					else:
						transaction.savepoint_rollback(sid)
						return Response({'message':'El peso supera el 100%','success':'fail',
			 					'data':''},status=status.HTTP_400_BAD_REQUEST)
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

#Fin Api rest para actividad

#Api rest para Linea
class LineaSerializer(serializers.HyperlinkedModelSerializer):

	intervalo=IntervaloCronogramaSerializer(read_only=True)
	intervalo_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=CIntervaloCronograma.objects.all())
	actividad=ActividadSerializer(read_only=True)
	actividad_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=DActividad.objects.all())


	class Meta:
		model = Linea
		fields=('id','intervalo','intervalo_id','tipo_linea','cantidad','actividad','actividad_id')


class LineaViewSet(viewsets.ModelViewSet):
	
	model=Linea
	queryset = model.objects.all()
	serializer_class = LineaSerializer
	model_log=Logs
	model_acciones=Acciones	
	nombre_modulo='avance_de_obra.linea'


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
			queryset = super(LineaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			if dato:
				qset = (
					Q(nombre__icontains=dato)
					)
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
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

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = LineaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(cronograma_id=request.DATA['cronograma_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
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
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = LineaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(cronograma_id=request.DATA['cronograma_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':''},status=status.HTTP_201_CREATED)
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

#Fin Api rest para linea


#Api rest para Meta
class MetaSerializer(serializers.HyperlinkedModelSerializer):

	actividad=ActividadSerializer(read_only=True)
	actividad_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=DActividad.objects.all())


	class Meta:
		model = Meta
		fields=('id','cantidad','actividad','actividad_id')


class MetaViewSet(viewsets.ModelViewSet):
	
	model=Meta
	queryset = model.objects.all()
	serializer_class = MetaSerializer
	model_log=Logs
	model_acciones=Acciones	
	nombre_modulo='avance_de_obra.meta'

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
			queryset = super(MetaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			actividad_id = self.request.query_params.get('actividad_id', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			qset=''

			if dato:
				qset = (
					Q(cantidad__icontains=dato)
					)

			if actividad_id:
				if dato:
					qset=qset&(Q(actividad_id=actividad_id))
				else:
					qset=(Q(actividad_id=actividad_id))

			if qset!='':
				queryset = Meta.objects.filter(qset)


			if sin_paginacion is None:
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

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = MetaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(actividad_id=request.DATA['actividad_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
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
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = MetaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(actividad_id=request.DATA['actividad_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
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

#Fin Api rest para meta

#Api rest para Porcentaje
class PorcentajeSerializer(serializers.HyperlinkedModelSerializer):

	intervalo=IntervaloCronogramaSerializer(read_only=True)
	intervalo_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=CIntervaloCronograma.objects.all())
	

	class Meta:
		model = Porcentaje
		fields=('id','tipo_linea','intervalo','intervalo_id','porcentaje')


class PorcentajeViewSet(viewsets.ModelViewSet):
	
	model=Porcentaje
	queryset = model.objects.all()
	serializer_class = PorcentajeSerializer
	model_log=Logs
	model_acciones=Acciones	
	nombre_modulo='avance_de_obra.porcentaje'

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
			queryset = super(PorcentajeViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			if dato:
				qset = (
					Q(tipo_linea=dato)
					)

			if sin_paginacion is None:
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

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = PorcentajeSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(intervalo_id=request.DATA['intervalo_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
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
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = PorcentajeSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(intervalo_id=request.DATA['intervalo_id'])
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
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

#Fin Api rest para Porcentaje



#Api rest para Soporte
class SoporteSerializer(serializers.HyperlinkedModelSerializer):

	intervalo=IntervaloCronogramaSerializer(read_only=True)
	intervalo_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=CIntervaloCronograma.objects.all())
	

	class Meta:
		model = Soporte
		fields=('id','intervalo','intervalo_id','ruta','nombre')


class AvanceObraSoporteViewSet(viewsets.ModelViewSet):
	
	model=Soporte
	queryset = model.objects.all()
	serializer_class = SoporteSerializer	
	model_log=Logs
	model_acciones=Acciones	
	nombre_modulo='avance_de_obra.soporte'

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
			queryset = super(AvanceObraSoporteViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			if dato:
				qset = (
					Q(nombre__icontains=dato)
					)
				queryset = self.model.objects.filter(qset)


			if sin_paginacion is None:
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

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = SoporteSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(intervalo_id=request.DATA['intervalo_id'],ruta=self.request.FILES.get('ruta') if self.request.FILES.get('ruta') is not None else None)
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
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
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = SoporteSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(intervalo_id=request.DATA['intervalo_id'],ruta=self.request.FILES.get('ruta') if self.request.FILES.get('ruta') is not None else None)
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
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

#Fin Api rest para Soporte




#eliminacion de regla de estado
@transaction.atomic
def eliminar_id_regla_estado(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		esquema_id=None

		for item in respuesta['lista']:
			valor=AReglasEstado.objects.get(pk=item['id'])
			esquema_id=valor.esquema_id
			valor.delete()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='avance_de_obra.regla_estado',id_manipulado=item['id'])
			logs_model.save()	

		updateAsyncEstado.delay(esquema_id)	
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
	except ProtectedError:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error',
			'data':''})		
	except Exception as e:
		functions.toLog(e,'avance_de_obra.regla_estado')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	

#Fin eliminacion de regla de estado

#actualizacion orden de regla de estado
@transaction.atomic
def eliminar_id_regla_estado(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		for item in respuesta['lista']:
			AReglasEstado.objects.get(pk=item['id']).delete()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='avance_de_obra.regla_estado',id_manipulado=item['id'])
			logs_model.save()
			
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
	except ProtectedError:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error',
			'data':''})		
	except Exception as e:
		functions.toLog(e,'avance_de_obra.regla_estado')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	

#actualizacion orden de regla de estado


#eliminacion de cronograma
@transaction.atomic
def eliminar_id_cronograma(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		for item in respuesta['lista']:
			actividad=DActividad.objects.filter(cronograma_id=item['id'])			
			if len(actividad) == 0:
				CIntervaloCronograma.objects.filter(cronograma_id=item['id']).delete()
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='avance_de_obra.intervalo',id_manipulado=item['id'])
				logs_model.save()
				BCronograma.objects.filter(id=item['id']).delete()
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='avance_de_obra.cronograma',id_manipulado=item['id'])
				logs_model.save()
				transaction.savepoint_commit(sid)
			else:
				transaction.savepoint_rollback(sid)
				return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error',
			'data':''})	

		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
	except ProtectedError:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error',
			'data':''})		
	except Exception as e:
		functions.toLog(e,'avance_de_obra.cronograma')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	

#Fin eliminacion de cronograma


#Inicio clonacion de los esquemas
def clonacion_esquema(request):
	cursor = connection.cursor()
	
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		cursor.callproc('[avance_de_obra].[clonacion_esquema]',[respuesta['id_etiqueta'],respuesta['nombre_esquema'],respuesta['id_macrocontrato'],])
				
		if cursor.return_value == 1:
			return JsonResponse({'message':'El registro se ha guardando correctamente','success':'ok',
						'data':''})
		else:
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
					'data':''})
			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.esquema')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()

#Fin clonacion de los esquemas

#eliminacion de capitulo/actividad de un esquema
@transaction.atomic
def eliminar_id_capitulo_actividad_esquema(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		for item in respuesta['lista']:
			valor=DActividad.objects.filter(esquema_actividades_id=item['id'])

			if len(valor)==0:
				modelpadre=AEsquemaCapitulosActividades.objects.filter(pk=item['id'])
				if len(modelpadre)>0:
					modelhijos=AEsquemaCapitulosActividades.objects.filter(padre=item['id'])
					modelpadre=AEsquemaCapitulosActividades.objects.get(pk=item['id'])
					if int(modelpadre.padre)>0:
						model=AEsquemaCapitulosActividades.objects.get(pk=modelpadre.padre)
						model.peso=float(model.peso) - float(modelpadre.peso)
						model.save()
						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='avance_de_obra.capitulos_esquema',id_manipulado=modelpadre.padre)
						logs_model.save()
						
					else:
						for item2 in list(modelhijos):
							AEsquemaCapitulosActividades.objects.filter(padre=item2.id).delete()
							logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='avance_de_obra.capitulos_esquema',id_manipulado=item2.id)
							logs_model.save()

					AEsquemaCapitulosActividades.objects.filter(padre=item['id']).delete()
					modelpadre.delete()
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='avance_de_obra.capitulos_esquema',id_manipulado=item['id'])
					logs_model.save()	
				transaction.savepoint_commit(sid)			
			else:
				transaction.savepoint_rollback(sid)
				return JsonResponse({'message':'Este capitulo o actividad se esta usado en un cronograma','success':'error',
			'data':''})	

		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
					'data':''})

			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.capitulos_esquema')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	

#Fin eliminacion de capitulo/actividad de un esquema

#Inicio eliminacion de un esquema
@transaction.atomic
def eliminar_esquema(request):

	sid = transaction.savepoint()
	try:
	
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		for item in respuesta['lista']:
			valor=BCronograma.objects.filter(esquema_id=item['id'])

			if len(valor)==0:
				AReglasEstado.objects.filter(esquema_id=item['id']).delete()
				AEsquemaCapitulosActividades.objects.filter(esquema_id=item['id']).delete()
				AEsquemaCapitulos.objects.get(pk=item['id']).delete()
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='avance_de_obra.esquema',id_manipulado=item['id'])
				logs_model.save()
				
			else:
				transaction.savepoint_rollback(sid)
				return JsonResponse({'message':'Este esquema se esta usado en un cronograma','success':'error',
					'data':''})	

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
					'data':''})
			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.esquema')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	


#Fin eliminacion de un esquema

#Inicio guardar las metas
def crear_metas_array(request):

	cursor = connection.cursor()
	
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		cursor.callproc('[avance_de_obra].[guardar_metas]',[respuesta['actividad_id'],respuesta['cantidades'],int(respuesta['id_cronograma']),])
		
		if cursor.return_value == 1:
			lista=Linea.objects.select_related('DActividad').filter(actividad__cronograma_id=respuesta['id_cronograma'],tipo_linea=1)		
			if len(lista) == 0:
				res=createAsyncLine.delay(respuesta['id_cronograma'],1)

			return JsonResponse({'message':'El registro se ha guardando correctamente','success':'ok',
				'data':''})
		else:
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
		
			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.metas')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()

#Fin guardar las metas


#Inicio listar las actividades
def listar_actividades(request,id_cronograma):


	cursor = connection.cursor()	
	try:
		cursor.callproc('[avance_de_obra].[consultar_actividades]',[int(id_cronograma),])
		columns = cursor.description 
		result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

		return JsonResponse({'message':'','success':'ok','data':result})
			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.actividades')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()
#Fin listar las actividades


#Inicio listar las metas
def lista_metas_actividad(request,id_cronograma):


	cursor = connection.cursor()	
	try:
		cursor.callproc('[avance_de_obra].[consultar_metas]',[int(id_cronograma),])
		columns = cursor.description 
		ListMetas = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		return JsonResponse({'message':'','success':'ok','data':ListMetas})
			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.metas')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})
	finally:
		cursor.close()	
#Fin listar las metas

#Inicio lista cualquier tipo de linea
def listar_linea_base(request,id_cronograma,pagina,tipo_linea,filtro):

	cursor = connection.cursor()
	registro=4
	paginacion=int(pagina)*registro

	try:
		cursor.callproc('[avance_de_obra].[consultar_linea]', [id_cronograma,paginacion,registro,tipo_linea,filtro,])
		
		columns = cursor.description 
		result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		header = [i[0] for i in columns]

		cursor.callproc('[avance_de_obra].[consultar_porcentaje]', [id_cronograma,tipo_linea,filtro,])
		
		columns = cursor.description 
		lisPorcentaje = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		listado_principal=[]

		if int(tipo_linea)==3:

			cursor.callproc('[avance_de_obra].[consultar_soporte]', [id_cronograma,tipo_linea,])
		
			columns = cursor.description 
			lisSoporte = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

			cursor.callproc('[avance_de_obra].[consultar_intervalos]', [id_cronograma,tipo_linea,])
		
			columns = cursor.description 
			lisFechaCorte = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]


			cursor.callproc('[avance_de_obra].[consultar_porcentaje]', [id_cronograma,1,filtro,])
		
			columns = cursor.description 
			lisPorcentajebase = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]


			cursor.callproc('[avance_de_obra].[consultar_porcentaje]', [id_cronograma,2,filtro,])
		
			columns = cursor.description 
			lisPorcentajeprogra = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

			#para llenar los vacios de los intervalos agregados
			
											
			xl=[len(list(lisPorcentajebase)),len(list(lisPorcentajeprogra)),len(list(lisPorcentaje))]
			valor=max(xl)-xl[0]
			if valor>0:
				for value in range(1,int(valor)+1):
					lisPorcentajebase.append({
							'porcentaje':(lisPorcentajebase[xl[0]-1]['porcentaje']),
							'intervalo':(lisPorcentajebase[xl[0]-1]['intervalo'])+value
					})
			valor=max(xl)-xl[1]
			if valor>0:
				for value in range(1,int(valor)+1):
					lisPorcentajeprogra.append({
							'porcentaje':(lisPorcentajeprogra[xl[1]-1]['porcentaje']),
							'intervalo':(lisPorcentajeprogra[xl[1]-1]['intervalo'])+value
					})
			valor=max(xl)-xl[2]
			if valor>0:
				for value in range(1,int(valor)+1):
					lisPorcentaje.append({
							'porcentaje':(lisPorcentajeprogra[xl[2]-1]['porcentaje']),
							'intervalo':(lisPorcentaje[xl[2]-1]['intervalo'])+value
					})
			# fin para llenar los vacios de los intervalos agregados
			

			listado_principal.append({'header':header,'result':result,
				'porcentaje_grafica':{'base':lisPorcentajebase,'programada':lisPorcentajeprogra,'avance':lisPorcentaje},
				'soporte':list(lisSoporte[int(paginacion):int(paginacion)+int(registro)]),
				'fecha_corte':list(lisFechaCorte[int(paginacion):int(paginacion)+int(registro)]),
				'porcentajes_base':list(lisPorcentajebase[int(paginacion):int(paginacion)+int(registro)]),
				'porcentajes_programada':list(lisPorcentajeprogra[int(paginacion):int(paginacion)+int(registro)]),
				'porcentajes':list(lisPorcentaje[int(paginacion):int(paginacion)+int(registro)])})
		
		else:
			listado_principal.append({'header':header,'result':result,'porcentajes':list(lisPorcentaje[int(paginacion):int(paginacion)+int(registro)])})
			
		
		return JsonResponse({'message':'','success':'ok','data':listado_principal[0]})	
	except Exception as e:
		functions.toLog(e,'avance_de_obra.linea')
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)	
	finally:
		cursor.close()
#fin lista cualquier tipo de linea

#Inicio cambio de sin avance

def actualizar_sin_avance(request):

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		intervalo=CIntervaloCronograma.objects.get(pk=respuesta['id'])
		intervalo.sinAvance=respuesta['estado']
		intervalo.comentario_sinAvance=respuesta['comentario']
		intervalo.save()
		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='avance_de_obra.intervalo_cronograma',id_manipulado=respuesta['id'])
		logs_model.save()

		return JsonResponse({'message':'El registro se ha guardando correctamente','success':'ok',
					'data':''})

	except Exception as e:
		functions.toLog(e,'avance_de_obra.linea')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})

#fin cambio de sin avance


#Inicio actualizar cualquier tipo de linea
def actualizar_intervalo_linea(request):

	cursor = connection.cursor()
	
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		cursor.callproc('[avance_de_obra].[guardar_intervalo_linea]',[respuesta['id_actividades'],respuesta['cantidad_actividades'],int(respuesta['tipo_linea']),int(respuesta['intervalo_id']),int(respuesta['id_cronograma']),])
		# cursor.callproc('[avance_de_obra].[actualizar_porcentajes]',[respuesta['id_actividades'],int(respuesta['tipo_linea']),int(respuesta['intervalo_id']),int(respuesta['id_cronograma']),])
		if cursor.return_value == 1:
			if respuesta['tipo_linea']==3:
				cronograma=BCronograma.objects.get(pk=respuesta['id_cronograma'])
				createAsyncEstado.delay(respuesta['id_cronograma'],cronograma.esquema_id)				
			return JsonResponse({'message':'El registro se ha guardando correctamente','success':'ok',
					'data':''})
		else:
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.intervalo')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()

#Fin actualizar cualquier tipo de linea

#Inicio registro de cantidad cualquier tipo de linea
def registro_cantidades(request):

	cursor = connection.cursor()
	
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		cursor.callproc('[avance_de_obra].[agregar_cantidades]',[respuesta['id_actividades'],respuesta['id_actividad'],float(respuesta['cantidad']),int(respuesta['tipo_linea']),int(respuesta['desde']),int(respuesta['hasta']),int(respuesta['id_cronograma']),])
		
		if cursor.return_value == 1:
			if respuesta['tipo_linea']==3:
				cronograma=BCronograma.objects.get(pk=respuesta['id_cronograma'])
				createAsyncEstado.delay(respuesta['id_cronograma'],cronograma.esquema_id)
			return JsonResponse({'message':'El registro se ha guardando correctamente','success':'ok',
				'data':''})
		else:
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})
			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.linea')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()
#Fin registro de cantidad cualquier tipo de linea


#Inicio guardar la linea base
@transaction.atomic
def guardar_linea_base(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		p=BCronograma.objects.get(pk=respuesta['id_cronograma'])
		i=CIntervaloCronograma.objects.filter(intervalo=p.intervalos,cronograma_id=respuesta['id_cronograma'])
		sw=1

		for item in i:
			por=Porcentaje.objects.filter(intervalo_id=item.id,tipo_linea=1)
			for item2 in por:
				if round(item2.porcentaje)>100 or round(item2.porcentaje)==100:
					sw=1

		if sw==1:
			p.linea_base_terminada=True
			p.save()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='avance_de_obra.linea_base',id_manipulado=respuesta['id_cronograma'])
			logs_model.save()
			res=createAsyncLine.delay(respuesta['id_cronograma'],2)
			res=createAsyncLine.delay(respuesta['id_cronograma'],3)

			transaction.savepoint_commit(sid)

			return JsonResponse({'message':'El registro se ha guardando correctamente','success':'ok',
				'data':''})

		else:
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'No se puede guardar la linea base, el porcentaje no llega 100%','success':'error',
			'data':''})		
			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.linea')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
#Fin guardar la linea base

#Inicio agregar intervalo a la linea
def agregar_intervalos(request):

	cursor = connection.cursor()
	
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		cursor.callproc('[avance_de_obra].[agregar_intervalos]',[respuesta['cantidades'],int(respuesta['tipo_linea']),int(respuesta['id_cronograma']),])
		
		if cursor.return_value == 1:
			return JsonResponse({'message':'El registro se ha guardando correctamente','success':'ok',
					'data':''})		
		else:
			return JsonResponse({'message':'Se presentaron errores al procesar en la linea de avance','success':'error',
				'data':''})

			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.intervalo')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()

#Fin agregar intervalo a la linea

#Inicio quitar intervalo a la linea
def quitar_intervalos(request):

	cursor = connection.cursor()
	
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		cursor.callproc('[avance_de_obra].[quitar_intervalos]',[respuesta['cantidades'],int(respuesta['tipo_linea']),int(respuesta['id_cronograma']),])
		
		if cursor.return_value != -1:
			if cursor.return_value != -2:
				if cursor.return_value == 1:
					return JsonResponse({'message':'El registro se ha eliminando correctamente','success':'ok',
					'data':''})
				else:
					return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
					'data':''})	

			else:
				return JsonResponse({'message':'Unos de los intervalos tiene datos registrado','success':'error',
				'data':''})
		else:
			return JsonResponse({'message':'No se debe incluir los intervalos que se no se haya agregado','success':'error',
			'data':''})
		
			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.intervalo')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()
#Fin quitar intervalo a la linea

#Inicio informe de cantidades de ejecutadas por capitulos
def export_excel_cantidades(request):
	
	cursor = connection.cursor()
	
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="informe_cantidades_ejecutadas.xls"'
		
		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Cantidades Ejecutadas')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':1,'align': 'center','valign': 'vcenter','fg_color': '#031F72','font_color':'#FFFFFF'})
		format2=workbook.add_format({'border':1,'font_size':10,'align': 'center','valign': 'vcenter'})

		worksheet.set_column('A:C', 50)
		worksheet.set_row(0, 30)
		worksheet.set_row(1, 30)

		id_esquema= request.GET['id_esquema']
		proyecto_id=None
		cronogramas=None

		proyecto_id= request.GET.get('proyecto_id',None)		

		if proyecto_id is not None:
			cronogramas=BCronograma.objects.filter(esquema_id=id_esquema,proyecto_id=proyecto_id)
		else:
			cronogramas=BCronograma.objects.filter(esquema_id=id_esquema)

		valores=AEsquemaCapitulosActividades.objects.filter(esquema_id=id_esquema,nivel=1)

		worksheet.merge_range('A1:A2', 'NOMBRE DEL PROYECTO', format1)
		worksheet.merge_range('B1:B2', 'No DE CONTRATO', format1)
		worksheet.merge_range('C1:C2', 'NOMBRE DE CRONOGRAMA', format1)

		row=0
		col=3
		for item in valores:
			worksheet.merge_range(row,col,row,col+3, item.nombre,format1)
			worksheet.write(row+1,col, 'Replanteo',format1)
			worksheet.write(row+1,col+1, 'A ejecutar',format1)
			worksheet.write(row+1,col+2, 'Ejecutado',format1)
			worksheet.write(row+1,col+3, '%'+'Ejecutado',format1)

			col +=4

		worksheet.set_column(3,col,15)
		row=2
		col=0
		for item in cronogramas:
			worksheet.write(row, col,item.proyecto.nombre,format2)
			numeros_contrato=''
			for contrato in item.proyecto.contrato.all():
				if numeros_contrato=='':
					numeros_contrato=contrato.numero
				else:
					numeros_contrato=numeros_contrato+','+contrato.numero

			worksheet.write(row, col+1,numeros_contrato,format2)
			worksheet.write(row, col+2,item.nombre,format2)
	
			actividades=DActividad.objects.select_related('AEsquemaCapitulosActividades').filter(cronograma_id=item.id,esquema_actividades__nivel=1)
			col=3				
			for item2 in actividades:
				valor_ejecutado=0
				valor_base=0
				valor_programada=0
				valor_avance=0
				for x in range(1,4):
					valores=Linea.objects.filter(actividad_id=item2.id,tipo_linea=x).aggregate(Sum('cantidad'))
					valores['cantidad__sum']=0 if valores['cantidad__sum']==None else valores['cantidad__sum']
					if x==1:
						valor_base=valores['cantidad__sum']

					if x==2:
						valor_programada=valores['cantidad__sum']

					if x==1:
						valor_avance=valores['cantidad__sum']

					worksheet.write(row, col,valores['cantidad__sum'],format2)

					col+=1

				if valor_programada>0:
					valor_ejecutado=(valor_avance/valor_programada)*100
					worksheet.write(row, col,str(round(valor_ejecutado,2))+'%',format2)

				if valor_base>0:
					valor_ejecutado=(valor_avance/valor_base)*100
					worksheet.write(row, col,str(round(valor_ejecutado,2))+'%',format2)

				if valor_base==0 and valor_programada==0:
					worksheet.write(row, col,str(round(valor_ejecutado,2))+'%',format2)

				col+=1



			row +=1
			col=0

		workbook.close()

		return response

	except Exception as e:
		functions.toLog(e,'avance_de_obra.linea')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()

#Fin informe de cantidades de ejecutadas por capitulos


#Inicio informe de resumen de avance
def export_excel_resumen(request):
	
	cursor = connection.cursor()
	
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="informe_resumen_avance.xls"'
		
		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Resumen de Avance')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':1,'align': 'center','valign': 'vcenter','fg_color': '#031F72','font_color':'#FFFFFF'})
		format2=workbook.add_format({'border':1,'font_size':10,'align': 'center','valign': 'vcenter'})

		worksheet.set_column('A:J', 50)
		worksheet.set_row(0, 30)

		id_esquema= request.GET['id_esquema']
		hasta= request.GET['hasta']
		desde= request.GET['desde']
		proyecto_id=None
		cronogramas=None

		tipo=tipoC()

		if 'proyecto_id' in request.GET:
			proyecto_id= request.GET['proyecto_id']		

		
		worksheet.write('A1', 'DEPARTAMENTO', format1)
		worksheet.write('B1', 'MUNICIPIO', format1)
		worksheet.write('C1', 'NOMBRE DEL PROYECTO', format1)
		worksheet.write('D1', 'No DE CONTRATO', format1)
		worksheet.write('E1', 'CONTRATISTA', format1)
		worksheet.write('F1', 'NOMBRE DE CRONOGRAMA', format1)
		worksheet.write('G1', '% PROYECTADO', format1)
		worksheet.write('H1', '% '+'EJECUTADO', format1)
		worksheet.write('I1', '% DIFERENCIA', format1)
		worksheet.write('J1', 'ACTIVIDADES EJECUTADAS', format1)

		if proyecto_id is not None:
			cronogramas=BCronograma.objects.filter(esquema_id=id_esquema,proyecto_id=proyecto_id)
		else:
			cronogramas=BCronograma.objects.filter(esquema_id=id_esquema)
		row=1
		col=0
		for listado in cronogramas:
			worksheet.write(row,col, listado.proyecto.municipio.departamento.nombre,format2)
			worksheet.write(row,col+1, listado.proyecto.municipio.nombre,format2)
			worksheet.write(row,col+2, listado.proyecto.nombre,format2)

			numeros_contrato=''
			for contrato in listado.proyecto.contrato.all():
				if contrato.tipo_contrato.id==tipo.contratoProyecto:
					if numeros_contrato=='':
						numeros_contrato=contrato.numero
					else:
						numeros_contrato=numeros_contrato+','+contrato.numero

			worksheet.write(row,col+3, numeros_contrato,format2)

			contratista=''
			for item in listado.proyecto.contrato.all():
				if contrato.tipo_contrato.id==tipo.contratoProyecto:
					if contratista=='':
						contratista=contrato.contratista.nombre
					else:
						contratista=contratista+','+contrato.contratista.nombre

			worksheet.write(row,col+4, contratista,format2)
			worksheet.write(row,col+5, listado.nombre,format2)

			intervalos=CIntervaloCronograma.objects.filter(cronograma_id=listado.id,tipo_linea=2)
			valor_intervalo=0
			sw=0
			valor_programada=0
			for listado2 in intervalos:
				valor=(listado.periodicidad.numero_dias*listado2.intervalo)-listado.periodicidad.numero_dias
				fecha=listado.fecha_inicio_cronograma
				fecha_total=fecha+timedelta(days=valor)
				if str(fecha_total)<=str(hasta):
					valor_intervalo=listado2.id
					sw=1

			if sw==1:
				porcentaje=Porcentaje.objects.filter(intervalo_id=valor_intervalo,tipo_linea=2).values('porcentaje')
				if len(porcentaje)==0:
					worksheet.write(row,col+6,str(round(0,2))+"%",format2)
				else:
					for por in porcentaje:
						valor_programada=round(por['porcentaje'],2)
						worksheet.write(row,col+6,str(round(por['porcentaje'],2))+"%",format2)				
			else:
				valor_programada=0
				worksheet.write(row,col+6, 'No aplica',format2)

			
			intervalos=CIntervaloCronograma.objects.filter(cronograma_id=listado.id,tipo_linea=3)
			valor_intervalo=0
			sw=0
			valor_avance=0
			for listado2 in intervalos:
				valor=(listado.periodicidad.numero_dias*listado2.intervalo)-listado.periodicidad.numero_dias
				fecha=listado.fecha_inicio_cronograma
				fecha_total=fecha+timedelta(days=valor)
				if str(fecha_total)<=str(hasta):
					valor_intervalo=listado2.id
					sw=1

			if sw==1:
				porcentaje=Porcentaje.objects.filter(intervalo_id=valor_intervalo,tipo_linea=3).values('porcentaje')
				if len(porcentaje)==0:
					worksheet.write(row,col+7,str(round(0,2))+"%",format2)
				else:
					for por in porcentaje:
						valor_avance=round(por['porcentaje'],2)
						worksheet.write(row,col+7,str(round(por['porcentaje'],2))+"%",format2)				
			else:
				valor_avance=0
				worksheet.write(row,col+7, 'No aplica',format2)			


			worksheet.write(row,col+8,str(round((valor_programada-valor_avance),2))+"%",format2)

			sw=0	
			listado_actividad=''				
			for listado2 in intervalos:
				valor=(listado.periodicidad.numero_dias*listado2.intervalo)-listado.periodicidad.numero_dias
				fecha=listado.fecha_inicio_cronograma
				fecha_total=fecha+timedelta(days=valor)
				if str(fecha_total)>=str(desde) and str(fecha_total)<=str(hasta):
					actividades=DActividad.objects.select_related('AEsquemaCapitulosActividades').filter(cronograma_id=listado.id,esquema_actividades__nivel=1)
					for lista in actividades:
						hijos=DActividad.objects.select_related('AEsquemaCapitulosActividades').filter(cronograma_id=listado.id,esquema_actividades__padre=lista.esquema_actividades_id)
						for lista2 in hijos:
							lis=DActividad.objects.select_related('AEsquemaCapitulosActividades').filter(cronograma_id=listado.id,esquema_actividades__padre=lista2.esquema_actividades_id).aggregate(Sum('id'))
							lis['id__sum']=0 if lis['id__sum']==None else lis['id__sum']
							if lis['id__sum']==0:
								cantidad=Linea.objects.filter(intervalo_id=listado2.id,actividad_id=lista2.id,tipo_linea__in=(2,3)).aggregate(Sum('cantidad'))
								if cantidad['cantidad__sum'] is not None and cantidad['cantidad__sum']>0:
									if listado_actividad=='':
										listado_actividad=lista2.esquema_actividades.nombre
									else:
										valor=listado_actividad.find(lista2.esquema_actividades.nombre)
										if valor<0:
											listado_actividad=listado_actividad+','+lista2.esquema_actividades.nombre
							else:
								lis2=DActividad.objects.select_related('AEsquemaCapitulosActividades').filter(cronograma_id=listado.id,esquema_actividades__padre=lista2.esquema_actividades_id)
								for item3 in lis2:
									cantidad=Linea.objects.filter(intervalo_id=listado2.id,actividad_id=item3.id,tipo_linea__in=(2,3)).aggregate(Sum('cantidad'))
									if cantidad['cantidad__sum'] is not None and cantidad['cantidad__sum']>0:
										if listado_actividad=='':
											listado_actividad=item3.esquema_actividades.nombre
										else:
											valor=listado_actividad.find(item3.esquema_actividades.nombre)
											if valor<0:
												listado_actividad=listado_actividad+','+item3.esquema_actividades.nombre

			worksheet.write(row,col+9,listado_actividad,format2)

			row +=1


		workbook.close()

		return response

	except Exception as e:
		functions.toLog(e,'avance_de_obra.resumen')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()

#Fin informe de cantidades de ejecutadas por capitulos


#Inicio listar las actividades de un esquema
def listar_esquema_actividades(request,id_esquema):


	cursor = connection.cursor()	
	try:
		cursor.callproc('[avance_de_obra].[consultar_esquema_actividades]',[int(id_esquema),])
		columns = cursor.description 
		result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

		return JsonResponse({'message':'','success':'ok','data':result})
			
	except Exception as e:
		functions.toLog(e,'avance_de_obra.esquema')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	
	finally:
		cursor.close()
#Fin listar las actividades de un esquema
				
@login_required
def avance_de_obra(request):
		tipo=tipoC()
		qset = (Q(contrato__tipo_contrato=tipo.m_contrato)) &(Q(empresa=request.user.usuario.empresa.id) & Q(participa=1))
		ListMacro = EmpresaContrato.objects.filter(qset)


		return render(request, 'avance_de_obra/index.html',{'model':'avance_de_obra','app':'avance_de_obra','macrocontrato':ListMacro})

@login_required
def administrar_capitulos(request):
		tipo=tipoC()
		qset = (Q(contrato__tipo_contrato=tipo.m_contrato)) &(Q(empresa=request.user.usuario.empresa.id) & Q(participa=1))
		ListMacro = EmpresaContrato.objects.filter(qset)

		return render(request, 'avance_de_obra/esquema_capitulos.html',{'model':'aesquemacapitulos','app':'avance_de_obra','macrocontrato':ListMacro})

@login_required
def administrar_actividades(request,id_esquema):
		tipo=tipoC()
		qset = (Q(contrato__tipo_contrato=tipo.m_contrato)) &(Q(empresa=request.user.usuario.empresa.id) & Q(participa=1))
		ListMacro = EmpresaContrato.objects.filter(qset)
		esquema=AEsquemaCapitulos.objects.get(pk=id_esquema)

		return render(request, 'avance_de_obra/administrar_capitulos.html',{'model':'aesquemacapitulosactividades','app':'avance_de_obra','macrocontrato':ListMacro,'id_esquema':id_esquema,'nombre_esquema':esquema.nombre})


@login_required
def cronograma(request,id_proyecto):

		ListProyecto=Proyecto.objects.get(pk=id_proyecto)
		tipo=tipoC()
		ListEsquema=AEsquemaCapitulos.objects.filter(macrocontrato_id=ListProyecto.mcontrato.id)
		qset = (Q(contrato__tipo_contrato=tipo.m_contrato)) &(Q(empresa=request.user.usuario.empresa.id) & Q(participa=1))
		ListMacro = EmpresaContrato.objects.filter(qset)

		empresaContrato = EmpresaContrato.objects.filter(contrato__id=ListProyecto.mcontrato.id, empresa__id=request.user.usuario.empresa.id).first()

		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True

		return render(request, 'avance_de_obra/cronograma.html',{'model':'bcronograma','app':'avance_de_obra','id_proyecto':id_proyecto,'nombre_proyecto':ListProyecto.nombre,'macrocontrato':ListMacro,'esquema':ListEsquema, 'soloLectura': soloLectura})

@login_required
def actividades(request,id_cronograma,id_proyecto):

		ListCronograma=BCronograma.objects.get(pk=id_cronograma)

		return render(request, 'avance_de_obra/actividad.html',{'model':'dactividad','app':'avance_de_obra','id_cronograma':id_cronograma,'nombre_cronograma':ListCronograma.nombre,'id_proyecto':id_proyecto})

@login_required
def metas(request,id_cronograma,id_proyecto):

		ListCronograma=BCronograma.objects.get(pk=id_cronograma)

		return render(request, 'avance_de_obra/metas.html',{'model':'meta','app':'avance_de_obra','id_cronograma':id_cronograma,'nombre_cronograma':ListCronograma.nombre,'id_proyecto':id_proyecto})

@login_required
def linea_base(request,id_cronograma,id_proyecto):

		ListCronograma=BCronograma.objects.get(pk=id_cronograma)

		return render(request, 'avance_de_obra/linea_base.html',{'model':'linea','app':'avance_de_obra','id_cronograma':id_cronograma,'nombre_cronograma':ListCronograma.nombre,'nombre_proyecto':ListCronograma.proyecto.nombre,'id_proyecto':id_proyecto,'linea_base':ListCronograma.linea_base_terminada,'periodo':ListCronograma.periodicidad.nombre})

@login_required
def linea_programada(request,id_cronograma,id_proyecto):

		ListCronograma=BCronograma.objects.get(pk=id_cronograma)
		
		return render(request, 'avance_de_obra/linea_programada.html',{'model':'linea','app':'avance_de_obra','id_cronograma':id_cronograma,'nombre_cronograma':ListCronograma.nombre,'nombre_proyecto':ListCronograma.proyecto.nombre,'id_proyecto':id_proyecto,'periodo':ListCronograma.periodicidad.nombre,'numeros_dias':ListCronograma.periodicidad.numero_dias,'fecha_cronograma':ListCronograma.fecha_inicio_cronograma})

@login_required
def linea_avance(request,id_cronograma,id_proyecto):

		ListCronograma=BCronograma.objects.get(pk=id_cronograma)

		return render(request, 'avance_de_obra/linea_avance.html',{'model':'linea','app':'avance_de_obra','id_cronograma':id_cronograma,'nombre_cronograma':ListCronograma.nombre,'nombre_proyecto':ListCronograma.proyecto.nombre,'id_proyecto':id_proyecto,'periodo':ListCronograma.periodicidad.nombre,'numeros_dias':ListCronograma.periodicidad.numero_dias,'fecha_cronograma':ListCronograma.fecha_inicio_cronograma})

@login_required
def regla_estado(request,id_esquema):

		return render(request, 'avance_de_obra/regla_estado.html',{'model':'regla_estado','app':'avance_de_obra','id_esquema':id_esquema})


