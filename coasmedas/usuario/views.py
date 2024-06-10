# -*- coding: utf-8 -*-
from django.shortcuts import render,redirect
#,render_to_response
from django.urls import reverse
from django.contrib.auth.models import User, Permission, Group
from .models import Usuario, Persona, UserSession
from empresa.models import Empresa
from contrato.models import EmpresaContrato
from rest_framework import viewsets, serializers
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.hashers import check_password,make_password

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from coasmedas.functions import functions
from django.db.models import Count, Sum
from contrato.models import Contrato, EmpresaContrato
from giros.models import DetalleGiro, DEncabezadoGiro

from adminMail.models import Mensaje
from django.conf import settings
from adminMail.tasks import sendAsyncMail
from django.db import transaction, connection
from logs.models import Logs,Acciones, LogsIngresoUsuario
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from opcion.models import Opcion, Opcion_Usuario
import json
from django.template import RequestContext
from parametrizacion.models import Funcionario
from rest_framework.decorators import api_view, throttle_classes
from django.contrib.auth.models import Permission, User, Group

import requests
from datetime import *

from indicadorCalidad.models import AIndicador,BSeguimientoIndicador
import base64

import boto 
from boto.s3.key import Key
import os
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in
from coasmedas.signals import user_logged_in_handler
from factura.models import Factura
# from snowpenguin.django.recaptcha2.fields import ReCaptchaField
# from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

# Create your views here. comentario
class PersonaSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model= Persona
		fields = ('id','cedula','nombres','apellidos','correo','telefono')

class PersonaLiteSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model= Persona
		fields = ('id','nombres','apellidos')

class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('id','username','is_active','password',)

class EmpresaSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Empresa
		fields = ('id','nombre','direccion','logo','esDisenador','esProveedor','esContratista','esContratante')

class UsuarioSerializer(serializers.HyperlinkedModelSerializer):    
    user=UserSerializer(read_only=True)
    user_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset = User.objects.all())
    persona = PersonaSerializer(read_only=True)
    persona_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Persona.objects.all())
    empresa = EmpresaSerializer(read_only=True)
    #empresa_id = serializers.PrimaryKeyRelatedField(write_only=True,queryset = Empresa.objects.all())
    
    class Meta:
        model = Usuario
        fields=('id','foto','user_id','user','persona_id','persona','empresa','iniciales', 'foto_publica')   

class UsuarioLiteSerializer(serializers.HyperlinkedModelSerializer):    

    persona = PersonaLiteSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields=('id','persona') 

class PersonaViewSet(viewsets.ModelViewSet):
	model=Persona
	queryset=model.objects.all()
	serializer_class=PersonaSerializer
	nombre_modulo='usuario.persona'
	paginate_by = 10

	def create(self,request,*args, **kwargs):
		if request.method == 'POST':
			try:
				persona = Persona.objects.filter(cedula=request.DATA['cedula'])				
				if persona:
					return Response({'message':'Ya existe una persona registrada con la cedula ingresada','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
				if request.DATA['correo'] is not None and request.DATA['correo']!='':							
					persona = Persona.objects.filter(correo=request.DATA['correo'])
					if persona:
						return Response({'message':'Ya existe una persona registrada con el correo ingresado','success':'fail',
						'data':''},status=status.HTTP_400_BAD_REQUEST)

				serializer = PersonaSerializer(data=request.DATA,context={'request': request})
				if serializer.is_valid():
					serializer.save()
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
					'data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				functions.toLog(e,self.nombre_modulo)
				return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
				'data':''},status=status.HTTP_400_BAD_REQUEST)

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
			queryset = super(PersonaViewSet, self).get_queryset()			
			paginacion = self.request.query_params.get('sin_paginacion', None)
			dato = self.request.query_params.get('dato', None)
			qset=''
			if dato:
				qset = (Q(nombres__icontains=dato)|
						Q(apellidos__icontains=dato)|
						Q(cedula__icontains=dato)
						)
				queryset = self.model.objects.filter(qset)

			if paginacion is None:
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
			functions.toLog(e,self.nombre_modulo)
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# api usuario
	
