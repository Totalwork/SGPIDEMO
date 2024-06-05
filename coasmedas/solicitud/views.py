# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response # render,redirect,
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

# Para importaciones a excel y retornar Json a la vista
from django.http import HttpResponse, JsonResponse

# Para consultas SQL
from django.db.models import Q #, Sum
from django.db import transaction #, connection
# from django.db.models.deletion import ProtectedError


from rest_framework import viewsets, serializers
# from rest_framework.renderers import JSONRenderer
# from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.parsers import MultiPartParser, FormParser

import json

from .models import ASolicitud,BRequisitoJuridico, CFavorabilidadJuridica, DFavorabilidadJuridicaRequisito, BRequisitoCompras, CFavorabilidadCompras, DFavorabilidadComprasRequisito,BRequisitoTecnico, CFavorabilidadTecnica, DFavorabilidadTecnicaRequisito
from .models import BRequisitoPoliza, CValidarPoliza, DPolizaTipo, EPolizaTipoRequisito
from .enumeration import estadoSolicitud
from logs.models import Logs, Acciones
from sinin4.functions import functions
from contrato.models import Contrato
from contrato.enumeration import tipoC
from estado.models import Estado
from tipo.models import Tipo
from empresa.models import Empresa

from estado.views import EstadoSerializer
from tipo.views import TipoSerializer
# Create your views here.

#Api rest para Solicitud
class ContratistaLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Empresa
		fields=('id','nombre')

class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):

	contratista = ContratistaLiteSerializer(read_only=True)
	# contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	class Meta:
		model = Contrato
		fields=('id','nombre','numero','contratista')

