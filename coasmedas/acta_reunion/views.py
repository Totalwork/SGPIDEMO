# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.urls import reverse

from .models import Consecutivo,Acta,Tema,Acta_historial,Participante_externo, \
Participante_interno,Compromiso,Compromiso_historial

from .serializers import ConsecutivoSerializer,ActaSerializer,TemaSerializer,Acta_historialSerializer,\
Participante_externoSerializer,Participante_internoSerializer,CompromisoSerializer,Compromiso_historialSerializer

from .serializers import ConsecutivoLiteSerializer,ActaLiteSerializer,TemaLiteSerializer,Acta_historialLiteSerializer,\
Participante_externoLiteSerializer,Participante_internoLiteSerializer,CompromisoLiteSerializer,Compromiso_historialLiteSerializer,\
NoParticipantesSerializer

from empresa.models import Empresa
from empresa.views import EmpresaSerializer, EmpresaLiteSerializer

from usuario.models import Usuario, Persona
from usuario.views import UsuarioSerializer, UsuarioLiteSerializer, PersonaSerializer, PersonaLiteSerializer

from tipo.models import Tipo
from tipo.views import TipoSerializer, TipoLiteSerializer

from estado.models import Estado
from estado.views import EstadoSerializer, EstadoLiteSerializer
from contrato.views import ContratoLiteSerializerByDidi
from proyecto.views import ProyectoLite3Serializer

from django.template import RequestContext
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required

from logs.models import Logs, Acciones
from coasmedas.functions import functions

from django.db.models import Q, Count

from rest_framework import viewsets, serializers, response
from django.db.models import Q

from django.db import IntegrityError,transaction
from django.http import HttpResponse,JsonResponse

from .enumeration import estadoA,tipoAH,estadoC,tipoCH
from contrato.enumeration import tipoC

from contrato.models import Contrato, EmpresaContrato
from proyecto.models import Proyecto, Proyecto_empresas
from datetime import *

import xlsxwriter
import json

from reportlab.pdfgen import canvas
import reportlab.pdfgen.canvas
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.lib import units
from reportlab.graphics.shapes import Drawing


# Create your views here.

#Rutas
@login_required
def acta(request):
	usuarios1 = Usuario.objects.filter(user__is_active=True,empresa__id=request.user.usuario.empresa.id).values('id','persona__nombres','persona__apellidos')
	usuarios2 = Usuario.objects.filter(user__is_active=True).values('id','persona__nombres','persona__apellidos')
	qset = (Q(contrato__tipo_contrato=tipoC.m_contrato))& (Q(edita=1)) &(Q(empresa=4) & Q(participa=1))
	mcrontratos = EmpresaContrato.objects.filter(qset).values('contrato__id','contrato__nombre').order_by("contrato__id")		
	
	estados = Estado.objects.filter(app=estadoA.app)

	return render(request, 'actareunion/acta.html',{'model':'acta','app':'acta','estados':estados,'macrocontratos':mcrontratos,'usuarios_organizador':usuarios1,'usuarios_filtro':usuarios2})

@login_required
def consecutivo(request):
	return render(request, 'actareunion/consecutivo.html',{'model':'consecutivo','app':'acta'})


@login_required
def mis_compromisos(request):
	participante_interno = Participante_interno.objects.filter().values('usuario__id','usuario__persona__nombres','usuario__persona__apellidos').distinct()
	estados = Estado.objects.filter(app='compromiso')
	return render(request, 'actareunion/mis_compromisos.html',{'model':'acta_compromiso','app':'acta','participantes_internos':list(participante_interno),'estados':list(estados)})


