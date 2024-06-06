from django.shortcuts import render
from coasmedas.functions import functions
from rest_framework import viewsets, response, status
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import IntegrityError,transaction
from logs.models import Logs, Acciones
# Create your views here.
from contrato.models import VigenciaContrato
from .models import Categoria, Tipo_Activo, Activo, Atributo, Activo_atributo, Activo_atributo_soporte, Activo_persona, Activo_gps, Motivo, Mantenimiento, Soporte_mantenimiento
from contrato.models import Contrato
from parametrizacion.models import Funcionario
from usuario.models import Persona
from datetime import *
from django.http import HttpResponse,JsonResponse

import xlsxwriter
import json

from rest_framework.decorators import api_view

from .serializers import CategoriaSerializer,Tipo_ActivoSerializer, Tipo_ActivoLiteSerializer, \
ActivoSerializer,ActivoLiteSerializer,ActivoLite2Serializer,ActivoLite3Serializer,ActivoLite4Serializer,\
AtributoSerializer,AtributoLiteSerializer,\
Activo_atributoSerializer,Activo_atributoLiteSerializer, Activo_atributoLite2Serializer,\
Activo_atributo_soporteSerializer,Activo_atributo_soporteLiteSerializer, Activo_atributo_soporteLite2Serializer,\
Activo_personaSerializer, Activo_personaLiteSerializer, \
MotivoSerializer, MotivoLiteSerializer, \
MantenimientoSerializer, MantenimientoLiteSerializer, \
Soporte_mantenimientoSerializer, Soporte_mantenimientoLiteSerializer, \
Puntos_gpsSerializer, Puntos_gpsLiteSerializer, Puntos_gpsLite2Serializer

#from utilidades.estructura import Estructura

