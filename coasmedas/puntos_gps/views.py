# -*- coding: utf-8 -*- 
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
from .models import PuntosGps
from proyecto.models import Proyecto, Proyecto_info_tecnica
from proyecto.views import ProyectoSerializer
from logs.models import Logs,Acciones
from django.db import connection
from django.db import transaction
from django.db.models.deletion import ProtectedError
from empresa.models import Empresa
from empresa.views import EmpresaSerializer
import openpyxl
from django.contrib.auth.decorators import login_required
from coasmedas.functions import functions
from contrato.enumeration import tipoC
from contrato.models import Contrato,EmpresaContrato
from estado.models import Estado
from estado.views import EstadoSerializer
from tipo.views import TipoSerializer
from parametrizacion.views import BancoSerializer , MunicipioSerializer , FuncionarioSerializer , DepartamentoSerializer
from rest_framework.decorators import api_view



# SERIALIZER LITE
class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	class Meta:
		model = Empresa
		fields=('id' , 'nombre'	, 'nit')



class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	contratista = EmpresaLiteSerializer(read_only=True)

	class Meta:
		model = Contrato
		fields=('id' , 'nombre'	, 'contratista')


#Serializer de proyecto
class ProyectoLiteSerializer(serializers.HyperlinkedModelSerializer):

	mcontrato = ContratoLiteSerializer(read_only = True , allow_null = True)

	municipio = MunicipioSerializer(read_only = True)

	estado_proyecto = EstadoSerializer(read_only = True)

	contratistaObra = serializers.SerializerMethodField('_contratista',read_only=True)


	no_usuarios = serializers.SerializerMethodField('_infotecnica',read_only=True)

	def _contratista(self,obj):

		proyectoobra = Proyecto.objects.get(pk=obj.id).contrato.filter(tipo_contrato=5).first()

		if proyectoobra is None:
			retorno = ''
		else:
			retorno= proyectoobra.contratista.nombre

		return retorno

	def _infotecnica(self,obj):

		infotecnica = Proyecto_info_tecnica.objects.filter(proyecto_id=obj.id, campo__in=(1,2,3)).first()

		if infotecnica is None:
			retorno = ''
		else:
			retorno= infotecnica.valor_diseno

		return retorno		



	class Meta: 
		model = Proyecto

		fields=( 'id','nombre','estado_proyecto','municipio','mcontrato','contratistaObra','valor_adjudicado','no_usuarios')


#Api rest para puntos gps
class PuntosGpsSerializer(serializers.HyperlinkedModelSerializer):

	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto.objects.all())
	proyecto=ProyectoLiteSerializer(read_only=True)

	class Meta:
		model = PuntosGps
		fields=('id','nombre','proyecto','proyecto_id','longitud','latitud')



class PuntosGpsSerializerLite(serializers.HyperlinkedModelSerializer):

	
	class Meta:
		model = PuntosGps
		fields=('id','nombre','longitud','latitud')



class PuntosGpsViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de los puntos gps del proyecto.
	"""
	model=PuntosGps
	queryset = model.objects.all()
	serializer_class = PuntosGpsSerializer
	nombre_modulo='puntos_gps.puntosGps'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(PuntosGpsViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion = self.request.query_params.get('sin_paginacion', None)
			proyecto_id= self.request.query_params.get('proyecto_id',None)
			id_empresa = request.user.usuario.empresa.id
			tipo_contrato= self.request.query_params.get('tipo_contrato').split(',') if self.request.query_params.get('tipo_contrato') else None
			mcontrato= self.request.query_params.get('mcontrato').split(',') if self.request.query_params.get('mcontrato') else None
			departamento= self.request.query_params.get('departamento').split(',') if self.request.query_params.get('departamento') else None
			contratista= self.request.query_params.get('contratista').split(',') if self.request.query_params.get('contratista') else None
			municipio= self.request.query_params.get('municipio').split(',') if self.request.query_params.get('municipio') else None
			estado_proyecto= self.request.query_params.get('estado_proyecto').split(',') if self.request.query_params.get('estado_proyecto') else None
			proyectonombre= self.request.query_params.get('proyectonombre',None)
			puntosgpslite= self.request.query_params.get('puntosgpslite',None)
			qset=''

			if (dato or proyecto_id or tipo_contrato or mcontrato or departamento or municipio or id_empresa):
				
				qset = Q(proyecto__mcontrato__empresacontrato__empresa=id_empresa)

				if proyecto_id and int(proyecto_id)>0:
					qset = qset &(
						Q(proyecto__id=proyecto_id)
					)

				if dato :		
					qset = qset & (Q(nombre__icontains=dato))

				if proyectonombre :		
					qset = qset & (Q(proyecto__nombre__icontains=proyectonombre))					

				if tipo_contrato :
					qset = qset & (Q(proyecto__contrato__tipo_contrato__id__in = tipo_contrato))


				if mcontrato:
					qset = qset & (Q(proyecto__mcontrato__id__in=mcontrato))

				if departamento:
					qset = qset & (Q(proyecto__municipio__departamento__id__in=departamento))

				if municipio:
					qset = qset & (Q(proyecto__municipio__id__in=municipio))

				if contratista:
					qset = qset & (Q(proyecto__contrato__contratista__in=contratista))	

				if estado_proyecto:
					qset = qset & (Q(proyecto__estado_proyecto_id__in=estado_proyecto))													

			if qset != '':
				queryset = self.model.objects.filter(qset)	


			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
				
				if puntosgpslite:
					serializer = PuntosGpsSerializerLite(queryset,many=True)
					return Response({'message':'','success':'ok',
							'data':serializer.data})
				else:
					serializer = self.get_serializer(queryset,many=True)
					return Response({'message':'','success':'ok',
							'data':serializer.data})
			else:
				if puntosgpslite:
					serializer = PuntosGpsSerializerLite(queryset,many=True)
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
				serializer = PuntosGpsSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():

					serializer.save(proyecto_id=request.DATA['proyecto_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='puntos.gps',id_manipulado=serializer.data['id'])
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

				serializer = PuntosGpsSerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(proyecto_id=request.DATA['proyecto_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='puntos.gps',id_manipulado=serializer.data['id'])
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


#Fin api rest para puntos gps


@login_required
def puntos_gps(request):
	return render(request, 'puntos_gps/gps.html',{'app':'puntos_gps','model':'putosgps'})


@login_required
def listado_gps(request,id_proyecto=None):

	qsProyecto=Proyecto.objects.filter(id=id_proyecto).first()

	model_proyecto = Proyecto.objects.get(pk=id_proyecto)
	queryset = model_proyecto.contrato.all().values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero', 'contratista__id', 'contratista__nombre')

	contratista_asociado=''

	for item in list(queryset):

		contratista_asociado=contratista_asociado+item['contratista__nombre']+' ,'


	return render(request, 'puntos_gps/listado_gps.html',{'contratista_asociado':contratista_asociado,'proyecto':qsProyecto,'app':'puntos_gps','model':'puntosgps','id_proyecto':int(id_proyecto)})


@login_required
def mapa_proyecto(request,id_proyecto=None):

	qsPuntos=PuntosGps.objects.filter(proyecto__id=id_proyecto).values('nombre', 'latitud', 'longitud', 
									'proyecto__mcontrato__nombre', 'proyecto__nombre', 'proyecto__mcontrato__contratista__nombre', 
									'proyecto__municipio__departamento__nombre', 'proyecto__municipio__nombre', 'proyecto__estado_proyecto__nombre',
									'proyecto__valor_adjudicado')


	model_proyecto = Proyecto.objects.get(pk=id_proyecto)
	queryset = model_proyecto.contrato.all().values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero', 'contratista__id', 'contratista__nombre')

	contratista_asociado=''

	for item in list(queryset):

		contratista_asociado=contratista_asociado+item['contratista__nombre']+' ,'


	qsProyecto=Proyecto.objects.filter(id=id_proyecto).first()
	qsInfotecnica=Proyecto_info_tecnica.objects.filter(proyecto__id=id_proyecto, campo__id=28).values('valor_diseno').first()
	
	for x in qsPuntos:
		x.update({'infotecnica':qsInfotecnica if qsInfotecnica is not None else {'valor_diseno': 0} })
	
	return render(request, 'puntos_gps/mapa.html',{'contratista_asociado':contratista_asociado,'proyecto':qsProyecto,'puntos':qsPuntos,'app':'proyecto','model':'putosgps','id_proyecto':int(id_proyecto)})


@login_required
def descargar_plantilla(request):
	return functions.exportarArchivoS3('plantillas/gps/plantilla puntos.xlsx')

@login_required
def ubicacion(request):
	tipo_c=tipoC()
	querysetmcontrato=Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato,empresacontrato__empresa=request.user.usuario.empresa.id,empresacontrato__participa=1,activo=1)
	querysetempresa=Empresa.objects.filter(esContratista=True)
	quesetestado=Estado.objects.filter(app='proyecto')
	quesetestadoo=Estado.objects.filter(app='proyecto_obra')
	return render(request, 'puntos_gps/ubicacion.html',{'estadoobra':quesetestadoo,'estadoproyecto':quesetestado,'mcontrato':querysetmcontrato,'contratista':querysetempresa,'app':'puntos_gps','model':'putos_gps'})	


#eliminar puntos gps
@api_view(['DELETE'])
@transaction.atomic
def eliminar_varios_id(request):
	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		
		for item in respuesta['lista']:
			PuntosGps.objects.filter(id=item['id']).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='puntos.gps',id_manipulado=item['id'])
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


#exportar los datos de las cuenta del financiero ya sea por parametro mcontrato o por id_empresa
def export_excel_gps(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="cuenta.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Cuenta')
	format1=workbook.add_format({'border':1,'font_size':15,'bold':True})
	format2=workbook.add_format({'border':1})

	row=1
	col=0
	qset='';

	proyecto_id= request.GET['proyecto_id']

	if (int(proyecto_id)>0):

		if proyecto_id:
	
			qset = (
					Q(proyecto_id=proyecto_id)
				)
						
		puntos = PuntosGps.objects.filter(qset)

		worksheet.write('A1', 'Nombre del proyecto', format1)
		worksheet.write('B1', 'Nombre del punto', format1)
		worksheet.write('C1', 'Longitud', format1)
		worksheet.write('D1', 'Latitud', format1)

		for puntos in puntos:
			worksheet.write(row, col,puntos.proyecto.nombre,format2)
			worksheet.write(row, col+1,puntos.nombre,format2)
			worksheet.write(row, col+2,puntos.longitud,format2)
			worksheet.write(row, col+3,puntos.latitud,format2)

			row +=1

	workbook.close()

	return response
    #return response

#funcion utilizada para cargar masivamente los puntos del gps del proyecto		
@transaction.atomic
def cargar_excel(request):

	try:
		proyecto= request.POST['proyecto']
		soporte= request.FILES['archivo']
		doc = openpyxl.load_workbook(soporte)

		nombrehoja=doc.get_sheet_names()[0]
		hoja = doc.get_sheet_by_name(nombrehoja)

		index=0
		nombre_punto=''
		latitud=''
		longitud=''

		# print hoja.rows
		for fila in hoja.rows:

			if index>=1:				
				nombre_punto =fila[0].value
				latitud =fila[1].value
				longitud =fila[2].value
				if latitud is not None and longitud is not None:							
					if not type(latitud) ==type(1.000) and type(longitud)==type(1.000):
						return JsonResponse({'message':"En la linea "+str(index)+" no se encontró un valor con formato decimal, tenga en cuenta que los numeros decimales en excel llevan el caracter ',' ",'status':'error','data':''})
				else:
					return JsonResponse({'message':"En la linea "+str(index)+" falta alguna la latitud y/o la longitud ',' ",'status':'error','data':''})
			index=index+1

		index=0
		for fila in hoja.rows:
			if index>=1:				
				nombre_punto =fila[0].value
				latitud =fila[1].value
				longitud =fila[2].value
				
				modelo=PuntosGps(nombre=nombre_punto,proyecto_id=proyecto,longitud=longitud,latitud=latitud)
				modelo.save()

			index=index+1
		
		

		return JsonResponse({'message':'Se registro exitosamente','success':'ok','data':''})
	
	except Exception as e:
		functions.toLog(e,'carga de puntos gps')
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)		

    #return response