#Api rest para Actas de reunion
class ConsecutivoViewSet(viewsets.ModelViewSet):
	model=Consecutivo
	queryset = model.objects.all()
	serializer_class = ConsecutivoSerializer
	nombre_modulo = 'Acta_reunion - ConsecutivoViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
	
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ConsecutivoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			page = self.request.query_params.get('page', None)
			lite = self.request.query_params.get('lite', None)		
			ID = self.request.query_params.get('id', None)

			empresa_id = self.request.query_params.get('empresa_id', None)
			consecutivo = self.request.query_params.get('consecutivo', None)
			
			qset = (~Q(id = 0))
			if dato:
				qset = qset & (Q(empresa__nombre__icontains=dato) | 
							  (Q(empresa__nit__icontains=dato)	|	
							  (Q(ano__icontains=dato)			  
						  	  ) ) )
			if empresa_id:
				qset = qset & Q(empresa__id=empresa_id)

			if consecutivo:
				qset = qset & Q(consecutivo__icontains=consecutivo)
			

			queryset = self.model.objects.filter(qset).order_by('-id')

			
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = ConsecutivoLiteSerializer(page,many=True, context={'request': request,})							
					else:
						serializer = self.get_serializer(page,many=True)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
			if lite:
				serializer = ConsecutivoLiteSerializer(queryset,many=True, context={'request': request,})
			else:
				serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})


		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				#import pdb; pdb.set_trace()			
				
				serializer = ConsecutivoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(empresa_id=request.DATA['empresa_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Consecutivo',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
						
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje=serializer.errors
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
    

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:				
				instance = self.get_object()
				serializer = ConsecutivoSerializer(instance,data=request.DATA,context={'request': request})

				#import pdb; pdb.set_trace()
				if serializer.is_valid():
					
					serializer.save(empresa_id=request.DATA['empresa_id'])										

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Consecutivo',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje=serializer.errors
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':
			sid = transaction.savepoint()				
			try:

				instance = self.get_object()
				no_acta_anterior = str(instance.empresa.id)+str(instance.consecutivo-1)
				
				if Acta.objects.filter(consecutivo=int(no_acta_anterior)).exists():
					return Response({'message':'Este consecutivo ya se encuentra en uso','success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
				else:
					self.perform_destroy(instance)
					serializer = self.get_serializer(instance)
					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='acta_reunion.Consecutivo',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
					'data':''},status=status.HTTP_200_OK)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class ActaViewSet(viewsets.ModelViewSet):
	model=Acta
	queryset = model.objects.all()
	serializer_class = ActaSerializer
	nombre_modulo = 'Acta_reunion - ActaViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			lite = self.request.query_params.get('lite', None)
			instance = self.get_object()

			if lite:
				serializer = ActaLiteSerializer(instance)
			else:
				serializer = self.get_serializer(instance)

			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
	

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ActaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			page = self.request.query_params.get('page', None)
			lite = self.request.query_params.get('lite', None)		
			ID = self.request.query_params.get('id', None)
			acta_previa = self.request.query_params.get('acta_previa', None)
			listActasPrevias = self.request.query_params.get('listActasPrevias', None)
						
			controlador_id = self.request.query_params.get('controlador_id', None)
			organizador_id = self.request.query_params.get('organizador_id', None)
			estado_id = self.request.query_params.get('estado_id', None)

			fecha_desde = self.request.query_params.get('fecha_desde', None)
			fecha_hasta = self.request.query_params.get('fecha_hasta', None)

			proyecto_id = self.request.query_params.get('proyecto_id', None)
			contrato_id = self.request.query_params.get('contrato_id', None)

			macrocontrato_id = self.request.query_params.get('macrocontrato_id', None)

			ListcontratosAsignados = self.request.query_params.get('ListcontratosAsignados', None)
			ListcontratosDisponibles = self.request.query_params.get('ListcontratosDisponibles', None)

			ListproyectosAsignados = self.request.query_params.get('ListproyectosAsignados', None)
			ListproyectosDisponibles = self.request.query_params.get('ListproyectosDisponibles', None)			

			ListHistorial = self.request.query_params.get('ListHistorial', None)			
			#import pdb; pdb.set_trace()			


			qset = (~Q(id = 0))
			if dato:
				qset = qset & (Q(consecutivo__icontains=dato) | 
							  (Q(tema_principal__icontains=dato)					  
						  	  ) )
			if controlador_id:
				qset = qset & Q(controlador_actual__id=controlador_id)

			if organizador_id:
				qset = qset & Q(usuario_organizador__id=organizador_id)

			if estado_id:
				qset = qset & Q(estado__id=estado_id)

			if macrocontrato_id:
				qset = qset & Q(contrato__id=macrocontrato_id)		

			if proyecto_id:
				qset = qset & Q(proyecto__id=proyecto_id)			

			if contrato_id:
				qset = qset & Q(contrato__id=contrato_id)
		
			if fecha_desde:
				qset = qset & (Q(fecha__gte=fecha_desde))

			if fecha_hasta:
				qset = qset & (Q(fecha__lte=fecha_hasta))
			
			actas_participantes = Participante_interno.objects.filter(usuario__id=request.user.usuario.id).values('acta__id')			

			if acta_previa:				
				
				if listActasPrevias:
					datoBusqueda = self.request.query_params.get('datoBusqueda', None)					
					qsetList = 	(~Q(id = ID) & Q(id__in=actas_participantes))
					
					if datoBusqueda:
						qsetList = qsetList & (Q(consecutivo__contains=datoBusqueda))

					queryset = self.model.objects.filter(qsetList)
					serializer = ActaLiteSerializer(queryset,many=True, context={'request': request,})				
					return Response({'message':'','success':'ok','data':serializer.data})					
									
				
				arrayActasPrevias = []
				state = True				
				index = 0

				acta = self.model.objects.get(id=ID)
				while state:
					if acta.acta_previa:						
						acta = self.model.objects.get(id=acta.acta_previa.id)						
						if acta not in arrayActasPrevias:
							arrayActasPrevias.append(acta)
						index += 1							
					else:
						if index != 0:
							if acta not in arrayActasPrevias:
								arrayActasPrevias.append(acta)
						state = False

				arrayActasPrevias.sort(key=lambda x: x.fecha, reverse=True)
				page = self.paginate_queryset(arrayActasPrevias)	
				if page is not None:				
					serializer = ActaLiteSerializer(page,many=True, context={'request': request,})																	
					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})

			if ListcontratosAsignados:
				
				actas_contratos = self.model.objects.get(id=ID)
				if 'datoContratoAsignado' in request.GET:
					qsetDato = (Q(numero__contains=request.GET['datoContratoAsignado']) | Q(nombre__contains=request.GET['datoContratoAsignado']))
					queryset =  actas_contratos.contrato.filter(qsetDato)
				else:
					queryset = actas_contratos.contrato.all()

				page = self.paginate_queryset(queryset)
				if page is not None:					
					serializer = ContratoLiteSerializerByDidi(page, many=True, context={'request': request,})	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})								
						
			if ListcontratosDisponibles:			
				#import pdb; pdb.set_trace()					
				actas_contratos = self.model.objects.get(id=ID)
				listContratosId = actas_contratos.contrato.all().distinct()
				arrayIds = []
				for c in listContratosId:
					arrayIds.append(c.id)

				qsetContratos = (~Q(id__in=arrayIds) & (Q(empresacontrato__empresa=request.user.usuario.empresa.id) & Q(empresacontrato__participa=1) & Q(activo=1)) )				
				if 'datoContratoDisponible' in request.GET:
					qsetContratos = qsetContratos & (Q(numero__contains=request.GET['datoContratoDisponible']) | Q(nombre__contains=request.GET['datoContratoDisponible']))					
				
				queryset = Contrato.objects.filter(qsetContratos)
				page = self.paginate_queryset(queryset)
				if page is not None:					
					serializer = ContratoLiteSerializerByDidi(page, many=True, context={'request': request,})	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})
		
			if ListproyectosAsignados:
				
				actas_proyectos = self.model.objects.get(id=ID)
				if 'datoProyectoAsignado' in request.GET:
					qsetDato = (Q(nombre__contains=request.GET['datoProyectoAsignado']))
					queryset =  actas_proyectos.proyecto.filter(qsetDato)
				else:
					queryset = actas_proyectos.proyecto.all()

				page = self.paginate_queryset(queryset)
				if page is not None:					
					serializer = ProyectoLite3Serializer(page, many=True, context={'request': request,})	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})								

			if ListproyectosDisponibles:			
				#import pdb; pdb.set_trace()					
				actas_proyectos = self.model.objects.get(id=ID)
				listProyectosId = actas_proyectos.proyecto.all().distinct()
				arrayIds = []
				for c in listProyectosId:
					arrayIds.append(c.id)

				ListProyectosValidos = Proyecto_empresas.objects.filter(empresa__id=request.user.usuario.empresa.id).values('proyecto__id').distinct()
				qsetProyectos =  (Q(id__in=ListProyectosValidos) & ~Q(id__in=arrayIds))
				
				if 'datoProyectoDisponible' in request.GET:
					qsetProyectos = qsetProyectos & (Q(nombre__contains=request.GET['datoProyectoDisponible']))
				
				queryset = Proyecto.objects.filter(qsetProyectos)
				page = self.paginate_queryset(queryset)
				if page is not None:					
					serializer = ProyectoLite3Serializer(page, many=True, context={'request': request,})	
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})
			
					
			qset = qset & (Q(id__in=actas_participantes))


			queryset = self.model.objects.filter(qset).order_by('-id')

			
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = ActaLiteSerializer(page,many=True, context={'request': request,})							
					else:
						serializer = self.get_serializer(page,many=True)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
			if lite:
				serializer = ActaLiteSerializer(queryset,many=True, context={'request': request,})
			else:
				serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})


		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				
				
				fecha=str(request.DATA['fecha'])
				fecha=datetime.strptime(fecha, '%Y-%m-%d').date()

				
				if Consecutivo.objects.filter(empresa__id=request.user.usuario.empresa.id,ano=fecha.year).exists():
					model_consecutivo=Consecutivo.objects.get(empresa__id=request.user.usuario.empresa.id,ano=fecha.year)
					consecutivo = str(model_consecutivo.empresa.id)+str(model_consecutivo.consecutivo)
					consecutivo = int(consecutivo)
				else:
					return Response({'message':'No se ha creado un consecutivo para este año','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

				request.DATA['consecutivo']=consecutivo
				request.DATA['estado_id']=estadoA.pausada
				serializer = ActaSerializer(data=request.DATA,context={'request': request})				

				if serializer.is_valid():					

					serializer.save(estado_id=estadoA.pausada,
						controlador_actual_id=int(request.DATA['controlador_actual_id']),
						usuario_organizador_id=int(request.DATA['usuario_organizador_id']
							))					

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Acta',id_manipulado=serializer.data['id'])
					logs_model.save()
					transaction.savepoint_commit(sid)

					#import pdb; pdb.set_trace()

					model_consecutivo.consecutivo=int(model_consecutivo.consecutivo)+1
					model_consecutivo.save()

					logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Consecutivo',id_manipulado=model_consecutivo.id)
					logs_model_con.save()
					transaction.savepoint_commit(sid)


					model_acta_historial = Acta_historial(
						acta_id=int(serializer.data['id']),
						fecha=date.today(),
						tipo_operacion_id=int(tipoAH.creacion),
						motivo='',
						controlador_id=int(request.DATA['controlador_actual_id']))
					model_acta_historial.save()

					logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Acta_historial',id_manipulado=model_acta_historial.id)
					logs_model_con.save()
					transaction.savepoint_commit(sid)

					if request.DATA['controlador_actual_id']!=request.DATA['usuario_organizador_id']:

						model_controlador = Participante_interno(acta_id=serializer.data['id'],usuario_id=int(request.DATA['controlador_actual_id']))
						model_controlador.save()

						logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Participante_interno',id_manipulado=model_controlador.id)
						logs_model_con.save()
						transaction.savepoint_commit(sid)

						model_organizador = Participante_interno(acta_id=serializer.data['id'],usuario_id=int(request.DATA['usuario_organizador_id']))
						model_organizador.save()

						logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Participante_interno',id_manipulado=model_organizador.id)
						logs_model_con.save()
						transaction.savepoint_commit(sid)

					else:
						model_controlador = Participante_interno(acta_id=serializer.data['id'],usuario_id=int(request.DATA['controlador_actual_id']))
						model_controlador.save()

						logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Participante_interno',id_manipulado=model_controlador.id)
						logs_model_con.save()
						transaction.savepoint_commit(sid)
					
					return Response({'message':'El registro ha sido guardado exitosamente.','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
						
				else:
					print(serializer.errors)
					return Response({'message':'Datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
    
	@transaction.atomic
	def update(self,request,*args,**kwargs):		
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()				
				modal_acta_anterior = Acta.objects.get(pk=instance.id)

				if 'acta_soporte' in request.DATA:
					if modal_acta_anterior:
						modal_acta_anterior.soporte = request.FILES['soporte']
						modal_acta_anterior.save()
						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Acta(SOPORTE)',id_manipulado=instance.id)
						logs_model.save()						
						return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
								
				if 'id_acta_previa' in request.DATA:
					if modal_acta_anterior:
						modal_acta_anterior.acta_previa_id = request.DATA['id_acta_previa']
						modal_acta_anterior.save()
						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Acta(SOPORTE)',id_manipulado=instance.id)
						logs_model.save()						
						return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':''},status=status.HTTP_201_CREATED)						

				serializer = ActaSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					
					serializer.save(controlador_actual_id=request.DATA['controlador_actual_id'],	
						usuario_organizador_id=request.DATA['usuario_organizador_id'],
						estado_id=request.DATA['estado_id'])
										

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Acta',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)

					validacion_participante_externo = Participante_interno.objects.filter(acta_id=instance.id,usuario_id=int(request.DATA['usuario_organizador_id'])).exists()
					#import pdb; pdb.set_trace()
					if modal_acta_anterior.usuario_organizador.id!=int(request.DATA['usuario_organizador_id']) and validacion_participante_externo==False:
						model_organizador = Participante_interno(acta_id=instance.id,usuario_id=int(request.DATA['usuario_organizador_id']))
						model_organizador.save()

						logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Participante_interno',id_manipulado=model_organizador.id)
						logs_model_con.save()
						transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':
			sid = transaction.savepoint()				
			try:
				instance = self.get_object()
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='acta_reunion.Acta',id_manipulado=instance.id)
				logs_model.save()

				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_200_OK)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class TemaViewSet(viewsets.ModelViewSet):
	model=Tema
	queryset = model.objects.all()
	serializer_class = TemaSerializer
	nombre_modulo = 'Acta_reunion - TemaViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
	
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(TemaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			page = self.request.query_params.get('page', None)
			lite = self.request.query_params.get('lite', None)		
			ID = self.request.query_params.get('id', None)
			
			acta_id = self.request.query_params.get('acta_id', None)	

			qset = (~Q(id = 0))
			if dato:
				qset = qset & (Q(acta__consecutivo__icontains=dato) | 
							  (Q(tema__icontains=dato)	|	
							  (Q(acta__tema_principal__icontains=dato)			  
						  	  ) ) )
			if acta_id:					
				qset = qset & (Q(acta__id=acta_id))

			queryset = self.model.objects.filter(qset).order_by('-id')

			
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = TemaLiteSerializer(page,many=True, context={'request': request,})							
					else:
						serializer = self.get_serializer(page,many=True)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
			if lite:
				serializer = TemaLiteSerializer(queryset,many=True, context={'request': request,})
			else:
				serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})


		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				#import pdb; pdb.set_trace()
				serializer = TemaSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(acta_id=request.DATA['acta_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Tema',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
						
				else:
					print(serializer.errors)
					return Response({'message':'Datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
    
	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = TemaSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					
					serializer.save(acta_id=request.DATA['acta_id'])
										

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Tema',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':
			sid = transaction.savepoint()				
			try:
				instance = self.get_object()
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='acta_reunion.Tema',id_manipulado=instance.id)
				logs_model.save()

				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_200_OK)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class Acta_historialViewSet(viewsets.ModelViewSet):
	model=Acta_historial
	queryset = model.objects.all()
	serializer_class = Acta_historialSerializer
	nombre_modulo = 'Acta_reunion - Acta_historialViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			#import pdb; pdb.set_trace()
			queryset = super(Acta_historialViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			page = self.request.query_params.get('page', None)
			lite = self.request.query_params.get('lite', None)		
			ID = self.request.query_params.get('id', None)

			acta_id = self.request.query_params.get('acta_id', None)

			fecha_desde = self.request.query_params.get('fecha_desde', None)
			fecha_hasta = self.request.query_params.get('fecha_hasta', None)

			tipo_operacion_id = self.request.query_params.get('tipo_operacion_id', None)
			controlador_id = self.request.query_params.get('controlador_id', None)
			
			qset = (~Q(id = 0))
			if dato:			
				qset = qset & (Q(motivo__icontains=dato) | 
							  (Q(acta__consecutivo__icontains=dato)			  
						  	  ) ) 

			if acta_id:
				qset = qset & (Q(acta__id=acta_id))

			if tipo_operacion_id:
				qset = qset & (Q(tipo_operacion__id=tipo_operacion_id))

			if controlador_id:
				qset = qset & (Q(controlador__id=controlador_id))	
			
			queryset = self.model.objects.filter(qset).order_by('-id')
			#import pdb; pdb.set_trace()
			for q in queryset:	
				if "_" in q.tipo_operacion.nombre:
					a = q.tipo_operacion
					b = a.nombre.replace("_"," ")
					a.nombre = b.capitalize()
					q.tipo_operacion = a
				else:
					a = q.tipo_operacion					
					a.nombre = a.nombre.capitalize()
					q.tipo_operacion = a					


			
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = Acta_historialLiteSerializer(page,many=True, context={'request': request,})							
					else:
						serializer = self.get_serializer(page,many=True)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
			if lite:
				serializer = Acta_historialLiteSerializer(queryset,many=True, context={'request': request,})
			else:
				serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})


		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				#import pdb; pdb.set_trace()
				serializer = Acta_historialSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(acta_id=request.DATA['acta_id'], 
						tipo_operacion_id=request.DATA['tipo_operacion_id'],
						controlador_id=request.DATA['controlador_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Acta_historial',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
						
				else:
					print(serializer.errors)
					return Response({'message':'Datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
    
	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = Acta_historialSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					
					serializer.save(acta_id=request.DATA['acta_id'], 
						tipo_operacion_id=request.DATA['tipo_operacion_id'],
						controlador_id=request.DATA['controlador_id'])
										

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Acta_historial',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':
			sid = transaction.savepoint()				
			try:
				instance = self.get_object()
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='acta_reunion.Acta_historial',id_manipulado=instance.id)
				logs_model.save()

				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_200_OK)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class Participante_externoViewSet(viewsets.ModelViewSet):
	model=Participante_externo
	queryset = model.objects.all()
	serializer_class = Participante_externoSerializer
	nombre_modulo = 'Acta_reunion - Participante_externoViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(Participante_externoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			page = self.request.query_params.get('page', None)
			lite = self.request.query_params.get('lite', None)		
			ID = self.request.query_params.get('id', None)

			acta_id = self.request.query_params.get('acta_id', None)
			persona_id = self.request.query_params.get('persona_id', None)

			asistio = self.request.query_params.get('asistio', None)
			
			qset = (~Q(id = 0))
			if dato:			
				qset = qset & (Q(persona__nombres__icontains=dato) | 
							  (Q(persona__apellidos__icontains=dato) | 
							  (Q(persona__cedula__icontains=dato) | 
							  (Q(acta__consecutivo__icontains=dato)			  
						  	  ) ) ))

			if acta_id:
				qset = qset & (Q(acta__id=acta_id))

			if persona_id:
				qset = qset & (Q(persona__id=persona_id))

			if asistio:
				qset = qset & (Q(asistio=asistio))	

			queryset = self.model.objects.filter(qset).order_by('-id')

			
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = Participante_externoLiteSerializer(page,many=True, context={'request': request,})							
					else:
						serializer = self.get_serializer(page,many=True)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
			if lite:
				serializer = Participante_externoLiteSerializer(queryset,many=True, context={'request': request,})
			else:
				serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})


		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				#import pdb; pdb.set_trace()
				serializer = Participante_externoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(acta_id=request.DATA['acta_id'], 
						persona_id=request.DATA['persona_id'])	

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Participante_externo',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
						
				else:
					print(serializer.errors)
					return Response({'message':'Datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
    
	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = Participante_externoSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					
					serializer.save(acta_id=request.DATA['acta_id'], 
						persona_id=request.DATA['persona_id'])					

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Participante_externo',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':
			sid = transaction.savepoint()				
			try:
				instance = self.get_object()
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='acta_reunion.Participante_externo',id_manipulado=instance.id)
				logs_model.save()

				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_200_OK)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class Participante_internoViewSet(viewsets.ModelViewSet):
	model=Participante_interno
	queryset = model.objects.all()
	serializer_class = Participante_internoSerializer
	nombre_modulo = 'Acta_reunion - Participante_internoViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
	
	def list(self, request, *args, **kwargs):
		try:
			queryset = super(Participante_internoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			page = self.request.query_params.get('page', None)
			lite = self.request.query_params.get('lite', None)		
			ID = self.request.query_params.get('id', None)

			acta_id = self.request.query_params.get('acta_id', None)
			usuario_id = self.request.query_params.get('usuario_id', None)

			asistio = self.request.query_params.get('asistio', None)
			
			qset = (~Q(id = 0))
			if dato:			
				qset = qset & (Q(usuario__persona__nombres__icontains=dato) | 
							  (Q(usuario__persona__apellidos__icontains=dato) | 
							  (Q(usuario__persona__cedula__icontains=dato) | 
							  (Q(acta__consecutivo__icontains=dato)			  
						  	  ) ) ))

			if acta_id:
				qset = qset & (Q(acta__id=acta_id))

			if usuario_id:
				qset = qset & (Q(usuario__id=usuario_id))

			if asistio:
				qset = qset & (Q(asistio=asistio))	

			queryset = self.model.objects.filter(qset).order_by('-id')

			
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = Participante_internoLiteSerializer(page,many=True, context={'request': request,})							
					else:
						serializer = self.get_serializer(page,many=True)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
			if lite:
				serializer = Participante_internoLiteSerializer(queryset,many=True, context={'request': request,})
			else:
				serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})


		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				#import pdb; pdb.set_trace()
				serializer = Participante_internoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(acta_id=request.DATA['acta_id'], 
						usuario_id=request.DATA['usuario_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Participante_interno',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
						
				else:
					print(serializer.errors)
					return Response({'message':'Datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
    
	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = Participante_internoSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					
					serializer.save(acta_id=request.DATA['acta_id'], 
						usuario_id=request.DATA['usuario_id'])					

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Participante_interno',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':
			sid = transaction.savepoint()				
			try:
				instance = self.get_object()
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='acta_reunion.Participante_interno',id_manipulado=instance.id)
				logs_model.save()

				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_200_OK)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class CompromisoViewSet(viewsets.ModelViewSet):
	model=Compromiso
	queryset = model.objects.all()
	serializer_class = CompromisoSerializer
	nombre_modulo = 'Acta_reunion - CompromisoViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			lite = self.request.query_params.get('lite', None)
			instance = self.get_object()

			if lite:
				serializer = CompromisoLiteSerializer(instance)
			else:
				serializer = self.get_serializer(instance)

			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(CompromisoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			page = self.request.query_params.get('page', None)
			lite = self.request.query_params.get('lite', None)		
			ID = self.request.query_params.get('id', None)

			acta_id = self.request.query_params.get('acta_id', None)
			supervisor_id= self.request.query_params.get('supervisor_id', None)
			participante_responsable_id= self.request.query_params.get('participante_responsable_id', None)
			usuario_responsable_id= self.request.query_params.get('usuario_responsable_id', None)
			estado_id= self.request.query_params.get('estado_id', None)

			fecha_compromiso_desde = self.request.query_params.get('fecha_compromiso_desde', None)
			fecha_compromiso_hasta = self.request.query_params.get('fecha_compromiso_hasta', None)

			fecha_cumplimiento_desde = self.request.query_params.get('fecha_cumplimiento_desde', None)
			fecha_cumplimiento_hasta = self.request.query_params.get('fecha_cumplimiento_hasta', None)

			responsable_interno = self.request.query_params.get('responsable_interno', None)
			requiere_soporte = self.request.query_params.get('requiere_soporte', None)
			tiene_prorroga = self.request.query_params.get('prorroga', None)
			#import pdb; pdb.set_trace()			
			qset = (~Q(id = 0))
			if acta_id:
				qset = qset & (Q(acta__id=acta_id))

			if dato and dato != 'null':			
				qset = qset & (Q(descripcion__icontains=dato) | 
							  (Q(acta__consecutivo__icontains=dato)			  
						  	  ) ) 
			if supervisor_id and supervisor_id != 'null':
				qset = qset & (Q(supervisor__id=supervisor_id))

			if participante_responsable_id and participante_responsable_id != 'null':
				qset = qset & (Q(participante_responsable__id=participante_responsable_id))

			if usuario_responsable_id and usuario_responsable_id != 'null':
				qset = qset & (Q(usuario_responsable__id=usuario_responsable_id))	

			if estado_id and estado_id != 'null':
				qset = qset & (Q(estado__id=estado_id))

			if responsable_interno and responsable_interno != 'null':
				qset = qset & (Q(responsable_interno=responsable_interno))	

			if requiere_soporte and requiere_soporte != 'null':
				qset = qset & (Q(requiere_soporte=requiere_soporte))

			if fecha_compromiso_desde and fecha_compromiso_desde != 'null':
				if fecha_compromiso_hasta:
					qset = qset & (Q(fecha_compromiso__range=(fecha_compromiso_desde,fecha_compromiso_hasta)))
				else:
					qset = qset & (Q(fecha_compromiso__gte=fecha_compromiso_desde))

			if fecha_compromiso_hasta and fecha_compromiso_hasta != 'null':
				if fecha_compromiso_desde:
					qset = qset & (Q(fecha_compromiso__range=(fecha_compromiso_desde,fecha_compromiso_hasta)))
				else:
					qset = qset & (Q(fecha_compromiso__lte=fecha_compromiso_hasta))

			if tiene_prorroga == 'true':
				queryset2 = self.model.objects.filter(acta_id=acta_id).values('id').distinct()
				qset = qset & (Q(id__in=queryset2))			

			compromisos = []
			if fecha_cumplimiento_desde or fecha_cumplimiento_hasta:
				qsetcumplimiento = (~Q(id = 0))
				if fecha_cumplimiento_desde:				
					qsetcumplimiento = qsetcumplimiento & (Q(fecha__gte=fecha_compromiso_desde))

				if fecha_cumplimiento_hasta:				
					qsetcumplimiento = qsetcumplimiento & (Q(fecha__lte=fecha_compromiso_hasta))

				compromisos = Compromiso_historial.objects.filter(qsetcumplimiento).values('compromiso__id')

			if compromisos:
				qset = qset & (Q(id__in=compromisos))

			queryset = self.model.objects.filter(qset).order_by('-id')

			
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = CompromisoLiteSerializer(page,many=True, context={'request': request,})							
					else:
						serializer = self.get_serializer(page,many=True)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
			if lite:
				serializer = CompromisoLiteSerializer(queryset,many=True, context={'request': request,})
			else:
				serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})


		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				
				serializer = CompromisoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					#import pdb; pdb.set_trace()

					diferencias = datetime.strptime(str(request.DATA['fecha_compromiso']), '%Y-%m-%d').date() - date.today()					
					diferencias_proximidad = datetime.strptime(str(request.DATA['fecha_compromiso']), '%Y-%m-%d').date() - datetime.strptime(str(request.DATA['fecha_proximidad']), '%Y-%m-%d').date()
					if diferencias.days > 0 and diferencias.days <= diferencias_proximidad.days:
						estado = estadoC.por_vencer

					if diferencias.days > diferencias_proximidad.days:
						estado = estadoC.por_cumplir


					if not request.DATA['participante_responsable_id']:
						request.DATA['participante_responsable_id'] = None
					
					#import pdb; pdb.set_trace()
					serializer.save(acta_id=request.DATA['acta_id'], 
						supervisor_id=request.DATA['supervisor_id'],	
						participante_responsable_id=request.DATA['participante_responsable_id'], 
						usuario_responsable_id=request.DATA['usuario_responsable_id'],
						estado_id=estado)				

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Compromiso',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)

					

					if request.DATA['responsable_interno']=='true':
						model_participante_interno=Participante_interno.objects.filter(acta__id=request.DATA['acta_id'],usuario__id=request.DATA['usuario_responsable_id'])
						model_historial = Compromiso_historial(
							compromiso_id=int(serializer.data['id']),
							fecha=request.DATA['fecha_compromiso'],
							tipo_operacion_id=int(tipoCH.creacion),
							motivo='',
							participante_interno_id=int(model_participante_interno[0].id))
						model_historial.save()

					else :
						model_historial = Compromiso_historial(
							compromiso_id=int(serializer.data['id']),
							fecha=request.DATA['fecha_compromiso'],
							tipo_operacion_id=int(tipoCH.creacion),
							motivo='',
							participante_externo_id=int(request.DATA['participante_responsable_id']))
						model_historial.save()

						

					logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Compromiso_historial',id_manipulado=model_historial.id)
					logs_model_con.save()

					transaction.savepoint_commit(sid)

					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
						
				else:
					print(serializer.errors)
					return Response({'message':'Datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
    
	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				#import pdb; pdb.set_trace()
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = CompromisoSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					
					serializer.save(acta_id=request.DATA['acta_id'], 
						supervisor_id=request.DATA['supervisor_id'],	
						participante_responsable_id=request.DATA['participante_responsable_id'], 
						usuario_responsable_id=request.DATA['usuario_responsable_id'],
						estado_id=instance.estado.id)			

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Compromiso',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':
			sid = transaction.savepoint()				
			try:
				instance = self.get_object()
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='acta_reunion.Compromiso',id_manipulado=instance.id)
				logs_model.save()

				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_200_OK)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class Compromiso_historialViewSet(viewsets.ModelViewSet):
	model=Compromiso_historial
	queryset = model.objects.all()
	serializer_class = Compromiso_historialSerializer
	nombre_modulo = 'Acta_reunion - Compromiso_historialViewSet'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(Compromiso_historialViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			page = self.request.query_params.get('page', None)
			lite = self.request.query_params.get('lite', None)		
			ID = self.request.query_params.get('id', None)

			compromiso_id = self.request.query_params.get('compromiso_id', None)
			tipo_operacion_id = self.request.query_params.get('tipo_operacion_id', None)

			participante_externo_id = self.request.query_params.get('participante_externo_id', None)
			participante_interno_id = self.request.query_params.get('participante_interno_id', None)

			fecha_desde = self.request.query_params.get('fecha_desde', None)
			fecha_hasta = self.request.query_params.get('fecha_hasta', None)

			
			qset = (~Q(id = 0))
			if dato:			
				qset = qset & (Q(motivo__icontains=dato) | 
							  (Q(compromiso__descripcion__icontains=dato)		  
						  	  ) ) 

			if compromiso_id:
				qset = qset & (Q(compromiso__id=compromiso_id))

			if tipo_operacion_id:
				qset = qset & (Q(tipo_operacion__id=tipo_operacion_id))

			if participante_externo_id:
				qset = qset & (Q(participante_externo__id=participante_externo_id))

			if participante_interno_id:
				qset = qset & (Q(participante_interno__id=participante_interno_id))

			if fecha_desde:
				qset = qset & (Q(fecha__gte=fecha_desde))

			if fecha_hasta:
				qset = qset & (Q(fecha__lte=fecha_hasta))

			queryset = self.model.objects.filter(qset).order_by('-id')

			
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					if lite:
						serializer = Compromiso_historialLiteSerializer(page,many=True, context={'request': request,})							
					else:
						serializer = self.get_serializer(page,many=True)

					return self.get_paginated_response({'message':'','success':'ok',
					'data':serializer.data})
			if lite:
				serializer = Compromiso_historialLiteSerializer(queryset,many=True, context={'request': request,})
			else:
				serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok',
				'data':serializer.data})


		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				#import pdb; pdb.set_trace()
				serializer = Compromiso_historialSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(compromiso_id=request.DATA['compromiso_id'], 
						tipo_operacion_id=request.DATA['tipo_operacion_id'],	
						participante_externo_id=request.DATA['participante_externo_id'], 
						participante_interno_id=request.DATA['participante_interno_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Compromiso_historial',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
						
				else:
					print(serializer.errors)
					return Response({'message':'Datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
    	
	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = Compromiso_historialSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					
					serializer.save(compromiso_id=request.DATA['compromiso_id'], 
						tipo_operacion_id=request.DATA['tipo_operacion_id'],	
						participante_externo_id=request.DATA['participante_externo_id'], 
						participante_interno_id=request.DATA['participante_interno_id'])					

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Compromiso_historial',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if serializer.errors['non_field_errors']:
						mensaje = serializer.errors['non_field_errors']
					else:
						mensaje='datos requeridos no fueron recibidos'
					return Response({'message':mensaje,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def destroy(self,request,*args,**kwargs):
		if request.method == 'DELETE':
			sid = transaction.savepoint()				
			try:
				instance = self.get_object()
				self.perform_destroy(instance)
				serializer = self.get_serializer(instance)
				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='acta_reunion.Compromiso_historial',id_manipulado=instance.id)
				logs_model.save()

				transaction.savepoint_commit(sid)
				return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_200_OK)
			except Exception as e:
				transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)

@login_required
def filtrar_proyectoscontratos(request):
	
	if request.method == 'GET':
		try:
			macrocontrato_id = request.GET['mcontrato'] if request.GET['mcontrato'] else None
			proyecto_id = request.GET['proyecto'] if request.GET['proyecto'] else None	

			if macrocontrato_id and proyecto_id==None:
				proyectos=Proyecto.objects.filter(mcontrato__id=macrocontrato_id).values('id','nombre')
				contratos=Contrato.objects.filter(mcontrato__id=macrocontrato_id).values('id','nombre')
				
				return JsonResponse({'message':'','success':'ok',
					'data':{'contratos':list(contratos),'proyectos':list(proyectos)}})

			elif macrocontrato_id and proyecto_id:
				#import pdb; pdb.set_trace()
				contratos=Proyecto.objects.filter(pk=proyecto_id,contrato__mcontrato=None).values('contrato__id','contrato__nombre')
				list_contratos = []

				for p in contratos:
					list_contratos.append({'id': p['contrato__id'], 'nombre': p['contrato__nombre']})

				contratos=Contrato.objects.filter(mcontrato__id=macrocontrato_id).values('id','nombre')
				for p in contratos:
					list_contratos.append({'id': p['id'], 'nombre': p['nombre']} )

				return JsonResponse({'message':'','success':'ok',
					'data':{'contratos':list(list_contratos)}})

			else:
				return JsonResponse({'message':'No se recibió filtro','success':'fail', 'data':''},
					status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:			
			functions.toLog(e,self.nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
		    'data':''},status=status.HTTP_400_BAD_REQUEST)


@login_required
def obtener_participantes(request):
	#import pdb; pdb.set_trace()
	if request.method == 'GET':
		try:
			acta_id = request.GET['acta_id'] if request.GET['acta_id'] else None
			participantes = []

			externos = Participante_externo.objects.filter(acta__id=acta_id)
			internos = Participante_interno.objects.filter(acta__id=acta_id)

			model_acta = Acta.objects.get(pk=acta_id)

			for participante in internos:
				if participante.usuario.id==model_acta.usuario_organizador.id and participante.usuario.id!=model_acta.controlador_actual.id:
					participantes.append({
						'id':participante.id,
						'nombre_completo':participante.usuario.persona.nombres+' '+participante.usuario.persona.apellidos,
						'tipo':'interno',
						'empresa':participante.usuario.empresa.nombre,
						'funcion':'Organizador',
						'asistio':participante.asistio,
						})
				elif participante.usuario.id==model_acta.controlador_actual.id and participante.usuario.id!=model_acta.usuario_organizador.id:
					participantes.append({
						'id':participante.id,
						'nombre_completo':participante.usuario.persona.nombres+' '+participante.usuario.persona.apellidos,
						'tipo':'interno',
						'empresa':participante.usuario.empresa.nombre,
						'funcion':'Controlador',
						'asistio':participante.asistio,
						})
				elif participante.usuario.id==model_acta.controlador_actual.id and participante.usuario.id==model_acta.usuario_organizador.id:
					participantes.append({
						'id':participante.id,
						'nombre_completo':participante.usuario.persona.nombres+' '+participante.usuario.persona.apellidos,
						'tipo':'interno',
						'empresa':participante.usuario.empresa.nombre,
						'funcion':'Controlador y Organizador',
						'asistio':participante.asistio,
						})
				else:					
					if participante.usuario.user.is_active:
						participantes.append({
							'id':participante.id,
							'nombre_completo':participante.usuario.persona.nombres+' '+participante.usuario.persona.apellidos,
							'tipo':'interno',
							'empresa':participante.usuario.empresa.nombre,
							'funcion':'',
							'asistio':participante.asistio,
							})

			for participante in externos:
				if Usuario.objects.filter(persona__id=participante.persona.id).exists():
					empresa=Usuario.objects.filter(persona__id=participante.persona.id).values('empresa__nombre')
					participantes.append({
						'id':participante.id,
						'nombre_completo':participante.persona.nombres+' '+participante.persona.apellidos,
						'tipo':'externo',
						'empresa':empresa[0]['empresa__nombre'],
						'funcion':'',
						'asistio':participante.asistio,
						})
				else:
					participantes.append({
						'id':participante.id,
						'nombre_completo':participante.persona.nombres+' '+participante.persona.apellidos,
						'tipo':'externo',
						'empresa':'',
						'funcion':'',
						'asistio':participante.asistio,
						})

			return JsonResponse({'message':'','success':'ok','data':list(participantes)})
		except Exception as e:			
			functions.toLog(e,self.nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
		    'data':''},status=status.HTTP_400_BAD_REQUEST)

@transaction.atomic
def eliminar_varios_participantes_id(request):
	sid = transaction.savepoint()
	try:
		
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		#print respuesta['lista'].split()

		#lista=respuesta['lista'].split(',')
		#import pdb; pdb.set_trace()
		count = 0
		count2 = 0
		lista_no_eliminado = []
		for item in respuesta['lista']:
			if item['tipo'] == 'interno':
				model_participante = Participante_interno.objects.get(id=item['id'])
				validation = True

				if Compromiso.objects.filter(supervisor__id=model_participante.usuario.id).count()>0:
					validation = False

				elif Compromiso.objects.filter(usuario_responsable__id=model_participante.usuario.id).count()>0:
					validation = False

				if validation == True:
					model_participante.delete()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='acta_reunion.Participante_interno',id_manipulado=item['id'])
					logs_model.save()
				else:
					count2+=1
					lista_no_eliminado.append({
						'nombre_completo':model_participante.usuario.persona.nombres+' '+model_participante.usuario.persona.apellidos
						})

				

			elif item['tipo'] == 'externo':
				model_participante = Participante_externo.objects.get(id=item['id'])
				if Compromiso.objects.filter(acta__id=int(model_participante.acta.id),participante_responsable__id=model_participante.id).count()==0:
					model_participante.delete()

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='acta_reunion.Participante_externo',id_manipulado=item['id'])
					logs_model.save()

				else:
					count2+=1
					lista_no_eliminado.append({
						'nombre_completo':model_participante.persona.nombres+' '+model_participante.persona.apellidos
						})
			count+=1
		#return HttpResponse(str('0'), content_type="text/plain")

		transaction.savepoint_commit(sid)
		mensaje = ''
		if count==1:			
			mensaje = 'El registro se ha eliminado correctamente'
		elif count>1:
			mensaje = 'Los registros se ha eliminado correctamente'

		if count2>0:
			mensaje = 'Debido a que estan vinculados con algunos compromisos, los siguientes participantes no se pudieron eliminar: <br>'		

			for item in lista_no_eliminado:				
				mensaje = mensaje + '<br>-'+item['nombre_completo']
				


		return JsonResponse({'message':mensaje,'success':'ok',
					'data':''})

	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})
		
	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})			 

