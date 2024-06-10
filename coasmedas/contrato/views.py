# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
#, render_to_response
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, serializers
from django.db.models import Q

from estado.views import EstadoSerializer, EstadoLiteSerializer
from tipo.views import TipoSerializer, TipoLiteSerializer
from empresa.views import EmpresaSerializer, EmpresaContratanteSerializer, EmpresaLiteSerializer, EmpresaContratanteLiteSelectSerializer

from cronogramacontrato.models import CcActividadContrato

from django.template import RequestContext
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

import json
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import connection

from .models import Contrato, VigenciaContrato, EmpresaContrato, Rubro, Sub_contratista, Contrato_cesion, Cesion_economica
from .models import ActaAsignacionRecursos, ActaAsignacionRecursosContrato
from .tasks import notificacionMcontrato
from estado.models import Estado
from tipo.models import Tipo
from empresa.models import Empresa, EmpresaContratante
from proyecto.models import Proyecto
from factura.models import Factura
from poliza.models import VigenciaPoliza
from django.db.models import Q, Sum

from logs.models import Logs, Acciones
from coasmedas.functions import functions
from django.db import transaction
from .enumeration import tipoC, estadoC, tipoV
from poliza.enumeration import TipoDocumento, TipoActa

import xlsxwriter

from datetime import *
import calendar
import re
import threading
from rest_framework.decorators import api_view
# Create your views here.

#Api rest para Contrato
class Empresa_contratoConsultaSerializer(serializers.HyperlinkedModelSerializer):

	empresa = EmpresaSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	class Meta:
		model = EmpresaContrato
		fields=('id','empresa','empresa_id','participa','edita')

class Vigencia_contratoConsultaSerializer(serializers.HyperlinkedModelSerializer):

	tipo = TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='VigenciaContrato'))

	class Meta:
		model = VigenciaContrato
		fields=('id','nombre','tipo','tipo_id','fecha_inicio','fecha_fin','valor','soporte')

class Vigencia_contratoLiteDetalleContratoSerializer(serializers.HyperlinkedModelSerializer):

	tipo = TipoLiteSerializer(read_only=True)

	class Meta:
		model = VigenciaContrato
		fields=('id','tipo','valor')


class ContratoSerializer(serializers.HyperlinkedModelSerializer):
	tipo_c=tipoC()

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='Contrato'))

	tipo_contrato = TipoSerializer(read_only=True)
	tipo_contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='Contrato'))

	contratista = EmpresaSerializer(read_only=True)
	contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	contratante = EmpresaSerializer(read_only=True)
	contratante_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	# mcontrato = self(read_only=True)
	mcontrato = serializers.PrimaryKeyRelatedField(queryset = Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato), allow_null = True)
	empresa_contrato = Empresa_contratoConsultaSerializer(many=True,read_only=True)
	vigencia_contrato = Vigencia_contratoConsultaSerializer(many=True,read_only=True)

	sub_contratista = EmpresaSerializer(read_only = True, many=True)

	totalFactura = serializers.SerializerMethodField()
	soloLectura = serializers.SerializerMethodField()

	class Meta:
		model = Contrato
		fields=('id','nombre','numero','tipo_contrato','tipo_contrato_id',
			'descripcion','estado','estado_id','contratista','contratista_id',
			'contratante','contratante_id','mcontrato','activo','empresa_contrato',
			'vigencia_contrato','sub_contratista','fecha_inicio','fecha_fin' , 'valor_actual','totalFactura','suma_vigencia_contrato', 'soloLectura')

	def get_fields(self):
		fields = super(ContratoSerializer, self).get_fields()
		fields['mcontrato'] = ContratoSerializer(read_only=True)
		return fields


	def get_totalFactura(self,obj):		
		total_factura=Factura.objects.filter(contrato_id=obj.id,pagada=True).aggregate(Sum('valor_contable'))

		return 0 if total_factura['valor_contable__sum'] is None else total_factura['valor_contable__sum']

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

class ContratoLiteSerializerByDidi(serializers.HyperlinkedModelSerializer):
	class Meta:
		model=Contrato
		fields=('id','nombre','numero',)

class ContratoLiteSerializerByJs(serializers.HyperlinkedModelSerializer):
	class Meta:
		model=Contrato
		fields=('id','nombre',)	

class ContratoLiteSerializerByRj(serializers.HyperlinkedModelSerializer):
	tipo_contrato = TipoSerializer(read_only=True)
	estado = EstadoSerializer(read_only=True)
	
	class Meta:
		model = Contrato
		fields=('id', 'nombre','tipo_contrato','estado','fecha_firma',)

class ContratoLiteEditarSerializer(serializers.HyperlinkedModelSerializer):
	tipo_c=tipoC()

	estado = EstadoLiteSerializer(read_only=True)

	tipo_contrato = TipoLiteSerializer(read_only=True)

	contratista = EmpresaLiteSerializer(read_only=True)

	contratante = EmpresaLiteSerializer(read_only=True)
	
	
	# mcontrato = self(read_only=True)
	mcontrato = serializers.PrimaryKeyRelatedField(queryset = Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato), allow_null = True)
	soloLectura = serializers.SerializerMethodField()
	class Meta:
		model = Contrato
		fields=('id','nombre','numero','tipo_contrato',
			'descripcion','estado','contratista','contratante',
			'mcontrato', 'activo', 'soloLectura')

	def get_fields(self):
		fields = super(ContratoLiteEditarSerializer, self).get_fields()
		fields['mcontrato'] = ContratoLiteSelectSerializer(read_only=True)
		return fields

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

class ContratoCronogramaSerializer(serializers.HyperlinkedModelSerializer):
	ano = serializers.SerializerMethodField('_ano',read_only=True)
	fondo = TipoLiteSerializer(read_only=True)
	avance = serializers.SerializerMethodField('_avance',read_only=True)

	class Meta:
		model = Contrato
		fields = ('id','ano','fondo','nombre','avance')

	def _ano(self,obj):
		if obj.fecha_firma:
			return obj.fechaAdjudicacion.strftime("%Y")
		else:
			return 'No definido'

	def _avance(self,obj):
		totalActividades = 0
		actividadesTerminadas = 0
		queryset = CcActividadContrato.objects.filter(
			contrato__id=obj.id)

		# if obj.id == 1920:
		# 	import pdb; pdb.set_trace()


		totalActividades = queryset.count()
		if totalActividades > 0:
			estados=Estado.objects.filter(codigo__in=['172','173']).values_list('id',flat=True)

			actividadesTerminadas = queryset.filter(
				estadofin__id__in = list(estados) ).count()
				
			return round((float(actividadesTerminadas) / float(totalActividades)) * 100,1)
		else:
			return 0

	

class ContratoLiteDetalleSerializer(serializers.HyperlinkedModelSerializer):
	tipo_c=tipoC()

	estado = EstadoLiteSerializer(read_only=True)
	# estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='Contrato'))

	tipo_contrato = TipoLiteSerializer(read_only=True)
	# tipo_contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='Contrato'))

	contratista = EmpresaLiteSerializer(read_only=True)
	# contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	contratante = EmpresaLiteSerializer(read_only=True)
	# contratante_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	# mcontrato = self(read_only=True)
	mcontrato = serializers.PrimaryKeyRelatedField(queryset = Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato), allow_null = True)
	# empresa_contrato = Empresa_contratoConsultaSerializer(many=True,read_only=True)
	vigencia_contrato = Vigencia_contratoLiteDetalleContratoSerializer(many=True,read_only=True)

	# sub_contratista = EmpresaSerializer(read_only = True, many=True)

	totalFactura = serializers.SerializerMethodField()

	interventoresContrato = serializers.SerializerMethodField()

	soloLectura = serializers.SerializerMethodField()
	class Meta:
		model = Contrato
		fields=('id','nombre','numero','tipo_contrato','interventoresContrato',
			'descripcion','estado','contratista','contratante','mcontrato',
			'vigencia_contrato', 'fecha_inicio', 'fecha_fin', 'valor_actual', 'totalFactura', 'suma_vigencia_contrato', 'soloLectura')

	def get_fields(self):
		fields = super(ContratoLiteDetalleSerializer, self).get_fields()
		fields['mcontrato'] = ContratoLiteSelectSerializer(read_only=True)
		return fields

	def get_interventoresContrato(self,obj):
		proyectos=Proyecto.objects.filter(contrato__id=obj.id)
		interventor=''

		for item in proyectos:
			for item_contrato in item.contrato.all():
				if int(item_contrato.tipo_contrato.id)==9:
					sw=0
					nombre=interventor.split(',')
					for i in nombre:
						if i == item_contrato.contratista.nombre:
							sw=1

					if sw == 0:
						if interventor=='':
							interventor=item_contrato.contratista.nombre
						else:
							interventor=interventor+","+item_contrato.contratista.nombre

		return interventor

	def get_totalFactura(self,obj):
		total_factura=Factura.objects.filter(contrato_id=obj.id,pagada=True).aggregate(Sum('valor_contable'))

		return 0 if total_factura['valor_contable__sum'] is None else total_factura['valor_contable__sum']

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


