from django.shortcuts import render
#, render_to_response
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

from .models import Cuenta , Cuenta_movimiento
from tipo.models import Tipo
from tipo.views import TipoSerializer

from empresa.models import Empresa
from empresa.views import EmpresaSerializer

from contrato.models import Contrato
from contrato.views import ContratoSerializer

# Create your views here.
class CuentaSerializer(serializers.HyperlinkedModelSerializer):
	
	tipo = TipoSerializer(read_only = True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Tipo.objects.filter(app="cuenta"))

	contrato = ContratoSerializer(read_only = True)
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Contrato.objects.all())

	empresa = EmpresaSerializer(read_only = True)

	class Meta:
		model = Cuenta
		fields=( 'id','nombre', 'numero' , 'valor' , 'fiduciaria' , 'codigo_fidecomiso' , 'codigo_fidecomiso_a' , 
				 'contrato' , 'contrato_id' , 
				 'empresa' , 
				 'tipo' , 'tipo_id')

class CuentaViewSet(viewsets.ModelViewSet):
	"""
		"""
	model = Cuenta
	queryset = model.objects.all()
	serializer_class = CuentaSerializer
	parser_classes = (FormParser, MultiPartParser,)
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
			queryset = super(CuentaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			
			if (dato):
				if dato:
					qset = (
						Q(nombre__icontains=dato)
						)

				queryset = self.model.objects.filter(qset)
			
			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page,many=True)	
				return self.get_paginated_response({'message':'','success':'ok',
				'data':serializer.data})

			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})			
		except Exception as e:
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			##print request.DATA				
			try:
				serializer = CuentaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(tipo_id = request.DATA['tipo_id'],
						            empresa_id = request.user.usuario.empresa.id,
						            contrato_id = request.DATA['contrato_id'])
				
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
					return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
	

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = CuentaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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

# Create your views here.
class CuentaMovimientoSerializer(serializers.HyperlinkedModelSerializer):
	
	tipo = TipoSerializer(read_only = True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Tipo.objects.filter(app="cuenta_movimiento"))

	cuenta = CuentaSerializer(read_only = True)
	cuenta_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Cuenta.objects.all())

	class Meta:
		model = Cuenta_movimiento
		fields=( 'id','cuenta', 'cuenta_id' ,
				 'tipo' , 'tipo_id' , 'valor' , 'descripcion' , 'fecha' , 'periodo_inicial' , 
				 'periodo_final' , 'ano' )



class CuentaMovimientoViewSet(viewsets.ModelViewSet):
	"""
		"""
	model = Cuenta_movimiento
	queryset = model.objects.all()
	serializer_class = CuentaMovimientoSerializer
	parser_classes = (FormParser, MultiPartParser,)
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
			queryset = super(CuentaMovimientoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			
			if (dato):
				if dato:
					qset = (
						Q(nombre__icontains=dato)
						)

				queryset = self.model.objects.filter(qset)
			
			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page,many=True)	
				return self.get_paginated_response({'message':'','success':'ok',
				'data':serializer.data})

			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})			
		except Exception as e:
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				serializer = CuentaMovimientoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(tipo_id = request.DATA['tipo_id'],
						            cuenta_id = request.DATA['cuenta_id'])
				
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
					print(e)
					return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
	

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = CuentaMovimientoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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

def cuenta(request):
		return render(request, 'cuenta/cuenta.html', {'model':'cuenta','app':'cuenta'})		