@transaction.atomic
@api_view(['DELETE',])
def cerrar_acta(request):
	sid = transaction.savepoint()
	try:
		#import pdb; pdb.set_trace()
		lista=request.POST['_content']
		respuesta= json.loads(lista)

		model = Acta.objects.get(pk=int(respuesta['acta_id']))

		if not model.soporte:
			return JsonResponse({'message':'No se puede cerrar el acta, hasta que se cargue a SININ el soporte del acta','success':'fail',
				'data':''})
		model.estado_id=estadoA.cerrada			
		model.save()		

		model_acta_historial = Acta_historial(
			acta_id=int(respuesta['acta_id']),
			fecha=date.today(),
			tipo_operacion_id=tipoAH.cerrar,
			motivo=str(respuesta['motivo']),
			controlador_id=model.controlador_actual.id,)

		model_acta_historial.save()

		logs_model=Logs(usuario_id=request.user.usuario.id
								,accion=Acciones.accion_actualizar
								,nombre_modelo='actareunion.Acta_historial'
								,id_manipulado=model_acta_historial.id)
		logs_model.save()		
		#import pdb; pdb.set_trace()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El acta de reunión No. Acta '+str(model.consecutivo)+' se ha cerrado correctamente','success':'ok',
				'data':''})

	except Exception as e:
		##print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})