class SolicitudSerializer(serializers.HyperlinkedModelSerializer):
	tipo_c=tipoC()

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='Solicitud'))

	tipo = TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='Solicitud'))

	contrato = ContratoLiteSerializer(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	concepto = serializers.SerializerMethodField('_concepto',read_only=True)
	juridico = serializers.SerializerMethodField('_juridico',read_only=True)
	compras = serializers.SerializerMethodField('_compras',read_only=True)
	tecnica = serializers.SerializerMethodField('_tecnica',read_only=True)
	poliza = serializers.SerializerMethodField('_poliza',read_only=True)

	# Cuenta los conceptos cumplidos
	def _concepto(self, obj):
		model_fj = CFavorabilidadJuridica.objects.filter(solicitud_id=obj.id).first()
		# print "soporte: "+str(model_fj.soporte)
		model_fc = CFavorabilidadCompras.objects.filter(solicitud_id=obj.id).first()
		model_ft = CFavorabilidadTecnica.objects.filter(solicitud_id=obj.id).first()

		cont = 0
		if model_fj:
			if model_fj.soporte:
				cont += 1

		if model_fc:
			if model_fc.soporte:
				cont += 1

		if model_ft:
			if model_ft.soporte:
				cont += 1

		return cont

	def _juridico(self, obj):

		model_fj = CFavorabilidadJuridica.objects.filter(solicitud_id=obj.id).values('id', 'observacion', 'soporte').first()

		sb_soporte = 1
		if model_fj:
			model_fjr = DFavorabilidadJuridicaRequisito.objects.filter(favorabilidad_id=model_fj['id']).values('id', 'requisito', 'estado', 'requisito__nombre')

			cont = 0
			total_r = 0
			for fjr in model_fjr:
				total_r += 1
				if fjr['estado']:
					cont += 1

			# Validar si puede cargar el archivo
			if total_r != cont:
				sb_soporte = 0

			model_fj.update({'requisito':model_fjr})
			model_fj.update({'sb_soporte':sb_soporte})

			return model_fj
		else:
			return ''

	def _compras(self, obj):

		model_fc = CFavorabilidadCompras.objects.filter(solicitud_id=obj.id).values('id', 'observacion', 'soporte').first()

		sb_soporte = 1
		if model_fc:
			model_fcr = DFavorabilidadComprasRequisito.objects.filter(favorabilidad_id=model_fc['id']).values('id','requisito','estado','requisito__nombre')

			cont = 0
			total_r = 0
			for fcr in model_fcr:
				total_r += 1
				if fcr['estado']:
					cont += 1

			# Validar si puede cargar el archivo
			if total_r != cont:
				sb_soporte = 0

			model_fc.update({'requisito':model_fcr})
			model_fc.update({'sb_soporte':sb_soporte})

			return model_fc
		else:
			return ''

	def _tecnica(self, obj):

		model_ft = CFavorabilidadTecnica.objects.filter(solicitud_id=obj.id).values('id', 'observacion', 'soporte').first()

		sb_soporte = 1
		if model_ft:
			model_ftr = DFavorabilidadTecnicaRequisito.objects.filter(favorabilidad_id=model_ft['id']).values('id','requisito','estado','requisito__nombre')

			cont = 0
			total_r = 0
			for ftr in model_ftr:
				total_r += 1
				if ftr['estado']:
					cont += 1

			# Validar si puede cargar el archivo
			if total_r != cont:
				sb_soporte = 0

			model_ft.update({'requisito':model_ftr})
			model_ft.update({'sb_soporte':sb_soporte})

			return model_ft
		else:
			return ''

	def _poliza(self, obj):

		model_vp = CValidarPoliza.objects.filter(solicitud_id=obj.id).values('id', 'soporte').first()

		if model_vp:
			model_pt = DPolizaTipo.objects.filter(validar_poliza_id=model_vp['id']).values('id', 'tipo', 'tipo__nombre')

			# model_ptr = EPolizaTipoRequisito.objects.filter(poliza_tipo_id=model_pt['id']).values('id','requisito','requisito__nombre','estado')

			# model_vp.update({'requisito':model_vpr}) EPolizaTipoRequisito

			sb_soporte = 1
			for model in model_pt:

				model_ptr = EPolizaTipoRequisito.objects.filter(poliza_tipo_id=model['id']).values('id','requisito','requisito__nombre','poliza_tipo','estado')
				model.update({'requisito':model_ptr})

				cont = 0
				total_r = 0
				for ptr in model_ptr:
					total_r += 1
					if ptr['estado']:
						cont += 1

				# print "total_r: "+str(total_r)
				model.update({'activos':cont})

				# Validar si puede cargar el archivo
				if total_r != cont:
					sb_soporte = 0

			model_vp.update({'tipo_poliza':model_pt})
			model_vp.update({'sb_soporte':sb_soporte})
			return model_vp
		else:
			return ''

	class Meta:
		model = ASolicitud
		fields=('id','tipo','tipo_id','estado','estado_id','contrato_id','contrato',
						'fecha','observacion','carta_aceptacion','soporte','juridico','compras','tecnica','poliza','concepto')

class SolicitudContratoViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=ASolicitud
	queryset = model.objects.all()
	serializer_class = SolicitudSerializer
	nombre_modulo = 'Solicitud - SolicitudContratoViewSet'

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
			queryset = super(SolicitudContratoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)

			desde = self.request.query_params.get('desde', None)
			hasta = self.request.query_params.get('hasta', None)
			id_estado = self.request.query_params.get('id_estado').split(',') if self.request.query_params.get('id_estado') else None
			id_tipo = self.request.query_params.get('id_tipo').split(',') if self.request.query_params.get('id_tipo') else None

			# id_contrato = self.request.query_params.get('id_contrato', None)
			# tipo_contrato = self.request.query_params.get('tipo_contrato', None)
			# numero_contrato = self.request.query_params.get('numero_contrato', None)
			id_contratista = self.request.query_params.get('id_contratista').split(',') if self.request.query_params.get('id_contratista') else None
			# id_mcontrato = self.request.query_params.get('id_mcontrato', None)

			tipo = self.request.query_params.get('tipo',None)
			num_estado = self.request.query_params.get('num_estado',None)
			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			if dato:
				qset = qset &(
					Q(observacion__icontains=dato)|Q(contrato__contratista__nombre__icontains=dato)|Q(contrato__nombre__icontains=dato)|Q(contrato__numero__icontains=dato)
					)

			if desde:
				qset = qset &(Q(fecha__gte=desde))
			if hasta:
				qset = qset &(Q(fecha__lte=hasta))

			if id_contratista:
				qset = qset &(Q(contrato__contratista__in=id_contratista))
			# if tipo_contrato:
			# 	qset = qset &(Q(contrato__tipo_contrato=tipo_contrato))
			# if numero_contrato:
			# 	qset = qset &(Q(contrato__numero=numero_contrato))
			# if id_contratista and int(id_contratista)>0:
			# 	qset = qset &(Q(contrato__contratista_id=id_contratista))
			# if id_mcontrato and int(id_mcontrato)>0:
			# 	qset = qset &(Q(contrato__mcontrato_id=id_mcontrato))

			if id_estado:
				qset = qset &(Q(estado__in=id_estado))
			if id_tipo:
				qset = qset &(Q(tipo__in=id_tipo))

			if id_empresa:
				qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))


			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:

					serializer = self.get_serializer(page,many=True)

					if num_estado:
						qsEnEstudio=ASolicitud.objects.filter(estado=estadoSolicitud.enEstudio, contrato__empresacontrato__empresa=id_empresa, contrato__empresacontrato__participa=1, contrato__activo=1)
						qsAprobada=ASolicitud.objects.filter(estado=estadoSolicitud.aprobada)
						qsRechazada=ASolicitud.objects.filter(estado=estadoSolicitud.rechazada)

						enEstudio = len(qsEnEstudio)
						aprobada = len(qsAprobada)
						rechazada = len(qsRechazada)
					else:
						enEstudio = ''
						aprobada = ''
						rechazada = ''

					if tipo:
						querysetTipos=Tipo.objects.filter(app='Solicitud')
						querysetTiposContrato=Tipo.objects.filter(app='contrato')
						querysetEstado = Estado.objects.filter(app='Solicitud')

						tipos = TipoSerializer(querysetTipos,many=True).data
						tipos_contrato = TipoSerializer(querysetTiposContrato,many=True).data
						estado = EstadoSerializer(querysetEstado,many=True).data

						return self.get_paginated_response({'message':'',
																								'success':'ok',
																								'data':{'listado':serializer.data,
																												'tipo':tipos,
																												'tipo_contrato':tipos_contrato,
																												'estado':estado,
																												'num_estado':{'enEstudio':enEstudio,
																																			'aprobada':aprobada,
																																			'rechazada':rechazada} }})
					else:
						return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = SolicitudSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():
					# print "qwqw"
					serializer.save(contrato_id=request.DATA['contrato_id'], estado_id=request.DATA['estado_id'], tipo_id=request.DATA['tipo_id'],
						soporte=request.FILES['soporte'] if request.FILES.get('soporte') is not None else '',
						carta_aceptacion=request.FILES['carta_aceptacion'] if request.FILES.get('carta_aceptacion') is not None else '')
					# print "asasas"
					createFavorabilidadPoliza(request, serializer.data['id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.solicitud',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = SolicitudSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(
						soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte,
						carta_aceptacion=self.request.FILES['carta_aceptacion'] if self.request.FILES.get('carta_aceptacion') is not None else instance.carta_aceptacion,
						contrato_id=self.request.DATA['contrato_id'],
						estado_id=self.request.DATA['estado_id'],
						tipo_id=self.request.DATA['tipo_id'])

					if self.request.FILES.get('carta_aceptacion') is not None:
						print("carta")
						# cambiarEstadoSolicitud(request, estadoSolicitud.aprobada)
					else:
						print("sin carta")

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.solicitud',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.solicitud',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para Solicitud


#Api rest para BRequisitoJuridico
class RequisitoJuridicoSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = BRequisitoJuridico
		fields=('id','nombre')

class RequisitoJuridicoViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=BRequisitoJuridico
	queryset = model.objects.all()
	serializer_class = RequisitoJuridicoSerializer
	nombre_modulo = 'Solicitud - RequisitoJuridicoViewSet'

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
			queryset = super(RequisitoJuridicoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(nombre__icontains=dato))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = RequisitoJuridicoSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Requisito_Juridico',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = RequisitoJuridicoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Requisito_Juridico',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Requisito_Juridico',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para BRequisitoJuridico

#Api rest para CFavorabilidadJuridica
class FavorabilidadJuridicaSerializer(serializers.HyperlinkedModelSerializer):

	solicitud = SolicitudSerializer(read_only=True)
	solicitud_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = ASolicitud.objects.all())

	# requisito = serializers.SerializerMethodField('_requisito',read_only=True)

	# def _juridico(self, obj):
	# 	model_fj = CFavorabilidadJuridica.objects.filter(solicitud_id=obj.id).values('id','solicitud','observacion','soporte').first()

	# 	return model_fj

	class Meta:
		model = CFavorabilidadJuridica
		fields=('id','solicitud','solicitud_id','observacion','soporte')

class FavorabilidadJuridicaViewSet(viewsets.ModelViewSet):
	"""

	"""
	model = CFavorabilidadJuridica
	queryset = model.objects.all()
	serializer_class = FavorabilidadJuridicaSerializer
	nombre_modulo = 'Solicitud - FavorabilidadJuridicaViewSet'

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
			queryset = super(FavorabilidadJuridicaViewSet, self).get_queryset()

			dato = self.request.query_params.get('dato', None)
			solicitud = self.request.query_params.get('id_solicitud').split(',') if self.request.query_params.get('id_solicitud') else None

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			# id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(observacion__icontains=dato))

			if solicitud:
				qset = qset &(Q(solicitud__in=solicitud))

			# if id_empresa:
			# 	qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = FavorabilidadJuridicaSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save(solicitud_id=request.DATA['solicitud_id'],
													soporte=request.FILES['soporte'] if request.FILES.get('soporte') is not None else '')

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Favorabilidad_Juridica',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = FavorabilidadJuridicaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte,
													solicitud_id=request.DATA['solicitud_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Juridica',id_manipulado=instance.id)
					logs_model.save()

					editarRequisito(request, 'juridica', request.DATA['requisitos'], request.DATA['id'], 1)

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Favorabilidad_Juridica',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para CFavorabilidadJuridica

