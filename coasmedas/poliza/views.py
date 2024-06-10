from django.db import transaction, connection
from datetime import *
from django.shortcuts import render,redirect
#,render_to_response
from django.urls import reverse
from .models import Aseguradora, Poliza, VigenciaPoliza, ZBeneficiorio
from rest_framework import viewsets, serializers

from django.db.models import Q,Sum,Prefetch,Max
from django.template import RequestContext
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
import xlsxwriter
import json
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from rest_framework.parsers import MultiPartParser, FormParser
from empresa.views import EmpresaSerializer
from empresa.models import Empresa
from usuario.views import PersonaSerializer
from tipo.views import TipoSerializer
from tipo.models import Tipo
from estado.views import EstadoSerializer
from estado.models import Estado
from contrato.models import Contrato, VigenciaContrato
from logs.models import Logs,Acciones
from django.conf import settings
import boto 
from boto.s3.key import Key
import os
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.auth.decorators import login_required
from giros.models import DEncabezadoGiro
from .enumeration import TipoDocumento, TipoActa
from coasmedas.functions import functions
from contrato.enumeration import tipoV

# from django import template
# import locale
# locale.setlocale(locale.LC_ALL, 'es_CO')
# register = template.Library()

# @register.filter()
# def currency(value):
#     return locale.currency(value, grouping=True)

class TipoLiteSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = Tipo
		fields=( 'id','nombre')

class AseguradoraSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Aseguradora
		fields=('id','nombre',)

class AseguradoraViewSet(viewsets.ModelViewSet):
	model=Aseguradora
	queryset = model.objects.all()
	serializer_class = AseguradoraSerializer	
	paginate_by = 10
	nombre_modulo = 'poliza'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(AseguradoraViewSet, self).get_queryset()
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
				serializer = AseguradoraSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='poliza.aseguradora',id_manipulado=serializer.data['id'])
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
				serializer = AseguradoraSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='poliza.aseguradora',id_manipulado=instance.id)
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
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='poliza.aseguradora',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)


#poliza 

class BeneficiarioReadOnlySerializer(serializers.HyperlinkedModelSerializer):	
	class Meta:
		model = ZBeneficiorio
		fields=('id','nombre')

class VigenciaPolizaReadOnlySerializer(serializers.HyperlinkedModelSerializer):
	aseguradora = AseguradoraSerializer(read_only=True)
	aseguradora_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Aseguradora.objects.all())
	beneficiarios = BeneficiarioReadOnlySerializer(many=True)
	tipo_acta = TipoSerializer(read_only=True)
	tipo_acta_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Tipo.objects.filter(app='poliza_tipo_acta'))
	tipo_documento = TipoSerializer(read_only=True)
	tipo_documento_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Tipo.objects.filter(app='poliza_tipo_documento'))
	class Meta:
		model = VigenciaPoliza
		fields=('id', 'fecha_inicio', 'fecha_final', 'valor', 
				'observacion', 'soporte', 'amparo', 'tomador', 
				'numero', 'reemplaza', 'aseguradora', 'aseguradora_id','beneficiarios', 'documento_id', 
				'tipo_acta', 'tipo_acta_id', 'tipo_documento', 'tipo_documento_id', 'numero_certificado')

class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):
	contratante = EmpresaSerializer(read_only=True)
	contratante_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())
	contratista = EmpresaSerializer(read_only=True)
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())
	tipo_contrato = TipoLiteSerializer(read_only=True)
	tipo_contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='Contrato'))

	class Meta:
		model = Contrato
		fields=('id','nombre','numero', 'tipo_contrato', 'tipo_contrato_id', 'contratante', 'contratante_id', 'contratista', 'contratista_id')

class PolizaLiteSerializer(serializers.HyperlinkedModelSerializer):
	contrato = ContratoLiteSerializer(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Contrato.objects.all())
	tipo=TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Tipo.objects.filter(app='poliza'))
	class Meta:
		model = Poliza
		fields=('id', 'contrato', 'contrato_id', 'tipo', 'tipo_id', 'fecha_inicio','fecha_final','valor',)

class PolizaLite2Serializer(serializers.HyperlinkedModelSerializer):	
	tipo=TipoSerializer(read_only=True)	
	class Meta:
		model = Poliza
		fields=('id', 'tipo',)

