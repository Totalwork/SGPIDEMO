from django.shortcuts import render, render_to_response
from django.urls import reverse

from rest_framework import viewsets, serializers, response
from django.db.models import Q

from django.db import IntegrityError,transaction
from .models import Proyecto ,P_tipo , Proyecto_empresas , P_fondo , Proyecto_campo_info_tecnica , Proyecto_info_tecnica, Proyecto_actividad

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
from django.db import connection

from django.db.models import Count

from puntos_gps.models import PuntosGps
from contrato.models import Contrato,EmpresaContrato,VigenciaContrato
from contrato.views import ContratoSerializer, ContratoDescargoSerializer
from contrato.enumeration import tipoC
from tipo.models import Tipo
from tipo.views import TipoSerializer
from estado.models import Estado
from estado.views import EstadoSerializer
from parametrizacion.models import Banco , Municipio , Funcionario , Departamento
from parametrizacion.views import BancoSerializer , MunicipioSerializer , FuncionarioSerializer , DepartamentoSerializer, MunicipioLiteSerializer
from empresa.models import Empresa , EmpresaAcceso
from empresa.views import EmpresaSerializer
from giros.models import DEncabezadoGiro,DetalleGiro
from descargo.models import Descargo
from poliza.models import VigenciaPoliza
from administrador_fotos.models import CFotosProyecto
from servidumbre.models import Servidumbre_expediente

from avance_de_obra.models import BCronograma
from correspondencia.models import CorrespondenciaEnviada
from django.contrib.contenttypes.models import ContentType
from proceso.models import FProcesoRelacion,AProceso
from django.db.models import F, FloatField, Sum
from django.conf import settings
from django.contrib.auth.decorators import login_required

from logs.models import Logs,Acciones
# from datetime import *
from django.db import transaction,connection
from django.db.models.deletion import ProtectedError

from rest_framework.decorators import api_view
from .tasks import notificacionProyecto
import re
import threading

# DATOS QUE SE NECESITAN PARA EL REGISTRO O MODIFICACION DEL PROYECTO
# select necesarios para el  registro o modificacion del proyecto
@api_view(['GET'])
def select_create_update_proyecto(request):
	if request.method == 'GET':
		try:
			tipo_contrato = tipoC()

			proyecto = request.GET['proyecto_id'] if 'proyecto_id' in request.GET else 0;		
 
			qsetEstadoProyectos = Estado.objects.filter(app = "proyecto")
			estadosProyectosData = EstadoSerializer(qsetEstadoProyectos,many=True).data

			qsetTipoProyectos = P_tipo.objects.all()
			tiposProyectosData = P_tipoSerializer(qsetTipoProyectos,many=True).data

			qsetDepartamentos = Departamento.objects.all()
			departamentosData = DepartamentoSerializer(qsetDepartamentos,many=True).data

			qsetBancos = Banco.objects.all()
			bancosData = BancoSerializer(qsetBancos,many=True).data

			qsetTipoCuentas = Tipo.objects.filter(app = "cuenta")
			tipoCuentasData = TipoSerializer(qsetTipoCuentas,many=True).data


			if int(proyecto)>0:
				p = Proyecto.objects.get(pk=request.GET['proyecto_id'])
				queryset = Contrato.objects.filter(Q(id__in = contratoEmpresa)|Q(id = p.mcontrato.id)).values('id', 'nombre')

				qset = (Q(empresacontrato__participa = True))
				qset = qset & (Q(empresacontrato__empresa = request.user.usuario.empresa.id))
				qset = qset & (Q(tipo_contrato_id = tipo_contrato.m_contrato))

				qsetMcontratos = Contrato.objects.filter(qset).values('id', 'nombre').exclude(pk__in = [1840,1839,1838])
			else:
				qsetMcontratos = Contrato.objects.filter(empresacontrato__participa = True , empresacontrato__empresa = request.user.usuario.empresa.id , tipo_contrato_id = tipo_contrato.m_contrato).values('id', 'nombre').exclude(pk__in = [1840,1839,1838])
			
			return JsonResponse({'message':'','success':'ok','data':{
										  'mcontratos' : list(qsetMcontratos)
										, 'tipoProyectos' : tiposProyectosData
										, 'estadoProyectos' : estadosProyectosData
										, 'departamentos' : departamentosData
										, 'bancos' : bancosData
										, 'tipoCuentas' : tipoCuentasData
									 }})

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def select_filter_proyecto(request):
	if request.method == 'GET':
		try:
			tipo_contrato = tipoC()
			mcontrato = request.GET['mcontrato'] if 'mcontrato' in request.GET else 0;
			consulta_contratista = request.GET['consulta_contratista'] if 'consulta_contratista' in request.GET else 0;
			consulta_departamento = request.GET['consulta_departamento'] if 'consulta_departamento' in request.GET else 0;
			consulta_proveedores = request.GET['consulta_proveedores'] if 'consulta_proveedores' in request.GET else 0;

			excluir_contratista = request.GET['excluir_contratista'] if 'excluir_contratista' in request.GET else 0;

			qset = (Q(empresacontrato__participa = True))
			qset = qset & (Q(empresacontrato__empresa = request.user.usuario.empresa.id))
			qset = qset & (Q(tipo_contrato_id = tipo_contrato.contratoProyecto))

			if consulta_proveedores:

				# CONTRATISTAS DEL PROYECTO
				qsetEmpresas = Empresa.objects.filter(esProveedor = True)
				empresasData = EmpresaLiteSerializer(qsetEmpresas,many=True).data

				return JsonResponse({'message':'','success':'ok','data':{
											'proveedores' : empresasData
										 }})

			elif consulta_contratista:

				if mcontrato:
					qset = qset & (Q(mcontrato_id = mcontrato))
						
				contratistas = Contrato.objects.filter(qset).values_list('contratista_id').distinct()


				# CONTRATISTAS DEL PROYECTO
				qsetEmpresas = Empresa.objects.filter(id__in = contratistas , esContratista = True)
				empresasData = EmpresaLiteSerializer(qsetEmpresas,many=True).data

				return JsonResponse({'message':'','success':'ok','data':{
											'contratistas' : empresasData
										 }})

			else:				

				empresasData = []
				if excluir_contratista==0 :
					contratistas = Contrato.objects.filter(qset).values_list('contratista_id').distinct()

					# CONTRATISTAS DEL PROYECTO
					qsetEmpresas = Empresa.objects.filter(id__in = contratistas , esContratista = True)
					empresasData = EmpresaLiteSerializer(qsetEmpresas,many=True).data

				qsetMcontratos = Contrato.objects.filter(empresacontrato__participa = True , empresacontrato__empresa = request.user.usuario.empresa.id , tipo_contrato_id = tipo_contrato.m_contrato).values('id', 'nombre').distinct()

				departamentosData = []

				if int(consulta_departamento)==1:
					qsetDepartamentos = Departamento.objects.all()
					departamentosData = DepartamentoSerializer(qsetDepartamentos,many=True).data


				return JsonResponse({'message':'','success':'ok','data':{
											  'mcontratos' : list(qsetMcontratos)
											, 'contratistas' : empresasData
											, 'departamentos' : departamentosData
										 }})

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# SERIALIZER LITE
class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	class Meta:
		model = Empresa
		fields=('id' , 'nombre'	, 'nit')

class ContratoLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	tipo_contrato = TipoSerializer(read_only=True)
	contratista = EmpresaLiteSerializer(read_only=True)
	contratante = EmpresaLiteSerializer(read_only=True)

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='Contrato'))

	class Meta:
		model = Contrato
		fields=('id' , 'nombre'	, 'contratista' , 'contratante' , 'tipo_contrato' , 'numero', 'estado','estado_id','fecha_inicio','fecha_fin')

class ContratoSimpleSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Contrato
		fields = ('id','nombre');

class ContratoEmpresaIdLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	tipo_contrato = TipoSerializer(read_only=True)
	contratista = EmpresaLiteSerializer(read_only=True)
	#contratante = EmpresaLiteSerializer(read_only=True)

	class Meta:
		model = Contrato
		fields=('id' , 'nombre'	, 'contratista' , 'tipo_contrato' , 'numero')

class ContratoSuperLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	

	class Meta:
		model = Contrato
		fields=('id' , 'nombre'	)


#Api rest para Proyecto_fondo
class ProyectoFondoSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = P_fondo
		fields=('id' , 'nombre' , 'descripcion')

class ProyectoFondoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de fondos de proyectos ,
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los fondos.
	"""
	model=P_fondo
	queryset = model.objects.all()
	serializer_class = ProyectoFondoSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ProyectoFondoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)

			if (dato):
				if dato:
					qset = (
						Q(nombre__icontains=dato)
						)

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
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				serializer = ProyectoFondoSerializer(data=request.DATA,context={'request': request})
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
				serializer = ProyectoFondoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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
#Fin api rest para Proyecto_fondo

# Create your views here.
class P_tipoSerializer(serializers.HyperlinkedModelSerializer):
	fondo_proyecto = ProyectoFondoSerializer(read_only = True)
	fondo_proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=P_fondo.objects.all())
	class Meta:
		model = P_tipo
		fields=( 'id' , 'nombre' , 'fondo_proyecto' , 'fondo_proyecto_id' )

class P_tipoViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de tipos de proyectos
	"""
	model = P_tipo
	queryset = model.objects.all()
	serializer_class = P_tipoSerializer
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
			queryset = super(P_tipoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)

			if (dato):
				if dato:
					qset = (
						Q(nombre__icontains=dato)
						)

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
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			##print request.DATA
			try:
				serializer = P_tipoSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(fondo_proyecto_id = request.DATA['fondo_proyecto_id'])
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
					print(e)
					return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