class UsuarioViewSet(viewsets.ModelViewSet):
	model=Usuario
	queryset = model.objects.all()
	serializer_class = UsuarioSerializer
	nombre_modulo='usuario.usuario'
	paginate_by = 10

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
			queryset = super(UsuarioViewSet, self).get_queryset()
			dato = self.request.query_params.get('dato', None)
			paginacion = self.request.query_params.get('sin_paginacion', None)
			empresa_id = self.request.query_params.get('empresa_id', None)
			activado = self.request.query_params.get('activado', None)

			if dato or empresa_id or activado:
				if dato:
					qset=(Q(user__username__icontains=dato) |
						Q(iniciales__icontains=dato) |
						Q(persona__nombres__icontains=dato) |
						Q(persona__apellidos__icontains=dato) |
						Q(persona__cedula__icontains=dato))	

				if empresa_id and int(empresa_id)>0:
					if dato:
						qset=qset & (Q(empresa_id=empresa_id))	
					else:
						qset=(Q(empresa_id=empresa_id))

				if activado and int(activado)>0:
					if dato:
						qset=qset & (Q(user__is_active=True))	
					else:
						qset=(Q(user__is_active=True))	

				
				queryset = self.model.objects.filter(qset)
						
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
			return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		if request.method == 'POST':
			sid = transaction.savepoint()
			try:				

				if int(request.DATA['user_id']) == 0:
					try:
						user = User.objects.get(username=request.DATA['usuario'])
						transaction.savepoint_rollback(sid)
						return Response({'message':'El usuario ya existe','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
					except User.DoesNotExist:
						user_model=User(username=request.DATA['usuario'],password=request.DATA['clave'])
						user_model.save()
						request.DATA['user_id']=user_model.id

				
				if int(request.DATA['persona_id']) == 0:
					consulta_persona=Persona.objects.filter(cedula=request.DATA['persona.cedula'])
					if len(consulta_persona)==0:
						persona=Persona(cedula=request.DATA['persona.cedula'],nombres=request.DATA['persona.nombres'],apellidos=request.DATA['persona.apellidos'],correo=request.DATA['persona.correo'],telefono=request.DATA['persona.telefono'])
						persona.save()	
						request.DATA['persona_id']=persona.id
					else:
						transaction.savepoint_rollback(sid)
						return Response({'message':'La cedula de la persona ya existe','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
					
				serializer = UsuarioSerializer(data=request.DATA,context={'request': request})

				if serializer.is_valid():
					empresa_id=request.user.usuario.empresa.id
					if 'empresa_id' in request.DATA: 
						empresa_id=request.DATA['empresa_id']


					serializer.save(
						user_id=request.DATA['user_id'],
						persona_id=request.DATA['persona_id'],
						empresa_id=empresa_id,
						foto=request.FILES['foto'] if request.FILES.get('foto') else 'usuario/default.jpg')

					# persona=Persona(cedula=request.DATA['persona.cedula'],
					# 				nombres=request.DATA['persona.nombres'],
					# 				apellidos=request.DATA['persona.apellidos'],
					# 				correo=request.DATA['persona.correo'],
					# 				telefono=request.DATA['persona.telefono'])
					# persona.save();

					# logs_model_p=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='usuario.persona',id_manipulado=persona.id)
					# logs_model_p.save()

					logs_model_u=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='usuario.usuario',id_manipulado=serializer.data['id'])
					logs_model_u.save()

					transaction.savepoint_commit(sid)
					return Response({'message':'El registro ha sido guardado exitosamente','success':'ok','data':serializer.data},status=status.HTTP_201_CREATED)
				else:
					transaction.savepoint_rollback(sid)
					return Response({'message':'datos requeridos no fueron recibidos','success':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
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
				serializer = UsuarioSerializer(instance,data=request.DATA,context={'request': request},partial=partial)
				
				if serializer.is_valid():
					
					#self.perform_update(serializer)
					
					instance.foto=foto=request.FILES['foto'] if request.FILES.get('foto') else instance.foto
					instance.persona_id=request.DATA['persona_id']
					instance.iniciales=request.DATA['iniciales']
					instance.empresa_id=request.DATA['empresa_id']
					instance.save()	
					
					persona=Persona.objects.get(pk=request.DATA['persona_id'])
					persona.cedula=request.DATA['persona.cedula']
					persona.nombres=request.DATA['persona.nombres']
					persona.apellidos=request.DATA['persona.apellidos']
					persona.correo=request.DATA['persona.correo']
					persona.telefono=request.DATA['persona.telefono']
					persona.save()

					logs_model_p=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='usuario.persona',id_manipulado=persona.id)
					logs_model_p.save()

					logs_model_u=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='usuario.usuario',id_manipulado=instance.id)
					logs_model_u.save()

					if 'notificaciones' in request.DATA:
						notificaciones=json.loads(request.DATA['notificaciones'])
						funcionario=Funcionario.objects.filter(persona__id=request.DATA['persona_id'])
						if funcionario and notificaciones:
							funcionario.first().notificaciones.clear()
							funcionario.first().notificaciones.add(*notificaciones)
						# funcionario.first().notificaciones.clear()
						# funcionario.first().notificaciones.add(*notificaciones)
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
			self.perform_destroy(instance)
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='seguridad_social.escolaridad',id_manipulado=instance.id)
			logs_model.save()
			transaction.savepoint_commit(sid)
			return Response({'message':'El registro se ha eliminado correctamente','success':'ok','data':''},status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			functions.toLog(e,self.nombre_modulo)
			transaction.savepoint_rollback(sid)
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''},status=status.HTTP_400_BAD_REQUEST)
 
	# def get_queryset(self):
	# 	queryset = super(UsuarioViewSet, self).get_queryset()
	# 	dato = self.request.query_params.get('dato', None)
	# 	if dato:
	# 		qset = (
	# 			Q(nombres__icontains=dato)|
	# 			Q(apellidos__icontains=dato)|
	# 			Q(empresa__icontains=dato)
	# 			)
	# 		queryset = self.model.objects.filter(qset)


	# 	return queryset

def login_view(request):
	# Si el usuario esta ya logueado, lo redireccionamos a index_view

	if request.user.is_authenticated:
		# validar sesion del usuario
		userSessiones = UserSession.objects.filter(user__id=request.user.id)
		listaSessionKey = []
		for item in userSessiones:
			listaSessionKey.append(item.session.session_key)
		if len(listaSessionKey) > 0 and request.session.session_key not in listaSessionKey:
			Session.objects.filter(session_key__in=listaSessionKey).delete()

			userSession = UserSession()
			userSession.user_id = request.user.id
			userSession.session_id = request.session.session_key
			userSession.save()	

		if request.GET.get('next'):
			return redirect(request.GET['next'])
		return redirect(reverse('usuario.index'))

	mensaje = ''
	if request.method == 'POST':
		username = request.POST.get('usuario')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		
		# user_logged_in.connect(user_logged_in_handler)

		# Inicio de validacion del reCAPTCHA
		recaptcha_response = request.POST.get('g-recaptcha-response')
		url = 'https://www.google.com/recaptcha/api/siteverify'
		params = {
			'secret': settings.RECAPTCHA_PRIVATE_KEY,
			'response': recaptcha_response
		}
		verify_rs = requests.get(url, params=params, verify=True)
		result = verify_rs.json()
		# data = urllib.urlencode(values)
		# req = urllib2.Request(url, data)
		# response = urllib2.urlopen(req)
		# result = json.load(response)
		# Fin de validacion del reCAPTCHA

		if result['success']:

			if user:
				if user.is_active:
					usuario = Usuario.objects.filter(user=user)
					if usuario:
						obtenerToken(request)
						login(request, user)
						log = LogsIngresoUsuario.objects.filter(usuario_id=usuario[0].id)
						if log:
							logU = LogsIngresoUsuario.objects.get(id=log[0].id)
							logU.ingreso = logU.ingreso + 1
							logU.fecha_hora = datetime.now()
							logU.save()
						else:
							logs_model=LogsIngresoUsuario(usuario_id=usuario[0].id,ingreso=1)
							logs_model.save()						
						# if request.GET.get('next'):
						# 	return redirect(request.GET['next'])
						logs_model=Logs(usuario_id=usuario[0].id,accion='Login',nombre_modelo='logs.Logs',id_manipulado=usuario[0].id)
						logs_model.save()	
						
						if request.GET.get('next') and request.user.is_authenticated:							

							return redirect(request.GET['next'])

						return redirect(reverse('usuario.index'))
					else:
						mensaje = 'El nombre de usuario ingresado no se encuentra el sistema'	
				else:
					mensaje = 'Cuenta inactiva'
			else:
				mensaje = 'Nombre de usuario o clave no valido.'
		else:
			mensaje = 'Demuestra que no eres un robot.'

	if request.GET.get('next') and request.user.is_authenticated():
		return redirect(request.GET['next'])
		       
	return render(request, 'usuario/login.html', {'mensaje': mensaje})

@login_required
def index_view(request):
	accesosDirectos=Opcion_Usuario.objects.filter(usuario_id=request.user.usuario.id)
	if settings.DATABASES['default']['NAME']=='SININ_CARIBE_MAR':
		indicador= AIndicador.objects.all()
	else:
		indicador=None

	seguimientos=None
	
	#print accesosDirectos
	# return render('usuario/index.html',
	# 	{'accesosDirectos':accesosDirectos, 'indicador':indicador,'seguimientos':seguimientos})  
	return render(request,'usuario/index.html',
		{'accesosDirectos':accesosDirectos, 'indicador':indicador,'seguimientos':seguimientos})       
    
def logout_view(request):
	logout(request)
	return redirect(reverse('usuario.login'))

def resetPassword(request):
	mensaje = None
	status=''
	res=''
	if request.method=='POST':
		username = request.POST.get('usuario')		
		try:
			if username != None and username != '':				
				usuario= Usuario.objects.get(user__username=username)
				if usuario:				
					persona = Persona.objects.get(id=usuario.persona.id)
					#inicio del codigo del envio de correo
					contenido='<h3>SININ - Sistema Integral de informacion</h3>'
					contenido = contenido + 'Para reinicio de su clave de acceso a SININ haga click en '
					contenido = contenido + 'el siguiente enlace: <br/><br/>'

					contenido = contenido + '<a href="'+ settings.SERVER_URL2 +'/usuario/finishResetPass/'+str(usuario.user.id)+'/">'

					contenido = contenido + '<b>Reiniciar Clave</b></a><br/><br/>'
					contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
					contenido = contenido + 'Soporte SININ<br/>soporte@totalwork.co'
					mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=persona.correo,
						asunto='Reinicio de clave de acceso a SININ',
						contenido=contenido,
						appLabel='Usuario',
						)			
					mail.save()
					res=sendAsyncMail(mail)
					mensaje='Se ha enviado un correo a ' + persona.correo + ' para iniciar el proceso de recuperacion de clave de acceso al sistema.'
					status='ok'			
					
				else:
					mensaje='El usuario '+ str(username) +' esta mal escrito o no esta registrado en el sistema, verifique e intente nuevamente.'
					status='error'				
				return render(request,'usuario/resetPass.html',{'mensaje': mensaje, 'status':status})
					
		except Usuario.DoesNotExist:
			mensaje='El usuario '+ str(username) +' esta mal escrito o no esta registrado en el sistema, verifique e intente nuevamente.'#'El usuario ' + str(username) + ' No se encuentra registrado en el sistema'
			status='error'
			return render(request,'usuario/resetPass.html',{'mensaje': mensaje, 'status':status})
	
	return render(request,'usuario/resetPass.html')


