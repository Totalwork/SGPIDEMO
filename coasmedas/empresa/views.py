from django.shortcuts import render
#, render_to_response
from .models import Empresa , EmpresaAcceso, EmpresaContratante,EmpresaCuenta
from logs.models import Logs,Acciones
from rest_framework import viewsets, serializers, response
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
from django.contrib.auth.decorators import login_required
from .enum import enumEstados
from estado.views import EstadoSerializer
from estado.models import Estado
from tipo.models import Tipo
from tipo.views import TipoSerializer
from django.db import transaction
from coasmedas.functions import functions
#from rest_framework_oauth.authentication import OAuth2Authentication
# Create your views here.


class EmpresaSerializer(serializers.HyperlinkedModelSerializer):
	esDisenador = serializers.BooleanField(default=False)
	esProveedor = serializers.BooleanField(default=False)
	esContratista = serializers.BooleanField(default=False)
	esContratante = serializers.BooleanField(default=False)
	consecutivoDigitado = serializers.BooleanField(default=False)
	codigo_acreedor = serializers.IntegerField(allow_null=True,required=False)
	#logo = serializers.ImageField(required=False)

	class Meta:
		model = Empresa
		fields=('url','id','nombre','nit','direccion','abreviatura','logo','esDisenador','esProveedor','esContratista','esContratante' , 'encabezado' , 'piePagina' , 'marcaAgua' , 'peso' , 'consecutivoDigitado','control_pago_factura','codigo_acreedor')

class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Empresa
		fields=('id','nombre')