# SERIALIZADORES
class ProyectoSerializer(serializers.HyperlinkedModelSerializer):
	mcontrato = ContratoSerializer(read_only = True , allow_null = True)
	mcontrato_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Contrato.objects.all() , allow_null = True)

	tipo_cuenta = TipoSerializer(read_only = True)
	tipo_cuenta_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Tipo.objects.filter(app="cuenta") , allow_null = True )

	estado_proyecto = EstadoSerializer(read_only = True)
	estado_proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Estado.objects.filter(app="proyecto"))

	tipo_proyecto = P_tipoSerializer(read_only = True)
	tipo_proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=P_tipo.objects.all())

	entidad_bancaria = BancoSerializer(read_only = True)
	entidad_bancaria_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Banco.objects.all()  , allow_null = True)

	municipio = MunicipioSerializer(read_only = True)
	municipio_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Municipio.objects.all())

	contrato = ContratoSerializer(read_only = True, many = True)

	funcionario = FuncionarioSerializer(read_only = True, many = True)

	totalCronograma=serializers.SerializerMethodField()
	soloLectura = serializers.SerializerMethodField()
	class Meta: 
		model = Proyecto
		fields=( 'id','nombre',
				 'mcontrato' , 'mcontrato_id' ,
				 'No_cuenta' ,
				 'tipo_cuenta' , 'tipo_cuenta_id' ,
				 'estado_proyecto' , 'estado_proyecto_id' ,
				 'valor_adjudicado' ,
				 'tipo_proyecto' , 'tipo_proyecto_id' ,
				 'fecha_inicio' , 'fecha_fin' ,
				 'entidad_bancaria' , 'entidad_bancaria_id' ,
				 'municipio'  , 'municipio_id','contrato','totalCronograma','funcionario', 'soloLectura')
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'municipio_id' , 'nombre' ),
				message=('El nombre del proyecto  no puede  estar repetido en el la misma ciudad.')
				)
				]

	def get_totalCronograma(self, obj):
		return BCronograma.objects.filter(proyecto_id=obj.id).count()

	def get_soloLectura(self, obj):
		request = self.context.get("request")
		if request is None:
			return False
		empresaContrato = EmpresaContrato.objects.filter(contrato__id=obj.mcontrato.id, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		return soloLectura	

	
class ProyectoLiteSerializer(serializers.HyperlinkedModelSerializer):
	mcontrato = ContratoLiteSerializer(read_only = True)
	estado_proyecto = EstadoSerializer(read_only = True)
	tipo_proyecto = P_tipoSerializer(read_only = True)
	municipio = MunicipioSerializer(read_only = True)

	contrato = ContratoLiteSerializer(read_only = True, many = True)
	funcionario = FuncionarioSerializer(read_only = True, many = True)
	totalCronograma=serializers.SerializerMethodField()

	tipo_cuenta = TipoSerializer(read_only = True)
	tipo_cuenta_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Tipo.objects.filter(app="cuenta") , allow_null = True )

	entidad_bancaria = BancoSerializer(read_only = True)
	entidad_bancaria_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Banco.objects.all()  , allow_null = True)
	soloLectura = serializers.SerializerMethodField()

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre',
				 'mcontrato' ,
				 'estado_proyecto' ,
				 'tipo_proyecto' ,
				 'municipio' ,'contrato','totalCronograma','funcionario',
				 'tipo_cuenta' , 'tipo_cuenta_id',
				 'entidad_bancaria' , 'entidad_bancaria_id', 'soloLectura'
				 )
	def get_totalCronograma(self, obj):
		return BCronograma.objects.filter(proyecto_id=obj.id).count()

	def get_soloLectura(self, obj):
		request = self.context.get("request")
		if request is None:
			return False
		empresaContrato = EmpresaContrato.objects.filter(contrato__id=obj.mcontrato.id, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		return soloLectura		

class ProyectoEmpresaIdLiteSerializer(serializers.HyperlinkedModelSerializer):
	#mcontrato = ContratoLiteSerializer(read_only = True)			
	contrato = ContratoEmpresaIdLiteSerializer(read_only = True, many = True)
	soloLectura = serializers.SerializerMethodField()

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre',				 				 				 
				 'contrato',				 
				 'soloLectura'
				 )
	def get_totalCronograma(self, obj):
		return BCronograma.objects.filter(proyecto_id=obj.id).count()

	def get_soloLectura(self, obj):
		request = self.context.get("request")
		if request is None:
			return False
		empresaContrato = EmpresaContrato.objects.filter(contrato__id=obj.mcontrato.id, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		return soloLectura

# se usa el serializador por ID de los proyectos
class ProyectoPorIdSerializer(serializers.HyperlinkedModelSerializer):

	entidad_bancaria = BancoSerializer(read_only = True)
	estado_proyecto = EstadoSerializer(read_only = True)
	mcontrato = ContratoSuperLiteSerializer(read_only = True)
	municipio = MunicipioSerializer(read_only = True)
	tipo_cuenta = TipoSerializer(read_only = True)	
	tipo_proyecto = P_tipoSerializer(read_only = True)
	soloLectura = serializers.SerializerMethodField()

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre', 'No_cuenta' , 'valor_adjudicado' , 'fecha_inicio' , 'fecha_fin' , 
			'entidad_bancaria', 'estado_proyecto' , 'mcontrato' , 'municipio' , 'tipo_cuenta' ,
			'tipo_proyecto', 'soloLectura')

	def get_soloLectura(self, obj):
		request = self.context.get("request")
		if request is None:
			return False
		empresaContrato = EmpresaContrato.objects.filter(contrato__id=obj.mcontrato.id, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		return soloLectura	


# se usa en el descarego
class ProyectoPorIdLiteSerializer(serializers.HyperlinkedModelSerializer):

	# entidad_bancaria = BancoSerializer(read_only = True)
	# estado_proyecto = EstadoSerializer(read_only = True)
	# mcontrato = ContratoSuperLiteSerializer(read_only = True)
	# municipio = MunicipioSerializer(read_only = True)
	# tipo_cuenta = TipoSerializer(read_only = True)	
	# tipo_proyecto = P_tipoSerializer(read_only = True)

	contrato = ContratoDescargoSerializer(read_only = True, many = True)

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre', 'contrato' )

#serializer lite de proyecto
class ProyectoLite2Serializer(serializers.HyperlinkedModelSerializer):
	mcontrato = ContratoSimpleSerializer(read_only = True)
	municipio = MunicipioSerializer(read_only = True)
	contrato = ContratoSimpleSerializer(read_only = True, many = True)
	conteo_puntos=serializers.SerializerMethodField()

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre',
				 'mcontrato' ,
				 'municipio' ,
				 'contrato',
				 'conteo_puntos'
				 )

	def get_conteo_puntos(self, obj):
		return PuntosGps.objects.filter(proyecto_id=obj.id).count()

class ProyectoLite3Serializer(serializers.HyperlinkedModelSerializer):
	
	municipio = MunicipioSerializer(read_only = True)	

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre','municipio' )


class ProyectoEmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):

	proyecto = ProyectoLiteSerializer(read_only = True )
	empresa = EmpresaLiteSerializer(read_only = True  )
	class Meta:
		model = Proyecto_empresas
		fields=('id' ,
				'proyecto',
 				'empresa',
 				'propietario',		 
				)
class ProyectoEmpresaLite2Serializer(serializers.HyperlinkedModelSerializer):

	proyecto = ProyectoLite2Serializer(read_only = True )
	empresa = EmpresaLiteSerializer(read_only = True  )
	class Meta:
		model = Proyecto_empresas
		fields=('id' ,
				'proyecto',
 				'empresa',
 				'propietario',		 
				)				
class ProyectoEmpresaPorIdLiteSerializer(serializers.HyperlinkedModelSerializer):

	proyecto = ProyectoEmpresaIdLiteSerializer(read_only = True )
	#empresa = EmpresaLiteSerializer(read_only = True  )
	class Meta:
		model = Proyecto_empresas
		fields=('id' ,
				'proyecto', 				
 				'propietario',		 
				)
class ProyectoSuperLiteSerializer(serializers.HyperlinkedModelSerializer):
	mcontrato = ContratoLiteSerializer(read_only = True)
	municipio = MunicipioSerializer(read_only = True)
	tipo_proyecto = P_tipoSerializer(read_only = True)
	soloLectura = serializers.SerializerMethodField()
	class Meta: 
		model = Proyecto
		fields=( 'id','nombre', 'tipo_proyecto' , 'mcontrato' , 'municipio' , 'soloLectura')

	def get_soloLectura(self, obj):
		request = self.context.get("request")
		if request is None:
			return False	
		empresaContrato = EmpresaContrato.objects.filter(contrato__id=obj.mcontrato.id, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		return soloLectura	

class ProyectoSuperLite2Serializer(serializers.HyperlinkedModelSerializer):
	municipio = MunicipioLiteSerializer(read_only = True)

	class Meta: 
		model = Proyecto
		fields=('id','nombre', 'municipio')

# SE USA ESTE SERIALIZADOR PARA CONSULTAR CONTRATISTAS DEL PROYECTO
# class ProyectoEmpresaContratistasLiteSerializer(serializers.HyperlinkedModelSerializer):

# 	proyecto = ProyectoSuperLiteSerializer(read_only = True )
# 	empresa = EmpresaLiteSerializer(read_only = True  )

# 	class Meta:
# 		model = Proyecto_empresas
# 		fields=('id' , 'proyecto', 'empresa', 'propietario')

# SE USA ESTE SERIALIZADOR PARA LA CONSULTA GENERAL DE PROYECTO
class ProyectoConsultaGeneralSerializer(serializers.HyperlinkedModelSerializer):
	mcontrato = ContratoSuperLiteSerializer(read_only = True)
	municipio = MunicipioSerializer(read_only = True)
	tipo_proyecto = P_tipoSerializer(read_only = True)
	soloLectura = serializers.SerializerMethodField()
	class Meta: 
		model = Proyecto
		fields=( 'id','nombre', 'tipo_proyecto' , 'mcontrato' , 'municipio', 'soloLectura')

	def get_soloLectura(self, obj):
		request = self.context.get("request")
		if request is None:
			return False	
		empresaContrato = EmpresaContrato.objects.filter(contrato__id=obj.mcontrato.id, empresa__id=request.user.usuario.empresa.id).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		return soloLectura		

class ProyectoEmpresaSuperLiteSerializer(serializers.HyperlinkedModelSerializer):

	# proyecto = ProyectoSuperLiteSerializer(read_only = True )
	proyecto = ProyectoConsultaGeneralSerializer(read_only = True )
	empresa = EmpresaLiteSerializer(read_only = True  )
	class Meta:
		model = Proyecto_empresas
		fields=('id' , 'proyecto', 'empresa', 'propietario',)

class ProyectoEmpresaSerializer(serializers.HyperlinkedModelSerializer):

	proyecto = ProyectoSerializer(read_only = True )
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto.objects.all())

	empresa = EmpresaLiteSerializer(read_only = True  )
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Empresa.objects.all())
	class Meta:
		model = Proyecto_empresas
		fields=('id' ,
				'proyecto','proyecto_id' ,
 				'empresa','empresa_id' ,
 				'propietario',		 
				)
	
class ProyectoEmpresaLiteNombreSerializer(serializers.HyperlinkedModelSerializer):

	proyecto = ProyectoSuperLite2Serializer(read_only = True )

	class Meta:
		model = Proyecto_empresas
		fields=('id' , 'proyecto')

def listEmpresasSinProyecto(request):
	if request.method == 'GET':
		try:
			empresaActual = request.user.usuario.empresa.id

			# empresas que puede ver la empresa actual
			empresas_puede_ver = EmpresaAcceso.objects.filter(empresa_id = empresaActual).values_list("empresa_ver_id")

			dato = request.GET['dato'] if 'dato' in request.GET else None;
			proyecto_id = request.GET['proyecto_id'] if 'proyecto_id' in request.GET else 0;

			qset=(~Q(id=0))

			if dato:
				qset = qset & (Q(nit__icontains = dato) | Q(nombre__icontains = dato))

			if empresas_puede_ver:
				qset = qset & (Q(pk__in = empresas_puede_ver))

			e = Empresa.objects.filter(fk_proyecto_empresa_empresa__proyecto = proyecto_id)

			queryset = Empresa.objects.filter(qset).values('id', 'nit', 'nombre').exclude(pk__in = e)
			return JsonResponse({'message':'','success':'ok','data':list(queryset)})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#funcion lista empresas que no estan asociadas al proyecto filtrado

def listEmpresasDelProyecto(request):
	if request.method == 'GET':
		try:
			# filtro por proyecto_id
			dato = request.GET['dato'] if 'dato' in request.GET else None;
			proyecto_id = request.GET['proyecto_id'] if 'proyecto_id' in request.GET else 0;
			propietario = request.GET['propietario'] if 'propietario' in request.GET else None;

			qset=(~Q(id=0))

			if propietario:
				qset = qset & (Q(propietario = propietario))

			if int(proyecto_id)>0:
				qset = qset & (Q(proyecto_id = proyecto_id))

			if dato:
				qset = qset & (Q(empresa__nombre__icontains = dato) | Q(empresa__nit__icontains = dato))

			queryset = Proyecto_empresas.objects.filter(qset).values('id' , 'empresa__id' , 'empresa__nit' , 'empresa__nombre')


			return JsonResponse({'message':'','success':'ok','data':list(queryset)})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#funcion lista empresas que pueden ver el proyecto 