def sendMail(request):
	mensaje=''
	status=''
	res=''
	if request.method=='POST':
		username = request.POST.get('usuario')		
		try:
			usuario= Usuario.objects.get(user__username=username)
			if usuario:				
				persona = Persona.objects.get(id=usuario.persona.id)
				#inicio del codigo del envio de correo
				contenido='<h3>SININ - Sistema Integral de informacion</h3>'
				contenido = contenido + 'Para reinicio de su clave de acceso a SININ haga click en '
				contenido = contenido + 'el siguiente enlace: <br/><br/>'

				contenido = contenido + '<a href="'+ settings.SERVER_URL2 +'/usuario/finishResetPass/'+str(usuario.user.id)+'/">'

				contenido = contenido + '<b>Reiniciar Clave</b></a><br/><br/>'
				contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
				contenido = contenido + 'Soporte SININ<br/>soporte@totalwork.co'
				mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=persona.correo,
					asunto='Reinicio de clave de acceso a SININ',
					contenido=contenido,
					appLabel='Usuario',
					)			
				mail.save()
				res=sendAsyncMail(mail)
				mensaje='Se ha enviado un correo a ' + persona.correo + ' para iniciar el proceso de recuperacion de clave de acceso al sistema.'
				status='ok'			
				# if mail.simpleSend()==1:
				# 	mensaje='Se ha enviado un correo a ' + persona.correo + ' para iniciar el proceso de recuperacion de clave de acceso al sistema.'
				# 	status='ok'
				# else:
				# 	mensaje = 'Error al enviar el correo'
				# 	status='error'
				#fin del envio de correo
			else:
				mensaje='El usuario '+ str(username) +' esta mal escrito o no esta registrado en el sistema, verifique e intente nuevamente.'
				status='error'

		except Usuario.DoesNotExist:
			mensaje='El usuario ' + str(username) + ' No se encuentra registrado en el sistema'
			status='error'
			return Response({'message':mensaje,'success':status,'data':''},status=status.HTTP_400_BAD_REQUEST)

			
	return render(request,'usuario/resetPass.html',{'mensaje': mensaje, 'status':status})

