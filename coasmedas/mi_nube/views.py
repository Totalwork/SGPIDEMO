# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from coasmedas.functions import functions
from django.core import serializers
from django.db import IntegrityError,transaction
from datetime import date
import datetime
import math
import time
import zipfile
import os
from io import StringIO
from django.shortcuts import render
#, render_to_response
from django.db import transaction
from .models import Archivo, ArchivoUsuario
from rest_framework import viewsets, serializers, response
from django.db.models import Q
from django.template import RequestContext
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.decorators import login_required
#import xlsxwriter
import json
from django.http import HttpResponse,JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser

from tipo.models import Tipo
from tipo.views import TipoSerializer
from usuario.models import Usuario
from usuario.views import UsuarioSerializer
from empresa.models import Empresa , EmpresaAcceso
from empresa.views import EmpresaSerializer

from usuario.models import Usuario ,Persona
from proyecto.models import Proyecto , Proyecto_empresas
from proyecto.views import ProyectoSerializer , ProyectoEmpresaSerializer
from contrato.models import Contrato
from contrato.views import ContratoSerializer

from mi_nube.tasks import subirArchivoAsync
import celery
from celery.result import AsyncResult
from django.conf import settings

from babel.dates import format_date, format_datetime, format_time
from babel.numbers import format_number, format_decimal, format_percent

global tipoCarpeta 
tipoCarpeta = 58

from logs.models import Logs,Acciones
# from datetime import *
from django.db import transaction,connection
from django.db.models.deletion import ProtectedError

from rest_framework.decorators import api_view
from contrato.enumeration import tipoC
import re

class EmpresaLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	class Meta:
		model = Empresa
		fields=('id' , 'nombre'	)
class PersonaLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	class Meta:
		model = Persona
		fields = ('id', 'nombres','apellidos')
class UsuarioLiteSerializer(serializers.HyperlinkedModelSerializer):
	"""docstring for ClassName"""	
	persona = PersonaLiteSerializer(read_only=True)
	class Meta:
		model = Usuario
		fields=('id', 'persona')

#Api rest para Archivo
class ArchivoSerializer(serializers.HyperlinkedModelSerializer):

	tipoArchivo = TipoSerializer(read_only = True)
	tipoArchivo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Tipo.objects.filter(app="archivo"))

	propietario = UsuarioLiteSerializer(read_only = True)
	propietario_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	usuarioModificado = UsuarioLiteSerializer(read_only = True)
	usuarioModificado_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	class Meta:
		model = Archivo
		fields=('id' , 'nombre' , 'padre' , 'destino' ,
				 'tipoArchivo' , 'tipoArchivo_id' ,
				 'eliminado' , 'peso' 
				 , 'propietario' , 'propietario_id'
				 , 'fechaModificado'
				 , 'usuarioModificado' , 'usuarioModificado_id' )
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'padre' , 'nombre' , 'tipoArchivo_id' , 'propietario_id' , 'eliminado' ),
				message=('El nombre del archivo no se puede repetir.')
				)
				]


class ArchivoViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de archivos ,
	puede utilizar el parametro (dato) a traves del cual puede consultar todos los archivos.<br>
	puede utilizar el parametro (padre) a traves del cual puede filtrar la consulta por el parametro indicado.<br>
	puede utilizar el parametro (eliminado) a traves del cual puede filtrar la consulta por el parametro indicado.<br>
	puede utilizar el parametro (propietario) a traves del cual puede filtrar la consulta por el parametro indicado.<br>
	"""
	model = Archivo
	queryset = model.objects.all()
	serializer_class = ArchivoSerializer
	nombre_modulo = 'Mi Nube'

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ArchivoViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			padre = self.request.query_params.get('padre', None)
			eliminado = self.request.query_params.get('eliminado', None)
			propietario = self.request.query_params.get('propietario', None)

			qset=(~Q(id=0))

			if (dato or padre or eliminado or propietario):
				if dato:
					qset = qset & ( Q(nombre__icontains=dato) )
				if padre:
					qset = qset & ( Q(padre=padre) )
				if eliminado:
					qset = qset & ( Q(eliminado=eliminado) )
				if propietario:
					qset = qset & ( Q(propietario_id=propietario) )

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

	# @transaction.atomic	
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':			
			try:

				app_escritorio = request.DATA['app_escritorio'] if 'app_escritorio' in request.DATA else None;

				validaArchivo = False
				if request.DATA['tipoArchivo_id']=='':
					request.DATA['tipoArchivo_id']=0
								
				if int(request.DATA['tipoArchivo_id'])==int(tipoCarpeta):
					request.DATA['destino'] = None
					peso = 0.000001
					request.DATA['peso'] = float(peso)
					validaArchivo = True

				else:
					listaTipo=[59,60,61,62,63,64,65,66,67,68,69]
					if app_escritorio:

						if request.DATA.get('tipoArchivo_id') is None or request.DATA['tipoArchivo_id'] == '':							
							request.DATA['tipoArchivo_id'] = 68

						filename, file_extension = os.path.splitext(request.DATA['url_archivo'])
						tipoArchivo = validaTipoArchivo(file_extension.replace(".", "").lower())
						
						# tipoArchivo = int(request.DATA['tipoArchivo_id'])
						if tipoArchivo in listaTipo:
							request.DATA['tipoArchivo_id'] = tipoArchivo							
							validaArchivo = True
							request.DATA['peso'] = float(request.DATA['peso'])

					elif self.request.FILES.get('destino') is not None:
						archivo= self.request.FILES.get('destino')

						filename, file_extension = os.path.splitext(archivo.name)
						tipoArchivo = validaTipoArchivo(file_extension.replace(".", "").lower())						

						if tipoArchivo in listaTipo:							
							request.DATA['tipoArchivo_id'] = tipoArchivo
							validaArchivo = True							

						if archivo:
							# print 'mendoza'
							# valida si seleccionan para cambiar el nombre del archivo
							validaNombre = request.DATA['validaNombre'] if 'validaNombre' in request.DATA else None;
							if validaNombre:
								# print 'hernandez'
								if request.DATA['validaNombre'] == 'true':

									text = request.DATA['nombreActual']
									for ch in ['\\' ,'/' ,':' ,'*' ,'?' ,'"' ,'<' ,'>' ,'|']:
										if ch in text:
											text = text.replace(ch,"")
									request.DATA['nombre'] = text
									# request.DATA['nombre'] = request.DATA['nombreActual']
								
								elif request.DATA['validaNombre'] == 'false':	
									request.DATA['nombre'] = filename								

							t = datetime.datetime.now()
							archivo.name = str(request.user.usuario.empresa.id)+'-'+str(request.user.usuario.id)+'-'+str(t.year)+str(t.month)+str(t.day)+str(t.hour)+str(t.minute)+str(t.second)+str(file_extension)
							peso = (float(archivo.size)/float(1048576))
							request.DATA['peso'] = float(peso)
							request.DATA['destino'] = archivo

				# with transaction.atomic():			
				if validaArchivo:
					propietario = request.DATA['propietario_id']
					
					
					# verifica si exiiste un archivo eliminado para cambiarle el nombre por; nombre  + eliminado + id
					try:
						archivo_eliminado = Archivo.objects.get(nombre = request.DATA['nombre'] , padre = request.DATA['padre'] , propietario_id = propietario , eliminado = True , tipoArchivo_id = request.DATA['tipoArchivo_id'] )
						archivo_eliminado.nombre = str(archivo_eliminado.nombre)+"-backup"+str(archivo_eliminado.id)
						archivo_eliminado.save()

					except Archivo.DoesNotExist as e:
						pass
						
					archivo = Archivo.objects.filter(nombre = request.DATA['nombre'] , padre = request.DATA['padre'] , propietario_id = propietario , eliminado = False , tipoArchivo_id = request.DATA['tipoArchivo_id'] )
					if archivo.count()>0:
						mensaje=' Ya existe un archivo con el mismo nombre y tipo.'						
						return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)	


					serializer = ArchivoSerializer(data=request.DATA,context={'request': request})

					if serializer.is_valid():						
						try:
							if app_escritorio:	
								# print 'entro 3'
								url_archivo = request.DATA['url_archivo']								
								serializer.save(propietario_id = propietario
											, usuarioModificado_id = request.DATA['usuarioModificado_id']
											,tipoArchivo_id = request.DATA['tipoArchivo_id']
											,destino=url_archivo)
							else:

								serializer.save(propietario_id = propietario
									, usuarioModificado_id = request.DATA['usuarioModificado_id']
									,tipoArchivo_id = request.DATA['tipoArchivo_id'] , eliminado = False)								


							# print 'entro 4'	
							# SE GUARDA LA TRANSACCION DE EL RESGITRO DEL ARCHIVO
							logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='mi_nube.Archivo',id_manipulado=serializer.data['id'])
							logs_model.save()

							au = ArchivoUsuario( usuario_id = propietario
											, archivo_id = serializer.data["id"] , escritura = 1)
							au.save()
							# SE GUARDA LA TRANSACCION DEL USUARIO QUE CREA EL ARCHIVO
							logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='mi_nube.ArchivoUsuario',id_manipulado=au.id)
							logs_model.save()

							if int(serializer.data["padre"])>1:
								archivoCreado = Archivo.objects.get(pk=serializer.data["id"])
								archivo2 = Archivo.objects.get(pk=serializer.data["padre"])
								contratos = archivo2.contrato.all()
								proyectos = archivo2.proyecto.all()

								if contratos:
									archivoCreado.contrato.add(*list(contratos))

								if proyectos:
									archivoCreado.proyecto.add(*list(proyectos))										
									
								archivoUser = ArchivoUsuario.objects.get(archivo_id = archivo2.id , usuario_id = archivo2.propietario_id)

								archivoUserCompartir = ArchivoUsuario.objects.filter(archivo_id = archivo2.id).exclude(usuario_id = propietario)
									
								insert_list = []
								if archivoUserCompartir:
									for i in archivoUserCompartir:								
										# print i.usuario_id
										# print i.archivo_id
										# print i.escritura
										auc=ArchivoUsuario(usuario_id = i.usuario_id 
														, archivo_id = serializer.data["id"] , escritura = i.escritura ) 
										auc.save()
										# SE GUARDA LA TRANSACCION DEL USUARIO QUE COMPARTE EL ARCHIVO
										logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='mi_nube.ArchivoUsuario',id_manipulado=auc.id)
										logs_model.save()



							# transaction.savepoint_commit(sid)
							# transaction.commit()
							# print 'entro al commit'
							return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
								'data':serializer.data},status=status.HTTP_201_CREATED)
						except Exception as e:	
							print(e)														
							functions.toLog(e,self.nombre_modulo)
							return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
								'data':''},status=status.HTTP_400_BAD_REQUEST)
						
					else:
						# VALIDA SI ALGUN CAMPO VIENE VACIO O ERROR EN LA VALIDACION DE CAMPOS
						# print(serializer.errors)

						if "non_field_errors" in serializer.errors:
							mensaje = serializer.errors['non_field_errors']
						elif "nombre" in serializer.errors:
							mensaje = serializer.errors["nombre"][0]+" En el campo nombre"
						elif "padre" in serializer.errors:
							mensaje = serializer.errors["padre"][0]+" En el campo padre"
						else:
							mensaje = 'datos requeridos no fueron recibidos'
						
						return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)		

				else:					
					return Response({'message':'El tipo de archivo no esta permitido guardar.','success':'fail','data': ''})

			except Exception as e:				
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
			  		'data':''},status=status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def update(self,request,*args,**kwargs):
		if request.method == 'PUT':
			sid = None
			try:
				partial = kwargs.pop('partial', False)
				instance = self.get_object()
				request.DATA['destino'] = None
				serializer = ArchivoSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				
				usuarioActual = request.DATA['usuario_id'] if 'usuario_id' in request.DATA else None;
				if usuarioActual is None:
					usuarioActual = request.user.usuario.id
				id = request.DATA['id']
				padre = request.DATA['padre']
				
				text = request.DATA['nombre']
				for ch in ['\\' ,'/' ,':' ,'*' ,'?' ,'"' ,'<' ,'>' ,'|']:
					if ch in text:
						text = text.replace(ch,"")
				
				nombre = text

				tipoArchivo = request.DATA['tipoArchivo_id']
				queryset = Archivo.objects.get(pk = id)

				# if queryset.destino:
				# 	request.DATA['destino'] = queryset.destino
				# else:
				# 	request.DATA['destino'] = None

				if serializer.is_valid():
					sid = transaction.savepoint()
					try:
						archivoUser = ArchivoUsuario.objects.get(usuario_id = usuarioActual, archivo_id = id , escritura = True)
					
						if padre == 1:
							archivo = Archivo.objects.filter(propietario_id = usuarioActual , nombre = nombre , tipoArchivo_id = tipoArchivo).exclude(pk = id)
						else:
							archivo = Archivo.objects.filter(padre = padre , nombre = nombre , tipoArchivo_id = tipoArchivo).exclude(pk = id)	
					
						
						if archivo.count()>0:
							# return JsonResponse({'message':'El nombre del archivo ya existe en la carpeta.','success':'fail','data': '' })
							queryset.nombre = nombre+'- copia'
						else:									
							queryset.nombre = nombre

						t = datetime.datetime.now()
						queryset.usuarioModificado_id = usuarioActual
						queryset.fechaModificado = t
						
						queryset.save()

						# SE GUARDA LA TRANSACCION DEL USUARIO QUE ACTUALIZA EL ARCHIVO
						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='mi_nube.Archivo',id_manipulado=queryset.id)
						logs_model.save()

						transaction.savepoint_commit(sid)
						return JsonResponse({'message':'El registro ha sido actualizado exitosamente','success':'ok','data': '' })
				
					except ArchivoUsuario.DoesNotExist as e:
						if sid:
							transaction.savepoint_rollback(sid)

						return JsonResponse({'message':' No tiene permiso para modificar el nombre del archivo.','success':'fail','data': '' })							
				else:
					print(serializer.errors)
					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "nombre" in serializer.errors:
						mensaje = serializer.errors["nombre"][0]+" En el campo nombre"
					elif "padre" in serializer.errors:
						mensaje = serializer.errors["padre"][0]+" En el campo padre"
					else:
						mensaje = 'datos requeridos no fueron recibidos'

					if sid:
						transaction.savepoint_rollback(sid)	
					return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				if sid:
					transaction.savepoint_rollback(sid)
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

	# def destroy(self,request,*args,**kwargs):
	# 	try:
	# 		instance = self.get_object()
	# 		self.perform_destroy(instance)
	# 		return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
	# 			'data':''},status=status.HTTP_204_NO_CONTENT)
	# 	except Exception as e:
	# 		return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
	# 		'data':''},status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
def validarEspacio(request):
	if request.method == 'GET':
		try:
			empresa = request.GET['empresa'] if 'empresa' in request.GET else 0;
			if int(empresa)>0:
				queryset = Archivo.objects.raw("SELECT	empresa.id , empresa.[peso] as espacioTotal , SUM(archivo.[peso]) as espacioUtilizado FROM [dbo].[mi_nube_archivo] as archivo INNER JOIN [dbo].[usuario_usuario] as  usuario ON  usuario.id = archivo.propietario_id INNER JOIN [dbo].[empresa_empresa] as  empresa ON empresa.id = usuario.empresa_id Where archivo.[id]>1 AND empresa.[id] = "+str(empresa)+" AND archivo.[eliminado]=0 GROUP BY empresa.[peso] , empresa.id")
				lista = []
				for obj in queryset:
					if obj.espacioUtilizado>1000:
						utilizado = (obj.espacioUtilizado*1)/1024

						utilizado = format_decimal(utilizado,  locale='es')

						utilizado = str(utilizado)+' gigabyte(GB)'
					elif (obj.espacioUtilizado<1 and obj.espacioUtilizado>0.001):
						utilizado = (obj.espacioUtilizado*1024)/1
						utilizado = str(utilizado)[:6]
						utilizado = str(utilizado)+' kilobyte(KB)'
					elif (obj.espacioUtilizado>1 and obj.espacioUtilizado<1000):
						utilizado = str(obj.espacioUtilizado)[:6]
						utilizado = str(utilizado)+ ' megabyte(MB)'
					elif obj.espacioUtilizado<0.001:
						utilizado = (obj.espacioUtilizado*1024)
						utilizado = (utilizado*1024)
						utilizado = str(utilizado)[:6]
						utilizado = str(utilizado)+' byte(B)'

					utilizadoGB = (obj.espacioUtilizado*1)/1024

					if obj.espacioTotal>0:
						porcentajeUsado = (utilizadoGB/obj.espacioTotal)*100
					else:
						porcentajeUsado = 100

					lista.append({'espacioUtilizado': utilizado, 'porcentajeUsado': porcentajeUsado , 'espacioTotal' : obj.espacioTotal })
				if lista:
					return JsonResponse({'message':'','success':'ok','data':list(lista)})
				else:
					empresaUser = Empresa.objects.get(pk=empresa)
					lista.append({'espacioUtilizado': 0, 'porcentajeUsado': 0 , 'espacioTotal' : empresaUser.peso })
					return JsonResponse({'message':'','success':'ok','data':list(lista)})
			else:
				# print 'luis'
				return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
@api_view(['DELETE'])
def destroyArchivo(request):
	# FUNCION PARA ELIMINAR ARCHIVO
	# recibe el usuario actual y una lista de archivos
	if request.method == 'DELETE':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			usuarioActual = respuesta['usuario'] if 'usuario' in request.POST['_content'] else 0;
			if int(usuarioActual)>0:

				myListArchivos = respuesta['lista']
				for i in myListArchivos:
					hijos = Archivo.objects.raw('with query (id,eliminado) as ( SELECT id,eliminado FROM mi_nube_archivo WHERE id='+str(i)+' UNION ALL SELECT a.id,a.eliminado FROM mi_nube_archivo a INNER JOIN query cte ON a.padre = cte.id ) select id from query WHERE eliminado = 0')
					listaHijos = []
					for j in hijos:
						listaHijos.append(j.id)
						# print k.id
						# SE GUARDA LA TRANSACCION DEL USUARIO QUE ELIMINA EL ARCHIVO
						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='mi_nube.Archivo',id_manipulado=j.id)
						logs_model.save()

					Archivo.objects.filter(id__in = listaHijos).update(eliminado = 1)
				transaction.savepoint_commit(sid)
				return JsonResponse({'message':'El registro se ha eliminado correctamente.','success':'ok','data': '' })	
			else:
				return JsonResponse({'message':'El usuario es requerido.','success':'fail','data': '' })	
		except Exception as e:
			print(e)
			transaction.savepoint_rollback(sid)

@api_view(['GET'])
def listArchivoUsuarioCarpeta(request):
	#lista todas las carpetas que puede ver un usuario para crear el arbol
	if request.method == 'GET':
		try:
			
			usuarioActual = request.GET['usuario'] if 'usuario' in request.GET else request.user.usuario.id;

			queryset = Archivo.objects.raw('SELECT a.id,a.nombre,a.padre,CASE	WHEN  ( (SELECT av.id FROM  mi_nube_archivo av   WHERE av.id=a.padre)=1)   THEN 1 	WHEN  (SELECT av.id FROM mi_nube_archivousuario uav inner join mi_nube_archivo av on uav.archivo_id=av.id  WHERE av.id=a.padre AND uav.usuario_id='+str(usuarioActual)+') IS null THEN 0 else (select av.id FROM mi_nube_archivousuario uav INNER JOIN mi_nube_archivo av on uav.archivo_id=av.id  WHERE av.id=a.padre AND uav.usuario_id='+str(usuarioActual)+') END AS valida	FROM mi_nube_archivousuario ua  INNER JOIN mi_nube_archivo a on ua.archivo_id =a.id WHERE  ua.usuario_id ='+str(usuarioActual)+' AND a.tipoArchivo_id='+str(tipoCarpeta)+' AND a.eliminado=0')
			# importante comentario si valida es igual a cero no tiene padre y se le asigna uno
			lista = []
			lista.append({'id':1 , 'text': 'Inicio' , 'parent' : '#'})
			for obj in queryset:
				if int(obj.valida)== 0:
					lista.append({ 'id': obj.id , 'text': obj.nombre ,'parent': 1 }) 
				else:	
					lista.append({ 'id': obj.id , 'text': obj.nombre ,'parent':obj.padre }) 
			return JsonResponse({'message':'','success':'ok','data':list(lista) })	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def listArchivoUsuario(request):
	#lista el contenido de una carpeta o de archivo que tiene el en arbol de inicio
	if request.method == 'GET':
		try:

			padre = request.GET['padre'] if 'padre' in request.GET else 0;
			id = request.GET['id'] if 'id' in request.GET else 0;
			usuario = request.GET['usuario'] if 'usuario' in request.GET else 0;
			dato = request.GET['dato'] if 'dato' in request.GET else None;

			if int(padre)==1:
				string = ''
				if dato:
					string = "  AND c3.nombre like '%"+str(dato)+"%' "

				queryset = ArchivoUsuario.objects.raw("""
					WITH c3 as ( 
						SELECT a.[id] , a.[nombre] ,a.[padre] ,a.[destino] ,a.[tipoArchivo_id] ,a.[propietario_id] 
								,a.[eliminado] ,a.[peso], CONCAT(persona.nombres,' ',persona.apellidos) as usuarioModifico 
								, a.[fechaModificado]
								, tipo.[nombre] as tipoArchivo , CONCAT(persona2.nombres,' ',persona2.apellidos) as propietario 
								, tipo.[icono] , tipo.[color],[dbo].[mi_nube_crear_navegacion](a.id, tipo.id) as navegacion 
							
							FROM  mi_nube_archivo a 
							INNER JOIN dbo.mi_nube_archivousuario permiso on permiso.archivo_id = a.id 
							INNER JOIN [dbo].[usuario_usuario] usuario ON usuario.id = a.usuarioModificado_id 
							INNER JOIN [dbo].[usuario_persona] persona ON persona.id = usuario.persona_id 
							INNER JOIN [dbo].[tipo_tipo] tipo ON tipo.id = a.tipoArchivo_id 
							INNER JOIN [dbo].[usuario_usuario] usuario2 ON usuario2.id = a.propietario_id 
							INNER JOIN [dbo].[usuario_persona] persona2 ON persona2.id = usuario2.persona_id 
							WHERE permiso.usuario_id="""+str(usuario)+""") 
						SELECT c3.* , (SELECT COUNT(*) 
											FROM mi_nube_archivousuario ur 
											where  ur.archivo_id = c3.id AND ur.usuario_id <> """+str(usuario)+""" ) as compartido	
							FROM c3  
							WHERE padre not in (SELECT id FROM C3)  AND c3.[eliminado] = 0  """+str(string)+""" 
							ORDER BY tipoArchivo_id,nombre""")

			else:
				string = ' AND archivo.[eliminado]=0 '
				if int(padre)>0:
					string = string + ' AND archivo.[padre] = '+str(padre) 

				if int(id)>0:
					string = string + ' AND archivo.[id] = '+str(id)

				if dato:
					string = string + " AND archivo.[nombre] like '%"+str(dato)+"%'"

				queryset = ArchivoUsuario.objects.raw("""
					SELECT DISTINCT(archivo.[id]) , archivo.[nombre] , archivo.[padre] , archivo.[destino] 
						, archivo.[tipoArchivo_id]  , archivo.[propietario_id] , archivo.[eliminado] , archivo.[peso] 
						, CONCAT(persona.nombres,' ',persona.apellidos) as usuarioModifico 
						, archivo.[fechaModificado]
						, tipo.[nombre] as tipoArchivo 
						, CONCAT(persona2.nombres,' ',persona2.apellidos) as propietario , tipo.[icono] , tipo.[color] 
						, (SELECT COUNT(*) FROM mi_nube_archivousuario ur where  ur.archivo_id = archivo.id AND ur.usuario_id <> """+str(usuario)+""" ) as compartido
								,[dbo].[mi_nube_crear_navegacion](archivo.id, tipo.id) as navegacion 
								FROM [dbo].[mi_nube_archivo] as archivo 
								INNER JOIN  [dbo].[mi_nube_archivousuario]  permiso ON archivo.[id]=permiso.[archivo_id] 
								INNER JOIN [dbo].[usuario_usuario] usuario ON usuario.id = archivo.usuarioModificado_id 
								INNER JOIN [dbo].[usuario_persona] persona ON persona.id = usuario.persona_id 
								INNER JOIN [dbo].[tipo_tipo] tipo ON tipo.id = archivo.tipoArchivo_id 
								INNER JOIN [dbo].[usuario_usuario] usuario2 ON usuario2.id = archivo.propietario_id 
								INNER JOIN [dbo].[usuario_persona] persona2 ON persona2.id = usuario2.persona_id 
								WHERE  archivo.[id]>1 AND permiso.[usuario_id] = """+str(usuario)+""+string)

			lista = []
			for obj in queryset:
				lista.append({ 'id': obj.id , 'nombre': obj.nombre ,'padre':obj.padre ,'destino' : settings.MEDIA_URL+obj.destino  , 'tipoArchivo_id' : obj.tipoArchivo_id , 'propietario_id' : obj.propietario_id , 'eliminado' : obj.eliminado , 'peso' : obj.peso , 'usuarioModificado' : obj.usuarioModifico , 'fechaModificado' : obj.fechaModificado , 'tipoArchivo' : obj.tipoArchivo , 'propietario' : obj.propietario , 'icono' : obj.icono , 'color' : obj.color , 'compartido' : obj.compartido, 'navegacion':'Inicio/'+obj.navegacion }) 
			return JsonResponse({'message':'','success':'ok','data':list(lista)})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def listUsuarioSinArchivo(request):
	if request.method == 'GET':
		#api rest usuarios que no estan asociado a la lista de archivos
		try:
			dato = request.GET['dato'] if 'dato' in request.GET else None;
			empresa = request.GET['empresa'] if 'empresa' in request.GET else None;
			myList = request.GET['archivo'].split(',')
			queryset2 = ArchivoUsuario.objects.filter(archivo_id__in = myList).values( 'usuario_id')
			queryset = Usuario.objects.filter(user__is_active=True).values( 'id' , 'persona__nombres' , 'persona__apellidos' , 'user__username' , 'empresa__nombre').exclude(pk__in = queryset2)	
			
			if empresa:
				queryset = queryset.filter(empresa_id = empresa)
			else:
				empresaActual = request.user.usuario.empresa.id
				# empresas que puede ver la empresa actual
				empresas_puede_ver = EmpresaAcceso.objects.filter(empresa_id = empresaActual).values_list("empresa_ver_id")
				queryset = queryset.filter(empresa_id__in = empresas_puede_ver)

			if dato :
				queryset = queryset.filter(Q( user__username__icontains = dato )  
										 | Q( persona__nombres__icontains = dato )  
										 | Q( persona__apellidos__icontains = dato ) )

			return JsonResponse({'message':'','success':'ok','data': list(queryset) })			
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def listUsuarioConArchivo(request):
	if request.method == 'GET':
		#api rest usuarios que estan asociados a la lista de archivos
		try:
			dato = request.GET['dato'] if 'dato' in request.GET else None;
			empresa = request.GET['empresa'] if 'empresa' in request.GET else None;
			myList = request.GET['archivo'].split(',')
			queryset3 = Archivo.objects.filter(id__in = myList).values('propietario_id')
			queryset = ArchivoUsuario.objects.filter(archivo_id__in = myList, usuario__user__is_active=True).exclude(usuario_id__in = queryset3).values( 'id' , 'usuario_id' , 'usuario__persona__nombres' , 'usuario__persona__apellidos' , 'usuario__user__username' , 'usuario__empresa__nombre' , 'escritura')
			if empresa :
				queryset = queryset.filter(usuario__empresa_id = empresa)
			if dato :
				queryset = queryset.filter( Q( usuario__user__username__icontains = dato)
										 | Q(usuario__persona__nombres__icontains = dato)
										 | Q(usuario__persona__apellidos__icontains = dato) )

			return JsonResponse({'message':'','success':'ok','data':list(queryset)})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
@api_view(['POST'])
def createUsuarioConArchivo(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myListArchivos = respuesta['archivo']
			myListUsuarios = respuesta['usuario']
			# print myListUsuarios
			insert_list = []
			for i in myListUsuarios:				
				for j in myListArchivos:
					hijos = Archivo.objects.raw('with query (id,nombre,padre) as ( SELECT id, nombre,padre FROM mi_nube_archivo WHERE id='+str(j)+' UNION ALL SELECT a.id,a.nombre,a.padre FROM mi_nube_archivo a INNER JOIN query cte ON a.padre = cte.id ) select id,nombre,padre from query')
					for k in hijos:
						validaArchivo = ArchivoUsuario.objects.filter(usuario_id = i['id'] , archivo_id = k.id)
						if validaArchivo.count()==0:
							a = ArchivoUsuario(usuario_id = i['id'] , archivo_id = k.id , escritura = i['escritura'] ) 
							a.save()
							# SE GUARDA LA TRANSACCION DEL USUARIO QUE SE LE ASIGNA
					insert_list.append(Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='mi_nube.ArchivoUsuario',id_manipulado=j))

			Logs.objects.bulk_create(insert_list)
			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro ha sido guardado exitosamente.','success':'ok','data': '' })
		except Exception as e:
			print(e)
			functions.toLog(e,'mi_nube.createUsuarioConArchivo')
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin api rest asociar usuarios de la lista de archivos

@transaction.atomic
@api_view(['DELETE'])
def destroyUsuarioConArchivo(request):
	if request.method == 'DELETE':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myListArchivos = respuesta['archivo']
			myListUsuarios = respuesta['usuario']

			listaUpdateEscritura = respuesta['listaUpdate'] if 'listaUpdate' in respuesta else [];

			for i in myListUsuarios:
				for j in myListArchivos:
					hijos = Archivo.objects.raw('with query (id,nombre,padre) as ( SELECT id, nombre,padre FROM mi_nube_archivo WHERE id='+str(j)+' UNION ALL SELECT a.id,a.nombre,a.padre FROM mi_nube_archivo a INNER JOIN query cte ON a.padre = cte.id ) select id,nombre,padre from query')
					for k in hijos:
						a = ArchivoUsuario.objects.get(usuario_id = i , archivo_id = k.id)
						# SE GUARDA LA TRANSACCION DEL USUARIO QUE ELIMINA EL PERMISO DEL USUARIO
						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='mi_nube.ArchivoUsuario',id_manipulado=a.id)
						logs_model.save()
						a.delete()

			for i in listaUpdateEscritura:
				for j in myListArchivos:
					hijos = Archivo.objects.raw('with query (id,nombre,padre) as ( SELECT id, nombre,padre FROM mi_nube_archivo WHERE id='+str(j)+' UNION ALL SELECT a.id,a.nombre,a.padre FROM mi_nube_archivo a INNER JOIN query cte ON a.padre = cte.id ) select id,nombre,padre from query')
				
					for k in hijos:						
						archivoUpdate=ArchivoUsuario.objects.get(usuario_id = i['id'] , archivo_id = k.id)
						archivoUpdate.escritura = i['escritura']
						archivoUpdate.save()
						# print str(i['id'])+"---"+str(k.id)
						# SE GUARDA LA TRANSACCION DEL USUARIO QUE ACTUALIZA EL PERMISO DEL USUARIO
						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='mi_nube.ArchivoUsuario',id_manipulado=archivoUpdate.id)
						logs_model.save()

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'Los registros se han actualizado correctamente.','success':'ok','data': '' })	

		except Exception as e:
			print(e)
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin api rest quitar usuarios de la lista de archivos

def get_ruta(archivoId):
	
	ruta = ''
	sep=''
	padre = Archivo.objects.filter(id=archivoId).values('id','padre','nombre')
	if padre:
		while padre[0]['id'] != 1:
			if padre[0]['id'] != archivoId:
				ruta = padre[0]['nombre'] + sep + ruta
				sep = '/'
			padre = Archivo.objects.filter(id=padre[0]['padre']).values('id','padre','nombre')
	#import pdb; pdb.set_trace()
	return ruta

##### DOWNLOAD FILE
@login_required
def downloadFile(request):
	if request.method == 'GET':
		
		try:
			t = datetime.datetime.now()
			myListArchivos = request.GET['archivo']

			myListArchivos = myListArchivos.split(',')
			# myListArchivos = [69,70,71]
			# Files (local path) to put in the .zip
			# FIXME: Change this (get paths from DB etc)

			nombreArchivo = str(t.year)+str(t.month)+str(t.day)+str(t.hour)+str(t.minute)+str(t.second)		
			newpath = r'media/mi_nube/descargas/'+str(nombreArchivo)+"/"
			
			if not os.path.exists(newpath):
				os.makedirs(newpath)

			carpetaNoExiste = ''
			reemplazar_por = ''

			for i in myListArchivos:
				
				hijos = Archivo.objects.raw('with query (id,nombre,padre,tipoArchivo_id,destino,eliminado) as ( SELECT id, nombre,padre,tipoArchivo_id,destino,eliminado FROM mi_nube_archivo WHERE id='+str(i)+' UNION ALL SELECT a.id,a.nombre,a.padre,a.tipoArchivo_id,a.destino,a.eliminado FROM mi_nube_archivo a INNER JOIN query cte ON a.padre = cte.id ) select id,nombre,padre,tipoArchivo_id,destino,eliminado from query')
				for k in hijos:
					if k.eliminado == False:
						#INVOCAR FUNCION PARA TRAER LA RUTA:
						#ruta = Archivo.objects.raw("with query_2 as ( SELECT id, nombre,padre,destino,tipoArchivo_id,eliminado FROM mi_nube_archivo WHERE id="+str(k.id)+" UNION ALL SELECT a.id,a.nombre,a.padre,a.destino,a.tipoArchivo_id,a.eliminado FROM mi_nube_archivo a INNER JOIN query_2 cte2 ON a.id = cte2.padre WHERE a.id<>1 )  SELECT  (SELECT id FROM mi_nube_archivo WHERE id="+str(k.id)+") as id , stuff(( select CASE WHEN  tipoArchivo_id="+str(tipoCarpeta)+" THEN '/' + nombre ELSE '' END  from query_2 as p2 WHERE id <> "+str(k.id)+" order by id asc for xml path('') ), 1, 1, '') as destino ") 
						ruta = get_ruta(k.id)
						#if ruta[0].eliminado == False:
						if ruta != '':
							#newCarpeta = ruta[0].destino
							newCarpeta = ruta
							rutaArchivo = ''
							if k.tipoArchivo_id==tipoCarpeta:
								rutaCarpeta = (str(newpath)+str(newCarpeta)).replace(carpetaNoExiste, reemplazar_por)+"/"
								if not os.path.exists(rutaCarpeta):
									carpetaNoExiste = carpetaNoExiste +"/"+str(newCarpeta)
									os.makedirs(newpath+str(k.nombre))
								else:	
									os.makedirs(rutaCarpeta+str(k.nombre))
							else:						
								filename = ""+str(k.destino)+""
								extension = filename[filename.rfind('.'):]
								rutaArchivo = (newpath+str(newCarpeta)).replace(carpetaNoExiste, reemplazar_por)+"/"

								if not os.path.exists(rutaArchivo):
									functions.descargarArchivoS3(str(k.destino), str(newpath)+"/" ,k.nombre+extension )				
								else:
									functions.descargarArchivoS3(str(k.destino), str(rutaArchivo) ,k.nombre+extension )				
				
			# Folder name in ZIP archive which contains the above files
			# E.g [thearchive.zip]/somefiles/file2.txt
			# FIXME: Set this to something better
			zip_subdir = nombreArchivo
			zip_filename = "%s.zip" % zip_subdir

			# Open StringIO to grab in-memory ZIP contents
			s = StringIO.StringIO()

			# The zip compressor
			zf = zipfile.ZipFile(s, "w")			

			# zf.write("media/mi_nube/descargas/prueba.txt")
			buscar = 'media/mi_nube/descargas/'
			
			for dirname, subdirs, files in os.walk(newpath):
				zf.write(dirname, dirname.replace(buscar, reemplazar_por) )
				for filename in files:
					zf.write(os.path.join(dirname, filename) , os.path.join(dirname, filename).replace(buscar, reemplazar_por))

			# Must close zip for all contents to be written
			zf.close()
			# Grab ZIP file from in-memory, make response with correct MIME-type
			resp = HttpResponse(s.getvalue(), content_type="application/zip")
			# # ..and correct content-disposition
			resp['Content-Disposition'] = 'attachment; filename='+str(nombreArchivo)+'.zip'

			return resp

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

##### DOWNLOAD FILE
@login_required
def descargarUnArchivo(request):
	if request.method == 'GET':
		try:
			
			archivo = Archivo.objects.get(pk=request.GET['archivo'])
			
			filename = ""+str(archivo.destino)+""
			extension = filename[filename.rfind('.'):]
			f = re.sub('[^A-Za-z0-9 ]+', '', archivo.nombre)
			return functions.exportarArchivoS3(str(archivo.destino),  f + extension)

		except Exception as e:
			functions.toLog(e,'mi_nube.descargarUnArchivo')
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

##### PROYECTOS Y CONTRATOS ASOCIADOS A ARCHIVOS
def listProyectosSinArchivo(request):
	if request.method == 'GET':
		#api rest usuarios que no estan asociado a la lista de archivos
		try:
			
			dato = request.GET['dato'] if 'dato' in request.GET else None;
			mcontrato = request.GET['mcontrato'] if 'mcontrato' in request.GET else None;
			departamento = request.GET['departamento'] if 'departamento' in request.GET else None;
			municipio = request.GET['municipio'] if 'municipio' in request.GET else None;
			
			usuarioActual = request.GET['usuario'] if 'usuario' in request.GET else request.user.usuario.id
			empresaActual = request.GET['empresa'] if 'empresa' in request.GET else request.user.usuario.empresa.id

			qset = ( Q(empresa_id = empresaActual ) )

			if dato:
				qset = qset & ( Q(proyecto__nombre__icontains = dato ) )

			if mcontrato:
				qset = qset & ( Q(proyecto__mcontrato_id = mcontrato ) )

			if departamento:
				qset = qset & ( Q(proyecto__municipio__departamento_id = departamento ) )

			if municipio:		
				qset = qset & ( Q(proyecto__municipio_id = municipio ) )

			listaArchivo = request.GET['archivo'].split(',')
			a = Archivo.objects.filter(id__in = listaArchivo)
			lista = []
			for i in a:
				proyectos = i.proyecto.all().values('id')
				if proyectos:
					for j in proyectos:
						lista.append(j['id'])
				else:
					lista = []
					break

			queryset2 = Proyecto_empresas.objects.filter(qset).exclude(proyecto_id__in = lista).values( 'proyecto__id' , 'proyecto__nombre' , 'proyecto__mcontrato__nombre' , 'proyecto__municipio__nombre' , 'proyecto__municipio__departamento__nombre')
			return JsonResponse({'message':'','success':'ok','data': list(queryset2) })			
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def listProyectosConArchivo(request):
	if request.method == 'GET':
		#api rest usuarios que estan asociados a la lista de archivos
		try:
			listaArchivo = request.GET['archivo'].split(',')
			dato = request.GET['dato'] if 'dato' in request.GET else None;

			a = Archivo.objects.filter(id__in = listaArchivo)
			lista = []
			for i in a:
				proyectos = i.proyecto.all().values('id')
				if proyectos:
					for j in proyectos:
						lista.append(j['id'])
				else:
					lista = []
					break

			qset = ( Q(id__in = lista ) )

			if dato:
				qset = qset & ( Q(nombre__icontains = dato ) )

			queryset = Proyecto.objects.filter(qset).values( 'id' , 'nombre' , 'mcontrato__nombre' , 'municipio__nombre' , 'municipio__departamento__nombre')
			
			return JsonResponse({'message':'','success':'ok','data':list(queryset)})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def listContratosSinArchivo(request):
	if request.method == 'GET':
		#api rest usuarios que no estan asociado a la lista de archivos
		try:
			listaArchivo = request.GET['archivo'].split(',')

			# administrador de recursos 
			tipoContrato = 12

			dato = request.GET['dato'] if 'dato' in request.GET else None;
			estado = request.GET['estado'] if 'estado' in request.GET else None;

			a = Archivo.objects.filter(id__in =  listaArchivo)
			lista = []
			for i in a:
				contratos = i.contrato.all().values('id')
				for j in contratos:
					lista.append(j['id'])

			qset = None

			if estado is not None and qset is not None:
				qset = qset & (Q(estado_id = estado))
			elif estado:
				qset = (Q(estado_id = estado))


			if (dato is not None and qset is not None):
				qset = qset & (Q(nombre__icontains = dato) | Q(numero__icontains = dato))
			elif dato:
				qset = (Q(nombre__icontains = dato) | Q(numero__icontains = dato))

			if (tipoContrato is not None and qset is not None):
				qset = qset & (Q(tipo_contrato_id = tipoContrato) )
			elif tipoContrato:
				qset = (Q(tipo_contrato_id = tipoContrato) )	

			if qset:
				queryset2 = Contrato.objects.filter(qset).exclude(pk__in = lista ).values('id' , 'nombre' , 'numero' , 'tipo_contrato__nombre' , 'estado__nombre')	
			else:
				queryset2 = Contrato.objects.all().exclude(pk__in = lista ).values('id' , 'nombre' , 'numero' , 'tipo_contrato__nombre' , 'estado__nombre')	

			return JsonResponse({'message':'','success':'ok','data': list(queryset2) })			
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def listContratosConArchivo(request):
	if request.method == 'GET':
		#api rest contratos que estan asociados a una lista de archivos
		try:
			listaArchivo = request.GET['archivo'].split(',')
			a = Archivo.objects.filter(id__in =  listaArchivo)
			lista = []
			for i in a:
				contratos = i.contrato.all().values('id')
				for j in contratos:
					lista.append(j['id'])
			queryset = Contrato.objects.filter(pk__in = lista).values( 'id' , 'nombre' , 'numero' , 'tipo_contrato__nombre' , 'estado__nombre')
			return JsonResponse({'message':'','success':'ok','data':list(queryset)})	

		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#API PARA ASOCIAR PROYECTOS A UN ARCHIVO 
@transaction.atomic
@api_view(['POST'])
def createProyectoConArchivo(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myListArchivos = respuesta['archivo']
			myListProyectos = respuesta['proyecto']

			if myListArchivos and myListProyectos:
				insert_list = []
				for i in myListArchivos:
					hijos = Archivo.objects.raw('with query (id,nombre,padre) as ( SELECT id, nombre,padre FROM mi_nube_archivo WHERE id='+str(i)+' UNION ALL SELECT a.id,a.nombre,a.padre FROM mi_nube_archivo a INNER JOIN query cte ON a.padre = cte.id ) select id,nombre,padre from query')
					for k in hijos:
						a = Archivo.objects.get(pk=k.id)
						a.proyecto.add(*myListProyectos)

						cc= a.proyecto.through.objects.filter(proyecto_id__in = myListProyectos)

						insert_list = []
						for i in cc:
							insert_list.append(Logs(usuario_id=request.user.usuario.id
													,accion=Acciones.accion_crear
													,nombre_modelo='mi_nube.Archivo.proyecto'
													,id_manipulado=i.id)
													)
					
						Logs.objects.bulk_create(insert_list)

				transaction.savepoint_commit(sid)
				return JsonResponse({'message':'El registro ha sido guardado exitosamente.','success':'ok','data': '' })
			else:
				return JsonResponse({'message':'No se recibierón los datos requeridos.','success':'fail','data': '' })
			
		except Exception as e:
			print(e)
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin api rest asociar proyectos de la lista de archivos

# API PARA ASOCIAR CONTRATOS A UN ARCHIVO
@transaction.atomic
@api_view(['POST'])
def createContratoConArchivo(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myListArchivos = respuesta['archivo']
			myListContratos = respuesta['contrato']

			insert_list = []
			for i in myListArchivos:
				hijos = Archivo.objects.raw('with query (id,nombre,padre) as ( SELECT id, nombre,padre FROM mi_nube_archivo WHERE id='+str(i)+' UNION ALL SELECT a.id,a.nombre,a.padre FROM mi_nube_archivo a INNER JOIN query cte ON a.padre = cte.id ) select id,nombre,padre from query')
				for k in hijos:
					a = Archivo.objects.get(pk=k.id)
					a.contrato.add(*myListContratos)

					cc= a.contrato.through.objects.filter(contrato_id__in = myListContratos)

					insert_list = []
					for i in cc:
						insert_list.append(Logs(usuario_id=request.user.usuario.id
												,accion=Acciones.accion_crear
												,nombre_modelo='mi_nube.Archivo.contrato'
												,id_manipulado=i.id)
												)
				
					Logs.objects.bulk_create(insert_list)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro ha sido guardado exitosamente.','success':'ok','data': '' })
		except Exception as e:
			print(e)
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin api rest asociar contrato de la lista de archivos

# API PARA DESASOCIAR PROYECTOS A UN ARCHIVO
@transaction.atomic
@api_view(['DELETE'])
def destroyProyectoConArchivo(request):
	if request.method == 'DELETE':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myListArchivos = respuesta['archivo']
			myListProyectos = respuesta['proyecto']

			insert_list = []
			for i in myListArchivos:
				hijos = Archivo.objects.raw('with query (id,nombre,padre) as ( SELECT id, nombre,padre FROM mi_nube_archivo WHERE id='+str(i)+' UNION ALL SELECT a.id,a.nombre,a.padre FROM mi_nube_archivo a INNER JOIN query cte ON a.padre = cte.id ) select id,nombre,padre from query')
				for k in hijos:
					a = Archivo.objects.get(pk=k.id)

					cc= a.proyecto.through.objects.filter(proyecto_id__in = myListProyectos)

					insert_list = []
					for i in cc:
						insert_list.append(Logs(usuario_id=request.user.usuario.id
												,accion=Acciones.accion_borrar
												,nombre_modelo='mi_nube.Archivo.proyecto'
												,id_manipulado=i.id)
												)
				
					Logs.objects.bulk_create(insert_list)
					a.proyecto.remove(*myListProyectos)

			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha eliminado correctamente.','success':'ok','data': '' })	

		except Exception as e:
			print(e)
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin api rest quitar proyectos de la lista de archivos

# API PARA DESASOCIAR CONTRATOS A UN ARCHIVO
@transaction.atomic
@api_view(['DELETE'])
def destroyContratoConArchivo(request):
	if request.method == 'DELETE':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)
			myListArchivos = respuesta['archivo']
			myListContratos = respuesta['contrato']

			insert_list = []
			for i in myListArchivos:
				hijos = Archivo.objects.raw('with query (id,nombre,padre) as ( SELECT id, nombre,padre FROM mi_nube_archivo WHERE id='+str(i)+' UNION ALL SELECT a.id,a.nombre,a.padre FROM mi_nube_archivo a INNER JOIN query cte ON a.padre = cte.id ) select id,nombre,padre from query')
				for k in hijos:
					a = Archivo.objects.get(pk=k.id)

					cc= a.contrato.through.objects.filter(contrato_id__in = myListContratos)

					insert_list = []
					for i in cc:
						insert_list.append(Logs(usuario_id=request.user.usuario.id
												,accion=Acciones.accion_borrar
												,nombre_modelo='mi_nube.Archivo.contrato'
												,id_manipulado=i.id)
												)
				
					Logs.objects.bulk_create(insert_list)
					a.contrato.remove(*myListContratos)
					
			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El registro se ha eliminado correctamente.','success':'ok','data': '' })	

		except Exception as e:
			print(e)
			transaction.savepoint_rollback(sid)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Fin api rest quitar contratos de la lista de archivos

#Api rest para ArchivoUsuario
class ArchivoUsuarioSerializer(serializers.HyperlinkedModelSerializer):

	archivo = ArchivoSerializer(read_only = True)
	usuario = UsuarioLiteSerializer(read_only = True)

	class Meta:
		model = ArchivoUsuario
		fields=('id' , 'usuario' , 'archivo' , 'escritura')

class ArchivoUsuarioViewSet(viewsets.ModelViewSet):
	"""
	Retorna una lista de usuarios asociados a un archivo,
	<br>puede utilizar el parametro (dato) a traves del cual puede consultar todos los registros.
	<br>puede utilizar el parametro (usuario) a traves del cual puede filtrar consulta por usuarios que tengan permiso de lectura a un archivo.
	<br>puede utilizar el parametro (archivo) a traves del cual puede filtrar la consulta por archivo.
	<br>puede utilizar el parametro (escritura) (escritura = 0 o escritura = 1) a traves del cual puede filtrar la consulta que tengan o no tengan permiso de escritura.
	"""
	model=ArchivoUsuario
	queryset = model.objects.all()
	serializer_class = ArchivoUsuarioSerializer

	def retrieve(self,request,*args, **kwargs):
		try:
			instance = self.get_object()
			serializer = self.get_serializer(instance)
			return Response({'message':'','status':'success','data':serializer.data})
		except Exception as e:
			return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	def list(self, request, *args, **kwargs):
		try:
			queryset = super(ArchivoUsuarioViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			usuario = self.request.query_params.get('usuario', None)
			archivo = self.request.query_params.get('archivo', None)
			escritura = self.request.query_params.get('escritura', None)

			qset=(~Q(id=0))

			if (dato or usuario or archivo or escritura):
				if dato:
					qset = qset & ( Q(archivo__nombre__icontains=dato) )
				if usuario:
					qset = qset & ( Q(usuario_id = usuario) )
				if archivo:
					qset = qset & ( Q(archivo_id = archivo) )
				if escritura:
					qset = qset & ( Q(escritura = escritura) )

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
				serializer = ArchivoUsuarioSerializer(data=request.DATA,context={'request': request})
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
				serializer = ArchivoUsuarioSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
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
#Fin api rest para ArchivoUsuario

# Create your views here.
@login_required
def miNube(request):
	return render(request, 'mi_nube/miNube.html',{'model':'archivo','app':'mi_nube'})


def subirAsyncArchivos(request):
	
	if request.method == 'POST':
		archivos = request.FILES.getlist("archivos[]")
		
		empresa = str(request.user.usuario.empresa.id)
		usuario = str(request.user.usuario.id)
		res = subirArchivoAsync.delay(archivos,empresa,usuario)

		# print 'luis mendoza'+res.task_id
		# print 'nombre tarea'+res.task_name
		# print res.task_status
		# print res
		# try:
		# 	result = AsyncResult(res.task_id)
		# 	time.sleep(100)
		# 	print 'resultado'+str(result.status)
		# 	print 'resultado'+str(result.result)
		# 	if result.ready():
		# 		print 'mendoza'
		# 	else:
		# 		print 'hernandez'
		# except Exception as e:
		# 	print(e)
		

		# if result.ready():
		# 	print "Task has run"
		# 	if result.successful():
		# 		print "Result was: %s" % result.result
		# 	else:
		# 		if isinstance(result.result, Exception):
		# 			print "Task failed due to raising an exception"
		# 			raise result.result
		# 		else:
		# 			print "Task failed without raising exception"
		# else:
		# 	print "Task has not yet run"

		return JsonResponse({'message':'El archivo  esta siendo cargado.'+str(res),'success':'ok','data': '' })

def verificaTareaArchivo(request):
	tarea_id = request.GET['id_tarea']
	result = AsyncResult(tarea_id)

	# print 'ESTADO = '+str(result.status)
	# print 'RESULTADO = '+str(result.result)
	# if result.ready():
	# 	print 'mendoza'
	# else:
	# 	print 'hernandez'
	return JsonResponse({'message':'El archivo  esta siendo cargado.','success':'ok','data': '' })


def validaTipoArchivo(extension):

	tipo = 0
	# DOCUMENTOS DE WORD
	if extension=='doc' or extension=='docx':
		tipo=59
	#ARCHIVOS DE EXCEL
	elif extension=='xls' or extension=='xlsx' or extension=='xlsb' or extension=='xlsm':
		tipo=60
	#ARCHIVOS DE POWER POINT
	elif extension=='pptx' or extension=='pps' or extension=="pot" or extension=="pptm" or extension=="potx" or extension=="ppsx" :
		tipo=61
	#ARCHIVOS COMPRIMIDOS
	elif extension=='zip':
		tipo=62
	#pdf
	elif extension=='pdf':
		tipo=63
	#ARCHIVOS DE IMAGEN
	elif extension=='jpeg' or extension=='jpg' or extension=='png':
		tipo=64
	#ARCHIVOS DE VIDEO
	elif extension=="avi" or extension=="mpeg" or extension=="wmv":
		tipo=65
	#ARCHIVOS DE MUSICA
	elif extension=="mp3" or extension=="mp4" or extension=="wma" or extension=="wav":
		tipo=66
	#AUTOCAD
	elif extension=='dwg':
		tipo=67
	#ARCHIVOS DE TEXTOS
	elif extension=='txt':
		tipo=69
	else:
	# LISTA PERMITIDA ARCHIVOS GENERICOS
		listaPermitida=["iso"]
		if extension in listaPermitida:
			tipo=68 

	return tipo

#MOVER ARCHIVO A OTRA CARPETA
@transaction.atomic
def moveFile(request):
	if request.method == 'POST':
		sid = transaction.savepoint()
		try:
			lista=request.POST['_content']
			respuesta= json.loads(lista)

			padre_id = respuesta['padre_id'] if 'padre_id' in respuesta else 0;
			archivo_id = respuesta['archivo_id'] if 'archivo_id' in respuesta else 0;
			usuario = respuesta['usuario'] if 'usuario' in respuesta else 0;
			
			archivo = Archivo.objects.get(pk = archivo_id)
			archivo.padre = padre_id
			archivo.save()
			transaction.savepoint_commit(sid)
			return JsonResponse({'message':'El (archivo ó carpeta) ha sido actualizado exitosamente','success':'ok','data': '' })
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# LISTA DE CARPETA CONTRATO Y PROYECTO
def listFolderContratoProyecto(request):
	if request.method == 'GET':
		try:
			mcontrato_id = request.GET['mcontrato'] if 'mcontrato' in request.GET else 0;
			proyecto_id = request.GET['proyecto'] if 'proyecto' in request.GET else 0;

			queryset = Archivo.objects.raw("""select a.id , a.nombre , a.padre
													, (select count(*) 
															from mi_nube_archivo_proyecto pa2 
															INNER JOIN mi_nube_archivo a2  on a2.id=pa2.archivo_id 
															where pa2.archivo_id=a.padre AND pa2.proyecto_id="""+str(proyecto_id)+""") as valida 
												FROM mi_nube_archivo_proyecto pa 
												INNER JOIN mi_nube_archivo a  ON a.id=pa.archivo_id 
												where pa.proyecto_id="""+str(proyecto_id)+" AND a.tipoArchivo_id="+str(tipoCarpeta)) 
			lista = []
			lista.append({'id':1 , 'text': 'Inicio' , 'parent' : '#'})
			for obj in queryset:
				if int(obj.valida)== 0:
					lista.append({ 'id': obj.id , 'text': obj.nombre ,'parent': 1 }) 
				else:	
					lista.append({ 'id': obj.id , 'text': obj.nombre ,'parent':obj.padre }) 
			return JsonResponse({'message':'','success':'ok','data':list(lista) })	
		except Exception as e:
			print(e)
			raise e

# LISTA FILE  DE CONTRATOO Y PROYECTO
def listFileContratoProyecto(request):
	if request.method == 'GET':
		try:

			tipo_contrato = tipoC()

			dato = request.GET['dato'] if 'dato' in request.GET else None;
			padre = request.GET['padre'] if 'padre' in request.GET else 0;
			mcontrato_id = request.GET['mcontrato'] if 'mcontrato' in request.GET else None;
			proyecto_id = request.GET['proyecto'] if 'proyecto' in request.GET else None;
			usuario_id = request.GET['usuario'] if 'usuario' in request.GET else None;

			string = ''
			stringP= ''
			stringC= ''

			if dato:			
				string = "  AND a.nombre like '%"+str(dato)+"%' "

			if usuario_id:
				u = Usuario.objects.get(pk = usuario_id)
				empresaIdActual = u.empresa.id
				
				if mcontrato_id is None or mcontrato_id=="":
					
					stringC = stringC+"""  AND c.contrato_id in (
						SELECT c.id 
							FROM contrato c
							INNER JOIN contrato_empresa emp_c ON emp_c.contrato_id = c.id
							WHERE emp_c.empresa_id = """+str(empresaIdActual)+""" and c.tipo_contrato_id = """+str(tipo_contrato.m_contrato)+"""
					)"""

				if proyecto_id is None or proyecto_id=="":
					
					stringP = stringP+"""  AND p.proyecto_id in (
							(SELECT p.id 
							FROM proyecto_proyecto p
							INNER JOIN proyecto_proyecto_empresas emp_p ON emp_p.proyecto_id = p.id
							WHERE emp_p.empresa_id = """+str(empresaIdActual)+"""  )

					)"""

			if mcontrato_id:			
				stringC = stringC+"  AND c.contrato_id ="+str(mcontrato_id)

			if proyecto_id:			
				stringP = stringP+"  AND p.proyecto_id ="+str(proyecto_id)

			if int(padre)==1:
				queryset = ArchivoUsuario.objects.raw("""WITH query (id,nombre,padre,destino,tipoArchivo_id,propietario_id,eliminado,peso,usuarioModifico,fechaModificado,tipoArchivo,propietario,icono,color,compartido ) as 
								(SELECT a.id, a.nombre , a.padre , a.destino , a.tipoArchivo_id , a.propietario_id , a.eliminado, a.peso,CONCAT(persona.nombres,' ',persona.apellidos) as usuarioModifico,CONVERT(VARCHAR(20), a.[fechaModificado], 0) as fechaModificado , tipo.[nombre] as tipoArchivo , CONCAT(persona2.nombres,' ',persona2.apellidos) as propietario , tipo.[icono] , tipo.[color]
										,CASE 
											WHEN  (select COUNT(*) from mi_nube_archivousuario au where au.archivo_id = a.id)>1 THEN 1 
											ELSE 0 
										END as compartido 
								FROM mi_nube_archivo a 	
								INNER JOIN mi_nube_archivo_contrato c ON c.archivo_id = a.id 
								INNER JOIN [dbo].[usuario_usuario] usuario ON usuario.id = a.usuarioModificado_id 
								INNER JOIN [dbo].[usuario_persona] persona ON persona.id = usuario.persona_id  
								INNER JOIN [dbo].[tipo_tipo] tipo ON tipo.id = a.tipoArchivo_id 
								INNER JOIN [dbo].[usuario_usuario] usuario2 ON usuario2.id = a.propietario_id 
								INNER JOIN [dbo].[usuario_persona] persona2 ON persona2.id = usuario2.persona_id 
								WHERE a.eliminado = 0 """+str(string)+str(stringC)+""" 
								UNION ALL  
								SELECT a.id , a.nombre , a.padre ,a.destino , a.tipoArchivo_id , a.propietario_id , a.eliminado ,a.peso,CONCAT(persona.nombres,' ',persona.apellidos) as usuarioModifico,CONVERT(VARCHAR(20), a.[fechaModificado], 0) as fechaModificado , tipo.[nombre] as tipoArchivo , CONCAT(persona2.nombres,' ',persona2.apellidos) as propietario , tipo.[icono] , tipo.[color]
								,CASE 
									WHEN  (select COUNT(*) from mi_nube_archivousuario au where au.archivo_id = a.id)>1 THEN 1  
									ELSE 0  
								END as compartido 
								FROM mi_nube_archivo a 	
								INNER JOIN mi_nube_archivo_proyecto p ON p.archivo_id = a.id 
								INNER JOIN [dbo].[usuario_usuario] usuario ON usuario.id = a.usuarioModificado_id 
								INNER JOIN [dbo].[usuario_persona] persona ON persona.id = usuario.persona_id 
								INNER JOIN [dbo].[tipo_tipo] tipo ON tipo.id = a.tipoArchivo_id 
								INNER JOIN [dbo].[usuario_usuario] usuario2 ON usuario2.id = a.propietario_id 
								INNER JOIN [dbo].[usuario_persona] persona2 ON persona2.id = usuario2.persona_id 
								WHERE a.eliminado = 0  """+str(string)+str(stringP)+""" ) 
								select DISTINCT * from query q WHERE padre not in (SELECT id FROM query) """)			
			elif int(padre)>1:
				string = str(string) + " AND a.padre ="+str(padre)
				queryset = ArchivoUsuario.objects.raw("WITH query (id,nombre,padre,destino,tipoArchivo_id,propietario_id,eliminado,peso,usuarioModifico,fechaModificado,tipoArchivo,propietario,icono,color,compartido ) as (SELECT a.id, a.nombre , a.padre , a.destino , a.tipoArchivo_id , a.propietario_id , a.eliminado, a.peso,CONCAT(persona.nombres,' ',persona.apellidos) as usuarioModifico,CONVERT(VARCHAR(20), a.[fechaModificado], 0) as fechaModificado , tipo.[nombre] as tipoArchivo , CONCAT(persona2.nombres,' ',persona2.apellidos) as propietario , tipo.[icono] , tipo.[color],CASE WHEN  (select COUNT(*) from mi_nube_archivousuario au where au.archivo_id = a.id)>1 THEN 1 ELSE 0 END as compartido FROM mi_nube_archivo a 	INNER JOIN mi_nube_archivo_contrato c ON c.archivo_id = a.id INNER JOIN [dbo].[usuario_usuario] usuario ON usuario.id = a.usuarioModificado_id INNER JOIN [dbo].[usuario_persona] persona ON persona.id = usuario.persona_id  INNER JOIN [dbo].[tipo_tipo] tipo ON tipo.id = a.tipoArchivo_id INNER JOIN [dbo].[usuario_usuario] usuario2 ON usuario2.id = a.propietario_id INNER JOIN [dbo].[usuario_persona] persona2 ON persona2.id = usuario2.persona_id WHERE a.eliminado = 0 "+str(string)+str(stringC)+" UNION ALL  SELECT a.id , a.nombre , a.padre ,a.destino , a.tipoArchivo_id , a.propietario_id , a.eliminado ,a.peso,CONCAT(persona.nombres,' ',persona.apellidos) as usuarioModifico,CONVERT(VARCHAR(20), a.[fechaModificado], 0) as fechaModificado , tipo.[nombre] as tipoArchivo , CONCAT(persona2.nombres,' ',persona2.apellidos) as propietario , tipo.[icono] , tipo.[color],CASE WHEN  (select COUNT(*) from mi_nube_archivousuario au where au.archivo_id = a.id)>1 THEN 1  ELSE 0  END as compartido FROM mi_nube_archivo a 	INNER JOIN mi_nube_archivo_proyecto p ON p.archivo_id = a.id INNER JOIN [dbo].[usuario_usuario] usuario ON usuario.id = a.usuarioModificado_id INNER JOIN [dbo].[usuario_persona] persona ON persona.id = usuario.persona_id INNER JOIN [dbo].[tipo_tipo] tipo ON tipo.id = a.tipoArchivo_id INNER JOIN [dbo].[usuario_usuario] usuario2 ON usuario2.id = a.propietario_id INNER JOIN [dbo].[usuario_persona] persona2 ON persona2.id = usuario2.persona_id WHERE a.eliminado = 0  "+str(string)+str(stringP)+" ) select DISTINCT * from query q")			

			elif int(padre)==0: 
				queryset = ArchivoUsuario.objects.raw("""
					WITH query (id,nombre,padre,destino,tipoArchivo_id,propietario_id,eliminado,peso,usuarioModifico,fechaModificado,tipoArchivo,propietario,icono,color,compartido ) as 
						(SELECT a.id, a.nombre , a.padre , a.destino , a.tipoArchivo_id , a.propietario_id , a.eliminado, a.peso,CONCAT(persona.nombres,' ',persona.apellidos) as usuarioModifico,CONVERT(VARCHAR(20), a.[fechaModificado], 0) as fechaModificado , tipo.[nombre] as tipoArchivo , CONCAT(persona2.nombres,' ',persona2.apellidos) as propietario , tipo.[icono] , tipo.[color]
						,CASE 
							WHEN  (select COUNT(*) from mi_nube_archivousuario au where au.archivo_id = a.id)>1 THEN 1 
							ELSE 0 
						END as compartido 
						FROM mi_nube_archivo a 	
						INNER JOIN mi_nube_archivo_contrato c ON c.archivo_id = a.id 
						INNER JOIN [dbo].[usuario_usuario] usuario ON usuario.id = a.usuarioModificado_id 
						INNER JOIN [dbo].[usuario_persona] persona ON persona.id = usuario.persona_id  
						INNER JOIN [dbo].[tipo_tipo] tipo ON tipo.id = a.tipoArchivo_id 
						INNER JOIN [dbo].[usuario_usuario] usuario2 ON usuario2.id = a.propietario_id 
						INNER JOIN [dbo].[usuario_persona] persona2 ON persona2.id = usuario2.persona_id 
						WHERE a.eliminado = 0 """+str(string)+str(stringC)+""" 
						UNION ALL  
						SELECT a.id , a.nombre , a.padre ,a.destino , a.tipoArchivo_id , a.propietario_id , a.eliminado ,a.peso,CONCAT(persona.nombres,' ',persona.apellidos) as usuarioModifico,CONVERT(VARCHAR(20), a.[fechaModificado], 0) as fechaModificado , tipo.[nombre] as tipoArchivo , CONCAT(persona2.nombres,' ',persona2.apellidos) as propietario , tipo.[icono] , tipo.[color]
						,CASE 
							WHEN  (select COUNT(*) from mi_nube_archivousuario au where au.archivo_id = a.id)>1 THEN 1  
							ELSE 0  
						END as compartido 
						FROM mi_nube_archivo a 	
						INNER JOIN mi_nube_archivo_proyecto p ON p.archivo_id = a.id 
						INNER JOIN [dbo].[usuario_usuario] usuario ON usuario.id = a.usuarioModificado_id 
						INNER JOIN [dbo].[usuario_persona] persona ON persona.id = usuario.persona_id 
						INNER JOIN [dbo].[tipo_tipo] tipo ON tipo.id = a.tipoArchivo_id 
						INNER JOIN [dbo].[usuario_usuario] usuario2 ON usuario2.id = a.propietario_id 
						INNER JOIN [dbo].[usuario_persona] persona2 ON persona2.id = usuario2.persona_id 
						WHERE a.eliminado = 0  """+str(string)+str(stringP)+""" ) 
						select DISTINCT * from query q""")			

			

			lista = []
			for obj in queryset:
				lista.append({ 'id': obj.id , 'nombre': obj.nombre ,'padre':obj.padre ,'destino' : settings.MEDIA_URL+obj.destino  , 'tipoArchivo_id' : obj.tipoArchivo_id , 'propietario_id' : obj.propietario_id , 'eliminado' : obj.eliminado , 'peso' : obj.peso , 'usuarioModificado' : obj.usuarioModifico , 'fechaModificado' : obj.fechaModificado , 'tipoArchivo' : obj.tipoArchivo , 'propietario' : obj.propietario , 'icono' : obj.icono , 'color' : obj.color , 'compartido' : obj.compartido }) 
			return JsonResponse({'message':'','success':'ok','data':list(lista) })
		except Exception as e:
			print(e)
			return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtenerCarpetasArbol(request):
	#lista todas las carpetas que puede ver un usuario para crear el arbol
	if request.method == 'GET':
		try:
			cursor = connection.cursor()
			usuarioActual = request.user.usuario.id

			# importante comentario si valida es igual a cero no tiene padre y se le asigna uno
			cursor.execute('select t.id, t.nombre, iif(t.valida=0, 1 , t.padre) as padre, t.propietario_id,t.valida, t.tipoArchivo_id,dbo.mi_nube_crear_navegacion(t.id,t.tipoArchivo_id) as navegacion, \
							(SELECT COUNT(*) FROM mi_nube_archivousuario ur where ur.archivo_id = t.id AND ur.usuario_id <> '+str(usuarioActual)+' ) as compartido \
							from (SELECT a.id,a.nombre,a.padre, a.propietario_id,a.tipoArchivo_id, \
							CASE WHEN ( (SELECT av.id FROM  mi_nube_archivo av   WHERE av.id=a.padre)=1) THEN 1 \
							WHEN(SELECT av.id FROM mi_nube_archivousuario uav inner join mi_nube_archivo av on uav.archivo_id=av.id  \
							WHERE av.id=a.padre AND uav.usuario_id='+str(usuarioActual)+') IS null THEN 0 else \
							(select av.id FROM mi_nube_archivousuario uav INNER JOIN mi_nube_archivo av on uav.archivo_id=av.id  \
							WHERE av.id=a.padre AND uav.usuario_id='+str(usuarioActual)+') END AS valida	\
							FROM mi_nube_archivousuario ua  INNER JOIN mi_nube_archivo a on ua.archivo_id =a.id \
							WHERE  ua.usuario_id ='+str(usuarioActual)+' AND a.tipoArchivo_id='+str(tipoCarpeta)+' AND a.eliminado=0) as t \
							ORDER BY t.tipoArchivo_id,t.nombre')
			
			columns = cursor.description 
			result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
						
			lista = [{'id':1 , 
							'nombre': 'Inicio' , 
							'padre' : None,			
							'propietario_id' : usuarioActual,
							'compartido' : 0,		
							'navegacion' : 'Inicio/',	
							'tipoArchivo_id' : tipoCarpeta,	
							'hijos': obtenerArchivos(result, 1)}]
			
			return Response({'message':'', 'success':'ok', 'data':lista})

		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def obtenerArchivos(lista, id):
	newLista=[]	
	for item in lista:
		if id==item['padre']:				
			newLista.append({
				'id':item['id'] , 
				'nombre': item['nombre'] , 
				'padre' : item['padre'],
				'propietario_id' : item['propietario_id'],
				'compartido' : item['compartido'],
				'navegacion' : 'Inicio/' + item['navegacion'],
				'tipoArchivo_id' : item['tipoArchivo_id'],
				'hijos' : obtenerArchivos(lista, item['id'])
				})
			#navegacion+item['nombre'],
	return newLista	

@api_view(['GET'])
def obtener_archivo_por_id(request, id):
	#lista todas las carpetas que puede ver un usuario para crear el arbol
	if request.method == 'GET':
		try:
			cursor = connection.cursor()
			usuarioActual = request.user.usuario.id
			
			# importante comentario si valida es igual a cero no tiene padre y se le asigna uno
			cursor.execute('select t.id, t.nombre, iif(t.valida=0, 1 , t.padre) as padre, t.propietario_id,t.valida, t.tipoArchivo_id, dbo.mi_nube_crear_navegacion(t.id,t.tipoArchivo_id) as navegacion,\
							(SELECT COUNT(*) FROM mi_nube_archivousuario ur where ur.archivo_id = t.id AND ur.usuario_id <> '+str(usuarioActual)+' ) as compartido \
							from (SELECT a.id,a.nombre,a.padre, a.propietario_id,a.tipoArchivo_id, \
							CASE WHEN ( (SELECT av.id FROM  mi_nube_archivo av   WHERE av.id=a.padre)=1) THEN 1 \
							WHEN(SELECT av.id FROM mi_nube_archivousuario uav inner join mi_nube_archivo av on uav.archivo_id=av.id  \
							WHERE av.id=a.padre AND uav.usuario_id='+str(usuarioActual)+') IS null THEN 0 else \
							(select av.id FROM mi_nube_archivousuario uav INNER JOIN mi_nube_archivo av on uav.archivo_id=av.id  \
							WHERE av.id=a.padre AND uav.usuario_id='+str(usuarioActual)+') END AS valida	\
							FROM mi_nube_archivousuario ua  INNER JOIN mi_nube_archivo a on ua.archivo_id =a.id \
							WHERE a.id={} ua.usuario_id ='+str(usuarioActual)+' AND a.tipoArchivo_id='+str(tipoCarpeta)+' AND a.eliminado=0) as t'.format(id))
			
			columns = cursor.description 
			result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
			item=result[0]	

			lista = {'id':1 , 
							'id':item['id'] , 
							'nombre': item['nombre'] , 
							'padre' : item['padre'],
							'propietario_id' : item['propietario_id'],
							'compartido' : item['compartido'],
							'navegacion' : item['navegacion']
					}
			
			return Response({'message':'', 'success':'ok', 'data':lista})

		except Exception as e:
			print(e)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#metodos para guardar archivo desde la aplicacion de escritorio

#Api rest para Archivo
class ArchivoEscritorioSerializer(serializers.HyperlinkedModelSerializer):

	tipoArchivo = TipoSerializer(read_only = True)
	tipoArchivo_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Tipo.objects.filter(app="archivo"))

	propietario = UsuarioLiteSerializer(read_only = True)
	propietario_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	usuarioModificado = UsuarioLiteSerializer(read_only = True)
	usuarioModificado_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset=Usuario.objects.all())

	class Meta:
		model = Archivo
		fields=('id' , 'nombre' , 'padre' ,
				 'tipoArchivo' , 'tipoArchivo_id' ,
				 'eliminado' , 'peso' 
				 , 'propietario' , 'propietario_id'
				 , 'fechaModificado'
				 , 'usuarioModificado' , 'usuarioModificado_id' )
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'padre' , 'nombre' , 'tipoArchivo_id' , 'propietario_id' , 'eliminado' ),
				message=('El nombre del archivo no se puede repetir.')
				)
				]


@transaction.atomic
@api_view(['POST'])
def guardarArchivo(request):
	if request.method == 'POST':
		# sid = transaction.savepoint()
		try:

			validaArchivo = False
			archivos = request.DATA['lista'];
			# print archivos
			# for request.DATA in archivos:

			if request.DATA['tipoArchivo_id']=='':
				request.DATA['tipoArchivo_id']=0
			
			if int(request.DATA['tipoArchivo_id'])==int(tipoCarpeta):
				request.DATA['destino'] = None
				peso = 0.000001
				request.DATA['peso'] = float(peso)
				validaArchivo = True

			else:
				listaTipo=[59,60,61,62,63,64,65,66,67,68,69]				
				tipoArchivo = int(request.DATA['tipoArchivo_id'])
				if tipoArchivo in listaTipo:
					request.DATA['tipoArchivo_id'] = tipoArchivo
					validaArchivo = True
					request.DATA['peso'] = float(request.DATA['peso'])

			if validaArchivo:
				propietario = request.DATA['propietario_id']				
				
				# verifica si exiiste un archivo eliminado para cambiarle el nombre por; nombre  + eliminado + id
				try:
					archivo_eliminado = Archivo.objects.get(nombre = request.DATA['nombre'] , padre = request.DATA['padre'] , propietario_id = propietario , eliminado = True , tipoArchivo_id = request.DATA['tipoArchivo_id'] )
					archivo_eliminado.nombre = str(archivo_eliminado.nombre)+"-backup"+str(archivo_eliminado.id)
					archivo_eliminado.save()

				except Archivo.DoesNotExist as e:
					pass
					# if sid:
					# 	transaction.savepoint_rollback(sid)

				archivo = Archivo.objects.filter(nombre = request.DATA['nombre'] , padre = request.DATA['padre'] , propietario_id = propietario , eliminado = False , tipoArchivo_id = request.DATA['tipoArchivo_id'] )
				if archivo.count()>0:
					mensaje=' Ya existe un archivo con el mismo nombre y tipo.'
					# if sid:
					# 	transaction.savepoint_rollback(sid)
					return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)	


				serializer = ArchivoEscritorioSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():						
					try:
						
						url_archivo = request.DATA['url_archivo']								
						serializer.save(propietario_id = propietario
									, usuarioModificado_id = request.DATA['usuarioModificado_id']
									,tipoArchivo_id = request.DATA['tipoArchivo_id']
									,destino=url_archivo,
									eliminado=False)
						
						# print 'entro 4'	
						# SE GUARDA LA TRANSACCION DE EL RESGITRO DEL ARCHIVO
						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='mi_nube.Archivo',id_manipulado=serializer.data['id'])
						logs_model.save()

						au = ArchivoUsuario( usuario_id = propietario
										, archivo_id = serializer.data["id"] , escritura = 1)
						au.save()
						# SE GUARDA LA TRANSACCION DEL USUARIO QUE CREA EL ARCHIVO
						logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='mi_nube.ArchivoUsuario',id_manipulado=au.id)
						logs_model.save()

						if int(serializer.data["padre"])>1:
							archivoCreado = Archivo.objects.get(pk=serializer.data["id"])
							archivo2 = Archivo.objects.get(pk=serializer.data["padre"])
							contratos = archivo2.contrato.all()
							proyectos = archivo2.proyecto.all()

							if contratos:
								archivoCreado.contrato.add(*list(contratos))

							if proyectos:
								archivoCreado.proyecto.add(*list(proyectos))										
								
							archivoUser = ArchivoUsuario.objects.get(archivo_id = archivo2.id , usuario_id = archivo2.propietario_id)

							archivoUserCompartir = ArchivoUsuario.objects.filter(archivo_id = archivo2.id).exclude(usuario_id = propietario)
								
							insert_list = []
							if archivoUserCompartir:
								for i in archivoUserCompartir:								
									# print i.usuario_id
									# print i.archivo_id
									# print i.escritura
									auc=ArchivoUsuario(usuario_id = i.usuario_id 
													, archivo_id = serializer.data["id"] , escritura = i.escritura ) 
									auc.save()
									# SE GUARDA LA TRANSACCION DEL USUARIO QUE COMPARTE EL ARCHIVO
									logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='mi_nube.ArchivoUsuario',id_manipulado=auc.id)
									logs_model.save()



						# transaction.savepoint_commit(sid)
						# print 'entro al commit'
						return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
							'data':serializer.data},status=status.HTTP_201_CREATED)
					except Exception as e:	
						print(e)
						functions.toLog(e, 'mi_nube.guardarArchivo')
						# if sid:
						# 	print 'entro en la exception'
						# 	transaction.savepoint_rollback(sid)
						functions.toLog(e, 'mi_nube.guardarArchivo')
						return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
							'data':''},status=status.HTTP_400_BAD_REQUEST)
					
				else:
					# VALIDA SI ALGUN CAMPO VIENE VACIO O ERROR EN LA VALIDACION DE CAMPOS
					# print(serializer.errors)

					if "non_field_errors" in serializer.errors:
						mensaje = serializer.errors['non_field_errors']
					elif "nombre" in serializer.errors:
						mensaje = serializer.errors["nombre"][0]+" En el campo nombre"
					elif "padre" in serializer.errors:
						mensaje = serializer.errors["padre"][0]+" En el campo padre"
					else:
						mensaje = 'datos requeridos no fueron recibidos'

					# if sid:	
					# 	transaction.savepoint_rollback(sid)
					return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)		

			else:
				if len(archivos) > 1: #mostramos solo en el caso de que sea un solo archivo						
					# if sid:
					# 	transaction.savepoint_rollback(sid)
					return Response({'message':'El tipo de archivo no esta permitido guardar.','success':'fail','data': ''})

		except Exception as e:
			# if sid:
			# 	transaction.savepoint_rollback(sid)
			functions.toLog(e, 'mi_nube.guardarArchivo')
			return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
		  		'data':''},status=status.HTTP_400_BAD_REQUEST)	

# @transaction.atomic
# @api_view(['POST'])
# def guardarArchivo(request):
# 	if request.method == 'POST':
# 		sid = transaction.savepoint()
# 		try:

# 			validaArchivo = False
# 			archivos = request.DATA['lista'];
# 			print archivos
# 			for itemData in archivos:

# 				if itemData['tipoArchivo_id']=='':
# 					itemData['tipoArchivo_id']=0
				
# 				if int(itemData['tipoArchivo_id'])==int(tipoCarpeta):
# 					itemData['destino'] = None
# 					peso = 0.000001
# 					itemData['peso'] = float(peso)
# 					validaArchivo = True

# 				else:
# 					listaTipo=[59,60,61,62,63,64,65,66,67,68,69]
# 					if app_escritorio:
# 						print 'entro 1'
# 						tipoArchivo = int(itemData['tipoArchivo_id'])
# 						if tipoArchivo in listaTipo:
# 							itemData['tipoArchivo_id'] = tipoArchivo
# 							validaArchivo = True
# 							itemData['peso'] = float(itemData['peso'])

# 				if validaArchivo:
# 					propietario = itemData['propietario_id']
					
					
# 					# verifica si exiiste un archivo eliminado para cambiarle el nombre por; nombre  + eliminado + id
# 					try:
# 						archivo_eliminado = Archivo.objects.get(nombre = itemData['nombre'] , padre = itemData['padre'] , propietario_id = propietario , eliminado = True , tipoArchivo_id = itemData['tipoArchivo_id'] )
# 						archivo_eliminado.nombre = str(archivo_eliminado.nombre)+"-backup"+str(archivo_eliminado.id)
# 						archivo_eliminado.save()

# 					except Archivo.DoesNotExist as e:
# 						if sid:
# 							transaction.savepoint_rollback(sid)

# 					archivo = Archivo.objects.filter(nombre = itemData['nombre'] , padre = itemData['padre'] , propietario_id = propietario , eliminado = False , tipoArchivo_id = itemData['tipoArchivo_id'] )
# 					if archivo.count()>0:
# 						mensaje=' Ya existe un archivo con el mismo nombre y tipo.'
# 						if sid:
# 							transaction.savepoint_rollback(sid)
# 						return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)	


# 					serializer = ArchivoEscritorioSerializer(data=itemData,context={'request': request})

# 					if serializer.is_valid():						
# 						try:
							
# 							url_archivo = itemData['url_archivo']								
# 							serializer.save(propietario_id = propietario
# 										, usuarioModificado_id = itemData['usuarioModificado_id']
# 										,tipoArchivo_id = itemData['tipoArchivo_id']
# 										,destino=url_archivo,
# 										eliminado=False)
							
# 							print 'entro 4'	
# 							# SE GUARDA LA TRANSACCION DE EL RESGITRO DEL ARCHIVO
# 							logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='mi_nube.Archivo',id_manipulado=serializer.data['id'])
# 							logs_model.save()

# 							au = ArchivoUsuario( usuario_id = propietario
# 											, archivo_id = serializer.data["id"] , escritura = 1)
# 							au.save()
# 							# SE GUARDA LA TRANSACCION DEL USUARIO QUE CREA EL ARCHIVO
# 							logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='mi_nube.ArchivoUsuario',id_manipulado=au.id)
# 							logs_model.save()

# 							if int(serializer.data["padre"])>1:
# 								archivoCreado = Archivo.objects.get(pk=serializer.data["id"])
# 								archivo2 = Archivo.objects.get(pk=serializer.data["padre"])
# 								contratos = archivo2.contrato.all()
# 								proyectos = archivo2.proyecto.all()

# 								if contratos:
# 									archivoCreado.contrato.add(*list(contratos))

# 								if proyectos:
# 									archivoCreado.proyecto.add(*list(proyectos))										
									
# 								archivoUser = ArchivoUsuario.objects.get(archivo_id = archivo2.id , usuario_id = archivo2.propietario_id)

# 								archivoUserCompartir = ArchivoUsuario.objects.filter(archivo_id = archivo2.id).exclude(usuario_id = propietario)
									
# 								insert_list = []
# 								if archivoUserCompartir:
# 									for i in archivoUserCompartir:								
# 										# print i.usuario_id
# 										# print i.archivo_id
# 										# print i.escritura
# 										auc=ArchivoUsuario(usuario_id = i.usuario_id 
# 														, archivo_id = serializer.data["id"] , escritura = i.escritura ) 
# 										auc.save()
# 										# SE GUARDA LA TRANSACCION DEL USUARIO QUE COMPARTE EL ARCHIVO
# 										logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='mi_nube.ArchivoUsuario',id_manipulado=auc.id)
# 										logs_model.save()



# 							transaction.savepoint_commit(sid)
# 							print 'entro al commit'
# 							return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
# 								'data':serializer.data},status=status.HTTP_201_CREATED)
# 						except Exception as e:	
# 							print(e)
# 							functions.toLog(e,self.nombre_modulo)
# 							if sid:
# 								print 'entro en la exception'
# 								transaction.savepoint_rollback(sid)
# 							functions.toLog(e,self.nombre_modulo)
# 							return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
# 								'data':''},status=status.HTTP_400_BAD_REQUEST)
						
# 					else:
# 						# VALIDA SI ALGUN CAMPO VIENE VACIO O ERROR EN LA VALIDACION DE CAMPOS
# 						# print(serializer.errors)

# 						if "non_field_errors" in serializer.errors:
# 							mensaje = serializer.errors['non_field_errors']
# 						elif "nombre" in serializer.errors:
# 							mensaje = serializer.errors["nombre"][0]+" En el campo nombre"
# 						elif "padre" in serializer.errors:
# 							mensaje = serializer.errors["padre"][0]+" En el campo padre"
# 						else:
# 							mensaje = 'datos requeridos no fueron recibidos'

# 						if sid:	
# 							transaction.savepoint_rollback(sid)
# 						return Response({'message':mensaje,'success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)		

# 				else:
# 					if len(archivos) > 1: #mostramos solo en el caso de que sea un solo archivo						
# 						if sid:
# 							transaction.savepoint_rollback(sid)
# 						return Response({'message':'El tipo de archivo no esta permitido guardar.','success':'fail','data': ''})

# 		except Exception as e:
# 			if sid:
# 				transaction.savepoint_rollback(sid)
# 			functions.toLog(e, 'mi_nube.guardarArchivo')
# 			return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
# 		  		'data':''},status=status.HTTP_400_BAD_REQUEST)			