#Api rest para Proyecto_empresa
@transaction.atomic
def createProyectoEmpresa(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			myList = request.POST['empresa_id'].split(',')
			proyecto_id = request.POST['proyecto_id']
			insert_list = []
			for item in myList:
				p = Proyecto_empresas(empresa_id = item 
										, proyecto_id = proyecto_id 
										, propietario = 0
										)
				p.save()

				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_crear
										,nombre_modelo='proyecto.Proyecto_empresas'
										,id_manipulado=p.id)
										)
			if insert_list:
				Logs.objects.bulk_create(insert_list)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})	
		except Exception as e:
			transaction.savepoint_rollback(sid)	
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def destroyProyectoEmpresa(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			content=request.POST['_content']
			respuesta= json.loads(content)
			proyecto_id = respuesta['proyecto_id']
			insert_list = []
			for item in respuesta['empresa_id']:
				proyectoEmpresa	= Proyecto_empresas.objects.get(id = item )
				proyectoEmpresa.delete()

				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_borrar
										,nombre_modelo='proyecto.Proyecto_empresas'
										,id_manipulado=item)
										)			

			if insert_list:
				Logs.objects.bulk_create(insert_list)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			print(e)
			transaction.savepoint_rollback(sid)	
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProyectoEmpresaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de proyectos relacionados a las empresas que tienen acceso,
	puede utilizar el parametro (empresa , propietario , proyecto) a traves del cual, se podra buscar por cada uno de estos filtros
	<br>empresa = [numero]
	<br>propietario = [booleano] (1 o 0) "Indica la empresa que registro el proyecto"
	<br>proyecto = [numero].
	"""
	model=Proyecto_empresas
	queryset = model.objects.all()
	serializer_class = ProyectoEmpresaSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ProyectoEmpresaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			proyecto_empresa_por_id = self.request.query_params.get('proyecto_empresa_por_id', None)			
			# si el parametro viene vacio consulta empresa 
			# si el parametro viene con un dato consulta las contratista del proyecto
			contratista_empresa = self.request.query_params.get('contratista_empresa', None)
			proyecto = self.request.query_params.get('proyecto', None)
			empresa = self.request.query_params.get('empresa', None)
			propietario = self.request.query_params.get('propietario', None)

			# proyecto
			mcontrato = self.request.query_params.get('mcontrato', None)
			departamento = self.request.query_params.get('departamento', None)
			municipio = self.request.query_params.get('municipio', None)
			estado_proyecto = self.request.query_params.get('estado_proyecto', None)
			tipo_proyecto= self.request.query_params.get('tipo_proyecto', None)

			#contratista
			contratista = self.request.query_params.get('contratista', None)
			#contrato
			contrato = self.request.query_params.get('contrato', None)
			tipo_contrato=self.request.query_params.get('tipo_contrato', None)

			# consulta solo nombre y id de del proyecto
			consulta_lite_id_nombre =self.request.query_params.get('consulta_lite_nombre', None)

			qset=(~Q(id=0))

			if(dato or proyecto or empresa or propietario or mcontrato or departamento or municipio or estado_proyecto or tipo_proyecto or tipo_contrato or contrato):

				if dato:
					qset = qset & ( Q(empresa__nombre__icontains = dato) |
								Q(empresa__nit__icontains = dato) |
								Q(proyecto__nombre__icontains = dato))					

				if proyecto and int(proyecto)>0:
					qset = qset & (Q(proyecto__id = proyecto))					

				if empresa and int(empresa)>0:
					qset = qset & (Q(empresa__id = empresa))					

				if propietario and int(propietario)>0:
					qset = qset & (Q(propietario = propietario))

				if mcontrato and int(mcontrato)>0:
					qset = qset & (Q(proyecto__mcontrato = mcontrato))
					
				if departamento and int(departamento)>0:
					qset = qset & (Q(proyecto__municipio__departamento__id = departamento))
					
				if municipio and int(municipio)>0:
					qset = qset & (Q(proyecto__municipio = municipio))
					
				if estado_proyecto and int(estado_proyecto)>0:
					qset = qset & (Q(proyecto__estado_proyecto = estado_proyecto))

				if tipo_proyecto and int(tipo_proyecto)>0:
					qset = qset & (Q(proyecto__tipo_proyecto = tipo_proyecto))

				if tipo_contrato and int(tipo_contrato)>0:
					qset = qset & (Q(proyecto__contrato__tipo_contrato__id = tipo_contrato))

				if contratista and int(contratista)>0:
					qset = qset & (Q(proyecto__contrato__contratista__id = contratista))	

				if propietario and proyecto and empresa:
					empresa = request.user.usuario.empresa.id
					qset = qset & ( Q(empresa__id = empresa))

				if contrato and int(contrato)>0:
					qset = qset & (Q(proyecto__contrato__id = contrato))


			if contratista_empresa:
				queryset = self.model.objects.filter(
					qset).order_by(
					'-id',
					'proyecto__mcontrato__nombre',
					'proyecto__municipio__departamento__nombre',
					'proyecto__municipio__nombre',
					'proyecto__nombre'
					).exclude(tipo_contratista__isnull=True)
			else:
				queryset = self.model.objects.filter(
					qset).order_by(
					'-id',
					'proyecto__mcontrato__nombre',
					'proyecto__municipio__departamento__nombre',
					'proyecto__municipio__nombre',
					'proyecto__nombre')


			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			serializer_context = {
				'request': request,
			}

			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					# serializer = self.get_serializer(page,many=True)
					

					# TRAER DATOS CON PARAMETROS DE REGISTRO
					parametro_registro = self.request.query_params.get('parametro_registro', None)
					parametro_consulta_general = self.request.query_params.get('parametro_consulta_general', None)
					parametro_consulta_giro = self.request.query_params.get('parametro_consulta_giro', None)
					# consulta la vista general
					if parametro_consulta_general:	

						serializer = ProyectoEmpresaSuperLiteSerializer(page,many=True,context=serializer_context)					

						qsetTipoContratos = Tipo.objects.filter(app = "contrato")
						tipoContratosData = TipoSerializer(qsetTipoContratos,many=True).data

						return self.get_paginated_response({'message':'','success':'ok'
							,'data':{'proyectos':serializer.data 						
									, 'tipoContratos' : tipoContratosData
									 }})
					#import pdb; pdb.set_trace()
					if parametro_consulta_giro:
						serializer = ProyectoEmpresaSuperLiteSerializer(page,many=True,context=serializer_context)
					else:
						if self.request.query_params.get('superLite', None):
							serializer = ProyectoEmpresaLite2Serializer(page,many=True,context=serializer_context)
						else:
							serializer = ProyectoEmpresaLiteSerializer(page,many=True,context=serializer_context)
					#import pdb; pdb.set_trace()
					if proyecto_empresa_por_id:
						serializer = ProyectoEmpresaPorIdLiteSerializer(page,many=True,context=serializer_context)					
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			# serializer = self.get_serializer(queryset,many=True)
			if consulta_lite_id_nombre:
				serializer = ProyectoEmpresaLiteNombreSerializer(queryset,many=True,context=serializer_context)			
			else:
				serializer = ProyectoEmpresaLiteSerializer(queryset,many=True,context=serializer_context)			

			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ProyectoEmpresaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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

#Fin api rest para Proyecto_empresa
# funciones de proyecto asociado a funcionario
@transaction.atomic
def createProyectoFuncionario(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			myList = request.POST['funcionario_id'].split(',')
			model = Proyecto.objects.get(pk=request.POST['proyecto_id'])
			model.funcionario.add(*myList)

			cc = model.funcionario.through.objects.filter(funcionario_id__in = myList)

			insert_list = []
			for i in cc:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_crear
										,nombre_modelo='proyecto.Proyecto.funcionario'
										,id_manipulado=i.id)
										)
		
			Logs.objects.bulk_create(insert_list)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
		except Exception as e:
			transaction.savepoint_rollback(sid)
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def destroyProyectoFuncionario(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['funcionario_id']
			model = Proyecto.objects.get(pk=respuesta['proyecto_id'])

			cc= model.funcionario.through.objects.filter(funcionario_id__in = myList)
			
			insert_list = []
			for i in cc:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_borrar
										,nombre_modelo='proyecto.Proyecto.funcionario'
										,id_manipulado=i.id)
										)
			
			model.funcionario.remove(*myList)
			Logs.objects.bulk_create(insert_list)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def listProyectoFuncionario(request):
	if request.method == 'GET':
		try:
			dato = request.GET['dato'] if 'dato' in request.GET else None;
			empresa_id = request.GET['empresa_id'] if 'empresa_id' in request.GET else None;
			cargo_id = request.GET['cargo_id'] if 'cargo_id' in request.GET else None;
			active = request.GET['active'] if 'active' in request.GET else None;
			p = Proyecto.objects.get(pk=request.GET['proyecto_id'])

			qset=(~Q(id=0))

			if dato or empresa_id or cargo_id or active:
				if dato:
					qset = qset & (Q(persona__nombres__icontains = dato) | Q(persona__apellidos__icontains = dato))

				if empresa_id:
					qset = qset & ( Q( empresa_id = empresa_id) )
					qset =  qset & ( Q( activo = 1) )

				if cargo_id:
					qset = qset & ( Q( cargo_id = cargo_id) )

				if active:
					qset = qset & ( Q( activo= active) )
				
			queryset = p.funcionario.filter(qset).values('id', 'cargo__nombre', 'persona__nombres' , 'persona__apellidos' , 'empresa__nombre','empresa__id','activo','persona__correo')

			return JsonResponse({'message':'','success':'ok','data':list(queryset)})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin de funciones de proyecto asocido a funcionario

def listFuncionariosSinProyecto(request):
	if request.method == 'GET':
		try:
			# filtro por proyecto_id
			dato = request.GET['dato'] if 'dato' in request.GET else None;
			empresa_id = request.GET['empresa_id'] if 'empresa_id' in request.GET else None;
			cargo_id = request.GET['cargo_id'] if 'cargo_id' in request.GET else None;
			active = request.GET['active'] if 'active' in request.GET else None;
			p = Proyecto.objects.get(pk=request.GET['proyecto_id'])
			qFuncionario = p.funcionario.all()

			qset=(~Q(id=0))
			if dato or empresa_id or cargo_id or active:
				if dato:
					qset =  qset & (Q(persona__nombres__icontains = dato) | Q(persona__apellidos__icontains = dato))
				if empresa_id:
					qset = qset & ( Q( empresa_id = empresa_id) )
					qset =  qset & ( Q( activo = 1) )

				if cargo_id:
					qset = qset & ( Q( cargo_id = cargo_id) )

				if active:
					qset = qset & ( Q( activo= active) )
		
			queryset = Funcionario.objects.filter(qset).values('id', 'empresa__nombre', 'cargo__nombre' , 'persona__nombres' , 'persona__apellidos' ).exclude(pk__in = qFuncionario)
			
			return JsonResponse({'message':'','success':'ok','data':list(queryset)})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#funcion lista funcionarios  que no estan asociadas al proyecto filtrado

# funciones de proyecto asociado a contratos
@transaction.atomic
def createProyectoContrato(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			myList = request.POST['contrato_id'].split(',')
			model = Proyecto.objects.get(pk=request.POST['proyecto_id'])
			model.contrato.add(*myList)

			cc = model.contrato.through.objects.filter(contrato_id__in = myList)

			insert_list = []
			for i in cc:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_crear
										,nombre_modelo='proyecto.Proyecto.contrato'
										,id_manipulado=i.id)
										)
		
			Logs.objects.bulk_create(insert_list)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
		except Exception as e:
			transaction.savepoint_rollback(sid)
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def destroyProyectoContrato(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['contrato_id']
			model = Proyecto.objects.get(pk=respuesta['proyecto_id'])
			cc= model.contrato.through.objects.filter(contrato_id__in = myList)
			
			insert_list = []
			for i in cc:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
										,accion=Acciones.accion_borrar
										,nombre_modelo='proyecto.Proyecto.contrato'
										,id_manipulado=i.id)
										)
			
			model.contrato.remove(*myList)
			Logs.objects.bulk_create(insert_list)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def listProyectoContrato(request):
	if request.method == 'GET':
		try:
			proyecto = request.GET['proyecto_id'] if 'proyecto_id' in request.GET else None;
			contrato = request.GET['contrato_id'] if 'contrato_id' in request.GET else None;
			tipoContrato = request.GET['tipoContrato'] if 'tipoContrato' in request.GET else None;
			dato = request.GET['dato'] if 'dato' in request.GET else None;

			if dato or proyecto or contrato or tipoContrato:
				if proyecto:
					model_proyecto = Proyecto.objects.get(pk=proyecto)

					if contrato is not None and int(contrato)>0 :
						queryset = model_proyecto.contrato.filter(id = contrato).values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero')
					else:
						queryset = model_proyecto.contrato.all().values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero')
				
					if tipoContrato:
						queryset  = queryset.filter(tipo_contrato_id = tipoContrato)

					if dato:
						queryset  = queryset.filter( Q(nombre__icontains = dato) | Q(numero__icontains = dato))

				elif contrato:
					#import pdb; pdb.set_trace()
					encabezado_id = request.GET['encabezado_id'] if 'encabezado_id' in request.GET else None;
					model_encabezado = DEncabezadoGiro.objects.get(pk=int(encabezado_id))
					id_mcontrato = model_encabezado.nombre.contrato.id

					queryset = Proyecto.objects.filter(mcontrato__id=id_mcontrato,contrato__id = contrato).values('id', 'nombre' , 'No_cuenta' , 'entidad_bancaria__nombre','entidad_bancaria__id','tipo_cuenta__id')

			return JsonResponse({'message':'','success':'ok','data':list(queryset)})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin de funciones de proyecto asocido a contratos

def listContratosSinProyecto(request):
	if request.method == 'GET':
		try:
			# filtro por proyecto_id
			dato = request.GET['dato'] if 'dato' in request.GET else None;
			p = Proyecto.objects.get(pk=request.GET['proyecto_id'])
			qContrato = p.contrato.all()
			qset =  (Q(numero__icontains = dato) | Q(nombre__icontains = dato))

			empresaId = request.user.usuario.empresa.id

			contratos = EmpresaContrato.objects.filter(empresa_id = empresaId).values('contrato__id')

			if request.GET['tipoContrato']:
				qset = qset & (Q(tipo_contrato = request.GET['tipoContrato'] ))
			queryset = Contrato.objects.filter(qset , id__in = contratos).values('id', 'nombre', 'numero' , 'tipo_contrato__nombre').exclude(pk__in = qContrato)

			return JsonResponse({'message':'','success':'ok','data':list(queryset)})
		except Exception as e:
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin de funciones de proyecto asocido a contratos

def listMacroContratosParaAsignarProyecto(request):
	if request.method == 'GET':
		try:
			proyecto = request.GET['proyecto_id']
			contratoEmpresa = EmpresaContrato.objects.filter(empresa_id = request.user.usuario.empresa.id , participa = 1 , contrato__tipo_contrato_id = 12).values('contrato_id')
			
			if int(proyecto)>0:
				p = Proyecto.objects.get(pk=request.GET['proyecto_id'])
				queryset = Contrato.objects.filter(Q(id__in = contratoEmpresa)|Q(id = p.mcontrato.id)).values('id', 'nombre')
			else:
				queryset = Contrato.objects.filter(Q(id__in = contratoEmpresa)).values('id', 'nombre')
			
			return JsonResponse({'message':'','success':'ok','data':list(queryset)})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#fin funcion lista todos los macros contratos

@transaction.atomic
def destroyProyecto(request):
	if request.method == 'POST':
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']
			
			try:
				sid = transaction.savepoint()
				for item in myList:
					Proyecto_empresas.objects.filter(proyecto_id = item ).delete()
					Proyecto.objects.get(pk = item ).delete()
				transaction.savepoint_commit(sid)
				return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
			except Exception as e:
				transaction.savepoint_rollback(sid)	
				return JsonResponse({'message':'Algunos de los proyectos seleccionados estan asociados a datos tecnicos. ','status':'error','data':''})							

		except Exception as e:
			
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProyectoServidumbreSerializer(serializers.HyperlinkedModelSerializer):
	mcontrato = serializers.SerializerMethodField()
	municipio = serializers.SerializerMethodField()
	departamento = serializers.SerializerMethodField()

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre', 'mcontrato' , 'municipio', 'departamento')

	def get_mcontrato(self, obj):
		return obj.mcontrato.nombre

	def get_municipio(self, obj):
		return obj.municipio.nombre

	def get_departamento(self, obj):
		return obj.municipio.departamento.nombre

# Create your views here.
class ProyectoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de proyectos , puede utilizar el parametro (dato) a traves del cual consulta por nombre de los proyectos.
		"""
	model=Proyecto
	queryset = model.objects.all()
	serializer_class = ProyectoSerializer
	parser_classes=(FormParser, MultiPartParser,)
	paginate_by = 10

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			
			descargo = self.request.query_params.get('descargo',None)
			lite_detalle = self.request.query_params.get('lite_detalle',None)
			
			if descargo:
				serializer = ProyectoPorIdLiteSerializer(instance, context={'request': request})
			elif lite_detalle:
				serializer = ProyectoServidumbreSerializer(instance, context={'request': request})
			else:
				serializer = ProyectoPorIdSerializer(instance, context={'request': request})

			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):

		try:
			queryset = super(ProyectoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			departamento_id = self.request.query_params.get('departamento_id').split(',') if self.request.query_params.get('departamento_id') else None
			contrato_id = self.request.query_params.get('contrato').split(',') if self.request.query_params.get('contrato') else None
			id_contratista = self.request.query_params.get('id_contratista').split(',') if self.request.query_params.get('id_contratista') else None
			municipio_id = self.request.query_params.get('municipio_id').split(',') if self.request.query_params.get('municipio_id') else None
			proyecto = self.request.query_params.get('proyecto', None)
			contrato_obra = self.request.query_params.get('contrato_obra',None)
			funcionario = self.request.query_params.get('funcionario',None)
			listadoasociado = self.request.query_params.get('listado').split(',') if self.request.query_params.get('listado') else None
			servidumbre = self.request.query_params.get('servidumbre',None)
			proyectos_post_eca = self.request.query_params.get('proyectos_post_eca',None)
			
			lite = self.request.query_params.get('lite', None)
			filtros = self.request.query_params.get('filtros',None)

			
			
			if filtros is None:
				if (dato or departamento_id or contrato_id or id_contratista or municipio_id or proyecto or contrato_obra or funcionario or proyectos_post_eca):
					qset=(~Q(id=0))

					if dato:
						qset = qset & (Q(nombre__icontains=dato))
		
					# if contrato_id and int(contrato_id)>0:
					if contrato_id:
						qset = qset &(Q(mcontrato__in=contrato_id))
					
					if id_contratista and len(id_contratista) == 1:
						id_contratista = id_contratista[0]

					if id_contratista and int(id_contratista)>0:
						qset = qset &( Q(contrato__contratista__id=id_contratista))

					if departamento_id and len(departamento_id) == 1:
						departamento_id = departamento_id[0]

					if departamento_id and int(departamento_id)>0:
						qset = qset &( Q(municipio__departamento__id=departamento_id))


					if municipio_id and len(municipio_id) == 1:
						# print "id_munni: "+str(municipio_id[0])
						municipio_id = municipio_id[0]

					if municipio_id and  int(municipio_id)>0:
						qset = qset &( Q(municipio__id=municipio_id) )

					if proyecto and int(proyecto)>0:
						qset = qset &( Q(id=proyecto) )

					if contrato_obra:
						qset = qset &( Q(contrato__id=contrato_obra) )

					if funcionario:
						qset = qset &(Q(funcionario__id=funcionario))	

					if proyectos_post_eca:
						ListProyectosValidos = Proyecto_empresas.objects.filter(empresa__id=request.user.usuario.empresa.id).values('proyecto__id').distinct()
						qset = qset & (Q(id__in=ListProyectosValidos))

					if servidumbre:
						proyectos_servidumbre= Servidumbre_expediente.objects.all().values('proyecto__id')
						qset = qset & (~Q(id__in=proyectos_servidumbre))

					if listadoasociado:
						queryset = self.model.objects.filter(qset).exclude(pk__in = listadoasociado)

					else:
						queryset = self.model.objects.filter(qset)
				
				#utilizar la variable ignorePagination para quitar la paginacion
				ignorePagination= self.request.query_params.get('ignorePagination',None)
				if ignorePagination is  None:
					page = self.paginate_queryset(queryset)

					if page is not None:

						if lite is not None:
							if lite == '2':
								serializer = ProyectoSuperLite2Serializer(page,many=True, context={'request': request})
							elif servidumbre:
								serializer = ProyectoServidumbreSerializer(page,many=True, context={'request': request})
							else:
								serializer = ProyectoSuperLiteSerializer(page,many=True, context={'request': request})
						else:
							serializer = self.get_serializer(page,many=True)

						# serializer = self.get_serializer(page,many=True)
						return self.get_paginated_response({'message':'','success':'ok',
						'data':serializer.data})
				else:
					if lite is not None:
						serializer = ProyectoSuperLite2Serializer(queryset,many=True, context={'request': request})
					else:
						serializer = self.get_serializer(queryset,many=True, context={'request': request})

			# contratista = ContratoSerializer(Contrato.objects.filter(qset),many=True,context=serializer_context)

			# return Response({'message':'','success':'ok','data':serializer.data,'contratista':contratista.data})
			if filtros:
				tipo_c=tipoC()
				proyectos=[]
				municipios=[]
				departamentos=[]
				contratistas=[]
				qProyecto=(~Q(id=0))
				qContratista=(Q(empresa__id=request.user.usuario.empresa.id)) & (
						Q(contrato__tipo_contrato_id=tipo_c.contratoProyecto)) & (
						Q(participa=1)) & (
						Q(contrato__activo=1))
				
				

				if contrato_id:
					qProyecto=qProyecto & (Q(mcontrato__in=contrato_id))


					qContratista=qContratista & (Q(contrato__mcontrato__in=contrato_id))
						
				# else:
				# 	# municipios = Municipio.objects.all().order_by('nombre').values('id','nombre')
				# 	print "algo"
				# 	contratistas = EmpresaContrato.objects.filter(
				# 		empresa__id=request.user.usuario.empresa.id).values(
				# 		'contrato__contratista__id','contrato__contratista__nombre')


				if id_contratista:
					qProyecto=qProyecto & (Q(contrato__contratista__id__in=id_contratista)) & (
						Q(contrato__tipo_contrato_id=tipo_c.contratoProyecto))


				if departamento_id:
					qProyecto = qProyecto & (Q(municipio__departamento__id__in=departamento_id))

				if municipio_id:
					qProyecto = qProyecto & (Q(municipio__id__in=municipio_id))

				
				proyectos=Proyecto.objects.filter(qProyecto).values('id','nombre').distinct()

				contratistas = EmpresaContrato.objects.filter(qContratista).values(
						'contrato__contratista__id','contrato__contratista__nombre').distinct()

				contratoobra = EmpresaContrato.objects.filter(qContratista).values(
						'contrato__id','contrato__nombre').distinct()				

				# departamentos=Proyecto.objects.filter(qProyecto).values('municipio__departamento__id','municipio__departamento__nombre').distinct()
				departamentos=Proyecto.objects.filter(qProyecto).values('municipio__departamento__id',
																		'municipio__departamento__nombre').distinct()
				municipios=Proyecto.objects.filter(qProyecto).values('municipio__id','municipio__nombre').distinct()

				# departamentos = departamentos.order_by('municipio__departamento__id').distinct('municipio__departamento__id')
				departamentos2 = []
				for i in departamentos:
					if i not in departamentos2:
						departamentos2.append(i)
				municipios2 = []
				for i in municipios:
					if i not in municipios2:
						municipios2.append(i)

				return Response({'count':'','results':{'message':'','success':'ok','data':{
					'proyectos':proyectos,'municipios':municipios2,
					'departamentos':departamentos2,'contratistas':contratistas,'contratosobra':contratoobra}}})
			else:
				return Response({'message':'','success':'ok','data':serializer.data})
			
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ProyectoSerializer(data=request.DATA,context={'request': request})

				request.DATA['mcontrato_id'] = request.DATA['mcontrato_id'] if 'mcontrato_id' in request.DATA else '';

				if serializer.is_valid():
					if request.DATA['entidad_bancaria_id']=='':
						entidadBancaria = None
					else:
						entidadBancaria = request.DATA['entidad_bancaria_id']

					if 	request.DATA['tipo_cuenta_id']=='':
						tipoCuenta = None
					else:
						tipoCuenta = request.DATA['tipo_cuenta_id']

					# MACRO CONTRATO NO ASIGNADO 53
					request.DATA['mcontrato_id'] = 53 if request.DATA['mcontrato_id']=='' else request.DATA['mcontrato_id']
					# validar para no repetir numeros de cuenta en los proyectos

					validaNoCuenta = 1
					if request.DATA['No_cuenta']:
						proyectos	= Proyecto.objects.filter(No_cuenta__exact = request.DATA['No_cuenta'])
						if proyectos:
							validaNoCuenta = 0

					if validaNoCuenta == 1: 

						serializer.save(mcontrato_id = request.DATA['mcontrato_id'] ,
										municipio_id = request.DATA['municipio_id'] ,
										entidad_bancaria_id = entidadBancaria ,
										tipo_proyecto_id = request.DATA['tipo_proyecto_id'] ,
										tipo_cuenta_id = tipoCuenta ,
										estado_proyecto_id = request.DATA['estado_proyecto_id']
										)
						sendEmail = threading.Thread(target=notificacionProyecto, args=(serializer.data,request.user.usuario,))
						sendEmail.start()
						# new create proyecto_empresa 
						p = Proyecto_empresas(empresa_id = request.user.usuario.empresa.id 
												, proyecto_id = serializer.data["id"] 
												, propietario = 1
												)
						p.save()
						transaction.savepoint_commit(sid)	
						return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)
					else:
						return Response({'message':'El numero de cuenta digitado existe en el proyecto : '+str(proyectos),'success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
				else:	
					print(serializer.errors)				
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
				'data':''},status=status.HTTP_400_BAD_REQUEST)


	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				request.DATA['mcontrato_id'] = request.DATA['mcontrato_id'] if 'mcontrato_id' in request.DATA else '';
				request.DATA['mcontrato_id'] = 53 if request.DATA['mcontrato_id']=='' else request.DATA['mcontrato_id']

				serializer = ProyectoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():

					if request.DATA['entidad_bancaria_id']=='':
						entidadBancaria = None
					else:
						entidadBancaria = request.DATA['entidad_bancaria_id']

					if 	request.DATA['tipo_cuenta_id']=='':
						tipoCuenta = None
					else:
						tipoCuenta = request.DATA['tipo_cuenta_id']

					# validar para no repetir numeros de cuenta en los proyectos
					validaNoCuuenta = 1
					if request.DATA['No_cuenta']:						
						proyectos	= Proyecto.objects.filter(No_cuenta__exact = request.DATA['No_cuenta']).exclude(id = request.DATA['id'] )

						if proyectos:
							validaNoCuuenta = 0

					if validaNoCuuenta == 1: 

						serializer.save(mcontrato_id = request.DATA['mcontrato_id'] ,
										municipio_id = request.DATA['municipio_id'] ,
										entidad_bancaria_id = entidadBancaria ,
										tipo_proyecto_id = request.DATA['tipo_proyecto_id'] ,
										tipo_cuenta_id = tipoCuenta ,
										estado_proyecto_id = request.DATA['estado_proyecto_id']
										)
						return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)
					else:
						return Response({'message':'El numero de cuenta digitado existe en el proyecto : '+str(proyectos[0].nombre),'success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
			 		'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
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

#Api rest para Proyecto_campo_info_tecnica
class ProyectoCampoInfoTecnicaSerializer(serializers.HyperlinkedModelSerializer):

	tipo_proyecto = P_tipoSerializer(read_only = True, required = False)
	tipo_proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=P_tipo.objects.all())

	class Meta:
		model = Proyecto_campo_info_tecnica
		fields = ('id' , 'nombre' , 'unidad_medida' , 'tipo_proyecto' , 'tipo_proyecto_id' )

def createProyectoCampoInfoTecnica(request):
	if request.method == 'POST':
		try:
			p = Proyecto_campo_info_tecnica(contratista_id = request.POST['contratista_id'] , proyecto_id = request.POST['proyecto_id'] , tipo_contratista_id = request.POST['tipo_contratista_id'])
			p.save()
			transaction.commit()
			return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProyectoCampoInfoTecnicaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de proyectos relacionados a las empresas que tienen acceso,
	puede utilizar el parametro (empresa , grupo_empresa , proyecto) a traves del cual, se podra buscar por cada uno de estos filtros.
	"""
	model = Proyecto_campo_info_tecnica
	queryset = model.objects.all()
	serializer_class = ProyectoCampoInfoTecnicaSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ProyectoCampoInfoTecnicaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			tipo_proyecto = self.request.query_params.get('tipo_proyecto', None)

			if(dato or tipo_proyecto):
				if dato:
					qset = (Q(nombre__icontains = dato) )
					if tipo_proyecto:
						qset = qset & (Q(tipo_proyecto = tipo_proyecto))
					
				elif tipo_proyecto:
					qset = ( Q(tipo_proyecto = tipo_proyecto))
				queryset = self.model.objects.filter(qset)
			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			serializer = self.get_serializer(queryset,many=True)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ProyectoCampoInfoTecnicaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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
#Fin api rest para Proyecto_campo_info_tecnica


#Api rest para Proyecto_info_tecnica
class ProyectoInfoTecnicaSerializer(serializers.HyperlinkedModelSerializer):

	campo = ProyectoCampoInfoTecnicaSerializer(read_only = True)
	campo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto_campo_info_tecnica.objects.all())

	proyecto = ProyectoLiteSerializer(read_only = True)
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto.objects.all())

	class Meta:
		model = Proyecto_info_tecnica
		fields = ('id' ,
				'valor_diseno' , 'valor_replanteo' , 'valor_ejecucion' ,
				'campo' , 'campo_id' ,
				'proyecto' , 'proyecto_id'
				)
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'proyecto_id' , 'campo_id' ),
				message=('Existe un registro con el campo seleccionado.')
				)
				]

# solo consultas
class ProyectoInfoTecnicaSuperLiteSerializer(serializers.HyperlinkedModelSerializer):

	campo = ProyectoCampoInfoTecnicaSerializer(read_only = True)

	class Meta:
		model = Proyecto_info_tecnica
		fields=('id' ,
				'valor_diseno' , 'valor_replanteo' , 'valor_ejecucion' ,
				'campo' 	 
				)

def destroyProyectoInfoTecnica(request):
	if request.method == 'POST':
			try:
				lista=request.POST['_content']
				respuesta= json.loads(lista)
				Proyecto_info_tecnica.objects.filter(id = respuesta['id'] ).delete()
				transaction.commit()
				return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
			except Exception as e:
					return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProyectoInfoTecnicaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de informacion tecnica del proyectos ,
	puede utilizar el parametro (campo , proyecto) a traves del cual, se podra buscar por cada uno de estos filtros
	<br>campo = [numero] <br>
	proyecto = [numero].
	"""
	model = Proyecto_info_tecnica
	queryset = model.objects.all()
	serializer_class = ProyectoInfoTecnicaSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ProyectoInfoTecnicaViewSet, self).get_queryset()
			campo = self.request.query_params.get('campo', None)
			proyecto = self.request.query_params.get('proyecto', None)

			# serializador
			serializer_super_lite = self.request.query_params.get('serializer_super_lite', None)

			if(campo or proyecto):
				if campo:
					qset = (
						Q(campo_id = campo)
						)
				if proyecto:
					qset = (
						Q(proyecto_id = proyecto)
						)
				queryset = self.model.objects.filter(qset)

			serializer_context = { 'request': request, }

			#utilizar la variable ignorePagination para quitar la paginacion
			ignorePagination= self.request.query_params.get('ignorePagination',None)
			if ignorePagination is None:
				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			if serializer_super_lite:

				serializer = ProyectoInfoTecnicaSuperLiteSerializer(queryset,many=True,context=serializer_context)

			else:
				serializer = self.get_serializer(queryset,many=True)
			
			return Response({'message':'','success':'ok','data':serializer.data})
		
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ProyectoInfoTecnicaSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():					

					serializer.save(campo_id = request.DATA['campo_id'] ,
									proyecto_id = request.DATA['proyecto_id'] 
									)
					# SE REGISTRA EL LOG 
					logs_model=Logs(usuario_id=request.user.usuario.id
									,accion=Acciones.accion_crear
									,nombre_modelo='proyecto.Proyecto_info_tecnica'
									,id_manipulado=serializer.data['id'])
					logs_model.save()
						
					transaction.savepoint_commit(sid)	
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)

				else:	
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "valor_diseno" in serializer.errors:
						mensaje = serializer.errors["valor_diseno"][0] +" En el campo valor diseno"
					elif "valor_ejecucion" in serializer.errors:
						mensaje = serializer.errors["valor_ejecucion"][0] +" En el campo valor ejecucion"
					elif "valor_replanteo" in serializer.errors:
						mensaje = serializer.errors["valor_replanteo"][0] +" En el campo valor replanteo"
					else:
						mensaje = 'datos requeridos no fueron recibidos'

					return Response({'message':mensaje ,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
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
				serializer = ProyectoInfoTecnicaSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				if serializer.is_valid():

					serializer.save(campo_id = request.DATA['campo_id'] ,
									proyecto_id = request.DATA['proyecto_id'] 
									)
					# SE REGISTRA EL LOG 
					logs_model=Logs(usuario_id=request.user.usuario.id
									,accion=Acciones.accion_actualizar
									,nombre_modelo='proyecto.Proyecto_info_tecnica'
									,id_manipulado=serializer.data['id'])
					logs_model.save()
						
					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)

				else:

					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "valor_diseno" in serializer.errors:
						mensaje = serializer.errors["valor_diseno"][0] +" En el campo valor diseno"
					elif "valor_ejecucion" in serializer.errors:
						mensaje = serializer.errors["valor_ejecucion"][0] +" En el campo valor ejecucion"
					elif "valor_replanteo" in serializer.errors:
						mensaje = serializer.errors["valor_replanteo"][0] +" En el campo valor replanteo"
					else:
						mensaje = 'datos requeridos no fueron recibidos'
					print (mensaje)
					return Response({'message': mensaje ,'success':'fail', 'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
#Fin api rest para Proyecto_info_tecnica

#Api rest para Proyecto Actividades
class ProyectoActividadesLiteSerializer(serializers.HyperlinkedModelSerializer):

	municipio = MunicipioSerializer(read_only = True)

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre', 'municipio')

class ProyectoActividadesSerializer(serializers.HyperlinkedModelSerializer):

	proyecto = ProyectoActividadesLiteSerializer(read_only=True)
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Proyecto.objects.all())

	class Meta:
		model = Proyecto_actividad
		fields=('id','descripcion','proyecto','proyecto_id','fecha')

class ProyectoActividadesViewSet(viewsets.ModelViewSet):
	"""
	
	"""
	model=Proyecto_actividad
	queryset = model.objects.all()
	serializer_class = ProyectoActividadesSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ProyectoActividadesViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			descripcion = self.request.query_params.get('descripcion', None)
			nombre_proyecto = self.request.query_params.get('nombre_proyecto', None)
			id_proyecto = self.request.query_params.get('id_proyecto', None)
			fecha = self.request.query_params.get('fecha', None)
			sin_paginacion = self.request.query_params.get('sin_paginacion',None)

			# if con_funcionario is not None:
			# 	funcionario_model = Funcionario.objects.get(persona_id = request.user.usuario.persona.id)

			# if empresa_id:
			# 	id_empresa = request.user.usuario.empresa.id

			qset=(~Q(id=0))
			if dato:
				qset = qset &(Q(proyecto__nombre__icontains=dato)|Q(descripcion__icontains=dato))

			if descripcion:
				qset = qset &(Q(descripcion__icontains=descripcion))

			if nombre_proyecto:
				qset = qset &(Q(proyecto__nombre__icontains=nombre_proyecto))

			if id_proyecto:
				qset = qset &(Q(proyecto__id=id_proyecto))

			if qset is not None:
				queryset = self.model.objects.filter(qset).order_by('-fecha')

			if sin_paginacion is None:
				page = self.paginate_queryset(queryset)

				if page is not None:
					serializer = self.get_serializer(page,many=True)
					return self.get_paginated_response({'message':'','success':'ok','data':serializer.data})

			else:
				serializer = self.get_serializer(queryset,many=True)
				return Response({'message':'','success':'ok','data':serializer.data})
		
		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:
				serializer = ProyectoActividadesSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					serializer.save(proyecto_id=request.DATA['proyecto_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='proyecto.proyecto_actividades',id_manipulado=serializer.data['id'])
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = transaction.savepoint()
			try:
				# partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = ProyectoActividadesSerializer(instance,data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save(proyecto_id=request.DATA['proyecto_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='proyecto.proyecto_actividades',id_manipulado=instance.id)
					logs_model.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				transaction.savepoint_rollback(sid)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

	def destroy(self,request,*args,**kwargs):
		sid = transaction.savepoint()
		try:
			instance = self.get_object()
			# print instance.id
			self.model.objects.get(pk=instance.id).delete()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='proyecto.proyecto_actividades',id_manipulado=instance.id)
			logs_model.save()

			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_201_CREATED)
		except Exception as e:
			transaction.savepoint_rollback(sid)
			print(e)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)

@login_required
def proyectoActividades(request, id_proyecto=None):
	return render(request, 'proyecto/proyectoActividades.html',{'id_proyecto':id_proyecto,'model':'Proyecto_actividad','app':'proyecto'})

# Eliminar Actividades del proyecto
@transaction.atomic
def destroyProyectoActividadesConLista(request):
	if request.method == 'POST':
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myList = respuesta['lista']

			# model_funcionario = Funcionario.objects.get(pk=respuesta['id_funcionario'])

			actividades = Proyecto_actividad.objects.filter(id__in = myList)
			insert_list = []
			for i in actividades:
				insert_list.append(Logs(usuario_id=request.user.usuario.id
																,accion=Acciones.accion_borrar
																,nombre_modelo='proyecto.Proyecto_actividad'
																,id_manipulado=i.id))
			Logs.objects.bulk_create(insert_list)

			actividades.delete()

			# transaction.commit()
			return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Fin api rest para Proyecto Actividades

@login_required
def proyecto(request):
	return render(request, 'proyecto/proyecto.html',{'model':'proyecto','app':'proyecto'})
	
def filtrarProyecto(request):

	try:
		mcontrato = request.GET['mcontrato'] if 'mcontrato' in request.GET else None;
		contratista = request.GET['contratista'] if 'contratista' in request.GET else None;
		departamento = request.GET['departamento'] if 'departamento' in request.GET else None;
		municipio = request.GET['municipio'] if 'municipio' in request.GET else None;
		tipo = request.GET['tipo'].split(',') if 'tipo' in request.GET else None
		empresa_sin_logueo = request.GET['empresa_sin_logueo'] if 'empresa_sin_logueo' in request.GET else None;
		idcontrato = request.GET['idcontrato'] if 'idcontrato' in request.GET else None;
		tipo_contratista = request.GET['tipo_contratista'] if 'tipo_contratista' in request.GET else None;
		contratos_asociados = request.GET['contratos_asociados'] if 'contratos_asociados' in request.GET else None;

		if empresa_sin_logueo is not None:

			empresa = empresa_sin_logueo

		else:

			empresa = request.user.usuario.empresa.id

		listado_principal=[]
		ListMacrocontrato=[]
		Listcontrato=[]
		Listcontratista=[]
		Listdepartamento=[]
		Listmunicipio=[]
		qset1=''
		qset2=''
		qset3=''
		qset4=''

		if empresa is not None:
			qset1 = (Q(empresa_id=empresa))

		if tipo is not None and len(tipo)>0:
			qset1= qset1 & (
				Q(contrato__tipo_contrato__id__in=tipo)) & (Q(participa=1)
				)

		if mcontrato is not None and int(mcontrato)>0:
			qset3 =  qset1  & (Q(contrato__mcontrato_id=mcontrato))
			qset3= qset3 & (Q(contrato__contratista__esContratista=tipo_contratista))
			qset4 =  qset1  & (Q(contrato__mcontrato_id=mcontrato))
			qset2=(Q(mcontrato_id=mcontrato))

		else:

			if tipo_contratista is not None and len(tipo_contratista)>0:
				qset3= qset1 & (Q(contrato__contratista__esContratista=tipo_contratista))


			else:
				qset3 =  qset1

			if idcontrato is not None and int(idcontrato)>0:

				qset4 =  qset1  & (Q(contrato_id=idcontrato))

			else:

				qset4 =  qset1  & (Q(contrato__empresacontrato__empresa=empresa))

		if contratista is not None and int(contratista)>0:
			if qset4!='':
				qset4=qset4 & (Q(contrato__contratista__id=contratista))
			else:
				qset4=(Q(contrato__contratista__id=contratista))

			if qset2!='':
				qset2=qset2 & (Q(contrato__contratista__id=contratista))
			else:
				qset2=(Q(contrato__contratista__id=contratista))

		if departamento is not None and int(departamento)>0:
			if qset2!='':
				qset2=qset2 & (Q(municipio__departamento__id=departamento))
			else:
				qset2=(Q(municipio__departamento__id=departamento))
			

		ListMacrocontrato=EmpresaContrato.objects.filter(qset1).values('contrato__id','contrato__nombre').distinct().order_by('contrato__nombre')  if qset1!='' else []
		Listcontrato=EmpresaContrato.objects.filter(qset4).values('contrato__id','contrato__nombre','contrato__mcontrato__id').distinct().order_by('contrato__nombre')  if qset4!='' else []
		Listcontratista=EmpresaContrato.objects.filter(qset3).values('contrato__contratista__id','contrato__contratista__nombre').distinct().order_by('contrato__contratista__nombre') if qset3!='' else []
		Listdepartamento = Proyecto.objects.select_related('proyecto_contrato').filter(qset2).values('municipio__departamento_id','municipio__departamento__nombre').distinct().order_by('municipio__departamento__nombre')if qset2!='' else []
		Listmunicipio = Proyecto.objects.select_related('proyecto_contrato').filter(qset2).values('municipio__id','municipio__nombre').distinct().order_by('municipio__nombre') if qset2!='' else []

		Listcontrato_list = list(Listcontrato)

		#import pdb; pdb.set_trace()
		if contratos_asociados is not None and int(contratos_asociados)>0 and mcontrato is not None and int(mcontrato)>0:
			
			contratos = Proyecto.objects.filter(mcontrato__id=int(mcontrato), contrato__mcontrato__id=None).values('contrato__id','contrato__nombre','contrato__mcontrato__id').distinct().order_by('contrato__nombre')

			for contrato in contratos:
				Listcontrato_list.append(contrato);

		listado_principal.append({'macrocontrato':[{'id': p['contrato__id'], 'nombre': p['contrato__nombre']} for p in list(ListMacrocontrato)]
		,'contrato':[{'id': p['contrato__id'], 'nombre': p['contrato__nombre'], 'mcontrato_id': p['contrato__mcontrato__id']} for p in Listcontrato_list]
		,'contratista':[{'id': p['contrato__contratista__id'], 'nombre': p['contrato__contratista__nombre']} for p in list(Listcontratista)]
		,'departamento':[{'id': p['municipio__departamento_id'], 'nombre': p['municipio__departamento__nombre']} for p in list(Listdepartamento)] if qset2!='' else list(Departamento.objects.values('id','nombre'))
		,'municipio':[{'id': p['municipio__id'], 'nombre': p['municipio__nombre']} for p in list(Listmunicipio)]})

		return JsonResponse({'message':'','success':'ok','data':listado_principal[0]})

	except Exception as e:
		print(e)
		return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
				'data':''},status=status.HTTP_400_BAD_REQUEST)

