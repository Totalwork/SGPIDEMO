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
import json
from django.http import HttpResponse,JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from .models import InformeMME, InformeConsecutivo
from contrato.models import Contrato
from contrato.views import ContratoSerializer
from empresa.models import Empresa
from empresa.views import EmpresaSerializer
from logs.models import Logs,Acciones
from django.db import connection
from datetime import *
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required
from coasmedas.functions import functions
#import io
from django.core.files import File


# Serializador de contrato
class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Contrato
		fields=('id','nombre','numero')

#Serialezer de empresa
class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Empresa
		fields=('id','nombre')

#Api rest para informe
class InformeMMESerializer(serializers.HyperlinkedModelSerializer):

	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Contrato.objects.all())
	contrato=ContratoLiteSerializer(read_only=True)

	#empresa = EmpresaLiteSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())
	
	class Meta:
		model = InformeMME
		fields=('id','contrato','contrato_id','empresa_id','fecha','consecutivo','soporte','ano')


class InformeMMEViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de informes guardados.
	"""
	model=InformeMME
	queryset = model.objects.all()
	serializer_class = InformeMMESerializer
	nombre_modulo='informe.informe_mme'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:

			queryset = super(InformeMMEViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			desde= self.request.query_params.get('desde',None)
			hasta= self.request.query_params.get('hasta',None)
			contrato= self.request.query_params.get('contrato_id',None)
			sin_paginacion=self.request.query_params.get('sin_paginacion',None)
			id_empresa = request.user.usuario.empresa.id
			qset=''

			qset=(~Q(id=0))

			if id_empresa and int(id_empresa)>0:
				qset =qset &(
					Q(empresa__id=id_empresa)
					)
			
			if contrato and int(contrato)>0:
				qset =qset &(
					Q(contrato__id=contrato)
					)

			if dato:
				qset = qset &(
					Q(contrato__nombre__icontains=dato)
					)

			if (desde and (hasta is not None)):

					qset = qset & (
						Q(fecha__gte=desde)
						)

			if(desde and hasta):
					qset = qset &(
						Q(fecha__gte=desde) and Q(fecha__lte=hasta) 
					)


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
			print(e)
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()

			try:

				id_empresa = request.user.usuario.empresa.id
				fecha = request.DATA['fecha'] if 'fecha' in request.DATA else None;
				anoEnvio = int(fecha[:4])
				ruta_archivo = 'C:/servicios.sinin.co/wwwroot/plantillas/'+str(request.POST['nombre_soporte'])
				#ruta_archivo = "C:\Users\danny\source\\repos\serviciosSinin\Serviciocoasmedas1\wwwroot\plantillas\\"+str(request.POST['nombre_soporte'])

				f = open(ruta_archivo, 'rb')
				myfile = File(f)

				cC = InformeConsecutivo.objects.get(empresa_id=id_empresa, ano = anoEnvio)	
				consecutivo = cC.numero	
				request.DATA['consecutivo'] = consecutivo

				request.DATA['empresa_id'] = id_empresa
				request.DATA['ano'] = anoEnvio	

				serializer = InformeMMESerializer(data=request.DATA,context={'request': request})

				##print request.DATA

				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'],empresa_id=request.DATA['empresa_id'],
						soporte=myfile)

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='informe.informe_mme',id_manipulado=serializer.data['id'])
					logs_model.save()

					cC.numero = cC.numero+1
					cC.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					print(serializer.errors)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				print(e)
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
				serializer = InformeMMESerializer(instance,data=request.DATA,context={'request': request},partial=partial)

				# if request.DATA['desde'] =='' and request.DATA['hasta'] =='':
				# 	request.DATA['desde']=None
				# 	request.DATA['hasta']=None

				if serializer.is_valid():
					serializer.save(contrato_id=request.DATA['contrato_id'],empresa_id=request.DATA['empresa_id'],
						soporte=request.FILES['soporte'] if request.FILES.get('soporte') is not None else '')

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='informe.informe_mme',id_manipulado=serializer.data['id'])
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




#Fin api rest para informe
@login_required
def informe_ministerio(request):
		return render(request, 'informe/informe.html',{'app':'informe_mme','model':'informemme'})