def finishResetPass(request, id):
	mensaje=''
	status=''
	try:
		if request.method=='POST':
			#print 'contra: '
			#print request.POST.get('password')
			#print 'confirmacion: '
			#print  request.POST.get('confirmPassword')
			if request.POST.get('password') == request.POST.get('confirmPassword'):
				status='ok'
				user=User.objects.get(id=id)
				user.set_password(request.POST.get('password'))
				user.save()
				mensaje='Su nueva clave de acceso al sistema ha sido establecida correctamente. '
				

			else:
				mensaje='La clave y su confirmacion no son iguales'
				status='error'
	except Usuario.DoesNotExist:
		mensaje='Error al procesar la peticion'
		status='error'
	return render(request,'usuario/finishResetPass.html',{'mensaje':mensaje, 'status': status})

@login_required
def perfil(request):
    return render(request, 'usuario/perfil.html')

@login_required
def accesos_directos(request):	
	return render(request,'usuario/accesos_directos.html')

@login_required
def cambiar_usuario(request):	
	return render(request,'usuario/passChange.html') 	      


@api_view(['GET'])
def obtener_opciones(request):
	if request.method == 'GET':		
		try:

			usr = request.user
			dato = request.GET.get('dato')
			permisos = [(x.id) for x in Permission.objects.filter(user=request.user)]
			opciones_usuario=[(x.opcion.id) for x in Opcion_Usuario.objects.filter(usuario__id=request.user.usuario.id)]	
			
			opciones=None
			qset=''
			if request.user.is_superuser:
				if dato:
					qset=(Q(padre__texto__icontains=dato) | Q(texto__icontains=dato))						 
			else:	
				qset = (Q(permiso_id__in=Permission.objects.filter(user=usr.id).values('id')) |
		  	 	Q(permiso_id__in=Permission.objects.filter(group__id__in=Group.objects.filter(user=usr.id).values('id')).values('id')) |
		   		Q(permiso_id=None))			
				if dato:
					qset=qset & (Q(padre__texto__icontains=dato) | Q(texto__icontains=dato))
			if qset:					
				opciones=Opcion.objects.filter(qset).exclude(id__in=opciones_usuario).exclude(destino__contains="#")		
			else:
				opciones=Opcion.objects.exclude(id__in=opciones_usuario).exclude(destino__contains="#")						

			
			lista=[]	
			if opciones:
				for x in opciones:
					item={
						'id':x.id,
						# 'nombre':'test'
						'nombre': "{}({})".format(x.padre.texto.encode('utf8') if x.padre else x.texto.encode('utf8'), x.texto.encode('utf8'))
					}
					lista.append(item)
			
			return Response({'message':'','success':'ok','data':lista})	
					
		except Exception as e:
			functions.toLog(e,'usuario.opciones')
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	