# exporta a excel contrato
def exportReporteProyecto(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="Reporte_proyecto.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Proyectos')
	
	# FORMATO PARA ENCABEZADOS	
	format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
	# FORMATO PARA CAMPOS DE TIPOS TEXTO
	format2=workbook.add_format({'border':1})

	# FORMATO DE FECHA
	format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})

	# FORMATO MONEDA
	format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})


	row=1
	col=0

	dato = request.GET['dato'] if 'dato' in request.GET else None;
	mcontrato = request.GET['mcontrato'] if 'mcontrato' in request.GET else None;
	contratista = request.GET['contratista'] if 'contratista' in request.GET else None;

	empresaId = request.GET['empresa_id']

	qset = ( Q(empresa_id = empresaId) )

	if dato:
		qset = qset & ( Q(proyecto__nombre__icontains = dato) )

	if mcontrato:
		qset = qset &( Q(proyecto__mcontrato_id= mcontrato) )

	if contratista:
		qset = qset &( Q(proyecto__contrato_contratista_id = contratista) )


	model=Proyecto_empresas
	formato_fecha = "%Y-%m-%d"
	
	queryset = model.objects.filter(qset).order_by('-id')

	worksheet.set_column('A:D', 20)

	worksheet.write('A1', 'Mcontrato', format1)
	worksheet.write('B1', 'Departamento', format1)
	worksheet.write('C1', 'Municipio', format1)
	worksheet.write('D1', 'Proyecto - Servicio', format1)
	worksheet.write('E1', 'Valor Adjudicado', format1)
	worksheet.write('F1', 'Entidad Bancaria', format1)
	worksheet.write('G1', 'Tipo de Cuenta', format1)
	worksheet.write('H1', 'Numero de Cuenta', format1)

	worksheet.set_column('A:A', 40)
	worksheet.set_column('B:B', 30)
	worksheet.set_column('C:C', 25)
	worksheet.set_column('D:D', 60)
	worksheet.set_column('E:E', 18)
	worksheet.set_column('F:F', 18)
	worksheet.set_column('G:G', 18)
	worksheet.set_column('H:H', 18)

	for proyectoEmpresa in queryset:

		entidadBancaria = None	
		if proyectoEmpresa.proyecto.entidad_bancaria:
			entidadBancaria = proyectoEmpresa.proyecto.entidad_bancaria.nombre	

		tipoCuenta = None
		if proyectoEmpresa.proyecto.tipo_cuenta:
			tipoCuenta = proyectoEmpresa.proyecto.tipo_cuenta.nombre

		numeroCuenta =None
		if proyectoEmpresa.proyecto.No_cuenta:
			numeroCuenta = proyectoEmpresa.proyecto.No_cuenta

		worksheet.write(row, col,proyectoEmpresa.proyecto.mcontrato.nombre ,format2)
		worksheet.write(row, col+1,proyectoEmpresa.proyecto.municipio.departamento.nombre ,format2)
		worksheet.write(row, col+2,proyectoEmpresa.proyecto.municipio.nombre ,format2)
		worksheet.write(row, col+3,proyectoEmpresa.proyecto.nombre ,format2)
		worksheet.write(row, col+4,proyectoEmpresa.proyecto.valor_adjudicado ,format_money)
		worksheet.write(row, col+5,entidadBancaria ,format2)
		worksheet.write(row, col+6,tipoCuenta ,format2)
		worksheet.write(row, col+7,numeroCuenta ,format2)

		
		row +=1
	workbook.close()
	return response