class PolizaSerializer(serializers.HyperlinkedModelSerializer):
	contrato = ContratoLiteSerializer(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Contrato.objects.all())
	tipo=TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Tipo.objects.filter(app='poliza'))
	# estado = EstadoSerializer(read_only=True)
	# estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='poliza'))
	vigencias = VigenciaPolizaReadOnlySerializer(many=True,read_only=True)
	class Meta:
		model = Poliza
		fields=('id', 'contrato', 'contrato_id', 'tipo', 'tipo_id', 'fecha_inicio','fecha_final','valor','vigencias',)

class PolizaViewSet(viewsets.ModelViewSet):
	model=Poliza
	queryset = model.objects.all()
	serializer_class = PolizaSerializer	
	paginate_by = 10
	nombre_modulo = 'poliza'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(PolizaViewSet, self).get_queryset()
			paginacion = self.request.query_params.get('sin_paginacion', None)
			dato = self.request.query_params.get('dato', None)
			contrato_id = self.request.query_params.get('contrato_id', None)
			tipo_id = self.request.query_params.get('tipo_id', None)
			lite = self.request.query_params.get('lite', None)
			qset=~Q(id=0)
			if dato:
				qset= qset & (Q(contrato__nombre__icontains=dato))	
			if contrato_id and int(contrato_id)>0:
				if qset:
					qset= qset & (Q(contrato__id=contrato_id))
				else:	
					qset=(Q(contrato__id=contrato_id))
			if tipo_id and int(tipo_id)>0:
				if qset:
					qset= qset & (Q(tipo__id=tipo_id))
				else:	
					qset=(Q(tipo__id=tipo_id))
						
			queryset = self.model.objects.filter(qset)	

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite is not None:
						serializer = PolizaLiteSerializer(page, many=True, context={'request': request})	
					else:	
						serializer = self.get_serializer(page, many=True)						
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})
			else:
				if lite is not None:
					serializer = PolizaLiteSerializer(queryset, many=True, context={'request': request})
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
				serializer = PolizaSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'],
									tipo_id=request.DATA['tipo_id'],
									estado_id=28)# estado vigente

					vigencia=VigenciaPoliza(fecha_inicio=request.DATA['fecha_inicio'],fecha_final=request.DATA['fecha_final'], \
									valor=request.DATA['valor'],numero=request.DATA['numero'],aseguradora_id=request.DATA['aseguradora_id'], \
									poliza_id=serializer.data['id'], soporte=request.FILES['soporte'] if request.FILES.get('soporte') is not None else '',
									documento_id=int(request.DATA['documento_id']) if request.DATA['documento_id'] is not None and request.DATA['documento_id']!='' else None, 
									tipo_acta_id=int(request.DATA['tipo_acta_id']) if request.DATA['tipo_acta_id'] is not None and request.DATA['tipo_acta_id']!='' else None,
									tipo_documento_id=int(request.DATA['tipo_documento_id']) if request.DATA['tipo_documento_id'] is not None and request.DATA['tipo_documento_id'] != '' else None,
									numero_certificado=request.DATA['numero_certificado'])
					vigencia.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='poliza.poliza',id_manipulado=serializer.data['id'])
					logs_model.save()
					beneficiarios = json.loads(request.DATA['beneficiarios'])
					for b in beneficiarios:
						beneficiario=ZBeneficiorio(vigencia_poliza_id=vigencia.id,nombre=b['nombre'])
						beneficiario.save()
					
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					# print(serializer.errors)
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
				serializer = PolizaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'], tipo_id=request.DATA['tipo_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='poliza.poliza',id_manipulado=instance.id)
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
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='poliza.poliza',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

#fin poliza
 
#VigenciaPoliza

class VigenciaPolizaSerializer(serializers.HyperlinkedModelSerializer):
	aseguradora = AseguradoraSerializer(read_only=True)
	aseguradora_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Aseguradora.objects.all())		
	poliza = PolizaSerializer(read_only=True)
	poliza_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Poliza.objects.all())		
	beneficiarios=BeneficiarioReadOnlySerializer(many=True)
	tipo_acta = TipoSerializer(read_only=True)
	tipo_acta_id = serializers.PrimaryKeyRelatedField(queryset = Tipo.objects.filter(app='poliza_tipo_acta'), allow_null=True)
	tipo_documento = TipoSerializer(read_only=True)
	tipo_documento_id = serializers.PrimaryKeyRelatedField(queryset = Tipo.objects.filter(app='poliza_tipo_documento'), allow_null=True)
	class Meta:
		model = VigenciaPoliza
		fields=('id', 'fecha_inicio', 'fecha_final', 'valor', 
				'observacion', 'soporte', 'amparo', 'tomador', 
				'numero', 'reemplaza', 'aseguradora', 'aseguradora_id', 
				'poliza', 'poliza_id','beneficiarios', 'documento_id', 
				'tipo_acta', 'tipo_acta_id', 'tipo_documento', 'tipo_documento_id', 'numero_certificado')