class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):
	tipo_c=tipoC()

	estado = EstadoLiteSerializer(read_only=True)
	# estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='Contrato'))

	mcontrato = serializers.PrimaryKeyRelatedField(queryset = Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato), allow_null = True)
	soloLectura = serializers.SerializerMethodField()

	tipo_contrato = TipoLiteSerializer(read_only=True)

	class Meta:
		model = Contrato
		fields=('id','nombre','numero', 'fecha_inicio', 'fecha_fin',
			'estado','mcontrato', 'soloLectura', 'tipo_contrato'
			)

	def get_fields(self):
		fields = super(ContratoLiteSerializer, self).get_fields()
		fields['mcontrato'] = ContratoLiteSerializer(read_only=True)
		return fields

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

class ContratoLiteContratoListSerializer(serializers.HyperlinkedModelSerializer):
	tipo_c=tipoC()
	estado = EstadoLiteSerializer(read_only=True)
	soloLectura = serializers.SerializerMethodField()
	mcontrato = serializers.PrimaryKeyRelatedField(queryset = Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato), allow_null = True)
	tipo_contrato = TipoLiteSerializer(read_only=True)
	class Meta:
		model = Contrato
		fields=('id', 'nombre', 'numero', 'fecha_inicio', 'fecha_fin', 'estado', 'soloLectura', 'mcontrato', 'tipo_contrato')

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

class ContratoLiteMultaListSerializer(serializers.HyperlinkedModelSerializer):
	tipo_c=tipoC()
	estado = EstadoLiteSerializer(read_only=True)
	contratante = EmpresaLiteSerializer(read_only=True)
	soloLectura = serializers.SerializerMethodField()
	mcontrato = serializers.PrimaryKeyRelatedField(queryset = Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato), allow_null = True)
	class Meta:
		model = Contrato
		fields=('id', 'nombre', 'numero', 'fecha_inicio', 'fecha_fin', 'estado' , 'contratante', 'soloLectura', 'mcontrato')

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

class ContratoLiteSelectSerializer(serializers.HyperlinkedModelSerializer):
    
	class Meta:
		model = Contrato
		fields=('id', 'nombre')

class ContratoLiteVigenciaSerializer(serializers.HyperlinkedModelSerializer):
    
	tipo_contrato = TipoLiteSerializer(read_only=True)

	class Meta:
		model = Contrato
		fields=('id', 'nombre', 'numero', 'tipo_contrato')

class ContratoDescargoSerializer(serializers.HyperlinkedModelSerializer):
	# tipo_c=tipoC()

	# estado = EstadoSerializer(read_only=True)
	# estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='Contrato'))

	tipo_contrato = TipoLiteSerializer(read_only=True)
	# tipo_contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='Contrato'))

	contratista = EmpresaLiteSerializer(read_only=True)
	# contratista_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	# contratante = EmpresaSerializer(read_only=True)
	# contratante_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	# mcontrato = self(read_only=True)
	# mcontrato = serializers.PrimaryKeyRelatedField(queryset = Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato), allow_null = True)
	# empresa_contrato = Empresa_contratoConsultaSerializer(many=True,read_only=True)
	# vigencia_contrato = Vigencia_contratoConsultaSerializer(many=True,read_only=True)

	# sub_contratista = EmpresaSerializer(read_only = True, many=True)

	# totalFactura = serializers.SerializerMethodField()

	class Meta:
		model = Contrato
		fields=('id','nombre','numero','tipo_contrato',
			'contratista')

	# def get_fields(self):
	# 	fields = super(ContratoSerializer, self).get_fields()
	# 	fields['mcontrato'] = ContratoSerializer(read_only=True)
	# 	return fields