@login_required
def resumen(request):
	return render(request, 'proyecto/resumen.html',{'model':'proyecto','app':'proyecto'})
 

@login_required
def hoja_resumen(request,id_proyecto=None):

	monto=0
	model_proyecto = Proyecto.objects.get(pk=id_proyecto)
	queryset = model_proyecto.contrato.all().values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero')

	#valida si el proyecto tiene contratos
	if queryset.count()>0:

		for item in list(queryset):

			queryset2=DEncabezadoGiro.objects.filter(contrato__id=item['id']).values('nombre__nombre','id','nombre__contrato__id','contrato__id')

			#valida si los contratos tienen giros
			if queryset2.count()>0:

				for items in  list(queryset2):

					#calcula el valor total de todos los detalles del giro segun el encabezado giro
					sumatoria=DetalleGiro.objects.filter(encabezado_id=items['id']).aggregate(suma_detalle=Sum('valor_girar'))	

					if sumatoria['suma_detalle']:

						monto=monto+int(sumatoria['suma_detalle'])

	empresa = request.user.usuario.empresa.id
	qsProyecto=Proyecto_empresas.objects.filter(proyecto__id=id_proyecto, empresa__id=empresa ).first()
	qsfotoAntes=CFotosProyecto.objects.filter(proyecto__id=id_proyecto, tipo__id=35).order_by('-id')[:6]
	qsfotoDurante=CFotosProyecto.objects.filter(proyecto__id=id_proyecto, tipo__id=36).order_by('-id')[:6]
	qsfotoDespues=CFotosProyecto.objects.filter(proyecto__id=id_proyecto, tipo__id=37).order_by('-id')[:6]
	qsDatosTecnicos = Proyecto_info_tecnica.objects.filter(proyecto__id=id_proyecto)
	qsCronograma = BCronograma.objects.filter(proyecto__id=id_proyecto)
	empres=request.user.usuario.empresa.id
	qsprocesos = FProcesoRelacion.objects.filter(idApuntador=id_proyecto,proceso__apuntador=1,proceso__empresas__id=empres).values('proceso__id','proceso__nombre','id','proceso__apuntador')

	return render(request, 'proyecto/hoja_resumen.html',{'total_giros':monto,'procesoProyecto':qsprocesos,'cronograma':qsCronograma,'datos_tecnicos':qsDatosTecnicos,'fotos_despues':qsfotoDespues,'fotos_durante':qsfotoDurante,'fotos_antes':qsfotoAntes,'empresa_proyecto':qsProyecto,'app':'proyecto','model':'proyecto','id_proyecto':int(id_proyecto)})		