@login_required
def obtener_opciones_usuario(request):
	try:

		dato = request.GET.get('dato', None)
		
		opciones=None
		
		opciones=Opcion_Usuario.objects.filter(usuario__id=request.user.usuario.id)		
		
		lista=[]	
		if opciones:
			for x in opciones:
				item={
					'id':x.opcion.id,
					'nombre':"{}({})".format(x.opcion.texto,x.opcion.padre.texto) if x.opcion.padre else x.opcion.texto,
					'id_opcion_usuario':x.id
				}
				lista.append(item)
		return JsonResponse({'message':'','success':'ok','data':lista})	
				
	except Exception as e:
		functions.toLog(e,'usuario.opciones')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})


@login_required
@transaction.atomic
def eliminar_varios_usuarios(request):
	sid = transaction.savepoint()
	try:
		lista=request.POST['_content']
		respuesta= json.loads(lista)
		#print respuesta['lista'].split()

		#lista=respuesta['lista'].split(',')
		
		for item in respuesta['lista']:
			usuario=Usuario.objects.get(pk=item['id'])
			if usuario.user.is_active==False:
				usuario.user.is_active=True
			else:
				usuario.user.is_active=False
			usuario.user.save()
			usuario.save()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='usuario.usuario',id_manipulado=item['id'])
			logs_model.save()
		
		

		#return HttpResponse(str('0'), content_type="text/plain")
		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'El registro se ha desactivado/activado correctamente','success':'ok',
				'data':''})
		
	except Exception as e:
		functions.toLog(e,'usuario.usuario')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	