#Api rest para DFavorabilidadJuridicaRequisito
class FavorabilidadJuridicaRequisitoSerializer(serializers.HyperlinkedModelSerializer):

	requisito = RequisitoJuridicoSerializer(read_only=True)
	requisito_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = BRequisitoJuridico.objects.all())

	favorabilidad = FavorabilidadJuridicaSerializer(read_only=True)
	favorabilidad_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = CFavorabilidadJuridica.objects.all())

	class Meta:
		model = DFavorabilidadJuridicaRequisito
		fields=('id','requisito','requisito_id','favorabilidad','favorabilidad_id','estado')

class FavorabilidadJuridicaRequisitoViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=DFavorabilidadJuridicaRequisito
	queryset = model.objects.all()
	serializer_class = FavorabilidadJuridicaRequisitoSerializer
	nombre_modulo = 'Solicitud - FavorabilidadJuridicaRequisitoViewSet'

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
			queryset = super(FavorabilidadJuridicaRequisitoViewSet, self).get_queryset()

			dato = self.request.query_params.get('dato', None)
			estado = self.request.query_params.get('estado', None)
			requisito = self.request.query_params.get('id_requisito').split(',') if self.request.query_params.get('id_requisito') else None
			favorabilidad = self.request.query_params.get('id_favorabilidad').split(',') if self.request.query_params.get('id_favorabilidad') else None

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			# id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(requisito__nombre__icontains=dato)|Q(favorabilidad__observacion__icontains=dato))

			if estado:
				qset = qset &(Q(estado=estado))

			if requisito:
				qset = qset &(Q(requisito__in=requisito))

			if favorabilidad:
				qset = qset &(Q(favorabilidad__in=favorabilidad))

			# if id_empresa:
			# 	qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = FavorabilidadJuridicaRequisitoSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save(requisito_id=request.DATA['requisito_id'], favorabilidad_id=request.DATA['favorabilidad_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Favorabilidad_Juridica_Requisito',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = FavorabilidadJuridicaRequisitoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(requisito_id=request.DATA['requisito_id'], favorabilidad_id=request.DATA['favorabilidad_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Juridica_Requisito',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Favorabilidad_Juridica_Requisito',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para DFavorabilidadJuridicaRequisito


#Api rest para BRequisitoCompras
class RequisitoComprasSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = BRequisitoCompras
		fields=('id','nombre')

class RequisitoComprasViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=BRequisitoCompras
	queryset = model.objects.all()
	serializer_class = RequisitoComprasSerializer
	nombre_modulo = 'Solicitud - RequisitoComprasViewSet'

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
			queryset = super(RequisitoComprasViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(nombre__icontains=dato))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = RequisitoComprasSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Requisito_Compras',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = RequisitoComprasSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Requisito_Compras',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Requisito_Compras',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para BRequisitoCompras

#Api rest para CFavorabilidadCompras
class FavorabilidadComprasSerializer(serializers.HyperlinkedModelSerializer):

	solicitud = SolicitudSerializer(read_only=True)
	solicitud_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = ASolicitud.objects.all())

	class Meta:
		model = CFavorabilidadCompras
		fields=('id','solicitud','solicitud_id','observacion','soporte')

class FavorabilidadComprasViewSet(viewsets.ModelViewSet):
	"""

	"""
	model = CFavorabilidadCompras
	queryset = model.objects.all()
	serializer_class = FavorabilidadComprasSerializer
	nombre_modulo = 'Solicitud - FavorabilidadComprasViewSet'

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
			queryset = super(FavorabilidadComprasViewSet, self).get_queryset()

			dato = self.request.query_params.get('dato', None)
			solicitud = self.request.query_params.get('id_solicitud').split(',') if self.request.query_params.get('id_solicitud') else None

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			# id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(observacion__icontains=dato))

			if solicitud:
				qset = qset &(Q(solicitud__in=solicitud))

			# if id_empresa:
			# 	qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = FavorabilidadComprasSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save(solicitud_id=request.DATA['solicitud_id'],
													soporte=request.FILES['soporte'] if request.FILES.get('soporte') is not None else '')

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Favorabilidad_Compras',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = FavorabilidadComprasSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte,
													solicitud_id=request.DATA['solicitud_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Compras',id_manipulado=instance.id)
					logs_model.save()

					editarRequisito(request, 'compras', request.DATA['requisitos'], request.DATA['id'], 1)

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Favorabilidad_Compras',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para CFavorabilidadCompras

#Api rest para DFavorabilidadComprasRequisito
class FavorabilidadComprasRequisitoSerializer(serializers.HyperlinkedModelSerializer):

	requisito = RequisitoComprasSerializer(read_only=True)
	requisito_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = BRequisitoCompras.objects.all())

	favorabilidad = FavorabilidadComprasSerializer(read_only=True)
	favorabilidad_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = CFavorabilidadCompras.objects.all())

	class Meta:
		model = DFavorabilidadComprasRequisito
		fields=('id','requisito','requisito_id','favorabilidad','favorabilidad_id','estado')

class FavorabilidadComprasRequisitoViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=DFavorabilidadComprasRequisito
	queryset = model.objects.all()
	serializer_class = FavorabilidadComprasRequisitoSerializer
	nombre_modulo = 'Solicitud - FavorabilidadComprasRequisitoViewSet'

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
			queryset = super(FavorabilidadComprasRequisitoViewSet, self).get_queryset()

			dato = self.request.query_params.get('dato', None)
			estado = self.request.query_params.get('estado', None)
			requisito = self.request.query_params.get('id_requisito').split(',') if self.request.query_params.get('id_requisito') else None
			favorabilidad = self.request.query_params.get('id_favorabilidad').split(',') if self.request.query_params.get('id_favorabilidad') else None

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			# id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(requisito__nombre__icontains=dato)|Q(favorabilidad__observacion__icontains=dato))

			if estado:
				qset = qset &(Q(estado=estado))

			if requisito:
				qset = qset &(Q(requisito__in=requisito))

			if favorabilidad:
				qset = qset &(Q(favorabilidad__in=favorabilidad))

			# if id_empresa:
			# 	qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = FavorabilidadComprasRequisitoSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save(requisito_id=request.DATA['requisito_id'], favorabilidad_id=request.DATA['favorabilidad_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Favorabilidad_Compras_Requisito',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = FavorabilidadComprasRequisitoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(requisito_id=request.DATA['requisito_id'], favorabilidad_id=request.DATA['favorabilidad_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Compras_Requisito',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Favorabilidad_Compras_Requisito',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para DFavorabilidadComprasRequisito


#Api rest para BRequisitoTecnico
class RequisitoTecnicoSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = BRequisitoTecnico
		fields=('id','nombre')

class RequisitoTecnicoViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=BRequisitoTecnico
	queryset = model.objects.all()
	serializer_class = RequisitoTecnicoSerializer
	nombre_modulo = 'Solicitud - RequisitoTecnicoViewSet'

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
			queryset = super(RequisitoTecnicoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(nombre__icontains=dato))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = RequisitoTecnicoSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Requisito_Tecnico',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = RequisitoTecnicoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Requisito_Tecnico',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Requisito_Tecnico',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para BRequisitoTecnico

#Api rest para CFavorabilidadTecnica
class FavorabilidadTecnicaSerializer(serializers.HyperlinkedModelSerializer):

	solicitud = SolicitudSerializer(read_only=True)
	solicitud_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = ASolicitud.objects.all())

	class Meta:
		model = CFavorabilidadTecnica
		fields=('id','solicitud','solicitud_id','observacion','soporte')