#Vista sin necesidad de loguearse
def resumen_dispac(request):
	empresa = 18
	return render(request, 'proyecto/resumen_dispac.html',{'empresa':empresa,'model':'proyecto','app':'proyecto'})


#Vista sin necesidad de loguearse
def hoja_resumen_dispac(request,id_proyecto=None):

	empresa = 18
	qsProyecto=Proyecto_empresas.objects.filter(proyecto__id=id_proyecto, empresa__id=empresa ).first()
	qsfotoAntes=CFotosProyecto.objects.filter(proyecto__id=id_proyecto, tipo__id=35).order_by('-id')[:6]
	qsfotoDurante=CFotosProyecto.objects.filter(proyecto__id=id_proyecto, tipo__id=36).order_by('-id')[:6]
	qsfotoDespues=CFotosProyecto.objects.filter(proyecto__id=id_proyecto, tipo__id=37).order_by('-id')[:6]
	qsDatosTecnicos = Proyecto_info_tecnica.objects.filter(proyecto__id=id_proyecto)

	qsCronograma = BCronograma.objects.filter(proyecto__id=id_proyecto)
	qsprocesos = FProcesoRelacion.objects.filter(idApuntador=id_proyecto,proceso__apuntador=1).values('proceso__id','proceso__nombre','id','proceso__apuntador')
	#qscorrespondencia = CorrespondenciaEnviada.objects.filter(proyecto__id=id_proyecto)

	return render(request, 'proyecto/hoja_resumen_dispac.html',{'procesoProyecto':qsprocesos,'cronograma':qsCronograma,'datos_tecnicos':qsDatosTecnicos,'fotos_despues':qsfotoDespues,'fotos_durante':qsfotoDurante,'fotos_antes':qsfotoAntes,'empresa_proyecto':qsProyecto,'app':'proyecto','model':'proyecto','id_proyecto':int(id_proyecto)})		



