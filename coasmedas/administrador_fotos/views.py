from django.shortcuts import render,redirect
#,render_to_response
from django.urls import reverse
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
from p_p_construccion.models import ALote
from tipo.models import Tipo
from tipo.views import TipoSerializer
from contrato.models import Contrato
from contrato.views import ContratoSerializer
from proyecto.models import Proyecto,Proyecto_empresas
from empresa.models import Empresa
from parametrizacion.models import Municipio , Departamento
from parametrizacion.views import  MunicipioSerializer , DepartamentoSerializer
from proyecto.views import ProyectoSerializer
from puntos_gps.views import PuntosGps
from control_cambios.views import CCambio
from .models import ACategoria,BSubcategoria,CFotosProyecto,DFotosSubcategoria
from logs.models import Logs,Acciones
from datetime import *
from django.db import transaction,connection
from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required

from avance_de_obra.models import BCronograma
from avanceObraGrafico.models import EPresupuesto

from avanceObraGrafico2.models import Cronograma
from coasmedas.functions import functions

from contrato.enumeration import tipoC


# Serializer de proyecto
class ProyectoLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre')


# Serializador de contrato
class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Contrato
		fields=('id','nombre', 'contratista')

#Api rest para categoria de administrador de fotos
class CategoriaSerializer(serializers.HyperlinkedModelSerializer):
	
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto.objects.all())
	proyecto=ProyectoLiteSerializer(read_only=True)

	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Contrato.objects.all())
	contrato=ContratoLiteSerializer(read_only=True)

	totalSubCategoria = serializers.SerializerMethodField()

	class Meta:
		model = ACategoria
		fields=('id','proyecto','proyecto_id','categoria','contrato','contrato_id','totalSubCategoria')


	def get_totalSubCategoria(self, obj):

		parametro_contar=self.context.get("cantidad")

		cantidad=BSubcategoria.objects.filter(categoria_id=obj.id,proyecto_id=parametro_contar).count()

		return cantidad


class CategoriaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista las categorias de administrador de fotos
	"""
	model=ACategoria
	queryset = model.objects.all()
	serializer_class = CategoriaSerializer
	nombre_modulo='administrador_foto.categoria'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CategoriaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			contrato= self.request.query_params.get('contrato',None)
			proyecto= self.request.query_params.get('proyecto',None)
			categoria_id= self.request.query_params.get('categoria_id',None)
			sin_paginacion = self.request.query_params.get('sin_paginacion', None)
			id_empresa = request.user.usuario.empresa.id
			tipo_contrato=self.request.query_params.get('tipo_contrato', None)
			qset=None

			if (dato or contrato or proyecto or categoria_id or id_empresa):

				qset = Q(contrato__empresacontrato__empresa=id_empresa)

				if contrato and int(contrato)>0:
					qset = qset &(
						Q(contrato__id=contrato)
					)


				if tipo_contrato and int(tipo_contrato)>0:
					qset = qset &(
						Q(proyecto__contrato__tipo_contrato__id=tipo_contrato)
					)


				if categoria_id and int(categoria_id)>0:
					qset = qset &(
						Q(id=categoria_id)
					)


				if proyecto and int(proyecto)>0:
					qset = qset &(
						Q(proyecto__id=proyecto)
					)


				if dato:
					qset = qset &(
						Q(categoria__icontains=dato)
					)
			
				queryset = self.model.objects.filter(qset)

			parametro_contar=self.request.query_params.get('parametro_contar', 0)

			serializer_context = {
				'request': request,
				'cantidad' : parametro_contar,
			}

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = CategoriaSerializer(page,many=True,context=serializer_context)	
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
			#print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = CategoriaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():

					serializer.save(proyecto_id=request.DATA['proyecto_id'],contrato_id=request.DATA['contrato_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='administrador_foto.categoria',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				#print(e)
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)


	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()

			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = CategoriaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(proyecto_id=request.DATA['proyecto_id'],contrato_id=request.DATA['contrato_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='administrador_foto.categoria',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
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


#Fin api rest para categorias de administrador de fotos

#Serializer de categoria
class CategoriaLiteSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = ACategoria
		fields=('id','categoria')


#Api rest para las subcategorias de administrador de fotos
class SubcategoriaSerializer(serializers.HyperlinkedModelSerializer):

	categoria_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=ACategoria.objects.all())
	categoria=CategoriaLiteSerializer(read_only=True)

	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto.objects.all())
	proyecto=ProyectoLiteSerializer(read_only=True)

	class Meta:
		model = BSubcategoria
		fields=('id','categoria','categoria_id','titulo','contenido','proyecto','proyecto_id','cantidad_fotos_subcategoria')


class SubcategoriaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de movientos de las cuentas del financiero.
	"""
	model=BSubcategoria
	queryset = model.objects.all()
	serializer_class = SubcategoriaSerializer
	nombre_modulo='administrador_foto.subcategoria'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:

			queryset = super(SubcategoriaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			# desde= self.request.query_params.get('desde',None)
			#hasta= self.request.query_params.get('hasta',None)
			categoria= self.request.query_params.get('id_categoria',None)
			proyecto= self.request.query_params.get('id_proyecto',None)
			sin_paginacion=self.request.query_params.get('sin_paginacion',None)
			subcategoria_id= self.request.query_params.get('subcategoria_id',None)
			id_empresa = request.user.usuario.empresa.id
			tipo_contrato=self.request.query_params.get('tipo_contrato', None)
			listado_categoria=self.request.query_params.get('lista', None)
			qset=None

			if listado_categoria:
				lista_cate=listado_categoria.split(',')
				lista_cate = list(map(int, lista_cate))

			if (dato or categoria or proyecto or subcategoria_id or id_empresa):

				qset = Q(categoria__contrato__empresacontrato__empresa=id_empresa)

				if categoria and int(categoria)>0:
					qset = qset &(
						Q(categoria__id=categoria)
					)


				if tipo_contrato and int(tipo_contrato)>0:
					qset = qset &(
						Q(categoria__proyecto__contrato__tipo_contrato__id=tipo_contrato)
					)


				if subcategoria_id and int(subcategoria_id)>0:
					qset = qset &(
						Q(id=subcategoria_id)
					)


				if proyecto and int(proyecto)>0:
					qset = qset &(
						Q(proyecto__id=proyecto)
					)


				if dato:
					qset = qset &(
						Q(titulo__icontains=dato)
					)


				if listado_categoria:

					if lista_cate:

						if qset != None:
							qset = qset &(
								Q(categoria__id__in=lista_cate)
								)
						else:
							qset = (
								Q(categoria__id__in=lista_cate)
								)


			#print qset
			if qset != '':
				queryset = self.model.objects.filter(qset)

			if sin_paginacion is None:	
	
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					#print serializer
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
			#print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()

			try:
				serializer = SubcategoriaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(categoria_id=request.DATA['categoria_id'],proyecto_id=request.DATA['proyecto_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='administrador_foto.subcategoria',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				#print(e)
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)	


	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()

			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = SubcategoriaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(categoria_id=request.DATA['categoria_id'],proyecto_id=request.DATA['proyecto_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='administrador_foto.subcategoria',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
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


#Fin api rest para subcategoria de administrador de fotos




#Api rest para fotos proyecto de administrador de fotos
class FotosProyectoSerializer(serializers.HyperlinkedModelSerializer):
	
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto.objects.all())
	proyecto=ProyectoLiteSerializer(read_only=True)

	tipo = TipoSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='administradorFotos'),allow_null=True,default=None)

	fecha = serializers.DateField(format=None)

	class Meta:
		model = CFotosProyecto
		fields=('id','proyecto','proyecto_id','fecha','ruta','comentarios','asociado_reporte','tipo','tipo_id', 'ruta_publica')


class FotosProyectoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de las fotos del Proyecto de administrador de fotos
	"""
	model=CFotosProyecto
	queryset = model.objects.all()
	serializer_class = FotosProyectoSerializer
	nombre_modulo='administrador_foto.fotos_proyecto'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(FotosProyectoViewSet, self).get_queryset()
			categoria_id = self.request.query_params.get('id', None)
			dato = self.request.query_params.get('dato', None)
			sin_paginacion = self.request.query_params.get('sin_paginacion', None)
			proyecto_id = self.request.query_params.get('proyecto_id', None)
			tipo_id = self.request.query_params.get('tipo_id', None)
			desde = self.request.query_params.get('desde', None)
			hasta = self.request.query_params.get('hasta', None)
			tipo_foto = self.request.query_params.get('tipo_foto', None)
			asociado = self.request.query_params.get('asociado', None)
			id_empresa = request.user.usuario.empresa.id
			tipo_contrato=self.request.query_params.get('tipo_contrato', None)
			qset=None

			if (dato or categoria_id or proyecto_id or tipo_id or desde or hasta or tipo_foto or asociado or id_empresa or tipo_contrato):

				qset = Q(proyecto__mcontrato__empresacontrato__empresa=id_empresa)

				if proyecto_id  and int(proyecto_id)>0:
					qset = qset & (Q(proyecto__id = proyecto_id))

				if tipo_contrato and int(tipo_contrato)>0:
					qset = qset & (Q(proyecto__contrato__tipo_contrato__id = tipo_contrato))

				if categoria_id  and int(categoria_id)>0:

					qset = qset & (Q(id=categoria_id))

				if tipo_id and int(tipo_id)>0:

					qset = qset & (Q(tipo__id=tipo_id))	
					

				if (desde and (hasta is not None)):

					qset = qset & (Q(fecha__gte=desde))


				if(desde and hasta):

					qset = qset &(Q(fecha__gte=desde) and Q(fecha__lte=hasta))


				if tipo_foto and int(tipo_foto)>0:

					qset =qset &(Q(tipo__id=tipo_foto))


				if asociado and int(asociado)!=2:

					qset =qset &(Q(asociado_reporte=asociado))							


			if qset is not None:
				queryset = self.model.objects.filter(qset)

			if sin_paginacion is None:
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
			#print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()

			try:
				lista=self.request.FILES.getlist('archivo[]')
				for item in lista:
					serializer = FotosProyectoSerializer(data=request.DATA,context={'request': request})				
					## print item
					if serializer.is_valid():
						##print request.DATA['fecha']
						serializer.save(proyecto_id=request.DATA['proyecto_id'],tipo_id=request.DATA['tipo_id'],ruta=item)
						#print 'asddas'

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='administrador_foto.FotosProyecto',id_manipulado=serializer.data['id'])
						logs_model.save()

						transaction.savepoint_commit(sid)
					else:
						print(serializer.errors)
						return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)

				return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				

			except Exception as e:
				#print(e)
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)	


	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()

			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = FotosProyectoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(proyecto_id=request.DATA['proyecto_id'],tipo_id=request.DATA['tipo_id'], ruta=self.request.FILES.get('ruta'))

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='administrador_foto.FotosProyecto',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
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


#Fin api rest para las fotos del proyecto de administrador de fotos

#Serializer de subcategoria
class SubcategoriaLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = BSubcategoria
		fields=('id','categoria','titulo','contenido')

#Api rest para fotos subcategorias de administrador de las fotos
class FotosSubcategoriaSerializer(serializers.HyperlinkedModelSerializer):

	subcategoria_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=BSubcategoria.objects.all())
	subcategoria=SubcategoriaLiteSerializer(read_only=True)
	ruta_publica = serializers.SerializerMethodField()

	class Meta:
		model = DFotosSubcategoria
		fields=('id','subcategoria','subcategoria_id','ruta','ruta_publica','cantidad_fotosSubcategoria','mes','ano')
	def get_ruta_publica(self,obj):
		if obj.ruta:			
			return functions.crearRutaTemporalArchivoS3(str(obj.ruta))
		else:
	 		return None


class FotosSubcategoriaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de movientos de las cuentas del financiero.
	"""
	model=DFotosSubcategoria
	queryset = model.objects.all()
	serializer_class = FotosSubcategoriaSerializer
	nombre_modulo='administrador_foto.fotos_subcategorias'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:

			queryset = super(FotosSubcategoriaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			subcategoria_id= self.request.query_params.get('subcategoria_id',None)
			sin_paginacion=self.request.query_params.get('sin_paginacion',None)
			id_empresa = request.user.usuario.empresa.id
			tipo_contrato=self.request.query_params.get('tipo_contrato', None)
			mes=self.request.query_params.get('mes', None)
			ano=self.request.query_params.get('ano', None)
			listado_subcategoria=self.request.query_params.get('lista', None)
			qset=None


			if listado_subcategoria:
				lista_sub=listado_subcategoria.split(',')
				lista_sub = list(map(int, lista_sub))

			if (dato or subcategoria_id or id_empresa):

				qset = Q(subcategoria__categoria__contrato__empresacontrato__empresa=id_empresa)

				if subcategoria_id and int(subcategoria_id)>0:
					qset = qset &(
						Q(subcategoria__id=subcategoria_id)
					)


				if tipo_contrato and int(tipo_contrato)>0:
					qset = qset &(
						Q(subcategoria__categoria__proyecto__contrato__tipo_contrato__id=tipo_contrato)
					)


				if mes:
					qset = qset &(
						Q(mes=mes)
					)


				if ano:
					qset = qset &(
						Q(ano=ano)
					)

				if listado_subcategoria:
					if lista_sub:

						if qset != None:
							qset = qset &(
								Q(subcategoria__id__in=lista_sub)
							)
						else:
							qset = (
								Q(subcategoria__id__in=lista_sub)
							)

			#print qset
			if qset != '':
				queryset = self.model.objects.filter(qset)

			if sin_paginacion is None:	
	
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					#print serializer
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
			#print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()

			try:
				lista=self.request.FILES.getlist('archivo[]')
				for item in lista:
					serializer = FotosSubcategoriaSerializer(data=request.DATA,context={'request': request})				
					## print item
					if serializer.is_valid():
						
						serializer.save(subcategoria_id=request.DATA['subcategoria_id'], ruta=item)

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='administrador_foto.FotosSubcategoria',id_manipulado=serializer.data['id'])
						logs_model.save()

						transaction.savepoint_commit(sid)
					else:
						print(serializer.errors)
						return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)

				return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				

			except Exception as e:
				#print(e)
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)	


	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()

			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = FotosSubcategoriaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(subcategoria_id=request.DATA['subcategoria_id'], ruta=self.request.FILES.get('ruta'))

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='administrador_foto.FotosSubcategoria',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
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