class ContratoViewSet(viewsets.ModelViewSet):
	"""
	{dato='abc'}: Retorna la lista de contratos filtrados con nombre y número.
	{id_tipo=1} ó {id_tipo='1,2,3'}: Retorna la lista de contratos por tipos.
	{id_estado=1} ó {id_estado='1,2,3'}: Retorna la lista de contratos por estados.
	{mcontrato=1}: Retorna la lista de contratos filtrados con mContrato.
	{sin_paginacion=1}: Retorna la lista de contratos sin paginacion.
	"""
	model=Contrato
	queryset = model.objects.all()
	serializer_class = ContratoSerializer
	nombre_modulo = 'Contrato - ContratoViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()

			lite_editar = self.request.query_params.get('lite_editar',None)
			lite_detalle = self.request.query_params.get('lite_detalle',None)

			if lite_editar:
				serializer = ContratoLiteEditarSerializer(instance, context={'request': request})
			elif lite_detalle:
				serializer = ContratoLiteDetalleSerializer(instance, context={'request': request})
			else:
				serializer = self.get_serializer(instance)

			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ContratoViewSet, self).get_queryset()
			num_nom = self.request.query_params.get('dato', None)
			contrato_id = self.request.query_params.get('id', None)
			id_tipo = self.request.query_params.get('id_tipo').split(',') if self.request.query_params.get('id_tipo') else None
			id_tipo_codigo = self.request.query_params.get('id_tipo_codigo').split(',') if self.request.query_params.get('id_tipo_codigo') else None
			id_estado = self.request.query_params.get('id_estado').split(',') if self.request.query_params.get('id_estado') else None
			mcontrato = self.request.query_params.get('mcontrato').split(',') if self.request.query_params.get('mcontrato') else None
			contratista_id = self.request.query_params.get('contratista_id', None)

			lite = self.request.query_params.get('lite', None)
			liteD = self.request.query_params.get('liteD', None) # DEFINIDO POR DIDI POR CAMPOS ESPECIFICOS

			#Parametros para manejo de cronograma contratos
			sin_paginacion= self.request.query_params.get('sin_paginacion',None)
			cronogramaContrato = self.request.query_params.get('cronogramaContrato',None)
			ano = self.request.query_params.get('ano', None) #Falta el campo fondo
			fondo = self.request.query_params.get('fondo', None)
			id_cronogramacontrato = self.request.query_params.get('id', None)

			id_empresa = request.user.usuario.empresa.id

			
			if cronogramaContrato:
				try:
					qset = Q(empresa__id=id_empresa, contrato__tipo_contrato__id=12)
					if fondo:
						qset = qset & Q(contrato__fondo__id=fondo)
					if ano:
						desde = ano + '-01-01'
						hasta = ano + '-12-31'
						qset = qset & Q(contrato__fechaAdjudicacion__range=[desde,hasta])
					
					if id_cronogramacontrato:
						qset= qset & Q(contrato__id=int(id_cronogramacontrato))

					querysetContratosConAcceso = EmpresaContrato.objects.filter(
						qset).values_list('contrato__id',flat=True) 
					#import pdb; pdb.set_trace()
					queryset = Contrato.objects.filter(
						id__in=list(querysetContratosConAcceso)).order_by(
						'fechaAdjudicacion','fondo__nombre','nombre')

					if sin_paginacion is None:
						page = self.paginate_queryset(queryset)
						if page is not None:
							serializer = ContratoCronogramaSerializer(
								page,
								many=True, 
								context={'request': request,}
							)

							return self.get_paginated_response(
								{'message':'','success':'ok',
								'data':serializer.data})



					else:
						serializer = ContratoCronogramaSerializer(queryset,many=True)
						return Response({'message':'','success':'ok','data':serializer.data})

				except Exception as e:
					functions.toLog(e,'cronogramaContrato')
					return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

			sin_list_contrato= self.request.query_params.get('sin_list_contrato',None)

			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			otros = self.request.query_params.get('otros',None)
			contratante = self.request.query_params.get('contratante',None)
			contratista = self.request.query_params.get('contratista',None)
			tipo = self.request.query_params.get('tipo',None)
			list_mcontrato = self.request.query_params.get('list_mcontrato',None)
			noAsignado = self.request.query_params.get('noAsignado',None)

			id_empresa = request.user.usuario.empresa.id

			if sin_list_contrato is None:

				qset=(~Q(id=0))

				#import pdb; pdb.set_trace()
			
				if num_nom:
					qset = qset &(Q(nombre__icontains=num_nom)|Q(numero__icontains=num_nom))
				if contrato_id:
					qset = qset &(Q(id=contrato_id))
				if id_tipo:
					qset = qset &(Q(tipo_contrato__in=id_tipo))
				if id_tipo_codigo:
					qset = qset &(Q(tipo_contrato__codigo__in=id_tipo_codigo))
				if contratista_id:
					qset = qset &(Q(contratista_id=contratista_id))


				if id_estado:
					qset = qset &(Q(estado__in=id_estado))

				if mcontrato:
					qset = qset &(Q(mcontrato__in=mcontrato))

				if id_empresa:
					qset = qset &(Q(empresacontrato__empresa=id_empresa) & Q(empresacontrato__participa=1) & Q(activo=1))

				if qset is not None:
					if noAsignado:
						queryset = self.model.objects.filter(qset).exclude(pk = 1843).order_by('-id')
					else:
						queryset = self.model.objects.filter(qset).order_by('nombre').distinct()

				serializer_context = {
					'request': request,
				}

				if sin_paginacion is None:
					page = self.paginate_queryset(queryset)

					if page is not None:

						if lite is not None:
							if lite == '2':
								serializer = ContratoLiteContratoListSerializer(page,many=True, context=serializer_context)
							elif lite == '3':
								serializer = ContratoLiteSerializerByDidi(page,many=True, context=serializer_context)
							elif lite == '4':
								serializer = ContratoLiteSerializerByJs(page,many=True, context=serializer_context)								
							else:
								serializer = ContratoLiteSerializer(page,many=True, context=serializer_context)
						else:
							serializer = self.get_serializer(page,many=True, context=serializer_context)

						return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

					serializer = self.get_serializer(queryset,many=True)
					return Response({'message':'','success':'ok','data':serializer.data})

				else:
					if liteD:

						if liteD == '2':
							serializer = ContratoLiteContratoListSerializer(queryset,many=True, context=serializer_context)
						elif liteD == '3':
							serializer = ContratoLiteMultaListSerializer(queryset,many=True, context=serializer_context)
						elif liteD == '4':
							serializer = ContratoLiteSelectSerializer(queryset,many=True, context=serializer_context)
						else:
							serializer = ContratoLiteVigenciaSerializer(queryset,many=True, context=serializer_context)

						return Response({'message':'','success':'ok','data':serializer.data})
					else:
						serializer = self.get_serializer(queryset,many=True)
						return Response({'message':'','success':'ok','data':serializer.data})
			else:
				# if liteD:
				# 	serializer = ContratoLiteVigenciaSerializer(queryset,many=True)
				# 	return Response({'message':'','success':'ok','data':serializer.data})
		

				serializer_context = {
					'request': request,
				}
				if contratante:
					querysetContratante=EmpresaContratante.objects.filter(empresa_id=id_empresa)
					listContratante = EmpresaContratanteLiteSelectSerializer(querysetContratante,many=True, context=serializer_context).data
				else:
					listContratante = ''

				if contratista:
					querysetContratista=Empresa.objects.filter(esContratista=1)
					listContratista = EmpresaLiteSerializer(querysetContratista,many=True, context=serializer_context).data
				else:
					listContratista = ''

				if tipo:
					querysetTipo=Tipo.objects.filter(app='contrato')
					listTipo = TipoLiteSerializer(querysetTipo,many=True, context=serializer_context).data
				else:
					listTipo = ''

				if list_mcontrato:
					tipo_c=tipoC()
					querysetList_mcontrato = self.model.objects.filter(empresacontrato__empresa=id_empresa, empresacontrato__participa=1, tipo_contrato=tipo_c.m_contrato, activo=1)
					listList_mcontrato = ContratoLiteSelectSerializer(querysetList_mcontrato,many=True, context=serializer_context).data
				else:
					listList_mcontrato = ''

				return Response({'message':'','success':'ok','data':{'contratante':listContratante,
																		'contratista':listContratista,
																		'tipo':listTipo,
																		'mcontrato':listList_mcontrato}})

		except IndexError as ie:
			# print ie
			return Response({'message':'No existen contratos registrados con el tipo indicado','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		except  Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			tipo_c=tipoC()
			sid = transaction.savepoint()
			try:
				# #print request.DATA
				serializer = ContratoSerializer(data=request.DATA,context={'request': request})
				
				if request.DATA['mcontrato_id'] == '':
					request.DATA['mcontrato_id']=None

				if serializer.is_valid():

					if EmpresaContrato.objects.filter(contrato__numero = request.DATA['numero'], empresa=request.user.usuario.empresa.id).exists():
						return Response({'message':'El Número ya existe en el sistema.','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
					else:
						serializer.save(estado_id=request.DATA['estado_id'], tipo_contrato_id=int(request.DATA['tipo_contrato_id']),
										contratista_id=request.DATA['contratista_id'], contratante_id=request.DATA['contratante_id'],
										mcontrato_id=request.DATA['mcontrato_id'])

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='contrato.contrato',id_manipulado=serializer.data['id'])
						logs_model.save()

						serializer_conto_empresa = Empresa_contratoSerializer(data={'contrato_id':serializer.data['id'],
								'empresa_id':request.user.usuario.empresa.id,
								'participa':1,
								'edita':1}, context={'request': request})
						if serializer_conto_empresa.is_valid():
							serializer_conto_empresa.save(contrato_id=serializer.data['id'],empresa_id=request.user.usuario.empresa.id)
						
						if request.user.usuario.empresa.id != request.DATA['contratante_id']:							
							empresa_contrato = EmpresaContrato(empresa_id=request.DATA['contratante_id'],
												participa=1,
												contrato_id=serializer.data['id'],
												edita=1
												)
							empresa_contrato.save()
							# logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='contrato.contrato_empresa',id_manipulado=serializer.data['id'])
							# logs_model.save()

							# if request.DATA['proyecto'] != '0':
							# 	createProyectoContrato(request.DATA['proyecto'], serializer.data['id'])

							if request.DATA['tipo_contrato_id'] == str(tipo_c.m_contrato):
								# print ("RUBROS:",request.DATA['rubros'])
								createRubroContrato(request.DATA['rubros'], serializer.data['id'])
						# import pdb; pdb.set_trace()
						transaction.savepoint_commit(sid)
						if serializer.data['tipo_contrato']['id'] == 12:															
							sendEmail = threading.Thread(target=notificacionMcontrato, args=(serializer.data,request.user.usuario,))
							sendEmail.start()																			

						return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					
					print(serializer.errors)
					return Response({'message':'Datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			tipo_c=tipoC()
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				# print instance
				serializer = ContratoSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					if request.DATA['mcontrato_id']=='':
						request.DATA['mcontrato_id']=None
					serializer.save(estado_id=request.DATA['estado_id'], tipo_contrato_id=request.DATA['tipo_contrato_id'],
									contratista_id=request.DATA['contratista_id'], contratante_id=request.DATA['contratante_id'],
									mcontrato_id=request.DATA['mcontrato_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='contrato.contrato',id_manipulado=serializer.data['id'])
					logs_model.save()

					# if request.DATA['proyecto'] != '0':
					# 	eliminarProyectoContrato(serializer.data['id'], request.DATA['proyecto'])
					# 	createProyectoContrato(request.DATA['proyecto'], serializer.data['id'])

					if request.DATA['tipo_contrato_id'] == str(tipo_c.m_contrato):
						rubros = str(request.DATA['rubros']).split(',')
						# print rubros
						eliminarRubroContrato(request.DATA['id'])
						createRubroContrato(rubros, serializer.data['id'])

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
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)	
#Fin api rest para Contrato


#Api rest para Vigencia_contrato
class Vigencia_contratoSerializer(serializers.HyperlinkedModelSerializer):

	contrato = ContratoSerializer(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	tipo = TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='VigenciaContrato'))
	soloLectura = serializers.SerializerMethodField()
	class Meta:
		model = VigenciaContrato
		fields=('id','nombre','contrato','contrato_id','tipo','tipo_id',
		'fecha_inicio','fecha_fin','valor','soporte','acta_id','acta_compra', 'soloLectura')

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


class Vigencia_contratoLiteListSerializer(serializers.HyperlinkedModelSerializer):

	contrato = ContratoLiteVigenciaSerializer(read_only=True)
	# contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	tipo = TipoLiteSerializer(read_only=True)
	# tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='VigenciaContrato'))

	num = serializers.SerializerMethodField('_num',read_only=True)

	def _num(self, obj):
		tipo_v=tipoV()

		model_vigencia = VigenciaContrato.objects.get(pk=obj.id)

		cadena = re.sub('\D', '', model_vigencia.nombre)

		if cadena != '':
			return int(cadena)
		elif model_vigencia.tipo.id == tipo_v.liquidacion:
			return 30
		else:
			return 0
	soloLectura = serializers.SerializerMethodField()
	class Meta:
		model = VigenciaContrato
		fields=('id','nombre','contrato','tipo','fecha_inicio','fecha_fin',
				'valor','soporte','num','acta_compra', 'soloLectura')
		# order_by = (('nombre',))

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

class Vigencia_contratoViewSet(viewsets.ModelViewSet):
	"""
	"""
	model=VigenciaContrato
	queryset = model.objects.all()
	serializer_class = Vigencia_contratoSerializer
	nombre_modulo = 'Contrato - Vigencia_contratoViewSet'
	# ordering = ('nombre',)

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance, context={'request': request})
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(Vigencia_contratoViewSet, self).get_queryset()
			id_vigencia = self.request.query_params.get('id_vigencia', None)
			id_contrato = self.request.query_params.get('id_contrato', None)
			id_tipo = self.request.query_params.get('id_tipo').split(',') if self.request.query_params.get('id_tipo') else None
			num_nom = self.request.query_params.get('dato', None)
			nombre = self.request.query_params.get('nombre', None)
			id_acta = self.request.query_params.get('id_acta', None)

			lite_list = self.request.query_params.get('lite_list', None)

			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			id_empresa = request.user.usuario.empresa.id

			qset = (~Q(id=0))
			if num_nom:
				qset = (
					Q(contrato__nombre__icontains=num_nom)|Q(contrato__numero__icontains=num_nom)
					)

			if id_vigencia:
				if qset != None:
					qset = qset &(
						Q(id=id_vigencia)
						)
				else:
					qset = (
						Q(id=id_vigencia)
						)

			if nombre:
				if qset != None:
					qset = qset &(
						Q(nombre__icontains=nombre)
						)
				else:
					qset = (
						Q(nombre__icontains=nombre)
						)

			if id_contrato:
				if qset != None:
					qset = qset &(
						Q(contrato=id_contrato)
						)
				else:
					qset = (
						Q(contrato=id_contrato)
						)

			if id_tipo:
				if qset != None:
					qset = qset &(
						Q(tipo__in=id_tipo)
						)
				else:
					qset = (
						Q(tipo__in=id_tipo)
						)

			if id_empresa:
				if qset != None:
					qset = qset &(
						#Q(empresa_contrato__empresa_id=id_empresa)
						Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1)
					)
				else:
					qset = (
						#Q(empresa_contrato__empresa_id=id_empresa)
						Q(contrato__empresacontrato__empresa=id_empresa) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1)
					)

			if id_acta:
				if qset != None:
					qset = qset &(
						Q(acta_id=id_acta)
						)
				else:
					qset = (
						Q(acta_id=id_acta)
						)

			# if qset is not None:
			queryset = self.model.objects.filter(qset).order_by('-id')

			serializer_context = {
				'request': request,
			}

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			else:
				if lite_list is not None:

					serializer = Vigencia_contratoLiteListSerializer(queryset, many=True, context=serializer_context)
				else:
					serializer = self.get_serializer(queryset,many=True, context=serializer_context)

				return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			estado_c=estadoC()
			tipo_v=tipoV()
			sid = transaction.savepoint()
			try:

				serializer = Vigencia_contratoSerializer(data=request.DATA,context={'request': request})
				# #print request.DATA
				acta_id = request.DATA.get('acta_id', None)
				# print "asas:"+acta_id
				if acta_id == '':
					acta_id=None
				
				if serializer.is_valid():
					#serializer.save()

					if self.request.FILES.get('soporte') is not None:
						#nombre = self.request.FILES.get('soporte')
						#print ("archivo: ", self.request.FILES['soporte']['filename'])
						#print ("archivo: ", nombre['filename'])
						# pass , acta_id=request.DATA['acta_id']
						serializer.save(soporte=self.request.FILES['soporte'],
										acta_compra=request.FILES['acta_compra'] if request.FILES.get('acta_compra') is not None else '',
										contrato_id=request.DATA['contrato_id'],
										tipo_id=request.DATA['tipo_id'],
										acta_id=acta_id)

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='contrato.contrato_vigencia',id_manipulado=serializer.data['id'])
						logs_model.save()

					else:
						#print self.request.FILES.get('soporte')
						serializer.save(soporte='',
										acta_compra=request.FILES['acta_compra'] if request.FILES.get('acta_compra') is not None else '',
										contrato_id=request.DATA['contrato_id'],
										tipo_id=request.DATA['tipo_id'],
										acta_id=request.DATA['acta_id'])

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='contrato.contrato_vigencia',id_manipulado=serializer.data['id'])
						logs_model.save()

					

					if serializer.data['tipo']['id'] == tipo_v.actaSuspension:
						actualizarEstadoContrato(serializer.data['contrato']['id'], estado_c.suspendido)

						# Buscar poliza para actulizarla
						tipo_documento = TipoDocumento()
						tipo_acta = TipoActa()
						ActulizarPolizaVigenciaContrato(request, serializer.data['id'], tipo_documento.VigenciaContrato, tipo_acta.ActaSuspension)

					if serializer.data['tipo']['id'] == tipo_v.actaReinicio:
						actualizarEstadoContrato(serializer.data['contrato']['id'], estado_c.vigente)

						# Buscar poliza para actulizarla
						tipo_documento = TipoDocumento()
						tipo_acta = TipoActa()
						ActulizarPolizaVigenciaContrato(request, serializer.data['id'], tipo_documento.VigenciaContrato, tipo_acta.ActaReinicio)

					if serializer.data['tipo']['id'] == tipo_v.liquidacion:
						actualizarEstadoContrato(serializer.data['contrato']['id'], estado_c.liquidado)

						# Buscar poliza para actulizarla
						tipo_documento = TipoDocumento()
						tipo_acta = TipoActa()
						ActulizarPolizaVigenciaContrato(request, serializer.data['id'], tipo_documento.VigenciaContrato, tipo_acta.ActaLiquidacion)

					if serializer.data['tipo']['id'] == tipo_v.contrato or serializer.data['tipo']['id'] == tipo_v.otrosi or serializer.data['tipo']['id'] == tipo_v.replanteo or serializer.data['tipo']['id'] == tipo_v.actaCesion:
						actualizarEstadoContrato2(serializer.data['contrato']['id'])

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					# serializer.errors
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
				serializer = Vigencia_contratoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				
				# acta_id = request.DATA.get('acta_id', None)
				if request.DATA['acta_id'] == '':
					request.DATA['acta_id']=None
				
				if serializer.is_valid():
					# print 'entro'

					serializer.save(
						soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte,
						acta_compra=self.request.FILES['acta_compra'] if self.request.FILES.get('acta_compra') is not None else instance.acta_compra,
						contrato_id=self.request.DATA['contrato_id'],						
						tipo_id=self.request.DATA['tipo_id'],
						acta_id=request.DATA['acta_id'])

					# logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='contrato.contrato_vigencia',id_manipulado=instance.id)
					# logs_model.save()

					transaction.savepoint_commit(sid)
					actualizarEstadoContrato2(instance.contrato.id)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					# print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		tipo_v=tipoV()

		sid = transaction.savepoint()
		try:
			estado_c=estadoC()
			instance = self.get_object()
			self.perform_destroy(instance)

			if instance.tipo.id == tipo_v.actaSuspension:
				actualizarEstadoContrato(instance.contrato.id, estado_c.vigente)

			if instance.tipo.id == tipo_v.actaReinicio:
				actualizarEstadoContrato(instance.contrato.id, estado_c.suspendido)

			# logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='contrato.contrato_vigencia',id_manipulado=instance.id)
			# logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)	
