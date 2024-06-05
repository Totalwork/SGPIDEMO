from django.shortcuts import render
# Create your views here.
from django.shortcuts import render,redirect,render_to_response
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
from logs.models import Logs,Acciones
from django.db import connection
from django.db import transaction
from django.db.models.deletion import ProtectedError
import openpyxl
from django.contrib.auth.decorators import login_required
from sinin4.functions import functions
from .models import AIndicador,BSeguimientoIndicador,Periodicidad
from django.db.models import F, FloatField, Sum

class PeriodicidadSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model=Periodicidad
		fields=('id','descripcion','dias')

class IndicadorSerializer(serializers.HyperlinkedModelSerializer):
	periodicidad_id = serializers.IntegerField(write_only=True)
	periodicidad = PeriodicidadSerializer(read_only=True)
	#url = serializers.HyperlinkedIdentityField(view_name="myapp:contenttype-detail")
	class Meta:
		model=AIndicador
		fields=('id','nombre','unidadMedida','objetivoAnual','cantidad_seguimiento','inicio_periodo','fin_periodo','periodicidad_id','periodicidad')


class IndicadorViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de indicadores, puede utilizar el parametro <b>{dato=[texto a buscar]}</b>, 
		a traves del cual, se podra buscar por todo o parte del nombre del indicador.
	"""
	model=AIndicador
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = IndicadorSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo='indicadorCalidad.calidad'


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
			queryset = super(IndicadorViewSet, self).get_queryset().order_by('nombre')
			dato = self.request.query_params.get('dato', None)
			periodicidad = self.request.query_params.get('periodicidad', None)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			mensaje=''

			if periodicidad:
				queryset = Periodicidad.objects.all()	
				serializer = PeriodicidadSerializer(queryset,many=True)			
				return Response({'message':mensaje,'success':'ok',
					'data':serializer.data})

			qset=(~Q(id=0))	
			
			if (dato):
				qset = qset &(Q(nombre__icontains=dato))

				queryset = self.model.objects.filter(qset).order_by('nombre')

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
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = IndicadorSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():

					serializer.save()

					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)

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
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)


	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()

			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()

				serializer = IndicadorSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save()

					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_actualizar,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)

					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				#print(e)
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic			
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			logs_model=self.model_log(
				usuario_id=request.user.usuario.id,
				accion=self.model_acciones.accion_borrar,
				nombre_modelo=self.nombre_modulo,
				id_manipulado=instance.id
			)
			logs_model.save()	
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			functions.toLog(e,self.nombre_modulo)
			
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)


class IndicadorLiteSerializer(serializers.HyperlinkedModelSerializer):
	#url = serializers.HyperlinkedIdentityField(view_name="myapp:contenttype-detail")
	class Meta:
		model=AIndicador
		fields=('id','nombre')

class SeguimientoIndicadorSerializer(serializers.HyperlinkedModelSerializer):

	indicador_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=AIndicador.objects.all())
	indicador=IndicadorSerializer(read_only=True)

	class Meta:
		model = BSeguimientoIndicador
		fields=('id','indicador','indicador_id','inicioPeriodo','finPeriodo','valor')

class SeguimientoIndicadorViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de seguimiento de indicadores, puede utilizar el parametro <b>{dato=[texto a buscar]}</b>,
		 a traves del cual, se podra buscar por todo o parte del nombre del indicador.<br/>
		Puede utilizar el parametro <b>{indicador=[id del indicador]}</b> para ubicar registros de seguimiento
		asociados al indicador.<br/>
		Utilice el parametro <b>{ignorePagination=1}</b> para obtener los resultados sin paginacion.<br/>
	"""
	model=BSeguimientoIndicador
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = SeguimientoIndicadorSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10
	nombre_modulo='indicadorCalidad.seguimientoIndicador'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		#import pdb; pdb.set_trace()
		try:
			queryset = super(SeguimientoIndicadorViewSet, self).get_queryset().order_by('indicador__nombre','inicioPeriodo')
			dato = self.request.query_params.get('dato', None)
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			indicador = self.request.query_params.get('indicador', None)
			desde= self.request.query_params.get('desde',None)
			hasta= self.request.query_params.get('hasta',None)
			mensaje=''
			
			if (dato or indicador or desde or hasta ):

				qset = (Q(indicador=indicador))

				if dato:
					qset = qset & (Q(nombre__icontains=dato))


				if desde:
					qset = qset &(Q(inicioPeriodo__gte=desde))
				
				if hasta:
					qset = qset &(Q(finPeriodo__lte=hasta))

				queryset = self.model.objects.filter(qset).order_by('indicador__nombre','inicioPeriodo')
			
			if queryset.count()==0:
				mensaje='No se encontraron Items con los criterios de busqueda ingresados'	

			if ignorePagination:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'count':queryset.count(),'results':{'message':mensaje,'success':'ok',
				'data':serializer.data}})				
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
			return Response({'message':'Se presentaron errores de comunicacion con el servidor',
				'status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = SeguimientoIndicadorSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():

					serializer.save(indicador_id=request.DATA['indicador_id'])

					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_crear,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)

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

				serializer = SeguimientoIndicadorSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(indicador_id=request.DATA['indicador_id'])

					logs_model=self.model_log(
						usuario_id=request.user.usuario.id,
						accion=self.model_acciones.accion_actualizar,
						nombre_modelo=self.nombre_modulo,
						id_manipulado=serializer.data['id']
					)

					logs_model.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				#print(e)
				functions.toLog(e,self.nombre_modulo)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST) 	



	@transaction.atomic			
	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			logs_model=self.model_log(
				usuario_id=request.user.usuario.id,
				accion=self.model_acciones.accion_borrar,
				nombre_modelo=self.nombre_modulo,
				id_manipulado=instance.id
			)
			logs_model.save()	
			self.perform_destroy(instance)
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)