#Fin api rest para fotos subcategorias

@login_required
def CategoriaAdministrador(request,id_proyecto=None,id_contrato=None):
	qsProyecto=Proyecto.objects.filter(id=id_proyecto).first()

	return render(request, 'categoria.html',{'proyecto':qsProyecto,'app':'administrador_fotos','model':'acategoria','id_proyecto':id_proyecto,'id_contrato':id_contrato})		

@login_required
def SubcategoriaAdministrador(request,id_proyecto=None,id_categoria=None,id_contrato=None):

	qsCategoria=ACategoria.objects.filter(id=id_categoria,contrato_id=id_contrato).first()
	#qsProyecto=ACategoria.objects.filter(proyecto_id=id_proyecto,contrato_id=id_contrato).first()
	qsProyecto=Proyecto.objects.filter(id=id_proyecto).first()
	
	return render(request, 'subcategoria.html',{'proyecto':qsProyecto,'categoria':qsCategoria,'app':'administrador_fotos','model':'bsubcategoria','id_proyecto':id_proyecto,'id_categoria':id_categoria,'id_contrato':id_contrato})

@login_required
def FotosProyectoAdministrador(request,id_proyecto=None):

	qsProyecto=Proyecto.objects.filter(id=id_proyecto).first()
	tipo_contrato = tipoC()
	nombre_contratista=""
	for item in qsProyecto.contrato.all():
		if item.tipo_contrato.id == tipo_contrato.contratoProyecto:
			nombre_contratista=item.contratista.nombre

	return render(request, 'fotos_proyectos.html',{'proyecto':qsProyecto,'nombre_contratista':nombre_contratista,'app':'administrador_fotos','model':'cfotosproyecto','id_proyecto':id_proyecto})