@login_required
def acta_examinar(request,acta_id):	
	listActa = Acta.objects.get(id=acta_id)
	participante_interno = Participante_interno.objects.filter(acta__id=acta_id).values('usuario__id','usuario__persona__nombres','usuario__persona__apellidos')
	participante_externo = Participante_externo.objects.filter(acta__id=acta_id).values('id','persona__nombres','persona__apellidos')
	return render(request, 'actareunion/acta_examinar.html',{'model':'acta','app':'acta','acta':listActa,'participantes_internos':list(participante_interno),'participantes_externos':list(participante_externo)})	
	



@login_required
def ver_soporte_acta (request):
	if request.method == 'GET':
		try:			
			archivo = Acta.objects.get(pk=request.GET['id'])			
			return functions.exportarArchivoS3(str(archivo.soporte))

		except Exception as e:
			functions.toLog(e,'contrato.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			

@login_required
def obtener_noparticipantes(request):
	if request.method == 'GET':
		try:
			
			acta_id=request.GET['acta_id'] if request.GET['acta_id'] else None

			if acta_id:
				participantes=[]
				
				participantes_internos_actuales =Participante_interno.objects.filter(acta__id=acta_id).values('usuario__persona__id')
				participantes_externos_actuales =Participante_externo.objects.filter(acta__id=acta_id).values('persona__id')

				qset1 = (~Q(id__in=participantes_internos_actuales) &(Q(user__is_active=True)))
				personas_usuarios=Usuario.objects.filter(qset1).values('persona__id')


				personas_con_usuarios=Usuario.objects.filter(user__is_active=True).values('persona__id')
				qset2 = (~Q(id__in=participantes_externos_actuales) & (~Q(id__in=personas_con_usuarios)))
				personas=Persona.objects.filter(qset2)

				

				participantes.append({
					'internos':[{'id': p.id, 'nombre_completo': p.persona.nombres+' '+p.persona.apellidos} for p in usuarios],
					'externos':[{'id': p.id, 'nombre_completo': p.nombres+' '+p.apellidos} for p in personas],
					})

				#import pdb; pdb.set_trace()
				return JsonResponse({'message':'','success':'ok','data':list(participantes)})
			else:
				return JsonResponse({'message':'No se recibió acta_id','success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			functions.toLog(e,'contrato.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			




class NoParticipantesViewSet(viewsets.ModelViewSet):
	model=Persona
	queryset = model.objects.all()
	serializer_class = NoParticipantesSerializer
	nombre_modulo = 'Acta_reunion - NoParticipantesViewSet'

	def list(self, request, *args, **kwargs):
		try:
			
			queryset = super(NoParticipantesViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			page = self.request.query_params.get('page', None)
			cedula = self.request.query_params.get('cedula', None)
			acta_id = self.request.query_params.get('acta_id', None)
			solo_internos = self.request.query_params.get('solo_internos', None)

			qset = (~Q(id = 0))			

			if acta_id:
				participantes_internos_actuales =Participante_interno.objects.filter(acta__id=acta_id).values('usuario__persona__id')
				participantes_externos_actuales =Participante_externo.objects.filter(acta__id=acta_id).values('persona__id')

				qset = qset & (~Q(id__in=participantes_externos_actuales) & (~Q(id__in=participantes_internos_actuales)))
			
			if dato:			
				qset = qset & (Q(nombres__icontains=dato) |
							  (Q(apellidos__icontains=dato)	|
							  (Q(cedula__icontains=dato)  
						  	  ) ) )
			elif cedula:
				qset = qset & (Q(cedula__icontains=cedula)  
						  	  )

			
			if solo_internos=='true':
				#print(solo_internos)
				qsetUsuarios = (Q(user__is_active=True))
				usuario_internos = Usuario.objects.filter(qsetUsuarios).values('persona__id')
				qset = qset & (Q(id__in=usuario_internos)) 
			
			queryset = self.model.objects.filter(qset).order_by('nombres')

			#import pdb; pdb.set_trace()
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
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def exportar_actas(request):
	
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="Reporte_actas_reunion.xls"'
		
		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Actas de reunión')
		format1=workbook.add_format({'border':0,'font_size':12,'bold':True})		
		format2=workbook.add_format({'border':0})
		format1.set_align('center')
		format2.set_align('center')
		format2.set_align('vcenter')

		format3=workbook.add_format({'border':0,'font_size':12})
		#format3.set_align('center')
		#format3.set_align('vcenter')

		format5=workbook.add_format()
		format5.set_num_format('yyyy-mm-dd')
		format5.set_align('center')

		worksheet.set_column('A:C', 25)
		worksheet.set_column('D:D', 50)
		worksheet.set_column('E:F', 25)
		worksheet.set_column('G:I', 50)

		row=1
		col=0

		dato = request.GET['dato'] if request.GET['dato'] else None

		controlador_id = request.GET['controlador_id'] if request.GET['controlador_id'] else None
		organizador_id = request.GET['organizador_id'] if request.GET['organizador_id'] else None
		estado_id = request.GET['estado_id'] if request.GET['estado_id'] else None

		fecha_desde = request.GET['desde'] if request.GET['desde'] else None
		fecha_hasta = request.GET['hasta'] if request.GET['hasta'] else None

		proyecto_id = request.GET['proyecto_id'] if request.GET['proyecto_id'] else None
		contrato_id = request.GET['contrato_id'] if request.GET['contrato_id'] else None

		macrocontrato_id= request.GET['macrocontrato_id'] if request.GET['macrocontrato_id'] else None

		

		qset = (~Q(id = 0))
		if dato:
			qset = qset & (Q(consecutivo__icontains=dato) | 
						  (Q(tema_principal__icontains=dato)					  
					  	  ) )
		if controlador_id:
			qset = qset & Q(controlador_actual__id=controlador_id)

		if organizador_id:
			qset = qset & Q(usuario_organizador__id=organizador_id)

		if estado_id:
			qset = qset & Q(estado__id=estado_id)

		if macrocontrato_id:
			qset = qset & Q(contrato__id=macrocontrato_id)		

		if proyecto_id:
			qset = qset & Q(proyecto__id=proyecto_id)			

		if contrato_id:
			qset = qset & Q(contrato__id=contrato_id)
	
		if fecha_desde:
			qset = qset & (Q(fecha__gte=fecha_desde))

		if fecha_hasta:
			qset = qset & (Q(fecha__lte=fecha_hasta))

		actas_participantes = Participante_interno.objects.filter(usuario__id=request.user.usuario.id).values('acta__id')
		qset = qset & (Q(id__in=actas_participantes))

		queryset = Acta.objects.filter(qset).order_by('-id')

		serializer_context = {
			'request': request
		}

		#import pdb; pdb.set_trace()
		serializer = ActaLiteSerializer(queryset,many=True,context=serializer_context)

		if serializer:
			worksheet.write('A1', 'No. Acta', format1)
			worksheet.write('B1', 'Fecha', format1)
			worksheet.write('C1', 'Acta previa', format1)
			worksheet.write('D1', 'Tema principal', format1)
			worksheet.write('E1', 'Soporte', format1)
			worksheet.write('F1', 'Estado', format1)
			worksheet.write('G1', 'Organizador', format1)
			worksheet.write('H1', 'Controlador', format1)

			
			
			if serializer.data:
				for item in serializer.data:
					#import pdb; pdb.set_trace()
					worksheet.write(row, col,item['consecutivo'],format2)
					worksheet.write(row, col+1,item['fecha'],format5)
					worksheet.write(row, col+2,item['acta_previa'],format2)
					worksheet.write(row, col+3,item['tema_principal'],format3)
					
					if item['soporte']:
						worksheet.write(row, col+4,'Cargado',format2)
					else:
						worksheet.write(row, col+4,'Pendiente',format2)

					worksheet.write(row, col+5,item['estado']['nombre'],format2)
					worksheet.write(row, col+6,item['usuario_organizador']['persona']['nombres']+' '+item['controlador_actual']['persona']['apellidos'],format3)
					worksheet.write(row, col+7,item['controlador_actual']['persona']['nombres']+' '+item['controlador_actual']['persona']['apellidos'],format3)

					row +=1
					
		workbook.close()
		return response
	except Exception as e:
		#print(e)
		functions.toLog(e,'actareunion')
		return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def anularActa(request):
	#import pdb; pdb.set_trace()
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)

			model = Acta.objects.get(pk=int(respuesta['acta_id']))
			model.estado_id=estadoA.anulada			
			model.save()

			logs_model=Logs(usuario_id=request.user.usuario.id
									,accion=Acciones.accion_actualizar
									,nombre_modelo='actareunion.Acta'
									,id_manipulado=model.id)
			logs_model.save()

			transaction.savepoint_commit(sid)

			model_acta_historial = Acta_historial(
				acta_id=int(respuesta['acta_id']),
				fecha=date.today(),
				tipo_operacion_id=tipoAH.anulacion,
				motivo=str(respuesta['motivo_anular']),
				controlador_id=model.controlador_actual.id,)

			model_acta_historial.save()

			logs_model=Logs(usuario_id=request.user.usuario.id
									,accion=Acciones.accion_crear
									,nombre_modelo='actareunion.Acta_historial'
									,id_manipulado=model_acta_historial.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El acta se ha anulado correctamente','success':'ok',
						'data':''})

		except Exception as e:
			functions.toLog(e,'acta_reunion.Acta(anular)')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})