class EmpresaViewSet(viewsets.ModelViewSet):
	"""
		Retorna una lista de empresas, puede utilizar el parametro <b>{dato=[texto a buscar]}</b>, a traves del cual, se podra buscar por todo o parte del nombre y nit.<br/>
		Igualmente puede utilizar los siguientes parametros:<br/><br/>
		<b>{esContratante=1}</b>: Retorna la lista de empresas marcadas como Contratante.<br/>
		<b>{esContratista=1}</b>: Retorna la lista de empresas marcadas como Contratista.<br/>
		<b>{esProveedor=1}</b>: Retorna la lista de empresas marcadas como Proveedor.<br/>
		<b>{esDisenador=1}</b>: Retorna la lista de empresas marcadas como Dise&ntilde;ador.<br/><br/>
		Es posible utilizar los parametros combinados, por ejemplo: buscar en la lista de contratista aquellos que contentan determinado letra o numero en su nombre o Nit.
	"""	
	model=Empresa
	model_log=Logs
	model_acciones=Acciones
	queryset = model.objects.all()
	serializer_class = EmpresaSerializer
	parser_classes=(FormParser, MultiPartParser)
	paginate_by = 10
	nombre_modulo=''


	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','success':'ok','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(EmpresaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			esContratista= self.request.query_params.get('esContratista',None)
			esContratante= self.request.query_params.get('esContratante',None)
			esProveedor= self.request.query_params.get('esProveedor',None)
			esDisenador= self.request.query_params.get('esDisenador',None)
			filtro_empresa_campana= self.request.query_params.get('filtro_empresa_campana',None)

			sin_paginacion= self.request.query_params.get('sin_paginacion',None)

			if (dato or esContratista or esContratante or esProveedor or esDisenador or filtro_empresa_campana):
				if dato:
					qset = (
						Q(nombre__icontains=dato)|
						Q(nit__icontains=dato)|
						Q(abreviatura__icontains=dato)
						)
				if esContratista:
					if dato:
						qset = qset & (
							Q(esContratista=esContratista)
							)
					else:
						qset = (
							Q(esContratista=esContratista)
							)
				if esContratante:
					if dato or esContratista:
						qset = qset & (
							Q(esContratante=esContratante)
							)
					else:
						qset = (
							Q(esContratante=esContratante)
							)
				if esProveedor:
					if dato or esContratista or esContratante:
						qset = qset & (
							Q(esProveedor=esProveedor)
							)
					else:
						qset = (
							Q(esProveedor=esProveedor)
							)
				if esDisenador:
					if dato or esContratista or esContratante or esProveedor:
						qset = qset & (
							Q(esDisenador=esDisenador)
							)
					else:
						qset = (
							Q(esDisenador=esDisenador)
							)
				if filtro_empresa_campana:
					listado=filtro_empresa_campana.split(',')
					if dato or esContratista or esContratante or esProveedor:
						qset = qset & (
							~Q(id__in=listado)
							)
					else:
						qset = (
							~Q(id__in=listado)
							)
						
				queryset = self.model.objects.filter(qset)
			
			page = self.paginate_queryset(queryset)

			if sin_paginacion is None:
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
		##print request.DATA['esProveedor']	
		#import pdb; pdb.set_trace()
		if request.data['esProveedor']=='1':
			self.nombre_modulo='empresa.proveedor'
		if request.data['esContratista']=='1':
			self.nombre_modulo='empresa.contratista'
		if request.data['esDisenador']=='1':
			self.nombre_modulo='empresa.disenador'
		if request.data['esContratante']=='1':
			self.nombre_modulo='empresa.contratante'

		if 'codigo_acreedor' in request.data:
			if int(request.data['codigo_acreedor'])==0:
				request.data['codigo_acreedor']=None

		
		if request.method == 'POST':
			##print request.DATA				
			try:
				serializer = EmpresaSerializer(data=request.data,context={'request': request})
				empresa = Empresa.objects.filter(nit=request.data['nit'])

				codigo_acre=None
				if 'codigo_acreedor' in request.data:
					if request.data['codigo_acreedor'] is not None:
						codigo_acre = Empresa.objects.filter(codigo_acreedor=request.data['codigo_acreedor'])

				if empresa:
					return Response({'message':'Ya existe una empresa registrada con el Nit digitado','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)

				if codigo_acre is not None and codigo_acre:
					return Response({'message':'Ya existe una empresa registrada con el codigo acreedor digitado','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)


				if serializer.is_valid():

					serializer.save(logo=self.request.FILES.get('logo') if self.request.FILES.get('logo') is not None else 'empresa/default.jpg')
					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_crear,nombre_modelo=self.nombre_modulo,id_manipulado=serializer.data['id'])
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
				serializer = EmpresaSerializer(instance,data=request.data,context={'request': request},partial=partial)
				
				if serializer.is_valid():
					valores=Empresa.objects.get(id=instance.id)

					if self.request.FILES.get('logo') is not None:
						if request.data['esProveedor']=='1':
							self.nombre_modulo='empresa.proveedor'
							serializer.save(logo=self.request.FILES.get('logo'),esProveedor=request.data['esProveedor'],esContratista=valores.esContratista,esDisenador=valores.esDisenador,esContratante=valores.esContratante)
						if request.data['esContratista']=='1':
							self.nombre_modulo='empresa.contratista'
							serializer.save(logo=self.request.FILES.get('logo'),esProveedor=valores.esProveedor,esContratista=request.data['esContratista'],esDisenador=valores.esDisenador,esContratante=valores.esContratante)
						if request.data['esDisenador']=='1':
							self.nombre_modulo='empresa.disenador'
							serializer.save(logo=self.request.FILES.get('logo'),esProveedor=valores.esProveedor,esContratista=valores.esContratista,esDisenador=request.data['esDisenador'],esContratante=valores.esContratante)
						if request.data['esContratante']=='1':
							self.nombre_modulo='empresa.contratante'
							serializer.save(logo=self.request.FILES.get('logo'),esProveedor=valores.esProveedor,esContratista=valores.Contratista,esDisenador=valores.esDisenador,esContratante=request.data['esContratante'])
							
					else:	
						
						if request.data['esProveedor']=='1':
							self.nombre_modulo='empresa.proveedor'
							serializer.save(logo=valores.logo,esProveedor=request.data['esProveedor'],esContratista=valores.esContratista,esDisenador=valores.esDisenador,esContratante=valores.esContratante)
						if request.data['esContratista']=='1':
							self.nombre_modulo='empresa.contratista'
							serializer.save(logo=valores.logo,esProveedor=valores.esProveedor,esContratista=request.data['esContratista'],esDisenador=valores.esDisenador,esContratante=valores.esContratante)
						if request.data['esDisenador']=='1':
							self.nombre_modulo='empresa.disenador'
							serializer.save(logo=valores.logo,esProveedor=valores.esProveedor,esContratista=valores.esContratista,esDisenador=request.data['esDisenador'],esContratante=valores.esContratante)
						if request.data['esContratante']=='1':
							self.nombre_modulo='empresa.contratante'
							serializer.save(logo=valores.logo,esProveedor=valores.esProveedor,esContratista=valores.esContratista,esDisenador=valores.esDisenador,esContratante=request.data['esContratante'])					
						

					logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_actualizar,nombre_modelo=self.nombre_modulo,id_manipulado=instance.id)
					logs_model.save()
					return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
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
			logs_model=self.model_log(usuario_id=request.user.usuario.id,accion=self.model_acciones.accion_borrar,nombre_modelo=self.nombre_modulo)
			logs_model.save()
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)			 

class EmpresaContratanteSerializer(serializers.HyperlinkedModelSerializer):
	empresa = EmpresaSerializer(read_only = True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Empresa.objects.all())

	empresa_ver = EmpresaSerializer(read_only = True)
	empresa_ver_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Empresa.objects.filter(esContratista=1))

	class Meta:
		model = EmpresaContratante
		fields = ('id', 'empresa', 'empresa_id', 'empresa_ver', 'empresa_ver_id')
		validators=[
			serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'empresa_id' , 'empresa_ver_id' ),
				message=('La empresa que quiere asociar, ya esta registrada.')
			)]