#Fin api rest para Vigencia_contrato


#Api rest para Empresa_contrato
class Empresa_contratoSerializer(serializers.HyperlinkedModelSerializer):

	contrato = ContratoSerializer(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	empresa = EmpresaSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	class Meta:
		model = EmpresaContrato
		fields=('id','contrato','contrato_id','empresa','empresa_id','participa','edita')

		validators=[serializers.UniqueTogetherValidator(
								queryset=model.objects.all(),
								fields=('empresa_id','contrato_id'),
								message=('La empresa ya tiene asignado el permiso que intenta registrar') ) ]

class Empresa_contratoViewSet(viewsets.ModelViewSet):
	"""
	
	"""
	model=EmpresaContrato
	queryset = model.objects.all()
	serializer_class = Empresa_contratoSerializer
	nombre_modulo = 'Contrato - Empresa_contratoViewSet'

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
			queryset = super(Empresa_contratoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			id_contrato = self.request.query_params.get('id_contrato', None)
			id = self.request.query_params.get('id', None)
			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			dato_contratista = self.request.query_params.get('dato_contratista', None)
			contrato_contratista = self.request.query_params.get('contrato_contratista',None)

			otros = self.request.query_params.get('otros',None)
			contratante = self.request.query_params.get('contratante',None)

			id_empresa = request.user.usuario.empresa.id

			qset = None
			if dato:
				qset = (
					Q(empresa__nombre__icontains=dato)
					)
			if id_contrato:
				if qset != None:
					qset = qset &(
						Q(contrato=id_contrato)
						# Q(empresa__icontains=dato)|
						# Q(participa__icontains=dato)|
						# Q(edita__icontains=dato)
					)
				else:
					qset = (
						Q(contrato=id_contrato)
					)
			if id:
				if qset != None:
					qset = qset &(
						Q(id=id)
						# Q(empresa__icontains=dato)|
						# Q(participa__icontains=dato)|
						# Q(edita__icontains=dato)
					)
				else:
					qset = (
						Q(id=id)
					)


			if contrato_contratista:
				if dato_contratista is not None:
					qset=Q(empresa_id=request.user.usuario.empresa.id,participa=1,contrato__activo=1,contrato__contratista__nombre__icontains=dato_contratista)
				else:
					qset=Q(empresa_id=request.user.usuario.empresa.id,participa=1,contrato__activo=1)


			if contrato_contratista:
				queryset = self.model.objects.filter(qset).values('contrato__contratista__id','contrato__contratista__nombre','contrato__contratista__nit','contrato__contratista__abreviatura').distinct()
			else:		

				if qset is not None:
					queryset = self.model.objects.filter(qset)

			serializer_context = {
				'request': request,
			}

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:

					if contrato_contratista is not None:
						return self.get_paginated_response({'message':'','success':'ok','data':list(page)})
					else:
						serializer = self.get_serializer(page,many=True)

						if otros:
							if contratante:
								querysetContratante=EmpresaContratante.objects.filter(empresa_id=id_empresa).values('empresa_ver__nombre',
																																																		'empresa_ver__id')
								lista = EmpresaContratante.objects.filter(empresa_id=id_empresa).values('empresa_ver__id')

								# lista2 = EmpresaContratanteSerializer(lista,many=True, context=serializer_context).data
								# listContratante = EmpresaContratanteSerializer(querysetContratante,many=True, context=serializer_context).data

								querysetContratista=self.model.objects.filter(empresa_id=id_empresa,participa=1,contrato__activo=1).values('contrato__contratista__id',
																																																													'contrato__contratista__nombre',
																																																													).exclude(contrato__contratista__id__in = lista
																																																													).distinct()

							else:
								listContratante = ''

							return self.get_paginated_response({'message':'','success':'ok','data':{'listado':serializer.data,
																																											'contratante':list(querysetContratante),
																																											'contratista':list(querysetContratista)}})

						else:
							return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			else:

				if contrato_contratista is not None:
					return Response({'message':'','success':'ok','data':list(queryset)})
				else:

					serializer = self.get_serializer(queryset,many=True)
					return Response({'message':'','success':'ok','data':serializer.data})

	
			# page = self.paginate_queryset(queryset)
			# if page is not None:
			# 	serializer = self.get_serializer(page,many=True)
			# 	return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})
	
			# serializer = self.get_serializer(queryset,many=True)
			# return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = Empresa_contratoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'], empresa_id=request.DATA['empresa_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='contrato.contrato_empresa',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
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

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = Empresa_contratoSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'], empresa_id=request.DATA['empresa_id'])

					# logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='contrato.contrato_empresa',id_manipulado=instance.data['id'])
					# logs_model.save()

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

	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# print instance.id
			self.model.objects.get(pk=instance.id).delete()

			# logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='contrato.contrato_empresa',id_manipulado=instance.data['id'])
			# logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)	
#Fin api rest para Empresa_contrato


#Api rest para Rubro
class RubroSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Rubro
		fields=('id','nombre')

class RubroViewSet(viewsets.ModelViewSet):
	"""
	
	"""
	model = Rubro
	queryset = model.objects.all()
	serializer_class = RubroSerializer
	nombre_modulo = 'Contrato - RubroViewSet'

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
			queryset = super(RubroViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			if dato:
				qset = (
					Q(id=dato)|Q(nombre__icontains=dato)
					)
				queryset = self.model.objects.filter(qset)
	
			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page,many=True)
				return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})
	
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
				serializer = RubroSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save()

					#print serializer

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='contrato.contrato_rubro',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = RubroSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='contrato.contrato_rubro',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

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
#Fin api rest para Rubro