#Lista de los procesos segun proyecto
def listProyectoProceso(request):
	if request.method == 'GET':
		try:
			proyecto = request.GET['proyecto_id'] if 'proyecto_id' in request.GET else None;
			lista=[]
			validacion=''
			
			if proyecto:

				model_proyecto = Proyecto.objects.get(pk=proyecto)
				queryset = model_proyecto.contrato.all().values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero')

				if queryset.count()>0:

					for item in list(queryset):
					
						queryset2 = FProcesoRelacion.objects.filter(idApuntador=item['id']).values('idTablaReferencia','idApuntador','proceso__id','proceso__nombre','id')

						if queryset2.count()>0:

							if queryset2.first()['idTablaReferencia'] == queryset2.first()['idApuntador']:

								validacion='No aplica'

							else:

								objProceso = AProceso.objects.get(id=queryset2.first()['proceso__id'])

								modeloReferencia = ContentType.objects.get(pk=objProceso.tablaForanea.id).model_class()

								elemento = modeloReferencia.objects.filter(id=queryset2.first()['idTablaReferencia']).values(objProceso.etiqueta)

								#print(e)lemento[0][objProceso.etiqueta]

								validacion=elemento[0][objProceso.etiqueta]


							row={
									'nombre_contrato':item['nombre'],
									'numero_contrato':item['numero'],
									'nombre_proceso': "No tiene proceso relacionado" if queryset2.count()==0 else queryset2.first()['proceso__nombre'],
									'validacion':validacion,
									'proceso_id':"" if queryset2.count()==0 else queryset2.first()['proceso__id'],
								}

							lista.append(row)

						else:

							return JsonResponse({'message':'No se encontraron registros','success':'ok','data':''})
					
				else:

					return JsonResponse({'message':'No se encontraron contratos relacionados al proyecto','success':'ok','data':''})
			
			return JsonResponse({'message':'','success':'ok','data':lista})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin de la lista de los procesos



#Listado de los giros segun los contrato asociados al proyectos
def listadoGiroContrato(request):
	if request.method == 'GET':
		try:
			proyecto = request.GET['proyecto_id'] if 'proyecto_id' in request.GET else None;
			lista=[]
			validacion=''
			monto=''
			
			if proyecto:

				model_proyecto = Proyecto.objects.get(pk=proyecto)
				queryset = model_proyecto.contrato.all().values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero')

				#valida si el proyecto tiene contratos
				if queryset.count()>0:

					for item in list(queryset):

						queryset2=DEncabezadoGiro.objects.filter(contrato__id=item['id']).values('nombre__nombre','id','nombre__contrato__id','contrato__id')

						#valida si los contratos tienen giros
						if queryset2.count()>0:

							for items in  list(queryset2):

								#calcula el valor total de todos los detalles del giro segun el encabezado giro
								sumatoria=DetalleGiro.objects.filter(encabezado_id=items['id']).aggregate(suma_detalle=Sum('valor_girar'))	

								if sumatoria['suma_detalle']:

									monto=sumatoria['suma_detalle']
								else:
									monto=0 	
								row={
									 	'id_giro':items['id'],
									 	'nombre_giro':items['nombre__nombre'],
									 	'nombre_contrato_id':items['nombre__contrato__id'],
									 	'contrato_id':items['contrato__id'],
									 	'monto':monto,
									 	'nombre_contrato':item['nombre'],
										'numero_contrato':item['numero'],
								 	}


								lista.append(row)

						# else:

						#  	return JsonResponse({'message':'No se encontraron giros relacionados a los contratos','success':'ok','data':''})
					
				else:

					return JsonResponse({'message':'No se encontraron contratos relacionados al proyecto','success':'ok','data':''})
	
			return JsonResponse({'message':'','success':'ok','data':lista})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin del listado de los giros



#Listado de las polizas asociadas a los contratos del proyecto
def listadoPolizaContrato(request):
	if request.method == 'GET':
		try:

			lista=[]

			proyecto = request.GET['proyecto_id'] if 'proyecto_id' in request.GET else None; #Parametro de proyecto

			if proyecto:

				#Consulto los contratos asociadoas a ese proyecto
				model_proyecto = Proyecto.objects.get(pk=proyecto)
				queryset = model_proyecto.contrato.all().values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero')

				#valido si el proyecto tiene contrato
				if queryset.count()>0:

					for item in list(queryset):

						#Consulta las polizas segun el contrato
						qsPoliza=VigenciaPoliza.objects.filter(poliza__contrato__id=item['id']).values('poliza__tipo__nombre','fecha_inicio','fecha_final','valor')


						#valido si los contrato tienen polizas
						if qsPoliza.count()>0:

							for items in  list(qsPoliza):

						 		#Armo la lista que voy a mandar para el listado de las polizas
								row={
										'poliza_nombre':items['poliza__tipo__nombre'],
										'fecha_inicio':items['fecha_inicio'],
										'fecha_final':items['fecha_final'],
										'valor':items['valor'],
										'nombre_contrato':item['nombre'],
										'numero_contrato':item['numero'],
									}

								lista.append(row)

						# else:

						#  	return JsonResponse({'message':'No se encontraron polizas relacionadas a los contratos','success':'ok','data':''})

					if lista:

						return JsonResponse({'message':'','success':'ok','data':lista})
					else:

						return JsonResponse({'message':'No se encontraron vigencias relacionadas a los contratos','success':'ok','data':''})

				else:

					return JsonResponse({'message':'No se encontraron contratos relacionados al proyecto','success':'ok','data':''})

					
			return JsonResponse({'message':'','success':'ok','data':lista})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin de funciones de las polizas obtenidos por los contratos del proyecto



#Listado de las vigencias de los contratos asociados al proyecto
def listadoVigenciaContrato(request):
	if request.method == 'GET':
		try:

			lista=[]
			validacion=''

			proyecto = request.GET['proyecto_id'] if 'proyecto_id' in request.GET else None; #Parametro de proyecto
			validacion = request.GET['validacion']

			if proyecto:

				#Consulto los contratos asociadoas a ese proyecto
				model_proyecto = Proyecto.objects.get(pk=proyecto)
				queryset = model_proyecto.contrato.all().values('id', 'nombre' , 'tipo_contrato__nombre' , 'numero')

				#Valida si trae contratos
				if queryset.count()>0:

					for item in list(queryset):

						#Consulta las vigencias segun los contratos del proyecto
						if validacion=='1':
							qsVigencia = VigenciaContrato.objects.filter(contrato__id=item['id'], tipo__id__in=(18,19)).values('id', 'nombre', 'fecha_inicio' , 'fecha_fin', 'soporte','tipo__nombre','valor')

						if validacion=='2':


							qsVigencia = VigenciaContrato.objects.filter(contrato__id=item['id'], tipo__id__in=(20,21)).values('id', 'nombre', 'fecha_inicio' , 'fecha_fin', 'soporte','tipo__nombre','valor')


						#Valida si lis contratos tienen vigencias
						if qsVigencia.count()>0:

							for items in  list(qsVigencia):

						 		#Armo la lista que voy a mandar para el listado de las vigencias
								row={
										'id': items['id'],
										'operacion':items['nombre'],
										'desde':items['fecha_inicio'],
										'hasta':items['fecha_fin'],
										'soporte':settings.MEDIA_URL + items['soporte'],
										'tipo_nombre':items['tipo__nombre'],
										'valor':items['valor'],
										'nombre_contrato':item['nombre'],
										'numero_contrato':item['numero'],
									}

								lista.append(row)

						# else:

						#  	return JsonResponse({'message':'No se encontraron vigencias relacionadas a los contratos','success':'ok','data':''})

					if lista:

						return JsonResponse({'message':'','success':'ok','data':lista})
					else:

						return JsonResponse({'message':'No se encontraron datos','success':'ok','data':''})
							

				else:

					return JsonResponse({'message':'No se encontraron datos','success':'ok','data':''})
								
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin de funciones que trae las vigencias

@login_required
def AsignacionProyecto(request):
	tipo_c=tipoC()
	queryset_empresa=Empresa.objects.filter(esContratante=True)
	queryset_contrato=Contrato.objects.filter(tipo_contrato=tipo_c.m_contrato,empresacontrato__empresa=request.user.usuario.empresa.id,empresacontrato__participa=1,activo=1)
	return render(request, 'proyecto/asignacion_proyecto.html',{'mcontrato':queryset_contrato,'empresa':queryset_empresa, 'model':'proyecto','app':'proyecto'})

# Guardar proyectos a los funcionarios
def crearProyectoFuncionario(request):

	# print request.GET['proyecto_id']+"jj"

	proyecto_id = request.GET['proyecto_id']
	funcionario_id = request.GET['funcionario_id']
	# if request.method == 'POST':
	try:
		myList = proyecto_id.split(',')

		for item in myList:
			if item:
				# print "lasas:"
				model_proyecto = Proyecto.objects.get(pk=item)
				model_proyecto.funcionario.add(funcionario_id)

		return JsonResponse({'message':'El registro ha sido guardado exitosamente','success':'ok','data': ''})
	except Exception as e:
		print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)	

def destroylistaProyectoFuncionario(request):
	if request.method == 'POST':
			try:
				lista=request.POST['_content']
				respuesta= json.loads(lista)
				myList = respuesta['lista']
				funcionario_id = respuesta['funcionario_id']
				for item in myList:
					model_proyecto = Proyecto.objects.get(pk=item['id'])
					model_proyecto.funcionario.remove(funcionario_id)


				# transaction.commit()
				return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok','data': ''})
			except Exception as e:
				print(e)
				return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)		


# Vistas de informe ejecutivo

@login_required	
def resumen_por_fondo(request):
	cursor = connection.cursor()
	try:
		cursor.callproc('[dbo].[ejecutivo_resumen_por_fondo_aportes]')		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		return render(request, 'informe_ejecutivo/resumen_por_fondo.html',
		{'resumen':resumen,'model':'P_fondo','app':'proyecto'},
		)

	except Exception as e:
		print(e)

@login_required		
def resumen_por_contrato(request, fondo_id):
	cursor = connection.cursor()
	try:

		cursor.callproc('[dbo].[ejecutivo_resumen_por_contrato]', [fondo_id,])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		return render(request, 'informe_ejecutivo/resumen_por_contrato.html',
		{'resumen':resumen,'model':'P_fondo','app':'proyecto','fondo_id':fondo_id},
		)

	except Exception as e:
		print(e)

@login_required	
def resumen_por_contrato_tipo_proyecto(request, fondo_id):
	cursor = connection.cursor()
	try:
		
		cursor.callproc('[dbo].[ejecutivo_resumen_por_contrato_tipo_proyecto]', [fondo_id,])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		return render(request, 'informe_ejecutivo/resumen_por_tipo_proyecto.html',
		{'resumen':resumen,'model':'P_fondo','app':'proyecto','fondo_id':fondo_id},
		)

	except Exception as e:
		print(e)	

@login_required	
def consulta_fondo_proyecto(request):
	try:
		
		fondo_id=request.GET.get('fondo_id', None)
		contrato_id=request.GET.get('contrato_id', None)
		departamento_id=request.GET.get('departamento_id', None)
		municipio_id=request.GET.get('municipio_id', None)
		tipo_proyecto_id=request.GET.get('tipo_proyecto_id', None)

		cursor = connection.cursor()
		cursor.callproc('[dbo].[ejecutivo_consulta_fondo_proyecto]', [fondo_id,contrato_id,departamento_id,municipio_id,tipo_proyecto_id,])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
				
		return JsonResponse({'message':'','success':'ok','data':resumen})	

	except Exception as e:
		print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required	
def resumen_por_proyecto(request, fondo_id):	

	return render(request, 'informe_ejecutivo/resumen_por_proyecto.html',
	{'resumen':resumen,'model':'P_fondo','app':'proyecto','fondo_id':fondo_id},
	)

@login_required		
def resumen_por_giros(request, fondo_id):
	cursor = connection.cursor()
	try:
		
		cursor.callproc('[dbo].[ejecutivo_resumen_por_fondo_giro]')		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		return render(request, 'informe_ejecutivo/resumen_por_giros.html',
		{'resumen':resumen,'model':'P_fondo','app':'proyecto','fondo_id':fondo_id},
		)

	except Exception as e:
		print(e)	

@login_required		
def resumen_por_fondo_contrato_giro(request, fondo_id):
	cursor = connection.cursor()
	try:
		
		cursor.callproc('[dbo].[ejecutivo_resumen_por_fondo_contrato_giro]', [fondo_id,])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		return render(request, 'informe_ejecutivo/resumen_por_contrato_mme.html',
		{'resumen':resumen,'model':'P_fondo','app':'proyecto','fondo_id':fondo_id},
		)

	except Exception as e:
		print(e)	