class CategoriaViewSet(viewsets.ModelViewSet):
	model = Categoria
	queryset = model.objects.all()
	serializer_class = CategoriaSerializer
	nombre_modulo = 'Activos'

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
			queryset = super(CategoriaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			###import pdb; pdb.set_trace()			
			try:
				serializer = CategoriaSerializer(data=request.data,context={'request': request})
				###import pdb; pdb.set_trace()
				if serializer.is_valid():
					serializer.save()						

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.categoria',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer  = ActivoLite2Serializer(instance,data=request.data,context={'request': request})
				if serializer.is_valid():
					
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='activos.activo',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos.categoria',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				##respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)


class Tipo_ActivoViewSet(viewsets.ModelViewSet):
	model = Tipo_Activo
	queryset = model.objects.all()
	serializer_class = Tipo_ActivoSerializer
	nombre_modulo = 'Activos'

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
			queryset = super(Tipo_ActivoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			categoria= self.request.query_params.get('categoria',None)


			qset=(~Q(id=0))

			if categoria:
					qset = qset &(Q(categoria__id = int(categoria)))
			queryset = self.model.objects.filter(qset)	

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			###import pdb; pdb.set_trace()			
			try:
				serializer = Tipo_ActivoLiteSerializer(data=request.data,context={'request': request})
				###import pdb; pdb.set_trace()
				if serializer.is_valid():
					serializer.save()						

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.tipo_activo',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer  = ActivoLite2Serializer(instance,data=request.data,context={'request': request})
				if serializer.is_valid():
					
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='activos.tipo_activo',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos.tipo_activo',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				##respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

class ActivoViewSet(viewsets.ModelViewSet):
	model = Activo
	queryset = model.objects.all()
	serializer_class = ActivoSerializer
	nombre_modulo = 'Activos'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		###import pdb; pdb.set_trace()
		try:
			queryset = super(ActivoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			categoria = self.request.query_params.get('categoria', None)
			tipo = self.request.query_params.get('tipo', None)
			estado = self.request.query_params.get('estado', None)
			funcionario = self.request.query_params.get('funcionario', None)

			qset=(~Q(id=0))
			if dato:
				qset = qset &(Q(identificacion__icontains=dato)|Q(serial_placa__icontains=dato)|Q(contrato__numero__icontains=dato)|Q(contrato__nombre__icontains=dato))
			if categoria:
				qset = qset &(Q(tipo__categoria__id=int(categoria)))
			if tipo:
				qset = qset &(Q(tipo__id=int(tipo)))
			if estado:
				if int(estado)<2:
					qset = qset &(Q(debaja=estado))
			if funcionario:
				qset = qset &(Q(responsable__id=int(funcionario)))


			queryset = self.model.objects.filter(qset)
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			##import pdb; pdb.set_trace()			
			try:
						
				nombres=request.POST.getlist('nombre[]')

				for elemento in nombres:
					if nombres.count(elemento) > 1:
						return Response({'message':'El nombre: '+elemento+ ', se usa mas de una vez','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

				serializer = ActivoLite2Serializer(data=request.data,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(tipo_id=int(request.data['tipo_id']),responsable_id=int(request.data['responsable_id']),contrato_id=int(request.data['contrato_id']))						

					##import pdb; pdb.set_trace()
					valores=request.POST.getlist('valor[]')
					atributos=request.POST.getlist('atributo[]')
					estados= request.POST.getlist('estado_atributo[]')


					id_aux = request.POST.getlist('id_atributo[]')
					soportes= request.FILES.getlist('soporte_atributo[]')
					

					if valores and atributos and estados:
						j = 0
						serializer_activo_atributo=''
						for x in valores:

							serializer_activo_atributo = Activo_atributoLiteSerializer(data={
								'atributo_id':atributos[j],
								'valor':valores[j],
								'activo_id':serializer.data['id']
								},context={'request': request})

							if serializer_activo_atributo.is_valid():
								serializer_activo_atributo.save(atributo_id=atributos[j],activo_id=serializer.data['id'])								
								

								if estados[j]=='true':
									q = 0
									for sop in soportes:
										if id_aux[q]==atributos[j]:
											sp = Activo_atributo_soporte(activo_atributo_id=serializer_activo_atributo.data['id'],documento=soportes[q])
											sp.save()
										q = q + 1;

								j = j + 1;

								serializer_activo_atributo = ''




					latitudes=request.POST.getlist('latitud[]')
					longitudes=request.POST.getlist('longitud[]')
					
					

					if latitudes and longitudes and nombres:
							i = 0
							for sp in latitudes:
												
								s= Activo_gps(nombre=nombres[i],latitud=float(latitudes[i]), longitud=float(longitudes[i]), activo_id=serializer.data['id'])
								s.save()
								i = i + 1;

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.activo',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		#
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				
				##import pdb; pdb.set_trace()
								
				debaja = request.data['debaja']
				aux_tipo = instance.tipo.id	
				if debaja=='true':
					request.data._mutable = True
					request.data['fecha_baja'] = str(datetime.now().strftime('%Y-%m-%d'))
					request.data._mutable = False

					serializer  = ActivoLite3Serializer(instance,data=request.data,context={'request': request})
					if serializer.is_valid():

						serializer.save()

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='activos.activo',id_manipulado=instance.id)
						logs_model.save()

						transaction.savepoint_commit(sid)
						return Response({'message':'El registro ha dado de baja exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				
				else:
						
					nombres=request.POST.getlist('nombre[]')

					for elemento in nombres:
						if nombres.count(elemento) > 1:
							return Response({'message':'El nombre: '+elemento+ ', se usa mas de una vez','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)


					if request.data['periodicidad_mantenimiento']=='null':
						request.data._mutable = True
						request.data['periodicidad_mantenimiento']=None
						request.data._mutable = False

					if	request.data['fecha_baja']=='1900-01-01':
						request.data._mutable = True
						request.data['fecha_baja']=None
						request.data._mutable = False
						
					aux = request.FILES['soportedebaja'] if self.request.FILES.get('soportedebaja') is not None else instance.soportedebaja
					if aux:
						serializer  = ActivoLite4Serializer(instance,data={
							'tipo_id': request.data['tipo_id'],
							'identificacion':request.data['identificacion'],
							'serial_placa':request.data['serial_placa'],
							'descripcion':request.data['descripcion'],
							'contrato_id':request.data['contrato_id'],
							'valor_compra':request.data['valor_compra'],
							'responsable_id':request.data['responsable_id'],
							'vida_util_dias':request.data['vida_util_dias'],
							'periodicidad_mantenimiento':request.data['periodicidad_mantenimiento'],
							'fecha_baja':request.data['fecha_baja'],
							'fecha_alta':request.data['fecha_alta'],
							'motivo_debaja':request.data['motivo_debaja'],
							'soportedebaja': request.FILES['soportedebaja'] if self.request.FILES.get('soportedebaja') is not None else instance.soportedebaja,
							},context={'request': request},partial=partial)

					else:
						serializer  = ActivoLite4Serializer(instance,data={
							'tipo_id': request.data['tipo_id'],
							'identificacion':request.data['identificacion'],
							'serial_placa':request.data['serial_placa'],
							'descripcion':request.data['descripcion'],
							'contrato_id':request.data['contrato_id'],
							'valor_compra':request.data['valor_compra'],
							'responsable_id':request.data['responsable_id'],
							'vida_util_dias':request.data['vida_util_dias'],
							'periodicidad_mantenimiento':request.data['periodicidad_mantenimiento'],
							'fecha_baja':request.data['fecha_baja'],
							'fecha_alta':request.data['fecha_alta'],
							'motivo_debaja':request.data['motivo_debaja'],
							},context={'request': request},partial=partial)

					if serializer.is_valid():
						
						serializer.save(
							tipo_id=int(request.data['tipo_id']),
							responsable_id=int(request.data['responsable_id']),
							contrato_id=int(request.data['contrato_id']),
							soportedebaja=request.FILES['soportedebaja'] if self.request.FILES.get('soportedebaja') is not None else instance.soportedebaja)						


						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='activos.activo',id_manipulado=instance.id)
						logs_model.save()

						#import pdb; pdb.set_trace()

						if aux_tipo!=int(request.data['tipo_id']):
							Activo_atributo_soporte.objects.filter(activo_atributo__activo__id=instance.id).delete()
							Activo_atributo.objects.filter(activo__id=instance.id).delete()
							

							valores=request.POST.getlist('valor[]')
							atributos=request.POST.getlist('atributo[]')
							estados= request.POST.getlist('estado_atributo[]')


							id_aux = request.POST.getlist('id_atributo[]')
							soportes= request.FILES.getlist('soporte_atributo[]')
							

							if valores and atributos and estados:
								j = 0
								serializer_activo_atributo=''
								for x in valores:

									serializer_activo_atributo = Activo_atributoLiteSerializer(data={
										'atributo_id':atributos[j],
										'valor':valores[j],
										'activo_id':serializer.data['id']
										},context={'request': request})

									if serializer_activo_atributo.is_valid():
										serializer_activo_atributo.save(atributo_id=atributos[j],activo_id=serializer.data['id'])								
										

										if estados[j]=='true':
											q = 0
											for sop in soportes:
												if id_aux[q]==atributos[j]:
													sp = Activo_atributo_soporte(activo_atributo_id=serializer_activo_atributo.data['id'],documento=soportes[q])
													sp.save()
												q = q + 1;

										j = j + 1;

										serializer_activo_atributo = ''

						else:

							valores=request.POST.getlist('valor[]')
							atributos=request.POST.getlist('atributo[]')
							estados= request.POST.getlist('estado_atributo[]')

							activo_atributo_id= request.POST.getlist('activo_atributo_id[]')


							id_aux = request.POST.getlist('id_atributo[]')
							soportes= request.FILES.getlist('soporte_atributo[]')
							soportes_id= request.POST.getlist('soporte_id[]')
							

							if valores and atributos and estados:
								j = 0
								serializer_activo_atributo=''
								for x in activo_atributo_id:

									act_atri = Activo_atributo.objects.get(id=int(x))
									act_atri_serializer = Activo_atributoLite2Serializer(act_atri,data={
										'valor':valores[j],
										},context={'request': request},partial=partial)

									if act_atri_serializer.is_valid():
										act_atri_serializer.save()							

										if estados[j]=='true':
											q = 0
											for sop in soportes_id:
												if id_aux[q]==atributos[j]:
													if sop:
														obj_soporte = Activo_atributo_soporte.objects.get(id=int(sop))

														obj_soporte_serializer = Activo_atributo_soporteLite2Serializer(obj_soporte, data={
															'documento': soportes[q],
															},context={'request': request},partial=partial)

														if obj_soporte_serializer.is_valid():
															obj_soporte_serializer.save()
														
													else:	
														sp = Activo_atributo_soporte(activo_atributo_id=act_atri.id,documento=soportes[q])
														sp.save()
												q = q + 1;

										j = j + 1;

										serializer_activo_atributo = ''

						latitudes=request.POST.getlist('latitud[]')
						longitudes=request.POST.getlist('longitud[]')
						id_puntos = request.POST.getlist('id_puntosgps[]')
						

						if latitudes and longitudes and nombres and id_puntos:
							##import pdb; pdb.set_trace()
							i = 0
							for sp in id_puntos:
								
								if int(sp)>0:
									s = Activo_gps.objects.get(id=int(sp))								
									s_serializer = Puntos_gpsLite2Serializer(s,data={
										'nombre':nombres[i],
										'latitud':float(latitudes[i]),
										'longitud':float(longitudes[i]),
										},context={'request': request},partial=partial)
									if s_serializer.is_valid():
										s_serializer.save()
								else:
									#import pdb; pdb.set_trace()
									if len(latitudes)>i and len(longitudes)>i and len(nombres)>i:
										s_serializer = Puntos_gpsLiteSerializer(data={
											'nombre':nombres[i],
											'activo_id':int(instance.id),
											'latitud':float(latitudes[i]),
											'longitud':float(longitudes[i]),
											},context={'request': request})
										if s_serializer.is_valid():
											s_serializer.save(activo_id=int(instance.id))
									
								i = i + 1;

						transaction.savepoint_commit(sid)
						return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
					else:
						if serializer.errors['non_field_errors']:
							mensaje = serializer.errors['non_field_errors']
						else:
							mensaje='datos requeridos no fueron recibidos'
						return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				##respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

class AtributoViewSet(viewsets.ModelViewSet):
	model = Atributo
	queryset = model.objects.all()
	serializer_class = AtributoSerializer
	nombre_modulo = 'Activos'

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
			###import pdb; pdb.set_trace()
			queryset = super(AtributoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			tipo = self.request.query_params.get('tipo_id', None)

			qset=(~Q(id=0))
			if tipo:
				qset = qset &(Q(tipo__id=int(tipo)))


			queryset = self.model.objects.filter(qset)


			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			###import pdb; pdb.set_trace()			
			try:
				serializer = AtributoLiteSerializer(data=request.data,context={'request': request})
				###import pdb; pdb.set_trace()
				if serializer.is_valid():
					serializer.save()						

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.atributo',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer  = ActivoLite2Serializer(instance,data=request.data,context={'request': request})
				if serializer.is_valid():
					
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,
						nombre_modelo='activos.atributo',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos.atributo',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				##respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)


class Activo_atributoViewSet(viewsets.ModelViewSet):
	model = Activo_atributo
	queryset = model.objects.all()
	serializer_class = Activo_atributoSerializer
	nombre_modulo = 'Activos'

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
			queryset = super(Activo_atributoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			activo = self.request.query_params.get('activo', None)

			qset=(~Q(id=0))
			if activo:
				qset = qset &(Q(activo__id=int(activo)))


			queryset = self.model.objects.filter(qset)

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			###import pdb; pdb.set_trace()			
			try:
				serializer = Activo_atributoLiteSerializer(data=request.data,context={'request': request})
				###import pdb; pdb.set_trace()
				if serializer.is_valid():
					serializer.save()						

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.activo_atributo',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer  = ActivoLite2Serializer(instance,data=request.data,context={'request': request})
				if serializer.is_valid():
					
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,
						nombre_modelo='activos.activo_atributo',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos.activo_atributo',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				##respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

class Activo_atributo_soporteViewSet(viewsets.ModelViewSet):
	model = Activo_atributo_soporte
	queryset = model.objects.all()
	serializer_class = Activo_atributo_soporteSerializer
	nombre_modulo = 'Activos'

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
			###import pdb; pdb.set_trace()
			queryset = super(Activo_atributo_soporteViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			activo_atributo = self.request.query_params.get('activo_atributo', None)

			qset=(~Q(id=0))
			if activo_atributo:
				qset = qset &(Q(activo_atributo__id=int(activo_atributo)))


			queryset = self.model.objects.filter(qset)

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			###import pdb; pdb.set_trace()			
			try:
				serializer = Activo_atributo_soporteLiteSerializer(data={
					'activo_atributo_id':int(request.data['activo_atributo_id']),
					'documento':request.FILES['documento']
					},context={'request': request})
				###import pdb; pdb.set_trace()
				if serializer.is_valid():
					serializer.save(activo_atributo_id=request.data['activo_atributo_id'])						

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.activo_atributo_soporte',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer  = ActivoLite2Serializer(instance,data=request.data,context={'request': request})
				if serializer.is_valid():
					
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,
						nombre_modelo='activos.activo_atributo_soporte',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos.activo_atributo_soporte',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				##respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

class Activo_personaViewSet(viewsets.ModelViewSet):
	model = Activo_persona
	queryset = model.objects.all()
	serializer_class = Activo_personaSerializer
	nombre_modulo = 'Activos'

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
			queryset = super(Activo_personaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			###import pdb; pdb.set_trace()			
			try:
				serializer = Activo_personaLiteSerializer(data=request.data,context={'request': request})
				###import pdb; pdb.set_trace()
				if serializer.is_valid():
					serializer.save()						

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.activo_persona',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer  = Activo_personaLiteSerializer(instance,data=request.data,context={'request': request})
				if serializer.is_valid():
					
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,
						nombre_modelo='activos.activo_persona',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos.activo_persona',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				#respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

class MotivoViewSet(viewsets.ModelViewSet):
	model = Motivo
	queryset = model.objects.all()
	serializer_class = MotivoSerializer
	nombre_modulo = 'Activos'

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
			###import pdb; pdb.set_trace()
			queryset = super(MotivoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			tipo_activo = self.request.query_params.get('tipo_activo', None)
			
			qset=(~Q(id=0))
			if dato:
				qset = qset &(Q(motivo__nombre__icontains=dato))
			if tipo_activo:
				qset = qset &(Q(tipo_activo__id=int(tipo_activo)))	


			queryset = self.model.objects.filter(qset)
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			###import pdb; pdb.set_trace()			
			try:
				serializer = MotivoLiteSerializer(data=request.data,context={'request': request})
				###import pdb; pdb.set_trace()
				if serializer.is_valid():
					serializer.save()						

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.motivo',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer  = ActivoLite2Serializer(instance,data=request.data,context={'request': request})
				if serializer.is_valid():
					
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,
						nombre_modelo='activos.motivo',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos.motivo',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				#respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

class MantenimientoViewSet(viewsets.ModelViewSet):
	model = Mantenimiento
	queryset = model.objects.all()
	serializer_class = MantenimientoSerializer
	nombre_modulo = 'Activos'

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
			queryset = super(MantenimientoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			activo = self.request.query_params.get('activo', None)

			qset=(~Q(id=0))
			if dato:
				qset = qset &(Q(motivo__nombre__icontains=dato))
			if activo:
				qset = qset &(Q(activo__id=int(activo)))	


			queryset = self.model.objects.filter(qset)

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			###import pdb; pdb.set_trace()			
			try:
				

				serializer = MantenimientoLiteSerializer(data=request.data,context={'request': request})
				###import pdb; pdb.set_trace()
				if serializer.is_valid():
					serializer.save(motivo_id=int(request.data['motivo_id']),contrato_id=int(request.data['contrato_id']),activo_id=int(request.data['activo_id']))						

					soportes=request.FILES.getlist('soporte[]')
					nombres=request.POST.getlist('nombre[]')

					if soportes and nombres:
							i = 0
							for sp in soportes:							
								s= Soporte_mantenimiento(archivo=sp, nombre=nombres[i],mantenimiento_id=serializer.data['id'])
								s.save()
								i = i + 1;

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.mantenimiento',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer  = ActivoLite2Serializer(instance,data=request.data,context={'request': request})
				if serializer.is_valid():
					
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,
						nombre_modelo='activos.mantenimiento',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos.mantenimiento',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				#respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

class Soporte_mantenimientoViewSet(viewsets.ModelViewSet):
	model = Soporte_mantenimiento
	queryset = model.objects.all()
	serializer_class = Soporte_mantenimientoSerializer
	nombre_modulo = 'Activos'

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
			queryset = super(Soporte_mantenimientoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			mantenimiento = self.request.query_params.get('mantenimiento', None)

			qset=(~Q(id=0))
			if dato:
				qset = qset &(Q(nombre__icontains=dato))
			if mantenimiento:
				qset = qset &(Q(mantenimiento__id=int(mantenimiento)))	


			queryset = self.model.objects.filter(qset)

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			###import pdb; pdb.set_trace()			
			try:
				serializer = Soporte_mantenimientoLiteSerializer(data=request.data,context={'request': request})
				###import pdb; pdb.set_trace()
				if serializer.is_valid():
					serializer.save(mantenimiento_id=int(request.data['mantenimiento_id']))						

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.soporte_mantenimiento',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer  = ActivoLite2Serializer(instance,data=request.data,context={'request': request})
				if serializer.is_valid():
					
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,
						nombre_modelo='activos.soporte_mantenimiento',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos.soporte_mantenimiento',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				#respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

		

class Puntos_gpsViewSet(viewsets.ModelViewSet):
	model = Activo_gps
	queryset = model.objects.all()
	serializer_class = Puntos_gpsSerializer
	nombre_modulo = 'Activos'

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
			##import pdb; pdb.set_trace()
			queryset = super(Puntos_gpsViewSet, self).get_queryset()			
			activo = self.request.query_params.get('activo', None)
			punto_id = self.request.query_params.get('id', None)
			dato = self.request.query_params.get('dato', None)
			categoria = self.request.query_params.get('categoria', None)
			tipo = self.request.query_params.get('tipo', None)
			estado = self.request.query_params.get('estado', None)
			funcionario = self.request.query_params.get('funcionario', None)

			qset=(~Q(id=0))
			
			if punto_id:
				qset = qset &(Q(id=int(punto_id)))

			if activo:
				qset = qset &(Q(activo__id=int(activo)))

			if dato:
				qset = qset &(Q(nombre__icontains=dato) |
							 (Q(activo__identificacion__icontains=dato)|
							 Q(activo__serial_placa__icontains=dato) |
							 Q(activo__contrato__numero__icontains=dato)|
							 Q(activo__contrato__nombre__icontains=dato)))

			if categoria:
				qset = qset &(Q(activo__tipo__categoria__id=int(categoria)))
			if tipo:
				qset = qset &(Q(activo__tipo__id=int(tipo)))
			if estado:
				if int(estado)<2:
					qset = qset &(Q(activo__debaja=estado))
			if funcionario:
				qset = qset &(Q(activo__responsable__id=int(funcionario)))

			queryset = self.model.objects.filter(qset)

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			
			serializer = self.get_serializer(queryset,many=True)


			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			###import pdb; pdb.set_trace()			
			try:

				existepunto = Activo_gps.objects.filter(activo_id=int(request.data['activo_id']),nombre=request.data['nombre'])

				if existepunto:
					return Response({'message':'El nombre ya existe para este activo.','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
				
				# request.data._mutable = True
				# request.data['latitud']=float(request.data['latitud'])
				# request.data['longitud']=float(request.data['latitud'])
				# request.data._mutable = False

				serializer = Puntos_gpsSerializer(data=request.data,context={'request': request})

				if serializer.is_valid():
					serializer.save(activo_id=int(request.data['activo_id']))						

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,
							nombre_modelo='activos.punto_gps',id_manipulado=serializer.data['id'])
					logs_model.save()

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		###import pdb; pdb.set_trace()
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				partial = kwargs.pop('partial', False)
				instance = self.get_object()

				qset = (~Q(id = int(request.data['id'])) & (Q(activo_id=int(request.data['activo_id'])) & (Q(nombre=request.data['nombre']))))
				existepunto = Activo_gps.objects.filter(qset)

				if existepunto:
					return Response({'message':'El nombre ya existe para este activo.','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

				request.data._mutable = True
				request.data['latitud']=float(request.data['latitud'])
				request.data['longitud']=float(request.data['longitud'])
				request.data._mutable = False


				serializer  = Puntos_gpsSerializer(instance,data=request.data,context={'request': request})
				if serializer.is_valid():
					serializer.save(activo_id=int(request.data['activo_id']))

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,
						nombre_modelo='activos.punto_gps',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha dado de baja exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos',
					'success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':			
			try:
				###import pdb; pdb.set_trace()

				instance = self.get_object()
				id_aux = instance.id
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)	

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,
					nombre_modelo='activos.punto_gps',id_manipulado=id_aux)
				logs_model.save()

				return Response({'message':'El registro ha sido eliminado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_202_ACCEPTED)

			except Exception as e:
				#respuesta=Estructura.error500_2('Este tipo de documento no se puede eliminar debido a que se encuentra en uso')				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)



@login_required
def mantenimientos (request,id):
	activo = Activo.objects.get(id=id)
	return render(request, 'activos/mantenimientos.html',
		{'id':id,
		'activo':activo,
		'model':'activos_activo',
		'app':'activos',
		'model_activo': 'activo',
		'model_soporte_mantenimiento':'soporte_mantenimiento',
		'model_activo_atributo_soporte':'activo_atributo_soporte',
		'model_activo_atributo':'activo_atributo',
		'model_mantenimiento':'mantenimiento',
		'model_activo_persona':'activo_persona',
		'model_categoria':'categoria',
		'model_atributo':'atributo',
		'model_tipo_activo':'tipo_activo',
		'model_motivo':'motivo',
		'model_activo_gps':'activo_gps',	
		})


@login_required
def activo_view(request):
	#import pdb; pdb.set_trace()
	try:
		categorias = Categoria.objects.all()
		funcionarios = Funcionario.objects.all()
		app='activos'
		modulo='activo'
		return render(request,'activos/activo.html',
			{
				'app' : app,
				'model_activo': modulo,
				'model_soporte_mantenimiento':'soporte_mantenimiento',
				'model_activo_atributo_soporte':'activo_atributo_soporte',
				'model_activo_atributo':'activo_atributo',
				'model_mantenimiento':'mantenimiento',
				'model_activo_persona':'activo_persona',
				'model_categoria':'categoria',
				'model_atributo':'atributo',
				'model_tipo_activo':'tipo_activo',
				'model_motivo':'motivo',
				'model_activo_gps':'activo_gps',
				'categorias':categorias,
				'funcionarios':funcionarios,
			})
	except Exception as e:
		functions.toLog(e, 'activos')
		return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)


@login_required
def ubicacion_view(request):
	try:
		categorias = Categoria.objects.all()
		funcionarios = Funcionario.objects.all()
		app='activos'
		modulo='activo'
		return render(request,'activos/ubicacion.html',
			{
				'app' : app,
				'model_activo': modulo,
				'model_soporte_mantenimiento':'soporte_mantenimiento',
				'model_activo_atributo_soporte':'activo_atributo_soporte',
				'model_activo_atributo':'activo_atributo',
				'model_mantenimiento':'mantenimiento',
				'model_activo_persona':'activo_persona',
				'model_categoria':'categoria',
				'model_atributo':'atributo',
				'model_tipo_activo':'tipo_activo',
				'model_motivo':'motivo',
				'model_activo_gps':'activo_gps',
				'categorias':categorias,
				'funcionarios':funcionarios,
			})
	except Exception as e:
		functions.toLog(e, 'activos')
		return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)


@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			doc = Activo.objects.get(pk=request.GET['id'])			
			return functions.exportarArchivoS3(str(doc.soportedebaja))

		except Exception as e:
			functions.toLog(e,'documento')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
def VerSoporteManteniento(request):
	if request.method == 'GET':
		try:
			
			doc = Soporte_mantenimiento.objects.get(pk=request.GET['id'])			
			return functions.exportarArchivoS3(str(doc.archivo))

		except Exception as e:
			functions.toLog(e,'documento')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def VerSoporteAtributo(request):
	##import pdb; pdb.set_trace()
	if request.method == 'GET':
		try:
			
			doc = Activo_atributo_soporte.objects.get(pk=request.GET['id'])			
			return functions.exportarArchivoS3(str(doc.documento))

		except Exception as e:
			functions.toLog(e,'documento')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def VerSoporteActivos(request):
	#import pdb; pdb.set_trace()
	if request.method == 'GET':
		try:
			
			boolean_vigencia = VigenciaContrato.objects.filter(contrato_id=request.GET['id']).exists()

			if boolean_vigencia:
				vigencia = VigenciaContrato.objects.filter(contrato_id=request.GET['id'])

				archivo = vigencia[0]
				return functions.exportarArchivoS3(str(archivo.soporte))
			else:
				return JsonResponse({'message':'No se encuentra el soporte','success':'fail','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		except Exception as e:
			functions.toLog(e,'constrato.VerSoporteActivos')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			



def exportReporteActivos(request):

	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="Activos.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Activos')
	format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
	format_estado_true=workbook.add_format({'border':1, 'bg_color':'#10E615','font_color':'white'})
	format_estado_false=workbook.add_format({'border':1, 'bg_color':'#FF2727','font_color':'white'})
	format_noaplica=workbook.add_format({'border':1, 'bg_color':'#E7FC1C'})
	format2=workbook.add_format({'border':1})
	format_num=workbook.add_format({'border':1, 'num_format': '#'})
	format_money=workbook.add_format({'border':1, 'num_format': '$#,##0.00'})
	format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})

	row=1
	col=0
				
	Activoss = Activo.objects.filter()

	worksheet.write('A1', 'No. activo', format1)
	worksheet.write('B1', 'Tipo', format1)
	worksheet.write('C1', 'Identificacion', format1)
	worksheet.write('D1', 'Serial/Placa', format1)
	worksheet.write('E1', 'Descripcion', format1)
	worksheet.write('F1', 'Numero de contrato', format1)
	worksheet.write('G1', 'Valor de compra', format1)
	worksheet.write('H1', 'Responsable', format1)
	worksheet.write('I1', 'Vida util', format1)
	worksheet.write('J1', 'Periodicidad Mantenimiento', format1)
	worksheet.write('K1', 'Estado', format1)
	worksheet.write('L1', 'Fecha de alta', format1)
	worksheet.write('M1', 'Fecha de baja', format1)
	worksheet.write('N1', 'Motivo de baja', format1)



	worksheet.set_column('A:A', 10)
	worksheet.set_column('B:B', 25)
	worksheet.set_column('C:C', 15)
	worksheet.set_column('D:D', 15)
	worksheet.set_column('E:E', 40)
	worksheet.set_column('F:F', 20)
	worksheet.set_column('G:G', 20)
	worksheet.set_column('H:H', 30)
	worksheet.set_column('I:I', 10)
	worksheet.set_column('J:J', 15)
	worksheet.set_column('K:K', 10)
	worksheet.set_column('L:L', 15)
	worksheet.set_column('M:M', 15)
	worksheet.set_column('N:N', 20)

	for Act in Activoss:

			
		worksheet.write(row, col,Act.id,format2)
		worksheet.write(row, col+1,Act.tipo.nombre,format2)
		worksheet.write(row, col+2,Act.identificacion,format2)
		worksheet.write(row, col+3,Act.serial_placa,format2)
		worksheet.write(row, col+4,Act.descripcion,format2)
		worksheet.write(row, col+5,Act.contrato.numero,format2)
		worksheet.write(row, col+6,Act.valor_compra,format_money)
		worksheet.write(row, col+7,Act.responsable.contrato.contratista.nombre,format2)
		worksheet.write(row, col+8,Act.vida_util_dias,format_num)
		worksheet.write(row, col+9,Act.periodicidad_mantenimiento,format_num)
		if Act.debaja:
			worksheet.write(row, col+10,'De baja',format_estado_false)			
			worksheet.write(row, col+11,Act.fecha_alta,format_date)
			worksheet.write(row, col+12,Act.fecha_baja,format_date)
			worksheet.write(row, col+13,Act.motivo_debaja,format2)

		else:
			worksheet.write(row, col+10,'De alta',format_estado_true)			
			worksheet.write(row, col+11,Act.fecha_alta,format_date)
			worksheet.write(row, col+12,'No aplica',format_noaplica)
			worksheet.write(row, col+13,'No aplica',format_noaplica)



			

		row +=1


	workbook.close()

	return response


def exportReporteMantenimientos(request):

	activo_id = request.GET['activo'];

	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="Activo No.'+activo_id+' - Mantenimientos.xls"'

	Mantenimientos = Mantenimiento.objects.filter(activo_id=activo_id)


	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Activo No.'+activo_id+' - Mantenimientos')
	format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
	format_estado_true=workbook.add_format({'border':1, 'bg_color':'#10E615','font_color':'white'})
	format_estado_false=workbook.add_format({'border':1, 'bg_color':'#FF2727','font_color':'white'})
	format_noaplica=workbook.add_format({'border':1, 'bg_color':'#E7FC1C'})
	format2=workbook.add_format({'border':1})
	format_num=workbook.add_format({'border':1, 'num_format': '#'})
	format_money=workbook.add_format({'border':1, 'num_format': '$#,##0.00'})
	format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
	format_hour=workbook.add_format({'border':1,'num_format': 'hh:mm'})
	

	row=1
	col=0


	worksheet.write('A1', 'Motivo', format1)
	worksheet.write('B1', 'Fecha', format1)
	worksheet.write('C1', 'Hora', format1)
	worksheet.write('D1', 'Observaciones', format1)
	worksheet.write('E1', 'Contrato de mantenimiento', format1)
	worksheet.write('F1', 'Numero del contrato', format1)

	worksheet.set_column('A:A', 20)
	worksheet.set_column('B:B', 15)
	worksheet.set_column('C:C', 15)
	worksheet.set_column('D:D', 40)
	worksheet.set_column('E:E', 30)
	worksheet.set_column('F:F', 15)

	for Man in Mantenimientos:
		worksheet.write(row, col,Man.motivo.nombre,format2)
		worksheet.write(row, col+1,Man.fecha,format_date)
		worksheet.write(row, col+2,Man.hora,format_hour)
		worksheet.write(row, col+3,Man.observaciones,format2)
		worksheet.write(row, col+4,Man.contrato.nombre,format2)
		worksheet.write(row, col+5,Man.contrato.numero,format_num)

		row +=1


	workbook.close()

	return response