@login_required
def FotosSubcategoriaAdministrador(request,id_subcategoria=None,id_proyecto=None,id_categoria=None,id_contrato=None):

	qsFotosSubcategoria=BSubcategoria.objects.filter(id=id_subcategoria, categoria_id=id_categoria).first()
	return render(request, 'fotos_subcategoria.html',{'fotos_subcategoria':qsFotosSubcategoria,'app':'administrador_fotos','model':'dfotossubcategoria','id_subcategoria':id_subcategoria,'id_proyecto':id_proyecto,'id_categoria':id_categoria,'id_contrato':id_contrato})				

@login_required				
def AdministradorFotos(request):

	return render(request, 'administrador_fotos.html',{'app':'administrador_fotos'})				
				


#eliminar las categorias
@transaction.atomic
def eliminar_varios_id(request):
	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			ACategoria.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='administrador_foto.categoria',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})

	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})
		
	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})			 
		


#eliminar las subcategorias
@transaction.atomic
def eliminar_varias_subcategorias(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			BSubcategoria.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='administrador_fotos.subcategoria',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})	
		
	except Exception as e:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})



#eliminar las fotos subcategorias
@transaction.atomic
def eliminar_varias_fotos_subcategorias(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			DFotosSubcategoria.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='administrador_fotos.subcategoria_fotos',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})	
		
	except Exception as e:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})


