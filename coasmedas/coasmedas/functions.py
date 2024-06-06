# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import *
import os
from django.conf import settings
import boto 
from boto.s3.key import Key
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
import uuid
from django.utils.deconstruct import deconstructible
import sys,os
from adminMail.models import Mensaje
from adminMail.tasks import sendAsyncMail
from logs_errors.models import Excepciones
from django.shortcuts import render, render_to_response
import io
import base64
from io import StringIO
import boto3

class functions:	

	@staticmethod
	def path_and_rename(path,prefix):
		def wrapper(instance, filename):			
			filename, file_extension = os.path.splitext(filename)			
			# get filename
			fecha=datetime.now()
			filename = '{}_{}{}{}{}{}{}{}'.format(prefix,fecha.year,fecha.month,fecha.day,fecha.hour,fecha.minute,fecha.second, file_extension)		

			return os.path.join(path, filename)
		return wrapper

	@staticmethod
	def toLog(e,modulo):
		ahora=datetime.now()
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		exepciones = Excepciones();
		message = str(e)
		exepciones.error = ('\n'+ str(ahora) + '--> ' + str(fname) +' linea ' + str(exc_tb.tb_lineno) + ' --> ' + modulo + ': ' + message)
		exepciones.modulo = modulo
		exepciones.save()
		# 		+ ' --> ' + modulo + ': ' + e.message
		# with open(settings.LOG_ERROR,'a') as f:
		# 	f.write ('\n'+ str(ahora) + '--> ' + str(fname) +' linea ' + str(exc_tb.tb_lineno) 
		# 		+ ' --> ' + modulo + ': ' + e.message)
		# 	f.close()	

	@staticmethod
	def getDeatilLog(e, modulo):
		ahora=datetime.now()
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		return str(ahora) + '--> ' + str(fname) +' linea ' + str(exc_tb.tb_lineno) + ' --> ' + modulo + ': ' + e.message

	@staticmethod	
	def enviar_error(mensaje, request):	
		#inicio del codigo del envio de correo
		contenido = '<h3>SININ - Sistema Integral de informacion</h3>'
		contenido = contenido + 'Le informamos que ha ocurrido un error en el sistema SININ, a continuacion el detalle:<br><br>'	
		contenido = contenido + '<b>Excepcion</b>:' + mensaje + '<br/><br/>'
		contenido = contenido + '<b>Origen</b>: http://{}{}<br><br/>'.format(request.META.get('HTTP_HOST'), request.META.get('PATH_INFO'))				
		contenido = contenido + '<b>Datos</b>: {}<br><br><br/>'.format(str(request.DATA))
		
		contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
		contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
		mail = Mensaje(
			remitente=settings.REMITENTE,
			destinatario='dacosta@totalwork.co;cvisbal0724@gmail.com',
			asunto='Error SININ {}'.format(request.META.get('HTTP_HOST')),
			contenido=contenido,
			appLabel='Api Usuario',
			)			
		mail.save()
		res=sendAsyncMail(mail)	
		
	@staticmethod
	def descargarArchivoS3(ruta_relativa, ruta_descarga, nombre_archivo=None):
		try:	
			conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)	
			bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)	
			key = bucket.get_key(settings.MEDIAFILES_LOCATION+'/'+ruta_relativa)
			filename=os.path.basename(key.key)
			key.get_contents_to_filename(ruta_descarga + (nombre_archivo if nombre_archivo else filename))
			key.set_contents_from_filename(ruta_descarga + (nombre_archivo if nombre_archivo else filename))
			return {'archivo': ruta_relativa, 'success': True}
		except Exception as e:
			functions.toLog(e, 'Descargar archivo de s3')
			return {'archivo': ruta_relativa, 'success': False}


	@staticmethod
	def eliminarArchivoS3(nombre_archivo):
		conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)
		bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
		key = bucket.get_key(settings.MEDIAFILES_LOCATION+'/'+nombre_archivo)
		key.delete()
			

	@staticmethod
	def exportarArchivoS3(ruta_relativa, nombre_archivo=None):
			
			conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)	
			bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)	
			key = bucket.get_key(settings.MEDIAFILES_LOCATION+'/'+ruta_relativa)
			# print os.path.basename(key.key)
			filename= os.path.basename(key.key) if nombre_archivo is None else nombre_archivo
			
			extension = os.path.splitext(filename)[1]
			extension = extension.lower()
			validar = ['.jpeg', '.jpg', '.png']
									
			if extension == '.pdf':
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="application/pdf")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response
			elif extension == '.jpg':
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="image/jpg")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response
			elif extension == '.jpeg':
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="image/jpeg")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response	
			elif extension == '.png':
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="image/png")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response

			elif extension == '.zip':
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="application/zip")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response

			elif extension == '.docx':
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response
			elif extension == '.doc':											
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="application/msword")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response
			elif extension == '.msg':											
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="application/octet-stream")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response
			elif extension == '.xlsx':											
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response
			elif extension == '.xls':											
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="application/vnd.ms-excel")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response
			elif extension == '.dwg':											
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="image/vnd.dwg")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response
			elif extension == '.rar':						
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="application/x-rar")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response
			elif extension == '.xlsm':						
				content = key.get_contents_as_string()	
				file_stream = io.BytesIO(content)				
				response = HttpResponse(file_stream.getvalue(), content_type="application/vnd.ms-excel.sheet.macroEnabled.12")
				# response['Content-Disposition'] = 'attachment;filename="%s"'%filename
				file_stream.close()
				return response
	
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

	@staticmethod
	def crearRutaTemporalArchivoS3(ruta_relativa, duracion = 60):
		s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, aws_session_token=None)
		url = s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,'Key': settings.MEDIAFILES_LOCATION+'/'+ruta_relativa,},ExpiresIn=duracion)
		return url
		# conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)	
		# bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)	
		# key = bucket.get_key(settings.MEDIAFILES_LOCATION+'/'+ruta_relativa)
		# # print os.path.basename(key.key)
		# filename= os.path.basename(key.key)
		
		# # response_headers = {
		# # 'response-content-type': 'application/force-download',
		# # 'response-content-disposition':'attachment;filename="%s"'%filename
		# # }
		# url = key.generate_url(
		# 			duracion, 
		# 			'GET',				
		# 			response_headers=None,
	 	# 			force_http=False)

		# return url# HttpResponseRedirect(url)

	@staticmethod	
	def subirArchivoS3(keyV, file, callback=None, md5=None, reduced_redundancy=False, content_type=None):
		
		try:
			functions.eliminarArchivoS3(keyV)
		except Exception as e:
			pass

		try:
			size = os.fstat(file.fileno()).st_size
		except Exception as e:
			# Not all file objects implement fileno(),
			# so we fall back on this
			file.seek(0, os.SEEK_END)
			size = file.tell()

		conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
		bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME, validate=True)			
		k = Key(bucket)
		k.key = settings.MEDIAFILES_LOCATION+ '/' + keyV
		if content_type:
			k.set_metadata('Content-Type', content_type)
		sent = k.set_contents_from_file(file, cb=callback, md5=md5, reduced_redundancy=reduced_redundancy, rewind=True)
		# Rewind for later use
		file.seek(0)
		file.close()
		if sent == size:
			return {'archivo': keyV, 'success': True}
		return {'archivo': keyV, 'success': False}

@deconstructible
class RandomFileName(object):
	def __init__(self, path, prefix = ''):
		self.path = path
		self.prefix = prefix

	def __call__(self,_,filename):		
		filename, file_extension = os.path.splitext(filename)			
		# get filename
		fecha=datetime.now()
		filename = '{}_{}{}{}{}{}{}{}'.format(self.prefix,fecha.year,fecha.month,fecha.day,fecha.hour,fecha.minute,fecha.second, file_extension)		

		return os.path.join(self.path, filename)