class VigenciaPolizaLiteSerializer(serializers.HyperlinkedModelSerializer):
	poliza = PolizaLite2Serializer(read_only=True)
	class Meta:
		model = VigenciaPoliza
		fields=('id', 'fecha_inicio', 'fecha_final', 'valor', 
				'observacion', 'soporte', 'amparo', 'tomador', 'numero', 'reemplaza', 'poliza')		

class VigenciaPolizaGuardarSerializer(serializers.HyperlinkedModelSerializer):
	aseguradora = AseguradoraSerializer(read_only=True)
	aseguradora_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Aseguradora.objects.all())		
	poliza = PolizaSerializer(read_only=True)
	poliza_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Poliza.objects.all())
	tipo_acta = TipoSerializer(read_only=True)
	tipo_acta_id = serializers.PrimaryKeyRelatedField(queryset = Tipo.objects.filter(Q(app='poliza_tipo_documento') | Q(app='poliza_tipo_acta')), allow_null=True)
	tipo_documento = TipoSerializer(read_only=True)
	tipo_documento_id = serializers.PrimaryKeyRelatedField(queryset = Tipo.objects.filter(Q(app='poliza_tipo_documento') | Q(app='poliza_tipo_acta')), allow_null=True)			
	class Meta:
		model = VigenciaPoliza
		fields=('id', 'fecha_inicio', 'fecha_final', 'valor', 
				'observacion', 'amparo', 'tomador', 
				'numero', 'reemplaza', 'aseguradora', 'aseguradora_id', 'poliza', 'poliza_id',
				'documento_id', 'tipo_acta', 'tipo_acta_id', 'tipo_documento', 'tipo_documento_id', 'numero_certificado')		


class VigenciaPolizaViewSet(viewsets.ModelViewSet):
	model = VigenciaPoliza
	queryset = model.objects.all()
	serializer_class = VigenciaPolizaSerializer	
	paginate_by = 10
	nombre_modulo = 'poliza'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(VigenciaPolizaViewSet, self).get_queryset()
			paginacion = self.request.query_params.get('sin_paginacion', None)
			dato = self.request.query_params.get('dato', None)
			poliza_id = self.request.query_params.get('poliza_id', None)
			contrato_id = self.request.query_params.get('contrato_id', None)
			fecha = self.request.query_params.get('fecha', None)
			id_documento = self.request.query_params.get('id_documento', None)
			tipo_documento = self.request.query_params.get('tipo_documento', None)
			lite = self.request.query_params.get('lite', None)
			qset = (~Q(id=0))
			if dato:
				qset=qset & (Q(poliza__contrato__nombre__icontains=dato))			
				# queryset = self.model.objects.filter(qset)
			if poliza_id:
				qset=qset & (Q(poliza__id=poliza_id))			
				# queryset = self.model.objects.filter(qset)
			if contrato_id:
				qset=qset & (Q(poliza__contrato__id=contrato_id))
				# queryset = self.model.objects.filter(qset)
			if fecha:
				qset=qset & (Q(fecha_final__lt=fecha))
					# queryset = self.model.objects.filter(qset).annotate(max_fecha_final=Max('fecha_final')).order_by()

			if id_documento:
				qset=qset & (Q(documento_id=id_documento))
				# queryset = self.model.objects.filter(qset)
			if tipo_documento and tipo_documento == 'vigencia':
				qset=qset & (Q(tipo_documento__id__in=[86, 88, 89, 90, 100]))

			if tipo_documento and tipo_documento == 'giros':		
				qset=qset & (Q(tipo_documento__id__in=[87,]))

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
				if lite:
					serializer = VigenciaPolizaLiteSerializer(queryset,many=True)
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
				serializer = VigenciaPolizaGuardarSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					enTipoActa = TipoActa()
					serializer.save(poliza_id=request.DATA['poliza_id'], 
									aseguradora_id=request.DATA['aseguradora_id'],
									tipo_acta_id = enTipoActa.Ninguno,# request.DATA.get('tipo_acta_id', None),
									tipo_documento_id = request.DATA.get('tipo_documento_id', None),
									soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else '')
					
					beneficiarios=json.loads(request.DATA['beneficiarios'])					
					for item in beneficiarios:
						beneficiario=ZBeneficiorio(nombre=item['nombre'],vigencia_poliza_id=serializer.data['id'])
						beneficiario.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='poliza.vigencia_poliza',id_manipulado=serializer.data['id'])
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
				serializer = VigenciaPolizaGuardarSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					enTipoActa = TipoActa()
					serializer.save(
						poliza_id=instance.poliza_id, 
						aseguradora_id=request.DATA['aseguradora_id'],
						tipo_acta_id = enTipoActa.Ninguno,
						tipo_documento_id = request.DATA.get('tipo_documento_id', None),
						soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte)

					ZBeneficiorio.objects.filter(vigencia_poliza__id=instance.id).delete()

					beneficiarios=json.loads(request.DATA['beneficiarios'])					
					for item in beneficiarios:																
						beneficiario=ZBeneficiorio(nombre=item['nombre'],vigencia_poliza_id=serializer.data['id'])
						beneficiario.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='poliza.vigencia_poliza',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					# print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:				
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic				
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':
			sid = transaction.savepoint()
			try:
				instance = self.get_object()
				self.perform_destroy(instance)
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='poliza.poliza',id_manipulado=instance.id)
				logs_model.save()
				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
			except Exception as e:				
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 
#fin VigenciaPoliza