#eliminar las fotos de las subcategorias
@transaction.atomic
def eliminar_varias_fotos_subcategorias(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			DFotosSubcategoria.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='administrador_foto.fotos_subcategorias',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})	
		
	except Exception as e:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})		


#eliminar las fotos del proyecto
@transaction.atomic
def eliminar_varias_fotos_proyecto(request):

	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			CFotosProyecto.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='administrador_foto.fotos_proyecto',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})	
		
	except Exception as e:
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})		





#exportar las categorias
def export_excel_categoria(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="categoria.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Categorias')
	format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
	format2=workbook.add_format({'border':0})
	format3=workbook.add_format({'border':0,'font_size':12})
	format5=workbook.add_format()
	format5.set_num_format('yyyy-mm-dd')

	row=1
	col=0

	cursor = connection.cursor()

	contrato= request.GET['contrato']
	proyecto= request.GET['proyecto']
	qset=None

	if contrato != None:
				
		if qset != None:
			 		
			qset = qset &(
			 			Q(contrato__id=contrato)
			)
		else:
			qset = (
					Q(contrato__id=contrato)
			)

	# if proyecto != None:
				
	# 	if qset != None:
			 		
	# 		qset = qset &(
	# 		 			Q(proyecto__id=proyecto)
	# 		)
	# 	else:
	# 		qset = (
	# 				Q(proyecto__id=proyecto)
	# 		)

				
		categoria = ACategoria.objects.filter(qset)

		worksheet.write('A1', 'Contrato', format1)
		worksheet.write('B1', 'Proyecto', format1)
		worksheet.write('C1', 'Categoria', format1)

		for c in categoria:

			worksheet.write(row, col,c.contrato.nombre,format2)
			worksheet.write(row, col+1,c.proyecto.nombre,format2)
			worksheet.write(row, col+2,c.categoria,format2)
		
			row +=1


	workbook.close()

	return response
    #return response


#exportar los datos de las cuenta del financiero ya sea por parametro mcontrato o por id_empresa
def export_excel_subcategoria(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="subcategoria.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Subcategoria')
	format1=workbook.add_format({'border':1,'font_size':15,'bold':True})
	format2=workbook.add_format({'border':1})

	row=1
	col=0

	categoria= request.GET['categoria']
	proyecto= request.GET['proyecto']
	# desde= request.GET['desde']
	# hasta= request.GET['hasta']

	if (int(categoria)>0 or int(id_empresa)>0):
		
		qset = (Q(categoria__id=categoria) and Q(proyecto__id=proyecto))


		# if (desde and (hasta is not None)):

		# 	qset = qset & (Q(fecha__gte=desde))

		# if(desde and hasta):
		# 	qset = qset &(Q(fecha__gte=desde) and Q(fecha__lte=hasta) )
		
						
		subcategoria = BSubcategoria.objects.filter(qset)
		worksheet.write('A1', 'Titulo', format1)
		worksheet.write('B1', 'Contenido', format1)
		# worksheet.write('C1', 'Fecha', format1)

		for subcategorias in subcategoria:
			worksheet.write(row, col,subcategorias.titulo,format2)
			worksheet.write(row, col+1,subcategorias.contenido,format2)
			# worksheet.write(row, col+2,subcategorias.fecha,format2)

			row +=1


	workbook.close()

	return response
    #return response



#funcion para traer las carpetas de las fotos
def carpeta_foto(request):

	cursor = connection.cursor()
	try:
		proyecto_id = request.GET['proyecto_id']

		cursor.callproc('[dbo].[consultar_carpeta_foto]', [proyecto_id,])
		
		result_set = cursor.fetchall()
		lista=[]

		for x in list(result_set):
			item={
				'id_tipo':x[0],
				'tipo':x[1],
				'cantidad':x[2],

			}
			lista.append(item)
		
		return JsonResponse({'message':'','success':'ok','data':lista})	
	except Exception as e:

		#print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)	
	finally:
		cursor.close()



#actualizar fecha de las fotos
@transaction.atomic
def actualizar_fecha(request):

	sid = transaction.savepoint()

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		for item in respuesta['lista']:

			object_fotos=CFotosProyecto.objects.get(pk=item['id'])
			fecha=datetime.strptime(respuesta['fecha'], '%Y-%m-%d').date()

			object_fotos.fecha=respuesta['fecha']
			object_fotos.save()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='administrador_foto.fotos_proyectos',id_manipulado=item['id'])
			logs_model.save()

			transaction.savepoint_commit(sid)


		return JsonResponse({'message':'La fecha se a actualizado correctamente','success':'ok',
				'data':''})
		
	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})



