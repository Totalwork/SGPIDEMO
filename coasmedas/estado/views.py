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


from .models import Estado , Estados_posibles


# Api estados.
class EstadoSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Estado
		fields=('id', 'app', 'nombre', 'icono', 'color','codigo')

class EstadoLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Estado
		fields=('id','nombre')

class EstadoLite2Serializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Estado
		fields=('id', 'nombre', 'color')

class EstadoViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de estados, puede utilizar el parametro <b>{dato=[texto a buscar]}</b>, a traves del cual, se podra buscar por todo o parte del nombre y aplicacion.<br/>
		Igualmente puede utilizar los siguientes parametros:<br/><br/>

		<b>{aplicacion=TEXTO}</b>: Retorna la lista de estados  con el nombre de la aplicacion del TEXTO escrito.<br/>
		Es posible utilizar los parametros combinados, por ejemplo: buscar en la lista de estados aquellos que contentan determinado texto en su nombre o aplicacion.
	"""
	model=Estado
	queryset = model.objects.all()
	serializer_class = EstadoSerializer
	parser_classes=(FormParser, MultiPartParser,)
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
			queryset = super(EstadoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			aplicacion= self.request.query_params.get('aplicacion',None)
			
			if (dato or aplicacion):
				if dato:
					qset = (
						Q(nombre__icontains=dato) |
						Q(app__icontains=dato)
						)
				if aplicacion:
					qset = (
						Q(app__exact=aplicacion)
						)

				queryset = self.model.objects.filter(qset).order_by('orden')
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
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
				serializer = EstadoSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save()
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
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
				serializer = EstadoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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


# Api posibles estados.
class EstadosPosiblesSerializer(serializers.HyperlinkedModelSerializer):

	actual = EstadoSerializer(read_only = True)
	actual_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Estado.objects.all())

	siguiente = EstadoSerializer(read_only = True)
	siguiente_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Estado.objects.all())
	
	class Meta:
		model = Estados_posibles
		fields=( 'id','actual' , 'actual_id' , 'siguiente' , 'siguiente_id')



class EstadosPosiblesViewSet(viewsets.ModelViewSet):
	"""
		"""
	model = Estados_posibles
	queryset = model.objects.all()
	serializer_class = EstadosPosiblesSerializer
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
			queryset = super(EstadosPosiblesViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			actual = self.request.query_params.get('actual', None)
			siguiente = self.request.query_params.get('siguiente', None)
			
			qset=(~Q(id=0))
			if (dato or actual or siguiente):
				if dato:
					qset = qset & ( Q(actual__nombre__icontains=dato) )

				if actual:
					qset = qset &( Q(actual_id = actual) )

				if siguiente:
					qset = qset &( Q(siguiente_id = siguiente) )

				queryset = self.model.objects.filter(qset)
			
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
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
			#try:
				serializer = EstadosPosiblesSerializer(data=request.DATA,context={'request': request})


				if serializer.is_valid():
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			#except Exception as e:
					# return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					# 'data':''},status=status.HTTP_400_BAD_REQUEST)
	

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = EstadosPosiblesSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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