class EmpresaContratanteLiteSelectSerializer(serializers.HyperlinkedModelSerializer):
	empresa_ver = EmpresaLiteSerializer(read_only = True)

	class Meta:
		model = EmpresaContratante
		fields = ('id', 'empresa_ver')


def consultar_datos_nit(request):

	
	try:
		nit= request.GET.get('nit',None)
		tipo_empresa= request.GET.get('tipo_empresa',None)
		valores=Empresa.objects.filter(nit=nit)
		if valores:
			qset = (Q(nit=nit))

			if tipo_empresa=='esContratista':
				qset = qset &(Q(esContratista=1))
				
			if tipo_empresa=='esProveedor':
				qset = qset &(Q(esProveedor=1))
				
			if tipo_empresa=='esDisenador':
				qset = qset &(Q(esDisenador=1))
				
			if tipo_empresa=='esContratante':
				qset = qset &(Q(esContratante=1))

			valores2=Empresa.objects.filter(qset)

			if len(valores2) > 0:
				return JsonResponse({'message':'El nit ya existe','success':'ok',
				'data':''})
			else:
				lista=[]
				for item in list(valores):
					valor={
						'id':item.id,
						'nombre':item.nombre,
						'direccion':item.direccion,
						'nit':item.nit,
						'logo':unicode(item.logo)
					}
					#print json.dumps(valor)
					lista.append(valor)
				return JsonResponse({'message':'','success':'ok',
				'data':lista})

		#valores2=json.dumps(lista)
		else:
			return JsonResponse({'message':'','success':'ok',
			'data':''})			
		
	except Exception as e:
		print(e)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})		


def eliminar_varios_id(request):

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		#print respuesta['lista'].split()

		#lista=respuesta['lista'].split(',')

		#otra forma de eliminar una lista
		myList = respuesta['lista']
		Empresa.remove(*myList)

		#return HttpResponse(str('0'), content_type="text/plain")
		
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except Exception as e:
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	

def actualizar_estados_varios_id(request):

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		 
		#print respuesta['lista'].split()
		for item in respuesta['lista']:
			valores=Empresa.objects.get(pk=item['id'])
			if respuesta['tipo_empresa']=='esContratista':
				valores.esContratista=False
				valores.save()
			if respuesta['tipo_empresa']=='esProveedor':
				valores.esProveedor=False
				valores.save()
			if respuesta['tipo_empresa']=='esDisenador':
				valores.esDisenador=False
				valores.save()
			if respuesta['tipo_empresa']=='esContratante':
				valores.esContratante=False

			valores.save()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='empresa.contratista',id_manipulado=item['id'])
			logs_model.save()


		#lista=respuesta['lista'].split(',')
		
		#return HttpResponse(str('0'), content_type="text/plain")
		return JsonResponse({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''})
		
	except Exception as e:
		print(e)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})			 



