from django.db import transaction, connection
from django.shortcuts import render
from coasmedas.functions import functions
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from logs.models import Logs,Acciones
from django.db.models import Q,Sum,Prefetch,Max
from django.shortcuts import render,redirect,render_to_response
from .models import Bitacora
from proyecto.models import Proyecto
from contrato.models import Contrato
from usuario.models import Usuario
from usuario.views import UsuarioSerializer
from rest_framework import viewsets, serializers 
from parametrizacion.views import MunicipioSerializer , DepartamentoSerializer
from django.template import RequestContext
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

# Create your views here.

class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""
	class Meta:
		model = Contrato
		fields=('id' , 'nombre'	)

class ProyectoLiteSerializer(serializers.HyperlinkedModelSerializer):
	mcontrato = ContratoLiteSerializer(read_only = True)
	municipio = MunicipioSerializer(read_only = True)
	
	class Meta: 
		model = Proyecto
		fields=( 'id', 'nombre', 'mcontrato', 'municipio',)

class BitacoraSerializer(serializers.HyperlinkedModelSerializer):
	proyecto = ContratoLiteSerializer(read_only=True)
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Proyecto.objects.all())	
	usuario = UsuarioSerializer(read_only=True)
	usuario_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Usuario.objects.all())	
	class Meta:
		model = Bitacora
		fields=('id', 'comentario', 'usuario', 'usuario_id', 'proyecto', 'proyecto_id', 'fecha', 'minutos')

class BitacoraViewSet(viewsets.ModelViewSet):
	model=Bitacora
	queryset = model.objects.all()
	serializer_class = BitacoraSerializer	
	paginate_by = 20
	nombre_modulo = 'bitacora'
	
	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
			
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(BitacoraViewSet, self).get_queryset()
			paginacion = self.request.query_params.get('sin_paginacion', None)
			dato = self.request.query_params.get('dato', None)
			proyecto_id = self.request.query_params.get('proyecto_id', None)
			usuario_id = self.request.query_params.get('usuario_id', None)
			fecha_inicio = self.request.query_params.get('fecha_inicio', None)
			fecha_final = self.request.query_params.get('fecha_final', None)
			
			qset=(~Q(id=0))

			if dato or proyecto_id or usuario_id or (fecha_inicio and fecha_final):
				if dato:					
					qset=(Q(proyecto__nombre__icontains=dato) | Q(proyecto__mcontrato__nombre__icontains=dato) |
						Q(usuario__persona__nombres__icontains=dato) | Q(usuario__persona__apellidos__icontains=dato))	
				if proyecto_id:
					qset=qset & (Q(proyecto__id=proyecto_id))	
				if usuario_id:
					qset=qset & (Q(usuario__id=usuario_id))
				if fecha_inicio and fecha_final:
					qset=qset & (Q(fecha__range=(fecha_inicio, '{} {}'.format(fecha_final, '23:59:59'))))
				if fecha_inicio and fecha_final == None:
					qset=qset & (Q(fecha__range=(fecha_inicio, '{} {}'.format(fecha_inicio, '23:59:59'))))
				if fecha_inicio == None and fecha_final:
					qset=qset & (Q(fecha__range=(fecha_final, '{} {}'.format(fecha_final, '23:59:59'))))
				queryset = self.model.objects.filter(qset).order_by('-id')
					

			if paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})
			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})	
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = BitacoraSerializer(data=request.DATA,context={'request': request})
				
				if serializer.is_valid():
					serializer.save(proyecto_id=request.DATA['proyecto_id'], usuario_id=request.DATA['usuario_id'])
					
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='bitacora.bitacora',id_manipulado=serializer.data['id'])
					logs_model.save()
					
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
				
	@transaction.atomic			
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = BitacoraSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():
					serializer.save(proyecto_id=request.DATA['proyecto_id'], usuario_id=request.DATA['usuario_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='bitacora.bitacora',id_manipulado=instance.id)
					logs_model.save()
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
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
			if instance.minutos()<=10:				
				self.perform_destroy(instance)
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='bitacora.bitacora',id_manipulado=instance.id)
				logs_model.save()
				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
			else:
				return Response({'message':'No puede eliminar el registro','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

#fin bitacora

@login_required
def bitacora(request, proyecto_id):
	proyecto = Proyecto.objects.get(pk=proyecto_id)	
	return render(request, 'bitacora.html', 
	{'model':'bitacora','app':'bitacora', 'proyecto': proyecto})


@api_view(['GET'])
def obtener_usuario(request, proyecto_id):
	try:
		usuarios=Bitacora.objects.filter(proyecto__id=proyecto_id).distinct().values('usuario__id', 'usuario__persona__apellidos', 'usuario__persona__nombres')
		return Response({'message':'','success':'ok','data':usuarios})	
	except Exception as e:
		functions.toLog(e,'bitacora')		
		return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