@transaction.atomic
def transferir_acta(request):
	sid = transaction.savepoint()
	try:
		#import pdb; pdb.set_trace()

		respuesta=request.POST['_content']
		acta= json.loads(respuesta)
	

		model_acta = Acta.objects.get(pk=int(acta['acta_id']))
		model_acta.controlador_actual_id=int(acta['controlador_id'])
		model_acta.save()

		logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Acta',id_manipulado=acta['acta_id'])
		logs_model.save()

		transaction.savepoint_commit(sid)


		model_acta_historial = Acta_historial(
			acta_id=int(acta['acta_id']),
			fecha=date.today(),
			tipo_operacion_id=tipoAH.sesion_control,
			motivo=str(acta['motivo']),
			controlador_id=int(acta['controlador_id']),)

		model_acta_historial.save()

		logs_model=Logs(usuario_id=request.user.usuario.id
								,accion=Acciones.accion_crear
								,nombre_modelo='actareunion.Acta_historial'
								,id_manipulado=model_acta_historial.id)
		logs_model.save()

		transaction.savepoint_commit(sid)

		return JsonResponse({'message':'Se transfirió el control del acta de reunión No. '+str(model_acta.consecutivo)+' correctamente','success':'ok',
				'data':''})

	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})

@transaction.atomic
def subirsoporte_acta(request):
	sid = transaction.savepoint()
	try:
		#import pdb; pdb.set_trace()
		soporte= request.FILES['soporte'] if request.FILES['soporte'] else None
		acta_id= request.POST['id'] if request.POST['id'] else None

		if soporte and acta_id:
			model_acta = Acta.objects.get(pk=int(acta_id))
			model_acta.soporte=soporte
			model_acta.save()

			logs_model=Logs(usuario_id=request.user.usuario.id
								,accion=Acciones.accion_actualizar
								,nombre_modelo='actareunion.Acta(soporte)'
								,id_manipulado=model_acta.id)
			logs_model.save()

			transaction.savepoint_commit(sid)

			return JsonResponse({'message':'Se subió soporte del acta de reunión No. '+str(model_acta.consecutivo)+' correctamente','success':'ok',
				'data':''})
		else:
			return JsonResponse({'message':'No se recibió alguno de los datos','success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)

	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})