class FavorabilidadTecnicaViewSet(viewsets.ModelViewSet):
	"""

	"""
	model = CFavorabilidadTecnica
	queryset = model.objects.all()
	serializer_class = FavorabilidadTecnicaSerializer
	nombre_modulo = 'Solicitud - FavorabilidadTecnicaViewSet'

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
			queryset = super(FavorabilidadTecnicaViewSet, self).get_queryset()

			dato = self.request.query_params.get('dato', None)
			solicitud = self.request.query_params.get('id_solicitud').split(',') if self.request.query_params.get('id_solicitud') else None

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			# id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(observacion__icontains=dato))

			if solicitud:
				qset = qset &(Q(solicitud__in=solicitud))

			# if id_empresa:
			# 	qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = FavorabilidadTecnicaSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save(solicitud_id=request.DATA['solicitud_id'],
													soporte=request.FILES['soporte'] if request.FILES.get('soporte') is not None else '')

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Favorabilidad_Tecnica',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = FavorabilidadTecnicaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte,
													solicitud_id=request.DATA['solicitud_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Tecnica',id_manipulado=instance.id)
					logs_model.save()

					editarRequisito(request, 'tecnica', request.DATA['requisitos'], request.DATA['id'], 1)

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Favorabilidad_Tecnica',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para CFavorabilidadTecnica

#Api rest para DFavorabilidadTecnicaRequisito
class FavorabilidadTecnicaRequisitoSerializer(serializers.HyperlinkedModelSerializer):

	requisito = RequisitoTecnicoSerializer(read_only=True)
	requisito_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = BRequisitoTecnico.objects.all())

	favorabilidad = FavorabilidadTecnicaSerializer(read_only=True)
	favorabilidad_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = CFavorabilidadTecnica.objects.all())

	class Meta:
		model = DFavorabilidadTecnicaRequisito
		fields=('id','requisito','requisito_id','favorabilidad','favorabilidad_id','estado')

class FavorabilidadTecnicaRequisitoViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=DFavorabilidadTecnicaRequisito
	queryset = model.objects.all()
	serializer_class = FavorabilidadTecnicaRequisitoSerializer
	nombre_modulo = 'Solicitud - FavorabilidadTecnicaRequisitoViewSet'

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
			queryset = super(FavorabilidadTecnicaRequisitoViewSet, self).get_queryset()

			dato = self.request.query_params.get('dato', None)
			estado = self.request.query_params.get('estado', None)
			requisito = self.request.query_params.get('id_requisito').split(',') if self.request.query_params.get('id_requisito') else None
			favorabilidad = self.request.query_params.get('id_favorabilidad').split(',') if self.request.query_params.get('id_favorabilidad') else None

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			# id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(requisito__nombre__icontains=dato)|Q(favorabilidad__observacion__icontains=dato))

			if estado:
				qset = qset &(Q(estado=estado))

			if requisito:
				qset = qset &(Q(requisito__in=requisito))

			if favorabilidad:
				qset = qset &(Q(favorabilidad__in=favorabilidad))

			# if id_empresa:
			# 	qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = FavorabilidadTecnicaRequisitoSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save(requisito_id=request.DATA['requisito_id'], favorabilidad_id=request.DATA['favorabilidad_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Favorabilidad_Tecnica_Requisito',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = FavorabilidadTecnicaRequisitoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(requisito_id=request.DATA['requisito_id'], favorabilidad_id=request.DATA['favorabilidad_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Tecnica_Requisito',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Favorabilidad_Tecnica_Requisito',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para DFavorabilidadTecnicaRequisito


#Api rest para BRequisitoPoliza
class RequisitoPolizaSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = BRequisitoPoliza
		fields=('id','nombre')

class RequisitoPolizaViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=BRequisitoPoliza
	queryset = model.objects.all()
	serializer_class = RequisitoPolizaSerializer
	nombre_modulo = 'Solicitud - RequisitoPolizaViewSet'

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
			queryset = super(RequisitoPolizaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(nombre__icontains=dato))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = RequisitoPolizaSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Requisito_Poliza',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = RequisitoPolizaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Requisito_Poliza',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'Datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Requisito_Poliza',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para BRequisitoPoliza

#Api rest para CValidarPoliza
class ValidarPolizaSerializer(serializers.HyperlinkedModelSerializer):

	solicitud = SolicitudSerializer(read_only=True)
	solicitud_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = ASolicitud.objects.all())

	class Meta:
		model = CValidarPoliza
		fields=('id','solicitud','solicitud_id','soporte')

class ValidarPolizaViewSet(viewsets.ModelViewSet):
	"""

	"""
	model = CValidarPoliza
	queryset = model.objects.all()
	serializer_class = ValidarPolizaSerializer
	nombre_modulo = 'Solicitud - ValidarPolizaViewSet'

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
			queryset = super(ValidarPolizaViewSet, self).get_queryset()

			# dato = self.request.query_params.get('dato', None)
			solicitud = self.request.query_params.get('id_solicitud').split(',') if self.request.query_params.get('id_solicitud') else None
			# tipo = self.request.query_params.get('id_tipo').split(',') if self.request.query_params.get('id_tipo') else None

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			# id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			# if dato:
			# 	qset = qset &(Q(observacion__icontains=dato))

			if solicitud:
				qset = qset &(Q(solicitud__in=solicitud))

			# if tipo:
			# 	qset = qset &(Q(tipo__in=tipo))

			# if id_empresa:
			# 	qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = ValidarPolizaSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save(solicitud_id=request.DATA['solicitud_id'],
													soporte=request.FILES['soporte'] if request.FILES.get('soporte') is not None else '')

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Validar_Poliza',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = ValidarPolizaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte,
													solicitud_id=request.DATA['solicitud_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Validar_Poliza',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Validar_Poliza',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para CValidarPoliza

#Api rest para DPolizaTipo
class PolizaTipoSerializer(serializers.HyperlinkedModelSerializer):

	validar_poliza = SolicitudSerializer(read_only=True)
	validar_poliza_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = ASolicitud.objects.all())

	tipo = TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='poliza'))

	class Meta:
		model = DPolizaTipo
		fields=('id','validar_poliza','validar_poliza_id','tipo', 'tipo_id')