#eliminar las indicadores
@transaction.atomic
def eliminar_varios_id(request):
	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:

			AIndicador.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='indicador.indicador_calidad',id_manipulado=item['id'])
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
		



#exportar los indicadores
def export_excel_indicadores(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="indicadores.xlsx"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Indicadores')
	format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
	format2=workbook.add_format({'border':0})
	format3=workbook.add_format({'border':0,'font_size':12})

	row=1
	col=0

	cursor = connection.cursor()

	indicador = AIndicador.objects.all()

	worksheet.write('A1', 'Nombre del indicador', format1)
	worksheet.write('B1', 'Unidad de medida', format1)
	worksheet.write('C1', 'Objectivo anual', format1)

	for ind in indicador:

		worksheet.write(row, col,ind.nombre,format2)
		worksheet.write(row, col+1,ind.unidadMedida,format2)
		worksheet.write(row, col+2,ind.objetivoAnual,format2)
		
		row +=1

	workbook.close()

	return response
    #return response



#eliminar los seguimientos
@transaction.atomic
def eliminar_varios_seguimiento(request):
	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:

			BSeguimientoIndicador.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='indicador.seguimiento_indicador',id_manipulado=item['id'])
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})

	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})



#exportar los seguimientos
def export_excel_seguimiento(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="seguimiento.xlsx"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Seguimiento')
	format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
	format2=workbook.add_format({'border':0})
	format3=workbook.add_format({'border':0,'font_size':12})

	row=1
	col=0

	cursor = connection.cursor()

	seguimiento = BSeguimientoIndicador.objects.all()

	worksheet.write('A1', 'Nombre del indicador', format1)
	worksheet.write('B1', 'Periodo inicio', format1)
	worksheet.write('C1', 'Periodo final', format1)
	worksheet.write('D1', 'Valor', format1)

	for segui in seguimiento:

		worksheet.write(row, col,segui.indicador.nombre,format2)
		worksheet.write(row, col+1,segui.inicioPeriodo,format2)
		worksheet.write(row, col+2,segui.finPeriodo,format2)
		worksheet.write(row, col+3,segui.valor,format2)
		
		row +=1

	workbook.close()

	return response
    #return response

		

@login_required
def indicador(request):
	return render(request, 'indicadorCalidad/indicadorCalidad.html',{'app':'indicadorCalidad','model':'aindicador'})


@login_required
def seguimientoIndicador(request,id_indicador=None):

	qsIndicador=AIndicador.objects.filter(id=id_indicador).first()

	valor_total=BSeguimientoIndicador.objects.filter(indicador_id=id_indicador).aggregate(suma_detalle=Sum('valor'))

	return render(request, 'indicadorCalidad/seguimiento_indicador.html',{'total_seguimiento':valor_total['suma_detalle'],'indicadores':qsIndicador,'app':'indicadorCalidad','model':'bseguimientoindicador','id_indicador':int(id_indicador)})