@transaction.atomic
def desasignarContrato(request):
	nombre_modulo = 'Actas - AsignarContrato'
	if request.method == 'POST':
		try:
			#import pdb; pdb.set_trace()	
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']
			acta = Acta.objects.get(pk=respuesta['id'])
			for item in myList:				
				acta.contrato.remove(item['id'])
				# Proyecto.objects.filter(id = item ).delete()
			acta.save()
			# transaction.commit()
			return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok','data': ''})
		except Exception as e:
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def asignarContrato(request):
	nombre_modulo = 'Actas - AsignarContrato'
	if request.method == 'POST':
		try:
			#import pdb; pdb.set_trace()	
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']
			acta = Acta.objects.get(pk=respuesta['id'])
			for item in myList:				
				acta.contrato.add(item['id'])
				# Proyecto.objects.filter(id = item ).delete()
			acta.save()
			# transaction.commit()
			return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok','data': ''})
		except Exception as e:
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def desasignarProyecto(request):
	nombre_modulo = 'Actas - AsignarProyecto'
	if request.method == 'POST':
		try:
			#import pdb; pdb.set_trace()	
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']
			acta = Acta.objects.get(pk=respuesta['id'])
			for item in myList:				
				acta.proyecto.remove(item['id'])
				# Proyecto.objects.filter(id = item ).delete()
			acta.save()
			# transaction.commit()
			return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok','data': ''})
		except Exception as e:
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def asignarProyecto(request):
	nombre_modulo = 'Actas - AsignarProyecto'
	if request.method == 'POST':
		try:
			#import pdb; pdb.set_trace()	
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']
			acta = Acta.objects.get(pk=respuesta['id'])
			for item in myList:				
				acta.proyecto.add(item['id'])
				# Proyecto.objects.filter(id = item ).delete()
			acta.save()
			# transaction.commit()
			return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok','data': ''})
		except Exception as e:
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def subirconclusiones_acta(request):
	sid = transaction.savepoint()
	#import pdb; pdb.set_trace()
	nombre_modulo = 'Actas - SubirConclusiones'
	if request.method == 'POST':
		try:
			conclusiones= request.POST['conclusiones'] if request.POST['conclusiones'] else None
			acta_id= request.POST['id'] if request.POST['id'] else None

			if conclusiones and acta_id:
				model_acta = Acta.objects.get(pk=int(acta_id))
				model_acta.conclusiones=conclusiones
				model_acta.save()

				logs_model=Logs(usuario_id=request.user.usuario.id
									,accion=Acciones.accion_actualizar
									,nombre_modelo='actareunion.Acta(conclusiones)'
									,id_manipulado=model_acta.id)
				logs_model.save()

				transaction.savepoint_commit(sid)

				return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok','data': ''})
			else:
				return JsonResponse({'message':'No se recibió alguno de los datos','success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			functions.toLog(e, nombre_modulo)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def asistencia_acta(request):
	sid = transaction.savepoint()
	try:
		
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		#print respuesta['lista'].split()

		#lista=respuesta['lista'].split(',')
		#import pdb; pdb.set_trace()
		for item in respuesta['lista']:
			if item['tipo'] == 'interno':				
				model_interno= Participante_interno.objects.get(id=item['id'])
				model_interno.asistio = item['asistio']
				model_interno.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Participante_interno',id_manipulado=item['id'])
				logs_model.save()

			elif item['tipo'] == 'externo':
				model_externo= Participante_externo.objects.get(id=item['id'])
				model_externo.asistio = item['asistio']
				model_externo.save()

				logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Participante_externo',id_manipulado=item['id'])
				logs_model.save()
		#return HttpResponse(str('0'), content_type="text/plain")

			

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok',
				'data':''})

	except ProtectedError:
		return JsonResponse({'message':'No es posible eliminar el registro, se esta utilizando en otra seccion del sistema','success':'error','data':''})
		
	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})

@transaction.atomic
@login_required
def actualizar_tienes_acta(request):
	#import pdb; pdb.set_trace()
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)

			model = Acta.objects.get(pk=int(respuesta['id']))
			if str(respuesta['tipo'])=='tiene_contrato':
				model.tiene_contrato = respuesta['valor']

				if model.tiene_contrato == False:
					contratos = Acta.objects.filter(pk=model.id).values('contrato__id')
					for item in contratos:				
						model.contrato.remove(item['contrato__id'])

			elif str(respuesta['tipo'])=='tiene_proyecto':
				model.tiene_proyecto = respuesta['valor']

				if model.tiene_proyecto == False:
					proyectos = Acta.objects.filter(pk=model.id).values('proyecto__id')
					for item in proyectos:				
						model.proyecto.remove(item['proyecto__id'])

			elif str(respuesta['tipo'])=='tiene_conclusiones':
				model.tiene_conclusiones = respuesta['valor']


				if model.tiene_conclusiones == False:
					model.conclusiones=''

			elif str(respuesta['tipo'])=='tiene_compromisos':
				model.tiene_compromisos	 = respuesta['valor']				
		
				if model.tiene_compromisos==False:

					
					comprosmisos = Compromiso.objects.filter(acta__id=model.id,estado__id__in=[estadoC.por_cumplir, estadoC.por_vencer, estadoC.vencido, estadoC.cumplido, estadoC.cumplido_despues_vencido])
					for compromiso in comprosmisos:
						compromiso.estado_id = estadoC.cancelado
						compromiso.save()

						if compromiso.responsable_interno==True:
							model_participante_interno=Participante_interno.objects.filter(acta__id=compromiso.acta.id,usuario__id=compromiso.usuario_responsable.id)
							model_historial = Compromiso_historial(
								compromiso_id=int(compromiso.id),
								fecha=date.today(),
								tipo_operacion_id=int(tipoCH.cancelacion),
								motivo='El acta no tiene compromisos',
								participante_interno_id=int(model_participante_interno[0].id))
							model_historial.save()			
						else:
							model_historial = Compromiso_historial(
								compromiso_id=int(compromiso.id),
								fecha=date.today(),
								tipo_operacion_id=int(tipoCH.cancelacion),
								motivo='El acta no tiene compromisos',
								participante_externo_id=int(compromiso.participante_responsable_id))
							model_historial.save()

						logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Compromiso_historial',id_manipulado=model_historial.id)
						logs_model_con.save()

						transaction.savepoint_commit(sid)

				elif model.tiene_compromisos==True:
					comprosmisos = Compromiso.objects.filter(acta__id=model.id,estado__id=estadoC.cancelado)
					#import pdb; pdb.set_trace()
					for compromiso in comprosmisos:
						ultimo_historial_compromiso = Compromiso_historial.objects.filter(compromiso__id=compromiso.id,tipo_operacion__id__in=[tipoCH.creacion,tipoCH.proroga,tipoCH.cumplimiento]).order_by('id').last()
						if int(ultimo_historial_compromiso.tipo_operacion_id) in [tipoCH.creacion,tipoCH.proroga]:
							

							diferencias = datetime.strptime(str(compromiso.fecha_compromiso), '%Y-%m-%d').date() - date.today()
							diferencias_proximidad = datetime.strptime(str(compromiso.fecha_compromiso), '%Y-%m-%d').date() - datetime.strptime(str(compromiso.fecha_proximidad), '%Y-%m-%d').date()

							if diferencias.days <= 0:
								compromiso.estado_id = estadoC.vencido

							if diferencias.days > 0 and diferencias.days <= diferencias_proximidad.days:
								compromiso.estado_id = estadoC.por_vencer

							if diferencias.days > diferencias_proximidad.days:
								compromiso.estado_id = estadoC.por_cumplir

							compromiso.save()							

						elif int(ultimo_historial_compromiso.tipo_operacion_id)==tipoCH.cumplimiento:
				
							if compromiso.fecha_compromiso>=ultimo_historial_compromiso.fecha:
								compromiso.estado_id=estadoC.cumplido
							else:
								compromiso.estado_id=estadoC.cumplido_despues_vencido

							compromiso.save()


						if compromiso.responsable_interno==True:
							model_participante_interno=Participante_interno.objects.filter(acta__id=compromiso.acta.id,usuario__id=compromiso.usuario_responsable.id)
							model_historial = Compromiso_historial(
								compromiso_id=int(compromiso.id),
								fecha=date.today(),
								tipo_operacion_id=int(tipoCH.restablecer),
								motivo='El compromiso cancelado se ha restablecido',
								participante_interno_id=int(model_participante_interno[0].id))
							model_historial.save()			
						else:
							model_historial = Compromiso_historial(
								compromiso_id=int(compromiso.id),
								fecha=date.today(),
								tipo_operacion_id=int(tipoCH.restablecer),
								motivo='El compromiso cancelado se ha restablecido',
								participante_externo_id=int(compromiso.participante_responsable_id))
							model_historial.save()





			else:
				return JsonResponse({'message':'No se recibió los datos requeridos','success':'fail','data':''})

			model.save()

			logs_model=Logs(usuario_id=request.user.usuario.id
									,accion=Acciones.accion_actualizar
									,nombre_modelo='actareunion.Acta'
									,id_manipulado=model.id)
			logs_model.save()

			

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'La acta se ha actualizado correctamente','success':'ok',
						'data':''})

		except Exception as e:
			functions.toLog(e,'acta_reunion.Acta(boolean)')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})