#actualizar campo asociado a reporte
@transaction.atomic
def asociar_reporte(request):

	sid = transaction.savepoint()

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		for item in respuesta['lista']:

			object_fotos=CFotosProyecto.objects.get(pk=item['id'])

			if int(respuesta['asociar'])>0:

				asociado=True

			else:
				asociado=False	

			object_fotos.asociado_reporte=asociado
			object_fotos.save()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='administrador_foto.fotos_proyectos',id_manipulado=item['id'])
			logs_model.save()

			transaction.savepoint_commit(sid)


		return JsonResponse({'message':'La accion se ha guardado correctamente','success':'ok',
				'data':''})
		
	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})		



# #serializer de empresa
# class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):
# 	"""docstring for ClassName"""	
# 	class Meta:
# 		model = Empresa
# 		fields=('id' , 'nombre'	, 'nit')

# #serializer lite de proyecto
# class ProyectoLite2Serializer(serializers.HyperlinkedModelSerializer):
# 	mcontrato = ContratoLiteSerializer(read_only = True)
# 	municipio = MunicipioSerializer(read_only = True)
# 	contrato = ContratoLiteSerializer(read_only = True, many = True)
# 	conteo_puntos=serializers.SerializerMethodField()
# 	cantidad_cambio=serializers.SerializerMethodField()
# 	cantidad_lote=serializers.SerializerMethodField()

# 	class Meta: 
# 		model = Proyecto
# 		fields=( 'id','nombre',
# 				 'mcontrato' ,
# 				 'municipio' ,
# 				 'contrato',
# 				 'conteo_puntos',
#  				 'cantidad_cambio',
# 				 'cantidad_lote'
# 				 )

# 	def get_conteo_puntos(self, obj):
# 		return PuntosGps.objects.filter(proyecto_id=obj.id).count()

# 	def get_cantidad_cambio(self, obj):
# 		return CCambio.objects.filter(proyecto_id=obj.id).count()

# 	def get_cantidad_lote(self, obj):
# 		return ALote.objects.filter(proyecto_id=obj.id).count()

# #serializer lite de proyecto empresa
# class ProyectoEmpresaLite2Serializer(serializers.HyperlinkedModelSerializer):