#beneficiarios

class BeneficiarioSerializer(serializers.HyperlinkedModelSerializer):
	vigencia_poliza=VigenciaPolizaSerializer(read_only=True)
	vigencia_poliza_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset = VigenciaPoliza.objects.all())		
	class Meta:
		model = ZBeneficiorio
		fields=('id','nombre','vigencia_poliza_d','vigencia_poliza')

class BeneficiarioViewSet(viewsets.ModelViewSet):
	model=ZBeneficiorio
	queryset = model.objects.all()
	serializer_class = BeneficiarioSerializer	
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
			queryset = super(BeneficiarioViewSet, self).get_queryset()
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
				serializer = BeneficiarioSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='poliza.aseguradora',id_manipulado=serializer.data['id'])
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
				serializer = BeneficiarioSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='poliza.aseguradora',id_manipulado=instance.id)
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
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='poliza.aseguradora',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)


#fin beneficiario

@login_required
def poliza(request, contrato_id=0):
	qsTipos=Tipo.objects.filter(app='poliza')
	qsAseguradoras=Aseguradora.objects.all()
	qsContratos=Contrato.objects.all()	
	qsTiposContrato=Tipo.objects.filter(app='contrato')
	qsBeneficiarios=ZBeneficiorio.objects.values('nombre').distinct()

	# qsTipoDocumento=Tipo.objects.filter(app='poliza_tipo_documento')
	# qsTipoActa=Tipo.objects.filter(app='poliza_tipo_acta').order_by('codigo')
	
	# enTipoDocumento = TipoDocumento()
	# enTipoActa = TipoActa()

	qsTipoDocumento=Tipo.objects.filter(Q(app='poliza_tipo_documento') | Q(app='poliza_tipo_acta')).order_by('codigo')
	# qsTipoActa=Tipo.objects.filter(app='poliza_tipo_acta').order_by('codigo')		
	enTipoDocumento = TipoDocumento()
	enTipoActa = TipoActa()
	enTipoVigencia = tipoV()

	qsContrato=None
	qsGiros = None
	qsVigencias = None

	if contrato_id and int(contrato_id)>0:
		qsContrato=Contrato.objects.filter(id=contrato_id).first()
		request.session['viene_contrato_id']=contrato_id
		qsGiros=DEncabezadoGiro.objects.filter(contrato__id=contrato_id)
		qsVigencias=VigenciaContrato.objects.filter(contrato__id=contrato_id)
	else:
		request.session['viene_contrato_id']=''	
	contrato_id = contrato_id if contrato_id is not None else 0	
	return render(request, 'poliza.html',
		{'contrato_id':contrato_id,'contrato':qsContrato,'tipos':qsTipos,'aseguradoras':qsAseguradoras,'contratos':qsContratos,		
		'tipos_contrato':qsTiposContrato,'beneficiarios':qsBeneficiarios,'model':'poliza','app':'poliza',
		'tipoDocumento':qsTipoDocumento, 'giros':qsGiros, 
		'enTipoVigencia': enTipoVigencia,
		'vigencias':qsVigencias, 'enTipoDocumento':enTipoDocumento, 'enTipoActa':enTipoActa})