@login_required
@transaction.atomic
def obtener_porcentaje_acta(request):
	#import pdb; pdb.set_trace()
	sid = transaction.savepoint()
	if request.method == 'GET':
		try:
			acta_id = request.GET['acta_id'] if request.GET['acta_id'] else None

			model_acta = Acta.objects.get(pk=acta_id)

			porcentaje = 0

			#print(porcentaje)
			if model_acta.tiene_contrato:
				if model_acta.contrato.count()>0:
					porcentaje+=20
			else:
				porcentaje+=20


			#print(porcentaje)
			if model_acta.tiene_proyecto:
				if model_acta.proyecto.count()>0:
					porcentaje+=20
			else:
				porcentaje+=20

			#print(porcentaje)
			if model_acta.tiene_conclusiones:
				if model_acta.conclusiones:
					porcentaje+=20
			else:
				porcentaje+=20

			#print(porcentaje)
			if model_acta.tiene_compromisos:
				if Compromiso.objects.filter(acta__id=model_acta.id).count()>0:
					porcentaje+=20
			else:
				porcentaje+=20

			#print(porcentaje)
			if model_acta.soporte:
				porcentaje+=20

			
			#import pdb; pdb.set_trace()
			if porcentaje==100 and model_acta.estado_id==estadoA.pausada:
				
				model_acta.estado_id=estadoA.en_curso
				model_acta.save()
				
				model_acta_historial = Acta_historial(
					acta_id=model_acta.id,
					fecha=date.today(),
					tipo_operacion_id=int(tipoAH.dar_curso),
					motivo='',
					controlador_id=model_acta.controlador_actual_id)
				model_acta_historial.save()

				logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Acta_historial',id_manipulado=model_acta_historial.id)
				logs_model_con.save()

				transaction.savepoint_commit(sid)


				logs_model=Logs(usuario_id=request.user.usuario.id
								,accion=Acciones.accion_actualizar
								,nombre_modelo='actareunion.Acta(en_curso)'
								,id_manipulado=model_acta.id)
				logs_model.save()
				transaction.savepoint_commit(sid)


			#print(porcentaje)
			return JsonResponse({'message':'','success':'ok','data':{
				'porcentaje':porcentaje,
				'estado':{
					'id':model_acta.estado.id,
					'nombre':model_acta.estado.nombre,
					'icono':model_acta.estado.icono,
					'color':model_acta.estado.color
					}
				}})

		except Exception as e:			
			functions.toLog(e,'Acta_reunion.obtener_porcentaje')
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
		    'data':''},status=status.HTTP_400_BAD_REQUEST)

@transaction.atomic
def guardar_cumplimiento(request):
	sid = transaction.savepoint()
	try:		
		soporte=None		
		compromiso_id= request.POST['id'] if request.POST['id'] else None
		motivo = request.POST['motivo'] if request.POST['motivo'] else None
		requiere_soporte = request.POST['requiere_soporte'] if request.POST['requiere_soporte'] else None

		if str(requiere_soporte)=='true':
			soporte= request.FILES['soporte'] if request.FILES['soporte'] else None

		if compromiso_id:
			model_compromiso = Compromiso.objects.get(pk=int(compromiso_id))

			if str(requiere_soporte)=='true' and soporte:
				model_compromiso.soporte=soporte

			if model_compromiso.fecha_compromiso>=date.today() and model_compromiso.estado.id!=estadoC.vencido:
				model_compromiso.estado_id = estadoC.cumplido
			elif model_compromiso.fecha_compromiso<date.today() and model_compromiso.estado.id==estadoC.vencido:
				model_compromiso.estado_id = estadoC.cumplido_despues_vencido
		

			model_compromiso.save()

			logs_model=Logs(usuario_id=request.user.usuario.id
								,accion=Acciones.accion_actualizar
								,nombre_modelo='actareunion.Compromiso(cumplimiento)'
								,id_manipulado=model_compromiso.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			

			if model_compromiso.responsable_interno==True:
				model_participante_interno=Participante_interno.objects.filter(acta__id=model_compromiso.acta.id,usuario__id=model_compromiso.usuario_responsable.id)
				model_historial = Compromiso_historial(
					compromiso_id=int(model_compromiso.id),
					fecha=date.today(),
					tipo_operacion_id=int(tipoCH.cumplimiento),
					motivo=motivo,
					participante_interno_id=int(model_participante_interno[0].id))
				model_historial.save()			
			else:
				model_historial = Compromiso_historial(
					compromiso_id=int(model_compromiso.id),
					fecha=date.today(),
					tipo_operacion_id=int(tipoCH.cumplimiento),
					motivo=motivo,
					participante_externo_id=int(model_compromiso.participante_responsable_id))
				model_historial.save()

				

			logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Compromiso_historial',id_manipulado=model_historial.id)
			logs_model_con.save()

			transaction.savepoint_commit(sid)

			#import pdb; pdb.set_trace()
			model_acta = Acta.objects.get(pk=model_compromiso.acta.id)
			if Compromiso.objects.filter(acta__id=model_compromiso.acta.id).exists():
				if Compromiso.objects.filter(acta__id=model_compromiso.acta.id).count()==Compromiso.objects.filter(acta__id=model_compromiso.acta.id,estado__id__in=[estadoC.cumplido,estadoC.cumplido_despues_vencido]).count():
					model_acta.estado_id = estadoA.cerrada
					model_acta.save()

					logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Acta',id_manipulado=model_acta.id)
					logs_model_con.save()

					model_acta_historial = Acta_historial(
						acta_id=int(model_acta.id),
						fecha=date.today(),
						tipo_operacion_id=int(tipoAH.cerrar),
						motivo='Todos los compromisos han sido cumplidos',
						controlador_id=int(model_acta.controlador_actual.id))
					model_acta_historial.save()

					logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Acta_historial',id_manipulado=model_acta_historial.id)
					logs_model_con.save()


					transaction.savepoint_commit(sid)
			return JsonResponse({'message':'Se subió le cumplimiento del compromiso correctamente','success':'ok',
				'data':{				
				'estado':{
					'id':model_acta.estado.id,
					'nombre':model_acta.estado.nombre,
					'icono':model_acta.estado.icono,
					'color':model_acta.estado.color
					}
				}})
		else:
			return JsonResponse({'message':'No se recibió el compromiso','success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)

	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})

@login_required
def ver_soporte_compromiso (request):
	if request.method == 'GET':
		try:			
			archivo = Compromiso.objects.get(pk=request.GET['id'])			
			return functions.exportarArchivoS3(str(archivo.soporte))

		except Exception as e:
			functions.toLog(e,'contrato.VerSoporte')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			


@login_required
def cancelar_compromiso(request):
	#import pdb; pdb.set_trace()
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)

			model_compromiso = Compromiso.objects.get(pk=int(respuesta['compromiso_id']))
			model_compromiso.estado_id=estadoC.cancelado			
			model_compromiso.save()

			logs_model=Logs(usuario_id=request.user.usuario.id
									,accion=Acciones.accion_actualizar
									,nombre_modelo='actareunion.Compromiso'
									,id_manipulado=model_compromiso.id)
			logs_model.save()

			transaction.savepoint_commit(sid)

			if model_compromiso.responsable_interno==True:
				model_participante_interno=Participante_interno.objects.filter(acta__id=model_compromiso.acta.id,usuario__id=model_compromiso.usuario_responsable.id)
				model_historial = Compromiso_historial(
					compromiso_id=int(model_compromiso.id),
					fecha=date.today(),
					tipo_operacion_id=int(tipoCH.cancelacion),
					motivo=respuesta['motivo'],
					participante_interno_id=int(model_participante_interno[0].id))
				model_historial.save()			
			else:
				model_historial = Compromiso_historial(
					compromiso_id=int(model_compromiso.id),
					fecha=date.today(),
					tipo_operacion_id=int(tipoCH.cancelacion),
					motivo=respuesta['motivo'],
					participante_externo_id=int(model_compromiso.participante_responsable_id))
				model_historial.save()

				

			logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Compromiso_historial',id_manipulado=model_historial.id)
			logs_model_con.save()

			transaction.savepoint_commit(sid)

			
			return JsonResponse({'message':'El compromiso se ha cancelado correctamente','success':'ok',
						'data':''})

		except Exception as e:
			functions.toLog(e,'acta_reunion.Compromiso(cancelar)')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})



@login_required
def restablecer_compromiso(request):
	#import pdb; pdb.set_trace()
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)

			compromiso = Compromiso.objects.get(pk=int(respuesta['compromiso_id']))
			ultimo_historial_compromiso = Compromiso_historial.objects.filter(compromiso__id=compromiso.id,tipo_operacion__id__in=[tipoCH.creacion,tipoCH.proroga,tipoCH.cumplimiento]).order_by('id').last()
			if int(ultimo_historial_compromiso.tipo_operacion_id) in [tipoCH.creacion,tipoCH.proroga]:
				

				diferencias = datetime.strptime(str(compromiso.fecha_compromiso), '%Y-%m-%d').date() - date.today()
				diferencias_proximidad = datetime.strptime(str(compromiso.fecha_compromiso), '%Y-%m-%d').date() - datetime.strptime(str(compromiso.fecha_proximidad), '%Y-%m-%d').date()

				if diferencias.days <= 0:
					compromiso.estado_id = estadoC.vencido

				if diferencias.days > 0 and diferencias.days <= diferencias_proximidad.days:
					compromiso.estado_id = estadoC.por_vencer

				if diferencias.days > diferencias_proximidad.days:
					compromiso.estado_id = estadoC.por_cumplir

				compromiso.save()							

			elif int(ultimo_historial_compromiso.tipo_operacion_id)==tipoCH.cumplimiento:
	
				if compromiso.fecha_compromiso>=ultimo_historial_compromiso.fecha:
					compromiso.estado_id=estadoC.cumplido
				else:
					compromiso.estado_id=estadoC.cumplido_despues_vencido

				compromiso.save()

			logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Compromiso',id_manipulado=compromiso.id)
			logs_model_con.save()


			if compromiso.responsable_interno==True:
				model_participante_interno=Participante_interno.objects.filter(acta__id=compromiso.acta.id,usuario__id=compromiso.usuario_responsable.id)
				model_historial = Compromiso_historial(
					compromiso_id=int(compromiso.id),
					fecha=date.today(),
					tipo_operacion_id=int(tipoCH.restablecer),
					motivo='El compromiso cancelado se ha restablecido',
					participante_interno_id=int(model_participante_interno[0].id))
				model_historial.save()			
			else:
				model_historial = Compromiso_historial(
					compromiso_id=int(compromiso.id),
					fecha=date.today(),
					tipo_operacion_id=int(tipoCH.restablecer),
					motivo='El compromiso cancelado se ha restablecido',
					participante_externo_id=int(compromiso.participante_responsable_id))
				model_historial.save()
				

			logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Compromiso_historial',id_manipulado=model_historial.id)
			logs_model_con.save()

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El compromiso se ha restablecido correctamente','success':'ok',
						'data':''})

		except Exception as e:
			functions.toLog(e,'acta_reunion.Compromiso(restablecer)')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})

