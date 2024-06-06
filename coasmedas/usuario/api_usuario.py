# -*- coding: utf-8 -*-
from django.shortcuts import render,redirect,render_to_response
from django.urls import reverse
from django.contrib.auth.models import User, Permission, Group
from .models import Usuario, Persona
from empresa.models import Empresa
from rest_framework import viewsets, serializers
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.hashers import check_password,make_password

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from adminMail.models import Mensaje
from django.conf import settings
from adminMail.tasks import sendAsyncMail
from django.db import transaction, connection
from logs.models import Logs,Acciones
from django.http import HttpResponse,JsonResponse
from opcion.models import Opcion, Opcion_Usuario
import json
from django.contrib.auth.models import Permission, User, Group
from rest_framework.decorators import api_view, throttle_classes, authentication_classes, permission_classes
from rest_framework_oauth.authentication import OAuth2Authentication
from .views import UsuarioSerializer, UserSerializer, PersonaSerializer
from empresa.views import EmpresaSerializer
from coasmedas.functions import functions
from parametrizacion.models import Funcionario, Cargo

class UsuarioSerializer(serializers.HyperlinkedModelSerializer):    
    user=UserSerializer(read_only=True)
    user_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset = User.objects.all())
    persona = PersonaSerializer(read_only=True)
    persona_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Persona.objects.all())
    empresa = EmpresaSerializer(read_only=True)
    #empresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Empresa.objects.all())
    
    class Meta:
        model = Usuario
        fields=('id', 'user_id','user','persona_id','persona','empresa',)


@api_view(['POST'])
@authentication_classes((OAuth2Authentication,))
@transaction.atomic
def crear_usuario(request):
	#print request.DATA	
	if request.method == 'POST':	

		sid = transaction.savepoint()
		correo = request.DATA.get('correo', None)
		nit = request.DATA.get('nit', None)
		nombre = request.DATA.get('nombre', None)
		try:
			
			if correo == None or nit == None or nombre == None:
				functions.enviar_error('El correo el nit y el nombre son requeridos', request)
				return Response({'message':'El correo el nit y el nombre son requeridos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)	
			
			try:
				user = User.objects.get(username=correo)
				transaction.savepoint_rollback(sid)
				functions.enviar_error('El usuario ya existe', request)
				return Response({'message':'El usuario ya existe','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except User.DoesNotExist:
				password=make_password(nit, salt=None, hasher='default')
				user_model=User(username=correo, password=password)				
				user_model.save()
				grupo = Group.objects.get(pk=4)
				grupo.user_set.add(user_model)
				request.DATA['user_id'] = user_model.id
					
						
			consulta_persona=Persona.objects.filter(cedula=nit)
			if len(consulta_persona)==0:
				persona=Persona(cedula=nit, nombres=nombre, apellidos='',correo=correo,telefono='')
				persona.save()	
				logs_model_p=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='usuario.persona',id_manipulado=persona.id)
				logs_model_p.save()	
				request.DATA['persona_id']=persona.id
			else:
				transaction.savepoint_rollback(sid)
				functions.enviar_error('Ya existe un nit o cedula asociada a una persona', request)
				return Response({'message':'Ya existe un nit o cedula asociada a una persona','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			
			consulta_empresa=Empresa.objects.filter(nit=nit)
			if len(consulta_empresa)==0:
				empresa=Empresa(nit=nit, nombre = nombre, direccion='N/A', esContratista=True)
				empresa.save()
				logs_model_p=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='empresa.empresa',id_manipulado=empresa.id)
				logs_model_p.save()	
				request.DATA['empresa_id']=empresa.id
			else:
				transaction.savepoint_rollback(sid)
				functions.enviar_error('Los datos requeridos no fueron recibidos para crear la empresa', request)
				return Response({'message':'La cedula de la persona ya existe','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

			# creacion del cargo
			cargo = Cargo(nombre='Representante', empresa_id=request.DATA['empresa_id'])
			cargo.save()

			# creacion del funcionario			
			funcionario = Funcionario(empresa_id=request.DATA['empresa_id'], 
										persona_id=request.DATA['persona_id'], 
										cargo_id = cargo.id)	
			funcionario.save()
		
			serializer = UsuarioSerializer(data=request.DATA,context={'request': request})

			if serializer.is_valid():
				serializer.save(
					user_id=request.DATA['user_id'],
					persona_id=request.DATA['persona_id'],
					empresa_id=request.DATA['empresa_id'],
					foto = 'usuario/default.jpg')
				
				logs_model_u=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='usuario.usuario',id_manipulado=serializer.data['id'])
				logs_model_u.save()
				
				enviar_correo(correo, nit)

				transaction.savepoint_commit(sid)
				return Response({'message':'El usuario ha sido creado exitosamente, se le ha enviado un correo de confirmación.','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
			else:				
				transaction.savepoint_rollback(sid)				
				functions.enviar_error('Los datos requeridos no fueron recibidos en crear usuario', request)
				return Response({'message':'Los datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:			
			functions.toLog(e, 'usuario.api_usuario')
			transaction.savepoint_rollback(sid)
			functions.enviar_error(functions.getDeatilLog(e, 'usuario.api_usuario'), request)
			return Response({'message':'Se presentaron errores al procesar los datos','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
			

def enviar_correo(usuario, clave):	
	#inicio del codigo del envio de correo
	contenido = '<h3>SININ - Sistema Integral de informacion</h3>'
	contenido = contenido + 'Se ha creado una cuenta en nuestro sistema SININ, sus datos de acceso son los siguientes:<br><br>'
	contenido = contenido + 'Usuario: {}<br>'.format(usuario)
	contenido = contenido + 'Clave: {}<br><br>'.format(clave)
	contenido = contenido + '<p>Para poder acceder al sistema de <label><a href="http://caribemar.sinin.co/" target="_blank">Clic Aqui</a></label>.</p>: <br/><br/>'	
	contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
	contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
	mail = Mensaje(
		remitente=settings.REMITENTE,
		destinatario=usuario,
		asunto='Registro de usuario SININ',
		contenido=contenido,
		appLabel='Api Usuario',
		)			
	mail.save()
	res=sendAsyncMail(mail)