def export_excel(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="empresas.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Contratista')
	format1=workbook.add_format({'border':1,'font_size':15,'bold':True})
	format2=workbook.add_format({'border':1})

	row=1
	col=0

	esContratista= request.GET['esContratista']
	esContratante= request.GET['esContratante']
	esProveedor= request.GET['esProveedor']
	esDisenador= request.GET['esDisenador']
	dato= request.GET['dato']

	if (len(dato)>0 or esContratista=='1' or esContratante=='1' or esProveedor=='1' or esDisenador=='1'):
		if (len(dato)>0):
			qset=(
					Q(nombre__icontains=dato)|
					Q(nit__icontains=dato)
				)
		#print 'voy...'	
		if esContratista=='1':
			#print 'entre....'
			if dato:
				qset=qset & (Q(esContratista=1))
			else:
				qset = (
						Q(esContratista=1)
						)
		if esContratante=='1':
			if (len(dato)>0) or esContratista=='1':
				qset = qset & (
					Q(esContratante=1)
				)
			else:
				qset = (
					Q(esContratante=1)
				)
		if esProveedor=='1':
			if (len(dato)>0) or esContratista=='1' or esContratante=='1':
				qset = qset & (
					Q(esProveedor=1)
				)
			else:
				qset = (
					Q(esProveedor=1)
				)
		if esDisenador=='1':
			if (len(dato)>0) or esContratista=='1' or esContratante=='1' or esProveedor=='1':
				qset = qset & (
					Q(esDisenador=1)
				)
			else:
				qset = (
					Q(esDisenador=1)
				)

				
		empresas = Empresa.objects.filter(qset)
		worksheet.write('A1', 'Nit', format1)
		worksheet.write('B1', 'Nombre', format1)
		worksheet.write('C1', 'Direccion', format1)

		for empresa in empresas:
			worksheet.write(row, col,empresa.nit,format2)
			worksheet.write(row, col+1,empresa.nombre,format2)
			worksheet.write(row, col+2,empresa.direccion,format2)

			row +=1


	workbook.close()

	return response
    #return response


class EmpresaAccesoSerializer(serializers.HyperlinkedModelSerializer):
	empresa = EmpresaSerializer(read_only = True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Empresa.objects.all())

	empresa_ver = EmpresaSerializer(read_only = True)
	empresa_ver_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Empresa.objects.all())

	class Meta:
		model = EmpresaAcceso
		fields = ('empresa' ,'empresa_id' , 'empresa_ver' , 'empresa_ver_id')
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'empresa_id' , 'empresa_ver_id' ),
				message=('La empresa a la que quiere ver ya esta registrada.')
				)
				]

class EmpresaAccesoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de informacion , empresas que puede ver una empresa ,
	puede utilizar el parametro (dato) a traves del cual, se podra buscar por nombre o nit de la empresa
	<br>dato = [texto] <br>
	puede utilizar el parametro (empresa) a traves del cual, se podra buscar  las empresas que puede  ver una empresa en especifico
	<br>empresa = [numero].
	puede utilizar el parametro (empresa_ver) a traves del cual, se podra buscar todas las empresa que pueden ver esta empresa.
	<br>empresa_ver = [numero].
	"""
	model = EmpresaAcceso
	queryset = model.objects.all()
	serializer_class = EmpresaAccesoSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(EmpresaAccesoViewSet, self).get_queryset()

			dato = self.request.query_params.get('dato', None)
			empresa = self.request.query_params.get('empresa', None)
			empresa_ver = self.request.query_params.get('empresa_ver', None)

			excludeMiEmpresa = self.request.query_params.get('excludeMiEmpresa', None)

			qset=(~Q(id=0))

			if dato or empresa or empresa_ver:
				if dato:
					qset = qset & ( Q(nit__icontains = dato)  | Q(nombre__icontains = dato)  )	
				if empresa:
					qset = qset & ( Q(empresa_id = empresa) )					
				if empresa_ver:
					qset =  qset & ( Q(empresa_ver_id = empresa_ver) )
					

			if excludeMiEmpresa:
				queryset = self.model.objects.filter(qset).exclude(empresa_ver_id = empresa)
			else:
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
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			
			try:
				serializer = EmpresaAccesoSerializer(data=request.data,context={'request': request})

				if serializer.is_valid():			
										
					serializer.save(empresa_id =  request.data['empresa_id'] , empresa_ver_id = request.data['empresa_ver_id'])
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "consecutivo" in serializer.errors:
						mensaje = serializer.errors['consecutivo'][0]+" En el campo consecutivo"
					else: 
						mensaje = 'datos requeridos no fueron recibidos'
					return Response({'message': mensaje ,'success':'fail',
			 			'data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				# print(e)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error', 'data':''},status=status.HTTP_400_BAD_REQUEST)

	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				serializer = EmpresaAccesoSerializer(instance,data=request.data,context={'request': request},partial=partial)
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


#Api rest para empresa cuenta
class EmpresaCuentaSerializer(serializers.HyperlinkedModelSerializer):

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='EstadoCuenta'),allow_null=True)

	tipo_cuenta = TipoSerializer(read_only=True)
	tipo_cuenta_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='cuenta'),allow_null=True,default=None)

	empresa = EmpresaSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	class Meta:
		model = EmpresaCuenta
		fields=('id','tipo_cuenta','tipo_cuenta_id','numero_cuenta','entidad_bancaria','empresa','empresa_id','estado','estado_id')


class EmpresaCuentaViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de las empresas con cuentas.
	"""
	model=EmpresaCuenta
	queryset = model.objects.all()
	serializer_class = EmpresaCuentaSerializer
	nombre_modulo='EmpresaCuenta'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)


	def list(self, request, *args, **kwargs):
		try:
			queryset = super(EmpresaCuentaViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			sin_paginacion = self.request.query_params.get('sin_paginacion', None)
			estado = self.request.query_params.get('estado', None)
			id_empresa = request.user.usuario.empresa.id
			qset=''

			qset=(~Q(id=0))

			if dato:
				qset = qset & (
					Q(numero_cuenta__icontains=dato) | Q(empresa__nombre__icontains=dato) | Q(empresa__nit__icontains=dato)
					)

			if estado and int(estado)>0:
				qset = qset & (Q(estado__id=estado))


			if qset != '':
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
				serializer = EmpresaCuentaSerializer(data=request.data,context={'request': request})

				request.data['estado_id']=enumEstados.Activo

				if serializer.is_valid():

					empresaCu = EmpresaCuenta.objects.filter(numero_cuenta=request.data['numero_cuenta'])

					if empresaCu:
						return Response({'message':'Ya existe una empresa registrada con el No. de cuenta digitado','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)

					empres=EmpresaCuenta.objects.filter(empresa__id=request.data['empresa_id'], estado__id=request.data['estado_id']).values('id')

					if len(empres)<=0:

						serializer.save(estado_id=request.data['estado_id'],tipo_cuenta_id=request.data['tipo_cuenta_id'] if request.data['tipo_cuenta_id'] is not None else None ,empresa_id=request.data['empresa_id'])

						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='empresa.EmpresaCuenta',id_manipulado=serializer.data['id'])
						logs_model.save()

						transaction.savepoint_commit(sid)

						return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)

					else:

						return JsonResponse({'message':'Se encontro una cuenta activa de la empresa','success':'error','data':''})	

				else:
					#print(serializer.errors)
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
				serializer = EmpresaCuentaSerializer(instance,data=request.data,context={'request': request},partial=partial)

				if serializer.is_valid():
					serializer.save(tipo_cuenta_id=request.data['tipo_cuenta_id'],empresa_id=request.data['empresa_id'],estado_id=request.data['estado_id'])

					logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='empresa.EmpresaCuenta',id_manipulado=serializer.data['id'])
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