#Api rest para sub contratista
class Sub_contratistaSerializer(serializers.HyperlinkedModelSerializer):

	contrato = ContratoSerializer(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	empresa = EmpresaSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.filter(esContratista=1))

	class Meta:
		model = Sub_contratista
		fields=('id','contrato','contrato_id','empresa','empresa_id','soporte')

		validators=[serializers.UniqueTogetherValidator(
								queryset=model.objects.all(),
								fields=('empresa_id','contrato_id'),
								message=('El contrato ya tiene asignado el contratista que intenta registrar') ) ]

class Sub_contratistaViewSet(viewsets.ModelViewSet):
	"""

	"""
	model=Sub_contratista
	queryset = model.objects.all()
	serializer_class = Sub_contratistaSerializer
	nombre_modulo = 'Contrato - Sub_contratistaViewSet'

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
			queryset = super(Sub_contratistaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			id_contrato = self.request.query_params.get('id_contrato', None)
			id_empresa = self.request.query_params.get('id_empresa', None)
			sin_paginacion = self.request.query_params.get('sin_paginacion',None)
			id_empresa_usu = request.user.usuario.empresa.id

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(empresa__nombre__icontains=dato))

			if id_contrato:
				qset = qset &(Q(contrato=id_contrato))

			if id_empresa:
				qset = qset &(Q(empresa=id_empresa))

			if id_empresa_usu:
				qset = qset &(Q(contrato__empresacontrato__empresa=id_empresa_usu) & Q(contrato__empresacontrato__participa=1) & Q(contrato__activo=1))

			if qset is not None:
				queryset = self.model.objects.filter(qset)

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
				serializer = Sub_contratistaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'], empresa_id=request.DATA['empresa_id'],
						soporte=request.FILES['soporte'] if request.FILES.get('soporte') is not None else '')

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='contrato.sub_contratista',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
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

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = Sub_contratistaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'], empresa_id=request.DATA['empresa_id'],
						soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='contrato.sub_contratista',id_manipulado=instance.id)
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

	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# print instance.id
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='contrato.sub_contratista',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para sub contratista


#Api rest para contrato_cesion
class Contrato_cesionSerializer(serializers.HyperlinkedModelSerializer):

	contrato = ContratoSerializer(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	contratista_nuevo = EmpresaSerializer(read_only=True)
	contratista_nuevo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.filter(esContratista=1))

	contratista_antiguo = EmpresaSerializer(read_only=True)
	contratista_antiguo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.filter(esContratista=1))

	class Meta:
		model = Contrato_cesion
		fields=('id','contrato','contrato_id','contratista_nuevo','contratista_nuevo_id','contratista_antiguo','contratista_antiguo_id','fecha','soporte')

class Contrato_cesionViewSet(viewsets.ModelViewSet):
	"""
	
	"""
	model=Contrato_cesion
	queryset = model.objects.all()
	serializer_class = Contrato_cesionSerializer
	nombre_modulo = 'Contrato - Contrato_cesionViewSet'

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
			queryset = super(Contrato_cesionViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			fecha = self.request.query_params.get('fecha', None)
			id_contrato = self.request.query_params.get('id_contrato', None)
			nuevo = self.request.query_params.get('id_contratista_nuevo', None)
			antiguo = self.request.query_params.get('id_contratista_antiguo', None)
			sin_paginacion = self.request.query_params.get('sin_paginacion',None)

			qset=(~Q(id=0))
			if dato:
				qset = qset &(Q(contratista_nuevo__nombre__icontains=dato) | Q(contratista_antiguo__nombre__icontains=dato))

			if id_contrato:
				qset = qset &(Q(contrato=id_contrato))

			if nuevo:
				qset = qset &(Q(contratista_nuevo=nuevo))

			if antiguo:
				qset = qset &(Q(contratista_antiguo=antiguo))

			if fecha:
				qset = qset &(Q(fecha=fecha))

			if qset is not None:
				queryset = self.model.objects.filter(qset)

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
				serializer = Contrato_cesionSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'],
						contratista_nuevo_id=request.DATA['contratista_nuevo_id'],
						contratista_antiguo_id=request.DATA['contratista_antiguo_id'],
						soporte=request.FILES['soporte'] if request.FILES.get('soporte') is not None else '')

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='contrato.contrato_cesion',id_manipulado=serializer.data['id'])
					logs_model.save()

					actualizarContratistaContrato(request.DATA['contrato_id'],request.DATA['contratista_nuevo_id'])

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = Contrato_cesionSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'],
						contratista_nuevo_id=request.DATA['contratista_nuevo_id'],
						contratista_antiguo_id=request.DATA['contratista_antiguo_id'],
						soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='contrato.contrato_cesion',id_manipulado=instance.id)
					logs_model.save()

					actualizarContratistaContrato(request.DATA['contrato_id'],request.DATA['contratista_nuevo_id'])

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# print instance.id
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='contrato.contrato_cesion',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para contrato_cesion


#Api rest para cesion_economica
class Cesion_economicaSerializer(serializers.HyperlinkedModelSerializer):

	contrato = ContratoSerializer(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	empresa = EmpresaSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.filter(esContratista=1))

	class Meta:
		model = Cesion_economica
		fields=('id','contrato','contrato_id','empresa','empresa_id','fecha','soporte')

		validators=[serializers.UniqueTogetherValidator(
								queryset=model.objects.all(),
								fields=('empresa_id','contrato_id'),
								message=('El contrato ya tiene asignado el contratista que intenta registrar') ) ]