# 	proyecto = ProyectoLite2Serializer(read_only = True )
# 	empresa = EmpresaLiteSerializer(read_only = True  )

# 	totalCronograma=serializers.SerializerMethodField()

# 	totalPresupuesto=serializers.SerializerMethodField()

# 	totalCronogramaGrafico=serializers.SerializerMethodField()

# 	class Meta:
# 		model = Proyecto_empresas
# 		fields=('id' ,
# 				'proyecto',
#  				'empresa',
#  				'totalCronograma',
#  				'totalPresupuesto',
#  				'totalCronogramaGrafico',		 
# 				)

# 	def get_totalCronograma(self, obj):
# 		return BCronograma.objects.filter(proyecto_id=obj.proyecto.id).count()

# 	def get_totalCronogramaGrafico(self, obj):
# 		return Cronograma.objects.filter(proyecto_id=obj.proyecto.id).count()

# 	def get_totalPresupuesto(self, obj):
# 		return EPresupuesto.objects.filter(proyecto_id=obj.proyecto.id).count()

# #Api lite de empresa proyecto
# class ProyectoEmpresaLiteViewSet(viewsets.ModelViewSet):
# 	"""
# 	Retorna una lista las categorias de administrador de fotos
# 	"""
# 	model=Proyecto_empresas
# 	queryset = model.objects.all()
# 	serializer_class = ProyectoEmpresaLite2Serializer
# 	nombre_modulo='administrador_foto.Proyecto_empresa'

# 	def retrieve(self,request,*args, **kwargs):
# 		try:
# 			instance = self.get_object()
# 			serializer = self.get_serializer(instance)
# 			return Response({'message':'','status':'success','data':serializer.data})
# 		except Exception as e:
# 			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


# 	def list(self, request, *args, **kwargs):
# 		try:
# 			queryset = super(ProyectoEmpresaLiteViewSet, self).get_queryset()
# 			dato = self.request.query_params.get('dato', None)
# 			empresa = self.request.query_params.get('empresa', None)
# 			mcontrato = self.request.query_params.get('mcontrato', None)
# 			departamento = self.request.query_params.get('departamento', None)
# 			municipio = self.request.query_params.get('municipio', None)
# 			contratista = self.request.query_params.get('contratista', None)
# 			sin_paginacion = self.request.query_params.get('sin_paginacion', None)

# 			qset=(~Q(id=0))

# 			if(dato or empresa or mcontrato or departamento or municipio):

# 				if dato:
# 					qset = qset & ( Q(empresa__nombre__icontains = dato) |
# 								Q(empresa__nit__icontains = dato) |
# 								Q(proyecto__nombre__icontains = dato))					
			

# 				if empresa and int(empresa)>0:
# 					qset = qset & (Q(empresa__id = empresa))					


# 				if mcontrato and int(mcontrato)>0:
# 					qset = qset & (Q(proyecto__mcontrato = mcontrato))
					
# 				if departamento and int(departamento)>0:
# 					qset = qset & (Q(proyecto__municipio__departamento__id = departamento))
					
# 				if municipio and int(municipio)>0:
# 					qset = qset & (Q(proyecto__municipio = municipio))
					

# 				if contratista and int(contratista)>0:
# 					qset = qset & (Q(proyecto__contrato__contratista__id = contratista))	

			
# 			if qset != '':
# 				queryset = self.model.objects.filter(qset)

# 			if sin_paginacion is None:
# 				page = self.paginate_queryset(queryset)
# 				if page is not None:
# 					serializer = self.get_serializer(page,many=True)	
# 					return self.get_paginated_response({'message':'','success':'ok',
# 					'data':serializer.data})
		
# 				serializer = self.get_serializer(queryset,many=True)
# 				return Response({'message':'','success':'ok',
# 						'data':serializer.data})
# 			else:
# 				serializer = self.get_serializer(queryset,many=True)
# 				return Response({'message':'','success':'ok',
# 						'data':serializer.data})

# 		except Exception as e:
# 			#print(e)
# 			functions.toLog(e,self.nombre_modulo)
# 			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