#Fin api rest para empresa cuenta


#actualiza el campo estado de la tabla empresa cuenta
@transaction.atomic
def actualizar_estado_empresa_cuenta(request):

	sid = transaction.savepoint()

	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		estado= respuesta['estado']

		for item in respuesta['lista']:
			object_cuenta=EmpresaCuenta.objects.get(pk=item['id'])

			object_cuenta.estado_id=estado
			object_cuenta.save()

			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='empresa.EmpresaCuenta',id_manipulado=item['id'])
			logs_model.save()

			transaction.savepoint_commit(sid)

		return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok',
				'data':''})
		
	except Exception as e:
		#print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})



#exportar los datos de el modelo empresa cuenta
def export_excel_cuenta(request):
	
	response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="EmpresaCuenta.xls"'
	
	workbook = xlsxwriter.Workbook(response, {'in_memory': True})
	worksheet = workbook.add_worksheet('Cuenta')
	format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
	format2=workbook.add_format({'border':0,'font_size':12})

	row=1
	col=0
				
	Empresacuenta = EmpresaCuenta.objects.all().values('empresa__nombre','empresa__nit','numero_cuenta','entidad_bancaria','tipo_cuenta__nombre','estado__nombre')

	worksheet.write('A1', 'Empresa', format1)
	worksheet.write('B1', 'Nit', format1)
	worksheet.write('C1', 'Numero cuenta', format1)
	worksheet.write('D1', 'Entidad bancaria', format1)
	worksheet.write('E1', 'Tipo de cuenta', format1)
	worksheet.write('F1', 'Estado de cuenta', format1)


	for cue in Empresacuenta:
		worksheet.write(row, col,cue['empresa__nombre'],format2)
		worksheet.write(row, col+1,cue['empresa__nit'],format2)
		worksheet.write(row, col+2,cue['numero_cuenta'],format2)
		worksheet.write(row, col+3,cue['entidad_bancaria'],format2)
		worksheet.write(row, col+4,cue['tipo_cuenta__nombre'],format2)
		worksheet.write(row, col+5,cue['estado__nombre'],format2)

		row +=1


	workbook.close()

	return response
    #return response

@login_required
def contratistas(request):
		return render(request, 'empresa/contratistas.html',{'model':'empresa','app':'empresa'})

@login_required
def proveedor(request):
		return render(request, 'empresa/proveedor.html',{'model':'empresa','app':'empresa'})

@login_required
def empresa(request):
		return render(request, 'empresa/empresa.html',{'model':'empresa','app':'empresa'})

@login_required
def cargo(request):
		return render(request, 'empresa/cargo.html',{'model':'parametrizacion','app':'cargo'})