class PolizaTipoViewSet(viewsets.ModelViewSet):
	"""

	"""
	model = DPolizaTipo
	queryset = model.objects.all()
	serializer_class = PolizaTipoSerializer
	nombre_modulo = 'Solicitud - PolizaTipoViewSet'

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
			queryset = super(PolizaTipoViewSet, self).get_queryset()

			# dato = self.request.query_params.get('dato', None)
			validar_poliza = self.request.query_params.get('id_validar_poliza').split(',') if self.request.query_params.get('id_validar_poliza') else None
			tipo = self.request.query_params.get('id_tipo').split(',') if self.request.query_params.get('id_tipo') else None

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			# id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			# if dato:
			# 	qset = qset &(Q(observacion__icontains=dato))

			if validar_poliza:
				qset = qset &(Q(validar_poliza__in=validar_poliza))

			if tipo:
				qset = qset &(Q(tipo__in=tipo))

			# if id_empresa:
			# 	qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = PolizaTipoSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save(validar_poliza_id=request.DATA['validar_poliza_id'], tipo_id=request.DATA['tipo_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Poliza_Tipo',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = PolizaTipoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(validar_poliza_id=request.DATA['validar_poliza_id'], tipo_id=request.DATA['tipo_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Poliza_Tipo',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Poliza_Tipo',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para DPolizaTipo

#Api rest para EPolizaTipoRequisito
class PolizaTipoRequisitoSerializer(serializers.HyperlinkedModelSerializer):

	requisito = RequisitoPolizaSerializer(read_only=True)
	requisito_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = BRequisitoPoliza.objects.all())

	poliza_tipo = PolizaTipoSerializer(read_only=True)
	poliza_tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = DPolizaTipo.objects.all())

	class Meta:
		model = EPolizaTipoRequisito
		fields=('id','requisito','requisito_id','poliza_tipo','poliza_tipo_id')

class PolizaTipoRequisitoViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=EPolizaTipoRequisito
	queryset = model.objects.all()
	serializer_class = PolizaTipoRequisitoSerializer
	nombre_modulo = 'Solicitud - PolizaTipoRequisitoViewSet'

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
			queryset = super(PolizaTipoRequisitoViewSet, self).get_queryset()

			dato = self.request.query_params.get('dato', None)
			estado = self.request.query_params.get('estado', None)
			requisito = self.request.query_params.get('id_requisito').split(',') if self.request.query_params.get('id_requisito') else None
			poliza_tipo = self.request.query_params.get('id_poliza_tipo').split(',') if self.request.query_params.get('id_poliza_tipo') else None

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			# id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(requisito__nombre__icontains=dato))

			if estado:
				qset = qset &(Q(estado=estado))

			if requisito:
				qset = qset &(Q(requisito__in=requisito))

			# if validar_poliza:
			# 	qset = qset &(Q(favorabilidad__in=validar_poliza))

			if poliza_tipo:
				qset = qset &(Q(poliza_tipo__in=poliza_tipo))

			# if id_empresa:
			# 	qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-id')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

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
				serializer = PolizaTipoRequisitoSerializer(data=request.DATA,context={'request': request})
				# print serializer

				if serializer.is_valid():

					serializer.save(requisito_id=request.DATA['requisito_id'],
													poliza_tipo_id=request.DATA['poliza_tipo_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Poliza_Tipo_Requisito',id_manipulado=serializer.data['id'])
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
				# #print request.DATA
				serializer = PolizaTipoRequisitoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():

					serializer.save(requisito_id=request.DATA['requisito_id'],
													poliza_tipo_id=request.DATA['poliza_tipo_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Poliza_Tipo_Requisito',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# self.perform_destroy(instance)
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.Poliza_Tipo_Requisito',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para EPolizaTipoRequisito


@login_required
def solicitud(request):
	# tipo_c = tipoC()
	# querysetTipos=Tipo.objects.filter(app='contrato')
	# id_empresa = request.user.usuario.empresa.id
	# querysetMContrato=Contrato.objects.filter(empresacontrato__empresa=id_empresa, empresacontrato__participa=1, tipo_contrato=tipo_c.m_contrato, activo=1)
	return render(request, 'solicitud/solicitud.html',{'aprobada':estadoSolicitud.aprobada,'est_enEstudio':estadoSolicitud.enEstudio,'model':'asolicitud','app':'solicitud'})


def createFavorabilidadPoliza(request, id_solicitud):
	nombre_modulo = 'Solicitud - createFavorabilidadPoliza'
	sid = transaction.savepoint()
	try:

		# Inicio Conceptos Juridicos
		model_fj = CFavorabilidadJuridica(solicitud_id=id_solicitud)
		model_fj.save()
		# print "id nueva favorabilidad juridica:"+str(model_fj.id)

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Favorabilidad_Juridica',id_manipulado=model_fj.id)
		logs_model.save()

		insert_list = []
		model_rj = BRequisitoJuridico.objects.all()

		for i in model_rj:
			insert_list.append(DFavorabilidadJuridicaRequisito(favorabilidad_id=model_fj.id, requisito_id=i.id))

		DFavorabilidadJuridicaRequisito.objects.bulk_create(insert_list)

		insert_list_log = []
		model_fjr = DFavorabilidadJuridicaRequisito.objects.filter(favorabilidad_id=model_fj.id)

		for i in model_fjr:
			insert_list_log.append(Logs(usuario_id=request.user.usuario.id
															,accion=Acciones.accion_crear
															,nombre_modelo='solicitud.Favorabilidad_Juridica_Requisito'
															,id_manipulado=i.id))
		Logs.objects.bulk_create(insert_list_log)
		# Fin de Conceptos Juridicos

		# Inicio Conceptos Compras
		model_fc = CFavorabilidadCompras(solicitud_id=id_solicitud)
		model_fc.save()
		# print "id nueva favorabilidad Compras:"+str(model_fc.id)

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Favorabilidad_Compras',id_manipulado=model_fc.id)
		logs_model.save()

		insert_list = []
		model_rc = BRequisitoCompras.objects.all()

		for i in model_rc:
			insert_list.append(DFavorabilidadComprasRequisito(favorabilidad_id=model_fc.id, requisito_id=i.id))

		DFavorabilidadComprasRequisito.objects.bulk_create(insert_list)

		insert_list_log = []
		model_fcr = DFavorabilidadComprasRequisito.objects.filter(favorabilidad_id=model_fc.id)

		for i in model_fcr:
			insert_list_log.append(Logs(usuario_id=request.user.usuario.id
															,accion=Acciones.accion_crear
															,nombre_modelo='solicitud.Favorabilidad_Compras_Requisito'
															,id_manipulado=i.id))
		Logs.objects.bulk_create(insert_list_log)
		# Fin de Conceptos Compras

		# Inicio Conceptos Tecnica
		model_ft = CFavorabilidadTecnica(solicitud_id=id_solicitud)
		model_ft.save()
		# print "id nueva favorabilidad Tecnica:"+str(model_ft.id)

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Favorabilidad_Tecnica',id_manipulado=model_ft.id)
		logs_model.save()

		insert_list = []
		model_rt = BRequisitoTecnico.objects.all()

		for i in model_rt:
			insert_list.append(DFavorabilidadTecnicaRequisito(favorabilidad_id=model_ft.id, requisito_id=i.id))

		DFavorabilidadTecnicaRequisito.objects.bulk_create(insert_list)

		insert_list_log = []
		model_ftr = DFavorabilidadTecnicaRequisito.objects.filter(favorabilidad_id=model_ft.id)

		for i in model_ftr:
			insert_list_log.append(Logs(usuario_id=request.user.usuario.id
															,accion=Acciones.accion_crear
															,nombre_modelo='solicitud.Favorabilidad_Tecnica_Requisito'
															,id_manipulado=i.id))
		Logs.objects.bulk_create(insert_list_log)
		# Fin de Conceptos Tecnica
		# #################################################################
		# Inicio Conceptos Poliza
		insert_list = []
		model_t = Tipo.objects.filter(app='poliza')

		# SE CREA LA SOLICITU POLIZA BRequisitoPoliza
		model_vp = CValidarPoliza(solicitud_id=id_solicitud)
		model_vp.save()
		# print "id nueva favorabilidad Poliza:"+str(model_vp.id)

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Validar_Poliza',id_manipulado=model_vp.id)
		logs_model.save()

		for i in model_t:
			insert_list.append(DPolizaTipo(validar_poliza_id=model_vp.id, tipo_id=i.id))

		DPolizaTipo.objects.bulk_create(insert_list)
		model_pt = DPolizaTipo.objects.filter(validar_poliza_id=model_vp.id)
		model_rp = BRequisitoPoliza.objects.all()

		insert_list = []
		for i in model_pt:
			for j in model_rp:
				insert_list.append(EPolizaTipoRequisito(requisito_id=j.id, poliza_tipo_id=i.id))

		EPolizaTipoRequisito.objects.bulk_create(insert_list)

		# model_vp = CValidarPoliza(solicitud_id=id_solicitud)
		# model_vp.save()
		# print "id nueva favorabilidad Poliza:"+str(model_vp.id)

		# logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='solicitud.Validar_Poliza',id_manipulado=model_vp.id)
		# logs_model.save()

		# insert_list = []
		# model_rt = BRequisitoTecnico.objects.all()

		# for i in model_rt:
		# 	insert_list.append(DFavorabilidadTecnicaRequisito(favorabilidad_id=model_vp.id, requisito_id=i.id))

		# DFavorabilidadTecnicaRequisito.objects.bulk_create(insert_list)

		insert_list_log = []
		model = DPolizaTipo.objects.filter(validar_poliza_id=model_vp.id)

		for i in model:
			insert_list_log.append(Logs(usuario_id=request.user.usuario.id
															,accion=Acciones.accion_crear
															,nombre_modelo='solicitud.Poliza_Tipo'
															,id_manipulado=i.id))
		Logs.objects.bulk_create(insert_list_log)

		insert_list_log = []
		model2 = EPolizaTipoRequisito.objects.filter(poliza_tipo__in=model)

		for i in model2:
			insert_list_log.append(Logs(usuario_id=request.user.usuario.id
															,accion=Acciones.accion_crear
															,nombre_modelo='solicitud.Poliza_Tipo_Requisito'
															,id_manipulado=i.id))
		Logs.objects.bulk_create(insert_list_log)
		# Fin de Conceptos Poliza

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Guardar cambios de estadi requisito
def editarRequisito(request, argument, requisitos_id, id_favorabilidad, estado):
	# if request.method == 'POST':
	nombre_modulo = 'Solicitud - editarRequisito'
	try:
		# print requisitos_id

		myList = requisitos_id.split(',')

		if argument == 'juridica':
			model_fjr = DFavorabilidadJuridicaRequisito.objects.filter(favorabilidad_id=id_favorabilidad).exclude(id__in=myList)

			for model in model_fjr:
				model_requisitos = DFavorabilidadJuridicaRequisito.objects.get(pk=model.id)
				model_requisitos.estado = 0
				model_requisitos.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Juridica_Requisito',id_manipulado=model_requisitos.id)
				logs_model.save()

			for requisitos in myList:
				if requisitos:

					model_requisitos = DFavorabilidadJuridicaRequisito.objects.get(pk=requisitos)
					model_requisitos.estado = estado
					model_requisitos.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Juridica_Requisito',id_manipulado=model_requisitos.id)
					logs_model.save()

		if argument == 'compras':
			model_fjr = DFavorabilidadComprasRequisito.objects.filter(favorabilidad_id=id_favorabilidad).exclude(id__in=myList)

			for model in model_fjr:
				model_requisitos = DFavorabilidadComprasRequisito.objects.get(pk=model.id)
				model_requisitos.estado = 0
				model_requisitos.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Compras_Requisito',id_manipulado=model_requisitos.id)
				logs_model.save()

			for requisitos in myList:
				if requisitos:

					model_requisitos = DFavorabilidadComprasRequisito.objects.get(pk=requisitos)
					model_requisitos.estado = estado
					model_requisitos.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Compras_Requisito',id_manipulado=model_requisitos.id)
					logs_model.save()

		if argument == 'tecnica':
			model_fjr = DFavorabilidadTecnicaRequisito.objects.filter(favorabilidad_id=id_favorabilidad).exclude(id__in=myList)

			for model in model_fjr:
				model_requisitos = DFavorabilidadTecnicaRequisito.objects.get(pk=model.id)
				model_requisitos.estado = 0
				model_requisitos.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Tecnica_Requisito',id_manipulado=model_requisitos.id)
				logs_model.save()

			for requisitos in myList:
				if requisitos:

					model_requisitos = DFavorabilidadTecnicaRequisito.objects.get(pk=requisitos)
					model_requisitos.estado = estado
					model_requisitos.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Favorabilidad_Tecnica_Requisito',id_manipulado=model_requisitos.id)
					logs_model.save()
		# return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Editar los requisitos por tipo de poliza
@transaction.atomic
def updateRequisitosPoliza(request):
	if request.method == 'POST':
		nombre_modulo = 'Solicitud - updateRequisitosPoliza'
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']
			id_poliza_tipo = respuesta['id_poliza_tipo']
			# print "id_poliza_tipo:"+str(id_poliza_tipo)

			model_ptr = EPolizaTipoRequisito.objects.filter(poliza_tipo_id=id_poliza_tipo).exclude(id__in=myList)

			for model in model_ptr:
				model_requisitos = EPolizaTipoRequisito.objects.get(pk=model.id)
				model_requisitos.estado = 0
				model_requisitos.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Poliza_Tipo_Requisito',id_manipulado=model_requisitos.id)
				logs_model.save()

			for requisitos in myList:
				if requisitos:

					model_requisitos = EPolizaTipoRequisito.objects.get(pk=requisitos)
					model_requisitos.estado = 1
					model_requisitos.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='solicitud.Poliza_Tipo_Requisito',id_manipulado=model_requisitos.id)
					logs_model.save()

			# transaction.commit()
			return JsonResponse({'message':'El registro ha sido actualizado exitosamente','success':'ok','data': ''})
			transaction.savepoint_commit(sid)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Eliminar Solicitud con una lista
@transaction.atomic
def destroySolicitud(request):
	if request.method == 'POST':
		nombre_modulo = 'Solicitud - destroySolicitud'
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']

			for item in myList:
				# print item['id']

				model_fj = CFavorabilidadJuridica.objects.filter(solicitud_id = item['id']).first()
				if model_fj:
					model_fjr = DFavorabilidadJuridicaRequisito.objects.filter(favorabilidad_id=model_fj.id)
					model_fjr.delete()
					model_fj.delete()

				model_fc = CFavorabilidadCompras.objects.filter(solicitud_id = item['id']).first()
				if model_fc:
					model_fcr = DFavorabilidadComprasRequisito.objects.filter(favorabilidad_id=model_fc.id)
					model_fcr.delete()
					model_fc.delete()

				model_ft = CFavorabilidadTecnica.objects.filter(solicitud_id = item['id']).first()
				if model_ft:
					model_ftr = DFavorabilidadTecnicaRequisito.objects.filter(favorabilidad_id=model_ft.id)
					model_ftr.delete()
					model_ft.delete()

				model_vp = CValidarPoliza.objects.filter(solicitud_id = item['id']).first()
				if model_vp:
					model_pt = DPolizaTipo.objects.filter(validar_poliza_id=model_vp.id)

					for model in model_pt:
						model_ptr = EPolizaTipoRequisito.objects.filter(poliza_tipo_id=model.id)
						model_ptr.delete()

					model_pt.delete()
					model_vp.delete()

				model_solicitud = ASolicitud.objects.get(pk=item['id'])
				model_solicitud.delete()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='solicitud.solicitud',id_manipulado=item['id'])
				logs_model.save()

			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
			transaction.savepoint_commit(sid)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