class Cesion_economicaViewSet(viewsets.ModelViewSet):
	"""
	
	"""
	model=Cesion_economica
	queryset = model.objects.all()
	serializer_class = Cesion_economicaSerializer
	nombre_modulo = 'Contrato - Cesion_economicaViewSet'

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
			queryset = super(Cesion_economicaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			fecha = self.request.query_params.get('fecha', None)
			id_contrato = self.request.query_params.get('id_contrato', None)
			id_empresa = self.request.query_params.get('id_empresa', None)
			sin_paginacion = self.request.query_params.get('sin_paginacion',None)

			qset=(~Q(id=0))

			if dato:
				qset = qset &(Q(empresa__nombre__icontains=dato))

			if id_contrato:
				qset = qset &(Q(contrato=id_contrato))

			if id_empresa:
				qset = qset &(Q(empresa=id_empresa))

			if fecha:
				qset = qset &(Q(fecha=fecha))

			if qset is not None:
				queryset = self.model.objects.filter(qset)

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
				serializer = Cesion_economicaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'], empresa_id=request.DATA['empresa_id'],
						soporte=request.FILES['soporte'] if request.FILES.get('soporte') is not None else '')

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='contrato.cesion_economica',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
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

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = Cesion_economicaSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'], empresa_id=request.DATA['empresa_id'],
						soporte=self.request.FILES['soporte'] if self.request.FILES.get('soporte') is not None else instance.soporte)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='contrato.cesion_economica',id_manipulado=instance.id)
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

	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# print instance.id
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='contrato.cesion_economica',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para Cesion_economica


@login_required
def contrato(request):
	tipo_c=tipoC()

	querysetTipos=Tipo.objects.filter(app='contrato')
	querysetEstado=Estado.objects.filter(app='contrato')
	querysetRubros=Rubro.objects.all()
	id_empresa = request.user.usuario.empresa.id
	# querysetMContrato=Contrato.objects.filter(empresacontrato__empresa__in=(id_empresa, 4, 198,), empresacontrato__participa=1, tipo_contrato=tipo_c.m_contrato, activo=1)
	querysetMContrato=Contrato.objects.filter(empresacontrato__empresa=id_empresa, empresacontrato__participa=1, tipo_contrato=tipo_c.m_contrato, activo=1)
	return render(request, 'contrato/contrato.html',{'tipos':querysetTipos,'estados':querysetEstado,'rubros':querysetRubros,'m_contratos':querysetMContrato,'model':'contrato','app':'contrato'})
	# return render(request, 'descargo/registrar_consulta.html',{'model':'contrato','app':'contrato'})

@login_required
def detalleContrato(request, id_contrato=None):
	# querysetTipos=Tipo.objects.filter(app='VigenciaContrato').values('id', 'nombre')//'tipos':list(querysetTipos),
	return render(request, 'contrato/detalleContrato.html',{'id_contrato':id_contrato,'model':'Contrato','app':'contrato'})

@login_required
def vigenciaContrato(request, id_contrato=None):
	tipo_v=tipoV()
	return render(request, 'contrato/vigencia.html',{'tipo_acta_ampliacion':tipo_v.actaAmpliacion,'id_contrato':id_contrato,'model':'vigenciacontrato','app':'contrato'})

@login_required
def historialContrato(request, id_contrato=None):
	return render(request, 'contrato/historialContrato.html',{'id_contrato':id_contrato,'model':'contrato','app':'contrato'})

@login_required
def gestionarProyectos(request, id_contrato=None):
	mcontratos=Contrato.objects.filter(tipo_contrato_id=12)
	return render(request, 'contrato/gestionarProyectos.html',{'mcontratos':mcontratos,'id_contrato':id_contrato,'model':'contrato','app':'contrato'})

@login_required
def permisoContrato(request, id_contrato=None):
	return render(request, 'contrato/permisoContrato.html',{'id_contrato':id_contrato,'model':'empresacontrato','app':'contrato'})

@login_required
def actasContrato(request, id_contrato=None):
	return render(request, 'contrato/actasContrato.html',{'id_contrato':id_contrato,'model':'vigenciacontrato','app':'contrato'})

@login_required
def subContratista(request, id_contrato=None):
	return render(request, 'contrato/subContratista.html',{'id_contrato':id_contrato,'model':'sub_contratista','app':'contrato'})

@login_required
def contratoCesion(request, id_contrato=None):
	return render(request, 'contrato/contratoCesion.html',{'id_contrato':id_contrato,'model':'contrato_cesion','app':'contrato'})

@login_required
def cesionEconomica(request, id_contrato=None):
	return render(request, 'contrato/cesionEconomica.html',{'id_contrato':id_contrato,'model':'cesion_economica','app':'contrato'})

def listRubroContrato(request):
	nombre_modulo = 'Contrato - listRubroContrato'
	cursor = connection.cursor()
	try:
		id_contrato=request.GET['id_contrato']
		cursor.callproc('[contrato].[lista_rubro_contrato]', [id_contrato,])
		#if cursor.return_value == 1:
		result_set = cursor.fetchall()
		lista=[]
		for x in list(result_set):
			item={
				'id':x[0],
				'nombre':x[1],
				'tiene_rubro':x[2]>0
			}
			lista.append(item)
		return JsonResponse({'message':'','success':'ok','data':lista})
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})

def createProyectoContrato(proyecto_id, contrato_id):
	# if request.method == 'POST':
	nombre_modulo = 'Contrato - createProyectoContrato'
	try:
		myList = contrato_id
		model_proyecto = Proyecto.objects.get(pk=proyecto_id)
		model_proyecto.contrato.add(myList)
		# return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Guardar los contratos con proyectos
def createProyectoContratoConLista(request):

	nombre_modulo = 'Contrato - createProyectoContratoConLista'

	proyecto_id = request.GET['proyecto_id']
	contrato_id = request.GET['contrato_id']
	# if request.method == 'POST':
	try:
		pass
		myList = proyecto_id.split(',')

		for item in myList:
			if item:
				# print "lasas:"
				model_proyecto = Proyecto.objects.get(pk=item)
				model_proyecto.contrato.add(contrato_id)

		return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Elimina los proyectoContrato
def eliminarProyectoContrato(id_contrato, id_proyecto):

	model_contrato = Contrato.objects.get(pk=id_contrato)
	model_proyecto = Proyecto.objects.get(pk=id_proyecto)

	model_proyecto.contrato.remove(model_contrato)

def destroyProyectoContrato(request):
	nombre_modulo = 'Contrato - destroyProyectoContrato'
	if request.method == 'POST':
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']

			for item in myList:
				model_proyecto = Proyecto.objects.get(pk=item['id'])
				model_proyecto.contrato.remove(respuesta['contrato'])
				# Proyecto.objects.filter(id = item ).delete()

			# transaction.commit()
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Guardar los rubros de los m-contratos
def createRubroContrato(rubros_id, contrato_id):
	nombre_modulo = 'Contrato - createRubroContrato'
	# if request.method == 'POST':
	try:
		for rubro in rubros_id:
			if rubro:
				model_rubro = Rubro.objects.get(pk=rubro)
				model_rubro.contrato.add(contrato_id)

		# return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Elimina los rubrosContrato
def eliminarRubroContrato(id_contrato):
	nombre_modulo = 'Contrato - eliminarRubroContrato'	
	# try:
	# 	model_contrato = Contrato.objects.get(pk=id_contrato)

	# 	# for rubro in id_rubro:
	# 	model_rubro = Rubro.objects.all()

	# 	model_rubro.contrato.clear(id_contrato)
	# except Exception as e:
	# 	functions.toLog(e,self.nombre_modulo)

	cursor = connection.cursor()
	try:
		# id_contrato=request.GET['id_contrato']
		cursor.callproc('[contrato].[eliminar_rubro_contrato]', [id_contrato,])
		#if cursor.return_value == 1:
		result_set = cursor.fetchall()

	except Exception as e:
		functions.toLog(e, nombre_modulo)

def listProyContrato(request):
	nombre_modulo = 'Contrato - listProyContrato'
	try:
		id_contrato=request.GET['id_contrato']
		model_proyecto = Proyecto.objects.filter(contrato=id_contrato).values('id', 'nombre')
		# queryset = p.funcionario.all().values('id', 'nombre')
		
		# p = Proyecto.objects.get(pk=request.GET['proyecto_id'])
		# queryset = p.funcionario.all().values('id', 'id_cargo__nombre', 'persona__nombres' , 'persona__apellidos' , 'empresa__nombre')
		return JsonResponse({'message':'','success':'ok','data':list(model_proyecto)})
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})