@login_required
def poliza_contrato(request):
	qsTipos=Tipo.objects.filter(app='poliza')
	qsTiposContrato=Tipo.objects.filter(app='contrato')	
	return render(request, 'poliza_contrato.html',
		{'tipos':qsTipos, 'tipos_contrato':qsTiposContrato,'model':'poliza','app':'poliza'},
		)


@login_required
def vigencia_poliza(request, poliza_id):	
	qsAseguradoras=Aseguradora.objects.all()	
	qsPoliza=Poliza.objects.get(pk=poliza_id)
	qsTipoDocumento=Tipo.objects.filter(Q(app='poliza_tipo_documento') | Q(app='poliza_tipo_acta')).order_by('codigo')
	# qsTipoActa=Tipo.objects.filter(app='poliza_tipo_acta').order_by('codigo')
	qsGiros=DEncabezadoGiro.objects.filter(contrato__id=qsPoliza.contrato.id)
	qsVigencias=VigenciaContrato.objects.filter(contrato__id=qsPoliza.contrato.id)	
	enTipoDocumento = TipoDocumento()
	enTipoActa = TipoActa()
	enTipoVigencia = tipoV()
	qsBeneficiarios=ZBeneficiorio.objects.values('nombre').distinct()
	return render(request, 'vigencia_poliza.html',
		{'poliza':qsPoliza,'aseguradoras':qsAseguradoras,
		'contrato_id':request.session['viene_contrato_id'],
		'model':'vigenciapoliza','app':'poliza',
		'tipoDocumento':qsTipoDocumento, 'giros':qsGiros, 
		'vigencias':qsVigencias, 'enTipoDocumento':enTipoDocumento, 
		'enTipoActa':enTipoActa,
		'enTipoVigencia': enTipoVigencia,
		'beneficiarios':qsBeneficiarios},
		)

@login_required
def asociar_soporte(request, vigencia_id):		
	qsVigencia=VigenciaPoliza.objects.get(pk=vigencia_id)
	return render(request, 'asociar_soporte.html',
		{'vigencia':qsVigencia,
		'contrato_id':request.session['viene_contrato_id'],
		'model':'vigencia_poliza','app':'poliza'},
		)

