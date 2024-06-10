from django.shortcuts import render,redirect
#, render_to_response
from django.urls import reverse
from rest_framework import viewsets, serializers
from django.db.models import Q
from .models import Opcion, Opcion_Usuario
from usuario.models import Usuario
from django.views.generic import ListView

from django import template
from django.http import HttpResponse
from django.template import Context, loader
from django.template import RequestContext
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import Permission


# Create your views here.
#Api rest para Opcion

#Serializador recursivo
class PermisoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Permission
		fields = ('id','name','codename', 'content_type')

class OpcionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Opcion
		fields=('id','orden','texto','destino','icono', 'padre', 'children', 'permiso')

	def get_fields(self):
		fields = super(OpcionSerializer, self).get_fields()
		fields['children'] = OpcionSerializer(many=True)
		fields['permiso'] = PermisoSerializer()
		return fields

class OpcionViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de Opcions, puede utilizar el parametro (dato) a traver del cual, se podra buscar por todo o parte del nombre, tambien puede ser buscado por sus iniciales.
	"""
	model=Opcion
	queryset = model.objects.all()
	serializer_class = OpcionSerializer

#Fin api rest para Opcion

#Api rest para Opcion_Usuario

#Serializador recursivo
class Opcion_UsuarioSerializer(serializers.ModelSerializer):
	opcion = OpcionSerializer();
	class Meta:
		model = Opcion_Usuario
		fields=('id','opcion','usuario')

class Opcion_UsuarioViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de Opcion_Usuarios, puede utilizar el parametro (dato) a traver del cual, se podra buscar por todo o parte del nombre, tambien puede ser buscado por sus iniciales.
	"""
	model=Opcion_Usuario
	queryset = model.objects.all()
	serializer_class = Opcion_UsuarioSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(Opcion_UsuarioViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			if dato:
				qset = (
					Q(etiqueta__icontains=dato)
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
				serializer = Opcion_UsuarioSerializer(data=request.DATA,context={'request': request})

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
				serializer = Opcion_UsuarioSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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

#Fin Api rest para Opcion_Usuario