def actualizarEstadoContrato(id,estado):
	nombre_modulo = 'Contrato - actualizarEstadoContrato'
	# sid = transaction.savepoint()
	try:
		result=Contrato.objects.get(pk=id)
		result.estado_id=estado
		result.save()

		# logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='contrato.contrato_vigencia',id_manipulado=id)
		# logs_model.save()

		# return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data':''})
		actualizarEstadoContrato2(id)
		# transaction.savepoint_commit(sid)
	except Exception as e:
		# transaction.savepoint_rollback(sid)
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def actualizarContratistaContrato(id,contratista):
	nombre_modulo = 'Contrato - actualizarContratistaContrato'
	sid = transaction.savepoint()
	try:
		result=Contrato.objects.get(pk=id)
		result.contratista_id=contratista
		result.save()

		# logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='contrato.contrato_vigencia',id_manipulado=id)
		# logs_model.save()

		# return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data':''})

		transaction.savepoint_commit(sid)
	except Exception as e:
		transaction.savepoint_rollback(sid)
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def actualizarEstadoContrato2(id):
	nombre_modulo = 'Contrato - actualizarEstadoContrato2'
	# sid = transaction.savepoint()
	try:
		tipo_v=tipoV()
		estado_c=estadoC()
		result = VigenciaContrato.objects.filter(contrato_id=id)
		cont = Contrato.objects.get(pk=id)
		# print "entroEstado2:"+str(id)

		if cont.estado_id != estado_c.suspendido and cont.estado_id != estado_c.liquidado:
			hoy = date.today()
			fecha_fin = ''
			formato_fecha = "%Y-%m-%d"
			a_inicio = None
			a_reinicio = None

			for vigencia in result:
				if vigencia.tipo.id == tipo_v.contrato:
					fecha_fin = vigencia.fecha_fin

			for vigencia in result:
				if vigencia.tipo.id == tipo_v.replanteo:
					fecha_fin = vigencia.fecha_fin

			for vigencia in result:
				if vigencia.tipo.id == tipo_v.otrosi or vigencia.tipo.id == tipo_v.actaAmpliacion:
					if vigencia.fecha_fin:
						fecha_fin = vigencia.fecha_fin

			fecha_fin = datetime.strptime(str(fecha_fin), formato_fecha)
			hoy = datetime.strptime(str(hoy), formato_fecha)
			for vigencia in result:

				if vigencia.tipo.id == tipo_v.actaSuspension:
					a_inicio = vigencia.fecha_inicio

				if vigencia.tipo.id == tipo_v.actaReinicio:
					a_reinicio = vigencia.fecha_inicio

				if a_reinicio != None and a_inicio != None:
					# print("a_inicio",a_inicio)
					# print("a_reinicio",a_reinicio)

					a_inicio = datetime.strptime(str(a_inicio), formato_fecha)
					a_reinicio = datetime.strptime(str(a_reinicio), formato_fecha)
					
					dias = a_reinicio - a_inicio
					# print "dias:"+str(dias.days)

					if dias.days > 0:
						fecha_fin = fecha_fin + timedelta(days=dias.days)

					a_inicio = None
					a_reinicio = None

			# print ("fec fin:",fecha_fin)
			diferencias = fecha_fin - hoy
			# print ("dias:",diferencias.days)

			if diferencias.days <= 0:
				cont.estado_id = estado_c.vencido
				# print "estd:"+str(cont.estado_id)
			if diferencias.days > 0 and diferencias.days <= 90:
				cont.estado_id = estado_c.porVencer
			if diferencias.days > 90:
				cont.estado_id = estado_c.vigente

			cont.save()
			# transaction.savepoint_commit(sid)

		# return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data':''})
	except Exception as e:
		# transaction.savepoint_rollback(sid)
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Exporta a excel vigencia contratos
def exportReporteVigenciaContrato(request):
	try:

		contrato= request.GET['id_contrato'] if request.GET['id_contrato'] else None
		contrato=Contrato.objects.get(id=int(contrato))
		tipo_v=tipoV()

		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="Reporte_vigencias_contrato_'+str(contrato.numero)+'.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Vigencias contrato')
		format1=workbook.add_format({'border':0,'font_size':12,'bold':True,'bg_color':'#4a89dc','font_color':'white'})
		format1.set_align('center')
		format1.set_align('vcenter')
		format2=workbook.add_format({'border':0})
		format3=workbook.add_format({'border':0,'font_size':12})
		format5=workbook.add_format()
		format5.set_num_format('yyyy-mm-dd')
		format_money=workbook.add_format({'border':0, 'num_format': '$#,##0.00'})

		row=1
		col=0

		worksheet.write('A1', 'Nombre Documento', format1)
		worksheet.write('B1', 'Nombre Contrato', format1)
		worksheet.write('C1', 'Numero Contrato', format1)
		worksheet.write('D1', 'Fecha Inicio', format1)
		worksheet.write('E1', 'Fecha Fin', format1)
		worksheet.write('F1', 'Valor', format1)
		worksheet.write('G1', 'Tipo de Vigencia', format1)
		worksheet.write('H1', 'Soporte', format1)
		worksheet.write('I1', 'Soporte compras', format1)

		worksheet.set_column('A:A', 20)
		worksheet.set_column('B:B', 60)
		worksheet.set_column('C:C', 25)
		worksheet.set_column('D:D', 15)
		worksheet.set_column('E:E', 15)
		worksheet.set_column('F:F', 25)
		worksheet.set_column('G:G', 20)
		worksheet.set_column('H:H', 20)
		worksheet.set_column('I:I', 20)

		#import pdb; pdb.set_trace()
		qset= (Q(contrato__id=contrato.id)) & (Q(tipo__id=tipo_v.contrato)| Q(tipo__id=tipo_v.otrosi) | Q(tipo__id=tipo_v.replanteo) | Q(tipo__id=tipo_v.liquidacion))
		Vigencias=VigenciaContrato.objects.filter(qset)

		for v in Vigencias:
			worksheet.write(row, col,v.nombre,format2)
			worksheet.write(row, col+1,contrato.nombre,format2)
			worksheet.write(row, col+2,contrato.numero,format2)
			worksheet.write(row, col+3,v.fecha_inicio,format5)
			worksheet.write(row, col+4,v.fecha_fin,format5)
			worksheet.write(row, col+5,v.valor,format_money)
			worksheet.write(row, col+6,v.tipo.nombre,format2)
			if v.soporte:
				worksheet.write(row, col+7,'Si',format2)
			else:
				worksheet.write(row, col+7,'No',format2)

			if v.acta_compra:
				worksheet.write(row, col+8,'Si',format2)
			else:
				worksheet.write(row, col+8,'No',format2)


			row +=1
		return response
	except Exception as e:
		# transaction.savepoint_rollback(sid)
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Exporta a excel contrato 
def exportReporteContrato2(request):
	estado_c=estadoC()
	tipo_v=tipoV()

	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="Reporte_contrato.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Contratos')
	format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
	format1.set_align('center')
	format1.set_align('vcenter')
	format2=workbook.add_format({'border':0})
	format3=workbook.add_format({'border':0,'font_size':12})
	format5=workbook.add_format()
	format5.set_num_format('yyyy-mm-dd')

	worksheet.set_column('A:A', 30)
	worksheet.set_column('B:E', 12)
	worksheet.set_column('F:H', 18)

	row=1
	col=0

	# cursor = connection.cursor()

	num_nom = None
	contrato_id = None
	id_tipo = None
	id_estado = None
	mcontrato = None
	id_empresa = request.user.usuario.empresa.id

	cadena = 'SELECT distinct c.[id] ,c.[nombre],c.[numero],es.nombre As estado,(select top 1 con.nombre from dbo.contrato con where con.id=c.mcontrato_id) as macro,(Select Top 1 cv.valor From dbo.contrato_vigencia As cv Where cv.tipo_id = '+str(tipo_v.contrato)+' And cv.contrato_id = c.id) As valor_contrato, (Select Top 1 cv.valor From dbo.contrato_vigencia As cv Where cv.tipo_id = '+str(tipo_v.replanteo)+' And cv.contrato_id = c.id order by cv.id desc) As valor_replante ,(Select Top 1 cv.valor From dbo.contrato_vigencia As cv Where cv.tipo_id = '+str(tipo_v.liquidacion)+' And cv.contrato_id = c.id order by cv.id desc) As valor_liquidacion, (Select Top 1 max([fecha_inicio]) From [dbo].contrato_vigencia Where contrato_id = c.[id] And [tipo_id] In('+str(tipo_v.contrato)+','+str(tipo_v.replanteo)+')) As fecha_inicio FROM [dbo].[contrato] As c Inner Join dbo.estado_estado		As es	On c.estado_id = es.id Inner Join dbo.contrato_empresa	As ce	On c.id = ce.contrato_id Where c.activo = 1 And ce.empresa_id = '+str(id_empresa)+' And ce.participa = 1 '


	if request.GET['dato']:
		num_nom = request.GET['dato']
		cadena = cadena+"And (c.nombre Like'%"+str(num_nom)+"%' or c.numero Like'%"+str(num_nom)+"%') "
	if request.GET['id_tipo']:
		id_tipo = request.GET['id_tipo']
		cadena = cadena+' And c.tipo_contrato_id = '+str(id_tipo)
	if request.GET['id_estado']:
		id_estado = request.GET['id_estado']
		cadena = cadena+' And c.estado_id In('+str(id_estado)+') '
	if request.GET['contratista_id']:
		contratista_id = request.GET['contratista_id']
		cadena = cadena+' And c.contratista_id = '+str(contratista_id)
	if request.GET['mcontrato']:
		mcontrato = request.GET['mcontrato']
		# thingy = list(map(str, mcontrato))
		# thingy = [str(item) for item in mcontrato]
		# definitions_list = [definition.encode("utf8") for definition in mcontrato]
		cadena = cadena+' And c.mcontrato_id In('+str(mcontrato)+') '

	# print cadena
	cursor = connection.cursor()
	cursor.execute(cadena)
	columns = cursor.description 
	qset = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
	# print qset

	formato_fecha = "%Y-%m-%d"

	if qset:
		worksheet.write('A1', 'Nombre del Macrocontrato', format1)
		worksheet.write('B1', 'Nombre', format1)
		worksheet.write('C1', 'Numero', format1)
		worksheet.write('D1', 'Fecha Inicio', format1)
		worksheet.write('E1', 'Fecha Fin', format1)
		worksheet.write('F1', 'Estado', format1)
		worksheet.write('G1', 'Valor Contrato', format1)
		worksheet.write('H1', 'Valor Replanteo', format1)
		worksheet.write('I1', 'Valor Liquidacion', format1)

	for contrato in qset:

		worksheet.write(row, col,contrato['macro'],format2)
		worksheet.write(row, col+1,contrato['nombre'],format2)
		worksheet.write(row, col+2,contrato['numero'],format2)
		worksheet.write(row, col+5,contrato['estado'],format2)
		worksheet.write(row, col+3,contrato['fecha_inicio'],format5)
		worksheet.write(row, col+6,contrato['valor_contrato'],format2)
		worksheet.write(row, col+7,contrato['valor_replante'],format2)
		worksheet.write(row, col+8,contrato['valor_liquidacion'],format2)

		cursor.callproc('[dbo].[consultar_dias_suspendico]',[contrato['id'],])#3 es el id de la notificacion 
		# columns = cursor.description 
		# personas_notificar = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		result_set = cursor.fetchall()

		worksheet.write(row, col+4,result_set[0][0],format5)

		row +=1
	workbook.close()
	return response