@login_required
@transaction.atomic
def guardar_opciones_usuario(request):
	sid = transaction.savepoint()
	try:
		
		resultado=json.loads(request.POST['_content'])		
		lista=resultado['lista_opciones']

		for x in lista:
			ee=Opcion_Usuario(usuario_id=request.user.usuario.id, opcion_id=x)	
			ee.save()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_crear,nombre_modelo='usuario.opcion_usuario',id_manipulado=ee.id)
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'Los accesos directo fueron agregados satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:
		functions.toLog(e,'usuario.opciones')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

@login_required
@transaction.atomic
def eliminar_opciones_usuario(request):
	sid = transaction.savepoint()
	try:
		
		resultado=json.loads(request.POST['_content'])		
		lista=resultado['lista']

		for x in lista:
			ee=Opcion_Usuario.objects.get(pk=x)	
			ee.delete()
			logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_borrar,nombre_modelo='usuario.opcion_usuario',id_manipulado=x)
			logs_model.save()

		transaction.savepoint_commit(sid)
		return JsonResponse({'message':'Los accesos directos fueron eliminados satisfactoriamente.','success':'ok','data':''})	
	except Exception as e:
		functions.toLog(e,'usuario.opciones')
		transaction.savepoint_rollback(sid)
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	


@login_required
def obtener_notificaciones_autogestionables(request):
	cursor = connection.cursor()
	try:

		cursor.callproc('[dbo].[parametrizacion_obtener_notificaciones_autogestionables]', [request.user.usuario.id,request.user.usuario.empresa.id,])
		columns = cursor.description 
		notificaciones = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		
		if notificaciones:
			return JsonResponse({'message':'','success':'ok','data':notificaciones})	
		else:
			return JsonResponse({'message':'Usted no tiene un funcionario asociado o notificaciones!','success':'ok','data':None})	
		
				
	except Exception as e:
		functions.toLog(e,'usuario.notificaciones')
		return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	


@api_view(['POST'])
def autenticar(request):
	try:  	  
		if request.method == 'POST':		
			#return Response({'message':request.DATA['usuario']})
			mensaje=''
			username = request.DATA['usuario']
			password = request.DATA['password']
			user = authenticate(username=username, password=password)

			if user:
				if user.is_active:					
					usuario = Usuario.objects.get(pk=user.usuario.id)
					if usuario:
						key = base64.b64encode(bytes("{}:{}".format(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)))						
						serializer = UsuarioSerializer(usuario)						
						return Response({'message':'','success':'ok','data':{"usuario": serializer.data, "token": key}}, status=status.HTTP_201_CREATED)
					else:					
						return Response({'message':'El nombre de usuario ingresado no se encuentra el sistema','success':'error','data':None})		
				else:
					return Response({'message':'Cuenta inactiva','success':'error','data':None},status=status.HTTP_201_CREATED)	
			else:
				mensaje = 'Nombre de usuario o clave no valido'
				return Response({'message':mensaje,'success':'error','data':None},status=status.HTTP_201_CREATED)	

	except Exception as e:
		functions.toLog(e,'usuario.usuario')
		return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':None})

@api_view(['POST'])
def passwordChange(request):
	try:  	  
		if request.method == 'POST':		
			#return Response({'message':request.DATA['usuario']})
			mensaje=''
			password = request.DATA['password']
			passwordnew = request.DATA['passwordnew']
			usuario = User.objects.get(pk=request.user.id)
			if check_password(password,usuario.password)==True:
				if password==passwordnew:
					return Response({'message':'La contraseña actual no puede ser la misma que la contraseña nueva.','success':'error','data':None})	
				else:
					usuario.password=make_password(passwordnew, salt=None, hasher='default')
					usuario.save()
					return Response({'message':'Su nueva clave de acceso al sistema ha sido establecida correctamente. Vuelva a ingresar al sistema.','success':'ok','data':None})		
			else:					
				return Response({'message':'Contraseña incorrecta.','success':'error','data':None})		


	except Exception as e:
		functions.toLog(e,'usuario.usuario')
		return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':None})	


