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
import xlsxwriter
import json
from django.http import HttpResponse,JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from tipo.models import Tipo
from tipo.views import TipoSerializer
from proyecto.models import Proyecto,Proyecto_empresas
from proyecto.views import ProyectoSerializer
from .models import ALote,BSoporte,CEstructura,DPropietario,EPropietarioLote
from proceso.models import FProcesoRelacion,GProcesoRelacionDato,BItem
from logs.models import Logs,Acciones
from datetime import *
from django.db import transaction,connection
from django.db.models.deletion import ProtectedError
from rest_framework.decorators import api_view, throttle_classes
from django.contrib.auth.decorators import login_required


# Serializer de proyecto
class ProyectoLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre')


#Api rest para los lotes
class LoteSerializer(serializers.HyperlinkedModelSerializer):
	
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto.objects.all())
	proyecto=ProyectoLiteSerializer(read_only=True)

	class Meta:
		model = ALote
		fields=('id','proyecto','proyecto_id','nombre','direccion','cantidad_estructura','cantidad_propietarios_asociados','proceso_relacion_id')


class LoteViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de los lotes
	"""
	model=ALote
	queryset = model.objects.all()
	serializer_class = LoteSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(LoteViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			proyecto= self.request.query_params.get('proyecto_id',None)
			sin_paginacion = self.request.query_params.get('sin_paginacion', None)
			id_empresa = request.user.usuario.empresa.id
			qset=''

			if (dato or proyecto or id_empresa):

				qset = Q(proyecto__id=proyecto)

				if dato:
					qset = qset &(
						Q(nombre__icontains=dato)
					)
			
			if qset != '':
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
			else:
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
				serializer = LoteSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():

					serializer.save(proyecto_id=request.DATA['proyecto_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='pp_construccion.lote',id_manipulado=serializer.data['id'])
					logs_model.save()

					proceso_relacion=FProcesoRelacion(idApuntador=request.DATA['proyecto_id'],idTablaReferencia=serializer.data['id'],proceso_id=7)
					proceso_relacion.save()

					proceso_item = BItem.objects.filter(proceso_id=7)

					for p in proceso_item:

						proceso_relacion_dato=GProcesoRelacionDato(procesoRelacion_id=proceso_relacion.id,item_id=p.id,valor='vacio',estado=0)
						proceso_relacion_dato.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
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


	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()

			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = LoteSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(proyecto_id=request.DATA['proyecto_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='p_p_construccion.lote',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:

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


#Fin api rest para los lotes



#Api rest para los propietarios
class PropietarioSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = DPropietario
		fields=('id','cedula','nombres','apellidos','telefono','correo')


class PropietarioViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de los propietarios
	"""
	model=DPropietario
	queryset = model.objects.all()
	serializer_class = PropietarioSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(PropietarioViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			proyecto= self.request.query_params.get('proyecto',None)
			sin_paginacion = self.request.query_params.get('sin_paginacion', None)
			id_empresa = request.user.usuario.empresa.id
			qset=''

			if dato:
				qset = (Q(nombres__icontains=dato)|
						Q(apellidos__icontains=dato)|
						Q(cedula__icontains=dato)
						)
			
			if qset != '':
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
			else:
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

				propietario = DPropietario.objects.filter(cedula=request.DATA['cedula'])
				#print propietario
				if propietario:
					return Response({'message':'Ya existe un propietario registrado con la cedula ingresada','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

				propietario = DPropietario.objects.filter(correo=request.DATA['correo'])
				if propietario:
					return Response({'message':'Ya existe un propietario registrado con el correo ingresado','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

				serializer = PropietarioSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save()
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				#print(e)
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
				serializer = PropietarioSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='p_p_construccion.lote',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:

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


#Fin api rest para los propietarios



#Api rest para los soportes de reunion
class SoporteReunionSerializer(serializers.HyperlinkedModelSerializer):
	
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto.objects.all())
	proyecto=ProyectoLiteSerializer(read_only=True)

	tipo = TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='p_p_construccion'))

	class Meta:
		model = BSoporte
		fields=('id','proyecto','proyecto_id','nombre','soporte','tipo','tipo_id')


class SoporteReunionViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de los soportes de reunion
	"""
	model=BSoporte
	queryset = model.objects.all()
	serializer_class = SoporteReunionSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(SoporteReunionViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion = self.request.query_params.get('sin_paginacion', None)
			proyecto = self.request.query_params.get('proyecto_id', None)
			tipo = self.request.query_params.get('tipo', None)		
			id_empresa = request.user.usuario.empresa.id
			qset=''

			if (dato or proyecto or tipo):

				qset = Q(proyecto__id = proyecto)

				if tipo:
					qset = qset &(Q(tipo__id=tipo))

				if dato:
					qset = qset &(Q(nombre__icontains=dato))		


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
			else:
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

				lista=self.request.FILES.getlist('archivo[]')
				for item in lista:
					serializer = SoporteReunionSerializer(data=request.DATA,context={'request': request})				

					if serializer.is_valid():

						serializer.save(proyecto_id=request.DATA['proyecto_id'],tipo_id=request.DATA['tipo_id'],soporte=item)

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='administrador_foto.FotosProyecto',id_manipulado=serializer.data['id'])
						logs_model.save()

						transaction.savepoint_commit(sid)
					else:
						print(serializer.errors)
						return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)

				return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)

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
				serializer = SoporteReunionSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					
					if self.request.FILES.get('soporte') is not None:
						#print self.request.FILES.get('soporte')
						serializer.save(soporte=self.request.FILES.get('soporte'),proyecto_id=request.DATA['proyecto_id'],tipo_id=request.DATA['tipo_id'])

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='p_p_construccion.soporte',id_manipulado=serializer.data['id'])
						logs_model.save()

						transaction.savepoint_commit(sid)
					else:
						soporte=self.model.objects.get(pk=instance.id)
						serializer.save(soporte=soporte.soporte,proyecto_id=request.DATA['proyecto_id'],tipo_id=request.DATA['tipo_id'])

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='p_p_construccion.soporte',id_manipulado=serializer.data['id'])
						logs_model.save()

						transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:

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


#Fin api rest para los soportes


#Api rest para los estructuras
class EstructurasSerializer(serializers.HyperlinkedModelSerializer):

	lote_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=ALote.objects.all())
	lote=LoteSerializer(read_only=True)

	class Meta:
		model = CEstructura
		fields=('id','lote','lote_id','codigo')


class EstructurasViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de movientos de las cuentas del financiero.
	"""
	model=CEstructura
	queryset = model.objects.all()
	serializer_class = EstructurasSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:

			queryset = super(EstructurasViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			lote= self.request.query_params.get('lote_id',None)
			sin_paginacion=self.request.query_params.get('sin_paginacion',None)
			id_empresa = request.user.usuario.empresa.id
			qset=''

			if (dato or lote or id_empresa):

				qset = Q(lote__id=lote)
				#qset = Q(lote__proyecto__mcontrato__empresacontrato__empresa=id_empresa)

				if dato:
					qset = qset &(Q(codigo__icontains=dato))	

			#print qset
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
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()

			try:

				serializer = EstructurasSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(lote_id=request.DATA['lote_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='p_p_construccion.estructura',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
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

				serializer = EstructurasSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(lote_id=request.DATA['lote_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='p_p_construccion.estructura',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:

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


#Fin api rest para las estructuras



#Api rest para los propietarios lote
class PropietarioLoteSerializer(serializers.HyperlinkedModelSerializer):

	lote_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=ALote.objects.all())
	lote=LoteSerializer(read_only=True)

	propietario_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=DPropietario.objects.all())
	propietario=PropietarioSerializer(read_only=True)

	class Meta:
		model = EPropietarioLote
		fields=('id','lote','lote_id','propietario','propietario_id')


class PropietarioLoteViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de los propietarios lote
	"""
	model=EPropietarioLote
	queryset = model.objects.all()
	serializer_class = PropietarioLoteSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:

			queryset = super(PropietarioLoteViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			lote= self.request.query_params.get('lote_id',None)
			sin_paginacion=self.request.query_params.get('sin_paginacion',None)
			id_empresa = request.user.usuario.empresa.id
			qset=''

			if (dato or lote or id_empresa):

				#qset = Q(lote__proyecto__mcontrato__empresacontrato__empresa=id_empresa)

				qset = Q(lote__id=lote)

				if dato:
					qset =  qset &(Q(propietario__nombres__icontains=dato)|
							Q(propietario__apellidos__icontains=dato)|
							Q(propietario__cedula__icontains=dato)
							)

			#print qset
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
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()

			try:

				serializer = PropietarioLoteSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(lote_id=request.DATA['lote_id'],propietario_id=request.DATA['propietario_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='p_p_construccion.propietario_lote',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				#print(e)
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

				serializer = PropietarioLoteSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(lote_id=request.DATA['lote_id'],propietario_id=request.DATA['propietario_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='p_p_construccion.propietario_lote',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:

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


#Fin api rest para los propietarios lote


#eliminar lotes 
@transaction.atomic
def eliminar_lotes(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			ALote.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='p_p_construccion.lote',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})	
		
	except Exception as e:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})		





#eliminar los documentos 
@transaction.atomic
def eliminar_documentos(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			BSoporte.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='p_p_construccion.soporte',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})	
		
	except Exception as e:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})		


					
#eliminar las estructuras
@transaction.atomic
def eliminar_varios_estruturas(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		for item in respuesta['lista']:

			model_d = CEstructura.objects.get(id=item['id'])

			model_d.delete()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='p_p_construccion.estructura',id_manipulado=item['id'])
			logs_model.save()

			transaction.savepoint_commit(sid)
	
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data':''})

	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})	

	except Exception as e:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})




#guardar la asociacion de los propietarios al lote
@api_view(['POST'])
@transaction.atomic
def AsociarPropietariosLote(request):

	sid = transaction.savepoint()
	if request.method == 'POST':
		try:
			
			lista=request.DATA['lista']
			lote_id= request.DATA['lote_id']
  
			# print lote_id

			for item in lista:

				propietarioLote=EPropietarioLote(propietario_id=item['id'],lote_id=lote_id)
				propietarioLote.save()

				transaction.savepoint_commit(sid)


			return JsonResponse({'message':'El registro se ha guardado correctamente','success':'ok',
					'data':''})
			
		except Exception as e:
			print(e)
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
				'data':''})




#recorre el archivo en excel
def consulta_listado_propietarios(request):

	try:

		propietario = DPropietario.objects.all()

		lista_propietarios=[]

		for item in list(propietario):

			propietario_lote = EPropietarioLote.objects.filter(propietario__id=item.id).first()

		 	# print propietario_lote

			if propietario_lote is None:

				lista_propietarios.append(

					{		
						'id':item.id,
						'cedula':item.cedula,
						'nombres':item.nombres,
						'apellidos':item.apellidos,
						'telefono':item.telefono,
						'correo':item.correo,
					}

				)

		return JsonResponse({'message':'No se encontraron registros con los parametros ingresados','success':'ok','data':lista_propietarios})

	except Exception as e:
		print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)		

    #return response



#desasociar los propietario del lote
@transaction.atomic
def desasociar_propietario(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			EPropietarioLote.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='p_p_construccion.propietario_lote',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})	
		
	except Exception as e:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	

@login_required
def ListadoProyectos(request):

	return render(request, 'p_p_construccion/proyecto_construccion.html',{'app':'p_p_construccion'})		


@login_required
def PropietarioVista(request,lote_id=None,proyecto_id=None):

	return render(request, 'p_p_construccion/propietario.html',{'app':'p_p_construccion','model':'EPropietarioLote','lote_id':lote_id,'proyecto_id':proyecto_id})		


@login_required
def Lote(request,id_proyecto=None):
	qsProyecto=Proyecto.objects.filter(id=id_proyecto).first()

	return render(request, 'p_p_construccion/lote.html',{'proyecto':qsProyecto,'app':'p_p_construccion','model':'ALote','id_proyecto':id_proyecto})		