@login_required		
def resumen_por_fondo_giro_contratista(request, fondo_id):	
	try:
		
		fondos=P_fondo.objects.all()
		contratistas=Empresa.objects.filter(esContratista=True)

		return render(request, 'informe_ejecutivo/resumen_por_contratista.html',
		{'model':'P_fondo','app':'proyecto','fondo_id':fondo_id, 'fondos':fondos, 'contratistas':contratistas},
		)

	except Exception as e:
		print(e)			

@login_required	
def balance_financiero(request, contrato_id, fondo_id):
	cursor = connection.cursor()
	try:
		
		# cursor.callproc('[dbo].[ejecutivo_balance_financiero]', [contrato_id,])		
		# columns = cursor.description 
		# resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		return render(request, 'informe_ejecutivo/balance_financiero.html',
		{'model':'P_fondo','app':'proyecto','fondo_id':fondo_id},
		)

	except Exception as e:
		print(e)	

@login_required	
def consulta_balance_financiero(request):
	try:
				
		contrato_id=request.GET.get('contrato_id', None)		
		cursor = connection.cursor()
		cursor.callproc('[dbo].[ejecutivo_balance_financiero]', [contrato_id,])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
				
		return JsonResponse({'message':'','success':'ok','data':resumen})	

	except Exception as e:
		print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required	
def consultar_fondo_giro_contratista(request):
	cursor = connection.cursor()
	try:
				
		contratista_id=request.GET.get('contratista_id', None)		
		fondo_id=request.GET.get('fondo_id', None)		
		contrato_id=request.GET.get('contrato_id', None)
		cursor.callproc('[dbo].[ejecutivo_resumen_por_fondo_giro_contratista]', [contratista_id, fondo_id, contrato_id, ])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
				
		return JsonResponse({'message':'','success':'ok','data':resumen})	

	except Exception as e:
		print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required	
def exportar_resumen_por_fondo(request):
	cursor = connection.cursor()
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="resumen-por-fondo.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Lista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})
		
		worksheet.write('A1','Fondo de financiacion', format1)
		worksheet.write('B1','No.Proyectos', format1)
		worksheet.write('C1','No.Clientes', format1)
		worksheet.write('D1','Valor Proyecto MME', format1)
		worksheet.write('E1','Aportes MME', format1)
		
		worksheet.set_column('A:A', 24)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 24)
		worksheet.set_column('E:E', 18)		
		
		row=1
		col=0
		
		cursor.callproc('[dbo].[ejecutivo_resumen_por_fondo_aportes]')		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		for r in resumen:			
			worksheet.write(row,col,r['fondo'] ,format2)
			worksheet.write(row,col+1,r['numero_proyecto'] ,format2)
			worksheet.write(row,col+2,r['n_clientes'] ,format2)
			worksheet.write(row,col+3,r['valor'] ,format_money)
			worksheet.write(row,col+4,r['aporte'] ,format_money)							
			row +=1
		
		workbook.close()
		return response
	except Exception as e:
		print(e)

@login_required	
def exportar_resumen_por_contrato(request, fondo_id):
	cursor = connection.cursor()
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="resumen-por-fondo.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Lista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})
		
		worksheet.write('A1','Fondo de financiacion', format1)
		worksheet.write('B1','Contrato', format1)
		worksheet.write('C1','No.Proyectos', format1)
		worksheet.write('D1','No.Clientes', format1)
		worksheet.write('E1','Valor Proyecto MME', format1)
		worksheet.write('F1','Aportes MME', format1)
		
		worksheet.set_column('A:A', 24)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 28)
		worksheet.set_column('E:E', 24)		
		worksheet.set_column('F:F', 18)		
		
		row=1
		col=0
		
		cursor.callproc('[dbo].[ejecutivo_resumen_por_contrato]', [fondo_id,])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		for r in resumen:			
			worksheet.write(row,col,r['fondo'] ,format2)
			worksheet.write(row,col+1,r['contrato'] ,format2)
			worksheet.write(row,col+2,r['numero_proyecto'] ,format2)
			worksheet.write(row,col+3,r['n_clientes'] ,format2)
			worksheet.write(row,col+4,r['valor'] ,format_money)					
			worksheet.write(row,col+5,r['aporte'] ,format_money)							
			row +=1
		
		workbook.close()
		return response
	except Exception as e:
		print(e)

@login_required	
def exportar_resumen_por_contrato_tipo_proyecto(request, fondo_id):
	cursor = connection.cursor()
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="resumen-por-contratos.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Lista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})
		
		worksheet.write('A1','Fondo de financiacion', format1)
		worksheet.write('B1','No.Proyectos', format1)
		worksheet.write('C1','No.Clientes', format1)
		worksheet.write('D1','Valor Proyecto MME', format1)
		worksheet.write('E1','Aportes MME', format1)
		
		worksheet.set_column('A:A', 24)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 28)
		worksheet.set_column('E:E', 24)		
		
		row=1
		col=0
		
		cursor.callproc('[dbo].[ejecutivo_resumen_por_contrato_tipo_proyecto]', [fondo_id,])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		for r in resumen:			
			worksheet.write(row,col,r['fondo'] ,format2)
			worksheet.write(row,col+1,r['nombre'] ,format2)
			worksheet.write(row,col+2,r['tipo_id'] ,format2)
			worksheet.write(row,col+3,r['contrato'] ,format2)
			worksheet.write(row,col+4,r['numero_proyecto'] ,format_money)					
			worksheet.write(row,col+5,r['aporte'] ,format_money)							
			row +=1
		
		workbook.close()
		return response
	except Exception as e:
		print(e)	

@login_required	
def exportar_resumen_por_fondo_proyecto(request):
	cursor = connection.cursor()
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="resumen-por-contratos.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Lista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})
		
		worksheet.write('A1','Fondo de financiacion', format1)
		worksheet.write('B1','Contrato MME', format1)
		worksheet.write('C1','Departamento', format1)
		worksheet.write('D1','Municipio', format1)
		worksheet.write('E1','Proyecto', format1)
		worksheet.write('F1','No. Usuario', format1)

		worksheet.write('G1','Valor proyecto MME', format1)
		worksheet.write('H1','% avance', format1)
		worksheet.write('I1','Estado del contrato', format1)
		worksheet.write('J1','Estado del proyecto', format1)
		
		worksheet.set_column('A:A', 24)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 18)
		worksheet.set_column('D:D', 28)
		worksheet.set_column('E:E', 24)		
		worksheet.set_column('F:F', 18)	
		worksheet.set_column('G:G', 18)		
		worksheet.set_column('H:H', 18)		
		worksheet.set_column('I:I', 18)		
		worksheet.set_column('J:J', 18)		
		
		row=1
		col=0
		
		fondo_id=request.GET.get('fondo_id', None)
		contrato_id=request.GET.get('contrato_id', None)
		departamento_id=request.GET.get('departamento_id', None)
		municipio_id=request.GET.get('municipio_id', None)
		tipo_proyecto_id=request.GET.get('tipo_proyecto_id', None)
		
		cursor.callproc('[dbo].[ejecutivo_consulta_fondo_proyecto]', [fondo_id,contrato_id,departamento_id,municipio_id,tipo_proyecto_id,])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		for r in resumen:			
			worksheet.write(row,col,r['fondo'] ,format2)
			worksheet.write(row,col+1,r['nombre_contrato'] ,format2)
			worksheet.write(row,col+2,r['departamento'] ,format2)
			worksheet.write(row,col+3,r['municipio'] ,format2)
			worksheet.write(row,col+4,r['nombre'] ,format2)					
			worksheet.write(row,col+5,r['usuarios'] ,format2)							

			worksheet.write(row,col+6,r['valor'] ,format_money)							
			worksheet.write(row,col+7,r['porcen'] ,format2)							
			worksheet.write(row,col+8,r['contrato_estado'] ,format2)							
			worksheet.write(row,col+9,r['estado_proyecto'] ,format2)							
			row +=1
		
		workbook.close()
		return response
	except Exception as e:
		print(e)	

@login_required	
def exportar_resumen_por_giros(request, fondo_id):
	cursor = connection.cursor()
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="resumen-por-contratos.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Lista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})
		
		worksheet.write('A1','Fondo de financiacion', format1)
		worksheet.write('B1','Valor Girado', format1)
		worksheet.write('C1','Saldo en cuentas', format1)
				
		worksheet.set_column('A:A', 24)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 18)
				
		row=1
		col=0
		
		cursor.callproc('[dbo].[ejecutivo_resumen_por_fondo_giro]')		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]


		for r in resumen:			
			worksheet.write(row,col,r['fondo'] ,format2)
			worksheet.write(row,col+1,r['valor'] ,format_money)
			worksheet.write(row,col+2,r['saldo'] ,format_money)								
			row +=1
		
		workbook.close()
		return response
	except Exception as e:
		print(e)	

@login_required	
def exportar_balance_financiero(request):
	cursor = connection.cursor()
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="resumen-balance-financiero.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Lista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})
		
		worksheet.write('A1','Estado', format1)
		worksheet.write('B1','No.Proyectos', format1)
		worksheet.write('C1','No. Usuarios Aprobados', format1)
		worksheet.write('D1','No. Usuarios Normalizados', format1)
		worksheet.write('E1','Valor Proyecto Aprobado MME', format1)		
		worksheet.write('F1','Valor Liquidacion Proyecto', format1)
		worksheet.write('G1','Valor Girado al proyecto', format1)
		worksheet.write('H1','Balance Contratista', format1)
		worksheet.write('I1','Balance Proyecto', format1)
		worksheet.write('J1','Total Materiales', format1)
		
		worksheet.set_column('A:A', 17)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 24)
		worksheet.set_column('D:D', 24)
		worksheet.set_column('E:E', 24)		
		worksheet.set_column('F:F', 24)	
		worksheet.set_column('G:G', 24)
		worksheet.set_column('H:H', 24)		
		worksheet.set_column('I:I', 24)		
		worksheet.set_column('J:J', 24)		
		
		row=1
		col=0
		
		contrato_id=request.GET.get('contrato_id', None)				
		cursor.callproc('[dbo].[ejecutivo_balance_financiero]', [contrato_id,])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
			
		for r in resumen:			
			worksheet.write(row,col,r['estado'] ,format2)
			worksheet.write(row,col+1,r['no_proyectos'] ,format_money)
			worksheet.write(row,col+2,r['diseno'] ,format_money)
			worksheet.write(row,col+3,r['usuario_replanteo'] ,format_money)
			worksheet.write(row,col+4,r['valor_proyecto'] ,format_money)					
			worksheet.write(row,col+5,r['valor_liquidacion'] ,format_money)	
			worksheet.write(row,col+6,r['valor_girado'] ,format_money)
			worksheet.write(row,col+7,r['balance_proyecto'] ,format_money)					
			worksheet.write(row,col+8,r['valor_liquidacion'] ,format_money)		
			worksheet.write(row,col+9,'0' ,format_money)							
			row +=1
		
		workbook.close()
		return response
	except Exception as e:
		print(e)

@login_required	
def exportar_fondo_giro_contratista(request):
	cursor = connection.cursor()
	try:
		response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
		response['Content-Disposition'] = 'attachment; filename="fondo-giro-contratista.xls"'

		workbook = xlsxwriter.Workbook(response, {'in_memory': True})
		worksheet = workbook.add_worksheet('Lista')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money=workbook.add_format({'border':1,'num_format': '$#,##0'})
		
		worksheet.write('A1','Contratista', format1)
		worksheet.write('B1','Fondo', format1)
		worksheet.write('C1','Contrato MME', format1)
		worksheet.write('D1','Valor girado', format1)
				
		worksheet.set_column('A:A', 17)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:C', 24)
		worksheet.set_column('D:D', 24)
				
		row=1
		col=0
		
		contrato_id=request.GET.get('contrato_id', None)				
		cursor.callproc('[dbo].[ejecutivo_balance_financiero]', [contrato_id,])		
		columns = cursor.description 
		resumen = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
			
		for r in resumen:			
			worksheet.write(row,col,r['contratista'] ,format2)
			worksheet.write(row,col+1,r['fondo'] ,format2)
			worksheet.write(row,col+2,r['contrato'] ,format2)
			worksheet.write(row,col+3,r['valor'] ,format_money)						
			row +=1
		
		workbook.close()
		return response
	except Exception as e:
		print(e)

# Fin vistas de informe ejecutivo