@api_view(['POST'])
def passwordChangeUsuario(request):
	try:  	  
		if request.method == 'POST':		
			#return Response({'message':request.DATA['usuario']})
			mensaje=''
			password = request.DATA['password']
			usuario_id = request.DATA['usuario_id']
			usuario = Usuario.objects.get(pk=usuario_id)
			usuario.user.password=make_password(password, salt=None, hasher='default')
			usuario.user.save()
			return Response({'message':'Su nueva clave de acceso al sistema ha sido establecida correctamente.','success':'ok','data':None})		
	
	except Exception as e:
		functions.toLog(e,'usuario.usuario')
		return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':None})	


@login_required
def index_usuario(request):	
	empresas=Empresa.objects.all()
	return render(request,'usuario/index_usuario.html',{'model':'usuario','app':'usuario','empresas':empresas}) 

def autenticar_externos(request):

	if request.user.is_authenticated():
		return redirect(reverse('usuario.index'))

	mensaje = ''
	if request.method == 'GET':
		username = request.GET.get('tOqRYjrYScCBtuCPETwjVeYMzyTQi7S0NM0c')#usuario
		password = request.GET.get('FVwkZkMYBu3606pHzjCO')#password
		user = authenticate(username=username, password=password)
		if user:
			if user.is_active:
				usuario = Usuario.objects.filter(user=user)

				if usuario:
					login(request, user)
					return redirect(reverse('usuario.index'))
				else:
					return render(request, 'usuario/login.html', {'mensaje': mensaje})	
			else:
				return render(request, 'usuario/login.html', {'mensaje': mensaje})
		else:
			return render(request, 'usuario/login.html', {'mensaje': mensaje})
	return render(request, 'usuario/login.html', {'mensaje': mensaje})


def descargarAplicaion(request):

	conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)	
	bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)	
	key = bucket.get_key(settings.MEDIAFILES_LOCATION+'/deploy/aplicacion/v2/Sinin.msi')	
	filename=os.path.basename(key.key)
	
	response_headers = {
		'response-content-type': 'application/force-download',
		'response-content-disposition':'attachment;filename="%s"'%filename
    }
	url = key.generate_url(
				60, 
				'GET',				
				response_headers=response_headers,
 				force_http=True)

	return HttpResponseRedirect(url)

def estaAutenticado(request):
	return JsonResponse({'message':'','success':'ok','data':request.user.is_authenticated})

