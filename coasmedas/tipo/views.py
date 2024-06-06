from django.shortcuts import render
from rest_framework import viewsets, serializers, response
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

from .models import Tipo

from coasmedas.functions import functions

# Create your views here.

# Api Tipos.
class TipoSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = Tipo
		fields=( 'id','app', 'nombre' , 'icono' , 'color')

class TipoLiteSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = Tipo
		fields=( 'id','nombre')

class TipoViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de tipos, puede utilizar el parametro <b>{dato=[texto a buscar]}</b>, a traves del cual, se podra buscar por todo o parte del nombre y aplicacion.<br/>
		Igualmente puede utilizar los siguientes parametros:<br/><br/>

		<b>{aplicacion=TEXTO}</b>: Retorna la lista de tipos  con el nombre de la aplicacion del TEXTO escrito.<br/>
		Es posible utilizar los parametros combinados, por ejemplo: buscar en la lista de tipos aquellos que contentan determinado texto en su nombre o aplicacion.
	"""
	model=Tipo
	queryset = model.objects.all()
	serializer_class = TipoSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo = 'tipo - TipoViewSet'

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
			queryset = super(TipoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			aplicacion= self.request.query_params.get('aplicacion',None)
			lite = self.request.query_params.get('lite', None)
			
			if (dato or aplicacion):
				if dato:
					qset = (
						Q(nombre__icontains=dato) |
						Q(app__icontains=dato)
						)
				if aplicacion:
					qset = (
						Q(app__exact = aplicacion )
						)

				queryset = self.model.objects.filter(qset)

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			serializer_context = {
				'request': request,
			}

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			if lite is not None:
				serializer = TipoLiteSerializer(queryset, many=True, context=serializer_context)
			else:
				serializer = self.get_serializer(queryset,many=True)

			return Response({'message':'','success':'ok','data':serializer.data})			
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			##print request.DATA				
			try:
				serializer = TipoSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save()					
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
	

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = TipoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					self.perform_update(serializer)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
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
