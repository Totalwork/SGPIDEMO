from django.shortcuts import render
#, render_to_response
from rest_framework import viewsets, serializers, response
from django.db.models import Q
from django.template import RequestContext
from .models import Ubicacion
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
#import xlsxwriter
import json
from django.http import HttpResponse,JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser

from logs.models import Logs, Acciones
from proyecto.models import Proyecto
from proyecto.views import ProyectoSerializer


#Api rest para Ubicacion
class UbicacionSerializer(serializers.HyperlinkedModelSerializer):
	proyecto = ProyectoSerializer(read_only=True)

	class Meta:
		model = Ubicacion
		fields=('id','nombre','longitud','latitud')


class UbicacionViewSet(viewsets.ModelViewSet):

	model=Ubicacion
	model_log=Logs
	model_acciones=Acciones
	nombre_modulo='ubicacion.ubicacion'
	queryset = model.objects.all()
	serializer_class = UbicacionSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			paginacion = self.request.query_params.get('sin_paginacion', None)


			queryset = super(UbicacionViewSet, self).get_queryset()
			#con busqueda en un solo campo:
			# valorEsContratista = self.request.query_params.get('nombre', None)
			# if valorEsContratista:
			# 	queryset = queryset.filter(nombre__icontains=valorEsContratista)
			dato = self.request.query_params.get('dato', None)
			qset=(Q(proyecto=request.user.usuario.proyecto.id))

			if dato:
				qset = qset & (Q(nombre__icontains=dato))

			queryset = self.model.objects.filter(qset)

			if paginacion==None:

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
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				serializer = UbicacionSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(proyecto_id=request.user.usuario.proyecto.id)
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo)
					logs_model.save()
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
				serializer = UbicacionSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(proyecto_id=request.user.usuario.proyecto.id)
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo)
					logs_model.save()
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
#Fin Api rest para Ubicacion

def Ubicacion(request, num="1"):
	return render(request, 'ubicacion/ubicacion.html',{'app':'ubicacion','model':'ubicacion', 'proyecto_id': num})