@api_view(['GET'])
def get_dataGraph(request):
	if request.method == 'GET':
		try:
			datos = []
			#cantidad de contratos por estado
			
			qset = None
			qset = EmpresaContrato.objects.filter(empresa__id=request.user.usuario.empresa.id,
				edita=True).values(
				'contrato__estado__nombre').annotate(total=Count('contrato__estado__nombre'))
			
			datagrafica = []
			total = 0
			for obj in qset:
				total = total + obj['total']
			for obj in qset:
				#import pdb; pdb.set_trace()
				datagrafica.append([obj['contrato__estado__nombre'],
					round((float(obj['total']) / float(total))*100,2)])

			datos.append(
				{
					'grafica' : 'Contratos por estado',
					'datagrafica' : datagrafica
				}
			)
			#dinero girado por macrocontrato
			qset = None
			if request.GET.get('filtro'):
				filtro = request.GET.get('filtro')
			else:
				filtro = datetime.now().year - 1
			#import pdb; pdb.set_trace()	
			qset = DetalleGiro.objects.filter(
				encabezado__id__in=DEncabezadoGiro.objects.filter(
					contrato__id__in=EmpresaContrato.objects.filter(
						empresa__id=request.user.usuario.empresa.id,
						edita=True).values('contrato__id')
					).values('id'),estado__codigo=3,encabezado__contrato__mcontrato__nombre__icontains=str(filtro)).values(
			'encabezado__contrato__mcontrato__nombre',
			'encabezado__contrato__mcontrato__id').order_by(
			'encabezado__contrato__mcontrato__id').annotate(
			total_girado=Sum('valor_girar'))

			datagrafica_categorias = []
			datagrafica_girado = []
			datagrafica_legalizado = []
			#idcontratos = []

			for obj in qset:
				datagrafica_categorias.append(obj['encabezado__contrato__mcontrato__nombre'])
				datagrafica_girado.append(round(obj['total_girado']/1000000,2))
				qset = Factura.objects.filter(
					contrato__mcontrato__id=obj['encabezado__contrato__mcontrato__id'],
					contrato__tipo_contrato__id__in=[8,14]).values(
					'contrato__mcontrato__id',).annotate(total_facturas=Sum('valor_contable'))
				datagrafica_legalizado.append(round(qset[0]['total_facturas']/1000000,2) if qset else 0)


			datos.append(
				{
					'grafica' : 'Girado y legalizado por Macrocontrato',
					'datagrafica' : {
						'categorias' : datagrafica_categorias,
						'girado' : datagrafica_girado,
						'legalizado' : datagrafica_legalizado
					}
				}
			)

			#porcentaje promedio de avance de obra
			datagrafica_avance_de_obra = []
			qset = EmpresaContrato.objects.filter(
				empresa__id=request.user.usuario.empresa.id,
				edita=True,
				contrato__tipo_contrato__id=12).values('contrato__nombre')
			for obj in qset:
				datagrafica_avance_de_obra.append({
					'nombre' : obj['contrato__nombre'],
					'avance' : 0
				})
			# qset = BCronograma.objects.filter(
			# 	proyecto__mcontrato__nombre__icontains=str(filtro)
			# 	).values('id','proyecto__mcontrato__nombre').order_by('proyecto__mcontrato__nombre')
			# mcontrato_anterior = ''
			# cont = 0
			# acum = 0
			# prom = 0

			# if qset:
			# 	for obj in qset:
			# 		if mcontrato_anterior != '' and mcontrato_anterior != obj['proyecto__mcontrato__nombre']:
			# 			#import pdb; pdb.set_trace()
			# 			#sacar promedio, reiniciar contador y acumulador
			# 			prom = round(acum / cont , 2)
			# 			cont = 0
			# 			acum = 0
			# 			#agregar datos al array datagrafica_avance_de_obra
			# 			datagrafica_avance_de_obra.append(
			# 				{
			# 					'nombre': mcontrato_anterior,
			# 					'avance' : prom
			# 				}
			# 			)

			# 		cronograma = BCronograma.objects.get(pk=obj['id'])
			# 		mcontrato_anterior = obj['proyecto__mcontrato__nombre']
			# 		if cronograma:
			# 			cont = cont + 1
			# 			acum = acum + cronograma.porcentaje_avance()

			# 	if cont > 0:
			# 		datagrafica_avance_de_obra.append(
			# 			{
			# 				'nombre': mcontrato_anterior,
			# 				'avance' : round(acum / cont , 2)
			# 			}
			# 		)
		
			datos.append(
				{
					'grafica' : 'Avance de obra promedio',
					'datagrafica' : datagrafica_avance_de_obra
				}
			)


			return Response({'message':'','success':'ok','data':datos})	
					
		except Exception as e:
			functions.toLog(e,'usuario.datosGraficas')
			return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error','data':''})	

def obtenerToken(request):
	url = os.environ['LOCAL_END_POINT']
	username = request.POST.get('usuario')
	password = request.POST.get('password')
	client_id = os.environ['CLIENT_ID']
	client_secret = os.environ['CLIENT_SECRET']
	params = 'grant_type=password&username={}&password={}&client_id={}&client_secret={}'.format(username, password, client_id, client_secret)	
	_headers = {
				'Content-Type': 'application/x-www-form-urlencoded',
				'cache-control': "no-cache",
				}
	result = requests.post(url + '/o/token/', data=params, headers=_headers)
	token = result.json()
	if token.get("error"):
		logout_view(request)
	request.session['token'] = token		
	return result.json()

def refrescarToken(request):
	token = request.session.get('token')
	if token is None or token.get("error"):
		logout_view(request)
	url = os.environ['LOCAL_END_POINT']
	refresh_token = request.session['token']['refresh_token']
	client_id = os.environ['CLIENT_ID']
	client_secret = os.environ['CLIENT_SECRET']
	params = 'grant_type=refresh_token&client_id={}&client_secret={}&refresh_token={}'.format(client_id, client_secret, refresh_token)	
	_headers = {
				'Content-Type': 'application/x-www-form-urlencoded',
				'cache-control': "no-cache",
				}
	result = requests.post(url + '/o/token/', data=params, headers=_headers)
	token = result.json()
	if token.get("error"):
		logout_view(request)
	request.session['token'] = token
	return result.json()	