@login_required
@transaction.atomic
def guardar_asociacion_soporte(request):
	sid = transaction.savepoint()
	try:

		resultado=json.loads(request.POST['_content'])
		vig=VigenciaPoliza.objects.get(pk=resultado['vigencia_id'])

		for id in resultado['lista']:
			v=VigenciaPoliza.objects.get(pk=id)
			v.soporte=vig.soporte
			v.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro fue actualizado satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:
		transaction.savepoint_rollback(sid)
		functions.toLog(e,self.nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	


@login_required
@transaction.atomic
def eliminar_vigencias(request):
	sid = transaction.savepoint()
	try:
		resultado=json.loads(request.POST['_content'])
		for id in  resultado['lista']:
			ZBeneficiorio.objects.filter(vigencia_poliza__id=id).delete()			
			vigencia=VigenciaPoliza.objects.get(pk=id)
			vigencia.delete()
		
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El(Los) registro(s) fueron eliminado satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:
		transaction.savepoint_rollback(sid)
		functions.toLog(e,self.nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

@login_required
@transaction.atomic
def eliminar_polizas(request):
	sid = transaction.savepoint()
	try:
		resultado=json.loads(request.POST['_content'])

		for id in resultado['lista']:
			poliza=Poliza.objects.get(pk=id)
			if poliza.vigencias():
				for vigencia in poliza.vigencias():
					ZBeneficiorio.objects.filter(vigencia_poliza__id=vigencia.id).delete()				
					vigencia.delete()
			poliza.delete()		
		
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El(Los) registro(s) fueron eliminado satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:
		transaction.savepoint_rollback(sid)
		functions.toLog(e,self.nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	


def exportar_polizas(request):
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="Listado-de-polizas.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Polizas')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})

		dato = request.GET.get('dato', None)
		contrato_id = request.GET.get('contrato_id', None)
		tipo_id = request.GET.get('tipo_id', None)
		qset=None
		if dato:
			qset=(Q(contrato__nombre__icontains=dato))	
		if contrato_id and int(contrato_id)>0:
			if qset:
				qset= qset & (Q(contrato__id=contrato_id))
			else:	
				qset=(Q(contrato__id=contrato_id))
		if tipo_id and int(tipo_id)>0:
			if qset:
				qset= qset & (Q(tipo__id=tipo_id))
			else:	
				qset=(Q(tipo__id=tipo_id))

		polizas=None		
		if qset:				
			polizas = Poliza.objects.filter(qset)	
		else:
			polizas = Poliza.objects.all()	

		worksheet.write('A1', 'M Contrato', format1)
		worksheet.write('B1', 'N Contrato', format1)
		worksheet.write('C1', 'Contrato', format1)
		worksheet.write('D1', 'Tipo', format1)
		# worksheet.write('E1', 'Estado', format1)
		worksheet.write('E1', 'Fecha Inicio', format1)
		worksheet.write('F1', 'Fecha Fin', format1)
		worksheet.write('G1', 'Valor Total', format1)
		# worksheet.write('H1', 'N poliza', format1)

		worksheet.set_column('A:A', 30)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 30)
		worksheet.set_column('D:D', 25)
		worksheet.set_column('E:G', 15)

		row=1
		col=0

		for item in polizas:
			worksheet.write(row,col  ,item.contrato.mcontrato.nombre ,format2)
			worksheet.write(row,col+1,item.contrato.numero ,format2)
			worksheet.write(row,col+2,item.contrato.nombre ,format2)
			worksheet.write(row,col+3,item.tipo.nombre ,format2)
			# worksheet.write(row,col+4,item.tipo.nombre ,format2)
			worksheet.write(row,col+4,item.fecha_inicio() ,format_date)
			worksheet.write(row,col+5,item.fecha_final(),format_date)
			worksheet.write(row,col+6,item.valor(),format_money)
			# worksheet.write(row,col+7,item.vigencias.numero ,format2)
			row +=1		

		workbook.close()
		return response					

	except Exception as e:
		functions.toLog(e,self.nombre_modulo)

def exportar_vigencias(request):
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="Listado-de-polizas-vigencias.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Vigencias')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})

		dato = request.GET.get('dato', None)
		poliza_id = request.GET.get('poliza_id', None)
		contrato_id = request.GET.get('contrato_id', None)

		qset=None
		if dato:
			qset=(Q(poliza__contrato__nombre__icontains=dato))
		if poliza_id:
			qset=(Q(poliza__id=poliza_id))	
		if contrato_id:
			qset=(Q(contrato__id=contrato_id))			
			

		vigencias=None			
		if qset:
			vigencias = VigenciaPoliza.objects.filter(qset)	
		else:
			vigencias=VigenciaPoliza.objects.all()

		worksheet.write('A1', 'Numero', format1)		
		worksheet.write('B1', 'Fecha Inicio', format1)
		worksheet.write('C1', 'Fecha Fin', format1)
		worksheet.write('D1', 'Amparo', format1)
		worksheet.write('E1', 'Valor', format1)		
		worksheet.write('F1', 'Reemplaza', format1)		

		worksheet.set_column('A:A', 24)		
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 18)
		worksheet.set_column('E:E', 18)		
		worksheet.set_column('E:E', 18)			
		worksheet.set_column('F:F', 18)	

		row=1
		col=0

		for item in vigencias:
			worksheet.write(row,col  ,item.numero ,format2)			
			worksheet.write(row,col+1,item.fecha_inicio ,format_date)
			worksheet.write(row,col+2,item.fecha_final,format_date)
			worksheet.write(row,col+3,item.amparo,format2)					
			worksheet.write(row,col+4,item.valor,format_money)	
			worksheet.write(row,col+5,'Si' if item.reemplaza else 'No',format2)
			row +=1		

		workbook.close()
		return response	

	except Exception as e:
		functions.toLog(e,self.nombre_modulo)


@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			archivo = VigenciaPoliza.objects.get(pk=request.GET['id'])
			
			# filename = ""+str(archivo.soporte)+""
			# extension = filename[filename.rfind('.'):]
			# nombre = re.sub('[^A-Za-z0-9 ]+', '', archivo.nombre)
			return functions.exportarArchivoS3(str(archivo.soporte))

		except Exception as e:
			functions.toLog(e,'poliza.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

			