# Guardar los sub contratista
def createSubContratistaConLista(request):

	nombre_modulo = 'Contrato - createSubContratistaConLista'
	# print request.GET['proyecto_id']+"jj"
	empresa_id = request.GET['empresa_id']
	contrato_id = request.GET['contrato_id']
	# if request.method == 'POST':
	try:
		pass
		myList = empresa_id.split(',')

		for item in myList:
			if item:
				# print "lasas:"
				model_contrato = Contrato.objects.get(pk=contrato_id)
				model_contrato.sub_contratista.add(item)

		return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def listSubContratista(request):
	nombre_modulo = 'Contrato - listSubContratista'
	try:
		id_contrato=request.GET['id_contrato']
		
		if str(request.GET['dato']) != "":
			dato=request.GET['dato']
			# print "dd:"+request.GET['dato']
			# if dato:
			qset = (
				(Q(nombre__icontains=dato)|
				Q(nit__icontains=dato))#&
				# Q(id=id_contrato)
				)
			model_contrato = Contrato.objects.get(pk=id_contrato)
			# queryset = Contrato.objects.filter(qset).values('sub_contratista__id',  'sub_contratista__nombre')
			queryset = model_contrato.sub_contratista.filter(qset).values('id', 'nit', 'nombre')
		else:
			# print "jj"
			model_contrato = Contrato.objects.get(pk=id_contrato)
			queryset = model_contrato.sub_contratista.all().values('id', 'nit', 'nombre')
			#queryset = model_contrato.sub_contratista.felter(empresa__nombre__icontains=dato, empresa__nit__icontains=dato).values('id', 'nit', 'nombre')

		return JsonResponse({'message':'','success':'ok','data':list(queryset)})
	except Exception as e:
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})


# def destroySubContratista(request):
	# 	if request.method == 'POST':
	# 			try:
	# 				lista=request.POST['_content']
	# 				respuesta= json.loads(lista)
	# 				myList = respuesta['lista']

	# 				# for item in myList:
	# 				model_contrato = Contrato.objects.get(pk=respuesta['contrato'])
	# 				model_contrato.sub_contratista.remove(*myList)
	# 				# Proyecto.objects.filter(id = item ).delete()

	# 				# transaction.commit()
	# 				return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
	# 			except Exception as e:
	# 				print(e)
	# 				return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def destroySubContratista(request):
	nombre_modulo = 'Contrato - destroySubContratista'
	if request.method == 'POST':
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']

			for item in myList:
				print (item)
				model_contrato = Sub_contratista.objects.get(pk=item['id'])
				model_contrato.delete()
			# Proyecto.objects.filter(id = item ).delete()

			# transaction.commit()
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def destroyContratoCesion(request):
	nombre_modulo = 'Contrato - destroyContratoCesion'
	if request.method == 'POST':
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']

			for item in myList:
				print (item)
				model = Contrato_cesion.objects.get(pk=item['id'])
				model.delete()
			# Proyecto.objects.filter(id = item ).delete()

			# transaction.commit()
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def destroyCesionEconomica(request):
	nombre_modulo = 'Contrato - destroyCesionEconomica'
	if request.method == 'POST':
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']

			for item in myList:
				print (item)
				model = Cesion_economica.objects.get(pk=item['id'])
				model.delete()
			# Proyecto.objects.filter(id = item ).delete()

			# transaction.commit()
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Actuliza un el registro en poliza
def ActulizarPolizaVigenciaContrato(request, id_vigencia, tipo_documento, tipo_acta):
	nombre_modulo = 'Contrato - ActulizarPolizaVigenciaContrato'
	try:
		qset = (
			Q(poliza__contrato__id=request.DATA['contrato_id'])&#|
			Q(tipo_documento__id=tipo_documento)&
			Q(tipo_acta__id=tipo_acta)
		)

		queryset = VigenciaPoliza.objects.filter(qset).last()

		# print "Num:"+str(queryset.count())
		if queryset:
			# if queryset.documento_id is None:
			queryset.documento_id = id_vigencia
			queryset.save()

		return JsonResponse({'message':'','success':'ok','data':'OK'})
	except Exception as e:
		# print(e)
		functions.toLog(e, nombre_modulo)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def VerSoporte(request):
	if request.method == 'GET':
		try:
			
			archivo = VigenciaContrato.objects.get(pk=request.GET['id'])			
			return functions.exportarArchivoS3(str(archivo.soporte))

		except Exception as e:
			functions.toLog(e,'contrato.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			

@login_required
def VerSoporteCompra(request):
	if request.method == 'GET':
		try:
			
			archivo = VigenciaContrato.objects.get(pk=request.GET['id'])
			
			# if archivo.acta_compra :				
			return functions.exportarArchivoS3(str(archivo.acta_compra))

				
			# return JsonResponse({'message':'No se encontro el acta de compra','status':'error','data':''})
		except Exception as e:
			functions.toLog(e,'contrato.VerSoporteCompra')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)						

@login_required
@api_view(['GET',])
def validarPermiso(request):
	try:
		contratoId = request.query_params.get('contrato_id')
		contrato = Contrato.objects.get(pk=contratoId)
		newContratoId = None
		if contrato.mcontrato:
			newContratoId = contrato.mcontrato.id
		else:
			newContratoId = contrato.id

		contratoEmpresa = EmpresaContrato.objects.filter(contrato__id=newContratoId, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if contratoEmpresa is not None and contratoEmpresa.edita else True
		return Response({'message':'','success':'ok','data': {'solo_lectura': soloLectura}},status=status.HTTP_201_CREATED)
	except Exception as e:
		functions.toLog(e,'contrato.validarPermiso')
		return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)


class ActaAsignacionRecursosSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = ActaAsignacionRecursos
		fields = ('id','nombre','fechafirma',)

class ActaAsignacionRecursosContratoSerializer (serializers.HyperlinkedModelSerializer):

	actaAsignacion = ActaAsignacionRecursosSerializer(read_only=True)
	actaAsignacion_id = serializers.PrimaryKeyRelatedField(write_only=True, 
		queryset = ActaAsignacionRecursos.objects.all())

	contrato = ContratoLiteSerializerByDidi(read_only=True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True,
		queryset = Contrato.objects.all())

	class Meta:
		model = ActaAsignacionRecursosContrato
		fields = ('id','actaAsignacion','actaAsignacion_id',
			'contrato','contrato_id')

class ActaAsignacionRecursosContratoViewSet(viewsets.ModelViewSet):

	model=ActaAsignacionRecursosContrato
	queryset = model.objects.all()
	serializer_class = ActaAsignacionRecursosContratoSerializer
	nombre_modulo = 'Contrato - AsignacionRecursosViewSet'


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
			queryset = super(ActaAsignacionRecursosContratoViewSet, self).get_queryset()
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			contrato = self.request.query_params.get('contrato', None)

			mensaje=''

			qset = ~(Q(id=0))
			if contrato:
				qset = qset & (Q(contrato__id=contrato))

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
			return Response({'message':'Se presentaron errores al procesar su peticion','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

@login_required
def VerSoporteActaAdjudicacion(request):
	if request.method == 'GET':
		try:
			
			acta = ActaAsignacionRecursos.objects.get(pk=request.GET['id'])			
			return functions.exportarArchivoS3(str(acta.soporte))

		except Exception as e:
			functions.toLog(e,'contrato.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			