@login_required
def prorrogar_compromiso(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			#lista=request.POST['_content']
			#import pdb; pdb.set_trace()
			respuesta= request.POST

			compromiso = Compromiso.objects.get(pk=int(respuesta['id']))
			compromiso.fecha_compromiso = respuesta['fecha']
			compromiso.fecha_proximidad = respuesta['fecha_proximidad']
			

			diferencias = datetime.strptime(str(compromiso.fecha_compromiso), '%Y-%m-%d').date() - date.today()
			diferencias_proximidad = datetime.strptime(str(compromiso.fecha_compromiso), '%Y-%m-%d').date() - datetime.strptime(str(compromiso.fecha_proximidad), '%Y-%m-%d').date()

			if diferencias.days <= 0:
				compromiso.estado_id = estadoC.vencido

			if diferencias.days > 0 and diferencias.days <= diferencias_proximidad.days:
				compromiso.estado_id = estadoC.por_vencer

			if diferencias.days > diferencias_proximidad.days:
				compromiso.estado_id = estadoC.por_cumplir

			compromiso.save()

			logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Compromiso',id_manipulado=compromiso.id)
			logs_model_con.save()


			if compromiso.responsable_interno==True:
				model_participante_interno=Participante_interno.objects.filter(acta__id=compromiso.acta.id,usuario__id=compromiso.usuario_responsable.id)
				model_historial = Compromiso_historial(
					compromiso_id=int(compromiso.id),
					fecha=respuesta['fecha'],
					tipo_operacion_id=int(tipoCH.proroga),
					motivo=respuesta['motivo'],
					participante_interno_id=int(model_participante_interno[0].id))
				model_historial.save()			
			else:
				model_historial = Compromiso_historial(
					compromiso_id=int(compromiso.id),
					fecha=respuesta['fecha'],
					tipo_operacion_id=int(tipoCH.proroga),
					motivo=respuesta['motivo'],
					participante_externo_id=int(compromiso.participante_responsable_id))
				model_historial.save()
				

			logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Compromiso_historial',id_manipulado=model_historial.id)
			logs_model_con.save()


			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El compromiso se ha actualizado correctamente','success':'ok',
						'data':''})
		except Exception as e:
			functions.toLog(e,'acta_reunion.Compromiso(prorrogar)')
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
				'data':''})

@login_required
def reasignar_compromiso(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			#lista=request.POST['_content']
			#import pdb; pdb.set_trace()
			respuesta= request.POST

			compromiso = Compromiso.objects.get(pk=int(respuesta['id']))


			if str(respuesta['responsable_interno'])=='true':
				compromiso.responsable_interno = True

				compromiso.participante_responsable_id = None
				compromiso.usuario_responsable_id= respuesta['responsable_id']

			elif str(respuesta['responsable_interno']) =='false':
				compromiso.responsable_interno = False

				compromiso.participante_responsable_id = respuesta['responsable_id']
				compromiso.usuario_responsable_id= respuesta['supervisor_id']


			compromiso.save()

			logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='acta_reunion.Compromiso',id_manipulado=compromiso.id)
			logs_model_con.save()


			if compromiso.responsable_interno==True:
				model_participante_interno=Participante_interno.objects.filter(acta__id=compromiso.acta.id,usuario__id=compromiso.usuario_responsable.id)
				model_historial = Compromiso_historial(
					compromiso_id=int(compromiso.id),
					fecha=date.today(),
					tipo_operacion_id=int(tipoCH.resignacion),
					motivo=respuesta['motivo'],
					participante_interno_id=int(model_participante_interno[0].id))
				model_historial.save()			
			else:
				model_historial = Compromiso_historial(
					compromiso_id=int(compromiso.id),
					fecha=date.today(),
					tipo_operacion_id=int(tipoCH.resignacion),
					motivo=respuesta['motivo'],
					participante_externo_id=int(compromiso.participante_responsable_id))
				model_historial.save()
				

			logs_model_con=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='acta_reunion.Compromiso_historial',id_manipulado=model_historial.id)
			logs_model_con.save()


			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El compromiso se ha actualizado correctamente','success':'ok',
						'data':''})
		except Exception as e:
			functions.toLog(e,'acta_reunion.Compromiso(reasignar)')
			return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
				'data':''})


@api_view(['GET'])
def llenar_graficas_actas(request):
	#import pdb; pdb.set_trace()	
	if request.method == 'GET':
		try:				
			estados = [{'id':estadoA.anulada,'color':'#C70039'},
					{'id':estadoA.cerrada,'color':'#2ECC71'},
					{'id':estadoA.pausada,'color':'#CDCDCD'},
					{'id':estadoA.en_curso,'color':'#FFC300'}]
			datagrafica = []
			dataColores = []
			data = []
			actas_participantes = Participante_interno.objects.filter(usuario__id=request.user.usuario.id).values('acta__id')			
			#Actas por estado
			for e in estados:
				qsetActa = (Q(estado_id = int(e['id'])) & Q(id__in=actas_participantes))
				ActasPorEstado = Acta.objects.filter(qsetActa).values('estado__nombre').annotate(total=Count('estado__nombre'))
				if ActasPorEstado:
					datagrafica.append([ActasPorEstado[0]['estado__nombre'], ActasPorEstado[0]['total']])
					dataColores.append(e['color'])
			data.append(
				{
					'grafica' : 'Actas por estado',
					'datagrafica' : datagrafica,
					'datoColores' : dataColores
				})
			#Actas por estado

			#Compromisos por estado
			estados = [{'id':estadoC.por_cumplir,'color':'#CDCDCD'},
					{'id':estadoC.por_vencer,'color':'#FFC300'},
					{'id':estadoC.vencido,'color':'#C70039'},
					{'id':estadoC.cumplido,'color':'#2ECC71'},
					{'id':estadoC.cumplido_despues_vencido,'color':'#2874A6'},
					{'id':estadoC.cancelado,'color':'#9B59B6'}]
			datagrafica = []
			dataColores = []			
			for e in estados:
				qsetCompromiso = (Q(estado_id = int(e['id'])) & Q(acta_id__in=actas_participantes))
				CompromisosPorEstado = Compromiso.objects.filter(qsetCompromiso).values('estado__nombre').annotate(total=Count('estado__nombre'))
				if CompromisosPorEstado:
					datagrafica.append([CompromisosPorEstado[0]['estado__nombre'], CompromisosPorEstado[0]['total']])
					dataColores.append(e['color'])

			data.append(
				{
					'grafica' : 'Compromisos por estado',
					'datagrafica' : datagrafica,
					'datoColores' : dataColores
				})			
			#Compromisos por estado		

			#Mis Compromisos por estado
			estados = [{'id':estadoC.por_cumplir,'color':'#CDCDCD'},
					{'id':estadoC.por_vencer,'color':'#FFC300'},
					{'id':estadoC.vencido,'color':'#C70039'},
					{'id':estadoC.cumplido,'color':'#2ECC71'},
					{'id':estadoC.cumplido_despues_vencido,'color':'#2874A6'},
					{'id':estadoC.cancelado,'color':'#9B59B6'}]
			datagrafica = []
			dataColores = []			
			for e in estados:
				qsetCompromiso = (Q(estado_id = int(e['id'])))
				qsetCompromiso = qsetCompromiso & (Q(usuario_responsable_id = request.user.usuario.id) & Q(acta_id__in=actas_participantes))
				qsetCompromiso = qsetCompromiso & (Q(responsable_interno = 1))
				MisCompromisosPorEstado = Compromiso.objects.filter(qsetCompromiso).values('estado__nombre').annotate(total=Count('estado__nombre'))
				if MisCompromisosPorEstado:
					datagrafica.append([MisCompromisosPorEstado[0]['estado__nombre'], MisCompromisosPorEstado[0]['total']])
					dataColores.append(e['color'])

			data.append(
				{
					'grafica' : 'Mis Compromisos por estado',
					'datagrafica' : datagrafica,
					'datoColores' : dataColores
				})			
			#Mis Compromisos por estado			

			#Compromisos supervisados por estado
			estados = [{'id':estadoC.por_cumplir,'color':'#CDCDCD'},
					{'id':estadoC.por_vencer,'color':'#FFC300'},
					{'id':estadoC.vencido,'color':'#C70039'},
					{'id':estadoC.cumplido,'color':'#2ECC71'},
					{'id':estadoC.cumplido_despues_vencido,'color':'#2874A6'},
					{'id':estadoC.cancelado,'color':'#9B59B6'}]
			datagrafica = []
			dataColores = []			
			for e in estados:
				qsetCompromiso = (Q(estado_id = int(e['id'])))
				qsetCompromiso = qsetCompromiso & (Q(supervisor_id = request.user.usuario.id) & Q(acta_id__in=actas_participantes))				
				CompromisosSupervisorPorEstado = Compromiso.objects.filter(qsetCompromiso).values('estado__nombre').annotate(total=Count('estado__nombre'))
				if CompromisosSupervisorPorEstado:
					datagrafica.append([CompromisosSupervisorPorEstado[0]['estado__nombre'], CompromisosSupervisorPorEstado[0]['total']])
					dataColores.append(e['color'])

			data.append(
				{
					'grafica' : 'Compromisos supervisados por estado',
					'datagrafica' : datagrafica,
					'datoColores' : dataColores
				})			
			#Compromisos supervisados por estado	


			return Response({'message':'','success':'ok','data':data})	

		except Exception as e:
			functions.toLog(e,'acta.LlenarGraficas')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)			
	


@login_required
def generar_codigo_qr(request):
	# import pdb; pdb.set_trace()					
	if request.method == 'GET':
		try:
			model = Acta.objects.get(pk=request.GET['acta_id'])
			response = HttpResponse(content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="CodigoQR_ActaNo'+str(model.consecutivo)+'.pdf"'

			c = canvas.Canvas(response)

			url = request.META["HTTP_HOST"] + '/actareunion/acta-examinar/' + str(request.GET['acta_id'])			

			qrw = qr.QrCodeWidget (url)
			b = qrw.getBounds ()
			w = b[2] - b[0]
			h = b[3] - b[1]


			d = Drawing(60, 60, transform=[60./w, 0, 0, 60./h, 0, 0])
			d.add(qrw)			
			c.drawImage(renderPDF.draw(d, c , 0, 0), 170, 690, 70, 60)	
								
			c.setPageSize((60, 60))			
			c.showPage()
			c.save()	

			return response			

		except Exception as e:
			functions.toLog(e,'activos.generar_qr_activo')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
